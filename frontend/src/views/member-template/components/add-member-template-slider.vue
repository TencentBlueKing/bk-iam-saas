<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :width="width"
      :title="$t(`m.memberTemplate['新建人员模板']`)"
      ext-cls="iam-member-template-side"
      :quick-close="true"
      @update:isShow="handleCancel"
    >
      <div slot="content" class="iam-member-template-side-content">
        <div class="member-template-content">
          <bk-form form-type="vertical">
            <bk-form-item
              :label="$t(`m.memberTemplate['模板名称']`)"
              :label-width="300"
              :required="true"
            >
              <bk-input
                v-model="formData.template_name"
                :placeholder="$t(`m.memberTemplate['请输入模板名称']`)"
                @input="handleNameInput"
              />
            </bk-form-item>
            <bk-form-item
              :label="$t(`m.common['描述']`)"
              :label-width="300"
              :required="false"
            >
              <bk-input
                type="textarea"
                v-model="formData.description"
                :placeholder="$t(`m.memberTemplate['请输入描述']`)"
                :rows="3"
                :maxlength="100"
                @input="handleDescInput"
              />
            </bk-form-item>
            <bk-form-item>
              <div ref="memberRef" class="members-template-content">
                <render-member
                  :is-all="false"
                  :render-title="$t(`m.memberTemplate['模板成员']`)"
                  :custom-content-class="'members-template-content'"
                  :users="users"
                  :departments="departments"
                  @on-add="handleAddMember"
                  @on-delete="handleMemberDelete"
                  @on-delete-all="handleDeleteAll"
                />
              </div>
            </bk-form-item>
          </bk-form>
        </div>
      </div>
      <div slot="footer">
        <div class="iam-member-template-side-footer">
          <bk-button
            theme="primary"
            class="member-footer-btn"
            :loading="submitLoading"
            @click="handleSubmit"
          >
            {{ $t(`m.common['提交']`) }}
          </bk-button>
          <bk-button theme="default" class="member-footer-btn" @click="handleCancel">
            {{ $t(`m.common['取消']`) }}
          </bk-button>
        </div>
      </div>
    </bk-sideslider>
    <add-member-dialog
      :show.sync="isShowAddMemberDialog"
      :users="users"
      :departments="departments"
      :title="addMemberTitle"
      :all-checked="false"
      show-limit
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd"
    />
  </div>
</template>

<script>
  import _ from 'lodash';
  import { leaveConfirm } from '@/common/leave-confirm';
  import RenderMember from '@/views/grading-admin/components/render-member';
  import AddMemberDialog from '@/views/group/components/iam-add-member.vue';
  export default {
    components: {
      RenderMember,
      AddMemberDialog
    },
    props: {
      show: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        submitLoading: false,
        isShowAddMemberDialog: false,
        width: 640,
        formData: {
          template_name: '',
          description: '',
          template_members: []
        },
        customButtonStyle: {
          width: '160px'
        },
        users: [],
        departments: [],
        addMemberTitle: this.$t(`m.common['添加成员']`)
      };
    },
    computed: {
      isShowSideSlider: {
        get () {
          return this.show;
        },
        set (newValue) {
          console.log(newValue, 55);
          this.$emit('update:show', newValue);
        }
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
        this.$set(this.formData, 'template_members', [...this.users, ...this.departments]);
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
        this.$set(this.formData, 'template_members', [...this.users, ...this.departments]);
        this.isShowAddMemberDialog = false;
      },

      handleNameInput (payload) {
        if (payload) {
          window.changeAlert = true;
        }
      },

      handleDescInput (payload) {
        if (payload) {
          window.changeAlert = true;
        }
      },

      handleSubmit () {
        const { template_name, template_members } = this.formData;
        // eslint-disable-next-line camelcase
        if (!template_name) {
          return this.messageWarn(this.$t(`m.verify['模板名称不能为空']`), 3000);
        }
        if (!template_members.length) {
          return this.messageWarn(this.$t(`m.verify['模板成员不能为空']`), 3000);
        }
        try {
          this.$emit('on-submit', this.formData);
          this.$emit('update:show', false);
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      handleCancel () {
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
      },

      resetData () {
        this.width = 640;
        this.selectTableList = [];
        this.formData = Object.assign(
          {},
          {
            template_name: '',
            description: '',
            template_members: []
          }
        );
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-member-template-side {
  .member-template-content {
    padding: 0 40px;
  }
  &-content {
    height: calc(100vh - 114px);
    .member-template-content {
      padding-top: 4px;
      .bk-form-item {
        margin-top: 24px;
        .bk-label {
          font-size: 12px;
        }
      }
    }
  }
  &-footer {
    margin-left: 40px;
    .member-footer-btn {
      margin-right: 8px;
    }
  }
  /deep/ .members-template-content {
    .members-boundary-header {
      margin: 0;
      .perm-members-add {
        width: 160px;
      }
    }
    .iam-member-display-wrapper {
      margin-left: 0;
      .label {
        margin-bottom: 0;
      }
    }
  }
}
</style>
