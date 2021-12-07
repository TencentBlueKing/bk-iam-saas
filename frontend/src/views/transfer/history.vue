<template>
    <div class="iam-transfer-history-wrapper">
        <bk-table
            :data="tableList"
            size="small"
            class="transfer-history-table"
            :class="{ 'set-border': tableLoading }"
            :pagination="pagination"
            @page-change="handlePageChange"
            @page-limit-change="handleLimitChange"
            v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
            <bk-table-column :label="$t(`m.permTransfer['交接时间']`)">
                <template slot-scope="{ row }">
                    <span :title="row.updated_time">{{ row.updated_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.permTransfer['目标交接人']`)">
                <template slot-scope="{ row }">
                    <span class="grading-admin-name" :title="row.name">{{ row.name }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.permTransfer['交接状态']`)">
                <template slot-scope="{ row }">
                    <span :title="row.description !== '' ? row.description : ''">{{ row.description || '--' }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)" width="150">
                <!-- eslint-disable-next-line vue/no-unused-vars -->
                <template slot-scope="{ row }">
                    <bk-button theme="primary" text>{{ $t(`m.common['详情']`) }}</bk-button>
                </template>
            </bk-table-column>
        </bk-table>
    </div>
</template>
<script>
    import { buildURLParams } from '@/common/url'

    export default {
        name: '',
        components: {
        },
        data () {
            return {
                isFilter: false,
                tableList: [],
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                currentBackup: 1,
                tableLoading: false
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
                await this.fetchTransferHistory()
            },

            refreshCurrentQuery () {
                const { limit, current } = this.pagination
                const queryParams = {
                    limit,
                    current
                }
                window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`)
                return queryParams
            },

            setCurrentQueryCache (payload) {
                window.localStorage.setItem('permTransferList', JSON.stringify(payload))
            },

            getCurrentQueryCache () {
                return JSON.parse(window.localStorage.getItem('permTransferList'))
            },

            async fetchTransferHistory (isTableLoading = false) {
                this.tableLoading = isTableLoading
                this.setCurrentQueryCache(this.refreshCurrentQuery())
                try {
                    // const res = await this.$store.dispatch('role/getRatingManagerList', {
                    const res = await this.$store.dispatch('perm/getTransferHistory', {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit
                    })
                    this.pagination.count = res.data.count
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

            resetPagination () {
                this.pagination = Object.assign({}, {
                    current: 1,
                    count: 0,
                    limit: 10
                })
            },

            handlePageChange (page) {
                if (this.currentBackup === page) {
                    return
                }
                this.pagination.current = page
                this.fetchTransferHistory(true)
            },

            handleLimitChange (currentLimit, prevLimit) {
                this.pagination.limit = currentLimit
                this.pagination.current = 1
                this.fetchTransferHistory(true)
            }
        }
    }
</script>
<style lang="postcss">
    @import './history.css';
</style>
