<template>
    <div class="iam-grade-split-wrapper">
        <bk-table
            :data="tableList"
            :border="false"
            :header-border="false"
            :cell-class-name="getCellClass"
            :empty-text="$t(`m.verify['请选择操作']`)"
            @row-mouse-enter="handlerRowMouseEnter"
            @row-mouse-leave="handlerRowMouseLeave">
            <bk-table-column :resizable="false" :label="$t(`m.common['操作']`)" width="280">
                <template slot-scope="{ row }">
                    <div :class="!!row.isAggregate ? 'set-padding' : ''">
                        <span class="action-name" :title="row.name">{{ row.name }}</span>
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column
                :resizable="false"
                :label="$t(`m.common['所属系统']`)"
                :filters="systemFilter"
                :filter-method="systemFilterMethod"
                :filter-multiple="false"
                prop="system_id"
                width="240">
                <template slot-scope="{ row }">
                    <span :title="row.system_name">{{ row.system_name }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :resizable="false" :label="$t(`m.grading['资源实例范围']`)" min-width="240">
                <template slot-scope="{ row, $index }">
                    <div class="relation-content-wrapper" v-if="!!row.isAggregate">
                        <label class="resource-type-name">{{ row.aggregateResourceType.name }}</label>
                        <render-condition
                            :ref="`condition_${$index}_aggregateRef`"
                            :value="row.value"
                            :is-empty="row.empty"
                            :can-view="false"
                            :can-paste="row.canPaste"
                            :is-error="row.isError"
                            @on-mouseover="handlerAggregateConditionMouseover(row)"
                            @on-mouseleave="handlerAggregateConditionMouseleave(row)"
                            @on-copy="handlerAggregateOnCopy(row, $index)"
                            @on-paste="handlerAggregateOnPaste(row)"
                            @on-batch-paste="handlerAggregateOnBatchPaste(row, $index)"
                            @on-click="showAggregateResourceInstance(row, $index)" />
                    </div>
                    <div class="relation-content-wrapper" v-else>
                        <template v-if="!row.isEmpty">
                            <div v-for="(_, groIndex) in row.resource_groups" :key="_.id">
                                <div class="relation-content-item"
                                    v-for="(content, contentIndex) in _.related_resource_types" :key="contentIndex">
                                    <div class="content-name">
                                        {{ content.name }}
                                        <template v-if="row.isShowRelatedText">
                                            <div style="display: inline-block; color: #979ba5;">
                                                ({{ $t(`m.info['已帮您自动勾选依赖操作需要的实例']`) }})
                                            </div>
                                        </template>
                                    </div>
                                    <div class="content">
                                        <!-- eslint-disable max-len -->
                                        <render-condition
                                            :ref="`condition_${$index}_${contentIndex}_ref`"
                                            :value="content.value"
                                            :is-empty="content.empty"
                                            :can-view="row.canView"
                                            :params="curCopyParams"
                                            :can-paste="content.canPaste"
                                            :is-error="content.isError"
                                            @on-mouseover="handlerConditionMouseover(content)"
                                            @on-mouseleave="handlerConditionMouseleave(content)"
                                            @on-view="handlerOnView(row, content, contentIndex, groIndex)"
                                            @on-copy="handlerOnCopy(content, $index, contentIndex, row)"
                                            @on-paste="handlerOnPaste(...arguments, content)"
                                            @on-batch-paste="handlerOnBatchPaste(...arguments, content, $index, contentIndex)"
                                            @on-click="showResourceInstance(row, content, contentIndex, groIndex)" />
                                    </div>
                                </div>
                            </div>
                        </template>
                        <template v-else>
                            {{ $t(`m.common['无需关联实例']`) }}
                        </template>
                    </div>
                    <div class="remove-icon" @click.stop="handlerRemove(row, $index)">
                        <Icon type="close-small" />
                    </div>
                </template>
            </bk-table-column>
        </bk-table>

        <bk-sideslider
            :is-show="isShowResourceInstanceSideslider"
            :title="resourceInstanceSidesliderTitle"
            :width="720"
            quick-close
            transfer
            ext-cls="relate-instance-sideslider"
            @update:isShow="handleResourceCancel">
            <div slot="content" class="sideslider-content">
                <render-resource
                    ref="renderResourceRef"
                    :data="condition"
                    :original-data="originalCondition"
                    :flag="curFlag"
                    :selection-mode="curSelectionMode"
                    :disabled="curDisabled"
                    :params="params"
                    @on-limit-change="handlerLimitChange"
                    @on-init="handlerOnInit" />
            </div>
            <div slot="footer" style="margin-left: 25px;">
                <bk-button theme="primary" :disabled="disabled" :loading="sliderLoading" @click="handlerResourceSumit">{{ $t(`m.common['保存']`) }}</bk-button>
                <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handlerResourcePreview" v-if="isShowPreview">{{ $t(`m.common['预览']`) }}</bk-button>
                <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourceCancel">{{ $t(`m.common['取消']`) }}</bk-button>
            </div>
        </bk-sideslider>

        <preview-resource-dialog
            :show="isShowPreviewDialog"
            :title="previewDialogTitle"
            :params="previewResourceParams"
            @on-after-leave="handlerPreviewDialogClose" />

        <render-aggregate-sideslider
            :show.sync="isShowAggregateSideslider"
            :params="aggregateResourceParams"
            :value="aggregateValue"
            @on-selected="handlerSelectAggregateRes" />
    </div>
</template>

<script>
    import _ from 'lodash'
    import { mapGetters } from 'vuex'
    import Condition from '@/model/condition'
    import RenderAggregateSideslider from '@/components/choose-ip/sideslider'
    import { leaveConfirm } from '@/common/leave-confirm'
    import RenderResource from './render-resource'
    import RenderCondition from '../../perm-apply/components/render-condition'
    import PreviewResourceDialog from '../../perm-apply/components/preview-resource-dialog'
    import GradePolicy from '@/model/grade-policy'
    import { PERMANENT_TIMESTAMP } from '@/common/constants'

    export default {
        name: 'resource-instance-table',
        components: {
            RenderResource,
            RenderCondition,
            PreviewResourceDialog,
            RenderAggregateSideslider
        },
        props: {
            list: {
                type: Array,
                default: () => []
            },
            originalList: {
                type: Array,
                default: () => []
            },
            systemId: {
                type: String,
                default: ''
            },
            backupList: {
                type: Array,
                default: () => []
            },
            actions: {
                type: Array,
                default: () => []
            }
        },
        data () {
            return {
                tableList: [],
                isShowResourceInstanceSideslider: false,
                resourceInstanceSidesliderTitle: '',
                // 查询参数
                params: {},
                disabled: false,
                curIndex: -1,
                curResIndex: -1,
                curGroupIndex: -1,
                isShowPreviewDialog: false,
                previewDialogTitle: '',
                previewResourceParams: {},
                curCopyData: ['none'],
                curCopyKey: '',

                isShowAggregateSideslider: false,

                aggregateResourceParams: {},
                aggregateIndex: -1,
                aggregateValue: [],
                // 当前复制的数据形态: normal: 普通; aggregate: 聚合后
                curCopyMode: 'normal',
                curAggregateResourceType: {},
                curCopyParams: {},
                sliderLoading: false,
                systemFilter: []

            }
        },
        computed: {
            ...mapGetters(['user']),
            condition () {
                if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
                    return []
                }
                const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex]
                if (!curData) {
                    return []
                }
                return _.cloneDeep(curData.condition)
            },
            originalCondition () {
                if (this.curIndex === -1
                    || this.curResIndex === -1
                    || this.curGroupIndex === -1
                    || this.originalList.length < 1
                    || !this.originalList[this.curIndex]
                    || this.originalList[this.curIndex].resource_groups[this.curGroupIndex]
                        .related_resource_types.length < 1) {
                    return []
                }
                const curData = this.originalList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex]
                return _.cloneDeep(curData.condition)
            },
            curDisabled () {
                if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
                    return false
                }
                const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex]
                return curData.isDefaultLimit
            },
            curFlag () {
                if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
                    return 'add'
                }
                const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex]
                return curData.flag
            },
            curSelectionMode () {
                if (this.curIndex === -1 || this.curResIndex === -1 || this.curGroupIndex === -1) {
                    return 'all'
                }
                const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex]
                return curData.selectionMode
            },
            isShowPreview () {
                if (this.curIndex === -1) {
                    return false
                }
                return this.tableList[this.curIndex].policy_id !== ''
            }
        },
        watch: {
            list: {
                handler (value) {
                    // // mock数据
                    // value.forEach((element, index) => {
                    //     element.resource_groups = [{
                    //         id: index,
                    //         related_resource_types: element.related_resource_types
                    //     }]
                    // })
                    this.tableList = value
                    this.tableList.forEach(item => {
                        if (!this.systemFilter.find(subItem => subItem.value === item.system_id)) {
                            this.systemFilter.push({
                                text: item.system_name,
                                value: item.system_id
                            })
                        }
                    })
                },
                immediate: true
            },
            systemId: {
                handler (value) {
                    if (value !== '') {
                        this.curCopyKey = ''
                        this.curCopyData = ['none']
                        this.curIndex = -1
                        this.curResIndex = -1
                        this.curGroupIndex = -1
                        this.aggregateResourceParams = {}
                        this.aggregateIndex = -1
                        this.aggregateValue = []
                        this.curCopyMode = 'normal'
                        this.curAggregateResourceType = {}
                        this.curCopyParams = {}
                    }
                },
                immediate: true
            }
        },
        created () {
            console.log('1.我的分级管理员-最大可授权资源范围')
            // 判断数组是否被另外一个数组包含
            this.isArrayInclude = (target, origin) => {
                const itemAry = []
                target.forEach(function (p1) {
                    if (origin.indexOf(p1) !== -1) {
                        itemAry.push(p1)
                    }
                })
                if (itemAry.length === target.length) {
                    return true
                }
                return false
            }
        },
        methods: {
            // 过滤方法
            systemFilterMethod (value, row, column) {
                const property = column.property
                return row[property] === value
            },
            handlerRemove (row, payload) {
                window.changeDialog = true
                if (row.isAggregate) {
                    this.$emit('on-aggregate-delete', row.system_id, row.actions, payload)
                    return
                }
                this.$emit('on-delete', row.system_id, row.id, `${row.system_id}&${row.id}`, payload)
            },

            // handlerRowMouseEnter (index) {
            //     this.$set(this.tableList[index], 'canRemove', true)
            // },

            // handlerRowMouseLeave (index) {
            //     this.$delete(this.tableList[index], 'canRemove')
            // },

            getCellClass ({ row, column, rowIndex, columnIndex }) {
                if (columnIndex === 2) {
                    return 'iam-perm-table-cell-cls'
                }
                return ''
            },

            showMessage (payload) {
                this.bkMessageInstance = this.$bkMessage({
                    limit: 1,
                    theme: 'success',
                    message: payload
                })
            },

            handlerLimitChange () {
                const curData = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex]
                curData.isChange = true
            },

            handlerOnInit (payload) {
                this.disabled = !payload
            },

            showAggregateResourceInstance (data, index) {
                this.aggregateResourceParams = _.cloneDeep(data.aggregateResourceType)
                this.aggregateIndex = index
                this.aggregateValue = _.cloneDeep(data.instances.map(item => {
                    return {
                        id: item.id,
                        display_name: item.name
                    }
                }))
                this.isShowAggregateSideslider = true
            },

            handlerSelectAggregateRes (payload) {
                window.changeDialog = true
                this.tableList[this.aggregateIndex].instances = payload.map(item => {
                    return {
                        id: item.id,
                        name: item.display_name
                    }
                })
                this.tableList[this.aggregateIndex].isError = false
                this.$emit('on-select', this.tableList[this.aggregateIndex])
            },

            showResourceInstance (data, resItem, resIndex, groupIndex) {
                this.params = {
                    system_id: data.system_id,
                    action_id: data.id,
                    resource_type_system: resItem.system_id,
                    resource_type_id: resItem.type
                }
                const index = this.tableList.findIndex(item => `${item.system_id}${item.id}` === `${data.system_id}${data.id}`)
                this.curIndex = index
                this.curResIndex = resIndex
                this.curGroupIndex = groupIndex

                this.resourceInstanceSidesliderTitle = `${this.$t(`m.common['关联操作']`)}【${data.name}】${this.$t(`m.common['的资源实例']`)}`
                window.changeAlert = 'iamSidesider'
                this.isShowResourceInstanceSideslider = true
            },

            async handleMainActionSubmit (payload, relatedActions) {
                const curPayload = _.cloneDeep(payload)
                this.sliderLoading = true
                curPayload.forEach(item => {
                    item.instances = item.instance || []
                    item.attributes = item.attribute || []
                    delete item.instance
                    delete item.attribute
                })
                const curData = _.cloneDeep(this.tableList[this.curIndex])
                // eslint-disable-next-line max-len
                curData.resource_groups[this.curGroupIndex].related_resource_types = [curData.resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex]]
                curData.resource_groups[this.curGroupIndex].related_resource_types[0].condition = curPayload
                const relatedList = _.cloneDeep(this.tableList.filter(item => {
                    return !item.isExpiredAtDisabled
                        && !item.isAggregate
                        && relatedActions.includes(item.id)
                        && curData.system_id === item.system_id
                        && !item.resource_groups[this.curGroupIndex].related_resource_types.every(sub => sub.empty)
                }))
                if (relatedList.length > 0) {
                    relatedList.forEach(item => {
                        delete item.policy_id
                        item.resource_groups[this.curGroupIndex].related_resource_types.forEach(resItem => {
                            resItem.condition.forEach(conditionItem => {
                                conditionItem.instances = conditionItem.instance || []
                                conditionItem.attributes = conditionItem.attribute || []
                                delete conditionItem.instance
                                delete conditionItem.attribute
                            })
                        })
                        item.expired_at = PERMANENT_TIMESTAMP
                    })
                }
                try {
                    const res = await this.$store.dispatch('permApply/getRelatedPolicy', {
                        source_policy: curData,
                        system_id: curData.system_id,
                        target_policies: relatedList
                    })
                    this.handleRelatedAction(res.data)
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
                    this.sliderLoading = false
                }
            },

            // 需要确认
            handleRelatedAction (payload) {
                if (payload.length < 1) {
                    return
                }
                payload.forEach(item => {
                    const curIndex = this.tableList.findIndex(sub => sub.id === item.id
                        && sub.system_id === item.resource_groups[this.curGroupIndex]
                            .related_resource_types[0].system_id && !sub.isExpiredAtDisabled)
                    if (curIndex > -1) {
                        this.tableList.splice(curIndex, 1, new GradePolicy({
                            ...item,
                            isShowRelatedText: true,
                            system_id: this.tableList[curIndex].system_id,
                            system_name: this.tableList[curIndex].system_name,
                            tag: 'add'
                        }, 'detail'))
                    }
                })
            },

            async handlerResourceSumit () {
                window.changeDialog = true
                const conditionData = this.$refs.renderResourceRef.handleGetValue()
                const { isEmpty, data } = conditionData
                if (isEmpty || data[0] === 'none') {
                    this.isShowResourceInstanceSideslider = false
                    return
                }

                const { isMainAction, related_actions } = this.tableList[this.curIndex]
                // 如果为主操作
                if (isMainAction) {
                    await this.handleMainActionSubmit(data, related_actions)
                }
                window.changeAlert = false
                this.resourceInstanceSidesliderTitle = ''
                this.isShowResourceInstanceSideslider = false
                this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex].condition = data

                this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex].isError = false

                console.log('this.tableList11', this.tableList)
                this.curIndex = -1
                this.curResIndex = -1
                this.curGroupIndex = -1
            },

            handlerResourcePreview () {
                const { id } = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                const { system_id, type, name } = this.tableList[this.curIndex].resource_groups[this.curGroupIndex]
                    .related_resource_types[this.curResIndex]
                const condition = []
                const conditionData = this.$refs.renderResourceRef.handleGetPreviewValue()
                conditionData.forEach(item => {
                    const { id, attribute, instance } = item
                    condition.push({
                        id,
                        attributes: attribute ? attribute.filter(item => item.values.length > 0) : [],
                        instances: instance ? instance.filter(item => item.path.length > 0) : []
                    })
                })
                this.previewResourceParams = {
                    policy_id: this.tableList[this.curIndex].policy_id,
                    resource_group_id: id,
                    related_resource_type: {
                        system_id,
                        type,
                        name,
                        condition: condition.filter(item => item.attributes.length > 0 || item.instances.length > 0)
                    }
                }
                this.previewDialogTitle = `${this.$t(`m.common['操作']`)}【${this.tableList[this.curIndex].name}】${this.$t(`m.common['的资源实例']`)} ${this.$t(`m.common['差异对比']`)}`
                this.isShowPreviewDialog = true
            },

            handlerConditionMouseover (payload) {
                if (Object.keys(this.curCopyParams).length < 1 && this.curCopyMode === 'normal') {
                    return
                }
                if (this.curCopyData[0] === 'none' && this.curCopyMode === 'aggregate') {
                    return
                }
                if (this.curCopyKey === `${payload.system_id}${payload.type}`) {
                    payload.canPaste = true
                }
            },

            handlerAggregateConditionMouseover (payload) {
                if (this.curCopyData[0] === 'none') {
                    return
                }
                if (this.curCopyKey === `${payload.aggregateResourceType.system_id}${payload.aggregateResourceType.id}`) {
                    payload.canPaste = true
                }
            },

            handlerAggregateConditionMouseleave (payload) {
                payload.canPaste = false
            },

            handlerConditionMouseleave (payload) {
                payload.canPaste = false
            },

            handlerOnView (payload, item, itemIndex, groupIndex) {
                const { system_id, type, name } = item
                const condition = []
                item.condition.forEach(item => {
                    const { id, attribute, instance } = item
                    condition.push({
                        id,
                        attributes: attribute ? attribute.filter(item => item.values.length > 0) : [],
                        instances: instance ? instance.filter(item => item.path.length > 0) : []
                    })
                })
                this.previewResourceParams = {
                    policy_id: payload.policy_id,
                    resource_group_id: payload.resource_groups[groupIndex].id,
                    related_resource_type: {
                        system_id,
                        type,
                        name,
                        condition: condition.filter(item => item.attributes.length > 0 || item.instances.length > 0)
                    }
                }
                this.previewDialogTitle = `${this.$t(`m.common['操作']`)}【${payload.name}】${this.$t(`m.common['的资源实例']`)} ${this.$t(`m.common['差异对比']`)}`
                this.isShowPreviewDialog = true
            },

            handlerOnCopy (payload, index, subIndex, action) {
                window.changeDialog = true
                this.curCopyKey = `${payload.system_id}${payload.type}`
                this.curCopyData = _.cloneDeep(payload.condition)
                this.curCopyMode = 'normal'
                this.curCopyParams = this.getBacthCopyParms(action, payload)
                this.showMessage(this.$t(`m.info['实例复制']`))
                this.$refs[`condition_${index}_${subIndex}_ref`][0] && this.$refs[`condition_${index}_${subIndex}_ref`][0].setImmediatelyShow(true)
            },

            getBacthCopyParms (payload, content) {
                const actions = []
                this.tableList.forEach(item => {
                    if (!item.isAggregate) {
                        if (item.id !== payload.id) {
                            actions.push({
                                system_id: item.system_id,
                                id: item.id
                            })
                        }
                    }
                })
                actions.unshift({
                    system_id: payload.system_id,
                    id: payload.id
                })
                return {
                    resource_type: {
                        system_id: content.system_id,
                        type: content.type,
                        condition: content.condition.map(item => {
                            return {
                                id: item.id,
                                instances: item.instance || [],
                                attributes: item.attribute || []
                            }
                        })
                    },
                    actions
                }
            },

            handlerAggregateOnCopy (payload, index) {
                this.curCopyKey = `${payload.aggregateResourceType.system_id}${payload.aggregateResourceType.id}`
                this.curAggregateResourceType = payload.aggregateResourceType
                this.curCopyData = _.cloneDeep(payload.instances)
                this.curCopyMode = 'aggregate'
                this.showMessage(this.$t(`m.info['实例复制']`))
                this.$refs[`condition_${index}_aggregateRef`] && this.$refs[`condition_${index}_aggregateRef`].setImmediatelyShow(true)
            },

            handlerAggregateOnPaste (payload) {
                let tempInstances = []
                if (this.curCopyMode === 'aggregate') {
                    tempInstances = this.curCopyData
                } else {
                    if (this.curCopyData[0] !== 'none') {
                        const instances = this.curCopyData.map(item => item.instance)
                        const instanceData = instances[0][0]
                        tempInstances = instanceData.path.map(pathItem => {
                            return {
                                id: pathItem[0].id,
                                name: pathItem[0].name
                            }
                        })
                    }
                }
                if (tempInstances.length < 1) {
                    return
                }
                payload.instances = _.cloneDeep(tempInstances)
                payload.isError = false
                this.showMessage(this.$t(`m.info['粘贴成功']`))
            },

            handlerOnPaste (payload, content) {
                window.changeDialog = true
                let tempCurData = ['none']
                if (this.curCopyMode === 'normal') {
                    // if (this.curCopyData.length < 1) {
                    //     tempCurData = []
                    // } else {
                    //     if (this.curCopyData[0] !== 'none') {
                    //         tempCurData = this.curCopyData.map(item => {
                    //             delete item.id
                    //             return item
                    //         })
                    //         tempCurData.forEach((item, index) => {
                    //             if (content.condition[index]) {
                    //                 if (content.condition[index].id) {
                    //                     item.id = content.condition[index].id
                    //                 } else {
                    //                     item.id = ''
                    //                 }
                    //             } else {
                    //                 item.id = ''
                    //             }
                    //         })
                    //     }
                    // }
                    if (!payload.flag) {
                        return
                    }
                    if (payload.data.length === 0) {
                        content.condition = []
                    } else {
                        content.condition = payload.data.map(conditionItem => new Condition(conditionItem, '', 'add'))
                    }
                } else {
                    const instances = (() => {
                        const arr = []
                        const { id, name, system_id } = this.curAggregateResourceType
                        this.curCopyData.forEach(v => {
                            const curItem = arr.find(_ => _.type === id)
                            if (curItem) {
                                curItem.path.push([{
                                    id: v.id,
                                    name: v.name,
                                    system_id,
                                    type: id,
                                    type_name: name
                                }])
                            } else {
                                arr.push({
                                    name,
                                    type: id,
                                    path: [[{
                                        id: v.id,
                                        name: v.name,
                                        system_id,
                                        type: id,
                                        type_name: name
                                    }]]
                                })
                            }
                        })
                        return arr
                    })()
                    if (instances.length > 0) {
                        tempCurData = [new Condition({ instances }, '', 'add')]
                    }
                }
                if (tempCurData[0] === 'none') {
                    return
                }
                content.condition = _.cloneDeep(tempCurData)
                content.isError = false
                this.showMessage(this.$t(`m.info['粘贴成功']`))
            },

            handlerAggregateOnBatchPaste (payload, index) {
                let tempCurData = ['none']
                let tempArrgegateData = []
                if (this.curCopyMode === 'normal') {
                    if (this.curCopyData[0] !== 'none') {
                        tempCurData = this.curCopyData.map(item => {
                            delete item.id
                            return item
                        })
                        const instances = this.curCopyData.map(item => item.instance)
                        const instanceData = instances[0][0]
                        tempArrgegateData = instanceData.path.map(pathItem => {
                            return {
                                id: pathItem[0].id,
                                name: pathItem[0].name
                            }
                        })
                    }
                } else {
                    tempArrgegateData = this.curCopyData
                    const instances = (() => {
                        const arr = []
                        const { id, name, system_id } = this.curAggregateResourceType
                        this.curCopyData.forEach(v => {
                            const curItem = arr.find(_ => _.type === id)
                            if (curItem) {
                                curItem.path.push([{
                                    id: v.id,
                                    name: v.name,
                                    system_id,
                                    type: id,
                                    type_name: name
                                }])
                            } else {
                                arr.push({
                                    name,
                                    type: id,
                                    path: [[{
                                        id: v.id,
                                        name: v.name,
                                        system_id,
                                        type: id,
                                        type_name: name
                                    }]]
                                })
                            }
                        })
                        return arr
                    })()
                    if (instances.length > 0) {
                        tempCurData = [new Condition({ instances }, '', 'add')]
                    }
                }
                this.tableList.forEach(item => {
                    if (!item.isAggregate) {
                        item.resource_groups.forEach(groupItem => {
                            groupItem.related_resource_types.forEach(subItem => {
                                if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                                    subItem.condition = _.cloneDeep(tempCurData)
                                    subItem.isError = false
                                }
                            })
                        })
                    } else {
                        if (`${item.aggregateResourceType.system_id}${item.aggregateResourceType.id}` === this.curCopyKey) {
                            item.instances = _.cloneDeep(tempArrgegateData)
                            item.isError = false
                        }
                    }
                })
                payload.isError = false
                this.curCopyData = ['none']
                this.$refs[`condition_${index}_aggregateRef`] && this.$refs[`condition_${index}_aggregateRef`].setImmediatelyShow(false)
                this.showMessage(this.$t(`m.info['批量粘贴成功']`))
            },

            handlerOnBatchPaste (payload, content, index, subIndex) {
                window.changeDialog = true
                let tempCurData = ['none']
                let tempArrgegateData = []
                if (this.curCopyMode === 'normal') {
                    if (!payload.flag) {
                        return
                    }
                    // 预计算是否存在 聚合后的数据 可以粘贴
                    const flag = this.tableList.some(item => !!item.isAggregate
                        && `${item.aggregateResourceType.system_id}${item.aggregateResourceType.id}` === this.curCopyKey)
                    if (flag) {
                        if (this.curCopyData.length < 1) {
                            tempCurData = []
                        } else {
                            if (this.curCopyData[0] !== 'none') {
                                tempCurData = this.curCopyData.map(item => {
                                    delete item.id
                                    return item
                                })
                                tempCurData.forEach((item, index) => {
                                    if (content.condition[index]) {
                                        if (content.condition[index].id) {
                                            item.id = content.condition[index].id
                                        } else {
                                            item.id = ''
                                        }
                                    } else {
                                        item.id = ''
                                    }
                                })
                                const instances = this.curCopyData.map(item => item.instance)
                                const instanceData = instances[0][0]
                                tempArrgegateData = instanceData.path.map(pathItem => {
                                    return {
                                        id: pathItem[0].id,
                                        name: pathItem[0].name
                                    }
                                })
                            }
                        }
                    }
                    if (payload.data.length === 0) {
                        this.tableList.forEach(item => {
                            if (!item.isAggregate) {
                                item.resource_groups.forEach(groupItem => {
                                    groupItem.related_resource_types.forEach(resItem => {
                                        if (`${resItem.system_id}${resItem.type}` === this.curCopyKey) {
                                            resItem.condition = []
                                            resItem.isError = false
                                        }
                                    })
                                })
                            } else {
                                if (`${item.aggregateResourceType.system_id}${item.aggregateResourceType.id}` === this.curCopyKey) {
                                    item.instances = _.cloneDeep(tempArrgegateData)
                                    item.isError = false
                                    this.$emit('on-select', item)
                                }
                            }
                        })
                    } else {
                        this.tableList.forEach(item => {
                            if (!item.isAggregate) {
                                const curPasteData = payload.data.find(_ => _.id === item.id)
                                if (curPasteData) {
                                    item.resource_groups.forEach(groupItem => {
                                        groupItem.related_resource_types.forEach(resItem => {
                                            if (`${resItem.system_id}${resItem.type}` === `${curPasteData.resource_type.system_id}${curPasteData.resource_type.type}`) {
                                                resItem.condition = curPasteData.resource_type.condition.map(conditionItem => new Condition(conditionItem, '', 'add'))
                                                resItem.isError = false
                                            }
                                        })
                                    })
                                }
                            } else {
                                if (`${item.aggregateResourceType.system_id}${item.aggregateResourceType.id}` === this.curCopyKey) {
                                    item.instances = _.cloneDeep(tempArrgegateData)
                                    item.isError = false
                                    this.$emit('on-select', item)
                                }
                            }
                        })
                    }
                } else {
                    tempArrgegateData = this.curCopyData
                    const instances = (() => {
                        const arr = []
                        const { id, name, system_id } = this.curAggregateResourceType
                        this.curCopyData.forEach(v => {
                            const curItem = arr.find(_ => _.type === id)
                            if (curItem) {
                                curItem.path.push([{
                                    id: v.id,
                                    name: v.name,
                                    system_id,
                                    type: id,
                                    type_name: name
                                }])
                            } else {
                                arr.push({
                                    name,
                                    type: id,
                                    path: [[{
                                        id: v.id,
                                        name: v.name,
                                        system_id,
                                        type: id,
                                        type_name: name
                                    }]]
                                })
                            }
                        })
                        return arr
                    })()
                    if (instances.length > 0) {
                        tempCurData = [new Condition({ instances }, '', 'add')]
                    }
                    this.tableList.forEach(item => {
                        if (!item.isAggregate) {
                            item.resource_groups.forEach(groupItem => {
                                groupItem.related_resource_types.forEach(subItem => {
                                    if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                                        subItem.condition = _.cloneDeep(tempCurData)
                                        subItem.isError = false
                                    }
                                })
                            })
                        } else {
                            if (`${item.aggregateResourceType.system_id}${item.aggregateResourceType.id}` === this.curCopyKey) {
                                item.instances = _.cloneDeep(tempArrgegateData)
                                item.isError = false
                            }
                        }
                    })
                }
                content.isError = false
                this.$refs[`condition_${index}_${subIndex}_ref`][0] && this.$refs[`condition_${index}_${subIndex}_ref`][0].setImmediatelyShow(false)
                this.curCopyData = ['none']
                this.showMessage(this.$t(`m.info['批量粘贴成功']`))
            },

            handlerPreviewDialogClose () {
                this.previewDialogTitle = ''
                this.isShowPreviewDialog = false
            },

            handlerResourceSliderClose () {
                this.curIndex = -1
                this.curResIndex = -1
                this.curGroupIndex = -1
                this.previewResourceParams = {}
                this.params = {}
            },

            resetDataAfterClose () {
                this.curIndex = -1
                this.curResIndex = -1
                this.curGroupIndex = -1
                this.previewResourceParams = {}
                this.params = {}
                this.resourceInstanceSidesliderTitle = ''
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

            handleGetValue () {
                // flag：提交时校验标识
                let flag = false
                if (this.tableList.length < 1) {
                    flag = true
                    return {
                        flag,
                        actions: [],
                        attach_actions: []
                    }
                }
                const actionList = []
                this.tableList.forEach(item => {
                    const curSystemData = actionList.find(subItem => subItem.system_id === item.system_id)
                    if (!item.isAggregate) {
                        const groupResourceTypes = []
                        if (item.resource_groups.length > 0) {
                            item.resource_groups.forEach(groupItem => {
                                const relatedResourceTypes = []
                                if (groupItem.related_resource_types.length > 0) {
                                    groupItem.related_resource_types.forEach(resItem => {
                                        if (resItem.empty) {
                                            resItem.isError = true
                                            flag = true
                                        }
                                        const conditionList = (resItem.condition.length > 0 && !resItem.empty)
                                            ? resItem.condition.map(conItem => {
                                                const { id, instance, attribute } = conItem
                                                const attributeList = (attribute && attribute.length > 0)
                                                    // eslint-disable-next-line max-len
                                                    ? attribute.map(({ id, name, values }) => ({ id, name, values })) : []
        
                                                const instanceList = (instance && instance.length > 0)
                                                    ? instance.map(({ name, type, path }) => {
                                                        const tempPath = _.cloneDeep(path)
                                                        tempPath.forEach(pathItem => {
                                                            pathItem.forEach(pathSubItem => {
                                                                delete pathSubItem.disabled
                                                            })
                                                        })
                                                        return {
                                                            name,
                                                            type,
                                                            path: tempPath
                                                        }
                                                    })
                                                    : []
                                                return {
                                                    id,
                                                    instances: instanceList,
                                                    attributes: attributeList
                                                }
                                            })
                                            : []
                                        relatedResourceTypes.push({
                                            type: resItem.type,
                                            system_id: resItem.system_id,
                                            name: resItem.name,
                                            condition: conditionList
                                        })
                                    })
                                }
                                groupResourceTypes.push({
                                    id: groupItem.id,
                                    related_resource_types: relatedResourceTypes
                                })
                            })
                        }
                        const params = {
                            system_id: item.system_id,
                            actions: [
                                {
                                    id: item.id,
                                    resource_groups: groupResourceTypes
                                }
                            ],
                            aggregations: []
                        }
                        if (curSystemData) {
                            curSystemData.actions.push({
                                id: item.id,
                                resource_groups: groupResourceTypes
                            })
                        } else {
                            actionList.push(params)
                        }
                    } else {
                        const { actions, aggregateResourceType, instances } = item
                        if (instances.length < 1) {
                            item.isError = true
                            flag = true
                        }
                        if (instances.length > 0) {
                            const aggregateParams = {
                                system_id: item.system_id,
                                aggregations: [{
                                    actions,
                                    aggregate_resource_type: {
                                        id: aggregateResourceType.id,
                                        system_id: aggregateResourceType.system_id,
                                        instances
                                    }
                                }],
                                actions: []
                            }
                            if (curSystemData) {
                                curSystemData.aggregations.push({
                                    actions,
                                    aggregate_resource_type: {
                                        id: aggregateResourceType.id,
                                        system_id: aggregateResourceType.system_id,
                                        instances
                                    }
                                })
                            } else {
                                actionList.push(aggregateParams)
                            }
                        }
                    }
                })

                // const isExistBackList = this.tableList.filter(
                //     item => item.isAggregate && item.instances.length < 1 && item.selectValueDisplay !== ''
                // )
                // if (isExistBackList.length > 0) {
                //     const actions = isExistBackList.map(
                //         item => item.actions.map(subItem => `${subItem.system_id}&${subItem.id}`)
                //     ).flat()
                //     const backupList = this.backupList.filter(
                //         item => actions.includes(`${item.system_id}&${item.id}`)
                //     )
                //     backupList.forEach(item => {
                //         const curSystemData = actionList.find(subItem => subItem.system_id === item.system_id)
                //         if (!item.isAggregate) {
                //             const relatedResourceTypes = []
                //             if (item.related_resource_types.length > 0) {
                //                 item.related_resource_types.forEach(resItem => {
                //                     if (resItem.empty) {
                //                         resItem.isError = true
                //                         flag = true
                //                     }
                //                     const conditionList = (resItem.condition.length > 0 && !resItem.empty)
                //                         ? resItem.condition.map(conItem => {
                //                             const { id, instance, attribute } = conItem
                //                             const attributeList = (attribute && attribute.length > 0)
                //                                 ? attribute.map(({ id, name, values }) => ({ id, name, values }))
                //                                 : []

                //                             const instanceList = (instance && instance.length > 0)
                //                                 ? instance.map(({ name, type, path }) => {
                //                                     const tempPath = _.cloneDeep(path)
                //                                     tempPath.forEach(pathItem => {
                //                                         pathItem.forEach(pathSubItem => {
                //                                             delete pathSubItem.disabled
                //                                         })
                //                                     })
                //                                     return {
                //                                         name,
                //                                         type,
                //                                         path: tempPath
                //                                     }
                //                                 })
                //                                 : []
                //                             return {
                //                                 id,
                //                                 instances: instanceList,
                //                                 attributes: attributeList
                //                             }
                //                         })
                //                         : []
                //                     relatedResourceTypes.push({
                //                         type: resItem.type,
                //                         system_id: resItem.system_id,
                //                         name: resItem.name,
                //                         condition: conditionList
                //                     })
                //                 })
                //             }
                //             const params = {
                //                 system_id: item.system_id,
                //                 actions: [
                //                     {
                //                         id: item.id,
                //                         related_resource_types: relatedResourceTypes
                //                     }
                //                 ],
                //                 aggregations: []
                //             }
                //             if (curSystemData) {
                //                 curSystemData.actions.push({
                //                     id: item.id,
                //                     related_resource_types: relatedResourceTypes
                //                 })
                //             } else {
                //                 actionList.push(params)
                //             }
                //         }
                //     })
                // }

                return {
                    flag,
                    actions: actionList
                }
            }
        }
    }
