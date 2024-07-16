<template>
  <div
    :class="[
      'perm-group-all-content',
      { 'is-show-notice': showNoticeAlert && showNoticeAlert() }
    ]"
  >
    <template v-if="permData.hasPerm">
      <RenderPermItem
        v-for="(item, index) in allPermItem"
        :key="index"
        :ref="`rTemplateItem_${item.id}`"
        :mode="'detail'"
        :title="item.name"
        :count="item.pagination.count"
        :expanded.sync="item.expanded"
        :ext-cls="formatExtCls(index)"
        :class="[
          'resource-perm-side-content-table',
          { 'is-show-perm': isShowPerm(item) && item.pagination.count > 0 }
        ]"
        @on-expanded="handleExpanded(...arguments, item, index)"
      >
        <template v-if="item.pagination.count > 0">
          <div slot="headerTitle" class="single-hide header-content">
            <span class="header-content-title">{{ item.name }}</span>
            <span class="header-content-count">
              ({{ $t(`m.common['共']`) }}
              <span class="count">{{ formatPermItemLen(item) }}</span>
              {{ $t(`m.common['条']`) }})
            </span>
          </div>
          <component
            ref="childPermTable"
            :key="comKey"
            :is="curCom(item.id)"
            :mode="item.id"
            :is-loading="item.loading"
            :is-search-perm="isSearchResource"
            :is-has-handover="isHasHandover"
            :pagination="item.pagination"
            :cur-search-params="curSearchParams"
            :group-data="groupData"
            :list="item.list"
            :cur-selected-group="curSelectedGroup"
            :delete-confirm-data="deleteConfirmData"
            :empty-data="item.emptyData"
            @on-page-change="handlePageChange(...arguments, item)"
            @on-limit-change="handleLimitChange(...arguments, item)"
            @on-selected-group="handleSelectedGroup"
            @on-quit-group="handleQuitGroup"
            @on-clear="handleEmptyClear"
            @on-refresh="handleEmptyRefresh"
          />
        </template>
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
  import { existValue, formatCodeData, sleep } from '@/common/util';
  import RenderPermItem from '@/components/iam-expand-perm/index.vue';
  import CustomPermPolicy from './custom-perm-policy.vue';
  import GroupPermTable from './group-perm-table.vue';
  export default {
    inject: ['showNoticeAlert'],
    components: {
      RenderPermItem,
      CustomPermPolicy,
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
        comKey: -1,
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
            list: [],
            listBack: []
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
            list: [],
            listBack: []
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
            list: [],
            listBack: []
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
            list: [],
            listBack: []
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
            list: [],
            listBack: []
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
            list: [],
            listBack: []
          }
        ],
        allPermItemBack: [],
        curSelectedGroup: [],
        queryGroupData: {},
        curSearchParams: {},
        deleteConfirmData: {
          label: this.$t(`m.access['系统名称']`),
          title: this.$t(`m.dialog['确认清空该系统的权限？']`),
          tip: this.$t(`m.perm['清空后，该系统的所有操作权限和资源实例权限都会被清空。']`),
          btnTitle: this.$t(`m.common['清空权限']`)
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
      ...mapGetters(['user', 'externalSystemsLayout', 'externalSystemId', 'mainContentLoading']),
      curCom () {
        return (payload) => {
          let com = '';
          const list = new Map([
            [['personalPerm', 'departPerm', 'userTempPerm', 'departTempPerm', 'managerPerm'], 'GroupPermTable'],
            [['customPerm'], 'CustomPermPolicy']
          ]);
          for (const [key, value] of list.entries()) {
            if (key.includes(payload)) {
              com = value;
              break;
            }
          }
          return com;
        };
      },
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
          const { pagination, id } = this.allPermItem[index];
          const len = pagination.count;
          if (!len) {
            return 'no-perm-item-wrapper';
          }
          return `iam-${id}-ext-cls`;
        };
      },
      formatPermLength () {
        const len = this.allPermItem.filter((item) => item.pagination.count > 0).length;
        return len;
      },
      formatPermItemLen () {
        return (payload) => {
          // 处理一个展开项有多个表格，需要求和
          const isMulti = ['customPerm'].includes(payload.id);
          const typeMap = {
            true: () => {
               const countList = payload.list.map((v) => v.count);
               payload.pagination.count = countList.reduce((prev, cur) => {
                return cur + prev;
              }, 0);
              return payload.pagination.count;
            },
            false: () => {
              return payload.pagination.count;
            }
          };
          if (typeMap[isMulti]) {
            return typeMap[isMulti]();
          }
        };
      }
    },
    watch: {
      groupData: {
        handler (value) {
          this.queryGroupData = cloneDeep(value);
          this.handleSelectedGroup([]);
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
          let url = '';
          let params = {};
          if (this.isSearchResource) {
            url = 'perm/getUserGroupSearch';
            params = {
              ...this.curSearchParams,
              limit,
              offset: limit * (current - 1)
            };
          } else {
            url = 'perm/getPersonalGroups';
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
          const totalCount = data.count || 0;
          const tableList = data.results || [];
          curData = Object.assign(curData, {
            list: tableList,
            listBack: tableList,
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(curData.emptyData);
          // 跨页全选
          this.handleGetSelectedGroups(curData.id);
        } catch (e) {
          this.emptyPermData = formatCodeData(e.code, emptyData);
          curData = Object.assign(curData, {
            list: [],
            listBack: [],
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
          let url = '';
          let params = {};
          if (this.isSearchResource) {
            url = 'perm/getDepartGroupSearch';
            params = {
             ...this.curSearchParams,
             limit,
             offset: limit * (current - 1)
            };
          } else {
            url = 'perm/getDepartMentsPersonalGroups';
          }
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, params);
          // 搜索接口是后台分页
          if (data.hasOwnProperty('count')) {
            curData = Object.assign(curData, {
              list: data.results || [],
              listBack: data.results || [],
              emptyData: formatCodeData(code, emptyData, data.count === 0),
              pagination: { ...pagination, ...{ count: data.count } }
            });
          } else {
            curData = Object.assign(curData, {
              list: data || [],
              listBack: data || [],
              emptyData: formatCodeData(code, emptyData, data.length === 0),
              pagination: { ...pagination, ...{ count: data.length } }
            });
            this.handleGetDataByPage(current, curData);
          }
          this.emptyPermData = formatCodeData(code, emptyData);
          this.handleGetSelectedGroups(curData.id);
        } catch (e) {
          curData = Object.assign(curData, {
            list: [],
            listBack: [],
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
            listBack: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(curData.emptyData);
          this.handleGetSelectedGroups(curData.id);
        } catch (e) {
          curData = Object.assign(curData, {
            list: [],
            listBack: [],
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
            listBack: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          this.emptyPermData = cloneDeep(curData.emptyData);
          this.handleGetSelectedGroups(curData.id);
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
          const result = (data || []).map((v) => {
            return {
              ...v,
              ...{
                expanded: true
              }
            };
          });
          curData = Object.assign(curData, {
            list: result || [],
            listBack: result || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
          console.log(curData);
          this.handleGetSelectedGroups(curData.id);
        } catch (e) {
          curData = Object.assign(curData, {
            list: [],
            listBack: [],
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
          this.handleGetSelectedGroups(curData.id);
        } catch (e) {
          curData = Object.assign(curData, {
            list: [],
            emptyData: formatCodeData(e.code, emptyData),
            pagination: { ...pagination, ...{ count: 0 } }
          });
          this.messageAdvancedError(e);
        } finally {
          sleep(300).then(() => {
            curData.loading = false;
          });
        }
      },

      // 获取即将过期的用户组权限
      async fetchExpiredGroupPerm () {
        let url = 'renewal/getExpireSoonGroupWithUser';
        let params = {
          page: 1,
          page_size: 10
        };
        if (this.externalSystemId) {
          params.system_id = this.externalSystemId;
          params.hidden = false;
        }
        if (['renewalPerm'].includes(this.queryGroupData.value)) {
          let curData = this.allPermItem.find((v) => ['personalPerm'].includes(v.id));
          if (!curData) {
            return;
          }
          const { emptyData, pagination } = curData;
          try {
            curData.loading = true;
            const { current, limit } = pagination;
            if (this.isSearchResource) {
              url = 'renewal/getExpireSoonGroupWithUser';
              params = {
                ...this.curSearchParams,
                page: current,
                page_size: limit
              };
            }
            const { code, data } = await this.$store.dispatch(url, params);
            const totalCount = data.count || 0;
            const tableList = data.results || [];
            curData = Object.assign(curData, {
              list: tableList,
              listBack: tableList,
              emptyData: formatCodeData(code, emptyData, totalCount === 0),
              pagination: { ...pagination, ...{ count: totalCount } }
            });
            this.renewalGroupPermLen = totalCount;
            this.emptyPermData = cloneDeep(curData.emptyData);
            // 跨页全选
            this.handleGetSelectedGroups(curData.id);
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
        } else {
          try {
            const { data } = await this.$store.dispatch(url, params);
            this.renewalGroupPermLen = data.count || 0;
          } catch (e) {
            this.messageAdvancedError(e);
          }
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
        let defaultExpandItem = [];
        const typeMap = {
          all: async () => {
            defaultExpandItem = ['personalPerm'];
            const externalReqList = [
              this.fetchExpiredGroupPerm(),
              this.fetchUserGroupSearch(),
              this.fetchDepartGroupSearch(),
              this.fetchUserPermByTempSearch(),
              this.fetchDepartPermByTempSearch()
            ];
            const noExternalReqList = [
              this.fetchExpiredCustomPerm(),
              this.fetchCustomPermSearch(),
              this.fetchManagerPermSearch()
            ];
            // 是否有可交接数据
            if (this.isHideApply) {
              await Promise.all(externalReqList);
              this.isHasHandover = this.allPermItem.filter((item) => ['personalPerm'].includes(item.id)).some((v) => v.pagination.count > 0);
            } else {
              await Promise.all([...externalReqList, ...noExternalReqList]);
              this.isHasHandover = this.allPermItem.filter((item) => ['personalPerm', 'customPerm', 'managerPerm'].includes(item.id)).some((v) => v.pagination.count > 0);
            }
            this.$set(this.permData, 'hasPerm', this.allPermItem.some((v) => v.pagination.count > 0));
          },
          renewalPerm: async () => {
            defaultExpandItem = ['personalPerm', 'customPerm'];
            const initReqList = [
              this.fetchExpiredGroupPerm(),
              this.fetchExpiredCustomPerm(),
              // this.fetchUserGroupSearch(),
              this.fetchCustomPermSearch()
            ];
            await Promise.all(initReqList);
          },
          personalPerm: async () => {
            defaultExpandItem = ['personalPerm'];
            const initReqList = [
              this.fetchUserGroupSearch(),
              this.fetchExpiredGroupPerm()
            ];
            await Promise.all(initReqList);
          },
          departPerm: async () => {
            defaultExpandItem = ['departPerm'];
            const initReqList = [
              this.fetchDepartGroupSearch()
            ];
            await Promise.all(initReqList);
          },
          memberTempPerm: async () => {
            defaultExpandItem = ['userTempPerm', 'departTempPerm'];
            const initReqList = [
              this.fetchUserPermByTempSearch(),
              this.fetchDepartPermByTempSearch()
            ];
            await Promise.all(initReqList);
          },
          customPerm: async () => {
            defaultExpandItem = ['customPerm'];
            const initReqList = [
              this.fetchCustomPermSearch()
            ];
            await Promise.all(initReqList);
          },
          managerPerm: async () => {
            defaultExpandItem = ['managerPerm'];
            const initReqList = [
              this.fetchManagerPermSearch()
            ];
            await Promise.all(initReqList);
          }
        };
        if (typeMap[this.queryGroupData.value]) {
          await typeMap[this.queryGroupData.value]();
          // 全部权限选项涉及蓝盾交互单独处理
          if (!['all'].includes(this.queryGroupData.value)) {
            const curPermData = this.allPermItem.filter((item) => defaultExpandItem.includes(item.id));
            this.isHasHandover = curPermData.some((v) => v.pagination.count > 0);
            this.$set(this.permData, 'hasPerm', this.isHasHandover);
          }
          bus.$emit('on-update-all-perm', {
            allPerm: this.allPermItem,
            renewalGroupPermLen: this.renewalGroupPermLen,
            renewalCustomPermLen: this.renewalCustomPermLen
          });
          this.handleDefaultExpand(defaultExpandItem);
        }
      },

      handleGetSelectedGroups (payload) {
        setTimeout(() => {
          const tableRefList = this.$refs.childPermTable;
          const curData = this.allPermItem.find((item) => item.id === payload);
          const curSelectedId = this.curSelectedGroup.map((item) => `${item.id}&${item.name}&${item.mode_type}`);
          if (curData && tableRefList && tableRefList.length > 0) {
            const curTableRef = tableRefList.find((v) => v.mode === curData.id);
            if (curTableRef) {
              curData.list.forEach((item) => {
                this.$set(item, 'mode_type', curData.id);
                if (tableRefList && tableRefList.length > 0) {
                  if (curSelectedId.includes(`${item.id}&${item.name}&${item.mode_type}`)) {
                    curTableRef.$refs[`groupPermRef_${curData.id}`].toggleRowSelection(item, true);
                  }
                }
              });
              curTableRef.fetchCustomTotal && curTableRef.fetchCustomTotal(this.curSelectedGroup, curData.id);
            }
          }
        }, 0);
      },

      handleDefaultExpand (payload) {
        this.$nextTick(() => {
          this.allPermItem.forEach((item) => {
            const permRef = this.$refs[`rTemplateItem_${item.id}`];
            if (permRef && permRef.length && payload.includes(item.id)) {
              item.expanded = true;
            } else {
              item.expanded = false;
            }
          });
        });
      },

      handleGetDataByPage (page, payload) {
        const curData = this.allPermItem.find((item) => item.id === payload.id);
        if (!curData) {
          return;
        }
        if (!page) {
          payload.pagination.current = page = 1;
        }
        let startIndex = (page - 1) * payload.pagination.limit;
        let endIndex = page * payload.pagination.limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > payload.listBack.length) {
          endIndex = payload.listBack.length;
        }
        return payload.listBack.slice(startIndex, endIndex);
      },

      handleGetPaginationData (payload, current, limit) {
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
        if (!value) {
          const selectedGroup = this.curSelectedGroup.filter((v) => v.mode_type !== payload.id);
          this.handleSelectedGroup(selectedGroup);
          bus.$emit('on-remove-toggle-checkbox', selectedGroup);
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
        if (curData) {
          this.handleGetPaginationData(curData, current, curData.pagination.limit);
          this.handleSelectedGroup([]);
        }
      },

      handleQuitGroup (payload) {
        this.handleRefreshGroup(payload, 1);
      },
  
      handlePageChange (current, payload) {
        const curData = this.allPermItem.find((item) => item.id === payload.id);
        if (curData) {
          this.handleGetPaginationData(payload, current, curData.pagination.limit);
        }
      },
  
      handleLimitChange (limit, payload) {
        const curData = this.allPermItem.find((item) => item.id === payload.id);
        if (curData) {
          curData.current = 1;
          this.handleGetPaginationData(payload, curData.current, limit);
        }
      },

      handleSetBusQueryData () {
        this.$once('hook:beforeDestroy', () => {
          bus.$off('on-refresh-resource-search');
          bus.$off('on-system-perm');
        });
        bus.$on('on-system-perm', (payload) => {
          const { active } = payload;
          const curData = this.allPermItem.find((v) => v.id === active);
          if (curData) {
            this.fetchInitData();
          }
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
.perm-group-all-content {
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
      padding-left: 13px;
      height: 46px;
      line-height: 46px;
      .sub-header-content {
        .expanded-icon {
          line-height: 46px !important;
        }
        .header-content {
          width: 100%;
          &-title {
            font-size: 12px;
            font-weight: 700;
            color: #313238;
            margin-left: 9px;
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
    &.is-show-perm {
      display: block;
    }
    &.iam-customPerm-ext-cls {
      padding-bottom: 24px;
    }
    &.is-not-expanded {
      padding-bottom: 0;
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
