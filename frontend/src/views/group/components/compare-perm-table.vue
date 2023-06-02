<template>
  <div class="iam-compare-perm-table">
    <bk-table
      :data="tableList"
      border
      :cell-class-name="getCellClass">
      <bk-table-column :label="$t(`m.common['操作']`)" width="200">
        <template slot-scope="{ row }">
          <div>
            <s class="action-name is-delete" :title="row.name" v-if="row.tag === 'delete'">
              {{ row.name }}
            </s>
            <span class="action-name" :title="row.name" v-else>{{ row.name }}</span>
            <iam-svg name="icon-new" ext-cls="action-status-icon" v-if="row.isNew && curLanguageIsCn" />
            <iam-svg name="icon-new-en" ext-cls="action-status-icon" v-if="row.isNew && !curLanguageIsCn" />
            <iam-svg name="has-delete" ext-cls="action-status-icon"
              v-if="row.tag === 'delete' && curLanguageIsCn" />
            <iam-svg name="has-delete-en" ext-cls="action-status-icon"
              v-if="row.tag === 'delete' && !curLanguageIsCn" />
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)">
        <template slot-scope="{ row }">
          <template v-if="!row.isEmpty">
            <div v-for="_ in row.resource_groups" :key="_.id">
              <p class="related-resource-item"
                v-for="item in _.related_resource_types"
                :key="item.type">
                <template v-if="item.tag === 'delete'">
                  <s class="item-label is-delete">{{ item.name + '：'}}</s>
                  <s :title="item.value" class="value is-delete">{{ item.value }}</s>
                </template>
                <template v-else>
                  <label class="item-label">{{ item.name + '：'}}</label>
                  <span :title="item.value" class="value">{{ item.value }}</span>
                </template>
                <iam-svg name="icon-changed" ext-cls="relate-content-status-icon"
                  v-if="item.tag === 'update' && curLanguageIsCn" />
                <iam-svg name="icon-changed-en" ext-cls="relate-content-status-icon"
                  v-if="item.tag === 'update' && !curLanguageIsCn" />
              </p>
            </div>
          </template>
          <template v-else>
            {{ $t(`m.common['无需关联实例']`) }}
          </template>
          <Icon
            type="detail-new"
            :class="['view-icon', { 'is-disabled': row.tag === 'unchanged' }]"
            :title="row.tag === 'unchanged' ? $t(`m.related['无变更内容']`) : $t(`m.related['对比详情']`)"
            v-if="isShowPreview(row)"
            @click.stop="handleViewResource(row)" />
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>
<script>
  import _ from 'lodash';

  export default {
    name: '',
    props: {
      data: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        tableList: []
      };
    },
    computed: {
      isShowPreview () {
        return (payload) => {
          return !payload.isEmpty;
        };
      }
    },
    watch: {
      data: {
        handler (value) {
          this.tableList = _.cloneDeep(value);
        },
        immediate: true
      }
    },
    methods: {
      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 1) {
          return 'iam-perm-table-cell-cls';
        }
        return '';
      },

      handleViewResource (payload) {
        if (payload.tag === 'unchanged') {
          return;
        }
        const { id, related_resource_types, name, attach_actions, tag } = payload;
        this.$emit('on-compare', {
          tag,
          attach_actions,
          action_id: id,
          action_name: name,
          related_resource_types
        });
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-compare-perm-table {
        min-height: 101px;
        .bk-table-enable-row-hover .bk-table-body tr:hover > td {
            background-color: #fff;
        }
        .bk-table {
            border-right: none;
            border-bottom: none;
            .related-resource-item {
                /* line-height: 24px; */
                .item-label {
                    display: inline-block;
                    vertical-align: middle;
                    &.is-delete {
                        color: #c4c6cc;
                    }
                }
                .value {
                    display: inline-block;
                    max-width: 460px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    vertical-align: middle;
                    &.is-delete {
                        color: #c4c6cc;
                    }
                }
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
                        &.is-disabled {
                            cursor: not-allowed;
                        }
                    }
                    &:hover {
                        .view-icon {
                            display: inline-block;
                            color: #3a84ff;
                            &.is-disabled {
                                color: #c4c6cc;
                            }
                        }
                    }
                    .action-name {
                        margin-left: 6px;
                        display: inline-block;
                        max-width: 120px;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        word-break: keep-all;
                        vertical-align: bottom;
                        &.is-delete {
                            color: #c4c6cc;
                        }
                    }
                    .action-status-icon {
                        display: inline-block;
                        position: relative;
                        top: 1px;
                        width: 24px;
                    }
                    .relate-content-status-icon {
                        display: inline-block;
                        width: 24px;
                        vertical-align: middle;
                    }
                }
            }
            tr:hover {
                background-color: #fff;
            }
        }
    }
</style>
