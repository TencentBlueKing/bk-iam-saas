<template>
    <!-- eslint-disable max-len -->
    <div class="iam-system-access-wrapper">
        <render-search>
            <bk-form
                :model="formData"
                form-type="inline">
                <iam-form-item :label="$t(`m.common['系统']`)" class="pb10">
                    <bk-cascade
                        v-model="systemId"
                        :list="systemList"
                        :is-remote="false"
                        check-any-level
                        :remote-method="remoteMethod"
                        style="width: 200px;"
                        class="iam-custom-process-cascade-cls"
                        @change="handleCascadeChange">
                    </bk-cascade>
                </iam-form-item>
                <iam-form-item :label="$t(`m.common['操作']`)" class="pb10">
                    <bk-select
                        style="width: 200px"
                        v-model="actionId"
                        :clearable="true"
                        @selected="handleSelected">
                        <bk-option v-for="option in processesList"
                            :key="option.id"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                </iam-form-item>
                <iam-form-item v-if="!resourceTypeData.isEmpty" :label="$t(`m.common['资源实例']`)" class="pb10">
                    <!-- <iam-cascade
                        :disabled="!resourceActionId || !actionId || !resourceList.length"
                        v-bk-tooltips.right="(!resourceActionId || !actionId || !resourceList.length) ? '无资源实例' : ''"
                        style="width: 200px;"
                        v-model="resourceId"
                        :list="resourceList"
                        :is-remote="hasMore"
                        :remote-method="resourceRemoteMethod"
                        clearable
                        :dropdown-content-cls="'system-access-cascade-dropdown-content'"
                        @change="handleResourceCascadeChange">
                        <div slot="extension" class="resource-cascade-extension"
                            v-bkloading="{ isLoading: instanceLoading, opacity: 1, size: 'small', theme: 'default' }"
                            style="cursor: pointer;" @click="fetchMoreInstance">
                            加载更多
                        </div>
                    </iam-cascade> -->

                    <div class="resource-container">
                        <div class="relation-content-item" v-for="(content, contentIndex) in
                            resourceTypeData.related_resource_types" :key="contentIndex">
                            <!-- <div class="content-name">
                            {{ content.name }}
                        </div> -->
                            <div class="content">
                                <render-condition
                                    :ref="`condition_${$index}_${contentIndex}_ref`"
                                    :value="content.value"
                                    :is-empty="content.empty"
                                    :params="curCopyParams"
                                    :is-error="content.isLimitExceeded || content.isError"
                                    @on-click="showResourceInstance(resourceTypeData, content, contentIndex)" />
                            </div>
                            <p v-if="content.isLimitExceeded" class="is-limit-error">{{ $t(`m.info['实例数量限制提示']`) }}</p>
                        </div>
                    </div>

                </iam-form-item>
                <iam-form-item :label="$t(`m.resourcePermiss['权限类型']`)" class="pb10">
                    <bk-select
                        style="width: 200px"
                        v-model="permissionType"
                        :clearable="true">
                        <bk-option v-for="option in typeList"
                            :key="option.value"
                            :id="option.value"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                </iam-form-item>
                <iam-form-item :label="$t(`m.resourcePermiss['结果数展示']`)" class="pb10">
                    <bk-select
                        style="width: 200px"
                        v-model="limit"
                        :clearable="true">
                        <bk-option v-for="option in limitList"
                            :key="option"
                            :id="option"
                            :name="option">
                        </bk-option>
                    </bk-select>
                </iam-form-item>
                <bk-button class="ml10 mb10" theme="default" @click="handleReset">{{ $t(`m.common['重置']`) }}</bk-button>
                <bk-button class="mr10 ml10 mb10" theme="primary" @click="handleSearchAndExport(false)">
                    {{ $t(`m.common['查询']`) }}</bk-button>
                <bk-button class="mb10" theme="default" @click="handleSearchAndExport(true)">
                    {{ $t(`m.common['导出']`) }}</bk-button>
            </bk-form>
        </render-search>
        <bk-table
            :data="tableList"
            size="small"
            :class="{ 'set-border': tableLoading }"
            ext-cls="system-access-table"
            v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
            <bk-table-column :label="$t(`m.resourcePermiss['有权限的成员']`)">
                <template slot-scope="{ row }">
                    {{row.user || 'admin'}}
                </template>
            </bk-table-column>
        </bk-table>

        <bk-sideslider
            :is-show="isShowResourceInstanceSideslider"
            :title="resourceInstanceSidesliderTitle"
            :width="720"
            quick-close
            transfer
            :ext-cls="'relate-instance-sideslider'"
            @update:isShow="handleResourceCancel">
            <div slot="content" class="sideslider-content">
                <render-resource
                    ref="renderResourceRef"
                    :data="condition"
                    :original-data="originalCondition"
                    :flag="curFlag"
                    :selection-mode="curSelectionMode"
                    :params="params"
                    @on-limit-change="handleLimitChange"
                />
            </div>
            <div slot="footer" style="margin-left: 25px;">
                <bk-button theme="primary" :loading="sliderLoading" :disabled="disabled" @click="handleResourceSumit">{{ $t(`m.common['保存']`) }}</bk-button>
                <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourcePreview" v-if="isShowPreview">{{ $t(`m.common['预览']`) }}</bk-button>
                <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourceCancel">{{ $t(`m.common['取消']`) }}</bk-button>
            </div>
        </bk-sideslider>
    </div>
