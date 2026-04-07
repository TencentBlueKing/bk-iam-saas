<template>
  <div class="iam-user-group-basic-info-wrapper">
    <bk-form
      :model="formData"
      form-type="vertical"
      ref="basicInfoForm">
      <iam-form-item :label="$t(`m.userGroup['用户组名']`)" required>
        <bk-input
          :value="formData.name"
          style="width: 450px;"
          clearable
          :placeholder="$t(`m.verify['用户组名输入提示']`)"
          :ext-cls="isShowNameError ? 'group-name-error' : ''"
          data-test-id="group_input_groupName"
          @input="handleNameInput"
          @blur="handleNameBlur"
          @change="handleNameChange" />
        <p class="name-empty-error" v-if="isShowNameError">{{ nameValidateText }}</p>
      </iam-form-item>
      <iam-form-item :label="$t(`m.common['描述']`)">
        <bk-input
          :value="formData.description"
          type="textarea"
          :placeholder="$t(`m.verify['请输入']`)"
          maxlength="255"
          data-test-id="group_input_groupDesc"
          @input="handleDescInput"
          @blur="handleDescBlur"
          @change="handleDescChange" />
      </iam-form-item>
    </bk-form>
  </div>
</template>

<script>
  import { isEmojiCharacter } from '@/common/util';
  const getDefaultData = () => ({
    name: '',
    approval_process_id: 1,
    description: ''
  });

  export default {
    name: '',
    components: {
    },
    props: {
      data: {
        type: Object,
        default () {
          return {};
        }
      }
    },
    data () {
      return {
        formData: getDefaultData(),
        processList: [
          {
            id: '1',
            name: '流程1'
          },
          {
            id: '2',
            name: '流程2'
          }
        ],
        isShowNameError: false,
        isShowDescError: false,
        nameValidateText: '',
        descValidateText: ''
      };
    },
    watch: {
      data: {
        handler (value) {
          if (Object.keys(value).length) {
            const { name, approval_process_id, description } = value;
            this.formData = Object.assign({}, {
              name,
              approval_process_id,
              description
            });
          }
        },
        deep: true,
        immediate: true
      }
    },
    methods: {
      handleNameInput (payload) {
        this.isShowNameError = !this.formData.name.trim() || isEmojiCharacter(this.formData.name);
        if (payload) {
          window.changeAlert = true;
        }
      },

      handleDescInput () {
        this.isShowDescError = false;
      },

      handleDescBlur (payload) {
        // const minLength = 10;
        // if (payload === '') {
        //     this.descValidateText = this.$t(`m.verify['描述必填']`);
        //     this.isShowDescError = true;
        // }
        // if (!this.isShowDescError) {
        //     if (payload.trim().length < minLength) {
        //         this.descValidateText = this.$t(`m.verify['描述最短不少于10个字符']`);
        //         this.isShowDescError = true;
        //     }
        // }
      },

      handleNameBlur (payload) {
        const maxLength = 32;
        const minLength = 5;
        const inputValue = payload.trim();
        this.nameValidateText = '';
        this.isShowNameError = false;
        if (!inputValue) {
          this.nameValidateText = this.$t(`m.verify['用户组名必填']`);
          this.isShowNameError = true;
        }
        if (isEmojiCharacter(inputValue)) {
          this.nameValidateText = this.$t(`m.verify['用户组名不允许输入表情字符']`);
          this.isShowNameError = true;
        }
        if (!this.isShowNameError) {
          if (inputValue.length > maxLength) {
            this.nameValidateText = this.$t(`m.verify['用户组名最长不超过32个字符']`);
            this.isShowNameError = true;
          }
          if (inputValue.length < minLength) {
            this.nameValidateText = this.$t(`m.verify['用户组名最短不少于5个字符']`);
            this.isShowNameError = true;
          }
        }
      },

      handleNameChange (value) {
        this.formData.name = value.trim();
        this.$emit('on-change', 'name', value);
      },

      handleDescChange (value) {
        this.formData.description = value;
        this.$emit('on-change', 'description', value);
      },

      handleProcessChange (value) {
        this.formData.approval_process_id = value;
        this.$emit('on-change', 'approval_process_id', value);
      },

      submit () {
        return this.$refs.basicInfoForm.validate().then(validator => {
          return Promise.resolve(this.formData);
        }, validator => {
          return Promise.reject(validator.content);
        });
      },

      handleValidator () {
        const maxLength = 32;
        const minLength = 5;
        // const minDescLength = 10;
        const payload = this.formData.name;
        // const desc = this.formData.description;
        if (payload === '') {
          this.nameValidateText = this.$t(`m.verify['用户组名必填']`);
          this.isShowNameError = true;
        }
        if (!this.isShowNameError) {
          if (payload.trim().length > maxLength) {
            this.nameValidateText = this.$t(`m.verify['用户组名最长不超过32个字符']`);
            this.isShowNameError = true;
          }
          if (payload.trim().length < minLength) {
            this.nameValidateText = this.$t(`m.verify['用户组名最短不少于5个字符']`);
            this.isShowNameError = true;
          }
          // if (!/^[^\s]*$/g.test(payload)) {
          //     this.nameValidateText = this.$t(`m.verify['用户组名不允许空格']`)
          //     this.isShowNameError = true
          // }
        }

        // if (desc === '') {
        //     this.descValidateText = this.$t(`m.verify['描述必填']`);
        //     this.isShowDescError = true;
        // }
        // if (!this.isShowDescError) {
        //     if (desc.trim().length < minDescLength) {
        //         this.descValidateText = this.$t(`m.verify['描述最短不少于10个字符']`);
        //         this.isShowDescError = true;
        //     }
        // }
        // return this.isShowNameError || this.isShowDescError;
        return this.isShowNameError;
      },

      reset () {
        this.$refs.basicInfoForm.formItems.forEach(item => {
          item.validator.content = '';
          item.validator.state = '';
        });
      }
    }
  };
</script>
<style lang="postcss">
    .iam-user-group-basic-info-wrapper {
        position: relative;
        top: -6px;
        .group-name-error {
            .bk-form-input {
                border-color: #ff5656;
            }
        }
        .group-desc-error {
            .bk-textarea-wrapper {
                border-color: #ff5656;
            }
        }
        .name-empty-error,
        .desc-empty-error {
            font-size: 12px;
            color: #ff4d4d;
        }
    }
</style>
