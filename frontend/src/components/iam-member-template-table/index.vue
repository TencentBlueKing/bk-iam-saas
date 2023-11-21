<template>
  <div class="iam-member-template-wrapper">
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
        row-key="id"
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
          />
        </template>
      </bk-table>
    </div>
  </div>
</template>
  
<script>
  import _ from 'lodash';
  import { formatCodeData } from '@/common/util';
  export default {
    props: {
      hasSelectedTemplates: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        tableLoading: false,
        tableKeyWord: '',
        currentSelectList: [],
        templateTableList: [],
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
          console.log(this.currentSelectList);
        },
        immediate: true
      }
    },
    created () {
      this.fetchTemplateList();
    },
    methods: {
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
              if (currentSelectList.includes(String(item.id))) {
                this.$refs.templateTableRef
                  && this.$refs.templateTableRef.toggleRowSelection(item, true);
              }
            });
            if (this.currentSelectList.length < 1) {
              this.$refs.templateTableRef
                && this.$refs.templateTableRef.clearSelection();
            }
          });
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
            this.fetchCustomSelection();
            this.$emit('on-selected-templates', this.currentSelectList);
          },
          all: () => {
            const tableList = _.cloneDeep(this.templateTableList);
            const selectGroups = this.currentSelectList.filter(
              (item) => !tableList.map((v) => v.id.toString()).includes(item.id.toString())
            );
            this.currentSelectList = [...selectGroups, ...payload];
            this.fetchCustomSelection();
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

      fetchCustomSelection () {
        this.$nextTick(() => {
          const selectionCount = document.getElementsByClassName('bk-page-selection-count');
          if (this.$refs.templateTableRef && selectionCount && selectionCount.length && selectionCount[0].children) {
            selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
          }
        });
      },

      getDefaultSelect () {
        return this.templateTableList.length > 0;
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
        margin-bottom: 10px;
    }
    /deep/ .template-table-wrapper {
        .template-table {
            .template-name {
               color: #3a84ff;
            }
        }
    }
}
</style>
