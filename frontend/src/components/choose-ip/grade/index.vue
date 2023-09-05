<template>
  <div class="iam-choose-ip">
    <div class="topology-wrapper">
      <div class="resource-select-wrapper">
        <resource-select
          :list="selectList"
          :value="selectValue"
          @on-select="handleResourceSelect" />
      </div>
      <topology-input
        ref="headerInput"
        :is-filter="isFilter"
        :placeholder="curPlaceholder"
        @on-search="handleSearch" />
      <div class="topology-tree-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="treeData.length > 0 && !isLoading">
          <topology-tree
            ref="topologyRef"
            :all-data="treeData"
            :search-value="hasSearchValues"
            @on-expanded="handleOnExpanded"
            @on-search="handleTreeSearch"
            @on-select="handleTreeSelect"
            @on-load-more="handleLoadMore"
            @async-load-nodes="handleAsyncNodes" />
        </template>
        <template v-if="treeData.length < 1 && !isLoading">
          <div class="empty-wrapper">
            <ExceptionEmpty
              style="background: #fafbfd"
              :type="emptyData.type"
              :empty-text="emptyData.text"
              :tip-text="emptyData.tip"
              :tip-type="emptyData.tipType"
              @on-clear="handleEmptyClear"
              @on-refresh="handleEmptyRefresh"
            />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { guid, formatCodeData } from '@/common/util';
  import il8n from '@/language';
  import ResourceSelect from '../resource-select';
  import TopologyInput from '../topology-input';
  import TopologyTree from '../topology-tree';

  const LOAD_ITEM = {
    nodeId: guid(),
    id: -1,
    visiable: true,
    loading: false,
    display_name: il8n('common', '查看更多')
  };

  const SEARCH_ITEM = {
    nodeId: guid(),
    id: -2,
    visiable: true
  };

  const SEARCH_EMPTY_ITEM = {
    nodeId: guid(),
    id: -3,
    visiable: true
  };

  const SEARCH_LOAD_ITEM = {
    nodeId: guid(),
    id: -4,
    visiable: true
  };

  const ASYNC_ITEM = {
    nodeId: guid(),
    id: -4,
    visiable: true
  };

  const RESULT_TIP = {
    '0': il8n('common', '搜索无结果'),
    '1902204': il8n('common', '暂不支持搜索'),
    '1902229': il8n('info', '搜索过于频繁'),
    '1902222': il8n('info', '搜索结果太多')
  };

  const ERROR_CODE_LIST = [1902204, 1902229, 1902222, 1902206];

  class Node {
    constructor (payload, level = 0, isAsync = true, type = 'node') {
      this.disabled = payload.disabled || false;
      this.checked = payload.checked || false;
      this.expanded = false;
      this.loading = false;
      this.loadingMore = false;
      this.current = payload.current || 0;
      this.totalPage = payload.totalPage || 0;
      this.id = payload.id;
      this.name = payload.display_name || '';
      this.parentId = level > 0 ? payload.parentId : '';
      this.parentSyncId = level > 0 ? payload.parentSyncId : '';
      this.level = level;
      this.nodeId = guid();
      this.async = isAsync;
      this.children = [];
      this.parentChain = payload.parentChain || [];
      this.type = type;
      this.childType = payload.child_type || '';
      this.isRemote = payload.isRemote || false;
      this.isFilter = payload.isFilter || false;
      this.placeholder = payload.placeholder || '';
      // 是否存在未带下一级的无限制数据
      this.isExistNoCarryLimit = payload.isExistNoCarryLimit || false;
      this.isFrontendSearch = payload.isFrontendSearch || false;
      this.initVisiable(payload);
    }

    initVisiable (payload) {
      if (payload.hasOwnProperty('visiable')) {
        this.visiable = payload.visiable;
        return;
      }
      this.visiable = true;
    }
  }

  export default {
    name: '',
    components: {
      ResourceSelect,
      TopologyInput,
      TopologyTree
    },
    props: {
      selectList: {
        type: Array,
        default: () => []
      },
      selectValue: {
        type: String,
        default: ''
      },
      treeValue: {
        type: Array,
        default: () => []
      },
      limitValue: {
        type: Array,
        default: () => []
      },
      // mode: template grade
      mode: {
        type: String,
        default: 'template'
      },
      curSelectionCondition: {
        type: Array,
        default: () => []
      },
      systemParams: {
        type: Object,
        default: () => {
          return {
            action_id: '',
            system_id: ''
          };
        }
      }
    },
    data () {
      return {
        isLoading: false,
        // 节点数据分页的limit
        limit: 100,
        // limit: 11,
        // 当前选择的链路
        curChain: [],
        treeData: [],
        // 已选择的节点
        hasSelectedValues: [],
        // 已搜索到的节点
        hasSearchValues: [],
        // 忽略标识
        ignorePathFlag: false,
        // 是否存在忽略标识
        isExistIgnore: false,
        curKeyword: '',
        isFilter: false,
        curSearchObj: {},
        curPlaceholder: '',
        // 空数据或异常数据配置项
        emptyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      isExistLimitValue () {
        return this.getLimitResourceData().length > 0;
      },
      isTemplateMode () {
        return this.mode === 'template';
      }
    },
    watch: {
      treeValue: {
        handler (value) {
          if (value.length) {
            const hasSelecteds = [];
            value.forEach(item => {
              item.path.forEach(pathItem => {
                hasSelecteds.push({
                  ids: pathItem.map(v => `${v.id}&${v.type}`),
                  idChain: pathItem.map(v => `${v.id}&${v.type}`).join('#'),
                  disabled: pathItem.some(subItem => subItem.disabled)
                });
              });
            });
            this.hasSelectedValues = _.cloneDeep(hasSelecteds);
          } else {
            this.hasSelectedValues = [];
          }
        },
        deep: true,
        immediate: true
      },
      selectValue: {
        handler (value) {
          console.log('this.limitValue', this.limitValue);
          if (value) {
            this.curChain = this.selectList[0].resource_type_chain;
            console.log('choose-ip this.curChain', this.curChain);
            this.ignorePathFlag = this.selectList[0].ignore_iam_path;
            this.isExistIgnore = this.selectList.some(item => item.ignore_iam_path);
            const index = this.ignorePathFlag ? this.curChain.length - 1 : 0;
            this.curPlaceholder = `${this.$t(`m.common['搜索']`)} ${this.curChain[index].name}`;
            // 不存在限制范围时需首次请求接口
            if (this.limitValue.length < 1) {
              this.firstFetchResources();
            }
          }
        },
        immediate: true
      },
      limitValue: {
        handler (val) {
          if (val.length > 0) {
            this.treeData = this.getLimitResourceData();
          }
        },
        immediate: true
      }
    },
    methods: {
      isArrayInclude (target, origin) {
        const itemAry = [];
        target.forEach(function (p1) {
          if (origin.indexOf(p1) !== -1) {
            itemAry.push(p1);
          }
        });
        if (itemAry.length === target.length) {
          return true;
        }
        return false;
      },

      handleSearch (payload) {
        this.curKeyword = payload;
        this.emptyData.tipType = 'search';
        if (this.isFilter && payload === '') {
          this.isFilter = false;
        } else {
          this.isFilter = true;
        }
        if (this.isExistLimitValue) {
          this.emptyData.tipType = 'search';
          this.handleFrontendSearch();
          return;
        }
        this.firstFetchResources();
      },

      handleEmptyRefresh () {
        this.firstFetchResources();
      },

      handleEmptyClear () {
        this.$refs.headerInput.value = '';
        this.emptyData.tipType = '';
        if (this.isExistLimitValue) {
          this.curKeyword = '';
          this.handleFrontendSearch();
          return;
        }
        this.firstFetchResources();
      },

      handleFrontendSearch () {
        const keyword = this.curKeyword.trim();
        const treeData = this.getLimitResourceData();
        if (keyword === '') {
          this.treeData = treeData;
          return;
        }
        this.treeData = treeData.filter(
          item => item.name.toLowerCase().indexOf(this.curKeyword.toLowerCase()) !== -1
        );
        if (!this.treeData.length) {
          this.emptyData = formatCodeData(0, this.emptyData);
        }
      },

      getLimitResourceData () {
        // debugger
        const chainLen = this.curChain.length;
        const curChainId = this.curChain.map(item => item.id);
        const lastChainId = this.curChain[chainLen - 1].id;
        const limitValue = _.cloneDeep(this.limitValue);
        limitValue.forEach(item => {
          item.path = item.path.filter(pathItem => {
            return this.isArrayInclude(pathItem.map(v => v.type), curChainId)
              || (this.ignorePathFlag && pathItem.length === 1 && pathItem[0].type === lastChainId);
          });
        });
        const params = {
          system_id: this.curChain[0].system_id,
          type: this.curChain[0].id
        };
        let isAsync = chainLen > 1;
        const treeData = [];
        limitValue.forEach(item => {
          item.path.forEach(pathItem => {
            const node = pathItem[0];
            if (this.ignorePathFlag && pathItem.length === 1 && pathItem[0].type === lastChainId) {
              isAsync = false;
            }
            let checked = false;
            let disabled = false;
            let isRemote = false;
            let isExistNoCarryLimit = false;
            if (this.hasSelectedValues.length > 0) {
              let noCarryLimitData = {};
              let normalSelectedData = {};
              this.hasSelectedValues.forEach(val => {
                const curKey = `${node.id}&${params.type}`;
                if (isAsync) {
                  const curIdChain = `${curKey}#*&${this.curChain[1].id}`;
                  if (val.idChain === curIdChain) {
                    normalSelectedData = val;
                  }
                  if (val.idChain === curKey) {
                    noCarryLimitData = val;
                  }
                } else {
                  if (val.idChain === curKey) {
                    normalSelectedData = val;
                  }
                }
              });
              isExistNoCarryLimit = Object.keys(noCarryLimitData).length > 0;
              if (isExistNoCarryLimit && Object.keys(normalSelectedData).length > 0) {
                checked = true;
                disabled = normalSelectedData.disabled && noCarryLimitData.disabled;
                isRemote = disabled;
              } else {
                if (isExistNoCarryLimit || Object.keys(normalSelectedData).length > 0) {
                  checked = true;
                  disabled = normalSelectedData.disabled || noCarryLimitData.disabled;
                  isRemote = disabled;
                }
              }
            }
            const nodeItem = {
              id: node.id,
              display_name: node.name,
              checked,
              disabled: disabled || (!!pathItem[1] && pathItem[1].id !== '*'),
              isRemote,
              isExistNoCarryLimit
            };
            if (!treeData.map(v => v.id).includes(node.id)) {
              treeData.push(new Node(nodeItem, 0, isAsync));
            }
          });
        });

        return treeData;
      },

      handleOnExpanded (index, expanded) {
        window.changeAlert = true;
        if (!expanded && this.treeData[index + 2].type === 'search-empty') {
          this.treeData.splice(index + 2, 1);
        }
      },

      async handleTreeSearch (payload) {
        window.changeAlert = true;
        const { index, node, value } = payload;

        this.curSearchObj = Object.assign({}, {
          value,
          parentId: node.parentId
        });

        if (node.isFilter && value === '') {
          node.isFilter = false;
        } else {
          node.isFilter = true;
        }

        this.treeData = this.treeData.filter(item => item.type !== 'search-empty');

        const chainLen = this.curChain.length;
        const params = {
          limit: this.limit,
          offset: 0,
          ancestors: [],
          keyword: value
        };

        if (node.level > chainLen - 1) {
          params.system_id = this.curChain[chainLen - 1].system_id;
          params.type = this.curChain[chainLen - 1].id;
          params.action_system_id = this.systemParams.system_id || '';
          params.action_id = this.systemParams.action_id || '';
        } else {
          params.system_id = this.curChain[node.level].system_id;
          params.type = this.curChain[node.level].id;
          // params.action_system_id = this.curChain[node.level].system_id;
          params.action_system_id = this.systemParams.system_id || '';
          params.action_id = this.systemParams.action_id || '';
        }

        if (node.parentChain.length) {
          const parentData = node.parentChain.reduce((p, e) => {
            p.push({
              system_id: e.system_id,
              id: e.id,
              type: e.type
            });
            return p;
          }, []);
          params.ancestors.push(...parentData);
        }

        const parentNode = this.treeData.find(item => item.nodeId === node.parentId);

        if (parentNode && !parentNode.children) {
          parentNode.children = [];
        }

        if (node.isFrontendSearch) {
          const childrenNodes = parentNode.children.filter(
            item => item.name.toLowerCase().indexOf(value.trim().toLowerCase()) !== -1
          );
          const isAsync = this.curChain.length > (node.level + 1);

          this.treeData = this.treeData.filter(item => {
            const flag = item.type === 'search' && item.parentId === node.parentId;
            return flag || !item.parentChain.map(v => v.id).includes(node.parentSyncId);
          });

          if (childrenNodes.length < 1) {
            const searchEmptyItem = {
                            ...SEARCH_EMPTY_ITEM,
                            parentId: node.parentId,
                            parentSyncId: node.id,
                            parentChain: _.cloneDeep(node.parentChain),
                            level: node.level,
                            display_name: RESULT_TIP[0]
            };
            const searchEmptyData = new Node(searchEmptyItem, node.level, false, 'search-empty');
            this.treeData.splice((index + 1), 0, searchEmptyData);
            return;
          }

          const loadNodes = childrenNodes.map(item => {
            let tempItem = _.cloneDeep(item);
            let checked = false;
            let disabled = false;
            let isRemote = false;
            let isExistNoCarryLimit = false;
            if (this.hasSelectedValues.length > 0) {
              // 父级链路id + 当前id = 整条链路id
              const curIds = node.parentChain.map(v => `${v.id}&${v.type}`);
              // 取当前的请求的type
              curIds.push(`${item.id}&${params.type}`);
              const tempData = [...curIds];
              if (isAsync) {
                curIds.push(`*&${this.curChain[node.level + 1].id}`);
              }
              let noCarryLimitData = {};
              let normalSelectedData = {};
              this.hasSelectedValues.forEach(val => {
                if (isAsync && val.idChain === tempData.join('#')) {
                  noCarryLimitData = val;
                } else {
                  if (!isAsync && val.ids.length === 1 && this.ignorePathFlag && val.ids[0] === `${item.id}&${params.type}`) {
                    normalSelectedData = val;
                  } else {
                    if (val.idChain === curIds.join('#')) {
                      normalSelectedData = val;
                    }
                  }
                }
              });

              isExistNoCarryLimit = Object.keys(noCarryLimitData).length > 0;
              if (isExistNoCarryLimit && Object.keys(normalSelectedData).length > 0) {
                checked = true;
                disabled = normalSelectedData.disabled && noCarryLimitData.disabled;
                isRemote = disabled;
              } else {
                if (isExistNoCarryLimit || Object.keys(normalSelectedData).length > 0) {
                  checked = true;
                  disabled = normalSelectedData.disabled || noCarryLimitData.disabled;
                  isRemote = disabled;
                }
              }
            }

            if (node.level > 0) {
              tempItem = {
                id: item.id,
                display_name: item.name,
                parentId: node.parentId,
                parentSyncId: node.id,
                disabled: parentNode.checked || disabled,
                checked: checked || parentNode.checked,
                parentChain: _.cloneDeep(node.parentChain),
                isRemote,
                isExistNoCarryLimit
              };
            } else {
              tempItem.checked = checked;
              tempItem.disabled = disabled;
              tempItem.isExistNoCarryLimit = isExistNoCarryLimit;
            }

            const isAsyncFlag = isAsync || item.child_type !== '';
            return new Node(tempItem, node.level, isAsyncFlag);
          });

          this.treeData.splice((index + 1), 0, ...loadNodes);
          return;
        }

        const searchLoadingItem = {
                    ...SEARCH_LOAD_ITEM,
                    parentId: node.parentId,
                    parentSyncId: node.parentSyncId,
                    parentChain: _.cloneDeep(node.parentChain),
                    level: node.level
        };
        const searchLoadingData = new Node(searchLoadingItem, node.level, false, 'search-loading');
        this.treeData.splice((index + 1), 0, searchLoadingData);
        try {
          const { code, data } = await this.$store.dispatch('permApply/getResources', params);
          this.treeData = this.treeData.filter(item => {
            const flag = item.type === 'search' && item.parentId === node.parentId;
            return flag || !item.parentChain.map(v => v.id).includes(node.parentSyncId);
          });

          this.emptyData = formatCodeData(code, this.emptyData, data.results.length === 0);
          if (data.results.length < 1) {
            const searchEmptyItem = {
                            ...SEARCH_EMPTY_ITEM,
                            parentId: node.parentId,
                            parentSyncId: node.id,
                            parentChain: _.cloneDeep(node.parentChain),
                            level: node.level,
                            display_name: RESULT_TIP[code]
            };
            const searchEmptyData = new Node(searchEmptyItem, node.level, false, 'search-empty');
            this.treeData.splice((index + 1), 0, searchEmptyData);
            return;
          }

          const totalPage = Math.ceil(data.count / this.limit);

          let isAsync = this.curChain.length > (node.level + 1);
          const loadNodes = data.results.map(item => {
            let tempItem = _.cloneDeep(item);

            let checked = false;
            let disabled = false;
            let isRemote = false;
            let isExistNoCarryLimit = false;
            if (!isAsync && item.child_type !== '') {
              isAsync = true;
            }
            if (this.hasSelectedValues.length > 0) {
              // 父级链路id + 当前id = 整条链路id
              const curIds = node.parentChain.map(v => `${v.id}&${v.type}`);
              // 取当前的请求的type
              curIds.push(`${item.id}&${params.type}`);

              const tempData = [...curIds];

              if (isAsync) {
                const nextLevelId = (() => {
                  const nextLevelData = this.curChain[node.level + 1];
                  if (nextLevelData) {
                    return nextLevelData.id;
                  }
                  return this.curChain[chainLen - 1].id;
                })();
                curIds.push(`*&${nextLevelId}`);
              }

              let noCarryLimitData = {};
              let normalSelectedData = {};
              this.hasSelectedValues.forEach(val => {
                if (isAsync && val.idChain === tempData.join('#')) {
                  noCarryLimitData = val;
                } else {
                  if (!isAsync && val.ids.length === 1 && this.ignorePathFlag && val.ids[0] === `${item.id}&${params.type}`) {
                    normalSelectedData = val;
                  } else {
                    if (val.idChain === curIds.join('#')) {
                      normalSelectedData = val;
                    }
                  }
                }
              });

              isExistNoCarryLimit = Object.keys(noCarryLimitData).length > 0;
              if (isExistNoCarryLimit && Object.keys(normalSelectedData).length > 0) {
                checked = true;
                disabled = normalSelectedData.disabled && noCarryLimitData.disabled;
                isRemote = disabled;
              } else {
                if (isExistNoCarryLimit || Object.keys(normalSelectedData).length > 0) {
                  checked = true;
                  disabled = normalSelectedData.disabled || noCarryLimitData.disabled;
                  isRemote = disabled;
                }
              }
            }

            if (node.level > 0) {
              tempItem = {
                                ...item,
                                parentId: node.parentId,
                                parentSyncId: node.id,
                                disabled: parentNode.checked || disabled,
                                checked: checked || parentNode.checked,
                                parentChain: _.cloneDeep(node.parentChain),
                                isRemote,
                                isExistNoCarryLimit
              };
            } else {
              tempItem.checked = checked;
              tempItem.disabled = disabled;
              tempItem.isExistNoCarryLimit = isExistNoCarryLimit;
            }

            const isAsyncFlag = isAsync || item.child_type !== '';
            return new Node(tempItem, node.level, isAsyncFlag);
          });
          this.treeData.splice((index + 1), 0, ...loadNodes);

          // 将新加载的节点push到父级点的children中
          parentNode.children.splice(0, parentNode.children.length, ...loadNodes);

          if (totalPage > 1) {
            const loadItem = {
                            ...LOAD_ITEM,
                            totalPage: totalPage,
                            current: 1,
                            parentSyncId: node.id,
                            parentId: node.parentId,
                            parentChain: _.cloneDeep(node.parentChain)
            };
            const loadData = new Node(loadItem, node.level, isAsync, 'load');
            this.treeData.splice((index + loadNodes.length + 1), 0, loadData);
            parentNode.children.push(loadData);
          }
        } catch (e) {
          console.error(e);
          if (!ERROR_CODE_LIST.includes(e.code)) {
            this.messageAdvancedError(e);
          }
          const message = e.code !== 1902206 ? RESULT_TIP[e.code] : e.message;
          const searchEmptyItem = {
                        ...SEARCH_EMPTY_ITEM,
                        parentId: node.parentId,
                        parentSyncId: node.id,
                        parentChain: _.cloneDeep(node.parentChain),
                        level: node.level,
                        display_name: message
          };
          this.emptyData = formatCodeData(e.code, this.emptyData);
          const searchEmptyData = new Node(searchEmptyItem, node.level, false, 'search-empty');
          this.treeData.splice((index + 1), 0, searchEmptyData);
        } finally {
          this.$nextTick(() => {
            this.$refs.topologyRef && this.$refs.topologyRef.handleSetFocus(index);
          });
          this.treeData = this.treeData.filter(item => item.type !== 'search-loading');
        }
      },

      setNodeNoChecked (value, node) {
        if (node.children && node.children.length > 0) {
          const children = this.treeData.filter(item => item.parentId === node.nodeId);
          children.forEach(item => {
            // isRemote 已有默认权限标识
            if (item.checked !== value && !item.isRemote) {
              item.checked = value;
            }
            if (item.disabled !== value && !item.isRemote) {
              item.disabled = value;
            }
            if (item.children && item.children.length > 0) {
              this.setNodeNoChecked(value, item);
            }
          });
        }
      },

      setNodeChecked (value, node) {
        if (node.children && node.children.length > 0) {
          const children = this.treeData.filter(item => item.parentId === node.nodeId);
          children.forEach(item => {
            item.checked = value;
            item.disabled = true;
            if (item.children && item.children.length > 0) {
              this.setNodeChecked(value, item);
            }
          });
        }
      },

      handeCancelChecked (payload) {
        const curNode = this.treeData.find(item => {
          const { parentChain, id, async, childType } = item;
          const curIds = parentChain.map(v => `${v.id}&${v.type}`);
          let type = '';
          if (childType !== '') {
            type = childType;
            curIds.push(`${id}&${type}`);
          } else {
            type = this.curChain[item.level].id;
            curIds.push(`${id}&${type}`);
          }

          const chainCheckedFlag = curIds.join('#') === payload;

          if (!this.isExistIgnore) {
            return chainCheckedFlag;
          }
          // 优先判断整个链路是否相等
          if (chainCheckedFlag) {
            return chainCheckedFlag;
          }
          if (this.ignorePathFlag || (parentChain.length < 1 && !async)) {
            return `${id}&${type}` === payload;
          }
          return false;
        });
        if (curNode && !curNode.disabled) {
          curNode.checked = false;
          this.setNodeNoChecked(false, curNode);
        }
      },

      handeSetChecked (payload) {
        const curNode = this.treeData.find(item => {
          const { parentChain, id, async, childType } = item;
          const curIds = parentChain.map(v => `${v.id}&${v.type}`);
          let type = '';
          if (childType !== '') {
            type = childType;
            curIds.push(`${id}&${type}`);
          } else {
            type = this.curChain[item.level].id;
            curIds.push(`${id}&${type}`);
          }
          const chainCheckedFlag = curIds.join('#') === payload;

          if (!this.isExistIgnore) {
            return chainCheckedFlag;
          }
          // 优先判断整个链路是否相等
          if (chainCheckedFlag) {
            return chainCheckedFlag;
          }
          if (this.ignorePathFlag || (parentChain.length < 1 && !async)) {
            return `${id}&${type}` === payload;
          }
          return false;
        });
        if (curNode && !curNode.disabled) {
          curNode.checked = true;
          curNode.disabled = true;
          this.setNodeChecked(true, curNode);
        }
      },

      async firstFetchResources () {
        // debugger
        this.isLoading = true;
        this.treeData = [];
        const params = {
          limit: this.limit,
          offset: 0,
          system_id: this.curChain[0].system_id,
          // action_system_id: this.curChain[0].system_id,
          action_system_id: this.systemParams.system_id || '',
          action_id: this.systemParams.action_id || '',
          type: this.curChain[0].id,
          // parent_type: '',
          // parent_id: '',
          ancestors: [],
          keyword: this.curKeyword
        };
        try {
          const { code, data } = await this.$store.dispatch('permApply/getResources', params);
          if (this.curSelectionCondition.length) {
            data.results = [...this.curSelectionCondition];
            data.count = data.results.length;
          }
          const totalPage = Math.ceil(data.count / this.limit);
          const isAsync = this.curChain.length > 1;
          this.treeData = data.results.map(item => {
            let checked = false;
            let disabled = false;
            let isRemote = false;
            let isExistNoCarryLimit = false;
            if (this.hasSelectedValues.length > 0) {
              let noCarryLimitData = {};
              let normalSelectedData = {};
              this.hasSelectedValues.forEach(val => {
                const curKey = `${item.id}&${params.type}`;
                if (isAsync) {
                  const curIdChain = `${curKey}#*&${this.curChain[1].id}`;
                  if (val.idChain === curIdChain) {
                    normalSelectedData = val;
                  }
                  if (val.idChain === curKey) {
                    noCarryLimitData = val;
                  }
                } else {
                  if (val.idChain === curKey) {
                    normalSelectedData = val;
                  }
                }
              });
              isExistNoCarryLimit = Object.keys(noCarryLimitData).length > 0;
              if (isExistNoCarryLimit && Object.keys(normalSelectedData).length > 0) {
                checked = true;
                disabled = normalSelectedData.disabled && noCarryLimitData.disabled;
                isRemote = disabled;
              } else {
                if (isExistNoCarryLimit || Object.keys(normalSelectedData).length > 0) {
                  checked = true;
                  disabled = normalSelectedData.disabled || noCarryLimitData.disabled;
                  isRemote = disabled;
                }
              }
            }
            const isAsyncFlag = isAsync || item.child_type !== '';
            return new Node({ ...item, checked, disabled, isRemote, isExistNoCarryLimit }, 0, isAsyncFlag);
          });
          if (totalPage > 1 && data.results.length > 0) {
            const loadItem = {
                            ...LOAD_ITEM,
                            totalPage: totalPage,
                            current: 1
            };
            this.treeData.push(new Node(loadItem, 0, isAsync, 'load'));
          }
          this.emptyData = formatCodeData(code, this.emptyData, this.treeData.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.treeData = [];
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      async handleResourceSelect (value) {
        const curSelected = this.selectList.find(item => item.id === value);
        this.curChain = _.cloneDeep(curSelected.resource_type_chain);
        this.ignorePathFlag = curSelected.ignore_iam_path;
        this.curPlaceholder = `${this.$t(`m.common['搜索']`)} ${this.curChain[0].name}`;
        if (this.limitValue.length < 1) {
          await this.firstFetchResources();
        } else {
          this.treeData = this.getLimitResourceData();
        }
      },

      handleTreeSelect (value, node) {
        const parentChain = _.cloneDeep(node.parentChain);
        let isNeedAny = false;
        // 用户组以及权限模板这里，除了子节点没有“无限制”，其他节点，包括顶级节点和中间节点都有“无限制”
        // 如果顶级节点无数据，那么也有“无限制”
        if (this.isTemplateMode) {
          // 没有中间节点以及子节点，例如 业务访问
          if (this.curChain.length === 1) {
            isNeedAny = node.async;
          } else {
            // 有父节点
            if (node.parentChain && node.parentChain.length && node.parentId) {
              isNeedAny = node.async;
            } else {
              isNeedAny = node.async;
              // 没有子节点并且已经点过展开了
              if (!node.children.length && !node.async) {
                isNeedAny = true;
                // 这里需要把 node.async 设置为 true
                // 下面的 if (node.level === 0 && !node.async) 这个逻辑需要
                node.async = isNeedAny;
              }
            }
          }
        } else {
          if (node.parentChain && node.parentChain.length && node.parentId) {
            isNeedAny = node.async;
          } else {
            isNeedAny = false;
          }
        }
        // const isNeedAny = node.async && this.isTemplateMode
        const anyData = (() => {
          const data = this.curChain[node.level + 1];
          if (data) {
            return data;
          }
          return this.curChain[this.curChain.length - 1];
        })();

        const curChainData = this.curChain[node.level];
        const chainLen = this.curChain.length;
        let id = '';
        let name = '';
        let systemId = '';

        let parentChainData = null;
        if (!curChainData) {
          id = this.curChain[chainLen - 1].id;
          name = this.curChain[chainLen - 1].name;
          systemId = this.curChain[chainLen - 1].system_id;

          parentChainData = {
            type: id,
            type_name: name,
            id: node.id,
            name: node.name,
            system_id: systemId,
            child_type: node.childType || ''
          };
        } else {
          id = curChainData.id;
          name = curChainData.name;
          systemId = curChainData.system_id;

          console.log(node);
          if (node.level === 0 && !node.async) {
            parentChainData = {
              type: this.curChain[chainLen - 1].id,
              type_name: this.curChain[chainLen - 1].name,
              id: node.id,
              name: node.name,
              system_id: this.curChain[chainLen - 1].system_id,
              child_type: node.childType || ''
            };
          } else {
            parentChainData = {
              type: id,
              type_name: name,
              id: node.id,
              name: node.name,
              system_id: systemId,
              child_type: node.childType || ''
            };
          }
        }

        parentChain.forEach((item, index) => {
          let id = '';
          if (this.curChain[index]) {
            id = this.curChain[index].id;
          } else {
            id = this.curChain[this.curChain.length - 1].id;
          }
          item.type = id;
          item.type_name = id;
        });

        parentChain.push(parentChainData);
        // parentChain.push({
        //     type: id,
        //     type_name: name,
        //     id: node.id,
        //     name: node.name,
        //     system_id: systemId,
        //     child_type: node.childType || ''
        // })

        console.log('isNeedAnyisNeedAnyisNeedAny', isNeedAny);

        if (isNeedAny) {
          parentChain.push({
            type: anyData.id,
            type_name: anyData.name,
            id: '*',
            name: `${anyData.name}: ${this.$t(`m.common['无限制']`)}`,
            system_id: anyData.system_id,
            child_type: anyData.id
          });
        }

        // 判断是否忽略路径
        // const isNeedIgnore = this.ignorePathFlag && !isNeedAny
        const params = [{
          type: id,
          name,
          // path: isNeedIgnore ? [parentChain.slice(parentChain.length - 1)] : [parentChain],
          path: [parentChain],
          paths: [parentChain]
        }];

        if (node.isExistNoCarryLimit) {
          const p = [parentChain.slice(0, parentChain.length - 1)];
          params.push({
            type: id,
            name,
            path: p,
            paths: p
          });
        }

        this.$emit('on-tree-select', value, node, params);
      },

      async handleAsyncNodes (node, index, flag) {
        window.changeAlert = true;
        const asyncItem = {
                    ...ASYNC_ITEM,
                    parentId: node.nodeId,
                    parentSyncId: node.id
        };

        const chainLen = this.curChain.length;
        const params = {
          limit: this.limit,
          offset: 0,
          // parent_id: node.id,
          ancestors: [],
          keyword: ''
        };

        if (Object.keys(this.curSearchObj).length) {
          if (node.nodeId === this.curSearchObj.parentId) {
            this.curSearchObj = {};
          }
        }

        let placeholder = '';
        let parentType = '';
        let parentData = [];
        const ancestorItem = {};

        if (node.childType !== '') {
          params.system_id = this.curChain[chainLen - 1].system_id;
          params.type = node.childType;
          // params.action_system_id = this.curChain[chainLen - 1].system_id;
          params.action_system_id = this.systemParams.system_id || '';
          params.action_id = this.systemParams.action_id || '';
          parentType = this.curChain[chainLen - 1].id;
          placeholder = this.curChain[chainLen - 1].name;
          ancestorItem.system_id = this.curChain[chainLen - 1].system_id;
          ancestorItem.type = this.curChain[chainLen - 1].id;
        } else {
          // 针对用户管理的自身递归的逻辑做的兼容处理
          const tempData = this.curChain[node.level + 1]
            ? this.curChain[node.level + 1]
            : this.curChain[chainLen - 1];
          params.system_id = tempData.system_id;
          params.type = tempData.id;
          // params.action_system_id = tempData.system_id;
          params.action_system_id = this.systemParams.system_id || '';
          params.action_id = this.systemParams.action_id || '';
          parentType = this.curChain[node.level]
            ? this.curChain[node.level].id
            : this.curChain[chainLen - 1].id;
          placeholder = tempData.name;

          ancestorItem.system_id = this.curChain[node.level].system_id;
          ancestorItem.type = this.curChain[node.level].id;
        }

        ancestorItem.id = node.id;

        if (node.parentChain.length) {
          parentData = node.parentChain.reduce((p, e) => {
            p.push({
              system_id: e.system_id,
              id: e.id,
              type: e.type
            });
            return p;
          }, []);
        }
        params.ancestors.push(...parentData, ancestorItem);

        const curLevel = node.level + 1;
        let isAsync = chainLen > (curLevel + 1);
        const parentChain = _.cloneDeep(node.parentChain);
        parentChain.push({
          name: node.name,
          id: node.id,
          type: parentType,
          system_id: node.childType !== '' ? this.curChain[chainLen - 1].system_id : this.curChain[node.level] ? this.curChain[node.level].system_id : this.curChain[chainLen - 1].system_id,
          child_type: node.childType || ''
        });

        const curTreeValue = [];
        const wholePathChains = [];
        this.limitValue.forEach(item => {
          item.path.forEach(pathItem => {
            const filterPathItem = pathItem.filter(v => v.id !== '*');
            filterPathItem.forEach(v => {
              if (v.id === node.id) {
                curTreeValue.push(item);
              }
            });
            wholePathChains.push(filterPathItem.map(_ => _.id));
          });
        });
        let nextLevelNodes = [];
        curTreeValue.forEach(item => {
          item.path.forEach(pathItem => {
            let isExistChain = false;
            const nextLevelNode = pathItem[node.level + 1];
            if (nextLevelNode) {
              const nextLevelNodeId = nextLevelNode.id;
              const curPathChain = parentChain.map(_ => _.id);
              curPathChain.push(nextLevelNodeId);
              isExistChain = wholePathChains.some(subItem => subItem.join('').indexOf(curPathChain.join('')) > -1);
            }
            if (pathItem[node.level + 1]
              && !nextLevelNodes.map(v => v.id).includes(pathItem[node.level + 1].id)
              && isExistChain
            ) {
              nextLevelNodes.push({
                                ...pathItem[node.level + 1],
                                isDisabled: pathItem[node.level + 2] && pathItem[node.level + 2].id !== '*',
                                // async: !!nextLevelNode
                                async: !!pathItem[node.level + 2]
              });
            }
          });
        });
        nextLevelNodes = nextLevelNodes.filter(item => item.id !== '*');
        if (nextLevelNodes.length > 0) {
          const childNodes = nextLevelNodes.map(item => {
            let checked = false;
            let disabled = false;
            let isRemote = false;
            let isExistNoCarryLimit = false;
            const limitAsync = item.async;
            if (this.hasSelectedValues.length > 0) {
              // 父级链路id + 当前id = 整条链路id
              const curIds = parentChain.map(v => `${v.id}&${v.type}`);
              curIds.push(`${item.id}&${params.type}`);
              const tempData = [...curIds];
              if (limitAsync) {
                curIds.push(`*&${this.curChain[curLevel + 1].id}`);
              }

              let noCarryLimitData = {};
              let normalSelectedData = {};
              this.hasSelectedValues.forEach(val => {
                if (limitAsync && val.idChain === tempData.join('#')) {
                  noCarryLimitData = val;
                } else {
                  if (!limitAsync && val.ids.length === 1 && this.ignorePathFlag && val.ids[0] === `${item.id}&${params.type}`) {
                    normalSelectedData = val;
                  } else {
                    if (val.idChain === curIds.join('#')) {
                      normalSelectedData = val;
                    }
                  }
                }
              });

              isExistNoCarryLimit = Object.keys(noCarryLimitData).length > 0;
              if (isExistNoCarryLimit && Object.keys(normalSelectedData).length > 0) {
                checked = true;
                disabled = normalSelectedData.disabled && noCarryLimitData.disabled;
                isRemote = disabled;
              } else {
                if (isExistNoCarryLimit || Object.keys(normalSelectedData).length > 0) {
                  checked = true;
                  disabled = normalSelectedData.disabled || noCarryLimitData.disabled;
                  isRemote = disabled;
                }
              }
            }

            const childItem = {
              id: item.id,
              display_name: item.name,
              parentId: node.nodeId,
              parentSyncId: node.id,
              disabled: item.isDisabled || node.checked || disabled,
              checked: checked || node.checked,
              parentChain,
              isRemote,
              isExistNoCarryLimit
            };

            return new Node(childItem, curLevel, limitAsync);
          });
          this.treeData.splice((index + 1), 0, ...childNodes);
          node.children = [...nextLevelNodes.map(
            item => new Node({ id: item.id, display_name: item.name }, curLevel, false)
          )];
          const searchItem = {
                        ...SEARCH_ITEM,
                        parentSyncId: node.id,
                        isFrontendSearch: true,
                        parentId: node.nodeId,
                        parentChain,
                        visiable: flag,
                        placeholder: `${this.$t(`m.common['搜索']`)} ${placeholder}`
          };

          const searchData = new Node(searchItem, curLevel, false, 'search');
          this.treeData.splice((index + 1), 0, searchData);
          if (flag) {
            this.$nextTick(() => {
              this.$refs.topologyRef.handleSetFocus(index + 1);
            });
          }
          this.removeAsyncNode();
          return;
        }

        // 添加加载loading
        const asyncData = new Node(asyncItem, node.level + 1, false, 'async');
        this.treeData.splice((index + 1), 0, asyncData);

        try {
          const { code, data } = await this.$store.dispatch('permApply/getResources', params);
          this.emptyData = formatCodeData(code, this.emptyData, data.results.length === 0);
          if (data.results.length < 1) {
            this.removeAsyncNode();
            node.expanded = false;
            node.async = false;
            return;
          }
          const totalPage = Math.ceil(data.count / this.limit);
          const childNodes = data.results.map(item => {
            let checked = false;
            let disabled = false;
            let isRemote = false;
            let isExistNoCarryLimit = false;
            if (!isAsync && item.child_type !== '') {
              isAsync = true;
            }
            if (this.hasSelectedValues.length > 0) {
              // 父级链路id + 当前id = 整条链路id
              const curIds = parentChain.map(v => `${v.id}&${v.type}`);
              // 取当前的请求的type
              curIds.push(`${item.id}&${params.type}`);

              const tempData = [...curIds];

              if (isAsync) {
                const nextLevelId = (() => {
                  const nextLevelData = this.curChain[curLevel + 1];
                  if (nextLevelData) {
                    return nextLevelData.id;
                  }
                  return this.curChain[chainLen - 1].id;
                })();
                curIds.push(`*&${nextLevelId}`);
              }

              let noCarryLimitData = {};
              let normalSelectedData = {};
              this.hasSelectedValues.forEach(val => {
                if (isAsync && val.idChain === tempData.join('#')) {
                  noCarryLimitData = val;
                } else {
                  if (!isAsync && val.ids.length === 1 && this.ignorePathFlag && val.ids[0] === `${item.id}&${params.type}`) {
                    normalSelectedData = val;
                  } else {
                    if (val.idChain === curIds.join('#')) {
                      normalSelectedData = val;
                    }
                  }
                }
              });

              isExistNoCarryLimit = Object.keys(noCarryLimitData).length > 0;
              if (isExistNoCarryLimit && Object.keys(normalSelectedData).length > 0) {
                checked = true;
                disabled = normalSelectedData.disabled && noCarryLimitData.disabled;
                isRemote = disabled;
              } else {
                if (isExistNoCarryLimit || Object.keys(normalSelectedData).length > 0) {
                  checked = true;
                  disabled = normalSelectedData.disabled || noCarryLimitData.disabled;
                  isRemote = disabled;
                }
              }
            }

            const childItem = {
                            ...item,
                            parentId: node.nodeId,
                            parentSyncId: node.id,
                            disabled: node.checked || disabled,
                            checked: checked || node.checked,
                            parentChain,
                            isRemote,
                            isExistNoCarryLimit
            };

            const isAsyncFlag = isAsync || item.child_type !== '';
            return new Node(childItem, curLevel, isAsyncFlag);
          });
          this.treeData.splice((index + 1), 0, ...childNodes);
          node.children = [...data.results.map(item => new Node(item, curLevel, false))];
          if (totalPage > 1) {
            const loadItem = {
                            ...LOAD_ITEM,
                            totalPage: totalPage,
                            current: 1,
                            parentSyncId: node.id,
                            parentId: node.nodeId,
                            parentChain
            };
            const loadData = new Node(loadItem, curLevel, isAsync, 'load');
            this.treeData.splice((index + childNodes.length + 1), 0, loadData);
            node.children.push(new Node(loadItem, curLevel, false, 'load'));
          }

          const searchItem = {
                        ...SEARCH_ITEM,
                        totalPage: totalPage,
                        parentSyncId: node.id,
                        parentId: node.nodeId,
                        parentChain,
                        visiable: flag,
                        placeholder: `${this.$t(`m.common['搜索']`)} ${placeholder}`
          };

          const searchData = new Node(searchItem, curLevel, false, 'search');
          this.treeData.splice((index + 1), 0, searchData);
          if (flag) {
            this.$nextTick(() => {
              this.$refs.topologyRef.handleSetFocus(index + 1);
            });
          }
          this.removeAsyncNode();
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.removeAsyncNode();
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        }
      },

      removeAsyncNode () {
        const index = this.treeData.findIndex(item => item.type === 'async');
        if (index > -1) this.treeData.splice(index, 1);
      },

      async handleLoadMore (node, index) {
        window.changeAlert = true;
        node.current = node.current + 1;
        node.loadingMore = true;

        const chainLen = this.curChain.length;
        let keyword = this.curKeyword;
        if (Object.keys(this.curSearchObj).length) {
          if (node.parentId === this.curSearchObj.parentId) {
            keyword = this.curSearchObj.value;
          }
        }
        const params = {
          limit: this.limit,
          offset: this.limit * (node.current - 1),
          ancestors: [],
          // parent_id: node.level > 0 ? node.parentSyncId : '',
          keyword
        };

        if (node.level > chainLen - 1) {
          params.system_id = this.curChain[chainLen - 1].system_id;
          params.type = this.curChain[chainLen - 1].id;
          // params.action_system_id = this.curChain[chainLen - 1].system_id;
          params.action_system_id = this.systemParams.system_id || '';
          params.action_id = this.systemParams.action_id || '';
        } else {
          params.system_id = this.curChain[node.level].system_id;
          params.type = this.curChain[node.level].id;
          // params.action_system_id = this.curChain[node.level].system_id;
          params.action_system_id = this.systemParams.system_id || '';
          params.action_id = this.systemParams.action_id || '';
        }
        if (node.parentChain.length) {
          const parentData = node.parentChain.reduce((p, e) => {
            p.push({
              system_id: e.system_id,
              id: e.id,
              type: e.type
            });
            return p;
          }, []);
          params.ancestors.push(...parentData);
        }
        try {
          const { code, data } = await this.$store.dispatch('permApply/getResources', params);
          let isAsync = this.curChain.length > (node.level + 1);
          const loadNodes = data.results.map(item => {
            let tempItem = _.cloneDeep(item);

            let checked = false;
            let disabled = false;
            let isRemote = false;
            let isExistNoCarryLimit = false;
            if (!isAsync && tempItem.child_type !== '') {
              isAsync = true;
            }
            if (this.hasSelectedValues.length > 0) {
              // 父级链路id + 当前id = 整条链路id
              const curIds = node.parentChain.map(v => `${v.id}&${v.type}`);
              // 取当前的请求的type
              curIds.push(`${item.id}&${params.type}`);

              const tempData = [...curIds];

              if (isAsync) {
                const nextLevelId = (() => {
                  const nextLevelData = this.curChain[node.level + 1];
                  if (nextLevelData) {
                    return nextLevelData.id;
                  }
                  return this.curChain[chainLen - 1].id;
                })();
                curIds.push(`*&${nextLevelId}`);
              }

              let noCarryLimitData = {};
              let normalSelectedData = {};
              this.hasSelectedValues.forEach(val => {
                if (isAsync && val.idChain === tempData.join('#')) {
                  noCarryLimitData = val;
                } else {
                  if (!isAsync && val.ids.length === 1 && this.ignorePathFlag && val.ids[0] === `${item.id}&${params.type}`) {
                    normalSelectedData = val;
                  } else {
                    if (val.idChain === curIds.join('#')) {
                      normalSelectedData = val;
                    }
                  }
                }
              });

              isExistNoCarryLimit = Object.keys(noCarryLimitData).length > 0;
              if (isExistNoCarryLimit && Object.keys(normalSelectedData).length > 0) {
                checked = true;
                disabled = normalSelectedData.disabled && noCarryLimitData.disabled;
                isRemote = disabled;
              } else {
                if (isExistNoCarryLimit || Object.keys(normalSelectedData).length > 0) {
                  checked = true;
                  disabled = normalSelectedData.disabled || noCarryLimitData.disabled;
                  isRemote = disabled;
                }
              }
            }

            if (node.level > 0) {
              const parentData = this.treeData.find(sub => sub.nodeId === node.parentId);
              tempItem = {
                                ...item,
                                parentId: node.parentId,
                                parentSyncId: node.id,
                                disabled: parentData.checked || disabled,
                                checked: checked || parentData.checked,
                                parentChain: _.cloneDeep(node.parentChain),
                                isRemote,
                                isExistNoCarryLimit
              };
            } else {
              tempItem.checked = checked;
              tempItem.disabled = disabled;
              tempItem.isExistNoCarryLimit = isExistNoCarryLimit;
            }

            const isAsyncFlag = isAsync || item.child_type !== '';
            return new Node(tempItem, node.level, isAsyncFlag);
          });
          if (node.current >= node.totalPage) {
            this.treeData.splice(index, 1, ...loadNodes);
          } else {
            this.treeData.splice(index, 0, ...loadNodes);
          }
          // 将新加载的节点push到父级点的children中
          if (node.level > 0) {
            const parentNode = this.treeData.find(item => item.nodeId === node.parentId);
            if (parentNode.children.length > 0) {
              parentNode.children.push(...loadNodes);
            }
          }
          this.emptyData = formatCodeData(code, this.emptyData, data.results.length === 0);
        } catch (e) {
          console.error(e);
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          node.loadingMore = false;
        }
      }
    }
  };
</script>
<style lang="postcss">
    .iam-choose-ip {
        height: 100%;
        .topology-wrapper {
            height: calc(100% - 74px);
            .topology-tree-wrapper {
                position: relative;
                height: 100%;
                .empty-wrapper {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    img {
                        width: 120px;
                    }
                }
                .bk-loading {
                    background: #fafbfd !important;
                }
            }
        }
    }
</style>
