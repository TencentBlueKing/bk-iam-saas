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
      <bk-table-column :label="$t(`m.userGroup['用户组']`)">
        <template slot-scope="{ row }">
          <div class="user-groups" @click="handleOpen(row.id)">
            <span class="user-groups-name" :title="row.name">
              {{ row.name }}
            </span>
            <i class="user-groups-icon iam-icon iamcenter-jump-link" />
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
                  <div class="popover-title-text">
                    {{ $t(`m.dialog['确认解除与该用户组的关联？']`) }}
                  </div>
                </div>
                <div class="popover-content">
                  <div class="popover-content-item">
                    <span class="popover-content-item-label"
                    >{{ $t(`m.memberTemplate['用户组名称']`) }}:</span
                    >
                    <span class="popover-content-item-value"> {{ row.name }}</span>
                  </div>
                  <div class="popover-content-tip">
                    {{
                      $t(`m.memberTemplate['解除关联后，相关人员将失去用户组的权限。']`)
                    }}
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
  import { bus } from '@/common/bus';
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
            page: current,
            page_size: limit,
            name: this.groupValue,
            id: this.curDetailData.id
          };
          const { code, data } = await this.$store.dispatch('memberTemplate/getSubjectTemplatesGroups', params);
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

      async handleConfirmDisassociate ({ id }) {
        try {
          const params = {
            group_id: id,
            id: this.curDetailData.id
          };
          const { code } = await this.$store.dispatch('memberTemplate/deleteSubjectTemplateGroups', params);
          if (code === 0) {
            this.messageSuccess(this.$t(`m.memberTemplate['解除关联成功']`), 3000);
            this.pagination.current = 1;
            await this.fetchAssociateGroup(true);
            const params = {
              ...this.curDetailData,
              ...{
                group_count: this.pagination.count
              }
            };
            bus.$emit('on-related-change', params);
            // 用户/组织模块在模板详情里解除关联用户组需要同步更新各种方式加入的用户组权限
            if (['userOrgPerm'].includes(this.$route.name)) {
              bus.$emit('on-refresh-template-table', params);
            }
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
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
