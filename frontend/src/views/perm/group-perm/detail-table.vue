<template>
    <div class="iam-perm-table" v-bkloading="{ isLoading: loading, opacity: 1 }">
        <bk-table
            v-if="!loading"
            :data="tableList"
            border
            :cell-class-name="getCellClass">
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
            :width="880"
            :quick-close="true"
            @animation-end="handleAnimationEnd">
            <div slot="content">
                <!-- style="padding: 0 30px 17px 30px;" -->
                <component :is="renderDetailCom" :data="previewData" />
            </div>
        </bk-sideslider>
    </div>
</template>
<script>
    import _ from 'lodash';
    import RenderResourcePopover from '@/components/iam-view-resource-popover';
    import RenderDetail from '../components/render-detail';
    import PermPolicy from '@/model/my-perm-policy';

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
            templateId: {
                type: String,
                default: ''
            },
            version: {
                type: Number,
                default: -1
            }
        },
        data () {
            return {
                initRequestQueue: ['permTable'],
                previewData: [],
                curId: '',
                renderDetailCom: 'RenderDetail',
                isShowSideslider: false,
                tableList: [],
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
            templateId: {
                handler (value) {
                    if (value !== '') {
                        this.initRequestQueue = ['permTable'];
                        this.fetchData(value);
                    } else {
                        this.renderDetailCom = 'RenderDetail';
                        this.initRequestQueue = [];
                        this.tableList = [];
                        this.curDeleteIds = [];
                        this.policyCountMap = {};
                    }
                },
                immediate: true
            }
        },
        methods: {
            async fetchData (payload) {
                try {
                    const res = await this.$store.dispatch('perm/getTemplateDetail', {
                        id: payload,
                        version: this.version
                    });
                    const data = res.data || {};
                    this.tableList.splice(0, this.tableList.length, ...data.actions.map(item => new PermPolicy(item)));
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
                    this.initRequestQueue.shift();
                }
            },

            getCellClass ({ row, column, rowIndex, columnIndex }) {
                if (columnIndex === 1) {
                    return 'iam-perm-table-cell-cls';
                }
                return '';
            },

            handleAnimationEnd () {
                this.sidesliderTitle = '';
                this.previewData = [];
                this.actionTopologyData = [];
                this.curId = '';
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
                this.previewData = _.cloneDeep(params);
                this.sidesliderTitle = `${this.$t(`m.common['操作']`)}${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的资源实例']`)}`;
                this.isShowSideslider = true;
            }
        }
    };
</script>
<style lang='postcss'>
    .iam-perm-table {
        min-height: 101px;
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
