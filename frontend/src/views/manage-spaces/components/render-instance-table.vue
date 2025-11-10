<template>
  <div class="iam-resource-instance-table-wrapper">
    <div :class="[
           'iam-resource-expand',
           extCls
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
        :border="true"
        :header-border="false"
        :cell-class-name="getCellClass"
        :empty-text="$t(`m.verify['请选择操作']`)"
        @filter-change="handleFilterChange">
        <bk-table-column :resizable="false" :label="$t(`m.common['操作']`)" width="400">
          <template slot-scope="{ row }">
            <div :class="!!row.isAggregate ? 'set-padding' : ''">
              <span class="action-name" :title="row.name">{{ row.name }}</span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column
          :resizable="false"
          :label="$t(`m.common['所属系统']`)"
          :filters="systemFilter"
          :filter-method="systemFilterMethod"
          :filter-multiple="false"
          prop="system_id"
          column-key="filterTag"
          width="240">
          <template slot-scope="{ row }">
            <span :title="row.system_name">{{ row.system_name }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" min-width="240">
          <template slot-scope="{ row, $index }">
            <div class="relation-content-wrapper" v-if="!!row.isAggregate">
              <label class="resource-type-name" v-if="row.aggregateResourceType.length === 1">
                {{ row.aggregateResourceType[0].name }}
              </label>
              <div class="bk-button-group tab-button" v-else>
                <bk-button v-for="(item, index) in row.aggregateResourceType"
                  :key="item.id" @click="selectResourceType(row, index)"
                  :class="row.selectedIndex === index ? 'is-selected' : ''"
                  size="small">{{item.name}}
                  <span v-if="!row.isNoLimited && row.instancesDisplayData[item.id]
                    && row.instancesDisplayData[item.id].length">
                    ({{row.instancesDisplayData[item.id].length}})</span>
                </bk-button>
              </div>
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
            </div>
            <div class="relation-content-wrapper" v-else>
              <template v-if="!row.isEmpty">
                <div v-for="(_, groIndex) in row.resource_groups" :key="_.id">
                  <div
                    class="relation-content-item"
                    v-for="(content, contentIndex) in _.related_resource_types"
                    :key="contentIndex"
                  >
                    <div class="content-name">
                      {{ content.name }}
                      <template v-if="row.isShowRelatedText && _.id">
                        <div style="display: inline-block; color: #979ba5;">
                          ({{ $t(`m.info['已帮您自动勾选依赖操作需要的实例']`) }})
                        </div>
                      </template>
                    </div>
                    <div class="contents">
                      <!-- eslint-disable max-len -->
                      <render-condition
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
                        @on-copy="handlerOnCopy(content, $index, contentIndex, row)"
                        @on-paste="handlerOnPaste(...arguments, content)"
                        @on-batch-paste="handlerOnBatchPaste(...arguments, content, $index, contentIndex)"
                        @on-click="showResourceInstance(row, content, contentIndex, groIndex)" />
                    </div>
                  </div>
                </div>
              </template>
              <template v-else>
                {{ $t(`m.common['无需关联实例']`) }}
              </template>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column :resizable="false" width="50">
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
      :width="resourceSliderWidth"
      quick-close
      transfer
      ext-cls="related-instance-slider"
      @update:isShow="handleResourceCancel('mask')">
      <div slot="content" class="slider-content">
        <render-resource
          ref="renderResourceRef"
          :data="condition"
          :original-data="originalCondition"
          :flag="curFlag"
          :selection-mode="curSelectionMode"
          :disabled="curDisabled"
          :params="params"
          @on-limit-change="handlerLimitChange"
          @on-init="handlerOnInit" />
      </div>
      <div slot="footer" style="margin-left: 25px;">
        <bk-button theme="primary" :disabled="disabled" :loading="sliderLoading" @click="handlerResourceSubmit">{{ $t(`m.common['保存']`) }}</bk-button>
        <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourceCancel('cancel')">{{ $t(`m.common['取消']`) }}</bk-button>
      </div>
    </bk-sideslider>

    <preview-resource-dialog
      :show="isShowPreviewDialog"
      :title="previewDialogTitle"
      :params="previewResourceParams"
      @on-after-leave="handlerPreviewDialogClose" />

    <render-aggregate-side-slider
      ref="aggregateRef"
      :show.sync="isShowAggregateSideSlider"
      :params="aggregateResourceParams"
      :value="aggregateValue"
      @on-selected="handlerSelectAggregateRes" />
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { leaveConfirm } from '@/common/leave-confirm';
  import Condition from '@/model/condition';
  import RenderAggregateSideSlider from '@/components/choose-ip/sideslider';
  import RenderCondition from '@/views/perm-apply/components/render-condition';
  import RenderResource from '@/views/manage-spaces/components/render-resource';
  import PreviewResourceDialog from '@/views/perm-apply/components/preview-resource-dialog';
  import GradePolicy from '@/model/grade-policy';
  import GradeAggregationPolicy from '@/model/grade-aggregation-policy';

  export default {
    name: 'resource-instance-table',
    provide: function () {
      return {
        getResourceSliderWidth: () => this.resourceSliderWidth
      };
    },
    components: {
      RenderResource,
      RenderCondition,
      PreviewResourceDialog,
      RenderAggregateSideSlider
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
      systemId: {
        type: String,
        default: ''
      },
      backupList: {
        type: Array,
        default: () => []
      },
      actions: {
        type: Array,
        default: () => []
      },
      isAllExpanded: {
        type: Boolean,
        default: false
      },
      maxHeight: {
        type: Number,
        default: 500
      },
      extCls: {
        type: String,
        default: ''
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
        curCopyNoLimited: false,
        isShowPreviewDialog: false,
        previewDialogTitle: '',
        previewResourceParams: {},
        curCopyData: ['none'],
        curCopyKey: '',
        isShowAggregateSideSlider: false,
        aggregateResourceParams: {},
        aggregateIndex: -1,
        aggregateValue: [],
        // 当前复制的数据形态: normal: 普通; aggregate: 聚合后
        curCopyMode: 'normal',
        curAggregateResourceType: {},
        curCopyParams: {},
        sliderLoading: false,
        systemFilter: [],
        selectedIndex: 0,
        instanceKey: '',
        curCopyDataId: '',
        emptyResourceGroupsList: [],
        emptyResourceGroupsName: [],
        curSystemActions: [],
        relatedActionsList: [],
        isExpandTable: false,
        curFilterSystem: '',
        resourceSliderWidth: Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7)
      };
    },
    computed: {
        ...mapGetters(['user']),
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
                || this.originalList.length < 1
                || !this.originalList[this.curIndex]
                || this.originalList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types.length < 1) {
                return [];
            }
            const curData = this.originalList[this.curIndex].resource_groups[this.curGroupIndex]
                .related_resource_types[this.curResIndex];
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
          this.tableList = value;
          this.isExpandTable = value.length > 0;
          this.tableList.forEach(item => {
            if (!this.systemFilter.find(subItem => subItem.value === item.system_id)) {
              this.systemFilter.push({
                text: item.system_name,
                value: item.system_id
              });
            }
          });
        },
        immediate: true
      },
      systemId: {
        handler (value) {
          if (value !== '') {
            this.curCopyKey = '';
            this.curCopyData = ['none'];
            this.curIndex = -1;
            this.curResIndex = -1;
            this.curGroupIndex = -1;
            this.aggregateResourceParams = {};
            this.aggregateIndex = -1;
            this.aggregateValue = [];
            this.curCopyMode = 'normal';
            this.curAggregateResourceType = {};
            this.curCopyParams = {};
          }
        },
        immediate: true
      }
    },
    created () {
      // 判断数组是否被另外一个数组包含
      this.isArrayInclude = (target, origin) => {
        const itemAry = [];
        target.forEach(function (p1) {
          if (origin.indexOf(p1) !== -1) {
            itemAry.push(p1);
          }
        });
        if (itemAry.length === target.length) {
          return true;
        }
        return false;
      };
    },
    methods: {
      formatFormItemWidth () {
        this.resourceSliderWidth = Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7);
      },

      async fetchActions (systemId) {
        const params = {
          system_id: systemId,
          user_id: this.user.username
        };
        try {
          const res = await this.$store.dispatch('permApply/getActions', params);
          this.curSystemActions = _.cloneDeep(res.data);
          this.handleActionLinearData();
        } catch (e) {
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      handleActionLinearData () {
        const linearActions = [];
        this.curSystemActions.forEach((item) => {
          if (['myManageSpaceCreate', 'authorBoundaryEditFirstLevel'].includes(this.$route.name)) {
            item.actions = item.actions.filter(v => !v.hidden);
          }
          item.actions.forEach(act => {
            linearActions.push(act);
          });
          (item.sub_groups || []).forEach(sub => {
            if (['myManageSpaceCreate', 'authorBoundaryEditFirstLevel'].includes(this.$route.name)) {
              sub.actions = sub.actions.filter(v => !v.hidden);
            }
            sub.actions.forEach(act => {
              linearActions.push(act);
            });
          });
        });
        this.relatedActionsList = _.cloneDeep(linearActions);
      },

      // 过滤方法
      systemFilterMethod (value, row, column) {
        const property = column.property;
        if (row.isAggregate && value === row.system_id) {
          this.curFilterSystem = `${value}-${row.$id}`;
        }
        return row[property] === value;
      },

      handleFilterChange (payload) {
        const { filterTag } = payload;
        if (!filterTag.length) {
          this.curFilterSystem = '';
        }
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

      // handlerRowMouseEnter (index) {
      //     this.$set(this.tableList[index], 'canRemove', true)
      // },

      // handlerRowMouseLeave (index) {
      //     this.$delete(this.tableList[index], 'canRemove')
      // },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 2) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      showMessage (payload) {
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: payload
        });
      },

      handlerLimitChange () {
        const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
          .related_resource_types[this.curResIndex];
        curData.isChange = true;
      },

      handlerOnInit (payload) {
        this.disabled = !payload;
      },

      showAggregateResourceInstance (data, index) {
        const aggregateResourceParams = {
          ...data.aggregateResourceType[data.selectedIndex],
          curAggregateSystemId: data.system_id,
          isNoLimited: data.isNoLimited || false
        };
        this.aggregateResourceParams = _.cloneDeep(aggregateResourceParams);
        this.aggregateIndex = !this.curFilterSystem ? index : this.tableList.findIndex(item => `${item.system_id}-${item.$id}` === this.curFilterSystem);
        const instanceKey = data.aggregateResourceType[data.selectedIndex].id;
        this.instanceKey = instanceKey;
        if (!data.instancesDisplayData[instanceKey]) data.instancesDisplayData[instanceKey] = [];
        this.aggregateValue = _.cloneDeep(data.instancesDisplayData[instanceKey].map(item => {
          return {
            id: item.id,
            display_name: item.name
          };
        }));
        this.isShowAggregateSideSlider = true;
      },

      handlerSelectAggregateRes (payload) {
        window.changeDialog = true;
        const instances = payload.map(item => {
          return {
            id: item.id,
            name: item.display_name
          };
        });
        const curAggregateItem = this.tableList[this.aggregateIndex];
        curAggregateItem.isError = false;
        this.selectedIndex = curAggregateItem.selectedIndex;
        const instanceKey = curAggregateItem.aggregateResourceType[this.selectedIndex].id;
        const instancesDisplayData = curAggregateItem.instancesDisplayData;
        curAggregateItem.instancesDisplayData = {
          ...instancesDisplayData,
          [instanceKey]: instances
        };
        curAggregateItem.instances = [];
        for (const key in curAggregateItem.instancesDisplayData) {
          curAggregateItem.instances.push(...curAggregateItem.instancesDisplayData[key]);
        }
        const conditionData = this.$refs.aggregateRef.handleGetValue();
        const { isEmpty, data } = conditionData;
        if (isEmpty) {
          return;
        }
        const isConditionEmpty = data.length === 1 && data[0] === 'none';
        if (isConditionEmpty) {
          curAggregateItem.instances = ['none'];
          curAggregateItem.isLimitExceeded = false;
          curAggregateItem.isError = true;
          curAggregateItem.isNoLimited = false;
        } else {
          // data和isEmpty都为false代表是无限制
          const isNoLimited = !isEmpty && !data.length;
          curAggregateItem.instances = data;
          curAggregateItem.isError = !(isNoLimited || data.length);
          curAggregateItem.isNoLimited = isNoLimited;
        }
        this.$set(
          this.tableList,
          this.aggregateIndex,
          new GradeAggregationPolicy({ ...curAggregateItem, ...{ isNeedNoLimited: true } })
        );
        this.$emit('on-select', this.tableList[this.aggregateIndex]);
      },

      showResourceInstance (data, resItem, resIndex, groupIndex) {
        this.params = {
          system_id: data.system_id,
          action_id: data.id,
          resource_type_system: resItem.system_id,
          resource_type_id: resItem.type
        };
        const index = this.tableList.findIndex(item => `${item.system_id}${item.id}` === `${data.system_id}${data.id}`);
        this.curIndex = index;
        this.curResIndex = resIndex;
        this.curGroupIndex = groupIndex;
        this.resourceInstanceSidesliderTitle = this.$t(`m.info['关联侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}` });
        window.changeAlert = 'iamSidesider';
        this.isShowResourceInstanceSideslider = true;
      },

      async handleMainActionSubmit (payload, relatedActions) {
        const curPayload = _.cloneDeep(payload);
        this.sliderLoading = true;
        curPayload.forEach(item => {
          item.instances = item.instance || [];
          item.attributes = item.attribute || [];
          delete item.instance;
          delete item.attribute;
        });
        const tableList = _.cloneDeep(this.tableList);
        const curData = _.cloneDeep(tableList[this.curIndex]);
        // eslint-disable-next-line max-len
        curData.resource_groups[this.curGroupIndex].related_resource_types = [curData.resource_groups[this.curGroupIndex]
          .related_resource_types[this.curResIndex]];
        curData.resource_groups[this.curGroupIndex].related_resource_types[0].condition = curPayload;
        const relatedList = tableList.filter(item => {
          return !item.isExpiredAtDisabled
            && !item.isAggregate
            && relatedActions.includes(item.id)
            && curData.system_id === item.system_id
            && item.resource_groups[this.curGroupIndex]
            && !item.resource_groups[this.curGroupIndex].related_resource_types.every(sub => sub.empty);
        });
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
          this.messageAdvancedError(e);
        } finally {
          this.sliderLoading = false;
        }
      },

      // 需要确认
      handleRelatedAction (payload) {
        if (payload.length < 1) {
          return;
        }
        payload.forEach(item => {
          const curIndex = this.tableList.findIndex(sub => sub.id === item.id
            && item.resource_groups[this.curGroupIndex]
            && sub.system_id === item.resource_groups[this.curGroupIndex]
              .related_resource_types[0].system_id && !sub.isExpiredAtDisabled);
          if (curIndex > -1) {
            this.tableList.splice(curIndex, 1, new GradePolicy({
                            ...item,
                            isShowRelatedText: true,
                            system_id: this.tableList[curIndex].system_id,
                            system_name: this.tableList[curIndex].system_name,
                            tag: 'add'
            }, 'detail'));
          }
        });
      },

      async handlerResourceSubmit () {
        window.changeDialog = true;
        const conditionData = this.$refs.renderResourceRef.handleGetValue();
        const { isEmpty, data } = conditionData;
        if (isEmpty || data[0] === 'none') {
          this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResIndex].condition = data;
          this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResIndex].isError = true;
          this.isShowResourceInstanceSideslider = false;
          return;
        }
        const { isMainAction, related_actions, id, system_id: curSystemId } = this.tableList[this.curIndex];
        // 如果为主操作
        if (isMainAction) {
          await this.handleMainActionSubmit(data, related_actions);
        }
        // 处理编辑入口，逐项编辑授权边界
        if (!isMainAction) {
          await this.fetchActions(curSystemId);
          if (this.relatedActionsList.length) {
            const policyIdList = this.tableList.map(v => v.id);
            const linearActionList = this.relatedActionsList.filter(item => policyIdList.includes(item.id));
            const curActions = linearActionList.filter(item => item.id === id);
            if (curActions.length) {
              const relatedList = curActions.map((v) => v.related_actions);
              if (relatedList.length) {
                await this.handleMainActionSubmit(data, relatedList);
              }
            }
          }
        }
        window.changeAlert = false;
        this.resourceInstanceSidesliderTitle = '';
        this.isShowResourceInstanceSideslider = false;
        this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
          .related_resource_types[this.curResIndex].condition = data;

        this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
          .related_resource_types[this.curResIndex].isError = false;

        this.curIndex = -1;
        this.curResIndex = -1;
        this.curGroupIndex = -1;
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

      handlerAggregateConditionMouseover (payload) {
        if (this.curCopyData[0] === 'none') {
          return;
        }
        if (this.curCopyKey === `${payload.aggregateResourceType.system_id}${payload.aggregateResourceType.id}`) {
          payload.canPaste = true;
        }
      },

      handlerAggregateConditionMouseleave (payload) {
        payload.canPaste = false;
      },

      handlerConditionMouseleave (payload) {
        payload.canPaste = false;
      },

      handlerOnView (payload, item, itemIndex, groupIndex) {
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
          policy_id: payload.policy_id,
          resource_group_id: payload.resource_groups[groupIndex].id,
          related_resource_type: {
            system_id,
            type,
            name,
            condition: condition.filter(item => item.attributes.length > 0 || item.instances.length > 0)
          }
        };
        this.previewDialogTitle = this.$t(`m.info['操作侧边栏操作的资源实例差异对比']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        this.isShowPreviewDialog = true;
      },

      handlerOnCopy (payload, index, subIndex, action) {
        window.changeDialog = true;
        this.curCopyKey = `${payload.system_id}${payload.type}`;
        this.curCopyData = _.cloneDeep(payload.condition);
        this.curCopyMode = 'normal';
        this.curCopyParams = this.getBatchCopyParams(action, payload);
        this.showMessage(this.$t(`m.info['实例复制']`));
        this.$refs[`condition_${index}_${subIndex}_ref`][0] && this.$refs[`condition_${index}_${subIndex}_ref`][0].setImmediatelyShow(true);
      },

      getBatchCopyParams (payload, content) {
        const actions = [];
        this.tableList.forEach(item => {
          if (!item.isAggregate) {
            if (item.id !== payload.id) {
              actions.push({
                system_id: item.system_id,
                id: item.id
              });
            }
          }
        });
        actions.unshift({
          system_id: payload.system_id,
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

      handlerAggregateOnCopy (payload, index) {
        this.instanceKey = payload.aggregateResourceType[payload.selectedIndex].id;
        this.curCopyKey = `${payload.aggregateResourceType[payload.selectedIndex].system_id}${payload.aggregateResourceType[payload.selectedIndex].id}`;
        this.curAggregateResourceType = payload.aggregateResourceType[payload.selectedIndex];
        this.curCopyData = _.cloneDeep(payload.instancesDisplayData[this.instanceKey]);
        this.curCopyDataId = payload.$id;
        this.curCopyNoLimited = payload.isNoLimited;
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
      },

      handlerOnPaste (payload, content) {
        window.changeDialog = true;
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
            item.resource_groups && item.resource_groups.forEach(groupItem => {
              groupItem.related_resource_types && groupItem.related_resource_types.forEach(subItem => {
                if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                  subItem.condition = this.curCopyNoLimited ? [] : _.cloneDeep(tempCurData);
                  subItem.isError = false;
                }
              });
            });
          } else {
            item.aggregateResourceType.forEach(aggregateResourceItem => {
              if (`${aggregateResourceItem.system_id}${aggregateResourceItem.id}` === this.curCopyKey && this.curCopyDataId !== item.$id) {
                if (Object.keys(item.instancesDisplayData).length) {
                  item.instancesDisplayData[this.instanceKey] = _.cloneDeep(tempArrgegateData);
                  if (this.curCopyNoLimited) {
                    item.instances = [];
                    item.isNoLimited = true;
                  } else {
                    item.isNoLimited = false;
                    item.instances = this.setInstanceData(item.instancesDisplayData);
                  }
                } else {
                  if (this.curCopyNoLimited) {
                    item.instances = [];
                    item.isNoLimited = true;
                  } else {
                    item.isNoLimited = false;
                    item.instances = _.cloneDeep(tempArrgegateData);
                  }
                  this.setInstancesDisplayData(item);
                }
              }
            });
            item.isError = false;
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

      handlerOnBatchPaste (payload, content, index, subIndex) {
        window.changeDialog = true;
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
                item.resource_groups && item.resource_groups.forEach(groupItem => {
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
                  if (!item.instances.length) {
                    item.isNeedNoLimited = true;
                    item.isNoLimited = true;
                  }
                  this.$emit('on-select', item);
                }
              }
            });
          } else {
            this.tableList.forEach(item => {
              if (!item.isAggregate) {
                const curPasteData = payload.data.find(_ => _.id === item.id);
                if (curPasteData) {
                  item.resource_groups && item.resource_groups.forEach(groupItem => {
                    groupItem.related_resource_types && groupItem.related_resource_types.forEach(resItem => {
                      if (`${resItem.system_id}${resItem.type}` === `${curPasteData.resource_type.system_id}${curPasteData.resource_type.type}`) {
                        resItem.condition = curPasteData.resource_type.condition.map(conditionItem => new Condition(conditionItem, '', 'add'));
                        resItem.isError = false;
                      }
                    });
                  });
                }
              } else {
                // if (`${item.aggregateResourceType[item.selectedIndex].system_id}${item.aggregateResourceType[item.selectedIndex].id}` === this.curCopyKey) {
                item.aggregateResourceType.forEach(aggregateResourceItem => {
                  if (`${aggregateResourceItem.system_id}${aggregateResourceItem.id}` === this.curCopyKey) {
                    item.instances = _.cloneDeep(tempArrgegateData);
                    this.instanceKey = aggregateResourceItem.id;
                    this.setNomalInstancesDisplayData(item, this.instanceKey);
                    this.$set(item, 'isNoLimited', false);
                    this.instanceKey = ''; // 重置
                    item.isError = false;
                  }
                });
                this.$emit('on-select', item);
                // }
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
              item.resource_groups && item.resource_groups.forEach(groupItem => {
                groupItem.related_resource_types.forEach(subItem => {
                  if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                    subItem.condition = _.cloneDeep(tempCurData);
                    subItem.isError = false;
                  }
                });
              });
            } else {
              if (`${item.aggregateResourceType.system_id}${item.aggregateResourceType.id}` === this.curCopyKey) {
                item.instances = _.cloneDeep(tempArrgegateData);
                item.isError = false;
              }
            }
          });
        }
        content.isError = false;
        this.$refs[`condition_${index}_${subIndex}_ref`][0] && this.$refs[`condition_${index}_${subIndex}_ref`][0].setImmediatelyShow(false);
        this.curCopyData = ['none'];
        this.showMessage(this.$t(`m.info['批量粘贴成功']`));
      },

      handlerPreviewDialogClose () {
        this.previewDialogTitle = '';
        this.isShowPreviewDialog = false;
      },

      handlerResourceSliderClose () {
        this.curIndex = -1;
        this.curResIndex = -1;
        this.curGroupIndex = -1;
        this.previewResourceParams = {};
        this.params = {};
      },

      resetDataAfterClose () {
        this.curIndex = -1;
        this.curResIndex = -1;
        this.curGroupIndex = -1;
        this.previewResourceParams = {};
        this.params = {};
        this.resourceInstanceSidesliderTitle = '';
      },

      handleResourceCancel (payload) {
        const typeMap = {
          mask: () => {
            const { data } = this.$refs.renderResourceRef.handleGetValue();
            const { hasSelectedCondition } = this.$refs.renderResourceRef;
            let cancelHandler = Promise.resolve();
            if (JSON.stringify(data) !== JSON.stringify(hasSelectedCondition)) {
              cancelHandler = leaveConfirm();
            }
            cancelHandler.then(() => {
              this.isShowResourceInstanceSideslider = false;
              this.resetDataAfterClose();
            }, _ => _);
          },
          cancel: () => {
            this.resetDataAfterClose();
            this.isShowResourceInstanceSideslider = false;
          }
        };
        return typeMap[payload]();
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
        this.tableList.forEach(item => {
          const curSystemData = actionList.find(subItem => subItem.system_id === item.system_id);
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
              system_id: item.system_id,
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
            const { actions, aggregateResourceType, instances, instancesDisplayData, isNoLimited } = item;
            if (!isNoLimited && (instances.length < 1 || (instances.length === 1 && instances[0] === 'none'))) {
              // 如果存在多个资源类型，只要有一项有值就允许提交
              const isError = aggregateResourceType.length > 1
                ? aggregateResourceType.every(rs => ['', this.$t(`m.verify['请选择']`)].includes(rs.displayValue))
                : true;
              item.isError = isError;
              flag = true;
            } else {
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
      },
      selectResourceType (data, index) {
        this.selectedIndex = index;
        data.selectedIndex = index;
        data.isError = ['', this.$t(`m.verify['请选择']`)].includes(data.aggregateResourceType[index].displayValue);
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import '@/css/mixins/space-resource-instance-table.css';
</style>
