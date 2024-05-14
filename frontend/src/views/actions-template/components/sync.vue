<template>
  <div class="temp-group-sync-wrapper">
    <div class="temp-group-sync-table" v-for="(group, groupIndex) in tableList" :key="group.id">
      <div class="flex-between temp-group-sync-table-header" @click.stop="handleExpand(group)">
        <div class="temp-group-sync-table-header-left">
          <Icon bk :type="group.expand ? 'down-shape' : 'right-shape'" class="expand-icon" />
          <div :class="['group-status-btn', { 'no-fill-btn': isHasGroupEmpty(group) }]">
            <Icon :type="isHasGroupEmpty(group) ? 'unfinished' : 'check-fill'" class="fill-status" />
            <span class="fill-text">
              {{ isHasGroupEmpty(group) ? $t(`m.actionsTemplate['未填写']`) : $t(`m.actionsTemplate['已填写']`) }}
            </span>
          </div>
          <div class="single-hide group-name">{{ group.name }}</div>
        </div>
        <div class="temp-group-sync-table-header-right" v-show="group.expand" @click.stop="">
          <bk-popconfirm
            trigger="click"
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
            <bk-button size="small" text @click.stop="handleBatchRepeat">
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
        @cell-mouse-enter="handleCellMouseEnter"
        @cell-mouse-leave="handleCellMouseLeave">
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
              <span :class="[`${row.mode_type}-name`]">{{ row.name }}</span>
            </span>
          </template>
        </bk-table-column>
        <bk-table-column
          :resizable="false"
          :label="$t(`m.permApply['资源类型']`)"
        >
          <template slot-scope="{ row }">
            <div v-for="resource in row.resource_groups" :key="resource.id">
              <span
                v-for="related in resource.related_resource_types"
                :key="related.type"
                :class="['resource-type-item', `resource-type-item-${row.mode_type}`]"
              >
                {{ related.name }}
              </span>
            </div>
          </template>
        </bk-table-column>
        <bk-table-column
          :min-width="310"
          :resizable="false"
          :render-header="(h, { column, $index }) =>
            renderResourceHeader(h, { column, $index }, group, groupIndex)
          "
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
                          @on-mouseover="handlerConditionMouseover(content, row)"
                          @on-mouseleave="handlerConditionMouseleave(content)"
                          @on-restore="handlerOnRestore(content)"
                          @on-copy="handlerOnCopy(content, groupIndex, contentIndex, $index, row)"
                          @on-paste="handlerOnPaste(...arguments, content)"
                          @on-batch-paste="handlerOnBatchPaste(...arguments, content, groupIndex, contentIndex, $index)"
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
                      class="related-resource-item"
                      v-for="subItem in related.related_resource_types"
                      :key="subItem.type"
                      @click.stop="handleViewResource(row, groupIndex, relatedIndex)"
                    >
                      <render-resource-popover
                        :key="subItem.type"
                        :data="subItem.condition"
                        :value="`${subItem.name}: ${subItem.value}`"
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
      quick-close
      transfer
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
          @on-init="handleOnInit" />
      </div>
      <div slot="footer" class="sync-group-slider-footer">
        <bk-button theme="primary" :disabled="disabled" @click="handleResourceSubmit">
          {{ $t(`m.common['保存']`) }}
        </bk-button>
        <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourceCancel('cancel')">
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
        tableList: [],
        deleteProps: [],
        addProps: [],
        previewData: [],
        originalList: [],
        authorizationScopeActions: [],
        requestQueue: ['scope', 'group'],
        params: {},
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
      isHasGroupEmpty () {
        return (payload) => {
          // console.log(payload);
          return true;
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
        const curData = this.tableList[this.curIndex]
            .add_actions[this.curActionIndex].resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResourceIndex];
console.log(curData, this.curIndex, this.curActionIndex, this.curResourceIndex, '当前数据');
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
        const curId = this.tableList[this.curIndex].add_actions[this.curActionIndex].id;
        const curType = this.tableList[this.curIndex]
            .add_actions[this.curActionIndex]
            .resource_groups[this.curGroupIndex]
            .related_resource_types[this.curResourceIndex]
            .type;
        if (!this.originalList.some(item => item.add_actions[this.curActionIndex].id === curId)) {
          return [];
        }
        const curData = this.originalList.find(item => item.add_actions[this.curActionIndex].id === curId);
        if (!curData) {
          return [];
        }
        const curActionData = curData.add_actions[this.curActionIndex].resource_groups[this.curGroupIndex];
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
        const curData = this.tableList[this.curIndex]
            .add_actions[this.curActionIndex]
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
          const curData = this.tableList[this.curIndex]
              .add_actions[this.curActionIndex]
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
        const curData = this.tableList[this.curIndex]
            .add_actions[this.curActionIndex]
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
        return this.addActions.length < 1;
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
    async created () {
      this.curCopyKey = '';
      await this.fetchGroupsPreview();
      this.fetchAuthorizationScopeActions();
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
      });
      window.addEventListener('resize', (this.formatFormItemWidth));
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
          this.tableList = cloneDeep(data.results || []);
          this.tableList.forEach((item, index) => {
            this.$set(item, 'expand', !(index > 0));
            this.$set(item, 'tableList', []);
            if (index === 0) {
              this.$emit('on-expand', item);
            }
            if (this.addActions.length > 0) {
              this.$set(item, 'add_actions', cloneDeep(this.addActions));
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
          console.log(this.tableList, 555);
          this.setTableProps();
          this.originalList = cloneDeep(this.tableList);
          this.isLastPage = current === this.pagination.totalPage;
          this.$emit('on-change-location-group', { list: this.tableList });
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
        if (columnIndex !== 0) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      getBatchCopyParams (payload, content) {
        const actions = [];
        this.tableList.forEach(item => {
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
        this.tableList.forEach(groupItem => {
          const actionList = [];
          (groupItem.add_actions || []).forEach(item => {
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
        this.tableList.forEach((item) => {
          if (item.expand && payload.id !== item.id) {
            item.expand = false;
          }
        });
        this.$emit('on-expand', payload);
      },

      handleConfirmResynchronize (payload) {

      },

      handlePrevPage () {
        window.changeDialog = true;
        if (this.pagination.current > 1) {
          --this.pagination.current;
        }
        this.requestQueue = ['group'];
        this.fetchGroupsPreview();
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
              group_ids: this.tableList.map(item => item.id)
            }
          });
          const referList = res.data;
          this.tableList.forEach(item => {
            const temp = referList.find(sub => sub.group_id === item.id);
            if (temp) {
              item.add_actions.splice(index, 1, new SyncPolicy({ ...temp.policy, tag: 'add' }, 'detail'));
            }
          });
          this.$refs[`popover_${index}_${$index}_ref`][0]
            && this.$refs[`popover_${index}_${$index}_ref`][0].hideHandler();
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          setTimeout(() => {
            act.loading = false;
          }, 500);
        }
      },

      async handleUnSynchronize ({ id, type }) {
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

      handleBatchRepeat () {

      },

      handleAnimationEnd () {
        this.sideSliderTitle = '';
        this.previewData = [];
      },

      handleShowPopover (payload) {
        payload.showAction = true;
        payload.showPopover = true;
        payload = Object.assign(payload, { showAction: true, showPopover: true });
      },

      handleHidePopover (payload) {
        payload.showPopover = false;
      },

      handleCellMouseEnter (row, column, cell, event) {
        if (!row.add_actions) {
          return;
        }
        for (let i = 0; i < row.add_actions.length; i++) {
          if (row.add_actions[i].id === column.property) {
            row.add_actions[i].showAction = true;
            break;
          }
        }
      },

      handleCellMouseLeave (row, column, cell, event) {
        if (!row.add_actions) {
          return;
        }
        for (let i = 0; i < row.add_actions.length; i++) {
          if (row.add_actions[i].id === column.property && !row.add_actions[i].showPopover) {
            row.add_actions[i].showAction = false;
            break;
          }
        }
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
        const resItem = this.tableList[this.curIndex]
          .add_actions[this.curActionIndex]
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

      handlerConditionMouseover (payload, row) {
        if (Object.keys(this.curCopyParams).length < 1) {
          return;
        }

        if (this.curCopyKey === `${payload.system_id}${payload.type}`) {
          payload.canPaste = true;
        }
      },

      handlerConditionMouseleave (payload) {
        payload.canPaste = false;
      },

      handlerOnCopy (payload, $index, subIndex, index, action) {
        window.changeDialog = true;
        this.curCopyKey = `${payload.system_id}${payload.type}`;
        this.curCopyParams = this.getBatchCopyParams(action, payload);
        this.showMessage(this.$t(`m.info['实例复制']`));
        this.$refs[`condition_${index}_${$index}_${subIndex}_ref`][0]
          && this.$refs[`condition_${index}_${$index}_${subIndex}_ref`][0].setImmediatelyShow(true);
      },

      handlerOnPaste (payload, content) {
        if (!payload.flag) {
          return;
        }
        if (payload.data.length === 0) {
          content.condition = [];
        } else {
          content.condition = payload.data.map(conditionItem => new Condition(conditionItem, '', 'add'));
        }
        content.isError = false;
        this.showMessage(this.$t(`m.info['粘贴成功']`));
      },

      handlerOnBatchPaste (payload, content, $index, subIndex, index) {
        if (!payload.flag) {
          return;
        }
        if (!payload.data.length) {
          this.tableList.forEach(item => {
            item.add_actions.forEach(subItem => {
              subItem.related_resource_types.forEach(resItem => {
                if (`${resItem.system_id}${resItem.type}` === this.curCopyKey) {
                  resItem.condition = [];
                  resItem.isError = false;
                }
              });
            });
          });
        } else {
          this.tableList.forEach(item => {
            item.add_actions.forEach(subItem => {
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
        this.$refs[`condition_${index}_${$index}_${subIndex}_ref`][0]
          && this.$refs[`condition_${index}_${$index}_${subIndex}_ref`][0].setImmediatelyShow(false);
        this.showMessage(this.$t(`m.info['批量粘贴成功']`));
      },

      handleGroupNoLimited (payload) {
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
                    console.log(7777, types);
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
        payload.tableList = cloneDeep(tableData);
      },

      handleShowResourceSlider (data, resItem, resIndex, $index, index, groupIndex) {
        this.params = {
          system_id: this.$route.params.systemId,
          action_id: data.id,
          resource_type_system: resItem.system_id,
          resource_type_id: resItem.type
        };
        this.curScopeAction = this.authorizationScopeActions.find(item => item.id === data.id);
        this.curIndex = $index;
        this.curActionIndex = index;
        this.curResourceIndex = resIndex;
        this.curGroupIndex = groupIndex;
        this.instanceSideSliderTitle = this.$t(`m.info['关联侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}` });
        window.changeAlert = 'iamSidesider';
        this.isShowInstanceSideSlider = true;
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

      handleOnInit (payload) {
        this.disabled = !payload;
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
            <div class="instance-no-limited" onClick={ () => this.handleGroupNoLimited(group) }>
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
        this.addActions.forEach(item => {
          this.addProps.push({
            label: item.name,
            id: item.id
          });
        });
        if (this.tableList.some(item => item.delete_actions.length > 0)) {
          this.tableList[0].delete_actions.forEach(item => {
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
    &-content {
      border-right: none;
      border-bottom: none;
      .name-tag {
        margin-left: 0;
        font-size: 10px
      }
      .resource-type-item {
        margin-right: 8px;
      }
      .delete-name,
      .resource-type-item-delete {
        text-decoration: line-through;
      }
      .relation-content-wrapper {
        height: 100%;
        padding: 17px 0;
        color: #63656e;
        .resource-type-name {
          display: block;
          margin-bottom: 9px;
        }
      }
      /deep/ .related-resource-item {
        cursor: pointer;
        &:hover {
          color: #3a84ff;
        }
        .text {
          text-decoration: line-through;
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
      .iam-template-sync-popover-cls {
        position: absolute;
        top: 5px;
        right: 5px;
        cursor: pointer;
        &:hover {
          color: #3a84ff;
        }
      }
      /deep/ .resource-instance-custom-label {
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
      padding: 0 24px;
      .bk-button {
        min-width: 88px;
        margin-right: 8px;
      }
    }
  }
}
</style>
