<template>
  <div class="my-perm-custom-perm-table" v-bkloading="{ isLoading: loading, opacity: 1 }">
    <bk-table
      v-if="!loading"
      :data="policyList"
      border
      :cell-class-name="getCellClass">
      <bk-table-column :label="$t(`m.common['操作']`)" min-width="120">
        <template slot-scope="{ row }">
          <span :title="row.name">{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" min-width="450">
        <template slot-scope="{ row }">
          <template v-if="!row.isEmpty">
            <div v-for="(_, _index) in row.resource_groups" :key="_.id" class="related-resource-list"
              :class="row.resource_groups === 1 || _index === row.resource_groups.length - 1
                ? '' : 'related-resource-list-border'">
              <p class="related-resource-item"
                v-for="item in _.related_resource_types"
                :key="item.type">
                <render-resource-popover
                  :key="item.type"
                  :data="item.condition"
                  :value="`${item.name}：${item.value}`"
                  :max-width="380"
                  @on-view="handleViewResource(_, row)" />
              </p>
              <Icon
                type="detail-new"
                class="view-icon"
                :title="$t(`m.common['详情']`)"
                v-if="isShowPreview(row)"
                @click.stop="handleViewResource(_, row)" />
              <Icon v-if="isShowPreview(row)"
                :title="$t(`m.common['删除']`)" type="reduce-hollow"
                :class="row.resource_groups.length > 1 ? 'effect-icon' : 'effect-icon-disabled'"
                @click.stop="handlerReduceInstance(_, row)" />
            </div>
          </template>
          <template v-else>
            <div class="pl20 mt20">{{ $t(`m.common['无需关联实例']`) }}</div>
          </template>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['生效条件']`)" min-width="300">
        <template slot-scope="{ row }">
          <div class="condition-table-cell" v-if="!!row.related_environments.length">
            <div v-for="(_, groIndex) in row.resource_groups" :key="_.id"
              class="related-condition-list"
              :class="[row.resource_groups.length > 1 ? 'related-resource-list' : 'environ-group-one',
                       row.resource_groups === 1 || groIndex === row.resource_groups.length - 1
                         ? '' : 'related-resource-list-border']">
              <effect-conditon
                :value="_.environments"
                :is-empty="!_.environments.length">
              </effect-conditon>
              <Icon
                type="detail-new"
                class="effect-detail-icon"
                :title="$t(`m.common['详情']`)"
                v-if="isShowPreview(row)"
                @click.stop="handleEnvironmentsViewResource(_, row)" />
            </div>
          </div>
          <div v-else class="condition-table-cell empty-text">{{ $t(`m.common['无生效条件']`) }}</div>
        </template>
      </bk-table-column>
      <bk-table-column prop="expired_dis" :label="$t(`m.common['有效期']`)"></bk-table-column>
      <bk-table-column :label="$t(`m.common['操作']`)" width="180">
        <template slot-scope="{ row }">
          <bk-button text @click="handleDelete(row)">{{ $t(`m.common['删除']`) }}</bk-button>
          <bk-button v-if="row.expired_dis === $t(`m.common['已过期']`)"
            text @click="handleToTemporaryCustomApply(row)">
            {{ $t(`m.myApply['再次申请']`) }}
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>

    <delete-dialog
      :show.sync="deleteDialog.visible"
      :loading="deleteDialog.loading"
      :title="deleteDialog.title"
      :sub-title="deleteDialog.subTitle"
      @on-after-leave="handleAfterDeleteLeave"
      @on-cancel="hideCancelDelete"
      @on-sumbit="handleSumbitDelete" />

    <bk-sideslider
      :is-show="isShowSideslider"
      :title="sidesliderTitle"
      :width="960"
      quick-close
      data-test-id="myPerm_sideslider_resourceInsance"
      @update:isShow="handleResourceCancel">
      <div slot="header" class="iam-my-custom-perm-silder-header">
        <span>{{ sidesliderTitle}}</span>
        <div class="action-wrapper" v-if="canOperate">
          <bk-button
            text
            theme="primary"
            size="small"
            style="padding: 0;"
            :disabled="batchDisabled"
            v-if="isBatchDelete"
            @click="handleBatchDelete">{{ $t(`m.common['批量删除实例权限']`) }}</bk-button>
          <template v-else>
            <iam-popover-confirm
              :title="$t(`m.info['确定删除实例权限']`)"
              :disabled="disabled"
              :confirm-handler="handleDeletePerm">
              <bk-button
                theme="primary"
                :disabled="disabled">
                {{ $t(`m.common['删除']`) }}
              </bk-button>
            </iam-popover-confirm>
            <bk-button style="margin-left: 10px;" @click="handleCancel">
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
          @on-change="handleChange" />
      </div>
    </bk-sideslider>

    <bk-sideslider
      :is-show="isShowEnvironmentsSideslider"
      :title="environmentsSidesliderTitle"
      :width="640"
      quick-close
      @update:isShow="handleResourceCancel"
      ext-cls="effect-conditon-side">
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
      :ext-cls="'relate-instance-sideslider'">
      <div slot="content" class="sideslider-content">
        <sideslider-effect-conditon
          ref="sidesliderRef"
          :data="environmentsSidesliderData"
        ></sideslider-effect-conditon>
      </div>
      <div slot="footer" style="margin-left: 25px;">
        <bk-button theme="primary" :loading="sliderLoading"
          @click="handleResourceEffectTimeSumit">
          {{ $t(`m.common['保存']`) }}</bk-button>
        <bk-button style="margin-left: 10px;"
          @click="handleResourceEffectTimeCancel">{{ $t(`m.common['取消']`) }}</bk-button>
      </div>
    </bk-sideslider>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import IamPopoverConfirm from '@/components/iam-popover-confirm';
  import DeleteDialog from '@/components/iam-confirm-dialog/index.vue';
  import RenderResourcePopover from '../components/prem-view-resource-popover';
  import PermPolicy from '@/model/my-perm-policy';
  import { leaveConfirm } from '@/common/leave-confirm';
  import RenderDetail from '../components/render-detail-edit';
  import EffectConditon from './effect-conditon';
  import SidesliderEffectConditon from './sideslider-effect-condition';

  export default {
    name: 'CustomPermTable',
    components: {
      IamPopoverConfirm,
      RenderDetail,
      RenderResourcePopover,
      DeleteDialog,
      EffectConditon,
      SidesliderEffectConditon
    },
    props: {
      systemId: {
        type: String,
        default: ''
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
        resourceGrouParams: {},
        params: '',
        originalCustomTmplList: []

      };
    },
    computed: {
            ...mapGetters(['user']),
            loading () {
                return this.initRequestQueue.length > 0;
            },
            isShowPreview () {
                return (payload) => {
                    return !payload.isEmpty && payload.policy_id !== '';
                };
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
          system_id: systemId,
          user_id: this.user.username
        };
        try {
          const res = await this.$store.dispatch('permApply/getActions', params);
          this.originalCustomTmplList = _.cloneDeep(res.data);
          this.handleActionLinearData();
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
       * fetchData
       */
      async fetchData (params) {
        try {
          const res = await this.$store.dispatch('permApply/getProvisionPolicies', { system_id: params.systemId });
          this.policyList = res.data.map(item => {
            // eslint-disable-next-line max-len
            item.related_environments = this.linearActionList.find(sub => sub.id === item.id).related_environments;
            item.related_actions = this.linearActionList.find(sub => sub.id === item.id).related_actions;
            return new PermPolicy(item);
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
          this.initRequestQueue.shift();
        }
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
          this.messageSuccess(this.$t(`m.info['删除成功']`), 2000);
          this.handleRefreshData();
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
          payload && payload.hide();
        }
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
        console.log('environmentsSidesliderData', this.environmentsSidesliderData);
        this.isShowEnvironmentsSideslider = true;
        this.environmentsSidesliderTitle = this.$t(`m.info['关联侧边栏操作生效条件']`, { value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}` });
      },

      /**
       * handlerReduceInstance
       */
      handlerReduceInstance (payload, data) {
        if (data.resource_groups.length < 2) return;
        this.deleteDialog.subTitle = `${this.$t(`m.dialog['将删除']`)}${this.$t(`m.perm['一组实例权限']`)}`;
        this.deleteDialog.visible = true;
        this.resourceGrouParams = {
          id: data.policy_id,
          resourceGroupId: payload.id
        };
      },

      /**
       * handleViewSidesliderCondition
       */
      handleViewSidesliderCondition () {
        this.isShowResourceInstanceEffectTime = true;
      },

      /**
       * handleDelete
       */
      handleDelete (payload) {
        this.curDeleteIds.splice(0, this.curDeleteIds.length, ...[payload.policy_id]);
        this.deleteDialog.subTitle = `${this.$t(`m.dialog['将删除']`)}${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}权限`;
        this.deleteDialog.visible = true;
      },

      /**
       * handleSumbitDelete
       */
      async handleSumbitDelete () {
        this.deleteDialog.loading = true;
        try {
          if (this.resourceGrouParams.id && this.resourceGrouParams.resourceGroupId) { // 表示删除的是资源组
            await this.$store.dispatch('permApply/deleteRosourceGroupPerm', this.resourceGrouParams);
            this.fetchData(this.params);
            this.messageSuccess(this.$t(`m.info['删除成功']`), 2000);
          } else {
            await this.$store.dispatch('permApply/deleteTemporaryPerm', {
              policyIds: this.curDeleteIds,
              systemId: this.systemId
            });
            const index = this.policyList.findIndex(item => item.policy_id === this.curDeleteIds[0]);
            if (index > -1) {
              this.policyList.splice(index, 1);
            }
            this.messageSuccess(this.$t(`m.info['删除成功']`), 2000);
            this.$emit('after-delete', this.policyList.length);
          }
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
          this.deleteDialog.loading = false;
          this.deleteDialog.visible = false;
        }
      },

      // 跳转到临时权限
      async handleToTemporaryCustomApply (data) {
        await this.getTemporaryCustomRelatedActions(data);
        this.$nextTick(() => {
          this.$router.push({
            name: 'applyProvisionPerm',
            params: { ids: this.applyAgiagnIds, temporaryTableData: this.TemporaryCustomTableData },
            query: {
              system_id: this.systemId
            }
          });
        });
      },
            
      // 获取相对关系
      getTemporaryCustomRelatedActions (data) {
        this.applyAgiagnIds = [data.id];
        const hash = {};
        const TemporaryCustomTableData = this.policyList.reduce((prev, item) => {
          if (data.related_actions.includes(item.id)) {
            // eslint-disable-next-line no-unused-expressions
            hash[item.id] ? '' : hash[item.id] = true && this.applyAgiagnIds.push(item.id)
              && prev.push({ id: item.id, resource_groups: item.resource_groups });
          }
          return prev;
        }, [{ id: data.id, resource_groups: data.resource_groups }]);
        this.TemporaryCustomTableData = [...TemporaryCustomTableData].map(e => {
          e.resource_groups.forEach(item => {
            console.log('item', item);
            item.id = '';
          });
          return e;
        });
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
        }

        .effect-conditon-side{
            .text{
                font-size: 14px;
                color: #63656e;
            }
        }
    }
</style>
