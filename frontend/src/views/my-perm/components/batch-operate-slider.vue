<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :title="title"
      :width="sliderWidth"
      :quick-close="true"
      :show-mask="true"
      ext-cls="iam-batch-operate-side"
      @update:isShow="handleCancel('dialog')"
    >
      <div slot="content" class="iam-batch-operate-side-content">
        <div
          v-if="noSelectTableList.length"
          class="no-renewal-tip"
        >
          <Icon bk type="info-circle-shape" class="warn" />
          <span class="no-renewal-name">{{ formatTypeTip }}</span>
        </div>
        <div class="batch-operate-content">
          <bk-form form-type="vertical">
            <bk-form-item class="group-table-content" :label-width="0" :required="false">
              <div class="form-item-title">{{ formatFormItemTitle }}</div>
              <RenderPermItem
                :mode="'detail'"
                :expanded="true"
              >
                <div slot="headerTitle" class="single-hide header-content">
                  <span class="header-content-count">
                    {{ $t(`m.common['已选']`) }}
                    <span class="count">{{ formatSelectedGroup }}</span>
                    {{ formatTypeTitle }}
                  </span>
                </div>
                <IamUserGroupTable
                  ref="joinedUserGroupRef"
                  :mode="curSliderName"
                  :list="selectTableList"
                  :no-show-list="noSelectTableList"
                  @on-remove-group="handleRemoveGroup"
                />
              </RenderPermItem>
              <p class="user-group-error" v-if="isShowGroupError">{{ $t(`m.userOrOrg['用户组不能为空']`) }}</p>
            </bk-form-item>
          </bk-form>
        </div>
      </div>
      <div slot="footer">
        <div class="iam-batch-operate-side-footer">
          <bk-button theme="primary" class="member-footer-btn" :loading="submitLoading" @click="handleSubmit">
            {{ $t(`m.common['提交']`) }}
          </bk-button>
          <bk-button theme="default" class="member-footer-btn" @click="handleCancel('cancel')">
            {{ $t(`m.common['取消']`) }}
          </bk-button>
        </div>
      </div>
    </bk-sideslider>
  </div>
</template>
  
