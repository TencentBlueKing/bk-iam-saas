<template>
  <div :class="['iam-render-perm', extCls]">
    <div class="header" @click="handleExpanded">
      <label class="title">{{ title }}</label>
      <div class="sub-title" v-if="count > 0">
        {{ $t(`m.common['共']`) }}
        <span class="number">{{ count }}</span>
        {{ $t(`m.common['个']`) }}
        {{ $t(`m.perm['操作权限']`) }}
      </div>
      <div class="action">
        <div class="edit" @click.stop="handleEdit">
          <Icon type="edit-fill" />
        </div>
        <Icon type="close-small" class="delete" @click.stop="handleDelete" />
      </div>
    </div>
    <div class="content" v-if="isExpanded">
      <div class="slot-content">
        <slot />
      </div>
      <p class="expand-action" @click="handlePackup">
        <Icon :type="isExpanded ? 'up-angle' : 'down-angle'" />
        {{ $t(`m.common['点击收起']`) }}
      </p>
    </div>
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      expanded: {
        type: Boolean,
        default: false
      },
      title: {
        type: String,
        default: ''
      },
      count: {
        type: Number,
        default: 0
      },
      extCls: {
        type: String,
        default: ''
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
    methods: {
      handlePackup () {
        this.isExpanded = false;
        this.$emit('update:expanded', false);
        this.$emit('on-expanded', false);
      },

      handleDelete () {
        this.$emit('on-delete');
      },

      handleEdit () {
        this.$emit('on-edit');
      },

      handleExpanded () {
        // if (this.isExpanded) {
        //     return
        // }
        this.isExpanded = !this.isExpanded;
        this.$emit('update:expanded', true);
        this.$emit('on-expanded', true);
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-render-perm {
        position: relative;
        background: #fff;
        border-radius: 2px;
        border: 1px solid #fff;
        box-shadow: 0px 1px 2px 0px rgba(49, 50, 56, .1);
        &:hover {
            box-shadow: 0px 2px 4px 0px rgba(49, 50, 56, .15);
            .action {
                display: block;
            }
        }
        &.is-not-expanded:hover {
            .header {
                cursor: pointer;
            }
        }
        .header {
            position: relative;
            display: flex;
            justify-content: flex-start;
            padding: 0 30px;
            height: 64px;
            line-height: 60px;
            font-size: 14px;
            color: #63656e;
            border-radius: 2px;
            cursor: pointer;
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
            .action {
                position: absolute;
                right: 30px;
                .edit {
                    display: inline-block;
                    width: 26px;
                    height: 26px;
                    line-height: 26px;
                    text-align: center;
                    color: #979ba5;
                    cursor: pointer;
                }
                .delete {
                    position: relative;
                    top: 4px;
                    font-size: 26px;
                    color: #979ba5;
                    cursor: pointer;
                }
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
