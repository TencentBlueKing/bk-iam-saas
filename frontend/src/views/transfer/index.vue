<template>
  <div class="iam-transfer-wrapper" v-bkloading="{ isLoading: submitLoading, opacity: 1 }">
    <bk-button
      v-if="enablePermissionHandover.toLowerCase() === 'true'
        && !externalSystemsLayout.myPerm.transfer.hideTextBtn"
      data-test-id="permTransfer_btn_history"
      text
      style="position: relative; top: -13px; width: 100%; text-align: right;"
      @click="goPermTransferHistory">
      {{ $t(`m.permTransfer['交接历史']`) }}
    </bk-button>

    <Group @group-selection-change="handleGroupSelection" />

    <Custom
      v-if="!externalSystemsLayout.myPerm.transfer.hideCustomData"
      @custom-selection-change="handleCustomSelection" />

    <Manager
      v-if="!externalSystemsLayout.myPerm.transfer.hideManagerData"
      @manager-selection-change="handleManagerSelection" />

    <div class="iam-transfer-group-wrapper"
      :style="{
        minHeight: isLoading ? '328px' : 0,
        'marginBottom': '68px'
      }"
      v-bkloading="{ isLoading, opacity: 1 }">
      <div class="transfer-group-content">
        <div class="input-header">
          <label class="title">{{ $t(`m.permTransfer['将以上权限交接给']`) }}</label>
        </div>
        <div class="content">
          <div
            ref="formWrapper"
            :class="[
              'input-content',
              { 'input-content-lang': !curLanguageIsCn }
            ]"
          >
            <bk-form :model="formData" form-type="vertical" :rules="rules" ref="permTransferForm">
              <iam-form-item :label="$t(`m.permTransfer['交接人']`)" required>
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
              <iam-form-item :label="$t(`m.common['理由']`)" required>
                <bk-input
                  type="textarea"
                  v-model="formData.reason"
                  :maxlength="100"
                  :class="isShowReasonError ? 'group-name-error' : ''"
                  @input="handleReasonInput"
                  @blur="handleReasonBlur"
                  @change="handleReasonChange"
                  :placeholder="$t(`m.verify['请输入']`)">
                </bk-input>
                <p class="name-empty-error" v-if="isShowReasonError">{{ reasonValidateText }}</p>
              </iam-form-item>
            </bk-form>
          </div>
        </div>
      </div>
    </div>

    <!-- <div style="background: red; height: 800px;"></div> -->
    <div
      class="fixed-action"
      style="height: 50px;"
      :style="{
        paddingLeft: externalSystemsLayout.myPerm.transfer.setFooterBtnPadding ?
          '24px' : fixedActionPaddingLeft
      }"
    >
      <bk-button theme="primary" @click="submit">
        {{ $t(`m.common['提交']`) }}
      </bk-button>
    </div>
  </div>
