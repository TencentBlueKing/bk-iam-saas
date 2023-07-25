<template>
  <div class="iam-edit-member" :style="styles">
    <template v-if="!isEditable">
      <div class="edit-wraper">
        <div class="edit-content">
          <slot>
            <span
              v-for="(item, index) in value"
              :key="index"
              class="member-item">
              {{ item.username }}
              <Icon v-if="!isShowRole" type="close-small"
                @click.stop="handleDelete(index)" />
              <Icon v-else type="close-small"
                @click.stop="handleDelete(index)" />
            </span>
            <div class="edit-action-box">
              <span class="edit-action" v-if="!isLoading" @click.stop="handleEdit">
                <Icon bk type="plus" />
              </span>
              <Icon type="loading-circle" class="edit-loading" v-if="isLoading" />
            </div>
          </slot>
        </div>
      </div>
    </template>
    <template v-else>
      <bk-user-selector
        v-model="newVal"
        class="edit-input"
        ref="input"
        :api="userApi"
        :placeholder="$t(`m.verify['请输入']`)"
        :empty-text="$t(`m.common['无匹配人员']`)"
        @keydown="handleEnter(...arguments)"
        @blur="handleBlur"
        @change="handleRtxChange">
      </bk-user-selector>
    </template>
    <bk-dialog
      ext-cls="confirm-space-dialog"
      v-model="isShowDialog"
      :close-icon="showIcon"
      :title="`${$t(`m.common['确定退出管理空间']`)}?`"
      :width="600"
      :footer-position="footerPosition"
      @confirm="dropOut">
      <p class="iam-custom-dialog-title">
        <span>{{ $t(`m.common['退出后']`) }}</span>
        <span>{{ $t(`m.common['，']`) }}</span>
        <span>{{ deleteList.join('、') }}{{ $t(`m.common['将不再具备相应的管理权限']`) }}</span>
      </p>
    </bk-dialog>
  </div>
</template>

<script>
  import _ from 'lodash';
  import BkUserSelector from '@blueking/user-selector';
  export default {
    name: 'iam-edit-member',
    components: {
      BkUserSelector
    },
    props: {
      field: {
        type: String,
        required: true
      },
      value: {
        type: Array,
        default: () => []
      },
      width: {
        type: String,
        default: 'auto'
      },
      remoteHander: {
        type: Function,
        default: () => Promise.resolve()
      },
      rules: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        newVal: this.value,
        isEditable: false,
        isLoading: false,
        userApi: window.BK_USER_API,
        userInfo: '',
        isShowRole: false,
        isShowDialog: false,
        showIcon: false,
        footerPosition: 'center',
        newPayload: -1,
        deleteList: []
      };
    },
    computed: {
      styles () {
        return {
          width: this.width
        };
      }
    },
    watch: {
      value (newVal) {
        this.newVal = [...newVal].map(e => e.username);
      }
    },
    mounted () {
      document.body.addEventListener('click', this.hideEdit);
      this.$once('hook:beforeDestroy', () => {
        document.body.removeEventListener('click', this.hideEdit);
      });
    },
    async created () {
      await this.fetchUser();
      if (this.userInfo.role.type === 'super_manager') {
        this.isShowRole = true;
      }
    },
    methods: {
      /**
       * 获取 user 信息
       */
      async fetchUser () {
        try {
          this.userInfo = await this.$store.dispatch('userInfo');
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },
      // 设置只读
      handleReadOnly () {
        this.$nextTick(() => {
          if (this.isEditable) {
            const selectedTag = this.$refs.input.$refs.selected;
            if (selectedTag && selectedTag.length === 1) {
              selectedTag.forEach(item => {
                item.className = this.newVal.includes(item.innerText)
                  ? 'user-selector-selected user-selector-selected-readonly' : 'user-selector-selected';
              });
            }
          }
        });
      },
      handleEdit () {
        document.body.click();
        this.isEditable = true;
        this.$nextTick(() => {
          this.$refs.input.focus();
          this.handleReadOnly();
        });
      },
      handleBlur () {
        this.isEditable = false;
        if (!this.isEditable && this.newVal.length < 1) {
          this.newVal = [...this.value].map(e => e.username);
          this.messageError(this.$t(`m.verify['管理员不能为空']`), 2000);
          return;
        }
        this.deleteList = [];
        const editValue = this.editNewValue();
        if (JSON.stringify(editValue) !== JSON.stringify(this.value)) {
          if (this.isShowRole) {
            // this.newVal = [...this.value].map(e => e.username);
            this.deleteList = this.value.filter(item =>
              !this.newVal.includes(item.username) && !item.readonly).map(v => v.username);
            this.newPayload = -1;
            console.log(editValue, this.value, this.deleteList);
            if (this.deleteList.length) {
              // this.isShowDialog = true;
              this.dropOut();
            } else {
              this.triggerChange();
            }
          } else {
            this.triggerChange();
          }
        }
      },
      handleEnter (event) {
        if (!this.isEditable) return;
        if (event.key === 'Enter' && event.keyCode === 13) {
          if (this.newVal.length < 1) {
            this.isEditable = false;
            this.newVal = [...this.value].map(e => e.username);
            this.messageError(this.$t(`m.verify['管理员不能为空']`), 2000);
            return;
          }
          this.triggerChange();
        }
      },
      dropOut () {
        this.deleteRole(this.newPayload);
      },
      handleDelete (payload) {
        if (this.newVal.length === 1) {
          this.messageError(this.$t(`m.verify['管理员不能为空']`), 2000);
          return;
        }
        this.newPayload = payload;
        // 超级管理员操作
        if (this.isShowRole) {
          this.deleteList = [this.newVal[payload]];
          // this.isShowDialog = true;
          this.dropOut();
        } else {
          this.newVal.splice(payload, 1);
          this.triggerChange();
        }
      },
      async deleteRole (newPayload) {
        // 超级管理员操作
        const newVal = this.editNewValue();
        if (this.isShowRole) {
          // if (newVal.length === 1) {
          //     return;
          // }
          if (this.newPayload > -1) {
            if (newVal.length === 1) {
              return;
            }
            newVal.splice(newPayload, 1);
          } else {
            if (!newVal.length) {
              return;
            }
          }
          this.isLoading = true;
          this.remoteHander({
            [this.field]: newVal
          }).then(() => {
            this.$emit('on-change', {
              [this.field]: newVal
            });
          }).finally(() => {
            this.isLoading = false;
          });
        } else {
          // 普通用户操作
          if (newVal.length === 1) {
            return;
          }
          newVal.splice(newPayload, 1);
          this.isLoading = true;
          try {
            await this.$store.dispatch('role/deleteRatingManager', { id: this.$route.params.id });
            await this.$store.dispatch('roleList');
            this.messageSuccess(this.$t(`m.info['编辑成功']`), 2000);
          } catch (e) {
            console.error(e);
            this.bkMessageInstance = this.$bkMessage({
              limit: 1,
              theme: 'error',
              message: e.message || e.data.msg || e.statusText
            });
          } finally {
            this.isLoading = false;
          }
        }
      },
      hideEdit (event) {
        if (this.newVal.length < 1) {
          return;
        }
        if (event.path && event.path.length > 0) {
          for (let i = 0; i < event.path.length; i++) {
            const target = event.path[i];
            if (target.className === 'iam-edit-member') {
              return;
            }
          }
        }
        // this.isEditable = false;
      },
      triggerChange () {
        this.isEditable = false;
        const newVal = this.editNewValue();
        if (_.isEqual(newVal, this.value)) {
          return;
        }
        this.isLoading = true;
        this.remoteHander({
          [this.field]: newVal
        }).then(() => {
          this.$emit('on-change', {
            [this.field]: newVal
          });
        }).finally(() => {
          this.isLoading = false;
        });
      },
      editNewValue () {
        return this.newVal.reduce((p, v) => {
          p.push({
            username: v,
            readonly: false
          });
          return p;
        }, []);
      }
    }
  };
