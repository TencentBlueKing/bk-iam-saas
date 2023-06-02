<template>
  <div :class="['iam-topology-tree', { 'bk-has-border-tree': isBorder }]">
    <!-- eslint-disable max-len -->
    <div class="ghost-wrapper" :style="ghostStyle"></div>
    <div class="render-wrapper" ref="content">
      <div
        v-for="(item, index) in allData"
        :key="item.nodeId"
        :class="[
          'node-item',
          { 'load-more-node': item.type === 'load' },
          { 'search-node': item.type === 'search' },
          { 'can-hover': item.type === 'node' && !item.loading }
        ]"
        :style="getNodeStyle(item)"
        v-show="item.visiable"
      >
        <template v-if="item.type === 'node'">
          <Icon
            v-if="item.async"
            bk
            :type="item.expanded ? 'down-shape' : 'right-shape'"
            :class="['arrow-icon', { 'is-disabled': getExpandedDisabled(index) || isExistAsync(item) }]"
            @click.stop="expandNode(item, index)"
          />
          <div class="block" v-if="getComputedDisplay(item)">unit</div>
          <div class="node-radio" @click.stop>
            <bk-checkbox
              :true-value="true"
              :false-value="false"
              :disabled="item.disabled"
              v-model="item.checked"
              ext-cls="iam-topology-title-cls"
              :title="`ID：${item.id}`"
              data-test-id="topology_checkbox_chooseip"
              @change="handleNodeChange(...arguments, item, index)"
            >
              <span
                class="tree-node-name single-hide"
                :style="dragDynamicWidth(item)"
                :title="item.name"
              >
                {{ item.name }}
              </span>
            </bk-checkbox>
          </div>
          <div
            class="search-icon"
            v-if="item.async && item.type === 'node' && !item.loading"
            @click.stop="handleOpenSearch(item, index)"
          >
            <Icon bk type="search" />
          </div>
        </template>
        <template v-else-if="item.type === 'load'">
          <div class="load-more-wrapper">
            <div
              :class="[
                'load-item',
                { 'loading-more': item.loadingMore },
                { normal: !item.loadingMore && !isExistNodeLoadMore },
                { 'exist-load-more': isExistNodeLoadMore }
              ]"
              @click="loadMore(item, index)"
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
        <template v-else-if="item.type === 'search-empty'">
          <div class="search-empty-wrapper">
            <ExceptionEmpty
              style="background: #fafbfd"
              :type="item.name === $t(`m.common['搜索结果为空']`) ? 'search-empty' : 500"
              :tip-type="item.name === $t(`m.common['搜索结果为空']`) ? 'search' : 'refresh'"
              :empty-text="item.name === $t(`m.common['搜索结果为空']`) ? item.name : '数据不存在'"
              @on-clear="handleEmptyClear(...arguments, item, index)"
              @on-refresh="handleEmptyRefresh(...arguments, item, index)"
            />
          </div>
        </template>
        <template v-else-if="item.type === 'search-loading'">
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
        </template>
      </div>
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
      searchValue: {
        type: Array,
        default: []
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
        offsetWidth: 180
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
          const offsetWidth = this.getDragDynamicWidth() > 220 ? 180 + this.getDragDynamicWidth() - 220 : 180;
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
              maxWidth: offsetWidth - ((payload.level + 1) * this.leftBaseIndent) - asyncLevelWidth - searchIconWidth + 'px'
            };
          }
          if (isSameLevelExistSync && ['search', 'search-empty'].includes(payload.type)) {
            return {
              maxWidth: offsetWidth - ((payload.level + 1) * this.leftBaseIndent) + 'px'
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

      handleSearch (value, node, index) {
        this.$emit('on-search', { value, node, index });
      },

      handleEmptyClear (payload, item) {
        this.$nextTick(() => {
          this.$refs[`topologyInputRef${this.levelIndex}`][0].value = '';
        });
      },

      handleEmptyRefresh () {
        this.$nextTick(() => {
          this.$refs[`topologyInputRef${this.levelIndex}`][0].value = '';
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
          if (flag) {
            return {
              paddingLeft: `${this.leftBaseIndent + asyncIconWidth}px`
            };
          }
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
        this.$emit('on-select', newVal, node);
      }
    }
  };
</script>
<style lang="postcss">
.iam-topology-tree {
  height: 376px;
  padding: 10px 0;
  font-size: 14px;
  overflow: auto;
  position: relative;

  /*滚动条整体样式*/
  &::-webkit-scrollbar {
    width: 6px; /*竖向滚动条的宽度*/
    height: 6px; /*横向滚动条的高度*/
  }
  /*滚动条里面的小方块*/
  &::-webkit-scrollbar-thumb {
    background: #dcdee5;
    border-radius: 3px;
  }
  /*滚动条轨道的样式*/
  &::-webkit-scrollbar-track {
    background: transparent;
    border-radius: 3px;
  }

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
    }
    &.can-hover:hover {
      .search-icon {
        display: inline-block;
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
        line-height: 1;
        vertical-align: middle;
    }
  }

  .node-radio {
    display: inline-block;
    .bk-form-checkbox {
      position: relative;
      margin-right: 0;
      padding: 0;
      top: -2px;
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
      background: #fafbfd !important;
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
