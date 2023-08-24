<template>
  <div class="effect-wrap">
    <div class="effect-item" :class="timeRangeEmpty ? 'effect-item-empty' : ''"
      v-for="(environmentsItem, index) in environmentsData" :key="index">
      <bk-select
        v-model="environmentsItem.type"
        :clearable="false"
        ext-cls="effect-select-daily">
        <bk-option v-for="option in effectList"
          :key="option.value"
          :id="option.value"
          :name="$t(`m.info['${option.name}']`)">
        </bk-option>
      </bk-select>
      <div class="effect-flex">
        <bk-select
          v-bk-tooltips="tooltips"
          v-model="environmentsItem.date"
          :clearable="false"
          show-select-all
          multiple
          disabled
          ext-cls="effect-select-week"
          :placeholder="$t(`m.verify['请选择日期']`)">
          <bk-option v-for="option in effectWeekList"
            :key="option.value"
            :id="option.value"
            :name="$t(`m.info['${option.name}']`)"
          >
          </bk-option>
        </bk-select>
        <bk-select
          v-model="environmentsItem.TimeZone"
          :clearable="false"
          disabled
          ext-cls="effect-select-condition"
          :placeholder="$t(`m.verify['请选择时区']`)">
          <bk-option v-for="option in effectWeekTimeZone"
            :key="option.value"
            :id="option.value"
            :name="$t(`m.info['${option.name}']`)"
          >
          </bk-option>
        </bk-select>
        <div class="initTimeWarp">
          <bk-time-picker
            :type="'timerange'"
            v-model="environmentsItem.initTimeRange"
            :placeholder="$t(`m.verify['请选择时间范围']`)"
          />
          <p class="error-tips pt5" v-if="timeRangeEmpty &&
            (!environmentsItem.initTimeRange[0] || !environmentsItem.initTimeRange[1])">
            {{ $t(`m.verify['请选择时间范围']`) }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { GLOBAL_TIME_ZONE } from '@/common/constants';
  export default {
    name: '',
    props: {
      data: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        effectList: [{ name: '时间', value: 'period_daily' }],
        effectWeekList: [
          { name: '每周一', value: '1' },
          { name: '每周二', value: '2' },
          { name: '每周三', value: '3' },
          { name: '每周四', value: '4' },
          { name: '每周五', value: '5' },
          { name: '每周六', value: '6' },
          { name: '每周日', value: '0' }
        ],
        effectWeekTimeZone: GLOBAL_TIME_ZONE,
        date: [],
        environmentsData: [],
        timeRangeEmpty: false,
        tooltips: this.$t(`m.info['每天']`)
      };
    },
    watch: {
      data: {
        handler (val) {
          if (!val.length) {
            this.environmentsData = [{ type: 'period_daily', date: ['1', '2', '3', '4', '5', '6', '0'], TimeZone: 'Asia/Shanghai', initTimeRange: [] }];
          } else {
            this.environmentsData = val.map(e => {
              if (e.condition && e.condition.length) {
                e.date = ['1', '2', '3', '4', '5', '6', '0'];
                e.condition.forEach(item => {
                  if (item.type === 'weekday') {
                    e.date = item.values.reduce((p, v) => {
                      p.push(v.value);
                      return p;
                    }, []);
                  }
                  if (item.type === 'tz') {
                    e.TimeZone = item.values.reduce((p, v) => {
                      p = v.value;
                      return p;
                    }, '');
                  }
                  if (item.type === 'hms') {
                    e.initTimeRange = item.values.reduce((p, v) => {
                      p.push(v.value);
                      return p;
                    }, []);
                  }
                });
                delete e.condition;
              }
              return e;
            });
          }
        },
        immediate: true
      }
    },
    methods: {
      handleGetValue () {
        if (this.environmentsData.some(e => !e.initTimeRange[0] || !e.initTimeRange[1])) {
          this.timeRangeEmpty = true;
          return false;
        }
        const environments = _.cloneDeep(this.environmentsData).map(item => {
          item.condition = [];
          if (!!item.date.length && item.date.length !== 7) {
            item.date = item.date.reduce((prev, dataItem) => {
              prev.values.push({ name: '', value: dataItem });
              return prev;
            }, { type: 'weekday', values: [] });
            item.condition.push(item.date);
          }
          item.TimeZone = { type: 'tz', values: [{ name: '', value: item.TimeZone }] };
          item.initTimeRange = item.initTimeRange.reduce((p, v) => {
            p.values.push({ name: '', value: v });
            return p;
          }, { type: 'hms', values: [] });
          item.condition.push(item.initTimeRange, item.TimeZone);
          delete item.date;
          delete item.TimeZone;
          delete item.initTimeRange;
          return item;
        });
        return environments;
      }
    }
  };
</script>
<style lang="postcss">
    .effect-wrap{
        padding: 20px 30px 0 30px;
    }
    .effect-item{
        padding: 10px;
        margin-bottom: 20px;
        border: 1px solid #dcdee5;
    }
    .effect-item-empty{
        padding: 10px 10px 30px 10px !important;
    }
    .initTimeWarp{
        position: relative;
    }
    .effect-select-daily{
        width: 200px;
        margin-bottom: 20px;
    }
    .effect-select-week{
        width: 100px;
    }
    .effect-select-condition{
        width: 250px;
    }
    .effect-flex{
        display: flex;
        justify-content: space-between;
    }
</style>
