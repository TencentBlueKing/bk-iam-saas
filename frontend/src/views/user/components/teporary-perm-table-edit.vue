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
      <bk-table-column :label="$t(`m.common['操作']`)">
        <template slot-scope="{ row }">
          <bk-button text @click="handleDelete(row)">{{ $t(`m.common['删除']`) }}</bk-button>
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
  </div>
</template>
<script>
  import _ from 'lodash';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import DeleteDialog from '@/components/iam-confirm-dialog/index.vue';
  import RenderDetail from '../../perm/components/render-detail-edit';
  import PermPolicy from '@/model/my-perm-policy';

  export default {
    name: '',
    components: {
      RenderDetail,
      RenderResourcePopover,
      DeleteDialog
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
        canOperate: false
      };
    },
    computed: {
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
        handler (value) {
          if (value !== '') {
            this.initRequestQueue = ['permTable'];
            const params = {
              subjectType: 'user',
              subjectId: this.params.username,
              systemId: value
            };
            this.fetchData(params);
          } else {
            this.renderDetailCom = 'RenderDetail';
            this.initRequestQueue = [];
            this.tableList = [];
            this.policyCountMap = {};
          }
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
          const res = await this.$store.dispatch('perm/getTeporaryPersonalPolicy', { ...params });
          this.tableList = res.data.map(item => new PermPolicy(item));
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
          this.messageSuccess(this.$t(`m.info['删除成功']`), 2000);
          this.handleRefreshData();
          // this.$emit('after-resource-delete')
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

        this.canOperate = false;
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
        this.isShowSideslider = true;
      },

      /**
       * handleDelete
       */
      handleDelete (payload) {
        this.curDeleteIds.splice(0, this.curDeleteIds.length, ...[payload.policy_id]);
        this.deleteDialog.subTitle = `${this.$t(`m.dialog['将删除']`)}${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的权限']`)}`;
        this.deleteDialog.visible = true;
      },

      /**
       * handleSumbitDelete
       */
      async handleSumbitDelete () {
        this.deleteDialog.loading = true;
        const { type } = this.data;
        try {
          await this.$store.dispatch('permApply/deleteTemporarySubjectPerm', {
            policyIds: this.curDeleteIds,
            systemId: this.systemId,
            subjectType: type === 'user' ? type : 'department',
            subjectId: type === 'user' ? this.data.username : this.data.id
          });
          const index = this.tableList.findIndex(item => item.policy_id === this.curDeleteIds[0]);
          if (index > -1) {
            this.tableList.splice(index, 1);
          }
          this.messageSuccess(this.$t(`m.info['删除成功']`), 2000);
          this.$emit('after-delete', this.tableList.length);
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
