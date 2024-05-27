<template>
  <div class="temp-group-sync-wrapper">
    <div
      class="temp-group-sync-table"
      v-for="(group, groupIndex) in syncGroupList"
      :key="group.id"
      :ref="`${group.name}&${group.id}`"
    >
      <div class="flex-between temp-group-sync-table-header" @click.stop="handleExpand(group)">
        <div class="temp-group-sync-table-header-left">
          <Icon bk :type="group.expand ? 'down-shape' : 'right-shape'" class="expand-icon" />
          <div :class="['group-status-btn', { 'no-fill-btn': isCurGroupEmpty(group) }]">
            <Icon :type="isCurGroupEmpty(group) ? 'unfinished' : 'check-fill'" class="fill-status" />
            <span class="fill-text">
              {{ isCurGroupEmpty(group) ? $t(`m.actionsTemplate['未填写']`) : $t(`m.actionsTemplate['已填写']`) }}
            </span>
          </div>
          <div class="single-hide group-name">{{ group.name }}</div>
        </div>
        <div class="temp-group-sync-table-header-right" v-show="group.expand" @click.stop="">
          <bk-popconfirm
            trigger="click"
            :ref="`removeSyncGroupConfirm_${group.name}_${group.id}`"
            placement="bottom-end"
            ext-popover-cls="actions-temp-resynchronize-confirm"
            :width="320"
            @confirm="handleConfirmResynchronize(group)"
          >
            <div slot="content">
              <div class="popover-title">
                <div class="popover-title-text">
                  {{ $t(`m.dialog['确认解除与该操作模板的同步？']`) }}
                </div>
              </div>
              <div class="popover-content">
                <div class="popover-content-item">
                  <span class="popover-content-item-label"
                  >{{ $t(`m.memberTemplate['用户组名称']`) }}:</span
                  >
                  <span class="popover-content-item-value"> {{ group.name }}</span>
                </div>
                <div class="popover-content-tip">
                  {{ $t(`m.actionsTemplate['解除同步后，模板权限将转为用户组自定义权限，不会再继续同步该模板的操作。']`) }}
                </div>
              </div>
            </div>
            <bk-button
              size="small"
              theme="primary"
              class="un-sync"
              text
              :loading="removeSyncLoading"
              @click.stop="handleUnSynchronize(group)"
            >
              {{ $t(`m.actionsTemplate['解除同步']`) }}
            </bk-button>
          </bk-popconfirm>
          <bk-popover :content="$t(`m.actionsTemplate['批量复用资源实例值（资源模板）到其他用户组']`)">
            <bk-button size="small" text @click.stop="handleBatchRepeat(group, 'multiple')">
              {{ $t(`m.actionsTemplate['批量复用']`) }}
            </bk-button>
          </bk-popover>
        </div>
      </div>
      <bk-table
        v-bkloading="{ isLoading: syncLoading, opacity: 1 }"
        v-if="group.expand"
        :data="group.tableList"
        col-border
        border
        size="small"
        ext-cls="temp-group-sync-table-content"
        :key="tableKey"
        :cell-class-name="getCellClass"
      >
        <bk-table-column
          :min-width="180"
          :resizable="false"
          :label="$t(`m.common['操作']`)"
        >
          <template slot-scope="{ row }">
            <span>
              <bk-tag :type="formatModeType(row.mode_type).tag" class="name-tag">
                {{ formatModeType(row.mode_type).text }}
              </bk-tag>
              <span :class="[`${row.mode_type}-name`]" v-bk-tooltips="{ content: row.name }">
                {{ row.name }}
              </span>
            </span>
          </template>
        </bk-table-column>
        <bk-table-column
          :resizable="false"
          :label="$t(`m.permApply['资源类型']`)"
        >
          <template slot-scope="{ row }">
            <div class="resource-type-content" v-if="!!row.isAggregate">
              <div class="resource-type-list" v-if="['add'].includes(row.mode_type)">
                <div
                  v-bk-tooltips="{ content: aggregate.name, placement: 'left-start' }"
                  v-for="(aggregate, index) in row.aggregateResourceType"
                  :key="aggregate.id"
                  :class="['single-hide', 'resource-type-item', { 'is-selected': row.selectedIndex === index }]"
                >
                  {{ aggregate.name }}
                </div>
              </div>
            </div>
            <div class="resource-type-content" v-else>
              <div
                v-for="resource in row.resource_groups"
                :key="resource.id"
                class="resource-type-list"
              >
                <div
                  v-bk-tooltips="{ content: related.name, placement: 'left-start' }"
                  v-for="related in resource.related_resource_types"
                  :key="related.type"
                  :class="['single-hide', 'resource-type-item', `resource-type-item-${row.mode_type}`]"
                >
                  {{ related.name }}
                </div>
              </div>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column
          :min-width="310"
          :resizable="false"
          :render-header="(h, { column, $index }) => renderResourceHeader(h, { column, $index }, group, groupIndex)"
        >
          <template slot-scope="{ row, $index }">
            <div class="relation-content-wrapper" v-if="!!row.isAggregate">
              <template v-if="!row.isEmpty">
                <template v-if="['add'].includes(row.mode_type)" class="resource-type-content">
                  <div class="resource-type-list">
                    <div
                      v-for="(resourceType, resourceTypeIndex) in row.aggregateResourceType"
                      :key="resourceType.id"
                      :class="[
                        'single-hide',
                        'relation-content-item',
                        { 'set-margin-bottom': $index === group.tableList.length - 1 }
                      ]"
                    >
                      <div class="content">
                        <render-condition
                          :ref="`condition_${$index}_${resourceTypeIndex}_aggregateRef`"
                          :value="formatDisplayValue(row, resourceTypeIndex)"
                          :is-empty="row.empty"
                          :is-error="row.isError"
                          :can-view="false"
                          :cur-copy-mode="curCopyMode"
                          :can-paste="row.canPaste"
                          @on-mouseover="handleAggregateConditionMouseover(row)"
                          @on-mouseleave="handleConditionMouseleave(row)"
                          @on-copy="handleAggregateInstanceCopy(row, $index, resourceTypeIndex)"
                          @on-paste="handleAggregateInstancePaste(row, $index, resourceTypeIndex)"
                          @on-batch-paste="handleAggregateInstanceBatchPaste(row, $index, resourceTypeIndex)"
                          @on-click="handleShowAggregateResourceSlider(row, $index, resourceTypeIndex, groupIndex)"
                        />
                      </div>
                    </div>
                  </div>
                </template>
                <template v-if="['delete'].includes(row.mode_type)">
                  <div v-for="(related, relatedIndex) in row.resource_groups" :key="related.id">
                    <div
                      class="single-hide relation-content-item"
                      v-for="(types, typesIndex) in related.related_resource_types"
                      :key="types.type"
                      @click.stop="handleViewResource(row, relatedIndex, typesIndex)"
                    >
                      <div class="content">
                        <render-resource-popover
                          :key="types.type"
                          :data="types.condition"
                          :value="types.value"
                          :max-width="400"
                          @on-view="handleViewResource(row, relatedIndex, typesIndex)"
                        />
                      </div>
                    </div>
                  </div>
                </template>
              </template>
              <template v-else>{{ $t(`m.common['无需关联实例']`) }}</template>
            </div>
            <div class="relation-content-wrapper" v-else>
              <template v-if="!row.isEmpty">
                <template v-if="['add'].includes(row.mode_type)">
                  <div v-for="(related, relatedIndex) in row.resource_groups" :key="related.id">
                    <div
                      v-for="(content, contentIndex) in related.related_resource_types"
                      :key="`${groupIndex}${contentIndex}`"
                      :class="[
                        'relation-content-item',
                        { 'set-margin-bottom':
                          (related.related_resource_types.length === 1 && curAddActions.length === 1)
                          || (group.tableList.length > 1 && group.tableList.length - 1 === $index)
                        }
                      ]"
                    >
                      <div class="content">
                        <render-condition
                          :ref="`condition_${groupIndex}_${$index}_${contentIndex}_ref`"
                          :value="content.value"
                          :params="curCopyParams"
                          :is-empty="content.empty"
                          :is-error="content.isError"
                          :cur-copy-mode="curCopyMode"
                          :can-view="row.canView"
                          :can-paste="content.canPaste"
                          @on-mouseover="handleConditionMouseover(content)"
                          @on-mouseleave="handleConditionMouseleave(content)"
                          @on-copy="handleInstanceCopy(content, groupIndex, contentIndex, $index, row)"
                          @on-paste="handleInstancePaste(...arguments, content)"
                          @on-batch-paste="handleInstanceBatchPaste(...arguments, content, $index, contentIndex)"
                          @on-click="handleShowResourceSlider(
                            row, content, contentIndex, $index, groupIndex, relatedIndex
                          )"
                        />
                      </div>
                    </div>
                  </div>
                </template>
                <template v-if="['delete'].includes(row.mode_type)">
                  <div v-for="(related, relatedIndex) in row.resource_groups" :key="related.id">
                    <div
                      class="single-hide relation-content-item"
                      v-for="(types, typesIndex) in related.related_resource_types"
                      :key="types.type"
                      @click.stop="handleViewResource(row, relatedIndex, typesIndex)"
                    >
                      <div class="content">
                        <render-resource-popover
                          :key="types.type"
                          :data="types.condition"
                          :value="types.value"
                          :max-width="400"
                          @on-view="handleViewResource(row, relatedIndex, typesIndex)"
                        />
                      </div>
                    </div>
                  </div>
                </template>
              </template>
              <template v-else>{{ $t(`m.common['无需关联实例']`) }}</template>
            </div>
          </template>
        </bk-table-column>
      </bk-table>
      <div class="pagination-wrapper" v-if="pagination.totalPage > 1">
        <div class="page-display">
          {{ pagination.current }} / {{ pagination.totalPage }}
        </div>
        <bk-button
          theme="primary"
          :loading="prevLoading"
          :disabled="pagination.current < 2"
          style="margin-left: 5px;"
          @click="handlePrevPage">
          {{ $t(`m.common['上一页']`) }}
        </bk-button>
        <bk-button
          v-if="!isLastPage"
          theme="primary"
          :loading="nextLoading"
          style="margin-left: 6px;"
          @click="handleNextPage">
          {{ isAddActionEmpty ? $t(`m.common['下一页']`) : $t(`m.common['确认']`) }}
        </bk-button>
      </div>
    </div>

    <!-- 查看资源实例详情 -->
    <bk-sideslider
      :is-show.sync="isShowSideSlider"
      :title="sideSliderTitle"
      :width="640"
      :quick-close="true"
      @animation-end="handleAnimationEnd">
      <div slot="content">
        <render-detail :data="previewData" />
      </div>
    </bk-sideslider>

    <!-- 非聚合资源视图侧边栏 -->
    <bk-sideslider
      :is-show="isShowInstanceSideSlider"
      :title="instanceSideSliderTitle"
      :width="resourceSliderWidth"
      :quick-close="true"
      :transfer="true"
      ext-cls="related-instance-sideslider"
      @update:isShow="handleResourceCancel('mask')">
      <div slot="content">
        <render-resource
          ref="renderResourceRef"
          :key="`${curIndex}${curResourceIndex}${curActionIndex}`"
          :data="condition"
          :original-data="originalCondition"
          :flag="curFlag"
          :selection-mode="curSelectionMode"
          :disabled="curDisabled"
          :params="params"
          :res-index="curResourceIndex"
          :cur-scope-action="curScopeAction"
          @on-init="handleInit"
        />
      </div>
      <div slot="footer" class="sync-group-slider-footer">
        <bk-button theme="primary" :disabled="disabled" @click="handleResourceSubmit">
          {{ $t(`m.common['保存']`) }}
        </bk-button>
        <bk-button :disabled="disabled" @click="handleResourceCancel('cancel')">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </div>
    </bk-sideslider>
    
    <!-- 聚合后的资源视图侧边栏 -->
    <RenderAggregateSideslider
      ref="aggregateRef"
      :show.sync="isShowAggregateSlider"
      :params="aggregateResourceParams"
      :is-super-manager="isSuperManager"
      :value="aggregateValue"
      :default-list="defaultSelectList"
      :is-aggregate-empty-message="isAggregateEmptyMessage"
      @on-selected="handleAggregateResourceSubmit"
    />
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { leaveConfirm } from '@/common/leave-confirm';
  import Condition from '@/model/condition';
  import SyncPolicy from '@/model/template-sync-policy';
  import AggregationPolicy from '@/model/actions-temp-aggregation-policy';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import RenderCondition from '../components/render-condition';
  import RenderDetail from '../components/render-detail';
  import RenderResource from '../components/render-resource';
  import RelateResourceTypes from '@/model/related-resource-types';
  import RenderAggregateSideslider from '@/components/choose-ip/sideslider';

  export default {
    provide: function () {
      return {
        getResourceSliderWidth: () => this.resourceSliderWidth
      };
    },
    components: {
      RenderResourcePopover,
      RenderCondition,
      RenderDetail,
      RenderResource,
      RenderAggregateSideslider
    },
    props: {
      id: {
        type: [String, Number],
        default: ''
      },
      cloneAction: {
        type: Array,
        default: () => []
      },
      addActions: {
        type: Array,
        default: () => []
      },
      allActions: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        syncLoading: false,
        removeSyncLoading: false,
        nextLoading: false,
        isLastPage: false,
        prevLoading: false,
        disabled: false,
        curCopyNoLimited: false,
        isShowSideSlider: false,
        isShowInstanceSideSlider: false,
        isShowAggregateSlider: false,
        isAggregateEmptyMessage: false,
        instanceKey: '',
        curCopyKey: '',
        curCopyDataId: '',
        sideSliderTitle: '',
        instanceSideSliderTitle: '',
        curCopyMode: 'normal',
        tableKey: -1,
        curIndex: -1,
        curActionIndex: -1,
        curResourceIndex: -1,
        curGroupIndex: -1,
        aggregateIndex: -1,
        selectedIndex: 0,
        syncGroupList: [],
        deleteProps: [],
        addProps: [],
        previewData: [],
        originalList: [],
        curAddActions: [],
        addActionsList: [],
        authorizationScopeActions: [],
        defaultSelectList: [],
        aggregateValue: [],
        curCopyData: ['none'],
        requestQueue: ['scope', 'group'],
        params: {},
        curRemoveSyncData: {},
        curScopeAction: {},
        curCopyParams: {},
        curCopyAggregateParams: {},
        curAggregateResourceType: {},
        aggregateResourceParams: {},
        pagination: {
          current: 1,
          limit: 100,
          totalPage: 0
        },
        resourceSliderWidth: Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7)
      };
    },
    computed: {
      ...mapGetters('permTemplate', ['cloneActions']),
      ...mapGetters(['user']),
      isSuperManager () {
        return this.user.role.type === 'super_manager';
      },
      isCurGroupEmpty () {
        return (payload) => {
          if (payload.tableList && payload.tableList.length > 0) {
            const hasEmptyData = payload.tableList.some((item) => {
              if (item.resource_groups && item.resource_groups.length && ['add'].includes(item.mode_type)) {
               return item.resource_groups.some((v) => {
                 return v.related_resource_types.some((related) => related.condition.length === 1 && related.condition[0] === 'none');
                });
              }
            });
            this.$set(payload, 'fill_status', !hasEmptyData);
            return hasEmptyData;
          }
          return true;
        };
      },
      isCurGroupAllEmpty () {
        return (payload) => {
          let isEmpty = false;
          payload.tableList.every((item) => {
            if (['add'].includes(item.mode_type)) {
              isEmpty = item.resource_groups && item.resource_groups.every((v) => {
                const noCondition = v.related_resource_types.every((related) => related.condition.length === 1 && related.condition[0] === 'none');
                return noCondition;
              });
              return isEmpty;
            }
          });
          return isEmpty;
        };
      },
      isUnlimitedDisabled () {
        return (payload) => {
          const isDisabled = payload.tableList.every(item =>
            ((!item.resource_groups || (item.resource_groups && !item.resource_groups.length)) && !item.instances)
            );
          return isDisabled;
        };
      },
      condition () {
        if (
          this.curIndex === -1
          || this.curResourceIndex === -1
          || this.curActionIndex === -1
          || this.curGroupIndex === -1) {
            return [];
        }
        const curData = this.syncGroupList[this.curIndex]
            .tableList[this.curActionIndex].resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResourceIndex];
        if (!curData) {
            return [];
        }
        return cloneDeep(curData.condition);
      },
      originalCondition () {
        if (this.curIndex === -1
          || this.curResourceIndex === -1
          || this.curActionIndex === -1
          || this.curGroupIndex === -1
          || this.originalList.length < 1) {
          return [];
        }
        const curId = this.syncGroupList[this.curIndex].tableList[this.curActionIndex].id;
        const curType = this.syncGroupList[this.curIndex]
            .tableList[this.curActionIndex]
            .resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResourceIndex]
            .type;
        if (!this.originalList.some(item => item.tableList[this.curActionIndex].id === curId)) {
          return [];
        }
        const curData = this.originalList.find(item => item.tableList[this.curActionIndex].id === curId);
        if (!curData) {
          return [];
        }
        const curActionData = curData.tableList[this.curActionIndex].resource_groups[this.curGroupIndex];
        if (!curActionData.related_resource_types.some(item => item.type === curType)) {
          return [];
        }
        const curResData = curActionData.related_resource_types.find(item => item.type === curType);
        if (!curResData) {
          return [];
        }
        return cloneDeep(curResData.condition);
      },
      curDisabled () {
        if (
          this.curIndex === -1
          || this.curResourceIndex === -1
          || this.curActionIndex === -1
          || this.curGroupIndex === -1) {
          return false;
        }
        const curData = this.syncGroupList[this.curIndex]
            .tableList[this.curActionIndex]
            .resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResourceIndex];
        return curData.isDefaultLimit;
      },
      curFlag () {
          if (this.curIndex === -1
              || this.curResourceIndex === -1
              || this.curActionIndex === -1
              || this.curGroupIndex === -1) {
              return 'add';
          }
          const curData = this.syncGroupList[this.curIndex]
              .tableList[this.curActionIndex]
              .resource_groups[this.curGroupIndex]
              .related_resource_types[this.curResourceIndex];
          return curData.flag;
      },
      curSelectionMode () {
        if (this.curIndex === -1
            || this.curResourceIndex === -1
            || this.curActionIndex === -1
            || this.curGroupIndex === -1) {
            return 'all';
        }
        const curData = this.syncGroupList[this.curIndex]
            .tableList[this.curActionIndex]
            .resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResourceIndex];
        return curData.selectionMode;
      },
      isAddActionEmpty () {
        return this.curAddActions.length < 1;
      },
      formatModeType () {
        return (payload) => {
          const result = {
            tag: 'success',
            text: this.$t(`m.common['新增']`)
          };
          const modeMap = {
            add: () => {
              return {
                tag: 'success',
                text: this.$t(`m.common['新增']`)
              };
            },
            delete: () => {
              return {
                tag: 'danger',
                text: this.$t(`m.common['移除']`)
              };
            }
          };
          if (modeMap[payload]) {
            return modeMap[payload]();
          }
          return result;
        };
      },
      // 处理无限制和聚合后多个tab数据结构不兼容情况
      formatDisplayValue () {
        return (payload, index) => {
          const { isNoLimited, empty, value, aggregateResourceType } = payload;
          if (value && aggregateResourceType[index]) {
            let displayValue = aggregateResourceType[index].displayValue;
            if (isNoLimited || empty) {
              displayValue = value;
            }
            return displayValue;
          }
        };
      }
    },
    watch: {
      addActions: {
        handler (value) {
          this.curAddActions = [...value];
        },
        immediate: true
      }
    },
    async mounted () {
      this.curCopyKey = '';
      await this.fetchGroupsPreview();
      this.fetchAuthorizationScopeActions();
      this.handleGetBusData();
    },
    methods: {
      formatFormItemWidth () {
        this.resourceSliderWidth = Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7);
      },

      async fetchGroupsPreview () {
        try {
          const { current, limit } = this.pagination;
          const params = {
            id: this.id,
            data: {
              limit,
              offset: limit * (current - 1)
            }
          };
          const { data } = await this.$store.dispatch('permTemplate/getGroupsPreview', params);
          this.pagination.totalPage = Math.ceil(data.count / limit);
          this.syncGroupList = cloneDeep(data.results || []);
          this.syncGroupList.forEach((item, index) => {
            this.$set(item, 'expand', !(index > 0));
            this.$set(item, 'tableList', []);
            if (index === 0) {
              this.$emit('on-expand', item);
            }
            if (this.curAddActions.length > 0) {
              this.$set(item, 'add_actions', cloneDeep(this.curAddActions));
              item.add_actions = item.add_actions.map(act => {
                if (!act.resource_groups || !act.resource_groups.length) {
                  act.resource_groups = [];
                  if (act.related_resource_types && act.related_resource_types.length > 0) {
                    act.resource_groups = [{ id: '', related_resource_types: act.related_resource_types }];
                  }
                }
                const result = new SyncPolicy({ ...act, tag: 'add' }, 'detail');
                this.$set(result, 'mode_type', 'add');
                item.tableList.push(result);
                return result;
              });
              this.addActionsList.push({ ...item, ...{ tableList: item.tableList.filter((v) => !['delete'].includes(v.mode_type)) } });
            }
            item.delete_actions = item.delete_actions.map((act) => {
              if (!act.resource_groups || !act.resource_groups.length) {
                act.resource_groups = [];
                if (act.related_resource_types && act.related_resource_types.length > 0) {
                  act.resource_groups = [{ id: '', related_resource_types: act.related_resource_types }];
                }
              }
              const result = new SyncPolicy({ ...act, tag: 'add' }, 'detail');
              this.$set(result, 'mode_type', 'delete');
              item.tableList.push(result);
              return result;
            });
          });
          this.setTableProps();
          this.originalList = cloneDeep(this.syncGroupList);
          this.isLastPage = current === this.pagination.totalPage;
          this.handleGetTypeData();
          this.$emit('on-all-submit', this.isLastPage);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
        }
      },

      async fetchAuthorizationScopeActions () {
        try {
          const { data } = await this.$store.dispatch('permTemplate/getAuthorizationScopeActions', {
            systemId: this.$route.params.systemId
          });
          this.authorizationScopeActions = (data || []).filter(item => item.id !== '*');
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
        }
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        let hasMultipleResourceType = false;
        if (row.isAggregate) {
          hasMultipleResourceType = row.aggregateResourceType && row.aggregateResourceType.length > 1;
        } else {
          hasMultipleResourceType = row.resource_groups && row.resource_groups.some((item) => {
            return item.related_resource_types.length > 1;
          });
        }
        if (columnIndex === 1) {
          if (hasMultipleResourceType) {
            return 'resource-type-cell-cls';
          }
        }
        if (columnIndex === 2) {
          if (['add'].includes(row.mode_type)) {
            if (hasMultipleResourceType) {
              return 'resource-instance-add-cell-cls multiple-resource-type-instance';
            }
            return 'resource-instance-add-cell-cls';
          }
          if (['delete'].includes(row.mode_type)) {
            if (hasMultipleResourceType) {
              return 'resource-instance-delete-cell-cls multiple-resource-type-instance';
            }
            return 'resource-instance-delete-cell-cls';
          }
          return '';
        }
        return '';
      },
 
      getBatchCopyParams (payload, content) {
        const actions = [];
        const { systemId } = this.$route.params;
        this.syncGroupList.forEach(item => {
          item.add_actions.forEach(act => {
            if (act.id !== payload.id) {
              actions.push({
                system_id: systemId,
                id: act.id
              });
            }
          });
        });
        actions.unshift({
          system_id: systemId,
          id: payload.id
        });
        return {
          resource_type: {
            system_id: content.system_id,
            type: content.type,
            condition: content.condition.map(item => {
              return {
                id: item.id || '',
                instances: item.instance || [],
                attributes: item.attribute || []
              };
            })
          },
          actions
        };
      },

      // 格式化提交数据
      getData () {
        let flag = false;
        let isNoAdd = false;
        const groups = [];
        this.syncGroupList.forEach((item) => {
          const actionList = [];
          (item.tableList || []).forEach((sub) => {
            const { type, id, name, environment, description, mode_type } = sub;
            if (['add'].includes(mode_type)) {
              const relatedResourceTypes = [];
              const groupResourceTypes = [];
              if (sub.resource_groups.length > 0) {
                sub.resource_groups.forEach((groupItem) => {
                  if (groupItem.related_resource_types.length > 0) {
                    groupItem.related_resource_types.forEach((resItem) => {
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
                            ? instance.map(({ name, type, path, paths }) => {
                              let tempPath = cloneDeep(paths);
                              if (!tempPath.length && path && path.length) {
                                tempPath = cloneDeep(path);
                              }
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
                        condition: conditionList.filter((item) =>
                          item.instances.length > 0 || item.attributes.length > 0
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
                sub.resource_groups = cloneDeep(sub.resource_groups);
              }
              const params = {
                type,
                name,
                id,
                description,
                resource_groups: groupResourceTypes,
                environment
              };
              actionList.push(params);
            }
          });
          groups.push({
            id: item.id,
            actions: actionList
          });
        });
        isNoAdd = groups.every(item => item.actions.length < 1);
        return {
          flag,
          groups,
          isNoAdd
        };
      },

      handleExpand (payload) {
        payload.expand = !payload.expand;
        this.syncGroupList.forEach((item) => {
          this.$set(item, 'expand', payload.id === item.id ? payload.expand : false);
        });
        this.$emit('on-expand', payload);
      },

      async handleConfirmResynchronize () {
        const { id } = this.curRemoveSyncData;
        const params = {
          id: this.id,
          data: {
            members: [{
              id,
              type: 'group'
            }]
          }
        };
        this.removeSyncLoading = true;
        try {
          await this.$store.dispatch('permTemplate/deleteTemplateMember', params);
          this.messageSuccess(this.$t(`m.info['移除成功']`), 3000);
          this.fetchGroupsPreview();
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.removeSyncLoading = false;
        }
      },

      async handlePrevPage () {
        window.changeDialog = true;
        if (this.pagination.current > 1) {
          --this.pagination.current;
        }
        this.requestQueue = ['group'];
        await this.fetchGroupsPreview();
      },

      async handleNextPage () {
        window.changeDialog = true;
        if (this.isAddActionEmpty) {
          if (this.pagination.current < this.pagination.totalPage) {
            ++this.pagination.current;
            this.requestQueue = ['group'];
            this.fetchGroupsPreview();
          }
          return;
        }
        const { groups, flag } = this.getData();
        if (flag) {
          return;
        }
        this.nextLoading = true;
        try {
          await this.$store.dispatch('permTemplate/preGroupSync', {
            id: this.id,
            data: {
              groups
            }
          });
          if (this.pagination.current < this.pagination.totalPage) {
            ++this.pagination.current;
            this.requestQueue = ['group'];
            this.fetchGroupsPreview();
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.nextLoading = false;
        }
      },

      async handleBatchRepeat (payload, mode) {
        if (this.isCurGroupAllEmpty(payload) && !['all'].includes(mode)) {
          this.messageWarn(this.$t(`m.common['暂无可批量复用实例']`), 3000);
          return;
        }
        console.log(payload.tableList);
        let params = {};
        const relatedList = [];
        payload.tableList.forEach((item) => {
          if (['add'].includes(item.mode_type)) {
            if (!item.isAggregate) {
              item.resource_groups && item.resource_groups.forEach((v) => {
                v.related_resource_types.forEach((related) => {
                  if ((related.condition.length > 0 && related.condition !== 'none') || related.condition.length === 0) {
                    params = this.getBatchCopyParams(item, related);
                    relatedList.push(params);
                  }
                });
              });
            } else {
              const tempAggregateData = [];
              item.aggregateResourceType.forEach((aggregateResourceItem) => {
                if (`${aggregateResourceItem.system_id}${aggregateResourceItem.id}` === this.curCopyKey) {
                  if (Object.keys(item.instancesDisplayData).length) {
                    if (this.curCopyNoLimited) {
                      item = Object.assign(item, { isNoLimited: true, instances: [] });
                    } else {
                      item = Object.assign(item, {
                        isNoLimited: false,
                        instances: this.setInstanceData(item.instancesDisplayData)
                      });
                    }
                  } else {
                    if (this.curCopyNoLimited) {
                      item = Object.assign(item, { isNoLimited: true, instances: [] });
                    } else {
                      item = Object.assign(item, { isNoLimited: false, instances: cloneDeep(tempAggregateData) });
                    }
                    this.setInstancesDisplayData(item);
                  }
                }
              });
              item.isError = false;
            }
          }
        });
        // 如果是无限制或者空资源实例无需调用接口，否则会导致报错
        const paramsList = relatedList.filter((item) =>
          item.resource_type.condition
          && (item.resource_type.condition.length > 0 && item.resource_type.condition[0] !== 'none')
          && item.resource_type.condition.some((v) => v.instances.length > 0 || v.attributes.length > 0)
        );
        // 处理无限制的数据
        const noLimitedList = relatedList.filter((item) => item.resource_type.condition.length === 0);
        if (noLimitedList.length) {
          for (let i = 0; i < noLimitedList.length; i++) {
            this.syncGroupList.forEach((item, index) => {
              this.handleSetNoLimitedData(item, index, noLimitedList[i]);
            });
          }
        }
        if (paramsList.length > 0) {
          try {
            for (let i = 0; i < paramsList.length; i++) {
              const { data } = await this.$store.dispatch('permApply/resourceBatchCopy', paramsList[i]);
              const { resource_type } = paramsList[i];
              if (data && data.length) {
                this.syncGroupList.forEach((item) => {
                  item.tableList.forEach((v) => {
                    const curPasteData = data.find(_ => _.id === v.id);
                    if (curPasteData) {
                      v.resource_groups && v.resource_groups.forEach(groupItem => {
                        groupItem.related_resource_types.forEach(subItem => {
                          if (`${subItem.system_id}${subItem.type}` === `${resource_type.system_id}${resource_type.type}`) {
                            subItem.condition = curPasteData.resource_type.condition.map(conditionItem => new Condition(conditionItem, '', 'add'));
                            subItem.isError = false;
                          }
                        });
                      });
                    }
                  });
                });
              } else {
                this.messageWarn(this.$t(`m.info['暂无可批量复制包含有属性条件的资源实例']`), 3000);
              }
            }
          } catch (e) {
            this.messageAdvancedError(e);
          }
        }
        this.handleGetTypeData();
      },

      async handleGroupNoLimited (payload, groupIndex) {
        if (this.isUnlimitedDisabled(payload)) {
          return;
        }
        await this.handleSetNoLimitedData(payload, groupIndex, { mode: 'all' });
        this.handleGetTypeData();
      },

      handleSetNoLimitedData (payload, groupIndex, extraData) {
        const { tableList } = payload;
        const tableData = cloneDeep(tableList);
        tableData.forEach((item, index) => {
          if (['add'].includes(item.mode_type)) {
            const curScopeAction = this.authorizationScopeActions.find((v) => v.id === item.id);
            if (!item.isAggregate) {
              if (item.resource_groups && item.resource_groups.length) {
                item.resource_groups.forEach((groupItem) => {
                  groupItem.related_resource_types && groupItem.related_resource_types.forEach((types) => {
                    // 处理授权范围不是无限制的场景
                    if (curScopeAction) {
                      const { name, type } = curScopeAction;
                      const curData = new RelateResourceTypes(types, { name, type }, 'detail');
                      if (curData.condition.length > 0) {
                        return;
                      }
                    }
                    // 如果是直接设置无限制
                    if (extraData && ['all'].includes(extraData.mode)) {
                      types.condition = payload ? [] : ['none'];
                      if (payload) {
                        types.isError = false;
                      }
                    }
                    // 如果是有判断条件才设置无限制
                    if (extraData && extraData.resource_type) {
                      if (`${types.system_id}${types.type}` === `${extraData.resource_type.system_id}${extraData.resource_type.type}`) {
                        types = Object.assign(types, { isError: false, condition: [] });
                      }
                    }
                  });
                });
              } else {
                item.name = item.name.split('，')[0];
              }
            }
            if (item.instances && item.isAggregate) {
              item.isNoLimited = false;
              item.isError = !(item.instances.length || (!item.instances.length && item.isNoLimited));
              item.isNeedNoLimited = true;
              if (!payload || item.instances.length) {
                item.isNoLimited = false;
                item.isError = false;
              }
              if ((!item.instances.length && !payload && item.isNoLimited) || payload) {
                item.isNoLimited = true;
                item.isError = false;
                item.instances = [];
              }
              return this.$set(
                tableData,
                index,
                new AggregationPolicy({ ...item, ...{ mode_type: 'add' } })
              );
            }
          }
        });
        this.$set(this.syncGroupList[groupIndex], 'tableList', tableData);
      },

      handleUnSynchronize (payload) {
        this.$nextTick(() => {
          const { id, name } = payload;
          const removeSync = this.$refs[`removeSyncGroupConfirm_${name}_${id}`];
          if (removeSync && removeSync.length) {
            this.curRemoveSyncData = { ...payload };
            removeSync[0].$refs && removeSync[0].$refs.popover.showHandler();
          }
        });
      },

      handleInstanceCopy (payload, $index, subIndex, index, action) {
        this.curCopyMode = 'normal';
        this.curCopyKey = `${payload.system_id}${payload.type}`;
        this.curCopyData = cloneDeep(payload.condition);
        this.curCopyParams = this.getBatchCopyParams(action, payload);
        const conditionRef = this.$refs[`condition_${index}_${$index}_${subIndex}_ref`];
        if (conditionRef && conditionRef.length > 0) {
          conditionRef[0].setImmediatelyShow(true);
        }
        this.messageSuccess(this.$t(`m.info['实例复制']`), 3000);
      },

      handleInstancePaste (payload, content) {
        console.log(payload, content, 5555);
        if (!payload.flag) {
          return;
        }
        // content没有且curCopyMode为aggregate代表粘贴的是聚合后的数据
        if ((!content || !content.system_id) && ['aggregate'].includes(this.curCopyMode)) {
          if (payload && this.curCopyKey !== `${payload.system_id}${payload.type}`) {
            this.messageWarn(this.$t(`m.common['暂无可复制实例']`), 3000);
            return;
          }
          this.handleInstanceBatchPaste(payload);
          return;
        }
        if (!content || this.curCopyKey !== `${content.system_id}${content.type}`) {
          this.messageWarn(this.$t(`m.common['暂无可复制实例']`), 3000);
          return;
        }
        content.condition = payload.data.length > 0 ? payload.data.map(conditionItem => new Condition(conditionItem, '', 'add')) : [];
        content.isError = false;
        this.messageSuccess(this.$t(`m.info['粘贴成功']`), 3000);
      },

      handleInstanceBatchPaste  (payload, content, index) {
        let tempCurData = ['none'];
        let tempAggregateData = [];
        if (this.curCopyMode === 'normal') {
          if (!payload.flag) {
            return;
          }
          // 预计算是否存在 聚合后的数据 可以粘贴
          const flag = this.syncGroupList.some((item) => {
            return item.tableList && item.tableList.some((v) => {
              return !!v.isAggregate
                && v.aggregateResourceType.some((sub) => `${sub.system_id}${sub.id}` === this.curCopyKey);
            });
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
                tempAggregateData = instanceData.path.map(pathItem => {
                  return {
                    id: pathItem[0].id,
                    name: pathItem[0].name
                  };
                });
              }
            }
          }
          if (payload.data.length === 0) {
            this.syncGroupList.forEach((group) => {
              group.tableList && group.tableList.forEach((item) => {
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
                    item.instances = cloneDeep(tempAggregateData);
                    item.isError = false;
                    if (!item.instances.length) {
                      item.isNeedNoLimited = true;
                      item.isNoLimited = true;
                    }
                    this.$emit('on-select', item);
                  }
                }
              });
            });
          } else {
            const curCopyData = JSON.parse(JSON.stringify(payload.data));
            this.syncGroupList.forEach((group) => {
              group.tableList && group.tableList.forEach(item => {
                if (!item.isAggregate) {
                  const curPasteData = cloneDeep(curCopyData.find(_ => _.id === item.id));
                  if (curPasteData) {
                    const systemId = this.isCreateMode && item.detail ? item.detail.system.id : this.systemId;
                    const scopeAction = this.authorization[systemId] || [];
                    // eslint-disable-next-line max-len
                    const curScopeAction = cloneDeep(scopeAction.find(scopeItem => scopeItem.id === item.id));
                    // eslint-disable-next-line max-len
                    if (curScopeAction && curScopeAction.resource_groups && curScopeAction.resource_groups.length) {
                      curScopeAction.resource_groups.forEach(curScopeActionItem => {
                        curScopeActionItem.related_resource_types.forEach(curResItem => {
                          console.log('curResItem', curResItem, curPasteData, this.curCopyParams.resource_type);
                          if (`${curResItem.system_id}${curResItem.type}` === `${curPasteData.resource_type.system_id}${curPasteData.resource_type.type}`) {
                            // eslint-disable-next-line max-len
                            let canPasteName = [];
                            let hasConditionData = [];
                            let noConditionData = [];
                            if (curResItem.condition && curResItem.condition.length) {
                              hasConditionData = curResItem.condition[0].instances[0].path.reduce((p, v) => {
                                p.push(v[0].name);
                                return p;
                              }, []);
                            } else {
                              // 处理分级管理员下多个无限制操作的批量粘贴
                              if (this.curCopyParams.resource_type.condition
                                && this.curCopyParams.resource_type.condition.length) {
                                let instancesData = this.curCopyParams.resource_type.condition[0].instances;
                                if (!instancesData) {
                                  instancesData = this.curCopyParams.resource_type.condition[0].instance;
                                }
                                noConditionData = instancesData[0].path.reduce((p, v) => {
                                  p.push(v[0].name);
                                  return p;
                                }, []);
                              }
                            }
                            canPasteName = [...hasConditionData, ...noConditionData];
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
                                  console.log('condition', condition);
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
                  const scopeAction = cloneDeep(curCopyData.find(_ => item.actions.map((v) => v.id).includes(_.id)));
                  item.aggregateResourceType && item.aggregateResourceType.forEach(aggregateResourceItem => {
                    const systemId = this.isSuperManager
                      ? aggregateResourceItem.system_id : item.system_id;
                    if (`${systemId}${aggregateResourceItem.id}` === this.curCopyKey && scopeAction) {
                      item.instances = cloneDeep(tempAggregateData);
                      this.instanceKey = aggregateResourceItem.id;
                      this.setNomalInstancesDisplayData(item, this.instanceKey);
                      this.instanceKey = ''; // 重置
                      item.isError = false;
                      this.$set(item, 'isNoLimited', false);
                      item.isNeedNoLimited = true;
                    }
                  });
                  this.$emit('on-select', item);
                }
              });
            });
          }
        } else {
          tempAggregateData = this.curCopyData;
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
          this.syncGroupList.forEach((group) => {
            group.tableList && group.tableList.forEach((item) => {
              if (!item.isAggregate) {
                item.resource_groups && item.resource_groups.forEach((groupItem) => {
                  groupItem.related_resource_types
                    && groupItem.related_resource_types.forEach((subItem, subItemIndex) => {
                      if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                        subItem.condition = cloneDeep(tempCurData);
                        subItem.isError = false;
                        this.$emit('on-resource-select', index, subItemIndex, subItem.condition);
                      }
                    });
                });
              } else {
                if (`${item.aggregateResourceType.system_id}${item.aggregateResourceType.id}` === this.curCopyKey) {
                  item.instances = cloneDeep(tempAggregateData);
                  item.isError = false;
                  this.$emit('on-select', item);
                }
              }
            });
          });
        }
        if (Object.prototype.toString.call(content) === '[object Object]') {
          content.isError = false;
        }
        this.curCopyData = ['none'];
      },

      handleAggregateInstanceCopy (payload, index, resourceTypeIndex) {
        window.changeDialog = true;
        const aggregateRef = this.$refs[`condition_${index}_${resourceTypeIndex}_aggregateRef`];
        const { aggregationId, aggregateResourceType, isNoLimited, instancesDisplayData } = payload;
        const { id, system_id: systemId } = aggregateResourceType[resourceTypeIndex];
        this.curCopyMode = 'aggregate';
        this.instanceKey = id;
        this.curCopyDataId = aggregationId;
        this.curCopyNoLimited = isNoLimited;
        this.curCopyKey = `${systemId}${id}`;
        this.curAggregateResourceType = aggregateResourceType[resourceTypeIndex];
        this.curCopyData = cloneDeep(instancesDisplayData[this.instanceKey]);
        this.messageSuccess(this.$t(`m.info['实例复制']`), 3000);
        if (aggregateRef && aggregateRef.length) {
          aggregateRef[0].setImmediatelyShow(true);
        }
      },

      handleAggregateInstancePaste (payload) {
        let tempInstances = [];
        if (this.curCopyMode === 'aggregate') {
          tempInstances = this.curCopyData;
        } else {
          if (this.curCopyData[0] !== 'none') {
            const instances = this.curCopyData.map(item => item.instance);
            const instanceData = instances[0][0];
            tempInstances = instanceData.path.map((pathItem) => {
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
        payload = Object.assign(payload, { isError: false, instances: tempInstances });
        this.messageSuccess(this.$t(`m.info['粘贴成功']`), 3000);
        console.log(tempInstances, this.curCopyData);
      },

      handleAggregateInstanceBatchPaste (payload, index, resourceTypeIndex) {
        console.log(payload);
        let tempCurData = ['none'];
        let tempAggregateData = [];
        if (this.curCopyMode === 'normal') {
          if (this.curCopyData[0] !== 'none') {
            tempCurData = this.curCopyData.map((item) => {
              delete item.id;
              return item;
            });
            const instances = this.curCopyData.map((item) => item.instance);
            const instanceData = instances[0][0];
            tempAggregateData = instanceData.path.map((pathItem) => {
              return {
                id: pathItem[0].id,
                name: pathItem[0].name
              };
            });
          }
        } else {
          tempAggregateData = this.curCopyData;
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
        payload.tableList.forEach((item) => {
          if (!item.isAggregate) {
            item.resource_groups.forEach((groupItem) => {
              groupItem.related_resource_types && groupItem.related_resource_types.forEach(subItem => {
                if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                  subItem.condition = this.curCopyNoLimited ? [] : cloneDeep(tempCurData);
                  subItem.isError = false;
                }
              });
            });
          } else {
            item.aggregateResourceType.forEach((aggregateResourceItem) => {
              if (`${aggregateResourceItem.system_id}${aggregateResourceItem.id}` === this.curCopyKey) {
                if (Object.keys(item.instancesDisplayData).length) {
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
                    item.instances = cloneDeep(tempAggregateData);
                  }
                  this.setInstancesDisplayData(item);
                }
              }
            });
            item.isError = false;
          }
        });
        payload.isError = false;
        this.curCopyData = ['none'];
        const conditionRef = this.$refs[`condition_${index}_${resourceTypeIndex}_aggregateRef`][0];
        conditionRef && conditionRef.setImmediatelyShow(false);
        this.messageSuccess(this.$t(`m.info['批量粘贴成功']`), 3000);
      },

      handleShowResourceSlider (row, content, contentIndex, $index, groupIndex, relatedIndex) {
        this.params = {
          system_id: this.$route.params.systemId,
          action_id: row.id,
          resource_type_system: content.system_id,
          resource_type_id: content.type
        };
        this.curScopeAction = this.authorizationScopeActions.find(item => item.id === row.id);
        this.curIndex = groupIndex;
        this.curActionIndex = $index;
        this.curResourceIndex = contentIndex;
        this.curGroupIndex = relatedIndex;
        this.instanceSideSliderTitle = this.$t(
          `m.info['关联侧边栏操作的资源实例']`,
          {
            value: `${this.$t(`m.common['【']`)}${row.name}${this.$t(`m.common['】']`)}`
          }
        );
        this.isShowInstanceSideSlider = true;
        window.changeAlert = 'iamSidesider';
      },

      handleShowAggregateResourceSlider (data, index, resourceTypeIndex, groupIndex) {
        window.changeDialog = true;
        this.curIndex = groupIndex;
        this.aggregateIndex = index;
        this.selectedIndex = resourceTypeIndex;
        const aggregateResourceParams = {
          ...data.aggregateResourceType[resourceTypeIndex],
          curAggregateSystemId: data.system_id,
          isNoLimited: data.isNoLimited || false,
          actionsId: data.actions.map((item) => item.id)
        };
        this.aggregateResourceParams = cloneDeep(aggregateResourceParams);
        this.instanceKey = aggregateResourceParams.id;
        if (!data.instancesDisplayData[this.instanceKey]) {
          data.instancesDisplayData[this.instanceKey] = [];
        }
        this.aggregateValue = cloneDeep(data.instancesDisplayData[this.instanceKey].map(item => {
          return {
            id: item.id,
            display_name: item.name
          };
        }));
        this.defaultSelectList = this.handleGetScopeActionResource(
          data.actions,
          data.aggregateResourceType[data.selectedIndex].id,
          data.system_id
        );
        this.isShowAggregateSlider = true;
      },

      handleAggregateResourceSubmit (payload) {
        const instances = payload.map(item => {
          return {
            id: item.id,
            name: item.display_name
          };
        });
        let curAggregateItem = this.syncGroupList[this.curIndex].tableList[this.aggregateIndex];
        curAggregateItem = Object.assign(curAggregateItem, { isError: false, instances: [] });
        const instanceKey = curAggregateItem.aggregateResourceType[this.selectedIndex].id;
        const instancesDisplayData = curAggregateItem.instancesDisplayData;
        curAggregateItem.instancesDisplayData = {
          ...instancesDisplayData,
          [instanceKey]: instances
        };
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
          curAggregateItem = Object.assign(curAggregateItem, {
            instances: ['none'],
            isError: true,
            isNoLimited: false,
            isLimitExceeded: false
          });
        } else {
          // data和isEmpty都为false代表是无限制
          const isNoLimited = !isEmpty && !data.length;
          curAggregateItem = Object.assign(curAggregateItem, {
            instances: data,
            isError: !(isNoLimited || data.length),
            isNoLimited: isNoLimited
          });
        }
        this.$set(
          this.syncGroupList[this.curIndex].tableList,
          this.aggregateIndex,
          new AggregationPolicy({ ...curAggregateItem, ...{ isNeedNoLimited: true } })
        );
        this.$emit('on-select', this.syncGroupList[this.curIndex].tableList[this.aggregateIndex]);
      },

      handleViewResource (payload, relatedIndex, typesIndex) {
        const params = [];
        const resourceGroup = payload.resource_groups[relatedIndex];
        if (resourceGroup.related_resource_types.length > 0) {
          resourceGroup.related_resource_types.forEach((item) => {
            const { name, type, condition } = item;
            params.push({
              name: type || '',
              label: this.$t(`m.info['tab操作实例']`, { value: name }),
              tabType: 'resource',
              data: condition,
              activeName: resourceGroup.related_resource_types[typesIndex].type || ''
            });
          });
        }
        this.previewData = params;
        this.sideSliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        this.isShowSideSlider = true;
      },

      handleGetTypeData () {
        const needLocationList = this.syncGroupList.filter((v) => !v.fill_status);
        this.$emit('on-get-type-data', {
          locationList: needLocationList,
          addActionList: this.addActionsList,
          allActionList: this.syncGroupList
        });
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
              this.isShowInstanceSideSlider = false;
              this.resetDataAfterClose();
            }, _ => _);
          },
          cancel: () => {
            this.resetDataAfterClose();
            this.isShowInstanceSideSlider = false;
          }
        };
        return typeMap[payload]();
      },

      handleResourceSubmit () {
        const conditionData = this.$refs.renderResourceRef.handleGetValue();
        const { isEmpty, data } = conditionData;
        if (isEmpty) {
          return;
        }
        window.changeAlert = false;
        this.isShowInstanceSideSlider = false;
        this.instanceSideSliderTitle = '';
        const resItem = this.syncGroupList[this.curIndex]
          .tableList[this.curActionIndex]
          .resource_groups[this.curGroupIndex]
          .related_resource_types[this.curResourceIndex];
        const isConditionEmpty = data.length === 1 && data[0] === 'none';
        if (isConditionEmpty) {
          resItem.condition = ['none'];
        } else {
          resItem.condition = data;
          resItem.isError = false;
        }
        this.curIndex = -1;
        this.curResourceIndex = -1;
        this.curActionIndex = -1;
        this.curGroupIndex = -1;
        window.changeDialog = true;
        this.handleGetTypeData();
      },

      handleInit (payload) {
        this.disabled = !payload;
      },

      handleGetScopeActionResource (payload, id, systemId) {
        let actions = [];
        const scopeAction = this.authorizationScopeActions.find(item => item.id === systemId);
        if (scopeAction) {
          actions = scopeAction.filter(item => payload.map(_ => _.id).includes(item.id));
        }
        const conditions = actions.map(
          item => item.resource_groups[0].related_resource_types[0].condition
        ).filter(_ => _.length > 0);
        if (conditions.length < 1) {
          return [];
        }
        const instances = actions.map((item) => {
          const instancesItem = item.resource_groups[0].related_resource_types[0].condition[0]
            && item.resource_groups[0].related_resource_types[0].condition[0].instances;
          return (instancesItem && instancesItem.filter((v) => v.type === id)) || [];
        });
        const tempData = [];
        const resources = instances.map(item => item[0]
          && item[0].path).map(item => item && item.map(v => v.map(_ => _.id))).filter(item => item !== undefined);
        let resourceList = instances
          .map(item => item[0] && item[0].path)
          .map(item => item && item.map(v => v.map(({ id, name }) => ({ id, name }))))
          .flat(Infinity);
        resourceList = resourceList.filter(item => item !== undefined);
        resources.forEach(item => {
          item && item.forEach(subItem => {
            const hasIntersectionResource = resources.every(v => v && v.some(vItem => vItem[0] === subItem[0]));
            const hasResource = resources.find(v => v && v.some(vItem => vItem[0] === subItem[0]));
            if (hasIntersectionResource) {
              tempData.push(subItem[0]);
            }
            // 判断处理没有交集的情况
            if (!hasIntersectionResource && hasResource) {
              this.isAggregateEmptyMessage = true;
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

      handleConditionMouseover (payload) {
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

      handleAggregateConditionMouseover  (payload) {
        if (this.curCopyData[0] === 'none') {
          return;
        }
        if (this.curCopyKey === `${payload.aggregateResourceType.system_id}${payload.aggregateResourceType.id}`) {
          payload.canPaste = true;
        }
      },

      handleConditionMouseleave (payload) {
        payload.canPaste = false;
      },

      handleAnimationEnd () {
        this.sideSliderTitle = '';
        this.previewData = [];
      },

      handleShowPopover (payload) {
        payload = Object.assign(payload, { showAction: true, showPopover: true });
      },

      handleHidePopover (payload) {
        payload.showPopover = false;
      },

      handleGetBusData () {
        this.$once('hook:beforeDestroy', () => {
          window.removeEventListener('resize', this.formatFormItemWidth);
          bus.$off('on-group-perm-instance-copy');
        });
        bus.$on('on-group-perm-instance-copy', (payload) => {
          this.curCopyKey = `${payload.resource_type.system_id}${payload.resource_type.type}`;
          this.curCopyParams = { ...payload };
        });
        window.addEventListener('resize', this.formatFormItemWidth);
      },

      renderResourceHeader (h, { column, $index }, group, groIndex) {
        return (
          <div class="resource-instance-custom-label">
            <div class="instance-title">
              { this.$t(`m.common['资源实例']`) }
            </div>
            <div class="instance-no-limited" onClick={ () => this.handleGroupNoLimited(group, groIndex) }>
              <icon type="brush-fill" class="instance-no-limited-icon" />
              <div class="instance-no-limited-label">
                { this.$t(`m.common['批量无限制']`) }
              </div>
            </div>
          </div>
        );
      },

      setTableProps () {
        this.addProps = [];
        this.deleteProps = [];
        this.curAddActions.forEach(item => {
          this.addProps.push({
            label: item.name,
            id: item.id
          });
        });
        const hasDeleteData = this.syncGroupList.some(item => item.delete_actions.length > 0);
        if (hasDeleteData) {
          this.syncGroupList[0].delete_actions.forEach(item => {
            this.deleteProps.push({
              label: item.name,
              id: item.id
            });
          });
        }
      },

      // 设置instances
      setInstanceData (payload) {
        return Object.keys(payload).reduce((curr, next) => {
          curr.push(...payload[next]);
          return curr;
        }, []);
      },

      setAggregateTableData (payload) {
        this.syncGroupList = [...payload];
        this.tableKey = +new Date();
        console.log(this.syncGroupList, '最新数据');
      },

      setInstancesDisplayData (data) {
        const instancesDisplayData = data.reduce((p, v) => {
          if (!p[v['type']]) {
            p[v['type']] = [];
          }
          p[v['type']].push({
            id: v.id,
            name: v.name
          });
          return p;
        }, {});
        return instancesDisplayData;
      },
      
      resetDataAfterClose () {
        this.curIndex = -1;
        this.curResourceIndex = -1;
        this.curActionIndex = -1;
        this.curGroupIndex = -1;
        this.params = {};
        this.instanceSideSliderTitle = '';
      }
    }
  };
</script>

<style lang="postcss">
.actions-temp-resynchronize-confirm {
  .popover-title {
    font-size: 16px;
    padding-bottom: 16px;
  }
  .popover-content {
    color: #63656e;
    font-size: 12px;
    .popover-content-item {
      display: flex;
      &-value {
        color: #313238;
        margin-left: 5px;
      }
    }
    &-tip {
      padding: 4px 0 10px 0;
      line-height: 20px;
      word-break: break-all;
    }
  }
  .popconfirm-operate {
    .default-operate-button {
      min-width: 64px;
      margin-left: 0;
      margin-right: 8px;
    }
  }
}
</style>

<style lang="postcss" scoped>
  @import '../css/sync.css';
</style>
