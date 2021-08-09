<template>
    <div class="iam-system-access-wrapper">
        <render-search>
            <bk-button theme="primary" @click="goCreate">{{ $t(`m.common['新增']`) }}</bk-button>
            <!-- <div slot="right" class="right">
                <bk-link theme="primary" :href="'http://www.qq.com'" target="_blank">{{ $t(`m.access['1分钟了解蓝鲸权限中心']`) }}</bk-link>
            </div> -->
        </render-search>
        <bk-table
            :data="tableList"
            size="small"
            :class="{ 'set-border': tableLoading }"
            ext-cls="system-access-table"
            :pagination="pagination"
            @page-change="handlePageChange"
            @page-limit-change="handleLimitChange"
            @select="handlerChange"
            @select-all="handlerAllChange"
            v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
            <!-- <bk-table-column type="selection" align="center"></bk-table-column> -->
            <bk-table-column :label="$t(`m.access['系统名称']`)" :min-width="220">
                <template slot-scope="{ row }">
                    <span class="system-access-name" :title="row.system.name" @click="goDetail(row)">
                        {{ row.system.name }}
                    </span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.access['系统ID']`)">
                <template slot-scope="{ row }">
                    <span :title="row.system.id">{{ row.system.id }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.access['创建者']`)">
                <template slot-scope="{ row }">
                    <span :title="row.owner">{{ row.owner }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['创建时间']`)">
                <template slot-scope="{ row }">
                    <span :title="row.created_time">{{ row.created_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.access['更新时间']`)">
                <template slot-scope="{ row }">
                    <span :title="row.updated_time">{{ row.updated_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)" width="270">
                <template slot-scope="{ row }">
                    <section>
                        <bk-button theme="primary" text @click="goDetail(row)">
                            {{ $t(`m.common['编辑']`) }}
                        </bk-button>
                        <!-- <bk-button
                            theme="primary"
                            text
                            v-if="row.subject_count < 1"
                            @click="handleTemplateDelete(row)">
                            {{ $t(`m.access['查看']`) }}
                        </bk-button>
                        <bk-button
                            theme="primary"
                            text
                            v-if="row.subject_count < 1"
                            @click="handleTemplateDelete(row)">
                            {{ $t(`m.access['访问']`) }}
                        </bk-button>
                        <bk-button
                            theme="primary"
                            disabled
                            text
                            v-else>
                            <span v-bk-tooltips.bottom="$t(`m.access['有关联的组时不能删除']`)">
                                {{ $t(`m.common['删除']`) }}
                            </span>
                        </bk-button> -->
                    </section>
                </template>
            </bk-table-column>
        </bk-table>
    </div>
</template>
<script>
    import { buildURLParams } from '@/common/url'

    export default {
        name: 'system-access-index',
        data () {
            return {
                tableList: [],
                tableLoading: false,
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                currentBackup: 1,
                currentSelectList: []
            }
        },
        watch: {
            'pagination.current' (value) {
                this.currentBackup = value
            }
        },
        created () {
            const currentQueryCache = this.getCurrentQueryCache()
            if (currentQueryCache && Object.keys(currentQueryCache).length) {
                if (currentQueryCache.limit) {
                    this.pagination.limit = currentQueryCache.limit
                    this.pagination.current = currentQueryCache.current
                }
            }
        },
        methods: {
            async fetchPageData () {
                await this.fetchModelingList()
            },

            handleOpenMoreLink () {
                window.open(`${window.PRODUCT_DOC_URL_PREFIX}/权限中心/产品白皮书/场景案例/GradingManager.md`)
            },

            refreshCurrentQuery () {
                const { limit, current } = this.pagination
                const queryParams = { limit, current }
                window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`)
                return queryParams
            },

            setCurrentQueryCache (payload) {
                window.localStorage.setItem('templateList', JSON.stringify(payload))
            },

            getCurrentQueryCache () {
                return JSON.parse(window.localStorage.getItem('templateList'))
            },

            resetPagination () {
                this.pagination = Object.assign({}, {
                    limit: 10,
                    current: 1,
                    count: 0
                })
            },

            async fetchModelingList (isLoading = false) {
                this.tableLoading = isLoading
                this.setCurrentQueryCache(this.refreshCurrentQuery())
                const params = {
                    limit: this.pagination.limit,
                    offset: this.pagination.limit * (this.pagination.current - 1)
                }
                try {
                    const res = await this.$store.dispatch('access/getModelingList', params)
                    this.pagination.count = res.data.count
                    this.tableList.splice(0, this.tableList.length, ...(res.data.results || []))
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.tableLoading = false
                }
            },

            goDetail (payload) {
                this.$router.push({
                    name: 'systemAccessAccess',
                    params: {
                        id: payload.id
                    }
                })
            },

            goCreate () {
                this.$router.push({
                    name: 'systemAccessCreate'
                })
            },

            handlePageChange (page) {
                if (this.currentBackup === page) {
                    return
                }
                this.pagination.current = page
                this.fetchModelingList(true)
            },

            handleLimitChange (currentLimit, prevLimit) {
                this.pagination.limit = currentLimit
                this.pagination.current = 1
                this.fetchModelingList(true)
            },

            handlerAllChange (selection) {
                this.currentSelectList = [...selection]
            },

            handlerChange (selection, row) {
                this.currentSelectList = [...selection]
            }
        }
    }
</script>
<style lang="postcss">
    .iam-system-access-wrapper {
        .right {
            height: 32px;
            line-height: 32px;
        }
        .detail-link {
            color: #3a84ff;
            cursor: pointer;
            &:hover {
                color: #699df4;
            }
            font-size: 12px;
        }
        .system-access-table {
            margin-top: 16px;
            border-right: none;
            border-bottom: none;
            &.set-border {
                border-right: 1px solid #dfe0e5;
                border-bottom: 1px solid #dfe0e5;
            }
            .system-access-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
            .lock-status {
                font-size: 12px;
                color: #fe9c00;
            }
        }
    }
</style>
