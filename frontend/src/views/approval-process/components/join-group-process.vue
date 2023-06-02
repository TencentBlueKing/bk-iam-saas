<template>
  <div class="iam-join-group-process-wrapper">
    <render-search>
      <bk-button theme="primary"
        :disabled="!isCanBatchDelete"
        @click="handleBatchDelete">
        {{ $t(`m.approvalProcess['批量设置']`) }}
      </bk-button>
      <div slot="right">
        <bk-input
          v-model="searchValue"
          :placeholder="$t(`m.approvalProcess['加入用户组流程搜索提示']`)"
          clearable
          style="margin-left: 8px; width: 320px;"
          right-icon="bk-icon icon-search"
          @enter="handleSearch" />
      </div>
    </render-search>
    <section class="loading-wrapper" v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
      <bk-table
        :data="tableList"
        size="small"
        ext-cls="join-group-process-table"
        :outer-border="false"
        :header-border="false"
        :pagination="pagination"
        :header-cell-style="setCellStyle"
        v-if="!tableLoading"
        @page-change="pageChange"
        @page-limit-change="limitChange"
        @select="handlerChange"
        @select-all="handlerAllChange"
        @row-mouse-enter="handleRowMouseEnter"
        @row-mouse-leave="handleRowMouseLeave">
        <bk-table-column type="selection" align="center" :selectable="getSelectable"></bk-table-column>
        <bk-table-column :label="$t(`m.userGroup['用户组']`)" width="400">
          <template slot-scope="{ row }">
            <span class="group-name" :title="row.group_name" @click.stop="handleViewDetail(row)">
              {{ row.group_name }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.common['描述']`)" width="400">
          <template slot-scope="{ row }">
            <span :title="row.group_desc">{{ row.group_desc || '--' }}</span>
          </template>
        </bk-table-column>
        <template v-if="['rating_manager'].includes(user.role.type)">
          <bk-table-column :label="$t(`m.nav['管理空间']`)">
            <!-- <template slot-scope="{ row }">
                            <span class="user-group-name" :title="row.role.name" @click="handleView(row)">
                                {{ row.role.name || '--' }}
                            </span>
                            <span>{{ user.role.name === row.role.name ? `(${il8n('levelSpace', '当前空间')})` : '' }}</span>
                        </template> -->
          </bk-table-column>
        </template>
        <bk-table-column :label="$t(`m.approvalProcess['审批流程']`)">
          <template slot-scope="{ row }">
            <section class="process-select-wrapper" v-if="row.canEdit || row.isToggle">
              <bk-select
                :value="row.process_id"
                :clearable="false"
                searchable
                @selected="handleProcessSelect(...arguments, row)"
                @toggle="handleSelectToggle(...arguments, row)">
                <bk-option v-for="option in list"
                  :key="option.id"
                  :id="option.id"
                  :name="option.name">
                  <span style="display: block; line-height: 32px;"
                    :title="`${$t(`m.approvalProcess['审批节点']`)}：${option.node_names.join(' -> ')}`">
                    {{ option.name }}
                  </span>
                </bk-option>
                <div slot="extension" v-bk-tooltips="{ content: tips, extCls: 'iam-tooltips-cls' }"
                  @click="handleOpenCreateLink" style="cursor: not-allowed;">
                  <Icon bk type="plus-circle" />
                  <span>{{ $t(`m.common['新增']`) }}</span>
                </div>
                <div slot="trigger" style="padding-left: 10px;" :title="curTitle(row)">
                  {{ curSelectName(row) }}
                </div>
              </bk-select>
            </section>
            <section class="process-name" v-else>
              {{ row.process_id | proceeNameFilter(list) }}
            </section>
          </template>
        </bk-table-column>
        <template slot="empty">
          <ExceptionEmpty
            :type="emptyData.type"
            :empty-text="emptyData.text"
            :tip-text="emptyData.tip"
            :tip-type="emptyData.tipType"
            @on-clear="handleEmptyClear"
            @on-refresh="handleEmptyRefresh"
          />
        </template>
      </bk-table>
    </section>
    <edit-process-dialog
      :show.sync="isProcessDialogShow"
      :list="list"
      :procss-value="procssValue"
      :loading="batchEditLoading"
      @on-submit="handleEditProcess"
      @on-cancel="isProcessDialogShow = false"
      @on-after-leave="handleAfterLeave" />

    <render-perm-sideslider
      :show="isShowPermSidesilder"
      :name="curGroupName"
      :group-id="curGroupId"
      @animation-end="handleAnimationEnd" />
  </div>
</template>
<script>
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import editProcessDialog from './edit-process-dialog';
  import RenderPermSideslider from '../../perm/components/render-group-perm-sideslider';
  import { formatCodeData } from '@/common/util';
  export default {
    name: '',
    components: {
      editProcessDialog,
      RenderPermSideslider
    },
    filters: {
      proceeNameFilter (value, list) {
        const data = list.find(item => item.id === value);
        if (data) return data.name;
        return '默认审批流程';
      }
    },
    props: {
      list: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        currentSelectList: [],
        tableList: [],
        pagination: {
          current: 1,
          count: 1,
          limit: 10
        },
        currentBackup: 1,
        searchValue: '',
        tableLoading: false,
        isProcessDialogShow: false,
        curGroupId: '',
        isShowPermSidesilder: false,
        curGroupName: '',
        batchEditLoading: false,
        procssValue: '',
        tips: this.$t(`m.common['暂未开放']`),
        spaceFiltersList: [],
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
            ...mapGetters(['user']),
            isCanBatchDelete () {
                return this.currentSelectList.length > 0 && this.tableList.length > 0;
            },
            curSelectName () {
                return payload => {
                    if (this.list.length > 0 && payload.process_id !== '') {
                        if (this.list.find(item => item.id === payload.process_id)) {
                            return this.list.find(item => item.id === payload.process_id).name;
                        }
                        return '默认审批流程';
                    }
                    return '';
                };
            },
            curTitle () {
                return payload => {
                    if (this.list.length > 0 && payload.process_id !== '') {
                        if (this.list.find(item => item.id === payload.process_id)) {
                            return `${this.$t(`m.approvalProcess['审批节点']`)}：${this.list.find(item => item.id === payload.process_id).node_names.join(' -> ')}`;
                        } else {
                            return '';
                        }
                    }
                    return '';
                };
            }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      },
      searchValue (newVal, oldVal) {
        if (newVal === '' && oldVal !== '' && this.isFilter) {
          this.isFilter = false;
          this.pagination = Object.assign({}, {
            current: 1,
            count: 1,
            limit: 10
          });
          this.fetchGroupProcessesList();
        }
      }
    },
    created () {
      this.isFilter = false;
      const currentQueryCache = this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        if (currentQueryCache.limit) {
          this.pagination.limit = currentQueryCache.limit;
          this.pagination.current = currentQueryCache.current;
        }
        if (currentQueryCache.keyword) {
          this.searchValue = currentQueryCache.keyword;
        }
        if (this.searchValue !== '') {
          this.isFilter = true;
        }
      }
      this.fetchGroupProcessesList();
    },
    methods: {
      refreshCurrentQuery () {
        const { limit, current } = this.pagination;
        const queryParams = {
          limit,
          current
        };
        if (this.searchValue !== '') {
          this.emptyData.tipType = 'search';
          queryParams.keyword = this.searchValue;
        }
        window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        return queryParams;
      },

      setCurrentQueryCache (payload) {
        window.localStorage.setItem('joinGroupProcessList', JSON.stringify(payload));
      },

      getCurrentQueryCache () {
        return JSON.parse(window.localStorage.getItem('joinGroupProcessList'));
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.fetchGroupProcessesList();
      },

      setCellStyle ({ row, column, rowIndex, columnIndex }) {
        if (rowIndex === 0 && columnIndex === 3) {
          return {
            paddingLeft: '10px'
          };
        }
        return {};
      },

      async fetchGroupProcessesList (isLoading = true) {
        this.tableLoading = isLoading;
        this.setCurrentQueryCache(this.refreshCurrentQuery());
        const params = {
          limit: this.pagination.limit,
          offset: this.pagination.limit * (this.pagination.current - 1),
          keyword: this.searchValue
        };
        try {
          const { code, data } = await this.$store.dispatch('approvalProcess/getGroupProcessesList', params);
          this.pagination.count = data.count;
          this.tableList = data.results;
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
        } catch (e) {
          console.error(e);
          const { code, data, message, statusText } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: message || data.msg || statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.tableLoading = false;
        }
      },

      async updateGroupProcesses (params = {}) {
        try {
          await this.$store.dispatch('approvalProcess/updateGroupProcesses', params);
          this.messageSuccess(this.$t(`m.common['操作成功']`));
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      resetPagination () {
        this.pagination = Object.assign({}, {
          current: 1,
          count: 1,
          limit: 10
        });
        this.fetchGroupProcessesList();
      },

      handleOpenCreateLink () {
        // const url = `${window.BK_ITSM_APP_URL}/#/process/home`
        // window.open(url)
      },

      handleSearch () {
        if (!this.searchValue) {
          return;
        }
        this.isFilter = true;
        this.resetPagination();
      },

      handleEmptyClear () {
        this.searchValue = '';
        this.emptyData.tipType = '';
        this.resetPagination();
      },

      handleEmptyRefresh () {
        this.isFilter = false;
        this.resetPagination();
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.fetchGroupProcessesList();
      },

      handlerAllChange (selection) {
        this.currentSelectList = [...selection];
      },

      handlerChange (selection, row) {
        this.currentSelectList = [...selection];
      },

      handleProcessSelect (value, option, item) {
        const params = {
          group_ids: [item.group_id],
          process_id: value
        };
        item.process_id = value;
        this.updateGroupProcesses(params);
      },

      handleSelectToggle (payload, row) {
        if (payload) {
          this.$set(row, 'isToggle', true);
        } else {
          this.$delete(row, 'isToggle');
        }
      },

      handleRowMouseEnter (index) {
        this.$set(this.tableList[index], 'canEdit', true);
      },

      handleRowMouseLeave (index) {
        this.$delete(this.tableList[index], 'canEdit');
      },

      getSelectable (row, index) {
        if (this.tableList.length < 1) {
          return false;
        }
        return true;
      },

      handleBatchDelete () {
        this.isProcessDialogShow = true;
        const list = [...new Set(this.currentSelectList.map(item => item.process_id))];
        if (list.length === 1) {
          this.procssValue = list[0];
        }
      },

      handleAfterLeave () {
        this.procssValue = '';
      },

      async handleEditProcess (payload) {
        if (payload === this.procssValue) {
          this.isProcessDialogShow = false;
          return;
        }
        this.batchEditLoading = true;
        try {
          const params = {
            group_ids: this.currentSelectList.map(item => item.group_id),
            process_id: payload
          };
          await this.updateGroupProcesses(params);
          this.currentSelectList = [];
          this.isProcessDialogShow = false;
          this.fetchGroupProcessesList();
        } catch (e) {
          console.error(e);
        } finally {
          this.batchEditLoading = false;
        }
      },

      handleViewDetail (payload) {
        this.curGroupName = payload.group_name;
        this.curGroupId = payload.group_id;
        this.isShowPermSidesilder = true;
      },

      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSidesilder = false;
      }
    }
  };
</script>
<style lang="postcss">
    .iam-join-group-process-wrapper {
        .loading-wrapper {
            min-height: 255px;
        }
        .join-group-process-table {
            margin-top: 16px;
            border: none;
            .process-name {
                position: relative;
                padding-left: 11px;
                line-height: 30px;
                color: #63656e;
                cursor: pointer;
            }
            .process-select-wrapper {
                background: #fff;
            }
            .group-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
        }
    }
</style>
