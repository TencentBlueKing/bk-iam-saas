<template>
  <div :class="['iam-effect-time', { active: isActive }, { error: isError }]"
    @mouseenter="handleMouseenter"
    @mouseleave="handleMouseleave"
    @click.stop="handleClick">
    <div class="iam-input-text" :style="style" :title="!isEmpty ? curValue : ''" @click.stop="handleClick">
      <section :class="['iam-time-input', { 'is-empty': isEmpty }]" @click.stop="handleClick">
        {{ curValue }}
      </section>
    </div>
  </div>
</template>
<script>
  import { GLOBAL_TIME_ZONE_ENUM } from '@/common/constants';
  export default {
    name: '',
    props: {
      value: {
        type: Array,
        default: []
      },
      isEmpty: {
        type: Boolean,
        default: false
      },
      canView: {
        type: Boolean,
        default: false
      },
      canPaste: {
        type: Boolean,
        default: false
      },
      canOperate: {
        type: Boolean,
        default: true
      },
      canCopy: {
        type: Boolean,
        default: true
      },
      isError: {
        type: Boolean,
        default: false
      },
      params: {
        type: Object,
        default: () => {
          return {};
        }
      }
    },
    data () {
      return {
        curValue: '',
        isActive: false,
        immediatelyShow: false,
        effectWeekList: {
          1: this.$t(`m.info['每周一']`),
          2: this.$t(`m.info['每周二']`),
          3: this.$t(`m.info['每周三']`),
          4: this.$t(`m.info['每周四']`),
          5: this.$t(`m.info['每周五']`),
          6: this.$t(`m.info['每周六']`),
          0: this.$t(`m.info['每周日']`)
        },
        effectWeekTimeZone: GLOBAL_TIME_ZONE_ENUM,
        effectType: {
          'period_daily': this.$t(`m.info['时间']`)
        }
      };
    },
    computed: {
      style () {
        if (!this.canOperate) {
          return {
            width: '100%'
          };
        }
        if (this.isEmpty) {
          if (this.canPaste) {
            return {
              width: 'calc(100% - 30px)'
            };
          }
          return {
            width: '100%'
          };
        }
        const statusLen = [this.canView, this.canPaste, this.canCopy].filter(status => !!status).length;
        return {
          width: `calc(100% - ${statusLen * 30}px)`
        };
      }
    },
    watch: {
      value: {
        handler (val) {
          if (this.isEmpty) {
            this.curValue = this.$t(`m.permApply['请选择生效条件，默认无限制']`);
          } else {
            this.curValue = val.reduce((p, v) => {
              let curValue = '';
              let weekCopy = '';
              curValue = v.condition.reduce((prev, item) => {
                let hms = '';
                let tz = '';
                let weekday = '';
                if (item.type === 'weekday') {
                  weekday = item.values.reduce((pre, e) => {
                    pre = `${pre} ${this.effectWeekList[e.value]}`;
                    return pre;
                  }, '');
                  weekCopy = weekday;
                }

                if (item.type === 'hms') {
                  hms = item.values.reduce((pre, e) => {
                    if (pre) {
                      pre = `${pre} - ${e.value}`;
                    } else {
                      pre = `${pre} ${e.value}`;
                    }
                                        
                    return pre;
                  }, '');
                }

                if (item.type === 'tz') {
                  tz = item.values.reduce((pre, e) => {
                    pre = this.effectWeekTimeZone[e.value];
                    return pre;
                  }, '');
                }

                prev = `${prev}${hms}${tz}${weekday}`;
                return prev;
              }, '');
              p = `${p}${weekCopy ? '' : this.$t(`m.info['每天']`)}${curValue}${this.effectType[v.type]}${this.$t(`m.info['生效']`)}`;
              return p;
            }, this.$t(`m.info['在']`));
          }
        },
        immediate: true
      }
    },
    methods: {

      handleMouseenter () {
        this.isActive = true;
        this.$emit('on-mouseover');
      },

      handleMouseleave () {
        this.isActive = false;
        this.immediatelyShow = false;
        this.$emit('on-mouseleave');
      },

      handleRestore () {
        this.$emit('on-restore');
      },

      handleClick () {
        if (this.isDisabled) {
          return;
        }
        this.$emit('on-click');
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-effect-time {
        display: flex;
        justify-content: flex-start;
        position: relative;
        padding: 0 6px;
        width: 97%;
        line-height: 1;
        vertical-align: middle;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        font-size: 0;
        color: #63656e;
        background: #fff;
        cursor: pointer;
        &:hover {
            border-color: #3a84ff;
            .operate-icon {
                display: inline-block;
            }
        }
        &.active {
            border-color: #3a84ff;
        }
        &.error {
            border-color: #ff5656;
        }
        .iam-input-text {
            .iam-time-input {
                height: 32px;
                line-height: 32px;
                background-color: #fff;
                width: 100%;
                font-size: 12px;
                box-sizing: border-box;
                border: none;
                text-align: left;
                vertical-align: middle;
                outline: none;
                resize: none;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                cursor: pointer;
                &.is-empty {
                    color: #c4c6cc;
                }
            }
        }
        .operate-icon {
            display: none;
            margin: 6px 0 0 6px;
            padding: 2px;
            width: 20px;
            height: 20px;
            color: #979ba5;
            outline: none;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
                border-radius: 2px;
                background: #e1ecff;
                i {
                    color: #3a84ff;
                }
            }
            i {
                font-size: 16px;
                color: #979ba5;
            }
        }
    }
</style>
