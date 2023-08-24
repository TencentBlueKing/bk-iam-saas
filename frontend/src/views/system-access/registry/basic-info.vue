<template>
  <bk-form class="action-base-info" :model="formData" :rules="rules" form-type="vertical" ref="basicInfoForm">
    <iam-form-item :label="$t(`m.access['操作ID']`)" :property="'id'" required
      :desc="$t(`m.access['操作的唯一标识']`)">
      <bk-input class="input" :disabled="!formData.isNewAdd" v-model="formData.id"
        @change="handleChange('id', ...arguments)" :placeholder="$t(`m.access['请输入操作ID']`)" />
    </iam-form-item>
    <iam-form-item :label="$t(`m.access['操作类型']`)" :property="'type'" required
      :desc="$t(`m.access['仅使用建筑材料操作分类使用']`)">
      <bk-select v-model="formData.type" class="input" :disabled="!formData.isEdit"
        @change="handleChange('type', ...arguments)" searchable :placeholder="$t(`m.access['请选择操作类型']`)">
        <bk-option v-for="option in typeList"
          :key="option.id"
          :id="option.id"
          :name="`${option.name}（${option.id}）`">
        </bk-option>
      </bk-select>
    </iam-form-item>
    <iam-form-item :label="$t(`m.access['操作中文名']`)" :property="'name'" required
      :desc="$t(`m.access['即操作展示名称，中文名称：名词+动词，如：服务器重启，脚本操作']`)">
      <bk-input class="input" :disabled="!formData.isEdit" v-model="formData.name"
        @change="handleChange('name', ...arguments)" :placeholder="$t(`m.access['请输入操作中文名']`)" />
    </iam-form-item>
    <iam-form-item :label="$t(`m.access['操作英文名']`)" :property="'name_en'" required
      :desc="$t(`m.access['国际化版本会展示该字段']`)">
      <bk-input class="input" :disabled="!formData.isEdit" v-model="formData.name_en"
        @change="handleChange('name_en', ...arguments)" :placeholder="$t(`m.access['请输入操作英文名']`)" />
    </iam-form-item>
    <iam-form-item :label="$t(`m.access['操作中文描述']`)" :property="'description'" required
      :desc="$t(`m.access['简要描述清楚操作的功能作用']`)">
      <bk-input
        type="textarea"
        v-model="formData.description"
        :disabled="!formData.isEdit"
        @change="handleChange('description', ...arguments)"
        :placeholder="$t(`m.access['请输入操作中文描述']`)">
      </bk-input>
    </iam-form-item>
    <iam-form-item :label="$t(`m.access['操作英文描述']`)" :property="'description_en'" required
      :desc="$t(`m.access['国际化版本会展示该字段']`)">
      <!-- eslint-disable vue/camelcase -->
      <bk-input
        type="textarea"
        v-model="formData.description_en"
        :disabled="!formData.isEdit"
        @change="handleChange('description_en', ...arguments)"
        :placeholder="$t(`m.access['请输入操作英文描述']`)">
      </bk-input>
    </iam-form-item>
  </bk-form>
</template>
<script>
  export default {
    props: {
      // infoData
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
          type: '',
          name: '',
          name_en: '',
          description: '',
          description_en: '',
          isNewAdd: true,
          isEdit: true
        },
        typeList: [
          { id: 'create', name: '创建' },
          { id: 'edit', name: '编辑' },
          { id: 'view', name: '查看' },
          { id: 'delete', name: '删除' },
          { id: 'list', name: '列表' },
          { id: 'manage', name: '管理' },
          { id: 'execute', name: '执行' },
          { id: 'debug', name: '调试' },
          { id: 'use', name: '使用' }
        ],
        rules: null
      };
    },
    computed: {
      /**
       * modelingId
       */
      modelingId () {
        return this.$route.params.id;
      }
    },
    watch: {
      /**
       * infoData
       */
      infoData: {
        handler (value) {
          this.rules = {
            id: [
              { required: true, message: this.$t(`m.verify['操作ID必填']`), trigger: 'change' },
              {
                max: 32,
                message: '不能多于32个字符',
                trigger: 'change'
              },
              { regex: /^[a-z][a-z-z0-9_-]*$/, message: this.$t(`m.verify['只允许小写字母开头、包含小写字母、数字、下划线(_)和连接符(-)']`), trigger: 'blur' }
            ],
            type: [
              { required: true, message: this.$t(`m.verify['操作类型必选']`), trigger: 'change' }
            ],
            name: [
              { required: true, message: this.$t(`m.verify['操作中文名必填']`), trigger: 'change' }
            ],
            name_en: [
              { required: true, message: this.$t(`m.verify['操作英文名必填']`), trigger: 'change' },
              { regex: /^[a-zA-Z0-9,.!?\s_]*$/, message: this.$t(`m.verify['只允许输入英文']`), trigger: 'blur' }
            ],
            description: [
              { required: true, message: this.$t(`m.verify['操作中文描述必填']`), trigger: 'change' }
            ],
            description_en: [
              { required: true, message: this.$t(`m.verify['操作英文描述必填']`), trigger: 'change' },
              { regex: /^[a-zA-Z0-9,.!?\s_]*$/, message: this.$t(`m.verify['只允许输入英文']`), trigger: 'blur' }

            ]
          };
          if (value && Object.keys(value).length) {
            this.formData.id = value.id;
            this.formData.type = value.type;
            this.formData.name = value.name;
            this.formData.name_en = value.name_en;
            this.formData.description = value.description;
            this.formData.description_en = value.description_en;
            this.formData.isNewAdd = value.isNewAdd;
            this.formData.isEdit = value.isEdit;
          }
          if (this.formData.isNewAdd) {
            this.rules.id.push({ validator: this.checkName, message: this.$t(`m.verify['操作ID已被占用']`), trigger: 'change' });
          }
        },
        deep: true,
        immediate: true
      }
    },
    methods: {
      /**
       * checkName
       */
      // async checkName (val) {
      //     try {
      //         const res = await this.$store.dispatch('access/checkModelingId', {
      //             id: val.trim()
      //         })
      //         return !res.data.exists
      //     } catch (e) {
      //         console.error(e)
      //         return false
      //     }
      // },

      /**
       * 校验操作ID唯一性
       */
      async checkName (val) {
        try {
          const res = await this.$store.dispatch('access/checkResourceId', {
            id: this.modelingId,
            data: {
              type: 'action',
              id: val.trim()
            }
          });
          return !res.data.exists;
        } catch (e) {
          console.error(e);
          return false;
        }
      },

      /**
       * handleValidator
       */
      handleValidator () {
        return this.$refs.basicInfoForm.validate().then(validator => {
          this.$emit('on-change', this.formData);
        }, validator => {
          console.warn('validator', validator);
          return Promise.reject(validator.content);
        });
      },

      /**
       * handleChange
       */
      handleChange (idx, value) {
        this.formData[idx] = value;
        this.$emit('on-change', this.formData);
      },

      /**
       * resetError
       */
      resetError () {
        this.$refs.basicInfoForm.clearError();
      }
    }
  };
</script>

<style lang="postcss">
    .action-base-info {
        .input {
            width: 450px;
        }
    }
</style>
