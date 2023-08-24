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

    <bk-sideslider
      :is-show.sync="isShowSideslider"
      :title="sidesliderTitle"
      :width="960"
      :quick-close="true"
      @animation-end="handleAnimationEnd">
      <div slot="content">
        <!-- style="padding: 0 30px 17px 30px;" -->
        <component :is="renderDetailCom" :data="previewData" />
      </div>
    </bk-sideslider>
  </div>
</template>
<script>
  import _ from 'lodash';
  import RenderDetail from './render-detail';
  import PermPolicy from '@/model/my-perm-policy';
  import DeleteDialog from '@/components/iam-confirm-dialog/index.vue';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  export default {
    name: '',
    components: {
      RenderDetail,
      DeleteDialog,
      RenderResourcePopover
    },
    props: {
      systemId: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        tableList: [],
        policyCountMap: {},
        initRequestQueue: ['permTable'],
        previewData: [],
        curId: '',
        renderDetailCom: 'RenderDetail',
        isShowSideslider: false,
        curDeleteIds: [],

        deleteDialog: {
          visible: false,
          title: this.$t(`m.dialog['确认删除']`),
          subTitle: '',
          loading: false
        },
        sidesliderTitle: ''
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
            this.fetchData(value);
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
      async fetchData (payload) {
        try {
          const res = await this.$store.dispatch('permApply/getPolicies', { system_id: payload });
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

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 1) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      handleAnimationEnd () {
        this.sidesliderTitle = '';
        this.previewData = [];
        this.actionTopologyData = [];
        this.curId = '';
      },

      handleAfterDeleteLeave () {
        this.deleteDialog.subTitle = '';
        this.curDeleteIds = [];
      },

      hideCancelDelete () {
        this.deleteDialog.visible = false;
      },

      handleViewResource (payload) {
        this.curId = payload.id;
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
                  data: condition
                });
              });
            }
          });
        }
        this.previewData = _.cloneDeep(params);
        this.sidesliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        this.isShowSideslider = true;
      },

      handleDelete (payload) {
        this.curDeleteIds.splice(0, this.curDeleteIds.length, ...[payload.policy_id]);
        this.deleteDialog.subTitle = `${this.$t(`m.dialog['将删除']`)}${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['权限']`)}`;
        this.deleteDialog.visible = true;
      },

      async handleSumbitDelete () {
        this.deleteDialog.loading = true;
        try {
          await this.$store.dispatch('permApply/deletePerm', { policyIds: this.curDeleteIds, systemId: this.systemId });
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
    }
</style>
