<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :title="title"
      :width="sliderWidth"
      :quick-close="true"
      :show-mask="true"
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
            <bk-form-item :label-width="0" :required="true">
              <div v-html="formatGroupTitle" />
              <div class="joined-user-group" ref="selectTableRef">
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
        const modeMap = {
          add: () => {
            return this.isBatch
              ? `<div class="render-join">
                    <span class="render-join-label">${this.$t(`m.userOrOrg['追加的用户组']`)}</span>
                    <div class="render-join-tip">
                      <Icon bk type="info-circle-shape" class="render-join-tip-icon"></Icon>
                      <span>${this.$t(`m.userOrOrg['在已有用户组的基础上，追加以下所选的用户组']`)}</span>
                    </div>    
                  </div>`
              : `<div class="render-join-label">${this.$t(`m.userOrOrg['加入的用户组']`)}</div>`;
          },
          reset: () => {
            return this.isBatch
              ? `<div class="render-join">
                    <span class="render-join-label">${this.$t(`m.userOrOrg['重置的用户组']`)}</span>
                    <div class="render-join-tip">
                      <bk-icon type="info-circle-shape" class="render-join-tip-icon"></bk-icon>
                      <span>${this.$t(`m.userOrOrg['已选对象的权限将被清空，替换为以下所选的用户组']`)}</span>
                    </div>    
                  </div>`
              : `<div class="render-join-label">${this.$t(`m.userOrOrg['重置的用户组']`)}</div>`;
          }
        };
        if (modeMap[this.curSliderName]) {
          return modeMap[this.curSliderName]();
        }
        return '';
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

      handleSelectedGroup (payload) {
        this.selectTableList = [...payload];
      },

      async handleSubmit () {
        const groupsList = this.$refs.joinedUserGroupRef.currentSelectedGroups;
        if (!groupsList.length) {
          this.isShowGroupError = true;
          this.scrollToLocation(this.$refs.selectTableRef);
          return;
        }
        this.submitLoading = true;
        if (this.expiredAtUse === 15552000) {
          this.expiredAtUse = this.handleExpiredAt();
        }
        const params = {
          expired_at: this.expiredAtUse,
          group_ids: groupsList.map((item) => item.id),
          members: [...this.userList, ...this.departList]
        };
        try {
          const { code } = await this.$store.dispatch('userGroup/batchAddUserGroupMember', params);
          if (code === 0) {
            this.messageSuccess(this.$t(`m.info['添加用户组成功']`), 3000);
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
        this.isShowGroupError = false;
        this.isShowExpiredError = false;
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
