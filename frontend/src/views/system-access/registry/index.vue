<template>
    <div class="iam-system-access-registry-wrapper">
        <div class="inner">
            <bk-steps class="system-access-step" ref="systemAccessStep" :steps="steps" direction="vertical"></bk-steps>
            <smart-action class="content-wrapper">
                <template v-if="actionList.length">
                    <div class="registry-action-item" v-for="(item, index) in actionList" :key="index">
                        <div class="header" @click="handleExpanded(item)"
                            :style="{ position: item.isExpand ? 'absolute' : 'relative' }">
                            <Icon bk class="expanded-icon" :type="item.isExpand ? 'down-shape' : 'right-shape'" />
                            <label class="title">{{ item.title || $t(`m.access['注册操作']`) }}</label>
                        </div>
                        <div v-if="item.isExpand" class="btn-wrapper">
                            <template v-if="!item.isEdit">
                                <bk-button size="small" @click="item.isEdit = true">
                                    {{ $t(`m.common['编辑']`) }}
                                </bk-button>
                            </template>
                            <template v-else>
                                <bk-button size="small" :disabled="item.loading" theme="primary"
                                    @click.stop.prevent="saveAction(item, index)">{{ $t(`m.common['保存']`) }}</bk-button>
                                <bk-button size="small" :disabled="item.loading || item.isNewAdd"
                                    @click.stop.prevent="delAction(item, index)">{{ $t(`m.common['删除']`) }}</bk-button>
                                <bk-button size="small" :disabled="item.loading"
                                    @click.stop.prevent="cancelEdit(index)">{{ $t(`m.common['取消']`) }}</bk-button>
                            </template>
                        </div>
                        <div class="content" v-if="item.isExpand">
                            <div class="slot-content">
                                <div style="min-height: 60px;" v-bkloading="{ isLoading: item.loading, opacity: 1 }">
                                    <section :ref="`basicInfoContentRef${index}`">
                                        <basic-info :ref="`basicInfoRef${index}`" :info-data="item"
                                            @on-change="handleBasicInfoChange(...arguments, item, index)" />
                                    </section>
                                    <bk-button theme="primary" text :disabled="!item.isEdit"
                                        :style="{
                                            marginTop: '23px',
                                            marginBottom: item.isExpandAdvanced ? '6px' : '26px'
                                        }"
                                        @click="item.isExpandAdvanced = !item.isExpandAdvanced">
                                        {{ $t(`m.access['高级配置']`) }}
                                        <Icon :type="item.isExpandAdvanced ? 'up-angle' : 'down-angle'"
                                            class="expand-advanced-settings" />
                                    </bk-button>
                                    <template v-if="item.isExpandAdvanced">
                                        <div class="label-info">{{$t(`m.access['依赖资源']`)}}</div>
                                        <bk-table :data="item.related_resource_types" border
                                            :cell-class-name="getCellClass">
                                            <bk-table-column :resizable="false" min-width="250"
                                                :label="$t(`m.access['资源类型']`)">
                                                <template slot-scope="{ row }">
                                                    <iam-cascade
                                                        class="system-access-cascade"
                                                        :disabled="!item.isEdit"
                                                        v-model="row.resourceTypeCascadeValue"
                                                        :list="systemListResourceType"
                                                        :is-remote="true"
                                                        :remote-method="fetchResourceTypeListBySystem"
                                                        clearable
                                                        :dropdown-content-cls="'system-access-cascade-dropdown-content'"
                                                        :placeholder="$t(`m.access['请选择资源类型']`)"
                                                        :empty-text="$t(`m.access['无匹配数据']`)"
                                                        @change="handleResourceTypeChange(row, ...arguments)">
                                                        <div slot="extension" class="system-access-cascade-extension"
                                                            style="cursor: pointer;" @click="showAddResourceType">
                                                            <i class="bk-icon icon-plus-circle"></i>
                                                            {{ $t(`m.access['新增资源类型']`) }}
                                                        </div>
                                                    </iam-cascade>
                                                </template>
                                            </bk-table-column>
                                            <bk-table-column :resizable="false" min-width="450"
                                                :label="$t(`m.access['实例视图']`)" :render-header="renderHeader">
                                                <template slot-scope="{ row }">
                                                    <div class="related-instance-selections-wrapper">
                                                        <bk-checkbox :disabled="!item.isEdit"
                                                            :checked="row.selection_mode === 'instance'"
                                                            :true-value="'attribute'" :false-value="'instance'"
                                                            v-model="row.selection_mode"
                                                            style="margin-right: 20px; margin-top: 7px;">
                                                            {{$t(`m.access['通过拓扑选择']`)}}
                                                        </bk-checkbox>
                                                        <div class="related-instance-selections-cascade-wrapper">
                                                            <!-- eslint-disable max-len -->
                                                            <div style="position: relative;"
                                                                v-for="(isItem, isItemIndex) in row.related_instance_selections"
                                                                :key="isItemIndex">
                                                                <iam-cascade
                                                                    class="related-instance-selections-cascade"
                                                                    :disabled="!item.isEdit"
                                                                    v-model="isItem.instanceSelectionsCascadeValue"
                                                                    :list="systemListInstanceSelections"
                                                                    :is-remote="true"
                                                                    :remote-method="fetchInstanceSelectionsListBySystem"
                                                                    clearable
                                                                    :dropdown-content-cls="'system-access-cascade-dropdown-content'"
                                                                    :placeholder="$t(`m.access['请选择实例视图']`)"
                                                                    :empty-text="$t(`m.access['无匹配数据']`)"
                                                                    @change="handleInstanceSelectionsChange(isItem, ...arguments)">
                                                                    <div slot="extension" class="system-access-cascade-extension"
                                                                        style="cursor: pointer;" @click="showAddInstanceSelection">
                                                                        <i class="bk-icon icon-plus-circle"></i>{{ $t(`m.access['新增实例视图']`) }}
                                                                    </div>
                                                                </iam-cascade>
                                                                <Icon type="add-hollow" class="add-icon" :class="!item.isEdit ? 'disabled' : ''" @click="addRelatedInstanceSelections(item, row)" />
                                                                <Icon type="reduce-hollow" class="reduce-icon" v-if="row.related_instance_selections.length > 1" :class="!item.isEdit ? 'disabled' : ''" @click="delRelatedInstanceSelections(item, row, isItemIndex)" />
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <bk-checkbox :disabled="!item.isEdit" :checked="row.selection_mode === 'attribute'" :true-value="'attribute'" :false-value="'instance'" v-model="row.selection_mode">
                                                            {{$t(`m.access['通过属性选择']`)}}
                                                        </bk-checkbox>
                                                    </div>
                                                </template>
                                            </bk-table-column>
                                        </bk-table>

                                        <section class="add-related-resource-wrapper">
                                            <bk-button theme="primary" text :disabled="!item.isEdit" @click="addRelatedResource(item)">
                                                <Icon type="add-small" />
                                                {{ $t(`m.access['新增依赖资源']`) }}
                                            </bk-button>
                                        </section>

                                        <div class="label-info">{{$t(`m.access['依赖操作']`)}}</div>
                                        <bk-select style="margin-top: 10px;margin-bottom: 30px;"
                                            :disabled="!item.isEdit"
                                            searchable
                                            multiple
                                            display-tag
                                            v-model="item.related_actions">
                                            <bk-option v-for="option in relatedActionList"
                                                :key="option.id"
                                                :id="option.id"
                                                :name="option.name">
                                            </bk-option>
                                        </bk-select>
                                    </template>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>

                <render-action :title="$t(`m.access['新增操作']`)" style="margin-bottom: 20px;" @on-click="addAction"></render-action>

                <div slot="action">
                    <bk-button theme="primary" type="button" :loading="submitLoading" @click="handleSubmit">
                        {{ $t(`m.common['下一步']`) }}
                    </bk-button>
                    <bk-button style="margin-left: 10px;" @click="handlePrev">{{ $t(`m.common['上一步']`) }}</bk-button>
                </div>
            </smart-action>
        </div>
        <resource-type-sideslider
            :is-show.sync="isShowAddResourceTypeSideslider"
            @on-refresh-system-list="fetchSystemList"
            @on-cancel="hideAddResourceType" />

        <instance-selection-sideslider
            :is-show.sync="isShowAddInstanceSelectionSideslider"
            @on-refresh-system-list="fetchSystemList"
            @on-cancel="hideAddResourceType" />
    </div>
