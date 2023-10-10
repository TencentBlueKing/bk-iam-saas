<template>
  <div :class="['iam-topology-tree', { 'iam-topology-tree-only': isOnlyLevel }, { 'bk-has-border-tree': isBorder }]">
    <!-- eslint-disable max-len -->
    <!-- <div class="ghost-wrapper" :style="ghostStyle" v-if="!isOnlyLevel"></div> -->
    <div class="render-wrapper" ref="content">
      <template v-if="isOnlyLevel">
        <bk-table
          ref="topologyTableRef"
          size="small"
          data-test-id="topology_tree_group"
          ext-cls="topology-tree-table"
          :header-border="false"
          :outer-border="false"
          :data="renderTopologyData"
          @select="handleSelectChange"
          @select-all="handleSelectAllChange"
        >
          <bk-table-column type="selection" align="center" :selectable="setDefaultSelect" />
          <bk-table-column :label="formatPlaceHolder('table')">
            <template slot-scope="{ row }">
              {{ row.name }}
            </template>
          </bk-table-column>
          <template slot="empty">
            <ExceptionEmpty />
          </template>
        </bk-table>
        <template v-if="pagination.count > 0">
          <bk-pagination
            size="small"
            align="right"
            ext-cls="topology-tree-pagination-cls"
            :small="true"
            :show-total-count="true"
            :show-limit="false"
            :current.sync="pagination.current"
            :count="pagination.count"
            :limit="pagination.limit"
            @change="handlePageChange"
          />
        </template>
      </template>
      <template v-else>
        <div class="multiple-topology-tree">
          <div class="multiple-topology-tree-left" :style="formatLeftStyle">
            <topology-input
              ref="topologyInputRef"
              :is-filter="isFilter"
              :placeholder="curPlaceholder"
              @on-search="handleSearch"
            />
            <div class="multiple-topology-tree-left-content">
              <template>
                <div
                  v-for="(item, index) in allData"
                  :key="item.nodeId"
                  :class="[
                    'node-item',
                    { 'node-item-active': item.nodeId === selectNodeData.nodeId && item.type === 'node' },
                    { 'load-more-node': formatLoadMore(item) },
                    { 'search-node': item.type === 'search' },
                    { 'can-hover': item.type === 'node' && !item.loading }
                  ]"
                  :style="getNodeStyle(item)"
                  @click.stop="handleSelectNode(item, index)"
                >
                  <template v-if="item.type === 'node' && item.level < curChain.length - 1">
                    <Icon
                      v-if="!isTwoLevel"
                      bk
                      :type="item.expanded ? 'down-shape' : 'right-shape'"
                      :class="['arrow-icon', { 'is-disabled': getExpandedDisabled(index) || isExistAsync(item) }]"
                      @click.stop="expandNode(item, index)"
                    />
                    <div class="node-radio" @click.stop>
                      <bk-checkbox
                        :true-value="true"
                        :false-value="false"
                        :disabled="item.disabled"
                        v-model="item.checked"
                        ext-cls="iam-topology-title-cls"
                        :title="`ID: ${item.id}`"
                        data-test-id="topology_checkbox_chooseip"
                        @change="handleNodeChange(...arguments, item, index)"
                      >
                      </bk-checkbox>
                      <span
                        class="tree-node-name single-hide"
                        :style="dragDynamicWidth(item)"
                        :title="item.name"
                        @click.stop="handleSelectNode(item, index)"
                      >
                        {{ item.name }}
                      </span>
                    </div>
                  </template>
                  <template v-else-if="formatLoadMore(item)">
                    <div class="load-more-wrapper">
                      <div
                        :class="[
                          'load-item',
                          { 'loading-more': item.loadingMore },
                          { normal: !item.loadingMore && !isExistNodeLoadMore },
                          { 'exist-load-more': isExistNodeLoadMore }
                        ]"
                        @click.stop="loadMore(item, index)"
                      >
                        <template v-if="!item.loadingMore">
                          {{ item.name }}
                        </template>
                        <template v-else>
                          <div
                            class="node-load-more-loading"
                            v-bkloading="{ isLoading: item.loadingMore, opacity: 1, theme: 'primary', size: 'mini' }"
                          ></div>
                        </template>
                      </div>
                    </div>
                  </template>
                  <template v-else-if="item.type === 'search-empty' && curChain[curChain.length - 1] === item.level">
                    <div class="search-empty-wrapper">
                      <ExceptionEmpty
                        :type="item.name === $t(`m.common['搜索结果为空']`) ? 'search-empty' : 500"
                        :tip-type="item.name === $t(`m.common['搜索结果为空']`) ? 'search' : 'refresh'"
                        :empty-text="item.name === $t(`m.common['搜索结果为空']`) ? item.name : '数据不存在'"
                        @on-clear="handleEmptyClear(...arguments, item, index)"
                        @on-refresh="handleEmptyRefresh(...arguments, item, index)"
                      />
                    </div>
                  </template>
                  <!-- <template v-else-if="item.type === 'search-loading'">
                  <div
                    class="search-loading-wrapper"
                    v-bkloading="{ isLoading: true, opacity: 1, theme: 'primary', size: 'mini' }"
                  ></div>
                </template>
                <div class="node-loading" v-else-if="item.type === 'async'">
                  <spin-loading ext-cls="loading" />
                  <span class="loading-text">{{ $t(`m.common['加载中']`) }}</span>
                </div>
                <template v-else>
                  <topology-input
                    :ref="`topologyInputRef${index}`"
                    :scene="'tree'"
                    :placeholder="item.placeholder"
                    :is-filter="item.isFilter"
                    :disabled="getSearchDisabled(item)"
                    @on-search="handleSearch(...arguments, item, index)"
                  />
                </template> -->
                </div>
              </template>
              <template v-if="!visiableData.length">
                <ExceptionEmpty
                  :type="item.name === $t(`m.common['搜索结果为空']`) ? 'search-empty' : 500"
                  :tip-type="item.name === $t(`m.common['搜索结果为空']`) ? 'search' : 'refresh'"
                  :empty-text="item.name === $t(`m.common['搜索结果为空']`) ? item.name : '数据不存在'"
                  @on-clear="handleEmptyClear(...arguments, item, index)"
                  @on-refresh="handleEmptyRefresh(...arguments, item, index)"
                />
              </template>
            </div>
          </div>
          <div class="multiple-topology-tree-right">
            <topology-input
              :ref="`topologyInputRef${selectNodeDataIndex}`"
              :placeholder="formatPlaceHolder('input') || ''"
              :is-filter="selectNodeData.isFilter || false"
              :disabled="getSearchDisabled(selectNodeData)"
              @on-search="handleTableSearch(...arguments, selectNodeData, selectNodeDataIndex)"
            />
            <div class="multiple-topology-tree-right-content">
              <bk-table
                ref="topologyTableRef"
                size="small"
                data-test-id="topology_tree_group"
                ext-cls="topology-tree-table"
                :header-border="false"
                :outer-border="false"
                :data="renderTopologyData"
                @select="handleSelectChange"
                @select-all="handleSelectAllChange"
                v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
              >
                <bk-table-column type="selection" align="center" :selectable="setDefaultSelect" />
                <bk-table-column :label="formatPlaceHolder('table')">
                  <template slot-scope="{ row }">
                    <span :title="`ID: ${row.id}`">{{ row.name }}</span>
                  </template>
                </bk-table-column>
                <template slot="empty">
                  <ExceptionEmpty
                    v-if="!tableLoading"
                    :type="formatTableEmpty('type', tableEmptyData)"
                    :tip-type="formatTableEmpty('tipType', tableEmptyData)"
                    :empty-text="formatTableEmpty('emptyText', tableEmptyData)"
                    @on-clear="handleEmptyClear(...arguments, selectNodeData, selectNodeDataIndex)"
                    @on-refresh="handleEmptyRefresh(...arguments, selectNodeData, selectNodeDataIndex)"
                  />
                </template>
              </bk-table>
              <template v-if="subPagination.count > 0">
                <bk-pagination
                  size="small"
                  align="right"
                  ext-cls="topology-tree-pagination-cls"
                  :small="true"
                  :show-total-count="true"
                  :show-limit="false"
                  :current.sync="subPagination.current"
                  :count="subPagination.count"
                  :limit="subPagination.limit"
                  @change="handleTablePageChange"
                />
              </template>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
  import _ from 'lodash';
  import TopologyInput from './topology-input';

  export default {
    name: '',
    inject: ['getDragDynamicWidth'],
    components: {
      TopologyInput
    },
    props: {
      // 所有数据
      allData: {
        type: Array,
        default: () => []
      },
      allTableData: {
        type: Array,
        default: () => []
      },
      searchValue: {
        type: Array,
        default: () => []
      },
      curChain: {
        type: Array,
        default: () => []
      },
      // 每个节点的高度
      itemHeight: {
        type: Number,
        default: 32
      },
      // 子节点左侧偏移的基础值
      leftBaseIndent: {
        type: Number,
        default: 12
      },
      resourceTotal: {
        type: Number
      },
      subResourceTotal: {
        type: Number,
        default: 0
      },
      isBorder: {
        type: Boolean,
        default: false
      },
      isFilter: {
        type: Boolean,
        default: false
      },
      curPlaceholder: {
        type: String,
        default: ''
      },
      emptyData: {
        type: Object,
        default: () => {
          return {
            type: '',
            text: '',
            tip: '',
            tipType: ''
          };
        }
      },
      curTableData: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        startIndex: 0,
        endIndex: 0,
        isShiftBeingPress: false,
        pressIndex: -1,
        pressLevels: [],
        levelIndex: -1, // 获取当前搜索焦点的位置索引
        offsetWidth: 180,
        tableLoading: true,
        pagination: {
          current: 1,
          limit: 100,
          count: 0,
          showLimit: false,
          small: true
        },
        subPagination: {
          current: 1,
          limit: 100,
          count: 0,
          showLimit: false,
          small: true
        },
        emptyTableData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        tableEmptyData: {},
        renderTopologyData: [],
        checkedNodeIdList: [],
        currentSelectedNode: [],
        selectNodeData: {},
        selectNodeDataIndex: -1,
        curSearchMode: ''
      };
    },
    computed: {
      ghostStyle () {
        return {
          height: this.visiableData.length * this.itemHeight + 'px'
        };
      },
      // allData 中 visiable 为 true 的数据，visiable 属性辅助设置展开收起的
      // 当父节点收起时，子节点的 visiable 为 false
      visiableData () {
        return this.allData.filter((item) => item.visiable);
      },
      // 返回只有一层数据的排版
      isOnlyLevel () {
        return this.visiableData.every((item) => !item.async && item.level === 0) && this.curChain.length < 2;
      },
      // 返回两层数据的排版
      isTwoLevel () {
        return this.visiableData.every((item) => this.curChain.length === 2 && this.curChain.length > item.level);
      },
      // 页面渲染的数据
      renderData () {
        // 渲染 visiable 为 true 并且在可视区的，这里要注意，必须要先 filter visiable 然后 slice，不能反过来
        return this.visiableData.slice(this.startIndex, this.endIndex);
      },
      isExistNodeLoadMore () {
        return this.allData.some((item) => item.id === -1 && item.loadingMore);
      },
      dragDynamicWidth () {
        return (payload) => {
          // const offsetWidth = this.getDragDynamicWidth() > 600 ? 560 + this.getDragDynamicWidth() - 600 : 560;
          const offsetWidth = this.getDragDynamicWidth
            ? this.getDragDynamicWidth() - 500
            : 460 + this.getDragDynamicWidth() - 500;
          const isSameLevelExistSync = this.allData
            .filter((item) => item.level === payload.level)
            .some((item) => item.type === 'node' && item.async);
          const flag = !payload.async && isSameLevelExistSync;
          const asyncIconWidth = 5;
          const asyncLevelWidth = 30;
          const searchIconWidth = 12;
          if (!payload.level) {
            if (flag) {
              return {
                maxWidth: `${offsetWidth - this.leftBaseIndent + asyncIconWidth}px`
              };
            }
            if (payload.loading) {
              return {
                maxWidth: `${offsetWidth - 20}px`
              };
            }
            if (payload.async) {
              return {
                maxWidth: `${offsetWidth - asyncLevelWidth - searchIconWidth}px`
              };
            }
            return {
              maxWidth: `${offsetWidth}px`
            };
          }
          if (payload.async) {
            return {
              maxWidth: offsetWidth - (payload.level + 1) * this.leftBaseIndent - asyncLevelWidth - searchIconWidth + 'px'
            };
          }
          if (isSameLevelExistSync && ['search', 'search-empty'].includes(payload.type)) {
            return {
              maxWidth: offsetWidth - (payload.level + 1) * this.leftBaseIndent + 'px'
            };
          }
          if (flag) {
            return {
              maxWidth: offsetWidth - ((payload.level + 1) * this.leftBaseIndent + asyncIconWidth) + 'px'
            };
          }
          return {
            maxWidth: offsetWidth - ((payload.level + 1) * this.leftBaseIndent + 14) + 'px'
          };
        };
      },
      formatPlaceHolder () {
        return (payload) => {
          const typeMap = {
            input: () => {
              return this.$t(`m.info['搜索动态key值']`, {
                value: this.curChain.length ? this.curChain[this.curChain.length - 1].name : ''
              });
            },
            table: () => {
              return this.curChain.length ? this.curChain[this.curChain.length - 1].name : '';
            }
          };
          return typeMap[payload]();
        };
      },
      formatLeftStyle () {
        return {
          width: this.getDragDynamicWidth ? `${this.getDragDynamicWidth() - 200}px` : '600px'
        };
      },
      formatLoadMore () {
        return (payload) => {
          return payload.type === 'load' && payload.level < this.curChain.length - 1;
        };
      },
      formatTableEmpty () {
        return (mode, payload) => {
          const typeMap = {
            type: () => {
              if (Object.keys(payload).length) {
                if (payload.name === this.$t(`m.common['搜索结果为空']`)) {
                  return 'search-empty';
                }
                return 500;
              } else {
                return 'empty';
              }
            },
            tipType: () => {
              if (Object.keys(payload).length) {
                if (payload.name === this.$t(`m.common['搜索结果为空']`)) {
                  return 'search';
                }
                return 'refresh';
              } else {
                return '';
              }
            },
            emptyText: () => {
              if (Object.keys(payload).length) {
                if (payload.name === this.$t(`m.common['搜索结果为空']`)) {
                  return payload.name;
                }
                return '数据不存在';
              } else {
                return '暂无数据';
              }
            }
          };
          return typeMap[mode]();
        };
      }
    },
    watch: {
      pressIndex (newVal, oldVal) {
        if (newVal > -1 && oldVal > -1 && [...new Set(this.pressLevels)].length === 1) {
          const indexs = [...new Set([newVal, oldVal].sort())];
          if (indexs.length > 1 && indexs[1] - indexs[0] > 1) {
            for (let i = indexs[0] + 1; i < indexs[1]; i++) {
              const node = this.allData[i];
              node.checked = true;
              this.handleNodeChecked(true, node);
              this.$emit('on-select', true, node);
            }
          }
        }
      },
      resourceTotal: {
        handler (value) {
          this.pagination = Object.assign(this.pagination, { count: value });
        },
        immediate: true
      },
      subResourceTotal: {
        handler (value) {
          this.subPagination = Object.assign(this.subPagination, { count: value });
        },
        immediate: true
      },
      allData: {
        handler (value) {
          this.fetchLevelTree(value);
        },
        immediate: true
      },
      selectNodeDataIndex: {
        handler (newValue, oldValue) {
          if (newValue !== oldValue) {
            this.subPagination = Object.assign(this.subPagination, { current: 1 });
          }
          if (newValue === -1 && !this.isOnlyLevel) {
            this.handleSelectNode(this.visiableData[0], 0);
          }
        },
        immediate: true
      },
      emptyData: {
        handler (value) {
          if (this.curSearchMode === 'table') {
            this.emptyTableData = Object.assign({}, value);
          }
        },
        immediate: true
      }
    },
    mounted () {
      // 最大高度已固定
      const maxHeight = 256;
      // this.endIndex = Math.ceil(this.$el.clientHeight / this.itemHeight)
      this.endIndex = Math.ceil(maxHeight / this.itemHeight);
      document.addEventListener('keyup', this.handleKeyup);
      document.addEventListener('keydown', this.handleKeydown);
      this.$once('hook:beforeDestroy', () => {
        document.removeEventListener('keyup', this.handleKeyup);
        document.removeEventListener('keydown', this.handleKeydown);
      });
    },
    methods: {
      fetchLevelTree (value) {
        if (value.length) {
          if (this.isOnlyLevel) {
            this.renderTopologyData = value.filter((item) => item.type === 'node');
            this.checkedNodeIdList = this.renderTopologyData
              .filter((item) => item.checked)
              .map((v) => `${v.nodeId}&${v.id}`);
            this.$nextTick(() => {
              this.renderTopologyData.forEach((item) => {
                this.$refs.topologyTableRef
                  && this.$refs.topologyTableRef.toggleRowSelection(
                    item,
                    this.checkedNodeIdList.includes(`${item.nodeId}&${item.id}`)
                  );
              });
            });
          } else {
            if (Object.keys(this.selectNodeData).length) {
              const curNode = value.find(
                (item) => `${item.nodeId}&${item.id}` === `${this.selectNodeData.nodeId}&${this.selectNodeData.id}`
              );
              if (curNode) {
                const list = [...(curNode.children || [])].filter((item) => item.type === 'node');
                console.log(curNode.current, list, 564564);
                curNode.current = this.subPagination.current;
                this.renderTopologyData = this.getDataByPage(curNode.current, list);
                this.checkedNodeIdList = value
                  .filter((item) => item.checked && item.parentId === this.selectNodeData.nodeId)
                  .map((v) => `${this.selectNodeData.nodeId}&${v.id}`);
                if (!curNode.children.length) {
                  const searchEmptyData = value.find((item) => item.type === 'search-empty');
                  if (searchEmptyData) {
                    this.tableEmptyData = Object.assign({}, searchEmptyData);
                  }
                }
                this.$nextTick(() => {
                  this.renderTopologyData.forEach((item) => {
                    this.$refs.topologyTableRef
                      && this.$refs.topologyTableRef.toggleRowSelection(
                        item,
                        this.checkedNodeIdList.includes(`${this.selectNodeData.nodeId}&${item.id}`)
                      );
                  });
                });
              }
            }
          }
        }
      },

      setDefaultSelect (payload) {
        const allData = this.allData.filter((item) => item.disabled && item.type === 'node').map((item) => item.id);
        return !allData.includes(payload.id);
      },

      handleKeyup ($event) {
        if ($event.key === 'Shift') {
          this.isShiftBeingPress = false;
          this.pressIndex = -1;
          this.pressLevels = [];
        }
      },

      handleKeydown ($event) {
        if ($event.key === 'Shift') {
          this.isShiftBeingPress = true;
        }
      },

      loadMore (node, index) {
        if (this.isExistNodeLoadMore) {
          return;
        }
        this.$emit('on-load-more', node, index);
      },

      isExistAsync (payload) {
        // (asyncNode && asyncNode.parentId === payload.nodeId)
        const asyncNode = this.allData.find((item) => item.type === 'async');
        // if (!asyncNode) {
        //     return false
        // }
        return !!asyncNode;
      },

      getExpandedDisabled (index) {
        const data = this.allData[index + 2];
        if (data && data.hasOwnProperty('type') && data.type === 'search-loading') {
          return true;
        }
        return false;
      },

      handleSetFocus (index) {
        this.levelIndex = index;
        this.$refs[`topologyInputRef${index}`][0] && this.$refs[`topologyInputRef${index}`][0].handleSetFocus();
      },

      getSearchDisabled (item) {
        return this.allData.some((item) => item.type === 'search-loading');
      },

      handleSearch (value) {
        this.curSearchMode = 'tree';
        this.$emit('on-search', value);
      },

      handleTableSearch (value, node, index) {
        this.curSearchMode = 'table';
        const curNode = this.allData.find((item) => item.parentId === node.nodeId);
        if (curNode) {
          this.subPagination = Object.assign(this.subPagination, { current: 1, count: 0 });
          this.$emit('on-table-search', { value, node: curNode, index });
        }
      },

      handleEmptyClear (payload, node, index) {
        this.$nextTick(() => {
          const typeMap = {
            table: () => {
              this.$refs[`topologyInputRef${index}`].value = '';
              this.handleTableSearch('', node, index);
            },
            tree: () => {
              this.$refs[`topologyInputRef${index}`][0].value = '';
              this.handleSearch('', node, index);
            }
          };
          typeMap[this.curSearchMode]();
        });
      },

      handleEmptyRefresh (payload, node, index) {
        this.$nextTick(() => {
          const typeMap = {
            table: () => {
              this.$refs[`topologyInputRef${index}`].value = '';
              this.handleTableSearch('', node, index);
            },
            tree: () => {
              this.$refs[`topologyInputRef${index}`][0].value = '';
              this.handleSearch('', node, index);
            }
          };
          typeMap[this.curSearchMode]();
        });
      },

      handleOpenSearch (node, index) {
        console.log(node, index);
        if (
          (this.allData[index + 1] && this.allData[index + 1].type === 'search' && this.allData[index + 1].visiable)
          || this.isExistAsync(node)
        ) {
          return;
        }
        node.expanded = true;
        if (node.children && node.children.length) {
          const children = this.allData.filter((item) => item.parentId === node.nodeId);
          children.forEach((child) => {
            child.visiable = node.expanded;
            if (child.async && !node.expanded) {
              this.collapseNode(child);
            }
          });
          this.$nextTick(() => {
            this.handleSetFocus(index + 1);
          });
        } else {
          this.$emit('async-load-nodes', node, index, true);
        }
      },

      /**
       * 获取节点的样式
       *
       * @param {Object} node 当前节点对象
       */
      getNodeStyle (node) {
        const isSameLevelExistSync = this.allData
          .filter((item) => item.level === node.level)
          .some((item) => item.type === 'node' && item.async);
        const flag = !node.async && isSameLevelExistSync;
        const asyncIconWidth = 5;
        if (!node.level) {
          // if (flag) {
          //   return {
          //     paddingLeft: `${this.leftBaseIndent + asyncIconWidth}px`
          //   };
          // }
          return {
            paddingLeft: `${this.leftBaseIndent}px`
          };
        }
        if (node.async) {
          return {
            paddingLeft: (node.level + 1) * this.leftBaseIndent + 'px'
          };
        }
        if (isSameLevelExistSync && ['search', 'search-empty'].includes(node.type)) {
          return {
            paddingLeft: (node.level + 1) * this.leftBaseIndent + 'px'
          };
        }
        if (flag) {
          return {
            paddingLeft: (node.level + 1) * this.leftBaseIndent + asyncIconWidth + 'px'
          };
        }
        return {
          paddingLeft: (node.level + 1) * this.leftBaseIndent + 14 + 'px'
        };
      },

      getComputedDisplay (node) {
        const isSameLevelExistSync = this.allData
          .filter((item) => item.level === node.level)
          .some((item) => item.type === 'node' && item.async);
        return isSameLevelExistSync && !node.async;
      },

      /**
       * 滚动回调函数
       */
      rootScroll: _.throttle(function () {
      // this.updateRenderData(this.$el.scrollTop)
      }, 0),

      /**
       * 更新可视区渲染的数据列表
       *
       * @param {Number} scrollTop 滚动条高度
       */
      updateRenderData (scrollTop = 0) {
        // 可视区显示的条数
        const count = Math.ceil(this.$el.clientHeight / this.itemHeight);
        // 滚动后可视区新的 startIndex
        const newStartIndex = Math.floor(scrollTop / this.itemHeight);
        // 滚动后可视区新的 endIndex
        const newEndIndex = newStartIndex + count;
        this.startIndex = newStartIndex;
        this.endIndex = newEndIndex;
        this.$refs.content.style.transform = `translate3d(0, ${newStartIndex * this.itemHeight}px, 0)`;
      },

      /**
       * 节点展开/收起
       *
       * @param {Object} node 当前节点
       * @param {Boolean} isExpand 是否展开
       */
      expandNode (node, index, isExpand) {
        const flag = this.getExpandedDisabled(index);
        const canExpanded = this.isExistAsync(node) ? node.children && node.children.length : true;
        if (flag || !canExpanded) {
          return;
        }
        if (isExpand) {
          node.expanded = isExpand;
        } else {
          node.expanded = !node.expanded;
        }
        if (node.children && node.children.length) {
          const children = this.allData.filter((item) => item.parentId === node.nodeId);
          children.forEach((child) => {
            if (node.expanded) {
              child.visiable = child.type !== 'search' && node.expanded;
            } else {
              child.visiable = false;
            }
            if (child.async && !node.expanded) {
              this.collapseNode(child);
            }
          });
          this.$emit('on-expanded', index, node.expanded);
        } else {
          if (!node.expanded) {
            const nextNode = this.allData[index + 1];
            if (nextNode && nextNode.type === 'search') {
              this.allData.splice(index + 1, 1);
            }
            const nextOneNode = this.allData[index + 1];
            if (nextOneNode && nextOneNode.type === 'search-empty') {
              this.allData.splice(index + 1, 1);
            }
          }
          if (node.async && node.expanded) {
            this.$emit('async-load-nodes', node, index, false);
          }
        }
      },

      /**
       * 收起节点
       * 收起节点的时候需要把节点里面的所有节点都收起，节点里面的父节点收起同时节点里面的父节点下的子节点都要隐藏
       *
       * @param {Object} node 当前要收起的节点，这个节点指的是含有子节点的节点
       */
      collapseNode (node) {
        node.expanded = false;
        if (node.children && node.children.length) {
          const children = this.allData.filter((item) => item.parentId === node.nodeId);
          children.forEach((child) => {
            child.visiable = false;
            if (child.async) {
              this.collapseNode(child);
            }
          });
        }
      },

      // 选择当前节点，展示右侧表格数据
      handleSelectNode (node, index) {
        this.tableLoading = true;
        this.selectNodeDataIndex = index;
        this.selectNodeData = Object.assign({}, node);
        if (node.id !== this.curSearchMode.id) {
          this.$nextTick(() => {
            this.$refs[`topologyInputRef${index}`].value = '';
            this.tableEmptyData = Object.assign({}, {});
            this.subPagination.current = 1;
          });
        }
        this.$emit('async-load-table-nodes', node, index, false);
        setTimeout(() => {
          this.tableLoading = false;
        }, 0);
      },

      handleNodeChecked (value, node) {
        if (node.children && node.children.length > 0) {
          const children = this.allData.filter((item) => item.parentId === node.nodeId);
          children.forEach((item) => {
            // isRemote 已有默认权限标识
            if (item.checked !== value && !item.isRemote) {
              item.checked = value;
            }
            if (item.disabled !== value && !item.isRemote) {
              item.disabled = value;
            }
            if (item.children && item.children.length > 0) {
              this.handleNodeChecked(value, item);
            }
          });
        }
      },

      handleNodeChange (newVal, oldVal, localVal, node, index) {
        if (this.isShiftBeingPress) {
          this.pressIndex = index;
          this.pressLevels.push(node.level);
        }
        this.handleNodeChecked(newVal, node);
        this.getChildrenChecked(newVal, node);
        this.$emit('on-select', newVal, node);
      },

      // 获取子集默认选中的数据
      getChildrenChecked (newVal, node) {
        const childrenList = this.allData.filter((item) => item.parentId === node.nodeId);
        const childrenIdList = childrenList.map((v) => v.id);
        const defaultCheckedList = childrenList
          .filter((item) => item.disabled && childrenIdList.includes(item.id))
          .map((v) => v.id);
        this.$nextTick(() => {
          this.renderTopologyData.forEach((item) => {
            if (childrenIdList.includes(item.id) && this.$refs.topologyTableRef) {
              this.$refs.topologyTableRef.toggleRowSelection(item, newVal);
              if (defaultCheckedList.includes(item.id)) {
                this.$refs.topologyTableRef.toggleRowSelection(item, true);
              }
            }
          });
        });
      },

      handlePageChange (current) {
        this.pagination = Object.assign(this.pagination, { current });
        this.$emit('on-page-change', current, this.allData[this.allData.length - 1]);
      },

      handleTablePageChange (current) {
        const index = this.allData.findIndex(
          (item) => item.parentId === this.selectNodeData.nodeId && item.type === 'load'
        );
        if (index > -1) {
          this.$set(this.allData[index], 'current', current - 1);
          this.$emit('on-table-page-change', this.allData[index], index);
        }
      },

      getDataByPage (page, list) {
        if (!page) {
          this.subPagination.current = page = 1;
        }
        let startIndex = (page - 1) * this.subPagination.limit;
        let endIndex = page * this.subPagination.limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > list.length) {
          endIndex = list.length;
        }
        console.log(startIndex, endIndex);
        if (startIndex >= list.length) {
          return this.curTableData;
        } else {
          return list.slice(startIndex, endIndex);
        }
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectedNode.push(row);
              this.$set(row, 'checked', true);
              this.$emit('on-select', true, row);
            } else {
              this.currentSelectedNode = this.currentSelectedNode.filter(
                (item) => item.id.toString() !== row.id.toString()
              );
              this.$set(row, 'checked', false);
              this.$emit('on-select', false, row);
            }
            console.log(this.currentSelectedNode, 5555);
          },
          all: () => {
            const tableIdList = _.cloneDeep(this.renderTopologyData.map((v) => v.id.toString()));
            const currentSelect = payload.filter((item) => !item.disabled);
            const selectNode = this.currentSelectedNode.filter((item) => !tableIdList.includes(item.id.toString()));
            this.currentSelectedNode = [...selectNode, ...payload];
            let nodes = currentSelect.length ? currentSelect : this.renderTopologyData;
            if (nodes.length) {
              nodes = nodes.filter((item) => !item.disabled);
            }
            if (!payload) {
              this.renderTopologyData.forEach((item) => {
                if (!item.disabled) {
                  this.$set(
                    item,
                    'checked',
                    !(
                      !payload.length
                      || !this.currentSelectedNode.map((v) => v.id.toString()).includes(item.id.toString())
                    )
                  );
                  this.$refs.topologyTableRef && this.$refs.topologyTableRef.toggleRowSelection(item, item.checked);
                }
              });
            }
            this.$emit('on-select-all', nodes, currentSelect.length > 0);
          }
        };
        return typeMap[type]();
      },

      handleSelectChange (selection, node) {
        if (this.isShiftBeingPress) {
          this.pressIndex = this.allData.findIndex((item) => item.id === node.id);
          this.pressLevels.push(node.level);
        }
        this.fetchSelectedGroups('multiple', selection, node);
      },

      handleSelectAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      }
    }
  };
