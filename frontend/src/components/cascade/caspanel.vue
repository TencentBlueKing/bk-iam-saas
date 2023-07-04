<template>
  <div class="bk-cascade-panel">
    <ul v-if="list.length"
      class="bk-cascade-panel-ul"
      :class="{ 'bk-cascade-border': childrenList && childrenList.length }"
      :style="{
        width: scrollWidth + 'px'
      }">
      <iam-cascade-option-item
        v-for="(item, index) in list"
        :key="index"
        :item="item"
        :selected-item="selectedItem"
        :multiple="multiple"
        :is-remote="isRemote"
        @click.native.stop="cascadeClick(item)"
        @mouseenter.native.stop="cascadeHover(item)"
        @handleCheckItem="handleCheckItem">
        <template slot="prepend" slot-scope="{ node }">
          <slot name="prepend" :node="node"></slot>
        </template>
      </iam-cascade-option-item>
    </ul>
    <ul v-else
      class="bk-cascade-panel-ul"
      style="width: 100%">
      <li class="bk-option-none">
        <span>{{ $t(`m.common['暂无数据']`) }}</span>
      </li>
    </ul>
    <iam-cascade-caspanel
      v-if="childrenList && childrenList.length"
      :list="childrenList"
      :trigger="trigger"
      :disabled="disabled"
      :multiple="multiple"
      :check-any-level="checkAnyLevel"
      :is-remote="isRemote"
      :remote-method="remoteMethod"
      @updateSelectedList="updateSelectedList">
      <template slot="prepend" slot-scope="{ node }">
        <slot name="prepend" :node="node"></slot>
      </template>
    </iam-cascade-caspanel>
  </div>
</template>
<script>
  import iamCascadeOptionItem from './option-item.vue';
  import cascadeInfo from './cascade.js';

  export default {
    name: 'iamCascadeCaspanel',
    components: { iamCascadeOptionItem },
    mixins: [cascadeInfo],
    props: {
      list: {
        type: Array,
        default: () => ([])
      },
      trigger: {
        type: String,
        default: ''
      },
      scrollWidth: {
        type: Number,
        default: 160
      },
      multiple: {
        type: Boolean,
        default: false
      },
      disabled: {
        type: Boolean,
        default: false
      },
      checkAnyLevel: {
        type: Boolean,
        default: false
      },
      isRemote: {
        type: Boolean,
        default: false
      },
      remoteMethod: {
        type: Function
      }
    },
    data () {
      return {
        childrenList: [],
        selectedList: [],
        selectedItem: {},
        multipleSeleted: []
      };
    },
    mounted () {
      this.$on('change-selected', (params) => {
        const idInfo = params.idList;
        const valueList = [...idInfo];
        for (let i = 0; i < valueList.length; i++) {
          for (let j = 0; j < this.list.length; j++) {
            if (valueList[i] === this.list[j].id) {
              this.handleItemFn(this.list[j], true);
              valueList.splice(0, 1);
              this.$nextTick(() => {
                this.broadcast('iamCascadeCaspanel', 'change-selected', {
                  idList: valueList
                });
              });
              return false;
            }
          }
        }
      });
      this.$on('multiple-selected', (params) => {
        const valueList = params.idList;
        // 改变最终选中态
        const changeCheckStatus = (arr) => {
          arr.forEach(item => {
            if (valueList[valueList.length - 1] === item.id) {
              item.isSelected = params.isSelected;
              item.isIndeterminate = false;
              this.handleItemFn(item, true);
            }
            if (item.children && item.children.length) {
              changeCheckStatus(item.children);
            }
          });
        };
        changeCheckStatus(this.list);
      });
      this.$on('on-clear', () => {
        this.childrenList = [];
        this.selectedItem = {};
      });
    },
    methods: {
      // 点击事件
      cascadeClick (item) {
        if (this.trigger !== 'click' && item.children && item.children.length) return;
        this.handleItem(item, false);
      },
      cascadeHover (item) {
        if (this.trigger === 'hover' && item.children && item.children.length) {
          this.handleItem(item, false);
        }
      },
      handleItem (item, fromInit = false) {
        if (item.disabled) return;

        if (this.isRemote) {
          new Promise((resolve, reject) => {
            this.remoteMethod(item, resolve);
          }).then(() => {
            this.handleItemFn(item, fromInit);
          }).catch(() => {
            // console.error('catch')
          }).finally(() => {
            item.isLoading = false;
          });
        } else {
          this.handleItemFn(item, fromInit);
        }
      },
      handleItemFn (item, fromInit) {
        if (item.parent) {
          if (!item.children || !item.children.length) {
            return;
          }
        }
        // 清空数据
        this.broadcast('iamCascadeCaspanel', 'on-clear');
        this.childrenList = (item.children && item.children.length) ? item.children : [];
        // 当父级数据选中时，子集数据也选中(多选)
        if (this.multiple && this.childrenList.length) {
          // 使用递归对子集的子集也进行选中的操作
          if (!this.checkAnyLevel) {
            const childrenRecursive = (arr) => {
              arr.forEach(child => {
                this.childSelected(child, item);
                this.childIndeterminate(child, item);
                if (child.children && child.children.length) {
                  childrenRecursive(child.children);
                }
              });
            };
            childrenRecursive(this.childrenList);
          }
        }
        // 子集展示
        if (this.checkAnyLevel
          || (item.id !== this.selectedItem.id || item.name !== this.selectedItem.name)
          || (item.id === this.selectedItem.id && item.name === this.selectedItem.name)
        ) {
          this.selectedItem = item;
          this.emitUpdate([item]);
        }
        // multiple将数据存储在公共的一个选中的数组中
        if (this.multiple) {
          // 触发多选方法事件
          this.dispatch('iamCascade', 'on-multiple-change', {
            item: item,
            checkAnyLevel: this.checkAnyLevel,
            fromInit: fromInit
          });
        } else {
          this.dispatch('iamCascade', 'on-id-change', {
            item: item,
            isLast: !(item.children && item.children.length),
            checkAnyLevel: this.checkAnyLevel,
            fromInit: fromInit
          });
        }
        // 判断popoverWidth的层级
        this.dispatch('iamCascade', 'on-popover-width', {
          item: item
        });
      },
      childSelected (child, item) {
        if (child.disabled || (!item.isSelected && !item.isIndeterminate)) {
          child.isSelected = false;
        } else if (item.isSelected) {
          child.isSelected = true;
        }
      },
      childIndeterminate (child, item) {
        if (child.disabled || (!item.isSelected && !item.isIndeterminate) || item.isSelected) {
          child.isIndeterminate = false;
        }
      },
      updateSelectedList (item) {
        this.selectedList = [this.selectedItem].concat(item);
        // 在每一个caspanel里面做自己的数据处理
        if (!this.checkAnyLevel) {
          item.forEach(itemItem => {
            if (itemItem.children && itemItem.children.length) {
              // eslint-disable-next-line max-len
              itemItem.isSelected = itemItem.children.every(child => (child.isSelected || child.disabled));
              itemItem.isIndeterminate = itemItem.isSelected
                ? false
                : itemItem.children.some(child => (child.isSelected || child.isIndeterminate));
            }
          });
        }
        this.emitUpdate(this.selectedList);
      },
      emitUpdate (selectedList) {
        this.$emit('updateSelectedList', selectedList);
      },
      handleCheckItem (item) {
        item.isSelected = !item.isSelected;
        item.isIndeterminate = false;
      }
    }
  };
</script>
