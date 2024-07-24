<template>
  <div
    class="iam-transfer-wrapper"
    :class="[
      'iam-transfer-wrapper',
      { 'iam-transfer-wrapper-lang': !curLanguageIsCn }
    ]"
    v-bkloading="{ isLoading: submitLoading, opacity: 1 }"
  >
    <bk-button
      v-if="isShowHandoverHistory"
      text
      class="handover-history-btn"
      @click="goPermTransferHistory"
    >
      {{ $t(`m.permTransfer['交接历史']`) }}
    </bk-button>

    <div
      class="iam-transfer-group-wrapper"
      :style="{
        minHeight: isLoading ? '328px' : 0,
        'marginBottom': '68px'
      }"
      v-bkloading="{ isLoading, opacity: 1 }"
    >
      <div class="transfer-group-content">
        <div class="content">
          <div ref="formWrapper" class="transfer-content">
            <bk-form :model="formData" ref="permTransferForm">
              <iam-form-item :label="$t(`m.permTransfer['交接对象']`)" required>
                <bk-user-selector
                  :multiple="false"
                  :value="formData.members"
                  :api="userApi"
                  :placeholder="$t(`m.verify['请填写管理员']`)"
                  :empty-text="$t(`m.common['无匹配人员']`)"
                  style="width: 100%;"
                  :class="isShowMemberError ? 'is-member-empty-cls' : ''"
                  @focus="handleRtxFocus"
                  @blur="handleRtxBlur"
                  @change="handleRtxChange">
                </bk-user-selector>
                <p class="name-empty-error" v-if="isShowMemberError">
                  {{ $t(`m.verify['请填写管理员']`) }}
                </p>
                <p class="name-empty-error" v-if="isPermissionsPrompt">
                  {{ $t(`m.verify['目标交接人不能为本人']`) }}
                </p>
              </iam-form-item>
              <iam-form-item :label="$t(`m.permTransfer['交接理由']`)" required>
                <bk-input
                  type="textarea"
                  v-model="formData.reason"
                  :maxlength="100"
                  :class="[{ 'group-name-error': isShowReasonError }]"
                  :placeholder="$t(`m.verify['请输入']`)"
                  @input="handleReasonInput"
                  @blur="handleReasonBlur"
                  @change="handleReasonChange"
                />
                <p class="name-empty-error" v-if="isShowReasonError">{{ reasonValidateText }}</p>
              </iam-form-item>
              <iam-form-item :label="$t(`m.permTransfer['交接预览']`)" :required="false">
                <bk-input
                  type="textarea"
                  v-model="formData.reason"
                  :maxlength="100"
                  :class="isShowReasonError ? 'group-name-error' : ''"
                  @input="handleReasonInput"
                  @blur="handleReasonBlur"
                  @change="handleReasonChange"
                  :placeholder="$t(`m.verify['请输入']`)"
                />
                <p class="name-empty-error" v-if="isShowReasonError">{{ reasonValidateText }}</p>
              </iam-form-item>
            </bk-form>
          </div>
        </div>
      </div>
    </div>

    <Group @group-selection-change="handleGroupSelection" />

    <Custom
      v-if="!externalSystemsLayout.myPerm.transfer.hideCustomData"
      @custom-selection-change="handleCustomSelection" />

    <Manager
      v-if="!externalSystemsLayout.myPerm.transfer.hideManagerData"
      @manager-selection-change="handleManagerSelection"
    />

    <div
      class="fixed-action"
      :style="{
        'height': '50px',
        paddingLeft: externalSystemsLayout.myPerm.transfer.setFooterBtnPadding ?
          '24px' : fixedActionPaddingLeft
      }"
    >
      <bk-button theme="primary" @click="handleSubmit">
        {{ $t(`m.common['提交']`) }}
      </bk-button>
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { ALL_PERM_GROUP_LIST } from '@/common/constants';
  import BkUserSelector from '@blueking/user-selector';
  import Group from './group.vue';
  import Custom from './custom.vue';
  import Manager from './manager.vue';

  export default {
    components: {
      Group,
      Custom,
      Manager,
      BkUserSelector
    },
    data () {
      return {
        userApi: window.BK_USER_API,
        enablePermissionHandover: window.ENABLE_PERMISSION_HANDOVER,
        fixedActionPaddingLeft: '284px',
        groupSelectData: [],
        customSelectData: {},
        managerSelectData: [],
        allPermTypeTab: ALL_PERM_GROUP_LIST.map((v) => {
          return {
            ...v,
            ...{
              count: 0
            }
          };
        }),
        formData: {
          members: [],
          reason: ''
        },
        isShowMemberError: false,
        isShowReasonError: false,
        submitLoading: false,
        isPermissionsPrompt: false,
        isLoading: false,
        reasonValidateText: '',
        pageContainer: null
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemsLayout']),
      ...mapGetters('perm', ['handoverData']),
      isShowHandoverHistory () {
        return this.enablePermissionHandover.toLowerCase() === 'true' && !this.externalSystemsLayout.myPerm.transfer.hideTextBtn;
      }
    },
    mounted () {
      console.log(this.handoverData, '交接数据');
      this.pageContainer = document.querySelector('.main-scroller');
      bus.$on('nav-resize', flag => {
        if (flag) {
          this.fixedActionPaddingLeft = '284px';
        } else {
          this.fixedActionPaddingLeft = '84px';
        }
      });
    },
    methods: {
      handleGroupSelection (list) {
        this.groupSelectData.splice(0, this.groupSelectData.length, ...list);
      },
      handleCustomSelection (data) {
        // this.customSelectData.splice(0, this.customSelectData.length, ...list)
        this.customSelectData = Object.assign({}, data);
      },
      handleManagerSelection (list) {
        this.managerSelectData.splice(0, this.managerSelectData.length, ...list);
      },
      handleRtxFocus () {
        this.isShowMemberError = false;
        this.isPermissionsPrompt = false;
      },
      handleRtxBlur () {
        if (this.formData.members.length && this.user.username === this.formData.members[0]) {
          this.isPermissionsPrompt = true;
          return;
        }
        this.isShowMemberError = this.formData.members.length < 1;
      },
      handleReasonInput () {
        this.isShowReasonError = false;
        this.reasonValidateText = '';
      },
      handleRtxChange (payload) {
        this.isShowMemberError = false;
        this.isPermissionsPrompt = false;
        this.formData.members = payload;
      },

      handleReasonBlur (payload) {
        if (payload.trim() === '') {
          this.reasonValidateText = this.$t(`m.permTransfer['权限交接理由必填']`);
          this.isShowReasonError = true;
        }
        if (!this.isShowReasonError) {
          const maxLength = 100;
          if (payload.trim().length > maxLength) {
            this.reasonValidateText = this.$t(`m.permTransfer['权限交接理由最长不超过100个字符']`);
            this.isShowReasonError = true;
          }
        }
      },

      handleReasonChange (value) {
        this.formData.reason = value;
      },

      handleValidator () {
        const maxLength = 100;
        const { reason, members } = this.formData;
        if (reason === '') {
          this.reasonValidateText = this.$t(`m.permTransfer['权限交接理由必填']`);
          this.isShowReasonError = true;
        }
        if (!this.isShowNameError) {
          if (reason.trim().length > maxLength) {
            this.reasonValidateText = this.$t(`m.permTransfer['权限交接理由最长不超过100个字符']`);
            this.isShowReasonError = true;
          }
        }

        this.isShowMemberError = members.length < 1;

        return !this.isShowReasonError && !this.isShowMemberError;
      },

      async handleSubmit () {
        if (!this.groupSelectData.length
          && !Object.keys(this.customSelectData).length
          && !this.managerSelectData.length
        ) {
          this.messageWarn(this.$t(`m.permTransfer['还未选择权限']`));
          return;
        }
        if (this.formData.members.length && this.user.username === this.formData.members[0]) {
          this.isPermissionsPrompt = true;
          return;
        }
        if (!this.handleValidator()) {
          const top = this.$refs.formWrapper.getBoundingClientRect().top
            + this.pageContainer.scrollTop;

          this.pageContainer.scrollTo({
            top: top - 61, // 减去顶导的高度 61
            behavior: 'smooth'
          });
          return;
        }
        const groupIds = [];
        this.groupSelectData.forEach(item => {
          groupIds.push(item.id);
        });
        const roleIds = [];
        this.managerSelectData.forEach(item => {
          roleIds.push(item.id);
        });
        const customPolicies = [];
        Object.keys(this.customSelectData).forEach(key => {
          const customPolicy = {
            system_id: key,
            policy_ids: []
          };
          this.customSelectData[key].forEach(policyInfo => {
            customPolicy.policy_ids.push(policyInfo.policy_id);
          });
          customPolicies.push(customPolicy);
        });
        const submitData = {
          handover_to: this.formData.members[0],
          reason: this.formData.reason,
          handover_info: {
            group_ids: groupIds,
            role_ids: roleIds,
            custom_policies: customPolicies
          }
        };
        try {
          this.submitLoading = true;
          await this.$store.dispatch('perm/permTransfer', submitData);
          this.$bkMessage({
            theme: 'success',
            delay: 500,
            message: this.$t(`m.permTransfer['权限交接成功']`),
            onClose: () => {
              this.$router.push({
                name: 'myPerm'
              });
            }
          });
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.submitLoading = false;
        }
      },

      // 权限交接历史
      goPermTransferHistory () {
        this.$router.push({
          name: 'permTransferHistory'
        });
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-transfer-wrapper {
  padding-bottom: 44px;
  .handover-history-btn {
     position: relative;
     top: -13px;
     width: 100%;
     text-align: right;
  }
  .fixed-action {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1899;
    display: flex;
    align-items: center;
    height: 52px;
    background: #ffffff;
    box-shadow: 0px -2px 4px 0px rgba(0, 0, 0, 0.06);
  }
  /deep/ .transfer-content {
    .bk-form-item+.bk-form-item {
      margin-top: 24px;
    }
    .iam-form-item {
      padding: 0 32px;
      &:first-child {
        margin-top: 24px;
      }
      &:last-child {
        margin-bottom: 24px;
      }
      .bk-label {
        font-weight: 700;
        font-size: 14px;
        color: #63656E;
      }
      .bk-form-content {
        font-size: 0;
        line-height: 1;
        margin-left: 80px !important;
      }
    }
    .name-empty-error {
      font-size: 12px;
      color: #ff4d4d;
      margin-top: 4px;
    }
    .is-member-empty-cls {
      .user-selector-container {
        border-color: #ff4d4d !important;
      }
    }
    .group-name-error {
      .bk-textarea-wrapper {
        border-color: #ff5656;
      }
    }
  }
  &-lang {
    /deep/ .transfer-content {
      .iam-form-item {
        .bk-form-content {
          margin-left: 150px !important;
        }
      }
    }
  }
}
</style>
