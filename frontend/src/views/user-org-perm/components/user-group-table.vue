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
          <bk-table-column :key="item.prop" :label="item.label" :prop="item.prop" :min-width="200">
            <template slot-scope="{ row }">
              <span
                v-bk-tooltips="{
                  content: row.name,
                  placements: ['right-start']
                }"
                class="can-view-name"
                @click.stop="handleOpenTag(row, 'userGroupDetail')"
              >
                {{ row.name || '--' }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'expired_at_display'">
          <bk-table-column :key="item.prop" :label="item.label" :prop="item.prop">
            <template slot-scope="{ row }">
              <div :class="[
                'renewal-expired-at',
                { 'renewal-expired-at-near': formatHasExpired(row) }
              ]">
                <render-expire-display
                  selected
                  :renewal-time="expiredAt"
                  :cur-time="row.expired_at || 0"
                  :line-height="'22px'"
                />
              </div>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'operate'">
          <bk-table-column :key="item.prop" :label="item.label" :prop="item.prop" :width="'auto'">
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
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { formatCodeData, getNowTimeExpired } from '@/common/util';
  import renderExpireDisplay from '@/components/render-renewal-dialog/display';
  export default {
    components: {
      renderExpireDisplay
    },
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
        expiredAt: 15552000,
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
      ...mapGetters(['user']),
      formatHasExpired () {
        return (payload) => {
          const diff = payload.expired_at - getNowTimeExpired();
          if (diff < 1) {
            return true;
          }
         const days = Math.round(diff / (24 * 3600));
         return payload.expired_at < getNowTimeExpired() || days < 16;
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
          remove: () => {
            return [
              { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
            ];
          },
          renewal: () => {
            return [
              { label: this.$t(`m.userGroup['用户组名']`), prop: 'name' },
              { label: this.$t(`m.common['描述']`), prop: 'description' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' },
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

      handleOpenTag ({ id }, type) {
        const routeMap = {
          userGroupDetail: () => {
            const routeData = this.$router.resolve({
              path: `user-group-detail/${id}`,
              query: {
                noFrom: true,
                tab: 'group_perm'
              }
            });
            window.open(routeData.href, '_blank');
          }
        };
        return routeMap[type]();
      },

      handleRemove (payload) {
        this.tableList.splice(this.tableList.indexOf(payload), 1);
        this.pagination.count = this.tableList.length;
        this.handlePageChange(this.pagination.current);
        if (!this.tableList.length) {
          this.tableEmptyData = formatCodeData(0, this.tableEmptyData, true);
        }
        // 需要处理不需要续期和不能移除的用户组权限
        const noSelectTableList = [...this.noShowList];
        const list = [...this.tableList, ...noSelectTableList];
        this.$emit('on-remove-group', list);
        // 同步更新checkbox状态
        bus.$emit('on-remove-toggle-checkbox', list);
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
  border: 0;
  .bk-table-empty-block {
    border: none;
  }
  .can-view-name {
    color: #3A84FF;
    cursor: pointer;
  }
  .renewal-expired-at {
    .iam-expire-time-wrapper {
      .cur-text {
        font-size: 12px;
      }
      .after-renewal-icon {
        font-size: 20px;
      }
      .after-renewal-text {
        font-size: 12px;
        color: #3a84ff;
      }
    }
    &-near {
      .iam-expire-time-wrapper {
        .cur-text {
          background-color: #FFF1DB;
          color: #FE9C00;
          padding: 0 8px;
          border-radius: 2px;
        }
      }
    }
  }
}
</style>