</template>
<script>
    import { mapGetters } from 'vuex'

    import { leavePageConfirm } from '@/common/leave-page-confirm'
    import iamCascade from '@/components/cascade'
    import RenderAction from '../common/render-action'
    import BasicInfo from './basic-info'

    import ResourceTypeSideslider from './resource-type-sideslider'
    import InstanceSelectionSideslider from './instance-selection-sideslider'

    const getDefaultActionData = () => ({
        id: '',
        type: '',
        name: '',
        name_en: '',
        description: '',
        description_en: '',
        related_resource_types: [
            {
                resourceTypeCascadeValue: [],
                id: '',
                system_id: '',
                selection_mode: '',
                related_instance_selections: [
                    {
                        instanceSelectionsCascadeValue: [],
                        id: '',
                        system_id: ''
                    }
                ]
            }
        ],
        related_actions: [],
        isEdit: true,
        isExpand: true,
        isExpandAdvanced: false,
        loading: false,
        // 添加了还未保存的
        isNewAdd: true,
        title: ''
    })

    export default {
        name: '',
        components: {
            BasicInfo,
            RenderAction,
            iamCascade,
            ResourceTypeSideslider,
            InstanceSelectionSideslider
        },
        data () {
            return {
                submitLoading: false,

                steps: [
                    { title: '注册系统', icon: 1 },
                    { title: '注册操作', icon: 2 },
                    { title: '体验优化', icon: 3 },
                    { title: '完成', icon: 4 }
                ],

                isExpandAdvanced: false,
                // modelingSystemData: null,
                actionList: [],
                actionListBackup: [],
                isShowAddResourceTypeSideslider: false,
                isShowAddInstanceSelectionSideslider: false,
                systemListResourceType: [],
                systemListInstanceSelections: [],
                relatedActionList: []
            }
        },
        computed: {
            ...mapGetters(['user']),
            modelingId () {
                return this.$route.params.id
            }
        },
        watch: {
            actionList (v) {
                const relatedActionList = v.filter(item => !item.isNewAdd).map(item => {
                    return {
                        id: item.id, name: item.name
                    }
                })

                this.relatedActionList.splice(0, this.relatedActionList.length, ...relatedActionList)
            }
        },
        mounted () {
            const stepNode = this.$refs.systemAccessStep.$el
            if (stepNode) {
                const children = Array.from(stepNode.querySelectorAll('.bk-step') || [])
                children.forEach(child => {
                    child.classList.remove('current')
                })
                children[1].classList.add('current')
            }
        },
        methods: {
            async fetchPageData () {
                await Promise.all([
                    this.fetchSystemList(),
                    // this.fetchModeling()
                    this.fetchActionList()
                ])
            },

            async fetchSystemList () {
                try {
                    const res = await this.$store.dispatch('access/getSystemList', {
                        id: this.modelingId
                    })
                    const systemList = []
                    const list = res.data || []
                    list.forEach(item => {
                        systemList.push({
                            id: item[0],
                            name: item[1],
                            // TODO: cascade/caspanel.vue 的 handleItemFn 使用。目的是不允许选中第一层节点中没有子层级的节点，暂时先这么实现
                            parent: true
                        })
                    })
                    this.systemListResourceType.splice(0, this.systemListResourceType.length, ...systemList)
                    this.systemListInstanceSelections = JSON.parse(JSON.stringify(systemList))
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            async fetchActionList () {
                try {
                    const resModeling = await this.$store.dispatch('access/getModeling', {
                        id: this.modelingId,
                        data: {
                            type: 'action'
                        }
                    })
                    const actionList = []
                    actionList.splice(0, 0, ...(resModeling.data || []))

                    const preloadResourceTypeListBySys = []
                    const preloadResourceTypeListBySysParams = []

                    const preloadInstanceSelectionsBySys = []
                    const preloadInstanceSelectionsBySysParams = []

                    if (!actionList.length) {
                        actionList.push(getDefaultActionData())
                    } else {
                        actionList.forEach(item => {
                            item.title = item.name
                            item.isEdit = false
                            item.isExpand = false
                            item.loading = false
                            item.isNewAdd = false
                            if (!item.related_resource_types || !item.related_resource_types.length) {
                                item.isExpandAdvanced = false
                                item.related_resource_types = [
                                    {
                                        resourceTypeCascadeValue: [],
                                        id: '',
                                        system_id: '',
                                        selection_mode: '',
                                        related_instance_selections: [
                                            {
                                                instanceSelectionsCascadeValue: [],
                                                id: '',
                                                system_id: ''
                                            }
                                        ]
                                    }
                                ]
                            } else {
                                item.isExpandAdvanced = true
                                item.related_resource_types.forEach(c => {
                                    if (!c.related_instance_selections) {
                                        c.related_instance_selections = [
                                            {
                                                instanceSelectionsCascadeValue: [],
                                                id: '',
                                                system_id: ''
                                            }
                                        ]
                                    } else {
                                        c.related_instance_selections.forEach(is => {
                                            is.instanceSelectionsCascadeValue = [is.system_id, is.id]
                                            preloadInstanceSelectionsBySysParams.push(c.system_id)
                                            preloadInstanceSelectionsBySys.push(this.$store.dispatch('access/getInstanceSelectionsListBySystem', {
                                                id: this.modelingId,
                                                data: {
                                                    system_id: is.system_id
                                                }
                                            }))
                                        })
                                    }

                                    c.resourceTypeCascadeValue = [c.system_id, c.id]

                                    // preloadResourceTypeListBySysParams 和 preloadResourceTypeListBySys 的顺序是一致的
                                    preloadResourceTypeListBySysParams.push(c.system_id)
                                    preloadResourceTypeListBySys.push(this.$store.dispatch('access/getResourceTypeListBySystem', {
                                        id: this.modelingId,
                                        data: {
                                            system_id: c.system_id
                                        }
                                    }))
                                })
                            }
                        })
                        if (preloadResourceTypeListBySys.length) {
                            const resArr = await Promise.all(preloadResourceTypeListBySys)
                            resArr.forEach((res, index) => {
                                const curSysData = this.systemListResourceType.find(
                                    sys => sys.id === preloadResourceTypeListBySysParams[index]
                                )
                                if (curSysData) {
                                    curSysData.children = [];
                                    (res.data || []).forEach(d => {
                                        curSysData.children.push({
                                            ...d,
                                            isLoading: false
                                        })
                                    })
                                }
                            })
                        }
                        if (preloadInstanceSelectionsBySys.length) {
                            const resArr = await Promise.all(preloadInstanceSelectionsBySys)
                            resArr.forEach((res, index) => {
                                const curSysData = this.systemListInstanceSelections.find(
                                    sys => sys.id === preloadInstanceSelectionsBySysParams[index]
                                )
                                const curSysDataIndex = this.systemListInstanceSelections.findIndex(
                                    sys => sys.id === preloadInstanceSelectionsBySysParams[index]
                                )
                                if (curSysData) {
                                    curSysData.children = [];
                                    (res.data || []).forEach(d => {
                                        curSysData.children.push({
                                            ...d,
                                            isLoading: false
                                        })
                                    })
                                    this.$set(this.systemListInstanceSelections, curSysDataIndex, curSysData)
                                }
                            })
                        }
                    }
                    this.actionList.splice(0, this.actionList.length, ...actionList)
                    this.actionListBackup = JSON.parse(JSON.stringify(actionList))
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            // async fetchModeling () {
            //     try {
            //         const res = await this.$store.dispatch('access/getModeling', { id: this.modelingId })
            //         const systemData = (res.data || {}).system
            //         this.modelingSystemData = Object.assign({}, systemData || {})
            //     } catch (e) {
            //         console.error(e)
            //         this.bkMessageInstance = this.$bkMessage({
            //             limit: 1,
            //             theme: 'error',
            //             message: e.message || e.data.msg || e.statusText
            //         })
            //     }
            // },

            renderHeader (h, data) {
                return <span class="related-instance-selections-header-cell">{ data.column.label }</span>
            },

            handleResourceTypeChange (row, newValue, oldValue, selectList) {
                row.system_id = row.resourceTypeCascadeValue[0]
                // 只有一层的情况
                row.id = row.resourceTypeCascadeValue[1] || row.resourceTypeCascadeValue[0]
            },

            handleInstanceSelectionsChange (row, newValue, oldValue, selectList) {
                row.system_id = row.instanceSelectionsCascadeValue[0]
                // 只有一层的情况
                row.id = row.instanceSelectionsCascadeValue[1] || row.instanceSelectionsCascadeValue[0]
            },

            /**
             * 显示添加资源类型侧边栏
             */
            showAddResourceType () {
                this.isShowAddResourceTypeSideslider = true
            },

            /**
             * 隐藏添加资源类型侧边栏
             */
            hideAddResourceType () {
                this.isShowAddResourceTypeSideslider = false
            },

            /**
             * 显示添加实例视图侧边栏
             */
            showAddInstanceSelection () {
                this.isShowAddInstanceSelectionSideslider = true
            },

            /**
             * 隐藏添加实例视图侧边栏
             */
            hideAddInstanceSelection () {
                this.isShowAddInstanceSelectionSideslider = false
            },

            /**
             * 新增操作
             */
            addAction () {
                const actionList = []
                actionList.splice(0, 0, ...this.actionList)
                actionList.push(getDefaultActionData())
                this.actionList.splice(0, this.actionList.length, ...actionList)
                this.actionListBackup = JSON.parse(JSON.stringify(actionList))
            },

            /**
             * getCellClass
             */
            getCellClass ({ row, column, rowIndex, columnIndex }) {
                if (columnIndex === 1) {
                    return 'registry-action-table-cell-cls'
                }
                return ''
            },

            /**
             * delRelatedInstanceSelections
             */
            delRelatedInstanceSelections (curAction, row, index) {
                if (!curAction.isEdit) {
                    return
                }

                const relatedInstanceSelections = []
                relatedInstanceSelections.splice(0, 0, ...row.related_instance_selections)
                relatedInstanceSelections.splice(index, 1)

                row.related_instance_selections = JSON.parse(JSON.stringify(relatedInstanceSelections))
            },

            /**
             * addRelatedInstanceSelections
             */
            addRelatedInstanceSelections (curAction, row) {
                if (!curAction.isEdit) {
                    return
                }
                row.related_instance_selections.push({ instanceSelectionsCascadeValue: [], id: '', system_id: '' })
            },

            /**
             * fetchResourceTypeListBySystem
             */
            async fetchResourceTypeListBySystem (sys, resolve) {
                if (sys.isLoading === false) {
                    resolve(sys)
                    return
                }
                this.$set(sys, 'isLoading', true)
                try {
                    const res = await this.$store.dispatch('access/getResourceTypeListBySystem', {
                        id: this.modelingId,
                        data: {
                            system_id: sys.id
                        }
                    })
                    const list = []
                    res.data.forEach(item => {
                        list.push({
                            ...item,
                            isLoading: false
                        })
                    })
                    sys.children = list
                    resolve(sys)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * fetchInstanceSelectionsListBySystem
             */
            async fetchInstanceSelectionsListBySystem (sys, resolve) {
                if (sys.isLoading === false) {
                    resolve(sys)
                    return
                }
                this.$set(sys, 'isLoading', true)
                try {
                    const res = await this.$store.dispatch('access/getInstanceSelectionsListBySystem', {
                        id: this.modelingId,
                        data: {
                            system_id: sys.id
                        }
                    })
                    const list = []
                    res.data.forEach(item => {
                        list.push({
                            ...item,
                            isLoading: false
                        })
                    })
                    sys.children = list
                    resolve(sys)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * handleExpanded
             */
            handleExpanded (item) {
                item.isExpand = !item.isExpand
            },

            /**
             * handleBasicInfoChange
             */
            handleBasicInfoChange (value, item, index) {
                window.changeDialog = true
                item.id = value.id
                item.name = value.name
                item.name_en = value.name_en
                item.type = value.type
                item.description = value.description
                item.description_en = value.description_en
            },

            /**
             * addRelatedResource
             */
            addRelatedResource (item) {
                const relatedResourceTypes = []
                relatedResourceTypes.splice(0, 0, ...item.related_resource_types)
                relatedResourceTypes.push({
                    resourceTypeCascadeValue: [],
                    id: '',
                    system_id: '',
                    selection_mode: '',
                    related_instance_selections: [
                        {
                            instanceSelectionsCascadeValue: [],
                            id: '',
                            system_id: ''
                        }
                    ],
                    instanceSelectionsCascadeValue: []
                })
                item.related_resource_types.splice(0, item.related_resource_types.length, ...relatedResourceTypes)
            },

            /**
             * saveAction
             */
            async saveAction (item, index) {
                const formComp = this.$refs[`basicInfoRef${index}`]
                if (formComp && formComp[0]) {
                    try {
                        await formComp[0].handleValidator()
                    } catch (e) {
                        this.scrollToLocation(this.$refs[`basicInfoContentRef${index}`][0])
                        return
                    }

                    const relatedResourceTypes = []
                    item.related_resource_types.forEach(t => {
                        if (t.system_id && t.id) {
                            const obj = {
                                system_id: t.system_id,
                                id: t.id,
                                selection_mode: t.selection_mode
                            }
                            if (t.related_instance_selections && t.related_instance_selections.length) {
                                obj.related_instance_selections = []
                                t.related_instance_selections.forEach(is => {
                                    obj.related_instance_selections.push({
                                        system_id: is.system_id,
                                        id: is.id
                                    })
                                })
                            }
                            relatedResourceTypes.push(obj)
                        }
                    })

                    try {
                        item.loading = true
                        await this.$store.dispatch('access/updateModeling', {
                            id: this.modelingId,
                            data: {
                                type: 'action',
                                data: {
                                    id: item.id,
                                    type: item.type,
                                    name: item.name,
                                    name_en: item.name_en,
                                    description: item.description,
                                    description_en: item.description_en,
                                    related_resource_types: relatedResourceTypes,
                                    related_actions: item.related_actions || []
                                }
                            }
                        })
                        item.title = item.name
                        item.isEdit = false
                        item.isNewAdd = false
                        this.messageSuccess(this.$t(`m.access['保存操作成功']`), 1000)
                    } catch (e) {
                        console.error(e)
                        this.bkMessageInstance = this.$bkMessage({
                            limit: 1,
                            theme: 'error',
                            message: e.message || e.data.msg || e.statusText
                        })
                    } finally {
                        item.loading = false
                    }
                }
            },

            /**
             * cancelEdit
             */
            cancelEdit (index) {
                const formComp = this.$refs[`basicInfoRef${index}`]
                if (formComp && formComp[0]) {
                    formComp[0].resetError()
                }
                const curItem = this.actionList[index]
                // 如果是未保存过的，那么取消的时候直接删除
                if (curItem.isNewAdd) {
                    const actionList = []
                    actionList.splice(0, 0, ...this.actionList)
                    actionList.splice(index, 1)
                    this.actionList.splice(0, this.actionList.length, ...actionList)

                    this.actionListBackup = JSON.parse(JSON.stringify(actionList))
                } else {
                    const originalExpanded = curItem.isExpand
                    const originalExpandedAdvanced = curItem.isExpandAdvanced
                    const originalItem = Object.assign({}, this.actionListBackup[index])
                    originalItem.isEdit = false
                    originalItem.isExpand = originalExpanded
                    originalItem.isExpandAdvanced = originalExpandedAdvanced
                    this.$set(this.actionList, index, originalItem)
                }
            },

            /**
             * delAction
             */
            async delAction (item, index) {
                const directive = {
                    name: 'bkTooltips',
                    content: item.name,
                    placement: 'right'
                }
                const me = this
                me.$bkInfo({
                    title: this.$t(`m.access['确认删除下列操作？']`),
                    confirmLoading: true,
                    subHeader: (
                        <div class="add-resource-type-warn-info">
                            <p>
                                <span title={ item.name } v-bk-tooltips={ directive }>{ item.name }</span>
                            </p>
                        </div>
                    ),
                    confirmFn: async () => {
                        try {
                            item.loading = true
                            await me.$store.dispatch('access/deleteModeling', {
                                id: me.modelingId,
                                data: {
                                    id: item.id,
                                    type: 'action'
                                }
                            })

                            const actionList = []
                            actionList.splice(0, 0, ...me.actionList)
                            actionList.splice(index, 1)
                            me.actionList.splice(0, me.actionList.length, ...actionList)

                            me.messageSuccess(me.$t(`m.access['删除操作成功']`), 1000)
                            return true
                        } catch (e) {
                            console.error(e)
                            me.bkMessageInstance = me.$bkMessage({
                                limit: 1,
                                theme: 'error',
                                message: e.message || e.data.msg || e.statusText
                            })
                            return false
                        } finally {
                            item.loading = false
                            me.actionListBackup = JSON.parse(JSON.stringify(me.actionList))
                        }
                    }
                })
            },

            /**
             * handleSubmit
             */
            async handleSubmit () {
                if (!this.actionList.length) {
                    this.messageError(this.$t(`m.access['至少要注册一个操作']`), 1000)
                    return
                }

                const invalidItemList = this.actionList.filter(item => item.isEdit)
                if (invalidItemList.length) {
                    this.$bkInfo({
                        title: this.$t(`m.access['请先保存所有操作']`),
                        subHeader: (
                            <div class="add-resource-type-warn-info">
                                {
                                    invalidItemList.map(invalidItem => {
                                        const directive = {
                                            name: 'bkTooltips',
                                            content: invalidItem.name,
                                            placement: 'right'
                                        }
                                        return (
                                            <p>
                                                <span title={ invalidItem.name } v-bk-tooltips={ directive }>
                                                    { invalidItem.name }
                                                </span>
                                            </p>
                                        )
                                    })
                                }
                            </div>
                        )
                    })
                    return
                }

                console.log('actionList', this.actionList)
                console.log('actionListBackup', this.actionListBackup)

                this.$router.push({
                    // name: 'systemAccessComplete',
                    name: 'systemAccessOptimize',
                    params: {
                        id: this.modelingId
                    }
                })
            },

            /**
             * handlePrev
             */
            handlePrev () {
                let cancelHandler = Promise.resolve()
                if (window.changeDialog) {
                    cancelHandler = leavePageConfirm()
                }
                cancelHandler.then(() => {
                    this.$router.push({
                        name: 'systemAccessAccess',
                        params: this.$route.params
                    })
                }, _ => _)
            }
        }
    }
</script>
<style lang="postcss" scoped>
    @import './index.css';
</style>
