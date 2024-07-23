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
        :expanded.sync="item.expanded"
        :count="item.pagination.count"
        :ext-cls="formatExtCls(index)"
        :class="[
          'resource-perm-side-content-table',
          { 'is-show-perm': isShowPerm(item) && item.pagination.count > 0 }
        ]"
        @on-expanded="handleExpanded(...arguments, item, index)"
      >
        <template>
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
            :list="item.list"
            :pagination="item.pagination"
            :empty-data="item.emptyData"
            :is-loading="item.loading"
            :is-search-perm="isSearchResource"
            :is-has-handover="isHasHandover"
            :cur-search-params="curSearchParams"
            :group-data="groupData"
            :renewal-custom-perm="renewalCustomPerm"
            :cur-selected-group="curSelectedGroup"
            :delete-confirm-data="deleteConfirmData"
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
  import { ALL_PERM_GROUP_LIST } from '@/common/constants';
  import { existValue, formatCodeData, getNowTimeExpired, sleep } from '@/common/util';
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
        type: Object
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
        isFirstReq: false,
        isSearchResource: false,
        isHasHandover: false,
        isBatchDelAction: false,
        totalCount: 0,
        renewalGroupPermLen: 0,
        comKey: -1,
        allPermItem: ALL_PERM_GROUP_LIST.map((v) => {
          return {
          ...v,
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
          };
        }),
        allPermItemBack: [],
        curSelectedGroup: [],
        renewalCustomPerm: [],
        defaultExpandItem: [],
        queryGroupData: {},
        curSearchParams: {},
        permData: {
          hasPerm: true
        },
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
            [['personalPerm', 'departPerm', 'userTempPerm', 'departTempPerm', 'managerPerm', 'renewalPersonalPerm'], 'GroupPermTable'],
            [['customPerm', 'renewalCustomPerm'], 'CustomPermPolicy']
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
          let result = '';
          const permList = Object.freeze(new Map([
            [['personalPerm', 'departPerm', 'userTempPerm', 'departTempPerm', 'customPerm', 'managerPerm'], 'all'],
            [['renewalPersonalPerm', 'renewalCustomPerm'], 'renewalPerm'],
            [['personalPerm'], 'personalPerm'],
            [['departPerm'], 'departPerm'],
            [['userTempPerm', 'departTempPerm'], 'memberTempPerm'],
            [['customPerm'], 'customPerm'],
            [['managerPerm'], 'managerPerm']
          ]));
          for (const [key, value] of permList.entries()) {
            if (key.includes(payload.id) && value === this.queryGroupData.value) {
              result = value;
              break;
            }
          }
          return !!result;
        };
      },
      formatExtCls () {
        return (index) => {
          const { pagination, id } = this.allPermItem[index];
          const len = pagination.count;
          // 续期选项的自定义权限
         const isRenewalCustomPerm = ['renewalPerm'].includes(this.groupData.value) && ['renewalCustomPerm'].includes(id);
          if (!len || (isRenewalCustomPerm && !this.renewalCustomPerm.length)) {
            return 'no-perm-item-wrapper';
          }
          return `iam-${id}-ext-cls`;
        };
      },
      formatExpireSoon () {
        return (payload) => {
          const dif = payload - getNowTimeExpired();
          const days = Math.ceil(dif / (24 * 3600));
          return days < 16;
        };
      },
      formatPermLength () {
        const len = this.allPermItem.filter((item) => item.pagination.count > 0).length;
        return len;
      },
      formatPermItemLen () {
        return (payload) => {
          // 处理一个展开项有多个表格，需要求和
          const isMulti = ['customPerm', 'renewalCustomPerm'].includes(payload.id);
          const typeMap = {
            true: () => {
              if (['renewalPerm'].includes(this.groupData.value)) {
                return this.renewalCustomPerm.length;
              } else {
                const countList = payload.list.map((v) => v.count);
                payload.pagination.count = countList.reduce((prev, cur) => {
                 return cur + prev;
               }, 0);
               return payload.pagination.count;
              }
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
        handler (newValue, oldValue) {
          this.isFirstReq = !oldValue;
          this.queryGroupData = cloneDeep(newValue);
          this.curSelectedGroup = [];
          this.handleSelectedGroup([]);
          this.fetchResetData();
          this.comKey = +new Date();
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

      // 获取有权限的所有系统列表
      async fetchCustomPermSearch () {
        if (existValue('externalApp') && this.externalSystemId) {
          return;
        }
        // 是否是续期选项
        const isRenewalPerm = ['renewalPerm'].includes(this.queryGroupData.value);
        let curData = this.allPermItem.find((item) => isRenewalPerm ? ['renewalCustomPerm'].includes(item.id) : ['customPerm'].includes(item.id));
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
                expanded: true,
                pagination: {
                  current: 1,
                  limit: 10,
                  count: v.count
                }
              }
            };
          });
          curData = Object.assign(curData, {
            list: result || [],
            listBack: result || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
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
            listBack: data.results || [],
            emptyData: formatCodeData(code, emptyData, totalCount === 0),
            pagination: { ...pagination, ...{ count: totalCount } }
          });
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
          sleep(300).then(() => {
            curData.loading = false;
          });
        }
      },

      // 获取即将过期的用户组权限
      async fetchExpiredGroupPerm () {
        let curData = this.allPermItem.find((item) => item.id === 'renewalPersonalPerm');
        if (!curData) {
          return;
        }
        const { emptyData, pagination } = curData;
        try {
          curData.loading = true;
          const { current, limit } = pagination;
          const params = {
            page: current,
            page_size: limit
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch('renewal/getExpireSoonGroupWithUser', params);
          this.renewalGroupPermLen = data.count || 0;
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
          curData = Object.assign(curData, {
            list: [],
            listBack: [],
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
          this.renewalCustomPerm = data || [];
          if (['renewalPerm'].includes(this.queryGroupData.value)) {
            const curData = this.allPermItem.find((v) => ['renewalCustomPerm'].includes(v.id));
            if (curData) {
              curData.pagination = Object.assign(curData.pagination, {
                current: 1,
                limit: 10,
                count: this.renewalCustomPerm.length
              });
            }
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },
  
      async fetchInitData () {
        const typeMap = {
          all: async () => {
            this.defaultExpandItem = ['personalPerm'];
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
            bus.$emit('on-update-all-perm', {
              allPerm: this.allPermItem,
              renewalGroupPermLen: this.renewalGroupPermLen,
              renewalCustomPerm: this.renewalCustomPerm,
              isBatchDelAction: this.isBatchDelAction
            });
            this.handleDefaultExpand(this.defaultExpandItem);
          },
          renewalPerm: async () => {
            this.defaultExpandItem = ['renewalPersonalPerm', 'renewalCustomPerm'];
            const initReqList = [
              this.fetchExpiredGroupPerm(),
              this.fetchUserGroupSearch(),
              this.fetchCustomPermSearch(),
              this.fetchExpiredCustomPerm()
            ];
            await Promise.all(initReqList);
            this.handleGetPermData();
          },
          personalPerm: async () => {
            this.defaultExpandItem = ['personalPerm'];
            const initReqList = [
              this.fetchUserGroupSearch(),
              this.fetchExpiredGroupPerm()
            ];
            await Promise.all(initReqList);
            this.handleGetPermData();
          },
          departPerm: async () => {
            this.defaultExpandItem = ['departPerm'];
            const initReqList = [
              this.fetchDepartGroupSearch()
            ];
            await Promise.all(initReqList);
            this.handleGetPermData();
          },
          memberTempPerm: async () => {
            this.defaultExpandItem = ['userTempPerm', 'departTempPerm'];
            const initReqList = [
              this.fetchUserPermByTempSearch(),
              this.fetchDepartPermByTempSearch()
            ];
            await Promise.all(initReqList);
            this.handleGetPermData();
          },
          customPerm: async () => {
            this.defaultExpandItem = ['customPerm'];
            const initReqList = [
              this.fetchCustomPermSearch(),
              this.fetchExpiredCustomPerm()
            ];
            await Promise.all(initReqList);
            this.handleGetPermData();
          },
          managerPerm: async () => {
            this.defaultExpandItem = ['managerPerm'];
            const initReqList = [
              this.fetchManagerPermSearch()
            ];
            await Promise.all(initReqList);
            this.handleGetPermData();
          }
        };
        if (typeMap[this.queryGroupData.value]) {
          if (this.isFirstReq) {
            return typeMap['all']();
          }
          return typeMap[this.queryGroupData.value]();
        }
      },

      handleGetPermData () {
        const curPermData = this.allPermItem.filter((item) => this.defaultExpandItem.includes(item.id));
        this.isHasHandover = curPermData.some((v) => v.pagination.count > 0);
        this.$set(this.permData, 'hasPerm', this.isHasHandover);
        bus.$emit('on-update-all-perm', {
          allPerm: this.allPermItem,
          renewalGroupPermLen: this.renewalGroupPermLen,
          renewalCustomPerm: this.renewalCustomPerm,
          isBatchDelAction: this.isBatchDelAction
        });
        this.handleDefaultExpand(this.defaultExpandItem);
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
          bus.$off('on-update-perm-group');
        });
        bus.$on('on-update-perm-group', async (payload) => {
          // isBatchDelAction代表是批量删除，在全部权限和自定义权限会存在跨系统和跨权限类型勾选，所以需要调用接口更新最新数据
          const { active, count, systemId, isBatchDelAction } = payload;
          const curData = this.allPermItem.find((v) => v.id === active);
          this.isBatchDelAction = isBatchDelAction || false;
          if (curData) {
            curData.pagination.current = 1;
            this.curSelectedGroup = this.curSelectedGroup.filter((v) => v.mode_type !== active);
            if (['renewalPerm'].includes(this.queryGroupData.value)) {
              return;
            }
            if (['customPerm', 'renewalCustomPerm'].includes(active) && !isBatchDelAction) {
              if (systemId) {
                const curSystem = curData.list.find((v) => v.id === systemId);
                if (curSystem) {
                  curSystem.count = count;
                }
              }
              await this.fetchExpiredCustomPerm();
              bus.$emit('on-update-all-perm', {
                allPerm: this.allPermItem,
                renewalGroupPermLen: this.renewalGroupPermLen,
                renewalCustomPerm: this.renewalCustomPerm,
                isBatchDelAction: this.isBatchDelAction
              });
              return;
            }
            this.fetchInitData();
          }
        });
        bus.$on('on-refresh-resource-search', (payload) => {
          const { isSearchPerm, curSearchParams } = payload;
          this.curSearchParams = curSearchParams || {};
          if (!this.curSearchParams.action_id) {
            delete this.curSearchParams.resource_instances;
          }
          Object.keys(this.curSearchParams).forEach((item) => {
            if (['name', 'description', 'id'].includes(item) && !this.curSearchParams[item]) {
              delete this.curSearchParams[item];
            }
          });
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
