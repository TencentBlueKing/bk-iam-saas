<template>
  <div
    v-bkloading="{ isLoading: submitLoading, opacity: 1 }"
    ref="iamTransferPerm"
    :class="[
      'iam-transfer-wrapper',
      { 'iam-transfer-wrapper-lang': !curLanguageIsCn },
      { 'no-fixed-footer-wrapper': !isFixedFooter }
    ]"
  >
    <bk-button
      v-if="isShowHandoverHistory"
      text
      class="handover-history-btn"
      @click="handleNavPermTransferHistory"
    >
      {{ $t(`m.permTransfer['交接历史']`) }}
    </bk-button>
    <smart-action
      class="iam-transfer-group-wrapper"
      v-bkloading="{ isLoading, opacity: 1 }"
    >
      <render-horizontal-block class="transfer-group-content">
        <div class="content">
          <div ref="formWrapper" class="transfer-content">
            <bk-form :model="formData" ref="permTransferForm">
              <IamFormItem :label="$t(`m.permTransfer['交接对象']`)" required>
                <BkUserSelector
                  :multiple="false"
                  :value="formData.members"
                  :api="userApi"
                  :placeholder="$t(`m.verify['请填写管理员']`)"
                  :empty-text="$t(`m.common['无匹配人员']`)"
                  style="width: 100%;"
                  :class="isShowMemberError ? 'is-member-empty-cls' : ''"
                  @focus="handleRtxFocus"
                  @blur="handleRtxBlur"
                  @change="handleRtxChange"
                />
                <p class="name-empty-error" v-if="isShowMemberError">
                  {{ $t(`m.verify['请填写管理员']`) }}
                </p>
                <p class="name-empty-error" v-if="isPermissionsPrompt">
                  {{ $t(`m.verify['目标交接人不能为本人']`) }}
                </p>
              </IamFormItem>
              <IamFormItem :label="$t(`m.permTransfer['交接理由']`)" required>
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
              </IamFormItem>
              <IamFormItem :label="$t(`m.permTransfer['交接预览']`)" :required="false">
                <div class="transfer-preview" ref="formPermReview">
                  <div
                    v-for="item in allPermTab"
                    :key="item.id"
                    :class="[
                      'transfer-preview-tab',
                      { 'is-active': activeTab === item.id }
                    ]"
                    @click.stop="handleTabChange(item)"
                  >
                    <div class="transfer-preview-tab-item">
                      <span class="tab-name">{{ item.name }}</span>
                      <span class="tab-count">{{ item.pagination.count }}</span>
                    </div>
                  </div>
                </div>
                <component
                  :is="curCom(activeTab)"
                  :ref="`childPerm_${activeTab}`"
                  :cur-perm-data="formatTabPermData"
                  :selected-handover-object="formData.members"
                  :description="formData.reason"
                  @on-page-change="handlePageChange"
                  @on-limit-change="handleLimitChange"
                  @group-selection-change="handleGroupSelection"
                  @custom-selection-change="handleCustomSelection"
                  @manager-selection-change="handleManagerSelection"
                />
                <!-- <p class="name-empty-error" v-if="isShowReasonError">{{ reasonValidateText }}</p> -->
              </IamFormItem>
            </bk-form>
          </div>
        </div>
        <div class="transfer-footer no-fixed-footer" v-if="!isFixedFooter">
          <bk-button theme="primary" @click.stop="handleSubmit">
            {{ $t(`m.common['提交']`) }}
          </bk-button>
          <bk-button @click.stop="handleCancel">
            {{ $t(`m.common['取消']`) }}
          </bk-button>
        </div>
      </render-horizontal-block>
      <div slot="action" class="transfer-footer" v-if="isFixedFooter">
        <bk-button theme="primary" @click.stop="handleSubmit">
          {{ $t(`m.common['提交']`) }}
        </bk-button>
        <bk-button @click.stop="handleCancel">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </div>
    </smart-action>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { ALL_PERM_GROUP_LIST } from '@/common/constants';
  import { existValue, formatCodeData, sleep, getNowTimeExpired } from '@/common/util';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import BkUserSelector from '@blueking/user-selector';
  import Group from './group.vue';
  import Custom from './custom.vue';
  import Manager from './manager.vue';

  export default {
    inject: ['showNoticeAlert'],
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
        allPermTab: [],
        groupSelectData: [],
        customSelectData: {},
        managerSelectData: [],
        initConfigData: {
          loading: false,
          pagination: {
            current: 1,
            limit: 10,
            count: 0,
            showTotalCount: true
          },
          emptyData: {
            type: 'empty',
            text: '暂无数据',
            tip: '',
            tipType: ''
          },
          list: []
        },
        formData: {
          members: [],
          reason: ''
        },
        submitDataBack: {},
        isShowMemberError: false,
        isShowReasonError: false,
        submitLoading: false,
        isPermissionsPrompt: false,
        isFixedFooter: false,
        isLoading: false,
        activeTab: 'personalPerm',
        reasonValidateText: '',
        comKey: -1
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemsLayout', 'externalSystemId']),
      ...mapGetters('perm', ['handoverData']),
      isShowCustomPerm () {
        return !this.externalSystemsLayout.myPerm.transfer.hideCustomData;
      },
      isShowManagerPerm () {
        return !this.externalSystemsLayout.myPerm.transfer.hideManagerData;
      },
      isShowHandoverHistory () {
        return this.enablePermissionHandover.toLowerCase() === 'true' && !this.externalSystemsLayout.myPerm.transfer.hideTextBtn;
      },
      curCom () {
        return (payload) => {
          let com = '';
          const list = new Map([
            [['personalPerm', 'renewalPersonalPerm'], 'Group'],
            [['customPerm', 'renewalCustomPerm'], 'Custom'],
            [['managerPerm'], 'Manager']
          ]);
          for (const [key, value] of list.entries()) {
            if (key.includes(payload)) {
              com = value;
              break;
            }
          }
          return com;
        };
      },
      formatTabPermData () {
        const curData = this.allPermTab.find((v) => v.id === this.activeTab);
        if (curData) {
          return curData;
        }
        return this.initConfigData;
      }
    },
    watch: {
      formData: {
        handler () {
          this.handleRtxLeavePage();
        },
        deep: true
      }
    },
    created () {
      this.getAllPermHandoverTab();
      this.fetchInitData();
    },
    mounted () {
      console.log(this.handoverData, '交接数据');
      this.handleGetPageHeight();
      window.addEventListener('resize', this.handleGetPageHeight);
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.handleGetPageHeight);
      });
      this.submitDataBack = Object.assign({}, {
        ...this.formData,
        ...this.customSelectData,
        ...{
          list: [...this.groupSelectData, ...this.managerSelectData]
        }
      });
    },
    methods: {
      async fetchInitData () {
        await Promise.all([this.fetchPersonalGroupData(), this.fetchManagerGroupData()]);
      },

      async fetchPersonalGroupData () {
        let curData = this.allPermTab.find((v) => ['personalPerm', 'renewalPersonalPerm'].includes(v.id));
        if (!curData) {
          return;
        }
        curData.loading = true;
        const { emptyData, pagination } = curData;
        try {
          const { current, limit } = pagination;
          const params = {
            page_size: limit,
            page: current
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
          }
          const { code, data } = await this.$store.dispatch('perm/getPersonalGroups', params);
          const totalCount = data.count || 0;
          const tableList = data.results || [];
          curData = Object.assign(curData, {
            list: tableList,
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          curData.list && curData.list.forEach((v) => {
            if (String(v.department_id) !== '0' || v.expired_at < getNowTimeExpired()) {
              v.canNotTransfer = true;
            }
            this.$set(v, 'reason', this.formData.reason);
            this.$set(v, 'handover_object', this.formData.members);
          });
        } catch (e) {
          curData = Object.assign(curData, {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.messageAdvancedError(e);
        } finally {
          sleep(500).then(() => {
            curData.loading = false;
          });
        }
      },

      async fetchManagerGroupData () {
        let curData = this.allPermTab.find((v) => ['managerPerm'].includes(v.id));
        if (!curData) {
          return;
        }
        curData.loading = true;
        const { emptyData, pagination } = curData;
        try {
          const { current, limit } = pagination;
          const params = {
            limit,
            offset: (current - 1) * limit,
            with_super: true
          };
          const { code, data } = await this.$store.dispatch('role/getRatingManagerList', params);
          const totalCount = data.count || 0;
          const list = data.results || [];
          curData = Object.assign(curData, {
            list,
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          curData.list.forEach((v) => {
            this.$set(v, 'handover_object', this.formData.members);
          });
        } catch (e) {
          curData = Object.assign(curData, {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.messageAdvancedError(e);
        } finally {
          sleep(500).then(() => {
            curData.loading = false;
          });
        }
      },
      
      async handleSubmit () {
        if (this.formData.members.length && this.user.username === this.formData.members[0]) {
          this.isPermissionsPrompt = true;
          return;
        }
        if (!this.handleValidator()) {
          this.scrollToLocation(this.$refs.iamTransferPerm);
          return;
        }
        if (!this.groupSelectData.length
          && !Object.keys(this.customSelectData).length
          && !this.managerSelectData.length
        ) {
          this.messageWarn(this.$t(`m.permTransfer['还未选择权限']`));
          this.scrollToLocation(this.$refs.formPermReview);
          return;
        }
        const groupIds = [];
        const roleIds = [];
        const customPolicies = [];
        this.groupSelectData.forEach(item => {
          groupIds.push(item.id);
        });
        this.managerSelectData.forEach(item => {
          roleIds.push(item.id);
        });
        Object.keys(this.customSelectData).forEach((key) => {
          const customPolicy = {
            system_id: key,
            policy_ids: []
          };
          this.customSelectData[key].forEach((policyInfo) => {
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

      handleTabChange (payload) {
        this.activeTab = payload.id;
        const curData = this.allPermTab.find((v) => v.id === this.activeTab);
        if (curData) {
          this.handleGetPaginationData(curData.pagination);
        }
        this.handleGetPageHeight();
      },

      handleGetPaginationData (payload) {
        const curData = this.allPermTab.find((v) => v.id === this.activeTab);
        if (curData) {
          curData.pagination = Object.assign(curData.pagination, payload);
          const typeMap = {
            personalPerm: async () => {
              await this.fetchPersonalGroupData();
              this.$nextTick(() => {
                this.$refs[`childPerm_${this.activeTab}`].handleGetCheckData();
              });
            },
            managerPerm: async () => {
              await this.fetchManagerGroupData();
              this.$nextTick(() => {
                this.$refs[`childPerm_${this.activeTab}`].handleGetCheckData();
              });
            }
          };
          if (typeMap[this.activeTab]) {
            return typeMap[this.activeTab]();
          }
        }
      },

      handlePageChange (payload) {
        this.handleGetPaginationData(payload);
      },

      handleLimitChange (payload) {
        this.handleGetPaginationData(payload);
      },

      handleGroupSelection (payload) {
        this.groupSelectData.splice(0, this.groupSelectData.length, ...payload);
        this.handleRtxLeavePage();
      },

      handleCustomSelection (payload) {
        this.customSelectData = Object.assign({}, payload);
        console.log(this.customSelectData);
        this.handleRtxLeavePage();
      },

      handleManagerSelection (payload) {
        this.managerSelectData.splice(0, this.managerSelectData.length, ...payload);
        this.handleRtxLeavePage();
      },

      handleRtxFocus () {
        this.isShowMemberError = false;
        this.isPermissionsPrompt = false;
      },

      handleRtxBlur () {
        const { members } = this.formData;
        if (members.length && members.includes(this.user.username)) {
          this.isPermissionsPrompt = true;
          return;
        }
        this.isShowMemberError = members.length < 1;
      },

      handleReasonInput () {
        this.isShowReasonError = false;
        this.reasonValidateText = '';
      },

      handleRtxChange (payload) {
        this.isShowMemberError = false;
        this.isPermissionsPrompt = false;
        this.formData.members = [...payload];
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
        if (reason.trim() === '') {
          this.reasonValidateText = this.$t(`m.permTransfer['权限交接理由必填']`);
          this.isShowReasonError = true;
        }
        if (reason.trim().length > maxLength) {
          this.reasonValidateText = this.$t(`m.permTransfer['权限交接理由最长不超过100个字符']`);
          this.isShowReasonError = true;
        }
        this.isShowMemberError = members.length < 1;
        return !this.isShowReasonError && !this.isShowMemberError;
      },

      handleCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(() => {
          this.$router.go(-1);
        }, _ => _);
      },

      handleNavPermTransferHistory () {
        this.$router.push({
          name: 'permTransferHistory'
        });
      },

      handleRtxLeavePage () {
        const submitData = {
          ...this.formData,
          ...this.customSelectData,
          ...{
            list: [...this.groupSelectData, ...this.managerSelectData]
          }
        };
        window.changeDialog = JSON.stringify(this.submitDataBack) !== JSON.stringify(submitData);
      },

      handleGetPageHeight () {
        this.$nextTick(() => {
          const noticeComHeight = this.showNoticeAlert && this.showNoticeAlert() ? 40 : 0;
          const viewHeight = window.innerHeight - 51 - 51 - noticeComHeight;
          this.isFixedFooter = this.$refs.iamTransferPerm.offsetHeight > viewHeight;
        });
      },

      getAllPermHandoverTab () {
        if (existValue('externalApp') && this.externalSystemId) {
          let hidePermTab = [];
          if (!this.isShowCustomPerm) {
            hidePermTab = ['customPerm'];
          }
          if (!this.isShowManagerPerm) {
            hidePermTab = [...hidePermTab, ...['managerPerm']];
          }
          this.allPermTab = ALL_PERM_GROUP_LIST.filter((item) => !hidePermTab.includes(item.id)).map((v) => {
            return {
              ...v,
              ...this.initConfigData
            };
          });
        } else {
          this.allPermTab = ALL_PERM_GROUP_LIST.filter((item) => ['personalPerm', 'customPerm', 'managerPerm'].includes(item.id)).map((v) => {
            return {
              ...v,
             ...this.initConfigData
            };
          });
        }
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-transfer-wrapper {
  .handover-history-btn {
     width: 100%;
     position: relative;
     top: -13px;
     text-align: right;
  }
  /deep/ .iam-transfer-group-wrapper {
    .horizontal-item {
      padding: 0;
      margin-bottom: 32px;
      .label {
        min-width: 0 !important;
        width: 0;
      }
      .content {
        .transfer-content {
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
              .transfer-preview {
                display: flex;
                background-color: #F0F1F5;
                color: #313238;
                font-size: 14px;
                border: 1px solid #DCDEE5;
                &-tab {
                  min-width: 140px;
                  border-right: 1px solid #DCDEE5;
                  cursor: pointer;
                  &-item {
                    display: flex;
                    align-items: center;
                    padding: 16px 24px;
                    .tab-count {
                      min-width: 16px;
                      height: 16px;
                      line-height: 16px;
                      padding: 0 8px;
                      margin-left: 8px;
                      border-radius: 8px;
                      text-align: center;
                      font-size: 12px;
                      color: #63656E;
                      background-color: #DCDEE5;
                    }
                  }
                  &.is-active {
                    margin-bottom: -1px;
                    color: #3a84ff;
                    background-color: #ffffff;
                    border-top: 4px solid #3a84ff;
                    .transfer-preview-tab-item {
                      padding: 12px 24px 16px 24px;
                      .tab-count {
                        background-color: #E1ECFF;
                        color: #3a84ff;
                      }
                    }
                  }
                }
              }
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
      }
    }
  }
  /deep/ .transfer-footer {
    font-size: 0;
    padding-left: 108px;
    .bk-button {
      min-width: 88px;
      margin-right: 8px;
    }
  }
  /deep/ [role~="action-position"] {
    margin-top: 0 !important;
  }
  &-lang {
    /deep/ .iam-transfer-group-wrapper {
      .horizontal-item {
        .content {
          .transfer-content {
            .iam-form-item {
              .bk-form-content {
                margin-left: 151px !important;
              }
            }
          }
        }
      }
    }
    /deep/ .transfer-footer {
      padding-left: 180px;
    }
  }
  &.no-fixed-footer-wrapper {
    /deep/ .iam-transfer-group-wrapper {
      .horizontal-item {
        padding: 0 0 24px 0;
        margin-bottom: 16px;
      }
    }
    /deep/ [role~="action-position"] {
      display: none;
    }
  }
}
</style>
