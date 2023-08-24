<template>
  <div :class="['iam-render-perm', extCls]">
    <div class="header" @click="handleExpanded">
      <label class="title">{{ title }}</label>
      <template v-if="['action'].includes(mode)">
        <div class="sub-title" v-if="permLength > 0">
          {{ $t(`m.common['共']`) }}
          <span class="number">{{ permLength }}</span>
          {{ $t(`m.common['个']`) }}{{ $t(`m.perm['操作权限']`) }}
        </div>
      </template>
      <template v-if="['member'].includes(mode)">
        <template v-if="userLength > 0 || departLength > 0">
          <div class="sub-title" v-if="userLength > 0">
            {{ $t(`m.common['共']`) }}
            <span class="number">{{ userLength }}</span>
            {{ $t(`m.common['个用户']`) }}，
          </div>
          <div class="sub-title" v-if="departLength > 0">
            {{ $t(`m.common['共']`) }}
            <span class="number">{{ departLength }}</span>
            {{ $t(`m.common['个组织']`) }}
          </div>
        </template>
        <div class="sub-title" v-else>{{ $t(`m.common['全员']`) }}(All)</div>
      </template>
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
    <Icon type="dustbin" class="action" v-if="isShowDelete" @click.stop="handleDelete" />
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      mode: {
        type: String,
        default: 'action'
      },
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
      userLength: {
        type: Number,
        default: 0
      },
      departLength: {
        type: Number,
        default: 0
      },
      extCls: {
        type: String,
        default: ''
      },
      canDelete: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isExpanded: this.expanded
      };
    },
    computed: {
      isShowDelete () {
        return this.canDelete && !this.isExpanded;
      }
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

      handleExpanded () {
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
                display: inline-block;
            }
        }
        &.is-not-expanded:hover {
            .header {
                cursor: pointer;
            }
        }
        .header {
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
        .action {
            display: none;
            position: absolute;
            width: 24px;
            height: 24px;
            top: 21px;
            right: 0;
            font-size: 24px;
            color: #c4c6cc;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
        }
    }
</style>
