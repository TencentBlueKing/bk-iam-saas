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
      :resize="true"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column :label="$t(`m.userGroup['用户组']`)">
        <template slot-scope="{ row }">
          <div class="user-groups">
            <span class="user-groups-name" :title="row.name">
              {{ row.name }}
            </span>
            <Icon bk type="edit" class="user-groups-icon" @click="handleOpen(row.id)" />
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)" width="150">
        <template slot-scope="{ row }">
          <div>
            <bk-popconfirm
              trigger="click"
              placement="bottom-end"
              ext-popover-cls="disassociate-confirm"
              :confirm-text="$t(`m.memberTemplate['解除']`)"
              @confirm="handleConfirmDisassociate(row)"
            >
              <div slot="content">
                <div class="popover-title">
                  <div class="popover-title-text">{{ $t(`m.dialog['确认解除与该用户组的关联？']`) }}</div>
                </div>
                <div class="popover-content">
                  <div class="popover-content-item">
                    <span class="popover-content-item-label">{{ $t(`m.memberTemplate['用户组名称']`) }}:</span>
                    <span class="popover-content-item-value"> {{ row.name }}</span>
                  </div>
                  <div class="popover-content-tip">
                    {{ $t(`m.memberTemplate['解除关联后，相关人员将失去用户组的权限。']`) }}
                  </div>
                </div>
              </div>
              <bk-button theme="primary" text>
                {{ $t(`m.memberTemplate['解除关联']`) }}
              </bk-button>
            </bk-popconfirm>
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
        groupTableList: [
          {
            id: 1455,
            name: 'adminasasasasasasasasasasasssasadminasasasasasasasasasasasssasasasasadminasasasasasasasasasasasssasasasasasasas'
          }
        ],
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

      async handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit });
        await this.fetchAssociateGroup(true);
      },

      handleConfirmDisassociate () {},

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
    padding-bottom: 16px;
  }
  &-table {
    margin-top: 16px;
    border-bottom: 0;
    border-right: 0;
    .user-groups {
      display: flex;
      align-items: center;
      .user-groups-icon {
        display: none;
      }
      &:hover {
        color: #3a84ff;
        cursor: pointer;
        .user-groups-icon {
          display: block;
          margin-left: 5px;
        }
      }
    }
  }
}
.disassociate-confirm {
  .popover-title {
    font-size: 16px;
    padding-bottom: 16px;
  }
  .popover-content {
    color: #63656e;
    .popover-content-item {
      display: flex;
      &-value {
        color: #313238;
        margin-left: 5px;
      }
    }
    &-tip {
      padding: 6px 0 24px 0;
    }
  }
}
</style>
