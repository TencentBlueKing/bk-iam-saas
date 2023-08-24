<template>
  <div class="iam-deadline-wrapper">
    <bk-button type="primary" :disabled="disabled" @click="handleTrigger" class="iam-deadline-btn">
      <span class="iam-deadline-display">{{ deadlineMap[currentActive] }}</span>
      <Icon bk class="iam-deadline-icon" :type="isDropdownShow ? 'angle-up' : 'angle-down'" />
    </bk-button>
    <ul class="iam-dropdown-list" v-show="isDropdownShow" v-bk-clickoutside="handleClickOutside">
      <template v-for="(item, key) in deadlineMap">
        <li
          :key="key"
          :class="{ 'active': String(currentActive) === key }"
          v-if="key !== 'custom'">
          <a @click="handleChange(key)">
            {{ deadlineMap[key] }}
          </a>
        </li>
      </template>
      <li :class="{ 'reset-padding': isShowCustom }">
        <a
          @click="handleCustomChange"
          v-if="!isShowCustom">
          {{ $t(`m.common['自定义']`) }}
        </a>
        <template v-else>
          <bk-input
            v-model="customTime"
            @focus="handleFocus"
            @blur="handleBlur"
            @input="handleInput"
            @enter="handleEnter"
            :placeholder="$t(`m.verify['请输入']`)"
            :class="{ 'is-focus': isFocus }">
            <template slot="append">
              <div class="group-text">{{ $t(`m.common['天']`) }}</div>
            </template>
          </bk-input>
        </template>
      </li>
    </ul>
  </div>
</template>
<script>
  export default {
    name: 'iam-deadline',
    props: {
      active: {
        type: [String, Number],
        default: 4102444800
      },
      trigger: {
        type: String,
        default: 'mouseover',
        validator (value) {
          if (['click', 'mouseover'].indexOf(value) < 0) {
            console.error(`trigger property is not valid: '${value}'`);
            return false;
          }
          return true;
        }
      },
      disabled: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isDropdownShow: false,
        deadlineMap: {
          2592000: this.$t(`m.common['1个月']`),
          7776000: this.$t(`m.common['3个月']`),
          15552000: this.$t(`m.common['6个月']`),
          31104000: this.$t(`m.common['12个月']`),
          // 4102444800: this.$t(`m.common['永久']`),
          'custom': this.$t(`m.common['自定义']`)
        },
        currentActive: this.active,
        isShowCustom: false,
        customTime: 1,
        isFocus: false
      };
    },
    watch: {
      active (value) {
        this.currentActive = value;
      }
    },
    created () {
      this.deadlineMap.custom = `${this.customTime} ${this.$t(`m.common['天']`)}`;
    },
    methods: {
      handleTrigger () {
        this.isDropdownShow = !this.isDropdownShow;
        if (!this.isDropdownShow) {
          if (!this.isShowCustom) {
            this.customTime = 1;
          }
          this.isShowCustom = false;
        }
      },
      handleChange (payload) {
        this.currentActive = payload;
        this.isShowCustom = false;
        this.isFocus = false;
        this.customTime = 1;
        this.deadlineMap.custom = `${this.customTime} ${this.$t(`m.common['天']`)}`;
        this.$emit('on-change', payload, this.deadlineMap[payload]);
      },
      handleCustomChange () {
        this.isShowCustom = true;
      },
      handleFocus () {
        this.isFocus = true;
      },
      handleBlur () {
        this.isFocus = false;
      },
      handleInput (value) {
        const flag = /[^1-9]/g.test(value);
        if (flag || value === '') {
          setTimeout(() => {
            this.customTime = 1;
          }, 100);
        }
      },
      handleClickOutside () {
        if (arguments[0]['target']['className'].indexOf('iam-deadline-btn') !== -1
          || arguments[0]['target']['className'].indexOf('iam-deadline-display') !== -1
          || arguments[0]['target']['className'].indexOf('iam-deadline-icon') !== -1) {
          return;
        }
        this.isDropdownShow = false;
      },
      handleEnter () {
        this.currentActive = 'custom';
        this.deadlineMap.custom = `${this.customTime} ${this.$t(`m.common['天']`)}`;
        this.isDropdownShow = false;
        this.$emit('on-change', 'custom', this.customTime);
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-deadline-wrapper {
        position: relative;
        .iam-dropdown-list {
            position: absolute;
            top: 34px;
            padding: 10px 0;
            width: 116px;
            border: 1px solid #c4c6cc;
            border-radius: 2px;
            background: #fff;
            box-shadow: 0px 3px 6px 0px rgba(0, 0, 0, .15);
            z-index: 1;
            li {
                line-height: 32px;
                cursor: pointer;
                &:hover {
                    > a {
                        background-color: #eaf3ff;
                        color: #3a84ff;
                    }
                }
                a {
                    display: block;
                    padding: 0 15px;
                    width: 100%;
                    font-size: 12px;
                }
            }
            li.active {
                > a {
                    background-color: #eaf3ff;
                    color: #3a84ff;
                }
            }
            li.reset-padding {
                padding: 0 16px;
                &:hover {
                    background-color: #eaf3ff;
                    .group-box {
                        background-color: #fff;
                    }
                }
                .control-append-group {
                    top: -2px;
                    .group-box {
                        top: 5px;
                        .group-text {
                            vertical-align: top;
                        }
                    }
                }
            }
            .is-focus {
                .group-box {
                    border-color: #3a84ff;
                }
            }
            .bk-form-input {
                height: 26px;
                border-right: none;
            }
            .bk-form-control .group-box {
                height: 26px;
                .group-text {
                    padding: 0 8px;
                    line-height: 26px;
                    color: #979ba5;
                }
            }
        }
    }
</style>