</template>
<script>
    // import _ from 'lodash'
  import BkUserSelector from '@blueking/user-selector';

  import { bus } from '@/common/bus';
  import Group from './group.vue';
  import Custom from './custom.vue';
  import Manager from './manager.vue';
  import { mapGetters } from 'vuex';

  export default {
    name: '',
    components: {
      Group,
      Custom,
      Manager,
      BkUserSelector
    },
    data () {
      return {
        fixedActionPaddingLeft: '284px',
        groupSelectData: [],
        customSelectData: {},
        managerSelectData: [],
        formData: { members: [], reason: '' },
        isShowMemberError: false,
        isShowReasonError: false,
        reasonValidateText: '',
        userApi: window.BK_USER_API,
        pageContainer: null,
        submitLoading: false,
        enablePermissionHandover: window.ENABLE_PERMISSION_HANDOVER,
        isPermissionsPrompt: false
      };
    },
    computed: {
            ...mapGetters(['user', 'externalSystemsLayout'])
    },
    created () {
      // this.fetchCategories()
    },
    mounted () {
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
      // async fetchCategories () {
      //     try {
      //         const res = await this.$store.dispatch('organization/getCategories')
      //         const categories = [...res.data]
      //         categories.forEach((item, index) => {
      //             item.visiable = true
      //             item.level = 0
      //             item.showRadio = false
      //             item.selected = false
      //             item.expanded = index === 0
      //             item.count = 0
      //             item.disabled = !item.departments || item.departments.length < 1
      //             item.type = 'depart'
      //             item.showCount = false
      //             item.async = item.departments && item.departments.length > 0
      //             item.isNewMember = false
      //             item.loading = false
      //             item.is_selected = false
      //             item.parentNodeId = ''
      //             item.id = `${item.id}&${item.level}`
      //             if (item.departments && item.departments.length > 0) {
      //                 item.departments.forEach((child, childIndex) => {
      //                     child.visiable = false
      //                     child.level = 1
      //                     child.loading = false
      //                     child.showRadio = false
      //                     child.selected = false
      //                     child.expanded = false
      //                     child.disabled = false
      //                     child.type = 'depart'
      //                     child.count = child.recursive_member_count
      //                     child.showCount = true
      //                     child.async = child.child_count > 0 || child.member_count > 0
      //                     child.isNewMember = false
      //                     child.parentNodeId = item.id
      //                 })
      //                 item.children = _.cloneDeep(item.departments)
      //             }
      //         })
      //         // 默认展开第一个目录下的节点且选中第一个子节点
      //         const firstIndex = 0
      //         const children = categories[firstIndex].children
      //         children.forEach(item => {
      //             item.visiable = true
      //         })
      //         categories.splice(firstIndex + 1, 0, ...children)
      //         // this.treeList = _.cloneDeep(categories)
      //         console.warn(categories)
      //     } catch (e) {
      //         console.error(e)
      //         this.bkMessageInstance = this.$bkMessage({
      //             theme: 'error',
      //             message: e.message || e.data.msg || e.statusText
      //         })
      //     } finally {
      //         this.treeLoading = false
      //     }
      // },
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
        if (payload === '') {
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

      async submit () {
        if (!this.groupSelectData.length
          && !Object.keys(this.customSelectData).length
          && !this.managerSelectData.length
        ) {
          this.$bkMessage({
            limit: 1,
            delay: 1500,
            theme: 'error',
            message: this.$t(`m.permTransfer['还未选择权限']`)
          });
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
          console.error(e);
          this.$bkMessage({
            limit: 1,
            theme: 'error',
            delay: 1500,
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.submitLoading = false;
        }

        // const customData = []
        // Object.keys(this.customSelectData).forEach(key => {
        //     this.customSelectData[key].forEach(policyInfo => {
        //         const arr = key.split('|||')
        //         customData.push({
        //             id: arr[0],
        //             name: arr[1],
        //             policy_info: {
        //                 id: policyInfo.id,
        //                 related_resource_types: policyInfo.related_resource_types,
        //                 policy_id: policyInfo.policy_id,
        //                 expired_at: policyInfo.expired_at,
        //                 type: policyInfo.type,
        //                 name: policyInfo.name,
        //                 description: policyInfo.description,
        //                 expired_display: policyInfo.expired_display
        //             }
        //         })
        //     })
        // })

        // const groupData = []
        // this.groupSelectData.forEach(item => {
        //     groupData.push({
        //         id: item.id,
        //         name: item.name,
        //         expired_at: item.expired_at,
        //         expired_at_display: item.expired_at_display,
        //         department_id: item.department_id
        //     })
        // })

        // const superManager = this.managerSelectData.filter(item => item.type === 'super_manager')
        // const systemManager = this.managerSelectData.filter(item => item.type === 'system_manager')
        // const gradeManager = this.managerSelectData.filter(item =>
        //     item.type === 'grade_manager' || item.type === 'rating_manager'
        // )

        // const handoverInfo = {}
        // if (superManager.length) {
        //     handoverInfo.super_manager = superManager
        // }
        // if (systemManager.length) {
        //     handoverInfo.system_manager = systemManager
        // }
        // if (gradeManager.length) {
        //     handoverInfo.grade_manager = gradeManager
        // }
        // if (customData.length) {
        //     handoverInfo.custom = customData
        // }
        // if (groupData.length) {
        //     handoverInfo.group = groupData
        // }

        // const submitData = {
        //     handover_to: this.formData.members[0],
        //     reason: this.formData.reason,
        //     handover_info: handoverInfo
        // }

        // console.error(submitData)

        // try {
        //     this.submitLoading = true
        //     await this.$store.dispatch('perm/permTransfer', submitData)
        //     this.$bkMessage({
        //         theme: 'success',
        //         delay: 500,
        //         message: this.$t(`m.permTransfer['权限交接成功']`),
        //         onClose: () => {
        //             this.$router.push({
        //                 name: 'myPerm'
        //             })
        //         }
        //     })
        // } catch (e) {
        //     console.error(e)
        //     this.$bkMessage({
        //         limit: 1,
        //         theme: 'error',
        //         delay: 1500,
        //         message: e.message || e.data.msg || e.statusText,
        //         ellipsisLine: 2,
        //         ellipsisCopy: true
        //     })
        // } finally {
        //     this.submitLoading = false
        // }
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
<style lang="postcss">
    @import './index.css';
    .input-header {
        position: absolute;
        padding: 0 30px;
        height: 40px;
        line-height: 40px;
        font-size: 14px;
        color: #63656e;
        border-radius: 2px;
        cursor: pointer;
        .title{
           font-weight: 500;
            color: #313238;
        }
    }
    .input-content {
        padding: 5px 30px 5px 180px;
        &-lang {
          padding: 5px 30px 5px 300px;
        }
    }
    .name-empty-error {
        font-size: 12px;
        color: #ff4d4d;
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
</style>
