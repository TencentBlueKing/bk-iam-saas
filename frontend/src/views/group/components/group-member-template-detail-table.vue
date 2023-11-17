<template>
  <div
    class="iam-user-group-member member-template-detail-slider"
    v-bkloading="{ isLoading: tableLoading, opacity: 1, zIndex: 1000 }">
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
    created () {
      this.fetchAssociateGroupDetail();
    },
    methods: {
      async fetchAssociateGroupDetail (isTableLoading = false) {
        this.tableLoading = isTableLoading;
        try {
          const { id } = this.curDetailData;
          const { data } = await this.$store.dispatch('memberTemplate/subjectTemplateDetail', { id });
          console.log(333, data);
          this.emptyTableData = formatCodeData(0, this.emptyTableData, true);
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      handleSearchGroup (payload) {
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

      handleConfirmDisassociate () {},

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

<style lang="postcss" scoped>
@import '@/css/mixins/member-table.css';
.member-template-detail-slider {
  .user-group-member-table {
    padding: 0 40px;
    margin-top: 0;
  }
}
</style>
