<template>
  <div class="iam-perm-table" v-bkloading="{ isLoading: loading, opacity: 1 }">
    <bk-table
      v-if="!loading"
      :data="tableList"
      border
      :cell-class-name="getCellClass">
      <bk-table-column :label="$t(`m.common['操作']`)">
        <template slot-scope="{ row }">
          <span :title="row.name">{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" width="491">
        <template slot-scope="{ row }">
          <template v-if="!row.isEmpty">
            <div v-for="_ in row.resource_groups" :key="_.id">
              <p class="related-resource-item"
                v-for="item in _.related_resource_types"
                :key="item.type">
                <render-resource-popover
                  :key="item.type"
                  :data="item.condition"
                  :value="`${item.name}：${item.value}`"
                  :max-width="380"
                  @on-view="handleViewResource(row)" />
              </p>
            </div>
          </template>
          <template v-else>
            {{ $t(`m.common['无需关联实例']`) }}
          </template>
          <Icon
            type="detail-new"
            class="view-icon"
            :title="$t(`m.common['详情']`)"
            v-if="isShowPreview(row)"
            @click.stop="handleViewResource(row)" />
        </template>
      </bk-table-column>
      <bk-table-column prop="expired_dis" :label="$t(`m.common['有效期']`)"></bk-table-column>
      <!-- <bk-table-column :label="$t(`m.common['操作']`)">
        <template slot-scope="{ row }">
          <bk-button text @click="handleDelete(row)">{{ $t(`m.common['删除']`) }}</bk-button>
        </template>
      </bk-table-column> -->
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
      @on-sumbit="handleSubmitDelete" />

    <!-- <bk-sideslider
            :is-show.sync="isShowSideslider"
            :title="sidesliderTitle"
            :width="725"
            :quick-close="true"
            @animation-end="handleAnimationEnd">
            <div slot="content">
                <component :is="renderDetailCom" :data="previewData" />
            </div>
        </bk-sideslider> -->

    <bk-sideslider
      :is-show.sync="isShowSideslider"
      :title="sidesliderTitle"
      :width="960"
      :quick-close="true"
      @animation-end="handleAnimationEnd">
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
            <bk-button
              theme="primary"
              :loading="deleteLoading"
              :disabled="disabled"
              @click="handleDeletePerm">
              {{ $t(`m.common['删除']`) }}
            </bk-button>
            <bk-button style="margin-left: 10px;" @click="handleCancel">
              {{ $t(`m.common['取消']`) }}
            </bk-button>
          </template>
        </div>
      </div>
      <div slot="content">
        <component
          :is="renderDetailCom"
          :data="previewData"
          :can-edit="!isBatchDelete"
          ref="detailComRef"
          @tab-change="handleTabChange"
          @on-change="handleChange" />
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
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import DeleteDialog from '@/components/iam-confirm-dialog/index.vue';
  import RenderDetail from '../../perm/components/render-detail-edit';
  import PermPolicy from '@/model/my-perm-policy';
  import DeleteActionDialog from '@/views/group/components/delete-related-action-dialog.vue';
  import { formatCodeData } from '@/common/util';
  import { mapGetters } from 'vuex';

  export default {
    name: '',
    components: {
      RenderDetail,
      RenderResourcePopover,
      DeleteDialog,
      DeleteActionDialog
    },
    props: {
      systemId: {
        type: String,
        default: ''
      },
      params: {
        type: Object,
        default: () => {
          return {};
        }
      },
      data: {
        type: Object,
        default: () => {
          return {};
        }
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
      }
    },
    data () {
      return {
        tableList: [],
        policyCountMap: {},
        initRequestQueue: ['permTable'],
        previewData: [],
        curId: '',
        curPolicyId: '',
        renderDetailCom: 'RenderDetail',
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
        deleteLoading: false,
        disabled: true,
        canOperate: true,
        isShowDeleteDialog: false,
        currentActionName: '',
        currentInstanceGroupName: '',
        delActionDialogTitle: '',
        delActionDialogTip: '',
        delActionList: [],
        curInstancePaths: [],
        policyIdList: [],
        originalCustomTmplList: [],
        linearActionList: [],
        policyEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
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
      }
    },
    watch: {
      systemId: {
        async handler (value) {
          if (value !== '') {
            this.initRequestQueue = ['permTable'];
            const params = {
              subjectType: 'user',
              subjectId: this.params.username,
              systemId: value
            };
            await this.fetchActions(value);
            this.fetchData(params);
          } else {
            this.renderDetailCom = 'RenderDetail';
            this.initRequestQueue = [];
            this.tableList = [];
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
      }
    },
    methods: {
      /**
       * fetchData
       */
      async fetchData (params) {
        try {
          const { code, data } = await this.$store.dispatch('perm/getPersonalPolicy', { ...params });
          this.tableList = data && data.map(item => new PermPolicy(item));
          this.policyEmptyData = formatCodeData(code, this.policyEmptyData, data.length === 0);
        } catch (e) {
          console.error(e);
          this.policyEmptyData = formatCodeData(e.code, this.policyEmptyData);
          this.messageAdvancedError(e);
        } finally {
          this.initRequestQueue.shift();
        }
      },

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
        if (this.externalSystemId) {
          params.system_id = this.externalSystemId;
        }
        try {
          const { data } = await this.$store.dispatch('permApply/getActions', params);
          this.originalCustomTmplList = _.cloneDeep(data || []);
          this.handleActionLinearData();
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
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
        if (columnIndex === 1) {
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
          subjectType: 'user',
          subjectId: this.params.username,
          systemId: this.systemId
        };
        this.fetchData(params);
      },

      /**
       * handleBatchDelete
       */
      handleBatchDelete () {
        this.isBatchDelete = false;
      },

      /**
       * handleCancel
       */
      handleCancel () {
        this.isBatchDelete = true;
      },

      /**
       * handleDeletePerm
       */
      async handleDeletePerm () {
        const data = this.$refs.detailComRef.handleGetValue();
        const { ids, condition, type, resource_group_id } = data;
        const params = {
          subjectType: this.data.type === 'user' ? this.data.type : 'department',
          subjectId: this.data.type === 'user' ? this.data.username : this.data.id,
          id: this.curPolicyId,
          data: {
            system_id: data.system_id,
            type: type,
            ids,
            condition,
            resource_group_id
          }
        };
        this.deleteLoading = true;
        try {
          await this.$store.dispatch('permApply/updateSubjectPerm', params);
          this.isShowSideslider = false;
          this.handleAnimationEnd();
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          this.handleRefreshData();
          // this.$emit('after-resource-delete')
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.deleteLoading = false;
        }
      },

      /**
       * handleTabChange
       */
      handleTabChange (payload) {
        const { disabled, canDelete } = payload;
        this.batchDisabled = disabled;
        this.canOperate = canDelete;
      },

      /**
       * handleChange
       */
      handleChange () {
        const data = this.$refs.detailComRef.handleGetValue();
        this.disabled = data.ids.length < 1 && data.condition.length < 1;
      },

      /**
       * handleAnimationEnd
       */
      handleAnimationEnd () {
        this.sidesliderTitle = '';
        this.previewData = [];
        this.curId = '';

        this.canOperate = true;
        this.batchDisabled = false;
        this.disabled = true;
        this.isBatchDelete = true;
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
      handleViewResource (payload) {
        this.curId = payload.id;
        this.curPolicyId = payload.policy_id;
        const params = [];
        if (payload.resource_groups.length > 0) {
          payload.resource_groups.forEach(groupItem => {
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
          });
        }
        this.previewData = _.cloneDeep(params);
        this.sidesliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        // this.sidesliderTitle = `${this.$t(`m.common['操作']`)}${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的资源实例']`)}`;
        this.isShowSideslider = true;
      },

      handleShowDelDialog (payload) {
        this.handleDeleteActionOrInstance(payload, 'action');
      },

      /**
       * handleDelete
       */
      // handleDelete (payload) {
      //   this.curDeleteIds.splice(0, this.curDeleteIds.length, ...[payload.policy_id]);
      //   this.deleteDialog.subTitle = `${this.$t(`m.dialog['将删除']`)}${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的权限']`)}`;
      //   this.deleteDialog.visible = true;
      // },

      /**
       * handleSubmitDelete
       */
      async handleSubmitDelete () {
        this.deleteDialog.loading = true;
        const { type } = this.data;
        try {
          const params = {
            systemId: this.systemId,
            subjectType: type === 'user' ? type : 'department',
            subjectId: type === 'user' ? this.data.username : this.data.id
          };
          await this.$store.dispatch('permApply/deleteSubjectPerm', {
            ...params,
            ...{
              policyIds: this.curDeleteIds
            }
          });
          const index = this.tableList.findIndex(item => item.policy_id === this.curDeleteIds[0]);
          if (index > -1) {
            this.tableList.splice(index, 1);
          }
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          await this.fetchData(params);
          this.$emit('after-delete', this.tableList.length);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.deleteDialog.loading = false;
          this.deleteDialog.visible = false;
          this.isShowDeleteDialog = false;
        }
      },

      // 区分删除操作还是实例
      handleDeleteActionOrInstance (payload, type) {
        const { id, name, condition } = payload;
        let delRelatedActions = [];
        this.delActionList = [];
        const policyIdList = this.tableList.map(v => v.id);
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
          const list = this.tableList.filter(
            item => this.delActionList.map(action => action.id).includes(item.id));
          policyIds = [payload.policy_id].concat(list.map(v => v.policy_id));
        }
        this.policyIdList = _.cloneDeep(policyIds);
        const typeMap = {
          action: () => {
            this.currentActionName = name;
            if (!delRelatedActions.length && hasRelatedActions) {
              const list = [...this.tableList].filter(v => curAction.related_actions.includes(v.id));
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
          }
        };
        typeMap[type]();
      },

      handleCancelDelete () {
        this.isShowDeleteDialog = false;
        this.curDeleteIds = [];
      },

      handleAfterDeleteLeaveAction () {
        this.currentActionName = '';
        this.delActionList = [];
        this.curDeleteIds = [];
        this.policyIdList = [];
        this.resourceGroupParams = {};
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-perm-table {
        min-height: 101px;
        .bk-table-enable-row-hover .bk-table-body tr:hover > td {
            background-color: #fff;
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
                    .view-icon {
                        display: none;
                        position: absolute;
                        top: 50%;
                        right: 10px;
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
    }
</style>