</script>
<style lang="postcss">
    @keyframes textarea-edit-loading {
        to {
            transform: rotateZ(360deg)
        }
    }
</style>
<style lang='postcss' scoped>
    .iam-edit-member {
        position: relative;
        .edit-wraper {
            position: relative;
            display: flex;
            align-items: center;
            min-height: 34px;
            line-height: 34px;
            &:hover {
                .edit-action {
                    /* display: block; */
                }
            }
        }
        .edit-content {
            flex: 0 0 auto;
            max-width: calc(100% - 25px);
            .member-item {
                display: inline-block;
                padding: 0 5px;
                margin-right: 2px;
                line-height: 22px;
                border-radius: 2px;
                background: #f0f1f5;
                font-size: 12px;
                i {
                    font-size: 18px;
                    line-height: 22px;
                    color: #979ba5;
                    vertical-align: middle;
                    cursor: pointer;
                    &.disabled {
                        color: #c4c6cc;
                        cursor: not-allowed;
                    }
                }
            }
        }
        .edit-action-box {
            /* display: flex;
            align-items: center; */
            width: 24px;
            height: 24px;
            display: inline-block;
            width: 26px;
            height: 24px;
            margin-right: auto;
            font-size: 16px;
            .edit-action {
                display: inline-block;
                width: 24px;
                height: 24px;
                line-height: 24px;
                background: #f0f1f5;
                border-radius: 2px;
                color: #3a84ff;
                text-align: center;
                cursor: pointer;
                i {
                    font-size: 16px;
                    font-weight: 600;
                }
            }
            .edit-loading {
                position: absolute;
                top: 8px;
                margin-left: 2px;
                animation: 'textarea-edit-loading' 1s linear infinite;
            }
        }
        .edit-input {
            width: 100%;
        }
    }
    /deep/ .confirm-space-dialog {
            .bk-dialog-footer {
               background-color: #ffffff;
               border-top:none;
            }
        }
    /* /deep/.bk-button.bk-primary {
        background-color: #479ad0;
        border-color:#479ad0;
    } */

    /* /deep/ .user-selector-selected-readonly {
        cursor: not-allowed;
        .bk-biz-icon-close {
            display: none;
        }
    } */
</style>
