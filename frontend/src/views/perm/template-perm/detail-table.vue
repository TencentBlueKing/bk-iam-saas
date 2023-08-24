<template>
  <div class="iam-perm-table">
    <bk-table
      :data="renderList"
      border
      :ext-cls="loading ? 'is-being-loading' : ''"
      :cell-class-name="getCellClass"
      v-bkloading="{ isLoading: loading, opacity: 1 }">
      <bk-table-column :label="$t(`m.common['操作']`)" width="300">
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
                  :max-width="320"
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

    <bk-sideslider
      :is-show.sync="isShowSideslider"
      :title="sidesliderTitle"
      :width="960"
      :quick-close="true"
      @animation-end="handleAnimationEnd">
      <!-- style="padding: 0 35px 17px 35px;" -->
      <div slot="content">
        <component :is="renderDetailCom" :data="previewData" />
      </div>
    </bk-sideslider>
  </div>
</template>
<script>
  import _ from 'lodash';
  import RenderResourcePopover from '@/components/iam-view-resource-popover';
  import RenderDetail from '../components/render-detail';

  export default {
    name: '',
    components: {
      RenderResourcePopover,
      RenderDetail
    },
    props: {
      systemId: {
        type: String,
        default: ''
      },
      tableList: {
        type: Array,
        default: () => []
      },
      attachActions: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        initRequestQueue: [],
        previewData: [],
        curId: '',
        renderDetailCom: 'RenderDetail',
        isShowSideslider: false,
        renderList: [],
        sidesliderTitle: ''
      };
    },
    computed: {
      loading () {
        return this.initRequestQueue.length > 0;
      },
      isShowPreview () {
        return (payload) => {
          return !payload.isEmpty;
        };
      }
    },
    watch: {
      tableList: {
        handler (value) {
          this.renderList.splice(0, this.renderList.length, ...(value || []));
        },
        immediate: true
      }
    },
    methods: {
      handleAnimationEnd () {
        this.sidesliderTitle = '';
        this.previewData = [];
        this.curId = '';
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 1) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
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
                  label: this.$t(`m.info['tab操作实例']`, { value: name }),
                  tabType: 'resource',
                  data: condition
                });
              });
            }
          });
        }
        this.previewData = _.cloneDeep(params);
        this.sidesliderTitle = this.$t(`m.info['操作侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}` });
        // this.sidesliderTitle = `${this.$t(`m.common['操作']`)}${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的资源实例']`)}`;
        this.isShowSideslider = true;
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-perm-table {
        .bk-table-enable-row-hover .bk-table-body tr:hover > td {
            background-color: #fff;
        }
        .bk-table {
            border-right: none;
            border-bottom: none;
            &.is-being-loading {
                border-right: 1px solid #dfe0e5;
                border-bottom: 1px solid #dfe0e5;
            }
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
    .iam-delete-perm-dialog {
        .bk-dialog-body {
            display: none;
        }
        .bk-dialog-footer {
            border-top: none;
            background: #fff;
            padding: 0 65px 40px;
        }
    }
</style>
