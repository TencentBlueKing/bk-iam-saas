<template>
  <div class="iam-edit-textarea" :style="styles">
    <template v-if="!isEditable">
      <div class="edit-wraper">
        <div class="edit-content" :title="newVal">
          <slot v-bind:value="newVal">
            {{ newVal }}
            <template v-if="newVal === '' && !isLoading">
              --
            </template>
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
      <bk-input
        v-model="newVal"
        class="edit-input"
        ref="input"
        type="textarea"
        :placeholder="placeholder"
        :maxlength="maxLength"
        :rows="3"
        @input="handleInput"
        @blur="handleBlur" />
      <p class="validate-error-tips" v-if="isShowError">{{ errorTips }}</p>
    </template>
  </div>
</template>
<script>
  import il8n from '@/language';

  export default {
    name: 'iam-edit-textarea',
    props: {
      field: {
        type: String,
        required: true
      },
      value: {
        type: String,
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
      maxLength: {
        type: Number,
        default: 255
      },
      index: {
        type: Number
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
        newVal: this.value,
        isEditable: false,
        isLoading: false,
        isShowError: '',
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
        this.isEditable = true;
        this.$nextTick(() => {
          this.$refs.input.focus();
        });
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
            if (target.className === 'iam-edit-textarea') {
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
        }, this.index).then(() => {
          this.$emit('on-change', {
            [this.field]: this.newVal
          });
          // this.messageSuccess('编辑成功')
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
    .iam-edit-textarea {
        position: relative;
        .edit-wraper {
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
        .edit-input {
            width: 100%;
        }
        .validate-error-tips {
            font-size: 12px;
            color: #ff4d4d;
        }
    }
</style>
