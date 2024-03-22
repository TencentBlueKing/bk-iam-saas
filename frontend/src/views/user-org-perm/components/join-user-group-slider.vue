<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :title="title"
      :width="sliderWidth"
      :quick-close="true"
      ext-cls="iam-join-user-group-side"
      @update:isShow="handleCancel('dialog')"

    >
      <div slot="content" class="iam-join-user-group-side-content">
        <div class="join-user-group-content">
          <bk-form form-type="vertical">
            <bk-form-item
              :class="['operate-object', { 'operate-object-single': !isBatch }]"
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
              <div v-else class="single-object">
                <render-member-item v-if="isHasUser" mode="view" type="user" :data="userList" />
                <render-member-item v-if="isHasDepartment" mode="view" type="department" :data="departList" />
              </div>
            </bk-form-item>
            <bk-form-item
              :label-width="0"
              :required="true"
              class="joined-user-group">
              <template>
                <template v-if="isBatch">
                  <div class="render-join">
                    <span class="render-join-label">
                      {{ formatGroupTitle }}
                    </span>
                    <div class="render-join-tip">
                      <Icon bk type="info-circle-shape" class="render-join-tip-icon" />
                      <span>{{ formatGroupTip }}</span>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="render-join-label">{{ formatGroupTitle }}</div>
                </template>
              </template>
              <div ref="selectTableRef">
                <div class="joined-user-group-list">
                  <JoinedUserGroupTable ref="joinedUserGroupRef" @on-selected-group="handleSelectedGroup" />
                </div>
              </div>
              <p class="user-group-error" v-if="isShowGroupError">{{ $t(`m.permApply['请选择用户组']`) }}</p>
            </bk-form-item>
            <bk-form-item
              :label="$t(`m.userOrOrg['申请时长']`)"
              :label-width="300"
              class="apply-expired-at"
              :required="true"
            >
              <iam-deadline ref="expiredRef" :value="expiredAt" @on-change="handleDeadlineChange" :cur-role="curRole" />
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
  import { mapGetters } from 'vuex';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { cloneDeep } from 'lodash';
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
        selectTableList: [],
        submitFormData: {},
        submitFormDataBack: {}
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
      formatGroupTip () {
        const typeMap = {
          add: () => {
            return this.$t(`m.userOrOrg['在已有用户组的基础上，追加以下所选的用户组']`);
          },
          reset: () => {
            return this.$t(`m.userOrOrg['已选对象的权限将被清空，替换为以下所选的用户组']`);
          }
        };
        if (typeMap[this.curSliderName]) {
          return typeMap[this.curSliderName]();
        }
        return '';
      },
      formatGroupTitle () {
        const typeMap = {
          add: () => {
            return this.$t(`m.userOrOrg['追加的用户组']`);
          },
          reset: () => {
            return this.$t(`m.userOrOrg['重置的用户组']`);
          }
        };
        if (typeMap[this.curSliderName]) {
          return typeMap[this.curSliderName]();
        }
        return '';
      }
    },
    watch: {
      isShow: {
        handler (value) {
          if (value) {
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
    methods: {
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
        this.expiredAt = payload;
        if (payload && payload !== PERMANENT_TIMESTAMP) {
          const nowTimestamp = +new Date() / 1000;
          const tempArr = String(nowTimestamp).split('');
          const dotIndex = tempArr.findIndex((item) => item === '.');
          const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
          this.expiredAtUse = payload + nowSecond;
          this.submitFormData = Object.assign(this.submitFormData, { expiredAtUse: payload });
          return;
        }
        this.expiredAtUse = payload;
        this.submitFormData = Object.assign(this.submitFormData, { expiredAtUse: payload });
      },

      handleSelectedGroup (payload) {
        this.isShowGroupError = false;
        this.selectTableList = [...payload];
        this.submitFormData = Object.assign(this.submitFormData, { selectTableList: payload });
      },

      async handleSubmit () {
        const groupsList = this.$refs.joinedUserGroupRef.currentSelectedGroups;
        if (!groupsList.length) {
          this.isShowGroupError = true;
          this.scrollToLocation(this.$refs.selectTableRef);
          return;
        }
        if (!this.expiredAtUse) {
          this.isShowExpiredError = true;
          this.scrollToLocation(this.$refs.expiredRef);
          return;
        }
        this.submitLoading = true;
        if (this.expiredAtUse === 15552000) {
          this.expiredAtUse = this.handleExpiredAt();
        }
        const members = [...this.userList, ...this.departList];
        const params = {
          expired_at: this.expiredAtUse,
          group_ids: groupsList.map((item) => item.id),
          members: members.map(({ id, type }) => ({ id, type }))
        };
        let url = '';
        let msg = '';
        const typeMap = {
          add: () => {
            url = 'userGroup/batchAddUserGroupMember';
            msg = this.$t(`m.info['添加用户组成功']`);
          },
          reset: () => {
            url = 'userOrOrg/resetGroupMembers';
            msg = this.$t(`m.info['重置用户组成功']`);
          }
        };
        typeMap[this.curSliderName]();
        try {
          const { code } = await this.$store.dispatch(url, params);
          if (code === 0) {
            this.messageSuccess(msg, 3000);
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

      handleCancel (payload) {
        if (['cancel'].includes(payload)) {
          this.$emit('update:show', false);
          this.resetData();
        } else {
          window.changeAlert = JSON.stringify(this.submitFormData) !== JSON.stringify(this.submitFormDataBack);
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
        this.submitFormData = {};
        this.submitFormDataBack = {};
        this.selectTableList = [];
        this.isShowGroupError = false;
        this.isShowExpiredError = false;
        this.expiredAt = 15552000;
        this.expiredAtUse = 15552000;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-join-user-group-side {
  &-content {
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
      min-width: 88px;
      margin-right: 8px;
    }
  }
  /deep/ .bk-sideslider-footer {
    background-color: #ffffff !important;
  }
  /deep/ .operate-object {
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
        margin-bottom: 0 !important;
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
        .content {
          .member-item {
            margin-bottom: 0;
          }
        }
      }
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
    &-label {
      position: relative;
      font-weight: 700;
      font-size: 14px;
      line-height: 32px;
      color: #313238;
      margin-bottom: 8px !important;
      &::after {
        content: "*";
        height: 8px;
        line-height: 1;
        font-size: 12px;
        color: #ea3636;
        display: inline-block;
        vertical-align: middle;
        position: absolute;
        top: 50%;
        transform: translate(3px,-50%);
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
    .custom-time {
      height: 26px;
    }
  }
}
</style>