</template>
<script>
    import { buildURLParams } from '@/common/url'
    import Policy from '@/model/policy'
    import _ from 'lodash'
    import RenderCondition from './components/render-condition.vue'
    import RenderResource from './components/render-resource.vue'
    import { leaveConfirm } from '@/common/leave-confirm'
    // import iamCascade from '@/components/cascade'

    // 单次申请的最大实例数
    // const RESOURCE_MAX_LEN = 20
    export default {
        name: 'resource-permiss',
        components: {
            RenderCondition,
            RenderResource
            // iamCascade
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
                instancePagination: { current: 0, offset: 0, limit: 100 },
                instanceLoading: false,
                systemList: [],
                resourceList: [],
                resourceId: [],
                systemId: [],
                actionId: '',
                processesList: [],
                typeList: [{ name: '自定义权限', value: 'custom' }, { name: '模板权限', value: 'template' }],
                permissionType: '',
                groupValue: '1-1',
                limit: '',
                limitList: [10, 20, 50, 100, 200, 500],
                resourceActionId: 0,
                resourceActionSystemId: '',
                resourceSystemId: '',
                resourceActionData: [],
                hasMore: false,
                resourceType: '',
                parentId: '',
                resourceInstance: {},
                resourceListChilder: [],
                resourceTypeData: { isEmpty: true },
                isShowResourceInstanceSideslider: false,
                curResIndex: -1,
                params: {}
            }
        },
        computed: {
            condition () {
                if (this.curResIndex === -1) {
                    return []
                }
                const curData = this.resourceTypeData.related_resource_types[this.curResIndex]
                if (!curData) {
                    return []
                }
                if (curData.condition.length === 0) curData.condition = ['none']
                return _.cloneDeep(curData.condition)
            },
            curSelectionMode () {
                if (this.curResIndex === -1) {
                    return 'all'
                }
                console.log('this.curResIndex', this.curResIndex)
                console.log('this.resourceTypeData.related_resource_types[this.curResIndex]', this.resourceTypeData.related_resource_types[this.curResIndex])
                const curData = this.resourceTypeData.related_resource_types[this.curResIndex]
                return curData.selectionMode
            },
            originalCondition () {
                // if (this.curResIndex === -1) {
                //     return []
                // }
                // const curId = this.tableList[this.curIndex].id
                // const curType = this.tableList[this.curIndex].related_resource_types[this.curResIndex].type
                // if (!this.originalList.some(item => item.id === curId)) {
                //     return []
                // }
                // const curResTypeData = this.originalList.find(item => item.id === curId)
                // if (!curResTypeData.related_resource_types.some(item => item.type === curType)) {
                //     return []
                // }
                // const curData = curResTypeData.related_resource_types.find(item => item.type === curType)
                // if (!curData) {
                //     return []
                // }
                return _.cloneDeep(this.condition)
            }
        },
        created () {
            this.handleSearchAndExport(false)
            this.fetchSystemList()
        },
        methods: {
            async fetchSystemList () {
                try {
                    const res = await this.$store.dispatch('system/getSystems')
                    this.systemList = res.data
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

            async handleCascadeChange () {
                this.resourceActionData = []
                this.processesList = []
                this.pagination = Object.assign({}, {
                    current: 1,
                    count: 1,
                    limit: 10000
                })
                if (!this.systemId[0]) return
                this.actionId = ''
                this.resourceId = []
                this.instancePagination = { current: 0, offset: 0, limit: 100 }
                // this.fetchActionProcessesList()
                const systemId = this.systemId[0]
                try {
                    const res = await this.$store.dispatch('approvalProcess/getActionGroups', { system_id: systemId })
                    // item.children = res.data || []
                    console.log('res', res)
                    this.recursionFunc(res.data)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },
            handleSelected () {
                this.resourceTypeData = this.processesList.find(e => e.id === this.actionId)
                console.log('resourceTypeData', this.resourceTypeData)
            },

            async handleSearchAndExport (isExport = false) {
                this.tableLoading = true
                const params = {
                    system_id: this.systemId[0] || '',
                    action_id: this.actionId,
                    resource_instance: this.resourceInstance || {},
                    permission_type: this.permissionType,
                    limit: this.limit
                }
                console.log('params', params)
                try {
                    const fetchUrl = isExport ? 'resourcePermiss/exportResourceManager' : 'resourcePermiss/getResourceManager'
                    const res = await this.$store.dispatch(fetchUrl, params)
                    console.log('res', res)
                    if (!isExport) {
                        this.tableList = res.data
                    }
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

            handleReset () {
                this.instancePagination = { current: 0, offset: 0, limit: 100 }
                this.resourceId = []
                this.systemId = []
                this.actionId = ''
                this.resourceInstance = {}
                this.permissionType = ''
                this.limit = ''
            },

            handleResourceCascadeChange () {
                console.log('this.resourceId', this.resourceId)
                // if(this.resourceId)
                const resourceList = this.resourceId.length > 1 ? [...this.resourceListChilder] : [...this.resourceList]
                console.log('resourceList', resourceList)
                const resourceId = this.resourceId[this.resourceId.length - 1]
                console.log('resourceId', resourceId)
                const resourceData = resourceList.find(e => e.id === resourceId)
                console.log('resourceData', resourceData)
                this.resourceInstance = {
                    id: resourceData.id,
                    name: resourceData.name,
                    type: this.resourceType
                }
            },

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
                    const resourceListChilder = res.data && res.data.results.map(item => {
                        item.name = item.display_name
                        return item
                    })
                    item.children = _.cloneDeep(resourceListChilder)
                    if (item.children.length) this.resourceListChilder = _.cloneDeep(item.children)
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
                        resource_type_system: this.resourceActionSystemId,
                        resource_type_id: this.resourceActionId
                    }
                    const res = await this.$store.dispatch('permApply/getInstanceSelection', params)
                    this.resourceType = res.data && res.data.length && res.data[0].resource_type_chain[0].id
                    this.resourceSystemId = res.data && res.data.length && res.data[0].resource_type_chain[0].system_id
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
                    limit: this.instancePagination.limit,
                    offset: this.instancePagination.offset,
                    system_id: this.resourceSystemId,
                    type: this.resourceType,
                    parent_type: '',
                    parent_id: '',
                    keyword: ''
                }
                try {
                    const res = await this.$store.dispatch('permApply/getResources', params)
                    // this.resourceList = res.data && res.data.results
                    if (res.data && res.data.results.length) {
                        this.resourceList.push(...res.data.results)
                    }
                    this.resourceList = this.resourceList.map(item => {
                        item.name = item.display_name
                        return item
                    })
                } catch (error) {
                    
                } finally {
                    // this.requestQueue.shift()
                    this.instanceLoading = false
                }
            },

            // 加载更多资源实例
            fetchMoreInstance () {
                this.instanceLoading = true
                this.instancePagination.current = ++this.instancePagination.current
                this.instancePagination.offset = this.instancePagination.limit * (this.instancePagination.current)
                this.firstFetchResources()
            },

            // 求值
            recursionFunc (list) {
                console.log('data', list)
                list.forEach(data => {
                    if (data.actions && data.actions.length) {
                        data.actions.forEach(e => {
                            this.resourceActionData.push(e)
                        })
                    }
                    if (data.sub_groups && data.sub_groups.length) {
                        data.sub_groups.forEach(item => {
                            if (item.actions && item.actions.length) {
                                item.actions.forEach(e => {
                                    this.resourceActionData.push(e)
                                })
                            }
                        })
                    }
                })
                this.resourceActionData = this.resourceActionData.filter((e, index, self) => self.indexOf(e) === index)
                this.resourceActionData.forEach(item => {
                    this.processesList.push(new Policy({ ...item, tag: 'add' }, 'custom'))
                })
                console.log('this.resourceActionData', this.resourceActionData)
                console.log('this.processesList', this.processesList)
            },

            showResourceInstance (data, resItem, resIndex) {
                this.params = {
                    system_id: this.systemId[0],
                    action_id: data.id,
                    resource_type_system: resItem.system_id,
                    resource_type_id: resItem.type
                }

                this.curResIndex = resIndex
                this.resourceInstanceSidesliderTitle = `${this.$t(`m.common['关联操作']`)}【${data.name}】${this.$t(`m.common['的资源实例']`)}`
                window.changeAlert = 'iamSidesider'
                console.log(this.params)
                this.isShowResourceInstanceSideslider = true
            },

            handleResourceCancel () {
                let cancelHandler = Promise.resolve()
                if (window.changeAlert) {
                    cancelHandler = leaveConfirm()
                }
                cancelHandler.then(() => {
                    this.isShowResourceInstanceSideslider = false
                    this.resetDataAfterClose()
                }, _ => _)
            },

            async handleResourceSumit () {
                const conditionData = this.$refs.renderResourceRef.handleGetValue()
                console.log('conditionData', conditionData)
                debugger
                const { isEmpty, data } = conditionData
                if (isEmpty) {
                    return
                }

                const resItem = this.resourceTypeData.related_resource_types[this.curResIndex]
                const isConditionEmpty = data.length === 1 && data[0] === 'none'
                if (isConditionEmpty) {
                    resItem.condition = ['none']
                    resItem.isLimitExceeded = false
                    this.resource_instances = {}
                } else {
                    // const { isMainAction, related_actions } = this.tableList[this.curIndex]
                    // // 如果为主操作
                    // if (isMainAction) {
                    //     await this.handleMainActionSubmit(data, related_actions)
                    // }
                    // resItem.condition = data
                    // resItem.isError = false
                }

                window.changeAlert = false
                this.resourceInstanceSidesliderTitle = ''
                this.isShowResourceInstanceSideslider = false
                this.curResIndex = -1

                // if (!isConditionEmpty && resItem.isLimitExceeded) {
                //     let newResourceCount = 0
                //     const conditionList = resItem.condition
                //     conditionList.forEach(item => {
                //         item.instance.forEach(instanceItem => {
                //             instanceItem.paths.forEach(v => {
                //                 // 是否带有下一层级的无限制
                //                 const isHasNoLimit = v.some(({ id }) => id === '*')
                //                 const isDisabled = v.some(_ => !!_.disabled)
                //                 // 可编辑的才会计数
                //                 if (!isHasNoLimit && !isDisabled) {
                //                     ++newResourceCount
                //                 }
                //             })
                //         })
                //     })
                //     console.warn('newResourceCount: ' + newResourceCount)
                //     if (newResourceCount <= RESOURCE_MAX_LEN) {
                //         resItem.isLimitExceeded = false
                //     }
                // }

                // this.curIndex = -1
                // this.curResIndex = -1

                // // 主操作的实例映射到了具体的依赖操作上，需更新到父级的缓存数据中
                // if (this.needEmitFlag) {
                //     this.$emit('on-realted-change', this.tableList)
                // }
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
    .resource-container {
        display: flex;
        justify-content: space-between;
        .relation-content-item{
            width: 200px;
            /* margin-right: 20px; */
        }
    }
</style>
