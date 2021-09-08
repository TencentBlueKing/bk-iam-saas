<template>
    <!-- eslint-disable max-len -->
    <div class="resource-instance-table-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
        <bk-table
            v-if="!isLoading"
            :data="tableList"
            border
            :row-class-name="handleRowClass"
            :cell-class-name="getCellClass"
            :empty-text="$t(`m.verify['请选择操作']`)">
            <bk-table-column :resizable="false" :label="$t(`m.common['操作']`)" width="250">
                <template slot-scope="{ row }">
                    <div v-if="!!row.isAggregate" style="padding: 10px 0;">
                        <span class="action-name" :title="row.name">{{ row.name }}</span>
                    </div>
                    <div v-else>
                        <span class="action-name" :title="row.name">{{ row.name }}</span>
                        <iam-svg name="icon-new" ext-cls="iam-new-action" v-if="row.isNew && curLanguageIsCn" />
                        <iam-svg name="icon-new-en" ext-cls="iam-new-action" v-if="row.isNew && !curLanguageIsCn" />
                        <iam-svg name="icon-changed" ext-cls="iam-new-action" v-if="row.isChanged && curLanguageIsCn" />
                        <iam-svg name="icon-changed-en" ext-cls="iam-new-action" v-if="row.isChanged && !curLanguageIsCn" />
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" min-width="450">
                <template slot-scope="{ row, $index }">
                    <!-- isAggregate代表批量编辑状态 -->
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
                            <div class="relation-content-item" v-for="(content, contentIndex) in row.related_resource_types" :key="contentIndex">
                                <div class="content-name">
                                    {{ content.name }}
                                    <template v-if="row.isShowRelatedText">
                                        <div style="display: inline-block; color: #979ba5;">
                                            ({{ $t(`m.info['已帮您自动勾选依赖操作需要的实例']`) }})
                                        </div>
                                    </template>
                                </div>
                                <div class="content">
                                    <render-condition
                                        :ref="`condition_${$index}_${contentIndex}_ref`"
                                        :value="content.value"
                                        :is-empty="content.empty"
                                        :can-view="row.canView"
                                        :params="curCopyParams"
                                        :can-paste="content.canPaste"
                                        :is-error="content.isLimitExceeded || content.isError"
                                        @on-mouseover="handlerConditionMouseover(content)"
                                        @on-mouseleave="handlerConditionMouseleave(content)"
                                        @on-view="handlerOnView(row, content, contentIndex)"
                                        @on-copy="handlerOnCopy(content, $index, contentIndex, row)"
                                        @on-paste="handlerOnPaste(...arguments, row, content)"
                                        @on-batch-paste="handlerOnBatchPaste(...arguments, content, $index, contentIndex)"
                                        @on-click="showResourceInstance(row, content, contentIndex)" />
                                </div>
                                <p v-if="content.isLimitExceeded" class="is-limit-error">{{ $t(`m.info['实例数量限制提示']`) }}</p>
                            </div>
                        </template>
                        <template v-else>
                            {{ $t(`m.common['无需关联实例']`) }}
                        </template>
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :resizable="false" prop="description" :label="$t(`m.common['申请期限']`)" min-width="150">
                <template slot-scope="{ row, $index }">
                    <!-- {{row.inOriginalList}}--++--{{row.isNew}}--{{row.expired_display}}--{{row.isExpired}}--{{row.tag}} -->
                    <!-- inOriginalList:{{row.inOriginalList}}--
                    isNew:{{row.isNew}}--
                    isChanged:{{row.isChanged}}--
                    isExpired:{{row.isExpired}}--{{row.tag}}--{{row.expired_display}} -->
                    <!-- tag add 不需要比较过期时间，直接不禁用下拉框 -->
                    <!-- tag update 需要比较过期时间，过期时，显示续期，点击续期然后操作下拉框；不过期时，下拉框禁用 -->
                    <template v-if="row.isShowRenewal">
                        <!-- 11 -->
                        <bk-button theme="primary" class="renewal-action" outline @click="handleOpenRenewal(row, $index)">
                            {{ $t(`m.renewal['续期']`) }}
                        </bk-button>
                    </template>
                    <template v-else>
                        <!-- 22 -->
                        <template v-if="!row.isNew && !row.isExpired">
                            <!-- 33 -->
                            <div class="mock-disabled-select">{{row.expired_display}}</div>
                        </template>
                        <template v-else>
                            <!-- 44 -->
                            <template v-if="row.isShowRelatedText && row.inOriginalList">
                                <!-- 55 -->
                                <div class="mock-disabled-select">{{row.expired_display}}</div>
                            </template>
                            <template v-else>
                                <!-- 66{{row.expiredAtPlaceholder}}--{{user.timestamp}} -->
                                <bk-select
                                    v-model="row.expired_at"
                                    :clearable="false"
                                    :ref="`${row.id}&expiredAtRef`"
                                    :placeholder="row.expiredAtPlaceholder"
                                    ext-cls="iam-deadline-select"
                                    ext-popover-cls="iam-deadline-select-dropdown-content"
                                    @toggle="handleExpiredToggle(...arguments, row)"
                                    @selected="handleExpiredSelect(...arguments, row)">
                                    <bk-option v-for="option in durationList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                    <div slot="extension" style="cursor: pointer;" @click.stop="handleOpenCustom(row)">
                                        <template v-if="!row.isShowCustom">
                                            {{ $t(`m.common['自定义']`) }}
                                        </template>
                                        <template v-else>
                                            <bk-input
                                                v-model="row.customValue"
                                                size="small"
                                                :placeholder="$t(`m.common['期限选择提示']`)"
                                                maxlength="3"
                                                ext-cls="iam-perm-apply-expired-input-cls"
                                                @blur="handleBlur(...arguments, row)"
                                                @input="handleInput(...arguments, row)"
                                                @enter="handleEnter(...arguments, row)">
                                                <template slot="append">
                                                    <div class="group-text">{{ $t(`m.common['天']`) }}</div>
                                                </template>
                                            </bk-input>
                                        </template>
                                    </div>
                                </bk-select>
                                <bk-button
                                    class="cancel-renewal-action"
                                    outline
                                    v-if="!row.isNew && !row.isShowRenewal"
                                    @click="handleCancelRenewal(row)">
                                    {{ $t(`m.permApply['取消续期']`) }}
                                </bk-button>
                            </template>
                        </template>
                    </template>
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
                    :disabled="curDisabled"
                    :params="params"
                    @on-limit-change="handleLimitChange"
                    @on-init="handleOnInit" />
            </div>
            <div slot="footer" style="margin-left: 25px;">
                <bk-button theme="primary" :loading="sliderLoading" :disabled="disabled" @click="handleResourceSumit">{{ $t(`m.common['保存']`) }}</bk-button>
                <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourcePreview" v-if="isShowPreview">{{ $t(`m.common['预览']`) }}</bk-button>
                <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourceCancel">{{ $t(`m.common['取消']`) }}</bk-button>
            </div>
        </bk-sideslider>

        <preview-resource-dialog
            :show="isShowPreviewDialog"
            :title="previewDialogTitle"
            :params="previewResourceParams"
            @on-after-leave="handlePreviewDialogClose" />

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
    import RenderAggregateSideslider from '@/components/choose-ip/sideslider'
    import Condition from '@/model/condition'
    import Policy from '@/model/policy'
    import { leaveConfirm } from '@/common/leave-confirm'
    import { PERMANENT_TIMESTAMP } from '@/common/constants'
    import RenderResource from './render-resource'
    import RenderCondition from './render-condition'
    import PreviewResourceDialog from './preview-resource-dialog'

    // 单次申请的最大实例数
    const RESOURCE_MAX_LEN = 20

    // 6个月的时间戳
    const DEFAULT_TIMESTAMP = 15552000

    export default {
        name: 'resource-instance-table',
        components: {
            RenderAggregateSideslider,
            RenderResource,
            RenderCondition,
            PreviewResourceDialog
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
            }
        },
        data () {
            return {
                tableList: [],
                durationList: [
                    { id: 2592000, name: this.$t(`m.common['1个月']`) },
                    { id: 7776000, name: this.$t(`m.common['3个月']`) },
                    { id: 15552000, name: this.$t(`m.common['6个月']`) },
                    { id: 31104000, name: this.$t(`m.common['12个月']`) }
                    // { id: 4102444800, name: this.$t(`m.common['永久']`) }
                ],
                isShowResourceInstanceSideslider: false,
                resourceInstanceSidesliderTitle: '',
                // 查询参数
                params: {},
                disabled: false,
                curIndex: -1,
                curResIndex: -1,
                isShowPreviewDialog: false,
                previewDialogTitle: '',
                previewResourceParams: {},
                curCopyData: ['none'],
                curCopyType: '',

                curId: '',
                isLoading: false,

                isShowAggregateSideslider: false,

                aggregateResourceParams: {},
                aggregateIndex: -1,
                aggregateValue: [],
                // 当前复制的数据形态: normal: 普通; aggregate: 聚合后
                curCopyMode: 'normal',
                curAggregateResourceType: {},
                curCopyParams: {},
                sliderLoading: false,
                needEmitFlag: false
            }
        },
        computed: {
            ...mapGetters(['user']),
            condition () {
                if (this.curIndex === -1 || this.curResIndex === -1) {
                    return []
                }
                const curData = this.tableList[this.curIndex].related_resource_types[this.curResIndex]
                if (!curData) {
                    return []
                }
                if (curData.condition.length === 0) curData.condition = ['none']
                return _.cloneDeep(curData.condition)
            },
            originalCondition () {
                if (this.curIndex === -1
                    || this.curResIndex === -1
                    || this.originalList.length < 1) {
                    return []
                }
                const curId = this.tableList[this.curIndex].id
                const curType = this.tableList[this.curIndex].related_resource_types[this.curResIndex].type
                if (!this.originalList.some(item => item.id === curId)) {
                    return []
                }
                const curResTypeData = this.originalList.find(item => item.id === curId)
                if (!curResTypeData.related_resource_types.some(item => item.type === curType)) {
                    return []
                }
                const curData = curResTypeData.related_resource_types.find(item => item.type === curType)
                if (!curData) {
                    return []
                }
                return _.cloneDeep(curData.condition)
            },
            curDisabled () {
                if (this.curIndex === -1 || this.curResIndex === -1) {
                    return false
                }
                const curData = this.tableList[this.curIndex].related_resource_types[this.curResIndex]
                return curData.isDefaultLimit
            },
            curFlag () {
                if (this.curIndex === -1 || this.curResIndex === -1) {
                    return 'add'
                }
                const curData = this.tableList[this.curIndex].related_resource_types[this.curResIndex]
                return curData.flag
            },
            curSelectionMode () {
                if (this.curIndex === -1 || this.curResIndex === -1) {
                    return 'all'
                }
                const curData = this.tableList[this.curIndex].related_resource_types[this.curResIndex]
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
                    this.tableList = value
                    console.log('this.tableList', this.tableList)
                },
                immediate: true
            },
            systemId: {
                handler (value) {
                    if (value !== '') {
                        this.curCopyType = ''
                        this.curCopyData = ['none']
                        this.curIndex = -1
                        this.curResIndex = -1
                        this.aggregateResourceParams = {}
                        this.aggregateIndex = -1
                        this.aggregateValue = []
                        this.curCopyMode = 'normal'
                        this.curCopyParams = {}
                        this.curAggregateResourceType = {}
                        this.needEmitFlag = false
                    }
                },
                immediate: true
            }
        },
        methods: {
            handleOpenRenewal (row, index) {
                row.isShowRenewal = false
                row.customValueBackup = row.customValue
                row.expired_at_backup = row.expired_at
                row.expired_display_backup = row.expired_display
                row.expired_at = DEFAULT_TIMESTAMP
                row.expired_display = ''
                row.customValue = ''
                this.$set(this.tableList, index, row)
            },

            handleCancelRenewal (payload) {
                payload.isShowRenewal = true
                payload.expired_at = payload.expired_at_backup
                payload.expired_display = payload.expired_display_backup
                payload.customValue = payload.customValueBackup
                delete payload.expired_at_backup
                delete payload.expired_display_backup
                delete payload.customValueBackup
            },

            handlerSelectAggregateRes (payload) {
                this.tableList[this.aggregateIndex].instances = payload.map(item => {
                    return {
                        id: item.id,
                        name: item.display_name
                    }
                })
                this.tableList[this.aggregateIndex].isError = false
                this.$emit('on-select', this.tableList[this.aggregateIndex])
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
                        item.related_resource_types.forEach(subItem => {
                            if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                                subItem.condition = _.cloneDeep(tempCurData)
                                subItem.isError = false
                            }
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

            showMessage (payload) {
                this.bkMessageInstance = this.$bkMessage({
                    limit: 1,
                    theme: 'success',
                    message: payload
                })
            },

            getCellClass ({ row, column, rowIndex, columnIndex }) {
                if (columnIndex === 1) {
                    return 'iam-perm-table-cell-cls'
                }
                return ''
            },

            handleRowClass (payload) {
                const { row } = payload
                if (row.isAggregate) {
                    return ''
                }
                if (row.tid !== '' && ['add', 'update'].includes(row.tag) && !this.$route.query.system_id && !this.$route.query.tid) {
                    return 'has-perm-row-cls'
                }
                if (row.isExistPermAnimation) {
                    return 'has-perm-row-animation-cls'
                }
                return ''
            },

            handleLinearData (payload, parentId = null) {
                payload.forEach(item => {
                    item.parent = parentId
                    this.actionLinearTopologies.push(_.cloneDeep(item))
                    if (item.sub_actions && item.sub_actions.length > 0) {
                        this.handleLinearData(item.sub_actions, item.id)
                    }
                })
            },

            handleLimitChange () {
                const curData = this.tableList[this.curIndex].related_resource_types[this.curResIndex]
                curData.isChange = true
            },

            handleOnInit (payload) {
                this.disabled = !payload
            },

            handleOpenCustom (payload) {
                payload.isShowCustom = true
            },

            showResourceInstance (data, resItem, resIndex) {
                this.params = {
                    system_id: this.systemId,
                    action_id: data.id,
                    resource_type_system: resItem.system_id,
                    resource_type_id: resItem.type
                }
                const index = this.tableList.findIndex(item => item.id === data.id)
                this.curIndex = index
                this.curResIndex = resIndex

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
                curData.related_resource_types = [curData.related_resource_types[this.curResIndex]]
                curData.related_resource_types[0].condition = curPayload
                if (curData.expired_at !== PERMANENT_TIMESTAMP) {
                    curData.expired_at = curData.expired_at + this.user.timestamp
                }
                const relatedList = _.cloneDeep(this.tableList.filter(item => {
                    return !item.isAggregate
                        && relatedActions.includes(item.id)
                        && !item.related_resource_types.every(sub => sub.empty)
                }))

                if (relatedList.length > 0) {
                    relatedList.forEach(item => {
                        if (!item.policy_id) {
                            item.expired_at = item.expired_at + this.user.timestamp
                        }
                        delete item.policy_id
                        item.related_resource_types.forEach(resItem => {
                            resItem.condition.forEach(conditionItem => {
                                conditionItem.instances = conditionItem.instance || []
                                conditionItem.attributes = conditionItem.attribute || []
                                delete conditionItem.instance
                                delete conditionItem.attribute
                            })
                        })
                    })
                }
                try {
                    const res = await this.$store.dispatch('permApply/getRelatedPolicy', {
                        source_policy: curData,
                        system_id: this.systemId,
                        target_policies: relatedList
                    })
                    this.handleRelatedAction(res.data)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.sliderLoading = false
                }
            },

            /**
             *new Policy() 第三个参数会影响@/components/choose-ip/view中是否可移除的disabled
             * 具体体现在instance.js文件initPath方法中
             */
            handleRelatedAction (payload) {
                if (payload.length < 1) {
                    return
                }

                payload.forEach(item => {
                    const curIndex = this.tableList.findIndex(sub => sub.id === item.id)
                    if (curIndex > -1) {
                        this.needEmitFlag = true
                        const inOriginalList = !!this.originalList.filter(
                            original => String(original.id) === String(item.id)
                        ).length
                        item.expired_at = item.expired_at - this.user.timestamp
                        this.tableList.splice(
                            curIndex,
                            1,
                            new Policy({ ...item, tag: 'add', isShowRelatedText: true, inOriginalList }, '', false)
                        )
                    }
                })
            },

            async handleResourceSumit () {
                const conditionData = this.$refs.renderResourceRef.handleGetValue()
                const { isEmpty, data } = conditionData
                if (isEmpty) {
                    return
                }

                const resItem = this.tableList[this.curIndex].related_resource_types[this.curResIndex]
                const isConditionEmpty = data.length === 1 && data[0] === 'none'
                if (isConditionEmpty) {
                    resItem.condition = ['none']
                    resItem.isLimitExceeded = false
                } else {
                    const { isMainAction, related_actions } = this.tableList[this.curIndex]
                    // 如果为主操作
                    if (isMainAction) {
                        await this.handleMainActionSubmit(data, related_actions)
                    }
                    resItem.condition = data
                    resItem.isError = false
                }

                window.changeAlert = false
                this.resourceInstanceSidesliderTitle = ''
                this.isShowResourceInstanceSideslider = false

                if (!isConditionEmpty && resItem.isLimitExceeded) {
                    let newResourceCount = 0
                    const conditionList = resItem.condition
                    conditionList.forEach(item => {
                        item.instance.forEach(instanceItem => {
                            instanceItem.paths.forEach(v => {
                                // 是否带有下一层级的无限制
                                const isHasNoLimit = v.some(({ id }) => id === '*')
                                const isDisabled = v.some(_ => !!_.disabled)
                                if (!isHasNoLimit && !isDisabled) {
                                    ++newResourceCount
                                }
                            })
                        })
                    })
                    console.warn('newResourceCount: ' + newResourceCount)
                    if (newResourceCount <= RESOURCE_MAX_LEN) {
                        resItem.isLimitExceeded = false
                    }
                }

                this.curIndex = -1
                this.curResIndex = -1

                // 主操作的实例映射到了具体的依赖操作上，需更新到父级的缓存数据中
                if (this.needEmitFlag) {
                    this.$emit('on-realted-change', this.tableList)
                }
            },

            handleResourcePreview () {
                const { system_id, type, name } = this.tableList[this.curIndex].related_resource_types[this.curResIndex]
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

            handlerConditionMouseleave (payload) {
                payload.canPaste = false
            },

            handlerOnView (payload, item, itemIndex) {
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
                                system_id: this.systemId,
                                id: item.id
                            })
                        }
                    }
                })
                actions.unshift({
                    system_id: this.systemId,
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

            handlerOnPaste (payload, row, content) {
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

            handlerOnBatchPaste (payload, content, index, subIndex) {
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
                                item.related_resource_types.forEach(resItem => {
                                    if (`${resItem.system_id}${resItem.type}` === this.curCopyKey) {
                                        resItem.condition = []
                                        resItem.isError = false
                                    }
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
                                    item.related_resource_types.forEach(resItem => {
                                        if (`${resItem.system_id}${resItem.type}` === `${curPasteData.resource_type.system_id}${curPasteData.resource_type.type}`) {
                                            resItem.condition = curPasteData.resource_type.condition.map(conditionItem => new Condition(conditionItem, '', 'add'))
                                            resItem.isError = false
                                        }
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
                            item.related_resource_types.forEach(subItem => {
                                if (`${subItem.system_id}${subItem.type}` === this.curCopyKey) {
                                    subItem.condition = _.cloneDeep(tempCurData)
                                    subItem.isError = false
                                }
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

            handlePreviewDialogClose () {
                this.previewDialogTitle = ''
                this.isShowPreviewDialog = false
            },

            resetDataAfterClose () {
                this.curIndex = -1
                this.curResIndex = -1
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

            handleExpiredToggle (value, row) {
                if (!value) {
                    row.isShowCustom = false
                    row.customValue = ''
                }
            },

            handleExpiredSelect (value, option, row) {
                row.isShowCustom = false
                row.customValue = ''
                const curSelected = this.durationList.find(item => item.id === value)
                row.expired_display = curSelected.name
            },

            handleBlur (value, e, row) {
                row.isShowCustom = false
                row.customValue = ''
            },

            handleInput (value, e, row) {
                const flag = /^([1-9]|[1-9][0-9]|[1-2][0-9][0-9]|[3][0-5][0-9]|(360|361|363|362|364|365))$/.test(value)
                if (!flag) {
                    if (parseInt(value, 10) > 365) {
                        setTimeout(() => {
                            row.customValue = 365
                        }, 100)
                    } else {
                        setTimeout(() => {
                            row.customValue = ''
                        }, 100)
                    }
                }
            },

            handleEnter (value, e, row) {
                if (value === '') {
                    return
                }
                row.isShowCustom = false
                row.customValue = Number(value)
                row.expired_at = ''
                row.expired_display = `${value} ${this.$t(`m.common['天']`)}`
                this.$refs[`${row.id}&expiredAtRef`] && this.$refs[`${row.id}&expiredAtRef`].close()
            },

            handleGetValue () {
                // flag：提交时校验标识
                let flag = false
                if (this.tableList.length < 1) {
                    flag = true
                    return {
                        flag,
                        actions: [],
                        aggregations: []
                    }
                }
                const actionList = []
                const aggregations = []
                this.tableList.forEach(item => {
                    let tempExpiredAt = ''
                    if (item.expired_at === '' && item.expired_display) {
                        tempExpiredAt = parseInt(item.expired_display, 10) * 24 * 3600
                    }
                    if (!item.isAggregate) {
                        const { type, id, name, environment, description, policy_id, isNew } = item
                        const relatedResourceTypes = []
                        if (item.related_resource_types.length > 0) {
                            item.related_resource_types.forEach(resItem => {
                                let newResourceCount = 0
                                if (resItem.empty) {
                                    resItem.isError = true
                                    flag = true
                                }
                                const conditionList = (resItem.condition.length > 0 && !resItem.empty)
                                    ? resItem.condition.map(conItem => {
                                        const { id, instance, attribute } = conItem
                                        const attributeList = (attribute && attribute.length > 0)
                                            ? attribute.map(({ id, name, values }) => ({ id, name, values }))
                                            : []

                                        const instanceList = (instance && instance.length > 0)
                                            ? instance.map(({ name, type, paths }) => {
                                                const tempPath = _.cloneDeep(paths)
                                                tempPath.forEach(pathItem => {
                                                    // 是否带有下一层级的无限制
                                                    const isHasNoLimit = pathItem.some(({ id }) => id === '*')
                                                    const isDisabled = pathItem.some(_ => !!_.disabled)
                                                    if (!isHasNoLimit && !isDisabled) {
                                                        ++newResourceCount
                                                    }
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
                                console.warn('newResourceCount: ' + newResourceCount)
                                if (newResourceCount > RESOURCE_MAX_LEN) {
                                    resItem.isLimitExceeded = true
                                    flag = true
                                }
                                relatedResourceTypes.push({
                                    type: resItem.type,
                                    system_id: resItem.system_id,
                                    name: resItem.name,
                                    condition: conditionList.filter(
                                        item => item.instances.length > 0 || item.attributes.length > 0
                                    )
                                })
                            })
                            // 强制刷新下
                            item.related_resource_types = _.cloneDeep(item.related_resource_types)
                        }
                        const params = {
                            type,
                            name,
                            id,
                            description,
                            related_resource_types: relatedResourceTypes,
                            environment,
                            policy_id,
                            expired_at: item.expired_at === '' ? tempExpiredAt : Number(item.expired_at)
                        }
                        if ((isNew || item.isExpired) && params.expired_at !== PERMANENT_TIMESTAMP) {
                            // 说明显示了 取消续期 按钮，即选择续期时间的下拉框已经选择了选择具体的续期时间，所以过期时间是选择的那个续期时间加上时间戳
                            // 如果没有显示 取消续期 按钮，那么就是显示的续期按钮，这时没有选择具体的续期时间因此过期时间还是之前的，不变
                            if (!item.isShowRenewal) {
                                params.expired_at = params.expired_at + this.user.timestamp
                            }
                        }
                        if (params.policy_id === '') {
                            delete params.policy_id
                        }
                        actionList.push(_.cloneDeep(params))
                    } else {
                        const { actions, aggregateResourceType, instances } = item
                        if (instances.length < 1) {
                            item.isError = true
                            flag = true
                        } else {
                            const params = {
                                actions,
                                expired_at: item.expired_at === '' ? tempExpiredAt : Number(item.expired_at),
                                aggregate_resource_type: {
                                    id: aggregateResourceType.id,
                                    system_id: aggregateResourceType.system_id,
                                    instances
                                }
                            }
                            if (params.expired_at !== PERMANENT_TIMESTAMP) {
                                params.expired_at = params.expired_at + this.user.timestamp
                            }
                            aggregations.push(params)
                        }
                    }
                })
                return {
                    flag,
                    actions: actionList,
                    aggregations
                }
            }
        }
    }
</script>

<style>
    @import './resource-instance-table.css';
</style>
