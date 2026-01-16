<template>
  <smart-action class="iam-create-secondary-manage-wrapper">
    <render-horizontal-block :label="$t(`m.common['基本信息']`)">
      <section ref="basicInfoContentRef">
        <BasicInfo
          :data="formData"
          ref="basicInfoRef"
          @on-change="handleBasicInfoChange"
        />
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
                @click.stop="handleAddCustom"
              >
                {{ $t(`m.common['添加']`) }}
              </bk-button>
            </section>
            <div
              v-if="isHasPermTemplate"
              class="aggregate-action-group"
            >
              <div
                v-for="item in AGGREGATION_EDIT_ENUM"
                :key="item.value"
                :class="[
                  'aggregate-action-btn',
                  { 'is-active': isAllExpanded === item.value },
                  { 'is-disabled': isAggregateDisabled }
                ]"
                @click.stop="handleAggregateAction(item.value)"
              >
                <span>{{ $t(`m.grading['${item.name}']`) }}</span>
              </div>
            </div>
          </div>
          <div v-if="isHasPermTemplate">
            <div
              class="resource-instance-wrapper"
              ref="instanceTableRef"
              v-bkloading="{
                isLoading,
                opacity: 1,
                zIndex: 1000,
                extCls: 'loading-resource-instance-cls'
              }"
            >
              <RenderInstanceTable
                is-edit
                mode="create"
                ref="resourceInstanceRef"
                :list="policyList"
                :authorization="curAllSystemAuthData"
                :original-list="originalList"
                :total-count="originalList.length"
                :is-all-expanded="isAllExpanded"
                :group-id="$route.params.id"
                @on-delete="handleDelete"
                @on-aggregate-delete="handleAggregateDelete"
                @handleAggregateAction="handleAggregateAction"
                @on-select="handleAttrValueSelected"
                @on-resource-select="handleResSelect"
                @on-clear-all="handleDeleteResourceAll"
              />
            </div>
          </div>
        </div>
        <p class="action-empty-error" v-if="isShowActionEmptyError">
          {{ $t(`m.verify['操作和资源边界不可为空']`) }}
        </p>
        <div ref="memberRef" class="authorize-members-boundary">
          <RenderMember
            :tip="addMemberTips"
            :users="users"
            :departments="departments"
            :expired-at-error="isShowExpiredError"
            :inherit-subject-scope="inheritSubjectScope"
            :label-width="renderLabelWidth('member')"
            @on-add="handleAddMember"
            @on-delete="handleMemberDelete"
            @on-change="handleChange"
          />
        </div>
        <p
          v-if="isShowMemberEmptyError && !inheritSubjectScope"
          class="action-empty-error"
        >
          {{ $t(`m.verify['可授权人员边界不可为空']`) }}
        </p>
      </div>
    </render-horizontal-block>
    <div slot="action">
      <bk-button
        theme="primary"
        type="button"
        :loading="loading"
        @click="handleSubmit"
      >
        {{ $t(`m.common['提交']`) }}
      </bk-button>
      <bk-button style="margin-left: 10px" @click="handleCancel">
        {{ $t(`m.common['取消']`) }}
      </bk-button>
    </div>

    <AddMemberDialog
      :show.sync="isShowAddMemberDialog"
      :users="users"
      :departments="departments"
      :is-rating-manager="isRatingManager"
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd"
    />

    <AddActionSideSlider
      :is-show.sync="isShowAddActionSlider"
      :default-value="curActionValue"
      :default-data="defaultValue"
      :aggregation="aggregationDataByCustom"
      :authorization="authorizationDataByCustom"
      @on-submit="handleSelectSubmit"
    />
  </smart-action>
</template>

