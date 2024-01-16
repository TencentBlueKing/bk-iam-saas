<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :width="width"
      :title="title"
      ext-cls="iam-member-template-side"
      :quick-close="true"
      @update:isShow="handleCancel('dialog')"
    >
      <div slot="content" class="iam-member-template-side-content">
        <div class="member-template-content">
          <bk-form form-type="vertical">
            <bk-form-item
              :label="$t(`m.userOrOrg['操作对象']`)"
              :label-width="300"
              :required="true"
            >
              <bk-input
                v-model="formData.name"
                :placeholder="$t(`m.memberTemplate['请输入模板名称']`)"
                :ext-cls="isShowNameError ? 'template-name-error' : ''"
                @input="handleNameInput"
                @blur="handleNameBlur"
              />
              <p class="verify-field-error" v-if="isShowNameError">{{ $t(`m.verify['模板名称必填, 不允许输入表情字符']`) }}</p>
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
                :maxlength="255"
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
              <p class="verify-field-error" v-if="isShowSubjectError">{{ $t(`m.verify['模板成员不能为空']`) }}</p>
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
          <bk-button theme="default" class="member-footer-btn" @click="handleCancel('cancel')">
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
      :is-rating-manager="isRatingManager"
      :all-checked="false"
      :show-limit="false"
      :show-expired-at="false"
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd"
    />
  </div>
</template>
  
  <script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { leaveConfirm } from '@/common/leave-confirm';
  import { isEmojiCharacter } from '@/common/util';
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
      },
      title: {
        type: String
      },
      groupData: {
        type: Object
      }
    },
    data () {
      return {
        submitLoading: false,
        isShowAddMemberDialog: false,
        isShowNameError: false,
        isShowSubjectError: false,
        isAll: false,
        width: 960,
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
        addMemberTitle: this.$t(`m.common['添加成员']`)
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
        isRatingManager () {
          return ['rating_manager', 'subset_manager'].includes(this.user.role.type);
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
  
      handleNameInput (payload) {
        this.isShowNameError = !this.formData.name.trim();
        if (isEmojiCharacter(this.formData.name)) {
          this.isShowNameError = true;
        }
        if (payload) {
          window.changeAlert = true;
        }
      },
  
      handleNameBlur (payload) {
        const inputValue = payload.trim();
        if (!inputValue || isEmojiCharacter(inputValue)) {
          this.isShowNameError = true;
        }
      },
  
      handleDescInput (payload) {
        if (payload) {
          window.changeAlert = true;
        }
      },
  
      handleSubmit () {
        const { name, subjects } = this.formData;
        this.isShowNameError = !name.trim();
        if (isEmojiCharacter(name)) {
          this.isShowNameError = true;
          return;
        }
        this.isShowSubjectError = !subjects.length;
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
        this.width = 640;
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
  .iam-member-template-side {
    &-content {
      height: calc(100vh - 140px);
      .member-template-content {
        padding: 0 40px;
        /deep/ .bk-form-item {
          margin-top: 24px;
          .bk-label {
            font-size: 12px;
          }
          .template-name-error {
            .bk-form-input {
              border-color: #ff5656;
            }
          }
          .verify-field-error {
            font-size: 12px;
            color: #ff4d4d;
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
