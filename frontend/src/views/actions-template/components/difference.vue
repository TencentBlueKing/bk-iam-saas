<template>
  <div class="sync-group-wrapper">
    <template v-if="hasRelatedGroup">
      <smart-action>
        <div :class="['sync-group-content', { 'is-full': isFullScreen }]">
          <div :class="['sync-group-content-left']" :style="leftStyle">
            <div class="related-instance-header">
              <div class="header-title">
                {{ $t(`m.actionsTemplate['关联用户组的实例']`) }}
              </div>
              <div class="flex-between header-content">
                <div class="header-content-btn">
                  <div class="operate-btn">
                    <bk-button
                      theme="primary"
                      class="fill"
                      :loading="fillLoading"
                      @click.stop="handleAllInstanceFill"
                      v-bk-tooltips="{ content: fillTip }"
                    >
                      {{ $t(`m.common['一键填充']`) }}
                    </bk-button>
                    <bk-button class="no-limited" @click.stop="handleAllNoLimited">
                      {{ $t(`m.common['全部无限制']`) }}
                    </bk-button>
                  </div>
                  <div class="aggregate-type-list">
                    <div
                      v-for="item in AGGREGATE_METHODS_LIST"
                      :key="item.value"
                      :class="[
                        'aggregate-action-btn',
                        { 'is-active': aggregateType === item.value },
                        { 'is-disabled': isAggregateDisabled }
                      ]"
                      @click.stop="handleChangeAggregate(item.value)"
                    >
                      <span>{{ $t(`m.common['${item.name}']`) }}</span>
                    </div>
                  </div>
                </div>
                <div
                  :class="[
                    'location-fill-btn',
                    { 'is-disabled': locationList.length === 0 }
                  ]"
                  @click.stop="handleChangeLocationIndex"
                >
                  <Icon type="locate" class="location-icon" />
                  <div class="location-content">
                    <span class="location-tip">{{ $t(`m.common['定位未填写']`) }}</span>
                    <span
                      v-if="curLocationIndex > 0 && locationList.length > 0"
                      class="location-count"
                    >
                      {{ `(${curLocationIndex}/${locationList.length})` }}
                    </span>
                    <span v-else :class="['location-count']">
                      {{ `(${locationList.length})` }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div class="related-instance-table">
              <RenderSync
                ref="syncRef"
                :id="$route.params.id"
                :all-actions="policyList"
                :add-actions="addActions"
                :clone-action="cloneActions"
                @on-expand="handleExpand"
                @on-get-type-data="handleChangeTypeData"
                @on-all-submit="handleAllSubmit"
              />
            </div>
          </div>
          <div class="sync-group-content-center">
            <div class="expand-icon" @click.stop="handleToggleExpand">
              <bk-icon :type="isFullScreen ? 'angle-left' : 'angle-right'" class="icon" />
            </div>
          </div>
          <div :class="['sync-group-content-right']" :style="rightStyle">
            <div class="drag-dotted-line" v-if="isDrag" :style="dottedLineStyle" />
            <div class="drag-line" :style="dragStyle">
              <img
                class="drag-bar"
                src="@/images/drag-icon.svg"
                :draggable="false"
                @mousedown="handleDragMouseenter($event)"
                alt=""
              />
            </div>
            <GroupDetail :expand-data="curExpandData" />
          </div>
        </div>
        <div slot="action">
          <div class="sync-group-btn">
            <bk-button :loading="prevLoading" @click.stop="handlePrevStep('prev')">
              {{ $t(`m.common['上一步']`) }}
            </bk-button>
            <bk-popover
              :content="$t(`m.actionsTemplate['还有用户组未完成实例关联']`)"
              :disabled="!isSubmitDisabled()"
            >
              <bk-button
                theme="primary"
                :loading="isLoading"
                :disabled="isSubmitDisabled()"
                @click.stop="handleNextStep"
              >
                {{ $t(`m.common['提交']`) }}
              </bk-button>
            </bk-popover>
            <bk-button @click.stop="handlePrevStep('cancel')">
              {{ $t(`m.common['取消']`) }}
            </bk-button>
          </div>
        </div>
      </smart-action>
    </template>
    <div v-else class="no-sync-group">
      <ExceptionEmpty
        :type="emptyGroupData.type"
        :empty-text="emptyGroupData.text"
        :error-message="emptyGroupData.tip"
        :tip-type="emptyGroupData.tipType"
      />
      <div class="no-sync-group-btn">
        <bk-button @click.stop="handleNoGroupOperate('prev')">
          {{ $t(`m.common['上一步']`) }}
        </bk-button>
        <bk-button theme="primary" @click.stop="handleNoGroupOperate('submit')">
          {{ $t(`m.common['直接提交']`) }}
        </bk-button>
        <bk-button @click.stop="handleNoGroupOperate('cancel')">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </div>
    </div>
  </div>
</template>

<script>
  import { cloneDeep, isEqual } from 'lodash';
  import { mapGetters } from 'vuex';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import { AGGREGATE_METHODS_LIST } from '@/common/constants';
  import Condition from '@/model/condition';
  import SyncPolicy from '@/model/template-sync-policy';
  import AggregationPolicy from '@/model/actions-temp-aggregation-policy';
  import RenderSync from './sync.vue';
  import GroupDetail from './group-detail';

  export default {
    components: {
      RenderSync,
      GroupDetail
    },
    props: {
      hasRelatedGroup: {
        type: Boolean
      },
      id: {
        type: [Number, String],
        default: 0
      },
      selectActions: {
        type: Array,
        default: () => []
      },
      selectActionsBack: {
        type: Array,
        default: () => []
      },
      allActions: {
        type: Array,
        default: () => []
      },
      allSyncGroupActions: {
        type: Array,
        default: () => []
      },
      linearActions: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        AGGREGATE_METHODS_LIST,
        isLoading: false,
        isOnePage: false,
        isLastPage: false,
        isNoAddActions: false,
        isFullScreen: false,
        isDrag: false,
        prevLoading: false,
        disabled: true,
        fillLoading: false,
        aggregateType: 'no-aggregate',
        fillTip: this.$t(`m.actionsTemplate['引用已有的操作实例一键填充']`),
        curLocationIndex: 0,
        navWidth: 260,
        dragWidth: window.innerWidth / 2 - 260 + 26,
        dragRealityWidth: window.innerWidth / 2 - 260 + 26,
        dottedLineWidth: 26,
        curExpandData: {},
        pagination: {
          current: 1,
          limit: 20
        },
        emptyGroupData: {
          type: 'empty',
          text: this.$t(`m.actionsTemplate['暂无关联的用户组']`),
          tip: this.$t(`m.actionsTemplate['无须进行操作实例的确认']`),
          tipType: 'noPerm'
        },
        allSyncGroupList: [],
        allAddSyncGroupList: [],
        locationList: [],
        addActions: [],
        policyList: [],
        linearActionList: [],
        aggregations: [],
        aggregationsBackup: [],
        aggregationsTableData: []
      };
    },
    computed: {
      ...mapGetters('permTemplate', ['actions', 'cloneActions', 'preGroupOnePage']),
      ...mapGetters(['navStick']),
      isAggregateDisabled () {
        return this.isNoAddActions;
      },
      leftStyle () {
        if (this.dragWidth > 0) {
          return {
            width: `calc(100% - ${this.dragWidth}px)`
          };
        }
        return {
          width: `calc(100% - ${window.innerWidth / 2 - this.navWidth}px)`
        };
      },
      rightStyle () {
        if (this.dragWidth > 0) {
          return {
            flexBasis: `${this.dragWidth}px`
          };
        }
        return {
          flexBasis: `${window.innerWidth / 2 - this.navWidth}px`
        };
      },
      dragStyle () {
        return {
          right: `${this.dragWidth}px`
        };
      },
      dottedLineStyle () {
        return {
          right: `${this.dragRealityWidth}px`
        };
      },
      batchFillActions () {
        return (payload) => {
          const temp = this.cloneActions.find((item) => {
            if (payload.isAggregate) {
              const actionsList = payload.actions.map((v) => v.id);
              return actionsList.includes(item.action_id);
            }
            return item.action_id === payload.id;
          });
          if (temp) {
            return temp.copy_from_actions;
          }
          return [];
        };
      },
      isSubmitDisabled () {
        return () => {
          const tableList = this.allSyncGroupList
            .map((item) => item.tableList)
            .flat(Infinity);
          const hasEmpty = tableList.some((item) => {
            return (
              item.resource_groups
              && item.resource_groups.some((v) => {
                return (
                  v.related_resource_types
                  && v.related_resource_types.some(
                    (related) =>
                      related.condition.length === 1 && related.condition[0] === 'none'
                  )
                );
              })
            );
          });
          return !!hasEmpty;
        };
      }
    },
    watch: {
      navStick (value) {
        this.navWidth = value ? 260 : 60;
      },
      allSyncGroupActions: {
        async handler (value) {
          const tempActions = this.handleGetAddAction(value);
          this.addActions = tempActions;
          this.isNoAddActions = this.addActions.length < 1;
          await this.fetchAggregationAction();
        },
        immediate: true
      },
      allActions: {
        handler (value) {
          this.policyList = [...value];
        },
        immediate: true
      },
      linearActions: {
        handler (value) {
          this.linearActionList = [...value];
        },
        immediate: true
      }
    },
    mounted () {
      window.addEventListener('resize', this.handleResizeView);
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.handleResizeView);
      });
    },
    methods: {
      // 获取能聚合的操作
      async fetchAggregationAction () {
        try {
          const { systemId } = this.$route.params;
          const { data } = await this.$store.dispatch('aggregate/getAggregateAction', {
            system_ids: systemId
          });
          if (data.aggregations && data.aggregations.length > 0) {
            // 过滤掉不存在于当前用户组下的操作
            const aggregations = [];
            const actionIds = this.addActions.map((item) => item.id);
            data.aggregations.forEach((item) => {
              const { actions, aggregate_resource_types } = item;
              const curActions = actions.filter((item) => actionIds.includes(item.id));
              if (curActions.length > 0) {
                aggregations.push({
                  actions: curActions,
                  aggregate_resource_types
                });
              }
            });
            [this.aggregations, this.aggregationsBackup] = [cloneDeep(aggregations), cloneDeep(aggregations)];
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async handleNextStep () {
        if (this.isNoAddActions) {
          this.handleUpdateCommit();
          return;
        }
        const { flag, groups, isNoAdd } = this.$refs.syncRef.getData();
        if (flag) {
          return;
        }
        groups.forEach((item) => {
          item.actions.forEach((sub) => {
            if (!sub.resource_groups || !sub.resource_groups.length) {
              sub.resource_groups
                = sub.related_resource_types && sub.related_resource_types.length
                  ? [{ id: '', related_resource_types: sub.related_resource_types }]
                  : [];
            }
          });
        });
        if (this.preGroupOnePage) {
          if (isNoAdd) {
            this.handleUpdateCommit();
            return;
          }
          this.submitPreGroupSync(groups);
          return;
        }
        if (this.isLastPage) {
          this.submitPreGroupSync(groups);
        }
      },

      async submitPreGroupSync (groups) {
        this.isLoading = true;
        try {
          const { code, result } = await this.$store.dispatch('permTemplate/preGroupSync', {
            id: this.$route.params.id,
            data: {
              groups
            }
          });
          if (code === 0 || result) {
            await this.handleUpdateCommit(false);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          setTimeout(() => {
            this.isLoading = false;
          }, 300);
        }
      },

      async handleUpdateCommit (isLoading = true) {
        if (isLoading) {
          this.isLoading = true;
        }
        try {
          await this.$store.dispatch('permTemplate/updateCommit', {
            id: this.$route.params.id
          });
          this.messageSuccess(this.$t(`m.info['提交成功']`), 3000);
          this.$router.push({
            name: 'actionsTemplate'
          });
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          if (isLoading) {
            this.isLoading = false;
          }
        }
      },

      handleNoGroupOperate (payload) {
        const typeMap = {
          prev: () => {
            this.$parent.handleSetCurActionStep && this.$parent.handleSetCurActionStep(1);
          },
          submit: async () => {
            try {
              // 如果没有操作变更不需要调用接口
              if (
                JSON.stringify(this.selectActionsBack)
                === JSON.stringify(this.selectActions)
              ) {
                this.messageSuccess(this.$t(`m.info['提交成功']`), 3000);
                this.$router.push({
                  name: 'actionsTemplate'
                });
                return;
              }
              const actionIdList = this.selectActions.map((item) => item.id);
              const { data } = await this.$store.dispatch('permTemplate/addPreUpdateInfo', {
                id: this.id,
                data: {
                  action_ids: actionIdList
                }
              });
              if (data) {
                await this.handleUpdateCommit();
              }
            } catch (e) {
              this.messageAdvancedError(e);
            }
          },
          cancel: () => {
            this.$router.push({
              name: 'actionsTemplate'
            });
          }
        };
        return typeMap[payload]();
      },

      async handleAllInstanceFill () {
        const syncGroupList = cloneDeep(this.allSyncGroupList);
        if (this.$refs.syncRef && syncGroupList.length) {
          const hasFillGroup = syncGroupList.filter((item) =>
            item.tableList.some((v) => this.batchFillActions(v).length > 0)
          );
          if (!hasFillGroup.length) {
            this.messageWarn(this.$t(`m.common['暂无可一键填充实例']`), 3000);
            return;
          }
          this.fillLoading = true;
          // 过滤掉不能引用的操作
          const fillActions = this.cloneActions.filter((item) =>
            this.addActions.map((v) => v.id).includes(item.action_id)
          );
          const groupIdList = hasFillGroup.map((item) => item.id);
          try {
            for (let i = 0; i < fillActions.length; i++) {
              const { action_id, copy_from_actions } = fillActions[i];
              if (copy_from_actions.length) {
                const { data } = await this.$store.dispatch('permTemplate/getCloneAction', {
                  id: this.id,
                  data: {
                    action_id,
                    clone_from_action_id: copy_from_actions[0].id,
                    group_ids: groupIdList
                  }
                });
                syncGroupList.forEach((item) => {
                  const temp = data.find(sub => sub.group_id === item.id);
                  if (temp) {
                    const curTableIndex = item.tableList.findIndex((v) => {
                      if (['add'].includes(v.mode_type)) {
                        if (v.isAggregate) {
                          return v.actions.map((sub) => sub.id).includes(temp.policy.id);
                        }
                        return v.id === temp.policy.id;
                      }
                    });
                    if (curTableIndex > -1) {
                      item.tableList.splice(curTableIndex, 1, new SyncPolicy({ ...temp.policy, tag: 'add', mode_type: 'add' }, 'detail'));
                    }
                  }
                });
              }
            }
            this.$nextTick(() => {
              this.$refs.syncRef && this.$refs.syncRef.setAggregateTableData(syncGroupList);
            });
          } catch (e) {
            this.messageAdvancedError(e);
          } finally {
            this.fillLoading = false;
          }
        }
      },

      async handleReferInstance (resItem, act, row, index, $index) {
        window.changeDialog = true;
        this.fillLoading = true;
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
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.fillLoading = false;
        }
      },

      handleAllNoLimited () {
        const { syncGroupList } = this.$refs.syncRef;
        if (this.$refs.syncRef && syncGroupList.length) {
          syncGroupList.forEach((item, index) => {
            this.$refs.syncRef.handleGroupNoLimited(item, index);
          });
        }
      },

      handleChangeAggregate (payload) {
        if (this.isAggregateDisabled || this.aggregateType === payload) {
          return;
        }
        this.aggregateType = payload;
        const typeMap = {
          'action-instance': () => {
            this.handleAggregateByAction(true);
          },
          'resource-type': () => {},
          'no-aggregate': () => {
            this.handleAggregateByAction(false);
          }
        };
        return typeMap[payload]();
      },

      handleAggregateByAction (payload) {
        const actionIds = [];
        const aggregationData = [];
        const newTableData = [];
        let addActionsList = [];
        const aggregationAction = cloneDeep(this.aggregations);
        const syncGroupList = cloneDeep(this.allSyncGroupList);
        if (this.addActions.length) {
          addActionsList = this.addActions.map((item) => item.id);
        }
        aggregationAction.forEach((item) => {
          item.actions.forEach((v) => {
            if (addActionsList.includes(v.id)) {
              actionIds.push(v.id);
            }
          });
          item.actions = item.actions.filter((v) => addActionsList.includes(v.id));
        });
        this.$nextTick(() => {
          syncGroupList.forEach((group) => {
            if (payload) {
              // 缓存新增加的操作权限数据
              aggregationAction.forEach((item) => {
                const filterList = group.tableList.filter((v) => {
                  return item.actions.map((v) => v.id).includes(v.id) && ['add'].includes(v.mode_type);
                });
                const addList = filterList.filter((item) =>
                  !this.aggregationsTableData.map((v) => v.id).includes(item.id)
                )
                ;
                if (addList.length > 0) {
                  this.aggregationsTableData.push(...addList);
                }
              });
              const aggregations = aggregationAction.filter((item) => {
                const target = item.actions.map((v) => v.id).sort();
                const existData = group.tableList.find((v) => {
                  return (
                    v.isAggregate
                    && ['add'].includes(v.mode_type)
                    && isEqual(target, v.actions.map((action) => action.id).sort())
                  );
                });
                return !existData;
              })
                .map((item) => {
                  const existTableData = this.aggregationsTableData.filter((subItem) =>
                    item.actions.map((act) => act.id).includes(subItem.id)
                  );
                  if (existTableData.length > 0) {
                    item.tag = existTableData.every((subItem) => subItem.tag === 'unchanged')
                      ? 'unchanged'
                      : 'add';
                    if (item.tag === 'add') {
                      const conditions = existTableData.map((subItem) =>
                        subItem.resource_groups && subItem.resource_groups.length
                          ? subItem.resource_groups[0].related_resource_types[0].condition
                          : []
                      );
                      // 是否都选择了实例
                      const isAllHasInstance = conditions.every(
                        (subItem) => subItem[0] !== 'none'
                      );
                      if (isAllHasInstance) {
                        const instances = conditions.map((subItem) =>
                          subItem.map((v) => v.instance || v.instances || [])
                        );
                        let isAllEqual = true;
                        for (let i = 0; i < instances.length - 1; i++) {
                          if (!isEqual(instances[i], instances[i + 1])) {
                            isAllEqual = false;
                            break;
                          }
                        }
                        if (isAllEqual) {
                          const instanceData = instances[0][0];
                          item.instances = [];
                          instanceData
                            && instanceData.map((pathItem) => {
                              const instance = pathItem.path.map((e) => {
                                return {
                                  id: e[0].id,
                                  name: e[0].name,
                                  type: e[0].type
                                };
                              });
                              item.instances.push(...instance);
                            });
                          this.setInstancesDisplayData(item);
                        } else {
                          item.instances = [];
                        }
                      } else {
                        item.instances = [];
                      }
                    }
                  }
                  return new AggregationPolicy({ ...item, ...{ mode_type: 'add' } });
                });
              group.tableList = group.tableList.filter((item) => !actionIds.includes(item.id));
              group.tableList.push(...aggregations);
              return;
            }
            // 如果是非聚合操作，需要过滤掉聚合操作
            if (!payload) {
              group.tableList = group.tableList.filter((v) => !v.isAggregate);
            }
            group.tableList.forEach((item) => {
              if (['add'].includes(item.mode_type)) {
                if (!item.isAggregate) {
                  newTableData.push(item);
                } else {
                  aggregationData.push(cloneDeep(item));
                }
              }
            });
            const reallyActionIds = actionIds.filter((item) => !newTableData.map((v) => v.id).includes(item));
            reallyActionIds.forEach((item) => {
              // 优先从已有权限取值
              const curObj = this.aggregationsTableData.find((v) => v.id === item);
              if (curObj) {
                group.tableList.push(curObj);
              } else {
                const curAction = this.linearActionList.find((v) => v.id === item);
                const curAggregation = aggregationData.find((v) => v.actions.map((v) => v.id).includes(item));
                group.tableList.push(new SyncPolicy({ ...curAction, tag: 'add' }, 'detail'));
                if (curAggregation && curAggregation.instances.length > 0) {
                  const curData = group.tableList[0];
                  const instances = (() => {
                    const arr = [];
                    const aggregateResourceType = curAggregation.aggregateResourceType;
                    aggregateResourceType.forEach((aggregateResourceItem) => {
                      const { id, name, system_id } = aggregateResourceItem;
                      curAggregation.instances.forEach((v) => {
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
                    });
                    return arr;
                  })();
                  if (instances.length > 0) {
                    curData.resource_groups.forEach((groupItem) => {
                      groupItem.related_resource_types
                        && groupItem.related_resource_types.forEach((subItem) => {
                          subItem.condition = [new Condition({ instances }, '', 'add')];
                        });
                    });
                  }
                }
              }
            });
          });
          this.$refs.syncRef.setAggregateTableData(syncGroupList);
        });
      },

      setInstancesDisplayData (data) {
        data.instancesDisplayData = data.instances.reduce((p, v) => {
          if (!p[v['type']]) {
            p[v['type']] = [];
          }
          p[v['type']].push({
            id: v.id,
            name: v.name
          });
          return p;
        }, {});
      },

      handleExpand (payload) {
        this.curExpandData = payload.expand ? payload : {};
      },

      handleChangeLocationIndex () {
        this.curLocationIndex++;
        if (this.curLocationIndex > this.locationList.length) {
          this.curLocationIndex = 1;
        }
        this.$nextTick(() => {
          const { name, id, expand } = this.locationList[this.curLocationIndex - 1];
          if (expand) {
            return;
          }
          this.$refs.syncRef.handleExpand(this.locationList[this.curLocationIndex - 1]);
          if (this.$refs.syncRef.$refs) {
            this.scrollToLocation(this.$refs.syncRef.$refs[`${name}&${id}`][0]);
          }
        });
      },

      handleChangeTypeData (payload) {
        const { locationList, allActionList } = payload;
        this.locationList = locationList || [];
        this.allSyncGroupList = allActionList || [];
      },

      handleAllSubmit (payload) {
        this.isLastPage = payload;
      },

      handlePrevStep (payload) {
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(
          () => {
            const typeMap = {
              prev: async () => {
                this.prevLoading = true;
                try {
                  await this.$store.dispatch('permTemplate/cancelPreUpdate', {
                    id: this.$route.params.id
                  });
                  this.$parent.handleSetCurActionStep
                    && this.$parent.handleSetCurActionStep(1);
                } catch (e) {
                  this.messageAdvancedError(e);
                } finally {
                  this.prevLoading = false;
                }
              },
              cancel: () => {
                this.$router.push({
                  name: 'actionsTemplate'
                });
              }
            };
            typeMap[payload]();
          },
          (_) => _
        );
      },

      handleGetAddAction (payload) {
        const tempActions = [];
        payload.forEach((item) => {
          item.actions.forEach((act) => {
            if (
              ['added'].includes(act.flag)
              || (['unchecked'].includes(act.tag) && act.checked)
            ) {
              tempActions.push(act);
            }
          });
          (item.sub_groups || []).forEach((sub) => {
            sub.actions.forEach((act) => {
              if (
                ['added'].includes(act.flag)
                || (['unchecked'].includes(act.tag) && act.checked)
              ) {
                tempActions.push(act);
              }
            });
          });
        });
        return tempActions;
      },

      handleToggleExpand () {
        this.isFullScreen = !this.isFullScreen;
        this.handleResizeView();
      },

      handleDragMouseenter () {
        if (this.isDrag) {
          return;
        }
        this.isDrag = true;
        document.addEventListener('mousemove', this.handleDragMousemove);
        document.addEventListener('mouseup', this.handleDragMouseup);
      },

      handleDragMouseup (e) {
        this.dragWidth = this.dragRealityWidth;
        this.isDrag = false;
        document.removeEventListener('mousemove', this.handleDragMousemove);
        document.removeEventListener('mouseup', this.handleDragMouseup);
      },

      handleDragMousemove (e) {
        const { clientX } = e;
        if (!this.isDrag) {
          return;
        }
        const minWidth = window.innerWidth / 2;
        const maxWidth = minWidth + 600;
        if (clientX < minWidth || clientX >= maxWidth) {
          return;
        }
        this.dragRealityWidth = window.innerWidth - clientX - this.navWidth;
      },

      handleResizeView () {
        const resizeWidth = window.innerWidth / 2 - this.navWidth;
        [this.dragWidth, this.dragRealityWidth] = [resizeWidth, resizeWidth];
      }
    }
  };
</script>

<style lang="postcss" scoped>
.sync-group-wrapper {
  .sync-group-content {
    position: relative;
    display: flex;
    &-left {
      width: calc(100% - 680px);
      .related-instance-header {
        padding-top: 16px;
        position: sticky;
        top: 0;
        left: 0;
        z-index: 2;
        .header-title {
          position: relative;
          font-weight: 700;
          font-size: 14px;
          color: #313238;
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
            -webkit-transform: translate(3px, -50%);
            transform: translate(3px, -50%);
          }
        }
        .header-content {
          margin-top: 12px;
          flex-wrap: wrap;
          &-btn {
            display: flex;
            align-items: center;
            padding-bottom: 12px;
            .operate-btn {
              font-size: 0;
              .bk-button {
                font-size: 12px;
                margin-right: 8px;
                &.fill {
                  min-width: 72px;
                }
                &.no-limited {
                  min-width: 84px;
                }
              }
            }
            .aggregate-type-list {
              min-width: 108px;
              position: relative;
              display: flex;
              justify-content: space-between;
              background-color: #eaebf0;
              border-radius: 2px;
              cursor: pointer;
              .aggregate-action-btn {
                background-color: #eaebf0;
                border: 4px solid #eaebf0;
                padding: 4px 12px;
                font-size: 12px;
                &.is-active {
                  color: #3a84ff;
                  background-color: #ffffff;
                }
                &.is-disabled {
                  cursor: not-allowed;
                }
              }
            }
          }
          .location-fill-btn {
            display: flex;
            align-items: center;
            min-width: 123px;
            height: 32px;
            line-height: 32px;
            padding: 0 12px;
            margin-bottom: 12px;
            background-color: #ffffff;
            border: 1px solid #c4c6cc;
            border-radius: 2px;
            box-sizing: border-box;
            vertical-align: middle;
            cursor: pointer;
            .location-icon {
              margin-right: 4px;
            }
            .location-content {
              font-size: 12px;
              color: #63656e;
            }
            &.is-disabled {
              cursor: inherit;
              .location-icon {
                color: #dcdee5;
              }
              .location-content {
                color: #c4c6cc;
              }
            }
          }
        }
      }
      .related-instance-table {
        overflow-y: auto;
        max-height: calc(100vh - 246px);
        &::-webkit-scrollbar {
          width: 6px;
          height: 6px;
          margin-left: 5px;
        }
        &::-webkit-scrollbar-thumb {
          background: #dcdee5;
          border-radius: 3px;
        }
        &::-webkit-scrollbar-track {
          background: transparent;
          border-radius: 3px;
        }
      }
      &.is-full {
        width: 100%;
      }
    }
    &-center {
      width: 16px;
      margin-left: 10px;
      height: calc(100vh - 61px);
      .expand-icon {
        width: 16px;
        height: 64px;
        background-color: #dcdee5;
        border-radius: 4px 0 0 4px;
        position: relative;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        .icon {
          color: #ffffff;
          font-size: 22px !important;
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
        }
        &:hover {
          background-color: #3a84ff;
        }
      }
    }
    &-right {
      position: relative;
      padding: 16px 0;
      height: calc(100vh - 61px);
      overflow: hidden;
      .drag-dotted-line {
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        border-left: 1px solid #dcdee5;
        background-color: #ffffff;
        z-index: 98;
      }
      .drag-line {
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 1px;
        background-color: #dcdee5;
        z-index: 98;
        .drag-bar {
          position: relative;
          top: calc(50% - 15px);
          left: 2px;
          width: 9px;
          color: #979ba5;
          cursor: col-resize;
        }
      }
    }
    &.is-full {
      .sync-group-content-left {
        flex: 0 0 100%;
      }
      .sync-group-content-center {
        .expand-icon {
          border-radius: 0 4px 4px 0;
        }
      }
      .sync-group-content-right {
        display: none;
      }
    }
  }
  .sync-group-btn {
    font-size: 0;
    .bk-button {
      min-width: 88px;
      margin-right: 8px;
    }
  }
  /deep/ .no-sync-group {
    position: absolute;
    top: 45%;
    left: 50%;
    transform: translate(-50%, -45%);
    .part-img {
      width: 440px !important;
    }
    .part-text {
      .empty-text {
        font-size: 20px;
        color: #63656e;
      }
      .tip-wrap {
        margin-top: 16px;
        .tip-message {
          font-size: 14px;
        }
      }
    }
    &-btn {
      margin-top: 24px;
      text-align: center;
      font-size: 0;
      .bk-button {
        min-width: 88px;
        margin-right: 8px;
      }
    }
  }
}
</style>
