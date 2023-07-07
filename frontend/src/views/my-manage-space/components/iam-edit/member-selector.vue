<template>
  <div class="iam-edit-selector" :style="styles">
    <template v-if="!isEditable">
      <div class="edit-wrapper">
        <div class="edit-content" :title="displayValue.map(item => item.username) || ''">
          <slot>
            <span
              v-for="(item, i) in displayValue"
              :key="i"
              class="member-item"
              :class="item.readonly ? 'member-readonly' : ''"
            >
              {{ item.username }}
              <!-- <Icon v-if="!isShowRole" type="close-small"
                                @click.stop="handleDelete(index)" />
                            <Icon v-else type="close-small"
                                @click.stop="handleDelete(index)" /> -->
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
        :class="['edit-selector', isErrorClass]"
        ref="selector"
        :api="userApi"
        :placeholder="$t(`m.verify['请输入']`)"
        :empty-text="$t(`m.common['无匹配人员']`)"
        @keydown="handleEnter(...arguments)"
        @blur="handleRtxBlur"
        @change="handleChange">
      </bk-user-selector>
    </template>
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
      allowEmpty: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        displayValue: [],
        isEditable: false,
        isLoading: false,
        userApi: window.BK_USER_API,
        newPayload: '',
        disabledValue: [],
        editValue: []
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
      },
      editValue: {
        handler () {
          this.handleReadOnly();
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
    methods: {
      // 设置只读
      handleReadOnly () {
        this.$nextTick(() => {
          if (this.isEditable && this.$refs.selector) {
            const selectedTag = this.$refs.selector.$refs.selected;
            if (selectedTag && selectedTag.length === 1) {
              selectedTag.forEach(item => {
                item.className = this.displayValue.length === 1
                  && this.displayValue.map(item => item.username).includes(item.innerText)
                  ? 'user-selector-selected user-selector-selected-readonly' : 'user-selector-selected';
              });
            }
          }
        });
      },

      // 设置默认值
      handleDefaultData (payload) {
        this.disabledValue = [...payload].filter(e => e.readonly);
        this.displayValue = [...payload];
        this.editValue = [...payload].filter(e => !e.readonly).map(e => e.username);
      },

      handleEdit () {
        document.body.click();
        this.isEditable = true;
        this.$nextTick(() => {
          this.$refs.selector && this.$refs.selector.focus();
          this.handleDefaultData(this.value);
          this.handleReadOnly();
        });
      },

      handleEnter (event) {
        if (!this.isEditable) return;
        const { key, keyCode } = event;
        const isUpdate = JSON.stringify(this.displayValue) !== JSON.stringify(this.value);
        if (key === 'Enter' && keyCode === 13) {
          this.handleDefaultEmpty();
          isUpdate ? this.handleEmptyChange() : this.isEditable = false;
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
          // this.triggerChange();
        }
      },
            
      triggerChange () {
        if (JSON.stringify(this.displayValue) !== JSON.stringify(this.value)) {
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
        if (JSON.stringify(this.displayValue) !== JSON.stringify(this.value)) {
          this.handleEmptyChange();
        }
      },

      // 判空校验
      handleEmptyChange () {
        if (this.displayValue.length < 1 && !this.allowEmpty) {
          this.displayValue = [...this.value];
          this.messageError(this.$t(`m.verify['管理员不能为空']`), 2000);
          return;
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
         .user-selector-container {
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
