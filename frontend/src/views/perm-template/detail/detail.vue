<template>
  <div class="iam-template-detail-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
    <template v-if="!isLoading">
      <p class="edit-action">
        {{ $t(`m.permTemplateDetail['如需编辑权限模板的内容请点击']`) }}
        <bk-button
          theme="primary"
          size="small"
          text
          @click="handleEdit">
          {{ $t(`m.common['编辑']`) }}
        </bk-button>
      </p>
      <render-horizontal-block :label="$t(`m.common['基本信息']`)" ext-cls="basic-info-wrapper">
        <detail-layout mode="see">
          <render-layout>
            <detail-item :label="$t(`m.permTemplateDetail['模板名称']`)">
              <iam-edit-input
                field="name"
                :placeholder="$t(`m.common['模板名称可随时修改']`)"
                :rules="rules"
                :value="basicInfo.name"
                :remote-hander="handleUpdateTemplate" />
            </detail-item>
            <detail-item label="ID：">
              <iam-edit-input
                field="id"
                mode="detail"
                :value="basicInfo.id" />
            </detail-item>
            <detail-item :label="$t(`m.permTemplateDetail['所属系统']`)">
              <iam-edit-input
                field="systemName"
                mode="detail"
                :value="basicInfo.systemName" />
            </detail-item>
            <detail-item :label="$t(`m.permTemplateDetail['最近更新时间']`)">
              <iam-edit-input
                field="updatedTime"
                mode="detail"
                :value="basicInfo.updatedTime" />
            </detail-item>
            <detail-item :label="$t(`m.permTemplateDetail['描述']`)">
              <iam-edit-textarea
                field="description"
                width="600px"
                :value="basicInfo.description"
                :remote-hander="handleUpdateTemplate" />
            </detail-item>
          </render-layout>
        </detail-layout>
      </render-horizontal-block>
      <render-horizontal-block :label="$t(`m.permTemplateDetail['操作详情']`)">
        <render-action :actions="basicInfo.actions" mode="detail" />
      </render-horizontal-block>
      <div slot="action" style="display: none">
        <!-- <bk-button
                    theme="primary"
                    :loading="editLoading"
                    @click="handleEdit">
                    {{ $t(`m.common['编辑']`) }}
                </bk-button>
                <bk-button
                    style="margin-left: 10px;"
                    @click="handleCancel">
                    {{ $t(`m.common['返回']`) }}
                </bk-button> -->
      </div>
    </template>
  </div>
