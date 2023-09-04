<template>
  <div class="iam-record-list-wrapper">
    <render-search>
      <Icon type="arrows-left" class="breadcrumbs-back" @click="handleBackClick" />
      <span class="display-name">{{$t(`m.user['同步记录']`)}}</span>
      <div slot="right">
        <bk-date-picker
          v-model="initDateTimeRange"
          :placeholder="$t(`m.user['选择日期范围']`)"
          :type="'daterange'"
          placement="bottom-end"
          :shortcuts="shortcuts"
          :shortcut-close="true"
          @change="handleDateChange">
        </bk-date-picker>
      </div>
    </render-search>
    <bk-table
      :data="tableList"
      size="small"
      ext-cls="system-access-table"
      :class="{ 'set-border': tableLoading }"
      :max-height="tableHeight"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
      <!-- <bk-table-column type="selection" align="center"></bk-table-column> -->
      <bk-table-column :label="$t(`m.user['开始时间']`)" :min-width="220">
        <template slot-scope="{ row }">
          {{ timestampToTime(row.created_time) }}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.user['耗时']`)">
        <template slot-scope="{ row }">
          <span :title="row.cost_time">{{ row.cost_time | getDuration }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.user['操作人']`)">
        <template slot-scope="{ row }">
          <span :title="row.executor">
            {{ row.trigger_type === 'periodic_task' ? $t(`m.user['定时同步']`) : row.executor }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.user['触发类型']`)">
        <template slot-scope="{ row }">
          <span :title="row.trigger_type">{{ triggerType[row.trigger_type] }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['状态']`)">
        <template slot-scope="{ row }">
          <render-status :status="row.status" />
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作']`)" width="270">
        <template slot-scope="{ row }">
          <section>
            <bk-button theme="primary" text @click="showLogDetails(row)">
              {{ $t(`m.user['日志详情']`) }}
            </bk-button>
          </section>
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

    <bk-sideslider
      :is-show.sync="isShowLogDetails"
      :title="$t(`m.user['日志详情']`)"
      :width="640"
      :quick-close="true"
      @animation-end="handleAnimationEnd">
      <div slot="content" v-bkloading="{ isLoading: logDetailLoading, opacity: 1 }">
        <section v-show="!logDetailLoading">
          <div class="link-btn">
            <bk-link class="link" theme="primary" href="https://bk.tencent.com/docs/document/6.0/160/8402" target="_blank">{{$t(`m.user['同步失败排查指引']`)}}</bk-link>
          </div>
          <div v-if="exceptionMsg || tracebackMsg"
            class="msg-content">
            <div>
              <div v-html="exceptionMsg"></div>
              <div v-html="tracebackMsg"></div>
            </div>
            <!-- <div v-else>{{ $t(`m.user['暂无日志详情']`) }}</div> -->
          </div>
          <div v-else>
            <ExceptionEmpty style="background: #ffffff" />
          </div>
        </section>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { formatCodeData, timestampToTime, getWindowHeight } from '@/common/util';
  import RenderStatus from './render-status';
  import moment from 'moment';

  export default {
    name: 'system-access-index',
    filters: {
      getDuration (val) {
        const d = moment.duration(val, 'seconds');
        if (val >= 86400) {
          return `${Math.floor(d.asDays())}d${d.hours()}h${d.minutes()}min${d.seconds()}s`;
        }
        if (val >= 3600) {
          return `${d.hours()}h${d.minutes()}min${d.seconds()}s`;
        }
        if (val > 60) {
          return `${d.minutes()}min${d.seconds()}s`;
        }
        return `${Math.floor(val)}s`;
      }
    },
    components: {
      RenderStatus
    },
    data () {
      return {
        tableList: [],
        tableLoading: false,
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        isShowLogDetails: false,
        logDetailLoading: false,
        exceptionMsg: '',
        tracebackMsg: '',
        timestampToTime: timestampToTime,
        initDateTimeRange: [],
        triggerType: { 'periodic_task': this.$t(`m.user['定时同步']`), 'manual_sync': this.$t(`m.user['手动同步']`) },
        shortcuts: [
          {
            text: this.$t(`m.user['今天']`),
            value () {
              const end = new Date();
              const start = new Date();
              return [start, end];
            }
          },
          {
            text: this.$t(`m.user['最近7天']`),
            value () {
              const end = new Date();
              const start = new Date();
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
              return [start, end];
            }
          },
          {
            text: this.$t(`m.user['最近30天']`),
            value () {
              const end = new Date();
              const start = new Date();
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
              return [start, end];
            }
          }
        ],
        dateRange: { startTime: '', endTime: '' },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      tableHeight () {
        return getWindowHeight() - 185;
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    created () {
      this.fetchPageData();
    },
    methods: {
      async fetchPageData () {
        await this.fetchModelingList(true);
      },

      async fetchModelingList (isLoading = false) {
        this.tableLoading = isLoading;
        const params = {
          limit: this.pagination.limit,
          offset: this.pagination.limit * (this.pagination.current - 1),
          start_time: this.dateRange.startTime,
          end_time: this.dateRange.endTime
        };
        try {
          const { code, data } = await this.$store.dispatch('organization/getRecordsList', params);
          this.pagination.count = data.count;
          data.results = data.results.length && data.results.sort(
            (a, b) => new Date(b.updated_time) - new Date(a.updated_time));
                        
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.fetchModelingList(true);
      },

      handleLimitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.fetchModelingList(true);
      },

      handleAnimationEnd () {
        this.isShowLogDetails = false;
      },

      async showLogDetails (data) {
        this.isShowLogDetails = true;
        this.logDetailLoading = true;
        try {
          const res = await this.$store.dispatch('organization/getRecordsLog', data.id);
          this.exceptionMsg = res.data.exception_msg.replace(/\n/g, '<br>');
          this.tracebackMsg = res.data.traceback_msg.replace(/\n/g, '<br>');
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.logDetailLoading = false;
        }
      },

      resetPagination () {
        this.pagination = Object.assign({}, {
          limit: 10,
          current: 1,
          count: 0
        });
      },

      handleDateChange (date) {
        this.resetPagination();
        this.dateRange = {
          startTime: `${date[0]}` ? `${date[0]} 00:00:00` : '',
          endTime: `${date[1]}` ? `${date[1]} 23:59:59` : ''
        };
        this.fetchModelingList(true);
      },

      handleBackClick () {
        this.$emit('handleBack');
      },

      handleEmptyRefresh () {
        this.fetchModelingList(true);
      }
    }
  };
</script>
<style lang="postcss">
    .iam-record-list-wrapper {
        .detail-link {
            color: #3a84ff;
            cursor: pointer;
            &:hover {
                color: #699df4;
            }
            font-size: 12px;
        }
        .system-access-table {
            margin-top: 16px;
            border-right: none;
            border-bottom: none;
            &.set-border {
                border-right: 1px solid #dfe0e5;
                border-bottom: 1px solid #dfe0e5;
            }
            .system-access-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
            .lock-status {
                font-size: 12px;
                color: #fe9c00;
            }
        }
        .link-btn {
            margin: 10px;
            text-align: right;
            word-break: break-all;
        }
        .msg-content{
            background: #555555;
            color: #fff;
            margin: 0 0px 0 30px;
            padding: 10px;
            max-height: 1200px;
            overflow-y: scroll;
        }

        .breadcrumbs-back{
            cursor: pointer;
            display: inline-block;
            vertical-align: middle;
            width: 24px;
            height: 24px;
            line-height: 24px;
            text-align: center;
            font-size: 24px;
            color: #3c96ff;
        }
        .bk-table-pagination-wrapper {
          background-color: #ffffff;
        }
    }
</style>
