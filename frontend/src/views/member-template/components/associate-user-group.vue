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
      ref="sensitivityTableRef"
      ext-cls="associate-user-group-table"
      :data="groupTableList"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column :label="$t(`m.userGroup['用户组']`)">
        <template slot-scope="{ row }">
          <span class="action-name" :title="row.name">
            {{ row.name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)">
        <template slot-scope="{ row }">
          <div>
            <bk-button theme="primary" text @click="handleDisassociate(row)">
              {{ $t(`m.memberTemplate['解除关联']`) }}
            </bk-button>
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
        try {
          console.log(333);
          this.emptyTableData = formatCodeData(0, this.emptyTableData, true);
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      handleSearchGroup (payload) {
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

      async handleLimitChange (currentLimit, prevLimit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: currentLimit });
        await this.fetchAssociateGroup(true);
      },

      handleDisassociate () {},

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
    padding-bottom: 16px;
  }
  &-table {
    margin-top: 16px;
    border-bottom: 0;
    border-right: 0;
  }
}
</style>
