<template>
  <smart-action class="iam-create-user-group-wrapper">
    <render-horizontal-block :label="$t(`m.common['基本信息']`)">
      <section ref="basicInfoContentRef">
        <basic-info
          :data="formData"
          ref="basicInfoRef"
          @on-change="handleBasicInfoChange" />
      </section>
    </render-horizontal-block>
    <render-action
      :title="$t(`m.userGroup['添加组权限']`)"
      ext-cls="add-perm-action"
      v-if="!isHasPermTemplate"
      data-test-id="group_btn_showAddGroupPerm"
      @on-click="handleAddPerm">
      <iam-guide
        type="add_group_perm_template"
        direction="left"
        :style="{ top: '-10px', left: '125px' }"
        :content="$t(`m.guide['添加组权限']`)" />
    </render-action>
    <render-horizontal-block
      :label="$t(`m.grading['操作和资源范围']`)"
      v-show="isHasPermTemplate">
      <div class="grade-admin-select-wrapper">
        <div class="action">
          <section class="action-wrapper" @click.stop="handleAddPerm">
            <Icon bk type="plus-circle-shape" />
            <span>{{ $t(`m.userGroup['添加组权限']`) }}</span>
          </section>
        </div>
        <div class="info-wrapper">
          <section style="min-width: 108px; position: relative;">
            <bk-switcher
              v-model="isAllExpanded"
              :disabled="isAggregateDisabled"
              size="small"
              theme="primary"
              @change="handleAggregateAction" />
            <span class="text">{{ expandedText }}</span>
          </section>
        </div>
        <section ref="instanceTableContentRef" v-bkloading="{ isLoading: cloneLoading, opacity: 1 }">
          <resource-instance-table
            is-edit
            mode="create"
            ref="resInstanceTableRef"
            :list="tableList"
            :authorization="curAuthorizationData"
            :original-list="tableListBackup"
            :is-all-expanded="isAllExpanded"
            :group-id="groupId"
            @handleAggregateAction="handleAggregateAction"
            @on-select="handleAttrValueSelected"
            @on-resource-select="handleResSelect" />
        </section>
      </div>
    </render-horizontal-block>
    <render-action
      :title="$t(`m.userGroup['添加组成员']`)"
      v-if="isShowMemberAdd"
      style="margin-bottom: 16px;"
      data-test-id="group_btn_showAddGroupMember"
      @on-click="handleAddMember">
      <iam-guide
        type="add_group_member"
        direction="left"
        :style="{ top: '-20px', left: '180px' }"
        :content="$t(`m.guide['添加组成员']`)" />
    </render-action>
    <section v-else ref="memberRef">
      <render-member
        :users="users"
        :departments="departments"
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
      :is-rating-manager="isRatingManager"
      :departments="departments"
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd" />

    <add-perm-sideslider
      :is-show.sync="isShowAddSideslider"
      :custom-perm="originalList"
      :template="tempalteDetailList"
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
      :id="templateDetailSideslider.id" />
  </smart-action>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { CUSTOM_PERM_TEMPLATE_ID, PERMANENT_TIMESTAMP, SIX_MONTH_TIMESTAMP } from '@/common/constants';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import IamGuide from '@/components/iam-guide/index.vue';
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
    components: {
      AddMemberDialog,
      basicInfo,
      renderAction,
      RenderMember,
      IamGuide,
      AddPermSideslider,
      AddActionSideslider,
      ResourceInstanceTable,
      RenderTemplateSideslider
    },
    data () {
      return {
        formData: {
          name: '',
          approval_process_id: 1,
          description: ''
        },
        isShowAddMemberDialog: false,
        isShowMemberAdd: true,
        expired_at: SIX_MONTH_TIMESTAMP,
        users: [],
        departments: [],
        submitLoading: false,
        isShowExpiredError: false,
        isShowAddSideslider: false,
        isShowAddActionSideslider: false,
        curActionValue: [],
        originalList: [],

        tableList: [],
        tableListBackup: [],
        tempalteDetailList: [],
        aggregationData: {},
        aggregationDataClone: {},
        authorizationDataClone: {},
        authorizationData: {},
        aggregationDataByCustom: {},
        authorizationDataByCustom: {},
        allAggregationData: {},
        isAllExpanded: false,

        hasDeleteCustomList: [],
        hasAddCustomList: [],
        templateDetailSideslider: {
          isShow: false,
          id: ''
        },
        curMap: null,
        groupSystemList: [],
        groupSystemListLength: 0,
        groupId: '',
        cloneLoading: true,
        permSideWidth: 960
      };
    },
    computed: {
            ...mapGetters(['user', 'externalSystemsLayout', 'externalSystemId']),
            /**
             * isAggregateDisabled
             */
            isAggregateDisabled () {
                const aggregationIds = this.tableList.reduce((counter, item) => {
                    return item.aggregationId !== '' ? counter.concat(item.aggregationId) : counter;
                }, []);
                const temps = [];
                console.log('aggregationIds', this.tableList, aggregationIds);
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

            /**
             * expandedText
             */
            expandedText () {
                return this.isAllExpanded ? this.$t(`m.grading['逐项编辑']`) : this.$t(`m.grading['批量编辑']`);
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
                const data = Object.assign(
                 this.authorizationData,
                 this.authorizationDataByCustom,
                 this.authorizationDataClone);
                return data;
            }
    },
    watch: {
      isShowAddSideslider (value) {
        if (!value) {
          this.permSideWidth = 960;
        }
      }
    },
    async mounted () {
      // this.formData.name = `${this.$route.query.name}_${this.$t(`m.grading['克隆']`)}`;
      // this.formData.description = this.$route.query.description;
      this.groupId = this.$route.query.id;
      await this.handleInit();
    },
    methods: {
      async handleInit () {
        if (this.groupId) {
          this.fetchDetail();
          this.fetchGroupSystem();
        }
      },

      async fetchDetail () {
        try {
          const params = {
            id: this.groupId
          };
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const { data } = await this.$store.dispatch('userGroup/getUserGroupDetail', params);
          const { name, description } = data;
          this.formData = Object.assign(this.formData, {
            name: `${name}_${this.$t(`m.grading['克隆']`)}`,
            description
          });
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },
            
      // 先请求最外层数据（系统）
      async fetchGroupSystem () {
        this.tableList = [];
        try {
          const params = {
            id: this.groupId
          };
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const res = await this.$store.dispatch('userGroup/getGroupSystems', params);
          this.groupSystemList = res.data || []; // groupSystemList会通过handleExpanded调用其他方法做属性的添加
          this.groupSystemListLength = res.data.length;
          console.log('this.groupSystemList', this.groupSystemList);
          for (let i = 0; i < this.groupSystemList.length; i++) {
            this.groupSystemList[i].count = this.groupSystemList[i].custom_policy_count;
            this.fetchAggregationAction(this.groupSystemList[i].id);
            this.fetchAuthorizationScopeActions(this.groupSystemList[i].id);
            if (this.groupSystemList[i].count > 0) {
              await this.getGroupCustomPolicy(this.groupSystemList[i]);
            }
            if (this.groupSystemList[i].template_count > 0) {
              setTimeout(async () => {
                await this.getGroupTemplateList(this.groupSystemList[i]);
              }, 500);
            }
          }
          this.handleAggregateData();
          this.cloneLoading = false;
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      // 自定义权限
      async getGroupCustomPolicy (item) {
        item.loading = true;
        try {
          const res = await this.$store.dispatch('userGroup/getGroupPolicy', {
            id: this.groupId,
            systemId: item.id
          });
          const tableData = res.data.map(row => {
            row.conditionIds = [];
            row.resource_groups.forEach(groupItem => {
              groupItem.related_resource_types.forEach(resourceTypeItem => {
                resourceTypeItem.id = resourceTypeItem.type;
                resourceTypeItem.condition && resourceTypeItem.condition.forEach((conditionItem) => {
                  conditionItem.instances.forEach((instanceItem) => {
                    instanceItem.path.forEach((pathItem) => {
                      pathItem.forEach((v) => {
                        const type = v.type === 'department' ? 'department' : '';
                        row.conditionIds.push(
                          { id: v.id, display_name: v.name, child_type: type }
                        );
                      });
                    });
                  });
                });
                resourceTypeItem.condition = '';
              });
            });
            // eslint-disable-next-line max-len
            // row.related_environments = this.linearActionList.find(sub => sub.id === row.id).related_environments;
            return new GroupPolicy(
              row,
              'add', // 此属性为flag，会在related-resource-types赋值为add
              'custom',
              {
                system: {
                  id: item.id,
                  name: item.name
                },
                id: CUSTOM_PERM_TEMPLATE_ID
              }
            );
          });
          // const tableDataBackup = res.data.map(row => {
          //     // eslint-disable-next-line max-len
          //     row.related_environments = this.linearActionList.find(sub => sub.id === row.id).related_environments;
          //     return new GroupPolicy(
          //         row,
          //         'detail',
          //         'custom',
          //         { system: item.system }
          //     );
          // });
          this.tableList.push(..._.cloneDeep(tableData));
          this.tableListBackup = _.cloneDeep(this.tableList);
          // this.$set(item, 'tableDataBackup', tableDataBackup);

          console.log('res', res);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      // 模版列表
      async getGroupTemplateList (groupSystem) {
        let res;
        try {
          res = await this.$store.dispatch('userGroup/getUserGroupTemplateList', {
            id: this.groupId,
            systemId: groupSystem.id
          });
          for (let i = 0; i < res.data.length; i++) {
            await this.getGroupTemplateDetail(res.data[i]);
          }

          // res.data.forEach(async item => {
          //     await this.getGroupTemplateDetail(item);
          // });
          groupSystem.templates = res.data; // 赋值给展开项
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      // 模版详情
      async getGroupTemplateDetail (item) {
        item.loading = true;
        try {
          const res = await this.$store.dispatch('userGroup/getGroupTemplateDetail', {
            id: this.groupId,
            templateId: item.id
          });
          const tableData = res.data.actions.map(row => {
            row.conditionIds = [];
            row.resource_groups.forEach(groupItem => {
              groupItem.related_resource_types.forEach(resourceTypeItem => {
                resourceTypeItem.id = resourceTypeItem.type;
                resourceTypeItem.condition && resourceTypeItem.condition.forEach((conditionItem) => {
                  conditionItem.instances.forEach((instanceItem) => {
                    instanceItem.path.forEach((pathItem) => {
                      pathItem.forEach((v) => {
                        const type = v.type === 'department' ? 'department' : '';
                        row.conditionIds.push(
                          { id: v.id, display_name: v.name, child_type: type }
                        );
                      });
                    });
                  });
                });
                resourceTypeItem.condition = '';
              });
            });
            // const temp = _.cloneDeep(row)
            // eslint-disable-next-line max-len
            // row.related_environments = this.linearActionList.find(sub => sub.id === row.id).related_environments;
            return new GroupPolicy(
              { ...row, policy_id: row.policy_id },
              'add',
              'template',
              { ...item }
            );
          });
          // const tableDataBackup = res.data.actions.map(row => {
          //     // eslint-disable-next-line max-len
          //     // row.related_environments = this.linearActionList.find(sub => sub.id === row.id).related_environments;
          //     return new GroupPolicy(
          //         { ...row, policy_id: 1 },
          //         'detail',
          //         'template',
          //         { system: res.data.system }
          //     );
          // });
          // this.$set(item, 'tableData', tableData);
          this.tableList.push(..._.cloneDeep(tableData));
          this.tableListBackup = _.cloneDeep(this.tableList);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          item.loading = false;
        }
      },

      // 合并操作需要的信息
      async fetchAggregationAction (id) {
        try {
          const res = await this.$store.dispatch('aggregate/getAggregateAction', { system_ids: id });
          this.aggregationDataClone[id] = res.data.aggregations;
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      async fetchAuthorizationScopeActions (id) {
        try {
          const res = await this.$store.dispatch(
            'permTemplate/getAuthorizationScopeActions',
            { systemId: id }
          );
          this.authorizationDataClone[id] = res.data.filter(item => item.id !== '*');
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
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
        const { customPerm } = payload;
        if (customPerm) {
          this.hasAddCustomList = [...customPerm];
          if (!customPerm.length) {
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
      },

      /**
       * handleSubmitPerm
       */
      handleSubmitPerm (templates, aggregation, authorization) {
        // debugger
        if (this.isAllExpanded) {
          this.isAllExpanded = false;
          this.handleAggregateAction(false);
        }

        this.aggregationData = aggregation;
        this.authorizationData = authorization;

        let hasDeleteTemplateList = [];
        let hasAddTemplateList = [];
        if (this.tempalteDetailList.length > 0) {
          const intersection = templates.filter(
            item => this.tempalteDetailList.map(sub => sub.id).includes(item.id)
          );
          hasDeleteTemplateList = this.tempalteDetailList.filter(
            item => !intersection.map(sub => sub.id).includes(item.id)
          );
          hasAddTemplateList = templates.filter(item => !intersection.map(sub => sub.id).includes(item.id));
        } else {
          hasAddTemplateList = templates;
        }
        this.tempalteDetailList = _.cloneDeep(templates);

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
        this.hasAddCustomList.forEach(item => {
          if (!item.resource_groups || !item.resource_groups.length) {
            item.resource_groups = item.related_resource_types.length ? [{ id: '', related_resource_types: item.related_resource_types }] : [];
          }
          tempList.push(new GroupPolicy(item, 'add', 'custom', {
            system: {
              id: item.system_id,
              name: item.system_name
            },
            id: CUSTOM_PERM_TEMPLATE_ID
          }));
        });

        if (this.tableList.length < 1) {
          this.tableList = _.cloneDeep(tempList);
        } else {
          this.tableList.push(..._.cloneDeep(tempList));
        }
        this.tableListBackup = _.cloneDeep(this.tableList);

        // 处理聚合的数据，将表格数据按照相同的聚合id分配好
        this.handleAggregateData();

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
        // debugger
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
        console.log('payload', payload);
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

      /**
       * handleAggregateData
       */
      handleAggregateData () {
        // debugger
        this.allAggregationData = Object.assign(
          this.aggregationData,
          this.aggregationDataByCustom,
          this.aggregationDataClone);
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

      /**
       * handleAggregateAction
       */
      handleAggregateAction (payload) {
        const tempData = [];
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
            } else {
              let curInstances = [];
              const conditions = value.map(subItem => subItem.resource_groups[0]
                .related_resource_types[0].condition);
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
            await this.$store.dispatch('userGroup/addUserGroup', params);
            this.messageSuccess(this.$t(`m.info['新建用户组成功']`), 1000);
            bus.$emit('show-guide', 'process');
            this.$router.push({
              name: 'userGroup'
            });
          } catch (e) {
            console.error(e);
            this.bkMessageInstance = this.$bkMessage({
              limit: 1,
              theme: 'error',
              message: e.message || e.data.msg || e.statusText,
              ellipsisLine: 2,
              ellipsisCopy: true
            });
          } finally {
            this.submitLoading = false;
          }
        }
      },

      /**
       * handleCancel
       */
      handleCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(() => {
          this.$router.push({
            name: 'userGroup'
          });
        }, _ => _);
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
        } else {
          this.departments.splice(payload, 1);
        }
        this.isShowMemberAdd = this.users.length < 1 && this.departments.length < 1;
      },

      /**
       * handleAddPerm
       */
      handleAddPerm () {
        if (this.externalSystemsLayout.userGroup.addGroup.hideAddTemplateTextBtn) {
          this.isShowAddActionSideslider = true;
        } else {
          this.isShowAddSideslider = true;
          this.permSideWidth = 1160;
        }
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
        const { users, departments } = payload;
        this.users = _.cloneDeep(users);
        this.departments = _.cloneDeep(departments);
        this.isShowMemberAdd = false;
        this.isShowAddMemberDialog = false;
      }
    },
    beforeRouteLeave (to, from, next) {
      delete to.query.id;
      next();
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-create-user-group-wrapper {
        padding-bottom: 50px;
        .add-perm-action {
            margin: 16px 0 20px 0;
        }
    }
    .grade-admin-select-wrapper {
        .action {
            position: relative;
            display: flex;
            justify-content: flex-start;
            .action-wrapper {
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
        .info-wrapper {
            display: flex;
            justify-content: flex-end;
            margin-top: 16px;
            line-height: 24px;
            .tips,
            .text {
                line-height: 20px;
                font-size: 12px;
            }
        }
    }
</style>
