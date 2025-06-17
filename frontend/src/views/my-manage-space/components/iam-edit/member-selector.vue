<template>
  <div
    ref="iamEditSelector"
    class="iam-edit-selector"
    :style="styles"
  >
    <template v-if="!isEditable">
      <div class="edit-wrapper">
        <template v-if="displayValue.length">
          <div class="edit-content">
            <slot>
              <IamUserDisplayName :display-value="displayValue">
                <div slot="customDisplayName" class="single-hide edit-content-tenant">
                  <span
                    v-for="(item, i) in displayValue"
                    :key="i"
                    :class="['member-item', { 'member-readonly': item.readonly }]"
                  >
                    <bk-user-display-name :user-id="item.username" />
                  </span>
                </div>
              </IamUserDisplayName>
            </slot>
          </div>
        </template>
        <template v-else>
          <span>--</span>
        </template>
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
      <BkUserSelector
        v-model="editValue"
        ref="selector"
        :api-base-url="apiBaseUrl"
        :tenant-id="tenantId"
        :multiple="multiple"
        :required="!isEditAllowEmpty"
        @change="handleChange"
      />
    </template>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  export default {
    name: 'iam-edit-selector',
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
      isErrorClass: {
        type: String,
        default: ''
      },
      index: {
        type: Number,
        default: 0
      },
      mode: {
        type: String,
        default: 'edit',
        validator: function (value) {
          return ['detail', 'edit'].includes(value);
        }
      },
      // 默认允许空
      allowEmpty: {
        type: Boolean,
        default: false
      },
      // 编辑不允许空
      isEditAllowEmpty: {
        type: Boolean,
        default: true
      },
      // 是否多选
      multiple: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        isEditable: false,
        isLoading: false,
        apiBaseUrl: window.BK_USER_WEB_APIGW_URL,
        displayValue: [],
        disabledValue: [],
        editValue: []
      };
    },
    computed: {
      ...mapGetters(['user']),
      styles () {
        return {
          width: this.width
        };
      },
      tenantId () {
        return this.user.tenant_id;
      },
      isEditMode () {
        return this.mode === 'edit';
      },
      isAllowTrigger () {
        return JSON.stringify(this.displayValue) !== JSON.stringify(this.value);
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
      document.body.addEventListener('keydown', this.handleEnter);
      this.$once('hook:beforeDestroy', () => {
        document.body.removeEventListener('click', this.hideEdit);
        document.body.removeEventListener('keydown', this.handleEnter);
      });
    },
    methods: {
      // 设置默认值
      handleDefaultData (payload) {
        this.displayValue = [...payload];
        this.disabledValue = [...payload].filter(e => e.readonly);
        this.editValue = [...payload].filter(e => !e.readonly).map(e => e.username);
      },

      handleEdit () {
        document.body.click();
        this.isEditable = true;
        this.$nextTick(() => {
          this.$refs.selector && this.$refs.selector.$el.querySelector('input').focus();
          this.handleDefaultData(this.value);
        });
      },

      handleEnter (event) {
        if (!this.isEditable) return;
        const { key, keyCode } = event;
        if (key === 'Enter' && keyCode === 13) {
          this.handleDefaultEmpty();
          if (this.isAllowTrigger) {
            this.handleEmptyChange();
            this.isEditable = false;
          } else {
            this.isEditable = false;
          }
        }
      },

      hideEdit (event) {
        if (this.$refs.iamEditSelector.contains(event.target)) {
          return;
        }
        this.handleRtxBlur();
      },
            
      triggerChange () {
        // 单独处理初始化为空但编辑不能为空数据
        if (!this.displayValue.length && !this.isEditAllowEmpty) {
          this.displayValue = [...this.value];
          this.messageWarn(this.$t(`m.verify['管理员不能为空']`), 3000);
          return;
        }
        if (this.isAllowTrigger) {
          this.isLoading = true;
          this.remoteHandler({
            [this.field]: this.displayValue
          }).then(() => {
            this.$emit('on-change', {
              [this.field]: this.displayValue
            }, this.index);
          }).finally(() => {
            this.isLoading = false;
          });
        }
      },

      handleChange () {
        if (this.displayValue.length < 1 && !this.allowEmpty) {
          return;
        }
        const editValue = this.editValue.reduce((p, v) => {
          p.push({
            username: v,
            readonly: false
          });
          return p;
        }, []);
        this.displayValue = [...this.disabledValue, ...editValue];
      },

      handleRtxBlur () {
        this.isEditable = false;
        this.handleDefaultEmpty();
        if (this.isAllowTrigger) {
          this.handleEmptyChange();
        }
      },

      // 判空校验
      handleEmptyChange () {
        if (this.displayValue.length < 1 && !this.allowEmpty) {
          let editValue = [];
          if (this.editValue.length) {
            if (!this.editValue.some((v) => v.username)) {
              editValue = this.editValue.reduce((p, v) => {
                p.push({
                  username: v,
                  readonly: false
                });
                return p;
              }, []);
              this.displayValue = [...this.disabledValue, ...editValue];
            } else {
              this.displayValue = [...this.disabledValue, ...this.editValue];
            }
          } else {
            this.displayValue = [...this.value];
            this.messageWarn(this.$t(`m.verify['管理员不能为空']`), 3000);
            return;
          }
        }
        this.triggerChange();
      },

      // 处理默认是空的管理员列表的数据
      handleDefaultEmpty () {
        if (!this.displayValue.length && this.allowEmpty) {
          this.$emit('on-empty-change', this.index);
        }
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
            max-width: calc(100% - 25px);
            .member-item {
                display: inline-block;
                padding: 0 10px;
                margin: 2px 0 2px 6px;
                line-height: 22px;
                border-radius: 2px;
                background: #f0f1f5;
                font-size: 12px;
                &:first-child {
                    margin-left: 0;
                }
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
            .member-readonly{
                background: #FFF1DB;
                color: #FE9C00;
            }
            &-tenant {
              max-width: 100%;
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
        .edit-selector {
            width: 100%;
        }

        /deep/  .is-member-empty-cls {
         .tags-container {
            border-color: #ff4d4d;
        }
    }
    }

    /* /deep/ .user-selector-selected-readonly {
        cursor: not-allowed;
        .bk-biz-icon-close {
            display: none;
        }
    } */
</style>
