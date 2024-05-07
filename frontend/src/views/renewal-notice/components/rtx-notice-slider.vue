<template>
  <div class="rtx-notice-slider-wrapper">
    <div class="rtx-notice-item">
      <div class="rtx-notice-item-header">
        <div :class="['header-title', { 'header-title-lang': !curLanguageIsCn }]">
          <span>{{ $t(`m.renewalNotice['发送对象']`) }}{{ $t(`m.common['：']`) }}</span>
          <span>{{ $t(`m.renewalNotice['续期用户']`) }}</span>
        </div>
      </div>
      <div class="rtx-notice-item-content">
        <div class="temp-title">{{ $t(`m.renewalNotice['模板内容']`) }}</div>
        <div class="temp-content">
          <p class="temp-textarea-html" v-html="formaData.user_temp_html" />
          <bk-input
            type="textarea"
            v-model="formaData.user_temp"
            :rows="6"
            @input="handleUserTempInput"
            @change="handleUserTempInput"
          />
        </div>
        <div class="temp-operate-btn">
          <bk-popconfirm
            ref="userTempConfirm"
            trigger="click"
            placement="bottom-start"
            ext-popover-cls="notice-temp-test-confirm"
            :width="664"
            @confirm="handleTestConfirm('user')"
          >
            <div slot="content">
              <div class="popover-content">
                <div class="flex-between popover-content-tip">
                  <bk-user-selector
                    ref="userSelector"
                    style="width: 100%;"
                    v-model="userTempMembers"
                    :api="userApi"
                    :placeholder="$t(`m.renewalNotice['请输入接收测试通知的用户（请确保账号正确）']`)"
                    :empty-text="$t(`m.common['无匹配人员']`)"
                    @change="handleUserChange"
                  />
                  <bk-button
                    theme="primary"
                    class="test-send-btn"
                    :loading="sendLoading"
                    :disabled="userTempMembers.length < 1"
                    @click.stop="handleSend('user')"
                  >
                    {{ $t(`m.common['发送']`) }}
                  </bk-button>
                </div>
              </div>
            </div>
            <bk-button
              theme="primary"
              text
              class="operate-btn"
              @click.stop="handleUserOperate('test')"
            >
              {{ $t(`m.common['测试']`) }}
            </bk-button>
          </bk-popconfirm>
          <bk-button text theme="primary" class="operate-btn" @click.stop="handleUserOperate('reset')">
            {{ $t(`m.common['重置']`) }}
          </bk-button>
          <bk-popconfirm
            trigger="click"
            placement="bottom-start"
            ext-popover-cls="notice-temp-default-confirm"
            @confirm="handleUserOperate('default')"
          >
            <div slot="content">
              <div class="popover-title">
                <div class="popover-title-text">
                  {{ $t(`m.dialog['确认恢复默认？']`) }}
                </div>
              </div>
              <div class="popover-content">
                <div class="popover-content-tip">
                  {{
                    $t(`m.renewalNotice['恢复后，模板将会回到系统默认设定']`)
                  }}
                </div>
              </div>
            </div>
            <bk-button
              theme="primary"
              text
              class="operate-btn"
              :loading="defaultLoading"
            >
              {{ $t(`m.common['恢复默认']`) }}
            </bk-button>
          </bk-popconfirm>
        </div>
      </div>
    </div>
    <div class="rtx-notice-item">
      <div class="rtx-notice-item-header">
        <div :class="['header-title', { 'header-title-lang': !curLanguageIsCn }]">
          <span>{{ $t(`m.renewalNotice['发送对象']`) }}{{ $t(`m.common['：']`) }}</span>
          <span>{{ $t(`m.renewalNotice['空间管理员']`) }}</span>
        </div>
      </div>
      <div class="rtx-notice-item-content">
        <div class="temp-title">{{ $t(`m.renewalNotice['模板内容']`) }}</div>
        <div class="temp-content">
          <p class="temp-textarea-html" v-html="formaData.manager_temp_html" />
          <bk-input type="textarea" v-model="formaData.manager_temp" :rows="6" />
        </div>
        <div class="temp-operate-btn">
          <bk-popconfirm
            ref="managerTempConfirm"
            trigger="click"
            placement="bottom-start"
            ext-popover-cls="notice-temp-test-confirm"
            :width="664"
            @confirm="handleTestConfirm('manager')"
          >
            <div slot="content">
              <div class="popover-content">
                <div class="popover-content-tip">
                  <div class="flex-between">
                    <bk-user-selector
                      ref="managerSelector"
                      v-model="managerTempMembers"
                      style="width: 100%;"
                      :api="userApi"
                      :placeholder="$t(`m.renewalNotice['请输入接收测试通知的用户（请确保账号正确）']`)"
                      :empty-text="$t(`m.common['无匹配人员']`)"
                      @change="handleManagerChange"
                    />
                    <bk-button
                      theme="primary"
                      class="test-send-btn"
                      :loading="sendLoading"
                      :disabled="managerTempMembers.length < 1"
                      @click.stop="handleSend('manager')"
                    >
                      {{ $t(`m.common['发送']`) }}
                    </bk-button>
                  </div>
                </div>
              </div>
            </div>
            <bk-button
              theme="primary"
              text
              class="operate-btn"
              @click.stop="handleManagerOperate('test')"
            >
              {{ $t(`m.common['测试']`) }}
            </bk-button>
          </bk-popconfirm>
          <bk-button text theme="primary" class="operate-btn" @click.stop="handleManagerOperate('reset')">
            {{ $t(`m.common['重置']`) }}
          </bk-button>
          <bk-popconfirm
            trigger="click"
            placement="bottom-start"
            ext-popover-cls="notice-temp-default-confirm"
            @confirm="handleManagerOperate('default')"
          >
            <div slot="content">
              <div class="popover-title">
                <div class="popover-title-text">
                  {{ $t(`m.dialog['确认恢复默认？']`) }}
                </div>
              </div>
              <div class="popover-content">
                <div class="popover-content-tip">
                  {{
                    $t(`m.renewalNotice['恢复后，模板将会回到系统默认设定']`)
                  }}
                </div>
              </div>
            </div>
            <bk-button
              theme="primary"
              text
              class="operate-btn"
              :loading="defaultLoading"
            >
              {{ $t(`m.common['恢复默认']`) }}
            </bk-button>
          </bk-popconfirm>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { getDataBetweenBraces } from '@/common/util';
  import BkUserSelector from '@blueking/user-selector';
  export default {
    components: {
      BkUserSelector
    },
    props: {
      detailData: {
        type: Object,
        default: () => {}
      }
    },
    data () {
      return {
        defaultLoading: false,
        sendLoading: false,
        userApi: window.BK_USER_API,
        formaData: {
          user_temp: '【蓝鲸权限中心】权限续期提醒\n您有以下权限操作即将到期，如有需要请及时续期\n{{task.app.name}},您有以下权限操作即将到期，如有需要请及时续期{{task.4454.name}}',
          manager_temp: '【蓝鲸权限中心】权限续期提醒\n您管理的用户组有成员的权限即将过期，如有需要请及时续期\n{{task.a55pp.name}}',
          user_temp_html: '',
          manager_temp_html: ''
        },
        tempDetail: {},
        userTempMembers: [],
        managerTempMembers: []
      };
    },
    watch: {
      detailData: {
        handler (value) {
          this.tempDetail = { ...value };
          this.fetchNoticeTemplateDetail();
        },
        immediate: true
      }
    },
    methods: {
      fetchNoticeTemplateDetail () {
        this.handleReplaceHtmlText();
      },

      async handleSend (payload) {
        const typeMap = {
          user: () => {
            this.messageSuccess(this.$t(`m.renewalNotice['测试通知已发送成功，请查收。']`), 3000);
          },
          manager: () => {
            this.messageSuccess(this.$t(`m.renewalNotice['测试通知已发送成功，请查收。']`), 3000);
          }
        };
        typeMap[payload]();
      },

      handleUserChange (payload) {
        console.log(payload);
        this.userTempMembers = [...payload];
      },

      handleUserTempInput  (payload) {
        this.formaData.user_temp = payload;
        this.handleReplaceHtmlText();
      },

      handleUserOperate (payload) {
        const typeMap = {
          test: () => {
            this.$nextTick(() => {
              const userTempRef = this.$refs.userTempConfirm;
              if (userTempRef && userTempRef.$refs) {
                userTempRef.$refs.popover.showHandler();
                this.$refs.userSelector && this.$refs.userSelector.focus();
              }
            });
          },
          reset: () => {},
          default: () => {}
        };
        return typeMap[payload]();
      },

      handleManagerChange (payload) {
        this.managerTempMembers = [...payload];
      },

      handleManagerOperate (payload) {
        const typeMap = {
          test: () => {
            const managerTempConfirm = this.$refs.managerTempConfirm;
            if (managerTempConfirm && managerTempConfirm.$refs) {
              managerTempConfirm.$refs.popover.showHandler();
              this.$refs.managerSelector && this.$refs.managerSelector.focus();
            }
          },
          reset: () => {},
          default: () => {}
        };
        return typeMap[payload]();
      },

      handleReplaceHtmlText () {
        let userTemp = cloneDeep(this.formaData.user_temp);
        let managerTemp = cloneDeep(this.formaData.manager_temp);
        const reg = /{{([^}]+)}}/g;
        const userTextList = getDataBetweenBraces(userTemp, reg);
        const managerTextList = getDataBetweenBraces(managerTemp, reg);
        if (userTextList && userTextList.length > 0) {
          for (let i = 0; i < userTextList.length; i++) {
            userTemp = userTemp.replace(`{{${userTextList[i]}}}`, `<span style=\'color: #3a84ff;position: relative;z-index: 10000;line-height: 29px;left: 1px;\'>{{${userTextList[i]}}}</span>`);
          }
          this.formaData.user_temp_html = cloneDeep(userTemp);
        }
        if (managerTextList && managerTextList.length > 0) {
          for (let i = 0; i < managerTextList.length; i++) {
            managerTemp = managerTemp.replace(`{{${managerTextList[i]}}}`, `<span style=\'color: #3a84ff;position: relative;z-index: 10000;line-height: 29px;left: 1px;\'>{{${managerTextList[i]}}}</span>`);
          }
          this.formaData.manager_temp_html = cloneDeep(managerTemp);
        }
      }
    }
  };
