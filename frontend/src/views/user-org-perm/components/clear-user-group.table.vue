<template>
  <div class="my-perm-group-perm">
    <bk-table
      ref="groupPermRef"
      size="small"
      ext-cls="user-org-perm-table"
      :data="curPageData"
      :outer-border="false"
      :header-border="false"
      :pagination="curPageConfig"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      v-bkloading="{ isLoading: loading, opacity: 1, zIndex: 1000 }"
    >
      <template v-for="item in tableProps">
        <template v-if="item.prop === 'name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :width="200">
            <template slot-scope="{ row }">
              <span v-bk-tooltips="{ content: formatName(row) }">
                {{ formatName(row) }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'group_perm'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <template v-if="row.perm_list && row.perm_list.length">
                <div class="perm-tag-list">
                  <div
                    ref="permTag"
                    class="single-hide perm-tag-item"
                    v-bk-tooltips="{ content: row.perm_list.map((v) => v.name) }"
                  >
                    <bk-tag
                      theme="danger"
                      v-for="tag in row.perm_list"
                      :key="tag.id">
                      {{tag.name}}
                    </bk-tag>
                  </div>
                  <div class="total-count-tag">
                    <bk-tag theme="danger" v-if="row.count > 5">+{{ row.count - 5}}</bk-tag>
                  </div>
                </div>
              </template>
              <template v-else>--</template>
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
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  export default {
    props: {
      mode: {
        type: String
      },
      curType: {
        type: String
      },
      loading: {
        type: Boolean,
        default: false
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
        curPageConfig: {
          current: 1,
          limit: 10,
          count: 0,
          showTotalCount: true
        },
        tableEmptyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['externalSystemId']),
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
      },
      formatPerm () {
        return (payload) => {
          console.log(payload);
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
      pagination: {
        handler (value) {
          this.curPageConfig = cloneDeep({ ...value, ...{ showTotalCount: true } });
        },
        deep: true,
        immediate: true
      },
      list: {
        handler (value) {
          this.tableList = [...value];
          this.curPageData = this.getDataByPage(this.curPageConfig.current);
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
              { label: this.$t(`m.userOrOrg['清空的个人用户组权限']`), prop: 'group_perm' }
            ];
          },
          department: () => {
            return [
              { label: this.$t(`m.common['用户名']`), prop: 'name' },
              { label: this.$t(`m.userOrOrg['清空的组织用户组权限']`), prop: 'group_perm' }
            ];
          }
        };
        return typeMap[payload] ? typeMap[payload]() : typeMap['user']();
      },

      getDataByPage (page) {
        if (!page) {
          page = 1;
        }
        const { limit } = this.curPageConfig;
        let startIndex = (page - 1) * limit;
        let endIndex = page * limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > this.tableList.length) {
          endIndex = this.tableList.length;
        }
        const result = this.tableList.slice(startIndex, endIndex);
        return result;
      },

      handlePageChange (current) {
        this.curPageConfig = Object.assign(this.curPageConfig, { current });
        const list = this.getDataByPage(current);
        this.curPageData.splice(0, this.curPageData.length, ...list);
        this.$emit('on-page-change', current);
      },

      handleLimitChange (limit) {
        this.curPageConfig = Object.assign(this.curPageConfig, { current: 1, limit });
        const list = this.getDataByPage(1);
        this.curPageData.splice(0, this.curPageData.length, ...list);
        this.$emit('on-limit-change', limit);
      }
    }
  };
</script>

<style lang="postcss" scoped>
/deep/ .user-org-perm-table {
  border-top: 0;
  .perm-tag-list {
    display: flex;
    .perm-tag-item {
      max-width: 580px;
      .bk-tag {
        &:first-child {
          margin-left: 0;
        }
      }
    }
    .total-count-tag {
      min-width: 50px;
      margin-left: 4px;
    }
  }
}
</style>
