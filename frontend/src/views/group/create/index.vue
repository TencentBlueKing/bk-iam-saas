<template>
  <smart-action class="iam-create-user-group-wrapper">
    <render-horizontal-block :label="$t(`m.common['基本信息']`)">
      <section ref="basicInfoContentRef">
        <basic-info
          :data="formData"
          ref="basicInfoRef"
          @on-change="handleBasicInfoChange" />
        <div class="select-wrap-checkbox">
          <bk-checkbox
            v-model="formData.apply_disable"
            :disabled="userGroupAttributes.apply_disable"
          >
            <span class="checkbox-sync-perm no-border">
              {{ $t(`m.userGroup['不可被申请']`) }}
            </span>
            <span>({{ $t(`m.userGroup['设置后该组只能管理员主动授权，用户无法主动申请']`) }})</span>
          </bk-checkbox>
        </div>
        <div class="select-wrap-checkbox" v-if="isShowTemplate">
          <bk-checkbox
            v-model="formData.sync_subject_template"
          >
            <span class="checkbox-sync-perm no-border">
              {{ $t(`m.userGroup['自动生成同名人员模板']`) }}
            </span>
          </bk-checkbox>
        </div>
      </section>
    </render-horizontal-block>
    <render-action
      :title="$t(`m.userGroup['添加组权限']`)"
      ext-cls="add-perm-action"
      v-if="!isHasPermTemplate"
      data-test-id="group_btn_showAddGroupPerm"
      @on-click="handleAddPerm">
    </render-action>
    <render-horizontal-block :label="$t(`m.grading['操作和资源范围']`)" v-if="isHasPermTemplate">
      <div class="user-group-select-wrapper">
        <div class="flex-between action">
          <div class="action-wrapper" @click.stop="handleAddPerm">
            <Icon bk type="plus-circle-shape" />
            <span>{{ $t(`m.userGroup['添加组权限']`) }}</span>
          </div>
          <div class="info-wrapper">
            <template v-if="['super_manager', 'system_manager'].includes(user.role.type)">
              <bk-switcher
                v-model="isAllUnlimited"
                theme="primary"
                size="small"
                :disabled="isUnlimitedDisabled"
                @change="handleUnlimitedActionChange">
              </bk-switcher>
              <span class="text">{{ $t(`m.common['批量无限制']`) }}</span>
            </template>
            <div class="aggregate-action-tab-group">
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
                <span>{{ $t(`m.grading['${item.name}']`)}}</span>
              </div>
            </div>
          </div>
        </div>
        <div ref="instanceTableContentRef" class="aggregate-tab-instance-table">
          <resource-instance-table
            is-edit
            mode="create"
            ref="resInstanceTableRef"
            :list="tableList"
            :authorization="curAuthorizationData"
            :original-list="tableListBackup"
            :is-all-expanded="isAllExpanded"
            @handleAggregateAction="handleAggregateAction"
            @on-select="handleAttrValueSelected"
            @on-resource-select="handleResSelect" />
        </div>
      </div>
    </render-horizontal-block>
    <render-action
      :title="$t(`m.userGroup['添加组成员']`)"
      v-if="isShowMemberAdd"
      style="margin-bottom: 16px;"
      data-test-id="group_btn_showAddGroupMember"
      @on-click="handleAddMember">
      <!-- <iam-guide
                type="add_group_member"
                direction="left"
                :style="{ top: '-20px', left: '180px' }"
                :content="$t(`m.guide['添加组成员']`)" /> -->
    </render-action>
    <section v-else ref="memberRef">
      <render-member
        :users="users"
        :departments="departments"
        :templates="templates"
        :expired-at-error="isShowExpiredError"
        @on-change="handleExpiredAtChange"
        @on-add="handleAddMember"
        @on-delete="handleMemberDelete" />
    </section>
    <div slot="action">
      <bk-button theme="primary" type="button" :loading="submitLoading"
        data-test-id="group_btn_createSubmit"
        @click="handleSubmit">
        {{ $t(`m.common['提交']`) }}
      </bk-button>
      <bk-button style="margin-left: 10px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
    </div>

    <add-member-dialog
      :show.sync="isShowAddMemberDialog"
      :users="users"
      :departments="departments"
      :templates="templates"
      :is-rating-manager="isRatingManager"
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd" />

    <add-perm-sideslider
      :is-show.sync="isShowAddSideslider"
      :custom-perm="originalList"
      :template="templateDetailList"
      :aggregation="aggregationData"
      :authorization="authorizationData"
      :external-template="externalSystemsLayout.userGroup.addGroup.hideAddTemplateTextBtn"
      :perm-side-width="permSideWidth"
      @on-view="handleViewDetail"
      @on-add-custom="handleAddCustom"
      @on-edit-custom="handleEditCustom"
      @on-cancel="handleAddCancel"
      @on-submit="handleSubmitPerm" />

    <add-action-sideslider
      :is-show.sync="isShowAddActionSideslider"
      :default-value="curActionValue"
      :default-data="defaultValue"
      :aggregation="aggregationDataByCustom"
      :authorization="authorizationDataByCustom"
      @on-cancel="handleSelectCancel"
      @on-submit="handleSelectSubmit" />

    <render-template-sideslider
      :is-show.sync="templateDetailSideslider.isShow"
      :id="templateDetailSideslider.id"
      @on-cancel="handleSelectCancel"
    />
  </smart-action>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { CUSTOM_PERM_TEMPLATE_ID, PERMANENT_TIMESTAMP, SIX_MONTH_TIMESTAMP, AGGREGATION_EDIT_ENUM } from '@/common/constants';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  // import IamGuide from '@/components/iam-guide/index.vue';
  import AddMemberDialog from '../components/iam-add-member';
  import RenderMember from '../components/render-member';
  import basicInfo from '../components/basic-info';
  import renderAction from '../common/render-action';
  import AddPermSideslider from '../components/add-group-perm-sideslider';
  import AddActionSideslider from '../components/add-action-sideslider';
  import ResourceInstanceTable from '../components/render-instance-table';
  import RenderTemplateSideslider from '../components/render-template-detail-sideslider';
  import GroupPolicy from '@/model/group-policy';
  import GroupAggregationPolicy from '@/model/group-aggregation-policy';
  import Condition from '@/model/condition';
  import { guid } from '@/common/util';

  export default {
    name: '',
    provide: function () {
      return {
        getGroupAttributes: () => this.groupAttributes
      };
    },
    components: {
      AddMemberDialog,
      basicInfo,
      renderAction,
      RenderMember,
      // IamGuide,
      AddPermSideslider,
      AddActionSideslider,
      ResourceInstanceTable,
      RenderTemplateSideslider
    },
    data () {
      return {
        AGGREGATION_EDIT_ENUM,
        formData: {
          name: '',
          approval_process_id: 1,
          description: '',
          apply_disable: false,
          sync_subject_template: false
        },
        isShowAddMemberDialog: false,
        isShowMemberAdd: true,
        expired_at: SIX_MONTH_TIMESTAMP,
        users: [],
        departments: [],
        templates: [],
        submitLoading: false,
        isShowExpiredError: false,
        isShowAddSideslider: false,
        isShowAddActionSideslider: false,
        curActionValue: [],
        originalList: [],

        tableList: [],
        tableListBackup: [],
        templateDetailList: [],
        aggregationData: {},
        authorizationData: {},
        aggregationDataByCustom: {},
        authorizationDataByCustom: {},
        allAggregationData: {},
        isAllExpanded: false,
        isAllUnlimited: false,
        hasDeleteCustomList: [],
        hasAddCustomList: [],
        templateDetailSideslider: {
          isShow: false,
          id: ''
        },
        curMap: null,
        permSideWidth: 960,
        groupAttributes: {
          source_type: '',
          source_from_role: false
        },
        userGroupAttributes: {
          apply_disable: false,
          sync_subject_template: false
        }
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId', 'externalSystemsLayout']),
      /**
       * isAggregateDisabled
       */
      isAggregateDisabled () {
          const aggregationIds = this.tableList.reduce((counter, item) => {
              return item.aggregationId !== '' ? counter.concat(item.aggregationId) : counter;
          }, []);
          const temps = [];
          aggregationIds.forEach(item => {
              if (!temps.some(sub => sub.includes(item))) {
                  temps.push([item]);
              } else {
                  const tempObj = temps.find(sub => sub.includes(item));
                  tempObj.push(item);
              }
          });
          return !temps.some(item => item.length > 1) && !this.isAllExpanded;
      },
      isUnlimitedDisabled () {
        const isDisabled = this.tableList.every(item =>
          ((!item.resource_groups || (item.resource_groups && !item.resource_groups.length)) && !item.instances)
          );
        if (isDisabled) {
          this.isAllUnlimited = false;
        }
        return isDisabled;
      },
      /**
       * expandedText
       */
      expandedText () {
          return this.isAllExpanded ? this.$t(`m.grading['批量编辑']`) : this.$t(`m.grading['逐项编辑']`);
      },
      members () {
          const arr = [];
          if (this.departments.length > 0) {
              arr.push(...this.departments.map(item => {
                  return {
                      id: item.id,
                      type: 'department'
                  };
              }));
          }
          if (this.users.length > 0) {
              arr.push(...this.users.map(item => {
                  return {
                      id: item.username,
                      type: 'user'
                  };
              }));
          }
          if (this.templates.length > 0) {
            arr.push(...this.templates.map(item => {
                  return {
                      id: item.id,
                      type: 'template'
                  };
              }));
          }
          return arr;
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
      isHasPermTemplate () {
          return this.tableList.length > 0;
      },
      isRatingManager () {
          return ['rating_manager', 'subset_manager'].includes(this.user.role.type);
      },
      isSuperManager () {
          return this.user.role.type === 'super_manager';
      },
      curAuthorizationData () {
          const data = Object.assign(this.authorizationData, this.authorizationDataByCustom);
          return data;
      },
      isShowTemplate () {
        return !['staff', 'subset_manager'].includes(this.user.role.type);
      }
    },
    watch: {
      isShowAddSideslider (value) {
        if (!value) {
          this.permSideWidth = 960;
        }
      }
    },
    async created () {
      // await this.fetchUserGroupSet();
      this.formData = Object.assign(this.formData, { sync_subject_template: !!this.externalSystemId });
      await this.fetchUserGroupSet();
    },
    methods: {
      // 获取分级管理员用户组配置
      async fetchUserGroupSet () {
        if (!['subset_manager', 'staff', ''].includes(this.user.role.type)) {
          try {
            const { data } = await this.$store.dispatch('userGroupSetting/getUserGroupSetConfig');
            if (data) {
              this.formData = Object.assign(this.formData, { apply_disable: data.apply_disable });
              this.userGroupAttributes = Object.assign({}, { apply_disable: data.apply_disable });
            }
          } catch (e) {
            console.error(e);
            this.messageAdvancedError(e);
          }
        }
      },
      
      /**
       * handleBasicInfoChange
       */
      handleBasicInfoChange (field, value) {
        window.changeDialog = true;
        this.formData[field] = value;
      },

      /**
       * handleAddCancel
       */
      handleAddCancel (payload) {
        const { customPerm, templateList } = payload;
        if (customPerm) {
          this.hasAddCustomList = [...customPerm];
          if (!customPerm.length && !templateList.length) {
            this.tableList = [];
            this.tableListBackup = [];
          }
        }
        this.isShowAddSideslider = false;
        this.permSideWidth = 960;
      },

      /**
       * handleAddCustom
       */
      handleAddCustom () {
        if (!this.externalSystemsLayout.userGroup.addGroup.hideAddTemplateTextBtn) {
          this.permSideWidth = 1160;
        }
        this.isShowAddActionSideslider = true;
      },

      /**
       * handleViewDetail
       */
      handleViewDetail ({ id }) {
        this.templateDetailSideslider.id = id;
        this.templateDetailSideslider.isShow = true;
        this.permSideWidth = 1160;
      },

      /**
       * handleSubmitPerm
       */
      handleSubmitPerm (templates, aggregation, authorization) {
        this.aggregationData = aggregation;
        this.authorizationData = authorization;
        let hasDeleteTemplateList = [];
        let hasAddTemplateList = [];
        if (this.templateDetailList.length > 0) {
          const intersection = templates.filter(
            item => this.templateDetailList.map(sub => sub.id).includes(item.id)
          );
          // 判断权限模板数量没做任何变动时
          if (JSON.stringify(this.templateDetailList) === JSON.stringify(templates)) {
            hasAddTemplateList = _.cloneDeep(templates);
          } else {
            hasDeleteTemplateList = this.templateDetailList.filter(
              item => !intersection.map(sub => sub.id).includes(item.id)
            );
            hasAddTemplateList = [
              ...intersection,
              ...templates.filter(item => !intersection.map(sub => sub.id).includes(item.id))
            ];
          }
        } else {
          hasAddTemplateList = templates;
        }
        this.templateDetailList = _.cloneDeep(templates);
        if (hasDeleteTemplateList.length > 0) {
          this.tableList = this.tableList.filter(
            item => !hasDeleteTemplateList.map(sub => sub.id).includes(item.detail.id)
          );
        }
        if (this.hasDeleteCustomList.length > 0) {
          this.tableList = this.tableList.filter(item => {
            return item.detail.id === CUSTOM_PERM_TEMPLATE_ID
              && !this.hasDeleteCustomList
                .map(sub => sub.$id).includes(`${item.detail.system.id}&${item.id}`);
          });
        }
        const temps = [];
        const tempList = [];
        hasAddTemplateList.forEach(item => {
          const temp = _.cloneDeep(item);
          delete temp.actions;
          item.actions.forEach(sub => {
            if (!sub.resource_groups || !sub.resource_groups.length) {
              sub.resource_groups = sub.related_resource_types.length ? [{ id: '', related_resource_types: sub.related_resource_types }] : [];
            }
            tempList.push(new GroupPolicy(sub, 'add', 'template', temp));
          });
        });
        this.tableList.forEach(item => {
          if (item.detail.id === CUSTOM_PERM_TEMPLATE_ID) {
            if (item.isAggregate) {
              temps.push(item.actions.map(_ => `${_.detail.system.id}&${_.id}`));
            } else {
              temps.push(`${item.detail.system.id}&${item.id}`);
            }
          }
        });
        console.log('this.hasAddCustomList', this.hasAddCustomList);
        const addCustomList = this.originalList.filter(item => !temps.includes(item.$id));
        addCustomList.forEach(item => {
          if (!item.resource_groups || !item.resource_groups.length) {
            item.resource_groups = item.related_resource_types && item.related_resource_types.length ? [{ id: '', related_resource_types: item.related_resource_types }] : [];
          }
          tempList.push(new GroupPolicy(item, 'add', 'custom', {
            system: {
              id: item.system_id,
              name: item.system_name
            },
            id: CUSTOM_PERM_TEMPLATE_ID
          }));
        });
        this.tableList.push(...tempList);
        this.tableListBackup = _.cloneDeep(this.tableList);
        // 处理当前是聚合形态再新增数据需要重新组装成非聚合形态，兼容新增的数据会存在可以聚合的数据业务场景
        if (this.isAllExpanded) {
          this.handleAggregateAction(false);
        }
        this.isAllExpanded = false;
        // 处理聚合的数据，将表格数据按照相同的聚合id分配好
        this.handleAggregateData();
        // 处理为批量无限制， 默认为新增的操作选中无实例
        this.handleUnlimitedActionChange(this.isAllUnlimited);
        this.$nextTick(() => {
          if (hasDeleteTemplateList.length > 0 || this.hasDeleteCustomList.length > 0) {
            this.setCurMapData(hasDeleteTemplateList);
          }
        });
      },

      /**
       * handleResSelect
       */
      handleResSelect (index, resIndex, condition, groupIndex, resItem) {
        // debugger;
        if (this.curMap.size > 0) {
          const item = this.tableList[index];
          const actions = this.curMap.get(item.aggregationId) || [];
          const len = actions.length;
          if (len > 0) {
            for (let i = 0; i < len; i++) {
              if (actions[i].id === item.id) {
                // eslint-disable-next-line max-len
                if (!actions[i].resource_groups[groupIndex]) {
                  actions[i].resource_groups.push({ id: '', related_resource_types: resItem });
                } else {
                  // eslint-disable-next-line max-len
                  actions[i].resource_groups[groupIndex].related_resource_types[resIndex].condition = _.cloneDeep(condition);
                }
                break;
              }
            }
          }
        }
      },

      /**
       * handleAttrValueSelected
       */
      handleAttrValueSelected (payload) {
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
        // debugger
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
                // const existDatas = this.tableList.filter(sub => sub.judgeId === item.judgeId)
                // const existDatas = this.tableList.filter(
                //     sub => aggItem.actions.find(act => act.id === sub.id)
                // )
                const existDatas = this.tableList.filter(
                  sub => aggItem.actions.find(act => act.id === sub.id)
                    && sub.judgeId === item.judgeId
                );
                if (existDatas.length > 1) {
                  const temp = existDatas.find(sub => sub.aggregationId !== '') || {};
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
              this.curMap.set(item.aggregationId, [_.cloneDeep(item)]);
            } else {
              const temps = this.curMap.get(item.aggregationId);
              if (!temps.map(sub => sub.id).includes(item.id)) {
                temps.push(_.cloneDeep(item));
              }
            }
          }
        });
      },

      /**
       * setCurMapData
       */
      setCurMapData (payload = []) {
        const flag = String(Number(payload.length > 0)) + String(Number(this.hasDeleteCustomList.length > 0));
        const hasDeleteIds = payload.map(item => item.id);
        const hasDeleteIdsTemp = this.hasDeleteCustomList.map(_ => _.$id);
        const tempData = {};
        for (const [key, value] of this.curMap.entries()) {
          tempData[key] = value;
        }
        const tempDataBackup = {};
        switch (flag) {
          case '11':
            for (const key in tempData) {
              const value = tempData[key];
              if (value[0].detail.id !== CUSTOM_PERM_TEMPLATE_ID) {
                const tempValue = _.cloneDeep(value);
                if (!value.every(item => hasDeleteIds.includes(item.detail.id))) {
                  tempDataBackup[key] = tempValue;
                }
              }
            }
            for (const key in tempData) {
              const value = tempData[key];
              if (value[0].detail.id === CUSTOM_PERM_TEMPLATE_ID) {
                let tempValue = _.cloneDeep(value);
                tempValue = tempValue.filter(item => !hasDeleteIdsTemp.includes(`${item.detail.system.id}&${item.id}`));
                if (tempValue.length > 0) {
                  tempDataBackup[key] = tempValue;
                }
              }
            }
            break;
          case '10':
            for (const key in tempData) {
              const value = tempData[key];
              if (value[0].detail.id !== CUSTOM_PERM_TEMPLATE_ID) {
                if (!value.every(item => hasDeleteIds.includes(item.detail.id))) {
                  tempDataBackup[key] = value;
                }
              } else {
                tempDataBackup[key] = value;
              }
            }
            break;
          case '01':
            for (const key in tempData) {
              const value = tempData[key];
              if (value[0].detail.id === CUSTOM_PERM_TEMPLATE_ID) {
                let tempValue = _.cloneDeep(value);
                tempValue = tempValue.filter(item => !hasDeleteIdsTemp.includes(`${item.detail.system.id}&${item.id}`));
                if (tempValue.length > 0) {
                  tempDataBackup[key] = tempValue;
                }
              } else {
                tempDataBackup[key] = value;
              }
            }
            break;
        }
        this.curMap.clear();
        for (const key in tempDataBackup) {
          this.curMap.set(key, _.cloneDeep(tempDataBackup[key]));
        }

        console.warn('curMap: ');
        console.warn(this.curMap);
        console.warn(this.tableList);
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
          // debugger
          this.tableList.forEach(item => {
            if (!item.aggregationId) {
              tempData.push(item);
              templateIds.push(item.detail.id);
            }
          });
          for (const [key, value] of this.curMap.entries()) {
            if (value.length === 1) {
              tempData.push(...value);
              tempData = _.uniqWith(tempData, _.isEqual);
            } else {
              let curInstances = [];
              // 这里避免从模板选择的权限和自定义权限下的操作是一致的，所以需要去重
              tempData = _.uniqWith(tempData, _.isEqual);
              const conditions = value.map((subItem) => subItem.resource_groups
                && subItem.resource_groups[0].related_resource_types[0].condition);
              // 是否都选择了实例
              const isAllHasInstance = conditions.every(subItem => subItem[0] !== 'none' && subItem.length > 0);
              if (isAllHasInstance) {
                const instances = conditions.map(subItem => subItem.map(v => v.instance));
                let isAllEqual = true;
                for (let i = 0; i < instances.length - 1; i++) {
                  if (!_.isEqual(instances[i], instances[i + 1])) {
                    isAllEqual = false;
                    break;
                  }
                }
                console.log('instances: ');
                console.log(instances);
                console.log('isAllEqual: ' + isAllEqual);
                console.log('value', value);
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
              tempData.push(new GroupAggregationPolicy({
                aggregationId: key,
                aggregate_resource_types: value[0].aggregateResourceType,
                actions: value,
                instances: curInstances,
                instancesDisplayData
              }));
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
        this.tableList = _.cloneDeep(tempList);
        this.handleUnlimitedActionChange(this.isAllUnlimited);
      },

      handleUnlimitedActionChange (payload) {
        if (['super_manager', 'system_manager'].includes(this.user.role.type)) {
          const tableData = _.cloneDeep(this.tableList);
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
                new GroupAggregationPolicy(item)
              );
            }
          });
          this.tableList = _.cloneDeep(tableData);
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

      /**
       * handleEditCustom
       */
      handleEditCustom () {
        if (!this.externalSystemsLayout.userGroup.addGroup.hideAddTemplateTextBtn) {
          this.permSideWidth = 1160;
        }
        this.curActionValue = this.originalList.map(item => item.$id);
        this.isShowAddActionSideslider = true;
      },

      /**
       * handleSelectSubmit
       */
      handleSelectSubmit (payload, aggregation, authorization) {
        // debugger
        if (this.originalList.length > 0) {
          const intersection = payload.filter(
            item => this.originalList.map(sub => sub.$id).includes(item.$id)
          );
          this.hasDeleteCustomList = this.originalList.filter(
            item => !intersection.map(sub => sub.$id).includes(item.$id)
          );
          // eslint-disable-next-line max-len
          this.hasAddCustomList = payload.filter(item => !intersection.map(sub => sub.$id).includes(item.$id));
        } else {
          this.hasAddCustomList = payload;
        }
        if (!payload.length) {
          this.curActionValue = [];
        }
        this.originalList = _.cloneDeep(payload);
        this.aggregationDataByCustom = _.cloneDeep(aggregation);
        this.authorizationDataByCustom = _.cloneDeep(authorization);
        if (this.externalSystemsLayout.userGroup.addGroup.hideAddTemplateTextBtn) {
          if (this.originalList.length) {
            this.curActionValue = this.originalList.map(item => item.$id);
            this.handleSubmitPerm(
              [],
              this.aggregationDataByCustom,
              this.authorizationDataByCustom
            );
          } else {
            this.curActionValue = [];
            this.handleSubmitPerm(
              [],
              this.aggregationDataByCustom,
              this.authorizationDataByCustom
            );
          }
        }
      },

      handleSelectCancel () {
        this.permSideWidth = 960;
      },

      /**
       * handleSubmit
       */
      async handleSubmit () {
        if (this.expired_at === 0) {
          this.isShowExpiredError = true;
        }
        const infoFlag = this.$refs.basicInfoRef.handleValidator();
        if (infoFlag) {
          this.scrollToLocation(this.$refs.basicInfoContentRef);
        }
        const $ref = this.$refs.resInstanceTableRef;
        let templates = [];
        let flag = false;
        if (!infoFlag) {
          if ($ref) {
            flag = $ref.getData().flag;
            templates = $ref.getData().templates;
          }
          if (!this.isShowMemberAdd) {
            if (this.expired_at === 0) {
              this.isShowExpiredError = true;
            }
          }
          if (this.isShowExpiredError || flag) {
            const $dom = flag ? this.$refs.instanceTableContentRef : this.$refs.memberRef;
            this.scrollToLocation($dom);
            return;
          }
          this.submitLoading = true;
          window.changeDialog = false;
          const params = {
            ...this.formData,
            members: this.members,
            expired_at: this.expired_at,
            templates
          };
          try {
            const { code, data } = await this.$store.dispatch('userGroup/addUserGroup', params);
            if (code === 0 && data) {
              this.messageSuccess(this.$t(`m.info['新建用户组管理成功']`), 3000);
              if (this.externalSystemId) { // 如果用户组新建成功需要发送一个postmessage给外部页面
                window.parent.postMessage({ type: 'IAM', data, code: 'create_user_group_submit' }, '*');
              } else {
                bus.$emit('show-guide', 'process');
                this.$router.push({
                  name: 'userGroup'
                });
              }
            }
          } catch (e) {
            console.error(e);
            this.messageAdvancedError(e);
          } finally {
            this.submitLoading = false;
          }
        }
      },

      /**
       * handleCancel
       */
      handleCancel () {
        if (this.externalSystemId) { // 用户组取消也需要发送一个postmessage给外部页面
          window.parent.postMessage({ type: 'IAM', code: 'create_user_group_cancel' }, '*');
        } else {
          let cancelHandler = Promise.resolve();
          if (window.changeDialog) {
            cancelHandler = leavePageConfirm();
          }
          cancelHandler.then(() => {
            this.$router.push({
              name: 'userGroup'
            });
          }, _ => _);
        }
      },

      /**
       * handleAddMember
       */
      handleAddMember () {
        this.isShowAddMemberDialog = true;
      },

      /**
       * handleExpiredAtChange
       */
      handleExpiredAtChange (payload) {
        window.changeDialog = true;
        if (payload) {
          this.isShowExpiredError = false;
        }
        if (payload !== PERMANENT_TIMESTAMP && payload) {
          const nowTimestamp = +new Date() / 1000;
          const tempArr = String(nowTimestamp).split('');
          const dotIndex = tempArr.findIndex(item => item === '.');
          const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
          this.expired_at = payload + nowSecond;
          return;
        }
        this.expired_at = payload;
      },

      /**
       * handleMemberDelete
       */
      handleMemberDelete (type, payload) {
        window.changeDialog = true;
        if (type === 'user') {
          this.users.splice(payload, 1);
        } else if (type === 'template') {
          this.templates.splice(payload, 1);
        } else {
          this.departments.splice(payload, 1);
        }
        this.isShowMemberAdd = this.users.length < 1 && this.departments.length < 1 && this.templates.length < 1;
      },

      /**
       * handleAddPerm
       */
      handleAddPerm () {
        this.externalSystemsLayout.userGroup.addGroup.hideAddTemplateTextBtn
          ? this.isShowAddActionSideslider = true : this.isShowAddSideslider = true;
      },

      /**
       * handleCancelAdd
       */
      handleCancelAdd () {
        this.isShowAddMemberDialog = false;
      },

      /**
       * handleSubmitAdd
       */
      handleSubmitAdd (payload) {
        window.changeDialog = true;
        const { users, departments, templates } = payload;
        this.users = _.cloneDeep(users);
        this.departments = _.cloneDeep(departments);
        this.templates = _.cloneDeep(templates);
        this.isShowMemberAdd = false;
        this.isShowAddMemberDialog = false;
      }
    },
    beforeRouteLeave (to, from, next) {
      if (this.externalSystemsLayout.userGroup.addGroup.hideAddTemplateTextBtn) {
        window.parent.postMessage({ type: 'IAM', code: 'create_user_group_cancel' }, '*');
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
          cancelHandler.then(() => {
            // next({ path: `${window.SITE_URL}${to.fullPath.slice(1, to.fullPath.length)}` });
            next();
          }, _ => _);
        } else {
          next();
        }
      } else {
        next();
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import '@/css/mixins/create-user-group.css';
@import '@/css/mixins/aggregate-action-group.css';
</style>
