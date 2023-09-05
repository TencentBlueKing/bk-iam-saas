<template>
  <div class="my-perm-custom-perm-table" v-bkloading="{ isLoading: loading, opacity: 1 }">
    <bk-table
      v-if="!loading"
      :data="policyList"
      border
      :cell-class-name="getCellClass">
      <bk-table-column :label="$t(`m.common['操作']`)" min-width="160">
        <template slot-scope="{ row }">
          <span :title="row.name">{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" min-width="360">
        <template slot-scope="{ row }">
          <template v-if="!row.isEmpty">
            <div
              v-for="(_, _index) in row.resource_groups"
              :key="_.id"
              class="related-resource-list"
              :class="
                row.resource_groups === 1 || _index === row.resource_groups.length - 1
                  ? ''
                  : 'related-resource-list-border'
              "
            >
              <p class="related-resource-item" v-for="item in _.related_resource_types" :key="item.type">
                <render-resource-popover
                  :key="item.type"
                  :data="item.condition"
                  :value="`${item.name}: ${item.value}`"
                  :max-width="380"
                  @on-view="handleViewResource(_, row)"
                />
              </p>
              <Icon
                v-if="isShowPreview(row)"
                type="detail-new"
                class="view-icon"
                :title="$t(`m.perm['查看实例资源权限组']`)"
                @click.stop="handleViewResource(_, row)"
              />
              <Icon
                v-if="isShowPreview(row) && row.resource_groups.length > 1"
                type="delete-line"
                :title="$t(`m.perm['删除实例资源权限组']`)"
                :class="row.resource_groups.length > 1 ? 'effect-icon' : 'effect-icon-disabled'"
                @click.stop="handlerReduceInstance(_, row)"
              />
            </div>
          </template>
          <template v-else>
            <span class="pl20" style="line-height: 62px;">{{ $t(`m.common['无需关联实例']`) }}</span>
          </template>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['生效条件']`)" min-width="300">
        <template slot-scope="{ row }">
          <div class="condition-table-cell" v-if="!!row.related_environments.length">
            <div
              v-for="(_, groIndex) in row.resource_groups"
              :key="_.id"
              class="related-condition-list"
              :class="[
                row.resource_groups.length > 1 ? 'related-resource-list' : 'environ-group-one',
                row.resource_groups === 1 || groIndex === row.resource_groups.length - 1
                  ? ''
                  : 'related-resource-list-border'
              ]"
            >
              <effect-conditon :value="_.environments" :is-empty="!_.environments.length"> </effect-conditon>
              <Icon
                type="detail-new"
                class="effect-detail-icon"
                :title="$t(`m.common['详情']`)"
                v-if="isShowPreview(row)"
                @click.stop="handleEnvironmentsViewResource(_, row)"
              />
            </div>
          </div>
          <div v-else class="condition-table-cell empty-text">{{ $t(`m.common['无生效条件']`) }}</div>
        </template>
      </bk-table-column>
      <bk-table-column prop="expired_dis" min-width="100" :label="$t(`m.common['有效期']`)"></bk-table-column>
      <bk-table-column
        :label="$t(`m.common['操作-table']`)"
        :width="200"
      >
        <template slot-scope="{ row }">
          <div class="custom-actions-item">
            <bk-button
              type="primary"
              text
              @click="handleShowDelDialog(row)">
              {{ $t(`m.userGroupDetail['删除操作权限']`) }}
            </bk-button>
          </div>
        </template>
      </bk-table-column>
      <template slot="empty">
        <ExceptionEmpty
          :type="policyEmptyData.type"
          :empty-text="policyEmptyData.text"
          :tip-text="policyEmptyData.tip"
          :tip-type="policyEmptyData.tipType"
          @on-refresh="handleRefreshData"
        />
      </template>
    </bk-table>

    <delete-dialog
      :show.sync="deleteDialog.visible"
      :loading="deleteDialog.loading"
      :title="deleteDialog.title"
      :sub-title="deleteDialog.subTitle"
      @on-after-leave="handleAfterDeleteLeave"
      @on-cancel="hideCancelDelete"
      @on-sumbit="handleSubmitDelete"
    />

    <bk-sideslider
      :is-show="isShowSideslider"
      :title="sidesliderTitle"
      :width="960"
      quick-close
      data-test-id="myPerm_sideslider_resourceInsance"
      @update:isShow="handleResourceCancel"
    >
      <div slot="header" class="iam-my-custom-perm-silder-header">
        <span>{{ sidesliderTitle }}</span>
        <div class="action-wrapper" v-if="canOperate">
          <bk-button
            text
            theme="primary"
            size="small"
            style="padding: 0"
            :disabled="batchDisabled"
            v-if="isBatchDelete"
            @click="handleBatchDelete"
          >
            {{ $t(`m.common['批量删除实例权限']`) }}
          </bk-button>
          <template v-else>
            <iam-popover-confirm
              :title="$t(`m.info['确定删除实例权限']`)"
              :disabled="disabled"
              :is-custom-footer="true"
              :cancel-text="$t(`m.common['取消-dialog']`)"
              :confirm-handler="handleDeletePerm"
            >
              <div
                slot="title"
                class="popover-custom-title">
                {{ $t(`m.dialog['确认删除内容？']`, { value: $t(`m.dialog['删除实例权限']`) }) }}
              </div>
              <!-- 这个地方后台需要增加跟当前操作有关联的操作下的资源实例一起删除的接口，目前暂不展示关联操作内容 -->
              <!-- <div
                slot="content"
                :class="[
                  'popover-custom-content',
                  { 'popover-custom-content-hide': !delActionList.length }
                ]">
                <div :title="formateDelPathTitle">
                  {{ $t(`m.info['删除依赖实例产生的影响']`, {
                    value: formateDelPathTitle.length > 1 ? `${formateDelPathTitle[0]}...` : formateDelPathTitle })
                  }}
                </div>
                <div class="custom-related-instance">
                  <p
                    v-for="item in delActionList"
                    :key="item.id">
                    <Icon
                      bk
                      type="info-circle-shape"
                      style=" color: #ffb848;"
                    />
                    {{ item.name }}
                  </p>
                </div>
              </div> -->
              <bk-button theme="primary" :disabled="disabled">
                {{ $t(`m.common['删除']`) }}
              </bk-button>
            </iam-popover-confirm>
            <bk-button style="margin-left: 10px" @click="handleCancel">
              {{ $t(`m.common['取消']`) }}
            </bk-button>
          </template>
        </div>
      </div>
      <div slot="content">
        <render-detail
          :data="previewData"
          :can-edit="!isBatchDelete"
          ref="detailComRef"
          @tab-change="handleTabChange"
          @on-change="handleChange"
          @on-select-all="handleSelectAll"
        >
        </render-detail>
      </div>
    </bk-sideslider>

    <bk-sideslider
      :is-show="isShowEnvironmentsSideslider"
      :title="environmentsSidesliderTitle"
      :width="640"
      quick-close
      @update:isShow="handleResourceCancel"
      ext-cls="effect-conditon-side"
    >
      <div slot="content">
        <effect-conditon
          :value="environmentsSidesliderData"
          :is-empty="!environmentsSidesliderData.length"
          @on-view="handleViewSidesliderCondition"
        >
        </effect-conditon>
      </div>
    </bk-sideslider>

    <!-- 生效时间编辑功能需要产品确认 暂时隐藏 -->
    <bk-sideslider
      :is-show="isShowResourceInstanceEffectTime"
      :title="environmentsSidesliderTitle"
      :width="640"
      quick-close
      @update:isShow="handleResourceEffectTimeCancel"
      :ext-cls="'relate-instance-sideslider'"
    >
      <div slot="content" class="sideslider-content">
        <sideslider-effect-conditon ref="sidesliderRef" :data="environmentsSidesliderData"></sideslider-effect-conditon>
      </div>
      <div slot="footer" style="margin-left: 25px">
        <bk-button theme="primary" :loading="sliderLoading" @click="handleResourceEffectTimeSumit">
          {{ $t(`m.common['保存']`) }}</bk-button
        >
        <bk-button style="margin-left: 10px" @click="handleResourceEffectTimeCancel">{{
          $t(`m.common['取消']`)
        }}</bk-button>
      </div>
    </bk-sideslider>

    <delete-action-dialog
      :show.sync="isShowDeleteDialog"
      :title="delActionDialogTitle"
      :tip="delActionDialogTip"
      :name="currentActionName"
      :related-action-list="delActionList"
      @on-after-leave="handleAfterDeleteLeaveAction"
      @on-cancel="handleCancelDelete"
      @on-submit="handleSubmitDelete"
    />
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { formatCodeData } from '@/common/util';
  import IamPopoverConfirm from '@/components/iam-popover-confirm';
  import DeleteDialog from '@/components/iam-confirm-dialog/index.vue';
  import RenderResourcePopover from '../components/prem-view-resource-popover';
  import PermPolicy from '@/model/my-perm-policy';
  import { leaveConfirm } from '@/common/leave-confirm';
  import RenderDetail from '../components/render-detail-edit';
  import EffectConditon from './effect-conditon';
  import SidesliderEffectConditon from './sideslider-effect-condition';
  import DeleteActionDialog from '@/views/group/components/delete-related-action-dialog.vue';

  export default {
    name: 'CustomPermTable',
    provide: function () {
      return {
        isCustom: () => this.isCustom
      };
    },
    components: {
      IamPopoverConfirm,
      RenderDetail,
      RenderResourcePopover,
      DeleteDialog,
      EffectConditon,
      SidesliderEffectConditon,
      DeleteActionDialog
    },
    props: {
      systemId: {
        type: String,
        default: ''
      },
      isSearchPerm: {
        type: Boolean,
        default: false
      },
      emptyData: {
        type: Object,
        default: () => {
          return {
            type: '',
            text: '',
            tip: '',
            tipType: ''
          };
        }
      },
      curSearchParams: {
        type: Object
      }
    },
    data () {
      return {
        policyList: [],
        policyCountMap: {},
        initRequestQueue: ['permTable'],
        previewData: [],
        curId: '',
        curPolicyId: '',
        isShowSideslider: false,
        curDeleteIds: [],
        deleteDialog: {
          visible: false,
          title: this.$t(`m.dialog['确认删除']`),
          subTitle: '',
          loading: false
        },
        sidesliderTitle: '',
        isBatchDelete: true,
        batchDisabled: false,
        disabled: true,
        canOperate: true,
        isShowEnvironmentsSideslider: false,
        environmentsSidesliderTitle: this.$t(`m.common['生效条件']`),
        environmentsSidesliderData: [],
        isShowResourceInstanceEffectTime: false,
        resourceGroupParams: {},
        params: '',
        originalCustomTmplList: [],
        isCustom: true,
        isShowDeleteDialog: false,
        currentActionName: '',
        currentInstanceGroupName: '',
        delActionDialogTitle: '',
        delActionDialogTip: '',
        delActionList: [],
        curInstancePaths: [],
        policyIdList: [],
        policyEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        searchParams: {}
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      loading () {
        return this.initRequestQueue.length > 0;
      },
      isShowPreview () {
        return (payload) => {
          return !payload.isEmpty && payload.policy_id !== '';
        };
      },
      formateDelPathTitle () {
        let tempList = [];
        tempList
          = this.curInstancePaths.length
          && this.curInstancePaths.reduce((prev, next) => {
            prev.push(
              ...next.path.map((v) => {
                return v.length && v.map((sub) => sub.name).join('/');
              })
            );
            return prev;
          }, []);
        return tempList || [];
      }
    },
    watch: {
      systemId: {
        async handler (value) {
          if (value !== '') {
            this.initRequestQueue = ['permTable'];
            const params = {
              systemId: value
            };
            this.params = params;
            await this.fetchActions(value);
            this.fetchData(params);
          } else {
            this.initRequestQueue = [];
            this.policyList = [];
            this.policyCountMap = {};
          }
        },
        immediate: true
      },
      emptyData: {
        handler (value) {
          this.policyEmptyData = Object.assign({}, value);
        },
        immediate: true
      },
      curSearchParams: {
        handler (value) {
          this.searchParams = Object.assign({}, value);
        },
        immediate: true
      }
    },
    methods: {
      /**
       * 获取系统对应的自定义操作
       *
       * @param {String} systemId 系统id
       * 执行handleActionLinearData方法
       */
      async fetchActions (systemId) {
        const params = {
          user_id: this.user.username
        };
        if (this.externalSystemId) {
          params.system_id = this.externalSystemId;
        }
        if (systemId) {
          params.system_id = systemId;
        }
        try {
          const res = await this.$store.dispatch('permApply/getActions', params);
          this.originalCustomTmplList = _.cloneDeep(res.data);
          this.handleActionLinearData();
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      /**
       * fetchData
       */
      async fetchData (params) {
        try {
          let url = '';
          let queryParams = {};
          if (this.isSearchPerm) {
            url = 'perm/getPoliciesSearch';
            queryParams = {
              ...this.searchParams
            };
          } else {
            url = 'permApply/getPolicies';
            queryParams = {
              system_id: params.systemId
            };
          }
          const { code, data } = await this.$store.dispatch(url, queryParams);
          // this.policyList = policyData[params.systemId].map(item => {
          this.policyList = data.length && data.map(item => {
            const relatedEnvironments = this.linearActionList.find(sub => sub.id === item.id);
            item.related_environments = relatedEnvironments ? relatedEnvironments.related_environments : [];
            return new PermPolicy(item);
          });
          this.policyEmptyData = formatCodeData(code, this.policyEmptyData, data.length === 0);
        } catch (e) {
          console.error(e);
          this.policyEmptyData = formatCodeData(e.code, this.policyEmptyData);
          this.messageAdvancedError(e);
        } finally {
          this.initRequestQueue.shift();
          if (this.isSearchPerm) {
            bus.$emit('on-perm-tab-count', { active: 'CustomPerm', count: this.policyList.length || 0 });
          }
        }
      },

      handleActionLinearData () {
        const linearActions = [];
        this.originalCustomTmplList.forEach((item, index) => {
          item.actions = item.actions.filter(v => !v.hidden);
          item.actions.forEach(act => {
            linearActions.push(act);
          });
          (item.sub_groups || []).forEach(sub => {
            sub.actions = sub.actions.filter(v => !v.hidden);
            sub.actions.forEach(act => {
              linearActions.push(act);
            });
          });
        });
        this.linearActionList = _.cloneDeep(linearActions);
      },

      /**
       * getCellClass
       */
      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 1 || columnIndex === 2) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      /**
       * handleRefreshData
       */
      handleRefreshData () {
        this.initRequestQueue = ['permTable'];
        const params = {
          systemId: this.systemId
        };
        this.fetchData(params);
      },

      /**
       * handleBatchDelete
       */
      handleBatchDelete () {
        window.changeAlert = true;
        this.isBatchDelete = false;
      },

      handleTabChange (payload) {
        const { disabled, canDelete } = payload;
        this.batchDisabled = disabled;
        this.canOperate = canDelete;
      },

      handleChange () {
        const data = this.$refs.detailComRef.handleGetValue();
        this.disabled = data.ids.length < 1 && data.condition.length < 1;
        if (!this.disabled) {
          this.handleDeleteActionOrInstance(Object.assign(data, { id: this.curId, policy_id: this.curPolicyId }), 'instance');
        }
      },

      handleSelectAll (isAll, payload) {
        if (!isAll) {
          this.curInstancePaths = [];
          return;
        }
        const { instance } = payload;
        this.curInstancePaths = [...instance];
      },

      async handleDeletePerm (payload) {
        const data = this.$refs.detailComRef.handleGetValue();
        const { ids, condition, type, resource_group_id } = data;
        const params = {
          id: this.curPolicyId,
          data: {
            system_id: data.system_id,
            type: type,
            ids,
            condition,
            resource_group_id
          }
        };
        try {
          await this.$store.dispatch('permApply/updatePerm', params);
          window.changeAlert = false;
          this.isShowSideslider = false;
          this.resetDataAfterClose();
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          this.handleRefreshData();
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          payload && payload.hide();
        }
      },
      
      // 区分删除操作还是实例
      handleDeleteActionOrInstance (payload, type) {
        const { id, name, condition } = payload;
        let delRelatedActions = [];
        this.delActionList = [];
        const policyIdList = this.policyList.map(v => v.id);
        const linearActionList = this.linearActionList.filter(item => policyIdList.includes(item.id));
        const curAction = linearActionList.find(item => item.id === id);
        const hasRelatedActions = curAction && curAction.related_actions && curAction.related_actions.length;
        linearActionList.forEach(item => {
          // 如果这里过滤自己还能在其他数据找到相同的related_actions，就代表有其他数据也关联了相同的操作
          if (hasRelatedActions && item.related_actions && item.related_actions.length && item.id !== id) {
            delRelatedActions = item.related_actions.filter(v => curAction.related_actions.includes(v));
          }
          if (item.related_actions && item.related_actions.includes(id)) {
            this.delActionList.push(item);
          }
        });
        let policyIds = [payload.policy_id];
        if (this.delActionList.length) {
          const list = this.policyList.filter(
            item => this.delActionList.map(action => action.id).includes(item.id));
          policyIds = [payload.policy_id].concat(list.map(v => v.policy_id));
        }
        this.policyIdList = _.cloneDeep(policyIds);
        const typeMap = {
          action: () => {
            this.currentActionName = name;
            if (!delRelatedActions.length && hasRelatedActions) {
              const list = [...this.policyList].filter(v => curAction.related_actions.includes(v.id));
              if (list.length) {
                policyIds = policyIds.concat(list.map(v => v.policy_id));
              }
            }
            this.curDeleteIds.splice(0, this.curDeleteIds.length, ...policyIds);
            this.policyIdList = _.cloneDeep(this.curDeleteIds);
            this.delActionDialogTitle = this.$t(`m.dialog['确认删除内容？']`, { value: this.$t(`m.dialog['删除操作权限']`) });
            this.delActionDialogTip = this.$t(`m.info['删除依赖操作产生的影响']`, { value: this.currentActionName });
            this.isShowDeleteDialog = true;
          },
          instance: () => {
            let curPaths = [];
            if (condition.length) {
              curPaths = condition.reduce((prev, next) => {
                prev.push(
                  ...next.instances.map(v => {
                    const paths = { ...v, ...next };
                    delete paths.instances;
                    return paths;
                  })
                );
                return prev;
              }, []);
              this.curInstancePaths = [...curPaths];
            }
          },
          groupInstance: () => {
            this.policyIdList = _.cloneDeep(policyIds);
            this.delActionDialogTitle = this.$t(`m.dialog['确认删除内容？']`, { value: this.$t(`m.dialog['删除一组实例权限']`) });
            this.delActionDialogTip = this.$t(`m.info['删除组依赖实例产生的影响']`, { value: this.currentActionName });
            this.isShowDeleteDialog = true;
          }
        };
        typeMap[type]();
      },

      handleCancel () {
        this.isBatchDelete = true;
      },

      handleResourceCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(() => {
          this.isShowSideslider = false;
          this.isShowEnvironmentsSideslider = false;
          this.resetDataAfterClose();
        }, _ => _);
      },

      handleResourceEffectTimeCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(() => {
          this.isShowResourceInstanceEffectTime = false;
          this.resetDataAfterClose();
        }, _ => _);
      },

      /**
       * handleResourceEffectTimeSumit
       */
      handleResourceEffectTimeSumit () {
        const environments = this.$refs.sidesliderRef.handleGetValue();
        console.log(this.curIndex, this.curGroupIndex, environments);
        window.changeAlert = false;
      },

      /**
       * resetDataAfterClose
       */
      resetDataAfterClose () {
        this.sidesliderTitle = '';
        this.previewData = [];
        this.canOperate = true;
        this.batchDisabled = false;
        this.disabled = true;
        this.isBatchDelete = true;
        this.curId = '';
        this.curPolicyId = '';
      },

      /**
       * handleAfterDeleteLeave
       */
      handleAfterDeleteLeave () {
        this.deleteDialog.subTitle = '';
        this.curDeleteIds = [];
      },

      /**
       * hideCancelDelete
       */
      hideCancelDelete () {
        this.deleteDialog.visible = false;
      },

      handleAfterDeleteLeaveAction () {
        this.currentActionName = '';
        this.delActionList = [];
        this.curDeleteIds = [];
        this.policyIdList = [];
        this.resourceGroupParams = {};
      },

      handleCancelDelete () {
        this.isShowDeleteDialog = false;
        this.curDeleteIds = [];
      },

      /**
       * handleViewResource
       */
      handleViewResource (groupItem, payload) {
        this.curId = payload.id;
        this.curPolicyId = payload.policy_id;
        const params = [];

        if (groupItem.related_resource_types.length > 0) {
          groupItem.related_resource_types.forEach(item => {
            const { name, type, condition } = item;
            params.push({
              name: type,
              label: this.$t(`m.info['tab操作实例']`, { value: name }),
              tabType: 'resource',
              data: condition,
              systemId: item.system_id,
              resource_group_id: groupItem.id
            });
          });
        }
        this.previewData = _.cloneDeep(params);
        if (this.previewData[0].tabType === 'relate') {
          this.canOperate = false;
        }
        if (this.previewData[0].tabType === 'resource' && (this.previewData[0].data.length < 1 || this.previewData[0].data.every(item => !item.instance || item.instance.length < 1))) {
          this.batchDisabled = true;
        }
        this.sidesliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        window.changeAlert = 'iamSidesider';
        this.isShowSideslider = true;
      },

      /**
       * handleEnvironmentsViewResource
       */
      handleEnvironmentsViewResource (payload, data) {
        this.environmentsSidesliderData = payload.environments;
        this.isShowEnvironmentsSideslider = true;
        this.environmentsSidesliderTitle = this.$t(`m.info['关联侧边栏操作生效条件']`, { value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}` });
      },

      /**
       * handlerReduceInstance
       */
      handlerReduceInstance (payload, data) {
        if (data.resource_groups.length < 2) return;
        // this.deleteDialog.subTitle = this.$t(`m.dialog['确认删除内容？']`, { value: this.$t(`m.dialog['删除一组实例权限']`) });
        // this.deleteDialog.visible = true;
        const { id, related_resource_types: relatedResourceTypes } = payload;
        this.resourceGroupParams = {
          id: data.policy_id,
          resourceGroupId: id
        };
        if (relatedResourceTypes && relatedResourceTypes.length) {
          this.currentActionName = relatedResourceTypes.map(item => item.name).join();
        }
        this.handleDeleteActionOrInstance(data, 'groupInstance');
      },

      /**
       * handleViewSidesliderCondition
       */
      handleViewSidesliderCondition () {
        console.log('environmentsSidesliderData', this.environmentsSidesliderData);
        this.isShowResourceInstanceEffectTime = true;
      },

      /**
       * handleShowDelDialog
       */
      handleShowDelDialog (payload) {
        this.handleDeleteActionOrInstance(payload, 'action');
      },

      /**
       * handleSubmitDelete
       */
      async handleSubmitDelete () {
        this.deleteDialog.loading = true;
        try {
          if (this.resourceGroupParams.id && this.resourceGroupParams.resourceGroupId) { // 表示删除的是资源组
            for (let i = 0; i < this.policyIdList.length; i++) {
              await this.$store.dispatch(
                'permApply/deleteRosourceGroupPerm',
                {
                  id: this.policyIdList[i],
                  resourceGroupId: this.resourceGroupParams.resourceGroupId
                }
              );
            }
            setTimeout(() => {
              this.fetchData(this.params);
              this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
            }, 2000);
          } else {
            await this.$store.dispatch('permApply/deletePerm', {
              policyIds: this.curDeleteIds,
              systemId: this.systemId
            });
            const index = this.policyList.findIndex(item => item.policy_id === this.curDeleteIds[0]);
            if (index > -1) {
              this.policyList.splice(index, 1);
            }
            await this.fetchActions(this.systemId);
            await this.fetchData(this.params);
            this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
            this.$emit('after-delete', this.policyList.length);
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.deleteDialog.loading = false;
          this.deleteDialog.visible = false;
          this.isShowDeleteDialog = false;
        }
      }
    }
  };
