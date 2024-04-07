<template>
  <div class="renewal-notice-wrapper">
    <div :class="['renewal-notice-content', { 'show-notice-alert': showNoticeAlert }]">
      <div class="notice-methods">
        <div class="notice-item-label notice-methods-title">{{ $t(`m.renewalNotice['通知方式']`) }}</div>
        <div class="notice-methods-list">
          <div
            v-for="item in noticeList"
            :key="item.value"
            :class="[
              'notice-methods-item',
              { 'is-active': noticeForm.notification_types.includes(item.value) }
            ]"
          >
            <i :class="['iam-icon', item.icon]" />
            <span>{{ item.label }}</span>
            <span class="mask">V</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    inject: ['showNoticeAlert'],
    data () {
      return {
        noticeList: [
          {
            label: this.$t(`m.renewalNotice['企业微信']`),
            value: 'WeCom',
            icon: 'iamcenter-qw',
            selected_icon: ''
          },
          {
            label: this.$t(`m.renewalNotice['邮件']`),
            value: 'mail',
            icon: 'iamcenter-youjian'
          },
          {
            label: this.$t(`m.renewalNotice['微信']`),
            value: 'WeChat',
            icon: 'iamcenter-wechat'
          },
          {
            label: this.$t(`m.renewalNotice['短信']`),
            value: 'rtx',
            icon: 'iamcenter-duanxin'
          }
        ],
        noticeForm: {
          notification_types: ['mail', 'rtx'],
          send_days: ['monday'],
          send_time: '10:00',
          expire_days_before: 15,
          expire_days_after: 1
        }
      };
    },
    methods: {}
  };
</script>

<style lang="postcss" scoped>
.renewal-notice-wrapper {
    padding: 24px;
    .renewal-notice-content {
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
            color: #63656E;
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
                -webkit-transform: translate(8px, -50%);
                transform: translate(8px, -50%);
            }
        }
        .notice-methods {
            margin-bottom: 24px;
            &-list {
                display: flex;
                align-items: center;
                .notice-methods-item {
                    min-width: 120px;
                    height: 40px;
                    line-height: 40px;
                    background-color: #F0F1F5;
                    font-size: 12px;
                    color: #63656E;
                    color: #313238;
                    border-radius: 2px;
                    cursor: pointer;
                    &:not(&:last-child) {
                        margin-right: 8px;
                    }
                    .iam-icon {
                        padding-left: 13px;
                    }
                    &.is-active {
                        position: relative;
                        color: #313238;
                        background-color: #F0F5FF;
                        border: 1px solid #3A84FF;
                        .mark {
                            display: inline-block;
                            width: 50px;
                            height: 40px;
                            position: absolute;
                            top: 5px;
                            right: 0;
                            display: inline-block;
                            /* 三角形 */
                            &::after {
                                content: '';
                                position: absolute;
                                bottom: 0px;
                                right: 0px;
                                border-top: 45px solid @primary-color;
                                border-left: 50px solid transparent;
                            }
                            /* 三角形勾 */
                            &::before {
                                content: '';
                                position: absolute;
                                width: 18px;
                                height: 11px;
                                background: transparent;
                                top: 2px;
                                right: 6px;
                                border: 4px solid white;
                                border-top: none;
                                border-right: none;
                                transform: rotate(-55deg);
                                z-index: 9;
                            }
                        }
                    }
                }
            }
        }
    }
}
</style>
