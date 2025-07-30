<template>
  <div class="mail-notice-slider-wrapper">
    <div class="mail-notice-item">
      <div class="mail-notice-item-header">
        <div :class="['header-title', { 'header-title-lang': !curLanguageIsCn }]">
          <span>{{ $t(`m.renewalNotice['发送对象']`) }}{{ $t(`m.common['：']`) }}</span>
          <span>{{ $t(`m.renewalNotice['续期用户']`) }}</span>
        </div>
      </div>
      <div class="mail-notice-item-content" v-show="['mail'].includes(active)">
        <div class="temp-title">{{ $t(`m.renewalNotice['邮件主题']`) }}</div>
        <div class="temp-content">
          <bk-input
            v-model="noticeTempData.user_title"
            :placeholder="titlePlaceHolder"
            :clearable="true"
            @input="handleTitleInput('user', ...arguments)"
          />
          <div class="empty-error-tip" v-if="isShowUserTitleError">{{ $t(`m.renewalNotice['邮件主题为必填项']`) }}</div>
        </div>
      </div>
      <div class="mail-notice-item-content">
        <div class="temp-title">{{ $t(`m.renewalNotice['模板内容']`) }}</div>
        <div class="temp-content">
          <div class="temp-content-popover-confirm">
            <bk-popconfirm
              ref="userTextareaConfirm"
              trigger="click"
              placement="left-start"
              ext-popover-cls="user-textarea-focus-confirm"
              :width="520"
            >
              <div slot="content">
                <div class="popover-title">
                  <div class="popover-title-text">
                    {{ $t(`m.renewalNotice['内置变量']`) }}
                  </div>
                </div>
                <div class="popover-content">
                  <div class="flex-between popover-content-tip">
                    <bk-table
                      size="small"
                      ext-cls="var-table-wrapper"
                      :data="userVarTableList"
                      :max-height="360"
                      :outer-border="false"
                      :header-border="false"
                    >
                      <bk-table-column
                        prop="name"
                        :label="$t(`m.renewalNotice['变量名']`)"
                        :show-overflow-tooltip="false"
                        :width="175"
                      >
                        <template slot-scope="{ row }">
                          <div class="var-name">
                            <span class="single-hide name">{{ row.name }}</span>
                            <span class="copy" @click.stop="handleNameCopy(row.name)">
                              {{ $t(`m.common['点击复制']`) }}
                            </span>
                          </div>
                        </template>
                      </bk-table-column>
                      <bk-table-column
                        prop="description"
                        :label="$t(`m.renewalNotice['变量描述']`)"
                        :show-overflow-tooltip="true"
                      />
                      <bk-table-column :label="$t(`m.common['备注']`)" prop="remark" :show-overflow-tooltip="true" />
                      <template slot="empty">
                        <ExceptionEmpty />
                      </template>
                    </bk-table>
                  </div>
                </div>
              </div>
            </bk-popconfirm>
          </div>
          <div>
            <div
              ref="userTextarea"
              class="temp-textarea-content"
              tabindex="0"
              contenteditable="plaintext-only"
              :placeholder="$t(`m.renewalNotice['请输入模板内容']`)"
              @click.stop="handleTempFocus('user')"
              @input="handleTempInput('user', ...arguments)"
            >
              {{ noticeTempData.user_temp_html }}
            </div>
            <div class="empty-error-tip" v-if="isShowUserTempError">{{ $t(`m.renewalNotice['邮件主题为必填项']`) }}</div>
          </div>
        </div>
        <div class="temp-operate-btn">
          <bk-popconfirm
            ref="userTempTestConfirm"
            trigger="click"
            placement="bottom-start"
            ext-popover-cls="notice-temp-test-confirm"
            :width="400"
            @confirm="handleTestConfirm('user')"
          >
            <div slot="content">
              <div class="popover-content">
                <div class="flex-between popover-content-tip">
      
                  <IamUserSelector
                    ref="userSelector"
                    style="width: 100%;"
                    v-model="userTempMembers"
                    :placeholder="$t(`m.renewalNotice['请输入接收测试通知的用户（请确保账号正确）']`)"
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
            ref="userTempDefaultConfirm"
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
    <div class="mail-notice-item">
      <div class="mail-notice-item-header">
        <div :class="['header-title', { 'header-title-lang': !curLanguageIsCn }]">
          <span>{{ $t(`m.renewalNotice['发送对象']`) }}{{ $t(`m.common['：']`) }}</span>
          <span>{{ $t(`m.renewalNotice['空间管理员']`) }}</span>
        </div>
      </div>
      <div class="mail-notice-item-content" v-show="['mail'].includes(active)">
        <div class="temp-title">{{ $t(`m.renewalNotice['邮件主题']`) }}</div>
        <div class="temp-content">
          <bk-input
            v-model="noticeTempData.manager_title"
            :placeholder="titlePlaceHolder"
            :clearable="true"
            @input="handleTitleInput('manager', ...arguments)"
          />
          <div class="empty-error-tip" v-if="isShowManagerTitleError">{{ $t(`m.renewalNotice['邮件主题为必填项']`) }}</div>
        </div>
      </div>
      <div class="mail-notice-item-content">
        <div class="temp-title">{{ $t(`m.renewalNotice['模板内容']`) }}</div>
        <div class="temp-content">
          <div class="temp-content-popover-confirm">
            <bk-popconfirm
              ref="managerTextareaConfirm"
              trigger="click"
              placement="left-start"
              ext-popover-cls="manager-textarea-focus-confirm"
              :width="520"
            >
              <div slot="content">
                <div class="popover-title">
                  <div class="popover-title-text">
                    {{ $t(`m.renewalNotice['内置变量']`) }}
                  </div>
                </div>
                <div class="popover-content">
                  <div class="flex-between popover-content-tip">
                    <bk-table
                      size="small"
                      ext-cls="var-table-wrapper"
                      :data="managerVarTableList"
                      :max-height="360"
                      :outer-border="false"
                      :header-border="false"
                    >
                      <bk-table-column
                        :label="$t(`m.renewalNotice['变量名']`)"
                        :show-overflow-tooltip="false"
                        :width="175"
                        prop="name"
                      >
                        <template slot-scope="{ row }">
                          <div class="var-name">
                            <span class="single-hide name">{{ row.name }}</span>
                            <span class="copy" @click.stop="handleNameCopy">
                              {{ $t(`m.renewalNotice['点击复制']`) }}
                            </span>
                          </div>
                        </template>
                      </bk-table-column>
                      <bk-table-column
                        :label="$t(`m.renewalNotice['变量描述']`)" prop="description" :show-overflow-tooltip="true" />
                      <bk-table-column :label="$t(`m.common['备注']`)" prop="remark" :show-overflow-tooltip="true" />
                      <template slot="empty">
                        <ExceptionEmpty />
                      </template>
                    </bk-table>
                  </div>
                </div>
              </div>
            </bk-popconfirm>
          </div>
          <div>
            <div
              ref="managerTextarea"
              class="temp-textarea-content"
              tabindex="0"
              contenteditable="plaintext-only"
              :placeholder="$t(`m.renewalNotice['请输入模板内容']`)"
              @click.stop="handleTempFocus('manager')"
              @input="handleTempInput('manager', ...arguments)"
            >
              {{ noticeTempData.manager_temp_html }}
            </div>
            <div class="empty-error-tip" v-if="isShowManagerTempError">{{ $t(`m.renewalNotice['模板内容为必填项']`) }}</div>
          </div>
        </div>
        <div class="temp-operate-btn">
          <bk-popconfirm
            ref="managerTempTestConfirm"
            trigger="click"
            placement="bottom-start"
            ext-popover-cls="notice-temp-test-confirm"
            :width="400"
          >
            <div slot="content">
              <div class="popover-content">
                <div class="popover-content-tip">
                  <div class="flex-between">
                    <IamUserSelector
                      ref="managerSelector"
                      v-model="managerTempMembers"
                      style="width: 100%;"
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
            ref="managerTempDefaultConfirm"
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
  import { bus } from '@/common/bus';
  import { getDataBetweenBraces, getCopyValue, xssFilter } from '@/common/util';
  export default {
    props: {
      active: {
        type: String
      },
      detailData: {
        type: Object,
        default: () => {}
      }
    },
    data () {
      return {
        defaultLoading: false,
        sendLoading: false,
        isShowUserTitleError: false,
        isShowUserTempError: false,
        isShowManagerTitleError: false,
        isShowManagerTempError: false,
        titlePlaceHolder: this.$t(`m.renewalNotice['请输入邮件主题']`),
        noticeTempData: {
          user_title: '',
          manager_title: '',
          user_temp: '【蓝鲸权限中心】权限续期提醒\n您有以下权限操作即将到期，\n{{task.4454.name}}如有需要请及时续期{{task.4454.name}}{{task.4454.name}}{{task.4454.name}}{{task.4454.name}}{{task.4454.name}}',
          manager_temp: '【蓝鲸权限中心】权限续期提醒\n您管理的用户组有成员的权限即将过期，如有需要请及时续期\n{{task.a55pp.name}}',
          user_temp_html: '',
          manager_temp_html: ''
        },
        noticeTempDataBack: {},
        tempDetail: {},
        userTempMembers: [],
        managerTempMembers: [],
        userVarTableList: [
          {
            name: '{{permission_list_content}}',
            description: '过期的内容',
            remark: '不同渠道展示内容不同，可预览查看'
          },
          {
            name: '{{permission_renewal_link}}',
            description: '续期详情链接',
            remark: '该链接可跳转至权限中心的续期页面'
          }
        ],
        managerVarTableList: []
      };
    },
    watch: {
      detailData: {
        async handler (value) {
          this.handleResetTempSliderData();
          this.tempDetail = { ...value };
          await this.fetchNoticeTemplateDetail();
          this.noticeTempDataBack = cloneDeep(this.noticeTempData);
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

      handleTempFocus (payload) {
        this.$nextTick(() => {
          const typeMap = {
            user: () => {
              const userTempRef = this.$refs.userTextareaConfirm;
              if (userTempRef && userTempRef.$refs) {
                userTempRef.$refs.popover.showHandler();
                if (window.innerWidth < 1600) {
                  bus.$emit('on-change-temp-zIndex', { zIndex: 99 });
                }
              }
            },
            manager: () => {
              const managerTempRef = this.$refs.managerTextareaConfirm;
              if (managerTempRef && managerTempRef.$refs) {
                managerTempRef.$refs.popover.showHandler();
                if (window.innerWidth < 1600) {
                  bus.$emit('on-change-temp-zIndex', { zIndex: 99 });
                }
              }
            }
          };
          typeMap[payload]();
        });
      },

      handleTitleInput (type, payload) {
        const typeMap = {
          user: () => {
            this.isShowUserTitleError = !payload.trim();
          },
          manager: () => {
            this.isShowManagerTitleError = !payload.trim();
          }
        };
        return typeMap[type]();
      },

      handleTempInput (type, e) {
        const { innerText, innerHTML } = e.target;
        const typeMap = {
          user: () => {
            this.isShowUserTempError = !innerText.trim();
            this.noticeTempData.user_temp_html = xssFilter(innerHTML);
          },
          manager: () => {
            this.isShowManagerTempError = !innerText.trim();
            this.noticeTempData.manager_temp_html = xssFilter(innerHTML);
          }
        };
        return typeMap[type]();
      },

      handleUserChange (payload) {
        this.userTempMembers = [...payload];
      },

      handleUserOperate (payload) {
        const typeMap = {
          test: () => {
            this.$nextTick(() => {
              const userTempRef = this.$refs.userTempTestConfirm;
              if (userTempRef && userTempRef.$refs) {
                userTempRef.$refs.popover.showHandler();
                this.$refs.userSelector && this.$refs.userSelector.handleSetAutoFocus();
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
            const managerTempTestConfirm = this.$refs.managerTempTestConfirm;
            if (managerTempTestConfirm && managerTempTestConfirm.$refs) {
              managerTempTestConfirm.$refs.popover.showHandler();
              this.$refs.managerSelector && this.$refs.managerSelector.handleSetAutoFocus();
            }
          },
          reset: () => {},
          default: () => {
            const managerTempDefaultConfirm = this.$refs.managerTempDefaultConfirm;
            if (managerTempDefaultConfirm && managerTempDefaultConfirm.$refs) {
              managerTempDefaultConfirm.$refs.popover.showHandler();
            }
          }
        };
        return typeMap[payload]();
      },

      handleNameCopy (payload) {
        getCopyValue(payload);
      },

      handleReplaceHtmlText () {
        this.$nextTick(() => {
          let userTemp = '';
          let managerTemp = '';
          const reg = /{{([^}]+)}}/g;
          const userTextList = getDataBetweenBraces(this.noticeTempData.user_temp, reg);
          const managerTextList = getDataBetweenBraces(this.noticeTempData.manager_temp, reg);
          if (userTextList && userTextList.length > 0) {
            for (let i = 0; i < userTextList.length; i++) {
              userTemp = this.noticeTempData.user_temp.replaceAll(`{{${userTextList[i]}}}`, `<span style=\'color: #3a84ff;position: relative;\'>{{${userTextList[i]}}}</span>`);
            }
            this.noticeTempData.user_temp_html = cloneDeep(xssFilter(userTemp));
            this.$refs.userTextarea.innerHTML = xssFilter(userTemp);
          }
          if (managerTextList && managerTextList.length > 0) {
            for (let i = 0; i < managerTextList.length; i++) {
              managerTemp = this.noticeTempData.manager_temp.replaceAll(`{{${managerTextList[i]}}}`, `<span style=\'color: #3a84ff;position: relative;z-index: 10000;line-height: 29px;left: 1px;\'>{{${managerTextList[i]}}}</span>`);
            }
            this.noticeTempData.manager_temp_html = cloneDeep(xssFilter(managerTemp));
            this.$refs.managerTextarea.innerHTML = xssFilter(managerTemp);
          }
        });
      },

      handleResetTempSliderData () {
        this.isShowUserTitleError = false;
        this.isShowUserTempError = false;
        this.isShowManagerTitleError = false;
        this.isShowManagerTempError = false;
      }
    }
  };
</script>
      
<style lang="postcss" scoped>
.mail-notice-slider-wrapper {
  .mail-notice-item {
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
        &-popover-confirm {
          height: 0;
        }
        .temp-textarea-content {
          width: 100%;
          height: 122px;
          padding: 5px 10px;
          /* resize: both; */
          overflow: auto;
          border: 1px solid #c4c6cc;
          background-color: #ffffff;
          display: block;
          box-sizing: border-box;
          font-size: 12px;
          outline: none;
          &:empty {
            &::before {
              content: attr(placeholder);
              color: #c4c6cc;
            }
          }
          &:focus {
            border-color: #3a84ff;
            &::before {
              content: none;
            }
          }
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
      .empty-error-tip {
        color: #ff5656;
        font-size: 12px;
        margin-top: 4px;
      }
    }
    &:first-child {
      margin-bottom: 0;
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
.user-textarea-focus-confirm,
.manager-textarea-focus-confirm {
  .popover-title {
    font-size: 12px;
    color: #313238;
    margin-bottom: 5px;
  }
  .popover-content {
    .var-table-wrapper {
      .var-name {
        display: flex;
        align-items: center;
        .name {
          max-width: 170px;
          word-break: break-all;
        }
        .copy {
          display: none;
        }
        &:hover {
          .name {
            max-width: 95px;
          }
          .copy {
            display: block;
            color: #3a84ff;
            cursor: pointer;
          }
        }
      }
    }
  }
}
</style>

<style lang="postcss">
.notice-temp-test-confirm,
.user-textarea-focus-confirm,
.manager-textarea-focus-confirm {
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
