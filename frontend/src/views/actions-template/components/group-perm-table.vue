<template>
  <div class="group-perm-table-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
    <bk-table
      v-if="!isLoading"
      :data="tableList"
      :ext-cls="!isEdit ? 'is-detail-view' : ''"
      :col-border="true"
      :cell-class-name="getCellClass"
    >
      <bk-table-column :resizable="false" :label="$t(`m.common['所属系统']`)" :min-width="100">
        <template slot-scope="{ row }">
          <span>{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.actionsTemplate['添加来源']`)" :min-width="130" prop="source_type">
        <template slot-scope="{ row }">
          <div
            v-for="(temp, tempIndex) of row.templates"
            :key="tempIndex"
            :class="[
              'child-table-content',
              'add-source-content',
              { 'set-border': isSetBorder(temp, tempIndex, row) },
              { 'is-search-no-border': isSearchNoBorder(temp, tempIndex, row) }
            ]"
          >
            <div
              v-for="(action, actionIndex) in temp.tableData"
              :key="action.id"
              :class="[
                'add-source-content-item',
                { 'multiple-temp-item': row.templates.length > 1 },
                { 'multiple-temp-action-item': row.templates.length > 1 && temp.tableData.length > 1 }
              ]"
            >
              <div class="source-name" v-show="isShowSource(temp, actionIndex)">
                <Icon type="action-temp" class="action-icon" />
                <div class="single-hide name" v-bk-tooltips="{ content: temp.name }">
                  {{ temp.name }}
                </div>
              </div>
            </div>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.common['操作']`)" :min-width="160" prop="action_name">
        <template slot-scope="{ row }">
          <div
            v-for="(temp, tempIndex) of row.templates"
            :key="tempIndex"
            class="child-table-content"
          >
            <div
              v-for="action in temp.tableData"
              :key="action.id"
              :class="[
                'actions-name',
                { 'set-border': isSetBorder(temp, tempIndex, row) },
                { 'is-search-no-border': isSearchNoBorder(temp, tempIndex, row) }
              ]"
            >
              <span class="single-hide name">{{ action.name }}</span>
            </div>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" :min-width="260" prop="resource_instance">
        <template slot-scope="{ row }">
          <div
            v-for="(temp, tempIndex) in row.templates"
            :key="tempIndex"
            class="child-table-content"
          >
            <div
              v-for="action of temp.tableData"
              :key="action.id"
              :class="[
                'flex-between',
                'resource-instance-name',
                { 'set-border': isSetBorder(temp, tempIndex, row) },
                { 'is-search-no-border': isSearchNoBorder(temp, tempIndex, row) }
              ]"
            >
              <div class="instance-select-content">
                <template v-if="action.resource_groups && action.resource_groups.length > 0">
                  <div v-for="group in action.resource_groups" :key="group.id">
                    <div
                      class="flex-between related-resource-item"
                      v-for="(related, relatedIndex) in group.related_resource_types"
                      :key="related.type"
                    >
                      <template v-if="relatedIndex < 1">
                        <div class="instance-label">
                          <span>{{ $t(`m.common['已选择']`) }}</span>
                          <span class="instance-count">{{ formatInstanceCount(related, group) || 0 }}</span>
                          <span>{{ $t(`m.common['个任务实例']`) }}</span>
                        </div>
                        <div class="instance-operate-icon">
                          <Icon
                            v-if="isShowView(action)"
                            v-bk-tooltips="{ content: $t(`m.common['详情']`) }"
                            type="detail"
                            class="view-icon"
                            @click.stop="handleViewResource(action)"
                          />
                          <Icon
                            v-bk-tooltips="{ content: $t(`m.common['复制']`) }"
                            type="copy"
                            class="copy-icon"
                            @click.stop="handleCopyInstance(related, relatedIndex, actionIndex, action)"
                          />
                        </div>
                      </template>
                    </div>
                  </div>
                </template>
                <div v-else>{{ $t(`m.common['无需关联实例']`) }}</div>
              </div>
            </div>
          </div>
        </template>
      </bk-table-column>
      <template slot="empty">
        <ExceptionEmpty />
      </template>
    </bk-table>

    <preview-resource-dialog
      :show="isShowPreviewDialog"
      :title="previewDialogTitle"
      :params="previewResourceParams"
      @on-after-leave="handlePreviewDialogClose"
    />
  
  </div>
