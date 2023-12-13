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
        :one-perm="formatPermLength"
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
            name: this.$t(`m.perm['通过用户加入人员模板的用户组权限']`),
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
        userList: [],
        departList: [],
        currentSelectGroupList: [],
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
      memberTempByUserCount: {
        handler (value) {
          this.$set(this.memberTempPermData[0].pagination, 'count', value);
        },
        immediate: true
      },
      memberTempByDepartCount: {
        handler (value) {
          this.$set(this.memberTempPermData[1].pagination, 'count', value);
        },
        immediate: true
      },
      memberTempByUserList: {
        handler (value) {
          this.$set(this.memberTempPermData[0], 'list', [...value]);
        },
        immediate: true
      },
      memberTempByDepartList: {
        handler (value) {
          this.$set(this.memberTempPermData[1], 'list', [...value]);
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
      }
    },
    created () {
      if (['user'].includes(this.$route.name) && !this.isSearchPerm) {
        this.fetchInitData();
      }
    },
    methods: {
      // 我的权限模块接口
      async fetchDataByUser () {
        const { emptyData, pagination } = this.memberTempPermData[0];
        try {
          this.memberTempPermData[0].loading = true;
          let url = '';
          let params = {};
          const { current, limit } = pagination;
          if (this.isSearchPerm) {
            url = 'perm/getMemberTempByUserSearch';
            params = {
              ...this.curSearchParams,
              limit,
              offset: limit * (current - 1)
            };
          } else {
            url = 'perm/getMemberTempByUser';
            params = {
              page_size: limit,
              page: current
            };
          }
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, params);
          this.memberTempPermData[0] = Object.assign(this.memberTempPermData[0], {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, data.count === 0),
            pagination: { ...pagination, ...{ count: data.count || 0 } }
          });
          this.$nextTick(() => {
            this.memberTempPermData[0].list.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          });
        } catch (e) {
          console.error(e);
          this.memberTempPermData[0] = Object.assign(this.memberTempPermData[1], {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.messageAdvancedError(e);
        } finally {
          this.memberTempPermData[0].loading = false;
        }
      },

      async fetchDataByDepart () {
        const { emptyData, pagination } = this.memberTempPermData[1];
        try {
          this.memberTempPermData[1].loading = true;
          let url = '';
          let params = {};
          const { current, limit } = pagination;
          if (this.isSearchPerm) {
            url = 'perm/getMemberTempByDepartSearch';
            params = {
              ...this.curSearchParams,
              limit,
              offset: limit * (current - 1)
            };
          } else {
            url = 'perm/getMemberTempByDepart';
            params = {
              page_size: limit,
              page: current
            };
          }
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, params);
          const totalCount = data.count;
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
          this.memberTempPermData[1].loading = false;
        }
      },

      // 用户模块接口
      async fetchPermGroupsByUser () {
        const { emptyData, pagination } = this.memberTempPermData[0];
        try {
          this.memberTempPermData[1].loading = true;
          let url = '';
          let params = {};
          const { current, limit } = pagination;
          if (this.isSearchPerm) {
            url = 'perm/getPermGroupsByTempSearch';
            params = {
              ...this.curSearchParams,
              limit,
              offset: limit * (current - 1)
            };
          } else {
            url = 'perm/getPermGroupsByTemp';
            params = {
              limit,
              offset: current
            };
          }
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { id, type, username } = this.data;
          const { code, data } = await this.$store.dispatch(url, {
            ...params,
            ...{
              subjectType: type === 'user' ? type : 'department',
              subjectId: type === 'user' ? username : id
            }
          });
          const totalCount = data.count;
          this.memberTempPermData[0] = Object.assign(this.memberTempPermData[0], {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.$nextTick(() => {
            this.memberTempPermData[0].list.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          });
        } catch (e) {
          console.error(e);
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

      async fetchPermGroupsByDepart () {
        const { emptyData, pagination } = this.memberTempPermData[1];
        try {
          this.memberTempPermData[1].loading = true;
          let url = '';
          let params = {};
          const { current, limit } = pagination;
          if (this.isSearchPerm) {
            url = 'perm/getDepartPermGroupsByTempSearch';
            params = {
              ...this.curSearchParams,
              limit,
              offset: limit * (current - 1)
            };
          } else {
            url = 'perm/getDepartPermGroupsByTemp';
            params = {
              limit,
              offset: current
            };
          }
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { id, type, username } = this.data;
          const { code, data } = await this.$store.dispatch(url, {
            ...params,
            ...{
              subjectType: type === 'user' ? type : 'department',
              subjectId: type === 'user' ? username : id
            }
          });
          const totalCount = data.count;
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
          console.error(e, 5555);
          this.memberTempPermData[1] = Object.assign(this.memberTempPermData[1], {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.messageAdvancedError(e);
        } finally {
          this.memberTempPermData[1].loading = false;
        }
      },

      fetchInitData () {
        const routeMap = {
          myPerm: () => {
            this.fetchDataByUser();
            this.fetchDataByDepart();
          },
          user: async () => {
            this.data.type === 'user'
              ? await Promise.all([this.fetchPermGroupsByUser(), this.fetchPermGroupsByDepart()])
              : await this.fetchPermGroupsByDepart();
            this.hasPerm = this.memberTempPermData.some((v) => v.pagination.count > 0);
          }
        };
        if (routeMap[this.$route.name]) {
          routeMap[this.$route.name]();
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

      handlePageChange (current, payload) {
        const typeMap = {
          user: async () => {
            this.memberTempPermData[0].pagination = Object.assign(this.memberTempPermData[0].pagination, { current });
            if (['myPerm'].includes(this.$route.name)) {
              await this.fetchDataByUser();
              return;
            }
            if (['user'].includes(this.$route.name)) {
              await this.fetchPermGroupsByUser();
            }
          },
          depart: async () => {
            this.memberTempPermData[1].pagination = Object.assign(this.memberTempPermData[1].pagination, { current });
            if (['myPerm'].includes(this.$route.name)) {
              await this.fetchDataByDepart();
              return;
            }
            if (['user'].includes(this.$route.name)) {
              await this.fetchPermGroupsByDepart();
            }
          }
        };
        return typeMap[payload.id]();
      },

      handleLimitChange (limit, payload) {
        const typeMap = {
          user: async () => {
            this.memberTempPermData[0].pagination
              = Object.assign(this.memberTempPermData[0].pagination, { current: 1, limit });
            if (['myPerm'].includes(this.$route.name)) {
              await this.fetchDataByUser();
              return;
            }
            if (['user'].includes(this.$route.name)) {
              await this.fetchPermGroupsByUser();
            }
          },
          depart: async () => {
            this.memberTempPermData[1].pagination
              = Object.assign(this.memberTempPermData[1].pagination, { current: 1, limit });
            if (['myPerm'].includes(this.$route.name)) {
              await this.fetchDataByDepart();
              return;
            }
            if (['user'].includes(this.$route.name)) {
              await this.fetchPermGroupsByDepart();
            }
          }
        };
        return typeMap[payload.id]();
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
  .iam-perm-ext-cls {
    margin-top: 1px;
  }
  .iam-perm-ext-reset-cls {
    margin-bottom: 20px;
  }
  .iam-perm-no-border {
    border: none;
  }
}
</style>
