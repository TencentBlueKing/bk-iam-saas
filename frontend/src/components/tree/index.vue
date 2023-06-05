<template>
  <ul :class="['bkiam-tree', extCls, { 'bk-has-border-tree': isBorder }]">
    <template v-for="(item, index) in data">
      <li
        @drop="drop(item, $event)"
        @dragover="dragover($event)"
        :key="item[nodeKey] ? item[nodeKey] : item.name"
        :class="{ 'leaf': isLeaf(item),
                  'tree-first-node': !parent && index === 0,
                  'tree-only-node': !parent && data.length === 1,
                  'tree-second-node': !parent && index === 1,
                  'single': !multiple }"
        v-if="item.hasOwnProperty('visible') ? item.visible : true">
        <div
          :class="['tree-drag-node', { 'tree-singe': !multiple }, { 'is-selected': item.id === curSelect }]"
          :draggable="draggable" @dragstart="drag(item, $event)"
          @click.stop="handleNodeClick(item)">
          <Icon
            bk
            v-if="(item.children && item.children.length) || item.async"
            class="tree-expanded-icon"
            :type="item.expanded ? 'down-shape' : 'right-shape'"
            @click.stop="expandNode(item)" />
          <bk-checkbox
            v-if="multiple"
            :true-value="true"
            :false-value="false"
            :indeterminate="item.halfcheck"
            :disabled="item.disabled"
            v-model="item.checked"
            @change="handleCheckboxChange(...arguments, item)">
          </bk-checkbox>
          <span class="node-title" :class="item.id === curSelect ? 'active' : ''" :title="item.name">
            {{ item.name }}
          </span>
          <spin-loading ext-cls="loading" v-if="item.loading" />
        </div>
        <collapse-transition>
          <tree v-if="!isLeaf(item)"
            :drag-after-expanded="dragAfterExpanded"
            :click-trigger-type="clickTriggerType"
            :draggable="draggable"
            :is-broadcast="isBroadcastUse"
            v-show="item.expanded"
            :data="item.children"
            :halfcheck="halfcheck"
            :cur-select="curSelect"
            :parent="item"
            :is-delete-root="isDeleteRoot"
            :multiple="multiple"
            @dropTreeChecked="nodeCheckStatusChange"
            @async-load-nodes="asyncLoadNodes"
            @on-expanded="onExpanded"
            @on-click="onClick"
            @on-check="onCheck"
            @on-broadcast-check="onBroadcastCheck"
            @on-select="onSelect"
            @on-drag-node="onDragNode">
          </tree>
        </collapse-transition>
      </li>
    </template>
    <p class="search-no-data" v-if="isEmpty && searchFlag">{{emptyText}}</p>
  </ul>
