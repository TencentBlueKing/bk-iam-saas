<template>
  <div class="iam-edit-input" :style="styles">
    <template v-if="!isEditable">
      <div class="edit-wraper">
        <div class="edit-content" :title="newVal">
          <slot v-bind:value="newVal">{{ newVal }}</slot>
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
      <bk-input
        ref="input"
        v-model="newVal"
        :placeholder="placeholder"
        @input="handleInput"
        @blur="handleBlur"
        @keyup="handleEnter" />
      <p class="validate-error-tips" v-if="isShowError">{{ errorTips }}</p>
    </template>
  </div>
</template>
<script>
  import il8n from '@/language';
    
  export default {
    name: 'iam-edit-input',
    props: {
      field: {
        type: String,
        required: true
      },
      value: {
        type: [Number, String],
        default: ''
      },
      width: {
        type: String,
        default: 'auto'
      },
      placeholder: {
        type: String,
        default: il8n('verify', '请输入')
      },
      remoteHander: {
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
      },
      isShowOther: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        newVal: this.value,
        isEditable: false,
        isLoading: false,
        isShowError: false,
        errorTips: ''
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
      value (newVal) {
        this.newVal = newVal;
      }
    },
    mounted () {
      document.body.addEventListener('click', this.hideEdit);
      this.$once('hook:beforeDestroy', () => {
        document.body.removeEventListener('click', this.hideEdit);
      });
    },
    methods: {
      handleValidate () {
        this.isShowError = false;
        this.errorTips = '';
        if (this.rules.length > 0) {
          for (let i = 0; i < this.rules.length; i++) {
            const validate = this.rules[i];
            if (validate.required && this.newVal === '') {
              this.isShowError = true;
              this.errorTips = validate.message;
              break;
            }
            if (validate.validator && !validate.validator(this.newVal)) {
              this.isShowError = true;
              this.errorTips = validate.message;
              break;
            }
            if ((validate.required && this.newVal !== '') && (validate.validator && validate.validator(this.newVal))) {
              this.isShowError = false;
              this.errorTips = '';
              break;
            }
          }
        }
      },
      handleEdit () {
        document.body.click();
        if (!this.isShowOther) {
          this.isEditable = true;
          this.$nextTick(() => {
            this.$refs.input.focus();
          });
        } else {
          this.$emit('handleShow');
        }
      },
      handleInput () {
        this.isShowError = false;
        this.errorTips = '';
      },
      handleBlur () {
        if (!this.isEditable) return;
        this.handleValidate();
        if (this.isShowError) return;
        this.triggerChange();
      },
      handleEnter (value, event) {
        if (!this.isEditable) return;
        if (event.key === 'Enter' && event.keyCode === 13) {
          this.triggerChange();
        }
      },
      hideEdit (event) {
        if (event.path && event.path.length > 0) {
          for (let i = 0; i < event.path.length; i++) {
            const target = event.path[i];
            if (target.className === 'iam-edit-input') {
              return;
            }
          }
        }

        this.handleValidate();
        if (this.isShowError) return;
        this.isEditable = false;
      },
      triggerChange () {
        this.isEditable = false;
        if (this.newVal === this.value) {
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
    @keyframes ani-edit-loading {
        to {
            transform: rotateZ(360deg)
        }
    }
</style>
<style lang='postcss' scoped>
    .iam-edit-input {
        .edit-wraper {
            position: relative;
            display: flex;
            height: 32px;
            &:hover {
                .edit-action-box {
                    .edit-action {
                        display: block;
                    }
                }
            }
        }
        .edit-content {
            max-width: calc(100% - 25px);
            line-height: 32px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .edit-action-box {
            display: flex;
            align-items: center;
            min-height: 1em;
            margin-right: auto;
            font-size: 16px;
            .edit-action {
                display: none;
                padding: 6px 15px 6px 2px;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                }
            }
            .edit-loading {
                position: absolute;
                top: 9px;
                margin-left: 2px;
                animation: 'ani-edit-loading' 1s linear infinite;
            }
        }
        .validate-error-tips {
            font-size: 12px;
            color: #ff4d4d;
        }
    }
</style>
