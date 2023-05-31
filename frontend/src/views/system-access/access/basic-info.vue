<template>
  <div class="iam-access-base-info-wrapper">
    <bk-form :model="formData" :rules="rules" form-type="vertical" ref="basicInfoForm">
      <iam-form-item :label="$t(`m.access['系统ID']`)" :property="'id'" required
        :desc="$t(`m.access['接入系统在权限中心的唯一标识，一般为接入系统的app_code']`)">
        <bk-input class="input" v-if="isEdit" disabled v-model="formData.id"
          :placeholder="$t(`m.access['请输入app_code']`)" />
        <bk-input class="input" v-else v-model="formData.id" :placeholder="$t(`m.access['请输入app_code']`)" />
      </iam-form-item>
      <iam-form-item :label="$t(`m.access['系统中文名称']`)" :property="'name'" required
        :desc="$t(`m.access['接入系统的中文名称']`)">
        <bk-input class="input" v-model="formData.name" :placeholder="$t(`m.access['请输入接入的系统中文名称']`)" />
      </iam-form-item>
      <iam-form-item :label="$t(`m.access['系统英文名称']`)" :property="'name_en'" required
        :desc="$t(`m.access['接入系统的英文文名称']`)">
        <bk-input class="input" v-model="formData.name_en" :placeholder="$t(`m.access['请输入接入的系统英文名称']`)" />
      </iam-form-item>
      <iam-form-item :label="$t(`m.access['系统回调地址']`)" :property="'host'" required
        :desc="$t(`m.access['权限中心会通过该URL访问访问系统进行一些的交互']`)">
        <bk-input class="input" v-model="formData.host" :placeholder="$t(`m.access['请输入接入的系统回调地址']`)" />
        <bk-checkbox class="basic-auth" :true-value="'basic'" :false-value="'none'" v-model="formData.auth">
          {{$t(`m.access['Basic认证']`)}}
        </bk-checkbox>
      </iam-form-item>
      <iam-form-item :label="$t(`m.access['系统健康检查地址']`)" :property="'healthz'" required
        :desc="$t(`m.access['权限中心会通过该URL确认接入系统状态正常']`)">
        <bk-input class="input" v-model="formData.healthz" :placeholder="$t(`m.access['请输入接入的系统健康检查地址']`)">
          <template slot="prepend">
            <div class="group-text">{{formData.host}}</div>
          </template>
        </bk-input>
      </iam-form-item>
      <iam-form-item :label="$t(`m.access['系统中文描述']`)" :property="'description'" required
        :desc="$t(`m.access['接入系统的产品功能简要描述']`)">
        <bk-input
          type="textarea"
          v-model="formData.description"
          :maxlength="100"
          :placeholder="$t(`m.verify['请输入系统中文描述']`)">
        </bk-input>
      </iam-form-item>
      <iam-form-item :label="$t(`m.access['系统英文描述']`)" :property="'description_en'" required
        :desc="$t(`m.access['国际化版本会展示该信息']`)">
        <!-- eslint-disable vue/camelcase -->
        <bk-input
          type="textarea"
          v-model="formData.description_en"
          :maxlength="100"
          :placeholder="$t(`m.verify['请输入系统英文描述']`)">
        </bk-input>
      </iam-form-item>
    </bk-form>
  </div>
</template>
<script>
  export default {
    props: {
      infoData: {
        type: Object,
        default: () => {
          return {};
        }
      }
    },
    data () {
      return {
        formData: {
          id: '',
          name: '',
          name_en: '',
          host: '',
          auth: 'basic',
          healthz: '',
          description: '',
          description_en: ''
        },
        isEdit: false
      };
    },
    watch: {
      infoData: {
        handler (value) {
          this.rules = {
            id: [
              { required: true, message: this.$t(`m.verify['系统ID必填']`), trigger: 'blur' },
              {
                max: 32,
                message: '不能多于32个字符',
                trigger: 'blur'
              },
              { regex: /^[a-z][a-z-z0-9_-]*$/, message: this.$t(`m.verify['只允许小写字母开头、包含小写字母、数字、下划线(_)和连接符(-)']`), trigger: 'blur' }
            ],
            name: [
              { required: true, message: this.$t(`m.verify['系统中文名称必填']`), trigger: 'blur' }
            ],
            name_en: [
              { required: true, message: this.$t(`m.verify['系统英文名称必填']`), trigger: 'blur' },
              { regex: /^[a-zA-Z0-9,.!?\s_]*$/, message: this.$t(`m.verify['只允许输入英文']`), trigger: 'blur' }
            ],
            host: [
              { required: true, message: this.$t(`m.verify['系统回调地址必填']`), trigger: 'blur' },
              { regex: /^((https|http|ftp|rtsp|mms)?:\/\/)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+(\/?[A-Za-z0-9]+(\/?))*$/, message: this.$t(`m.verify['请输入正确的系统回调地址']`), trigger: 'blur' }
            ],
            healthz: [
              { required: true, message: this.$t(`m.verify['系统健康检查地址必填']`), trigger: 'blur' },
              { regex: /^(\/[A-Za-z0-9_-]+(\/?))+$/, message: this.$t(`m.verify['请输入正确的系统健康检查地址']`), trigger: 'blur' }

            ],
            description: [
              { required: true, message: this.$t(`m.verify['系统中文描述必填']`), trigger: 'blur' }
            ],
            description_en: [
              { required: true, message: this.$t(`m.verify['系统英文描述必填']`), trigger: 'blur' },
              { regex: /^[a-zA-Z0-9,.!?\s_]*$/, message: this.$t(`m.verify['只允许输入英文']`), trigger: 'blur' }

            ]
          };
          if (value && Object.keys(value).length) {
            this.formData.id = value.id;
            this.formData.name = value.name;
            this.formData.name_en = value.name_en;
            this.formData.host = value.provider_config.host;
            this.formData.auth = value.provider_config.auth;
            this.formData.healthz = value.provider_config.healthz;
            this.formData.description = value.description;
            this.formData.description_en = value.description_en;
            this.isEdit = true;
          }
          if (!this.isEdit) {
            this.rules.id.push({ validator: this.checkName, message: this.$t(`m.verify['系统ID已被占用']`), trigger: 'change' });
          }
        },
        deep: true,
        immediate: true
      },
      formData: {
        handler (value) {
          this.$store.commit('updateHost', value.host);
        },
        deep: true,
        immediate: true
      }
    },
    methods: {
      async checkName (val) {
        try {
          const res = await this.$store.dispatch('access/checkModelingId', {
            id: val.trim()
          });
          return !res.data.exists;
        } catch (e) {
          console.error(e);
          return false;
        }
      },

      handleValidator () {
        return this.$refs.basicInfoForm.validate().then(validator => {
          this.$emit('on-change', this.formData);
        }, validator => {
          console.warn(validator);
          return Promise.reject(validator.content);
        });
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
    .iam-access-base-info-wrapper {
        width: 600px;
        position: relative;
        top: -6px;
        .input {
            width: 450px;
        }
        .basic-auth {
            margin-left: 10px;
        }
    }
</style>
