<template>
    <div class="iam-system-access-wrapper">
        <render-search>
            <!-- <bk-button theme="primary" @click="goCreate">{{ $t(`m.common['新增']`) }}</bk-button> -->
            <span class="display-name">同步记录</span>
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
            <bk-table-column :label="$t(`m.user['开始时间']`)" :min-width="220">
                <template slot-scope="{ row }">
                    <span class="system-access-name" :title="row.system.name" @click="goDetail(row)">
                        {{ row.system.name }}
                    </span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.user['耗时']`)">
                <template slot-scope="{ row }">
                    <span :title="row.system.id">{{ row.system.id }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.user['操作人']`)">
                <template slot-scope="{ row }">
                    <span :title="row.owner">{{ row.owner }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.user['触发类型']`)" :sortable="true" sort-by="created_time">
                <template slot-scope="{ row }">
                    <span :title="row.created_time">{{ row.created_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.audit['状态']`)" :sortable="true" sort-by="updated_time">
                <template slot-scope="{ row }">
                    <span :title="row.updated_time">{{ row.updated_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)" width="270">
                <template slot-scope="{ row }">
                    <section>
                        <bk-button theme="primary" text @click="showLogDetails(row)">
                            {{ $t(`m.user['日志详情']`) }}
                        </bk-button>
                    </section>
                </template>
            </bk-table-column>

        </bk-table>

        <bk-sideslider
            :is-show.sync="isShowLogDetails"
            title="日志详情"
            :width="725"
            :quick-close="true"
            @animation-end="handleAnimationEnd">
            <div slot="content">
                <log-details v-model="detailData" :value="detailData"></log-details>
            </div>
        </bk-sideslider>
    </div>
</template>
<script>
    import { buildURLParams } from '@/common/url'
    import LogDetails from './log-details'

    export default {
        name: 'system-access-index',
        components: {
            LogDetails
        },
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
                currentSelectList: [],
                isShowLogDetails: false,
                detailData: '测试'
            }
        },
        watch: {
            'pagination.current' (value) {
                this.currentBackup = value
            }
        },
        created () {
            console.log(123455)
            this.fetchPageData()
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
                await this.fetchModelingList(true)
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
                    res.data.results = res.data.results.length && res.data.results.sort(
                        (a, b) => new Date(b.updated_time) - new Date(a.updated_time))
                        
                    this.tableList.splice(0, this.tableList.length, ...(res.data.results || []))
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
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
            },

            handleAnimationEnd () {},

            showLogDetails () {
                this.isShowLogDetails = true
            }
            
        }
    }
</script>
<style lang="postcss">
    .iam-system-access-wrapper {
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
