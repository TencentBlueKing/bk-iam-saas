<template>
  <div class="template-resource-instance-table-wrapper">
    <div :class="[
           'iam-resource-expand'
         ]"
      @click.stop="handleExpanded">
      <div class="iam-resource-header flex-between">
        <div class="iam-resource-header-left">
          <Icon
            bk
            :type="isExpandTable ? 'down-shape' : 'right-shape'" />
          <span>{{ $t(`m.info['已添加']`) }}</span>
          <span class="number">{{ totalCount }}</span>
          <span>{{ $t(`m.common['个']`) }}{{ $t(`m.perm['操作权限']`) }}</span>
        </div>
        <div class="iam-resource-header-right">
          <bk-button
            text
            type="primary"
            size="small"
            @click.stop="handleClearAll"
          >
            {{ $t(`m.common['清空']`)}}
          </bk-button>
        </div>
      </div>
    </div>

    <template v-if="isExpandTable">
      <bk-table
        :data="tableList"
        :ext-cls="!isEdit ? 'is-detail-view' : ''"
        border
        :cell-class-name="getCellClass"
        :span-method="handleSpanMethod"
        @row-mouse-enter="handleRowMouseEnter"
        @row-mouse-leave="handleRowMouseLeave">
        <!-- eslint-disable max-len -->
        <bk-table-column :resizable="false" :label="$t(`m.common['模板名称']`)" width="180" v-if="isCreateMode">
          <template slot-scope="{ row }">
            <span>{{ !!row.isAggregate ? row.actions[0].detail.name || row.actions[0].displayName : row.displayName }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :resizable="false" :label="$t(`m.common['操作']`)" width="180">
          <template slot-scope="{ row }">
            <div v-if="!!row.isAggregate" style="padding: 10px 0;">
              <span class="action-name" :title="row.name">{{ row.name }}</span>
            </div>
            <div v-else>
              <span class="action-name" :title="row.name">{{ row.name }}</span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column :resizable="false" :label="$t(`m.common['所属系统']`)" width="180" v-if="isCreateMode">
          <template slot-scope="{ row }">
            <span>{{ !!row.isAggregate ? row.system_name : row.detail.system.name }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" min-width="450">
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
                      :value="`${item.name}：${item.value}`"
                      :max-width="380"
                      @on-view="handleViewResource(row)" />
                  </p>
                </div>
              </template>
              <template v-else>
                {{ $t(`m.common['无需关联实例']`) }}
              </template>
              <Icon
                type="detail-new"
                class="view-icon"
                :title="$t(`m.common['详情']`)"
                v-if="isShowView(row)"
                @click.stop="handleViewResource(row)" />
              <template v-if="!isUserGroupDetail ? false : true && row.showDelete">
                <Icon class="remove-icon" type="close-small" @click.stop="toHandleDelete(row)" />
              </template>
            </template>
            <template v-else>
              <div class="relation-content-wrapper" v-if="!!row.isAggregate">
                <label class="resource-type-name" v-if="row.aggregateResourceType.length === 1">{{ row.aggregateResourceType[0].name }}</label>
                <div class="bk-button-group tab-button" v-else>
                  <bk-button v-for="(item, index) in row.aggregateResourceType"
                    :key="item.id" @click="selectResourceType(row, index)"
                    :class="row.selectedIndex === index ? 'is-selected' : ''" size="small">{{item.name}}
                    <span v-if="!row.isNoLimited && row.instancesDisplayData[item.id] && row.instancesDisplayData[item.id].length">({{row.instancesDisplayData[item.id].length}})</span>
                  </bk-button>
                </div>
                <div class="content">
                  <render-condition
                    :ref="`condition_${$index}_aggregateRef`"
                    :value="formatDisplayValue(row)"
                    :is-empty="row.empty"
                    :can-view="false"
                    :can-paste="row.canPaste"
                    :is-error="row.isError"
                    @on-mouseover="handlerAggregateConditionMouseover(row)"
                    @on-mouseleave="handlerAggregateConditionMouseleave(row)"
                    @on-copy="handlerAggregateOnCopy(row, $index)"
                    @on-paste="handlerAggregateOnPaste(row)"
                    @on-batch-paste="handlerAggregateOnBatchPaste(row, $index)"
                    @on-click="showAggregateResourceInstance(row, $index)" />
                  <p class="error-tips" v-if="isShowErrorTips">{{ $t(`m.info['请选择资源实例']`) }}</p>
                </div>
              </div>
              <div class="relation-content-wrapper" v-else>
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
                          @on-mouseover="handlerConditionMouseover(content)"
                          @on-mouseleave="handlerConditionMouseleave(content)"
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
              <!-- <div class="remove-icon" @click.stop="handleRemove(row, $index)">
                                <Icon type="close-small" />
                            </div> -->
            </template>
          </template>
        </bk-table-column>
        <bk-table-column :resizable="false" width="50" align="center">
          <template slot-scope="{ row, $index }">
            <div class="relation-content-wrapper">
              <div class="remove-icon" @click.stop="handleRemove(row, $index)">
                <bk-icon
                  type="minus-circle-shape"
                  size="medium"
                  style="color: #C4C6CC;"
                />
              </div>
            </div>
          </template>
        </bk-table-column>
        <template slot="empty">
          <ExceptionEmpty />
        </template>
      </bk-table>
    </template>
        
    <bk-sideslider
      :is-show="isShowResourceInstanceSideslider"
      :title="resourceInstanceSidesliderTitle"
      :width="960"
      quick-close
      transfer
      :ext-cls="'relate-instance-sideslider'"
      @update:isShow="handleResourceCancel">
      <div slot="content" class="sideslider-content">
        <render-resource
          ref="renderResourceRef"
          :data="condition"
          :cur-selection-condition="curSelectionCondition"
          :original-data="originalCondition"
          :flag="curFlag"
          :selection-mode="curSelectionMode"
          :disabled="curDisabled"
          :params="params"
          :res-index="curResIndex"
          :cur-scope-action="curScopeAction"
          @on-limit-change="handleLimitChange"
          @on-init="handleOnInit" />
      </div>
      <div slot="footer" style="margin-left: 25px;">
        <bk-button theme="primary" :disabled="disabled" :loading="sliderLoading" @click="handleResourceSumit"
          data-test-id="group_btn_resourceInstanceSubmit">
          {{ $t(`m.common['保存']`) }}
        </bk-button>
        <bk-button style="margin-left: 10px;" :disabled="disabled" v-if="isShowPreview" @click="handleResourcePreview">{{ $t(`m.common['预览']`) }}</bk-button>
        <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourceCancel">{{ $t(`m.common['取消']`) }}</bk-button>
      </div>
    </bk-sideslider>

    <preview-resource-dialog
      :show="isShowPreviewDialog"
      :title="previewDialogTitle"
      :params="previewResourceParams"
      @on-after-leave="handlePreviewDialogClose" />

    <render-aggregate-sideslider
      :show.sync="isShowAggregateSideslider"
      :params="aggregateResourceParams"
      :is-super-manager="isSuperManager"
      :value="aggregateValue"
      :default-list="defaultSelectList"
      @on-selected="handlerSelectAggregateRes" />

    <bk-sideslider
      :is-show.sync="isShowSideslider"
      :title="sidesliderTitle"
      :width="sliderWidth"
      :quick-close="true"
      @animation-end="handleAnimationEnd">
      <div slot="content">
        <component :is="'RenderDetail'" :data="previewData" />
      </div>
    </bk-sideslider>
    <bk-dialog
      ext-cls="comfirmDialog"
      v-model="isShowDeleteDialog"
      :close-icon="showIcon"
      :footer-position="footerPosition"
      @confirm="handleDelete">
      <h3 style="text-align:center">{{ $t(`m.common['是否删除该自定义权限']`) }}</h3>
    </bk-dialog>
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import Condition from '@/model/condition';
  import GroupPolicy from '@/model/group-policy';
  import RenderAggregateSideslider from '@/components/choose-ip/sideslider';
  import { leaveConfirm } from '@/common/leave-confirm';
  import { CUSTOM_PERM_TEMPLATE_ID, PERMANENT_TIMESTAMP } from '@/common/constants';
  import RenderResource from './render-resource';
  import RenderCondition from './render-condition';
  import PreviewResourceDialog from './preview-resource-dialog';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import RenderDetail from '../common/render-detail';
  // import store from '@/store'
  export default {
    name: 'resource-instance-table',
    components: {
      RenderAggregateSideslider,
      RenderResource,
      RenderCondition,
      PreviewResourceDialog,
      RenderResourcePopover,
      RenderDetail
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
        type: String,
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
      totalCount: {
        type: Number
      }
    },
    data () {
      return {
        tableList: [],
        isShowResourceInstanceSideslider: false,
        resourceInstanceSidesliderTitle: '',
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
        footerPosition: 'center',
        newRow: '',
        role: '',
        selectedIndex: 0,
        instanceKey: '',
        curCopyDataId: '',
        emptyResourceGroupsList: [],
        isExpandTable: false
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
            return _.cloneDeep(curData.condition);
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
            return _.cloneDeep(curData.condition);
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
            if (this.curIndex === -1) {
                return false;
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
        }
    },
    watch: {
      list: {
        handler (value) {
          // if (this.isAllExpanded) {
          //     this.tableList = value.filter(e =>
          //         (e.resource_groups && e.resource_groups.length)
          //         || e.isAggregate);
          //     this.emptyResourceGroupsList = value.filter(e =>
          //         e.resource_groups && !e.resource_groups.length);
          //     let emptyGroupsIdList = this.emptyResourceGroupsList.map(e => e.judgeId) || [];
          //     emptyGroupsIdList = [...new Set(emptyGroupsIdList)];
          //     console.log('emptyGroupsIdList', emptyGroupsIdList);
          //     emptyGroupsIdList.forEach((item, index) => {
          //         console.log('this.emptyResourceGroupsList', this.emptyResourceGroupsList);
          //         this.emptyResourceGroupsName = (this.emptyResourceGroupsList || [])
          //             .filter(data => data.judgeId === item)
          //             .reduce((p, e) => {
          //                 p.push(e.name);
          //                 return p;
          //             }, []);
          //         console.log('this.emptyResourceGroupsName', this.emptyResourceGroupsName);
          //         if (this.emptyResourceGroupsName.length) {
          //             this.$nextTick(() => {
          //                 this.emptyResourceGroupsList[index].name = this.emptyResourceGroupsName.join('，');
          //                 this.emptyResourceGroupsTableList = this.emptyResourceGroupsList[index];
          //                 this.tableList.unshift(this.emptyResourceGroupsTableList);
          //                 console.log('this.tableList', this.tableList);
          //             });
          //         }
          //     });
          // } else {
          //     value.forEach(e => {
          //         e.name = e.name.split('，')[0];
          //     });
          //     this.emptyResourceGroupsList = []; // 重置变量
          //     value = _.uniqWith(value, _.isEqual); // 去重
          //     this.tableList.splice(0, this.tableList.length, ...value);
          // }
          value = _.uniqWith(value, _.isEqual); // 去重
          this.isExpandTable = value.length > 0;
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
      // tableList: {
      //     handler (newVal, oldVal) {
      //         debugger
      //     },
      //     deep: true
      // }
    },
    methods: {
      handleSpanMethod ({ row, column, rowIndex, columnIndex }) {
        if (this.isCreateMode) {
          if (columnIndex === 0) {
            const rowsCount = this.tableList.filter(item => item.detail.id === row.detail.id).length;
            const firstIndex = this.tableList.findIndex(item => item.detail.id === row.detail.id);
            const endIndex = firstIndex + rowsCount - 1;
            if (rowIndex === firstIndex) {
              return {
                rowspan: rowsCount,
                colspan: 1
              };
            } else {
              if (rowIndex <= endIndex) {
                return {
                  rowspan: 0,
                  colspan: 0
                };
              }
            }
          }
        } else {
          return {
            rowspan: 1,
            colspan: 1
          };
        }
      },
      handlerSelectAggregateRes (payload) {
        // debugger
        window.changeDialog = true;
        const instances = payload.map(item => {
          return {
            id: item.id,
            name: item.display_name
          };
        });
        this.tableList[this.aggregateIndex].isError = false;
        this.selectedIndex = this.tableList[this.aggregateIndex].selectedIndex;
        const instanceKey = this.tableList[this.aggregateIndex].aggregateResourceType[this.selectedIndex].id;
        const instancesDisplayData = _.cloneDeep(this.tableList[this.aggregateIndex].instancesDisplayData);
        this.tableList[this.aggregateIndex].instancesDisplayData = {
                    ...instancesDisplayData,
                    [instanceKey]: instances
        };
        this.tableList[this.aggregateIndex].instances = [];

        for (const key in this.tableList[this.aggregateIndex].instancesDisplayData) {
          // eslint-disable-next-line max-len
          this.tableList[this.aggregateIndex].instances.push(...this.tableList[this.aggregateIndex].instancesDisplayData[key]);
        }
        this.$emit('on-select', this.tableList[this.aggregateIndex]);
      },
      handleRowMouseEnter (index, event, row) {
        if (this.mode === 'detail' && !this.isEdit && this.isCustom && this.type !== 'view') {
          this.$set(row, 'showDelete', true);
        }
      },
      handleRowMouseLeave (index, event, row) {
        if (this.mode === 'detail' && !this.isEdit && this.isCustom && this.type !== 'view') {
          this.$set(row, 'showDelete', false);
        }
      },
      toHandleDelete (row) {
        this.isShowDeleteDialog = true;
        this.newRow = row;
      },
      handleDelete () {
        this.$emit('on-delete', this.newRow);
      },
      handleRemove (row, payload) {
        window.changeDialog = true;
        if (row.isAggregate) {
          this.$emit('on-aggregate-delete', row.system_id, row.actions, payload);
          return;
        }
        this.$emit('on-delete', row.system_id, row.id, `${row.system_id}&${row.id}`, payload);
      },
      handleExpanded () {
        this.isExpandTable = !this.isExpandTable;
      },
      handleClearAll () {
        this.tableList = [];
        this.isExpandTable = false;
        this.$emit('on-clear-all');
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
        this.previewData = _.cloneDeep(params);
        this.sidesliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        this.isShowSideslider = true;
      },
      handleAnimationEnd () {
        this.sidesliderTitle = '';
        this.previewData = [];
        this.curId = '';
      },
      handlerAggregateConditionMouseover (payload) {
        if (this.curCopyData[0] === 'none') {
          return;
        }
        if (this.curCopyKey === `${payload.aggregateResourceType.system_id}${payload.aggregateResourceType.id}`) {
          payload.canPaste = true;
        }
      },
      getScopeActionResource (payload, id, systemId) {
        const scopeAction = this.authorization[systemId];
        // eslint-disable-next-line max-len
        const actions = (scopeAction && scopeAction.filter(item => payload.map(_ => _.id).includes(item.id))) || [];
        const conditions = actions.map(
          item => item.resource_groups[0].related_resource_types[0].condition
        ).filter(_ => _.length > 0);
        if (conditions.length < 1) {
          return [];
        }

        const instances = actions.map(item => {
          const instancesItem = item.resource_groups[0].related_resource_types[0].condition[0]
            && item.resource_groups[0].related_resource_types[0].condition[0].instances;
          return (instancesItem && instancesItem.filter(e => e.type === id)) || [];
        });
        const tempData = [];
        const resources = instances.map(item => item[0]
          && item[0].path).map(item => item && item.map(v => v.map(_ => _.id)));
        const resourceList = instances
          .map(item => item[0] && item[0].path)
          .map(item => item && item.map(v => v.map(({ id, name }) => ({ id, name }))))
          .flat(2);
        resources.forEach(item => {
          item && item.forEach(subItem => {
            if (resources.every(v => v && v.some(vItem => vItem[0] === subItem[0]))) {
              tempData.push(subItem[0]);
            }
          });
        });
        if (instances.length !== actions.length) {
          return [];
        }
        const curResource = [...new Set(tempData)];
        const isEqual = curResource.length > 0;
        if (isEqual) {
          const curResourceList = [];
          resourceList.forEach(item => {
            if (!curResourceList.find(subItem => subItem.id === item.id)) {
              curResourceList.push({
                id: item.id,
                display_name: item.name
              });
            }
          });
          return curResourceList.filter(item => curResource.includes(item.id));
        }
        return [];
      },
      handlerAggregateConditionMouseleave (payload) {
        payload.canPaste = false;
      },
      handlerAggregateOnCopy (payload, index) {
        this.instanceKey = payload.aggregateResourceType[payload.selectedIndex].id;
        window.changeDialog = true;
        this.curCopyKey = `${payload.aggregateResourceType[payload.selectedIndex].system_id}${payload.aggregateResourceType[payload.selectedIndex].id}`;
        this.curAggregateResourceType = payload.aggregateResourceType[payload.selectedIndex];
        this.curCopyData = _.cloneDeep(payload.instancesDisplayData[this.instanceKey]);
        this.curCopyDataId = payload.aggregationId;
        this.curCopyMode = 'aggregate';
        this.showMessage(this.$t(`m.info['实例复制']`));
        this.$refs[`condition_${index}_aggregateRef`] && this.$refs[`condition_${index}_aggregateRef`].setImmediatelyShow(true);
      },
      handlerAggregateOnPaste (payload) {
        let tempInstances = [];
        if (this.curCopyMode === 'aggregate') {
          tempInstances = this.curCopyData;
        } else {
          if (this.curCopyData[0] !== 'none') {
            const instances = this.curCopyData.map(item => item.instance);
            const instanceData = instances[0][0];
            tempInstances = instanceData.path.map(pathItem => {
              return {
                id: pathItem[0].id,
                name: pathItem[0].name
              };
            });
          }
        }
        if (tempInstances.length < 1) {
          return;
        }
        payload.instances = _.cloneDeep(tempInstances);
        payload.isError = false;
        this.showMessage(this.$t(`m.info['粘贴成功']`));
        this.$emit('on-select', payload);
      },
      handlerAggregateOnBatchPaste (payload, index) {
        let tempCurData = ['none'];
        let tempArrgegateData = [];
        if (this.curCopyMode === 'normal') {
          if (this.curCopyData[0] !== 'none') {
            tempCurData = this.curCopyData.map(item => {
              delete item.id;
              return item;
            });
            const instances = this.curCopyData.map(item => item.instance);
            const instanceData = instances[0][0];
            tempArrgegateData = instanceData.path.map(pathItem => {
              return {
                id: pathItem[0].id,
                name: pathItem[0].name
              };
            });
          }
        } else {
          tempArrgegateData = this.curCopyData;
          const instances = (() => {
            const arr = [];
            const { id, name, system_id } = this.curAggregateResourceType;
            this.curCopyData && this.curCopyData.forEach(v => {
              const curItem = arr.find(_ => _.type === id);
              if (curItem) {
                curItem.path.push([{
                  id: v.id,
                  name: v.name,
                  system_id,
                  type: id,
                  type_name: name
                }]);
              } else {
                arr.push({
                  name,
                  type: id,
                  path: [[{
                    id: v.id,
                    name: v.name,
                    system_id,
                    type: id,
                    type_name: name
                  }]]
                });
              }
            });
            return arr;
          })();
          if (instances.length > 0) {
            tempCurData = [new Condition({ instances }, '', 'add')];
          }
        }
        this.tableList.forEach(item => {
          if (!item.isAggregate) {
            item.resource_groups.forEach(groupItem => {
              groupItem.related_resource_types
                && groupItem.related_resource_types.forEach((subItem, subItemIndex) => {
                  if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                    subItem.condition = _.cloneDeep(tempCurData);
                    subItem.isError = false;
                    this.$emit('on-resource-select', index, subItemIndex, subItem.condition);
                  }
                });
            });
          } else {
            item.aggregateResourceType.forEach(aggregateResourceItem => {
              const systemId = this.isSuperManager
                ? aggregateResourceItem.system_id : item.system_id;
              if (`${systemId}${aggregateResourceItem.id}` === this.curCopyKey && this.curCopyDataId !== item.aggregationId) {
                if (Object.keys(item.instancesDisplayData).length) {
                  item.instancesDisplayData[this.instanceKey] = _.cloneDeep(tempArrgegateData);
                  item.instances = this.setInstanceData(item.instancesDisplayData);
                } else {
                  item.instances = _.cloneDeep(tempArrgegateData);
                  this.setInstancesDisplayData(item);
                }
              }
            });
            item.isError = false;
            this.$emit('on-select', item);
            // if (`${item.aggregateResourceType.system_id}${item.aggregateResourceType.id}` === this.curCopyKey) {
            //     item.instances = _.cloneDeep(tempArrgegateData);
            //     item.isError = false;
            //     this.$emit('on-select', item);
            // }
          }
        });
        payload.isError = false;
        this.curCopyData = ['none'];
        this.$refs[`condition_${index}_aggregateRef`] && this.$refs[`condition_${index}_aggregateRef`].setImmediatelyShow(false);
        this.showMessage(this.$t(`m.info['批量粘贴成功']`));
      },

      // 设置instances
      setInstanceData (data) {
        return Object.keys(data).reduce((p, v) => {
          p.push(...data[v]);
          return p;
        }, []);
      },

      // 设置InstancesDisplayData
      setInstancesDisplayData (data) {
        data.instancesDisplayData = data.instances.reduce((p, v) => {
          if (!p[this.instanceKey]) {
            p[this.instanceKey] = [];
          }
          p[this.instanceKey].push({
            id: v.id,
            name: v.name
          });
          return p;
        }, {});
      },

      // 设置正常粘贴InstancesDisplayData
      setNomalInstancesDisplayData (data, key) {
        data.instancesDisplayData[key] = data.instances.map(e => ({
          id: e.id,
          name: e.name
        }));
      },

      showAggregateResourceInstance (data, index) {
        window.changeDialog = true;
        const aggregateResourceParams = {
          ...data.aggregateResourceType[data.selectedIndex],
          curAggregateSystemId: data.system_id
        };
        this.selectedIndex = data.selectedIndex;
        this.aggregateResourceParams = _.cloneDeep(aggregateResourceParams);
        this.aggregateIndex = index;
        const instanceKey = data.aggregateResourceType[data.selectedIndex].id;
        this.instanceKey = instanceKey;
        if (!data.instancesDisplayData[instanceKey]) data.instancesDisplayData[instanceKey] = [];
        this.aggregateValue = _.cloneDeep(data.instancesDisplayData[instanceKey].map(item => {
          return {
            id: item.id,
            display_name: item.name
          };
        }));
        this.defaultSelectList = this.getScopeActionResource(
          data.actions,
          data.aggregateResourceType[data.selectedIndex].id,
          data.system_id
        );
        this.isShowAggregateSideslider = true;
      },
      showMessage (payload) {
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: payload
        });
      },
      getCellClass ({ row, column, rowIndex, columnIndex }) {
        let judgeIndex = columnIndex;
        if (this.isCreateMode) {
          judgeIndex = 3;
        } else {
          judgeIndex = 1;
        }
        if (columnIndex === judgeIndex) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },
      handleLimitChange () {
        window.changeDialog = true;
        const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
          .related_resource_types[this.curResIndex];
        curData.isChange = true;
      },
      handleOnInit (payload) {
        this.disabled = !payload;
      },
      async showResourceInstance (data, index, resItem, resIndex, groupIndex) {
        window.changeDialog = true;
        this.params = {
          system_id: this.systemId,
          action_id: data.id,
          resource_type_system: resItem.system_id,
          resource_type_id: resItem.type
        };
        if (this.isCreateMode) {
          this.params.system_id = data.detail.system.id;
          await this.fetchAuthorizationScopeActions(this.params.system_id);
        }
        const scopeAction = this.authorization[this.params.system_id] || [];
        this.curScopeAction = _.cloneDeep(scopeAction.find(item => item.id === data.id));
        this.curIndex = index;
        this.curResIndex = resIndex;
        this.curGroupIndex = groupIndex;
        this.resourceInstanceSidesliderTitle = this.$t(`m.info['关联侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}` });
        window.changeAlert = 'iamSidesider';
        this.isShowResourceInstanceSideslider = true;
      },
      // 请求资源实例数据
      async handleMainActionSubmit (payload, relatedActions) {
        // debugger
        const curPayload = _.cloneDeep(payload);
        this.sliderLoading = true;
        curPayload.forEach(item => {
          item.instances = item.instance || [];
          item.attributes = item.attribute || [];
          delete item.instance;
          delete item.attribute;
        });
        const curData = _.cloneDeep(this.tableList[this.curIndex]);
        // eslint-disable-next-line max-len
        curData.resource_groups[this.curGroupIndex].related_resource_types = [curData.resource_groups[this.curGroupIndex]
          .related_resource_types[this.curResIndex]];
        curData.resource_groups[this.curGroupIndex].related_resource_types[0].condition = curPayload;
        const relatedList = _.cloneDeep(this.tableList.filter(item => {
          return !item.isAggregate
            && relatedActions.includes(item.id)
            && curData.detail.system.id === item.detail.system.id
            && item.resource_groups[this.curGroupIndex]
            && !item.resource_groups[this.curGroupIndex].related_resource_types.every(sub => sub.empty);
        }));
        if (relatedList.length > 0) {
          relatedList.forEach(item => {
            delete item.policy_id;
            item.resource_groups[this.curGroupIndex].related_resource_types.forEach(resItem => {
              resItem.condition.forEach(conditionItem => {
                conditionItem.instances = conditionItem.instance || [];
                conditionItem.attributes = conditionItem.attribute || [];
                delete conditionItem.instance;
                delete conditionItem.attribute;
              });
            });
            item.expired_at = PERMANENT_TIMESTAMP;
          });
        }
        curData.resource_groups = curData.resource_groups.filter(item => item.related_resource_types);
        const targetPolicies = relatedList.filter(item =>
          item.resource_groups[this.curGroupIndex].related_resource_types
          && item.resource_groups[this.curGroupIndex].related_resource_types.length);
        try {
          const res = await this.$store.dispatch('permApply/getRelatedPolicy', {
            source_policy: curData,
            system_id: curData.system_id,
            target_policies: targetPolicies
          });
          this.handleRelatedAction(res.data);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.sliderLoading = false;
        }
      },
      async fetchAuthorizationScopeActions (systemId) {
        try {
          const res = await this.$store.dispatch('permTemplate/getAuthorizationScopeActions', { systemId });
          this.authorization[systemId] = res.data.filter(item => item.id !== '*');
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },
      handleRelatedAction (payload) {
        if (payload.length < 1) {
          return;
        }
        payload.forEach(item => {
          const curIndex = this.tableList.findIndex(sub => sub.id === item.id
            && item.resource_groups[this.curGroupIndex]
            && sub.detail.system.id === item.resource_groups[this.curGroupIndex]
              .related_resource_types[0].system_id);
          if (curIndex > -1) {
            const old = this.tableList[curIndex];
            this.tableList.splice(curIndex, 1, new GroupPolicy(
              {
                                ...item,
                                tag: 'add',
                                isShowRelatedText: true
              },
              '',
              old.isTemplate ? 'template' : 'custom',
              // new GroupPolicy 最后一个参数是 detail 就是 this.tableList[curIndex].detail
              Object.assign({}, old.detail, {
                system: {
                  id: this.tableList[curIndex].detail.system.id,
                  name: this.tableList[curIndex].detail.system.name
                },
                // 此 id 会在 handleSpanMethod 方法中使用到，合并单元格的依据，使用 CUSTOM_PERM_TEMPLATE_ID 会导致问题
                // id: CUSTOM_PERM_TEMPLATE_ID
                id: old.isTemplate ? this.tableList[curIndex].detail.id : CUSTOM_PERM_TEMPLATE_ID
              }),
              true
            ));
          }
        });
      },
      // 保存
      async handleResourceSumit () {
        window.changeDialog = true;
        const conditionData = this.$refs.renderResourceRef.handleGetValue();
        const { isEmpty, data } = conditionData;
        if (isEmpty) {
          this.curIndex = -1;
          this.curResIndex = -1;
          this.curGroupIndex = -1;
          return;
        }
        const resItem = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
          .related_resource_types[this.curResIndex];
        const isConditionEmpty = data.length === 1 && data[0] === 'none';
        if (isConditionEmpty) {
          resItem.condition = ['none'];
        } else {
          const { isMainAction, related_actions } = this.tableList[this.curIndex];
          // 如果为主操作
          if (isMainAction) {
            await this.handleMainActionSubmit(data, related_actions);
          }
          resItem.condition = data;
          resItem.isError = false;
        }
        window.changeAlert = false;
        this.resourceInstanceSidesliderTitle = '';
        this.isShowResourceInstanceSideslider = false;
        this.$emit('on-resource-select', this.curIndex, this.curResIndex, resItem.condition, this.curGroupIndex);
        this.curIndex = -1;
        this.curResIndex = -1;
        this.curGroupIndex = -1;
        // 这里触发 create/index.vue 里 handleAggregateAction 事件会导致 tableList 变化，导致 list 属性变化
        // list 属性变化之后，isShowRelatedText 属性以及其他属性均会重置
        // if (!this.isAllExpanded) {
        //     // 调用合并展开的方法 重组tableList的排序
        //     this.$emit('handleAggregateAction', false)
        // }
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
          resource_group_id: this.tableList[this.curIndex].resource_groups[this.curGroupIndex].id,
          isTemplate: this.tableList[this.curIndex].isTemplate,
          isNotLimit: conditionData.length === 0
        };
        this.previewDialogTitle = this.$t(`m.info['操作侧边栏操作的资源实例差异对比']`, { value: `${this.$t(`m.common['【']`)}${this.tableList[this.curIndex].name}${this.$t(`m.common['】']`)}` });
        this.isShowPreviewDialog = true;
      },
      handlerConditionMouseover (payload) {
        if (Object.keys(this.curCopyParams).length < 1 && this.curCopyMode === 'normal') {
          return;
        }
        if (this.curCopyData[0] === 'none' && this.curCopyMode === 'aggregate') {
          return;
        }
        if (this.curCopyKey === `${payload.system_id}${payload.type}`) {
          payload.canPaste = true;
        }
      },
      handlerConditionMouseleave (payload) {
        payload.canPaste = false;
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
      },
      handlerOnCopy (payload, index, subIndex, action) {
        window.changeDialog = true;
        this.curCopyKey = `${payload.system_id}${payload.type}`;
        this.curCopyData = _.cloneDeep(payload.condition);
        this.curCopyMode = 'normal';
        this.curCopyParams = this.getBatchCopyParms(action, payload);
        this.showMessage(this.$t(`m.info['实例复制']`));
        this.$refs[`condition_${index}_${subIndex}_ref`][0] && this.$refs[`condition_${index}_${subIndex}_ref`][0].setImmediatelyShow(true);
      },
      getBatchCopyParms (payload, content) {
        const actions = [];
        this.tableList.forEach(item => {
          if (!item.isAggregate) {
            if (item.id !== payload.id) {
              actions.push({
                system_id: item.detail.system.id,
                id: item.id
              });
            }
          }
        });
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
      handlerOnPaste (payload, content, $index, contentIndex) {
        // debugger
        let tempCurData = ['none'];
        if (this.curCopyMode === 'normal') {
          if (!payload.flag) {
            return;
          }
          if (payload.data.length === 0) {
            content.condition = [];
          } else {
            content.condition = payload.data.map(conditionItem => new Condition(conditionItem, '', 'add'));
          }
        } else {
          const instances = (() => {
            const arr = [];
            const { id, name, system_id } = this.curAggregateResourceType;
            this.curCopyData.forEach(v => {
              const curItem = arr.find(_ => _.type === id);
              if (curItem) {
                curItem.path.push([{
                  id: v.id,
                  name: v.name,
                  system_id,
                  type: id,
                  type_name: name
                }]);
              } else {
                arr.push({
                  name,
                  type: id,
                  path: [[{
                    id: v.id,
                    name: v.name,
                    system_id,
                    type: id,
                    type_name: name
                  }]]
                });
              }
            });
            return arr;
          })();
          if (instances.length > 0) {
            tempCurData = [new Condition({ instances }, '', 'add')];
          }
          if (tempCurData[0] === 'none') {
            return;
          }
          content.condition = _.cloneDeep(tempCurData);
        }
        content.isError = false;
        this.showMessage(this.$t(`m.info['粘贴成功']`));
        this.$emit('on-resource-select', $index, contentIndex, content.condition);
      },
      handlerOnBatchPaste (payload, content, index, subIndex) {
        // debugger
        let tempCurData = ['none'];
        let tempArrgegateData = [];
        if (this.curCopyMode === 'normal') {
          if (!payload.flag) {
            return;
          }
          // 预计算是否存在 聚合后的数据 可以粘贴
          // const flag = this.tableList.some(item => !!item.isAggregate
          //     && `${item.aggregateResourceType[item.selectedIndex].system_id}${item.aggregateResourceType[item.selectedIndex].id}` === this.curCopyKey);
          const flag = this.tableList.some(item => {
            return !!item.isAggregate
              && item.aggregateResourceType.some(e => `${e.system_id}${e.id}` === this.curCopyKey);
          });
          if (flag) {
            if (this.curCopyData.length < 1) {
              tempCurData = [];
            } else {
              if (this.curCopyData[0] !== 'none') {
                tempCurData = this.curCopyData.map(item => {
                  delete item.id;
                  return item;
                });
                tempCurData.forEach((item, index) => {
                  if (content.condition[index]) {
                    if (content.condition[index].id) {
                      item.id = content.condition[index].id;
                    } else {
                      item.id = '';
                    }
                  } else {
                    item.id = '';
                  }
                });
                const instances = this.curCopyData.map(item => item.instance);
                const instanceData = instances[0][0];
                tempArrgegateData = instanceData.path.map(pathItem => {
                  return {
                    id: pathItem[0].id,
                    name: pathItem[0].name
                  };
                });
              }
            }
          }
          if (payload.data.length === 0) {
            this.tableList.forEach(item => {
              if (!item.isAggregate) {
                item.resource_groups.forEach(groupItem => {
                  groupItem.related_resource_types.forEach(resItem => {
                    if (`${resItem.system_id}${resItem.type}` === this.curCopyKey) {
                      resItem.condition = [];
                      resItem.isError = false;
                    }
                  });
                });
              } else {
                if (`${item.aggregateResourceType[item.selectedIndex].system_id}${item.aggregateResourceType[item.selectedIndex].id}` === this.curCopyKey) {
                  item.instances = _.cloneDeep(tempArrgegateData);
                  item.isError = false;
                  this.$emit('on-select', item);
                }
              }
            });
          } else {
            this.tableList.forEach(item => {
              if (!item.isAggregate) {
                const curPasteData = (payload.data || []).find(_ => _.id === item.id);
                if (curPasteData) {
                  const systemId = this.isCreateMode ? item.detail.system.id : this.systemId;
                  const scopeAction = this.authorization[systemId] || [];
                  // eslint-disable-next-line max-len
                  const curScopeAction = _.cloneDeep(scopeAction.find(scopeItem => scopeItem.id === item.id));
                  // eslint-disable-next-line max-len
                  if (curScopeAction && curScopeAction.resource_groups && curScopeAction.resource_groups.length) {
                    curScopeAction.resource_groups.forEach(curScopeActionItem => {
                      curScopeActionItem.related_resource_types.forEach(curResItem => {
                        if (`${curResItem.system_id}${curResItem.type}` === `${curPasteData.resource_type.system_id}${curPasteData.resource_type.type}`) {
                          // eslint-disable-next-line max-len
                          const canPasteName = curResItem.condition[0].instances[0].path.reduce((p, v) => {
                            p.push(v[0].name);
                            return p;
                          }, []);
                          // eslint-disable-next-line max-len
                          item.resource_groups.forEach(groupItem => {
                            groupItem.related_resource_types.forEach(resItem => {
                              if (`${resItem.system_id}${resItem.type}` === `${curPasteData.resource_type.system_id}${curPasteData.resource_type.type}`) {
                                // eslint-disable-next-line max-len
                                const curPasteDataCondition = curPasteData.resource_type.condition;
                                // eslint-disable-next-line max-len
                                const condition = curPasteDataCondition.map(c => {
                                  c.instances.forEach(j => {
                                    // eslint-disable-next-line max-len
                                    j.path = j.path.filter(e => {
                                      if (!canPasteName.includes(e[0].name)) {
                                        return false;
                                      }
                                      return canPasteName.includes(e[0].name);
                                    });
                                  });
                                  return c;
                                  // eslint-disable-next-line max-len
                                }).filter(d => !!(d.instances[0].path && d.instances[0].path.length));
                                if (condition && condition.length) {
                                  resItem.condition = condition.map(conditionItem => new Condition(conditionItem, '', 'add'));
                                  resItem.isError = false;
                                }
                              }
                            });
                          });
                        }
                      });
                    });
                  } else {
                    item.resource_groups && item.resource_groups.forEach(groupItem => {
                      groupItem.related_resource_types && groupItem.related_resource_types.forEach(resItem => {
                        if (`${resItem.system_id}${resItem.type}` === `${curPasteData.resource_type.system_id}${curPasteData.resource_type.type}`) {
                          resItem.condition = curPasteData.resource_type.condition.map(conditionItem => new Condition(conditionItem, '', 'add'));
                          resItem.isError = false;
                        }
                      });
                    });
                  }
                }
              } else {
                item.aggregateResourceType && item.aggregateResourceType.forEach(aggregateResourceItem => {
                  const systemId = this.isSuperManager
                    ? aggregateResourceItem.system_id : item.system_id;
                  if (`${systemId}${aggregateResourceItem.id}` === this.curCopyKey) {
                    item.instances = _.cloneDeep(tempArrgegateData);
                    this.instanceKey = aggregateResourceItem.id;
                    this.setNomalInstancesDisplayData(item, this.instanceKey);
                    this.instanceKey = ''; // 重置
                    item.isError = false;
                  }
                });
                this.$emit('on-select', item);
              }
            });
          }
        } else {
          tempArrgegateData = this.curCopyData;
          const instances = (() => {
            const arr = [];
            const { id, name, system_id } = this.curAggregateResourceType;
            this.curCopyData.forEach(v => {
              const curItem = arr.find(_ => _.type === id);
              if (curItem) {
                curItem.path.push([{
                  id: v.id,
                  name: v.name,
                  system_id,
                  type: id,
                  type_name: name
                }]);
              } else {
                arr.push({
                  name,
                  type: id,
                  path: [[{
                    id: v.id,
                    name: v.name,
                    system_id,
                    type: id,
                    type_name: name
                  }]]
                });
              }
            });
            return arr;
          })();
          if (instances.length > 0) {
            tempCurData = [new Condition({ instances }, '', 'add')];
          }
          this.tableList.forEach(item => {
            if (!item.isAggregate) {
              item.resource_groups.forEach(groupItem => {
                groupItem.related_resource_types.forEach((subItem, subItemIndex) => {
                  if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                    subItem.condition = _.cloneDeep(tempCurData);
                    subItem.isError = false;
                    this.$emit('on-resource-select', index, subItemIndex, subItem.condition);
                  }
                });
              });
            } else {
              if (`${item.aggregateResourceType.system_id}${item.aggregateResourceType.id}` === this.curCopyKey) {
                item.instances = _.cloneDeep(tempArrgegateData);
                item.isError = false;
                this.$emit('on-select', item);
              }
            }
          });
        }
        content.isError = false;
        this.$refs[`condition_${index}_${subIndex}_ref`][0] && this.$refs[`condition_${index}_${subIndex}_ref`][0].setImmediatelyShow(false);
        this.curCopyData = ['none'];
        this.showMessage(this.$t(`m.info['批量粘贴成功']`));
      },
      handlePreviewDialogClose () {
        this.previewDialogTitle = '';
        this.previewResourceParams = {};
        this.isShowPreviewDialog = false;
      },
      resetDataAfterClose () {
        this.curIndex = -1;
        this.curResIndex = -1;
        this.curGroupIndex = -1;
        this.previewResourceParams = {};
        this.params = {};
        this.resourceInstanceSidesliderTitle = '';
      },
      handleResourceCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(() => {
          this.isShowResourceInstanceSideslider = false;
          this.resetDataAfterClose();
        }, _ => _);
      },
      getData () {
        let flag = false;
        const templates = [];
        // debugger
        // 自定义时的模板id为0
        if (this.tableList.length < 1) {
          flag = true;
          return {
            flag,
            templates
          };
        }

        // 重新赋值
        // if (this.isAllExpanded) {
        //     this.tableList = this.tableList.filter(e =>
        //         (e.resource_groups && e.resource_groups.length)
        //         || e.isAggregate);
        //     if (this.emptyResourceGroupsList.length) {
        //         this.emptyResourceGroupsList[0].name = this.emptyResourceGroupsName[0];
        //         this.tableList = [...this.tableList, ...this.emptyResourceGroupsList];
        //     }
        // }

        this.tableList.forEach(item => {
          let actionParam = {};
          let aggregationParam = {};
          let systemId = '';
          if (!item.isAggregate) {
            const groupResourceTypes = [];
            const { type, id, name, environment, description } = item;
            systemId = item.detail.system.id;
            if (item.resource_groups.length > 0) {
              item.resource_groups.forEach(groupItem => {
                const relatedResourceTypes = [];
                if (groupItem.related_resource_types.length > 0) {
                  groupItem.related_resource_types.forEach(resItem => {
                    if (resItem.empty) {
                      resItem.isError = true;
                      flag = true;
                    }
                    const conditionList = (resItem.condition.length > 0 && !resItem.empty)
                      ? resItem.condition.map(conItem => {
                        const { id, instance, attribute } = conItem;
                        const attributeList = (attribute && attribute.length > 0)
                          ? attribute.map(({ id, name, values }) => ({ id, name, values }))
                          : [];
                        const instanceList = (instance && instance.length > 0)
                          ? instance.map(({ name, type, paths }) => {
                            const tempPath = _.cloneDeep(paths);
                            tempPath.forEach(pathItem => {
                              pathItem.forEach(pathSubItem => {
                                delete pathSubItem.disabled;
                              });
                            });
                            return {
                              name,
                              type,
                              path: tempPath
                            };
                          })
                          : [];
                        return {
                          id,
                          instances: instanceList,
                          attributes: attributeList
                        };
                      })
                      : [];
                    relatedResourceTypes.push({
                      type: resItem.type,
                      system_id: resItem.system_id,
                      name: resItem.name,
                      condition: conditionList.filter(
                        item => item.instances.length > 0 || item.attributes.length > 0
                      )
                    });
                  });
                }
                groupResourceTypes.push({
                  id: groupItem.id,
                  related_resource_types: relatedResourceTypes
                });
              });
              // 强制刷新下
              item.resource_groups = _.cloneDeep(item.resource_groups);
            }
            actionParam = {
              type,
              name,
              id,
              description,
              resource_groups: groupResourceTypes,
              environment
            };
          } else {
            systemId = item.system_id;
            const { actions, aggregateResourceType, instances, instancesDisplayData } = item;
            if (instances.length < 1) {
              item.isError = true;
              flag = true;
            } else {
              const temps = _.cloneDeep(actions);
              temps.forEach(sub => {
                sub.system_id = sub.detail.system.id;
              });
              const aggregateResourceTypes = aggregateResourceType.reduce((p, e) => {
                if (instancesDisplayData[e.id] && instancesDisplayData[e.id].length) {
                  const obj = {};
                  obj.id = e.id;
                  obj.system_id = e.system_id;
                  obj.instances = instancesDisplayData[e.id];
                  p.push(obj);
                }
                return p;
              }, []);
              aggregationParam = {
                actions: temps,
                aggregate_resource_types: aggregateResourceTypes,
                expired_at: PERMANENT_TIMESTAMP
              };
            }
          }
          // eslint-disable-next-line max-len
          const templateId = item.isTemplate ? item.isAggregate ? item.actions[0].detail.id : item.detail.id : CUSTOM_PERM_TEMPLATE_ID;
          const compareId = `${templateId}&${systemId}`;
          const isHasAggregation = Object.keys(aggregationParam).length > 0;
          const isHasActions = Object.keys(actionParam).length > 0;
          if (!templates.map(sub => `${sub.template_id}&${sub.system_id}`).includes(compareId)) {
            templates.push({
              system_id: systemId,
              template_id: templateId,
              actions: isHasActions ? [actionParam] : [],
              aggregations: isHasAggregation ? [aggregationParam] : []
            });
          } else {
            const tempActionData = templates.find(sub => `${sub.template_id}&${sub.system_id}` === compareId);
            if (tempActionData) {
              if (isHasActions) {
                if (!tempActionData.actions.map(_ => _.id).includes(actionParam.id)) {
                  tempActionData.actions.push(actionParam);
                }
              }
              if (isHasAggregation) {
                tempActionData.aggregations.push(aggregationParam);
              }
            }
          }
        });
        return {
          flag,
          templates
        };
      },
      getDataByNormal () {
        if (this.isCreateMode) {
          this.getData();
          return;
        }
        let flag = false;
        if (this.tableList.length < 1) {
          flag = true;
          return {
            flag,
            actions: [],
            aggregations: []
          };
        }
        const actionList = [];
        const aggregations = [];
        this.tableList.forEach(item => {
          if (!item.isAggregate) {
            const groupResourceTypes = [];
            const { type, id, name, environment, description } = item;
            if (item.resource_groups.length > 0) {
              item.resource_groups.forEach(groupItem => {
                const relatedResourceTypes = [];
                if (groupItem.related_resource_types.length > 0) {
                  groupItem.related_resource_types.forEach(resItem => {
                    if (resItem.empty) {
                      resItem.isError = true;
                      flag = true;
                    }
                    const conditionList = (resItem.condition.length > 0 && !resItem.empty)
                      ? resItem.condition.map(conItem => {
                        const { id, instance, attribute } = conItem;
                        const attributeList = (attribute && attribute.length > 0)
                          ? attribute.map(({ id, name, values }) => ({ id, name, values }))
                          : [];
                        const instanceList = (instance && instance.length > 0)
                          ? instance.map(({ name, type, paths }) => {
                            const tempPath = _.cloneDeep(paths);
                            tempPath.forEach(pathItem => {
                              pathItem.forEach(pathSubItem => {
                                delete pathSubItem.disabled;
                              });
                            });
                            return {
                              name,
                              type,
                              path: tempPath
                            };
                          })
                          : [];
                        return {
                          id,
                          instances: instanceList,
                          attributes: attributeList
                        };
                      })
                      : [];
                    relatedResourceTypes.push({
                      type: resItem.type,
                      system_id: resItem.system_id,
                      name: resItem.name,
                      condition: conditionList.filter(
                        item => item.instances.length > 0 || item.attributes.length > 0
                      )
                    });
                  });
                }

                groupResourceTypes.push({
                  id: groupItem.id,
                  related_resource_types: relatedResourceTypes
                });
              });
              // 强制刷新下
              item.resource_groups = _.cloneDeep(item.resource_groups);
            }
            const params = {
              type,
              name,
              id,
              description,
              resource_groups: groupResourceTypes,
              environment
            };
            actionList.push(_.cloneDeep(params));
          } else {
            const { actions, aggregateResourceType, instances } = item;
            if (instances.length < 1) {
              item.isError = true;
              flag = true;
            } else {
              const params = {
                actions,
                aggregate_resource_type: {
                  id: aggregateResourceType.id,
                  system_id: aggregateResourceType.system_id,
                  instances
                }
              };
              aggregations.push(params);
            }
          }
        });
        return {
          flag,
          actions: actionList,
          aggregations
        };
      },

      selectResourceType (data, index) {
        data.selectedIndex = index;
        this.selectedIndex = index;
      },

      handleGetValue () {
        // flag：提交时校验标识
        let flag = false;
        if (this.tableList.length < 1) {
          flag = true;
          return {
            flag,
            actions: [],
            attach_actions: []
          };
        }
        const actionList = [];

        // 重新赋值
        // 资源授权与操作不一致的bug
        // if (this.isAllExpanded) {
        //     this.tableList = this.tableList.filter(e =>
        //         (e.resource_groups && e.resource_groups.length)
        //         || e.isAggregate);
        //     if (this.emptyResourceGroupsList.length) {
        //         this.emptyResourceGroupsList[0].name = this.emptyResourceGroupsName[0];
        //         this.tableList = [...this.tableList, ...this.emptyResourceGroupsList];
        //     }
        // }
        this.tableList.forEach(item => {
          const curSystemData = actionList.find(subItem => subItem.system_id === item.detail.system.id);
          if (!item.isAggregate) {
            const groupResourceTypes = [];
            if (item.resource_groups.length > 0) {
              item.resource_groups.forEach(groupItem => {
                const relatedResourceTypes = [];
                if (groupItem.related_resource_types.length > 0) {
                  groupItem.related_resource_types.forEach(resItem => {
                    if (resItem.empty) {
                      resItem.isError = true;
                      flag = true;
                    }
                    const conditionList = (resItem.condition.length > 0 && !resItem.empty)
                      ? resItem.condition.map(conItem => {
                        const { id, instance, attribute } = conItem;
                        const attributeList = (attribute && attribute.length > 0)
                          // eslint-disable-next-line max-len
                          ? attribute.map(({ id, name, values }) => ({ id, name, values })) : [];
        
                        const instanceList = (instance && instance.length > 0)
                          ? instance.map(({ name, type, path }) => {
                            const tempPath = _.cloneDeep(path);
                            tempPath.forEach(pathItem => {
                              pathItem.forEach(pathSubItem => {
                                delete pathSubItem.disabled;
                              });
                            });
                            return {
                              name,
                              type,
                              path: tempPath
                            };
                          })
                          : [];
                        return {
                          id,
                          instances: instanceList,
                          attributes: attributeList
                        };
                      })
                      : [];
                    relatedResourceTypes.push({
                      type: resItem.type,
                      system_id: resItem.system_id,
                      name: resItem.name,
                      condition: conditionList
                    });
                  });
                }
                groupResourceTypes.push({
                  id: groupItem.id,
                  related_resource_types: relatedResourceTypes
                });
              });
            }
            const params = {
              system_id: item.detail.system.id,
              actions: [
                {
                  id: item.id,
                  resource_groups: groupResourceTypes
                }
              ],
              aggregations: []
            };
            if (curSystemData) {
              curSystemData.actions.push({
                id: item.id,
                resource_groups: groupResourceTypes
              });
            } else {
              actionList.push(params);
            }
          } else {
            const { actions, aggregateResourceType, instances, instancesDisplayData } = item;
            if (instances.length < 1) {
              item.isError = true;
              flag = true;
            }
            if (instances.length > 0) {
              const aggregateResourceTypes = aggregateResourceType.reduce((p, e) => {
                if (instancesDisplayData[e.id] && instancesDisplayData[e.id].length) {
                  const obj = {};
                  obj.id = e.id;
                  obj.system_id = e.system_id;
                  obj.instances = instancesDisplayData[e.id];
                  p.push(obj);
                }
                return p;
              }, []);
              const aggregateParams = {
                system_id: item.system_id,
                aggregations: [{
                  actions,
                  aggregate_resource_types: aggregateResourceTypes
                }],
                actions: []
              };
              if (curSystemData) {
                curSystemData.aggregations.push({
                  actions,
                  aggregate_resource_types: aggregateResourceTypes
                });
              } else {
                actionList.push(aggregateParams);
              }
            }
          }
        });
        return {
          flag,
          actions: actionList
        };
      }
    }
  };
