<template>
  <div
    :class="[
      'user-perm-group',
      { 'is-show-notice': showNoticeAlert && showNoticeAlert() }
    ]"
  >
    <template v-if="permData.hasPerm">
      <RenderPermItem
        v-for="(item, index) in allPermItem"
        :key="index"
        :class="[
          'resource-perm-side-content-table',
          { 'is-show-perm': isShowPerm(item) && item.pagination.count > 0 }
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
          :is-has-handover="isHasHandover"
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
      <div class="perm-empty-wrapper" v-if="isHasHandover">
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
  import { existValue, formatCodeData, sleep } from '@/common/util';
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
          hasPerm: true
        },
        isOnlyPerm: false,
        isSearchResource: false,
        isHasHandover: false,
        totalCount: 0,
        renewalGroupPermLen: 0,
        renewalCustomPermLen: 0,
        allPermItem: [
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
          },
          {
            id: 'customPerm',
            name: this.$t(`m.perm['自定义权限']`),
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
            id: 'managerPerm',
            name: this.$t(`m.perm['管理员权限']`),
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
        allPermItemBack: [],
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
      ...mapGetters(['user', 'roleList', 'externalSystemsLayout', 'externalSystemId', 'mainContentLoading']),
      isHideApply () {
        return this.externalSystemsLayout.myPerm.hideApplyBtn;
      },
      isShowPerm () {
        return (payload) => {
          const typeMap = {
            all: () => {
              return ['personalPerm', 'departPerm', 'userTempPerm', 'departTempPerm', 'customPerm', 'managerPerm'].includes(payload.id);
            },
            renewalPerm: () => {
              return ['personalPerm', 'customPerm'].includes(payload.id);
            },
            personalPerm: () => {
              return ['personalPerm'].includes(payload.id);
            },
            departPerm: () => {
              return ['departPerm'].includes(payload.id);
            },
            memberTempPerm: () => {
              return ['userTempPerm', 'departTempPerm'].includes(payload.id);
            },
            customPerm: () => {
              return ['customPerm'].includes(payload.id);
            },
            managerPerm: () => {
              return ['managerPerm'].includes(payload.id);
            }
          };
          if (typeMap[this.queryGroupData.value]) {
            return typeMap[this.queryGroupData.value]();
          }
          return false;
        };
      },
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
    created () {
      this.allPermItemBack = cloneDeep(this.allPermItem);
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
            page: current,
            page_size: limit
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
          sleep(500).then(() => {
            curData.loading = false;
          });
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
          let totalCount = 0;
          let tableList = [];
          // 搜索接口是后台分页
          if (data.hasOwnProperty('count')) {
            totalCount = data.count;
            tableList = data.results;
          } else {
            totalCount = data.length;
            tableList = data;
          }
          curData = Object.assign(curData, {
            list: tableList || [],
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
          sleep(500).then(() => {
            curData.loading = false;
          });
        }
      },
  
      // 用户人员模板用户组权限
      async fetchUserPermByTempSearch () {
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

      // 获取有权限的所有系统列表
      async fetchCustomPermSearch () {
        if (existValue('externalApp') && this.externalSystemId) {
          return;
        }
        let curData = this.allPermItem.find((item) => item.id === 'customPerm');
        if (!curData) {
          return;
        }
        const { emptyData, pagination } = curData;
        try {
          curData.loading = true;
          const params = {
            ...this.curSearchParams
          };
          const { code, data } = await this.$store.dispatch(
            'permApply/getHasPermSystem',
            params
          );
          const totalCount = data.length || 0;
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

      // 获取管理员权限
      async fetchManagerPermSearch () {
        if (existValue('externalApp') && this.externalSystemId) {
          return;
        }
        let curData = this.allPermItem.find((item) => item.id === 'managerPerm');
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
            offset: (current - 1) * limit,
            with_super: true
          };
          const { code, data } = await this.$store.dispatch(
            'role/getRatingManagerList',
            params
          );
          const totalCount = data.count || 0;
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

      // 获取即将过期的用户组权限
      async fetchExpiredGroupPerm () {
        try {
          const params = {
            page: 1,
            page_size: 10
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
          }
          const { data } = await this.$store.dispatch('renewal/getExpireSoonGroupWithUser', params);
          this.renewalGroupPermLen = data.count || 0;
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      // 获取即将过期的自定义权限
      async fetchExpiredCustomPerm () {
        if (existValue('externalApp') && this.externalSystemId) {
          return;
        }
        try {
          const params = {};
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
          }
          const { data } = await this.$store.dispatch('renewal/getExpireSoonPerm', params);
          this.renewalCustomPermLen = data.length || 0;
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },
  
      async fetchInitData () {
        const typeMap = {
          all: async () => {
            const initReqList = [
              this.fetchUserGroupSearch(),
              this.fetchDepartGroupSearch(),
              this.fetchUserPermByTempSearch(),
              this.fetchDepartPermByTempSearch(),
              this.fetchCustomPermSearch(),
              this.fetchManagerPermSearch(),
              this.fetchExpiredGroupPerm(),
              this.fetchExpiredCustomPerm()
            ];
            await Promise.all(initReqList);
            // 是否有可交接数据
            if (this.isHideApply) {
              this.isHasHandover = this.allPermItem.filter((item) => ['personalPerm'].includes(item.id)).some((v) => v.pagination.count > 0);
            } else {
              this.isHasHandover = this.allPermItem.filter((item) => ['personalPerm', 'customPerm', 'managerPerm'].includes(item.id)).some((v) => v.pagination.count > 0);
            }
            this.$set(this.permData, 'hasPerm', this.allPermItem.some((v) => v.pagination.count > 0));
            bus.$emit('on-update-all-perm', {
              allPerm: this.allPermItem,
              renewalGroupPermLen: this.renewalGroupPermLen,
              renewalCustomPermLen: this.renewalCustomPermLen
            });
            this.handleDefaultExpand();
          },
          renewalPerm: async () => {
            const initReqList = [
              this.fetchUserGroupSearch(),
              this.fetchCustomPermSearch(),
              this.fetchExpiredGroupPerm(),
              this.fetchExpiredCustomPerm()
            ];
            await Promise.all(initReqList);
            const curPermData = this.allPermItem.filter((item) => ['personalPerm', 'customPerm'].includes(item.id));
            this.isHasHandover = curPermData.some((v) => v.pagination.count > 0);
            this.$set(this.permData, 'hasPerm', this.isHasHandover);
            bus.$emit('on-update-all-perm', {
              allPerm: this.allPermItem,
              renewalGroupPermLen: this.renewalGroupPermLen,
              renewalCustomPermLen: this.renewalCustomPermLen
            });
            this.$nextTick(() => {
              this.allPermItem.forEach((item) => {
                const permRef = this.$refs[`rTemplateItem_${item.id}`];
                if (['personalPerm', 'customPerm'].includes(item.id) && permRef && permRef.length) {
                  item.expanded = true;
                }
              });
            });
          },
          personalPerm: async () => {
            const initReqList = [
              this.fetchUserGroupSearch(),
              this.fetchExpiredGroupPerm()
            ];
            await Promise.all(initReqList);
            const curPermData = this.allPermItem.filter((item) => ['personalPerm'].includes(item.id));
            this.isHasHandover = curPermData.some((v) => v.pagination.count > 0);
            this.$set(this.permData, 'hasPerm', this.isHasHandover);
            bus.$emit('on-update-all-perm', {
              allPerm: this.allPermItem,
              renewalGroupPermLen: this.renewalGroupPermLen,
              renewalCustomPermLen: this.renewalCustomPermLen
            });
            this.handleDefaultExpand();
          },
          departPerm: async () => {
            const initReqList = [
              this.fetchDepartGroupSearch()
            ];
            await Promise.all(initReqList);
            const curPermData = this.allPermItem.filter((item) => ['departPerm'].includes(item.id));
            this.isHasHandover = curPermData.some((v) => v.pagination.count > 0);
            this.$set(this.permData, 'hasPerm', this.isHasHandover);
            bus.$emit('on-update-all-perm', {
              allPerm: this.allPermItem,
              renewalGroupPermLen: this.renewalGroupPermLen,
              renewalCustomPermLen: this.renewalCustomPermLen
            });
            this.handleDefaultExpand();
          },
          memberTempPerm: async () => {
            const initReqList = [
              this.fetchUserPermByTempSearch(),
              this.fetchDepartPermByTempSearch()
            ];
            await Promise.all(initReqList);
            const curPermData = this.allPermItem.filter((item) => ['userTempPerm', 'departTempPerm'].includes(item.id));
            this.isHasHandover = curPermData.some((v) => v.pagination.count > 0);
            this.$set(this.permData, 'hasPerm', this.isHasHandover);
            bus.$emit('on-update-all-perm', {
              allPerm: this.allPermItem,
              renewalGroupPermLen: this.renewalGroupPermLen,
              renewalCustomPermLen: this.renewalCustomPermLen
            });
            this.handleDefaultExpand();
          },
          customPerm: async () => {
            const initReqList = [
              this.fetchCustomPermSearch()
            ];
            await Promise.all(initReqList);
            const curPermData = this.allPermItem.filter((item) => ['customPerm'].includes(item.id));
            this.isHasHandover = curPermData.some((v) => v.pagination.count > 0);
            this.$set(this.permData, 'hasPerm', this.isHasHandover);
            bus.$emit('on-update-all-perm', {
              allPerm: this.allPermItem,
              renewalGroupPermLen: this.renewalGroupPermLen,
              renewalCustomPermLen: this.renewalCustomPermLen
            });
            this.handleDefaultExpand();
          },
          managerPerm: async () => {
            const initReqList = [
              this.fetchManagerPermSearch()
            ];
            await Promise.all(initReqList);
            const curPermData = this.allPermItem.filter((item) => ['managerPerm'].includes(item.id));
            this.isHasHandover = curPermData.some((v) => v.pagination.count > 0);
            this.$set(this.permData, 'hasPerm', this.isHasHandover);
            bus.$emit('on-update-all-perm', {
              allPerm: this.allPermItem,
              renewalGroupPermLen: this.renewalGroupPermLen,
              renewalCustomPermLen: this.renewalCustomPermLen
            });
            this.handleDefaultExpand();
          }
        };
        if (typeMap[this.queryGroupData.value]) {
          return typeMap[this.queryGroupData.value]();
        }
      },

      handleDefaultExpand () {
        const curData = this.allPermItem.find((v) => v.pagination.count > 0);
        setTimeout(() => {
          this.allPermItem.forEach((item) => {
            const permRef = this.$refs[`rTemplateItem_${item.id}`];
            if (curData && curData.id === item.id && permRef && permRef.length > 0) {
              permRef[0].handleExpanded(false);
            }
          });
        }, 0);
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
          });
        }, 0);
      },

      formatPaginationData (payload, current, limit) {
        const curData = this.allPermItem.find((item) => item.id === payload.id);
        if (curData) {
          curData.pagination = Object.assign(curData, { current, limit });
          const typeMap = {
            personalPerm: async () => {
              await this.fetchUserGroupSearch();
            },
            departPerm: async () => {
              await this.fetchDepartGroupSearch();
            },
            userTempPerm: async () => {
              await this.fetchUserPermByTempSearch();
            },
            departTempPerm: async () => {
              await this.fetchDepartPermByTempSearch();
            },
            managerPerm: async () => {
              await this.fetchManagerPermSearch();
            }
          };
          return typeMap[curData.id]();
        }
      },

      handleExpanded (value, payload) {
        console.log(value, 415);
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
              await this.fetchUserPermByTempSearch();
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
    display: none;
    &:hover {
      background-color: #ffffff;
    }
    .expand-header {
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
    &.is-show-perm {
      display: block;
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
