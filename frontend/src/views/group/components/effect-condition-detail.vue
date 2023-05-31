<template>
  <div class="iam-effect-condition">
    <div class="edit-text">
      <bk-button v-if="isDetail" text @click="handleEdit">{{ $t(`m.common['编辑']`) }}</bk-button>
    </div>
    <span class="text">{{ curValue }}</span>
  </div>
</template>
<script>
  import _ from 'lodash';
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
      isDetail: {
        type: Boolean,
        default: false
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
    computed: {},
    watch: {
      value: {
        handler (val) {
          if (!val || !val.length) {
            this.curValue = this.$t(`m.common['无生效条件']`);
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
              p = `${this.effectType[v.type]}: ${p}${weekCopy ? '' : this.$t(`m.info['每天']`)}${curValue}${this.effectType[v.type]}${this.$t(`m.info['生效']`)}`;
              return p;
            }, this.$t(`m.info['在']`));
            this.effectConditionData = _.cloneDeep(val);
          }
        },
        immediate: true
      }
    },
    methods: {
      handleEdit () {
        this.$emit('on-view');
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-effect-condition {
        position: relative;
        color: #63656e;
        cursor: pointer;
        /* margin: 0 20px !important; */
        
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

        .text {
            /* display: inline-block; */
            overflow: hidden;
            /* text-overflow: ellipsis;
            white-space: nowrap;
            vertical-align: middle; */
            height: 30px;
            line-height: 30px;
            padding-left: 20px;
        }

        .edit-text{
            text-align: right;
        }
    }
</style>
