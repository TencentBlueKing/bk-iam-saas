<template>
  <div
    :class="[
      'iam-topology-tree',
      { 'iam-topology-tree-only': isOnlyLevel },
      { 'bk-has-border-tree': isBorder }
    ]"
    :style="formatLevelStyle"
  >
    <!-- <div class="ghost-wrapper" :style="ghostStyle" v-if="!isOnlyLevel"></div> -->
    <div class="render-wrapper" ref="content">
      <template v-if="isOnlyLevel">
        <div class="page-count-tip" v-if="formatSelectedCount.length">
          <span>{{ $t(`m.common['已选择']`) }}</span>
          <span>{{ $t(`m.common['本页']`) }}</span>
          <span class="selected-count">{{ formatSelectedCount.length }}</span>
          <span>{{ $t(`m.common['条']`) }}{{$t(`m.common['，']`)}}</span>
          <span
            :class="[
              'clear-select-tip',
              { 'is-disabled': !formatAllowClearCount.length }
            ]"
            v-bk-tooltips="{ content: $t(`m.common['暂无可清空数据']`), disabled: formatAllowClearCount.length > 0 }"
            @click.stop="handleClearPageAll"
          >
            {{ $t(`m.common['清除选择']`) }}
          </span>
        </div>
        <bk-table
          ref="topologyTableRef"
          size="small"
          data-test-id="topology_tree_group"
          ext-cls="topology-tree-table"
          :header-border="false"
          :outer-border="false"
          :max-height="formatTableHeight"
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
        <div v-if="pagination.count > 0" class="topology-table-pagination">
          <div class="custom-largest-count">
            <span>{{ $t(`m.common['每页']`) }}</span>
            <span class="max-count">{{maxPageCount}}</span>
            <span>{{ $t(`m.common['条']`) }}{{ $t(`m.common['，']`) }}</span>
          </div>
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
        </div>
      </template>
      <template v-else>
        <div class="multiple-topology-tree">
          <div class="multiple-topology-tree-left" :style="formatLeftStyle">
            <topology-input
              ref="topologyTreeInputRef"
              :is-filter="isFilter"
              :placeholder="curPlaceholder"
              @on-search="handleTreeSearch(...arguments)"
            />
            <div class="multiple-topology-tree-left-content" :style="formatLeftContentStyle">
              <template v-if="!isTreeEmpty">
                <div
                  v-for="(item, index) in allTreeData"
                  :key="item.nodeId"
                  :class="[
                    'node-item',
                    {
                      'node-item-active': item.nodeId === selectNodeData.nodeId && item.type === 'node'
                    },
                    { 'load-more-node': formatLoadMore(item) },
                    { 'search-node': item.type === 'search' },
                    { 'can-hover': item.type === 'node' && !item.loading }
                  ]"
                  :style="getNodeStyle(item)"
                  v-show="item.visiable"
                  @click.stop="handleSelectNode(item, index)"
                >
                  <template v-if="item.type === 'node'">
                    <Icon
                      v-if="!isTwoLevel && item.async"
                      bk
                      :type="item.expanded ? 'down-shape' : 'right-shape'"
                      :class="[
                        'arrow-icon'
                      ]"
                      @click.stop="expandNode(item, index)"
                    />
                    <div
                      :class="[
                        'node-radio',
                        { 'node-radio-no-icon': !(!isTwoLevel && item.async) },
                        { 'node-radio-no-icon-two-level': (!(!isTwoLevel && item.async)) && isTwoLevel },
                        { 'node-radio-none': isTwoLevel && item.level === 1 }
                      ]"
                      :style="formatNoIcon(item)"
                      @click.stop>
                      <bk-checkbox
                        :true-value="true"
                        :false-value="false"
                        :disabled="formatRadioDisabled(item)"
                        v-model="item.checked"
                        ext-cls="iam-topology-title-cls"
                        :title="`ID: ${item.id}; ${$t(`m.levelSpace['名称']`)}: ${item.name}`"
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
                            v-bkloading="{
                              isLoading: item.loadingMore,
                              opacity: 1,
                              theme: 'primary',
                              size: 'mini'
                            }"
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
                        @on-clear="handleEmptyClear('tree', item, index)"
                        @on-refresh="handleEmptyRefresh('tree', item, index)"
                      />
                    </div>
                  </template>
                </div>
              </template>
              <template v-else>
                <ExceptionEmpty
                  :type="formatTreeEmpty(emptyTreeData, 'tree', 'type')"
                  :tip-type="formatTreeEmpty(emptyTreeData, 'tree', 'tipType')"
                  :empty-text="formatTreeEmpty(emptyTreeData, 'tree', 'emptyText')"
                  @on-clear="handleEmptyClear('tree')"
                  @on-refresh="handleEmptyRefresh('tree')"
                />
              </template>
            </div>
          </div>
          <div class="multiple-topology-tree-right" :style="formatRightStyle">
            <topology-input
              ref="topologyTableInputRef"
              :placeholder="formatPlaceHolder('input') || ''"
              @on-search="handleTableSearch(...arguments, selectNodeData, selectNodeDataIndex)"
            />
            <div class="multiple-topology-tree-right-content">
              <div class="page-count-tip" v-if="formatSelectedCount.length">
                <span>{{ $t(`m.common['已选择']`) }}</span>
                <span>{{ $t(`m.common['本页']`) }}</span>
                <span class="selected-count">{{ formatSelectedCount.length }}</span>
                <span>{{ $t(`m.common['条']`) }}{{$t(`m.common['，']`)}}</span>
                <span
                  :class="[
                    'clear-select-tip',
                    { 'is-disabled': !formatAllowClearCount.length }
                  ]"
                  v-bk-tooltips="{ content: $t(`m.common['暂无可清空数据']`), disabled: formatAllowClearCount.length > 0 }"
                  @click.stop="handleClearPageAll"
                >
                  {{ $t(`m.common['清除选择']`) }}
                </span>
              </div>
              <bk-table
                ref="topologyTableRef"
                size="small"
                data-test-id="topology_tree_group"
                ext-cls="topology-tree-table"
                :header-border="false"
                :outer-border="false"
                :data="renderTopologyData"
                :max-height="formatTableHeight"
                @select="handleSelectChange"
                @select-all="handleSelectAllChange"
                v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
              >
                <bk-table-column type="selection" align="center" :selectable="setDefaultSelect" />
                <bk-table-column :label="formatPlaceHolder('table')">
                  <template slot-scope="{ row }">
                    <span :title="`ID: ${row.id}; ${$t(`m.levelSpace['名称']`)}: ${row.name}`">{{ row.name }}</span>
                  </template>
                </bk-table-column>
                <template v-if="!tableLoading && subPagination.count === 0">
                  <template slot="empty">
                    <ExceptionEmpty
                      :type="formatTreeEmpty(emptyData, 'table', 'type')"
                      :tip-type="formatTreeEmpty(emptyData, 'table', 'tipType')"
                      :empty-text="formatTreeEmpty(emptyData, 'table', 'emptyText')"
                      @on-clear="handleEmptyClear('table', selectNodeData, selectNodeDataIndex)"
                      @on-refresh="handleEmptyRefresh('table', selectNodeData, selectNodeDataIndex)"
                    />
                  </template>
                </template>
              </bk-table>
              <div v-if="subPagination.count > 0" class="topology-table-pagination">
                <div class="custom-largest-count">
                  <span>{{ $t(`m.common['每页']`) }}</span>
                  <span class="max-count">{{maxPageCount}}</span>
                  <span>{{ $t(`m.common['条']`) }}{{ $t(`m.common['，']`) }}</span>
                </div>
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
              </div>
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
  import { bus } from '@/common/bus';
  import { getWindowHeight, formatCodeData } from '@/common/util';
  import { mapGetters } from 'vuex';

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
      hasSelectedValues: {
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
        default: 16
      },
      resourceTotal: {
        type: Number
      },
      subResourceTotal: {
        type: Number,
        default: 0
      },
      maxPageCount: {
        type: Number,
        default: 100
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
      },
      curKeyword: {
        type: String
      },
      curTableKeyword: {
        type: String
      },
      curSelectedChain: {
        type: Object
      },
      searchDisplayText: {
        type: String
      },
      resourceValue: {
        type: Boolean,
        default: false
      },
      // 处理有自定义属性条件场景
      hasAttribute: {
        type: Boolean,
        default: false
      },
      // 处理有bar的场景
      hasStatusBar: {
        type: Boolean,
        default: false
      },
      // 处理可以添加新的拓扑实例组的场景
      hasAddInstance: {
        type: Boolean,
        default: false
      },
      // 是否显示添加属性或者拓扑实例bar
      isShowEditAction: {
        type: Boolean,
        default: false
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
        emptyTreeData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        emptyTableData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        selectNodeData: {},
        curSelectTreeNode: {},
        allTreeData: [],
        checkedNodeIdList: [],
        currentSelectedNode: [],
        renderTopologyData: [],
        tablePageData: [],
        curSelectedValues: [],
        selectNodeDataIndex: -1,
        curSearchMode: 'tree',
        treeKeyWord: '',
        tableKeyWord: '',
        maxCountContent: '',
        curExpandNode: {}
      };
    },
    computed: {
      ...mapGetters([
        'curTreeTableData',
        'curTreeTableDataIndex',
        'curAllTreeNode',
        'curTreeTableChecked',
        'curTreeSelectedNode'
      ]),
      // ghostStyle () {
      //   return {
      //     height: this.visiableData.length * this.itemHeight + 'px'
      //   };
      // },
      // allTreeData 中 visiable 为 true 的数据，visiable 属性辅助设置展开收起的
      // 当父节点收起时，子节点的 visiable 为 false
      visiableData () {
        return this.allTreeData.filter((item) => item.visiable);
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
        return this.allTreeData.some((item) => item.id === -1 && item.loadingMore);
      },
      dragDynamicWidth () {
        return (payload) => {
          // const offsetWidth = this.getDragDynamicWidth() > 600 ? 560 + this.getDragDynamicWidth() - 600 : 560;
          const offsetWidth = this.getDragDynamicWidth ? this.getDragDynamicWidth() * 0.37 : 500;
          const isSameLevelExistSync = this.allTreeData.filter((item) => item.level === payload.level).some((item) => item.type === 'node' && item.async);
          // flag点击展开后没有子集数据的场景
          const flag = !payload.async && isSameLevelExistSync;
          const asyncLevelWidth = 30;
          // 左右边距各16px加上距离复选框的编剧以及当前item的padding
          const paddingWidth = 32 + 10 + 12;
          if (!payload.level) {
            if (payload.loading) {
              return {
                maxWidth: `${offsetWidth - 20}px`
              };
            }
            if (payload.async || flag) {
              return {
                maxWidth: `${offsetWidth - asyncLevelWidth - paddingWidth}px`
              };
            }
            return {
              maxWidth: `${offsetWidth}px`
            };
          } else {
            if (payload.async || flag) {
              return {
                maxWidth: `${offsetWidth - (payload.level + 1) * this.leftBaseIndent - asyncLevelWidth - paddingWidth}px`
              };
            }
          }
          if (isSameLevelExistSync && ['search', 'search-empty'].includes(payload.type)) {
            return {
              maxWidth: `${offsetWidth - (payload.level + 1) * this.leftBaseIndent - paddingWidth}px`
            };
          }
          return {
            maxWidth: `${offsetWidth - (payload.level + 1) * this.leftBaseIndent - asyncLevelWidth - paddingWidth}px`
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
      formatLevelStyle () {
        const hasOther = this.hasAddInstance || this.hasAttribute || this.hasStatusBar || this.isShowEditAction;
        if (this.isOnlyLevel) {
          if (hasOther) {
            return {
             'height': 'calc(100vh - 410px)'
            };
          }
          return {
            'height': 'calc(100vh - 405px)'
          };
        } else {
          if (hasOther) {
            return {
              'height': 'calc(100vh - 350px)'
            };
          } else {
            return {
              'height': 'calc(100vh - 342px)'
            };
          }
        }
      },
      formatLeftStyle () {
        return {
          width: this.getDragDynamicWidth ? `${this.getDragDynamicWidth() * 0.37}px` : '600px'
        };
      },
      formatLeftContentStyle () {
        const hasOther = this.hasAddInstance || this.hasAttribute || this.hasStatusBar || this.isShowEditAction;
        if (hasOther) {
          return {
            'height': 'calc(100vh - 415px)',
            'overflow': 'auto'
          };
        }
        return {
          'height': 'calc(100vh - 415px)',
          'overflow': 'auto'
        };
      },
      formatRightStyle () {
        const leftWidth = this.getDragDynamicWidth ? `${this.getDragDynamicWidth() * 0.37}px` : '600px';
        return {
          width: `calc(100% - ${leftWidth})`
        };
      },
      formatTableHeight () {
        const tipHeight = this.formatSelectedCount.length ? 44 : 0;
        if (this.isOnlyLevel) {
          const tableHeight = getWindowHeight() - 460;
          return this.formatSelectedCount.length ? tableHeight - tipHeight : tableHeight;
        }
        return getWindowHeight() - 468 - tipHeight;
      },
      formatRadioDisabled () {
        return (payload) => {
          if (this.resourceValue && this.curSelectedValues.length) {
            return !payload.checked;
          }
          return payload.disabled;
        };
      },
      formatSelectedCount () {
        const curTableData = this.renderTopologyData.filter(
          (item) => item.checked || (item.disabled && item.parentChain.length));
        return curTableData;
      },
      formatAllowClearCount () {
        const curTableData = this.renderTopologyData.map((item) => `${item.name}${item.id}`);
        // 处理多层拓扑第一次无法在computed里更新checked值
        const curSelectedTableData = this.renderTopologyData.filter((item) => item.checked && !item.disabled).map((item) => `${item.name}${item.id}`);
        const result = this.allTreeData.filter((item) =>
          ((item.checked && !item.disabled) && curTableData.includes(`${item.name}${item.id}`))
          || curSelectedTableData.includes(`${item.name}${item.id}`));
        return result;
      },
      formatLoadMore () {
        return (payload) => {
          return payload.type === 'load' && payload.level < this.curChain.length - 1;
        };
      },
      formatNoIcon () {
        return (payload) => {
          const { async, expanded, level } = payload;
          const hasData = this.allTreeData.find((v) => v.level === level);
          if (!async && !expanded && !this.isTwoLevel) {
            if (hasData && hasData.async && level < 3) {
              return {
                'paddingLeft': `29px`
              };
            } else {
              return {
                'paddingLeft': `${16 + level * 8}px`
              };
            }
          }
        };
      },
      isTreeEmpty () {
        return this.allTreeData.filter((item) => item.type === 'node').length === 0 || this.searchDisplayText === this.$t(`m.common['搜索结果为空']`);
      }
    },
    watch: {
      pressIndex (newVal, oldVal) {
        if (newVal > -1 && oldVal > -1 && [...new Set(this.pressLevels)].length === 1) {
          const indexList = [...new Set([newVal, oldVal].sort())];
          if (indexList.length > 1 && indexList[1] - indexList[0] > 1) {
            for (let i = indexList[0] + 1; i < indexList[1]; i++) {
              const node = this.allTreeData[i];
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
      allData: {
        handler (value) {
          this.allTreeData = [...value];
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
            const curSelectNode = this.visiableData.length ? this.visiableData[0] : {};
            this.handleSelectNode(curSelectNode, 0);
            this.tableLoading = false;
          }
        },
        immediate: true
      },
      emptyData: {
        handler (value) {
          this.curSearchMode === 'tree'
            ? this.emptyTreeData = Object.assign({}, value)
            : this.emptyTableData = Object.assign({}, value);
        },
        immediate: true
      },
      hasSelectedValues: {
        handler (value) {
          this.curSelectedValues = [...value];
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
        bus.$off('update-table-toggleRowSelection');
      });
      document.addEventListener('resize', this.handleResize);
      bus.$on('update-table-toggleRowSelection', ({ isChecked, node }) => {
        const childData = this.renderTopologyData.find((item) => `${item.name}&${item.id}` === `${node.name}&${node.id}`);
        if (childData) {
          this.$nextTick(() => {
            this.renderTopologyData.forEach((item) => {
              if (`${item.name}&${item.id}` === `${node.name}&${node.id}`) {
                this.$refs.topologyTableRef.toggleRowSelection(item, isChecked);
                if (!item.disabled) {
                  item.checked = isChecked;
                }
              }
              if (!isChecked) {
                this.currentSelectedNode = this.currentSelectedNode.filter((v) => `${v.name}&${v.id}` !== `${node.name}&${node.id}`);
                this.$store.commit('setTreeSelectedNode', this.currentSelectedNode);
              }
            });
          });
        } else {
          this.getChildrenChecked(isChecked, node);
        }
      });
    },
    methods: {
      fetchLevelTree (value) {
        if (this.curKeyword) {
          this.$nextTick(() => {
            this.treeKeyWord = this.curKeyword;
            this.$refs.topologyTreeInputRef.value = this.treeKeyWord;
          });
        }
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
              this.curSelectTreeNode = value.find((v) =>
                `${v.nodeId}&${v.id}` === `${this.selectNodeData.nodeId}&${this.selectNodeData.id}`) || {};
              const curNode = value.find(
                (item) => `${item.name}&${item.id}` === `${this.selectNodeData.name}&${this.selectNodeData.id}`
              );
              // 判断搜索无数据
              const searchData = value.find((item) => ['search-empty', 'search-loading'].includes(item.type));
              if (curNode) {
                if (`${this.selectNodeData.name}&${this.selectNodeData.id}` === `${this.curExpandNode.name}&${this.curExpandNode.id}`) {
                  this.subPagination = Object.assign(this.subPagination, {
                    count: this.subResourceTotal
                  });
                }
                this.tablePageData = [...this.curTableData];
                const list = [...(curNode.children || [])].filter((item) => item.type === 'node');
                curNode.current = this.subPagination.current;
                this.renderTopologyData = list.length ? this.getDataByPage(curNode.current, list) : [];
                // 这里要兼容判断父级全选和直接点击子集表格全选
                const childSelectedNodes = this.currentSelectedNode.map((item) => `${item.name}&${item.id}`);
                this.checkedNodeIdList = value
                  .filter((item) => item.checked && item.parentId === this.selectNodeData.nodeId)
                  .map((v) => `${this.selectNodeData.nodeId}&${v.id}`);
                if (!curNode.children.length) {
                  if (this.tableKeyWord) {
                    const searchEmptyData = value.find((item) => item.type === 'search-empty');
                    if (searchEmptyData) {
                      this.emptyTableData = Object.assign({}, searchEmptyData);
                    }
                  } else {
                    this.emptyTableData = formatCodeData(0, {
                      tipType: ['refresh'].includes(this.emptyData.tipType) ? this.emptyData.tipType : ''
                    });
                  }
                }
                this.$nextTick(() => {
                  this.renderTopologyData.forEach((item) => {
                    this.$refs.topologyTableRef
                      && this.$refs.topologyTableRef.toggleRowSelection(
                        item,
                        this.checkedNodeIdList.includes(`${this.selectNodeData.nodeId}&${item.id}`)
                          || childSelectedNodes.includes(`${item.name}&${item.id}`)

                      );
                  });
                });
                // 如果父级搜索无数据，默认回显已选中的资源
                if (!this.allTreeData.length && this.curKeyword) {
                  const childNode = this.curAllTreeNode.find((item) => item.parentId === curNode.nodeId);
                  if (childNode) {
                    this.$store.commit('setTreeTableData', childNode);
                  }
                  // 存储回显直接勾选父级，子集全部默认勾选数据
                  this.formatDefaultSelected();
                }
              }
              if (!curNode && !searchData && this.selectNodeData.children.length) {
                this.renderTopologyData = [...this.selectNodeData.children].filter((item) =>
                  this.curTableData.map((v) => `${v.display_name}&${v.id}`).includes(`${item.name}&${item.id}`));
                this.formatDefaultSelected();
                return;
              }
              if (searchData) {
                if (
                  ['search-empty', 'search-loading'].includes(searchData.type)
                ) {
                  if (searchData.level > 0 && ['table'].includes(this.curSearchMode)) {
                    this.renderTopologyData = [];
                    this.emptyTableData = formatCodeData(0, { tipType: 'search' });
                  } else {
                    this.emptyTreeData = formatCodeData(0, { tipType: 'search' });
                  }
                }
              }
              if (!this.renderTopologyData.length) {
                this.subPagination.count = 0;
              }
            }
          }
        }
      },

      formatTreeEmpty (payload, mode, type) {
        const modeMap = {
          tree: () => {
            const typeMap = {
              type: () => {
                if (Object.keys(payload).length) {
                  if ([payload.name].includes(this.$t(`m.common['搜索结果为空']`)) || payload.tipType === 'search') {
                    return 'search-empty';
                  }
                  return 500;
                } else {
                  return 'empty';
                }
              },
              tipType: () => {
                if (Object.keys(payload).length) {
                  if ([payload.name].includes(this.$t(`m.common['搜索结果为空']`)) || payload.tipType === 'search') {
                    return 'search';
                  }
                  return 'refresh';
                } else {
                  return '';
                }
              },
              emptyText: () => {
                if (Object.keys(payload).length) {
                  if ([payload.name].includes(this.$t(`m.common['搜索结果为空']`)) || payload.tipType === 'search') {
                    return '搜索结果为空';
                  }
                  return '数据不存在';
                } else {
                  return '暂无数据';
                }
              }
            };
            return typeMap[type]();
          },
          table: () => {
            const typeMap = {
              type: () => {
                if (Object.keys(payload).length) {
                  if (payload.type === 'empty') {
                    return 'empty';
                  }
                  if (payload.name === this.$t(`m.common['搜索结果为空']`) || payload.tipType === 'search') {
                    return 'search-empty';
                  }
                  return payload.type;
                } else {
                  return 'empty';
                }
              },
              tipType: () => {
                if (Object.keys(payload).length) {
                  if (payload.type === 'empty') {
                    return '';
                  }
                  if (payload.name === this.$t(`m.common['搜索结果为空']`)) {
                    return 'search';
                  }
                  return payload.tipType;
                } else {
                  return '';
                }
              },
              emptyText: () => {
                if (Object.keys(payload).length) {
                  if (payload.type === 'empty') {
                    return '暂无数据';
                  }
                  if (payload.name === this.$t(`m.common['搜索结果为空']`)) {
                    return payload.name;
                  }
                  return payload.text;
                } else {
                  return '暂无数据';
                }
              }
            };
            return typeMap[type]();
          }
        };
        return modeMap[mode]();
      },

      formatDefaultSelected () {
        const defaultSelectList = this.curSelectedValues.map((v) => v.ids).flat(this.curChain.length);
        this.$nextTick(() => {
          this.renderTopologyData.forEach((item) => {
            this.$refs.topologyTableRef
              && this.$refs.topologyTableRef.toggleRowSelection(
                item,
                this.curTreeTableChecked.includes(`${this.selectNodeData.nodeId}&${item.id}`)
                  || this.curTreeSelectedNode.map((item) => `${item.name}&${item.id}`).includes(`${item.name}&${item.id}`)
                  || defaultSelectList.includes(`${item.id}&${this.curChain[item.level].id}`)
              );
          });
        });
      },

      setDefaultSelect (payload) {
        let singleCheckedData = [];
        if (this.curSelectedValues.length && !this.isOnlyLevel) {
          const defaultSelectList = this.curSelectedValues
            .filter((item) => item.disabled)
            .map((v) => v.ids).flat(this.curChain.length);
          if (defaultSelectList.length) {
            let childrenIdList = [];
            const result = !(defaultSelectList.includes(`${payload.id}&${this.curChain[payload.level].id}`)
              || defaultSelectList.includes(`${this.selectNodeData.id}&${this.curChain[payload.level - 1].id}`));
            // 处理多层资源权限搜索只支持单选
            if (this.resourceValue
              || (this.curSelectTreeNode.children
                && this.curSelectTreeNode.children.length)) {
              // 处理子集表格disabled
              if (this.curSelectTreeNode.checked) {
                this.curSelectTreeNode.children.forEach((v) => {
                  v.checked = true;
                  v.disabled = true;
                });
              }
              childrenIdList = this.curSelectTreeNode.children.filter((v) => v.disabled).map((v) => `${v.name}&${v.id}`);
              return !childrenIdList.includes(`${payload.name}&${payload.id}`);
            }
            return result || !childrenIdList.includes(`${payload.name}&${payload.id}`);
          }
        }
        const list = [...this.allTreeData].filter((item) => item.type === 'node');
        const allTreeData = list.filter((item) => item.disabled && item.type === 'node').map((item) => `${item.name}&${item.id}`);
        const selectNodeList = [...allTreeData, ...singleCheckedData];
        // 处理有的资源全选只能勾选一项
        if (this.resourceValue && this.curSelectedValues.length) {
          singleCheckedData = this.curSelectedValues.map((v) => v.ids).flat(this.curChain.length);
          return singleCheckedData.includes(`${payload.id}&${this.curChain[payload.level].id}`);
        }
        return !selectNodeList.includes(`${payload.name}&${payload.id}`);
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
        const asyncNode = this.allTreeData.find((item) => item.type === 'async');
        // if (!asyncNode) {
        //     return false
        // }
        return !!asyncNode;
      },

      getExpandedDisabled (index) {
        const data = this.allTreeData[index + 2];
        if (data && data.hasOwnProperty('type') && data.type === 'search-loading') {
          return true;
        }
        return false;
      },

      handleSetFocus (index) {
        this.levelIndex = index;
        if (this.$refs[`topologyInputRef${index}`]) {
          this.$refs[`topologyInputRef${index}`][0] && this.$refs[`topologyInputRef${index}`][0].handleSetFocus();
        }
      },

      getSearchDisabled (item) {
        return this.allTreeData.some((item) => item.type === 'search-loading');
      },

      handleTreeSearch (value, node, index) {
        // 如果没有node，代表是最外层的搜索
        this.curSearchMode = 'tree';
        this.treeKeyWord = value;
        if (node) {
          this.$emit('on-tree-search', { value, node, index });
        } else {
          this.$emit('on-search', value);
        }
      },

      handleTableSearch (value, node, index) {
        this.tableLoading = true;
        this.curSearchMode = 'table';
        this.tableKeyWord = value;
        const filterNodeType = ['node', 'search', 'search-empty'];
        let allTreeData = [...this.allTreeData].filter((item) => filterNodeType.includes(item.type));
        let curNode = allTreeData.find((item) => item.parentId === node.nodeId);
        if (this.treeKeyWord && !curNode) {
          allTreeData = [...this.curAllTreeNode].filter((item) => filterNodeType.includes(item.type));
          curNode = allTreeData.find((item) => item.parentId === node.nodeId);
        }
        if (curNode) {
          if (curNode.type === 'search-empty') {
            this.emptyTableData = formatCodeData(0, {
              tipType: value ? 'search' : '',
              name: curNode.name
            });
          }
          this.subPagination = Object.assign(this.subPagination, { current: 1, count: 0 });
          this.$emit('on-table-search', { value, node: curNode, index });
        } else {
          // this.emptyTableData = formatCodeData(0, {
          //   tipType: value ? 'search' : '',
          //   name: this.$t(`m.common['搜索结果为空']`)
          // });
          // 如果父级搜索了没数据，此时搜索表格需要提供当前父级下的children
          if (this.curTreeTableData.children && this.curTreeTableData.children.length) {
            const nodeItem = _.cloneDeep(this.curTreeTableData.children[0]);
            if (!nodeItem.parentChain.length) {
              const { id, system_id } = this.curChain[this.curTreeTableData.level];
              nodeItem.parentChain = [
                {
                  name: this.curTreeTableData.name,
                  id: this.curTreeTableData.id,
                  type: id,
                  system_id,
                  child_type: ''
                }
              ];
            }
            this.$emit('on-table-search', {
              value,
              node: nodeItem,
              index: this.curTreeTableDataIndex
            });
          }
        }
        setTimeout(() => {
          this.tableLoading = false;
        }, 1000);
      },

      handleEmptyClear (payload, node, index) {
        this.$nextTick(() => {
          const typeMap = {
            table: () => {
              this.emptyTableData.tipType = '';
              this.tableKeyWord = '';
              this.$refs.topologyTableInputRef.value = '';
              this.emptyTableData = Object.assign({}, formatCodeData(0, { tipType: '' }));
              // 如果父级搜索了没数据，此时搜索表格需要提供当前父级下的children
              if (!this.allTreeData.length && this.curTreeTableData.children && this.curTreeTableData.children.length) {
                this.$emit('on-table-search', {
                  value: '',
                  node: this.curTreeTableData.children[0],
                  index: this.curTreeTableDataIndex
                });
                return;
              }
              this.handleTableSearch('', node, index);
            },
            tree: () => {
              this.treeKeyWord = '';
              this.$refs.topologyTreeInputRef.value = '';
              this.handleTreeSearch('', node, index);
            }
          };
          typeMap[payload]();
        });
      },

      handleEmptyRefresh (payload, node, index) {
        this.handleEmptyClear(payload, node, index);
      },

      /**
       * 获取节点的样式
       *
       * @param {Object} node 当前节点对象
       */
      getNodeStyle (node) {
        const isSameLevelExistSync = this.allTreeData
          .filter((item) => item.level === node.level)
          .some((item) => item.type === 'node' && item.async);
        const flag = !node.async && isSameLevelExistSync;
        const asyncIconWidth = 5;
        if (!node.level) {
          // if (flag) {
          //   return {
          //     marginLeft: `${this.leftBaseIndent + asyncIconWidth}px`
          //   };
          // }
          return {
            marginLeft: `${this.leftBaseIndent}px`
          };
        }
        if (node.async) {
          return {
            marginLeft: (node.level + 1) * this.leftBaseIndent + 'px'
          };
        }
        if (isSameLevelExistSync && ['search', 'search-empty'].includes(node.type)) {
          return {
            marginLeft: (node.level + 1) * this.leftBaseIndent + 'px'
          };
        }
        if (flag) {
          return {
            marginLeft: (node.level + 1) * this.leftBaseIndent + asyncIconWidth + 'px'
          };
        }
        return {
          marginLeft: (node.level + 1) * this.leftBaseIndent + 14 + 'px'
        };
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
        // 处理当前不是选中项，点击的时候会刷新接口重置表格数量
        this.curExpandNode = _.cloneDeep(node);
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
          const children = this.allTreeData.filter((item) => item.parentId === node.nodeId);
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
            const nextNode = this.allTreeData[index + 1];
            if (nextNode && nextNode.type === 'search') {
              this.allTreeData.splice(index + 1, 1);
            }
            const nextOneNode = this.allTreeData[index + 1];
            if (nextOneNode && nextOneNode.type === 'search-empty') {
              this.allTreeData.splice(index + 1, 1);
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
          const children = this.allTreeData.filter((item) => item.parentId === node.nodeId);
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
        this.renderTopologyData = [];
        if (node.id !== this.selectNodeData.id) {
          this.handleEmptyClear('table', node, index);
        }
        if (Object.keys(node).length > 0) {
          node.expanded = true;
          this.selectNodeDataIndex = index;
          this.selectNodeData = Object.assign({}, node);
          this.curExpandNode = _.cloneDeep(node);
          // 当存在多层拓扑时，获取当前选中节点方便处理子集数据
          this.$store.commit('setTreeTableData', node);
          this.$store.commit('setTreeTableDataIndex', index);
          this.$store.commit('setToPoTreeData', this.allTreeData);
          // 存储回显直接勾选父级，子集全部默认勾选数据
          this.$store.commit('setTreeTableChecked', this.checkedNodeIdList);
          this.$store.commit('setTreeSelectedNode', this.currentSelectedNode);
          this.curSearchMode = 'table';
          // 存储只选择表格
          this.$emit('async-load-table-nodes', node, index, false);
        } else {
          this.selectNodeDataIndex = _.cloneDeep(this.curTreeTableDataIndex);
          this.selectNodeData = _.cloneDeep(this.curTreeTableData);
          this.fetchLevelTree(this.curAllTreeNode);
        }
        setTimeout(() => {
          this.tableLoading = false;
        }, 1000);
      },

      handleNodeChecked (value, node) {
        if (node.children && node.children.length > 0) {
          const children = this.allTreeData.filter((item) => item.parentId === node.nodeId);
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
        // 处理三层及以上拓扑不展开的场景下直接勾选同步右侧表格勾选状态
        if (!this.isOnlyLevel && !this.isTwoLevel) {
          let selectChildrenList = [];
          if (this.curSelectTreeNode.children.length) {
            selectChildrenList = this.curSelectTreeNode.children.map((item) => `${item.id}&${item.name}`);
          }
          this.renderTopologyData.forEach((item) => {
            if ((`${item.id}&${item.name}` === `${node.id}&${node.name}`)
              || selectChildrenList.includes(`${item.id}&${item.name}`)) {
              this.$refs.topologyTableRef.toggleRowSelection(item, value);
              // 如果上级数据checked， 子集默认disabled
              item.disabled = this.curSelectTreeNode.checked;
              item.checked = value;
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
        // this.$store.commit('setTreeSelectedNode');
        this.$emit('on-select', newVal, node);
      },

      handleClearPageAll () {
        if (!this.formatSelectedCount.length) {
          return;
        }
        const tableData = this.renderTopologyData.filter((item) => !item.disabled).map((v) => `${v.id}${v.name}`);
        this.currentSelectedNode = this.currentSelectedNode.filter((item) => !tableData.includes(`${item.id}${item.name}`));
        this.renderTopologyData.forEach((item) => {
          if (!item.disabled) {
            let allTreeData = [...this.allTreeData];
            if (!allTreeData.length && !this.isOnlyLevel && this.curKeyword) {
              allTreeData = [...this.curTreeTableData.children || []];
            }
            const curNode = allTreeData.find((v) => `${v.name}&${v.id}` === `${item.name}&${item.id}`);
            if (curNode) {
              if (!curNode.disabled) {
                curNode.checked = false;
              }
              item.checked = false;
              this.$emit('on-select', false, curNode);
            }
            this.$refs.topologyTableRef.toggleRowSelection(item, false);
          }
        });
      },

      // 获取子集默认选中的数据
      getChildrenChecked (newVal, node) {
        const childrenList = this.allTreeData.filter((item) => item.parentId === node.nodeId);
        const childrenIdList = childrenList.map((v) => v.id);
        const defaultCheckedList = childrenList
          .filter((item) => item.disabled && childrenIdList.includes(item.id))
          .map((v) => v.id);
        this.$nextTick(() => {
          const list = [];
          this.renderTopologyData.forEach((item) => {
            if (childrenIdList.includes(item.id) && this.$refs.topologyTableRef) {
              item.disabled = newVal;
              item.checked = newVal;
              this.$refs.topologyTableRef.toggleRowSelection(item, newVal);
              if (defaultCheckedList.includes(item.id)) {
                item.disabled = true;
                item.checked = true;
                list.push(item);
                this.$refs.topologyTableRef.toggleRowSelection(item, true);
              }
            }
          });
          this.$store.commit('setTreeSelectedNode', list);
        });
      },

      handlePageChange (current) {
        this.pagination = Object.assign(this.pagination, { current });
        this.$emit('on-page-change', current, this.allTreeData[this.allTreeData.length - 1]);
      },

      handleTablePageChange (current) {
        if (!this.allTreeData.length) {
          this.allTreeData = _.cloneDeep(this.curAllTreeNode);
        }
        const index = this.allTreeData.findIndex(
          (item) => item.parentId === this.selectNodeData.nodeId && item.type === 'load'
        );
        if (index > -1) {
          this.$set(this.allTreeData[index], 'current', current - 1);
          this.$emit('on-table-page-change', this.allTreeData[index], index);
        }
      },

      getDataByPage (page, list) {
        if (!page || page === 1) {
          this.subPagination.current = page = 1;
          let startIndex = (page - 1) * this.subPagination.limit;
          let endIndex = page * this.subPagination.limit;
          if (startIndex < 0) {
            startIndex = 0;
          }
          if (endIndex > list.length) {
            endIndex = list.length;
          }
          return list.slice(startIndex, endIndex);
        } else {
          return this.tablePageData;
        }
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            // 处理三层及以上拓扑不展开的场景下直接勾选同步右侧表格勾选状态
            if (!this.isOnlyLevel && !this.isTwoLevel) {
              this.allTreeData.forEach((item) => {
                if ((`${item.id}&${item.name}` === `${row.id}&${row.name}`) && !item.disabled) {
                  item.checked = !!isChecked;
                  this.handleNodeChecked(!!isChecked, item);
                }
              });
            }
            let allTreeData = [...this.allTreeData];
            if (!allTreeData.length && !this.isOnlyLevel && this.curKeyword) {
              allTreeData = [...this.curTreeTableData.children || []];
            }
            const curNode = allTreeData.find((item) => `${row.name}&${row.id}` === `${item.name}&${item.id}`);
            if (isChecked) {
              this.$set(row, 'checked', true);
              if (curNode) {
                this.currentSelectedNode.push(curNode);
                this.$emit('on-select', true, curNode);
              }
            } else {
              this.currentSelectedNode = this.currentSelectedNode.filter(
                (item) => `${item.name}&${item.id}` !== `${row.name}&${row.id}`
              );
              this.$set(row, 'checked', false);
              if (curNode) {
                this.$emit('on-select', false, curNode);
              }
            }
            this.$store.commit('setTreeSelectedNode', this.currentSelectedNode);
          },
          all: () => {
            // 针对资源权限搜索单选特殊处理
            const resourceList = this.resourceValue ? [...payload].slice(0, 1) : [...payload];
            let allTreeData = [...this.allTreeData];
            if (!allTreeData.length && !this.isOnlyLevel && this.curKeyword) {
              allTreeData = [...this.curTreeTableData.children || []];
            }
            const tableIdList = _.cloneDeep(this.renderTopologyData.map((v) => `${v.name}&${v.id}`));
            const selectNode = this.currentSelectedNode.filter(
              (item) => !tableIdList.includes(`${item.name}&${item.id}`)
            );
            this.currentSelectedNode = [...selectNode, ...resourceList];
            const currentSelect = allTreeData.filter(
              (item) => resourceList.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`) && !item.disabled
            );
            // 如果currentSelect有内容， 代表当前是勾选，否则就取从总数据里取当前页不是disabled的数据
            let noDisabledData = [];
            if (this.resourceValue) {
              // 处理单选业务
              const defaultSelectList = this.curSelectedValues
                .filter((item) => !item.disabled)
                .map((v) => v.ids).flat(this.curChain.length);
              noDisabledData = allTreeData.filter(
                (item) => defaultSelectList.includes(`${item.id}&${this.curChain[item.level].id}`)
              );
            } else {
              noDisabledData = allTreeData.filter(
                (item) =>
                  !resourceList.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`)
                  && this.renderTopologyData.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`)
              );
            }
            let nodes = currentSelect.length ? currentSelect : noDisabledData;
            this.renderTopologyData.forEach((item) => {
              if (!item.disabled) {
                this.$set(item, 'checked', resourceList.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`));
                if (resourceList.length && !currentSelect.length) {
                  this.$set(
                    item,
                    'disabled',
                    resourceList.map((v) => `${v.name}&${v.id}`).includes(`${item.name}&${item.id}`)
                  );
                }
                this.$refs.topologyTableRef && this.$refs.topologyTableRef.toggleRowSelection(item, item.checked);
              }
            });
            // 处理三层及以上拓扑不展开的场景下直接勾选同步右侧表格勾选状态
            if (!this.isOnlyLevel && !this.isTwoLevel) {
              const curSelectList = nodes.map((item) => `${item.id}&${item.name}`);
              const defaultSelectList = this.curSelectedValues.map((v) => v.ids).flat(this.curChain.length);
              nodes = nodes.filter((item) => !defaultSelectList.includes(`${item.id}&${this.curChain[item.level].id}`));
              this.allTreeData.forEach((item) => {
                if (curSelectList.includes(`${item.id}&${item.name}`) && !item.disabled) {
                  item.checked = currentSelect.length > 0;
                  this.handleNodeChecked(currentSelect.length > 0, item);
                }
              });
            }
            this.$store.commit('setTreeSelectedNode', this.currentSelectedNode);
            this.$emit('on-select-all', nodes, currentSelect.length > 0);
          }
        };
        return typeMap[type]();
      },

      handleSelectChange (selection, node) {
        if (this.isShiftBeingPress) {
          this.pressIndex = this.allTreeData.findIndex((item) => item.id === node.id);
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
    /* margin-right: 10px; */
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
    /* &::before {
      content: '';
      border: 1px dashed #C4C6CC;
    } */
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
    margin-left: 5px;
    margin-right: 10px;
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
    &-no-icon {
      padding-left: 29px;
      &-two-level {
        padding-left: 12px;
      }
    }
    &-none {
      display: none;
    }
    .bk-form-checkbox {
      position: relative;
      margin-right: 0;
      padding: 0;
      /* top: -2px; */
    }
    .tree-node-name {
      padding-left: 10px;
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
    width: 100%;
    position: relative;
    /* padding: 0 18px; */
    line-height: 26px;
    .load-item {
      width: 140px;
      text-align: center;
      margin: 0 auto;
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
  padding: 0 16px;
  .bk-table-empty-block {
    height: calc(100vh - 450px);
  }
  .bk-page.bk-page-align-right {
    padding: 16px;
  }
}

.multiple-topology-tree {
  display: flex;
  background-color: #ffffff;
  &-left {
    position: relative;
    &-content {
      margin-right: 16px;
    }
    &::after {
      content: '';
      position: absolute;
      top: 16px;
      right: 0;
      width: 1px;
      height: 100%;
      background-color: #dcdee5;
    }
  }
}

.iam-topology-tree-only,
.multiple-topology-tree-left-content,
.multiple-topology-tree-right-content {
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

.page-count-tip {
  background-color: #EAEBF0;
  color: #63656e;
  padding: 8px 0;
  margin: 0 16px 8px 16px;
  font-size: 12px;
  text-align: center;
  .selected-count {
    font-weight: 700;
  }
  .clear-select-tip {
    color: #3a84ff;
    cursor: pointer;
    &.is-disabled {
      color: #c4c6cc;
      cursor: not-allowed;
    }
  }
}

.topology-table-pagination {
  display: flex;
  padding: 16px 16px 0 16px;
  position: relative;

  .custom-largest-count {
    font-size: 12px;
    line-height: 36px;
  }
  /deep/ .topology-tree-pagination-cls {
   .bk-page-total-count {
      color: #3f4046;
      font-size: 12px;
    }
    .bk-page-small-jump {
      position: absolute;
      right: 16px;
      .jump-input {
        outline: none;
        min-width: 0;
      }
    }
  }
}
</style>