</script>

<style lang="postcss">
.iam-topology-tree {
  padding: 10px 0;
  font-size: 14px;
  position: relative;

  .ghost-wrapper {
    position: absolute;
    left: 0;
    top: 0;
    right: 0;
    z-index: -1;
  }

  .render-wrapper {
    left: 0;
    right: 0;
    top: 0;
    position: absolute;
  }

  .node-item {
    display: flex;
    position: relative;
    margin: 0;
    line-height: 32px;
    text-align: left;
    &.active {
      color: #3a84ff;
    }
    &.load-more-node {
      padding: 3px 0;
    }
    &.can-hover {
      cursor: pointer;
      &:hover {
        .search-icon {
          display: inline-block;
        }
      }
    }
    &-active {
      background-color: #e1ecff;
      cursor: pointer;
      .tree-node-name {
        color: #3a84ff;
      }
    }
  }
  .search-empty-wrapper {
    padding-left: 3px;
    font-size: 12px;
    color: #c4c6cc;
  }

  .search-icon {
    margin-left: 2px;
    display: none;
    cursor: pointer;
    i {
      position: relative;
      top: -2px;
      font-size: 12px;
      font-weight: 600;
      color: #3a84ff;
    }
  }

  .node-icon {
    position: relative;
    font-size: 16px;
    color: #c4c6cc;
    &.active {
      color: #3a84ff;
    }
  }

  .arrow-icon {
    margin-right: 5px;
    line-height: 32px;
    color: #c0c4cc;
    cursor: pointer;
    &.is-disabled {
      color: #c4c6cc;
      cursor: not-allowed;
    }
  }

  .block {
    display: inline-block;
    width: 14px;
    height: 14px;
    color: #fafbfd;
  }

  .iam-topology-title-cls {
    display: flex !important;
    line-height: 32px;
    .bk-checkbox {
      top: 9px;
    }
    .bk-checkbox-text {
      font-size: 12px;
      /* width: 180px; */
      /* white-space: nowrap;
          text-overflow: ellipsis;
          overflow: hidden; */
    }
    .tree-node-name {
      display: inline-block;
      /* line-height: 1; */
      vertical-align: middle;
    }
  }

  .node-radio {
    /* display: inline-block; */
    display: flex;
    .bk-form-checkbox {
      position: relative;
      margin-right: 0;
      padding: 0;
      /* top: -2px; */
    }
    .tree-node-name {
      margin-left: 10px;
      font-size: 12px;
    }
    /* .bk-checkbox-text {
          max-width: 200px;
      } */
  }

  .node-loading {
    .loading {
      display: inline-block;
      width: 14px;
      height: 14px;
    }
    .loading-text {
      display: inline-block;
      font-size: 12px;
      color: #a3c5fd;
    }
  }

  .search-loading-wrapper {
    position: relative;
    left: 20px;
    min-height: 32px;
    .bk-loading {
      /* background: #fafbfd !important; */
      background-color: #ffffff !important;
      .bk-loading-wrapper {
        top: 75% !important;
      }
    }
  }

  .load-more-wrapper {
    position: relative;
    padding: 0 18px;
    line-height: 26px;
    .load-item {
      width: 140px;
      text-align: center;
      background: #f0f1f5;
      font-size: 12px;
      color: #979ba5;
      &.normal {
        cursor: pointer;
      }
      &.normal:hover {
        background: #e1ecff;
        color: #3a84ff;
      }
      &.exist-load-more {
        cursor: not-allowed;
      }
      .node-load-more-loading {
        position: relative;
        min-height: 26px;
        .bk-loading {
          background: #f0f1f5 !important;
          .bk-loading-wrapper {
            top: 75% !important;
          }
        }
      }
    }
  }
}
</style>

<style lang="postcss" scoped>
.topology-tree-table {
  border: 0;
  .bk-table-empty-block {
    height: calc(100vh - 450px);
  }
  .bk-page.bk-page-align-right {
    padding: 10px;
  }
}

.multiple-topology-tree {
  display: flex;
  &-left {
    border-right: 1px solid #dcdee5;
  }
  &-right {
    width: 100%;
    padding-left: 20px;
  }
}

.iam-topology-tree-only,
.multiple-topology-tree-left-content,
.multiple-topology-tree-right-content {
  height: calc(100vh - 550px);
  overflow: auto;
  z-index: 2;
  &::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: #dcdee5;
    border-radius: 3px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
    border-radius: 3px;
  }
}

.iam-topology-tree-only {
  height: calc(100vh - 450px);
}

/deep/ .topology-tree-pagination-cls {
  padding: 10px 20px;
  .bk-page-small-jump {
    .jump-input {
      outline: none;
      min-width: 0;
    }
  }
}
</style>
