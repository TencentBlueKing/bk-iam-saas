<template>
  <div>
    <bk-table
      ref="groupMemberRef"
      size="small"
      ext-cls="user-group-perm-table"
      :data="curPageData"
      :outer-border="false"
      :header-border="false"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
    >
      <template v-for="item in tableProps">
        <template v-if="item.prop === 'name'">
          <bk-table-column :key="item.prop" :label="item.label" :prop="item.prop">
            <template slot-scope="{ row }">
              <span
                v-bk-tooltips="{
                  content: row.name,
                  placements: ['right-start']
                }"
                :class="[
                  { 'can-view-name': row.isViewDetail }
                ]"
                @click.stop="handleOpenTag(row, 'name')"
              >
                {{ row.name || '--' }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'related_policy_actions'">
          <bk-table-column :key="item.prop" :label="item.label" :prop="item.prop">
            <template slot-scope="{ row }">
              <template v-if="row.related_policy_actions && row.related_policy_actions.length > 0">
                <span
                  v-bk-tooltips="{
                    content: formatRelatedPolicy(row.related_policy_actions),
                    placements: ['left-start']
                  }"
                >
                  {{ formatRelatedPolicy(row.related_policy_actions) }}
                </span>
              </template>
              <span v-else>--</span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'operate'">
          <bk-table-column :key="item.prop" :label="item.label" :prop="item.prop" :fixed="'right'" :width="80">
            <template slot-scope="{ row }">
              <bk-button theme="primary" text @click.stop="handleRemove(row)">
                {{ $t(`m.common['移除']`) }}
              </bk-button>
            </template>
          </bk-table-column>
        </template>
        <template v-else>
          <bk-table-column :key="item.prop" :label="item.label" :prop="item.prop">
            <template slot-scope="{ row }">
              <span v-bk-tooltips="{ content: row[item.prop], disabled: !row[item.prop], placements: ['right-start'] }">
                {{ row[item.prop] || '--' }}
              </span>
            </template>
          </bk-table-column>
        </template>
      </template>
      <template slot="empty">
        <ExceptionEmpty
          :type="tableEmptyData.type"
          :empty-text="tableEmptyData.text"
          :tip-text="tableEmptyData.tip"
          :tip-type="tableEmptyData.tipType"
        />
      </template>
    </bk-table>
  </div>
</template>

<script>
  import { bus } from '@/common/bus';
  import { formatCodeData } from '@/common/util';
  export default {
    props: {
      mode: {
        type: String
      },
      list: {
        type: Array,
        default: () => []
      },
      noShowList: {
        type: Array,
        default: () => []
      },
      expiredAtNew: {
        type: Number
      }
    },
    data () {
      return {
        curPageData: [],
        tableList: [],
        tableProps: [],
        pagination: {
          current: 1,
          limit: 10,
          count: 0
        },
        tableEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      formatRelatedPolicy () {
        return (payload) => {
          if (payload && payload.length) {
            return payload.map((v) => v.name).join();
          }
          return '--';
        };
      }
    },
    watch: {
      list: {
        handler (value) {
          this.tableList = [...value];
          this.pagination = Object.assign(this.pagination, { current: 1, count: value.length });
          this.curPageData = this.getDataByPage(this.pagination.current);
        },
        immediate: true
      },
      mode: {
        handler (value) {
          this.tableProps = this.getTableProps(value);
        },
        immediate: true
      },
      expiredAtNew: {
        handler (value) {
          this.expiredAt = value;
        },
        immediate: true
      }
    },
    methods: {
      getTableProps (payload) {
        const typeMap = {
          quit: () => {
            return [
              { label: this.$t(`m.userGroup['用户组名']`), prop: 'name', isViewDetail: true },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
            ];
          },
          deleteAction: () => {
            return [
              { label: this.$t(`m.common['操作名']`), prop: 'name', isViewDetail: false },
              { label: this.$t(`m.perm['关联操作']`), prop: 'related_policy_actions' },
              { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
            ];
          }
        };
        if (typeMap[payload]) {
          return typeMap[payload]();
        }
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

      handleOpenTag ({ name, id, isViewDetail }, type) {
        if (isViewDetail) {
          const routeMap = {
            name: () => {
              bus.$emit('on-batch-view-group-perm', {
                name,
                id,
                show: true,
                width: 1160
              });
            }
          };
          return routeMap[type]();
        }
      },

      handleRemove (payload) {
        this.tableList.splice(this.tableList.indexOf(payload), 1);
        this.pagination.count = this.tableList.length;
        if (!this.tableList.length) {
          this.tableEmptyData = formatCodeData(0, this.tableEmptyData, true);
        }
        let noSelectTableList = [];
        // 需要处理不能移除的用户组权限
        if (['quit'].includes(this.mode)) {
          noSelectTableList = [...this.noShowList];
        }
        const list = [...this.tableList, ...noSelectTableList];
        this.handlePageChange(this.pagination.current);
        this.$emit('on-remove-group', list);
        // 同步更新checkbox状态
        bus.$emit('on-remove-perm-checkbox', list);
      },

      handlePageChange (page = 1) {
        this.pagination.current = page;
        const list = this.getDataByPage(page);
        this.curPageData.splice(0, this.curPageData.length, ...list);
      },

      handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit });
        this.handlePageChange(this.pagination.current);
      }
    }
  };
</script>

<style lang="postcss" scoped>
/deep/ .user-group-perm-table {
  border: none;
  .bk-table-header-wrapper {
    th {
      &:nth-child(1) {
        .cell {
          padding-left: 36px;
        }
      }
    }
  }
  .bk-table-body-wrapper {
    td, th {
      &:nth-child(1) {
        .cell {
          padding-left: 36px;
        }
      }
    }
  }
  .bk-table-empty-block {
    border: none;
  }
  .bk-table-fixed,
  .bk-table-fixed-right {
    border-bottom: 0;
  }
  .can-view-name {
    color: #3A84FF;
    cursor: pointer;
  }
}
</style>
