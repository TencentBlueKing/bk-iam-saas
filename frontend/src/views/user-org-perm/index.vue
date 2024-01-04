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
      <div class="user-org-wrapper-content-left" :style="leftStyle">
        <LeftLayout
          :empty-data="emptyData"
          :list="groupList"
        />
      </div>
      <div class="user-org-wrapper-content-right" :style="rightStyle">
        <RightLayout />
      </div>
    </div>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { formatCodeData } from '@/common/util';
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';
  import LeftLayout from './components/left-layout.vue';
  import RightLayout from './components/right-layout.vue';
  export default {
    components: {
      IamResourceCascadeSearch,
      LeftLayout,
      RightLayout
    },
    data () {
      return {
        isSearchPerm: false,
        curSearchParams: {},
        curSearchPagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        active: '',
        groupList: [],
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.userGroup['用户组名']`),
            default: true
          },
          {
            id: 'id',
            name: 'ID',
            default: true
          },
          {
            id: 'user_name',
            name: this.$t(`m.common['用户名']`),
            default: true
          },
          {
            id: 'department_name',
            name: this.$t(`m.common['组织名']`),
            default: true
          },
          {
            id: 'description',
            name: this.$t(`m.common['描述']`),
            default: true
          }
        ],
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        dragWidth: 240
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
          flexBasis: '240px'
        };
      },
      rightStyle () {
        if (this.dragWidth > 0) {
          return {
            width: `calc(100% - ${this.dragWidth}px)`
          };
        }
        return {
          width: `calc(100% - 240px)`
        };
      }
    },

    created () {},

    methods: {

      async fetchGroupMemberList () {
        this.listLoading = true;
        try {
          const { current, limit } = this.pageConf;
          const params = {
            page: current,
            page_size: limit
          };
          const { code, data } = await this.$store.dispatch('userOrOrg/getUserGroupMemberList', params);
          const { count, results } = data;
          if (results.length) {
            results.forEach((item) => {
              item.checked = false;
            });
          }
          const list = results || [];
          this.pageConf.count = count || 0;
          this.groupList = [...this.groupList, ...list];
          this.emptyData = formatCodeData(code, this.emptyData, this.groupList.length === 0);
        } catch (e) {
          this.groupList = [];
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.listLoading = false;
        }
      },

      async handleRemoteTable (payload) {
        if (!this.mainContentLoading) {
          this.componentLoading = true;
        }
        const { emptyData, pagination, searchParams, isNoTag } = payload;
        this.isSearchPerm = emptyData.tipType === 'search';
        this.curSearchParams = cloneDeep(searchParams);
        this.curSearchPagination = cloneDeep(pagination);
        if (!isNoTag) {
          this.curEmptyData = cloneDeep(emptyData);
          await this.fetchRemoteTable();
          this.formatCheckGroups();
        }
      },

      async fetchRemoteTable (isRefreshCurCount = false) {},

      // 处理只输入纯文本，不生成tag情况
      async handleInputValue (payload) {
        this.curEmptyData.tipType = payload ? 'search' : '';
        if (payload && !this.curSearchParams.system_id) {
          this.isSearchPerm = true;
          this.$set(this.curSearchParams, 'name', payload);
          await this.fetchRemoteTable();
          this.formatCheckGroups();
        }
      },

      handleRefreshTable () {
        this.curEmptyData.tipType = '';
        this.isSearchPerm = false;
        this.curSearchParams = {};
        this.tabKey = +new Date();
      // this.fetchData(true);
      },

      formatCheckGroups () {
        const selectList = this.panels[0].selectList.map((item) => item.id.toString());
        setTimeout(() => {
          this.personalGroupList.length
            && this.personalGroupList.forEach((item) => {
              item.role_members = this.formatRoleMembers(item.role_members);
              if (selectList.includes(item.id.toString())
                && this.$refs.childPermRef
                && this.$refs.childPermRef.length) {
                this.$refs.childPermRef[0].$refs.groupPermTableRef.toggleRowSelection(item, true);
              }
            });
          if (this.departmentGroupList && this.departmentGroupList.length) {
            this.departmentGroupList.forEach((item) => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          }
          if (this.memberTempByUserList && this.memberTempByUserList.length) {
            this.memberTempByUserList.forEach((item) => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          }
          if (this.memberTempByDepartList && this.memberTempByDepartList.length) {
            this.memberTempByDepartList.forEach((item) => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          }
        }, 0);
      }
    }
  };
</script>

<style lang="postcss" scoped>
.user-org-wrapper {
  padding: 0;
  &-search {
    box-shadow: 0 2px 3px 0 #0000000a;
  }
  .user-org-wrapper-content {
    &-left {
      padding-left: 16px;
      background-color: #fafbfd;
    }
  }
  .group-search-select {
    padding-bottom: 0;
  }
}
</style>
