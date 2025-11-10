<template>
  <smart-action class="iam-grading-admin-create-wrapper">
    <render-horizontal-block :label="$t(`m.common['基本信息']`)">
      <section ref="basicInfoContentRef">
        <basic-info
          :data="formData"
          @on-change="handleBasicInfoChange"
          ref="basicInfoRef"
        />
      </section>
    </render-horizontal-block>
    <render-horizontal-block
      v-if="isSelectSystem || isSelectSystemShow"
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
            <div v-if="isSelectSystemShow" class="switch-action-group">
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
                <iam-guide
                  type="rating_manager_merge_action"
                  direction="right"
                  :loading="isLoading"
                  :cur-style="renderLabelWidth('rating_manager_merge_action_guide')"
                  :content="$t(`m.guide['聚合操作']`)" />
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
          <div v-if="isSelectSystemShow">
            <div
              class="resource-instance-wrapper"
              ref="instanceTableContentRef"
              v-bkloading="{
                isLoading,
                opacity: 1,
                zIndex: 1000,
                extCls: 'loading-resource-instance-cls'
              }"
            >
              <render-instance-table
                ref="resourceInstanceRef"
                :is-all-expanded="isAllExpanded"
                :data="policyList"
                :list="policyList"
                :backup-list="aggregationsTableData"
                :total-count="originalList.length"
                @on-delete="handleDelete"
                @on-aggregate-delete="handleAggregateDelete"
                @on-select="handleAttrValueSelected"
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
      v-if="isStaff"
      ext-cls="reason-wrapper"
      :label="$t(`m.common['理由']`)"
      :required="true"
    >
      <section class="content-wrapper" ref="reasonRef">
        <bk-input
          type="textarea"
          :rows="5"
          :ext-cls="isShowReasonError ? 'join-reason-error' : ''"
          v-model="reason"
          @input="handleReasonInput"
          @blur="handleReasonBlur"
        >
        </bk-input>
      </section>
      <p class="reason-empty-error" v-if="isShowReasonError">
        {{ $t(`m.verify['理由不可为空']`) }}
      </p>
    </render-horizontal-block>
    <div slot="action">
      <bk-button
        theme="primary"
        type="button"
        @click="handleSubmit"
        data-test-id="grading_btn_createSubmit"
        :loading="submitLoading"
      >
        {{ $t(`m.common['提交']`) }}
      </bk-button>
      <bk-button style="margin-left: 10px" @click="handleCancel">{{
        $t(`m.common['取消']`)
      }}</bk-button>
    </div>

    <add-member-dialog
      :show.sync="isShowAddMemberDialog"
      :users="users"
      :departments="departments"
      :title="addMemberTitle"
      :all-checked="isAll"
      show-limit
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd"
    />

    <add-action-side-slider
      :is-show.sync="isShowAddActionSideSlider"
      :default-value="curActionValue"
      :default-data="defaultValue"
      @on-submit="handleSelectSubmit"
    />
  </smart-action>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { guid, renderLabelWidth } from '@/common/util';
  // import { leavePageConfirm } from '@/common/leave-page-confirm';
  import { AGGREGATION_EDIT_ENUM } from '@/common/constants';
  import IamGuide from '@/components/iam-guide/index';
  import basicInfo from '@/views/manage-spaces/components/basic-info';
  // import renderAction from '@/views/manage-spaces/common/render-action';
  import AddMemberDialog from '@/views/group/components/iam-add-member';
  import RenderMember from '@/views/grading-admin/components/render-member';
  import RenderInstanceTable from '@/views/manage-spaces/components/render-instance-table';
  import AddActionSideSlider from '@/views/manage-spaces/components/add-action-side-slider';
  import GradeAggregationPolicy from '@/model/grade-aggregation-policy';
  import GradePolicy from '@/model/grade-policy';
  import Condition from '@/model/condition';
  export default {
    components: {
      IamGuide,
      basicInfo,
      // renderAction,
      AddMemberDialog,
      RenderMember,
      AddActionSideSlider,
      RenderInstanceTable
    },
    props: {
      id: {
        type: [String, Number],
        default: 0
      }
    },
    data () {
      return {
        renderLabelWidth,
        formData: {
          name: '',
          description: '',
          members: [],
          sync_perm: true
        },
        users: [],
        departments: [],
        originalList: [],
        curActionValue: [],
        policyList: [],
        aggregations: [],
        aggregationsBackup: [],
        aggregationsTableData: [],
        curSystemId: [],
        reason: '',
        operate: '',
        tips: this.$t(`m.grading['添加操作提示']`),
        // infoText: this.$t(`m.grading['选择提示']`),
        addMemberTips: this.$t(
          `m.levelSpace['管理空间缩小/修改授权边界时，同步修改相关的二级管理空间的授权边界']`
        ),
        addMemberTitle: this.$t(`m.levelSpace['最大可授权人员边界']`),
        submitLoading: false,
        isShowAddMemberDialog: false,
        isShowMemberAdd: false,
        isShowAddActionSideSlider: false,
        isShowActionEmptyError: false,
        isShowReasonError: false,
        isExpanded: false,
        isShowMemberEmptyError: false,
        isShowReasonDialog: false,
        dialogLoading: false,
        isLoading: false,
        isAllExpanded: false,
        isAll: false,
        isAllUnlimited: false,
        AGGREGATION_EDIT_ENUM
      };
    },
    computed: {
      ...mapGetters(['user']),
      isSelectSystem () {
        return this.originalList.length === 0;
      },
      isSelectSystemShow () {
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
      }
    },
    watch: {
      reason () {
        this.isShowReasonError = false;
      },
      originalList: {
        handler (value) {
          this.setPolicyList(value);
          const params = [...new Set(this.policyList.map((item) => item.system_id))];
          // 无新增的的系统时无需请求聚合数据
          const difference = params.filter((item) => !this.curSystemId.includes(item));
          if (difference.length > 0) {
            this.curSystemId = [...this.curSystemId.concat(difference)];
            this.resetData();
            if (this.policyList.length > 0) {
              this.fetchAggregationAction(this.curSystemId.join(','));
            }
          } else {
            const data = this.getFilterAggregation(this.aggregationsBackup);
            this.aggregations = _.cloneDeep(data);
          }
          // 处理批量无限制，默认为新增的操作选中无实例
          this.handleUnlimitedActionChange(this.isAllUnlimited);
        },
        deep: true
      }
    },
    mounted () {
      this.formData.members = [{ username: this.user.username, readonly: false }];
    },
    methods: {
      async fetchPageData () {
        if (Number(this.id) > 0) {
          await this.fetchDetail();
        }
      },

      async fetchDetail () {
        try {
          const res = await this.$store.dispatch('role/getRatingManagerDetail', {
            id: this.id
          });
          this.formData.members = res.data.members;
          this.users = res.data.subject_scopes
            .filter((item) => item.type === 'user')
            .map((item) => {
              return {
                name: item.name,
                username: item.id,
                type: item.type
              };
            });
          this.departments = res.data.subject_scopes
            .filter((item) => item.type === 'department')
            .map((item) => {
              return {
                name: item.name,
                count: item.member_count,
                type: item.type,
                id: item.id
              };
            });
          this.isShowMemberAdd = false;
          const list = [];
          res.data.authorization_scopes.forEach((item) => {
            item.actions.forEach((act) => {
              const tempResource = _.cloneDeep(act.resource_groups);
              tempResource.forEach((groupItem) => {
                groupItem.related_resource_types.forEach((subItem) => {
                  subItem.condition = null;
                });
              });
              list.push({
                description: act.description,
                expired_at: act.expired_at,
                id: act.id,
                name: act.name,
                system_id: item.system.id,
                system_name: item.system.name,
                $id: `${item.system.id}&${act.id}`,
                tag: act.tag,
                type: act.type,
                resource_groups: tempResource
              });
            });
          });
          this.originalList = _.cloneDeep(list);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      setPolicyList (payload) {
        if (this.policyList.length < 1) {
          this.policyList = payload.map((item) => new GradePolicy(item));
          return;
        }
        const isAddIds = payload.map((item) => `${item.system_id}&${item.id}`);
        const isExistIds = [];
        this.policyList.forEach((item) => {
          if (item.isAggregate) {
            item.actions.forEach((subItem) => {
              isExistIds.push(`${item.system_id}&${subItem.id}`);
            });
          } else {
            isExistIds.push(`${item.system_id}&${item.id}`);
          }
        });
        // 下一次选择的与现存的交集
        const intersectionIds = isExistIds.filter((item) => isAddIds.includes(item));
        // 下一次选择所删除的操作
        const existRestIds = isExistIds.filter((item) => !intersectionIds.includes(item));
        // 下一次选择所新增的操作
        const newRestIds = isAddIds.filter((item) => !intersectionIds.includes(item));
        if (existRestIds.length > 0) {
          const tempData = [];
          this.policyList.forEach((item) => {
            if (
              !item.isAggregate
              && !existRestIds.includes(`${item.system_id}&${item.id}`)
            ) {
              tempData.push(item);
            }
            if (item.isAggregate) {
              const tempList = existRestIds.filter((act) =>
                item.actions.map((v) => `${item.system_id}&${v.id}`).includes(act)
              );
              if (tempList.length > 0) {
                item.actions = item.actions.filter(
                  (act) => !tempList.includes(`${item.system_id}&${act.id}`)
                );
              }
              tempData.push(item);
            }
          });
          this.policyList = tempData.filter(
            (item) => !item.isAggregate || (item.isAggregate && item.actions.length > 0)
          );
        }

        if (newRestIds.length > 0) {
          newRestIds.forEach((item) => {
            const curSys = payload.find((sys) => `${sys.system_id}&${sys.id}` === item);
            this.policyList.unshift(new GradePolicy(curSys));
          });
        }
      },

      handleAttrValueSelected (payload) {
        window.changeDialog = true;
        const instances = (function () {
          const arr = [];
          payload.aggregateResourceType.forEach((resourceItem) => {
            const { id, name, system_id } = resourceItem;
            payload.instancesDisplayData[id]
              && payload.instancesDisplayData[id].forEach((v) => {
                const curItem = arr.find((_) => _.type === id);
                if (curItem) {
                  curItem.path.push([
                    {
                      id: v.id,
                      name: v.name,
                      system_id,
                      type: id,
                      type_name: name
                    }
                  ]);
                } else {
                  arr.push({
                    name,
                    type: id,
                    path: [
                      [
                        {
                          id: v.id,
                          name: v.name,
                          system_id,
                          type: id,
                          type_name: name
                        }
                      ]
                    ]
                  });
                }
              });
          });
          return arr;
        })();
        const curAction = payload.actions.map((item) => `${payload.system_id}&${item.id}`);
        if (instances.length > 0) {
          this.aggregationsTableData.forEach((item) => {
            if (curAction.includes(`${item.system_id}&${item.id}`)) {
              item.resource_groups.forEach((groupItem) => {
                groupItem.related_resource_types
                  && groupItem.related_resource_types.forEach((subItem) => {
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
          const res = await this.$store.dispatch('aggregate/getAggregateAction', {
            system_ids: payload
          });
          (res.data.aggregations || []).forEach((item) => {
            item.$id = guid();
          });
          const data = this.getFilterAggregation(res.data.aggregations);
          this.aggregationsBackup = _.cloneDeep(res.data.aggregations);
          this.aggregations = _.cloneDeep(data);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      getFilterAggregation (payload) {
        const curSelectActions = [];
        this.policyList.forEach((item) => {
          if (item.isAggregate) {
            curSelectActions.push(...item.actions.map((v) => `${item.system_id}&${v.id}`));
          } else {
            curSelectActions.push(`${item.system_id}&${item.id}`);
          }
        });
        let aggregations = [];
        (payload || []).forEach((item) => {
          const { actions, aggregate_resource_types, $id } = item;
          const curActions = actions.filter((_) =>
            curSelectActions.includes(`${_.system_id}&${_.id}`)
          );
          if (curActions.length > 0) {
            aggregations.push({
              actions: curActions,
              aggregate_resource_types,
              $id,
              system_name: this.policyList.find(
                (_) => _.system_id === curActions[0].system_id
              ).system_name
            });
          }
        });
        aggregations = aggregations.filter((item) => item.actions.length > 1);
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
        aggregationAction.forEach((item) => {
          actionIds.push(...item.actions.map((_) => `${_.system_id}&${_.id}`));
        });
        if (payload) {
          // debugger
          // 缓存新增加的操作权限数据
          aggregationAction.forEach((item) => {
            const filterArray = this.policyList.filter((subItem) =>
              item.actions
                .map((_) => `${_.system_id}&${_.id}`)
                .includes(`${subItem.system_id}&${subItem.id}`)
            );
            const addArray = filterArray.filter(
              (subItem) =>
                !this.aggregationsTableData
                  .map((_) => `${_.system_id}&${_.id}`)
                  .includes(`${subItem.system_id}&${subItem.id}`)
            );
            if (addArray.length > 0) {
              this.aggregationsTableData.push(...addArray);
            }
          });
          const aggregations = aggregationAction
            .filter((item) => {
              // debugger
              const target = item.actions.map((v) => v.id).sort();
              const existData = this.policyList.find((subItem) => {
                return (
                  subItem.isAggregate
                  && _.isEqual(target, subItem.actions.map((v) => v.id).sort())
                );
              });
              return !existData;
            })
            .map((item, index) => {
              // debugger
              // 从缓存值中取值
              const isExistActions = this.aggregationsTableData.filter((subItem) =>
                item.actions
                  .map((v) => `${v.system_id}&${v.id}`)
                  .includes(`${subItem.system_id}&${subItem.id}`)
              );
              const conditions = isExistActions.map(
                (subItem) => subItem.resource_groups[0].related_resource_types[0].condition
              );
              // 是否都选择了实例
              const isAllHasInstance = conditions.every(
                (subItem) => subItem[0] !== 'none' && subItem.length > 0
              );
              if (isAllHasInstance) {
                const instances = conditions.map((subItem) =>
                  subItem.map((v) => v.instance)
                );
                let isAllEqual = true;
                for (let i = 0; i < instances.length - 1; i++) {
                  if (!_.isEqual(instances[i], instances[i + 1])) {
                    isAllEqual = false;
                    break;
                  }
                }
                if (isAllEqual) {
                  // const instanceData = instances[0][0][0];
                  // item.instances = instanceData.path.map(pathItem => {
                  //     return {
                  //         id: pathItem[0].id,
                  //         name: pathItem[0].name
                  //     };
                  // });

                  const instanceData = instances[0][0];
                  item.instances = [];
                  instanceData.map((pathItem) => {
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
              return new GradeAggregationPolicy(item);
            });
          this.policyList = this.policyList.filter(
            (item) => !actionIds.includes(`${item.system_id}&${item.id}`)
          );
          this.policyList.unshift(...aggregations);
          return;
        }
        const aggregationData = [];
        const newPolicyList = [];
        this.policyList.forEach((item) => {
          if (!item.isAggregate) {
            newPolicyList.push(item);
          } else {
            aggregationData.push(_.cloneDeep(item));
          }
        });
        this.policyList = _.cloneDeep(newPolicyList);
        const reallyActionIds = actionIds.filter(
          (item) => !this.policyList.map((v) => `${v.system_id}&${v.id}`).includes(item)
        );
        reallyActionIds.forEach((item) => {
          // 优先从缓存值中取值
          const curObj = this.aggregationsTableData.find(
            (_) => `${_.system_id}&${_.id}` === item
          );
          if (curObj) {
            this.policyList.unshift(curObj);
          } else {
            const curAction = this.originalList.find(
              (_) => `${_.system_id}&${_.id}` === item
            );
            const curAggregation = aggregationData.find((_) =>
              _.actions.map((v) => `${_.system_id}&${v.id}`).includes(item)
            );
            this.policyList.unshift(new GradePolicy({ ...curAction, tag: 'add' }, 'add'));
            if (curAggregation && curAggregation.instances.length > 0) {
              const curData = this.policyList[0];
              const instances = (function () {
                const arr = [];
                const aggregateResourceType = curAggregation.aggregateResourceType;
                aggregateResourceType.forEach((aggregateResourceItem) => {
                  const { id, name, system_id } = aggregateResourceItem;
                  curAggregation.instances.forEach((v) => {
                    const curItem = arr.find((_) => _.type === id);
                    if (curItem) {
                      curItem.path.push([
                        {
                          id: v.id,
                          name: v.name,
                          system_id,
                          type: id,
                          type_name: name
                        }
                      ]);
                    } else {
                      arr.push({
                        name,
                        type: id,
                        path: [
                          [
                            {
                              id: v.id,
                              name: v.name,
                              system_id,
                              type: id,
                              type_name: name
                            }
                          ]
                        ]
                      });
                    }
                  });
                });
                return arr;
              })();
              if (instances.length > 0) {
                curData.related_resource_types.forEach((subItem) => {
                  subItem.condition = [new Condition({ instances }, '', 'add')];
                });
              }
            }
          }
        });
      },

      // 批量无限制
      handleUnlimitedActionChange (payload) {
        const tableData = _.cloneDeep(this.policyList);
        tableData.forEach((item, index) => {
          if (!item.isAggregate) {
            if (item.resource_groups && item.resource_groups.length) {
              item.resource_groups.forEach(groupItem => {
                groupItem.related_resource_types && groupItem.related_resource_types.forEach(types => {
                  if (!payload && (types.condition.length > 0 && types.condition[0] !== 'none')) {
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
        return (
          this.$refs.resourceInstanceRef && this.$refs.resourceInstanceRef.handleGetValue()
        );
      },

      handleBasicInfoChange (field, data) {
        window.changeDialog = true;
        this.formData[field] = data;
      },

      handleAddAction () {
        this.curActionValue = this.originalList.map((item) => item.$id);
        this.isShowAddActionSideSlider = true;
      },

      setAggregateExpanded () {
        const flag = this.policyList.every((item) => !item.isAggregate);
        if (flag) {
          this.isAllExpanded = false;
        }
      },

      handleDelete (systemId, actionId, payload, index) {
        window.changeDialog = true;
        this.originalList = this.originalList.filter((item) => payload !== item.$id);
        this.policyList.splice(index, 1);
        for (let i = 0; i < this.aggregations.length; i++) {
          const item = this.aggregations[i];
          if (item.actions[0].system_id === systemId) {
            item.actions = item.actions.filter((subItem) => subItem.id !== actionId);
            break;
          }
        }
        this.aggregations = this.aggregations.filter((item) => item.actions.length > 1);
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
        const deleteAction = actions.map((item) => `${systemId}&${item.id}`);
        this.originalList = this.originalList.filter(
          (item) => !deleteAction.includes(item.$id)
        );
        this.aggregations = this.aggregations.filter(
          (item) =>
            !(
              item.actions[0].system_id === systemId
              && _.isEqual(
                item.actions.map((_) => _.id).sort(),
                actions.map((_) => _.id).sort()
              )
            )
        );
        this.setAggregateExpanded();
      },

      handleSelectSubmit (payload) {
        payload.forEach((item) => {
          if (!item.resource_groups || !item.resource_groups.length) {
            item.resource_groups = item.related_resource_types.length
              ? [{ id: '', related_resource_types: item.related_resource_types }]
              : [];
          }
        });
        window.changeDialog = true;
        this.originalList = _.cloneDeep(payload);
        if (this.isAllExpanded) {
          this.handleAggregateAction(false);
          this.isAllExpanded = false;
        }
        this.isShowActionEmptyError = false;
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

      async handleSubmitWithReason () {
        this.dialogLoading = true;
        window.changeDialog = false;
        const data = this.$refs.resourceInstanceRef.handleGetValue().actions;
        const subjects = [];
        if (this.isAll) {
          subjects.push({
            id: '*',
            type: '*'
          });
        } else {
          this.users.forEach((item) => {
            subjects.push({
              type: 'user',
              id: item.username,
              full_name: item.full_name
            });
          });
          this.departments.forEach((item) => {
            subjects.push({
              type: 'department',
              id: item.id,
              full_name: item.full_name || item.fullName
            });
          });
        }
        const { name, description, members, sync_perm } = this.formData;
        const params = {
          name,
          description,
          members,
          subject_scopes: subjects,
          authorization_scopes: data,
          reason: this.reason,
          sync_perm: sync_perm
        };
        try {
          await this.$store.dispatch('role/addRatingManagerWithGeneral', params);
          await this.$store.dispatch('roleList');
          this.isShowReasonDialog = false;
          this.messageSuccess(this.$t(`m.info['申请已提交']`), 3000);
          this.$router.push({
            name: 'apply'
          });
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.submitLoading = false;
          this.dialogLoading = false;
        }
      },

      handleDialogCancel () {
        this.isShowReasonDialog = false;
        this.dialogLoading = false;
      },

      async handleSubmit () {
        const validatorFlag = this.$refs.basicInfoRef.handleValidator();
        const tableResource = this.$refs.resourceInstanceRef.handleGetValue();
        let data = [];
        let flag = false;
        this.isShowActionEmptyError = this.originalList.length < 1;
        this.isShowReasonError = !this.reason;
        this.isShowMemberEmptyError
          = this.users.length < 1 && this.departments.length < 1 && !this.isAll;
        if (!this.isShowActionEmptyError) {
          data = tableResource.actions;
          flag = tableResource.flag;
        }
        if (
          validatorFlag
          || flag
          || this.isShowActionEmptyError
          || this.isShowMemberEmptyError
        ) {
          if (validatorFlag) {
            this.scrollToLocation(this.$refs.basicInfoContentRef);
          } else if (flag) {
            this.scrollToLocation(this.$refs.instanceTableContentRef);
          } else if (this.isShowMemberEmptyError) {
            this.scrollToLocation(this.$refs.memberRef);
          }
          return;
        }
        if (this.isStaff) {
          if (!this.reason) {
            this.isShowReasonError = true;
            this.scrollToLocation(this.$refs.reasonRef);
            return;
          }
          this.submitLoading = true;
          this.handleSubmitWithReason();
          // this.isShowReasonDialog = true;
          return;
        }
        const subjects = [];
        if (this.isAll) {
          subjects.push({
            id: '*',
            type: '*'
          });
        } else {
          this.users.forEach((item) => {
            subjects.push({
              type: 'user',
              id: item.username
            });
          });
          this.departments.forEach((item) => {
            subjects.push({
              type: 'department',
              id: item.id
            });
          });
        }
        const { name, description, members, sync_perm } = this.formData;
        const params = {
          name,
          description,
          members,
          subject_scopes: subjects,
          authorization_scopes: data,
          sync_perm: sync_perm
        };
        window.changeDialog = false;
        this.submitLoading = true;
        try {
          await this.$store.dispatch('role/addRatingManager', params);
          await this.$store.dispatch('roleList');
          this.messageSuccess(this.$t(`m.info['新建管理空间成功']`), 3000);
          this.$router.go(-1);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.submitLoading = false;
        }
      },

      handleCancel () {
        this.operate = 'cancel';
        this.$router.go(-1);
      },

      handleReasonInput () {
        this.isShowReasonError = false;
        window.changeDialog = true;
      },

      handleReasonBlur (payload) {
        if (!payload) {
          this.isShowReasonError = true;
        }
      }
    }
    // beforeRouteLeave (to, from, next) {
    //     let cancelHandler = Promise.resolve();
    //     if (window.changeDialog && this.operate !== 'cancel') {
    //         cancelHandler = leavePageConfirm();
    //         next(false);
    //         cancelHandler.then(
    //             () => {
    //                 next();
    //             },
    //             (_) => _
    //         );
    //     } else {
    //         next();
    //     }
    // }
  };
</script>
<style lang="postcss">
.iam-grading-admin-create-wrapper {
  .grading-admin-render-perm-cls {
    margin-bottom: 16px;
  }
  /* .action-empty-error {
    position: relative;
    top: -40px;
    left: 160px;
    font-size: 12px;
    color: #ff4d4d;
  } */

  /* .grade-admin-select-wrapper {
    .action {
      position: relative;
      display: flex;
      justify-content: flex-start;
      .action-wrapper {
        margin-left: 8px;
        font-size: 14px;
        color: #3a84ff;
        cursor: pointer;
        &:hover {
          color: #699df4;
        }
        i {
          position: relative;
          top: -1px;
          left: 2px;
        }
      }
      .info-icon {
        margin: 2px 0 0 2px;
        color: #c4c6cc;
        &:hover {
          color: #3a84ff;
        }
      }
    }
    .sub-title {
      margin-top: 10px;
      margin-left: 10px;
      font-size: 14px;
      color: #979ba5;
      .number {
        font-weight: 600;
      }
    }
    .info-wrapper {
      display: flex;
      justify-content: space-between;
      margin-top: 16px;
      margin-left: 8px;
      line-height: 24px;
      .tips,
      .text {
        line-height: 20px;
        font-size: 12px;
      }
    }
    .resource-instance-wrapper {
      margin-left: 8px;
      min-height: 200px;
    }
  } */
}
.iam-create-rate-manager-reason-dialog {
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

<style lang="postcss" scoped>
/deep/ .grade-admin-select-wrapper {
    .resource_boundary_title {
        font-size: 12px;
    }
    .perm-resource-add {
        width: 88px;
        height: 32px;
        background: #F0F5FF;
        color: v#3A84FF;
        border-radius: 2px;
        border: none;
        vertical-align: middle;
        .icon-plus-circle-shape {
            color: #3A84FF !important;
            font-size: 14px;
        }
        span {
             vertical-align: middle;
        }
    }

    .aggregate-action-btn {
        background-color: #F0F1F5;
    }
    
}
</style>
