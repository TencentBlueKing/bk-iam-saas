<template>
  <div class="user-org-group-perm">
    <template v-if="hasPerm">
      <MemberTempPermPolicy
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
        :one-perm="isOnlyPerm ? 1 : formatPermLength"
        :is-only-perm="isOnlyPerm"
        :is-all-delete="false"
        :show-collapse="false"
        @on-expanded="handleExpanded(...arguments, item)"
      >
        <GroupPermTable
          v-if="item.pagination.count > 0"
          :mode="item.id"
          :is-loading="item.loading"
          :is-search-perm="isSearchResource"
          :pagination="item.pagination"
          :group-data="groupData"
          :list="item.list"
          :empty-data="item.emptyData"
          @on-page-change="handlePageChange(...arguments, item)"
          @on-limit-change="handleLimitChange(...arguments, item)"
          @on-selected-group="handleSelectedGroup"
          @on-remove-group="handleRemoveGroup"
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
      isSearchPerm: {
        type: Boolean,
        default: false
      },
      isOnlyPerm: {
        type: Boolean,
        default: false
      },
      componentLoading: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        hasPerm: false,
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
            name: this.$t(`m.userOrOrg['人员模板用户组权限']`),
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
            name: this.$t(`m.userOrOrg['人员模板用户组权限']`),
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
        currentSelectGroupList: [],
        queryGroupData: [],
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
      emptyData: {
        handler (value) {
          this.emptyPermData = Object.assign({}, value);
        },
        immediate: true
      },
      totalCount: {
        handler (value) {
          this.hasPerm = value > 0;
        },
        immediate: true
      },
      hasPerm (value) {
        return value || this.totalCount > 0;
      },
      groupData: {
        handler (value) {
          if (Object.keys(value).length > 0) {
            this.fetchResetData(value);
          }
        },
        immediate: true
      },
      isSearchPerm: {
        handler (value) {
          this.isSearchResource = value;
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
        this.isSearchResource = isSearchPerm || false;
        this.resetPagination();
        this.fetchInitData();
      });
    },
    methods: {
      async fetchResetData (value) {
        this.emptyPermData.tipType = '';
        this.handleEmptyClear();
        this.queryGroupData = cloneDeep(value);
        this.fetchInitData();
      },

      // 获取个人/部门用户组
      async fetchUserGroupSearch () {
        const { id, type } = this.queryGroupData;
        let curData = this.memberTempPermData[0];
        const { emptyData, pagination } = curData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const url = 'userOrOrg/getUserOrDepartGroupList';
          let params = {
            limit,
            offset: limit * (current - 1)
          };
          if (this.isSearchResource) {
            params = {
                ...this.curSearchParams,
                limit,
                offset: limit * (current - 1)
            };
          }
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
          this.emptyPermData = formatCodeData(e.code, emptyData);
          curData = Object.assign(curData, {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.messageAdvancedError(e);
        } finally {
          curData.loading = false;
        }
      },

      // 获取用户所属部门用户组
      async fetchDepartGroupSearch () {
        const { id, type } = this.queryGroupData;
        const curData = this.memberTempPermData[1];
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
          // 'userOrOrg/getUserGroupByDepartList',
          const { code, data } = await this.$store.dispatch(
            'userOrOrg/getUserOrDepartGroupList',
            params
          );
          const totalCount = data.count || 0;
          this.memberTempPermData[1] = Object.assign(this.memberTempPermData[1], {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.$nextTick(() => {
            this.memberTempPermData[1].list.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
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
        const { emptyData, pagination } = this.memberTempPermData[2];
        const { id, type } = this.queryGroupData;
        try {
          this.memberTempPermData[2].loading = true;
          const { current, limit } = pagination;
          let url = 'userOrOrg/getUserMemberTempList';
          let params = {
            limit,
            offset: limit * (current - 1)
          };
          if (this.isSearchResource) {
            url = 'userOrOrg/getUserMemberTempList';
            params = {
                ...this.curSearchParams,
                limit,
                offset: limit * (current - 1)
            };
          }
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
          this.memberTempPermData[2] = Object.assign(this.memberTempPermData[2], {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(this.memberTempPermData[2].emptyData);
          this.$nextTick(() => {
            this.memberTempPermData[2].list.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          });
        } catch (e) {
          console.error(e);
          this.memberTempPermData[2] = Object.assign(this.memberTempPermData[2], {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.emptyPermData = formatCodeData(e.code, emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.memberTempPermData[2].loading = false;
        }
      },

      // 部门人员模版用户组权限
      async fetchDepartPermByTempSearch () {
        const { emptyData, pagination } = this.memberTempPermData[1];
        const { id, type } = this.queryGroupData;
        try {
          this.memberTempPermData[1].loading = true;
          const { current, limit } = pagination;
          let url = 'userOrOrg/getDepartMemberTempList';
          let params = {
            limit,
            offset: limit * (current - 1)
          };
          if (this.isSearchResource) {
            url = 'userOrOrg/getDepartMemberTempList';
            params = {
                ...this.curSearchParams,
                limit,
                offset: limit * (current - 1)
            };
          }
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
          this.memberTempPermData[1] = Object.assign(this.memberTempPermData[1], {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(this.memberTempPermData[1].emptyData);
          this.$nextTick(() => {
            this.memberTempPermData[1].list.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          });
        } catch (e) {
          console.error(e);
          this.memberTempPermData[1] = Object.assign(this.memberTempPermData[1], {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.emptyPermData = formatCodeData(e.code, emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.memberTempPermData[1].loading = false;
        }
      },
  
      async fetchInitData () {
        const routeMap = {
          userOrgPerm: () => {
            const typeMap = {
              user: async () => {
                this.memberTempPermData = this.initMemberTempPermData.filter((item) => ['personalOrDepartPerm', 'departPerm', 'userTempPerm'].includes(item.id));
                this.memberTempPermData[0] = Object.assign(this.memberTempPermData[0], { name: this.$t(`m.userOrOrg['个人用户组权限']`) });
                await Promise.all([
                  this.fetchUserGroupSearch(),
                  this.fetchDepartGroupSearch(),
                  this.fetchPermByTempSearch()
                ]);
                this.hasPerm = this.memberTempPermData.some((v) => v.pagination.count > 0);
              },
              department: async () => {
                this.memberTempPermData = this.initMemberTempPermData.filter((item) => ['personalOrDepartPerm', 'departTempPerm'].includes(item.id));
                this.memberTempPermData[0] = Object.assign(this.memberTempPermData[0], { name: this.$t(`m.perm['用户组权限']`) });
                await Promise.all([
                  this.fetchUserGroupSearch(),
                  this.fetchDepartPermByTempSearch()
                ]);
                this.hasPerm = this.memberTempPermData.some((v) => v.pagination.count > 0);
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
                await this.fetchUserGroupSearch();
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
        payload.loading = value;
        sleep(300).then(() => {
          payload.loading = false;
        });
      },

      handleSelectedGroup (payload) {
        this.$emit('on-selected-group', payload);
      },

      handleRemoveGroup (payload) {
        const curData = this.memberTempPermData.find((item) => item.id === payload.mode);
        this.formatPaginationData(curData, 1, curData.pagination.limit);
        this.$emit('on-selected-group', []);
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
