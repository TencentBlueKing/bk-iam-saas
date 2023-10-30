<template>
  <div class="iam-sensitivity-level-wrapper">
    <render-search>
      <div class="search_left">
        <bk-button
          theme="primary"
          :disabled="isBatchDisabled"
          @click="handleBatchTransferLevel"
          data-test-id="group_btn_create"
        >
          {{ $t(`m.sensitivityLevel['批量转移等级']`) }}
        </bk-button>
      </div>
      <!-- 先屏蔽 -->
      <div slot="right">
        <iam-search-select
          style="width: 500px"
          :placeholder="$t(`m.sensitivityLevel['搜索操作名称、当前等级']`)"
          :data="searchData"
          :value="searchValue"
          :quick-search-method="quickSearchMethod"
          @on-change="handleSearch"
        />
      </div>
    </render-search>
    <bk-table
      size="small"
      ref="sensitivityTableRef"
      ext-cls="sensitivity-level-table"
      :key="tabActive"
      :data="sensitivityTableList"
      :max-height="tableHeight"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handleSelectChange"
      @select-all="handleSelectAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column type="selection" align="center" :selectable="getDefaultSelect" />
      <bk-table-column :label="$t(`m.sensitivityLevel['操作名称']`)">
        <template slot-scope="{ row }">
          <span class="action-name" :title="row.action_name">
            {{ row.action_name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column
        :label="$t(`m.sensitivityLevel['所属系统']`)"
        prop="system_id"
      >
        <template slot-scope="{ row }">
          {{ formaSystemText(row.system_id) }}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.sensitivityLevel['当前审批流程']`)">
        <template slot-scope="{ row }">
          <span :title="row.process_name">{{ row.process_name || "--" }}</span>
        </template>
      </bk-table-column>
      <bk-table-column
        :label="$t(`m.sensitivityLevel['当前等级']`)"
        :sortable="true"
        :filters="formatLevelFilter"
        :filter-method="handleLevelFilter"
        :filter-multiple="false"
        width="280"
        prop="sensitivity_level"
      >
        <template slot-scope="{ row, $index }">
          <IamSensitivitySelect
            style="width: 220px"
            :selected-value="row.sensitivity_level || ''"
            :list="sensitivityLevelEnum"
            :index="$index"
            :attributes="curSensitivityLevel"
            @on-change="handleChangeLevel"
          />
        </template>
      </bk-table-column>
      <!-- <bk-table-column :label="$t(`m.sensitivityLevel['额外添加的审批节点']`)">
        <template slot-scope="{ row }">
          <span :title="row.description || ''">{{ row.description || "--" }}</span>
        </template>
      </bk-table-column> -->
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

    <IamBatchTransferSlider
      :show.sync="isShowTransferSlider"
      :title="$t(`m.sensitivityLevel['批量转移等级']`)"
      :cur-select-data="curSelectData"
      @on-confirm="handleConfirmTransfer"
    />
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { formatCodeData, getWindowHeight } from '@/common/util';
  import { SENSITIVITY_LEVEL_ENUM } from '@/common/constants';
  import IamSearchSelect from '@/components/iam-search-select';
  import IamSensitivitySelect from './iam-sensitivity-select.vue';
  import IamBatchTransferSlider from './iam-batch-transfer-slider.vue';
  export default {
    name: 'SensitivityLevelTable',
    components: {
      IamSearchSelect,
      IamSensitivitySelect,
      IamBatchTransferSlider
    },
    props: {
      curSystemData: {
        type: Object
      },
      tabActive: {
        type: String,
        default: 'all'
      }
    },
    data () {
      return {
        sensitivityLevelEnum: SENSITIVITY_LEVEL_ENUM,
        tableLoading: false,
        isShowTransferSlider: false,
        sensitivityTableList: [],
        currentSelectList: [],
        allSystemData: [],
        searchList: [],
        searchValue: [],
        searchData: [
          {
            id: 'action_name',
            name: this.$t(`m.sensitivityLevel['操作名称']`),
            default: true
          },
          {
            id: 'sensitivity_level',
            name: this.$t(`m.sensitivityLevel['当前等级']`),
            remoteMethod: this.handleRemoteLevel
          }
        ],
        searchParams: {},
        queryParams: {},
        curSelectData: {},
        curSensitivityLevel: {
          sensitivity_level: ''
        },
        pagination: {
          current: 1,
          limit: 10,
          count: 0
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
    ...mapGetters(['allSystemList', 'externalSystemId']),
    isBatchDisabled () {
      return this.currentSelectList.length === 0;
    },
    tableHeight () {
      return getWindowHeight() - 260;
    },
    formaSystemText () {
      return (payload) => {
        const curSystem = this.allSystemData.find((item) => item.value === payload);
        if (curSystem) {
          return curSystem.text;
        }
        return '--';
      };
    },
    formatLevelFilter () {
      return this.sensitivityLevelEnum.map(({ name, id }) => ({
        text: this.$t(`m.sensitivityLevel['${name}']`),
        value: id
      }));
    }
    },
    watch: {
      tabActive: {
        async handler (newVal, oldVal) {
          if (newVal) {
            if (oldVal && oldVal !== newVal) {
              this.resetPagination();
            }
            await this.fetchInitData();
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchInitData () {
        await this.fetchSystems();
        await this.fetchSensitivityLevelList(true);
      },

      async fetchSystems () {
        if (this.allSystemList.length) {
          this.allSystemData = [...this.allSystemList].map(({ id, name }) => ({
            value: id,
            text: name
          }));
          return;
        }
        const params = {};
        if (this.externalSystemId) {
          params.hidden = false;
        }
        const result = await this.$store.dispatch('getSystemList', params);
        if (result && result.length) {
          this.allSystemData = [...result].map(({ id, name }) => ({
            value: id,
            text: name
          }));
        }
      },

      async fetchSensitivityLevelList (tableLoading = false) {
        this.tableLoading = tableLoading;
        try {
          const { current, limit } = this.pagination;
          let systemId = this.curSystemData.id;
          if (['all'].includes(systemId)) {
            systemId = this.allSystemData.map((item) => item.value).join();
          }
          const params = {
            sensitivity_level: this.tabActive,
            system_id: systemId,
          ...this.searchParams,
            offset: limit * (current - 1),
            limit
          };
          const { code, data } = await this.$store.dispatch(
            'sensitivityLevel/getProcessesActionsList',
            params
          );
          this.pagination.count = data.count || 0;
          this.sensitivityTableList = [...data.results];
          this.emptyData = formatCodeData(code, this.emptyData);
          this.$nextTick(() => {
            const currentSelectList = this.currentSelectList.map((item) => item.action_id);
            this.sensitivityTableList.forEach((item) => {
              if (currentSelectList.includes(item.action_id)) {
                this.$refs.sensitivityTableRef
                  && this.$refs.sensitivityTableRef.toggleRowSelection(item, true);
              }
            });
            if (this.currentSelectList.length < 1) {
              this.$refs.sensitivityTableRef
                && this.$refs.sensitivityTableRef.clearSelection();
            }
          });
        } catch (e) {
          this.sensitivityTableList = [];
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      async handleChangeLevel (payload, index) {
        try {
          const { action_id, system_id } = this.sensitivityTableList[index];
          const params = {
            actions: [
              {
                id: action_id,
                system_id
              }
            ],
            sensitivity_level: payload
          };
          const { code } = await this.$store.dispatch(
            'sensitivityLevel/updateActionsSensitivityLevel',
            params
          );
          if (code === 0) {
            this.$set(this.sensitivityTableList[index], 'sensitivity_level', payload);
            this.messageSuccess(this.$t(`m.info['编辑成功']`), 3000);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectList.push(row);
            } else {
              this.currentSelectList = this.currentSelectList.filter(
                (item) => item.action_id !== row.action_id
              );
            }
            this.$nextTick(() => {
              const selectionCount = document.getElementsByClassName(
                'bk-page-selection-count'
              );
              if (this.$refs.sensitivityTableRef && selectionCount) {
                selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
              }
            });
          },
          all: () => {
            const tableList = _.cloneDeep(this.sensitivityTableList);
            const selectGroups = this.currentSelectList.filter(
              (item) => !tableList.map((v) => v.action_id).includes(item.action_id)
            );
            this.currentSelectList = [...selectGroups, ...payload];
            this.$nextTick(() => {
              const selectionCount = document.getElementsByClassName(
                'bk-page-selection-count'
              );
              if (this.$refs.sensitivityTableRef && selectionCount) {
                selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
              }
            });
          }
        };
        return typeMap[type]();
      },

      handleSearch (payload, result) {
        this.searchParams = payload;
        this.searchList = result;
        this.emptyData.tipType = 'search';
        this.queryParams = Object.assign(this.queryParams, {
          current: 1,
          limit: 10
        });
        this.resetPagination();
        this.fetchSensitivityLevelList(true);
      },

      handleSelectChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },

      handleSelectAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handlePageChange (page) {
        this.pagination.current = page;
        this.queryParams = Object.assign(this.queryParams, { current: page });
        this.fetchSensitivityLevelList(true);
      },

      handleLimitChange (currentLimit) {
        this.pagination = Object.assign(this.pagination, {
          current: 1,
          limit: currentLimit
        });
        this.queryParams = Object.assign(this.queryParams, {
          current: 1,
          limit: currentLimit
        });
        this.fetchSensitivityLevelList(true);
      },

      async handleRemoteLevel (value) {
        const list = _.cloneDeep(SENSITIVITY_LEVEL_ENUM);
        if (!value) {
          return Promise.resolve(list);
        }
        return Promise.resolve(list.filter((item) => item.name.indexOf(value) > -1));
      },

      handleSystemFilter (value, row, column) {
        const property = column.property;
        return row[property] === value;
      },

      handleLevelFilter (value, row, column) {
        const property = column.property;
        return row[property] === value;
      },

      handleBatchTransferLevel () {
        this.isShowTransferSlider = true;
        this.curSelectData = {
          tableList: this.currentSelectList
        };
      },

      handleConfirmTransfer () {
        this.isShowTransferSlider = false;
        this.curSelectData = {};
        this.currentSelectList = [];
        this.resetPagination();
        this.fetchSensitivityLevelList(true);
      },

      handleEmptyClear () {
        this.handleEmptyRefresh();
      },

      handleEmptyRefresh () {
        this.searchParams = {};
        this.queryParams = Object.assign(this.queryParams, {
          current: 1,
          limit: 10
        });
        this.currentSelectList = [];
        this.resetPagination();
        this.fetchSensitivityLevelList(true);
      },

      resetPagination () {
        this.pagination = Object.assign(
          {},
          {
            limit: 10,
            current: 1,
            count: 0
          }
        );
      },

      getDefaultSelect () {
        return this.sensitivityTableList.length > 0;
      },

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-sensitivity-level-wrapper {
  .sensitivity-level-table {
    margin-top: 16px;
    border-bottom: 0;
    border-right: 0;
  }
}
</style>
