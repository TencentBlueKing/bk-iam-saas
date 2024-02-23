<template>
  <div class="user-org-group-perm">
    <template v-if="permData.hasPerm">
      <MemberTempPermPolicy
        ref="memberTempPermPolicyRef"
        v-for="(item, index) in memberTempPermData"
        :key="index"
        :title="item.name"
        :type-title="$t(`m.userGroup['用户组']`)"
        :expanded.sync="item.expanded"
        :ext-cls="formatExtCls(index)"
        :class="[
          { 'iam-perm-ext-reset-cls': index === memberTempPermData.length - 1 }
        ]"
        :perm-length="item.pagination.count"
        :one-perm="formatPermLength"
        :is-all-delete="false"
        :show-collapse="false"
        @on-expanded="handleExpanded(...arguments, item)"
      >
        <GroupPermTable
          v-if="item.pagination.count > 0"
          ref="childPermTable"
          :mode="item.id"
          :is-loading="item.loading"
          :is-search-perm="isSearchResource"
          :pagination="item.pagination"
          :cur-search-params="curSearchParams"
          :group-data="groupData"
          :list="item.list"
          :cur-selected-group="curSelectedGroup"
          :empty-data="item.emptyData"
          @on-page-change="handlePageChange(...arguments, item)"
          @on-limit-change="handleLimitChange(...arguments, item)"
          @on-selected-group="handleSelectedGroup"
          @on-remove-group="handleRemoveGroup"
          @on-add-group="handleAddGroup"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </MemberTempPermPolicy>
    </template>
    <template v-else>
      <div class="perm-empty-wrapper">
        <ExceptionEmpty
          :type="emptyPermData.type"
          :empty-text="emptyPermData.text"
          :tip-text="emptyPermData.tip"
          :tip-type="emptyPermData.tipType"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </div>
    </template>
  </div>
