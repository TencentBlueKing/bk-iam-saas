<template>
    <div class="iam-user-group-template-perm-table">
        <bk-table
            :data="tableList"
            border
            :cell-class-name="getCellClass">
            <bk-table-column :label="$t(`m.common['操作']`)">
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
                                    :max-width="380"
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
            :width="725"
            :quick-close="true"
            @animation-end="handleAnimationEnd">
            <div slot="content">
                <component :is="renderDetailCom" :data="previewData" />
            </div>
        </bk-sideslider>
    </div>
</template>
<script>
    import _ from 'lodash';
    import store from '@/store';
    import RenderResourcePopover from '@/components/iam-view-resource-popover';
    import RenderDetail from '../common/render-detail';
    import PermPolicy from '@/model/my-perm-policy';
    export default {
        name: '',
        components: {
            RenderResourcePopover,
            RenderDetail
        },
        data () {
            return {
                tableList: [],
                policyCountMap: {},
                previewData: [],
                curId: '',
                renderDetailCom: 'RenderDetail',
                isShowSideslider: false,
                sidesliderTitle: '',
                templateId: '',
                systemId: ''
            };
        },
        computed: {
            isShowPreview () {
                return (payload) => {
                    return !payload.isEmpty;
                };
            }
        },
        beforeRouteEnter (to, from, next) {
            store.commit('setHeaderTitle', `${to.query.name}(${to.query.system_name})`);
            next();
        },
        created () {
            this.templateId = this.$route.params.templateId;
            this.systemId = this.$route.params.id;
        },
        methods: {
            async fetchPageData () {
                await this.fetchData();
            },

            getCellClass ({ row, column, rowIndex, columnIndex }) {
                if (columnIndex === 1) {
                    return 'iam-perm-table-cell-cls';
                }
                return '';
            },

            async fetchData () {
                try {
                    const res = await this.$store.dispatch('permTemplate/getTemplateDetail', { id: this.templateId });
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
                }
            },

            handleAnimationEnd () {
                this.sidesliderTitle = '';
                this.previewData = [];
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
                                    label: `${name}实例`,
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
    .iam-user-group-template-perm-table {
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