</template>
  
  <script>
  import { mapGetters } from 'vuex';
  import { cloneDeep, uniqWith, isEqual } from 'lodash';
  import { bus } from '@/common/bus';
  import PreviewResourceDialog from '@/views/group/components/preview-resource-dialog';
  export default {
    provide: function () {
      return {
        getResourceSliderWidth: () => this.resourceSliderWidth
      };
    },
    components: {
      PreviewResourceDialog
    },
    props: {
      isLoading: {
        type: Boolean
      },
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
      mode: {
        type: String,
        default: 'create'
      },
      isCustom: {
        type: Boolean,
        default: false
      },
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
      isSearch: {
        type: Boolean
      }
    },
    data () {
      return {
        tableList: [],
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
        curScopeAction: {},
        isShowAggregateSideslider: false,
        aggregateResourceParams: {},
        aggregateIndex: -1,
        aggregateValue: [],
        // 当前复制的数据形态: normal: 普通; aggregate: 聚合后
        curCopyMode: 'normal',
        curAggregateResourceType: {},
        defaultSelectList: [],
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
        curCopyKey: '',
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
        return 960;
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
      curSelectionCondition () {
        if (this.curIndex === -1 || this.isSuperManager) {
            return [];
        }
        const curSelectionCondition = this.tableList[this.curIndex].conditionIds;
        return curSelectionCondition;
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
      isShowSource () {
        return (payload, index) => {
          return (Math.floor(payload.tableData.length / 2)) === index;
        };
      },
      isShowDeleteAction () {
        return ['detail'].includes(this.mode) && this.isCustom && this.type !== 'view' && !this.externalDelete;
      },
      isNoBorder () {
        return (payload) => {
          const curIndex = payload.findLastIndex((v) => v.tableData.length > 0 && v.tableData.length < 2);
          return curIndex > -1;
        };
      },
      isSetBorder () {
        return (temp, tempIndex, row) => {
          return !(tempIndex === row.templates.length - 1
          && this.isNoBorder(row.templates)) && temp.tableData.length > 0;
        };
      },
      isSearchNoBorder () {
        return (temp, tempIndex, row) => {
          return this.isSearch && temp.tableData.length > 0
            && (row.templates.findLastIndex((v) => v.tableData.length > 0) === tempIndex);
        };
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
      formatInstanceCount () {
        return (payload, related) => {
          let curPaths = [];
          if (related.related_resource_types && related.related_resource_types.length > 1) {
            const list = related.related_resource_types.map((v) => {
              if (v.condition.length) {
                const { instance, instances } = v.condition[0];
                const list = instance || instances;
                curPaths = list.reduce((prev, next) => {
                  prev.push(
                    ...next.path.map(v => {
                      const paths = { ...v, ...next };
                      delete paths.instance;
                      delete paths.path;
                      return paths[0];
                    })
                  );
                  return prev;
                }, []);
                return curPaths.length;
              }
            });
            const count = list.reduce((prev, next) => prev + next, 0);
            return count;
          } else {
            if (payload.condition.length) {
              const { instance, instances } = payload.condition[0];
              const list = instance || instances;
              curPaths = list.reduce((prev, next) => {
                prev.push(
                  ...next.path.map(v => {
                    const paths = { ...v, ...next };
                    delete paths.instance;
                    delete paths.path;
                    return paths[0];
                  })
                );
                return prev;
              }, []);
              return curPaths.length;
            }
          }
        };
      }
    },
    watch: {
      list: {
        handler (value) {
          this.tableList = uniqWith(value, isEqual);
        },
        immediate: true
      },
      systemId: {
        handler (value) {
          if (value) {
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
      formatFormItemWidth () {
        this.resourceSliderWidth = Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7);
      },

      handleViewResource (payload) {
        this.curId = payload.id;
        const params = [];
        const sideSliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, {
          value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}`
        });
        if (payload.resource_groups.length > 0) {
          payload.resource_groups.forEach((groupItem) => {
            if (groupItem.related_resource_types.length > 0) {
              groupItem.related_resource_types.forEach((item) => {
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
        bus.$emit('on-drawer-side', { isShow: true, width: 640, title: sideSliderTitle, previewData: this.previewData });
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        const columnMap = {
          source_type: () => {
            return 'group-perm-table-source';
          },
          action_name: () => {
            return 'group-perm-table-action';
          },
          resource_instance: () => {
            return 'group-perm-table-resource-instance';
          }
        };
        if (columnMap[column.property]) {
          return columnMap[column.property]();
        }
        return '';
      },

      handleLimitChange () {
        window.changeDialog = true;
        const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
          .related_resource_types[this.curResIndex];
        curData.isChange = true;
      },

      handleResourcePreview () {
        // debugger
        window.changeDialog = true;
        // eslint-disable-next-line max-len
        const { system_id, type, name } = this.tableList[this.curIndex].resource_groups[this.curGroupIndex].related_resource_types[this.curResIndex];
        const condition = [];
        const conditionData = this.$refs.renderResourceRef.handleGetPreviewValue();
        conditionData.forEach(item => {
          const { id, attribute, instance } = item;
          condition.push({
            id,
            attributes: attribute ? attribute.filter(item => item.values.length > 0) : [],
            instances: instance ? instance.filter(item => item.path.length > 0) : []
          });
        });
        this.previewResourceParams = {
          id: this.templateId,
          action_id: this.tableList[this.curIndex].id,
          related_resource_type: {
            system_id,
            type,
            name,
            condition: condition.filter(item => item.attributes.length > 0 || item.instances.length > 0)
          },
          reverse: true,
          groupId: this.groupId,
          policy_id: this.tableList[this.curIndex].policy_id,
          isTemplate: this.tableList[this.curIndex].isTemplate,
          resource_group_id: this.tableList[this.curIndex].resource_groups[this.curGroupIndex].id,
          isNotLimit: conditionData.length === 0
        };
        this.previewDialogTitle = this.$t(`m.info['操作侧边栏操作的资源实例差异对比']`, { value: `${this.$t(`m.common['【']`)}${this.tableList[this.curIndex].name}${this.$t(`m.common['】']`)}` });
        this.isShowPreviewDialog = true;
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
          this.messageWarn(this.$t(`m.info['无资源ID，无法预览']`), 3000);
          return;
        }
        this.isShowPreviewDialog = true;
      },

      handleCopyInstance (sub, subIndex, index, payload) {
        this.curCopyMode = 'normal';
        this.curCopyKey = `${sub.system_id}${sub.type}`;
        this.curCopyData = cloneDeep(sub.condition);
        this.curCopyParams = this.getBatchCopyParams(payload, sub);
        bus.$emit('on-group-perm-instance-copy', this.curCopyParams);
        this.messageSuccess(this.$t(`m.info['实例复制']`), 3000);
      },

      getBatchCopyParams (payload, content) {
        const actions = [];
        actions.unshift({
          system_id: payload.detail.system.id,
          id: payload.id
        });
        return {
          resource_type: {
            system_id: content.system_id,
            type: content.type,
            condition: content.condition.map(item => {
              return {
                id: item.id,
                instances: item.instance || [],
                attributes: item.attribute || []
              };
            })
          },
          actions
        };
      },
     
      handlePreviewDialogClose () {
        this.previewDialogTitle = '';
        this.previewResourceParams = {};
        this.isShowPreviewDialog = false;
      }
    }
  };
  </script>
  
  <style lang="postcss" scoped>
  .group-perm-table-wrapper {
    /deep/ .bk-table {
      width: 100%;
      border-right: none;
      border-bottom: none;
      font-size: 12px;
      .cell {
        padding-left: 12px;
        padding-right: 12px;
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
      }
      .group-perm-table-action,
      .group-perm-table-resource-instance {
        .cell {
          width: 100%;
          padding: 0;
          display: block;
        }
        .child-table-content {
          /* tr {
            td {
              border-right: 0;
              border-bottom: 0;
            }
            &:last-child {
              td {
                border-bottom: 0;
                &.is-last {
                    .actions-name,
                    .resource-instance-name {
                      &:last-child {
                        border-bottom: 0;
                      }
                  }
                }
              }
            }
          } */
          .actions-name,
          .resource-instance-name {
            padding: 13px 12px 14px 12px;
            &.set-border {
              border-bottom: 1px solid #dcdee5;
            }
            &.is-search-no-border {
              border-bottom: 0;
            }
          }
          .view-icon,
          .copy-icon {
            color: #3A84FF;
            font-size: 16px;
            cursor: pointer;
          }
          .copy-icon {
            margin-left: 15px;
          }
          .resource-instance-name {
            .instance-select-content {
              width: 100%;
              .related-resource-item {
                .instance-label {
                  max-width: calc(100% - 80px);
                  line-height: 1;
                }
              }
            }
          }
          &:last-child {
            .actions-name,
            .resource-instance-name {
              &:last-child {
                border-bottom: 0;
              }
            }
          }
        }
      }
      .group-perm-table-source {
        .cell {
          width: 100%;
          padding: 0;
          display: block;
          .add-source-content {
            &-item {
              .source-name {
                padding: 0 12px;
                display: flex;
                align-items: center;
                line-height: 44px;
                .action-icon {
                  color: #979BA5;
                  margin-right: 4px;
                }
              }
              &.multiple-temp-item {
                min-height: 44px;
              }
              &.multiple-temp-action-item {
                .source-name {
                  transform: translateY(-22px);
                  margin-top: -1px;
                }
              }
            }
            &.set-border {
              border-bottom: 1px solid #dcdee5;
              &:last-child {
                border-bottom: 0;
              }
            }
            &:last-child {
              border-bottom: 0;
              .multiple-temp-action-item {
                .source-name {
                  transform: translate(0, 0);
                }
              }
              .source-name,
              .actions-name,
              .resource-instance-name {
                border-bottom: 0;
              }
            }
            &.is-search-no-border {
              border-bottom: 0;
            }
          }
        }
      }
      .group-perm-table-resource-instance {
        .instance-count {
          color: #3A84FF;
          font-weight: 700;
        }
      }
    }
  }
  </style>
