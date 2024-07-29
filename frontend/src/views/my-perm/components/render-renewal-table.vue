<template>
  <div class="iam-perm-renewal-table-wrapper" v-bkloading="{ isLoading: loading || isLoading, opacity: 1 }">
    <bk-table
      v-show="!loading"
      :data="tableList"
      size="small"
      ref="permTableRef"
      ext-cls="custom-perm-table-wrapper perm-renewal-table"
      :key="tableKey"
      :outer-border="false"
      :header-border="false"
      :max-height="500"
      :pagination="pagination"
      @page-change="pageChange"
      @page-limit-change="limitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      @filter-change="handleFilterChange"
    >
      <bk-table-column type="selection" align="center" :selectable="getIsSelect" />
      <template v-for="item in tableProps">
        <bk-table-column
          v-if="item.prop === 'system'"
          column-key="filterTag"
          :filters="systemFilter"
          :filter-method="systemFilterMethod"
          :filter-multiple="false"
          :key="item.prop"
          :label="item.label"
          :prop="item.prop">
          <template slot-scope="{ row }">
            <span
              v-bk-tooltips="{
                content: row.system && row.system.name ? row.system.name : '',
                disabled: !row.system || !row.system.name
              }"
            >
              {{ row.system ? row.system.name || '' : '' }}
            </span>
          </template>
        </bk-table-column>
        <template v-else-if="item.prop === 'name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <span
                class="renewal-user-group-name"
                v-bk-tooltips="{
                  content: row.name
                }"
                @click="handleViewDetail(row)"
              >
                {{ row.name || '--' }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'role.name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <span
                v-bk-tooltips="{
                  content: row.role && row.role.name ? row.role.name : '',
                  disabled: !row.role || !row.role.name
                }"
              >
                {{ row.role ? row.role.name : '--' }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'role_members'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :width="300">
            <template slot-scope="{ row, $index }">
              <template v-if="row.role_members && row.role_members.length">
                <iam-edit-member-selector
                  mode="detail"
                  field="members"
                  width="200"
                  :placeholder="$t(`m.verify['请输入']`)"
                  :value="formatRoleMembers(row.role_members)"
                  :index="$index"
                />
              </template>
              <template v-else>--</template>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'action'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <span>{{ row.action ? row.action.name || '' : '' }}</span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'policy'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
          >
            <template slot-scope="{ row }">
              <template v-if="row.policy && row.policy.resource_groups && row.policy.resource_groups.length > 0">
                <div
                  v-for="(_, _index) in row.policy.resource_groups"
                  :key="_.id"
                  :class="[
                    'related-resource-list',
                    { 'related-resource-list-border':
                      row.policy.resource_groups
                      && row.policy.resource_groups.length > 1
                      && _index === row.policy.resource_groups.length - 1
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
        </template>
        <template v-else-if="item.prop === 'effective_condition'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :min-width="150">
            <template slot-scope="{ row }">
              <div class="condition-table-cell" v-if="!!row.action.related_environments.length">
                <div
                  v-for="(_, groIndex) in row.policy.resource_groups"
                  :key="_.id"
                  class="related-condition-list"
                  :class="[
                    row.resource_groups.length > 1
                      ? 'related-resource-list'
                      : 'environ-group-one',
                    row.policy.resource_groups === 1 || groIndex === row.policy.resource_groups.length - 1
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
        </template>
        <template v-else-if="item.prop === 'operate'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <template v-if="['group'].includes(type)">
                <bk-button
                  v-if="row.department_id !== 0"
                  :disabled="true"
                  :text="true"
                >
                  <span :title="$t(`m.perm['通过组织加入的组无法退出']`)">
                    {{ $t(`m.common['退出']`) }}
                  </span>
                </bk-button>
                <bk-button
                  v-else
                  class="mr10"
                  theme="primary"
                  :text="true"
                  :title="isAdminGroup(row) ? $t(`m.perm['唯一管理员不可退出']`) : ''"
                  :disabled="isAdminGroup(row)"
                  @click="handleQuitRenewal(row)">
                  {{ $t(`m.common['退出']`) }}
                </bk-button>
              </template>
              <template v-if="['custom'].includes(type)">
                <bk-button
                  type="primary"
                  text
                  @click="handleShowDelDialog(row)">
                  {{ $t(`m.userGroupDetail['删除操作权限']`) }}
                </bk-button>
              </template>
            </template>
          </bk-table-column>
        </template>
        <template v-else>
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <render-expire-display
                v-if="item.prop === 'expired_at'"
                :selected="currentSelectList.map(v => v.id).includes(row.id)"
                :renewal-time="renewalTime"
                :cur-time="row.expired_at" />
              <span
                v-else
                v-bk-tooltips="{
                  content: row[item.prop],
                  disabled: !row[item.prop]
                }"
              >
                {{ row[item.prop] || '--'}}
              </span>
            </template>
          </bk-table-column>
        </template>
      </template>
      <template slot="empty">
        <ExceptionEmpty
          :type="emptyRenewalData.type"
          :empty-text="emptyRenewalData.text"
          :tip-text="emptyRenewalData.tip"
          :tip-type="emptyRenewalData.tipType"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
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

    <render-perm-side-slider
      :show="isShowPermSideSlider"
      :name="curGroupName"
      :group-id="curGroupId"
      :show-member="false"
      @animation-end="handleDetailAnimationEnd"
    />

    <delete-action-dialog
      :show.sync="isShowDeleteDialog"
      :title="delActionDialogTitle"
      :tip="delActionDialogTip"
      :name="currentActionName"
      :loading="batchQuitLoading"
      :related-action-list="delActionList"
      @on-after-leave="handleAfterDeleteLeaveAction"
      @on-submit="handleSubmitDelete"
      @on-cancel="handleCancelDelete"
    />
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { leaveConfirm } from '@/common/leave-confirm';
  import { formatCodeData, existValue } from '@/common/util';
  import RenderExpireDisplay from '@/components/render-renewal-dialog/display';
  import RenderDetail from '@/components/iam-render-detail';
  import RenderPermSideSlider from '@/views/my-perm/components/render-group-perm-side-slider';
  import IamPopoverConfirm from '@/components/iam-popover-confirm';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  import IamEffectCondition from '@/components/iam-effect-condition';
  import DeleteActionDialog from '@/views/group/components/delete-related-action-dialog.vue';

  // 过期时间的天数区间
  const EXPIRED_DISTRICT = 15;

  export default {
    name: '',
    components: {
      RenderExpireDisplay,
      RenderDetail,
      RenderPermSideSlider,
      IamPopoverConfirm,
      IamEditMemberSelector,
      IamEffectCondition,
      DeleteActionDialog
    },
    props: {
      type: {
        type: String,
        default: 'group'
      },
      renewalTime: {
        type: Number,
        default: 15552000
      },
      data: {
        type: Array,
        default: () => []
      },
      loading: {
        type: Boolean,
        default: false
      },
      count: {
        type: Number,
        default: () => 0
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
        allData: [],
        allDataBack: [],
        currentSelectList: [],
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        tableProps: [],
        systemFilter: [],
        emptyRenewalData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        isLoading: false,
        actionLoading: false,
        batchQuitLoading: false,
        isShowSideSlider: false,
        isShowPermSideSlider: false,
        isShowDeleteDialog: false,
        isBatchDelete: true,
        batchDisabled: false,
        disabled: true,
        canOperate: true,
        curId: '',
        curPolicyId: '',
        curOperate: '',
        delActionDialogTitle: '',
        delActionDialogTip: '',
        currentActionName: '',
        sideSliderTitle: '',
        curGroupName: '',
        curFilterSystem: '',
        tableKey: 0,
        curGroupId: -1,
        singleData: {},
        curCustomData: {},
        previewData: [],
        delActionList: [],
        policyIdList: [],
        originalCustomTmplList: [],
        curDeleteIds: [],
        curInstancePaths: [],
        linearActionList: [],
        sliderWidth: 960,
        renewalGroupCount: 0
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      isShowPreview () {
        return (payload) => {
          return payload.policy_id;
        };
      },
      isAdminGroup () {
        return (payload) => {
          if (payload) {
            const { attributes, role_members } = payload;
            if (attributes && attributes.source_from_role && role_members.length === 1) {
              return true;
            }
            return false;
          }
        };
      },
      isMultiple () {
        return !(Object.keys(this.singleData).length > 0);
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
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      },
      type: {
        handler (newValue, oldValue) {
          this.tableProps = this.getTableProps(newValue);
          if (oldValue && oldValue !== newValue) {
            this.curFilterSystem = '';
            this.pagination = Object.assign(this.pagination, {
              current: 1,
              limit: 10
            });
          }
        },
        immediate: true
      },
      currentSelectList: {
        handler (value) {
          const getTimestamp = payload => {
            if (this.renewalTime === PERMANENT_TIMESTAMP) {
              return this.renewalTime;
            }
            if (payload < this.user.timestamp) {
              return this.user.timestamp + this.renewalTime;
            }
            return payload + this.renewalTime;
          };
          const templateList = value.map(item => {
            return {
              ...item,
              expired_at: getTimestamp(item.expired_at)
            };
          });
          this.$emit('on-select', this.type, templateList);
        },
        immediate: true,
        deep: true
      },
      renewalTime (value) {
        const getTimestamp = payload => {
          if (value === PERMANENT_TIMESTAMP) {
            return value;
          }
          if (payload < this.user.timestamp) {
            return this.user.timestamp + value;
          }
          return payload + value;
        };
        const templateList = this.currentSelectList.map(item => {
          return {
            ...item,
            expired_at: getTimestamp(item.expired_at)
          };
        });
        this.$emit('on-select', this.type, templateList);
      },
      data: {
        handler (value) {
          this.allData = cloneDeep(value);
          this.allDataBack = cloneDeep(value);
          this.pagination = Object.assign(this.pagination, { count: this.count });
          this.$nextTick(() => {
            const tableItem = {
              group: () => {
                this.tableList.splice(0, this.tableList.length, ...value);
                this.currentSelectList = this.tableList.filter(item =>
                  this.getDays(item.expired_at) < EXPIRED_DISTRICT);
                this.tableList.forEach(item => {
                  if (this.currentSelectList.map(_ => _.id).includes(item.id)) {
                    this.$refs.permTableRef && this.$refs.permTableRef.toggleRowSelection(item, true);
                  }
                  this.fetchCustomSelection();
                });
              },
              custom: async () => {
                const result = await this.getCurPageData(this.pagination.current);
                this.tableList.splice(0, this.tableList.length, ...result);
                this.currentSelectList = this.allData.filter(item =>
                  this.getDays(item.expired_at) < EXPIRED_DISTRICT);
                this.allData.forEach(item => {
                  if (!this.systemFilter.find(subItem => subItem.value === item.system.id)) {
                    this.systemFilter.push({
                      text: item.system.name,
                      value: item.system.id
                    });
                  }
                  if (this.currentSelectList.map(_ => _.id).includes(item.id)) {
                    this.$refs.permTableRef && this.$refs.permTableRef.toggleRowSelection(item, true);
                  }
                  this.fetchCustomSelection();
                });
              }
            };
            return tableItem[this.type] ? tableItem[this.type]() : tableItem['group']();
          });
        },
        immediate: true
      },
      count: {
        handler (value) {
          this.pagination.count = value;
        },
        immediate: true
      },
      emptyData: {
        handler (value) {
          this.emptyRenewalData = value;
        },
        immediate: true
      }
    },
    methods: {
      getDays (payload) {
        const dif = payload - this.user.timestamp;
        if (dif < 1) {
          return 0;
        }
        return Math.ceil(dif / (24 * 3600));
      },

      getIsSelect () {
        return this.tableList.length > 0;
      },

      getTableProps (payload) {
        if (payload === 'group') {
          return [
            { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
            { label: this.$t(`m.common['描述']`), prop: 'description' },
            { label: this.$t(`m.grading['管理空间']`), prop: 'role.name' },
            { label: this.$t(`m.levelSpace['管理员']`), prop: 'role_members' },
            { label: this.$t(`m.common['有效期']`), prop: 'expired_at' }
            // { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
          ];
        }
        return [
          { label: this.$t(`m.common['系统名']`), prop: 'system' },
          { label: this.$t(`m.common['操作']`), prop: 'action' },
          { label: this.$t(`m.common['资源实例']`), prop: 'policy' },
          { label: this.$t(`m.common['生效条件']`), prop: 'effective_condition' },
          { label: this.$t(`m.common['有效期']`), prop: 'expired_at' }
          // { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
        ];
      },

      systemFilterMethod (value, row, column) {
        const property = column.property;
        this.curFilterSystem = value;
        if (row[property]) {
          return row[property].id === value;
        }
      },

      async handleFilterChange (payload) {
        const { filterTag } = payload;
        this.curFilterSystem = filterTag.length > 0 ? filterTag[0] : '';
        this.emptyRenewalData.tipType = 'search';
        await this.resetTableData();
        this.$emit('on-filter-system', { list: this.allData });
      },

      pageChange (page = 1) {
        this.pagination = Object.assign(
          this.pagination,
          {
            current: page
          }
        );
        this.fetchTableData();
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination = Object.assign(
          this.pagination,
          {
            current: 1,
            limit: currentLimit
          }
        );
        this.fetchTableData();
      },

      fetchCustomSelection () {
        this.$nextTick(() => {
          const selectionCount = document.getElementsByClassName('bk-page-selection-count');
          if (this.$refs.permTableRef && selectionCount && selectionCount.length && selectionCount[0].children) {
            const selectList = this.curFilterSystem && ['custom'].includes(this.type)
              ? this.currentSelectList.filter((item) => item.system.id === this.curFilterSystem)
              : cloneDeep(this.currentSelectList);
            selectionCount[0].children[0].innerHTML = selectList.length;
          }
        });
      },

      handlerAllChange (selection) {
        const tableList = this.type === 'custom' ? cloneDeep(this.allData) : cloneDeep(this.tableList);
        const selectGroups = this.currentSelectList.filter(item =>
          !tableList.map(v => v.id.toString()).includes(item.id.toString()));
        this.currentSelectList = [...selectGroups, ...selection];
        this.fetchCustomSelection();
      },

      handlerChange (selection, row) {
        const isChecked = selection.length && selection.indexOf(row) !== -1;
        if (isChecked) {
          this.currentSelectList.push(row);
        } else {
          this.currentSelectList = this.currentSelectList.filter(
            (item) => item.id.toString() !== row.id.toString()
          );
        }
        this.fetchCustomSelection();
      },

      handleViewDetail (payload) {
        this.curGroupName = payload.name;
        this.curGroupId = payload.id;
        this.isShowPermSideSlider = true;
      },

      handleResourceCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(
          () => {
            this.isShowSideSlider = false;
            this.resetDataAfterClose();
          },
          (_) => _
        );
      },

      handleViewResource (payload) {
        const { policy } = payload;
        const params = [];
        this.curId = policy.id;
        this.curPolicyId = policy.policy_id;
        if (policy.resource_groups.length > 0) {
          policy.resource_groups.forEach((groupItem) => {
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
          value: `${this.$t(`m.common['【']`)}${payload.policy.name}${this.$t(`m.common['】']`)}`
        });
        window.changeAlert = 'iamSidesider';
        this.isShowSideSlider = true;
      },

      // handleViewResource (groupItem, payload) {
      //   const params = [];
      //   if (groupItem.related_resource_types.length) {
      //     groupItem.related_resource_types.forEach(item => {
      //       const { name, type, condition } = item;
      //       params.push({
      //         name: type,
      //         label: this.$t(`m.info['tab操作实例']`, { value: name }),
      //         tabType: 'resource',
      //         data: condition,
      //         systemId: item.system_id,
      //         resource_group_id: groupItem.id
      //       });
      //     });
      //   }
      //   this.previewData = cloneDeep(params);
      //   this.sideSliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
      //   window.changeAlert = 'iamSidesider';
      //   this.isShowSideSlider = true;
      // },

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
      
      handleAnimationEnd () {
        this.sideSliderTitle = '';
        this.previewData = [];
      },

      getCurPageData (page = 1) {
        this.allData = this.curFilterSystem.length > 0
          ? this.allDataBack.filter((item) => this.curFilterSystem === item.system.id)
          : cloneDeep(this.allDataBack);
        let startIndex = (page - 1) * this.pagination.limit;
        let endIndex = page * this.pagination.limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > this.allData.length) {
          endIndex = this.allData.length;
        }
        if (page > Math.ceil(this.allData.length / this.pagination.limit)) {
          this.pagination = Object.assign(this.pagination, { current: 1 });
        }
        return this.allData.slice(startIndex, endIndex);
      },

      async fetchTableData () {
        this.isLoading = true;
        try {
          const { current, limit } = this.pagination;
          const tabItem = {
            group: async () => {
              const userGroupParams = {
                page_size: limit,
                page: current
              };
              if (this.externalSystemId) {
                userGroupParams.system_id = this.externalSystemId;
              }
              const { code, data } = await this.$store.dispatch('renewal/getExpireSoonGroupWithUser', userGroupParams);
              this.tableList = data.results || [];
              this.renewalGroupCount = data.count || 0;
              this.$nextTick(() => {
                const currentSelectList = this.currentSelectList.map(item => item.id.toString());
                this.tableList.forEach((item) => {
                  if (currentSelectList.includes(item.id.toString())) {
                    this.$refs.permTableRef && this.$refs.permTableRef.toggleRowSelection(item, true);
                  }
                });
              });
              this.pagination = Object.assign(this.pagination, { count: data.count });
              this.emptyRenewalData
                = formatCodeData(code, this.emptyRenewalData, this.tableList.length === 0);
            },
            custom: () => {
              this.tableList = this.getCurPageData(current);
              if (!this.tableList.length && this.curFilterSystem) {
                this.emptyRenewalData.tipType = 'search';
                this.emptyRenewalData = formatCodeData(0, this.emptyRenewalData, true);
              }
              this.$nextTick(() => {
                this.allData.forEach(item => {
                  if (this.currentSelectList.map(_ => _.id).includes(item.id)) {
                    this.$refs.permTableRef
                      && this.$refs.permTableRef.toggleRowSelection(item, true);
                  }
                });
              });
            }
          };
          return tabItem[this.type]();
        } catch (e) {
          this.emptyRenewalData = formatCodeData(e.code, this.emptyRenewalData);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
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
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          payload && payload.hide();
        }
      },

      async handleSubmitDelete () {
        const typeMap = {
          quit: async () => {
            let selectGroups = [];
            if (this.isMultiple) {
              selectGroups = this.currentSelectList.filter(item =>
                !this.delActionList.map(v => v.id.toString()).includes(item.id.toString()));
              if (!selectGroups.length) {
                this.messageWarn(this.$t(`m.perm['当前勾选项都为不可退出的用户组（唯一管理员不能退出）']`), 3000);
                return;
              }
            } else {
              selectGroups = [this.singleData];
            }
            this.batchQuitLoading = true;
            try {
              for (let i = 0; i < selectGroups.length; i++) {
                await this.$store.dispatch('perm/quitGroupPerm', {
                  type: 'group',
                  id: selectGroups[i].id
                });
              }
              this.messageSuccess(this.$t(`m.info['退出成功']`), 3000);
              this.pagination = Object.assign(this.pagination, { current: 1 });
              await this.fetchTableData();
            } catch (e) {
              console.error(e);
              this.messageAdvancedError(e);
            } finally {
              this.batchQuitLoading = false;
              this.isShowDeleteDialog = false;
              this.currentSelectList = [];
              this.singleData = {};
              this.$refs.permTableRef && this.$refs.permTableRef.clearSelection();
              this.fetchCustomSelection();
              this.$emit('on-change-count', this.renewalGroupCount, this.tableList);
            }
          },
          actions: async () => {
            this.batchQuitLoading = true;
            try {
              await this.$store.dispatch('permApply/deletePerm', {
                policyIds: this.curDeleteIds,
                systemId: this.curCustomData.system.id
              });
              this.allData = this.allData.filter((item) => !this.curDeleteIds.includes(item.policy.policy_id));
              this.tableList = this.tableList.filter((item) => !this.curDeleteIds.includes(item.policy.policy_id));
              this.currentSelectList = this.currentSelectList.filter((item) =>
                !this.curDeleteIds.includes(item.policy.policy_id)
              );
              this.allDataBack = cloneDeep(this.allData);
              this.pageChange(this.pagination.current);
              this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
            } catch (e) {
              this.messageAdvancedError(e);
            } finally {
              this.batchQuitLoading = false;
              this.isShowDeleteDialog = false;
              this.fetchCustomSelection();
              this.$emit('on-change-count', this.allData.length, this.allData);
            }
          }
        };
        typeMap[this.curOperate]();
      },

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
          this.originalCustomTmplList = cloneDeep(res.data);
          this.handleActionLinearData();
        } catch (e) {
          console.error(e);
          this.actionLoading = false;
          this.messageAdvancedError(e);
        }
      },

      handleDeleteActions (type, isMultiple = false) {
        const typeMap = {
          quit: () => {
            const checkboxMap = {
              true: () => {
                this.isShowDeleteDialog = true;
                this.delActionDialogTitle = this.$t(`m.dialog['确认批量退出所选的用户组吗？']`);
                const adminGroups = this.currentSelectList.filter(item =>
                  item.attributes && item.attributes.source_from_role
                  && item.role_members.length === 1 && item.department_id === 0);
                if (adminGroups.length) {
                  this.delActionDialogTip = this.$t(`m.perm['存在用户组不可退出（唯一管理员不能退出）']`);
                  this.delActionList = adminGroups;
                }
              },
              false: () => {
                this.isShowDeleteDialog = true;
                this.delActionDialogTitle = this.$t(`m.dialog['确认退出']`);
              }
            };
            return checkboxMap[isMultiple]();
          }
        };
        return typeMap[type]();
      },

      handleBatchQuit () {
        this.singleData = {};
        this.curOperate = 'quit';
        this.handleDeleteActions('quit', true);
      },
      
      handleQuitRenewal (row) {
        this.curOperate = 'quit';
        this.singleData = Object.assign({}, row);
        this.handleDeleteActions('quit', false);
      },

      async handleShowDelDialog (payload) {
        this.curOperate = 'actions';
        this.curCustomData = payload;
        this.actionLoading = true;
        await this.fetchActions(payload.system.id);
        this.handleDeleteActionOrInstance(payload.policy, 'actions');
      },

      handleDeleteActionOrInstance (payload, type) {
        let delRelatedActions = [];
        this.delActionList = [];
        const { id, name, policy_id: policyId, condition } = payload;
        const policyIdList = this.allData.map(v => v.policy.id);
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
        let policyIds = [policyId];
        if (this.delActionList.length) {
          const list = this.allData.filter(
            item => this.delActionList.map(action => action.id).includes(item.policy.id));
          policyIds = [policyId].concat(list.map(v => v.policy.policy_id));
        }
        this.policyIdList = cloneDeep(policyIds);
        const typeMap = {
          actions: () => {
            this.isShowDeleteDialog = true;
            this.currentActionName = name;
            if (!delRelatedActions.length && hasRelatedActions) {
              const list = [...this.allData].filter(v => curAction.related_actions.includes(v.policy.id));
              if (list.length) {
                policyIds = policyIds.concat(list.map(v => v.policy.policy_id));
              }
            }
            this.curDeleteIds.splice(0, this.curDeleteIds.length, ...policyIds);
            this.policyIdList = cloneDeep(this.curDeleteIds);
            this.delActionDialogTitle = this.$t(`m.dialog['确认删除内容？']`, { value: this.$t(`m.dialog['删除操作权限']`) });
            this.delActionDialogTip = this.$t(`m.info['删除依赖操作产生的影响']`, { value: this.currentActionName });
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
          }
        };
        typeMap[type]();
      },

      handleActionLinearData () {
        const linearActions = [];
        this.originalCustomTmplList.forEach((item) => {
          if (existValue('externalApp') || this.externalSystemId) {
            item.actions = item.actions.filter(v => !v.hidden);
          }
          item.actions.forEach(act => {
            linearActions.push(act);
          });
          (item.sub_groups || []).forEach(sub => {
            if (existValue('externalApp') || this.externalSystemId) {
              sub.actions = sub.actions.filter(v => !v.hidden);
            }
            sub.actions.forEach(act => {
              linearActions.push(act);
            });
          });
        });
        this.linearActionList = cloneDeep(linearActions);
      },

      handleCancelDelete () {
        this.curOperate = '';
        this.isShowDeleteDialog = false;
        this.isBatchDelete = true;
        this.delActionList = [];
        this.curDeleteIds = [];
        this.singleData = {};
        this.curCustomData = {};
      },

      handleAfterDeleteLeaveAction () {
        this.curOperate = '';
        this.currentActionName = '';
        this.delActionDialogTitle = '';
        this.delActionDialogTip = '';
        this.singleData = {};
        this.curCustomData = {};
        this.delActionList = [];
        this.curDeleteIds = [];
        this.policyIdList = [];
      },

      handleDetailAnimationEnd () {
        this.curOperate = '';
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSideSlider = false;
      },

      async handleEmptyClear () {
        this.curFilterSystem = '';
        this.emptyRenewalData.tipType = '';
        this.pagination.current = 1;
        if (['custom'].includes(this.type)) {
          this.tableKey = +new Date();
          await this.resetTableData();
          this.$emit('on-filter-system', { list: this.allData });
        }
      },

      handleEmptyRefresh () {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 10 });
        this.fetchTableData();
      },

      async resetTableData () {
        this.pagination.current = 1;
        await this.fetchTableData();
        this.fetchCustomSelection();
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
.iam-perm-renewal-table-wrapper {
  min-height: 200px;
  .iam-perm-renewal-btn {
    margin-top: 20px;
  }
  /deep/ .perm-renewal-table {
    /* border: none; */
    border-top: 0;
    .iam-expire-time-wrapper {
      height: 22px;
      line-height: 22px !important;
      .cur-text {
        &.yet {
          background-color: #FFF1DB;
          color: #FE9C00;
          font-size: 12px;
          padding: 0 8px;
          line-height: 22px !important;
        }
      }
      .after-renewal-icon {
        font-size: 20px;
        line-height: 22px !important;
        margin: 0 4px;
        color: #FE9C00;
      }
    }
  }
  .related-condition-list {
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
  .related-resource-list {
    position: relative;
    .related-resource-item {
      .instance-count {
        color: #3a84ff;
        cursor: pointer;
        &:hover {
          color: #699df4;
        }
      }
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
    .effect-icon {
      display: none;
      position: absolute;
      top: 50%;
      right: 10px;
      transform: translate(0, -50%);
      font-size: 18px;
      cursor: pointer;
      &-disabled {
        display: none;
        position: absolute;
        top: 50%;
        right: 10px;
        transform: translate(0, -50%);
        font-size: 18px;
        cursor: pointer;
      }
    }
    &:hover {
      .view-icon,
      .effect-icon {
        display: inline-block;
        color: #3a84ff;
      }
      .effect-icon-disabled {
        display: inline-block;
        color: #dcdee5;
      }
    }
    &-border {
      border-bottom: 1px solid #dfe0e5;
    }
  }
  .renewal-user-group-name {
    color: #3a84ff;
    cursor: pointer;
    &:hover {
      color: #699df4;
    }
  }
  /deep/ .iam-my-custom-perm-slider-header {
    display: flex;
    justify-content: space-between;
    .action-wrapper {
      margin-right: 30px;
    }
    .popover-custom-title {
      text-align: center;
      font-size: 24px;
    }
  }
}
</style>
