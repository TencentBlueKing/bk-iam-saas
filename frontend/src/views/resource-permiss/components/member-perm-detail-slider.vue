<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :width="width"
      :quick-close="true"
      ext-cls="resource-perm-member-detail-side"
      @update:isShow="handleCancel"
    >
      <div slot="header" class="resource-perm-member-detail-side-header">
        <span>{{ $t(`m.resourcePermiss['人员权限详情']`) }}</span>
        <span class="custom-header-divider">|</span>
        <span
          class="single-hide custom-header-name"
          v-bk-tooltips="{ content: `${curDetailData.id} (${curDetailData.name})` }"
        >
          {{ `${curDetailData.id} (${curDetailData.name})` }}
        </span>
      </div>
      <div slot="content" class="resource-perm-member-detail-side-content">
        <div class="batch-operate">
          <bk-popover
            :content="removeGroupTitle"
            :disabled="!isNoBatchRemove()"
          >
            <bk-button
              class="batch-operate-remove"
              :disabled="isNoBatchRemove()"
              @click.stop="handleBatch('remove')"
            >
              {{ $t(`m.userOrOrg['批量移出用户组']`) }}
            </bk-button>
          </bk-popover>
        </div>
        <div class="resource-perm-side-content">
          <template v-if="permData.hasPerm">
            <RenderTemplateItem
              :class="[
                'resource-perm-side-content-table',
                formatExtCls(index)
              ]"
              v-for="(item, index) in memberTempPermList"
              :key="index"
              :ref="`rTemplateItem${item.id}`"
              :mode="'detail'"
              :title="item.name"
              :count="item.pagination.count"
              :expanded.sync="item.expanded"
              :ext-cls="formatExtCls(index)"
              @on-expanded="handleExpanded(...arguments, item, index)"
            >
              <div v-bkloading="{ isLoading: item.loading, opacity: 1 }">
                <MemberPermTable
                  v-if="item.pagination.count > 0"
                  ref="childPermTable"
                  :mode="item.id"
                  :is-loading="item.loading"
                  :pagination="item.pagination"
                  :cur-search-params="curSearchParams"
                  :group-data="curDetailData"
                  :list="item.list"
                  :cur-selected-group="curSelectedGroup"
                  :empty-data="item.emptyData"
                  @on-page-change="handlePageChange(...arguments, item)"
                  @on-limit-change="handleLimitChange(...arguments, item)"
                  @on-selected-group="handleSelectedGroup"
                  @on-remove-group="handleRemoveGroup"
                  @on-delete="handleSingleDelete(...arguments, item)"
                  @on-delete-instances="handleDeleteInstances"
                  @on-refresh="handleEmptyRefresh(...arguments, item)"
                />
              </div>
            </RenderTemplateItem>
          </template>
          <template v-else>
            <div class="perm-empty-wrapper">
              <ExceptionEmpty
                :type="emptyPermData.type"
                :empty-text="emptyPermData.text"
                :tip-text="emptyPermData.tip"
                :tip-type="emptyPermData.tipType"
                @on-refresh="handleDetailRefresh"
              />
            </div>
          </template>
        </div>
      </div>
    </bk-sideslider>

    <BatchOperateSlider
      :slider-width="960"
      :is-batch="false"
      :show.sync="isShowBatchSlider"
      :cur-slider-name="curSliderName"
      :user-list="userList"
      :depart-list="departList"
      :title="batchSliderTitle"
      :group-data="curDetailData"
      :group-list="curSelectedGroup"
      @on-submit="handleOperateGroupSubmit"
    />
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { cloneDeep } from 'lodash';
  import { formatCodeData, sleep } from '@/common/util';
  import { bus } from '@/common/bus';
  import PermPolicy from '@/model/my-perm-policy';
  import RenderTemplateItem from './render-template-item.vue';
  import MemberPermTable from './member-perm-table.vue';
  import BatchOperateSlider from '@/views/user-org-perm/components/batch-operate-slider.vue';
  import getActionsMixin from '../common/js/getActionsMixin';

  export default {
    components: {
      RenderTemplateItem,
      MemberPermTable,
      BatchOperateSlider
    },
    mixins: [getActionsMixin],
    props: {
      show: {
        type: Boolean,
        default: false
      },
      curDetailData: {
        type: Object
      }
    },
    data () {
      return {
        isShowSideSlider: false,
        isShowBatchSlider: false,
        isOnlyPerm: false,
        readOnly: false,
        curSliderName: '',
        batchSliderTitle: '',
        removeGroupTitle: '',
        width: 960,
        initMemberTempPermList: [
          {
            id: 'personalOrDepartPerm',
            name: this.$t(`m.userOrOrg['个人用户组权限']`),
            loading: false,
            expanded: true,
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            },
            emptyData: {
              type: 'empty',
              text: '暂无数据',
              tip: '',
              tipType: ''
            },
            list: []
          },
          {
            id: 'departPerm',
            name: this.$t(`m.userOrOrg['组织用户组权限']`),
            loading: false,
            expanded: false,
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            },
            emptyData: {
              type: 'empty',
              text: '暂无数据',
              tip: '',
              tipType: ''
            },
            list: []
          },
          {
            id: 'userTempPerm',
            name: this.$t(`m.perm['直接加入人员模板的用户组权限']`),
            loading: false,
            expanded: false,
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            },
            emptyData: {
              type: 'empty',
              text: '暂无数据',
              tip: '',
              tipType: ''
            },
            list: []
          },
          {
            id: 'departTempPerm',
            name: this.$t(`m.perm['通过组织加入人员模板的用户组权限']`),
            loading: false,
            expanded: false,
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            },
            emptyData: {
              type: 'empty',
              text: '暂无数据',
              tip: '',
              tipType: ''
            },
            list: []
          },
          {
            id: 'customPerm',
            name: this.$t(`m.perm['自定义权限']`),
            loading: false,
            expanded: true,
            pagination: {
              current: 1,
              limit: 10,
              count: 0,
              showTotalCount: true
            },
            emptyData: {
              type: 'empty',
              text: '暂无数据',
              tip: '',
              tipType: ''
            },
            list: []
          }
        ],
        memberTempPermList: [],
        userList: [],
        departList: [],
        curSelectedGroup: [],
        curSearchParams: {},
        permData: {
          hasPerm: false
        },
        groupAttributes: {
          source_from_role: false,
          source_type: ''
        },
        emptyPermData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['externalSystemId']),
      isNoBatchRemove () {
        return () => {
          const hasData = this.curSelectedGroup.length > 0;
          if (!hasData) {
            this.removeGroupTitle = this.$t(`m.userOrOrg['请先勾选用户组权限']`);
          }
          if (hasData) {
            const list = this.curSelectedGroup.filter((item) =>
              item.role_members.length === 1
              && item.attributes
              && item.attributes.source_from_role
            );
            const result = this.curSelectedGroup.length === list.length;
            this.removeGroupTitle = result ? this.$t(`m.userOrOrg['已选择的用户组权限为不可移出的管理员组']`) : '';
            return result;
          }
          return !hasData;
        };
      },
      formatExtCls () {
        return (index) => {
          const len = this.memberTempPermList[index].pagination.count;
          if (!len) {
            return 'no-perm-item-wrapper';
          }
          return index > 0 ? 'iam-perm-ext-cls' : '';
        };
      }
    },
    watch: {
      show: {
        async handler (value) {
          this.isShowSideSlider = !!value;
          if (value) {
            console.log(this.curDetailData);
            await this.fetchInitData();
          }
        },
        immediate: true
      }
    },

    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-drawer-side');
      });
      bus.$on('on-drawer-side', (payload) => {
        this.width = payload.width;
      });
    },
    methods: {
      // 获取个人/部门用户组
      async fetchUserGroup () {
        const { emptyData, pagination } = this.memberTempPermList[0];
        try {
          this.memberTempPermList[0].loading = true;
          const { current, limit } = pagination;
          const url = 'userOrOrg/getUserOrDepartGroupList';
          const {
            id,
            type,
            system_id: systemId,
            action_id: actionId,
            resource_instances: resourceInstances
          } = this.curDetailData;
          const params = {
            ...{
              subject_type: type,
              subject_id: id,
              system_id: systemId,
              action_id: actionId,
              resource_instances: resourceInstances || []
            },
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, params);
          const totalCount = data.count || 0;
          this.memberTempPermList[0] = Object.assign(this.memberTempPermList[0], {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(this.memberTempPermList[0].emptyData);
          setTimeout(() => {
            const curSelectedId = this.curSelectedGroup.map((item) => item.id);
            this.memberTempPermList[0].list.forEach((item) => {
              if (this.$refs.childPermTable && this.$refs.childPermTable.length) {
                if (curSelectedId.includes(item.id)) {
                  this.$refs.childPermTable[0].$refs.groupPermRef.toggleRowSelection(item, true);
                }
                this.$refs.childPermTable[0].fetchCustomTotal(this.curSelectedGroup);
              }
            });
          }, 0);
        } catch (e) {
          this.emptyPermData = formatCodeData(e.code, emptyData);
          this.memberTempPermList[0] = Object.assign(this.memberTempPermList[0], {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.messageAdvancedError(e);
        } finally {
          this.memberTempPermList[0].loading = false;
        }
      },

      // 获取用户所属部门用户组
      async fetchDepartGroup () {
        const curData = this.memberTempPermList.find((item) => item.id === 'departPerm');
        if (!curData) {
          return;
        }
        const { emptyData, pagination } = curData;
        const { current, limit } = pagination;
        const {
          id,
          type,
          system_id: systemId,
          action_id: actionId,
          resource_instances: resourceInstances
        } = this.curDetailData;
        try {
          curData.loading = true;
          const params = {
            ...{
              subject_type: type,
              subject_id: id,
              system_id: systemId,
              action_id: actionId,
              resource_instances: resourceInstances || []
            },
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(
            'userOrOrg/getUserGroupByDepartList',
            params
          );
          const totalCount = data.count || 0;
          this.memberTempPermList[1] = Object.assign(this.memberTempPermList[1], {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
        } catch (e) {
          this.memberTempPermList[1] = Object.assign(this.memberTempPermList[1], {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.messageAdvancedError(e);
        } finally {
          curData.loading = false;
        }
      },
  
      // 用户人员模板用户组权限
      async fetchPermByTemp () {
        let curData = this.memberTempPermList.find((item) => item.id === 'userTempPerm');
        if (!curData) {
          return;
        }
        const { emptyData, pagination } = curData;
        const {
          id,
          type,
          system_id: systemId,
          action_id: actionId,
          resource_instances: resourceInstances
        } = this.curDetailData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const url = 'userOrOrg/getUserMemberTempList';
          const params = {
            ...{
              subject_type: type,
              subject_id: id,
              system_id: systemId,
              action_id: actionId,
              resource_instances: resourceInstances || []
            },
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, params);
          const totalCount = data.count;
          curData = Object.assign(curData, {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(curData.emptyData);
          this.$nextTick(() => {
            curData.list.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          });
        } catch (e) {
          curData = Object.assign(curData, {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.emptyPermData = formatCodeData(e.code, emptyData);
          this.messageAdvancedError(e);
        } finally {
          curData.loading = false;
        }
      },

      // 部门人员模版用户组权限
      async fetchDepartPermByTemp () {
        let curData = this.memberTempPermList.find((item) => item.id === 'departTempPerm');
        if (!curData) {
          return;
        }
        const { emptyData, pagination } = curData;
        const {
          id,
          type,
          system_id: systemId,
          action_id: actionId,
          resource_instances: resourceInstances
        } = this.curDetailData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const url = 'userOrOrg/getDepartMemberTempList';
          const params = {
            ...{
              subject_type: type,
              subject_id: id,
              system_id: systemId,
              action_id: actionId,
              resource_instances: resourceInstances || []
            },
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, params);
          const totalCount = data.count;
          curData = Object.assign(curData, {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(curData.emptyData);
        } catch (e) {
          curData = Object.assign(curData, {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.emptyPermData = formatCodeData(e.code, emptyData);
          this.messageAdvancedError(e);
        } finally {
          curData.loading = false;
        }
      },

      // 获取自定义权限
      async fetchCustomPerm () {
        let curData = this.memberTempPermList.find((item) => item.id === 'customPerm');
        if (!curData) {
          return;
        }
        const { emptyData, pagination } = curData;
        const {
          system_id: systemId,
          action_id: actionId,
          resource_instances: resourceInstances
        } = this.curDetailData;
        if (!systemId) {
          return;
        }
        const params = {
          system_id: systemId,
          action_id: actionId,
          resource_instances: resourceInstances || []
        };
        try {
          const { code, data } = await this.$store.dispatch('perm/getPoliciesSearch', params);
          const result = data || [];
          if (result.length) {
            await this.fetchActions(this.curDetailData);
            curData.list = data.map((item) => {
              const relatedEnvironments = this.linearActionList.find((sub) => sub.id === item.id);
              item.related_environments = relatedEnvironments ? relatedEnvironments.related_environments : [];
              return new PermPolicy(item);
            });
          }
          curData = Object.assign(curData, {
            emptyData: formatCodeData(code, emptyData, result.length === 0),
            pagination: { ...pagination, ...{ count: result.length } }
          });
          this.emptyPermData = cloneDeep(curData.emptyData);
        } catch (e) {
          curData = Object.assign(curData, {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.emptyPermData = formatCodeData(e.code, emptyData);
          this.messageAdvancedError(e);
        } finally {
          curData.loading = false;
        }
      },

      async fetchInitData () {
        const routeMap = {
          resourcePermiss: () => {
            const typeMap = {
              user: async () => {
                this.memberTempPermList = cloneDeep(this.initMemberTempPermList);
                this.memberTempPermList[0] = Object.assign(this.memberTempPermList[0], { name: this.$t(`m.userOrOrg['个人用户组权限']`) });
                await Promise.all([
                  this.fetchUserGroup(),
                  this.fetchDepartGroup(),
                  this.fetchPermByTemp(),
                  this.fetchDepartPermByTemp(),
                  this.fetchCustomPerm()
                ]);
                this.$set(this.permData, 'hasPerm', this.memberTempPermList.some((v) => v.pagination.count > 0));
                this.isOnlyPerm = this.memberTempPermList.filter((v) => v.pagination.count > 0).length === 1;
              }
            };
            return typeMap[this.curDetailData.type]();
          }
        };
        if (routeMap[this.$route.name]) {
          await routeMap[this.$route.name]();
        }
      },

      handleBatch (payload) {
        this.curSliderName = payload;
        this.handleGetMembers();
        const typeMap = {
          remove: () => {
            if (!this.isNoBatchRemove()) {
              this.batchSliderTitle = this.$t(`m.userOrOrg['批量移出用户组']`);
              this.isShowBatchSlider = true;
              this.width = 1160;
            }
          }
        };
        typeMap[payload]();
      },

      handleExpanded (value, payload) {
        if (!value) {
          this.handleSelectedGroup([]);
        }
        payload.loading = value;
        sleep(300).then(() => {
          payload.loading = false;
        });
      },

      async handleSingleDelete (payload) {
        console.log(payload.ids);
        await this.handleDeleteUserPolicy({
          systemId: this.curDetailData.system_id,
          policyIds: payload.ids
        });
      },

      async handleDeleteInstances () {
        await this.fetchCustomPerm();
      },

      async handleDeleteUserPolicy (params = {}) {
        try {
          await this.$store.dispatch('permApply/deletePerm', params);
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          await this.fetchCustomPerm();
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      handleOperateGroupSubmit () {
        this.curSelectedGroup = [];
        this.memberTempPermList[0].expanded = true;
        this.memberTempPermList[0].pagination = Object.assign(this.memberTempPermList[0].pagination, {
          current: 1
        });
        this.fetchUserGroup();
      },

      handleGetMembers () {
        const userList = [];
        const departList = [];
        const typeMap = {
          user: () => {
            userList.push(this.curDetailData);
            this.userList = [...userList];
          },
          department: () => {
            departList.push(this.curDetailData);
            this.departList = [...departList];
          }
        };
        typeMap[this.curDetailData.type]();
      },

      handleSelectedGroup (payload) {
        this.curSelectedGroup = [...payload];
      },

      handleRefreshGroup (payload, current) {
        const curData = this.memberTempPermList.find((item) => item.id === payload.mode);
        this.formatPaginationData(curData, current, curData.pagination.limit);
        this.curSelectedGroup = [];
      },

      handleRemoveGroup (payload) {
        this.handleRefreshGroup(payload, 1);
      },
      
      handleCancel () {
        this.resetData();
        this.$emit('update:show', false);
      },

      handlePageChange (current, payload) {
        const curData = this.memberTempPermList.find((item) => item.id === payload.id);
        this.formatPaginationData(payload, current, curData.pagination.limit);
      },
  
      handleLimitChange (limit, payload) {
        const curData = this.memberTempPermList.find((item) => item.id === payload.id);
        curData.current = 1;
        this.formatPaginationData(payload, curData.current, limit);
      },

      handleEmptyRefresh (payload, row) {
        console.log(payload, row);
        const curData = this.memberTempPermList.find((item) => item.id === row.id);
        if (curData) {
          curData.pagination = Object.assign(curData.pagination, { current: 1, limit: 10 });
          this.handlePageChange(1, curData);
        }
      },

      handleDetailRefresh () {
        this.resetPagination();
        this.fetchInitData();
      },

      formatPaginationData (payload, current, limit) {
        const curData = this.memberTempPermList.find((item) => item.id === payload.id);
        if (curData) {
          curData.pagination = Object.assign(curData, { current, limit });
          const typeMap = {
            personalOrDepartPerm: async () => {
              await this.fetchUserGroup();
            },
            departPerm: async () => {
              await this.fetchDepartGroup();
            },
            userTempPerm: async () => {
              await this.fetchPermByTemp();
            },
            departTempPerm: async () => {
              await this.fetchDepartPermByTemp();
            }
          };
          return typeMap[curData.id]();
        }
      },

      formatRoleMembers (payload) {
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
        }
        return payload || [];
      },

      resetPagination (limit = 10) {
        this.memberTempPermList.forEach((item) => {
          item.pagination = Object.assign(item.pagination, { current: 1, limit });
        });
      },
  
      resetData () {
        this.width = 960;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.resource-perm-member-detail-side {
  &-header {
    display: flex;
    .custom-header-divider {
      margin: 0 8px;
      color: #dcdee5;
    }
    .custom-header-name {
      max-width: 700px;
      font-size: 12px;
      color: #979ba5;
      word-break: break-all;
    }
  }
  &-content {
    padding: 24px;
    box-sizing: border-box;
    .batch-operate {
      margin-bottom: 16px;
      &-remove {
        &.is-disabled {
          background-color: #ffffff;
        }
      }
    }
    /deep/ .resource-perm-side-content {
      &-table {
        margin-bottom: 16px;
        .header {
          padding-left: 16px;
        }
      }
    }
  }
}
</style>
