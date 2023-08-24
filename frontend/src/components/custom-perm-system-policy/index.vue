<template>
  <div :class="['iam-perm-item', extCls]">
    <div class="header" @click="handleExpanded">
      <Icon bk class="expanded-icon" :type="isExpanded ? 'down-shape' : 'right-shape'" />
      <label class="title">{{ title }}</label>
      <div class="sub-title" v-if="permLength > 0">
        {{ $t(`m.common['共']`) }}
        <span class="number">{{ permLength }}</span>
        {{ $t(`m.common['个']`) }}
        {{ $t(`m.perm['操作权限']`) }}
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
      <p class="expand-action" @click="handleCollapse">
        <Icon :type="isExpanded ? 'up-angle' : 'down-angle'" />
        {{ $t(`m.common['点击收起']`) }}
      </p>
    </div>
  </div>
</template>
<script>
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
      permLength: {
        type: Number,
        default: 0
      },
      extCls: {
        type: String,
        default: ''
      },
      onePerm: {
        type: Number,
        default: 0
      },
      isAllDelete: {
        type: Boolean,
        default: false
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
      }
    },
    created () {
      if (this.onePerm === 1) {
        this.$nextTick(() => {
          this.handleExpanded();
        });
      }
    },
    methods: {
      handleCollapse () {
        this.isExpanded = false;
        this.$emit('update:expanded', false);
        this.$emit('on-expanded', false);
      },

      handleExpanded () {
        this.isExpanded = !this.isExpanded;
        this.$emit('update:expanded', true);
        this.$emit('on-expanded', true);
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
    }
</style>
