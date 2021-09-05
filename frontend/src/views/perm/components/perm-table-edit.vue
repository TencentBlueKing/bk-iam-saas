<template>
    <div class="iam-perm-edit-table" v-bkloading="{ isLoading: loading, opacity: 1 }">
        <bk-table
            v-if="!loading"
            :data="tableList"
            border
            :cell-class-name="getCellClass">
            <bk-table-column :label="$t(`m.common['操作']`)">
                <template slot-scope="{ row }">
                    <span :title="row.name">{{ row.name }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" width="491">
                <template slot-scope="{ row }">
                    <template v-if="!row.isEmpty">
                        <p class="related-resource-item"
                            v-for="item in row.related_resource_types"
                            :key="item.type">
                            <render-resource-popover
                                :key="item.type"
                                :data="item.condition"
                                :value="`${item.name}：${item.value}`"
                                :max-width="380"
                                @on-view="handleViewResource(row)" />
                        </p>
                    </template>
                    <template v-else>
                        {{ $t(`m.common['无需关联实例']`) }}
                    </template>
                    <Icon
                        type="detail-new"
                        class="view-icon"
                        :title="$t(`m.common['详情']`)"
                        v-if="isShowPreview(row)"
                        @click.stop="handleViewResource(row)" />
                </template>
            </bk-table-column>
            <bk-table-column prop="expired_dis" :label="$t(`m.common['到期时间']`)"></bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)">
                <template slot-scope="{ row }">
                    <bk-button text @click="handleDelete(row)">{{ $t(`m.common['删除']`) }}</bk-button>
                </template>
            </bk-table-column>
        </bk-table>

        <delete-dialog
            :show.sync="deleteDialog.visible"
            :loading="deleteDialog.loading"
            :title="deleteDialog.title"
            :sub-title="deleteDialog.subTitle"
            @on-after-leave="handleAfterDeleteLeave"
            @on-cancel="hideCancelDelete"
            @on-sumbit="handleSumbitDelete" />

        <delete-dialog
            :show.sync="confirmDialog.visible"
            :loading="confirmDialog.loading"
            :title="confirmDialog.title"
            :sub-title="confirmDialog.subTitle"
            @on-after-leave="handleAfterResDeleteLeave"
            @on-cancel="hideCancelResDelete"
            @on-sumbit="handleSumbitResDelete" />

        <bk-sideslider
            :is-show="isShowSideslider"
            :title="sidesliderTitle"
            :width="725"
            quick-close
            @update:isShow="handleResourceCancel">
            <div slot="header" class="iam-my-custom-perm-silder-header">
                <span>{{ sidesliderTitle}}</span>
                <div class="action-wrapper" v-if="canOperate">
                    <bk-button
                        text
                        theme="primary"
                        size="small"
                        style="padding: 0;"
                        :disabled="batchDisabled"
                        v-if="isBatchDelete"
                        @click="handleBatchDelete">{{ $t(`m.common['批量删除实例权限']`) }}</bk-button>
                    <template v-else>
                        <iam-popover-confirm
                            :title="$t(`m.info['确定删除实例权限']`)"
                            :disabled="disabled"
                            :confirm-handler="handleDeletePerm">
                            <bk-button
                                theme="primary"
                                :disabled="disabled">
                                {{ $t(`m.common['删除']`) }}
                            </bk-button>
                        </iam-popover-confirm>
                        <bk-button style="margin-left: 10px;" @click="handleCancel">
                            {{ $t(`m.common['取消']`) }}
                        </bk-button>
                    </template>
                </div>
            </div>
            <div slot="content">
                <component
                    :is="renderDetailCom"
                    :data="previewData"
                    :can-edit="!isBatchDelete"
                    ref="detailComRef"
                    @tab-change="handleTabChange"
                    @on-change="handleChange" />
            </div>
        </bk-sideslider>
    </div>
