<template>
  <div class="iam-apply-roles-table-wrapper">
    <RenderTable
      :expanded="expanded"
      :data="tableList"
      :type="applyType"
    >
      <bk-table
        size="small"
        border
        ext-cls="roles-table"
        :data="curPageData"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-limit-change="handleLimitChange"
      >
        <bk-table-column :label="$t(`m.permTransfer['管理员名称']`)" prop="name" />
        <bk-table-column :label="$t(`m.common['类型']`)">
          <template slot-scope="{ row }">
            <span>{{ getRolesType(row.type) }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.common['描述']`)">
          <template slot-scope="{ row }">
            <span :title="Boolean(row.description) ? row.description : ''">
              {{ row.description || '--' }}
            </span>
          </template>
        </bk-table-column>
      </bk-table>
    </RenderTable>
  </div>
</template>

<script>
  import { ALL_ROLES_MANAGERS } from '@/common/constants';
  import RenderTable from '../common/render-table';

  export default {
    components: {
      RenderTable
    },
    props: {
      list: {
        type: Array,
        default: () => []
      },
      count: {
        type: Number,
        default: 0
      },
      applyType: {
        type: String,
        default: 'roles_handover'
      }
    },
    data () {
      return {
        tableList: [],
        curPageData: [],
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        expanded: true
      };
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      },
      list: {
        handler (value) {
          this.tableList = [...value];
          this.curPageData = this.getDataByPage(this.pagination.current);
        },
        immediate: true
      },
      count: {
        handler (value) {
          this.pagination.count = value;
        },
        immediate: true
      }
    },
    methods: {
      getRolesType (role) {
        const roleData = ALL_ROLES_MANAGERS.find(item => item.value === role);
        if (roleData) {
          return roleData.label;
        }
        return '--';
      },

      getDataByPage (page) {
        if (!page) {
          this.pagination.current = page = 1;
        }
        let startIndex = (page - 1) * this.pagination.limit;
        let endIndex = page * this.pagination.limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > this.tableList.length) {
          endIndex = this.tableList.length;
        }
        return this.tableList.slice(startIndex, endIndex);
      },

      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        const data = this.getDataByPage(page);
        this.curPageData.splice(0, this.curPageData.length, ...data);
      },

      handleLimitChange (currentLimit, prevLimit) {
        this.pagination.current = 1;
        this.pagination.limit = currentLimit;
        const data = this.getDataByPage(this.pagination.current);
        this.curPageData.splice(0, this.curPageData.length, ...data);
      },

      handleResetPagination () {
        this.pagination = Object.assign({}, {
          limit: 10,
          current: 1,
          count: 0
        });
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-apply-roles-table-wrapper {
  margin-top: 16px;

  .roles-table {
    border-right: none;
    border-bottom: none;
  }
}
</style>
