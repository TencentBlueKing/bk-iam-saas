<template>
  <bk-dialog
    v-model="isShowDialog"
    width="500"
    :title="$t(`m.access['编辑分组']`)"
    :mask-close="false"
    :close-icon="false"
    header-position="left"
    ext-cls="add-group-dialog"
    @after-leave="handleAfterLeave">
    <div class="content-wrapper">
      <bk-form :label-width="110" :model="formData" :rules="rules" ref="editGroupForm">
        <bk-form-item :label="$t(`m.access['分组名称']`)" :required="true" :property="'name'" :icon-offset="-5">
          <bk-input style="width: 320px;" v-model="formData.name"
            :placeholder="$t(`m.access['请输入分组名称']`)"></bk-input>
        </bk-form-item>
        <bk-form-item :label="$t(`m.access['分组英文名称']`)" :required="true"
          :property="'name_en'" :icon-offset="-5">
          <bk-input style="width: 320px;" v-model="formData.name_en"
            :placeholder="$t(`m.access['请输入分组英文名称']`)"></bk-input>
        </bk-form-item>
        <bk-form-item :label="$t(`m.access['分组操作']`)" :required="true"
          :property="'selectedActions'" :icon-offset="-5">
          <bk-select style="width: 320px;" v-model="formData.selectedActions"
            show-select-all searchable multiple display-tag :placeholder="$t(`m.access['请选择分组操作']`)">
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
      // show props
      show: {
        type: Boolean,
        default: false
      },
      // modelingId props
      modelingId: {
        type: String,
        default: ''
      },
      // 已分组的操作以及分组本身的数据
      groupList: {
        type: Array,
        default: () => ([])
      },
      // 还没有分组的操作
      noGroupActionList: {
        type: Array,
        default: () => ([])
      },
      // 当前更新的 group
      curEditGroup: {
        type: Object,
        default: () => ({})
      },
      // 当前更新的 group 的索引
      curEditGroupIndex: {
        type: Number,
        default: -1
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
      /**
       * show
       */
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
                message: this.$t(`m.access['请输入分组名称']`),
                trigger: 'change'
              },
              {
                validator: this.checkName,
                message: this.$t(`m.access['分组名称已存在']`),
                trigger: 'change'
              }
            ],
            name_en: [
              {
                required: true,
                message: this.$t(`m.access['请输入分组英文名称']`),
                trigger: 'change'
              },
              {
                validator: this.checkNameEn,
                message: this.$t(`m.access['分组英文名称已存在']`),
                trigger: 'change'
              }
            ],
            selectedActions: [
              {
                required: true,
                message: this.$t(`m.access['请选择分组操作']`),
                trigger: 'change'
              }
            ]
          };

          const formData = {};
          formData.name = this.curEditGroup.name;
          formData.name_en = this.curEditGroup.name_en;
          const selectedActions = JSON.parse(JSON.stringify(this.curEditGroup.actions));
          formData.selectedActions = selectedActions.map(sa => sa.id);
          this.formData = Object.assign({}, formData);

          const actionList = selectedActions.concat();
          this.noGroupActionList.forEach(item => {
            actionList.push(item);
          });

          this.actionList.splice(0, this.actionList.length, ...actionList);
        },
        immediate: true
      }
    },
    methods: {
      /**
       * checkName
       */
      checkName (v) {
        const val = v.trim();
        if (val === this.curEditGroup.name) {
          return true;
        }
        const isExist = !!this.groupList.filter(item => item.name.trim() === val).length;
        if (isExist) {
          return false;
        }

        const isExistInSub = !!this.groupList.filter(item => {
          if (item.sub_groups && item.sub_groups.length) {
            return item.sub_groups.filter(subGroup => subGroup.name.trim() === val).length;
          }
        }).length;

        if (isExistInSub) {
          return false;
        }

        return true;
      },

      /**
       * checkNameEn
       */
      checkNameEn (v) {
        const val = v.trim();
        if (val === this.curEditGroup.name_en) {
          return true;
        }
        const isExist = !!this.groupList.filter(item => item.name_en.trim() === val).length;
        if (isExist) {
          return false;
        }

        const isExistInSub = !!this.groupList.filter(item => {
          if (item.sub_groups && item.sub_groups.length) {
            return item.sub_groups.filter(subGroup => subGroup.name_en.trim() === val).length;
          }
        }).length;

        if (isExistInSub) {
          return false;
        }

        return true;
      },

      /**
       * handleSumbit
       */
      handleSumbit () {
        const formComp = this.$refs.editGroupForm;
        formComp.validate().then(async validator => {
          try {
            this.submitLoading = true;
            const groupList = [];
            groupList.splice(0, 0, ...this.groupList);

            const actions = this.formData.selectedActions.map(
              actionId => this.actionList.find(act => act.id === actionId)
            );

            this.$set(groupList, this.curEditGroupIndex, {
              name: this.formData.name,
              name_en: this.formData.name_en,
              actions: actions
            });

            await this.$store.dispatch('access/updateModeling', {
              id: this.modelingId,
              data: {
                type: 'action_groups',
                data: groupList
              }
            });
            this.$emit('on-success', this.curEditGroupIndex);
          } catch (e) {
            console.error(e);
            this.bkMessageInstance = this.$bkMessage({
              limit: 1,
              theme: 'error',
              message: e.message || e.data.msg || e.statusText
            });
          } finally {
            this.submitLoading = false;
          }
        }, validator => {
          console.warn(validator);
          // return Promise.reject(validator.content)
        });
      },

      /**
       * hide
       */
      hide () {
        this.$emit('on-hide');
      },

      /**
       * handleAfterLeave
       */
      handleAfterLeave () {
        this.$emit('update:show', false);
        this.$emit('on-after-leave');
        this.$refs.editGroupForm.clearError();
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
