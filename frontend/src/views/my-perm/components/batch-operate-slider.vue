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
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { leaveConfirm } from '@/common/leave-confirm';
  import RenderPermBoundary from '@/components/render-perm-boundary';
  import IamUserGroupTable from './user-group-table.vue';
  
  export default {
    components: {
      IamUserGroupTable,
      RenderPermBoundary
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
      formatTableTitle () {
        const typeMap = {
          quit: () => {
            return this.$t(`m.perm['退出用户组名']`);
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
          }
        };
        if (modeMap[this.curSliderName]) {
          return modeMap[this.curSliderName]();
        }
        return '';
      },
      formatTypeTip () {
        return () => {
          const list = this.noSelectTableList.map((item) => item.name);
          const modeMap = {
            quit: () => {
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
      async handleSubmit () {
        if (!this.selectTableList.length) {
          this.isShowGroupError = true;
          return;
        }
        const modeMap = {
          quit: async () => {
            try {
              this.submitLoading = true;
              for (let i = 0; i < this.selectTableList.length; i++) {
                await this.$store.dispatch('perm/quitGroupPerm', {
                  type: 'group',
                  id: this.selectTableList[i].id
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
          deleteAction: () => {

          }
        };
        return modeMap[this.curSliderName]();
      },

      handleRemoveGroup (payload) {
        this.selectTableList = payload;
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
