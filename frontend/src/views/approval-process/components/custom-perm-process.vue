<template>
  <div class="iam-custom-perm-process-wrapper">
    <render-search>
      <bk-button theme="primary"
        :disabled="!isCanBatchDelete"
        @click="handleBatchDelete">
        {{ $t(`m.approvalProcess['批量设置']`) }}
      </bk-button>
      <div slot="right" style="display: flex;">
        <bk-cascade
          v-model="searchValue"
          :list="systemList"
          is-remote
          check-any-level
          :remote-method="remoteMethod"
          style="width: 200px;"
          class="iam-custom-process-cascade-cls"
          @change="handleCascadeChange">
        </bk-cascade>
        <bk-input
          v-model="searchKeyword"
          :placeholder="$t(`m.approvalProcess['搜索提示']`)"
          clearable
          style="margin-left: 8px; width: 320px;"
          right-icon="bk-icon icon-search"
          @enter="handleSearch" />
      </div>
    </render-search>
    <section class="loading-wrapper" v-bkloading="{ isLoading: tableLoading, opacity: 1, zIndex: 2000 }">
      <bk-table
        size="small"
        ref="customPermRef"
        ext-cls="custom-perm-process-table"
        :data="tableList"
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
        <bk-table-column :label="$t(`m.common['操作']`)">
          <template slot-scope="{ row }">
            <span :title="row.action_name">{{ row.action_name }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.approvalProcess['审批流程']`)">
          <template slot-scope="{ row }">
            <section class="process-select-wrapper" v-if="row.canEdit || row.isToggle">
              <bk-select
                :value="row.process_id"
                :clearable="false"
                searchable
                :search-placeholder="$t(`m.approvalProcess['请输入关键字搜索']`)"
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
              {{ row.process_id | processNameFilter(list) }}
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
  </div>
</template>
<script>
  import _ from 'lodash';
  import il8n from '@/language';
  import editProcessDialog from './edit-process-dialog';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData, xssFilter } from '@/common/util';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  export default {
    name: '',
    components: {
      editProcessDialog
    },
    filters: {
      processNameFilter (value, list) {
        const data = list.find(item => item.id === value);
        if (data) return data.name;
        return il8n('approvalProcess', '默认审批流程');
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
        searchKeyword: '',
        isProcessDialogShow: false,
        batchEditLoading: false,
        systemList: [],
        requestQueue: ['list', 'system'],
        searchValue: [],
        procssValue: '',
        tips: this.$t(`m.common['暂未开放']`),
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
            ...mapGetters(['externalSystemId', 'user']),
            isCanBatchDelete () {
                return this.currentSelectList.length > 0 && this.tableList.length > 0;
            },
            tableLoading () {
                return this.requestQueue.length > 0;
            },
            curSelectName () {
                return payload => {
                    if (this.list.length > 0 && payload.process_id !== '') {
                        if (this.list.find(item => item.id === payload.process_id)) {
                            return this.list.find(item => item.id === payload.process_id).name;
                        }
                    }
                    return this.$t(`m.approvalProcess['默认审批流程']`);
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
      searchKeyword (newVal, oldVal) {
        if (newVal === '' && oldVal !== '' && this.isFilter) {
          this.isFilter = false;
          this.pagination = Object.assign({}, {
            current: 1,
            count: 1,
            limit: 10
          });
          this.fetchActionProcessesList();
        }
      }
    },
    created () {
      this.isFilter = false;
      this.cacheSystemId = '';
      const currentQueryCache = this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        if (currentQueryCache.limit) {
          this.pagination.limit = currentQueryCache.limit;
          this.pagination.current = currentQueryCache.current;
        }
        if (currentQueryCache.keyword) {
          this.searchKeyword = currentQueryCache.keyword;
        }
        this.cacheSystemId = currentQueryCache.system_id;
        if (this.searchKeyword !== '') {
          this.isFilter = true;
        }
      }
      this.fetchSystemList();
      this.$once('hook:beforeDestroy', () => {
        bus.$off('update-tab-table-list');
      });
    },
    mounted () {
      bus.$on('update-tab-table-list', ({ type }) => {
        if (['CustomPermProcess'].includes(type)) {
          this.pagination = Object.assign(this.pagination, {
            current: 1,
            limit: 10
          });
          this.fetchActionProcessesList();
        }
      });
    },
    methods: {
      async fetchSystemList () {
        try {
          const params = {};
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const res = await this.$store.dispatch('system/getSystems', params);
          this.systemList = res.data;
          setTimeout(() => {
            if (this.cacheSystemId) {
              this.searchValue = [this.cacheSystemId];
            } else {
              if (this.systemList.length) {
                this.searchValue = [this.systemList[0].id];
              }
            }
            this.fetchActionProcessesList();
          });
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
        }
      },

      async fetchActionProcessesList () {
        if (!this.searchValue.length) {
          this.requestQueue.shift();
          return;
        }
        this.setCurrentQueryCache(this.refreshCurrentQuery());
        const systemId = this.searchValue[0];
        let actionGroupId = '';
        if (this.searchValue.length > 1) {
          actionGroupId = this.searchValue[this.searchValue.length - 1];
        }
        const params = {
          limit: this.pagination.limit,
          offset: this.pagination.limit * (this.pagination.current - 1),
          keyword: this.searchKeyword,
          system_id: systemId,
          action_group_id: actionGroupId
        };
        try {
          const { code, data } = await this.$store.dispatch('approvalProcess/getActionProcessesList', params);
          this.tableList = data.results;
          this.pagination.count = data.count;
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
          const currentSelectList = this.currentSelectList.map(item => item.action_id);
          if (currentSelectList.length) {
            this.$nextTick(() => {
              this.tableList.forEach(item => {
                if (this.$refs.customPermRef && currentSelectList.includes(item.action_id)) {
                  this.$refs.customPermRef.toggleRowSelection(item, true);
                }
              });
            });
          }
        } catch (e) {
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
          this.fetchCustomTotal();
        }
      },

      refreshCurrentQuery () {
        const { limit, current } = this.pagination;
        const queryParams = {
          limit,
          current,
          system_id: this.searchValue[0],
          role_name: this.user.role.name
        };
        if (this.searchKeyword !== '') {
          queryParams.keyword = this.searchKeyword;
          this.emptyData.tipType = 'search';
        }
        window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        return queryParams;
      },

      setCurrentQueryCache (payload) {
        window.localStorage.setItem('customPermProcessList', JSON.stringify(payload));
      },

      getCurrentQueryCache () {
        return JSON.parse(window.localStorage.getItem('customPermProcessList'));
      },

      handleOpenCreateLink () {
        // const url = `${window.BK_ITSM_APP_URL}/#/process/home`
        // window.open(url)
      },

      handleCascadeChange (payload) {
        this.currentSelectList = [];
        this.requestQueue = ['list'];
        this.pagination = Object.assign({}, {
          current: 1,
          count: 1,
          limit: 10
        });
        this.fetchActionProcessesList();
      },

      handleEmptyClear () {
        this.searchKeyword = '';
        this.emptyData.tipType = '';
        this.pagination = Object.assign({}, {
          current: 1,
          count: 1,
          limit: 10
        });
        this.fetchActionProcessesList();
      },

      handleEmptyRefresh () {
        this.pagination = Object.assign({}, {
          current: 1,
          count: 1,
          limit: 10
        });
        this.fetchActionProcessesList();
      },

      setCellStyle ({ row, column, rowIndex, columnIndex }) {
        if (rowIndex === 0 && columnIndex === 2) {
          return {
            paddingLeft: '10px'
          };
        }
        return {};
      },

      async remoteMethod (item, resolve) {
        const flag = this.systemList.some(v => v.id === item.id);
        if (item.isLoading === false || !flag) {
          if (!flag && item.sub_groups && item.sub_groups.length > 0) {
            item.children = _.cloneDeep(item.sub_groups);
            resolve(item);
          } else {
            resolve(item);
          }
        } else {
          this.$set(item, 'isLoading', true);
          try {
            const res = await this.$store.dispatch('approvalProcess/getActionGroups', { system_id: item.id });
            item.children = res.data || [];
            resolve(item);
          } catch (e) {
            console.error(e);
            this.messageAdvancedError(e);
          }
        }
      },

      async updateActionProcesses (params = {}) {
        try {
          await this.$store.dispatch('approvalProcess/updateActionProcesses', params);
          this.messageSuccess(this.$t(`m.common['操作成功']`));
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.requestQueue = ['list'];
        this.pagination.current = page;
        this.fetchActionProcessesList();
      },

      handleSearch () {
        if (this.searchKeyword === '') {
          return;
        }
        this.isFilter = true;
        this.requestQueue = ['list'];
        this.pagination = Object.assign({}, {
          current: 1,
          count: 1,
          limit: 10
        });
        this.fetchActionProcessesList();
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.requestQueue = ['list'];
        this.fetchActionProcessesList();
      },

      // 自定义分页勾选后的总数
      fetchCustomTotal () {
        this.$nextTick(() => {
          const tableRef = this.$refs.customPermRef;
          if (tableRef && tableRef.$refs && tableRef.$refs.paginationWrapper) {
            const paginationWrapper = tableRef.$refs.paginationWrapper;
            const selectCount = paginationWrapper.getElementsByClassName('bk-page-selection-count');
            if (selectCount && selectCount.length && selectCount[0].children) {
              selectCount[0].children[0].innerHTML = xssFilter(this.currentSelectList.length);
            }
          }
        });
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectList.push(row);
            } else {
              this.currentSelectList = this.currentSelectList.filter((item) => item.action_id !== row.action_id);
            }
            this.fetchCustomTotal();
          },
          all: () => {
            const list = payload.filter(item => !this.currentSelectList.includes(item.action_id));
            const selectGroups = this.currentSelectList.filter(item =>
              !this.tableList.map(v => v.action_id).includes(item.action_id));
            this.currentSelectList = [...selectGroups, ...list];
            this.fetchCustomTotal();
          }
        };
        return typeMap[type]();
      },

      handlerAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handlerChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },

      handleProcessSelect (value, option, item) {
        const params = {
          actions: [{
            id: item.action_id,
            system_id: item.system_id
          }],
          process_id: value
        };
        item.process_id = value;
        this.updateActionProcesses(params);
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
            actions: this.currentSelectList.map(item => {
              return {
                id: item.action_id,
                system_id: item.system_id
              };
            }),
            process_id: payload
          };
          await this.updateActionProcesses(params);
          this.isProcessDialogShow = false;
          this.currentSelectList = [];
          this.requestQueue = ['list'];
          this.fetchActionProcessesList();
        } catch (e) {
          console.error(e);
        } finally {
          this.batchEditLoading = false;
        }
      }
    }
  };
</script>
<style lang="postcss">
    .iam-custom-perm-process-wrapper {
        .iam-custom-process-cascade-cls {
            .bk-cascade-angle {
                top: 8px;
                right: 5px;
                font-size: 14px;
            }
        }
        .loading-wrapper {
            min-height: 255px;
        }
        .custom-perm-process-table {
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
        }
    }
</style>