</script>

<style lang="postcss">
    .iam-grade-split-wrapper {
        min-height: 101px;
        .bk-table {
            width: 100%;
            margin-top: 8px;
            border-right: none;
            border-bottom: none;
            font-size: 12px;
            .bk-table-header-wrapper {
                th:first-child .cell {
                    padding-left: 20px;
                }
            }
            .bk-table-body {
                tr {
                    &:hover {
                        background-color: transparent;
                        & > td {
                            background-color: transparent;
                        .remove-icon {
                            display: inline-block;
                        }
                        }
                    }
                }
                td:first-child .cell,
                th:first-child .cell {
                    padding-left: 15px;
                }
            }
            .relation-content-wrapper,
            .conditions-wrapper {
                position: relative;
                height: 100%;
                padding: 17px 0;
                color: #63656e;
                .resource-type-name {
                    display: block;
                    margin-bottom: 9px;
                }
                .iam-condition-item {
                    width: 90%;
                }
            }

            .remove-icon {
                display: none;
                position: absolute;
                top: 5px;
                right: 10px;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                }
                i {
                    font-size: 20px;
                }
            }

            .relation-content-item {
                margin-top: 17px;
                &:first-child {
                    margin-top: 0;
                }
                .content-name {
                    margin-bottom: 9px;
                }
            }

            .set-padding {
                padding: 10px 0;
            }

            .action-name {
                margin-left: 6px;
                display: inline-block;
                max-width: 200px;
                overflow: hidden;
                text-overflow: ellipsis;
                word-break: keep-all;
                vertical-align: bottom;
            }

            .conditions-item {
                margin-top: 7px;
                &:first-child {
                    margin-top: 0;
                }
            }
        }

    }
    .relate-instance-sideslider {
        .sideslider-content {
            height: calc(100vh - 114px);
        }
        .bk-sideslider-footer {
            background-color: #f5f6fa!important;
            border-color: #dcdee5!important;
        }
    }
</style>
