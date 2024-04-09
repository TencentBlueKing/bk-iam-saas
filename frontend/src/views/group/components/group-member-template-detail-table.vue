<template>
  <div
    class="iam-user-group-member member-template-detail-slider"
  >
    <div class="template-search-input">
      <bk-input
        v-model="tableKeyWord"
        class="template-input-wrapper"
        :placeholder="$t(`m.memberTemplate['请输入用户/组织，按enter键搜索']`)"
        :right-icon="'bk-icon icon-search'"
        :clearable="true"
        @clear="handleClearSearch"
        @enter="handleSearchGroup"
        @right-icon-click="handleSearchGroup" />
    </div>
    <bk-table
      size="small"
      ext-cls="user-group-member-table"
      :outer-border="false"
      :header-border="false"
      :data="groupTableList"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column :label="$t(`m.userGroup['用户/组织']`)">
        <template slot-scope="{ row }">
          <div v-if="row.type === 'user'" class="user" :title="`${row.id}(${row.name})`">
            <Icon type="personal-user" />
            <span class="name">{{ row.id }}</span>
            <span class="count" v-if="row.name">
              {{ '(' + row.name + ')' }}
            </span>
          </div>
          <div v-else class="depart" :title="row.full_name">
            <Icon type="organization-fill" />
            <span class="name">
              {{ row.name || '--' }}
            </span>
            <span class="count" v-if="row.member_count && enableOrganizationCount"> ({{ row.member_count }}) </span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.userGroupDetail['所属组织架构']`)">
        <template slot-scope="{ row }">
          <template v-if="row.type === 'user'">
            <template v-if="row.user_departments && row.user_departments.length">
              <div
                :title="row.user_departments.join(';')"
                v-for="(item, index) in row.user_departments"
                :key="index"
                class="user_departs"
              >
                {{ item }}
              </div>
            </template>
            <template v-else>
              <div>--</div>
            </template>
          </template>
          <template v-else>
            {{ row.full_name }}
          </template>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['有效期']`)" prop="expired_at_display" />
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
  export default {
    props: {
      curDetailData: {
        type: Object
      }
    },
    data () {
      return {
        tableLoading: false,
        tableKeyWord: '',
        groupTableList: [],
        searchTableData: [],
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
        },
        enableOrganizationCount: window.ENABLE_ORGANIZATION_COUNT.toLowerCase() === 'true'
      };
    },
    created () {
      this.fetchTemplateGroupList();
    },
    methods: {
      getDataByPage (page) {
        if (!page) {
          this.pagination.current = page = 1;
        }
        let startIndex = (page - 1) * this.pagination.limit;
        let endIndex = page * this.pagination.limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > this.searchTableData.length) {
          endIndex = this.searchTableData.length;
        }
        return this.searchTableData.slice(startIndex, endIndex);
      },

      async fetchTemplateGroupList () {
        this.tableLoading = true;
        try {
          const { current, limit } = this.pagination;
          const { id, template_id } = this.curDetailData;
          const params = {
            id,
            template_id,
            limit,
            offset: limit * (current - 1),
            keyword: this.tableKeyWord
          };
          const { code, data } = await this.$store.dispatch('memberTemplate/getGroupSubjectTemplateMembers', params);
          const { count, results } = data;
          this.pagination.count = count || 0;
          this.groupTableList = results || [];
          if (!data.hasOwnProperty('count')) {
            this.pagination.count = results.length || 0;
            this.searchTableData = [...results || []];
            this.groupTableList = this.getDataByPage(this.pagination.current);
          } else {
            this.pagination.count = count || 0;
            this.groupTableList = results || [];
          }
          this.emptyTableData = formatCodeData(
            code,
            Object.assign(this.emptyTableData, { tipType: this.tableKeyWord.length > 0 ? 'search' : '' }),
            this.groupTableList.length === 0
          );
        } catch (e) {
          this.groupTableList = [];
          this.emptyTableData = formatCodeData(e.code, this.emptyTableData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      handleSearchGroup (payload) {
        this.tableKeyWord = payload;
        this.emptyTableData.tipType = 'search';
        this.resetPagination();
        this.fetchTemplateGroupList();
      },

      handleClearSearch () {
        this.tableKeyWord = '';
        this.emptyTableData.tipType = '';
        this.resetPagination();
        this.fetchTemplateGroupList();
      },

      async handlePageChange (current) {
        this.pagination = Object.assign(this.pagination, { current });
        if (this.emptyTableData.tipType === 'search') {
          const list = this.getDataByPage(current);
          this.groupTableList.splice(0, this.groupTableList.length, ...list);
        } else {
          await this.fetchTemplateGroupList();
        }
      },

      handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit });
        this.handlePageChange(this.pagination.current);
      },

      handleEmptyClear () {
        this.emptyTableData.tipType = '';
        this.tableKeyWord = '';
        this.resetPagination();
        this.fetchTemplateGroupList();
      },

      handleEmptyRefresh () {
        this.handleEmptyClear();
      },

      resetPagination () {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 10 });
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import '@/css/mixins/member-table.css';
.member-template-detail-slider {
  padding: 0 40px;
  .user-group-member-table {
    margin-top: 20px;
  }
}
</style>