</template>
<script>
    /* eslint-disable max-len */

  import CollapseTransition from '../../common/collapse-transition';
  import il8n from '@/language';

  export default {
    name: 'tree',
    components: { CollapseTransition },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      parent: {
        type: Object,
        default: () => null
      },
      multiple: {
        type: Boolean,
        default: false
      },
      nodeKey: {
        type: String,
        default: 'id'
      },
      draggable: {
        type: Boolean,
        default: false
      },
      hasBorder: {
        type: Boolean,
        default: false
      },
      dragAfterExpanded: {
        type: Boolean,
        default: true
      },
      isDeleteRoot: {
        type: Boolean,
        default: false
      },
      isBroadcast: {
        type: Boolean,
        default: true
      },
      emptyText: {
        type: String,
        default: il8n('common', '暂无数据')
      },
      extCls: {
        type: String,
        default: ''
      },
      curSelect: {
        type: [String, Number],
        default: ''
      }
    },
    data () {
      return {
        halfcheck: true,
        isBorder: this.hasBorder,
        bkTreeDrag: {},
        visibleStatus: [],
        isEmpty: false,
        searchFlag: false,
        isBroadcastUse: this.isBroadcast
      };
    },
    watch: {
      data () {
        this.initTreeData();
      },
      hasBorder (value) {
        this.isBorder = !!value;
      },
      isBroadcast (value) {
        this.isBroadcastUse = !!value;
      }
    },
    mounted () {
      this.$on('childChecked', (node, checked) => {
        if (node.children && node.children.length) {
          for (const child of node.children) {
            if (!child.disabled) {
              this.$set(child, 'checked', checked);
            }
            this.$emit('on-broadcast-check', child, checked);
          }
        }
      });

      this.$on('parentChecked', (node, checked) => {
        if (!node.parent) {
          const allChildNodeChecked = node.children.every(node => node.checked);
          const someChildNodeChecked = (node.children.some(node => node.halfcheck) || node.children.some(node => node.checked)) && !allChildNodeChecked;
          if (this.halfcheck) {
            if (!node.disabled) {
              this.$set(node, 'checked', allChildNodeChecked);
              this.$set(node, 'halfcheck', someChildNodeChecked);
            }
          }
          return false;
        }

        if (!node.parent.children.filter(child => child[this.nodeKey] === node[this.nodeKey]).length && !node.disabled) {
          this.$set(node, 'checked', checked);
        }

        const allBortherNodeChecked = node.parent.children.every(node => node.checked);
        const someBortherNodeChecked = (node.parent.children.some(node => node.halfcheck) || node.parent.children.some(node => node.checked)) && !allBortherNodeChecked;
        if (this.halfcheck) {
          if (allBortherNodeChecked) {
            this.$set(node.parent, 'halfcheck', false);
            this.$set(node.parent, 'checked', true);
          } else {
            if (someBortherNodeChecked) {
              this.$set(node.parent, 'halfcheck', true);
              this.$set(node.parent, 'checked', false);
            } else {
              this.$set(node.parent, 'halfcheck', false);
              this.$set(node.parent, 'checked', false);
            }
          }
          if (!checked && someBortherNodeChecked) {
            this.$set(node.parent, 'halfcheck', true);
          }
          this.$emit('parentChecked', node.parent, checked);
        } else {
          if (checked && allBortherNodeChecked) this.$emit('parentChecked', node.parent, checked);
          if (!checked) this.$emit('parentChecked', node.parent, checked);
        }
      });

      this.$on('on-broadcast-check', (node, checked) => {
        // 根节点下无子节点需异步加载数据时 不进行check事件的传递
        if (!node.parent && !node.children) {
          return;
        }
        this.$emit('parentChecked', node, checked);
        this.$emit('childChecked', node, checked);
        this.$emit('dropTreeChecked', node, checked);
      });

      this.$on('toggleshow', (node, isShow) => {
        this.$set(node, 'visible', isShow);
        this.visibleStatus.push(node.visible);
        if (this.visibleStatus.every(item => !item)) {
          this.isEmpty = true;
          return;
        }
        if (isShow && node.parent) {
          this.searchFlag = false;
          this.$emit('toggleshow', node.parent, isShow);
        }
      });

      this.$on('cancelSelected', (root) => {
        for (const child of root.$children) {
          for (const node of child.data) {
            child.$set(node, 'selected', false);
          }
          if (child.$children) child.$emit('cancelSelected', child);
        }
      });

      this.initTreeData();
    },
    destroyed () {
      this.$delete(window, 'bkTreeDrag');
    },
    methods: {
      gid () {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
          const r = Math.random() * 16 | 0;
          const v = c === 'x' ? r : (r & 0x3 | 0x8);
          return v.toString(16);
        });
      },

      setDragNode (id, node) {
        window['bkTreeDrag'] = {};
        window['bkTreeDrag'][id] = node;
      },

      getDragNode (id) {
        return window['bkTreeDrag'][id];
      },

      hasInGenerations (root, node) {
        if (root.hasOwnProperty('children') && root.children) {
          for (const rn of root.children) {
            if (rn === node) return true;
            if (rn.children) return this.hasInGenerations(rn, node);
          }
          return false;
        }
      },

      /**
       * 节点拖拽
       *
       * @param {Object} node 当前拖拽节点
       * @param {Object} ev   $event
       */
      drop (node, ev) {
        ev.preventDefault();
        ev.stopPropagation();
        const gid = ev.dataTransfer.getData('gid');
        const drag = this.getDragNode(gid);
        // if drag node's parent is enter node or root node
        if (drag.parent === node || drag.parent === null || drag === node) return false;
        // drag from parent node to child node
        if (this.hasInGenerations(drag, node)) return false;
        const dragHost = drag.parent.children;
        if (node.children && node.children.indexOf(drag) === -1) {
          node.children.push(drag);
          dragHost.splice(dragHost.indexOf(drag), 1);
        } else {
          this.$set(node, 'children', [drag]);
          dragHost.splice(dragHost.indexOf(drag), 1);
        }
        this.$set(node, 'expanded', this.dragAfterExpanded);
        this.$emit('on-drag-node', { dragNode: drag, targetNode: node });
      },

      drag (node, ev) {
        const gid = this.gid();
        this.setDragNode(gid, node);
        ev.dataTransfer.setData('gid', gid);
      },

      dragover (ev) {
        ev.preventDefault();
        ev.stopPropagation();
      },

      initTreeData () {
        for (const node of this.data) {
          this.$set(node, 'parent', this.parent);
          if (this.multiple) {
            if (node.hasOwnProperty('selected')) {
              this.$delete(node, 'selected');
            }
            if (node.checked && this.isBroadcastUse) {
              this.$emit('on-broadcast-check', node, true);
            }
          } else {
            if (node.hasOwnProperty('checked')) {
              this.$delete(node, 'checked');
            }
          }
        }
      },

      expandNode (node) {
        this.$set(node, 'expanded', !node.expanded);
        if (node.async && !node.children) {
          this.$emit('async-load-nodes', node);
        }
        if (node.children && node.children.length) {
          this.$emit('on-expanded', node, node.expanded);
        }
      },

      onExpanded (node) {
        if (node.children && node.children.length) {
          this.$emit('on-expanded', node, node.expanded);
        }
      },

      asyncLoadNodes (node) {
        if (node.async && !node.children) {
          this.$emit('async-load-nodes', node);
        }
      },

      isLeaf (node) {
        return !(node.children && node.children.length) && node.parent && !node.async;
      },

      addNode (parent, newNode) {
        let addnode = {};
        this.$set(parent, 'expanded', true);
        if (typeof newNode === 'undefined') {
          throw new ReferenceError('newNode is required but undefined');
        }
        if (typeof newNode === 'object' && !newNode.hasOwnProperty('name')) {
          throw new ReferenceError('the name property is missed');
        }
        if (typeof newNode === 'object' && !newNode.hasOwnProperty(this.nodeKey)) {
          throw new ReferenceError('the nodeKey property is missed');
        }
        if (typeof newNode === 'object' && newNode.hasOwnProperty('name') && newNode.hasOwnProperty(this.nodeKey)) {
          addnode = Object.assign({}, newNode);
        }
        if (this.isLeaf(parent)) {
          this.$set(parent, 'children', []);
          parent.children.push(addnode);
        } else {
          parent.children.push(addnode);
        }
        this.$emit('addNode', { parentNode: parent, newNode: newNode });
      },

      addNodes (parent, newChildren) {
        for (const n of newChildren) {
          this.addNode(parent, n);
        }
      },

      handleNodeClick (node) {
        this.$emit('on-click', node);
      },

      onClick (node) {
        this.$emit('on-click', node);
      },

      onCheck (node, checked) {
        this.$emit('on-check', node, checked);
      },

      /**
       * 节点复选框 change 事件 触发传递给子节点
       *
       * @param {Object} node 当前节点
       * @param {Boolean} checked 选中状态
       */
      onBroadcastCheck (node, checked) {
        this.$emit('on-broadcast-check', node, checked);
      },

      onSelect (newVal, node) {
        this.$emit('on-select', newVal, node);
      },

      nodeCheckStatusChange (node, checked) {
        this.$emit('dropTreeChecked', node, checked);
      },

      onDragNode (event) {
        this.$emit('on-drag-node', event);
      },

      delNode (parent, node) {
        if (parent === null || typeof parent === 'undefined') {
          // isDeleteRoot 为false时不可删除根节点
          if (this.isDeleteRoot) {
            this.data.splice(0, 1);
          } else {
            throw new ReferenceError('the root element can\'t deleted!');
          }
        } else {
          parent.children.splice(parent.children.indexOf(node), 1);
        }
        this.$emit('delNode', { parentNode: parent, delNode: node });
      },

      handleCheckboxChange (newVal, oldVal, val, node) {
        this.$emit('on-check', node, newVal);
        if (this.isBroadcastUse) {
          this.$emit('on-broadcast-check', node, newVal);
        }
      },

      nodeSelected (node) {
        const getRoot = (el) => {
          if (el.$parent.$el.nodeName === 'UL') {
            el = el.$parent;
            return getRoot(el);
          } return el;
        };
        const root = getRoot(this);
        if (!this.multiple) {
          for (const rn of root.data || []) {
            this.$set(rn, 'selected', false);
            this.$emit('cancelSelected', root);
          }
        }
        // 当为多选时 必须通过选择复选框触发
        // if (this.multiple) this.$set(node, 'checked', !node.selected)
        this.$set(node, 'selected', !node.selected);
        this.$emit('on-click', node);
      },

      /**
       * 节点数据处理
       *
       * @param {Object} opt 参数设置
       * @param {Array}  data 根节点或子节点数组
       * @param {Array/String}  keyParton 自定义键值
       */
      nodeDataHandler (opt, data, keyParton) {
        data = data || this.data;
        let res = [];
        const keyValue = keyParton;
        for (const node of data) {
          for (const [key, value] of Object.entries(opt)) {
            if (node[key] === value) {
              if (!keyValue.length || !keyValue) {
                const n = Object.assign({}, node);
                delete n['parent'];
                if (!(n.children && n.children.length)) {
                  res.push(n);
                }
              } else {
                const n = {};
                if (Object.prototype.toString.call(keyValue) === '[object Array]') {
                  for (let i = 0; i < keyValue.length; i++) {
                    if (node.hasOwnProperty(keyValue[i])) {
                      n[keyValue[i]] = node[keyValue[i]];
                    }
                  }
                }
                if (Object.prototype.toString.call(keyValue) === '[object String]') {
                  n[keyValue] = node[keyValue];
                }
                if (!(node.children && node.children.length)) {
                  res.push(n);
                }
              }
            }
          }
          if (node.children && node.children.length) {
            res = res.concat(this.nodeDataHandler(opt, node.children, keyValue));
          }
        }
        return res;
      },

      getNode (keyParton) {
        if (!this.multiple) {
          return this.nodeDataHandler({ selected: true }, this.data, keyParton);
        } else {
          return this.nodeDataHandler({ checked: true }, this.data, keyParton);
        }
      },

      searchNode (filter, data) {
        this.searchFlag = true;
        data = data || this.data;
        for (const node of data) {
          const searched = filter ? (typeof filter === 'function' ? filter(node) : node['name'].indexOf(filter) > -1) : false;
          this.$set(node, 'searched', searched);
          this.$set(node, 'visible', false);
          this.$emit('toggleshow', node, filter ? searched : true);
          if (node.children && node.children.length) {
            if (searched) this.$set(node, 'expanded', true);
            this.visibleStatus.splice(0, this.visibleStatus.length, ...[]);
            this.searchNode(filter, node.children);
          }
        }
      }
    }
  };
</script>
<style lang="postcss">
    @import './index.css';
</style>