</script>

<style lang="postcss">
    .template-resource-instance-table-wrapper {
        min-height: 101px;
        .bk-table {
            width: 100%;
            margin-top: 8px;
            border-right: none;
            border-bottom: none;
            font-size: 12px;
            &.is-detail-view {
                .bk-table-body-wrapper {
                    .cell {
                        padding: 20px !important;
                    }
                }
            }
            .bk-table-header-wrapper {
                th:first-child .cell {
                    padding-left: 20px;
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
                        .remove-icon {
                            display: inline-block;
                        }
                    }
                }
                td:first-child .cell,
                th:first-child .cell {
                    /* padding-left: 15px; */
                    padding-left: 10px;
                }
                .iam-new-action {
                    display: inline-block;
                    position: relative;
                    top: 3px;
                    width: 24px;
                    vertical-align: top;
                }
            }
            .relation-content-wrapper,
            .conditions-wrapper {
                position: relative;
                height: 100%;
                padding: 17px 0;
                color: #63656e;
                .resource-type-name {
                    display: block;
                    margin-bottom: 9px;
                }
                .iam-condition-item {
                    width: 90%;
                }
            }
            .remove-icon {
                /* display: none; */
                position: absolute;
                /* top: 5px; */
                top: 5px;
                right: 0;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                }
                i {
                    font-size: 20px;
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
                margin-left: 6px;
                display: inline-block;
                vertical-align: bottom;
                word-wrap: break-word;
                word-break: break-all;
            }
            .conditions-item {
                margin-top: 7px;
                &:first-child {
                    margin-top: 0;
                }
            }
        }
    }
    .relate-instance-sideslider {
        .sideslider-content {
            height: calc(100vh - 114px);
        }
        .bk-sideslider-footer {
            background-color: #f5f6fa!important;
            border-color: #dcdee5!important;
        }
    }
    .error-tips {
        position: absolute;
        line-height: 16px;
        font-size: 10px;
        color: #ea3636;
    }

    .tab-button{
        margin: 10px 0;
    }
</style>

<style lang="postcss" scoped>
@import '@/css/mixins/space-resource-instance-table.css';
</style>
