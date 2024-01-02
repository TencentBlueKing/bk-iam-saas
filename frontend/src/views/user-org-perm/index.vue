<template>
  <div class="user-org-perm-wrapper">
    <div class="IamResourceCascadeSearch">
      <IamResourceCascadeSearch
        ref="iamResourceSearchRef"
        :custom-class="'user-org-resource-perm'"
        :active="active"
        :is-full-width="true"
        @on-remote-table="handleRemoteTable"
        @on-refresh-table="handleRefreshTable"
        @on-input-value="handleInputValue"
      />
    </div>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';
  export default {
    components: {
      IamResourceCascadeSearch
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
        active: 'GroupPerm',
        customSelectWidth: window.innerWidth <= 1520 ? '160px' : '3000px'
      };
    },

    created () {
        
    },

    methods: {
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

      handleRefreshTable () {},

      formatCheckGroups () {
        const selectList = this.panels[0].selectList.map(item => item.id.toString());
        setTimeout(() => {
          this.personalGroupList.length && this.personalGroupList.forEach(item => {
            item.role_members = this.formatRoleMembers(item.role_members);
            if (selectList.includes(item.id.toString())
              && this.$refs.childPermRef
              && this.$refs.childPermRef.length) {
              this.$refs.childPermRef[0].$refs.groupPermTableRef.toggleRowSelection(item, true);
            }
          });
          if (this.departmentGroupList && this.departmentGroupList.length) {
            this.departmentGroupList.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          }
          if (this.memberTempByUserList && this.memberTempByUserList.length) {
            this.memberTempByUserList.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          }
          if (this.memberTempByDepartList && this.memberTempByDepartList.length) {
            this.memberTempByDepartList.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          }
        }, 0);
      }
    }
  };
</script>

<style lang="postcss" scoped>
.user-org-perm-wrapper {
  padding: 0;
  .left {
    width: calc(100% - 20px);
  }
}
</style>