</template>
  
  <script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { formatCodeData, sleep } from '@/common/util';
  import MemberTempPermPolicy from '@/components/custom-perm-system-policy/index.vue';
  import GroupPermTable from './group-perm-table.vue';
  export default {
    components: {
      MemberTempPermPolicy,
      GroupPermTable
    },
    props: {
      groupData: {
        type: Object,
        default: () => {
          return {};
        }
      },
      emptyData: {
        type: Object,
        default: () => {
          return {
            type: 'empty',
            text: '暂无数据',
            tip: '',
            tipType: ''
          };
        }
      
      },
      componentLoading: {
        type: Boolean,
        default: false
      },
      searchParams: {
        type: Object
      }
    },
    data () {
      return {
        permData: {
          hasPerm: false
        },
        isOnlyPerm: false,
        isSearchResource: false,
        onePerm: 0,
        totalCount: 0,
        initMemberTempPermData: [
          {
            id: 'personalOrDepartPerm',
            name: this.$t(`m.userOrOrg['个人用户组权限']`),
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
          }
        ],
        memberTempPermData: [],
        curSelectedGroup: [],
        queryGroupData: {},
        curSearchParams: {},
        emptyPermData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
        ...mapGetters(['user', 'externalSystemId', 'mainContentLoading']),
        formatExtCls () {
          return (index) => {
            if (this.isOnlyPerm) {
              return 'only-perm-item-wrapper';
            }
            const isOnePerm = this.memberTempPermData.filter((item) => item.pagination.count > 0).length;
            if (isOnePerm < 2) {
              return 'iam-perm-no-border';
            }
            return index > 0 ? 'iam-perm-ext-cls' : '';
          };
        },
        formatPermLength () {
          const len = this.memberTempPermData.filter((item) => item.pagination.count > 0).length;
          return len;
        }
    },
    watch: {
      groupData: {
        handler (value) {
          this.curSelectedGroup = [];
          this.queryGroupData = cloneDeep(value);
          // 只有手动切换组织架构成员时才重置数据，默认以兄弟组件通信处理交互
          if (value.isClick) {
            this.fetchResetData();
          }
        },
        immediate: true
      },
      searchParams: {
        handler (value) {
          if (!value.action_id) {
            delete value.resource_instances;
          }
          this.curSearchParams = { ...value };
        },
        immediate: true
      },
      emptyData: {
        handler (value) {
          this.emptyPermData = Object.assign({}, value);
        },
        immediate: true
      }
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-refresh-resource-search');
      });
      bus.$on('on-refresh-resource-search', (payload) => {
        const { isSearchPerm, curSearchParams } = payload;
        this.curSearchParams = curSearchParams || {};
        if (!this.curSearchParams.action_id) {
          delete this.curSearchParams.resource_instances;
        }
        this.isSearchResource = isSearchPerm || false;
        this.resetPagination();
        this.fetchInitData();
      });
    },
    methods: {
      async fetchResetData () {
        // this.emptyPermData.tipType = '';
        // this.handleEmptyClear();
        this.memberTempPermData.forEach((item) => {
          item.expanded = false;
        });
        await this.fetchInitData();
      },

      // 获取个人/部门用户组
      async fetchUserGroupSearch () {
        const { id, type } = this.queryGroupData;
        const { emptyData, pagination } = this.memberTempPermData[0];
        try {
          this.memberTempPermData[0].loading = true;
          const { current, limit } = pagination;
          const url = 'userOrOrg/getUserOrDepartGroupList';
          const params = {
            ...this.curSearchParams,
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, {
              ...params,
              ...{
                subject_type: type,
                subject_id: id
              }
          });
          const totalCount = data.count || 0;
          this.memberTempPermData[0] = Object.assign(this.memberTempPermData[0], {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(this.memberTempPermData[0].emptyData);
          this.$nextTick(() => {
            const curSelectedId = this.curSelectedGroup.map((item) => item.id);
            this.memberTempPermData[0].list.forEach((item) => {
              if (this.$refs.childPermTable && this.$refs.childPermTable.length) {
                if (curSelectedId.includes(item.id)) {
                  this.$refs.childPermTable[0].$refs.groupPermRef.toggleRowSelection(item, true);
                }
                this.$refs.childPermTable[0].fetchCustomTotal(this.curSelectedGroup);
              }
            });
          });
        } catch (e) {
          console.error(e);
          this.emptyPermData = formatCodeData(e.code, emptyData);
          this.memberTempPermData[0] = Object.assign(this.memberTempPermData[0], {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.messageAdvancedError(e);
        } finally {
          this.memberTempPermData[0].loading = false;
        }
      },

      // 获取用户所属部门用户组
      async fetchDepartGroupSearch () {
        const { id, type } = this.queryGroupData;
        const curData = this.memberTempPermData.find((item) => item.id === 'departPerm');
        const { emptyData, pagination } = curData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const params = {
            ...this.curSearchParams,
            ...{
              subject_type: type,
              subject_id: id
            },
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          // 'userOrOrg/getUserOrDepartGroupList',
          const { code, data } = await this.$store.dispatch(
            'userOrOrg/getUserGroupByDepartList',
            params
          );
          const totalCount = data.count || 0;
          this.memberTempPermData[1] = Object.assign(this.memberTempPermData[1], {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
        } catch (e) {
          console.error(e);
          this.memberTempPermData[1] = Object.assign(this.memberTempPermData[1], {
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
      async fetchPermByTempSearch () {
        let curData = this.memberTempPermData.find((item) => item.id === 'userTempPerm');
        const { emptyData, pagination } = curData;
        const { id, type } = this.queryGroupData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const url = 'userOrOrg/getUserMemberTempList';
          // let url = 'userOrOrg/getUserOrDepartGroupList';
          const params = {
            ...this.curSearchParams,
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, {
              ...params,
              ...{
                subject_type: type,
                subject_id: id
              }
          });
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
          console.error(e);
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
      async fetchDepartPermByTempSearch () {
        let curData = this.memberTempPermData.find((item) => item.id === 'departTempPerm');
        const { emptyData, pagination } = curData;
        const { id, type } = this.queryGroupData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const url = 'userOrOrg/getDepartMemberTempList';
          // let url = 'userOrOrg/getUserOrDepartGroupList';
          const params = {
            ...this.curSearchParams,
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, {
              ...params,
              ...{
                subject_type: type,
                subject_id: id
              }
          });
          const totalCount = data.count;
          curData = Object.assign(curData, {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(curData.emptyData);
        } catch (e) {
          console.error(e);
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
          userOrgPerm: () => {
            const typeMap = {
              user: async () => {
                this.memberTempPermData = cloneDeep(this.initMemberTempPermData);
                this.memberTempPermData[0] = Object.assign(this.memberTempPermData[0], { name: this.$t(`m.userOrOrg['个人用户组权限']`) });
                await Promise.all([
                  this.fetchUserGroupSearch(),
                  this.fetchDepartGroupSearch(),
                  this.fetchPermByTempSearch(),
                  this.fetchDepartPermByTempSearch()
                ]);
                this.$set(this.permData, 'hasPerm', this.memberTempPermData.some((v) => v.pagination.count > 0));
                this.isOnlyPerm = this.memberTempPermData.filter((v) => v.pagination.count > 0).length === 1;
              },
              department: async () => {
                this.memberTempPermData = this.initMemberTempPermData.filter((item) => ['personalOrDepartPerm', 'userTempPerm'].includes(item.id));
                this.memberTempPermData[0] = Object.assign(this.memberTempPermData[0], { name: this.$t(`m.perm['用户组权限']`) });
                await Promise.all([
                  this.fetchUserGroupSearch(),
                  this.fetchPermByTempSearch()
                ]);
                this.$set(this.permData, 'hasPerm', this.memberTempPermData.some((v) => v.pagination.count > 0));
                this.isOnlyPerm = this.memberTempPermData.filter((v) => v.pagination.count > 0).length === 1;
              }
            };
            return typeMap[this.queryGroupData.type]();
          }
        };
        if (routeMap[this.$route.name]) {
          await routeMap[this.$route.name]();
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

      async formatPaginationData (payload, current, limit) {
        const curData = this.memberTempPermData.find((item) => item.id === payload.id);
        if (curData) {
          const typeMap = {
            personalOrDepartPerm: async () => {
              curData.pagination = Object.assign(curData, { current, limit });
              if (['userOrgPerm'].includes(this.$route.name)) {
                await this.fetchUserGroupSearch();
              }
            },
            departPerm: async () => {
              curData.pagination = Object.assign(curData, { current, limit });
              if (['userOrgPerm'].includes(this.$route.name)) {
                await this.fetchDepartGroupSearch();
              }
            },
            userTempPerm: async () => {
              curData.pagination = Object.assign(curData, { current, limit });
              if (['userOrgPerm'].includes(this.$route.name)) {
                await this.fetchPermByTempSearch();
              }
            },
            departTempPerm: async () => {
              curData.pagination = Object.assign(curData, { current, limit });
              if (['userOrgPerm'].includes(this.$route.name)) {
                await this.fetchDepartPermByTempSearch();
              }
            }
          };
          return typeMap[payload.id]();
        }
      },

      handleExpanded (value, payload) {
        if (!value) {
          this.handleSelectedGroup([]);
          bus.$emit('on-remove-toggle-checkbox', this.curSelectedGroup);
        }
        payload.loading = value;
        sleep(300).then(() => {
          payload.loading = false;
        });
      },

      handleSelectedGroup (payload) {
        this.$emit('on-selected-group', payload);
        this.curSelectedGroup = [...payload];
      },

      handleRefreshGroup (payload) {
        const curData = this.memberTempPermData.find((item) => item.id === payload.mode);
        this.formatPaginationData(curData, 1, curData.pagination.limit);
        this.curSelectedGroup = [];
        this.$emit('on-selected-group', []);
      },

      handleAddGroup (payload) {
        this.handleRefreshGroup(payload);
      },

      handleRemoveGroup (payload) {
        this.handleRefreshGroup(payload);
      },
  
      handlePageChange (current, payload) {
        const curData = this.memberTempPermData.find((item) => item.id === payload.id);
        this.formatPaginationData(payload, current, curData.pagination.limit);
      },
  
      handleLimitChange (limit, payload) {
        const curData = this.memberTempPermData.find((item) => item.id === payload.id);
        this.formatPaginationData(payload, curData.pagination.current, limit);
      },
  
      handleEmptyRefresh () {
        this.resetPagination();
        this.$emit('on-refresh');
      },
  
      handleEmptyClear () {
        this.resetPagination();
        this.$emit('on-clear');
      },

      resetPagination (limit = 10) {
        this.memberTempPermData.forEach((item) => {
          item.pagination = Object.assign(item.pagination, { current: 1, limit });
        });
      }
    }
  };
  </script>
  
  <style lang="postcss" scoped>
  .user-org-group-perm {
    width: 100%;
    position: relative;
    .iam-perm-ext-cls {
      margin-top: 1px;
    }
    .iam-perm-ext-reset-cls {
      margin-bottom: 20px;
    }
    .iam-perm-no-border {
      border: none;
    }
    .perm-empty-wrapper {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, 50%);
    }
  }
  </style>
