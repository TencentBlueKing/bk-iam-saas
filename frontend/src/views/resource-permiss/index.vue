<template>
    <div class="iam-system-access-wrapper">
        <render-search>
            <bk-form
                :model="formData"
                form-type="inline">
                <iam-form-item :label="$t(`m.common['系统']`)">
                    <bk-cascade
                        v-model="searchValue"
                        :list="systemList"
                        is-remote
                        check-any-level
                        :remote-method="remoteMethod"
                        style="width: 200px;"
                        class="iam-custom-process-cascade-cls"
                        @change="handleCascadeChange">
                    </bk-cascade>
                </iam-form-item>
                <iam-form-item :label="$t(`m.common['操作']`)">
                    <bk-select
                        style="width: 200px"
                        :value="processes"
                        :clearable="true"
                        @selected="handleSelected">
                        <bk-option v-for="option in processesList"
                            :key="option.action_id"
                            :id="option.action_id"
                            :name="option.action_name">
                        </bk-option>
                    </bk-select>
                </iam-form-item>
                <iam-form-item :label="$t(`m.resourcePermiss['权限类型']`)">
                    <bk-select
                        style="width: 200px"
                        :value="type"
                        :clearable="true"
                        @selected="handleSelected">
                        <bk-option v-for="option in typeList"
                            :key="option.value"
                            :id="option.value"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                </iam-form-item>
                <iam-form-item :label="$t(`m.resourcePermiss['结果数展示']`)">
                    <bk-select
                        style="width: 200px"
                        :value="type"
                        :clearable="true"
                        @selected="handleSelected">
                        <bk-option v-for="option in typeList"
                            :key="option.action_id"
                            :id="option.action_id"
                            :name="option.action_name">
                        </bk-option>
                    </bk-select>
                </iam-form-item>
                <bk-button class="mr10 ml10" theme="primary" @click="handleSearch">
                    {{ $t(`m.common['查询']`) }}</bk-button>
                <bk-button theme="default" @click="handleExport">{{ $t(`m.common['导出']`) }}</bk-button>
            </bk-form>
        </render-search>
        <bk-table
            :data="tableList"
            size="small"
            :class="{ 'set-border': tableLoading }"
            ext-cls="system-access-table"
            :pagination="pagination"
            v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
            <bk-table-column :label="$t(`m.resourcePermiss['有权限的成员']`)">
                <template slot-scope="{ row }">
                    {{row.user || 'admin'}}
                </template>
            </bk-table-column>

        </bk-table>
    </div>
</template>
<script>
    import { buildURLParams } from '@/common/url'
    import _ from 'lodash'
    export default {
        name: 'resource-permiss',
        components: {
        },
        data () {
            return {
                tableList: [],
                tableLoading: false,
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10000
                },
                currentBackup: 1,
                logDetailLoading: false,
                exceptionMsg: '',
                cacheSystemId: '',
                systemList: [],
                searchValue: '',
                processesList: [],
                processes: '',
                typeList: [{ name: '自定义权限', value: 'grant_action' }, { name: '模板权限', value: 'join_group' }]
            }
        },
        watch: {
            'pagination.current' (value) {
                this.currentBackup = value
            }
        },
        created () {
            this.isFilter = false
            this.cacheSystemId = ''
            const currentQueryCache = this.getCurrentQueryCache()
            if (currentQueryCache && Object.keys(currentQueryCache).length) {
                if (currentQueryCache.limit) {
                    this.pagination.limit = currentQueryCache.limit
                    this.pagination.current = currentQueryCache.current
                }
                this.cacheSystemId = currentQueryCache.system_id
            }
            this.fetchSystemList()
        },
        methods: {
            async fetchSystemList () {
                try {
                    const res = await this.$store.dispatch('system/getSystems')
                    this.systemList = res.data
                    setTimeout(() => {
                        if (this.cacheSystemId) {
                            this.searchValue = [this.cacheSystemId]
                        } else {
                            this.searchValue = [this.systemList[0].id]
                        }
                        this.fetchActionProcessesList()
                    })
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
                    // this.requestQueue.shift()
                }
            },

            async fetchActionProcessesList () {
                this.setCurrentQueryCache(this.refreshCurrentQuery())
                const systemId = this.searchValue[0]
                let actionGroupId = ''
                if (this.searchValue.length > 1) {
                    actionGroupId = this.searchValue[this.searchValue.length - 1]
                }
                const params = {
                    limit: this.pagination.limit,
                    offset: this.pagination.limit * (this.pagination.current - 1),
                    system_id: systemId,
                    action_group_id: actionGroupId
                }
                console.log('params', params)
                try {
                    const res = await this.$store.dispatch('approvalProcess/getActionProcessesList', params)
                    this.$nextTick(() => {
                        this.processesList = res.data.results
                        console.log('this.processesList', this.processesList)
                    })
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
                    // this.requestQueue.shift()
                }
            },

            async remoteMethod (item, resolve) {
                const flag = this.systemList.some(v => v.id === item.id)
                if (item.isLoading === false || !flag) {
                    if (!flag && item.sub_groups && item.sub_groups.length > 0) {
                        item.children = _.cloneDeep(item.sub_groups)
                        resolve(item)
                    } else {
                        resolve(item)
                    }
                } else {
                    this.$set(item, 'isLoading', true)
                    try {
                        const res = await this.$store.dispatch('approvalProcess/getActionGroups', { system_id: item.id })
                        item.children = res.data || []
                        resolve(item)
                    } catch (e) {
                        console.error(e)
                        this.bkMessageInstance = this.$bkMessage({
                            limit: 1,
                            theme: 'error',
                            message: e.message || e.data.msg || e.statusText
                        })
                    }
                }
            },

            resetPagination () {
                this.pagination = Object.assign({}, {
                    limit: 10000,
                    current: 1,
                    count: 0
                })
            },

            refreshCurrentQuery () {
                const { limit, current } = this.pagination
                const queryParams = {
                    limit,
                    current,
                    system_id: this.searchValue[0]
                }
                console.log('queryParams', queryParams)
                window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`)
                return queryParams
            },

            setCurrentQueryCache (payload) {
                window.localStorage.setItem('resourcePermissParams', JSON.stringify(payload))
            },

            getCurrentQueryCache () {
                return JSON.parse(window.localStorage.getItem('resourcePermissParams'))
            },

            handleCascadeChange () {
                this.pagination = Object.assign({}, {
                    current: 1,
                    count: 1,
                    limit: 10000
                })
                if (!this.searchValue[0]) return
                this.processes = ''
                this.fetchActionProcessesList()
            },
            handleSelected () {},

            handleSearch () {},

            handleExport () {}
            
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
        .link-btn{
            margin: 10px 0 10px 600px;
        }
        .msg-content{
            background: #555555;
            color: #fff;
            margin: 0 0px 0 30px;
            padding: 10px;
            max-height: 1200px;
            overflow-y: scroll;
        }
    }
</style>
