<template>
  <ul :class="['iam-attach-tree', extCls, { 'iam-attach-has-border-tree': isBorder }]">
    <template v-for="(item, index) in data">
      <li
        :key="item[nodeKey] ? item[nodeKey] : item.name"
        v-if="item.hasOwnProperty('visible') ? item.visible : true"
        :class="{ 'tree-first-node': !parent && index === 0,
                  'tree-only-node': !parent && data.length === 1,
                  'tree-second-node': !parent && index === 1,
                  'single': true }">
        <div class="tree-node" :class="item.isRelateActionEmpty ? 'set-padding-bottom' : ''">
          <span class="node-title" :title="item.name">
            <template v-if="item.tag === 'delete'">
              <s style="color: #c4c6cc;">{{ item.name }}</s>
            </template>
            <template v-else-if="item.tag === 'add'">
              <span class="add-status-sign"></span>
              {{ item.name }}
            </template>
            <template v-else>
              {{ item.name }}
            </template>
          </span>
          <template v-if="!item.isRelateActionEmpty">
            <div :class="['relate-actions',
                          { 'relate-actions-has-children': hasChild(item) },
                          { 'relate-actions-is-view': isBeingView(item) }]">
              <div class="relate-action-item"
                v-for="relate in item.related_actions"
                :key="relate.id">
                <render-tag
                  v-if="relate.tag !== 'unchecked'"
                  :status="relate.tag"
                  :content="relate.name" />
              </div>
            </div>
          </template>
        </div>
        <collapse-transition>
          <tree
            v-if="!isLeaf(item)"
            v-show="item.expanded"
            :data="item.children"
            :is-view="isView"
            :parent="item" />
        </collapse-transition>
      </li>
    </template>
  </ul>
</template>
<script>
  import CollapseTransition from '@/common/collapse-transition';
  import RenderTag from '@/components/render-span/tag';
  export default {
    name: 'tree',
    components: {
      CollapseTransition,
      RenderTag
    },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      parent: {
        type: Object,
        default: () => {
          return null;
        }
      },
      nodeKey: {
        type: String,
        default: 'id'
      },
      hasBorder: {
        type: Boolean,
        default: false
      },
      extCls: {
        type: String,
        default: ''
      },
      isView: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isBorder: this.hasBorder
      };
    },
    computed: {
      hasChild () {
        return payload => {
          return payload.related_actions.some(item => item.tag !== 'unchecked')
            && (payload.children && payload.children.length > 0)
            && payload.children.some(item => !item.isRelateActionEmpty || item.tag !== 'unchecked');
        };
      },
      isBeingView () {
        return payload => {
          return this.isView
            && payload.children
            && payload.children.length > 0
            && payload.children.some(
              child => !child.isRelateActionEmpty || (child.children && child.children.length > 0)
            );
        };
      }
    },
    watch: {
      data () {
        this.initTreeData();
      },
      hasBorder (value) {
        this.isBorder = !!value;
      }
    },
    mounted () {
      this.initTreeData();
    },
    methods: {
      initTreeData () {
        for (const node of this.data) {
          this.$set(node, 'parent', this.parent);
        }
      },

      isLeaf (node) {
        return !(node.children && node.children.length) && node.parent && !node.async;
      }
    }
  };
</script>
<style lang="postcss">
    .fade-enter-active, .fade-leave-active {
        transition: opacity .2s
    }
    .fade-enter, .fade-leave-to {
        opacity: 0
    }
    .iam-attach-tree {
        padding: 0 20px;
        font-size: 14px;
        transition: .3s height ease-in-out, .3s padding-top ease-in-out, .3s padding-bottom ease-in-out;
        .expand-enter-active {
            transition: all 3s ease;
            height: 50px;
            overflow: hidden;
        }
        .expand-leave-active {
            transition: all 3s ease;
            height: 0px;
            overflow: hidden;
        }
        .expand-enter, .iam-attach-tree .expand-leave {
            height: 0;
            opacity: 0;
        }
        ul {
            min-width: 150px;
            box-sizing: border-box;
            list-style-type: none;
            text-align: left;
            padding-left: 18px;
        }
        li {
            position: relative;
            margin: 0;
            list-style: none;
            list-style-type: none;
            text-align: left;
        }
        .tree-node {
            line-height: 26px;
            &.set-padding-bottom {
                padding-bottom: 10px;
            }
            .tree-expanded-icon {
                display: inline-block;
                color: #c0c4cc;
                cursor: pointer;
                vertical-align: middle;
            }
            .relate-actions {
                position: relative;
                padding-left: 15px;
                /* &::before {
                    content: '';
                    left: 3px;
                    position: absolute;
                    right: auto;
                    border-width: 1px;
                    border-left: 1px dashed #c4c6cc;
                    bottom: 50px;
                    height: 100%;
                    top: -3px;
                } */
                &.relate-actions-is-view::before {
                    content: '';
                    left: 3px;
                    position: absolute;
                    right: auto;
                    border-width: 1px;
                    border-left: 1px dashed #c4c6cc;
                    bottom: 50px;
                    height: 100%;
                    top: -3px;
                }
                &.relate-actions-has-children::before {
                    content: '';
                    left: 3px;
                    position: absolute;
                    right: auto;
                    border-width: 1px;
                    border-left: 1px dashed #c4c6cc;
                    bottom: 50px;
                    height: 100%;
                    top: -3px;
                }
                .relate-action-item {
                    display: inline-block;
                    margin: 0 4px 4px 0;
                }
            }
        }
        .node-title {
            display: inline-block;
            max-width: 180px;
            font-size: 12px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            vertical-align: top;
            .add-status-sign {
                display: inline-block;
                position: relative;
                top: -3px;
                width: 5px;
                height: 5px;
                border: 1px solid #10c178;
                background: #85dcb8;
                border-radius: 50%;
            }
        }
    }
    .iam-attach-tree > ul {
        padding-left: 0
    }
    .iam-attach-has-border-tree {
        li:before {
            content: '';
            position: absolute;
            right: auto;
            border-width: 1px;
            border-left: 1px dashed #c4c6cc;
            bottom: 50px;
            height: 100%;
            left: -15px;
            top: -11px;
            width: 1px;
        }
        li:after {
            content: '';
            position: absolute;
            top: 13px;
            right: auto;
            left: -15px;
            height: 20px;
            width: 14px;
            border-width: 1px;
            border-top: 1px dashed #c4c6cc;
        }
        li:last-child::before {
            height: 26px
        }
        li.single:before {
            top: -15px;
        }
        li.single:after {
            top: 12px;
        }
    }
    .iam-attach-has-border-tree > li.tree-first-node:before {
        top: 17px;
    }
    .iam-attach-has-border-tree > li.tree-second-node:before {
        top: 4px;
    }
    .iam-attach-has-border-tree > li.tree-first-node.tree-only-node::before {
        border-left: none;
    }
    .iam-attach-has-border-tree > li.tree-only-node:after {
        border-top: none;
    }

</style>
