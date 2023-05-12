<template>
    <div class="iam-join-template-table-wrapper">
        <render-table
            :expanded="expanded"
            :data="tableList"
            type="template">
            <bk-table
                :data="curPageData"
                size="small"
                ext-cls="template-table"
                :pagination="pagination"
                @page-change="pageChange"
                @page-limit-change="limitChange">
                <bk-table-column :label="$t(`m.common['模板名称']`)">
                    <template slot-scope="{ row }">
                        <span class="template-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.common['所属系统']`)">
                    <template slot-scope="{ row }">
                        <span :title="row.system.name">{{ row.system.name }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.common['描述']`)">
                    <template slot-scope="{ row }">
                        <span :title="row.description !== '' ? row.description : ''">
                            {{ row.description || '--' }}
                        </span>
                    </template>
                </bk-table-column>
            </bk-table>
        </render-table>

        <render-perm-sideslider
            :show="isShowPermSidesilder"
            :title="permSidesilderTitle"
            :template-id="curTemplateId"
            :template-version="curTemplateVersion"
            @on-view="handleOnView"
            @animation-end="handleAnimationEnd" />

        <bk-sideslider
            :is-show.sync="isShowSideslider"
            :title="sidesliderTitle"
            :width="880"
            :quick-close="true"
            @animation-end="handleViewResourceAnimationEnd">
            <div slot="content">
                <component :is="renderDetailCom" :data="previewData" />
            </div>
        </bk-sideslider>
    </div>
</template>
<script>
    import _ from 'lodash';
    import RenderTable from './render-table';
    import RenderPermSideslider from '../../perm/components/render-template-perm-sideslider';
    import RenderDetail from '../../perm/components/render-detail';

    export default {
        name: '',
        components: {
            RenderTable,
            RenderPermSideslider,
            RenderDetail
        },
        props: {
            data: {
                type: Array,
                default: () => []
            },
            count: {
                type: Number,
                default: 0
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
                expanded: false,
                isShowPermSidesilder: false,
                permSidesilderTitle: '',
                curTemplateId: '',
                curTemplateVersion: '',

                previewData: [],
                sidesliderTitle: '',
                isShowSideslider: false,
                renderDetailCom: 'RenderDetail'
            };
        },
        watch: {
            'pagination.current' (value) {
                this.currentBackup = value;
            },
            data: {
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
            /**
             * handleResetPagination
             */
            handleResetPagination () {
                this.pagination = Object.assign({}, {
                    limit: 10,
                    current: 1,
                    count: 0
                });
            },

            /**
             * getDataByPage
             */
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

            /**
             * handleView
             */
            handleView (payload) {
                this.curTemplateId = payload.id;
                this.curTemplateVersion = payload.version || '';
                this.permSidesilderTitle = `${payload.name}(${payload.system_name})`;
                this.isShowPermSidesilder = true;
            },

            /**
             * handleOnView
             */
            handleOnView (payload) {
                const { name, data } = payload;
                this.sidesliderTitle = `${this.$t(`m.common['操作']`)}${this.$t(`m.common['【']`)}${name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的资源实例']`)}`;
                this.previewData = _.cloneDeep(data);
                this.isShowSideslider = true;
            },

            /**
             * handleAnimationEnd
             */
            handleAnimationEnd () {
                this.permSidesilderTitle = '';
                this.curTemplateVersion = '';
                this.curTemplateId = '';
                this.isShowPermSidesilder = false;
            },

            /**
             * handleViewResourceAnimationEnd
             */
            handleViewResourceAnimationEnd () {
                this.previewData = [];
                this.sidesliderTitle = '';
                this.isShowSideslider = false;
            },

            /**
             * pageChange
             */
            pageChange (page) {
                if (this.currentBackup === page) {
                    return;
                }
                this.pagination.current = page;
                const data = this.getDataByPage(page);
                this.curPageData.splice(0, this.curPageData.length, ...data);
            },

            /**
             * limitChange
             */
            limitChange (currentLimit, prevLimit) {
                this.pagination.limit = currentLimit;
                this.pagination.current = 1;
                const data = this.getDataByPage(this.pagination.current);
                this.curPageData.splice(0, this.curPageData.length, ...data);
            }
        }
    };
</script>
<style lang="postcss">
    .iam-join-template-table-wrapper {
        margin-top: 20px;
        .template-table {
            margin-top: 16px;
            border-right: none;
            border-bottom: none;
            .template-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
        }
    }
</style>