<script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { classifyArrayByField } from '@/common/util';
  import { leaveConfirm } from '@/common/leave-confirm';
  import RenderPermItem from '@/components/iam-expand-perm/index.vue';
  import IamUserGroupTable from './user-group-table.vue';
  
  export default {
    components: {
      IamUserGroupTable,
      RenderPermItem
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      isBatch: {
        type: Boolean,
        default: false
      },
      sliderWidth: {
        type: Number
      },
      title: {
        type: String
      },
      curSliderName: {
        type: String
      },
      groupData: {
        type: Object
      },
      userList: {
        type: Array,
        default: () => []
      },
      departList: {
        type: Array,
        default: () => []
      },
      groupList: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        submitLoading: false,
        isShowGroupError: false,
        customButtonStyle: {
          width: '160px'
        },
        groupListBack: [],
        selectTableList: [],
        noSelectTableList: [],
        submitFormData: {},
        submitFormDataBack: {},
        curSliderNameBack: ''
      };
    },
    computed: {
      ...mapGetters(['user']),
      isShowSideSlider: {
        get () {
          return this.show;
        },
        set (newValue) {
          this.$emit('update:show', newValue);
        }
      },
      curRole () {
        return this.user.role.type;
      },
      isHasUser () {
        return this.userList.length > 0;
      },
      isHasDepartment () {
        return this.departList.length > 0;
      },
      formatFormItemTitle () {
        const typeMap = {
          quit: () => {
            return this.$t(`m.perm['退出用户组名']`);
          },
          deleteAction: () => {
            return this.$t(`m.userGroupDetail['删除操作权限']`);
          }
        };
        if (typeMap[this.curSliderName]) {
          return typeMap[this.curSliderName]();
        }
        return '';
      },
      formatSelectedGroup () {
        const modeMap = {
          quit: () => {
            const list = cloneDeep(this.groupListBack);
            this.noSelectTableList = list.filter((item) =>
              item.role_members
              && item.role_members.length === 1
              && item.attributes
              && item.attributes.source_from_role
            );
            this.selectTableList = this.selectTableList.filter(
              (item) => !this.noSelectTableList.map((v) => v.id).includes(item.id));
            return this.selectTableList.length;
          },
          deleteAction: () => {
            const list = this.selectTableList.filter((item) => ['customPerm', 'renewalCustomPerm'].includes(item.mode_type));
            return list.length;
          }
        };
        if (modeMap[this.curSliderName]) {
          return modeMap[this.curSliderName]();
        }
        return '';
      },
      formatTypeTitle () {
        const list = this.noSelectTableList.map((item) => item.name);
        const modeMap = {
          quit: () => {
            return this.$t(`m.common['个用户组']`, { value: list });
          },
          deleteAction: () => {
            return this.$t(`m.common['个操作']`, { value: list });
          }
        };
        return modeMap[this.curSliderName] ? modeMap[this.curSliderName]() : '';
      },
      formatTypeTip () {
        const list = this.noSelectTableList.map((item) => item.name);
        const modeMap = {
          quit: () => {
            return this.$t(`m.info['不可移出的用户组如下']`, { value: list });
          }
        };
        return modeMap[this.curSliderName] ? modeMap[this.curSliderName]() : '';
      }
    },
    watch: {
      show: {
        handler (value) {
          if (value) {
            [this.groupListBack, this.selectTableList] = [this.groupList, this.groupList];
            this.submitFormData = Object.assign({}, {
              selectTableList: this.selectTableList
            });
            this.submitFormDataBack = cloneDeep(this.submitFormData);
          }
        },
        immediate: true
      }
    },
    methods: {
      async handleSubmit () {
        if (!this.selectTableList.length) {
          this.isShowGroupError = true;
          return;
        }
        const modeMap = {
          quit: async () => {
            try {
              this.submitLoading = true;
              const list = this.selectTableList.filter((item) => ['personalPerm'].includes(item.mode_type));
              for (let i = 0; i < list.length; i++) {
                await this.$store.dispatch('perm/quitGroupPerm', {
                  type: 'group',
                  id: list[i].id
                });
              }
              this.messageSuccess(this.$t(`m.info['移出成功']`), 3000);
              bus.$emit('on-update-perm-group', { active: 'personalPerm' });
              this.$emit('update:show', false);
            } catch (e) {
              this.messageAdvancedError(e);
            } finally {
              this.submitLoading = false;
            }
          },
          deleteAction: async () => {
            try {
              this.submitLoading = true;
              const list = this.selectTableList.filter((item) => ['customPerm', 'renewalCustomPerm'].includes(item.mode_type));
              if (list.length) {
                const systemList = classifyArrayByField(list, 'system_id');
                for (const [key, value] of systemList.entries()) {
                  const policyIds = value.map((v) => v.policy_id);
                  await this.$store.dispatch('permApply/deletePerm', {
                    policyIds,
                    systemId: key
                  });
                }
                this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
                const isRenewalPerm = ['renewalPerm'].includes(this.groupData.value);
                bus.$emit('on-update-perm-group', { active: isRenewalPerm ? 'renewalCustomPerm' : 'customPerm', isBatchDelAction: true });
                // 刷新自定义权限表格，更新可续期自定义权限数量
                bus.$emit('on-all-delete-policy', { allDeletePolicy: systemList });
                this.$emit('update:show', false);
              }
            } catch (e) {
              this.messageAdvancedError(e);
            } finally {
              this.submitLoading = false;
            }
          }
        };
        return modeMap[this.curSliderName]();
      },

      handleRemoveGroup (payload) {
        this.selectTableList = [...payload];
        this.submitFormData = Object.assign({}, { selectTableList: this.selectTableList });
      },
  
      handleCancel (payload) {
        if (['cancel'].includes(payload)) {
          this.$emit('update:show', false);
          this.resetData();
        } else {
          let cancelHandler = Promise.resolve();
          window.changeAlert = JSON.stringify(this.submitFormData) !== JSON.stringify(this.submitFormDataBack);
          if (window.changeAlert) {
            cancelHandler = leaveConfirm();
          }
          cancelHandler.then(
            () => {
              this.$emit('update:show', false);
              this.resetData();
            },
            (_) => _
          );
        }
      },
  
      resetData () {
        this.submitFormData = {};
        this.submitFormDataBack = {};
        this.selectTableList = [];
        this.isShowGroupError = false;
      }
    }
  };
</script>
  
<style lang="postcss" scoped>
.iam-batch-operate-side {
  &-content {
    .no-renewal-tip {
      padding: 24px 40px 0 40px;
      .warn {
        color: #ffb848;
      }
      .no-renewal-name {
        font-size: 12px;
        word-break: break-all;
      }
    }
    .batch-operate-content {
      padding: 0 40px 16px 40px;
      /deep/ .group-table-content {
        margin-top: 24px;
        .form-item-title {
          color: #313238;
          font-size: 14px;
          font-weight: 700;
          margin-bottom: 8px;
        }
        .system-render-template-item {
          .expand-header {
            padding-left: 17px;
            .expanded-icon {
              color: #63656E;
            }
            .header-content {
              padding-left: 9px;
              color: #63656E;
              font-weight: 700;
              .count {
                color: #3A84FF;
              }
            }
          }
        }
      }
      .user-group-error,
      .expired-at-error {
        margin-top: 5px;
        font-size: 12px;
        color: #ff4d4d;
      }
    }
  }
  &-footer {
    margin-left: 40px;
    .member-footer-btn {
      min-width: 88px;
      margin-right: 8px;
    }
  }
  /deep/ .bk-sideslider-footer {
    border-top: 0;
    background-color: #ffffff !important;
  }
}
</style>
