<template>
  <div
    class="resource-perm-manage-instance-table-wrapper"
    v-bkloading="{ isLoading, opacity: 1 }"
  >
    <bk-table
      v-if="!isLoading"
      :data="tableList"
      :ext-cls="!isEdit ? 'is-detail-view' : ''"
      :border="false"
      :header-border="false"
      :outer-border="false"
      :cell-class-name="getCellClass"
      :span-method="handleSpanMethod"
    >
      <bk-table-column :resizable="false" :label="$t(`m.common['操作']`)" :min-width="300">
        <template slot-scope="{ row }">
          <span class="action-name">{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" :min-width="450">
        <template slot-scope="{ row, $index }">
          <template v-if="!isEdit">
            <template v-if="!row.isEmpty">
              <div v-for="_ in row.resource_groups" :key="_.id">
                <p class="related-resource-item"
                  v-for="item in _.related_resource_types"
                  :key="item.type">
                  <render-resource-popover
                    :key="item.type"
                    :data="item.condition"
                    :value="`${item.name}: ${item.value}`"
                    :max-width="450"
                    @on-view="handleViewResource(row)"
                  />
                </p>
              </div>
            </template>
            <template v-else>
              {{ $t(`m.common['无需关联实例']`) }}
            </template>
          </template>
          <template v-else>
            <div class="relation-content-wrapper">
              <template v-if="!row.isEmpty">
                <div v-for="(_, groIndex) in row.resource_groups" :key="_.id">
                  <div class="relation-content-item"
                    v-for="(content, contentIndex) in _.related_resource_types"
                    :key="contentIndex">
                    <div class="content-name">
                      {{ content.name }}
                      <template v-if="row.isShowRelatedText && _.id">
                        <div style="display: inline-block; color: #979ba5;">
                          ({{ $t(`m.info['已帮您自动勾选依赖操作需要的实例']`) }})
                        </div>
                      </template>
                    </div>
                    <div class="content">
                      <render-condition
                        data-test-id="group_input_resourceInstanceCondition"
                        :ref="`condition_${$index}_${contentIndex}_ref`"
                        :value="content.value"
                        :is-empty="content.empty"
                        :can-view="row.canView"
                        :params="curCopyParams"
                        :can-paste="content.canPaste"
                        :is-error="content.isError"
                        @on-view="handlerOnView(row, content, contentIndex, groIndex)"
                        @on-restore="handlerOnRestore(content)"
                        @on-copy="handlerOnCopy(content, $index, contentIndex, row)"
                        @on-paste="handlerOnPaste(...arguments, content, $index, contentIndex)"
                        @on-batch-paste="handlerOnBatchPaste(...arguments, content, $index, contentIndex)"
                        @on-click="showResourceInstance(row, $index, content, contentIndex, groIndex)" />
                      <p class="error-tips" v-if="isShowErrorTips">{{ $t(`m.info['请选择资源实例']`) }}</p>
                    </div>
                  </div>
                </div>
              </template>
              <template v-else>
                {{ $t(`m.common['无需关联实例']`) }}
              </template>
            </div>
          </template>
        </template>
      </bk-table-column>
      <template v-if="isCustomActionButton">
        <bk-table-column
          :resizable="true"
          :label="$t(`m.common['操作-table']`)"
          :width="formateOperateWidth"
        >
          <template slot-scope="{ row }">
            <bk-button
              v-if="isShowDetailAction"
              type="primary"
              style="margin-right: 8px;"
              text
              :disabled="row.isEmpty"
              :title="row.isEmpty ? $t(`m.userGroupDetail['暂无关联实例']`) : ''"
              @click.stop="handleViewResource(row)"
            >
              {{ $t(`m.userGroupDetail['查看实例权限']`) }}
            </bk-button>
            <bk-button
              v-if="isShowDeleteAction"
              type="primary"
              text
              @click.stop="handleShowDelDialog(row)"
            >
              {{ $t(`m.userGroupDetail['删除操作权限']`) }}
            </bk-button>
          </template>
        </bk-table-column>
      </template>
      <template slot="empty">
        <ExceptionEmpty />
      </template>
    </bk-table>

    <delete-action-dialog
      :show.sync="isShowDeleteDialog"
      :title="delActionDialogTitle"
      :tip="delActionDialogTip"
      :name="currentActionName"
      :related-action-list="delActionList"
      @on-after-leave="handleAfterDeleteLeave"
      @on-cancel="handleCancelDelete"
      @on-submit="handleDelete"
    />
  </div>
</template>

<script>
  import { bus } from '@/common/bus';
  import { mapGetters } from 'vuex';
  import { cloneDeep, uniqWith, isEqual } from 'lodash';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import DeleteActionDialog from '@/views/group/components/delete-related-action-dialog.vue';
  export default {
    components: {
      RenderResourcePopover,
      DeleteActionDialog
    },
    props: {
      list: {
        type: Array,
        default: () => []
      },
      originalList: {
        type: Array,
        default: () => []
      },
      remoteAction: {
        type: Array,
        default: () => []
      },
      systemId: {
        type: String,
        default: ''
      },
      templateId: {
        type: [String, Number],
        default: ''
      },
      isEdit: {
        type: Boolean,
        default: false
      },
      // create，detail
      mode: {
        type: String,
        default: 'create'
      },
      isCustom: {
        type: Boolean,
        default: false
      },
      // type: action，view
      type: {
        type: String,
        default: 'action'
      },
      groupId: {
        type: [String, Number],
        default: ''
      },
      authorization: {
        type: Object,
        default: () => {
          return {};
        }
      },
      isShowErrorTips: {
        type: Boolean,
        default: false
      },
      isAllExpanded: {
        type: Boolean,
        default: false
      },
      isGroup: {
        type: Boolean,
        default: false
      },
      externalDelete: {
        type: Boolean,
        default: false
      },
      linearActionList: {
        type: Array,
        default: () => []
      },
      // 单独处理需要自定义操作按钮的页面
      isCustomActionButton: {
        type: Boolean,
        default: false
      },
      isShowDetailAction: {
        type: Boolean,
        default: true
      },
      isShowDeleteAction: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        tableList: [],
        isShowResourceInstanceSideslider: false,
        resourceInstanceSideSliderTitle: '',
        // 查询参数
        params: {},
        disabled: false,
        curIndex: -1,
        curResIndex: -1,
        curGroupIndex: -1,
        isShowPreviewDialog: false,
        previewDialogTitle: '',
        previewResourceParams: {},
        curCopyData: ['none'],
        curCopyType: '',
        curId: '',
        isLoading: false,
        curScopeAction: {},
        isShowAggregateSideslider: false,
        aggregateResourceParams: {},
        aggregateIndex: -1,
        aggregateValue: [],
        // 当前复制的数据形态: normal: 普通; aggregate: 聚合后
        curCopyMode: 'normal',
        curAggregateResourceType: {},
        defaultSelectList: [],
        sidesliderTitle: '',
        isShowSideslider: false,
        previewData: [],
        curCopyParams: {},
        sliderLoading: false,
        isShowDeleteDialog: false,
        showIcon: false,
        curCopyNoLimited: false,
        footerPosition: 'center',
        newRow: '',
        role: '',
        selectedIndex: 0,
        instanceKey: '',
        curCopyDataId: '',
        emptyResourceGroupsList: [],
        delActionList: [],
        delPathList: [],
        policyIdList: [],
        customData: [],
        curInstancePaths: [],
        currentActionName: '',
        delActionDialogTitle: '',
        delActionDialogTip: '',
        isAggregateEmptyMessage: false,
        resourceSliderWidth: Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7)
      };
    },
    computed: {
      ...mapGetters(['user']),
      isSuperManager () {
          return this.user.role.type === 'super_manager';
      },
      sliderWidth () {
          return this.mode === 'detail' ? 960 : 640;
      },
      condition () {
          if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
              return [];
          }
          const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
              .related_resource_types[this.curResIndex];
          if (!curData) {
              return [];
          }
          return cloneDeep(curData.condition);
      },
      originalCondition () {
          if (this.curIndex === -1
              || this.curResIndex === -1
              || this.curGroupIndex === -1
              || this.originalList.length < 1) {
              return [];
          }
          const curId = this.tableList[this.curIndex].id;
          const curType = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
              .related_resource_types[this.curResIndex].type;
          if (!this.originalList.some(item => item.id === curId)) {
              return [];
          }
          const curResTypeData = this.originalList.find(item => item.id === curId);
          if (!curResTypeData.resource_groups[this.curGroupIndex]
              .related_resource_types.some(item => item.type === curType)) {
              return [];
          }
          const curData = (curResTypeData.resource_groups[this.curGroupIndex]
              .related_resource_types || []).find(item => item.type === curType);
          if (!curData) {
              return [];
          }
          return cloneDeep(curData.condition);
      },
      curDisabled () {
          if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
              return false;
          }
          const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
              .related_resource_types[this.curResIndex];
          return curData.isDefaultLimit;
      },
      curFlag () {
          if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
              return 'add';
          }
          const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
              .related_resource_types[this.curResIndex];
          return curData.flag;
      },
      curSelectionMode () {
          if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
              return 'all';
          }
          const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
              .related_resource_types[this.curResIndex];
          return curData.selectionMode;
      },
      isShowPreview () {
          if (this.curIndex === -1) {
              return false;
          }
          return this.tableList[this.curIndex].policy_id !== '';
      },
      isShowView () {
          return (payload) => {
              return !payload.isEmpty;
          };
      },
      isCreateMode () {
          return this.mode === 'create';
      },
      isUserGroupDetail () {
          return this.$route.name === 'userGroupDetail';
      },
      curSelectionCondition () {
          if (this.curIndex === -1 || this.isSuperManager) {
              return [];
          }
          const curSelectionCondition = this.tableList[this.curIndex].conditionIds;
          return curSelectionCondition;
      },
      // 处理无限制和聚合后多个tab数据结构不兼容情况
      formatDisplayValue () {
        return (payload) => {
          const { isNoLimited, empty, value, aggregateResourceType, selectedIndex } = payload;
          if (value && aggregateResourceType[selectedIndex]) {
            let displayValue = aggregateResourceType[selectedIndex].displayValue;
            if (isNoLimited || empty) {
              displayValue = value;
            }
            return displayValue;
          }
        };
      },
      formateOperateWidth () {
        const langMap = {
          true: () => {
            if (this.isShowDeleteAction && this.isShowDetailAction) {
              return 200;
            }
            return 130;
          },
          false: () => {
            if (this.isShowDeleteAction && this.isShowDetailAction) {
              return 400;
            }
            return 192;
          }
        };
        return langMap[this.curLanguageIsCn]();
      }
    },
    watch: {
      list: {
        handler (value) {
          value = uniqWith(value, isEqual); // 去重
          if (this.isAllExpanded) {
            this.tableList.splice(0, this.tableList.length, ...value);
          } else {
            const customData = value.filter(e => e.mode === 'custom');
            const templateData = value.filter(e => e.mode === 'template');
            this.tableList.splice(0, this.tableList.length, ...customData, ...templateData);
          }
        },
        immediate: true
      },
      systemId: {
        handler (value) {
          if (value !== '') {
            this.curCopyType = '';
            this.curCopyData = ['none'];
            this.curIndex = -1;
            this.curResIndex = -1;
            this.curGroupIndex = -1;
            this.aggregateResourceParams = {};
            this.aggregateIndex = -1;
            this.aggregateValue = [];
            this.curCopyMode = 'normal';
            this.curAggregateResourceType = {};
            this.defaultSelectList = [];
          }
        },
        immediate: true
      }
    },
    mounted () {
      window.addEventListener('resize', (this.formatFormItemWidth));
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
      });
    },
    methods: {
      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 0) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      formatFormItemWidth () {
        this.resourceSliderWidth = Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7);
      },

      handleSpanMethod ({ row, column, rowIndex, columnIndex }) {
        return {
          rowspan: 1,
          colspan: 1
        };
      },

      // 处理操作和资源实例删除
      handleDelActionOrInstance (payload, type) {
        const { id, mode, name } = payload;
        let delRelatedActions = [];
        this.delActionList = [];
        this.currentActionName = name;
        const isCustom = ['custom'].includes(mode);
        const policyIdList = this.tableList.map((item) => item.id);
        const linearActionList = this.linearActionList.filter((item) =>
          policyIdList.includes(item.id)
        );
        const curAction = linearActionList.find((item) => item.id === id);
        const hasRelatedActions
          = curAction && curAction.related_actions && curAction.related_actions.length;
        linearActionList.forEach((item) => {
          // 如果这里过滤自己还能在其他数据找到相同的related_actions，就代表有其他数据也关联了相同的操作
          if (
            isCustom
            && hasRelatedActions
            && item.related_actions
            && item.related_actions.length
            && item.id !== id
          ) {
            delRelatedActions = item.related_actions.filter((v) =>
              curAction.related_actions.includes(v)
            );
          }
          if (isCustom && item.related_actions && item.related_actions.includes(id)) {
            this.delActionList.push(item);
          }
        });
        let ids = [payload.policy_id];
        if (this.delActionList.length) {
          const list = this.tableList.filter((item) =>
            this.delActionList.map((action) => action.id).includes(item.id)
          );
          ids = [payload.policy_id].concat(list.map((v) => v.policy_id));
        }
        const typeMap = {
          action: () => {
            if (isCustom && !delRelatedActions.length && hasRelatedActions) {
              const list = [...this.tableList].filter((v) =>
                curAction.related_actions.includes(v.id)
              );
              if (list.length) {
                ids = ids.concat(list.map((v) => v.policy_id));
              }
            }
            this.delActionDialogTitle = this.$t(`m.dialog['确认删除内容？']`, {
              value: this.$t(`m.dialog['删除操作权限']`)
            });
            this.delActionDialogTip = this.$t(`m.info['删除依赖操作产生的影响']`, {
              value: name
            });
            this.newRow = Object.assign(payload, { ids });
            this.isShowDeleteDialog = true;
          },
          instance: () => {
            const scopeAction = this.authorization[this.params.system_id] || [];
            this.curScopeAction = cloneDeep(scopeAction.find((item) => item.id === id));
            this.policyIdList = cloneDeep(ids);
            this.resourceInstanceSideSliderTitle = this.$t(
              `m.info['关联侧边栏操作的资源实例']`,
              { value: `${this.$t(`m.common['【']`)}${name}${this.$t(`m.common['】']`)}` }
            );
            window.changeAlert = 'iamSidesider';
            this.isShowResourceInstanceSideslider = true;
          }
        };
        typeMap[type]();
      },

      handleShowDelDialog (row) {
        this.handleDelActionOrInstance(row, 'action');
      },

      handleDelete () {
        this.$emit('on-delete', this.newRow);
      },

      showResourceInstance (data, index, resItem, resIndex, groupIndex) {
        window.changeDialog = true;
        this.params = {
          system_id: this.systemId,
          action_id: data.id,
          resource_type_system: resItem.system_id,
          resource_type_id: resItem.type
        };
        if (this.isCreateMode) {
          this.params.system_id = data.detail.system.id;
        }
        this.curIndex = index;
        this.curResIndex = resIndex;
        this.curGroupIndex = groupIndex;
        if (this.customData.length && ['userGroupDetail'].includes(this.$route.name)) {
          const customData = this.customData.find(
            (item) => item.policy_id === data.policy_id
          );
          if (customData) {
            const curCondition = customData.resource_groups[this.curGroupIndex]
              .related_resource_types[this.curResIndex].conditionBackup;
            // conditionBackup代表的是接口返回的缓存数据，处理新增未提交的资源实例删
            const curPaths
              = curCondition.length
                && curCondition.reduce((prev, next) => {
                  prev.push(
                    ...next.instance.map((v) => {
                      const paths = { ...v.path, ...next.path };
                      delete paths.instance;
                      return paths;
                    })
                  );
                  return prev;
                }, []);
            this.curInstancePaths = [...curPaths];
          }
        }
        this.handleDelActionOrInstance(data, 'instance');
      },

      handleViewResource (payload) {
        this.curId = payload.id;
        const params = [];
        if (payload.resource_groups.length > 0) {
          payload.resource_groups.forEach(groupItem => {
            if (groupItem.related_resource_types.length > 0) {
              groupItem.related_resource_types.forEach(item => {
                const { name, type, condition } = item;
                params.push({
                  name: type,
                  label: this.$t(`m.info['tab操作实例']`, { value: name }),
                  tabType: 'resource',
                  data: condition
                });
              });
            }
          });
        }
        this.previewData = cloneDeep(params);
        this.sidesliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, {
          value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}`
        });
        bus.$emit('on-drawer-side', { width: 1160 });
        this.isShowSideslider = true;
      },

      handleAfterDeleteLeave () {
        this.currentActionName = '';
        this.delActionList = [];
        this.policyIdList = [];
      },

      handleCancelDelete () {
        this.isShowDeleteDialog = false;
      },

      handleOnInit (payload) {
        this.disabled = !payload;
      },

      handlerOnView (payload, item, itemIndex) {
        const { system_id, type, name } = item;
        const condition = [];
        item.condition.forEach(item => {
          const { id, attribute, instance } = item;
          condition.push({
            id,
            attributes: attribute ? attribute.filter(item => item.values.length > 0) : [],
            instances: instance ? instance.filter(item => item.path.length > 0) : []
          });
        });
        this.previewResourceParams = {
          id: this.templateId,
          action_id: payload.id,
          related_resource_type: {
            system_id,
            type,
            name,
            condition: condition.filter(item => item.attributes.length > 0 || item.instances.length > 0)
          },
          reverse: true,
          groupId: this.groupId,
          policy_id: payload.policy_id,
          resource_group_id: payload.resource_groups[this.curGroupIndex].id,
          isTemplate: payload.isTemplate
        };
        this.previewDialogTitle = this.$t(`m.info['操作侧边栏操作的资源实例差异对比']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        if (!this.previewResourceParams.id) {
          this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: this.$t(`m.info['无资源ID，无法预览']`)
          });
          return;
        }
        this.isShowPreviewDialog = true;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.resource-perm-manage-instance-table-wrapper {
  /deep/ .bk-table {
    width: 100%;
    border: none;
    font-size: 12px;
    .relation-content-wrapper,
    .conditions-wrapper {
      height: 100%;
      padding: 17px 0;
      color: #63656e;
      .resource-type-name {
        display: block;
        margin-bottom: 9px;
      }
    }
    .remove-icon {
      position: absolute;
      right: 2px;
      top: 2px;
      font-size: 20px;
      cursor: pointer;
      &:hover {
        color: #3a84ff;
      }
    }
    .relation-content-item {
      margin-top: 17px;
      &:first-child {
        margin-top: 0;
      }
      &.reset-margin-top {
        margin-top: 10px;
      }
      .content-name {
        margin-bottom: 9px;
      }
    }
    .action-name {
      display: inline-block;
      vertical-align: bottom;
      word-wrap: break-word;
      word-break: break-all;
    }
    &.is-detail-view {
      .bk-table-header-wrapper {
        th {
          &:first-child {
            .cell {
              padding-left: 48px;
            }
          }
        }
      }
      .bk-table-body-wrapper {
        .cell {
          .view-icon {
            display: none;
            position: absolute;
            top: 50%;
            right: 30px;
            transform: translate(0, -50%);
            font-size: 18px;
            cursor: pointer;
          }
          &:hover {
            .view-icon {
              display: inline-block;
              color: #3a84ff;
            }
          }
        }
      }
      .bk-table-body {
        tr {
          &:hover {
            background-color: transparent;
            & > td {
              background-color: transparent;
            }
          }
        }
        td:first-child .cell,
        th:first-child .cell {
          padding-left: 48px;
        }
      }
    }
  }
}
</style>
