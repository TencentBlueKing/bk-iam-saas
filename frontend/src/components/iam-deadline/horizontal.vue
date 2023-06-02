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
  export default {
    name: '',
    props: {
      value: {
        type: [String, Number],
        default: 4102444800
      },
      // type：normal，dialog
      type: {
        type: String,
        default: 'normal'
      },
      curRole: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        timeFilters: {
          2592000: this.$t(`m.common['1个月']`),
          7776000: this.$t(`m.common['3个月']`),
          15552000: this.$t(`m.common['6个月']`),
          31104000: this.$t(`m.common['12个月']`),
          // 4102444800: this.$t(`m.common['永久']`),
          'custom': this.$t(`m.common['自定义']`)
        },
        currentActive: this.value,
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
            }
    },

    created () {
      if (this.isSuper) {
        this.timeFilters = {
          2592000: this.$t(`m.common['1个月']`),
          7776000: this.$t(`m.common['3个月']`),
          15552000: this.$t(`m.common['6个月']`),
          31104000: this.$t(`m.common['12个月']`),
          4102444800: this.$t(`m.common['永久']`),
          'custom': this.$t(`m.common['自定义']`)
        };
      }
    },
    methods: {
      handleTimeFilter (payload) {
        this.currentActive = payload;
        if (payload === 'custom') {
          this.handleTrigger();
          this.$delete(this.timeFilters, 'custom');
          this.$nextTick(() => {
            this.$refs.deadlineRef.focus();
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
        if (!/^[0-9]*$/.test(e.target.value)) {
          this.customTime = 1;
          this.handleTrigger();
          return;
        }
        if (e.target.value.length === 1) {
          this.customTime = e.target.value.replace(/[^1-9]/g, '');
        } else {
          this.customTime = e.target.value.replace(/\D/g, '');
        }
        if (e.target.value > 365 && e.target.value.length === 3) {
          this.customTime = 365;
        } else {
          if (e.target.value.length > 3) {
            this.customTime = parseInt(e.target.value.slice(0, 3), 10);
          }
        }
        this.handleTrigger();
      },

      handleTrigger () {
        let timestamp = 0;
        if (this.currentActive === 'custom') {
          timestamp = this.customTime * 24 * 3600;
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
            border: 1px solid #c3cdd7;
            vertical-align: bottom;
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
                border-right: 1px solid #c3cdd7;
            }
            .unit {
                position: relative;
                top: -31px;
                right: -40px;
                width: 40px;
                height: 32px;
                line-height: 32px;
                font-size: 14px;
                text-align: center;
                border: 1px solid #c3cdd7;
                float: right;
                &.is-focus {
                    border-left-color: #3a84ff;
                }
            }
            input.custom-time:focus {
                border-color: #c3cdd7 !important;
                outline: none !important;
                box-shadow: none !important;
            }
        }
    }
</style>
