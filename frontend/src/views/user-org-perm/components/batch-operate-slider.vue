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
          <span class="no-renewal-name">{{ formatTypeTip() }}</span>
        </div>
        <div class="batch-operate-content">
          <bk-form form-type="vertical">
            <bk-form-item
              :class="['operate-object', { 'operate-object-single': !isBatch }]"
              :label="!isBatch ? $t(`m.userOrOrg['操作对象']`) : ''"
            >
              <template v-if="isBatch">
                <RenderPermBoundary
                  :modules="['membersPerm']"
                  :user-length="userList.length"
                  :depart-length="departList.length"
                  :custom-title="$t(`m.userOrOrg['操作对象']`)"
                  :custom-slot-name="'operateObject'"
                  :is-custom-title-style="true"
                >
                  <div slot="operateObject">
                    <span>{{ $t(`m.common['已选']`) }}</span>
                    <template v-if="isHasUser">
                      <span class="number">{{ userList.length }}</span>
                      {{ $t(`m.common['个用户']`) }}
                    </template>
                    <template v-if="isHasUser && isHasDepartment">
                      {{ $t(`m.common['，']`) }}
                    </template>
                    <template v-if="isHasDepartment">
                      <span class="number">{{ departList.length }}</span>
                      {{ $t(`m.common['个组织']`) }}
                    </template>
                  </div>
                  <div slot="membersPerm" class="members-boundary-detail">
                    <template>
                      <render-member-item v-if="isHasUser" mode="view" type="user" :data="userList" />
                      <render-member-item v-if="isHasDepartment" mode="view" type="department" :data="departList" />
                    </template>
                  </div>
                </RenderPermBoundary>
              </template>
              <template v-else>
                <render-member-item v-if="isHasUser" mode="view" type="user" :data="userList" />
                <render-member-item v-if="isHasDepartment" mode="view" type="department" :data="departList" />
              </template>
            </bk-form-item>
            <bk-form-item
              v-if="['renewal'].includes(curSliderName)"
              :label="$t(`m.userOrOrg['续期时长']`)"
              :label-width="300"
              class="apply-expired-at"
              :required="true"
            >
              <IamDeadline :value="expiredAt" @on-change="handleDeadlineChange" :cur-role="curRole" />
              <p class="expired-at-error" v-if="isShowExpiredError">{{ $t(`m.userOrOrg['请选择续期时长']`) }}</p>
            </bk-form-item>
            <bk-form-item class="group-table-content" :label-width="0" :required="false">
              <RenderPermBoundary
                :modules="['transferPreview']"
                :custom-title="formatTableTitle"
                :custom-slot-name="'renewalPreview'"
                :expanded="true"
                :is-custom-title-style="true"
              >
                <div slot="renewalPreview">
                  <span>{{ $t(`m.common['已选']`) }}</span>
                  <template>
                    <span class="number">{{ formatSelectedGroup }}</span>
                    {{ $t(`m.common['个用户组']`) }}
                  </template>
                </div>
                <div slot="transferPreview">
                  <IamUserGroupTable
                    ref="joinedUserGroupRef"
                    :mode="curSliderName"
                    :list="selectTableList"
                    :no-show-list="noSelectTableList"
                    :expired-at-new="expiredAt"
                    @on-remove-group="handleRemoveGroup"
                  />
                </div>
              </RenderPermBoundary>
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
  import { mapGetters } from 'vuex';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { cloneDeep } from 'lodash';
  import { leaveConfirm } from '@/common/leave-confirm';
  import { getNowTimeExpired } from '@/common/util';
  import { bus } from '@/common/bus';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import RenderPermBoundary from '@/components/render-perm-boundary';
  import RenderMemberItem from '@/views/group/common/render-member-display';
  import IamUserGroupTable from './user-group-table.vue';

  export default {
    components: {
      IamDeadline,
      IamUserGroupTable,
      RenderPermBoundary,
      RenderMemberItem
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
        isShowExpiredError: false,
        expiredAt: 15552000,
        expiredAtUse: 15552000,
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
      formatTableTitle () {
        const typeMap = {
          remove: () => {
            return this.$t(`m.userOrOrg['移出用户组名']`);
          },
          renewal: () => {
            return this.$t(`m.userOrOrg['续期预览']`);
          }
        };
        if (typeMap[this.curSliderName]) {
          return typeMap[this.curSliderName]();
        }
        return typeMap[this.curSliderName] ? typeMap[this.curSliderName]() : '';
      },
      formatSelectedGroup () {
        const modeMap = {
          remove: () => {
            const list = cloneDeep(this.groupListBack);
            this.noSelectTableList = list.filter((item) =>
              item.role_members.length === 1
              && item.attributes
              && item.attributes.source_from_role
            );
            this.selectTableList = this.selectTableList.filter(
              (item) => !this.noSelectTableList.map((v) => v.id).includes(item.id));
            return this.selectTableList.length;
          },
          renewal: () => {
            const list = cloneDeep(this.groupListBack);
            this.noSelectTableList = list.filter((item) => item.expired_at === PERMANENT_TIMESTAMP);
            this.selectTableList = this.selectTableList.filter(
              (item) => !this.noSelectTableList.map((v) => v.id).includes(item.id));
            return this.selectTableList.length;
          }
        };
        return modeMap[this.curSliderName] ? modeMap[this.curSliderName]() : '';
      },
      formatTypeTip () {
        return () => {
          const list = this.noSelectTableList.map((item) => item.name);
          const modeMap = {
            remove: () => {
              return this.$t(`m.info['不可移出的用户组如下']`, { value: list });
            },
            renewal: () => {
              return this.$t(`m.info['不可续期的用户组如下']`, { value: list });
            }
          };
          return modeMap[this.curSliderName] ? modeMap[this.curSliderName]() : '';
        };
      }
    },
    watch: {
      show: {
        handler (value) {
          if (value) {
            [this.groupListBack, this.selectTableList] = [this.groupList, this.groupList];
            this.submitFormData = Object.assign({}, {
              expiredAtUse: this.expiredAtUse,
              selectTableList: this.selectTableList
            });
            this.submitFormDataBack = cloneDeep(this.submitFormData);
          }
        },
        immediate: true
      }
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-remove-toggle-checkbox');
      });
      // 同步更新checkbox状态
      bus.$on('on-remove-toggle-checkbox', (payload) => {
        this.selectTableList = [...payload];
        this.submitFormData = Object.assign({}, { selectTableList: this.selectTableList });
      });
    },
    methods: {
      handleRemoveGroup (payload) {
        this.selectTableList = payload;
      },
      async handleExpiredAt () {
        const nowTimestamp = await getNowTimeExpired();
        const expiredAt = this.expiredAtUse + nowTimestamp;
        return expiredAt;
      },

      async handleDeadlineChange (payload) {
        if (payload) {
          this.isShowExpiredError = false;
        }
        this.expiredAt = payload;
        if (payload && payload !== PERMANENT_TIMESTAMP) {
          const nowTimestamp = await getNowTimeExpired();
          this.expiredAtUse = payload + nowTimestamp;
          this.submitFormData = Object.assign(this.submitFormData, { expiredAtUse: payload });
          return;
        }
        this.expiredAtUse = payload;
        this.submitFormData = Object.assign(this.submitFormData, { expiredAtUse: payload });
      },

      async handleSubmit () {
        if (!this.selectTableList.length) {
          this.isShowGroupError = true;
          return;
        }
        const { type, id } = this.groupData;
        let params = {
          group_ids: this.selectTableList.map((item) => item.id),
          members: [...this.userList, ...this.departList].map(({ id, type }) => ({ id, type }))
        };
        const modeMap = {
          remove: async () => {
            try {
              this.submitLoading = true;
              const deleteParams = {
                members: [{
                  type,
                  id
                }],
                group_ids: this.selectTableList.map((item) => item.id)
              };
              const { code } = await this.$store.dispatch('userOrOrg/deleteGroupMembers', deleteParams);
              if (code === 0) {
                this.messageSuccess(this.$t(`m.info['移出成功']`), 3000);
                bus.$emit('on-remove-toggle-checkbox', this.selectTableList);
                this.$emit('on-submit', params);
                this.$emit('update:show', false);
              }
            } catch (e) {
              console.error(e);
              this.messageAdvancedError(e);
            } finally {
              this.submitLoading = false;
            }
          },
          renewal: async () => {
            try {
              if (this.expiredAtUse === 15552000) {
                this.expiredAtUse = await this.handleExpiredAt();
              }
              if (!this.expiredAtUse) {
                this.isShowExpiredError = true;
                return;
              }
              this.submitLoading = true;
              const batchMembers = cloneDeep([...this.userList, ...this.departList]);
              const result = batchMembers.map((item) => {
                return this.selectTableList.map((subItem) => {
                  return {
                    id: item.id,
                    type: item.type,
                    group_id: subItem.id,
                    expired_at: getNowTimeExpired() > subItem.expired_at
                      ? this.expiredAtUse : this.expiredAtUse + (subItem.expired_at - getNowTimeExpired())
                  };
                });
              });
              const groupMembers = result.flat(Infinity);
              params = {
                group_members: groupMembers
              };
              const { code } = await this.$store.dispatch('userOrOrg/batchJoinOrRenewal', params);
              if (code === 0) {
                this.messageSuccess(this.$t(`m.renewal['续期成功']`), 3000);
                this.$emit('on-submit', params);
                this.$emit('update:show', false);
              }
            } catch (e) {
              console.error(e);
              this.messageAdvancedError(e);
            } finally {
              this.submitLoading = false;
            }
          }
        };
        return modeMap[this.curSliderName]();
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
        this.expiredAt = 15552000;
        this.expiredAtUse = 15552000;
        this.isShowGroupError = false;
        this.isShowExpiredError = false;
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
      /deep/ .bk-form-item {
        margin-top: 24px;
        .bk-label {
          font-weight: 700;
          font-size: 14px;
          color: #313238;
        }
        .verify-field-error {
          font-size: 12px;
          color: #ff4d4d;
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

  /deep/ .operate-object,
  /deep/ .group-table-content {
    .horizontal-item {
      width: 100%;
      padding: 0;
      margin-bottom: 0;
      box-shadow: none;
      display: inline-block;
      .perm-boundary-title {
        font-weight: 700;
        font-size: 14px;
        color: #313238;
        margin-bottom: 8px !important;
      }
      .render-form-item {
        margin-bottom: 0 !important;
      }
    }

    .members-boundary-detail {
      padding: 16px;
    }

    .iam-member-display-wrapper {
      margin-left: 0;
      .label {
        margin-bottom: 0 !important;
      }
    }

    &-single {
      .iam-member-display-wrapper {
        .label {
          display: none;
        }
      }
    }
  }

  /deep/ .group-table-content {
    margin-top: 18px !important;
    .iam-resource-expand {
      background-color: #eaebf0;
    }
  }

  /deep/ .joined-user-group {
    .bk-label {
      width: 100% !important;
    }
    &-list {
      border: 1px solid #dcdee5;
      border-radius: 2px;
    }
  }

  /deep/ .render-join {
    display: flex;
    margin-bottom: 8px;
    &-label {
      position: relative;
      font-weight: 700;
      font-size: 14px;
      line-height: 32px;
      color: #313238;
      margin-bottom: 8px !important;
      &::after {
        content: '*';
        height: 8px;
        line-height: 1;
        font-size: 12px;
        color: #ea3636;
        display: inline-block;
        vertical-align: middle;
        position: absolute;
        top: 50%;
        transform: translate(3px, -50%);
      }
    }
    &-tip {
      margin-left: 20px;
      line-height: 32px;
      font-size: 12px;
      color: #979ba5;
      &-icon {
        font-size: 13px;
        color: #c4c6cc;
      }
    }
  }

  /deep/ .apply-expired-at {
    margin-top: 18px !important;
    .custom-time {
      height: 26px;
    }
  }
}
</style>