</script>

<style lang='postcss'>
    .my-perm-custom-perm-table {
        min-height: 101px;
        .bk-table-enable-row-hover .bk-table-body tr:hover > td {
            background-color: #fff;
        }
        .related-condition-list{
            flex: 1;
            display: flex;
            flex-flow: column;
            justify-content: center;
            position: relative;
            .effect-detail-icon {
                display: none;
                position: absolute;
                top: 50%;
                right: 10px;
                transform: translate(0, -50%);
                font-size: 18px;
                cursor: pointer;
            }
            &:hover {
                .effect-detail-icon {
                    display: inline-block;
                    color: #3a84ff;
                }
            }
        }
        .related-resource-list{
            position: relative;
            .related-resource-item{
                margin: 20px !important;
            }
            .view-icon {
                display: none;
                position: absolute;
                top: 50%;
                right: 40px;
                transform: translate(0, -50%);
                font-size: 18px;
                cursor: pointer;
            }
            &:hover {
                .view-icon {
                    display: inline-block;
                    color: #3a84ff;
                }
            }
            .effect-icon {
                display: none;
                position: absolute;
                top: 50%;
                right: 10px;
                transform: translate(0, -50%);
                font-size: 18px;
                cursor: pointer;
            }
            &:hover {
                .effect-icon {
                    display: inline-block;
                    color: #3a84ff;
                }
            }
            .effect-icon-disabled{
                display: none;
                position: absolute;
                top: 50%;
                right: 10px;
                transform: translate(0, -50%);
                font-size: 18px;
                cursor: pointer;
            }
            &:hover {
                .effect-icon-disabled {
                    display: inline-block;
                    color: #dcdee5;
                }
            }
            &-border{border-bottom: 1px solid #dfe0e5;}
        }
        .bk-table {
            border-right: none;
            border-bottom: none;
            .bk-table-header-wrapper {
                .cell {
                    padding-left: 20px !important;
                }
            }
            .bk-table-body-wrapper {
                .cell {
                    padding: 20px !important;
                }
            }

            .iam-perm-table-cell-cls {
                .cell {
                    padding: 0px !important;
                    height: 100%;
                }
                .condition-table-cell{
                    height: 100%;
                    flex-flow: column;
                    display: flex;
                    justify-content: center;
                    /* padding: 15px 0; */
                }
                .empty-text {
                    padding: 0 20px;
                }
            }
            tr:hover {
                background-color: #fff;
            }
        }

        .iam-my-custom-perm-silder-header {
            display: flex;
            justify-content: space-between;
            .action-wrapper {
                margin-right: 30px;
                font-weight: normal;
            }
            .popover-custom-title {
              text-align: center;
              font-size: 24px;
            }
        }

        .effect-conditon-side{
            .text{
                font-size: 14px;
                color: #63656e;
            }
        }
    }
</style>

<style lang="postcss" scoped>
.popover-custom-title {
  text-align: center;
  font-size: 18px;
}
.popover-custom-content {
  padding-left: 44px;
  font-size: 14px;
  word-break: break-all;
  max-height: 220px;
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
  &-hide {
    display: none;
  }
  .custom-related-instance {
    padding: 10px 0;
  }
}
</style>
