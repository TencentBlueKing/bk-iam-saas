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
      <bk-table-column :label="$t(`m.userGroup['用户组名']`)" :show-overflow-tooltip="true">
        <template slot-scope="{ row }">
          <span class="user-groups-name" @click="handleOpen(row.id)">
            {{ row.name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)" width="150">
        <template slot-scope="{ row }">
          <div>
            <bk-popconfirm
              trigger="click"
              :ref="`removeSyncGroupConfirm_${row.name}_${row.id}`"
              placement="bottom-end"
              ext-popover-cls="actions-temp-resynchronize-confirm"
              :width="320"
              @confirm="handleConfirmResynchronize(row)"
            >
              <div slot="content">
                <div class="popover-title">
                  <div class="popover-title-text">
                    {{ $t(`m.dialog['确认解除与该操作模板的同步？']`) }}
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
                    {{ $t(`m.actionsTemplate['解除同步后，模板权限将转为用户组自定义权限，不会再继续同步该模板的操作。']`) }}
                  </div>
                </div>
              </div>
              <bk-button
                size="small"
                theme="primary"
                class="un-sync"
                text
                @click.stop="handleUnSynchronize(row)"
              >
                {{ $t(`m.actionsTemplate['解除同步']`) }}
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

      async handleConfirmResynchronize (payload) {
        const { id } = this.curDetailData;
        const params = {
          id,
          data: {
            members: [{
              id: payload.id,
              type: 'group'
            }]
          }
        };
        try {
          await this.$store.dispatch('permTemplate/deleteTemplateMember', params);
          this.messageSuccess(this.$t(`m.info['移除成功']`), 3000);
          this.resetPagination();
          await this.fetchAssociateGroup();
          bus.$emit('on-related-group-change', {
            ...payload,
            ...{
              id,
              subject_count: this.pagination.count
            }
          });
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },
      
      handleUnSynchronize (payload) {
        this.$nextTick(() => {
          const { id, name } = payload;
          const removeSync = this.$refs[`removeSyncGroupConfirm_${name}_${id}`];
          if (removeSync) {
            removeSync.$refs && removeSync.$refs.popover.showHandler();
          }
        });
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

<style lang="postcss">
.actions-temp-resynchronize-confirm {
  .popconfirm-operate {
    .default-operate-button {
      min-width: 64px;
      margin-left: 0;
      margin-right: 8px;
    }
  }
}
</style>

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
    .user-groups-name {
        color: #3a84ff;
        &:hover {
          color: #699df4;
          cursor: pointer;
        }
      }
    /deep/ .un-sync {
      padding: 0;
    }
  }
}
.actions-temp-resynchronize-confirm {
  .popover-title {
    font-size: 16px;
    padding-bottom: 16px;
  }
  .popover-content {
    color: #63656e;
    font-size: 12px;
    .popover-content-item {
      display: flex;
      &-value {
        color: #313238;
        margin-left: 5px;
      }
    }
    &-tip {
      padding: 4px 0 10px 0;
      line-height: 20px;
      word-break: break-all;
    }
  }
}
</style>
