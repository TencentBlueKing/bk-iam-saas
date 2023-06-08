<template>
  <div :class="['iam-perm-item', extCls]">
    <div class="header" @click="handleExpanded">
      <Icon bk class="expanded-icon" :type="isExpanded ? 'down-shape' : 'right-shape'" />
      <label class="title">{{ title }}</label>
      <div class="sub-title" v-if="templateCount > 0">
        {{ $t(`m.common['关联']`) }}
        <span class="number">{{ templateCount }}</span>
        {{ $t(`m.common['个']`) }}
        {{ $t(`m.nav['权限模板']`) }}
      </div>
      <template v-if="templateCount > 0 && policyCount > 0">，</template>
      <div :class="['sub-title', { 'no-margin': templateCount }, { 'set-margin': !templateCount }]"
        v-if="policyCount > 0">
        <span class="number">{{ policyCount }}</span>
        {{ $t(`m.common['个']`) }}
        {{ $t(`m.perm['自定义权限']`) }}
      </div>
    </div>
    <div class="content" v-if="isExpanded">
      <div class="slot-content">
        <slot />
      </div>
      <p class="expand-action" @click="handlePackup" data-test-id="renderPermItem_btn_expandAction">
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
      policyCount: {
        type: Number,
        default: 0
      },
      templateCount: {
        type: Number,
        default: 0
      },
      extCls: {
        type: String,
        default: ''
      },
      groupSystemListLength: {
        type: Number,
        default: 0
      }
    },
    data () {
      return {
        isExpanded: this.expanded,
        role: ''
      };
    },
    watch: {
      expanded (value) {
        this.isExpanded = !!value;
      }
    },
    created () {
      this.isShowTable();
    },
    methods: {
      isShowTable () {
        if (this.groupSystemListLength === 1 && this.templateCount >= 1) {
          this.handleExpanded();
        } else if (this.groupSystemListLength === 1 && this.templateCount === 0 && this.policyCount >= 1) {
          this.handleExpanded();
        }
      },
      handlePackup () {
        this.isExpanded = false;
        this.$emit('update:expanded', false);
        this.$emit('on-expanded', false);
      },

      handleExpanded () {
        this.isExpanded = !this.isExpanded;
        this.$emit('update:expanded', true); // 更新expanded
        this.$emit('on-expanded', this.isExpanded); // 执行on-expanded
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
                &.no-margin {
                    margin-left: 0;
                }
                &.set-margin {
                    margin-left: 42px;
                }
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
    }
</style>
