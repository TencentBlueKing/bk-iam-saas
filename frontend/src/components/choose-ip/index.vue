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
            <!-- <iam-svg />
                        <section class="search-text-wrapper" v-if="searchDisplayText !== ''">
                            {{ searchDisplayText }}
                        </section> -->
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
  import ResourceSelect from './resource-select';
  import TopologyInput from './topology-input';
  import TopologyTree from './topology-tree';

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
    '0': il8n('common', '搜索结果为空'),
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
      resourceValue: {
        type: Boolean,
        default: () => false
      },
      systemParams: {
        type: Object,
        default: () => {
          return {
            action_id: ''
          };
        }
      }
    },
    data () {
      return {
        isLoading: false,
        limit: 100,
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
        searchDisplayText: '',
        resourceNeedDisable: false,
        resourceNode: {},
        // 空数据或异常数据配置项
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        emptyTreeData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
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
          if (value) {
            this.curChain = _.cloneDeep(this.selectList[0].resource_type_chain);
            this.ignorePathFlag = this.selectList[0].ignore_iam_path;
            this.isExistIgnore = this.selectList.some(item => item.ignore_iam_path);
            this.curPlaceholder = `${this.$t(`m.common['搜索']`)} ${this.curChain[0].name}`;
            this.firstFetchResources();
          }
        },
        immediate: true
      }
    },
    methods: {
      handleSearch (payload) {
        this.curKeyword = payload;
        if (this.isFilter && payload === '') {
          this.isFilter = false;
        } else {
          this.isFilter = true;
        }
        this.emptyData.tipType = 'search';
        this.firstFetchResources();
      },

      handleEmptyRefresh () {
        this.firstFetchResources();
      },

      handleEmptyClear () {
        this.$refs.headerInput.value = '';
        this.emptyData.tipType = '';
        this.firstFetchResources();
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

        const searchLoadingItem = {
                    ...SEARCH_LOAD_ITEM,
                    parentId: node.parentId,
                    parentSyncId: node.id,
                    parentChain: _.cloneDeep(node.parentChain),
                    level: node.level
        };
        const searchLoadingData = new Node(searchLoadingItem, node.level, false, 'search-loading');
        this.treeData.splice((index + 1), 0, searchLoadingData);

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
          const parentNode = this.treeData.find(item => item.nodeId === node.parentId);
          if (parentNode || !parentNode.children) {
            parentNode.children = [];
          }
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

          if (this.resourceValue) {
            this.handlerResourceNode();
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
          // const curIds = parentChain.map(v => v.id)
          const curIds = parentChain.map(v => `${v.id}&${v.type}`);
          let type = '';
          // curIds.push(id)
          if (childType !== '') {
            type = childType;
            curIds.push(`${id}&${type}`);
          } else {
            type = this.curChain[item.level].id;
            curIds.push(`${id}&${type}`);
          }

          // curIds.push(`${id}&${type}`)

          // const chainCheckedFlag = curIds.join('&') === payload
          const chainCheckedFlag = curIds.join('#') === payload;

          // (parentChain.length > 0 && !async)
          if (!this.isExistIgnore) {
            return chainCheckedFlag;
          }
          // 优先判断整个链路是否相等
          if (chainCheckedFlag) {
            return chainCheckedFlag;
          }
          if (this.ignorePathFlag || (parentChain.length < 1 && !async)) {
            // return item.id === payload
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
        this.isLoading = true;
        this.treeData = [];
        const params = {
          limit: this.limit,
          offset: 0,
          system_id: this.curChain[0].system_id,
          action_system_id: this.curChain[0].system_id,
          action_id: this.systemParams.action_id || '',
          type: this.curChain[0].id,
          // parent_type: '',
          // parent_id: '',
          ancestors: [],
          keyword: this.curKeyword
        };
        try {
          const { code, data } = await this.$store.dispatch('permApply/getResources', params);
          this.emptyData = formatCodeData(code, this.emptyData, data.results.length === 0);
          if (data.results.length < 1) {
            this.searchDisplayText = RESULT_TIP[code];
            return;
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

          if (this.resourceValue) {
            this.handlerResourceNode();
          }
        } catch (e) {
          console.error(e);
          if (!ERROR_CODE_LIST.includes(e.code)) {
            this.messageAdvancedError(e);
          }
          const message = e.code !== 1902206 ? RESULT_TIP[e.code] : e.message;
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.searchDisplayText = message;
        } finally {
          this.isLoading = false;
        }
      },

      async handleResourceSelect (value) {
        const curSelected = this.selectList.find(item => item.id === value);
        this.curChain = _.cloneDeep(curSelected.resource_type_chain);
        this.ignorePathFlag = curSelected.ignore_iam_path;
        this.curPlaceholder = `${this.$t(`m.common['搜索']`)} ${this.curChain[0].name}`;
        await this.firstFetchResources();
      },

      handleTreeSelect (value, node) {
        const parentChain = _.cloneDeep(node.parentChain);
        // const isNeedAny = node.level < this.curChain.length - 1
        const isNeedAny = node.async;
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
        if (!curChainData) {
          id = this.curChain[chainLen - 1].id;
          name = this.curChain[chainLen - 1].name;
          systemId = this.curChain[chainLen - 1].system_id;
        } else {
          id = curChainData.id;
          name = curChainData.name;
          systemId = curChainData.system_id;
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
        parentChain.push({
          type: id,
          type_name: name,
          id: node.id,
          name: node.name,
          system_id: systemId,
          child_type: node.childType || ''
        });
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
        // 针对资源权限特殊处理
        if (this.resourceValue) {
          if (value) {
            this.treeData.forEach(item => {
              if (item.id !== node.id) {
                item.disabled = true;
              }
            });
            this.resourceNode = node;
            this.resourceNeedDisable = true;
          } else {
            this.treeData.forEach(item => {
              item.disabled = false;
            });
            this.resourceNode = {};
            this.resourceNeedDisable = false;
          }
        }
      },

      // 针对资源权限特殊处理
      handlerResourceNode () {
        if (this.treeData.some(item => item.checked)) {
          this.treeData.forEach(item => {
            item.disabled = !item.checked;
          });
        }
      },

      async handleAsyncNodes (node, index, flag) {
        console.log('handleAsyncNodes', node);
        window.changeAlert = true;
        const asyncItem = {
                    ...ASYNC_ITEM,
                    parentId: node.nodeId,
                    parentSyncId: node.id
        };

        const asyncData = new Node(asyncItem, node.level + 1, false, 'async');
        this.treeData.splice((index + 1), 0, asyncData);

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
          const isExistNextChain = !!this.curChain[node.level + 1];
          const ExistSystemId = isExistNextChain
            ? this.curChain[node.level + 1].system_id
            : this.curChain[chainLen - 1].system_id;
          params.system_id = ExistSystemId;
          // params.action_system_id = ExistSystemId;
          params.action_system_id = this.systemParams.system_id || '';
          params.action_id = this.systemParams.action_id || '';

          params.type = isExistNextChain
            ? this.curChain[node.level + 1].id
            : this.curChain[chainLen - 1].id;

          parentType = this.curChain[node.level].id;

          placeholder = isExistNextChain
            ? this.curChain[node.level + 1].name
            : this.curChain[chainLen - 1].name;
                    
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

        try {
          const { code, data } = await this.$store.dispatch('permApply/getResources', params);
          this.emptyData = formatCodeData(code, this.emptyData, data.results.length === 0);
          if (data.results.length < 1) {
            this.removeAsyncNode();
            node.expanded = false;
            node.async = false;
            return;
          }
          const curLevel = node.level + 1;
          const totalPage = Math.ceil(data.count / this.limit);
          let isAsync = this.curChain.length > (curLevel + 1);
          const parentChain = _.cloneDeep(node.parentChain);
          parentChain.push({
            name: node.name,
            id: node.id,
            type: parentType,
            system_id: node.childType !== '' ? this.curChain[chainLen - 1].system_id : this.curChain[node.level].system_id,
            child_type: node.childType || ''
          });
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
        console.log('handleLoadMore', node, index);
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
          // params.parent_type = this.curChain[chainLen - 1].id || '';
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

          // 针对资源权限特殊处理
          if (this.resourceValue && this.resourceNeedDisable) {
            this.treeData.forEach(item => {
              if (item.id !== this.resourceNode.id) {
                item.disabled = true;
              }
            });
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
                    /* .search-text-wrapper {
                        position: relative;
                        top: -20px;
                        font-size: 12px;
                        color: #c4c6cc;
                        word-break: break-all;
                        text-align: center;
                    } */
                }
                .bk-loading {
                    background: #fafbfd !important;
                }
            }
        }
    }
</style>
