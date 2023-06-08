<template>
  <div :class="['iam-perm-item', extCls]">
    <div class="header" @click="handleExpanded">
      <Icon bk class="expanded-icon" :type="isExpanded ? 'down-shape' : 'right-shape'" />
      <label class="title">{{ curType === 'group' ? $t(`m.perm['加入的用户组']`) : $t(`m.myApply['申请的权限模板']`) }}</label>
      <div class="sub-title" v-if="data.length > 0 && !isExpanded">
        {{ curType === 'group' ? $t(`m.myApply['申请加入']`) : $t(`m.myApply['申请']`) }}
        <div class="sub-item">
          <span v-for="item in data" :key="item.id">
            {{$t(`m.common['【']`)}}{{ item.name }}{{$t(`m.common['】']`)}}
          </span>
        </div>
        {{ $t(`m.common['共']`) }}
        <span class="number">{{ data.length }}</span>
        {{ $t(`m.common['个']`) }}
        {{ curType === 'group' ? $t(`m.myApply['用户组']`) : $t(`m.myApply['权限模板']`) }}
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
      extCls: {
        type: String,
        default: ''
      },
      type: {
        type: String,
        default: 'group'
      },
      data: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        isExpanded: this.expanded,
        curType: ''
      };
    },
    watch: {
      expanded (value) {
        this.isExpanded = !!value;
      },
      type: {
        handler (value) {
          this.curType = value;
        },
        immediate: true
      }
    },
    methods: {
      handlePackup () {
        this.isExpanded = false;
        this.$emit('update:expanded', false);
        this.$emit('on-expanded', false);
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
            height: 64px;
            line-height: 60px;
            font-size: 14px;
            color: #63656e;
            border-radius: 2px;
            cursor: pointer;
            .expanded-icon {
                position: absolute;
                top: 23px;
                left: 10px;
            }
            .title {
                font-weight: 600;
            }
            .sub-title {
                margin-left: 10px;
                width: calc(100% - 270px);
                color: #979ba5;
                .number {
                    font-weight: 600;
                }
                .sub-item {
                    display: inline-block;
                    max-width: calc(100% - 240px);
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    vertical-align: bottom;
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
