<template>
  <div class="iam-edit-member" :style="styles">
    <template v-if="!isEditable">
      <div class="edit-wrapper">
        <div class="edit-content">
          <slot>
            <span
              v-for="(item, index) in newVal"
              :key="index"
              class="member-item">
              {{ item }}
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
        @blur="handleBlur"
        @change="handleRtxChange">
      </bk-user-selector>
    </template>
    <bk-dialog
      ext-cls="confirm-space-dialog"
      v-model="isShowDialog"
      :close-icon="showIcon"
      :title="`${$t(`m.common['确定退出管理空间']`)}?`"
      :width="language === 'zh-cn' ? 400 : 600"
      :footer-position="footerPosition"
      @confirm="dropOut">
      <p>{{ $t(`m.common['退出将不在具备相应的管理权限']`) }}</p>
    </bk-dialog>
  </div>
</template>
<script>
  import _ from 'lodash';
  import BkUserSelector from '@blueking/user-selector';
  import { language } from '@/language';
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
        newPayload: '',
        language
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
        this.newVal = [...newVal];
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
          this.messageAdvancedError(e);
        }
      },
      handleEdit () {
        document.body.click();
        this.isEditable = true;
        this.$nextTick(() => {
          this.$refs.input.focus();
        });
      },
      handleBlur () {
        if (!this.isEditable || this.newVal.length < 1) return;
        this.triggerChange();
      },
      handleEnter (value, event) {
        if (!this.isEditable) return;
        if (event.key === 'Enter' && event.keyCode === 13) {
          this.triggerChange();
        }
      },
      dropOut () {
        this.deleteRole(this.newPayload);
      },
      handleDelete (payload) {
        // 超级管理员操作
        if (this.isShowRole) {
          if (this.newVal.length !== 1) {
            this.isShowDialog = true;
          }
          this.newPayload = payload;
        }
        if (!this.isShowRole) {
          if (this.newVal.length !== 1) {
            this.newVal.splice(payload, 1);
            this.triggerChange();
          }
          // this.newPayload = payload;
        }
      },
      async deleteRole (newPayload) {
        // 超级管理员操作
        if (this.isShowRole) {
          if (this.newVal.length === 1) {
            return;
          }
          this.newVal.splice(newPayload, 1);
          this.isLoading = true;
          this.remoteHander({
            [this.field]: this.newVal
          }).then(() => {
            this.$emit('on-change', {
              [this.field]: this.newVal
            });
          }).finally(() => {
            this.isLoading = false;
          });
        } else {
          // 普通用户操作
          if (this.newVal.length === 1) {
            return;
          }
          this.newVal.splice(newPayload, 1);
          this.isLoading = true;
          try {
            await this.$store.dispatch('role/deleteRatingManager', { id: this.$route.params.id });
            await this.$store.dispatch('roleList');
            this.messageSuccess(this.$t(`m.info['退出成功']`), 3000);
          } catch (e) {
            console.error(e);
            this.messageAdvancedError(e);
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
        this.isEditable = false;
      },
      triggerChange () {
        this.isEditable = false;
        if (_.isEqual(this.newVal, this.value)) {
          return;
        }
        this.isLoading = true;
        this.remoteHander({
          [this.field]: this.newVal
        }).then(() => {
          this.$emit('on-change', {
            [this.field]: this.newVal
          });
        }).finally(() => {
          this.isLoading = false;
        });
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
        .edit-wrapper {
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
                line-height: 24px;
                border-radius: 2px;
                background: #f0f1f5;
                font-size: 12px;
                i {
                    font-size: 18px;
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
    .confirm-space-dialog {
        h2,
        p{
            text-align: center;
            color:#333333
        }
    }
    /deep/.bk-dialog-wrapper .bk-dialog-footer {
        background-color:#ffffff;
        border-top:none
    }
    /* /deep/.bk-button.bk-primary {
        background-color: #479ad0;
        border-color:#479ad0;
    } */
</style>
