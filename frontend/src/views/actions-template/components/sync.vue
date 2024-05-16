<template>
  <div class="temp-group-sync-wrapper">
    <div class="temp-group-sync-table" v-for="(group, groupIndex) in syncGroupList" :key="group.id">
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
            <bk-button size="small" text @click.stop="handleBatchRepeat(group)">
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
            <div class="resource-type-content">
              <div v-for="resource in row.resource_groups" :key="resource.id" class="resource-type-list">
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
          :show-overflow-tooltip="true"
        >
          <template slot-scope="{ row, $index }">
            <div class="relation-content-wrapper">
              <template v-if="!row.isEmpty">
                <template v-if="['add'].includes(row.mode_type)">
                  <div v-for="(related, relatedIndex) in row.resource_groups" :key="related.id">
                    <div class="relation-content-item"
                      v-for="(content, contentIndex) in related.related_resource_types"
                      :key="`${groupIndex}${contentIndex}`">
                      <div class="content">
                        <render-condition
                          :ref="`condition_${groupIndex}_${$index}_${contentIndex}_ref`"
                          :value="content.value"
                          :params="curCopyParams"
                          :is-empty="content.empty"
                          :can-view="row.canView"
                          :can-paste="content.canPaste"
                          :is-error="content.isError"
                          @on-mouseover="handleConditionMouseover(content, row)"
                          @on-mouseleave="handleConditionMouseleave(content)"
                          @on-copy="handleInstanceCopy(content, groupIndex, contentIndex, $index, row)"
                          @on-paste="handleInstancePaste(...arguments, content)"
                          @on-batch-paste="handleBatchInstancePaste(
                            ...arguments, content, groupIndex, contentIndex, $index
                          )"
                          @on-click="handleShowResourceSlider(
                            row, content, contentIndex, $index, groupIndex, relatedIndex
                          )"
                        />
                      </div>
                    </div>
                  </div>
                  <bk-popover
                    :ref="`popover_${groupIndex}_${$index}_ref`"
                    trigger="click"
                    class="iam-template-sync-popover-cls"
                    theme="light"
                    placement="right"
                    :on-hide="() => handleHidePopover(row)"
                    :on-show="() => handleShowPopover(row)">
                    <div class="edit-wrapper" v-if="!!row.showAction">
                      <spin-loading v-if="row.loading" />
                      <Icon type="edit-fill" v-else />
                    </div>
                    <div slot="content" class="sync-popover-content">
                      <p class="refer-title" v-if="isShowBatchRefer(row)">
                        <Icon type="down-angle" />{{ $t(`m.permTemplateDetail['批量引用已有的操作实例']`) }}
                      </p>
                      <template v-if="batchReferAction(row).length > 0">
                        <p v-for="resItem in batchReferAction(row)"
                          :key="resItem.id"
                          class="cursor"
                          @click.stop="handleReferInstance(resItem, row, group, groupIndex, $index)">
                          {{ resItem.name }}
                        </p>
                      </template>
                      <template
                        v-if="!isShowBatchRefer(row)
                          && batchReferAction(row).length === 0"
                      >
                        {{ $t(`m.common['暂无数据']`) }}
                      </template>
                    </div>
                  </bk-popover>
                </template>
                <template v-if="['delete'].includes(row.mode_type)">
                  <div v-for="(related, relatedIndex) in row.resource_groups" :key="related.id">
                    <div
                      class="single-hide relation-content-item"
                      v-for="subItem in related.related_resource_types"
                      :key="subItem.type"
                      @click.stop="handleViewResource(row, groupIndex, relatedIndex)"
                    >
                      <render-resource-popover
                        :key="subItem.type"
                        :data="subItem.condition"
                        :value="subItem.value"
                        :max-width="185"
                        @on-view="handleViewResource(row, groupIndex, relatedIndex)"
                      />
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

    <!-- 打开资源视图选择器 -->
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
          @on-init="handleInit" />
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
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { leaveConfirm } from '@/common/leave-confirm';
  import SyncPolicy from '@/model/template-sync-policy';
  import Condition from '@/model/condition';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import RenderCondition from '../components/render-condition';
  import RenderDetail from '../components/render-detail';
  import RenderResource from '../components/render-resource';
  import AggregationPolicy from '@/model/actions-temp-aggregation-policy';
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
      RenderResource
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
        isShowSideSlider: false,
        isShowInstanceSideSlider: false,
        sideSliderTitle: '',
        instanceSideSliderTitle: '',
        curIndex: -1,
        curActionIndex: -1,
        curResourceIndex: -1,
        curGroupIndex: -1,
        syncGroupList: [],
        deleteProps: [],
        addProps: [],
        previewData: [],
        originalList: [],
        curAddActions: [],
        authorizationScopeActions: [],
        requestQueue: ['scope', 'group'],
        params: {},
        curRemoveSyncData: {},
        curScopeAction: {},
        curCopyParams: {},
        pagination: {
          current: 1,
          limit: 5,
          totalPage: 0
        },
        resourceSliderWidth: Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7)
      };
    },
    computed: {
      ...mapGetters('permTemplate', ['cloneActions']),
      isShowBatchRefer () {
        return (payload) => {
          return this.cloneActions.some(item => item.action_id === payload.id);
        };
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
      batchReferAction () {
        return payload => {
          const temp = this.cloneActions.find(item => item.action_id === payload.id);
          if (temp) {
              return temp.copy_from_actions;
          }
          return [];
        };
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
      }
    },
    watch: {
      addActions: {
        handler (value) {
          this.curAddActions = [...value];
        },
        immediate: true,
        deep: true
      }
    },
    async created () {
      this.curCopyKey = '';
      await this.fetchGroupsPreview();
      this.fetchAuthorizationScopeActions();
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
      });
      window.addEventListener('resize', this.formatFormItemWidth);
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
          this.pagination.totalPage = Math.ceil(data.count / this.pagination.limit);
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
                const result = new SyncPolicy({ ...act, tag: 'add' }, 'add');
                this.$set(result, 'mode_type', 'add');
                item.tableList.push(result);
                return result;
              });
            }
            item.delete_actions = item.delete_actions.map(act => {
              if (!act.resource_groups || !act.resource_groups.length) {
                act.resource_groups = [];
                if (act.related_resource_types && act.related_resource_types.length > 0) {
                  act.resource_groups = [{ id: '', related_resource_types: act.related_resource_types }];
                }
              }
              const result = new SyncPolicy({ ...act, tag: 'add' }, 'add');
              this.$set(result, 'mode_type', 'delete');
              item.tableList.push(result);
              return result;
            });
          });
          console.log(this.syncGroupList, 555);
          this.setTableProps();
          this.originalList = cloneDeep(this.syncGroupList);
          this.isLastPage = current === this.pagination.totalPage;
          this.$emit('on-change-location-group', { list: this.syncGroupList });
          this.$emit('on-all-submit', current === this.pagination.totalPage);
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
        const hasMultipleResourceType = row.resource_groups && row.resource_groups.some((item) => {
          return item.related_resource_types.length > 1;
        });
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
        this.syncGroupList.forEach(item => {
          item.add_actions.forEach(act => {
            if (act.id !== payload.id) {
              actions.push({
                system_id: this.$route.params.systemId,
                id: act.id
              });
            }
          });
        });
        actions.unshift({
          system_id: this.$route.params.systemId,
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

      getData () {
        let flag = false;
        let isNoAdd = false;
        const groups = [];
        this.syncGroupList.forEach(groupItem => {
          const actionList = [];
          (groupItem.tableList || []).forEach(item => {
            const { type, id, name, environment, description } = item;
            const relatedResourceTypes = [];
            const groupResourceTypes = [];
            if (item.resource_groups.length > 0) {
              item.resource_groups.forEach(groupItem => {
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
              item.resource_groups = cloneDeep(item.resource_groups);
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
          });
          groups.push({
            id: groupItem.id,
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
          if (item.expand && payload.id !== item.id) {
            item.expand = false;
          }
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
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.nextLoading = false;
        }
      },

      async handleReferInstance (resItem, act, row, index, $index) {
        window.changeDialog = true;
        act.loading = true;
        try {
          const res = await this.$store.dispatch('permTemplate/getCloneAction', {
            id: this.id,
            data: {
              action_id: act.id,
              clone_from_action_id: resItem.id,
              group_ids: this.syncGroupList.map(item => item.id)
            }
          });
          const referList = res.data;
          this.syncGroupList.forEach(item => {
            const temp = referList.find(sub => sub.group_id === item.id);
            if (temp) {
              item.tableList.splice(index, 1, new SyncPolicy({ ...temp.policy, tag: 'add' }, 'detail'));
            }
          });
          this.$refs[`popover_${index}_${$index}_ref`][0]
            && this.$refs[`popover_${index}_${$index}_ref`][0].hideHandler();
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          setTimeout(() => {
            act.loading = false;
          }, 500);
        }
      },

      async handleBatchRepeat (payload) {
        if (this.isCurGroupAllEmpty(payload)) {
          this.messageWarn(this.$t(`m.common['暂无可批量复用实例']`), 3000);
          return;
        }
        let params = {};
        payload.tableList.forEach((item) => {
          if (['add'].includes(item.mode_type)) {
            item.resource_groups && item.resource_groups.forEach((v) => {
              v.related_resource_types.forEach((related) => {
                params = this.getBatchCopyParams(item, related);
              });
            });
          }
        });
        try {
          const { data } = await this.$store.dispatch('permApply/resourceBatchCopy', params);
          if (data && data.length) {
            this.handleBatchInstancePaste({ flag: true, data });
          } else {
            this.messageWarn(this.$t(`m.info['暂无可批量复制包含有属性条件的资源实例']`), 3000);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
        payload.tableList && payload.tableList.forEach((item) => {
          console.log(item);
        });
        this.syncGroupList.forEach((item) => {
          if (['add'].includes(item.mode_type)) {
            item.tableList.forEach((v) => {
              console.log(v);
            });
          }
        });
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
        this.instanceSideSliderTitle = '';
        this.isShowInstanceSideSlider = false;
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
      },

      handleInstanceCopy (payload, $index, subIndex, index, action) {
        window.changeDialog = true;
        this.curCopyKey = `${payload.system_id}${payload.type}`;
        this.curCopyParams = this.getBatchCopyParams(action, payload);
        const conditionRef = this.$refs[`condition_${index}_${$index}_${subIndex}_ref`];
        if (conditionRef && conditionRef.length > 0) {
          conditionRef[0].setImmediatelyShow(true);
        }
        this.messageSuccess(this.$t(`m.info['实例复制']`), 3000);
      },

      handleInstancePaste (payload, content) {
        if (!payload.flag) {
          return;
        }
        if (this.curCopyKey !== `${content.system_id}${content.type}`) {
          this.messageWarn(this.$t(`m.common['暂无可复制实例']`), 3000);
          return;
        }
        content.condition = payload.data.length > 0 ? payload.data.map(conditionItem => new Condition(conditionItem, '', 'add')) : [];
        content.isError = false;
        this.messageSuccess(this.$t(`m.info['粘贴成功']`), 3000);
      },

      handleBatchInstancePaste (payload, content, $index, subIndex, index) {
        if (!payload.flag) {
          return;
        }
        if (!payload.data.length) {
          this.syncGroupList.forEach(item => {
            item.tableList.forEach(subItem => {
              subItem.related_resource_types.forEach(resItem => {
                if (`${resItem.system_id}${resItem.type}` === this.curCopyKey) {
                  resItem.condition = [];
                  resItem.isError = false;
                }
              });
            });
          });
        } else {
          this.syncGroupList.forEach(item => {
            item.tableList.forEach(subItem => {
              const curPasteData = payload.data.find(_ => _.id === subItem.id);
              if (curPasteData) {
                subItem.resource_groups && subItem.resource_groups.forEach(groupItem => {
                  groupItem.related_resource_types.forEach(subItem => {
                    if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                      subItem.condition = curPasteData.resource_type.condition.map(conditionItem => new Condition(conditionItem, '', 'add'));
                      subItem.isError = false;
                    }
                  });
                });
              }
            });
          });
        }
        this.curCopyParams = {};
        content.isError = false;
        const conditionRef = this.$refs[`condition_${index}_${$index}_${subIndex}_ref`][0];
        conditionRef && conditionRef.setImmediatelyShow(false);
        this.messageSuccess(this.$t(`m.info['批量粘贴成功']`), 3000);
      },

      handleGroupNoLimited (payload, groupIndex) {
        if (this.isUnlimitedDisabled(payload)) {
          return;
        }
        const { tableList } = payload;
        const tableData = cloneDeep(tableList);
        tableData.forEach((item, index) => {
          if (['add'].includes(item.mode_type)) {
            if (!item.isAggregate) {
              if (item.resource_groups && item.resource_groups.length) {
                item.resource_groups.forEach(groupItem => {
                  groupItem.related_resource_types && groupItem.related_resource_types.forEach(types => {
                    if (!payload && (types.condition.length && types.condition[0] !== 'none')) {
                      return;
                    }
                    types.condition = payload ? [] : ['none'];
                    if (payload) {
                      types.isError = false;
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
                new AggregationPolicy(item)
              );
            }
          }
        });
        this.$set(this.syncGroupList[groupIndex], 'tableList', tableData);
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
        this.instanceSideSliderTitle = this.$t(`m.info['关联侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${row.name}${this.$t(`m.common['】']`)}` });
        this.isShowInstanceSideSlider = true;
        window.changeAlert = 'iamSidesider';
      },

      handleViewResource (payload, index, relatedIndex) {
        const data = payload.resource_groups[relatedIndex];
        const params = [];
        if (data.related_resource_types.length > 0) {
          data.related_resource_types.forEach(item => {
            const { name, type, condition } = item;
            params.push({
              name: type || '',
              label: this.$t(`m.info['tab操作实例']`, { value: name }),
              tabType: 'resource',
              data: condition
            });
          });
        }
        this.previewData = params;
        this.sideSliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        this.isShowSideSlider = true;
      },

      handleInit (payload) {
        this.disabled = !payload;
      },
      
      handleConditionMouseover (payload, row) {
        payload.canPaste = true;
        // if (Object.keys(this.curCopyParams).length < 1) {
        //   return;
        // }

        // if (this.curCopyKey === `${payload.system_id}${payload.type}`) {
        //   payload.canPaste = true;
        // }
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

      resetDataAfterClose () {
        this.curIndex = -1;
        this.curResourceIndex = -1;
        this.curActionIndex = -1;
        this.curGroupIndex = -1;
        this.params = {};
        this.instanceSideSliderTitle = '';
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
.temp-group-sync-wrapper {
  .temp-group-sync-table {
    margin-bottom: 12px;
    &-header {
      background-color: #DCDEE5;
      min-height: 40px;
      line-height: 40px;
      padding: 0 16px;
      cursor: pointer;
      &-left {
        display: flex;
        align-items: center;
        .expand-icon {
          font-size: 12px;
        }
        .group-status-btn {
          min-width: 68px;
          font-size: 12px;
          background-color: #ffffff;
          border-radius: 12px;
          line-height: 24px;
          padding: 0 6px;
          margin-left: 10px;
          .fill-status {
            font-size: 14px;
            color: #2DCB9D;
          }
          .fill-text {
            color: #1CAB88;
          }
          &.no-fill-btn {
            .fill-status {
              color: #FFB848;
            }
            .fill-text {
              color: #FF9C01;
            }
          }
        }
        .group-name {
          margin: 0 8px;
          font-size: 12px;
        }
      }
      &-right {
        .bk-button-small {
          padding: 0;
          &.un-sync {
            margin-right: 16px;
          }
        }
      }
    }
    /deep/ .temp-group-sync-table-content {
      border-right: none;
      border-bottom: none;
      &.bk-table {
        background-color: #ffffff;
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
      }
      .name-tag {
        margin-left: 0;
        margin-right: 4px;
        padding: 0 4px;
        font-size: 10px
      }
      .delete-name,
      .resource-type-item-delete {
        text-decoration: line-through;
      }
      .cell {
        .relation-content-wrapper {
          height: 100%;
          color: #63656e;
          .iam-condition-item {
            border: none;
            padding: 0;
          }
        }
      }
      .resource-type-cell-cls {
        .cell {
          width: 100%;
          /* height: 100%; */
          padding: 0;
          display: block;
          .resource-type-content {
            height: 100%;
            .resource-type-list {
              height: 100%;
              .resource-type-item {
                border-bottom: 1px solid #dfe0e5;
                padding: 12px 15px;
                &:last-of-type {
                  border-bottom: 0;
                }
              }
            }
          }
        }
      }
      .resource-instance-add-cell-cls {
        &:hover {
          border: none;
        }
        .cell {
          padding: 0;
          .relation-content-wrapper {
            .relation-content-item {
              padding: 5px 15px;
              &:hover {
                border: 1px solid #699DF4;
                margin-right: 1px;
              }
            }
          }
        }
        &.multiple-resource-type-instance {
          .cell {
            .relation-content-wrapper {
              &:hover {
                border-bottom: 1px solid #dfe0e5;
              }
              .relation-content-item {
                border-bottom: 1px solid #dfe0e5;
                &:last-of-type {
                  border-bottom: 0;
                  &:hover {
                    border-bottom: 1px solid #699DF4;
                  }
                }
                &:hover {
                  border: 1px solid #699DF4;
                  &:last-of-type {
                    border-bottom: 1px solid #699DF4;
                  }
                }
              }
            }
          }
        }
      }
      .resource-instance-delete-cell-cls {
        .cell {
          .relation-content-item {
            cursor: pointer;
            &:hover {
              color: #3a84ff;
            }
            .text {
              text-decoration: line-through;
            }
          }
        }
      }
      .iam-template-sync-popover-cls {
        position: absolute;
        top: 5px;
        right: 5px;
        cursor: pointer;
        &:hover {
          color: #3a84ff;
        }
      }
      .resource-instance-custom-label {
        display: flex;
        align-items: baseline;
        .instance-title {
          position: relative;
          min-width: 62px;
          &::after {
            height: 8px;
            line-height: 1;
            content: "*";
            color: #ea3636;
            font-size: 12px;
            position: absolute;
            top: 50%;
            display: inline-block;
            vertical-align: middle;
            transform: translate(6px, -50%);
          }
        }
        .instance-no-limited {
          display: flex;
          align-items: center;
          color: #3a84ff;
          margin-left: 10px;
          cursor: pointer;
          &-label {
            margin-left: 5px;
          }
        }
      }
    }
  }
}
.pagination-wrapper {
  margin-top: 16px;
  text-align: center;
  .page-display {
    display: inline-block;
    width: 74px;
    height: 32px;
    line-height: 32px;
    border: 1px solid #c4c6cc;
    border-radius: 2px;
    vertical-align: bottom;
  }
}
.sync-popover-content {
  max-height: 250px;
  overflow-y: auto;
  &::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: #dcdee5;
    border-radius: 3px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
    border-radius: 3px;
  }
  .cursor {
    line-height: 24px;
    color: #63656e;
    cursor: pointer;
    &:hover {
      color: #3a84ff;
    }
    &.disabled {
      color: #c4c6cc;
      cursor: not-allowed;
      &:hover {
        color: #c4c6cc;
      }
    }
  }
  p.refer-title {
    line-height: 24px;
    color: #313238;
  }
}
.related-instance-sideslider {
  /deep/ .bk-sideslider-footer {
    background-color: #ffffff !important;
    font-size: 0;
    .sync-group-slider-footer {
      width: 100%;
      padding: 0 24px;
      .bk-button {
        min-width: 88px;
        margin-right: 8px;
      }
    }
  }
}
</style>
