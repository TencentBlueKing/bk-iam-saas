<template>
  <div class="iam-member-template-wrapper">
    <render-search>
      <div class="search_left">
        <bk-button theme="primary" @click="handleCreate">
          {{ $t(`m.common['新建']`) }}
        </bk-button>
        <bk-button :disabled="isBatchDisabled" @click="handleBatchAddMember">
          {{ $t(`m.common['批量添加成员']`) }}
        </bk-button>
      </div>
      <div slot="right">
        <IamSearchSelect
          style="width: 420px"
          :placeholder="$t(`m.memberTemplate['搜索模板名称、描述、创建人']`)"
          :data="searchData"
          :value="searchValue"
          :quick-search-method="quickSearchMethod"
          @on-change="handleSearch"
        />
      </div>
    </render-search>
    <bk-table
      ref="tableRef"
      size="small"
      ext-cls="member-template-table"
      :data="memberTemplateList"
      :max-height="tableHeight"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column type="selection" align="center" :selectable="getIsSelect" reserve-selection />
      <bk-table-column :label="$t(`m.memberTemplate['模板名称']`)" :sortable="true">
        <template slot-scope="{ row }">
          <span class="user-group-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['描述']`)">
        <template slot-scope="{ row }">
          <span :title="row.description || ''">{{ row.description || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.memberTemplate['关联用户组']`)" :sortable="true">
        <template slot-scope="{ row }">
          <span :title="row.created_time">{{ row.created_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.memberTemplate['创建人']`)">
        <template slot-scope="{ row }">
          <span>{{ row.creator || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.memberTemplate['最近更新时间']`)" width="240">
        <template slot-scope="{ row }">
          <span :title="row.created_time">{{ row.created_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)" width="320" fixed="right">
        <template slot-scope="{ row }">
          <div>
            <bk-button theme="primary" text :disabled="row.readonly" @click="handleAddMember(row)">
              {{ $t(`m.common['添加成员']`) }}
            </bk-button>
            <bk-button theme="primary" text style="margin-left: 10px" @click="handleDelete(row)">
              {{ $t(`m.common['删除']`) }}
            </bk-button>
          </div>
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
  </div>
</template>

<script>
  import _ from 'lodash';
  import { formatCodeData, getWindowHeight } from '@/common/util';
  import IamSearchSelect from '@/components/iam-search-select';
  export default {
    components: {
      IamSearchSelect
    },
    data () {
      return {
        memberTemplateList: [],
        currentSelectList: [],
        searchList: [],
        searchValue: [],
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.memberTemplate['模板名称']`),
            default: true
          },
          {
            id: 'description',
            name: this.$t(`m.memberTemplate['描述']`),
            default: true
          },
          {
            id: 'creator',
            name: this.$t(`m.grading['创建人']`),
            default: true
          }
        ],
        searchParams: {},
        queryParams: {},
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
      isBatchDisabled () {
        return this.memberTemplateList.length === 0;
      },
      tableHeight () {
        return getWindowHeight() - 185;
      }
    },
    async created () {
      await this.fetchMemberTemplateList(true);
    },
    methods: {
      async fetchMemberTemplateList (tableLoading = false) {
        try {
          this.emptyData = formatCodeData(0, this.emptyData, true);
        } catch (e) {
          console.error(e);
        }
      },

      async handleSearch (payload, result) {
        this.searchParams = payload;
        this.searchList = result;
        this.emptyData.tipType = 'search';
        this.queryParams = Object.assign(this.queryParams, {
          current: 1,
          limit: 10
        });
        this.resetPagination();
        await this.fetchMemberTemplateList(true);
      },

      handleBatchAddMember () {
        const hasDisabledData = this.currentSelectList.filter((item) => item.readonly);
        if (hasDisabledData.length) {
          const disabledNames = hasDisabledData.map((item) => item.name);
          this.messageWarn(
            this.$t(`m.info['用户组为只读用户组不能添加成员']`, {
              value: `${this.$t(`m.common['【']`)}${disabledNames}${this.$t(`m.common['】']`)}`
            }),
            3000
          );
          return;
        }
        this.isBatch = true;
        this.isShowAddMemberDialog = true;
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectList.push(row);
            } else {
              this.currentSelectList = this.currentSelectList.filter((item) => item.id !== row.id);
            }
            this.$nextTick(() => {
              const selectionCount = document.getElementsByClassName('bk-page-selection-count');
              if (this.$refs.sensitivityTableRef && selectionCount) {
                selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
              }
            });
          },
          all: () => {
            const tableList = _.cloneDeep(this.memberTemplateList);
            const selectGroups = this.currentSelectList.filter((item) => !tableList.map((v) => v.id).includes(item.id));
            this.currentSelectList = [...selectGroups, ...payload];
            this.$nextTick(() => {
              const selectionCount = document.getElementsByClassName('bk-page-selection-count');
              if (this.$refs.sensitivityTableRef && selectionCount) {
                selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
              }
            });
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

      handlePageChange (page) {
        this.pagination.current = page;
        this.fetchMemberTemplateList(true);
      },

      handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { limit });
        this.fetchMemberTemplateList(true);
      },

      handleEmptyClear () {},

      handleEmptyRefresh () {},

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
        return this.memberTemplateList.length > 0;
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
.iam-member-template-wrapper {
  .member-template-table {
    margin-top: 20px;
  }
}
</style>
