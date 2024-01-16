<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :title="title"
      :width="sliderWidth"
      ext-cls="iam-join-user-group-side"
      :quick-close="true"
      @update:isShow="handleCancel('dialog')"
    >
      <div slot="content" class="iam-join-user-group-side-content">
        <div class="join-user-group-content">
          <bk-form form-type="vertical">
            <bk-form-item
              :class="[
                'operate-object',
                { 'operate-object-single': !isBatch }
              ]"
              :label="!isBatch ? $t(`m.userOrOrg['操作对象']`) : ''"
            >
              <template v-if="isBatch">
                <RenderPermBoundary
                  ref="renderPermBoundaryRef"
                  :modules="['membersPerm']"
                  :user-length="userList.length"
                  :depart-length="departList.length"
                  :custom-title="$t(`m.userOrOrg['操作对象']`)"
                  :custom-slot-name="'operateObject'"
                  :is-custom-title-style="true"
                >
                  <div slot="operateObject">
                    <span>{{ $t(`m.common['已选择']`) }}</span>
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
                  <div
                    slot="membersPerm"
                    class="members-boundary-detail"
                  >
                    <template>
                      <render-member-item
                        v-if="isHasUser"
                        mode="view"
                        type="user"
                        :data="userList"
                      />
                      <render-member-item
                        v-if="isHasDepartment"
                        mode="view"
                        type="department"
                        :data="departList"
                      />
                    </template>
                  </div>
                </RenderPermBoundary>
              </template>
              <template v-else>
                <render-member-item
                  v-if="isHasUser"
                  mode="view"
                  type="user"
                  :data="userList"
                />
                <render-member-item
                  v-if="isHasDepartment"
                  mode="view"
                  type="department"
                  :data="departList"
                />
              </template>
            </bk-form-item>
            <div class="joined-user-group">
              <bk-form-item
                :label="formatGroupTitle"
                :label-width="0"
                :required="true">
                <JoinedUserGroupTable />
              </bk-form-item>
              <div class="joined-user-group-tip">
                <bk-icon type="info-circle-shape" class="joined-user-group-tip-icon" />
                <span>{{ $t(`m.userOrOrg['在已有用户组的基础上，追加以下所选的用户组']`) }}</span>
              </div>
            </div>
            <bk-form-item
              :label="$t(`m.userOrOrg['申请时长']`)"
              :label-width="300"
              :class="[
                'apply-expired-at'
              ]"
              :required="true">
              <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" :cur-role="curRole" />
              <p class="expired-at-error" v-if="isShowExpiredError">{{ $t(`m.userOrOrg['请选择申请时长']`) }}</p>
            </bk-form-item>
          </bk-form>
        </div>
      </div>
      <div slot="footer">
        <div class="iam-join-user-group-side-footer">
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
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { leaveConfirm } from '@/common/leave-confirm';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import RenderPermBoundary from '@/components/render-perm-boundary';
  import RenderMemberItem from '@/views/group/common/render-member-display';
  import JoinedUserGroupTable from '@/views/user-org-perm/components/join-user-group-table.vue';

  export default {
    components: {
      IamDeadline,
      RenderPermBoundary,
      RenderMemberItem,
      JoinedUserGroupTable
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
      }
    },
    data () {
      return {
        submitLoading: false,
        isShowAddMemberDialog: false,
        isShowSubjectError: false,
        isShowExpiredError: false,
        isAll: false,
        expiredAt: 2592000,
        expiredAtUse: 2592000,
        formData: {
          name: '',
          description: '',
          subjects: []
        },
        customButtonStyle: {
          width: '160px'
        },
        users: [],
        departments: [],
        selectTableList: []
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
      formatGroupTitle () {
        return this.isBatch ? `${this.$t(`m.userOrOrg['追加的用户组']`)}` : this.$t(`m.userOrOrg['加入的用户组']`);
      }
    },
    methods: {
      handleMemberDelete (type, payload) {
        window.changeDialog = true;
        if (type === 'user') {
          this.users.splice(payload, 1);
        } else {
          this.departments.splice(payload, 1);
        }
        this.$set(this.formData, 'subjects', [...this.users, ...this.departments]);
      },

      handleDeleteAll () {
        this.isAll = false;
      },

      handleAddMember () {
        this.isShowAddMemberDialog = true;
      },

      handleCancelAdd () {
        this.isShowAddMemberDialog = false;
      },

      handleSubmitAdd (payload) {
        window.changeAlert = true;
        const { users, departments, isAll } = payload;
        this.isAll = isAll;
        this.users = _.cloneDeep(users);
        this.departments = _.cloneDeep(departments);
        this.$set(this.formData, 'subjects', [...this.users, ...this.departments]);
        this.isShowAddMemberDialog = false;
        this.isShowSubjectError = false;
      },

      handleExpiredAt () {
        const nowTimestamp = +new Date() / 1000;
        const tempArr = String(nowTimestamp).split('');
        const dotIndex = tempArr.findIndex((item) => item === '.');
        const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
        const expiredAt = this.expiredAtUse + nowSecond;
        return expiredAt;
      },

      handleDeadlineChange (payload) {
        if (payload) {
          this.isShowExpiredError = false;
        }
        if (payload && payload !== PERMANENT_TIMESTAMP) {
          const nowTimestamp = +new Date() / 1000;
          const tempArr = String(nowTimestamp).split('');
          const dotIndex = tempArr.findIndex((item) => item === '.');
          const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
          this.expiredAtUse = payload + nowSecond;
          return;
        }
        this.expiredAtUse = payload;
      },

      handleSubmit () {
        if (this.expiredAtUse === 15552000) {
          this.expiredAtUse = this.handleExpiredAt();
        }
        const isVerify = this.isShowNameError || this.isShowSubjectError;
        if (isVerify) {
          return;
        }
        this.$emit('on-submit', this.formData);
      },

      handleCancel (payload) {
        if (['cancel'].includes(payload)) {
          this.$emit('update:show', false);
          this.resetData();
        } else {
          let cancelHandler = Promise.resolve();
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
        this.selectTableList = [];
        this.users = [];
        this.departments = [];
        this.formData = Object.assign(
          {},
          {
            name: '',
            description: '',
            subjects: []
          }
        );
        this.isShowNameError = false;
        this.isShowSubjectError = false;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-join-user-group-side {
  &-content {
    height: calc(100vh - 140px);
    .join-user-group-content {
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
      margin-right: 8px;
    }
  }
  /deep/ .operate-object {
    .horizontal-item {
      width: 100%;
      padding: 0;
      box-shadow: none;
      display: inline-block;
    }
    .perm-boundary-title {
      font-weight: 700;
      font-size: 14px;
      color: #313238;
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

  /deep/ .joined-user-group {
    /* display: flex; */
    .bk-label {
      width: 100% !important;
    }
    &-tip {
      margin-top: 24px;
      line-height: 32px;
      font-size: 12px;
      color: #979BA5;
      &-icon {
        font-size: 13px;
        color: #C4C6CC;
      }
    }
  }

  /deep/ .apply-expired-at {
    .custom-time {
      height: 26px;
    }
  }
}
</style>