<script>
  import { cloneDeep, uniqWith, isEqual } from 'lodash';
  import { mapGetters } from 'vuex';
  import { guid, renderLabelWidth } from '@/common/util';
  import { AGGREGATION_EDIT_ENUM, CUSTOM_PERM_TEMPLATE_ID } from '@/common/constants';
  import Condition from '@/model/condition';
  import GroupPolicy from '@/model/group-policy';
  import GroupAggregationPolicy from '@/model/group-aggregation-policy';
  import AddMemberDialog from '@/views/group/components/iam-add-member';
  import BasicInfo from '@/views/manage-spaces/components/basic-info';
  import RenderMember from '@/views/manage-spaces/components/render-member';
  import AddActionSideSlider from '../components/add-action-sideslider';
  import RenderInstanceTable from '../components/render-instance-table';

  export default {
    components: {
      AddMemberDialog,
      BasicInfo,
      RenderMember,
      AddActionSideSlider,
      RenderInstanceTable
    },
    props: {
      id: {
        type: [String, Number],
        default: 0
      },
      title: {
        type: String,
        default: ''
      },
      loading: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isLoading: false,
        isAll: false,
        isAllExpanded: false,
        isShowMemberEmptyError: false,
        isShowAddMemberDialog: false,
        isShowMemberAdd: false,
        isShowActionEmptyError: false,
        isShowExpiredError: false,
        isShowAddSideSlider: false,
        isShowAddActionSlider: false,
        inheritSubjectScope: true,
        users: [],
        departments: [],
        curActionValue: [],
        originalList: [],
        curSystemId: [],
        policyList: [],
        aggregationsBackup: [],
        aggregations: [],
        aggregationData: {},
        aggregationDataByCustom: {},
        authorizationDataByCustom: {},
        authorizationData: {},
        allAggregationData: {},
        curAllSystemAuthData: {},
        formData: {
          name: '',
          description: '',
          members: [],
          sync_perm: true
        },
        reason: '',
        curMap: null,
        tips: this.$t(`m.grading['添加操作提示']`),
        infoText: this.$t(`m.grading['选择提示']`),
        addMemberTips: this.$t(`m.levelSpace['管理空间可以编辑、管理二级管理空间的权限']`),
        addMemberTitle: this.$t(`m.levelSpace['最大可授权人员边界']`),
        renderLabelWidth,
        AGGREGATION_EDIT_ENUM
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemsLayout']),
      isAggregateDisabled () {
        const aggregationIds = this.policyList.reduce((counter, item) => {
          return item.aggregationId ? counter.concat(item.aggregationId) : counter;
        }, []);
        const temps = [];
        aggregationIds.forEach((item) => {
          if (!temps.some((sub) => sub.includes(item))) {
            temps.push([item]);
          } else {
            const tempObj = temps.find((sub) => sub.includes(item));
            tempObj.push(item);
          }
        });
        return !temps.some((item) => item.length > 1) && !this.isAllExpanded;
      },
      members () {
        const arr = [];
        if (this.departments.length > 0) {
          arr.push(
            ...this.departments.map((item) => {
              return {
                id: item.id,
                type: 'department'
              };
            })
          );
        }
        if (this.users.length > 0) {
          arr.push(
            ...this.users.map((item) => {
              return {
                id: item.username,
                type: 'user'
              };
            })
          );
        }
        return arr;
      },
      defaultValue () {
        if (this.originalList.length < 1) {
          return [];
        }
        const tempList = [];
        this.originalList.forEach((item) => {
          if (!tempList.some((sys) => sys.system_id === item.system_id)) {
            tempList.push({
              system_id: item.system_id,
              system_name: item.system_name,
              list: [item]
            });
          } else {
            const curData = tempList.find((sys) => sys.system_id === item.system_id);
            curData.list.push(item);
          }
        });
        return tempList;
      },
      isHasPermTemplate () {
        return this.policyList.length > 0;
      },
      isRatingManager () {
        return ['rating_manager', 'subset_manager'].includes(this.user.role.type);
      },
      isEdit () {
        return ['secondaryManageSpaceEdit'].includes(this.$route.name);
      }
    },
    watch: {
      originalList: {
        handler (value) {
          this.setPolicyList(value);
          const uniqueList = [...new Set(this.policyList.map((item) => item.system_id))];
          // 无新增的的系统时无需请求聚合数据
          const difference = uniqueList.filter((item) => !this.curSystemId.includes(item));
          if (difference.length) {
            this.curSystemId = [...this.curSystemId, ...difference];
            this.resetData();
            if (this.policyList.length > 1 && this.curSystemId.length > 0) {
              const aggregationKeys = Object.keys(this.aggregationData);
              // 如果是克隆或者编辑首次不需要聚合，优先从详情接口获取
              if (this.id) {
                const intersection = Array.from(this.curSystemId).filter(item => !aggregationKeys.includes(item));
                this.fetchAggregationSystem(intersection);
              } else {
                this.fetchAggregationSystem(this.curSystemId);
              }
            }
          } else {
            const data = this.getFilterAggregation(this.aggregationsBackup);
            this.aggregations = cloneDeep(data);
          }
        },
        deep: true
      }
    },
    async created () {
      await this.fetchInitData();
    },
    methods: {
      async fetchInitData () {
        const propsId = Number(this.id);
        this.$store.commit('setHeaderTitle', this.title);
        if (propsId) {
          await this.fetchDetail();
        } else {
          const { username } = this.user;
          this.formData.members = [{ username, readonly: true }];
        }
      },

      async fetchDetail () {
        try {
          const { code, data } = await this.$store.dispatch(
            'spaceManage/getSecondManagerDetail',
            {
              id: this.id
            }
          );
          if (code === 0) {
            this.getDetailData(data);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async fetchAggregationAction (payload) {
        this.isLoading = true;
        try {
          const { data } = await this.$store.dispatch('aggregate/getAggregateAction', {
            system_ids: payload
          });
          const aggregations = data.aggregations || [];
          const result = this.getFilterAggregation(aggregations);
          this.aggregationsBackup = cloneDeep(aggregations);
          this.aggregations = cloneDeep(result);
          const systemList = payload.split(',');
          systemList.forEach((item) => {
            this.aggregationData[item] = [...aggregations].filter((v) => v.system_id === item);
          });
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },
 
      async fetchAuthorizationScopeActions (systemId) {
        try {
          const { data } = await this.$store.dispatch(
            'permTemplate/getAuthorizationScopeActions',
            { systemId }
          );
          this.authorizationData[systemId] = (data || []).filter(item => item.id !== '*');
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      // 实例数据更新后实时获取不同系统下的聚合操作
      async fetchAggregationSystem (payload) {
        if (!payload.length) return;
        await this.fetchAggregationAction(payload.join());
        for (let i = 0; i < payload.length; i++) {
          await this.fetchAuthorizationScopeActions(payload[i]);
        }
        this.curAllSystemAuthData = Object.assign(this.authorizationDataByCustom, this.authorizationData);
        this.handleAggregateData();
      },

      getDetailData (payload) {
        const tempActions = [];
        const {
          name,
          description,
          members,
          sync_perm,
          inherit_subject_scope: inheritSubjectScope,
          subject_scopes,
          authorization_scopes
        } = payload;
        this.inheritSubjectScope = inheritSubjectScope;
        this.formData = Object.assign(
          {},
          {
            name: this.isEdit ? name : `${name}_${this.$t(`m.grading['克隆']`)}`,
            members,
            description,
            sync_perm: sync_perm
          }
        );
        this.isAll = subject_scopes.some((item) => item.type === '*' && item.id === '*');
        this.users = subject_scopes
          .filter((item) => item.type === 'user')
          .map((item) => {
            return {
              name: item.name,
              username: item.id,
              type: item.type
            };
          });
        this.departments = subject_scopes
          .filter((item) => item.type === 'department')
          .map((item) => {
            return {
              name: item.name,
              count: item.member_count,
              type: item.type,
              id: item.id
            };
          });
        authorization_scopes.forEach((item) => {
          item.actions.forEach((act) => {
            const tempResource = cloneDeep(act.resource_groups);
            tempResource.forEach((groupItem) => {
              groupItem.related_resource_types.forEach((resourceTypeItem) => {
                resourceTypeItem.id = resourceTypeItem.type;
                // 如果是克隆页面，资源实例需要置空
                if (!this.isEdit) {
                  resourceTypeItem.condition = null;
                }
              });
            });
            tempActions.push({
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
        this.isShowMemberAdd = false;
        this.originalList = cloneDeep(tempActions);
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
          if (curActions.length) {
            const curSystem = this.policyList.find(v => v.system_id === curActions[0].system_id) || {};
            aggregations.push({
              actions: curActions,
              aggregate_resource_types,
              $id,
              system_name: curSystem.system_name || ''
            });
          }
        });
        aggregations = aggregations.filter(item => item.actions.length > 1);
        return aggregations;
      },

      setPolicyList (payload) {
        if (!this.policyList.length) {
          this.policyList = payload.map(item => {
            const result = new GroupPolicy(
              item,
              'add',
              'custom',
              {
                system: {
                  id: item.system_id,
                  name: item.system_name
                },
                id: CUSTOM_PERM_TEMPLATE_ID
              }
            );
            this.$set(result, '$id', `${item.system_id}&${item.id}`);
            return result;
          });
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
            this.policyList.unshift(new GroupPolicy(curSys));
          });
        }
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

      handleBasicInfoChange (field, value) {
        window.changeDialog = true;
        this.formData[field] = value;
      },

      handleAddCustom () {
        this.curActionValue = this.originalList.map((item) => item.$id);
        this.isShowAddActionSlider = true;
      },

      handleResSelect (index, resIndex, condition, groupIndex, resItem) {
        if (this.curMap && this.curMap.size > 0) {
          const item = this.policyList[index];
          const actions = this.curMap.get(item.aggregationId) || [];
          const len = actions.length;
          if (len > 0) {
            for (let i = 0; i < len; i++) {
              if (actions[i].id === item.id) {
                const resourceGroups = actions[i].resource_groups[groupIndex];
                if (!resourceGroups) {
                  actions[i].resource_groups.push({
                    id: '',
                    related_resource_types: resItem
                  });
                } else {
                  resourceGroups.related_resource_types[resIndex].condition = cloneDeep(condition);
                }
                break;
              }
            }
          }
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
                const curItem = arr.find((k) => k.type === id);
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
          const actions = this.curMap.get(payload.aggregationId);
          actions.forEach(item => {
            item.resource_groups.forEach(groupItem => {
              groupItem.related_resource_types.forEach(subItem => {
                subItem.condition = [new Condition({ instances }, '', 'add')];
              });
            });
          });
        }
      },

      handleAggregateData () {
        this.allAggregationData = Object.assign(
          this.aggregationDataByCustom,
          this.aggregationData
        );
        this.policyList.forEach((item) => {
          const curSystemId = item.detail.system.id;
          const aggregationData = this.allAggregationData[curSystemId] || [];
          if (aggregationData && aggregationData.length) {
            aggregationData.forEach((aggItem) => {
              if (aggItem.actions.map((act) => act.id).includes(item.id)) {
                const existData = this.policyList.filter((sub) =>
                  aggItem.actions.find((act) => act.id === sub.id)
                  && sub.judgeId === item.judgeId
                );
                if (existData.length > 1) {
                  const temp = existData.find((sub) => sub.aggregationId !== '') || {};
                  item.aggregationId = temp.aggregationId || guid();
                  item.aggregateResourceType = aggItem.aggregate_resource_types;
                }
              }
            });
          }
        });
        if (!this.curMap) {
          this.curMap = new Map();
        }
        this.policyList.forEach((item) => {
          if (item.aggregationId) {
            if (!this.curMap.has(item.aggregationId)) {
              this.curMap.set(item.aggregationId, [cloneDeep(item)]);
            } else {
              const temps = this.curMap.get(item.aggregationId);
              if (!temps.map((sub) => sub.id).includes(item.id)) {
                temps.push(cloneDeep(item));
              }
            }
          }
        });
      },

      handleAggregateAction (payload) {
        if (this.isAggregateDisabled) {
          return;
        }
        this.isAllExpanded = payload;
        let tempData = [];
        let templateIds = [];
        let instancesDisplayData = {};
        if (payload) {
          this.policyList.forEach(item => {
            if (!item.aggregationId) {
              tempData.push(item);
              templateIds.push(item.detail.id);
            }
          });
          const cacheMap = cloneDeep(this.curMap);
          for (const [key, cacheValue] of cacheMap.entries()) {
            const isExistKey = this.policyList.some((v) => v.aggregationId === key);
            if (isExistKey) {
              const value = cacheValue.filter(item => this.policyList.map((v) => v.$id).includes(item.$id));
              this.curMap.set(key, value);
              if (value.length === 1) {
                tempData.push(...value);
                tempData = uniqWith(tempData, isEqual);
              } else {
                let curInstances = [];
                // 这里避免从模板选择的权限和自定义权限下的操作是一致的，所以需要去重
                tempData = uniqWith(tempData, isEqual);
                const conditions = value.map((subItem) => subItem.resource_groups
                  && subItem.resource_groups[0].related_resource_types[0].condition);
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
                    const instanceData = instances[0][0];
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
                  } else {
                    curInstances = [];
                  }
                } else {
                  curInstances = [];
                }
                tempData.push(new GroupAggregationPolicy({
                  aggregationId: key,
                  aggregate_resource_types: value[0].aggregateResourceType,
                  actions: value,
                  instances: curInstances,
                  instancesDisplayData
                }));
              }
              templateIds.push(value[0].detail.id);
            } else {
              this.curMap.delete(key);
            }
          }
        } else {
          this.policyList.forEach(item => {
            if (item.isAggregate) {
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
        this.policyList = cloneDeep(tempList);
      },

      handleSelectSubmit (payload, aggregation, authorization) {
        let addCustomList = [];
        let deleteCustomList = [];
        const actionList = payload.map((item) => {
          if (!item.resource_groups || !item.resource_groups.length) {
            item.resource_groups = item.related_resource_types.length
              ? [{ id: '', related_resource_types: item.related_resource_types }]
              : [];
          }
          const result = new GroupPolicy(
            item,
            'add',
            'custom',
            {
              system: {
                id: item.system_id,
                name: item.system_name
              },
              id: CUSTOM_PERM_TEMPLATE_ID
            }
          );
          this.$set(result, '$id', `${item.system_id}&${item.id}`);
          return result;
        });
        // 获取上一次已选数据
        if (this.originalList.length) {
          const originalIds = this.originalList.map(v => v.$id);
          const intersection = actionList.filter(v => originalIds.includes(v.$id));
          addCustomList = actionList.filter(v => !originalIds.includes(v.$id));
          deleteCustomList = this.originalList.filter(v => !intersection.map(sub => sub.$id).includes(v.$id));
          this.policyList = [...this.policyList, ...addCustomList];
        } else {
          this.policyList = [...actionList];
        }
        // 处理既有新增操作又存在删除已有操作场景
        if (deleteCustomList.length) {
          const deleteIds = deleteCustomList.map(v => v.$id);
          this.policyList = this.policyList.filter(item => !deleteIds.includes(`${item.$id}`));
        }
        if (!actionList.length) {
          this.curActionValue = [];
        }
        this.originalList = cloneDeep(actionList);
        this.aggregationDataByCustom = cloneDeep(aggregation);
        this.authorizationDataByCustom = cloneDeep(authorization);
        // 处理当前是聚合形态再新增数据需要重新组装成非聚合形态，兼容新增的数据会存在可以聚合的数据业务场景
        if (this.isAllExpanded) {
          this.handleAggregateAction(false);
        }
        // 处理聚合的数据，将表格数据按照相同的聚合id分配好
        this.handleAggregateData();
        this.isShowActionEmptyError = false;
      },

      async handleSubmit () {
        const validatorFlag = this.$refs.basicInfoRef.handleValidator();
        let data = [];
        let flag = false;
        this.isShowActionEmptyError = !this.originalList.length;
        this.isShowMemberEmptyError = false;
        if (!this.isShowActionEmptyError) {
          const { actions, flag: isFlag } = this.$refs.resourceInstanceRef.handleGetValue();
          data = [...actions];
          flag = isFlag;
        }
        if (!this.inheritSubjectScope) {
          this.isShowMemberEmptyError = !this.users.length && !this.departments.length && !this.isAll;
        }
        if (validatorFlag) {
          this.scrollToLocation(this.$refs.basicInfoContentRef);
          return;
        }
        if (flag || this.isShowActionEmptyError) {
          this.scrollToLocation(this.$refs.instanceTableRef);
          return;
        }
        if (this.isShowMemberEmptyError) {
          this.scrollToLocation(this.$refs.memberRef);
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
          sync_perm: sync_perm,
          inherit_subject_scope: this.inheritSubjectScope
        };
        // 如果是动态继承上级空间 组织架构可为空
        if (this.inheritSubjectScope) {
          this.isShowMemberEmptyError = false;
          params.subject_scopes = [];
        }
        window.changeDialog = false;
        this.$emit('on-submit', params);
      },

      handleAddMember () {
        this.isShowAddMemberDialog = true;
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

      handleCancel () {
        this.$router.go(-1);
      },

      handleCancelAdd () {
        this.isShowAddMemberDialog = false;
      },

      handleSetAggregateExpanded () {
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
        this.handleSetAggregateExpanded();
      },

      handleDeleteResourceAll () {
        this.originalList = [];
        this.policyList = [];
        this.isAllExpanded = false;
        this.curMap && this.curMap.clear();
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
              && isEqual(
                item.actions.map((v) => v.id).sort(),
                actions.map((k) => k.id).sort()
              )
            )
        );
        this.handleSetAggregateExpanded();
      },

      handleSubmitAdd (payload) {
        window.changeDialog = true;
        const { users, departments } = payload;
        this.users = cloneDeep(users);
        this.departments = cloneDeep(departments);
        this.isShowMemberAdd = false;
        this.isShowMemberEmptyError = false;
        this.isShowAddMemberDialog = false;
      },

      handleChange (payload) {
        this.inheritSubjectScope = payload;
        if (payload) {
          this.users = [];
          this.departments = [];
        }
      },

      resetData () {
        this.aggregations = [];
        this.aggregationsBackup = [];
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import "@/css/mixins/authorize-boundary.css";
.iam-create-secondary-manage-wrapper {
  margin-bottom: 36px;
  .action-empty-error {
    position: relative;
    top: 0;
    left: 0;
    font-size: 12px;
    color: #ff4d4d;
  }
}
</style>
