<template>
  <!-- eslint-disable max-len -->
  <div class="iam-deadline-wrapper">
    <div class="bk-button-group time-button-groups">
      <bk-button :class="key === String(currentActive) ? 'is-selected' : ''"
        v-for="(key, index) in Object.keys(timeFilters)"
        :key="index"
        :name="key"
        @click="handleTimeFilter(key)">
        {{timeFilters[key]}}
      </bk-button>
    </div>
    <div :class="['custom-time-select', { 'is-focus': isFocus }, { 'is-normal': isNormal }, { 'is-dialog': isDialog }]"
      v-if="isShowCustomTime">
      <input
        ref="deadlineRef"
        type="text"
        class="bk-form-input custom-time"
        @input="handleTimeInput"
        @focus="handleTimeFocus"
        @blur="handleTimeBlur"
        v-model="customTime"
        placeholder="1-365" />
      <div :class="['unit', { 'is-focus': isFocus }]">{{ $t(`m.common['天']`) }}</div>
    </div>
  </div>
</template>
<script>
  import { mapGetters } from 'vuex';

  // 提取常量：避免魔法值，便于统一维护
  const TIME_CONSTANTS = {
    // 月数对应的秒数（30天/月）
    MONTH_SECONDS_MAP: {
      1: 2592000,
      3: 7776000,
      6: 15552000,
      12: 31104000
    },
    // 永久续期的时间戳
    PERMANENT_TIMESTAMP: 4102444800,
    // 自定义天数最大值
    MAX_CUSTOM_DAY: 365,
    // 文案key常量
    TEXT_KEYS: {
      ONE_MONTH: 'm.common["1个月"]',
      THREE_MONTH: 'm.common["3个月"]',
      SIX_MONTH: 'm.common["6个月"]',
      TWELVE_MONTH: 'm.common["12个月"]',
      PERMANENT: 'm.common["永久"]',
      CUSTOM: 'm.common["自定义"]'
    }
  };

  export default {
    props: {
      value: {
        type: [String, Number],
        default: TIME_CONSTANTS.PERMANENT_TIMESTAMP
      },
      // type：normal，dialog
      type: {
        type: String,
        default: 'normal'
      },
      curRole: {
        type: String,
        default: ''
      },
      // 是否展示永久续期选项
      showPermanentRenewal: {
        type: Boolean,
        default: false,
        required: false
      }
    },
    data () {
      return {
        currentActive: 4102444800,
        customTime: 1,
        isFocus: false
      };
    },
    computed: {
      ...mapGetters(['user']),
      isShowCustomTime () {
          return this.currentActive === 'custom';
      },
      isNormal () {
          return this.type === 'normal';
      },
      isDialog () {
          return this.type === 'dialog';
      },
      isSuper () {
          return this.user.role.type === 'super_manager';
      },
      timeFilters () {
        // 基础时间选项（1/3/6/12个月 + 自定义）
        const baseFilters = {
          [TIME_CONSTANTS.MONTH_SECONDS_MAP[1]]: this.$t(TIME_CONSTANTS.TEXT_KEYS.ONE_MONTH),
          [TIME_CONSTANTS.MONTH_SECONDS_MAP[3]]: this.$t(TIME_CONSTANTS.TEXT_KEYS.THREE_MONTH),
          [TIME_CONSTANTS.MONTH_SECONDS_MAP[6]]: this.$t(TIME_CONSTANTS.TEXT_KEYS.SIX_MONTH),
          [TIME_CONSTANTS.MONTH_SECONDS_MAP[12]]: this.$t(TIME_CONSTANTS.TEXT_KEYS.TWELVE_MONTH),
          custom: this.$t(TIME_CONSTANTS.TEXT_KEYS.CUSTOM)
        };

        // 超管或需展示永久选项时，添加永久选项
        const shouldShowPermanent = this.isSuper || this.showPermanentRenewal;
        if (shouldShowPermanent) {
          return {
            ...baseFilters,
            [TIME_CONSTANTS.PERMANENT_TIMESTAMP]: this.$t(TIME_CONSTANTS.TEXT_KEYS.PERMANENT)
          };
        }

        return baseFilters;
      },
      // 所有合法的固定时间戳集合（用于value校验）
      validFixedTimestamps () {
        return [
          ...Object.values(TIME_CONSTANTS.MONTH_SECONDS_MAP),
          TIME_CONSTANTS.PERMANENT_TIMESTAMP
        ];
      }
    },
    watch: {
      value: {
        handler (newValue) {
          const numValue = Number(newValue);
          // 非固定时间戳则选中自定义
          if (!this.validFixedTimestamps.includes(numValue)) {
            this.currentActive = 'custom';
            // 反向计算自定义天数（兼容父组件传入自定义时间戳的场景）
            this.customTime = Math.min(
              Math.floor(numValue / (24 * 3600)) || 1,
              TIME_CONSTANTS.MAX_CUSTOM_DAY
            );
            return;
          }
          this.currentActive = numValue;
        },
        immediate: true
      }
    },
    created () {
      
    },
    methods: {
      handleTimeFilter (payload) {
        this.currentActive = payload;
        if (payload === 'custom') {
          this.handleTrigger();
          this.$delete(this.timeFilters, 'custom');
          this.$nextTick(() => {
            this.$refs.deadlineRef && this.$refs.deadlineRef.focus();
          });
        } else {
          this.customTime = 1;
          this.handleTrigger();
          this.$set(this.timeFilters, 'custom', this.$t(`m.common['自定义']`));
        }
      },

      handleTimeFocus () {
        this.isFocus = true;
      },

      handleTimeBlur () {
        this.isFocus = false;
      },

      handleTimeInput (e) {
        // 过滤所有非数字字符
        let inputValue = e.target.value.replace(/\D/g, '');

        if (!/^[0-9]*$/.test(inputValue)) {
          this.customTime = 1;
          this.handleTrigger();
          return;
        }

        // 限制最大365天
        if (inputValue.length > 3 || Number(inputValue) > TIME_CONSTANTS.MAX_CUSTOM_DAY) {
          inputValue = String(TIME_CONSTANTS.MAX_CUSTOM_DAY);
        }

        this.customTime = inputValue.length === 1 ? inputValue.replace(/[^1-9]/g, '') : inputValue;
        this.handleTrigger();
      },

      handleTrigger () {
        let timestamp = 0;
        if (this.currentActive === 'custom') {
          // 自定义天数转秒数，确保至少1天
          timestamp = Math.max(Number(this.customTime) || 1, 1) * 24 * 3600;
        } else {
          timestamp = Number(this.currentActive);
        }
        this.$emit('on-change', timestamp);
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-deadline-wrapper {
        .time-button-groups {
            .bk-button {
                min-width: 100px;
            }
        }
        .custom-time-select {
            display: inline-block;
            position: relative;
            width: 62px;
            height: 32px;
            border: 1px solid #c4c6cc;
            vertical-align: bottom;
            box-sizing: border-box;
            &.is-focus {
                border-color: #3a84ff;
            }
            &.is-normal {
                left: -6px;
            }
            &.is-dialog {
                left: -5px;
            }
            input.custom-time {
                width: 61px;
                height: 30px;
                padding-top: 1px;
                border-radius: 0;
                border: 0px;
                border-right: 1px solid #c4c6cc;
            }
            .unit {
                /* position: relative;
                top: -31px; */
                position: absolute;
                top: -1px;
                right: -40px;
                right: -40px;
                width: 40px;
                height: 32px;
                line-height: 32px;
                font-size: 14px;
                text-align: center;
                border: 1px solid #c4c6cc;
                /* float: right; */
                &.is-focus {
                    border-left-color: #3a84ff;
                }
            }
            input.custom-time:focus {
                border-color: #c4c6cc !important;
                outline: none !important;
                box-shadow: none !important;
            }
        }
    }
</style>
