<template>
  <div class="iam-edit-selector" :style="styles">
    <template v-if="!isEditable">
      <div class="edit-wrapper">
        <div class="edit-content">
          <slot>
            <span
              v-for="(item, index) in displayValue"
              :key="index"
              class="member-item"
              :class="item.readonly ? 'member-readonly' : ''">
              {{ item.username }}
              <Icon v-if="!item.readonly && isEditMode" type="close-small"
                @click.stop="handleDelete(index)" />
            </span>
          </slot>
        </div>
        <div class="edit-action-box" v-if="isEditMode">
          <Icon
            type="edit-fill"
            class="edit-action"
            v-if="!isLoading"
            @click.self.stop="handleEdit" />
          <Icon
            type="loading-circle"
            class="edit-loading"
            v-if="isLoading" />
        </div>
      </div>
    </template>
    <template v-else>
      <bk-user-selector
        v-model="editValue"
        :ext-cls="[
          'user-selector'
        ]"
        ref="input"
        :api="userApi"
        :placeholder="$t(`m.verify['请输入']`)"
        :empty-text="$t(`m.common['无匹配人员']`)"
        @blur="handleRtxBlur"
        @change="handleChange">
      </bk-user-selector>
    </template>
    <bk-dialog
      ext-cls="confirm-space-dialog"
      v-model="isShowDialog"
      :close-icon="false"
      :title="`${$t(`m.common['确定退出管理空间']`)}?`"
      :width="600"
      :footer-position="footerPosition"
      @cancel="handleCancel"
      @confirm="handleDeleteRole">
      <p class="iam-custom-dialog-title">
        <span>{{ $t(`m.common['退出后']`) }}</span>
        <span>{{ $t(`m.common['，']`) }}</span>
        <span>{{ deleteList.join('、') }}{{ $t(`m.common['将不再具备相应的管理权限']`) }}</span>
      </p>
    </bk-dialog>
  </div>
