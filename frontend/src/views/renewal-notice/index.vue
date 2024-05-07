<template>
  <div class="renewal-notice-wrapper">
    <div
      :class="[
        'renewal-notice-content',
        { 'renewal-notice-content-lang': !curLanguageIsCn },
        { 'show-notice-alert': showNoticeAlert }
      ]"
    >
      <template v-if="!isLoading && noticeForm.enable">
        <div class="notice-methods">
          <div class="notice-item-label mb8">
            {{ $t(`m.renewalNotice['通知方式']`) }}
          </div>
          <div class="notice-methods-list">
            <div
              v-for="item in noticeList"
              :key="item.value"
              :class="[
                'notice-methods-item',
                {
                  'is-active': noticeForm.notification_types.includes(item.value)
                }
              ]"
            >
              <div class="notice-type-item" @click.stop="handleSelectNoticeType(item)">
                <div class="notice-type-content">
                  <i :class="['iam-icon active-icon', item.icon]" />
                  <img
                    class="notice-type-img"
                    :src="item.selected_icon"
                  />
                  <span class="notice-type-label">{{ item.label }}</span>
                </div>
                <div class="gou" />
              </div>
              <div class="notice-temp">
                <Icon type="setting" class="notice-temp-icon" />
                <div class="notice-temp-label" @click.stop="handleShowNoticeTemp(item)" style="z-index: 9999">
                  {{ $t(`m.renewalNotice['模板']`) }}
                </div>
              </div>
            </div>
          </div>
          <div v-if="isMethodsEmpty" class="notice-empty-error">{{ $t(`m.renewalNotice['通知方式为必填项']`) }}</div>
        </div>
        <div class="notice-time">
          <div class="notice-item-label mb8">
            {{ $t(`m.renewalNotice['通知时间']`) }}
          </div>
          <div class="notice-time-content">
            <div class="notice-time-item notice-scope">
              <div class="notice-item-label notice-time-title notice-scope-title">
                {{ $t(`m.renewalNotice['通知范围']`) }}
              </div>
              <div class="notice-item-value notice-item-scope">
                <div class="notice-item-scope-input">
                  <bk-input
                    type="number"
                    v-model="noticeForm.expire_days_before"
                    :precision="0"
                    :min="0"
                    :max="15"
                    :maxlength="2"
                    @input="handleDayBeforeInput">
                    <template slot="prepend">
                      <div class="group-text"> {{ $t(`m.renewalNotice['过期前']`) }}</div>
                    </template>
                    <template slot="append">
                      <div class="group-text"> {{ $t(`m.common['天']`) }}</div>
                    </template>
                  </bk-input>
                  <span class="and-icon">~</span>
                  <bk-input
                    type="number"
                    v-model="noticeForm.expire_days_after"
                    :precision="0"
                    :min="0"
                    :max="15"
                    :maxlength="2"
                    @input="handleDayAfterInput"
                  >
                    <template slot="prepend">
                      <div class="group-text"> {{ $t(`m.renewalNotice['过期后']`) }}</div>
                    </template>
                    <template slot="append">
                      <div class="group-text"> {{ $t(`m.common['天']`) }}</div>
                    </template>
                  </bk-input>
                </div>
                <div class="notice-item-scope-tip">
                  <bk-icon type="info-circle" class="icon" />
                  <span>{{ $t(`m.renewalNotice['整个通知范围，需要 >= 7 天']`) }}</span>
                </div>
                <div v-if="isScopeEmpty" class="notice-empty-error">{{ scopeEmptyError }}</div>
              </div>
            </div>
            <div class="notice-time-item notice-day">
              <div class="notice-item-label notice-time-title">
                {{ $t(`m.renewalNotice['通知日']`) }}
              </div>
              <div class="notice-item-value">
                <bk-checkbox-group v-model="noticeForm.send_days" @change="handleDayChange">
                  <bk-checkbox
                    v-for="item in sendDaysList"
                    :key="item.value"
                    :value="item.value"
                    class="notice-day-checkbox"
                  >
                    {{ $t(`m.renewalNotice['${item.label}']`) }}
                  </bk-checkbox>
                </bk-checkbox-group>
                <div v-if="isDayEmpty" class="notice-empty-error">{{ $t(`m.renewalNotice['通知日为必填项']`) }}</div>
              </div>
            </div>
            <div class="notice-time-item notice-send-time">
              <div class="notice-item-label notice-time-title">
                {{ $t(`m.renewalNotice['发送时间']`) }}
              </div>
              <div class="notice-item-value">
                <bk-time-picker v-model="noticeForm.send_time" :format="'HH:mm'" @change="handleSendTimeChange" />
                <div class="notice-item-time-tip">
                  <span>{{ $t(`m.renewalNotice['过期前']`) }}</span>
                  <span class="bold-text">{{ noticeForm.expire_days_before }}</span>
                  <span>{{ $t(`m.common['天']`) }}</span>
                  <span>~</span>
                  <span>{{ $t(`m.renewalNotice['过期后']`) }}</span>
                  <span class="bold-text">{{ noticeForm.expire_days_after }}</span>
                  <span>{{ $t(`m.renewalNotice['天内']`) }}</span>
                  <span>{{ $t(`m.common['，']`) }}</span>
                  <span>{{ $t(`m.renewalNotice['逢']`) }}</span>
                  <span class="bold-text">{{ formatDayLabel }}</span>
                  <span>{{ $t(`m.renewalNotice['的']`) }}</span>
                  <span class="bold-text">{{ noticeForm.send_time }}</span>
                  <span>{{ $t(`m.renewalNotice['发送通知']`) }}</span>
                </div>
                <div v-if="isSendTimeEmpty" class="notice-empty-error">{{ $t(`m.renewalNotice['发送时间为必填项']`) }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="renewal-notice-footer">
          <bk-button
            theme="primary"
            class="renewal-notice-footer-btn"
            @click.stop="handleSubmit('submit')"
          >
            {{ $t(`m.common['保存']`)}}
          </bk-button>
          <bk-button
            class="renewal-notice-footer-btn"
            @click.stop="handleReset"
          >
            {{ $t(`m.common['重置']`)}}
          </bk-button>
        </div>
      </template>
      <div v-if="!isLoading && !noticeForm.enable" class="close-renewal-notice">
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :error-message="emptyData.tip"
          :tip-type="emptyData.tipType"
        />
      </div>
    </div>

    <bk-sideslider
      :is-show.sync="noticeTempSlider.isShow"
      :title="noticeTempSlider.title"
      :width="noticeTempSlider.width"
      :quick-close="true"
      :show-mask="false"
      @animation-end="handleAnimationEnd"
    >
      <div slot="header" class="notice-temp-header">
        <div class="notice-temp-header-title">{{ $t(`m.renewalNotice['通知模板']`) }}</div>
        <div class="notice-temp-header-divider">|</div>
        <div class="notice-temp-header-content">
          <img class="selected-img" :src="noticeTempSlider.detailData.selected_icon" alt="" />
          <div class="selected-label">{{ noticeTempSlider.detailData.label }}</div>
        </div>
      </div>
      <div slot="content" class="notice-temp-content">
        <component :is="noticeTempSlider.slideName" :detail-data="noticeTempSlider.detailData" />
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { bus } from '@/common/bus';
  import { SEND_DAYS_LIST } from '@/common/constants';
  import MailNoticeSlider from '@/views/renewal-notice/components/mail-notice-slider.vue';
  import RtxNoticeSlider from '@/views/renewal-notice/components/rtx-notice-slider.vue';
  export default {
    inject: ['showNoticeAlert'],
    components: {
      MailNoticeSlider,
      RtxNoticeSlider
    },
    data () {
      return {
        noticeList: [
          {
            label: this.$t(`m.renewalNotice['企业微信']`),
            value: 'rtx',
            icon: 'iamcenter-qw',
            selected_icon: require('@/images/qw.svg')
          },
          {
            label: this.$t(`m.renewalNotice['邮件']`),
            value: 'mail',
            icon: 'iamcenter-youjian',
            selected_icon: require('@/images/mail.svg')
          }
          // {
          //   label: this.$t(`m.renewalNotice['微信']`),
          //   value: 'weixin',
          //   icon: 'iamcenter-wechat',
          //   selected_icon: require('@/images/weChat.svg')
          // },
          // {
          //   label: this.$t(`m.renewalNotice['短信']`),
          //   value: 'sms',
          //   icon: 'iamcenter-duanxin',
          //   selected_icon: require('@/images/sms.svg')
          // }
        ],
        sendDaysList: SEND_DAYS_LIST,
        noticeForm: {
          notification_types: [],
          send_days: [],
          send_time: '',
          expire_days_before: 0,
          expire_days_after: 0,
          enable: false
        },
        noticeFormReset: {},
        noticeTempSlider: {
          title: '',
          slideName: '',
          isShow: false,
          width: 960,
          detailData: {}
        },
        emptyData: {
          type: 'empty',
          text: this.$t(`m.renewalNotice['续期通知暂未开启']`),
          tip: this.$t(`m.renewalNotice['请在顶部开启相关功能']`),
          tipType: 'noPerm'
        },
        isLoading: true,
        isMethodsEmpty: false,
        isScopeEmpty: false,
        isDayEmpty: false,
        isSendTimeEmpty: false,
        submitLoading: false,
        scopeEmptyError: ''
      };
    },
    computed: {
      formatDayLabel () {
        const result = this.sendDaysList.filter((item) => this.noticeForm.send_days.includes(item.value))
          .map((v) => this.$t(`m.renewalNotice['${v.label}']`));
        if (result.length) {
          return result.join('、');
        }
        return '';
      }
    },
    created () {
      this.fetchSuperNoticeConfig(false, false);
    },
    mounted () {
      this.handleGetBusQueryData();
    },
    methods: {
      async fetchSuperNoticeConfig (isReset = false, isStatus = false) {
        this.isLoading = true;
        try {
          const { data } = await this.$store.dispatch('renewalNotice/getSuperNoticeConfig');
          if (data) {
            if (!data.hasOwnProperty('enable')) {
              data.enable = true;
            }
            // 如果是重置操作，只需赋值给重置变量
            if (isReset) {
              this.noticeFormReset = Object.assign(this.noticeFormReset, data);
              return;
            }
            this.noticeForm = Object.assign(this.noticeForm, data);
            this.noticeFormReset = cloneDeep(this.noticeForm);
            if (!isStatus) {
              bus.$emit('on-refresh-renewal-status', { isShowRenewalNotice: data.enable });
            }
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      async handleSubmit (payload) {
        const isEmpty = this.handleGetValidate();
        if (isEmpty) {
          return;
        }
        this.submitLoading = true;
        try {
          const typeMap = {
            submit: async () => {
              if (JSON.stringify(this.noticeForm) !== JSON.stringify(this.noticeFormReset)) {
                await this.fetchSuperNoticeConfig(true, false);
              }
              await this.$store.dispatch('renewalNotice/updateSuperNoticeConfig', this.noticeForm);
              this.messageSuccess(this.$t(`m.info['保存成功']`), 3000);
            },
            status: async () => {
              await this.$store.dispatch('renewalNotice/updateSuperNoticeConfig', this.noticeForm);
              const msg = this.noticeForm.enable ? this.$t(`m.renewalNotice['开启成功']`) : this.$t(`m.renewalNotice['关闭成功']`);
              this.messageSuccess(msg, 3000);
            }
          };
          typeMap[payload]();
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.submitLoading = false;
        }
      },

      handleSelectNoticeType (payload) {
        const isExist = this.noticeForm.notification_types.includes(payload.value);
        if (isExist) {
          this.noticeForm.notification_types = this.noticeForm.notification_types.filter(
            (item) => item !== payload.value
          );
        } else {
          this.noticeForm.notification_types.push(payload.value);
        }
        this.isMethodsEmpty = this.noticeForm.notification_types.length < 1;
      },

      handleDayBeforeInput (payload) {
        if (Number(payload) > 15) {
          payload = 15;
          this.noticeForm.expire_days_before = 15;
        }
        this.isScopeEmpty = !(String(payload).length > 0 && String(this.noticeForm.expire_days_after).length > 0);
        const isLessSevenDay = Number(payload) + Number(this.noticeForm.expire_days_after) < 7;
        if (this.isScopeEmpty) {
          this.scopeEmptyError = this.$t(`m.renewalNotice['通知范围为必填项']`);
        }
        if (isLessSevenDay && !this.isScopeEmpty) {
          this.scopeEmptyError = this.$t(`m.renewalNotice['通知范围至少7天']`);
          this.isScopeEmpty = true;
        }
      },

      handleDayAfterInput (payload) {
        if (Number(payload) > 15) {
          payload = 15;
          this.noticeForm.expire_days_after = 15;
        }
        this.isScopeEmpty = !(String(payload).length > 0 && String(this.noticeForm.expire_days_before).length > 0);
        const isLessSevenDay = Number(payload) + Number(this.noticeForm.expire_days_before) < 7;
        if (this.isScopeEmpty) {
          this.scopeEmptyError = this.$t(`m.renewalNotice['通知范围为必填项']`);
        }
        if (isLessSevenDay && !this.isScopeEmpty) {
          this.scopeEmptyError = this.$t(`m.renewalNotice['通知范围至少7天']`);
          this.isScopeEmpty = true;
        }
      },

      handleDayChange (payload) {
        this.isDayEmpty = !(payload.length > 0);
      },

      handleSendTimeChange (payload) {
        this.isSendTimeEmpty = !(payload.length > 0);
      },

      handleShowNoticeTemp (payload) {
        console.log(payload.value);
        const typeMap = {
          rtx: () => {
            this.noticeTempSlider = Object.assign(this.noticeTempSlider, { slideName: 'RtxNoticeSlider', isShow: true, detailData: payload });
          },
          mail: () => {
            this.noticeTempSlider = Object.assign(this.noticeTempSlider, { slideName: 'MailNoticeSlider', isShow: true, detailData: payload });
          }
        };
        return typeMap[payload.value]();
      },

      handleAnimationEnd () {
        this.noticeTempSlider = {
          title: '',
          slideName: '',
          isShow: false,
          width: 960,
          detailData: {}
        };
      },

      handleReset () {
        this.noticeForm = cloneDeep(this.noticeFormReset);
        this.handleGetValidate();
      },

      handleGetValidate () {
        const {
          notification_types,
          send_days, send_time: sendTime,
          expire_days_before: expireDaysBefore,
          expire_days_after: expireDaysAfter
        } = this.noticeForm;
        this.isScopeEmpty = false;
        this.isMethodsEmpty = !(notification_types.length > 0);
        this.isDayEmpty = !(send_days.length > 0);
        this.isSendTimeEmpty = !(sendTime.length > 0);
        const isScopeEmpty = !(String(expireDaysBefore).length > 0 || String(expireDaysAfter).length > 0);
        const isLessSevenDay = Number(expireDaysBefore) + Number(expireDaysAfter) < 7;
        if (isScopeEmpty) {
          this.scopeEmptyError = this.$t(`m.renewalNotice['通知范围为必填项']`);
          this.isScopeEmpty = true;
        }
        if (isLessSevenDay && !isScopeEmpty) {
          this.scopeEmptyError = this.$t(`m.renewalNotice['通知范围至少7天']`);
          this.isScopeEmpty = true;
        }
        const result = this.isMethodsEmpty || this.isScopeEmpty || this.isDayEmpty || this.isSendTimeEmpty;
        return result;
      },

      handleGetBusQueryData () {
        bus.$on('on-update-renewal-notice', async ({ isShowRenewalNotice }) => {
          await this.fetchSuperNoticeConfig(false, true);
          this.noticeForm.enable = isShowRenewalNotice || false;
          await this.handleSubmit('status');
        });
        this.$once('hook:beforeDestroy', () => {
          bus.$off('on-update-renewal-notice');
        });
      }
    }
  };
</script>

<style lang="postcss" scoped>
.renewal-notice-wrapper {
  padding: 24px;
  .renewal-notice-content {
    position: relative;
    padding: 16px 24px;
    min-height: calc(100vh - 150px);
    background-color: #ffffff;
    border-radius: 2px;
    box-shadow: 0 2px 4px 0 #1919290d;
    &.show-notice-alert {
      min-height: calc(100vh - 190px);
    }
    .notice-item-label {
      position: relative;
      font-size: 12px;
      color: #63656e;
      &::after {
        height: 8px;
        line-height: 1;
        content: "*";
        color: #ea3636;
        font-size: 12px;
        position: absolute;
        top: 50%;
        display: inline-block;
        vertical-align: middle;
        -webkit-transform: translate(3px, -50%);
        transform: translate(3px, -50%);
      }
    }
    .notice-methods {
      margin-bottom: 44px;
      &-list {
        display: flex;
        align-items: center;
        .notice-methods-item {
          min-width: 120px;
          height: 40px;
          line-height: 40px;
          background-color: #f0f1f5;
          font-size: 12px;
          color: #63656e;
          border-radius: 2px;
          cursor: pointer;
          &:not(&:last-child) {
            margin-right: 8px;
          }
          .active-icon {
            color: #979ba5;
            margin-left: 13px;
            margin-right: 6px;
            font-size: 16px;
            line-height: 0;
          }
          .notice-type-img {
            display: none;
          }
          .notice-type-content {
            display: flex;
            align-items: center;
            .notice-type-label {
              padding-right: 10px;
            }
          }
          .notice-temp {
            display: flex;
            align-items: center;
            line-height: 20px;
            color: #3a84ff;
            &-icon {
              margin-right: 4px;
            }
          }
          &.is-active {
            position: relative;
            color: #313238;
            background-color: #f0f5ff;
            border: 1px solid #3a84ff;
            .active-icon {
              display: none;
            }
            .notice-type-img {
              width: 16px;
              margin-left: 13px;
              margin-right: 4px;
              display: inline-block;
            }
            .gou {
              display: inline-block;
              width: 24px;
              height: 24px;
              position: absolute;
              top: 0;
              right: 0;
              display: inline-block;
              &::before {
                content: "";
                position: absolute;
                width: 8px;
                height: 5px;
                background: transparent;
                top: 2px;
                right: 3px;
                border-left: 2px solid #ffffff;
                border-bottom: 2px solid #ffffff;
                transform: rotate(-50deg);
                z-index: 9;
              }
              &::after {
                content: "";
                position: absolute;
                bottom: 0;
                right: 0;
                border-top: 24px solid #3a84ff;
                border-left: 24px solid transparent;
              }
            }
          }
        }
      }
    }
    .notice-time {
      &-content {
        background-color: #F5F7FA;
        color: #63656E;
        width: 504px;
        padding: 16px 0;
        .notice-time-item {
          display: flex;
          &:not(&:last-child) {
            margin-bottom: 24px;
          }
          &.notice-scope {
            align-items: center;
            width: calc(100% - 28px);
            .notice-scope-title {
              margin-top: -22px;
              margin-bottom: 0;
            }
            /deep/ .notice-item-scope {
              margin-left: 0;
              &-input {
                display: flex;
                align-items: center;
                .group-box {
                  background-color: #FAFBFD;
                  .group-text {
                    padding: 0 8px;
                  }
                  &.group-append {
                    min-width: 40px;
                  }
                }
                .bk-input-number {
                  width: 88px;
                }
              }
              &-tip {
                color: #979BA5;
                font-size: 12px;
                margin-top: 4px;
                word-break: break-all;
                .icon {
                  color: #C4C6CC;
                  margin-right: 6px;
                  font-size: 14px !important;
                }
              }
              .and-icon {
                margin: 0 8px;
                color: #63656E;
              }
            }
          }
          &.notice-day {
            align-items: self-start;
            margin-bottom: 16px !important;
           /deep/ .notice-day-checkbox {
              margin-right: 40px;
              margin-top: 8px;
              line-height: 20px;
              &:nth-child(-n+5) {
                margin-top: 0;
              }
              &:nth-child(5) {
                margin-right: 0;
              }
              .bk-checkbox-text {
                font-size: 12px;
              }
            }
          }
          &.notice-send-time {
            align-items: baseline;
            width: calc(100% - 28px);
            .notice-item-value {
              .bk-date-picker {
                width: 100%;
              }
            }
            .notice-item-time-tip {
              padding: 8px;
              margin-top: 13px;
              font-size: 12px;
              color: #000000;
              background-color: #DCDEE5;
              word-break: break-all;
              .bold-text {
                font-weight: 700;
              }
            }
          }
        }
        .notice-time-title {
          min-width: 70px;
          margin-right: 20px;
          text-align: right;
        }
        .notice-item-value {
          min-width: 390px;
        }
      }
    }
    .notice-empty-error {
      color: #ff5656;
      font-size: 12px;
      margin-top: 4px;
    }
    .renewal-notice-footer {
      width: 100%;
      display: flex;
      margin-top: 32px;
      &-btn {
        min-width: 88px;
        &:nth-child(2) {
          min-width: 64px;
          margin: 0 8px;
        }
      }
    }
    .mb8 {
      margin-bottom: 8px;
    }
    /deep/.close-renewal-notice {
      position: absolute;
      top: 45%;
      left: 50%;
      transform: translate(-50%, -45%);
      .part-img {
        width: 440px !important;
      }
      .part-text {
        .empty-text {
          font-size: 24px;
          color: #63656E;
        }
        .tip-wrap {
          margin-top: 16px;
        }
      }
    }
    &-lang {
      .notice-time {
        &-content {
          width: 666px;
          .notice-time-title {
            min-width: 96px;
          }
          /deep/ .notice-item-scope {
            .bk-input-number {
              min-width: 93px;
            }
          }
          .notice-day {
           /deep/ .notice-day-checkbox {
              .bk-checkbox-text {
                min-width: 51px;
              }
            }
          }
        }
      }
    }
  }
  .notice-temp-header {
    width: 100%;
    display: flex;
    &-title {
      font-size: 16px;
      color: #313238;
    }
    &-divider {
      margin: 0 8px;
      color: #C4C6CC;
    }
    &-content {
      display: flex;
      align-items: center;
      font-size: 12px;
      color: #63656E;
      .selected-img {
        width: 16px;
        margin-right: 4px;
      }
    }
  }
}
</style>