</script>
      
<style lang="postcss" scoped>
.rtx-notice-slider-wrapper {
  .rtx-notice-item {
    margin: 24px 24px 16px 24px;
    background-color: #F5F7FA;
    &-header {
      margin-bottom: 12px;
      .header-title {
        width: 140px;
        padding: 0 8px;
        border-radius: 2px 0 11px 0;
        background-color: #979BA5;
        color: #ffffff;
        font-size: 12px;
        line-height: 24px;
        &-lang {
          width: 200px;
        }
      }
    }
    &-content {
      padding: 0 24px 16px 24px;
      font-size: 12px;
      .temp-title {
        position: relative;
        margin-bottom: 6px;
        color: #63656E;
        &:after {
          height: 8px;
          line-height: 1;
          content: "*";
          color: #ea3636;
          font-size: 12px;
          position: absolute;
          top: 50%;
          display: inline-block;
          vertical-align: middle;
          transform: translate(3px, -50%);
        }
      }
      .temp-content {
        position: relative;
        .temp-textarea-html {
          width:100%;
          position: absolute;
          top: 0;
          left: 0;
          padding: 5px 10px;
          white-space:pre-wrap;
        }
      }
      .temp-operate-btn {
        margin-top: 8px;
        .operate-btn {
          font-size: 12px;
          &:not(&:last-child) {
            margin: 0 24px;
          }
        }
      }
    }
  }
}
.notice-temp-test-confirm,
.notice-temp-default-confirm {
  .popover-title {
    font-size: 16px;
    padding-bottom: 8px;
    color: #313238;
  }
  .popover-content {
    color: #63656e;
    .popover-content-item {
      display: flex;
      margin-bottom: 8px;
      &-value {
        color: #313238;
        margin-left: 8px;
      }
    }
    &-tip {
      padding-bottom: 20px;
      color: #63656E;
    }
  }
}
</style>

<style lang="postcss">
.notice-temp-test-confirm {
  .popconfirm-operate {
    display: none;
  }
  .popover-content {
    &-tip {
      padding-bottom: 0 !important;
      .test-send-btn {
        margin-left: 8px;
      }
    }
  }
}
</style>
