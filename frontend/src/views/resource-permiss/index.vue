<template>
    <div class="iam-system-access-wrapper">
        <render-search>
            <bk-form
                :model="formData"
                form-type="inline">
                <iam-form-item :label="$t(`m.common['系统']`)">
                    <bk-cascade
                        v-model="systemId"
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
                        v-model="actionId"
                        :clearable="true"
                        @selected="handleSelected">
                        <bk-option v-for="option in processesList"
                            :key="option.action_id"
                            :id="option.action_id"
                            :name="option.action_name">
                        </bk-option>
                    </bk-select>
                </iam-form-item>
                <iam-form-item :label="$t(`m.common['资源实例']`)">
                    <iam-cascade
                        :disabled="!resourceActionId || !actionId"
                        style="width: 200px;"
                        v-model="resourceId"
                        :list="resourceList"
                        :is-remote="hasMore"
                        :remote-method="resourceRemoteMethod"
                        clearable
                        :dropdown-content-cls="'system-access-cascade-dropdown-content'"
                        @change="handleResourceCascadeChange">
                        <!-- <div slot="extension" class="system-access-cascade-extension"
                            style="cursor: pointer;">
                            <i class="bk-icon icon-plus-circle"></i>
                            1111
                        </div> -->
                    </iam-cascade>
                </iam-form-item>
                <iam-form-item :label="$t(`m.resourcePermiss['权限类型']`)">
                    <bk-select
                        style="width: 200px"
                        v-model="permissionType"
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
                        v-model="limit"
                        :clearable="true"
                        @selected="handleSelected">
                        <bk-option v-for="option in limitList"
                            :key="option"
                            :id="option"
                            :name="option">
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
    import iamCascade from '@/components/cascade'
    export default {
        name: 'resource-permiss',
        components: {
            iamCascade
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
                resourceList: [],
                resourceId: '',
                systemId: '',
                processesList: [],
                actionId: '',
                typeList: [{ name: '自定义权限', value: 'custom' }, { name: '模板权限', value: 'template' }],
                permissionType: '',
                groupValue: '1-1',
                groupList: [
                    {
                        id: 1,
                        name: '爬山',
                        children: [
                            { id: '1-1', name: '爬山-1' },
                            { id: '1-2', name: '爬山-2' }
                        ]
                    },
                    {
                        id: 2,
                        name: '跑步',
                        children: [
                            { id: '2-1', name: '跑步-1' },
                            { id: '2-2', name: '跑步-2' }
                        ]
                    }
                ],
                limit: 10,
                limitList: [10, 20, 50, 100, 200],
                resourceActionId: 0,
                resourceActionData: [],
                hasMore: false,
                resourceType: '',
                parentId: ''
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
                    console.log('this.systemList', this.systemList)
                    setTimeout(() => {
                        if (this.cacheSystemId) {
                            this.systemId = [this.cacheSystemId]
                        } else {
                            this.systemId = [this.systemList[0].id]
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
                const systemId = this.systemId[0]
                let actionGroupId = ''
                if (this.systemId.length > 1) {
                    actionGroupId = this.systemId[this.systemId.length - 1]
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
                console.log('22222', item)
                this.resourceActionId = ''
                this.resourceActionData = []
                
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
                this.recursionFunc(item)
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
                    system_id: this.systemId[0]
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
                if (!this.systemId[0]) return
                this.actionId = ''
                this.fetchActionProcessesList()
            },
            handleSelected () {
                const resourceAction = this.resourceActionData.find(e => e.id === this.actionId)
                this.resourceActionId = resourceAction && resourceAction.related_resource_types.length
                    && resourceAction.related_resource_types[0].id
                this.fetchInstanceSelection()
            },

            handleSearch () {
                const params = {
                    system_id: this.systemId,
                    action_id: this.actionId,
                    resource_instance: {
                        'id': 'cmdb',
                        'type': 'app',
                        'name': '配置平台'
                    },
                    permission_type: this.permissionType,
                    limit: this.limit
                }
                console.log('params', params)
            },

            handleExport () {},

            handleResourceCascadeChange () {},

            async resourceRemoteMethod (item, resolve) {
                console.log('item', item)
                this.parentId = item.id
                const params = {
                    limit: 100,
                    offset: 0,
                    system_id: this.systemId[0],
                    type: this.resourceActionId,
                    parent_type: this.resourceType,
                    parent_id: this.parentId,
                    keyword: ''
                }
                try {
                    const res = await this.$store.dispatch('permApply/getResources', params)
                    const resourceList = res.data && res.data.results.map(item => {
                        item.name = item.display_name
                        item.child_type = true
                        return item
                    })
                    item.children = _.cloneDeep(resourceList)
                    resolve(item)
                } catch (error) {
                    
                }
            },

            async fetchInstanceSelection () {
                if (!this.resourceActionId) return
                try {
                    const params = {
                        system_id: this.systemId[0],
                        action_id: this.actionId,
                        resource_type_system: this.systemId[0],
                        resource_type_id: this.resourceActionId
                    }
                    const res = await this.$store.dispatch('permApply/getInstanceSelection', params)
                    this.resourceType = res.data && res.data.length && res.data[0].resource_type_chain[0].id
                    this.hasMore = res.data && res.data.length && res.data[0].resource_type_chain.length > 1
                    console.log('this.resourceType', this.resourceType)
                    this.firstFetchResources()
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

            // 资源实例接口
            async firstFetchResources () {
                const params = {
                    limit: 100,
                    offset: 0,
                    system_id: this.systemId[0],
                    type: this.resourceType,
                    parent_type: '',
                    parent_id: '',
                    keyword: ''
                }
                try {
                    const res = await this.$store.dispatch('permApply/getResources', params)
                    this.resourceList = res.data && res.data.results
                    console.log('this.resourceList', this.resourceList)
                    this.resourceList = this.resourceList.map(item => {
                        item.name = item.display_name
                        return item
                    })
                } catch (error) {
                    
                }
            },

            // 求值
            recursionFunc (data) {
                console.log('data', data)
                if (data.actions && data.actions.length) {
                    data.actions.forEach(e => {
                        this.resourceActionData.push(e)
                    })
                }
                if (data.children && data.children.length) {
                    data.children.forEach(item => {
                        if (item.actions && item.actions.length) {
                            item.actions.forEach(e => {
                                this.resourceActionData.push(e)
                            })
                        }

                        if (item.sub_groups && item.sub_groups.length) {
                            item.sub_groups.forEach(e => {
                                e.actions.forEach(ele => {
                                    this.resourceActionData.push(ele)
                                })
                            })
                        }
                    })
                }
                this.resourceActionData = this.resourceActionData.filter((e, index, self) => self.indexOf(e) === index)
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
