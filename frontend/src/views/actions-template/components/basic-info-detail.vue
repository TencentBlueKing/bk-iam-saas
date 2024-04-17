<template>
  <div
    class="action-template-basic-info"
    v-bkloading="{ isLoading: detailLoading, opacity: 1 }"
  >
    <detail-layout mode="action-template-detail">
      <render-layout class="sads">
        <detail-item :label="`${$t(`m.memberTemplate['模板名称']`)}${$t(`m.common['：']`)}`">
          <div class="basic-info-value">
            <iam-edit-input
              field="name"
              :mode="formatEdit"
              :placeholder="$t(`m.memberTemplate['请输入模板名称']`)"
              :rules="rules"
              :value="basicInfo.name"
              :remote-hander="handleChangeInfo"
            />
          </div>
        </detail-item>
        <detail-item :label="`${$t(`m.memberTemplate['模板 ID']`)}${$t(`m.common['：']`)}`">
          <span class="basic-info-value">{{ basicInfo.id }}</span>
        </detail-item>
        <detail-item :label="`${$t(`m.common['创建时间']`)}${$t(`m.common['：']`)}`">
          <span class="basic-info-value">{{ basicInfo.created_time }}</span>
        </detail-item>
        <detail-item :label="`${$t(`m.memberTemplate['模板描述']`)}${$t(`m.common['：']`)}`">
          <div class="basic-info-value">
            <iam-edit-textarea
              field="description"
              width="600px"
              :mode="formatEdit"
              :placeholder="$t(`m.memberTemplate['请输入模板描述']`)"
              :max-length="255"
              :value="basicInfo.description"
              :remote-hander="handleChangeInfo"
            />
          </div>
        </detail-item>
      </render-layout>
    </detail-layout>
  </div>
</template>

<script>
  import { bus } from '@/common/bus';
  import { isEmojiCharacter } from '@/common/util';
  import RenderLayout from '@/views/group/common/render-layout';
  import DetailLayout from '@/components/detail-layout';
  import DetailItem from '@/components/detail-layout/item';
  import IamEditInput from '@/components/iam-edit/input';
  import IamEditTextarea from '@/components/iam-edit/textarea';
  export default {
    components: {
      RenderLayout,
      DetailLayout,
      DetailItem,
      IamEditInput,
      IamEditTextarea
    },
    props: {
      curDetailData: {
        type: Object
      }
    },
    data () {
      return {
        detailLoading: false,
        basicInfo: {
          name: '',
          description: '',
          systemName: '',
          systemId: '',
          actions: [],
          updatedTime: '',
          id: 0
        },
        rules: [
          {
            required: true,
            message: this.$t(`m.verify['模板名称必填, 不允许输入表情字符']`),
            trigger: 'blur',
            validator: (value) => {
              return !isEmojiCharacter(value);
            }
          }
        ],
        defaultCheckedActions: []
      };
    },
    computed: {
      formatEdit () {
        return this.curDetailData.readonly ? 'detail' : 'edit';
      }
    },
    methods: {
      async fetchDetailInfo () {
        this.detailLoading = true;
        try {
          const { id } = this.curDetailData;
          const { data } = await this.$store.dispatch('permTemplate/getTemplateDetail', { id, grouping: true });
          this.basicInfo = Object.assign({}, {
            name: data.name,
            description: data.description,
            systemName: data.system.name,
            systemId: data.system.id,
            actions: data.actions,
            updatedTime: data.updated_time,
            id
          });
          this.handleActionData();
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.detailLoading = false;
        }
      },

      handleActionData () {
        this.basicInfo.actions.forEach((item) => {
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
          });
          (item.sub_groups || []).forEach(sub => {
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
        const temps = [...this.basicInfo.actions || []];
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

      async handleChangeInfo (payload) {
        const { id, name, description } = this.basicInfo;
        const params = {
          name,
          description,
          id,
          ...payload
        };
        try {
          await this.$store.dispatch('permTemplate/updateTemplate', params);
          this.messageSuccess(this.$t(`m.info['编辑成功']`), 3000);
          const { name, description } = params;
          this.basicInfo = Object.assign(this.basicInfo, {
            name,
            description
          });
          bus.$emit('on-info-change', { id, name, description, mode: this.curDetailData.mode || '' });
        } catch (e) {
          this.messageAdvancedError(e);
        }
      }
    }
  };
</script>

<style lang="postcss" scoped>
.action-template-basic-info {
  padding-left: 40px;
  .basic-info-value {
    margin-left: 8px;
  }
  /deep/.action-template-detail {
    .iam-render-common-layout {
      .detail-label {
        min-width: 80px;
        /* text-align: right; */
      }
    }
  }
}
</style>
