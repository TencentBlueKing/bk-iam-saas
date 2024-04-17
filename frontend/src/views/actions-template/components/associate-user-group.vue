<template>
  <div class="associate-user-group">
    <div class="associate-user-group-search">
      <bk-input
        clearable
        :placeholder="$t(`m.memberTemplate['搜索用户组']`)"
        :right-icon="'bk-icon icon-search'"
        v-model="groupValue"
        @enter="handleSearchGroup"
        @clear="handleEmptyClear"
        @right-icon-click="handleSearchGroup"
      />
    </div>
    <bk-table
      size="small"
      ext-cls="associate-user-group-table"
      :data="groupTableList"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column :label="$t(`m.userGroup['用户组名']`)">
        <template slot-scope="{ row }">
          <div class="user-groups" @click="handleOpen(row.id)">
            <span class="user-groups-name" v-bk-tooltips="{ content: row.name, placement: 'right-start' }">
              {{ row.name }}
            </span>
          </div>
        </template>
      </bk-table-column>
      <template slot="empty">
        <ExceptionEmpty
          :type="emptyTableData.type"
          :empty-text="emptyTableData.text"
          :tip-text="emptyTableData.tip"
          :tip-type="emptyTableData.tipType"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </template>
    </bk-table>
  </div>
</template>

<script>
  import { formatCodeData } from '@/common/util';
  export default {
    props: {
      curDetailData: {
        type: Object
      }
    },
    data () {
      return {
        tableLoading: false,
        groupValue: '',
        groupTableList: [],
        pagination: {
          current: 1,
          limit: 10,
          count: 0
        },
        emptyTableData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    methods: {
      async fetchAssociateGroup (tableLoading = false) {
        this.tableLoading = tableLoading;
        try {
          const { current, limit } = this.pagination;
          const params = {
            types: 'group',
            limit,
            offset: limit * (current - 1),
            name: this.groupValue,
            id: this.curDetailData.id
          };
          const { code, data } = await this.$store.dispatch('permTemplate/getTemplateMember', params);
          const { count, results } = data;
          this.pagination.count = count || 0;
          this.groupTableList = results || [];
          this.emptyTableData = formatCodeData(code, this.emptyTableData, this.groupTableList.length === 0);
        } catch (e) {
          this.groupTableList = [];
          this.emptyTableData = formatCodeData(0, this.emptyTableData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
          this.$emit('on-associate-change', { count: this.pagination.count });
        }
      },

      handleSearchGroup () {
        this.emptyTableData.tipType = 'search';
        this.fetchAssociateGroup(true);
      },

      handleClearGroup () {
        this.groupValue = '';
        this.emptyTableData.tipType = '';
        this.fetchAssociateGroup(true);
      },

      async handlePageChange (page) {
        this.pagination = Object.assign(this.pagination, { current: page });
        await this.fetchAssociateGroup(true);
      },

      async handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit });
        await this.fetchAssociateGroup(true);
      },

      handleOpen (id) {
        const routeData = this.$router.resolve({
          path: `user-group-detail/${id}`,
          query: {
            noFrom: true
          }
        });
        window.open(routeData.href, '_blank');
      },

      handleEmptyClear () {
        this.emptyTableData.tipType = '';
        this.groupValue = '';
        this.resetPagination();
        this.fetchAssociateGroup(true);
      },

      handleEmptyRefresh () {
        this.resetPagination();
        this.fetchAssociateGroup(true);
      },

      resetPagination () {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 10 });
      }
    }
  };
</script>

<style lang="postcss" scoped>
.associate-user-group {
  padding: 0 24px;
  &-search {
    position: static;
    top: 0;
  }
  &-table {
    margin-top: 16px;
    border-bottom: 0;
    border-right: 0;
    .user-groups {
      display: flex;
      align-items: center;
      color: #3a84ff;
      .user-groups-icon {
        display: none;
      }
      &:hover {
        cursor: pointer;
        .user-groups-icon {
          display: block;
          margin-left: 5px;
        }
      }
    }
  }
}
</style>