</template>
<script>
  import _ from 'lodash';
  import DetailLayout from '@/components/detail-layout';
  import DetailItem from '@/components/detail-layout/item';
  import IamEditInput from '@/components/iam-edit/input';
  import IamEditTextarea from '@/components/iam-edit/textarea';
  import RenderLayout from '../common/render-layout';
  import RenderAction from '../components/render-action';
  export default {
    name: '',
    components: {
      DetailLayout,
      DetailItem,
      IamEditInput,
      IamEditTextarea,
      RenderLayout,
      RenderAction
    },
    props: {
      id: {
        type: [String, Number],
        default: ''
      },
      version: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        basicInfo: {
          name: '',
          description: '',
          systemName: '',
          systemId: '',
          actions: [],
          updatedTime: '',
          id: ''
        },
        requestQueue: ['detail'],
        defaultCheckedActions: [],
        editRequestQueue: []
      };
    },
    computed: {
      isLoading () {
        return this.requestQueue.length > 0;
      },
      editLoading () {
        return this.editRequestQueue.length > 0;
      }
    },
    watch: {
      id: {
        handler () {
          this.fetchTemplateDetail();
        },
        immediate: true
      }
    },
    created () {
      this.rules = [
        {
          required: true,
          message: this.$t(`m.verify['模板名称必填']`),
          trigger: 'blur'
        },
        {
          validator: (value) => {
            return value.length <= 32;
          },
          message: this.$t(`m.verify['模板名称最长不超过32个字符']`),
          trigger: 'blur'
        }
      ];
    },
    methods: {
      async fetchTemplateDetail () {
        try {
          const res = await this.$store.dispatch('permTemplate/getTemplateDetail', { id: this.id, grouping: true });
          this.basicInfo = Object.assign({}, {
            name: res.data.name,
            description: res.data.description,
            systemName: res.data.system.name,
            systemId: res.data.system.id,
            actions: res.data.actions,
            updatedTime: res.data.updated_time,
            id: this.id
          });
          this.basicInfo.actions = res.data.actions;
          this.handleActionData();
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
        }
      },

      handleActionData () {
        this.basicInfo.actions.forEach((item, index) => {
          this.$set(item, 'expanded', false);
          let count = 0;
          let allCount = 0;
          let deleteCount = 0;
          if (!item.actions) {
            this.$set(item, 'actions', []);
          }
          item.actions.forEach(act => {
            this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
            this.$set(act, 'disabled', act.tag === 'readonly');
            if (act.checked) {
              ++count;
              this.defaultCheckedActions.push(act.id);
            }
            if (act.tag === 'delete') {
              ++deleteCount;
            }
            ++allCount;
          })
          ;(item.sub_groups || []).forEach(sub => {
            this.$set(sub, 'expanded', false);
            this.$set(sub, 'actionsAllChecked', false);
            if (!sub.actions) {
              this.$set(sub, 'actions', []);
            }
            sub.actions.forEach(act => {
              this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
              this.$set(act, 'disabled', act.tag === 'readonly');
              if (act.checked) {
                ++count;
                this.defaultCheckedActions.push(act.id);
              }
              if (act.tag === 'delete') {
                ++deleteCount;
              }
              ++allCount;
            });

            const isSubAllChecked = sub.actions.every(v => v.checked);
            this.$set(sub, 'allChecked', isSubAllChecked);
          });

          this.$set(item, 'deleteCount', deleteCount);
          this.$set(item, 'count', count);
          this.$set(item, 'allCount', allCount);

          const isAllChecked = item.actions.every(v => v.checked);
          const isAllDisabled = item.actions.every(v => v.disabled);
          this.$set(item, 'allChecked', isAllChecked);
          if (item.sub_groups && item.sub_groups.length > 0) {
            this.$set(item, 'actionsAllChecked', isAllChecked && item.sub_groups.every(v => v.allChecked));
            this.$set(item, 'actionsAllDisabled', isAllDisabled && item.sub_groups.every(v => {
              return v.actions.every(sub => sub.disabled);
            }));
          } else {
            this.$set(item, 'actionsAllChecked', isAllChecked);
            this.$set(item, 'actionsAllDisabled', isAllDisabled);
          }
        });
        if (this.basicInfo.actions.length === 1) {
          this.basicInfo.actions[0].expanded = true;
        }
      },

      getActionsData (payload) {
        const temps = _.cloneDeep(this.basicInfo.actions);
        // 交集
        const intersections = this.defaultCheckedActions.filter(item => payload.includes(item));
        // 已删除的
        const hasDeleteActions = this.defaultCheckedActions.filter(item => !intersections.includes(item));
        // 新增的
        const hasAddActions = payload.filter(item => !intersections.includes(item));
        temps.forEach((item, index) => {
          this.$set(item, 'expanded', index === 0);
          let count = 0;
          let deleteCount = 0;
          if (!item.actions) {
            this.$set(item, 'actions', []);
          }
          item.actions.forEach(act => {
            this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
            this.$set(act, 'disabled', act.tag === 'readonly');
            if (hasAddActions.includes(act.id)) {
              this.$set(act, 'checked', true);
              this.$set(act, 'flag', 'added');
            }
            if (act.checked && hasDeleteActions.includes(act.id)) {
              act.checked = false;
              this.$set(act, 'flag', 'cancel');
            }
            if (act.checked) {
              ++count;
            }
            if (act.tag === 'delete') {
              ++deleteCount;
            }
          })
          ;(item.sub_groups || []).forEach(sub => {
            this.$set(sub, 'expanded', false);
            this.$set(sub, 'actionsAllChecked', false);
            if (!sub.actions) {
              this.$set(sub, 'actions', []);
            }
            sub.actions.forEach(act => {
              this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
              this.$set(act, 'disabled', act.tag === 'readonly');
              if (hasAddActions.includes(act.id)) {
                this.$set(act, 'checked', true);
                this.$set(act, 'flag', 'added');
              }
              if (act.checked && hasDeleteActions.includes(act.id)) {
                act.checked = false;
                this.$set(act, 'flag', 'cancel');
              }
              if (act.checked) {
                ++count;
              }
              if (act.tag === 'delete') {
                ++deleteCount;
              }
            });

            const isSubAllChecked = sub.actions.every(v => v.checked);
            this.$set(sub, 'allChecked', isSubAllChecked);
          });

          this.$set(item, 'deleteCount', deleteCount);
          this.$set(item, 'count', count);

          const isAllChecked = item.actions.every(v => v.checked);
          const isAllDisabled = item.actions.every(v => v.disabled);
          this.$set(item, 'allChecked', isAllChecked);
          if (item.sub_groups && item.sub_groups.length > 0) {
            this.$set(item, 'actionsAllChecked', isAllChecked && item.sub_groups.every(v => v.allChecked));
            this.$set(item, 'actionsAllDisabled', isAllDisabled && item.sub_groups.every(v => {
              return v.actions.every(sub => sub.disabled);
            }));
          } else {
            this.$set(item, 'actionsAllChecked', isAllChecked);
            this.$set(item, 'actionsAllDisabled', isAllDisabled);
          }
        });

        return temps;
      },

      async handleEdit () {
        this.editRequestQueue = ['getPre', 'addPre'];
        await this.getPreUpdateInfo();
      },

      async getPreUpdateInfo () {
        try {
          const res = await this.$store.dispatch('permTemplate/getPreUpdateInfo', { id: this.id });
          const flag = Object.keys(res.data).length > 0;
          const nameCache = window.localStorage.getItem('iam-header-name-cache');
          window.localStorage.setItem('iam-header-title-cache', `${this.$t(`m.nav['编辑权限模板']`)}(${nameCache})`);
          if (flag) {
            this.$store.commit('permTemplate/updatePreActionIds', res.data.action_ids);
            this.$store.commit('permTemplate/updateAction', this.getActionsData(res.data.action_ids));
            await this.addPreUpdateInfo(res.data.action_ids);
            this.$router.push({
              name: 'permTemplateDiff',
              params: this.$route.params
            });
          } else {
            this.editRequestQueue = ['getPre'];
            this.$router.push({
              name: 'permTemplateEdit',
              params: this.$route.params
            });
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.editRequestQueue.shift();
        }
      },

      async addPreUpdateInfo (payload) {
        try {
          const res = await this.$store.dispatch('permTemplate/addPreUpdateInfo', {
            id: this.$route.params.id,
            data: {
              action_ids: payload
            }
          });
          this.$store.commit('permTemplate/updateCloneActions', res.data);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.editRequestQueue.shift();
        }
      },

      handleCancel () {
        this.$router.push({
          name: 'permTemplate'
        });
      },

      handleUpdateTemplate (payload) {
        const { name, description } = this.basicInfo;
        const params = {
          name: name.trim(),
          description,
          id: this.id,
                    ...payload
        };
        return this.$store.dispatch('permTemplate/updateTemplate', params)
          .then(() => {
            this.messageSuccess(this.$t(`m.info['编辑成功']`), 3000);
            this.basicInfo.name = params.name;
            this.basicInfo.description = params.description;
            window.localStorage.setItem('iam-header-title-cache', this.basicInfo.name);
            this.$store.commit('setHeaderTitle', this.basicInfo.name);
          }, (e) => {
            console.warn('error');
            this.messageAdvancedError(e);
          });
      }
    }
  };
</script>
<style lang="postcss">
    .iam-template-detail-wrapper {
        position: relative;
        min-height: calc(100vh - 145px);
        .basic-info-wrapper {
            .content {
                position: relative;
                top: -6px;
            }
        }
        .edit-action {
            font-size: 12px;
        }
    }
</style>

<style lang="postcss" scoped>
.edit-action {
    margin-bottom: 13px;
}
</style>