</template>
<script>
    import _ from 'lodash'
    import IamPopoverConfirm from '@/components/iam-popover-confirm'
    import DeleteDialog from '@/components/iam-confirm-dialog/index.vue'
    import RenderResourcePopover from '@/components/iam-view-resource-popover'
    import PermPolicy from '@/model/my-perm-policy'
    import { leaveConfirm } from '@/common/leave-confirm'
    import RenderDetail from './render-detail-edit'

    export default {
        name: '',
        components: {
            IamPopoverConfirm,
            RenderDetail,
            RenderResourcePopover,
            DeleteDialog
        },
        props: {
            systemId: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                tableList: [],
                policyCountMap: {},
                initRequestQueue: ['permTable'],
                previewData: [],
                curId: '',
                curPolicyId: '',
                renderDetailCom: 'RenderDetail',
                isShowSideslider: false,
                curDeleteIds: [],

                deleteDialog: {
                    visible: false,
                    title: this.$t(`m.dialog['确认删除']`),
                    subTitle: '',
                    loading: false
                },

                confirmDialog: {
                    visible: false,
                    title: this.$t(`m.dialog['确认删除']`),
                    subTitle: '',
                    loading: false
                },

                sidesliderTitle: '',

                isBatchDelete: true,
                batchDisabled: false,
                disabled: true,
                canOperate: true,
                cellStyle: {
                    '-webkit-line-clamp': 'unset'
                }
            }
        },
        computed: {
            loading () {
                return this.initRequestQueue.length > 0
            },
            isShowPreview () {
                return (payload) => {
                    return !payload.isEmpty && payload.policy_id !== ''
                }
            }
        },
        watch: {
            systemId: {
                handler (value) {
                    if (value !== '') {
                        this.initRequestQueue = ['permTable']
                        this.fetchData(value)
                    } else {
                        this.renderDetailCom = 'RenderDetail'
                        this.initRequestQueue = []
                        this.tableList = []
                        this.policyCountMap = {}
                    }
                },
                immediate: true
            }
        },
        methods: {
            async fetchData (payload) {
                try {
                    const res = await this.$store.dispatch('permApply/getPolicies', { system_id: payload })
                    this.tableList = res.data.map(item => new PermPolicy(item))
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.initRequestQueue.shift()
                }
            },

            getCellClass ({ row, column, rowIndex, columnIndex }) {
                if (columnIndex === 1) {
                    return 'iam-perm-table-cell-cls'
                }
                return ''
            },

            handleRefreshData () {
                this.initRequestQueue = ['permTable']
                this.fetchData(this.systemId)
            },

            handleBatchDelete () {
                window.changeAlert = true
                this.isBatchDelete = false
            },

            handleTabChange (payload) {
                const { disabled, canDelete } = payload
                this.batchDisabled = disabled
                this.canOperate = canDelete
            },

            handleChange () {
                const data = this.$refs.detailComRef.handleGetValue()
                this.disabled = data.ids.length < 1 && data.condition.length < 1
            },

            async handleDeletePerm (payload) {
                const data = this.$refs.detailComRef.handleGetValue()
                const { ids, condition, type } = data
                const params = {
                    id: this.curPolicyId,
                    data: {
                        system_id: data.system_id,
                        type: type,
                        ids,
                        condition
                    }
                }
                try {
                    await this.$store.dispatch('permApply/updatePerm', params)
                    window.changeAlert = false
                    this.isShowSideslider = false
                    this.resetDataAfterClose()
                    this.messageSuccess(this.$t(`m.info['删除成功']`), 2000)
                    this.handleRefreshData()
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    payload && payload.hide()
                }
            },

            handleCancel () {
                this.isBatchDelete = true
            },

            handleResourceCancel () {
                let cancelHandler = Promise.resolve()
                if (window.changeAlert) {
                    cancelHandler = leaveConfirm()
                }
                cancelHandler.then(() => {
                    this.isShowSideslider = false
                    this.resetDataAfterClose()
                }, _ => _)
            },

            resetDataAfterClose () {
                this.sidesliderTitle = ''
                this.previewData = []
                this.canOperate = true
                this.batchDisabled = false
                this.disabled = true
                this.isBatchDelete = true
                this.curId = ''
                this.curPolicyId = ''
            },

            handleAfterDeleteLeave () {
                this.deleteDialog.subTitle = ''
                this.curDeleteIds = []
            },

            hideCancelDelete () {
                this.deleteDialog.visible = false
            },

            handleViewCondition (row) {
                console.warn('view')
            },

            handleViewResource (payload) {
                this.curId = payload.id
                this.curPolicyId = payload.policy_id
                const params = []
                if (payload.related_resource_types.length > 0) {
                    payload.related_resource_types.forEach(item => {
                        const { name, type, condition } = item
                        params.push({
                            name: type,
                            label: `${name} ${this.$t(`m.common['实例']`)}`,
                            tabType: 'resource',
                            data: condition,
                            systemId: item.system_id
                        })
                    })
                }
                this.previewData = _.cloneDeep(params)

                if (this.previewData[0].tabType === 'relate') {
                    this.canOperate = false
                }
                if (this.previewData[0].tabType === 'resource' && (this.previewData[0].data.length < 1 || this.previewData[0].data.every(item => !item.instance || item.instance.length < 1))) {
                    this.batchDisabled = true
                }
                this.sidesliderTitle = `${this.$t(`m.common['操作']`)}【${payload.name}】${this.$t(`m.common['的资源实例']`)}`
                window.changeAlert = 'iamSidesider'
                this.isShowSideslider = true
            },

            handleDelete (payload) {
                this.curDeleteIds.splice(0, this.curDeleteIds.length, ...[payload.policy_id])
                this.deleteDialog.subTitle = `${this.$t(`m.dialog['将删除']`)}【${payload.name}】权限`
                this.deleteDialog.visible = true
            },

            handleSumbitResDelete () {},

            hideCancelResDelete () {
                this.confirmDialog.visible = false
            },

            handleAfterResDeleteLeave () {
                this.confirmDialog.subTitle = ''
            },

            async handleSumbitDelete () {
                this.deleteDialog.loading = true
                try {
                    await this.$store.dispatch('permApply/deletePerm', { policyIds: this.curDeleteIds, systemId: this.systemId })
                    const index = this.tableList.findIndex(item => item.policy_id === this.curDeleteIds[0])
                    if (index > -1) {
                        this.tableList.splice(index, 1)
                    }
                    this.messageSuccess(this.$t(`m.info['删除成功']`), 2000)
                    this.$emit('after-delete', this.tableList.length)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.deleteDialog.loading = false
                    this.deleteDialog.visible = false
                }
            }
        }
    }
</script>
<style lang='postcss'>
    .iam-perm-edit-table {
        min-height: 101px;
        .bk-table-enable-row-hover .bk-table-body tr:hover > td {
            background-color: #fff;
        }
        .bk-table {
            border-right: none;
            border-bottom: none;
            .bk-table-header-wrapper {
                .cell {
                    padding-left: 20px !important;
                }
            }
            .bk-table-body-wrapper {
                .cell {
                    padding: 20px !important;
                    .view-icon {
                        display: none;
                        position: absolute;
                        top: 50%;
                        right: 10px;
                        transform: translate(0, -50%);
                        font-size: 18px;
                        cursor: pointer;
                    }
                    &:hover {
                        .view-icon {
                            display: inline-block;
                            color: #3a84ff;
                        }
                    }
                }
            }
            tr:hover {
                background-color: #fff;
            }
        }

        .iam-my-custom-perm-silder-header {
            display: flex;
            justify-content: space-between;
            .action-wrapper {
                margin-right: 30px;
                font-weight: normal;
            }
        }
    }
</style>
