<template>
  <div class="user-org-wrapper">
    <div class="user-org-wrapper-search">
      <IamResourceCascadeSearch
        ref="iamResourceSearchRef"
        :custom-class="'user-org-resource-perm'"
        :active="active"
        :is-full-screen="true"
        :search-select-place-holder="$t(`m.userOrOrg['输入ID、用户组名、用户名、组织名、描述等按回车进行搜索']`)"
        :cur-search-data="searchData"
        @on-remote-table="handleRemoteTable"
        @on-refresh-table="handleRefreshTable"
        @on-input-value="handleInputValue"
      />
    </div>
    <div class="user-org-wrapper-content">
      <Layout>
        <div class="user-org-wrapper-content-left" :style="leftStyle">
          <LeftLayout
            :loading="listLoading"
            :list="groupList"
            :group-data="currentGroupData"
            :cur-select-active="curSelectActive"
            :can-scroll-load="canScrollLoad"
            :empty-data="emptyData"
            @on-select="handleSelectUser"
            @on-load-more="handleLoadMore"
            @on-clear="handleEmptyUserClear"
            @on-refresh="handleEmptyUserRefresh"
          />
        </div>
        <div slot="right" class="user-org-wrapper-content-right">
          <component
            :key="comKey"
            :is="curCom"
            :is-search-perm="isSearchPerm"
            :group-data="currentGroupData"
            :cur-search-params="curSearchParams"
            :cur-search-pagination="curSearchPagination"
            @on-clear="handleEmptyClear"
            @on-refresh="handleEmptyRefresh"
          />
        </div>
      </Layout>
    </div>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { bus } from '@/common/bus';
  import { formatCodeData } from '@/common/util';
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';
  import Layout from './components/page-layout';
  import LeftLayout from './components/left-layout.vue';
  import RightLayout from './components/right-layout.vue';

  const COM_MAP = new Map([
    [['user', 'department'], 'RightLayout']
  ]);

  export default {
    components: {
      IamResourceCascadeSearch,
      Layout,
      LeftLayout,
      RightLayout
    },
    data () {
      return {
        listLoading: false,
        isSearchPerm: false,
        comKey: -1,
        curSearchParams: {},
        curSearchPagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        active: '',
        curSelectActive: '',
        groupList: [],
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.userGroup['用户/组织名']`),
            default: true
          },
          {
            id: 'id',
            name: 'ID',
            default: true
          },
          {
            id: 'description',
            name: this.$t(`m.common['描述']`),
            default: true
          }
        ],
        currentBackup: 1,
        pageConf: {
          current: 1,
          limit: 10,
          totalPage: 1,
          count: 0
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        curEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        currentGroupData: {},
        dragWidth: 224
      };
    },
    computed: {
      leftStyle () {
        if (this.dragWidth > 0) {
          return {
            flexBasis: `${this.dragWidth}px`
          };
        }
        return {
          flexBasis: '224px'
        };
      },
      canScrollLoad () {
        return this.pageConf.totalPage > this.currentBackup;
      },
      listHeight () {
        return window.innerHeight - 51 - 51 - 157 - 42 - 8;
      },
      curCom () {
        let com = '';
        for (const [key, value] of this.comMap.entries()) {
          if (Object.keys(this.currentGroupData).length && key.includes(this.currentGroupData.type)) {
            com = value;
            break;
          }
        }
        return com;
      }
    },

    async created () {
      this.comMap = COM_MAP;
      this.pageConf.limit = Math.ceil(this.listHeight / 36);
      await this.fetchInitData();
    },

    methods: {
      async fetchInitData () {
        this.pageConf.current = 1;
        await this.fetchGroupMemberList(true, false);
        if (this.groupList.length) {
          const { id, name } = this.groupList[0];
          this.curSelectActive = `${id}&${name}`;
        }
      },

      async fetchGroupMemberList (isLoading = false, isScrollLoad = false) {
        this.listLoading = isLoading;
        try {
          const { current, limit } = this.pageConf;
          let params = {
            page: current,
            page_size: limit
          };
          if (this.isSearchPerm) {
            params = {
              ...params,
              ...{
                name: this.curSearchParams.name || ''
              }
            };
          }
          const { code, data } = await this.$store.dispatch('userOrOrg/getUserGroupMemberList', params);
          const { count, results } = data;
          const list = results || [];
          this.pageConf.count = count || 0;
          if (!isScrollLoad) {
            this.groupList = [...list];
            this.currentGroupData = this.groupList.length ? this.groupList[0] : {};
            this.pageConf.totalPage = Math.ceil(this.pageConf.count / limit);
          } else {
            this.currentBackup++;
            this.groupList.push(...results);
          }
          this.handleRefreshTipType('emptyData');
          this.emptyData = formatCodeData(code, this.emptyData, this.groupList.length === 0);
        } catch (e) {
          this.groupList = [];
          this.handleRefreshTipType('emptyData');
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.listLoading = false;
        }
      },

      async handleLoadMore () {
        this.pageConf.current++;
        await this.fetchGroupMemberList(false, true);
      },

      async handleRemoteTable (payload) {
        const { emptyData, pagination, searchParams, isNoTag } = payload;
        this.isSearchPerm = emptyData.tipType === 'search';
        this.curSearchParams = cloneDeep(searchParams);
        this.curSearchPagination = cloneDeep(pagination);
        if (!isNoTag) {
          this.curEmptyData = cloneDeep(emptyData);
          await this.fetchRemoteTable();
        }
      },

      async fetchRemoteTable () {
        await this.fetchInitData();
        bus.$emit('on-refresh-resource-search', {
          isSearchPerm: true,
          curSearchParams: this.curSearchParams,
          curSearchPagination: this.curSearchPagination
        });
      },

      // 处理只输入纯文本，不生成tag情况
      async handleInputValue (payload) {
        this.curEmptyData.tipType = payload ? 'search' : '';
        if (payload && !this.curSearchParams.system_id) {
          this.isSearchPerm = true;
          this.$set(this.curSearchParams, 'name', payload);
          await this.fetchRemoteTable();
        }
      },

      handleSelectUser (payload) {
        this.currentGroupData = payload;
      },

      handleRefreshTable () {
        this.curEmptyData.tipType = '';
        this.isSearchPerm = false;
        this.curSearchParams = {};
        bus.$emit('on-refresh-resource-search', {
          isSearchPerm: false
        });
      },

      handleRefreshTipType (payload) {
        let tipType = '';
        if (this.isSearchPerm) {
          tipType = 'search';
        }
        if (this[payload].type === 500) {
          tipType = 'refresh';
        }
        this.emptyData = Object.assign({}, this[payload], { tipType });
      },
      
      handleEmptyRefresh () {
        this.isSearchPerm = false;
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyRefresh();
      },

      handleEmptyClear () {
        this.isSearchPerm = false;
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyClear();
      },

      handleEmptyUserClear () {
        this.emptyData.tipType = 'search';
        this.isSearchPerm = false;
        this.pageConf.current = 1;
        this.fetchGroupMemberList(true, false);
      },

      handleEmptyUserRefresh () {
        this.handleEmptyUserClear();
      }
    }
  };
</script>

<style lang="postcss" scoped>
.user-org-wrapper {
  padding: 0;
  color: #313238;
  &-search {
    box-shadow: 0 2px 3px 0 #0000000a;
    position: sticky;
    top: 0;
    z-index: 1;
  }
  .user-org-wrapper-content {
    &-left {
      padding: 0 16px;
      background-color: #FAFBFD;
      border-right: 1px solid#dcdee5;
      height: 100%;
    }
    /* &-right {
      height: 100%;
    } */
  }
}
</style>
