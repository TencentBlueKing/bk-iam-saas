<template>
  <div class="iam-transfer-history-wrapper">
    <bk-table
      :data="tableList"
      size="small"
      class="transfer-history-table"
      :class="{ 'set-border': tableLoading }"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
      <bk-table-column :label="$t(`m.permTransfer['交接时间']`)" :width="300">
        <template slot-scope="{ row }">
          <span :title="row.created_time">{{ row.created_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.permTransfer['目标交接人']`)" :width="300">
        <template slot-scope="{ row }">
          <span :title="row.handover_to">{{ row.handover_to }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.permTransfer['交接状态']`)">
        <template slot-scope="{ row }">
          <span class="status-icon" :class="row.statusCls"></span>{{row.statusStr}}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作']`)" width="150">
        <template slot-scope="{ row }">
          <bk-button theme="primary" text @click="showDetail(row)">{{ $t(`m.common['详情']`) }}</bk-button>
        </template>
      </bk-table-column>
      <template slot="empty">
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :tip-text="emptyData.tip"
          :tip-type="emptyData.tipType"
          @on-refresh="handleEmptyRefresh"
        />
      </template>
    </bk-table>

    <history-detail
      :show="isShowDetailSidesilder"
      :cur-history="curHistory"
      @animation-end="handleAnimationEnd" />
  </div>
</template>
<script>
  import { buildURLParams } from '@/common/url';
  import { formatCodeData } from '@/common/util';
  import HistoryDetail from './history-detail.vue';

  export default {
    name: '',
    components: {
      HistoryDetail
    },
    data () {
      return {
        isFilter: false,
        tableList: [],
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        tableLoading: false,
        curHistory: null,
        isShowDetailSidesilder: false,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    created () {
      const currentQueryCache = this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        if (currentQueryCache.limit) {
          this.pagination.limit = currentQueryCache.limit;
          this.pagination.current = currentQueryCache.current;
        }
      }
    },
    methods: {
      async fetchPageData () {
        await this.fetchTransferHistory();
      },

      refreshCurrentQuery () {
        const { limit, current } = this.pagination;
        const queryParams = {
          limit,
          current
        };
        window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        return queryParams;
      },

      setCurrentQueryCache (payload) {
        window.localStorage.setItem('permTransferList', JSON.stringify(payload));
      },

      getCurrentQueryCache () {
        return JSON.parse(window.localStorage.getItem('permTransferList'));
      },

      async fetchTransferHistory (isTableLoading = false) {
        this.tableLoading = isTableLoading;
        this.setCurrentQueryCache(this.refreshCurrentQuery());
        try {
          // const res = await this.$store.dispatch('role/getRatingManagerList', {
          const { data, code } = await this.$store.dispatch('perm/getTransferHistory', {
            limit: this.pagination.limit,
            offset: (this.pagination.current - 1) * this.pagination.limit
          });
          this.pagination.count = data.count || 0;
          const list = data.results || [];
          list.forEach(item => {
            // 2021-12-08 06:28:15.384996+00:00
            const timeArr = item.created_time.split('.');
            item.created_time = timeArr[0];

            const status = (item.status || '').toLowerCase();
            if (status === 'succeed') {
              item.statusStr = this.$t(`m.permTransfer['交接成功']`);
              item.statusCls = 'succeed';
            } else if (status === 'failed') {
              item.statusStr = this.$t(`m.permTransfer['交接失败']`);
              item.statusCls = 'failed';
            } else if (status === 'partial_failed') {
              item.statusStr = this.$t(`m.permTransfer['部分失败']`);
              item.statusCls = 'partial-failed';
            } else if (status === 'running') {
              item.statusStr = this.$t(`m.permTransfer['交接中']`);
              item.statusCls = 'running';
            } else {
              item.statusStr = '--';
            }
          });
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.emptyData = formatCodeData(code, this.emptyData, data.results.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      resetPagination () {
        this.pagination = Object.assign({}, {
          current: 1,
          count: 0,
          limit: 10
        });
      },

      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.fetchTransferHistory(true);
      },

      handleLimitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.fetchTransferHistory(true);
      },

      showDetail (row) {
        this.curHistory = Object.assign(row);
        this.isShowDetailSidesilder = true;
      },

      handleAnimationEnd () {
        this.curHistory = null;
        this.isShowDetailSidesilder = false;
      },

      handleEmptyRefresh () {
        this.resetPagination();
        this.fetchTransferHistory(false);
      }
    }
  };
</script>
<style lang="postcss">
    @import './history.css';
</style>
