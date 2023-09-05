<template>
  <bk-dialog
    v-model="isShowDialog"
    width="500"
    :title="$t(`m.access['添加常用操作']`)"
    :mask-close="false"
    :close-icon="false"
    header-position="left"
    ext-cls="add-group-dialog"
    @after-leave="handleAfterLeave">
    <div class="content-wrapper">
      <bk-form :label-width="140" :model="formData" :rules="rules" ref="addGroupForm">
        <bk-form-item :label="$t(`m.access['常用操作名称']`)" :required="true" :property="'name'" :icon-offset="-5">
          <bk-input style="width: 290px;" v-model="formData.name"
            :placeholder="$t(`m.access['请输入常用操作名称']`)"></bk-input>
        </bk-form-item>
        <bk-form-item :label="$t(`m.access['常用操作英文名称']`)" :required="true" :property="'name_en'"
          :icon-offset="-5">
          <bk-input style="width: 290px;" v-model="formData.name_en"
            :placeholder="$t(`m.access['请输入常用操作英文名称']`)"></bk-input>
        </bk-form-item>
        <bk-form-item :label="$t(`m.access['操作']`)" :required="true" :property="'selectedActions'"
          :icon-offset="-5">
          <bk-select style="width: 290px;" v-model="formData.selectedActions"
            show-select-all searchable multiple display-tag :placeholder="$t(`m.access['请选择操作']`)">
            <bk-option v-for="option in actionList"
              :key="option.id"
              :id="option.id"
              :name="option.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
      </bk-form>
    </div>
    <template slot="footer">
      <bk-button theme="primary" :loading="submitLoading" @click="handleSumbit">
        {{ $t(`m.common['确定']`) }}
      </bk-button>
      <bk-button style="margin-left: 10px;" :disabled="submitLoading" @click="hide">
        {{ $t(`m.common['取消']`) }}
      </bk-button>
    </template>
  </bk-dialog>
</template>
<script>
  export default {
    name: '',
    props: {
      show: {
        type: Boolean,
        default: false
      },
      modelingId: {
        type: String,
        default: ''
      },
      commonList: {
        type: Array,
        default: () => ([])
      },
      allActionList: {
        type: Array,
        default: () => ([])
      }
    },
    data () {
      return {
        isShowDialog: false,
        submitLoading: false,
        formData: {
          name: '',
          name_en: '',
          selectedActions: []
        },
        actions: [],
        actionList: [],
        rules: null
      };
    },
    watch: {
      show: {
        handler (value) {
          this.isShowDialog = !!value;
          if (!this.isShowDialog) {
            return;
          }
          this.rules = {
            name: [
              {
                required: true,
                message: this.$t(`m.access['请输入常用操作名称']`),
                trigger: 'change'
              }
            ],
            name_en: [
              {
                required: true,
                message: this.$t(`m.access['请输入常用操作英文名称']`),
                trigger: 'change'
              }
            ],
            selectedActions: [
              {
                required: true,
                message: this.$t(`m.access['请选择操作']`),
                trigger: 'change'
              }
            ]
          };

          this.actionList.splice(0, this.actionList.length, ...this.allActionList);
        },
        immediate: true
      }
    },
    methods: {
      handleSumbit () {
        const formComp = this.$refs.addGroupForm;
        formComp.validate().then(async validator => {
          try {
            this.submitLoading = true;
            const actions = this.formData.selectedActions.map(
              actionId => ({ id: this.actionList.find(act => act.id === actionId).id })
            );
                        
            const commonList = [];
            commonList.splice(0, 0, ...this.commonList);

            commonList.push({
              name: this.formData.name,
              name_en: this.formData.name_en,
              actions
            });

            await this.$store.dispatch('access/updateModeling', {
              id: this.modelingId,
              data: {
                type: 'common_actions',
                data: commonList
              }
            });
            this.$emit('on-success');
          } catch (e) {
            console.error(e);
            this.messageAdvancedError(e);
          } finally {
            this.submitLoading = false;
          }
        }, validator => {
          console.warn(validator);
          // return Promise.reject(validator.content)
        });
      },

      hide () {
        this.$emit('on-hide');
      },

      handleAfterLeave () {
        this.$emit('update:show', false);
        this.$emit('on-after-leave');
        this.$refs.addGroupForm.clearError();
        this.submitLoading = false;
        this.formData = Object.assign({}, {
          name: '',
          name_en: '',
          selectedActions: []
        });
        this.actionList.splice(0, this.actionList.length, ...[]);
        this.actions.splice(0, this.actions.length, ...[]);
      }
    }
  };
</script>