</template>
<script>
  import BkUserSelector from '@blueking/user-selector';

  export default {
    name: 'iam-edit-selector',
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
      remoteHandler: {
        type: Function,
        default: () => Promise.resolve()
      },
      rules: {
        type: Array,
        default: () => []
      },
      mode: {
        type: String,
        default: 'edit',
        validator: function (value) {
          return ['detail', 'edit'].includes(value);
        }
      }
    },
    data () {
      return {
        displayValue: this.value,
        isEditable: false,
        isLoading: false,
        isShowDialog: false,
        userApi: window.BK_USER_API,
        newPayload: '',
        disabledValue: [],
        editValue: [],
        footerPosition: 'center',
        roleIndex: -1,
        deleteList: []
      };
    },
    computed: {
      styles () {
        return {
          width: this.width
        };
      },
      isEditMode () {
        return this.mode === 'edit';
      }
    },
    watch: {
      value: {
        handler (newVal) {
          this.handleDefaultData(newVal);
        },
        immediate: true
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
    },
    methods: {
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

      // 设置默认值
      handleDefaultData (payload) {
        this.disabledValue = [...payload].filter(e => e.readonly);
        this.displayValue = [...payload];
        this.editValue = [...payload].filter(e => !e.readonly).map(e => e.username);
        // this.editValue = [...payload].map(e => e.username);
      },

      handleEdit () {
        document.body.click();
        this.isEditable = true;
        this.$nextTick(() => {
          if (this.isEditable) {
            this.$refs.input && this.$refs.input.focus();
            const disabledValue = [...this.disabledValue].map(item => item.username);
            const selectedTag = this.$refs.input.$refs.selected;
            if (selectedTag && selectedTag.length) {
              if (disabledValue.length) {
                selectedTag.forEach(item => {
                  if (disabledValue.includes(item.innerText)) {
                    item.className = 'user-selector-selected user-selector-selected-readonly';
                  }
                });
              }
            }
          }
        });
      },

      handleDelete (index) {
        if (this.displayValue.length === 1) {
          this.messageError(this.$t(`m.verify['管理员不能为空']`), 2000);
          return;
        }
        this.roleIndex = index;
        // this.isShowDialog = true;
        this.deleteList = [this.displayValue[index].username];
        this.handleDeleteRole();
      },

      async handleDeleteRole () {
        if (this.roleIndex > -1) {
          this.displayValue.splice(this.roleIndex, 1);
        }
        this.$emit('on-change', {
          [this.field]: this.displayValue
        });
      },

      handleEnter (value, event) {
        if (!this.isEditable) return;
        if (event.key === 'Enter' && event.keyCode === 13) {
          this.triggerChange();
        }
      },

      hideEdit (event) {
        // this.isEditable = false;
        if (this.displayValue.length < 1) {
          return;
        }
        if (event.path && event.path.length > 0) {
          for (let i = 0; i < event.path.length; i++) {
            const target = event.path[i];
            if (target.className && target.className === 'iam-edit-selector') {
              return;
            }
          }
        }
      },

      triggerChange () {
        this.isEditable = false;
        console.log(this.displayValue);
        if (JSON.stringify(this.displayValue) !== JSON.stringify(this.value)) {
          this.isLoading = true;
          this.remoteHandler({
            [this.field]: this.displayValue
          }).then(() => {
            this.$emit('on-change', {
              [this.field]: this.displayValue
            });
          }).finally(() => {
            this.isLoading = false;
          });
        }
      },

      handleChange () {
        const editValue = this.editValue.reduce((p, v) => {
          p.push({
            username: v,
            readonly: !!(this.disabledValue.length && this.disabledValue.map(e => e.username).includes(v))
          });
          return p;
        }, []);
        this.displayValue = [...this.disabledValue, ...editValue];
      },

      handleRtxBlur () {
        this.isEditable = false;
        this.deleteList = [];
        if (JSON.stringify(this.displayValue) !== JSON.stringify(this.value)) {
          if (this.displayValue.length < 1) {
            this.handleDefaultData(this.value);
            this.messageError(this.$t(`m.verify['管理员不能为空']`), 2000);
            return;
          }
          this.deleteList = this.value.filter(item =>
            !this.editValue.includes(item.username) && !item.readonly).map(v => v.username);
          this.roleIndex = -1;
          if (this.deleteList.length) {
            this.handleDeleteRole();
            // this.isShowDialog = true;
          } else {
            this.$emit('on-change', {
              [this.field]: this.displayValue
            });
          }
        }
      },

      handleCancel () {
        this.handleDefaultData(this.value);
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
   .iam-edit-selector {
        position: relative;
        .edit-wrapper {
            position: relative;
            display: flex;
            align-items: center;
            &:hover {
                .edit-action {
                    display: block;
                }
            }
        }

        .edit-content {
            flex: 0 0 auto;
            max-width: calc(100vh - 25px);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            .member-item {
                display: inline-block;
                padding: 0 10px;
                margin: 2px 0 2px 6px;
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
            .member-readonly{
                background: #FFF1DB;
                color: #FE9C00;
            }
        }
        .edit-action-box {
            display: flex;
            align-items: center;
            margin-right: auto;
            font-size: 16px;
            .edit-action {
                padding: 6px 15px 6px 2px;
                cursor: pointer;
                display: none;
                &:hover {
                    color: #3a84ff;
                }
            }
            .edit-loading {
                position: absolute;
                top: 8px;
                margin-left: 2px;
                animation: 'textarea-edit-loading' 1s linear infinite;
            }
        }
        .user-selector {
            width: 100%;
        }
        /deep/ .user-selector-selected-readonly {
            background: #FFF1DB;
            .user-selector-selected-value {
                color: #FE9C00;
            }
            .user-selector-selected-clear {
                display: none;
            }
        }
    }
    
    /deep/ .confirm-space-dialog {
            .bk-dialog-footer {
               background-color: #ffffff;
               border-top:none;
            }
        }
</style>
