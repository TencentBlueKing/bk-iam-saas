<template>
  <smart-action class="iam-grading-admin-create-wrapper">
    <render-horizontal-block :label="$t(`m.common['基本信息']`)">
      <section ref="basicInfoContentRef">
        <basic-info :data="formData" @on-change="handleBasicInfoChange" ref="basicInfoRef" />
      </section>
    </render-horizontal-block>
    <render-horizontal-block
      :label="$t(`m.nav['授权边界']`)"
      :label-width="renderLabelWidth('resource')"
      :required="false"
    >
      <div class="authorize-boundary-form">
        <div class="authorize-resource-boundary">
          <div class="resource-boundary-title is-required">
            {{ $t(`m.levelSpace['最大可授权操作和资源边界']`) }}
          </div>
          <div class="resource-boundary-header flex-between">
            <section>
              <bk-button
                theme="default"
                size="small"
                icon="plus-circle-shape"
                class="perm-resource-add"
                @click.stop="handleAddAction"
              >
                {{ $t(`m.common['添加']`) }}
              </bk-button>
            </section>
            <div v-if="isSelectSystem" class="switch-action-group">
              <div class="all-unlimited-switch">
                <bk-switcher
                  v-model="isAllUnlimited"
                  theme="primary"
                  size="small"
                  :disabled="isUnlimitedDisabled"
                  @change="handleUnlimitedActionChange"
                />
                <span class="expanded-text">{{ $t(`m.common['批量无限制']`) }}</span>
              </div>
              <div class="aggregate-action-group">
 
                <div
                  v-for="item in AGGREGATION_EDIT_ENUM"
                  :key="item.value"
                  :class="[
                    'aggregate-action-btn',
                    { 'is-active': isAllExpanded === item.value },
                    { 'is-disabled': isAggregateDisabled }
                  ]"
                  @click.stop="handleAggregateActionChange(item.value)"
                >
                  <span>{{ $t(`m.grading['${item.name}']`)}}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-show="isSelectSystem">
            <div class="resource-instance-wrapper"
              ref="instanceTableContentRef"
              v-bkloading="{ isLoading, opacity: 1, extCls: 'loading-resource-instance-cls' }">
              <render-instance-table
                ref="resourceInstanceRef"
                :is-all-expanded="isAllExpanded"
                :data="policyList"
                :list="policyList"
                :total-count="originalList.length"
                :group-id="$route.params.id"
                :backup-list="aggregationsTableData"
                @on-delete="handleDelete"
                @on-aggregate-delete="handleAggregateDelete"
                @on-select="handleResourceSelect"
                @on-clear-all="handleDeleteResourceAll"
              />
            </div>
          </div>
        </div>
        <p class="action-empty-error" v-if="isShowActionEmptyError">
          {{ $t(`m.verify['操作和资源边界不可为空']`) }}
        </p>
        <div ref="memberRef" class="authorize-members-boundary">
          <render-member
            :tip="addMemberTips"
            :is-all="isAll"
            :label-width="renderLabelWidth('member')"
            :users="users"
            :departments="departments"
            @on-add="handleAddMember"
            @on-delete="handleMemberDelete"
            @on-delete-all="handleDeleteAll"
          />
        </div>
        <p class="action-empty-error" v-if="isShowMemberEmptyError">
          {{ $t(`m.verify['可授权人员边界不可为空']`) }}
        </p>
      </div>
    </render-horizontal-block>

    <render-horizontal-block
      v-if="isRatingManager"
      ext-cls="reason-wrapper"
      :label="$t(`m.common['理由']`)"
      :required="true">
      <div ref="reasonRef" class="content-wrapper">
        <bk-input
          type="textarea"
          :rows="5"
          :ext-cls="isShowReasonError ? 'join-reason-error' : ''"
          v-model="reason"
        />
      </div>
      <p class="reason-empty-error" v-if="isShowReasonError">{{ $t(`m.verify['理由不可为空']`) }}</p>
    </render-horizontal-block>
    <div slot="action">
      <bk-button theme="primary" type="button" @click="handleSubmit" :loading="submitLoading">
        {{ $t(`m.common['确定']`) }}
      </bk-button>
      <bk-button @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
    </div>

    <add-member-dialog
      :show.sync="isShowAddMemberDialog"
      :users="users"
      :departments="departments"
      :title="addMemberTitle"
      :all-checked="isAll"
      show-limit
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd" />

    <add-action-sideslider
      :all="allSystem"
      :is-show.sync="isShowAddActionSideslider"
      :default-value="curActionValue"
      :default-system="curSystem"
      :default-data="defaultValue"
      @on-submit="handleSelectSubmit"
      @on-cancel="handleSelectCancel"
      @animation-end="handleAnimationEnd" />
  </smart-action>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  // import { leavePageConfirm } from '@/common/leave-page-confirm';
  import basicInfo from '@/views/manage-spaces/components/basic-info';
  // import renderAction from '@/views/manage-spaces/common/render-action';
  import AddMemberDialog from '@/views/group/components/iam-add-member';
  import RenderMember from '@/views/grading-admin/components/render-member';
  import AddActionSideslider from '@/views/manage-spaces/components/add-action-side-slider';
  import GradeAggregationPolicy from '@/model/grade-aggregation-policy';
  import GradePolicy from '@/model/grade-policy';
  import Condition from '@/model/condition';
  import RenderInstanceTable from '@/views/manage-spaces/components/render-instance-table';
  import { guid, renderLabelWidth } from '@/common/util';
  import { AGGREGATION_EDIT_ENUM } from '@/common/constants';
  export default {
    name: '',
    components: {
      basicInfo,
      // renderAction,
      AddMemberDialog,
      RenderMember,
      AddActionSideslider,
      RenderInstanceTable
    },
    data () {
      return {
        renderLabelWidth,
        formData: {
          name: '',
          description: '',
          members: [],
          sync_perm: false
        },
        submitLoading: false,
        addActionTips: this.$t(`m.levelSpace['二级管理空间，授权边界（授权操作范围、授权人员范围）小于等于一级管理员空间']`),
        addMemberTips: this.$t(`m.levelSpace['管理空间缩小/修改授权边界时，同步修改相关的二级管理空间的授权边界']`),
        isShowAddMemberDialog: false,
        users: [],
        departments: [],
        isShowMemberAdd: true,
        isShowAddActionSideslider: false,
        isShowActionEmptyError: false,
        isExpanded: false,
        isAllUnlimited: false,
        curSystem: '',
        curActionValue: [],
        addMemberTitle: this.$t(`m.levelSpace['选择可授权人员边界']`),
        originalList: [],
        isShowMemberEmptyError: false,
        infoText: this.$t(`m.grading['选择提示']`),
        tips: this.$t(`m.levelSpace['二级管理空间，授权边界（授权操作范围、授权人员范围）小于等于一级管理员空间']`),
        policyList: [],
        isLoading: false,
        isAllExpanded: false,
        aggregations: [],
        aggregationsBackup: [],
        aggregationsTableData: [],
        curSystemId: [],
        isShowReasonDialog: false,
        reason: '',
        dialogLoading: false,
        isAll: false,
        isShowTable: false,
        isShowReasonError: false,
        allSystem: true,
        AGGREGATION_EDIT_ENUM
      };
    },
    computed: {
      ...mapGetters(['user']),
      isSelectSystem () {
        return this.originalList.length > 0;
      },
      defaultValue () {
        if (this.originalList.length < 1) {
          return [];
        }
        const tempList = [];
        this.originalList.forEach(item => {
          if (!tempList.some(sys => sys.system_id === item.system_id)) {
            tempList.push({
              system_id: item.system_id,
              system_name: item.system_name,
              list: [item]
            });
          } else {
            const curData = tempList.find(sys => sys.system_id === item.system_id);
            curData.list.push(item);
          }
        });

        return tempList;
      },
      expandedText () {
        return this.isAllExpanded ? this.$t(`m.grading['批量编辑']`) : this.$t(`m.grading['逐项编辑']`);
      },
      isAggregateDisabled () {
        return this.policyList.length < 1
          || this.aggregations.length < 1
          || (this.policyList.length === 1 && !this.policyList[0].isAggregate);
      },
      isUnlimitedDisabled () {
        const isDisabled = this.policyList.every(item =>
          ((!item.resource_groups || (item.resource_groups && !item.resource_groups.length)) && !item.instances)
          );
        if (isDisabled) {
          this.isAllUnlimited = false;
        }
        return isDisabled;
      },
      isStaff () {
        return this.user.role.type === 'staff';
      },
      isRatingManager () {
        return this.user.role.type === 'rating_manager';
      }
    },
    watch: {
      reason () {
        this.isShowReasonError = false;
      },
      originalList: {
        handler (value) {
          this.setPolicyList(value);
          const params = [...new Set(this.policyList.map(item => item.system_id))];
          // 无新增的的系统时无需请求聚合数据
          const difference = params.filter(item => !this.curSystemId.includes(item));
          if (difference.length > 0) {
            this.curSystemId = [...this.curSystemId.concat(difference)];
            this.resetData();
            if (this.policyList.length > 1) {
              this.fetchAggregationAction(this.curSystemId.join(','));
            }
          } else {
            const data = this.getFilterAggregation(this.aggregationsBackup);
            this.aggregations = _.cloneDeep(data);
          }
        },
        deep: true
      }
    },
    methods: {
      isShowTableClick () {
        this.isShowTable = !this.isShowTable;
      },
      async fetchPageData () {
        await this.fetchRatingManagerDetail();
      },

      setPolicyList (payload) {
        if (this.policyList.length < 1) {
          this.policyList = payload.map(item => new GradePolicy(item));
          return;
        }
        const isAddIds = payload.map(item => `${item.system_id}&${item.id}`);
        const isExistIds = [];
        this.policyList.forEach(item => {
          if (item.isAggregate) {
            item.actions.forEach(subItem => {
              isExistIds.push(`${item.system_id}&${subItem.id}`);
            });
          } else {
            isExistIds.push(`${item.system_id}&${item.id}`);
          }
        });
        // 下一次选择的与现存的交集
        const intersectionIds = isExistIds.filter(item => isAddIds.includes(item));
        // 下一次选择所删除的操作
        const existRestIds = isExistIds.filter(item => !intersectionIds.includes(item));
        // 下一次选择所新增的操作
        const newRestIds = isAddIds.filter(item => !intersectionIds.includes(item));
        if (existRestIds.length > 0) {
          const tempData = [];
          this.policyList.forEach(item => {
            if (!item.isAggregate && !existRestIds.includes(`${item.system_id}&${item.id}`)) {
              tempData.push(item);
            }
            if (item.isAggregate) {
              const tempList = existRestIds.filter(act => item.actions.map(v => `${item.system_id}&${v.id}`).includes(act));
              if (tempList.length > 0) {
                item.actions = item.actions.filter(act => !tempList.includes(`${item.system_id}&${act.id}`));
              }
              tempData.push(item);
            }
          });
          this.policyList = tempData.filter(
            item => !item.isAggregate || (item.isAggregate && item.actions.length > 0)
          );
        }

        if (newRestIds.length > 0) {
          newRestIds.forEach(item => {
            const curSys = payload.find(sys => `${sys.system_id}&${sys.id}` === item);
            this.policyList.unshift(new GradePolicy(curSys));
          });
        }
      },

      handleResourceSelect (payload) {
        window.changeDialog = true;
        const instances = (function () {
          const arr = [];
          payload.aggregateResourceType.forEach(resourceItem => {
            const { id, name, system_id } = resourceItem;
            payload.instancesDisplayData[id] && payload.instancesDisplayData[id].forEach(v => {
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
        const curAction = payload.actions.map(item => `${payload.system_id}&${item.id}`);
        if (instances.length > 0) {
          this.aggregationsTableData.forEach(item => {
            if (curAction.includes(`${item.system_id}&${item.id}`)) {
              item.resource_groups.forEach(groupItem => {
                groupItem.related_resource_types
                  && groupItem.related_resource_types.forEach(subItem => {
                    subItem.condition = [new Condition({ instances }, '', 'add')];
                  });
              });
            }
          });
        }
      },

      async fetchAggregationAction (payload) {
        this.isLoading = true;
        try {
          const res = await this.$store.dispatch('aggregate/getAggregateAction', { system_ids: payload })
          ;(res.data.aggregations || []).forEach(item => {
            item.$id = guid();
          });
          const data = this.getFilterAggregation(res.data.aggregations);
          this.aggregationsBackup = _.cloneDeep(res.data.aggregations);
          this.aggregations = _.cloneDeep(data);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      getFilterAggregation (payload) {
        const curSelectActions = [];
        this.policyList.forEach(item => {
          if (item.isAggregate) {
            curSelectActions.push(...item.actions.map(v => `${item.system_id}&${v.id}`));
          } else {
            curSelectActions.push(`${item.system_id}&${item.id}`);
          }
        });
        let aggregations = [];
        (payload || []).forEach(item => {
          const { actions, aggregate_resource_types, $id } = item;
          const curActions = actions.filter(_ => curSelectActions.includes(`${_.system_id}&${_.id}`));
          if (curActions.length > 0) {
            aggregations.push({
              actions: curActions,
              aggregate_resource_types,
              $id,
              system_name: this.policyList.find(
                _ => _.system_id === curActions[0].system_id
              ).system_name
            });
          }
        });
        aggregations = aggregations.filter(item => item.actions.length > 1);
        return aggregations;
      },

      resetData () {
        this.aggregations = [];
        this.aggregationsBackup = [];
      },

      handleAggregateAction (payload) {
        if (this.isAggregateDisabled) {
          return;
        }
        window.changeDialog = true;
        this.isAllExpanded = payload;
        const aggregationAction = this.aggregations;
        const actionIds = [];
        aggregationAction.forEach(item => {
          actionIds.push(...item.actions.map(_ => `${_.system_id}&${_.id}`));
        });
        if (payload) {
          // 缓存新增加的操作权限数据
          aggregationAction.forEach(item => {
            const filterArray = this.policyList.filter(subItem => item.actions.map(_ => `${_.system_id}&${_.id}`).includes(`${subItem.system_id}&${subItem.id}`));
            const addArray = filterArray.filter(subItem => !this.aggregationsTableData.map(_ => `${_.system_id}&${_.id}`).includes(`${subItem.system_id}&${subItem.id}`));
            if (addArray.length > 0) {
              this.aggregationsTableData.push(...addArray);
            }
          });
          const aggregations = aggregationAction.filter(item => {
            const target = item.actions.map(v => v.id).sort();
            const existData = this.policyList.find(subItem => {
              return subItem.isAggregate && _.isEqual(target, subItem.actions.map(v => v.id).sort());
            });
            return !existData;
          }).map((item, index) => {
            // 从缓存值中取值
            const isExistActions = this.aggregationsTableData.filter(subItem =>
              item.actions.map(v => `${v.system_id}&${v.id}`).includes(`${subItem.system_id}&${subItem.id}`)
            );
            const conditions = isExistActions.map(subItem => subItem.resource_groups[0]
              .related_resource_types[0].condition);
            // 是否都选择了实例
            const isAllHasInstance = conditions.every(subItem => subItem.length > 0 && subItem[0] !== 'none');
            // 是否所有项都是空实例
            const isAllEmptyInstance = conditions.every(subItem => subItem.length > 0 && subItem[0] === 'none');
            // 是否所有项都是无限制
            const isAllNoLimited = conditions.every(subItem => subItem.length === 0);
            if (isAllHasInstance) {
              const instances = conditions.map(subItem => subItem.map(v => v.instance));
              let isAllEqual = true;
              for (let i = 0; i < instances.length - 1; i++) {
                if (!_.isEqual(instances[i], instances[i + 1])) {
                  isAllEqual = false;
                  break;
                }
              }
              if (isAllEqual) {
                const instanceData = instances[0][0];
                item.instances = [];
                instanceData.map(pathItem => {
                  const instance = pathItem.path.map(e => {
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
              if (isAllNoLimited) {
                item.isNoLimited = true;
                item.isNeedNoLimited = true;
              }
              if (isAllEmptyInstance) {
                item.isAddActions = true;
                item.instances = ['none'];
              }
            }
            return new GradeAggregationPolicy(item);
          });
          this.policyList = this.policyList.filter(item => !actionIds.includes(`${item.system_id}&${item.id}`));
          this.policyList.unshift(...aggregations);
          return;
        }
        const aggregationData = [];
        const newPolicyList = [];
        this.policyList.forEach(item => {
          if (!item.isAggregate) {
            newPolicyList.push(item);
          } else {
            aggregationData.push(_.cloneDeep(item));
          }
        });
        this.policyList = _.cloneDeep(newPolicyList);
        const reallyActionIds = actionIds.filter(item => !this.policyList.map(v => `${v.system_id}&${v.id}`).includes(item));
        reallyActionIds.forEach(item => {
          // 优先从缓存值中取值
          const curObj = this.aggregationsTableData.find(_ => `${_.system_id}&${_.id}` === item);
          if (curObj) {
            this.policyList.unshift(curObj);
          } else {
            const curAction = this.originalList.find(_ => `${_.system_id}&${_.id}` === item);
            const curAggregation = aggregationData.find(_ => _.actions.map(v => `${_.system_id}&${v.id}`).includes(item));
            this.policyList.unshift(new GradePolicy({ ...curAction, tag: 'add' }, 'add'));
            if (curAggregation && curAggregation.instances.length > 0) {
              const curData = this.policyList[0];
              const instances = (function () {
                const arr = [];
                const aggregateResourceType = curAggregation.aggregateResourceType;
                aggregateResourceType.forEach(aggregateResourceItem => {
                  const { id, name, system_id } = aggregateResourceItem;
                  curAggregation.instances.forEach(v => {
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
                curData.related_resource_types.forEach(subItem => {
                  subItem.condition = [new Condition({ instances }, '', 'add')];
                });
              }
            }
          }
        });
      },

      // 批量无限制
      handleUnlimitedActionChange (payload) {
        this.setPolicyList(this.originalList);
        const tableData = _.cloneDeep(this.policyList);
        tableData.forEach((item, index) => {
          if (!item.isAggregate) {
            if (item.resource_groups && item.resource_groups.length) {
              item.resource_groups.forEach(groupItem => {
                groupItem.related_resource_types && groupItem.related_resource_types.forEach(types => {
                  if (!payload && (types.condition.length > 0 && types.condition[0] !== 'none')) {
                    return;
                  }
                  if (payload) {
                    types.condition = [];
                    types.isError = false;
                  }
                  // 取消批量无限制后，还原上一次的操作
                  if (!payload && types.condition.length < 1 && types.conditionBackup.length > 0) {
                    types.condition = _.cloneDeep(types.conditionBackup);
                  }
                });
              });
            } else {
              item.name = item.name.split('，')[0];
            }
          }
          if (item.instances && item.isAggregate) {
            item = Object.assign(item, {
              isNoLimited: false,
              isNeedNoLimited: true,
              isError: !(item.instances.length || (!item.instances.length && item.isNoLimited))
            });
            if (!payload || item.instances.length) {
              item = Object.assign(item, {
                isNoLimited: false,
                isError: false
              });
            }
            if ((!item.instances.length && !payload && item.isNoLimited) || payload) {
              item = Object.assign(item, {
                isNoLimited: true,
                isError: false,
                instances: []
              });
            }
            // 多项相同资源类型只要满足其中一项资源类型有实例就可提交
            // 如果只是其中一项选择了资源，因为[]既代表是空集也代表是无限制，所以无法判断另外资源类型是无限制还是空集
            const curAggregateTab = item.aggregateResourceType[this.$refs.resourceInstanceRef.selectedIndex];
            if (curAggregateTab) {
              const isExistIns = item.instances.length > 0 && item.instances.some(ins => ins.type === curAggregateTab.id && ins !== 'none');
              if (!isExistIns && item.aggregateResourceType.length > 0) {
                const isExistNoLimited = item.aggregateResourceType.length > 1
                  ? Object.values(item.instancesDisplayData).flat(Infinity).length === 0
                  : item.instancesDisplayData[curAggregateTab.id].length < 1;
                // empty或者isAddActions为true代表是新增操作需要清空资源
                const isUnlimited = item.empty || item.isAddActions ? false : isExistNoLimited;
                item = Object.assign(item, {
                  isNoLimited: payload || isUnlimited,
                  isBatchNoLimited: payload
                });
              }
            }
            return this.$set(
              tableData,
              index,
              new GradeAggregationPolicy(item)
            );
          }
        });
        this.policyList = _.cloneDeep(tableData);
      },

      handleAggregateActionChange (payload) {
        this.handleAggregateAction(payload);
        this.handleUnlimitedActionChange(this.isAllUnlimited);
      },

      // 设置InstancesDisplayData
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

      handleGetValue () {
        return this.$refs.resourceInstanceRef && this.$refs.resourceInstanceRef.handleGetValue();
      },

      async fetchRatingManagerDetail () {
        try {
          const res = await this.$store.dispatch('role/getRatingManagerDetail', { id: this.$route.params.id });
          this.handleDetailData(res.data);
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      handleDetailData (payload) {
        const users = [];
        const departments = [];
        const tempActions = [];
        const {
          name,
          description,
          members,
          authorization_scopes,
          subject_scopes,
          sync_perm, reason
        } = payload;
        this.$store.commit('setHeaderTitle', name);
        this.reason = reason || '';
        this.formData = Object.assign({}, {
          name,
          description,
          members,
          sync_perm
        });
        subject_scopes.forEach(item => {
          if (item.type === 'department') {
            departments.push({
              id: Number(item.id),
              type: 'depart',
              name: item.name,
              fullName: item.full_name,
              count: item.member_count
            });
          }
          if (item.type === 'user') {
            users.push({
              type: 'user',
              name: item.name,
              username: item.id
            });
          }
        });
        this.isAll = subject_scopes.some(item => item.type === '*' && item.id === '*');
        this.users.splice(0, this.users.length, ...users);
        this.departments.splice(0, this.departments.length, ...departments);
        this.isShowMemberAdd = false;
        authorization_scopes.forEach(item => {
          item.actions.forEach(act => {
            tempActions.push({
              ...act,
              system_id: item.system.id,
              system_name: item.system.name,
              $id: `${item.system.id}&${act.id}`
            });
          });
        });
        this.originalList = _.cloneDeep(tempActions);
      },
      /**
       * @description: 处理 base-info数据
       * @param {*} field
       * @param {*} data
       * @return {*}
       */
      handleBasicInfoChange (field, data) {
        window.changeDialog = true;
        this.formData[field] = data;
      },

      handleAddAction () {
        this.isShowTable = true;
        this.curActionValue = this.originalList.map(item => item.$id);
        this.isShowAddActionSideslider = true;
      },

      setAggregateExpanded () {
        const flag = this.policyList.every(item => !item.isAggregate);
        if (flag) {
          this.isAllExpanded = false;
        }
      },

      handleDelete (systemId, actionId, payload, index) {
        window.changeDialog = true;
        this.originalList = this.originalList.filter(item => payload !== item.$id);
        this.policyList.splice(index, 1);
        for (let i = 0; i < this.aggregations.length; i++) {
          const item = this.aggregations[i];
          if (item.actions[0].system_id === systemId) {
            item.actions = item.actions.filter(subItem => subItem.id !== actionId);
            break;
          }
        }
        this.aggregations = this.aggregations.filter(item => item.actions.length > 1);
        this.setAggregateExpanded();
      },

      handleDeleteResourceAll () {
        this.originalList = [];
        this.policyList = [];
        this.isAllExpanded = false;
      },

      handleAggregateDelete (systemId, actions, index) {
        window.changeDialog = true;
        this.policyList.splice(index, 1);
        const deleteAction = actions.map(item => `${systemId}&${item.id}`);
        this.originalList = this.originalList.filter(item => !deleteAction.includes(item.$id));
        this.aggregations = this.aggregations.filter(item =>
          !(item.actions[0].system_id === systemId
            && _.isEqual(item.actions.map(_ => _.id).sort(), actions.map(_ => _.id).sort()))
        );
        this.setAggregateExpanded();
      },

      handleSelectSubmit (payload) {
        window.changeDialog = true;
        payload.forEach(e => {
          if (!e.resource_groups || !e.resource_groups.length) {
            e.resource_groups = (e.related_resource_types && e.related_resource_types.length)
              ? [{ id: '', related_resource_types: e.related_resource_types }]
              : [];
          }
        });
        this.originalList = _.cloneDeep(payload);
        // 为了兼容那些没有资源实例的操作，所以要重新聚合一次
        if (this.isAllExpanded) {
          this.handleAggregateAction(false);
          this.isAllExpanded = false;
        }
        // 处理批量无限制，默认为新增的操作选中无实例
        this.handleUnlimitedActionChange(this.isAllUnlimited);
        this.isShowActionEmptyError = false;
        this.isShowAddActionSideslider = false;
      },

      handleSelectCancel () {
        this.isShowAddActionSideslider = false;
      },

      handleAnimationEnd () {
        this.curSystem = '';
        this.curActionValue = [];
        this.isShowAddActionSideslider = false;
      },

      handleAddMember () {
        this.isShowAddMemberDialog = true;
      },

      handleCancelAdd () {
        this.isShowAddMemberDialog = false;
      },

      handleMemberDelete (type, payload) {
        window.changeDialog = true;
        if (type === 'user') {
          this.users.splice(payload, 1);
        } else {
          this.departments.splice(payload, 1);
        }
        this.isShowMemberAdd = this.users.length < 1 && this.departments.length < 1;
      },

      handleDeleteAll () {
        this.isAll = false;
        this.isShowMemberAdd = true;
      },

      handleSubmitAdd (payload) {
        window.changeDialog = true;
        const { users, departments } = payload;
        this.isAll = payload.isAll;
        this.users = _.cloneDeep(users);
        this.departments = _.cloneDeep(departments);
        this.isShowMemberAdd = false;
        this.isShowAddMemberDialog = false;
        this.isShowMemberEmptyError = false;
      },

      handleDialogCancel () {
        this.isShowReasonDialog = false;
        this.dialogLoading = false;
      },

      async handleSubmitWithReason () {
        const subjects = [];
        if (this.isAll) {
          subjects.push({
            id: '*',
            type: '*'
          });
        } else {
          this.users.forEach(item => {
            subjects.push({
              type: 'user',
              id: item.username
            });
          });
          this.departments.forEach(item => {
            subjects.push({
              type: 'department',
              id: item.id
            });
          });
        }
        const { name, description, members, sync_perm } = this.formData;
        const data = this.$refs.resourceInstanceRef.handleGetValue().actions;
        const params = {
          name,
          description,
          members,
          subject_scopes: subjects,
          authorization_scopes: data,
          reason: this.reason,
          id: this.$route.params.id,
          sync_perm
        };
        this.submitLoading = true;
        const dispatchMethod = this.isRatingManager ? 'editRatingManagerWithGeneral' : 'editRatingManager';
        try {
          await this.$store.dispatch(`role/${dispatchMethod}`, params);
          await this.$store.dispatch('role/updateCurrentRole', { id: 0 });
          await this.$store.dispatch('roleList');
          this.messageSuccess(this.$t(`m.info['申请已提交']`), 3000);
          this.$router.push({
            name: 'apply'
          });
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.submitLoading = false;
          window.changeDialog = false;
        }
      },

      async handleSubmit () {
        let flag = false;
        const validatorFlag = this.$refs.basicInfoRef.handleValidator();
        this.isShowActionEmptyError = this.originalList.length < 1;
        this.isShowMemberEmptyError = (this.users.length < 1 && this.departments.length < 1) && !this.isAll;
        this.isShowReasonError = !this.reason;
        if (!this.isShowActionEmptyError) {
          flag = this.$refs.resourceInstanceRef.handleGetValue().flag;
        }
        if (validatorFlag) {
          this.scrollToLocation(this.$refs.basicInfoContentRef);
          return;
        }
        if (flag || this.isShowActionEmptyError) {
          this.scrollToLocation(this.$refs.instanceTableContentRef);
          return;
        }
        if (this.isShowMemberEmptyError) {
          this.scrollToLocation(this.$refs.memberRef);
          return;
        }
        if (this.isShowReasonError) {
          this.scrollToLocation(this.$refs.reasonRef);
          return;
        }
        await this.handleSubmitWithReason();
      },

      handleCancel () {
        this.$router.push({
          name: 'authorBoundary',
          params: {
            id: this.$route.params.id
          }
        });
      },

      handleReasonInput () {
        this.isShowReasonError = false;
      },

      handleReasonBlur (payload) {
        if (!payload) {
          this.isShowReasonError = true;
        }
      }
    }
  };
</script>

<style lang="postcss">
.iam-edit-rate-manager-reason-dialog {
  .content-wrapper {
    display: flex;
    justify-content: flex-start;
    label {
      display: block;
      width: 70px;
      span {
        color: #ea3636;
      }
    }
  }
}
</style>

<style lang="postcss" scoped>
@import '@/css/mixins/authorize-boundary.css';
</style>
