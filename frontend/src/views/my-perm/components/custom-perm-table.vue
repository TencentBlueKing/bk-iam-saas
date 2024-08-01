<template>
  <div class="custom-perm-table-wrapper" v-bkloading="{ isLoading: loading, opacity: 1 }">
    <bk-table
      v-if="!loading"
      :ref="`customPermRef_${mode}_${systemId}`"
      :key="tableKey"
      :data="policyList"
      :header-border="false"
      :outer-border="false"
      :class="[
        { 'is-hide-pagination': policyListBack.length < 10 }
      ]"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handleSelectionChange"
      @select-all="handleAllSelectionChange"
    >
      <bk-table-column
        type="selection"
        align="center"
        :selectable="row => !row.canNotTransfer"
      />
      <template v-if="tableColumnConfig.isShowSystem">
        <bk-table-column :label="$t(`m.set['系统名称']`)" fixed="left">
          <template slot-scope="{ row }">
            <span v-bk-tooltips="{ content: row.system_name }">{{ row.system_name }}</span>
          </template>
        </bk-table-column>
      </template>
      <bk-table-column
        :label="$t(`m.common['操作']`)"
        :min-width="200"
        :fixed="!tableColumnConfig.isShowSystem ? 'left' : ''"
      >
        <template slot-scope="{ row }">
          <span
            v-bk-tooltips="{
              content: row.name,
              placements: ['right-start']
            }"
          >
            {{ row.name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column
        :label="$t(`m.common['资源实例']`)"
        :min-width="150"
      >
        <template slot-scope="{ row }">
          <template v-if="!row.isEmpty">
            <div
              v-for="(_, _index) in row.resource_groups"
              :key="_.id"
              :class="[
                'related-resource-list',
                { 'related-resource-list-border':
                  row.resource_groups && row.resource_groups.length > 1 && _index === row.resource_groups.length - 1
                }
              ]"
            >
              <div
                class="flex-between related-resource-item"
                v-for="(related, relatedIndex) in _.related_resource_types"
                :key="related.type"
              >
                <template v-if="relatedIndex < 1">
                  <div class="instance-label">
                    <span>{{ $t(`m.common['配置模板']`) }}{{ $t(`m.common['：']`) }}</span>
                    <span class="instance-count" @click.stop="handleViewResource(row)">
                      {{ formatInstanceCount(related, _) || 0 }}
                    </span>
                  </div>
                </template>
              </div>
            </div>
          </template>
          <template v-else>
            <span class="condition-table-cell empty-text">{{ $t(`m.common['无需关联实例']`) }}</span>
          </template>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['生效条件']`)" :min-width="150">
        <template slot-scope="{ row }">
          <div class="condition-table-cell" v-if="!!row.related_environments.length">
            <div
              v-for="(_, groIndex) in row.resource_groups"
              :key="_.id"
              class="related-condition-list"
              :class="[
                row.resource_groups.length > 1
                  ? 'related-resource-list'
                  : 'environ-group-one',
                row.resource_groups === 1 || groIndex === row.resource_groups.length - 1
                  ? ''
                  : 'related-resource-list-border'
              ]"
            >
              <IamEffectCondition :value="_.environments" :is-empty="!_.environments.length" />
            </div>
          </div>
          <div v-else class="condition-table-cell empty-text">
            {{ $t(`m.common['无生效条件']`) }}
          </div>
        </template>
      </bk-table-column>
      <bk-table-column
        prop="expired_dis"
        :min-width="100"
        :label="$t(`m.common['有效期']`)"
      />
      <template v-if="tableColumnConfig.isShowTransferObject">
        <bk-table-column :label="$t(`m.permTransfer['交接对象']`)" width="300">
          <template slot-scope="{ row, $index }">
            <div class="transfer-object-column" v-if="row.handover_object && row.handover_object.length > 0">
              <Icon type="arrows-left" />
              <IamEditMemberSelector
                mode="detail"
                field="role_members"
                width="300"
                :value="formatRoleMembers(row.handover_object)"
                :index="$index"
              />
            </div>
            <span v-else>--</span>
          </template>
        </bk-table-column>
      </template>
      <template v-if="tableColumnConfig.isShowOperate">
        <bk-table-column :label="$t(`m.common['操作-table']`)" fixed="right" :width="formatOperate">
          <template slot-scope="{ row }">
            <div class="custom-perm-operate-column">
              <div class="custom-actions-item">
                <bk-popconfirm
                  trigger="click"
                  placement="bottom-end"
                  ext-popover-cls="iam-custom-popover-confirm delete-popover-wrapper"
                  :width="280"
                  @confirm="handleSubmitDelete"
                >
                  <div slot="content">
                    <div class="popover-title">
                      <div class="popover-title-text">
                        {{ delActionDialogTitle }}
                      </div>
                    </div>
                    <div class="popover-content">
                      <div class="popover-content-item">
                        <span class="popover-content-item-label">
                          {{ $t(`m.userOrOrg['操作对象']`) }}{{ $t(`m.common['：']`)}}
                        </span>
                        <span class="popover-content-item-value"> {{ user.name }}</span>
                      </div>
                      <div v-if="delActionList.length" class="delete-tips">
                        <p class="delete-tips-title">
                          {{ delActionDialogTip }}
                        </p>
                        <div class="delete-tips-content">
                          <p v-for="item in delActionList" :key="item.id">
                            <Icon bk type="info-circle-shape" class="warn" />
                            <span>{{ item.name }}</span>
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <bk-button type="primary" text @click="handleShowDelDialog(row)">
                    {{ $t(`m.userGroupDetail['删除操作权限']`) }}
                  </bk-button>
                </bk-popconfirm>
              </div>
              <div class="custom-actions-item" v-if="isShowPreview(row)">
                <bk-button type="primary" text @click="handleViewResource(row)">
                  {{ $t(`m.userGroupDetail['查看实例权限']`) }}
                </bk-button>
              </div>
              <div class="custom-actions-item" v-if="isShowRenewal(row)">
                <bk-button type="primary" text @click="handleOperate(row, 'renewal')">
                  {{ $t(`m.renewal['续期']`) }}
                </bk-button>
              </div>
              <div class="custom-actions-item" v-if="isShowHandover(row)">
                <bk-button type="primary" text @click="handleOperate(row, 'handover')">
                  {{ $t(`m.perm['交接']`) }}
                </bk-button>
              </div>
            </div>
          </template>
        </bk-table-column>
      </template>
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

    <bk-sideslider
      :is-show="isShowSideSlider"
      :title="sideSliderTitle"
      :width="960"
      quick-close
      @update:isShow="handleResourceCancel"
    >
      <div slot="header" class="iam-my-custom-perm-slider-header">
        <span>{{ sideSliderTitle }}</span>
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
              <div slot="title" class="popover-custom-title">
                {{ $t(`m.dialog['确认删除内容？']`, { value: $t(`m.dialog['删除实例权限']`) }) }}
              </div>
              <bk-button theme="primary" :disabled="disabled">
                {{ $t(`m.common['删除']`) }}
              </bk-button>
            </iam-popover-confirm>
            <bk-button style="margin-left: 8px" @click="handleCancelDelete">
              {{ $t(`m.common['取消']`) }}
            </bk-button>
          </template>
        </div>
      </div>
      <div slot="content">
        <RenderDetail
          ref="detailComRef"
          :data="previewData"
          :can-edit="!isBatchDelete"
          @tab-change="handleTabChange"
          @on-change="handleDetailChange"
          @on-select-all="handleSelectAll"
        />
      </div>
    </bk-sideslider>

    <DeleteActionDialog
      :show.sync="isShowDeleteDialog"
      :loading="deleteDialog.loading"
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
  import { cloneDeep, isEqual, uniqWith } from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { formatCodeData, getNowTimeExpired } from '@/common/util';
  import { leaveConfirm } from '@/common/leave-confirm';
  import PermPolicy from '@/model/my-perm-policy';
  import DeleteActionDialog from '@/views/group/components/delete-related-action-dialog.vue';
  import RenderDetail from '@/components/iam-render-detail';
  import IamPopoverConfirm from '@/components/iam-popover-confirm';
  import IamEffectCondition from '@/components/iam-effect-condition';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  export default {
    provide: function () {
      return {
        isCustom: () => this.isCustom
      };
    },
    components: {
      IamPopoverConfirm,
      IamEffectCondition,
      IamEditMemberSelector,
      RenderDetail,
      DeleteActionDialog
    },
    props: {
      mode: {
        type: String
      },
      systemId: {
        type: String,
        default: ''
      },
      systemName: {
        type: String,
        default: ''
      },
      isSearchPerm: {
        type: Boolean,
        default: false
      },
      groupData: {
        type: Object
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
      },
      pagination: {
        type: Object,
        default: () => {
          return {
            current: 1,
            limit: 10,
            count: 0
          };
        }
      },
      curPermData: {
        type: Object
      },
      tableColumnConfig: {
        type: Object,
        default: () => {
          return {
            isShowSystem: false,
            isShowTransferObject: false,
            isShowOperate: true
          };
        }
      },
      selectedHandoverObject: {
        type: Array,
        default: () => []
      },
      curSelectedGroup: {
        type: Array,
        default: () => []
      },
      renewalCustomPerm: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        policyList: [],
        policyListBack: [],
        linearActionList: [],
        previewData: [],
        curDeleteIds: [],
        policyIdList: [],
        delActionList: [],
        curInstancePaths: [],
        currentSelectList: [],
        environmentsEffectData: [],
        systemActionList: [],
        initRequestQueue: ['permTable'],
        curId: '',
        curPolicyId: '',
        sideSliderTitle: '',
        currentActionName: '',
        currentInstanceGroupName: '',
        delActionDialogTitle: '',
        delActionDialogTip: '',
        tableKey: -1,
        environmentsSliderTitle: this.$t(`m.common['生效条件']`),
        batchDisabled: false,
        disabled: true,
        canOperate: true,
        isCustom: true,
        isBatchDelete: true,
        isShowDeleteDialog: false,
        isShowSideSlider: false,
        isShowEffectConditionSlider: false,
        isShowResourceInstanceEffectTime: false,
        params: {},
        searchParams: {},
        customPermData: {},
        deleteDialog: {
          visible: false,
          title: this.$t(`m.dialog['确认删除']`),
          subTitle: '',
          loading: false
        },
        resourceGroupParams: {},
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
      },
      isShowRenewal () {
        return (payload) => {
          const result = this.renewalCustomPerm.some((v) => v.id === payload.policy_id);
          return result;
        };
      },
      isShowHandover () {
        return (payload) => {
          return payload.expired_at >= getNowTimeExpired();
        };
      },
      formatRoleMembers () {
        return (payload) => {
          if (payload && payload.length) {
            const hasName = payload.some((v) => v.username);
            if (!hasName) {
              payload = payload.map(v => {
                return {
                  username: v,
                  readonly: false
                };
              });
            }
            return payload;
          }
          return payload || [];
        };
      },
      formatInstanceCount () {
        return (payload, related) => {
          let curPaths = [];
          if (related.related_resource_types && related.related_resource_types.length > 1) {
            const list = related.related_resource_types.map((v) => {
              if (v.condition.length) {
                const { instance, instances } = v.condition[0];
                const list = instance || instances;
                curPaths = list.reduce((prev, next) => {
                  prev.push(
                    ...next.path.map(v => {
                      const paths = { ...v, ...next };
                      delete paths.instance;
                      delete paths.path;
                      return paths[0];
                    })
                  );
                  return prev;
                }, []);
                return curPaths.length;
              }
            });
            const count = list.reduce((prev, next) => prev + next, 0);
            return count;
          } else {
            if (payload.condition.length) {
              const { instance, instances } = payload.condition[0];
              const list = instance || instances || [];
              curPaths = list.reduce((prev, next) => {
                prev.push(
                  ...next.path.map(v => {
                    const paths = { ...v, ...next };
                    delete paths.instance;
                    delete paths.path;
                    return paths[0];
                  })
                );
                return prev;
              }, []);
              return curPaths.length;
            }
          }
        };
      },
      formatOperate () {
        const isCN = ['zh-cn'].includes(window.CUR_LANGUAGE);
        return isCN ? 260 : 410;
      }
    },
    watch: {
      systemId: {
        async handler (value) {
          this.currentSelectList = [];
          this.initRequestQueue = [];
          this.policyList = [];
          this.policyListBack = [];
          if (value) {
            this.initRequestQueue = ['permTable'];
            await Promise.all([this.fetchActions(value), this.fetchPolicy({ systemId: value })]);
          }
        },
        immediate: true
      },
      emptyData: {
        handler (value) {
          if (!value.type) {
            this.policyEmptyData = Object.assign({}, value);
          }
        },
        immediate: true
      },
      curSearchParams: {
        handler (value) {
          this.searchParams = Object.assign({}, value);
        },
        immediate: true
      },
      curSelectedGroup: {
        handler (value) {
          this.currentSelectList = [...value];
        },
        deep: true
      },
      curPermData: {
        handler (value) {
          // 处理多系统操作合成一个表格
          this.handleGetPolicyData(value);
        },
        deep: true
      },
      selectedHandoverObject: {
        handler (value) {
          this.policyList.forEach((item) => {
            this.$set(item, 'handover_object', value);
          });
        },
        deep: true
      }
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-remove-perm-checkbox');
      });
      // 同步更新checkbox状态
      bus.$on('on-remove-perm-checkbox', (payload) => {
        this.$emit('on-select-perm', payload);
        this.$nextTick(() => {
          this.policyList.forEach((item) => {
            if (this.$refs[`customPermRef_${this.mode}_${this.systemId}`] && !payload.map((v) => v.id).includes(item.id)) {
              this.$refs[`customPermRef_${this.mode}_${this.systemId}`].toggleRowSelection(item, false);
            }
          });
        });
      });
    },
    methods: {
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
          const { data } = await this.$store.dispatch('permApply/getActions', params);
          const actionList = data || [];
          this.systemActionList = cloneDeep(actionList);
          this.handleActionLinearData();
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async fetchPolicy (params) {
        const { current, limit } = this.pagination;
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
          if (!queryParams.system_id) {
            return;
          }
          const { code, data } = await this.$store.dispatch(url, queryParams);
          let policyList = data || [];
          if (this.groupData && ['renewalPerm'].includes(this.groupData.value)) {
            const renewalCustomPerm = this.renewalCustomPerm.map((v) => `${v.policy.id}&${v.policy.name}`);
            policyList = (data || []).filter((v) => renewalCustomPerm.includes(`${v.id}&${v.name}`));
          }
          if (policyList.length) {
            const linearActionList = this.linearActionList.filter((item) =>
              policyList.map((v) => v.id).includes(item.id)
            );
            this.policyList = policyList.map((item) => {
              let relatedPolicyActions = [];
              const curAction = linearActionList.find((v) => v.id === item.id);
              // 处理多系统批量删除操作时，如果当前存在被关联操作，则同步删除依赖当前操作的数据
              const relatedData = linearActionList.filter((v) => v.related_actions.includes(item.id));
              if (relatedData.length) {
                const relatedIdList = relatedData.map((v) => v.id);
                relatedPolicyActions = (data || []).filter((v) => relatedIdList.includes(v.id));
              }
              if (curAction) {
                const { related_actions: relatedActions, related_environments: relatedEnvironments } = curAction;
                item.related_actions = relatedActions || [];
                item.related_environments = relatedEnvironments || [];
              }
              return {
                ...new PermPolicy(item),
                ...{
                  related_policy_actions: relatedPolicyActions,
                  system: {
                    id: this.systemId,
                    name: this.systemName
                  }
                }
              };
            });
          }
          this.policyListBack = cloneDeep(this.policyList);
          this.policyList = this.handleGetDataByPage(
            this.pagination.current,
            {
              list: this.policyListBack,
              pagination: this.pagination
            }
          );
          this.policyEmptyData = formatCodeData(code, this.policyEmptyData, data.length === 0);
        } catch (e) {
          this.policyEmptyData = formatCodeData(e.code, this.policyEmptyData);
          this.messageAdvancedError(e);
        } finally {
          this.initRequestQueue.shift();
          this.$emit('on-change-policy-perm', {
            current,
            limit,
            count: this.policyListBack.length
          });
        }
      },
  
      fetchSelectedGroups (type, payload, row) {
        const selectList = uniqWith([...this.currentSelectList, ...this.curSelectedGroup], isEqual);
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              selectList.push(row);
              this.currentSelectList = [...selectList];
            } else {
              this.currentSelectList = selectList.filter((item) => `${item.name}&${item.id}&${item.mode_type}` !== `${row.name}&${row.id}&${row.mode_type}`);
            }
            this.fetchCustomTotal(this.currentSelectList);
            this.$emit('on-select-perm', this.currentSelectList);
          },
          all: () => {
            const tableList = this.policyList.map((v) => `${v.name}&${v.id}&${this.mode}`);
            const selectGroups = selectList.filter((item) => !tableList.includes(`${item.name}&${item.id}&${item.mode_type}`));
            this.currentSelectList = [...selectGroups, ...payload];
            this.fetchCustomTotal(this.currentSelectList);
            this.$emit('on-select-perm', this.currentSelectList);
          }
        };
        return typeMap[type]();
      },
      
      fetchCustomTotal (payload) {
        this.$nextTick(() => {
          const permRef = this.$refs[`customPermRef_${this.mode}_${this.systemId}`];
          if (permRef && permRef.$refs && permRef.$refs.paginationWrapper) {
            const paginationWrapper = permRef.$refs.paginationWrapper;
            const selectCount = paginationWrapper.getElementsByClassName('bk-page-selection-count');
            if (selectCount.length && selectCount[0].children && selectCount[0].children.length) {
              // 查找当前系统下的操作
              if (['permTransfer'].includes(this.$route.name)) {
                selectCount[0].children[0].innerHTML = payload.length;
              } else {
                const actionsLen = payload.filter((v) => `${v.mode_type}&${v.system_id}` === `${this.mode}&${this.systemId}`).length;
                selectCount[0].children[0].innerHTML = actionsLen;
              }
            }
          }
        });
      },

      handleSelectionChange (selection, row) {
        row = Object.assign(row, {
          mode_type: this.mode,
          system_id: row.system_id || this.systemId,
          system: {
            id: row.system_id,
            name: row.system_name || ''
          }
        });
        this.fetchSelectedGroups('multiple', selection, row);
      },
      
      handleAllSelectionChange (selection) {
        if (selection.length > 0) {
          selection = selection.map((v) => {
            return {
              ...v,
              ...{
                mode_type: this.mode,
                system_id: v.system_id || this.systemId,
                system: {
                  id: v.system_id || this.systemId,
                  name: v.system_name || ''
                }
              }
            };
          });
        }
        this.fetchSelectedGroups('all', selection);
      },

      handleOperate (payload, type) {
        const list = [];
        const typeMap = {
          renewal: () => {
            list.push({
              ...payload,
              ...{
                mode_type: this.mode
              }
            });
            const selectGroup = list.map((item) => {
              if (['customPerm', 'renewalCustomPerm'].includes(item.mode_type)) {
                this.$set(item, 'policy', { policy_id: item.policy_id, name: item.name });
              }
              return item;
            });
            this.$store.commit('perm/updateRenewalData', selectGroup);
            this.$router.push({
              name: 'permRenewal'
            });
          },
          handover: () => {
            list.push({
              ...payload,
              ...{
                mode_type: this.mode
              }
            });
            this.$store.commit('perm/updateHandoverData', list);
            this.$router.push({
              name: 'permTransfer'
            });
          }
        };
        return typeMap[type]();
      },

      handleGetDataByPage (page, payload) {
        if (!page) {
          payload.pagination.current = page = 1;
        }
        let startIndex = (page - 1) * payload.pagination.limit;
        let endIndex = page * payload.pagination.limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > payload.list.length) {
          endIndex = payload.list.length;
        }
        return payload.list.slice(startIndex, endIndex);
      },

      handlePageChange (page) {
        this.$emit('on-page-change', page);
        const pagination = Object.assign(this.pagination, { current: page });
        this.policyList = this.handleGetDataByPage(
          page,
          {
            list: this.policyListBack,
            pagination
          }
        );
        // 切换分页时自动勾选已选的数据
        this.handleGetSelectedPerm();
      },
  
      handleLimitChange (limit) {
        this.$emit('on-limit-change', limit);
        const pagination = Object.assign(this.pagination, { current: 1, limit });
        this.policyList = this.handleGetDataByPage(
          1,
          {
            list: this.policyListBack,
            pagination
          }
        );
        this.handleGetSelectedPerm();
      },

      handleGetSelectedPerm () {
        const selectList = uniqWith([...this.currentSelectList, ...this.curSelectedGroup], isEqual);
        const policyData = selectList.map((v) => `${v.name}&${v.id}`);
        this.$nextTick(() => {
          const permRef = this.$refs[`customPermRef_${this.mode}_${this.systemId}`];
          if (permRef) {
            this.policyList.forEach((item) => {
              const curPolicy = `${item.name}&${item.policy ? item.policy.policy_id : item.id}`;
              this.$set(item, 'handover_object', this.selectedHandoverObject);
              permRef.toggleRowSelection(item, policyData.includes(curPolicy));
            });
          }
        });
        this.fetchCustomTotal(selectList);
      },

      handleActionLinearData () {
        const linearActions = [];
        this.systemActionList.forEach((item) => {
          item.actions = item.actions.filter((v) => !v.hidden);
          item.actions.forEach((act) => {
            linearActions.push(act);
          });
          (item.sub_groups || []).forEach((sub) => {
            sub.actions = sub.actions.filter((v) => !v.hidden);
            sub.actions.forEach((act) => {
              linearActions.push(act);
            });
          });
        });
        this.linearActionList = cloneDeep(linearActions);
      },

      handleRefreshData () {
        this.initRequestQueue = ['permTable'];
        const params = {
          systemId: this.systemId
        };
        this.fetchPolicy(params);
      },

      handleBatchDelete () {
        window.changeAlert = true;
        this.isBatchDelete = false;
      },

      handleTabChange (payload) {
        const { disabled, canDelete } = payload;
        this.batchDisabled = disabled;
        this.canOperate = canDelete;
      },

      handleDetailChange () {
        const data = this.$refs.detailComRef.handleGetValue();
        this.disabled = data.ids.length < 1 && data.condition.length < 1;
        if (!this.disabled) {
          this.handleDeleteActionOrInstance(
            Object.assign(data, { id: this.curId, policy_id: this.curPolicyId }),
            'instance'
          );
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
          this.isShowSideSlider = false;
          this.resetDataAfterClose();
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          this.handleRefreshData();
          this.handleGetSelectedPerm();
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          payload && payload.hide();
        }
      },

      async handleSubmitDelete () {
        this.deleteDialog.loading = true;
        try {
          if (this.resourceGroupParams.id && this.resourceGroupParams.resourceGroupId) {
            // 表示删除的是资源组
            for (let i = 0; i < this.policyIdList.length; i++) {
              await this.$store.dispatch('permApply/deleteResourceGroupPerm', {
                id: this.policyIdList[i],
                resourceGroupId: this.resourceGroupParams.resourceGroupId
              });
            }
            this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
            this.fetchPolicy({ systemId: this.systemId });
          } else {
            await this.$store.dispatch('permApply/deletePerm', {
              policyIds: this.curDeleteIds,
              systemId: this.systemId
            });
            const deletePolicyList = this.policyListBack.filter((item) => this.curDeleteIds.includes(item.policy_id));
            const policyList = this.policyListBack.filter((item) => !this.curDeleteIds.includes(item.policy_id));
            this.currentSelectList = this.currentSelectList.filter(
              (item) => !this.curDeleteIds.includes(item.policy_id)
            );
            await this.fetchActions(this.systemId);
            await this.fetchPolicy({ systemId: this.systemId });
            this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
            this.$emit('on-select-perm', this.currentSelectList);
            this.$emit('on-delete-action', policyList.length);
            // 处理删除续期数据同步更新其他选项的数量
            if (['renewalCustomPerm'].includes(this.mode)) {
              const list = deletePolicyList.map((v) => {
                return {
                    ...v,
                    mode_type: 'renewalCustomPerm'
                };
              });
              bus.$emit('on-update-renewal-perm', {
                list
              });
            }
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.deleteDialog.loading = false;
          this.handleGetSelectedPerm();
        }
      },
      
      handleShowDelDialog (payload) {
        this.handleDeleteActionOrInstance(payload, 'action');
      },

      // 区分删除操作还是实例
      handleDeleteActionOrInstance (payload, type) {
        const { id, name, condition } = payload;
        let delRelatedActions = [];
        this.delActionList = [];
        const policyIdList = this.policyListBack.map((v) => v.id);
        const linearActionList = this.linearActionList.filter((item) =>
          policyIdList.includes(item.id)
        );
        const curAction = linearActionList.find((item) => item.id === id);
        const hasRelatedActions
          = curAction && curAction.related_actions && curAction.related_actions.length > 0;
        linearActionList.forEach((item) => {
          // 如果这里过滤自己还能在其他数据找到相同的related_actions，就代表有其他数据也关联了相同的操作
          if (
            hasRelatedActions
            && item.related_actions
            && item.related_actions.length > 0
            && item.id !== id
          ) {
            delRelatedActions = item.related_actions.filter((v) => curAction.related_actions.includes(v));
          }
          if (item.related_actions && item.related_actions.includes(id)) {
            this.delActionList.push(item);
          }
        });
        let policyIds = [payload.policy_id];
        if (this.delActionList.length) {
          const list = this.policyList.filter((item) =>
            this.delActionList.map((action) => action.id).includes(item.id)
          );
          policyIds = [payload.policy_id].concat(list.map((v) => v.policy_id));
        }
        this.policyIdList = cloneDeep(policyIds);
        const typeMap = {
          action: () => {
            this.currentActionName = name;
            if (!delRelatedActions.length && hasRelatedActions) {
              const list = [...this.policyList].filter((v) =>
                curAction.related_actions.includes(v.id)
              );
              if (list.length) {
                policyIds = policyIds.concat(list.map((v) => v.policy_id));
              }
            }
            this.curDeleteIds.splice(0, this.curDeleteIds.length, ...policyIds);
            this.policyIdList = cloneDeep(this.curDeleteIds);
            this.delActionDialogTitle = this.$t(`m.dialog['确认删除内容？']`, {
              value: this.$t(`m.dialog['删除操作权限']`)
            });
            this.delActionDialogTip = this.$t(`m.info['删除依赖操作产生的影响']`, {
              value: this.currentActionName
            });
          },
          instance: () => {
            let curPaths = [];
            if (condition.length) {
              curPaths = condition.reduce((prev, next) => {
                prev.push(
                  ...next.instances.map((v) => {
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
            this.policyIdList = cloneDeep(policyIds);
            this.delActionDialogTitle = this.$t(`m.dialog['确认删除内容？']`, {
              value: this.$t(`m.dialog['删除一组实例权限']`)
            });
            this.delActionDialogTip = this.$t(`m.info['删除组依赖实例产生的影响']`, {
              value: this.currentActionName
            });
          }
        };
        return typeMap[type]();
      },

      handleResourceCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(
          () => {
            this.isShowSideSlider = false;
            this.isShowEffectConditionSlider = false;
            this.resetDataAfterClose();
          },
          (_) => _
        );
      },

      handleViewResource (payload) {
        const params = [];
        this.curId = payload.id;
        this.curPolicyId = payload.policy_id;
        if (payload.resource_groups.length > 0) {
          payload.resource_groups.forEach((groupItem) => {
            if (groupItem.related_resource_types.length > 0) {
              groupItem.related_resource_types.forEach((sub) => {
                const { name, type, condition } = sub;
                params.push({
                  name: type,
                  tabType: 'resource',
                  label: this.$t(`m.info['tab操作实例']`, { value: name }),
                  data: condition,
                  systemId: sub.system_id,
                  resource_group_id: groupItem.id
                });
              });
            }
          });
        }
        this.previewData = cloneDeep(params);
        if (this.previewData[0].tabType === 'relate') {
          this.canOperate = false;
        }
        if (this.previewData.length) {
          if (this.previewData[0].tabType === 'relate') {
            this.canOperate = false;
          }
          const noInstance = this.previewData[0].data.every((item) => !item.instance || item.instance.length < 1);
          if (this.previewData[0].tabType === 'resource' && (this.previewData[0].data.length < 1 || noInstance)) {
            this.batchDisabled = true;
          }
        }
        this.sideSliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, {
          value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}`
        });
        window.changeAlert = 'iamSidesider';
        this.isShowSideSlider = true;
      },

      handlerReduceInstance (payload, data) {
        if (data.resource_groups.length >= 2) {
          const { id, related_resource_types: relatedResourceTypes } = payload;
          this.resourceGroupParams = {
            id: data.policy_id,
            resourceGroupId: id
          };
          if (relatedResourceTypes && relatedResourceTypes.length) {
            this.currentActionName = relatedResourceTypes.map((item) => item.name).join();
          }
          this.handleDeleteActionOrInstance(data, 'groupInstance');
        }
      },

      handleGetPolicyData (payload) {
        const { policyList, pagination } = payload;
        this.pagination.count = policyList.length || 0;
        this.policyListBack = [...policyList || []];
        this.policyList = this.handleGetDataByPage(
          this.pagination.current,
          {
            list: this.policyListBack,
            pagination
          }
        );
        this.handleGetSelectedPerm();
      },

      handleViewEffectCondition () {
        this.isShowResourceInstanceEffectTime = true;
      },

      handleAfterDeleteLeave () {
        this.deleteDialog.subTitle = '';
        this.curDeleteIds = [];
      },
      
      handleAfterDeleteLeaveAction () {
        this.currentActionName = '';
        this.delActionList = [];
        this.curDeleteIds = [];
        this.policyIdList = [];
        this.resourceGroupParams = {};
      },

      handleCancelDelete () {
        this.deleteDialog.visible = false;
        this.isShowDeleteDialog = false;
        this.isBatchDelete = true;
        this.curDeleteIds = [];
      },

      resetDataAfterClose () {
        this.sideSliderTitle = '';
        this.previewData = [];
        this.canOperate = true;
        this.batchDisabled = false;
        this.disabled = true;
        this.isBatchDelete = true;
        this.curId = '';
        this.curPolicyId = '';
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import '@/css/mixins/custom-popover-confirm.css';
@import '../common/css/custom-perm-table.css';
/deep/ .transfer-object-column {
  display: flex;
  align-items: center;
  .iamcenter-arrows-left {
    color: #ff9c01;
    font-size: 16px;
    margin-right: 5px;
    transform: rotate(180deg);
  }
  .iam-edit-selector {
    width: 100%;
    .edit-content {
      max-width: 100%;
      .member-item {
        background-color: #f0f5ff;
        color: #3a84ff;
      }
    }
  }
}
</style>
