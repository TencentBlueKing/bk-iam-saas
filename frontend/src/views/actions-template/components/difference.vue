<template>
  <div class="sync-group-wrapper">
    <template v-if="hasRelatedGroup">
      <smart-action>
        <div :class="['sync-group-content', { 'is-full': isFullScreen }]">
          <div :class="['sync-group-content-left']" :style="leftStyle">
            <div class="related-instance-header">
              <div class="header-title">{{ $t(`m.actionsTemplate['关联用户组的实例']`)}}</div>
              <div class="flex-between header-content">
                <div class="header-content-btn">
                  <div class="operate-btn">
                    <bk-button
                      theme="primary"
                      class="fill"
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
                  :class="['location-fill-btn', { 'is-disabled': locationList.length === 0 }]"
                  @click.stop="handleChangeLocationIndex"
                >
                  <Icon type="locate" class="location-icon" />
                  <div class="location-content">
                    <span class="location-tip">{{ $t(`m.common['定位未填写']`)}}</span>
                    <span v-if="curLocationIndex > 0 && locationList.length > 0" class="location-count">
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
                @on-ready="handleSyncReady"
                @on-expand="handleExpand"
                @on-get-sync-group="handleGetSyncGroup"
                @on-change-location-group="handleChangeLocationCount"
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
            <bk-button
              :loading="prevLoading"
              @click.stop="handlePrevStep('prev')"
            >
              {{ $t(`m.common['上一步']`) }}
            </bk-button>
            <bk-popover
              :content="$t(`m.actionsTemplate['还有用户组未完成实例关联']`)"
              :disabled="(!isLastPage && !isNoAddActions)"
            >
              <bk-button
                theme="primary"
                :loading="isLoading"
                :disabled="(disabled || !isLastPage) && !isNoAddActions"
                @click.stop="handleNextStep">
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
        <bk-button theme="primary" @click.stop="handleNoGroupOperate('submit')"
        >
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
  import { guid } from '@/common/util';
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
        locationList: [],
        addActions: [],
        policyList: [],
        aggregations: [],
        aggregationsBackup: []
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
            'width': `calc(100% - ${this.dragWidth}px)`
          };
        }
        return {
          'width': `calc(100% - ${window.innerWidth / 2 - this.navWidth}px)`
        };
      },
      rightStyle () {
        if (this.dragWidth > 0) {
          return {
            'flexBasis': `${this.dragWidth}px`
          };
        }
        return {
          'flexBasis': `${(window.innerWidth / 2) - this.navWidth}px`
        };
      },
      dragStyle () {
        return {
          'right': `${this.dragWidth}px`
        };
      },
      dottedLineStyle () {
        return {
          'right': `${this.dragRealityWidth}px`
        };
      }
    },
    watch: {
      navStick (value) {
        this.navWidth = value ? 260 : 60;
      },
      actions: {
        async handler (value) {
          const tempActions = await this.handleGetAddAction(value);
          this.addActions = tempActions;
          this.isNoAddActions = this.addActions.length < 1;
          console.log(tempActions, '新增的操作');
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
      async fetchAggregationAction (payload) {
        try {
          const { systemId } = this.$route.params;
          const { data } = await this.$store.dispatch('aggregate/getAggregateAction', { system_ids: systemId });
          if (data.aggregations && data.aggregations.length > 0) {
            const actionIds = [];
            const aggregations = [];
            // 过滤掉不存在当前系统下的操作
            // this.originalCustomTmplList.forEach(item => {
            //   actionIds.push(...item.actions.map(_ => _.id));
            //   if (item.sub_groups && item.sub_groups.length > 0) {
            //     item.sub_groups.forEach(subItem => {
            //       actionIds.push(...subItem.actions.map(_ => _.id));
            //     });
            //   }
            // });
            data.aggregations.forEach(item => {
              const { actions, aggregate_resource_types } = item;
              const curActions = actions.filter((item) => actionIds.includes(item.id));
              if (curActions.length > 0) {
                aggregations.push({
                  actions: curActions,
                  aggregate_resource_types
                });
              }
            });
            this.aggregationsBackup = cloneDeep(aggregations);
            this.aggregations = aggregations;
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
        groups.forEach(e => {
          e.actions.forEach(_ => {
            if (!_.resource_groups || !_.resource_groups.length) {
              _.resource_groups = (_.related_resource_types && _.related_resource_types.length) ? [{ id: '', related_resource_types: _.related_resource_types }] : [];
            }
          });
        });
        if (flag) {
          return;
        }
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

      async handlePreGroupSync (groups) {
        try {
          await this.$store.dispatch('permTemplate/preGroupSync', {
            id: this.$route.params.id,
            data: {
              groups
            }
          });
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async submitPreGroupSync (groups) {
        this.isLoading = true;
        try {
          await this.handlePreGroupSync(groups);
          await this.handleUpdateCommit(false);
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
              if (JSON.stringify(this.selectActionsBack) === JSON.stringify(this.selectActions)) {
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

      handleAllInstanceFill () {
        const { syncGroupList, isCurGroupAllEmpty } = this.$refs.syncRef;
        if (this.$refs.syncRef && syncGroupList.length) {
          const isEmpty = syncGroupList.every((item) => isCurGroupAllEmpty(item));
          if (isEmpty) {
            this.messageWarn(this.$t(`m.common['暂无可批量复用实例']`), 3000);
            return;
          }
          syncGroupList.forEach((item) => {
            this.$refs.syncRef.handleBatchRepeat(item, 'all');
          });
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
        console.log(payload, this.$refs.syncRef);
        if (this.isAggregateDisabled || this.aggregateType === payload) {
          return;
        }
        this.aggregateType = payload;
        const typeMap = {
          'action-instance': async () => {
            await this.fetchAggregationAction();
            this.handleAggregateByAction(true);
          },
          'resource-type': () => {

          },
          'no-aggregate': () => {
            this.handleAggregateByAction(false);
          }
        };
        return typeMap[payload]();
      },

      handleAggregateByAction (payload) {
        const tempData = [];
        let templateIds = [];
        const tableList = cloneDeep(this.allSyncGroupList);
        let instancesDisplayData = {};
        if (payload) {
          tableList.forEach((item) => {
            console.log(item);
            item.tableList.forEach((sub) => {
              if (!sub.aggregationId) {
                tempData.push(sub);
                templateIds.push(item.detail.id);
              }
            });
          });
          for (const [key, value] of this.curMap.entries()) {
            if (value.length === 1) {
              tempData.push(...value);
            } else {
              let curInstances = [];
              const conditions = value.map(subItem => subItem.resource_groups[0].related_resource_types[0].condition);
              // 是否都选择了实例
              const isAllHasInstance = conditions.every(subItem => subItem[0] !== 'none' && subItem.length > 0);
              if (isAllHasInstance) {
                const instances = conditions.map(subItem => subItem.map(v => v.instance));
                let isAllEqual = true;
                for (let i = 0; i < instances.length - 1; i++) {
                  if (!isEqual(instances[i], instances[i + 1])) {
                    isAllEqual = false;
                    break;
                  }
                }
                if (isAllEqual) {
                  // const instanceData = instances[0][0][0];
                  // curInstances = instanceData.path.map(pathItem => {
                  //     return {
                  //         id: pathItem[0].id,
                  //         name: pathItem[0].name
                  //     };
                  // });
                  const instanceData = instances[0][0];
                  console.log('instanceData', instanceData);
                  curInstances = [];
                  instanceData.forEach(pathItem => {
                    const instance = pathItem.path.map(e => {
                      return {
                        id: e[0].id,
                        name: e[0].name,
                        type: e[0].type
                      };
                    });
                    curInstances.push(...instance);
                  });
                  instancesDisplayData = this.setInstancesDisplayData(curInstances);
                  console.log('instancesDisplayData', instancesDisplayData);
                } else {
                  curInstances = [];
                }
              } else {
                curInstances = [];
              }
              tempData.push(
                new AggregationPolicy({
                  aggregationId: key,
                  aggregate_resource_types: value[0].aggregateResourceType,
                  actions: value,
                  instances: curInstances,
                  instancesDisplayData
                })
              );
            }
            templateIds.push(value[0].detail.id);
          }
        } else {
          this.tableList.forEach(item => {
            if (item.hasOwnProperty('isAggregate') && item.isAggregate) {
              const actions = this.curMap.get(item.aggregationId);
              tempData.push(...actions);
              templateIds.push(actions[0].detail.id);
            } else {
              tempData.push(item);
              templateIds.push(item.detail.id);
            }
          });
        }
        // 为了合并单元格的计算，需将再次展开后的数据按照相同模板id重新排序组装一下
        const tempList = [];
        templateIds = [...new Set(templateIds)];
        templateIds.forEach(item => {
          const list = tempData.filter(subItem => subItem.detail.id === item);
          tempList.push(...list);
        });
        this.tableList = cloneDeep(tempList);
      },

      handleAggregateData () {
        this.allAggregationData = Object.assign(this.aggregationData, this.aggregationDataByCustom);
        const keys = Object.keys(this.allAggregationData);
        const data = {};
        keys.forEach(item => {
          if (this.allAggregationData[item] && this.allAggregationData[item].length > 0) {
            data[item] = this.allAggregationData[item];
          }
        });
        this.allAggregationData = data;
        this.tableList.forEach(item => {
          const aggregationData = this.allAggregationData[item.detail.system.id];
          if (aggregationData && aggregationData.length) {
            aggregationData.forEach(aggItem => {
              if (aggItem.actions.map(act => act.id).includes(item.id)) {
                const existData = this.tableList.filter(
                  sub => aggItem.actions.find(act => act.id === sub.id)
                    && sub.judgeId === item.judgeId
                );
                if (existData.length > 1) {
                  const temp = existData.find(sub => sub.aggregationId !== '') || {};
                  item.aggregationId = temp.aggregationId || guid();
                  item.aggregateResourceType = aggItem.aggregate_resource_types;
                }
              }
            });
          }
        });
        const aggregationIds = this.tableList.reduce((counter, item) => {
          return item.aggregationId !== '' ? counter.concat(item.aggregationId) : counter;
        }, []);
        console.warn('aggregationIds:');
        console.warn([...new Set(aggregationIds)]);
        if (!this.curMap) {
          this.curMap = new Map();
        }
        this.tableList.forEach(item => {
          if (item.aggregationId !== '') {
            if (!this.curMap.has(item.aggregationId)) {
              this.curMap.set(item.aggregationId, [cloneDeep(item)]);
            } else {
              const temps = this.curMap.get(item.aggregationId);
              if (!temps.map(sub => sub.id).includes(item.id)) {
                temps.push(cloneDeep(item));
              }
            }
          }
        });
      },

      handleGetSyncGroup ({ list }) {
        this.allSyncGroupList = [...list || []];
      },

      handleExpand (payload) {
        this.curExpandData = payload.expand ? payload : {};
      },

      handleChangeLocationIndex () {
        this.curLocationIndex++;
        if (this.curLocationIndex > this.locationList.length) {
          this.curLocationIndex = 1;
        }
        if (!this.locationList[this.curLocationIndex - 1].expand) {
          this.$refs.syncRef.handleExpand(this.locationList[this.curLocationIndex - 1]);
        }
      },
 
      handleChangeLocationCount (payload) {
        const { list } = payload;
        this.locationList = list || [];
      },
 
      handleAllSubmit (payload) {
        this.isLastPage = payload;
      },

      handleSyncReady () {
        this.disabled = false;
      },

      handlePrevStep (payload) {
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(() => {
          const typeMap = {
            prev: async () => {
              this.prevLoading = true;
              try {
                await this.$store.dispatch('permTemplate/cancelPreUpdate', {
                  id: this.$route.params.id
                });
                this.$parent.handleSetCurActionStep && this.$parent.handleSetCurActionStep(1);
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
        }, _ => _);
      },

      handleGetAddAction (payload) {
        const tempActions = [];
        payload.forEach((item) => {
          item.actions.forEach((act) => {
            if (['added'].includes(act.flag) || (['unchecked'].includes(act.tag) && act.checked)) {
              tempActions.push(act);
            }
          });
          (item.sub_groups || []).forEach((sub) => {
            sub.actions.forEach((act) => {
              if (['added'].includes(act.flag) || (['unchecked'].includes(act.tag) && act.checked)) {
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
        // console.log(clientX, minWidth, maxWidth);
        if (clientX < minWidth || clientX >= maxWidth) {
          return;
        }
        this.dragRealityWidth = window.innerWidth - clientX - this.navWidth;
      },

      handleResizeView () {
        const resizeWidth = (window.innerWidth / 2) - this.navWidth;
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
              background-color: #EAEBF0;
              border-radius: 2px;
              cursor: pointer;
              .aggregate-action-btn {
                background-color: #EAEBF0;
                border: 4px solid #EAEBF0;
                padding: 4px 12px;
                font-size: 12px;
                &.is-active {
                  color: #3A84FF;
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
              color: #63656E;
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
          color: #979BA5;
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
        color: #63656E;
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
