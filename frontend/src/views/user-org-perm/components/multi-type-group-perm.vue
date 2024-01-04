<template>
  <div class="my-template-group-perm">
    <template v-if="hasPerm">
      <MemberTempPermPolicy
        v-for="(item, index) in memberTempPermData"
        :key="item.id"
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
        @on-expanded="handleExpanded(...arguments, item)"
      >
        <TemplatePermTable
          v-if="item.pagination.count > 0"
          :mode="item.id"
          :is-loading="item.loading"
          :is-search-perm="isSearchPerm"
          :pagination="item.pagination"
          :list="item.list"
          :empty-data="item.emptyData"
          @on-page-change="handlePageChange(...arguments, item)"
          @on-limit-change="handleLimitChange(...arguments, item)"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </MemberTempPermPolicy>
    </template>
    <template v-else>
      <div class="my-perm-custom-perm-empty-wrapper">
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
  import { formatCodeData, sleep } from '@/common/util';
  import MemberTempPermPolicy from '@/components/custom-perm-system-policy/index.vue';
  import TemplatePermTable from './template-perm-table.vue';
  export default {
    components: {
      MemberTempPermPolicy,
      TemplatePermTable
    },
    props: {
      personalGroupList: {
        type: Array,
        default: () => []
      },
      memberTempByUserList: {
        type: Array,
        default: () => []
      },
      memberTempByDepartList: {
        type: Array,
        default: () => []
      },
      memberTempByUserCount: {
        type: Number
      },
      memberTempByDepartCount: {
        type: Number
      },
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
      curSearchParams: {
        type: Object,
        default: () => {}
      },
      curSearchPagination: {
        type: Object,
        default: () => {
          return {
            current: 1,
            limit: 10,
            count: 0
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
      totalCount: {
        type: Number
      },
      componentLoading: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        hasPerm: false,
        onePerm: 0,
        memberTempPermData: [
          {
            id: 'user',
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
            id: 'user',
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
            id: 'depart',
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
        userList: [],
        departList: [],
        currentSelectGroupList: [],
        queryGroupData: [],
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
            this.fetchDetailData(value);
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchDetailData (value) {
        this.emptyPermData.tipType = '';
        this.handleEmptyClear();
        this.queryGroupData = cloneDeep(value);
        this.fetchInitData();
      },

      // 获取个人用户组
      async fetchUserGroupSearch () {
        const { id, type } = this.queryGroupData;
        let curData = ['user'].includes(type) ? this.memberTempPermData[0] : this.memberTempPermData[1];
        const { emptyData, pagination } = curData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const url = 'userOrOrg/getUserGroupList';
          let params = {
            limit,
            offset: limit * (current - 1)
          };
          if (this.isSearchPerm) {
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

      // 获取部门用户组
      async fetchDepartGroupSearch () {
        try {
          const { current, limit } = this.curSearchPagination;
          const { id, type } = this.queryGroupData;
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
          const { code, data } = await this.$store.dispatch(
            'userOrOrg/getUserGroupByDepartList',
            params
          );
          this.de = data.results || [];
          // this.$set(this.panels[0], 'count', data.count || 0);
          this.curEmptyData = formatCodeData(code, this.curEmptyData, data.count === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.personalGroupList = [];
          this.curEmptyData = formatCodeData(code, this.curEmptyData);
          this.messageAdvancedError(e);
        } finally {
          this.componentLoading = false;
        }
      },
  
      async fetchPermGroupsByDepart () {
        const { emptyData, pagination } = this.memberTempPermData[1];
        try {
          this.memberTempPermData[1].loading = true;
          const { current, limit } = pagination;
          let url = 'perm/getDepartPermGroupsByTemp';
          let params = {
            limit,
            offset: limit * (current - 1)
          };
          if (this.isSearchPerm) {
            url = 'perm/getDepartPermGroupsByTempSearch';
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
          const { id, type, username } = this.groupData;
          const { code, data } = await this.$store.dispatch(url, {
              ...params,
              ...{
                subject_type: type === 'user' ? type : 'department',
                subject_id: type === 'user' ? username : id
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
  
      fetchInitData () {
        const routeMap = {
          userOrgPerm: async () => {
            this.groupData.type !== 'user'
              ? await this.fetchUserGroupSearch()
              : await Promise.all([this.fetchUserGroupSearch(), this.fetchPermGroupsByDepart()]);
            this.hasPerm = this.memberTempPermData.some((v) => v.pagination.count > 0);
          }
        };
        if (routeMap[this.$route.name]) {
          return routeMap[this.$route.name]();
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
  
      handleExpanded (value, payload) {
        payload.loading = value;
        sleep(300).then(() => {
          payload.loading = false;
        });
      },
  
      formatPaginationData (payload, current, limit) {
        const typeMap = {
          user: async () => {
            this.memberTempPermData[0].pagination
              = Object.assign(this.memberTempPermData[0].pagination, { current, limit });
            if (['myPerm'].includes(this.$route.name)) {
              await this.fetchDataByUser();
              return;
            }
            if (['user'].includes(this.$route.name)) {
              await this.fetchUserGroupSearch();
            }
          },
          depart: async () => {
            this.memberTempPermData[1].pagination
              = Object.assign(this.memberTempPermData[1].pagination, { current, limit });
            if (['myPerm'].includes(this.$route.name)) {
              await this.fetchDataByDepart();
              return;
            }
            if (['user'].includes(this.$route.name)) {
              this.groupData.type === 'user' ? await this.fetchPermGroupsByDepart() : await this.fetchUserGroupSearch();
            }
          }
        };
        return typeMap[payload.id]();
      },
  
      handlePageChange (current, payload) {
        const curData = this.memberTempPermData.find((item) => item.id === payload.id);
        this.formatPaginationData(payload, current, curData.pagination.limit);
      },
  
      handleLimitChange (limit, payload) {
        const curData = this.memberTempPermData.find((item) => item.id === payload.id);
        this.formatPaginationData(payload, curData.pagination.current, limit);
      },
  
      resetPagination (limit = 10) {
        this.memberTempPermData.forEach((item) => {
          item.pagination = Object.assign(item.pagination, { current: 1, limit });
        });
      },
  
      handleEmptyRefresh () {
        this.resetPagination();
        this.$emit('on-refresh');
      },
  
      handleEmptyClear () {
        this.resetPagination();
        this.$emit('on-clear');
      }
    }
  };
  </script>
  
  <style lang="postcss" scoped>
  .my-template-group-perm {
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
    .my-perm-custom-perm-empty-wrapper {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(50%, 50%);
    }
  }
  </style>
