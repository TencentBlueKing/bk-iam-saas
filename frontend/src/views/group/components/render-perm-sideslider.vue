<template>
  <bk-sideslider
    :is-show.sync="isShowSideslider"
    :title="title"
    :width="880"
    ext-cls="iam-group-perm-sideslider"
    :quick-close="true"
    :cell-class-name="getCellClass"
    @animation-end="handleAnimationEnd">
    <div
      slot="content"
      class="content-wrapper"
      v-bkloading="{ isLoading, opacity: 1 }">
      <bk-table
        v-if="!isLoading"
        :data="tableList"
        border
        :cell-class-name="getCellClass">
        <bk-table-column :label="$t(`m.common['操作']`)" width="180">
          <template slot-scope="{ row }">
            <span :title="row.name">{{ row.name }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)">
          <template slot-scope="{ row }">
            <template v-if="!row.isEmpty">
              <div v-for="_ in row.resource_groups" :key="_.id">
                <p class="related-resource-item"
                  v-for="item in _.related_resource_types"
                  :key="item.type">
                  <render-resource-popover
                    :key="item.type"
                    :data="item.condition"
                    :value="`${item.name}：${item.value}`"
                    @on-view="handleViewResource(row)" />
                </p>
              </div>
            </template>
            <template v-else>
              {{ $t(`m.common['无需关联实例']`) }}
            </template>
            <Icon
              type="detail-new"
              class="view-icon"
              :title="$t(`m.common['详情']`)"
              v-if="isShowPreview(row)"
              @click.stop="handleViewResource(row)" />
          </template>
        </bk-table-column>
      </bk-table>
    </div>
  </bk-sideslider>
</template>
<script>
  import PermPolicy from '@/model/my-perm-policy';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  export default {
    name: '',
    components: {
      RenderResourcePopover
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      templateId: {
        type: [String, Number],
        default: ''
      },
      systemId: {
        type: [String, Number],
        default: ''
      },
      title: {
        type: String,
        default: ''
      },
      version: {
        type: [String, Number],
        default: ''
      }
    },
    data () {
      return {
        tableList: [],
        policyCountMap: {},
        curId: '',
        isShowSideslider: false,
        requestQueue: ['list']
      };
    },
    computed: {
      isShowPreview () {
        return (payload) => {
          return !payload.isEmpty;
        };
      },
      isLoading () {
        return this.requestQueue.length > 0;
      }
    },
    watch: {
      show: {
        handler (value) {
          this.isShowSideslider = !!value;
          if (this.isShowSideslider) {
            this.handleInit();
          }
        },
        immediate: true
      }
    },
    methods: {
      async handleInit () {
        await this.fetchData();
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 1) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      async fetchData () {
        const params = {
          id: this.templateId
        };
        if (this.version !== '') {
          params.version = this.version;
        }
        try {
          const res = await this.$store.dispatch('permTemplate/getTemplateDetail', params);
          this.tableList = res.data.actions.map(item => new PermPolicy(item));
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.requestQueue.shift();
        }
      },

      handleAnimationEnd () {
        this.tableList = [];
        this.requestQueue = ['list'];
        this.curId = '';
        this.$emit('animation-end');
      },

      handleViewResource (payload) {
        this.curId = payload.id;
        const params = [];
        if (payload.resource_groups.length > 0) {
          payload.resource_groups.forEach(groupItem => {
            if (groupItem.related_resource_types.length > 0) {
              groupItem.related_resource_types.forEach(item => {
                const { name, type, condition } = item;
                params.push({
                  name: type,
                  label: `${name} ${this.$t(`m.common['实例']`)}`,
                  tabType: 'resource',
                  data: condition
                });
              });
            }
          });
        }
        this.$emit('on-view', {
          name: payload.name,
          data: params
        });
      }
    }
  };
</script>
<style lang="postcss">
    .iam-group-perm-sideslider {
        .content-wrapper {
            padding: 30px;
            height: calc(100vh - 60px);
        }
        .bk-table-enable-row-hover .bk-table-body tr:hover > td {
            background-color: #fff;
        }
        .bk-table {
            border-right: none;
            border-bottom: none;
            .bk-table-header-wrapper {
                .cell {
                    padding-left: 20px !important;
                }
            }
            .bk-table-body-wrapper {
                .cell {
                    padding: 20px !important;
                    .view-icon {
                        display: none;
                        position: absolute;
                        top: 50%;
                        right: 10px;
                        transform: translate(0, -50%);
                        font-size: 18px;
                        cursor: pointer;
                    }
                    &:hover {
                        .view-icon {
                            display: inline-block;
                            color: #3a84ff;
                        }
                    }
                }
            }
            tr:hover {
                background-color: #fff;
            }
        }
    }
</style>
