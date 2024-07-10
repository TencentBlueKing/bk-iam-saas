<template>
  <div
    :class="[
      'user-perm-group',
      { 'is-show-notice': showNoticeAlert }
    ]"
  >
    <template v-if="permData.hasPerm">
      <RenderPermItem
        v-for="(item, index) in allPermItem"
        :key="index"
        :class="[
          'resource-perm-side-content-table'
        ]"
        :ref="`rTemplateItem_${item.id}`"
        :mode="'detail'"
        :title="item.name"
        :count="item.pagination.count"
        :expanded.sync="item.expanded"
        :ext-cls="formatExtCls(index)"
        @on-expanded="handleExpanded(...arguments, item, index)"
      >
        <div v-if="item.pagination.count > 0" slot="headerTitle">
          <span class="sub-header-item-title">{{ item.name }}</span>
          <span class="sub-header-item-count">
            ({{ $t(`m.common['共']`) }}
            <span class="count">{{ item.pagination.count }}</span>
            {{ $t(`m.common['条']`) }})
          </span>
        </div>
        <GroupPermTable
          ref="childPermTable"
          v-if="item.pagination.count > 0"
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
          @on-quit-group="handleQuitGroup"
          @on-add-group="handleAddGroup"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </RenderPermItem>
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
  import { mapGetters } from 'vuex';
  import { cloneDeep } from 'lodash';
  import { bus } from '@/common/bus';
  import { formatCodeData, sleep } from '@/common/util';
  import RenderPermItem from '@/components/iam-expand-perm/index.vue';
  import GroupPermTable from './group-perm-table.vue';
  export default {
    inject: ['showNoticeAlert'],
    components: {
      RenderPermItem,
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
        initAllPermItem: [
          {
            id: 'personalPerm',
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
        allPermItem: [],
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
      ...mapGetters(['user', 'externalSystemsLayout', 'externalSystemId', 'mainContentLoading']),
      formatExtCls () {
        return (index) => {
          const len = this.allPermItem[index].pagination.count;
          if (!len) {
            return 'no-perm-item-wrapper';
          }
          return index > 0 ? 'iam-perm-ext-cls' : '';
        };
      },
      formatPermLength () {
        const len = this.allPermItem.filter((item) => item.pagination.count > 0).length;
        return len;
      }
    },
    watch: {
      groupData: {
        handler (value) {
          this.curSelectedGroup = [];
          this.queryGroupData = cloneDeep(value);
          this.fetchResetData();
        },
        immediate: true
      },
      searchParams: {
        handler (value) {
          if (value && !value.action_id) {
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
      this.handleSetBusQueryData();
    },
    methods: {
      async fetchResetData () {
        this.resetPagination();
        await this.fetchInitData();
      },

      // 获取个人用户组权限
      async fetchUserGroupSearch () {
        let curData = this.allPermItem.find((item) => item.id === 'personalPerm');
        if (!curData) {
          return;
        }
        const { emptyData, pagination } = curData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const url = 'perm/getPersonalGroups';
          const params = {
            ...this.curSearchParams,
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, params);
          const totalCount = data.count || 0;
          curData = Object.assign(curData, {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(curData.emptyData);
          setTimeout(() => {
            const curSelectedId = this.curSelectedGroup.map((item) => item.id);
            curData.list.forEach((item) => {
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
        let curData = this.allPermItem.find((item) => item.id === 'departPerm');
        if (!curData) {
          return;
        }
        const { emptyData, pagination } = curData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const params = {
            ...this.curSearchParams,
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(
            'perm/getDepartMentsPersonalGroups',
            params
          );
          const totalCount = data.count || data.length || 0;
          curData = Object.assign(curData, {
            list: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
        } catch (e) {
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
  
      // 用户人员模板用户组权限
      async fetchPermByTempSearch () {
        let curData = this.allPermItem.find((item) => item.id === 'userTempPerm');
        if (!curData) {
          return;
        }
        const { emptyData, pagination } = curData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const url = 'perm/getMemberTempByUser';
          const params = {
            ...this.curSearchParams,
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
        let curData = this.allPermItem.find((item) => item.id === 'departTempPerm');
        if (!curData) {
          return;
        }
        const { emptyData, pagination } = curData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const params = {
            ...this.curSearchParams,
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch('perm/getMemberTempByDepart', params);
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
  
      async fetchInitData () {
        const routeMap = {
          myPerm: () => {
            const typeMap = {
              all: async () => {
                this.allPermItem = cloneDeep(this.initAllPermItem);
                this.allPermItem[0] = Object.assign(this.allPermItem[0], { name: this.$t(`m.userOrOrg['个人用户组权限']`) });
                const hideApplyBtn = this.externalSystemsLayout.myPerm.hideApplyBtn;
                if (!hideApplyBtn) {
                  await Promise.all([
                    this.fetchUserGroupSearch(),
                    this.fetchDepartGroupSearch(),
                    this.fetchPermByTempSearch(),
                    this.fetchDepartPermByTempSearch()
                  ]);
                }
                this.$set(this.permData, 'hasPerm', this.allPermItem.some((v) => v.pagination.count > 0));
                this.isOnlyPerm = this.allPermItem.filter((v) => v.pagination.count > 0).length === 1;
                this.formatDefaultExpand();
                // 清空用户组需要判断如果有组织或者人员模板权限则代表左侧选中的数据还存在，不需要取第一条数据
                const hasData = this.allPermItem.filter((item) => !['personalPerm'].includes(item.id)).some((v) => v.pagination.count > 0);
                bus.$emit('on-exist-other-perm', { isRefreshUser: !hasData });
              }
              // department: async () => {
              //   this.allPermItem = this.initAllPermItem.filter((item) => ['personalPerm', 'userTempPerm'].includes(item.id));
              //   this.allPermItem[0] = Object.assign(this.allPermItem[0], { name: this.$t(`m.perm['用户组权限']`) });
              //   await Promise.all([
              //     this.fetchUserGroupSearch(),
              //     this.fetchPermByTempSearch()
              //   ]);
              //   this.$set(this.permData, 'hasPerm', this.allPermItem.some((v) => v.pagination.count > 0));
              //   this.isOnlyPerm = this.allPermItem.filter((v) => v.pagination.count > 0).length === 1;
              //   this.formatDefaultExpand();
              //   // 清空用户组需要判断如果有组织或者人员模板权限则代表左侧选中的数据还存在，不需要取第一条数据
              //   const hasData = this.allPermItem.filter((item) => !['personalPerm'].includes(item.id)).some((v) => v.pagination.count > 0);
              //   bus.$emit('on-exist-other-perm', { isRefreshUser: !hasData });
              // }
            };
            return typeMap[this.queryGroupData.type]();
          }
        };
        if (routeMap[this.$route.name]) {
          await routeMap[this.$route.name]();
        }
      },

      formatDefaultExpand () {
        const curData = this.allPermItem.find((v) => v.pagination.count > 0);
        this.$nextTick(() => {
          this.allPermItem.forEach((item) => {
            if (curData && curData.id === item.id && this.$refs[`rTemplateItem_${item.id}`]) {
              this.$refs[`rTemplateItem_${item.id}`][0].handleExpanded(false);
              item.expanded = true;
            } else {
              item.expanded = false;
            }
          });
        });
      },

      formatExpandedData (payload) {
        setTimeout(() => {
          this.allPermItem.forEach((item) => {
            if (item.expanded || item.id === payload.mode) {
              const hasRef = this.$refs[`rTemplateItem_${item.id}`];
              if (hasRef && hasRef.length > 0) {
                hasRef[0].handleExpanded(false);
              }
            } else {
              item.expanded = false;
            }
          }, 0);
        });
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

      formatPaginationData (payload, current, limit) {
        const curData = this.allPermItem.find((item) => item.id === payload.id);
        if (curData) {
          const typeMap = {
            personalPerm: async () => {
              curData.pagination = Object.assign(curData, { current, limit });
              await this.fetchUserGroupSearch();
              this.formatExpandedData(curData);
            },
            departPerm: async () => {
              curData.pagination = Object.assign(curData, { current, limit });
              await this.fetchDepartGroupSearch();
              this.formatExpandedData(curData);
            },
            userTempPerm: async () => {
              curData.pagination = Object.assign(curData, { current, limit });
              await this.fetchPermByTempSearch();
              this.formatExpandedData(curData);
            },
            departTempPerm: async () => {
              curData.pagination = Object.assign(curData, { current, limit });
              await this.fetchDepartPermByTempSearch();
              this.formatExpandedData(curData);
            }
          };
          typeMap[curData.id]();
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

      handleRefreshGroup (payload, current) {
        const curData = this.allPermItem.find((item) => item.id === payload.mode);
        this.formatPaginationData(curData, current, curData.pagination.limit);
        this.curSelectedGroup = [];
        this.$emit('on-selected-group', []);
      },

      handleAddGroup (payload) {
        const curData = this.allPermItem.find((item) => item.id === payload.mode);
        this.handleRefreshGroup(payload, curData.pagination.current);
      },

      handleQuitGroup (payload) {
        this.handleRefreshGroup(payload, 1);
      },
  
      handlePageChange (current, payload) {
        const curData = this.allPermItem.find((item) => item.id === payload.id);
        this.formatPaginationData(payload, current, curData.pagination.limit);
      },
  
      handleLimitChange (limit, payload) {
        const curData = this.allPermItem.find((item) => item.id === payload.id);
        curData.current = 1;
        this.formatPaginationData(payload, curData.current, limit);
      },

      handleSetBusQueryData () {
        this.$once('hook:beforeDestroy', () => {
          bus.$off('on-refresh-resource-search');
          bus.$off('on-refresh-template-table');
          bus.$off('on-info-change');
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
        bus.$on('on-info-change', ({ mode }) => {
          const modeMap = {
            userTempPerm: async () => {
              await this.fetchPermByTempSearch();
            },
            departTempPerm: async () => {
              await this.fetchDepartPermByTempSearch();
            }
          };
          if (modeMap[mode]) {
            modeMap[mode]();
          }
        });
        bus.$on('on-refresh-template-table', async (payload) => {
          this.resetPagination();
          await this.fetchInitData();
          this.formatExpandedData(payload);
        });
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
        this.allPermItem.forEach((item) => {
          item.pagination = Object.assign(item.pagination, { current: 1, limit });
        });
      }
    }
  };
</script>
  
<style lang="postcss" scoped>
.user-perm-group {
  position: relative;
  width: 100%;
  height: calc(100% - 190px);
  overflow-y: auto;
  &::-webkit-scrollbar {
    width: 8px;
    background-color: lighten(transparent, 80%);
  }
  &::-webkit-scrollbar-thumb {
    height: 5px;
    border-radius: 2px;
    background-color: #e6e9ea;
  }
  &::-webkit-scrollbar-track {
    background-color: transparent;
    border-radius: 3px;
  }
  /deep/ .resource-perm-side-content-table {
    margin: 12px 0;
    background-color: #ffffff;
    &:hover {
      background-color: #ffffff;
    }
    .header {
      padding-left: 16px;
      height: 46px;
      line-height: 46px;
      .sub-header-item {
        .expanded-icon {
          line-height: 46px;
        }
        &-title {
          margin-left: 12px;
        }
        &-count {
          .count {
            color: #3a84ff;
            font-weight: 700;
          }
        }
      }
    }
  }
  .perm-empty-wrapper {
    position: absolute;
    left: 50%;
    top: 45%;
    transform: translate(-50%, -45%);
  }
  &.is-show-notice {
    height: calc(100% - 230px);
  }
}
</style>
