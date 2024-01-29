<template>
  <div class="my-perm-group-perm">
    <bk-table
      ref="groupPermRef"
      size="small"
      ext-cls="user-org-perm-table"
      :data="curPageData"
      :outer-border="false"
      :header-border="false"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
    >
      <template v-for="item in tableProps">
        <template v-if="item.prop === 'name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <div>
                {{ formatName(row) }}
              </div>
            </template>
          </bk-table-column>
        </template>
        <template v-else>
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
          >
            <template slot-scope="{ row }">
              <span :title="row[item.prop] || ''">{{ row[item.prop] || '--'}}</span>
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
  export default {
    props: {
      mode: {
        type: String
      },
      pagination: {
        type: Object,
        default: () => {
          return {
            current: 1,
            limit: 10,
            count: 0,
            showTotalCount: true
          };
        }
      },
      list: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        tableProps: [],
        tableList: [],
        curPageData: [],
        tableEmptyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      formatName () {
        return (payload) => {
          const { id, type, name } = payload;
          const typeMap = {
            user: () => {
              return `${id}${this.$t(`m.common['（']`)}${name}${this.$t(`m.common['）']`)}`;
            },
            department: () => {
              return name;
            }
          };
          if (typeMap[type]) {
            return typeMap[type]();
          }
          return '';
        };
      }
    },
    watch: {
      curType: {
        handler (value) {
          this.tableProps = this.getTableProps(value);
        },
        immediate: true
      },
      list: {
        handler (value) {
          this.tableList = [...value];
          this.curPageData = this.getDataByPage(this.pagination.current);
        },
        immediate: true
      }
    },
    methods: {
      getTableProps (payload) {
        const typeMap = {
          user: () => {
            return [
              { label: this.$t(`m.common['用户名']`), prop: 'name' },
              { label: this.$t(`m.userOrOrg['清空的个人用户组权限']`), prop: 'clear_perm' }
            ];
          },
          department: () => {
            return [
              { label: this.$t(`m.common['用户名']`), prop: 'name' },
              { label: this.$t(`m.userOrOrg['清空的组织用户组权限']`), prop: 'clear_perm' }
            ];
          }
        };
        return typeMap[payload] ? typeMap[payload]() : typeMap['user']();
      },

      getDataByPage (page) {
        if (!page) {
          page = 1;
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

      handlePageChange (current) {
        const list = this.getDataByPage(current);
        this.curPageData.splice(0, this.curPageData.length, ...list);
        this.$emit('on-page-change', current);
      },

      handleLimitChange (limit) {
        this.handlePageChange(1);
        this.$emit('on-limit-change', limit);
      }
    }
  };
</script>

<style lang="postcss" scoped>

</style>
