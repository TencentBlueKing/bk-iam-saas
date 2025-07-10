<template>
  <div v-if="permLength > 0" :class="['iam-perm-item', extCls, `${$route.name}-perm-item`]" :ref="customPermRef">
    <div class="header" @click.stop="handleExpanded(isExpanded)" v-if="!isOnlyPerm">
      <Icon bk class="expanded-icon" :type="isExpanded ? 'down-shape' : 'right-shape'" />
      <span class="title">{{ title }}</span>
      <template>
      </template>
      <div class="sub-title">
        <template v-if="['userOrgPerm'].includes($route.name)">
          ({{ $t(`m.common['共']`) }}
          <span class="number">{{ permLength }}</span>
          {{ $t(`m.common['条']`) }})
        </template>
        <template v-else>
          {{ $t(`m.common['共']`) }}
          <span class="number">{{ permLength }}</span>
          {{ $t(`m.common['个']`) }}{{ typeTitle }}
        </template>
        <span
          v-if="isAllDelete"
          class="del-all-icon">
          <Icon type="delete-line" @click.stop="handleDeleteAll" />
        </span>
      </div>
    </div>
    <div class="content" v-if="isExpanded">
      <div class="slot-content">
        <slot />
      </div>
      <p v-if="showCollapse" class="expand-action" @click="handleCollapse">
        <Icon :type="isExpanded ? 'up-angle' : 'down-angle'" />
        {{ $t(`m.common['点击收起']`) }}
      </p>
    </div>
  </div>
</template>
<script>
  import il8n from '@/language';
  export default {
    name: 'CustomPermSystemPolicy',
    props: {
      expanded: {
        type: Boolean,
        default: false
      },
      title: {
        type: String,
        default: ''
      },
      typeTitle: {
        type: String,
        default: il8n('perm', '操作权限')
      },
      permLength: {
        type: Number,
        default: 0
      },
      extCls: {
        type: String,
        default: ''
      },
      customPermRef: {
        type: String,
        default: ''
      },
      onePerm: {
        type: Number,
        default: 0
      },
      isOnlyPerm: {
        type: Boolean,
        default: false
      },
      isAllDelete: {
        type: Boolean,
        default: false
      },
      showCollapse: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        isExpanded: this.expanded
      };
    },
    watch: {
      expanded (value) {
        this.isExpanded = !!value;
      },
      onePerm: {
        handler (value) {
          if (value === 1) {
            this.$nextTick(() => {
              this.handleExpanded(false);
            });
          } else {
            this.isExpanded = false;
          }
        },
        immediate: true,
        deep: true
      }
    },
    methods: {
      handleCollapse () {
        this.isExpanded = false;
        this.$emit('update:expanded', false);
        this.$emit('on-expanded', false);
      },

      handleExpanded (payload) {
        this.isExpanded = !payload;
        this.$emit('update:expanded', this.isExpanded);
        this.$emit('on-expanded', this.isExpanded);
      },
      
      handleDeleteAll () {
        this.$emit('on-delete-all');
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-perm-item {
        background: #fff;
        border-radius: 2px;
        border: 1px solid #fff;
        box-shadow: 0px 1px 2px 0px rgba(49, 50, 56, .1);
        &:hover {
            box-shadow: 0px 2px 4px 0px rgba(49, 50, 56, .15);
        }
        &.is-not-expanded:hover {
            .header {
                cursor: pointer;
            }
        }
        .header {
            display: flex;
            justify-content: flex-start;
            position: relative;
            padding: 0 30px;
            height: 40px;
            line-height: 40px;
            font-size: 12px;
            color: #63656e;
            border-radius: 2px;
            cursor: pointer;
            .expanded-icon {
                position: absolute;
                top: 15px;
                left: 10px;
            }
            .title {
                font-weight: 600;
            }
            .sub-title {
                margin-left: 10px;
                color: #979ba5;
                .number {
                    font-weight: 600;
                }
            }
            .del-all-icon {
              margin-left: 5px;
              font-size: 14px;
            }
        }
        .content {
            position: relative;
            .expand-action {
                padding: 20px 0 5px 0;
                width: 100%;
                line-height: 16px;
                font-size: 12px;
                color: #979ba5;
                text-align: center;
                cursor: pointer;
                i {
                    font-size: 16px;
                }
            }
            .slot-content {
                padding: 0 30px 0 30px;
            }
        }
        &.only-perm-item-wrapper {
          margin-bottom: 0 !important;
          box-shadow: none;
          .content {
            .slot-content {
              padding: 0;
            }
            .expand-action {
              display: none;
            }
          }
        }

        &.userOrgPerm-perm-item {
          box-shadow: 0 2px 4px 0 #1919290d;
          &:not(&:last-of-type) {
            margin-bottom: 12px;
          }
          .header {
            display: flex;
            align-items: center;
            height: 46px;
            line-height: 46px;
            padding: 0 32px;
            .expanded-icon {
              top: 18px;
            }
          }
          .title {
            color: #313238;
            font-weight: 700;
          }
          .sub-title {
            margin-left: 4px;
            color: #63656e;
          }
          .number {
            color: #3a84ff;
            font-weight: 700;
          }
          .content {
            .slot-content {
              padding: 0 24px;
              padding-bottom: 10px;
            }
          }
        }
    }
</style>
