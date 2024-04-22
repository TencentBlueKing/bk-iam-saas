<template>
  <div class="template-actions-table" v-bkloading="{ isLoading: detailLoading, opacity: 1 }">
    <div class="template-actions-table-header">
      <render-search>
        <bk-button theme="primary" @click="handleEdit(curDetailData)">
          {{ $t(`m.common['编辑']`) }}
        </bk-button>
        <bk-checkbox
          v-model="isShowAllAction"
          class="show-check-action"
          :true-value="false"
          :false-value="true"
          @change="handleShowAllAction"
        >
          {{ $t(`m.actionsTemplate['仅展示已勾选的操作']`) }}
        </bk-checkbox>
        <div slot="right">
          <bk-input
            style="width: 540px"
            v-model="actionValue"
            :placeholder="$t(`m.actionsTemplate['搜索 操作名称']`)"
            :clearable="true"
            :right-icon="'bk-icon icon-search'"
            @right-icon-click="handleTableSearch"
            @enter="handleTableSearch"
            @clear="handleClear"
          />
        </div>
      </render-search>
    </div>
    <div class="template-actions-table-content">
      <RenderAction v-if="isShowAction" mode="detail" :actions="basicInfo.actions" />
      <ExceptionEmpty
        v-else
        :type="emptyData.type"
        :empty-text="emptyData.text"
        :tip-text="emptyData.tip"
        :tip-type="emptyData.tipType"
        @on-clear="handleClear"
      />
    </div>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { formatCodeData } from '@/common/util';
  import RenderAction from '@/views/actions-template/components/render-action';
  export default {
    components: {
      RenderAction
    },
    props: {
      curDetailData: {
        type: Object,
        default: () => {
          return {};
        }
      }
    },
    data () {
      return {
        detailLoading: false,
        isShowAllAction: true,
        actionValue: '',
        basicInfo: {
          actions: []
        },
        basicInfoBack: {
          actions: []
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        defaultCheckedActions: []
      };
    },
    computed: {
      isShowAction () {
        if (this.basicInfo.actions.length) {
          return this.basicInfo.actions.some((item) =>
            item.actions.length > 0
            || item.sub_groups.some((v) => v.actions.length > 0 || v.sub_groups.length > 0)
          );
        }
        return false;
      }
    },
    methods: {
      async fetchDetailInfo () {
        this.detailLoading = true;
        try {
          const { id } = this.curDetailData;
          const { code, data } = await this.$store.dispatch('permTemplate/getTemplateDetail', { id, grouping: true });
          const result = {
            ...data,
            ...{
              system_name: data.system.name,
              system_id: data.system.id,
              actions: data.actions || []
            }
          };
          this.basicInfo = Object.assign({}, result);
          this.basicInfoBack = cloneDeep(this.basicInfo);
          this.emptyData = formatCodeData(code, this.emptyData, result.actions.length === 0);
          if (this.basicInfo.actions.length) {
            this.handleActionData();
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.detailLoading = false;
        }
      },

      handleActionData (keyword = '') {
        // 获取actions和sub_groups所有数据，并根据单双行渲染不同背景颜色
        let colorIndex = 0;
        this.basicInfo.actions.forEach((item) => {
          this.$set(item, 'expanded', true);
          let count = 0;
          let allCount = 0;
          let deleteCount = 0;
          if (!item.actions) {
            this.$set(item, 'actions', []);
          }
          if (!item.sub_groups) {
            this.$set(item, 'sub_groups', []);
          }
          if (!this.isShowAllAction) {
            item.actions = item.actions.filter((v) => ['checked', 'readonly', 'delete'].includes(v.tag));
          }
          if (keyword) {
            item.actions = item.actions.filter((v) => v.name.indexOf(keyword) > -1);
          }
          if (item.actions.length === 1 || !item.sub_groups.length) {
            this.$set(item, 'bgColor', colorIndex % 2 === 0 ? '#f7f9fc' : '#ffffff');
            colorIndex++;
          }
          item.actions.forEach((act) => {
            this.$set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
            this.$set(act, 'disabled', act.tag === 'readonly');
            if (item.actions.length > 1 && item.sub_groups.length > 0) {
              this.$set(act, 'bgColor', colorIndex % 2 === 0 ? '#ffffff' : '#f7f9fc');
              colorIndex++;
            }
            if (act.checked) {
              ++count;
              this.defaultCheckedActions.push(act.id);
            }
            if (act.tag === 'delete') {
              ++deleteCount;
            }
            ++allCount;
          });
          item.sub_groups.forEach((sub) => {
            this.$set(sub, 'expanded', false);
            this.$set(sub, 'actionsAllChecked', false);
            this.$set(sub, 'bgColor', colorIndex % 2 === 0 ? '#f7f9fc' : '#ffffff');
            colorIndex++;
            if (!sub.actions) {
              this.$set(sub, 'actions', []);
            }
            if (!this.isShowAllAction) {
              sub.actions = sub.actions.filter((v) => ['checked', 'readonly', 'delete'].includes(v.tag));
            }
            if (keyword) {
              sub.actions = sub.actions.filter((v) => v.name.indexOf(keyword) > -1);
            }
            sub.actions.forEach((act) => {
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
      },

      handleShowAllAction () {
        this.handleRefreshAction();
      },

      handleTableSearch () {
        this.emptyData.tipType = 'search';
        this.handleRefreshAction(this.actionValue);
        console.log(this.basicInfo.actions, this.isShowAction);
        if (!this.isShowAction) {
          this.emptyData = formatCodeData(0, this.emptyData, true);
        }
      },

      handleClear () {
        this.emptyData.tipType = '';
        this.actionValue = '';
        this.handleRefreshAction('');
      },

      handleRefreshAction (keyword = '') {
        this.basicInfo = cloneDeep(this.basicInfoBack);
        this.handleActionData(keyword);
      },

      handleEdit ({ id, system }) {
        this.$router.push({
          name: 'actionsTemplateEdit',
          params: {
            id,
            systemId: system.id
          }
        });
      }
    }
  };
</script>
<style lang="postcss" scoped>
.template-actions-table {
  padding: 0 24px;
  &-header {
    /deep/ .show-check-action {
      margin-left: 12px;
      .bk-checkbox-text {
        font-size: 12px;
      }
    }
  }
  &-content {
    margin-top: 16px;
  }
}
</style>
