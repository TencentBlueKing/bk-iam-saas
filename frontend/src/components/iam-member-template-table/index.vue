<template>
  <div class="iam-member-template-wrapper">
    <bk-alert type="info" :title="$t(`m.memberTemplate['最多只能选择10个人员模板']`)" />
    <div class="template-search-input">
      <bk-input
        v-model="tableKeyWord"
        class="template-input-wrapper"
        :placeholder="$t(`m.memberTemplate['搜索模板名称']`)"
        :right-icon="'bk-icon icon-search'"
        :clearable="true"
        @clear="handleClearSearch"
        @enter="handleTableSearch"
        @right-icon-click="handleTableSearch" />
    </div>
    <div class="template-table-wrapper">
      <bk-table
        ref="templateTableRef"
        size="small"
        :data="templateTableList"
        :max-height="360"
        :ext-cls="'template-table'"
        :outer-border="false"
        :header-border="false"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange"
        @select="handleSelectChange"
        @select-all="handleSelectAllChange"
        v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
        <bk-table-column type="selection" align="center" :selectable="getDefaultSelect" />
        <bk-table-column :label="$t(`m.memberTemplate['模板名称']`)" prop="name" :sortable="true">
          <template slot-scope="{ row }">
            <span class="template-name" :title="row.name ">
              {{ row.name}}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.common['描述']`)">
          <template slot-scope="{ row }">
            <span :title="row.description || ''">
              {{ row.description || '--' }}
            </span>
          </template>
        </bk-table-column>
        <template slot="empty">
          <ExceptionEmpty
            :type="emptyTableData.type"
            :empty-text="emptyTableData.text"
            :tip-text="emptyTableData.tip"
            :tip-type="emptyTableData.tipType"
            @on-clear="handleClearSearch"
            @on-refresh="handleClearSearch"
          />
        </template>
      </bk-table>
    </div>
  </div>
</template>
  
<script>
  import _ from 'lodash';
  import { formatCodeData, xssFilter } from '@/common/util';
  export default {
    props: {
      groupId: {
        type: [String, Number],
        default: ''
      },
      hasSelectedTemplates: {
        type: Array,
        default: () => []
      },
      maxSelectCount: {
        type: Number,
        default: 10
      }
    },
    data () {
      return {
        tableLoading: false,
        tableKeyWord: '',
        tableKey: 'tableKey',
        currentSelectList: [],
        templateTableList: [],
        curTempIdList: [],
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
    watch: {
      hasSelectedTemplates: {
        handler (value) {
          this.currentSelectList = [...value];
          const selectIdList = this.currentSelectList.map((v) => String(v.id));
          this.templateTableList.forEach((item) => {
            this.$refs.templateTableRef.toggleRowSelection(
              item,
              !!(selectIdList.includes(String(item.id)) || this.curTempIdList.includes(String(item.id)))
            );
          });
          this.fetchSelectedGroupCount();
        },
        immediate: true
      }
    },
    async created () {
      await this.fetchGroupSubjectTemplate();
      await this.fetchTemplateList();
    },
    methods: {
      // 获取用户组关联模板列表
      async fetchGroupSubjectTemplate () {
        if (this.groupId) {
          try {
            const params = {
              page: 1,
              page_size: 1000,
              id: this.groupId
            };
            const { data } = await this.$store.dispatch('memberTemplate/getGroupSubjectTemplate', params);
            if (data.results && data.results.length) {
              this.curTempIdList = data.results.map((item) => String(item.id));
            }
          } catch (e) {
            this.curTempIdList = [];
            this.messageAdvancedError(e);
          }
        }
      },
      
      async fetchTemplateList () {
        this.tableLoading = true;
        try {
          const { current, limit } = this.pagination;
          const params = {
            name: this.tableKeyWord,
            page: current,
            page_size: limit
          };
          const { code, data } = await this.$store.dispatch('memberTemplate/getSubjectTemplateList', params);
          const { count, results } = data;
          this.pagination.count = count || 0;
          this.templateTableList = results || [];
          this.emptyTableData = formatCodeData(code, this.emptyTableData, this.templateTableList.length === 0);
          this.$nextTick(() => {
            const currentSelectList = this.currentSelectList.map((item) => String(item.id));
            this.templateTableList.forEach((item) => {
              this.$set(item, 'type', 'template');
              if (currentSelectList.includes(String(item.id)) || this.curTempIdList.includes(String(item.id))) {
                this.$refs.templateTableRef
                  && this.$refs.templateTableRef.toggleRowSelection(item, true);
              } else {
                this.$refs.templateTableRef.toggleRowSelection(item, false);
              }
            });
            if (this.currentSelectList.length < 1 && this.curTempIdList.length < 1) {
              this.$refs.templateTableRef
                && this.$refs.templateTableRef.clearSelection();
            }
          });
          this.fetchSelectedGroupCount();
        } catch (e) {
          this.templateTableList = [];
          this.emptyTableData = formatCodeData(e.code, this.emptyTableData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      handleTableSearch (payload) {
        this.tableKeyWord = payload;
        this.emptyTableData.tipType = 'search';
        this.resetPagination();
        this.fetchTemplateList();
      },

      handleClearSearch () {
        this.tableKeyWord = '';
        this.emptyTableData.tipType = '';
        this.resetPagination();
        this.fetchTemplateList();
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectList.push(row);
            } else {
              this.currentSelectList = this.currentSelectList.filter(
                (item) => item.id.toString() !== row.id.toString()
              );
            }
            this.fetchSelectedGroupCount();
            this.$emit('on-selected-templates', this.currentSelectList);
          },
          all: () => {
            const list = payload.filter(item => !this.curTempIdList.includes(String(item.id)));
            const tableList = _.cloneDeep(this.templateTableList);
            const selectGroups = this.currentSelectList.filter(
              (item) =>
                !tableList.map((v) => v.id.toString()).includes(item.id.toString())
                && !this.curTempIdList.includes(String(item.id))
            );
            const selectList = _.cloneDeep([...selectGroups, ...list]).slice(0, 10);
            const selectIdList = selectList.map((v) => String(v.id));
            this.templateTableList.forEach((item) => {
              this.$refs.templateTableRef.toggleRowSelection(
                item,
                !!(selectIdList.includes(String(item.id)) || this.curTempIdList.includes(String(item.id)))
              );
            });
            this.currentSelectList = _.cloneDeep(selectList);
            this.fetchSelectedGroupCount();
            this.$emit('on-selected-templates', this.currentSelectList);
          }
        };
        return typeMap[type]();
      },

      handleSelectChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },

      handleSelectAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handlePageChange (current) {
        this.pagination = Object.assign(this.pagination, { current });
        this.fetchTemplateList();
      },

      handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit });
        this.fetchTemplateList();
      },

      fetchSelectedGroupCount () {
        this.$nextTick(() => {
          const tableRef = this.$refs.templateTableRef;
          if (tableRef && tableRef.$refs && tableRef.$refs.paginationWrapper) {
            const paginationWrapper = tableRef.$refs.paginationWrapper;
            const selectCount = paginationWrapper.getElementsByClassName('bk-page-selection-count');
            if (selectCount && selectCount.length && selectCount[0].children) {
              selectCount[0].children[0].innerHTML = xssFilter(this.currentSelectList.length);
            }
          }
        });
      },

      getDefaultSelect (row) {
        const index = this.currentSelectList.findIndex((v) => String(v.id) === String(row.id));
        const isMax = this.currentSelectList.length >= this.maxSelectCount ? index !== -1 : true;
        if (this.curTempIdList.length && this.curTempIdList.includes(String(row.id))) {
          return false;
        }
        return isMax;
      },

      resetPagination () {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 10 });
      }
    }
  };
</script>
  
<style lang="postcss" scoped>
.iam-member-template-wrapper {
    .template-input-wrapper {
      margin-top: 10px;
      margin-bottom: 10px;
    }
    /deep/ .bk-page.bk-page-align-right {
      .bk-page-selection-count-left {
        display: none;
      }
    }
}
</style>
