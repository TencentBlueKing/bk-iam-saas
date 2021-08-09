<template>
    <div class="iam-user-group-perm-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
        <bk-button theme="primary"
            style="margin-bottom: 16px;"
            v-if="!isLoading"
            @click="handleAddPerm">
            {{ $t(`m.common['添加权限']`) }}
        </bk-button>
        <bk-table
            :data="tableList"
            size="small"
            :ext-cls="tableLoading ? 'is-be-loading' : ''"
            :pagination="pagination"
            v-if="!isLoading"
            v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
            @page-change="pageChange"
            @page-limit-change="limitChange">
            <bk-table-column :label="$t(`m.permTemplate['模板名']`)">
                <template slot-scope="{ row }">
                    <span class="perm-template-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['所属系统']`)">
                <template slot-scope="{ row }">
                    <span :title="row.system.name">{{ row.system.name }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.perm['最近一次更新时间']`)">
                <template slot-scope="{ row }">
                    <span :title="row.updated_time">{{ row.updated_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)" width="200">
                <template slot-scope="{ row }">
                    <div>
                        <bk-button
                            theme="primary"
                            text
                            :disabled="row.is_latest"
                            @click="handleCheckUpdate(row)">
                            {{ row.is_latest ? $t(`m.permTemplate['最新版本']`) : $t(`m.permTemplate['检查更新']`) }}
                        </bk-button>
                        <bk-button style="margin-left: 10px;" theme="primary" text @click="handleDelete(row)">
                            {{ $t(`m.common['删除']`) }}
                        </bk-button>
                    </div>
                </template>
            </bk-table-column>
        </bk-table>

        <delete-dialog
            :show.sync="isShowDeleteDialog"
            :loading="deleteLoading"
            :title="$t(`m.dialog['确认删除']`)"
            :sub-title="deleteSubTitle"
            @on-after-leave="handleAfterDeleteLeave"
            @on-cancel="hideCancelDelete"
            @on-sumbit="handleSumbitDelete" />

        <perm-template-dialog
            :show.sync="isShowPermTemplateDialog"
            :name="permTemplateDialogTitleName"
            :loading="addPermLoading"
            :group-id="id"
            @on-cancel="handleCancelSelect"
            @on-sumbit="handleSumbitSelectTemplate" />

        <check-update-sideslider
            :is-show="isShowCheckUpdateSildeslider"
            :title="checkUpdateSildesliderTitle"
            :params="checkUpdateParams"
            @on-view="handleViewResource"
            @on-sync="handleSyncAfter"
            @animation-end="handleUpdateSildesliderClose" />

        <preview-resource-sideslider
            :is-show="isShowPreviewResourceSildeslider"
            :title="previewResourceSildesliderTitle"
            :params="previewResourceParams"
            @animation-end="handlePreviewSildesliderClose" />

        <render-perm-sideslider
            :show="isShowPermSidesilder"
            :title="permSidesilderTitle"
            :system-id="curSystemId"
            :template-id="curTemplateId"
            :version="curVersion"
            @on-view="handleOnView"
            @animation-end="handleAnimationEnd" />

        <bk-sideslider
            :is-show.sync="isShowSideslider"
            :title="sidesliderTitle"
            :width="880"
            :quick-close="true"
            @animation-end="handleViewResourceAnimationEnd">
            <div slot="content">
                <component :is="renderDetailCom" :data="previewData" />
            </div>
        </bk-sideslider>
    </div>
</template>
<script>
    import _ from 'lodash'
    import PermTemplateDialog from '@/components/render-perm-template-dialog'
    import DeleteDialog from '../common/iam-confirm-dialog'
    import CheckUpdateSideslider from '../components/check-update-sideslider'
    import PreviewResourceSideslider from '../components/preview-resource-sideslider'
    import RenderPermSideslider from '../components/render-perm-sideslider'
    import RenderDetail from '../common/render-detail'
    export default {
        name: '',
        components: {
            PermTemplateDialog,
            DeleteDialog,
            CheckUpdateSideslider,
            PreviewResourceSideslider,
            RenderPermSideslider,
            RenderDetail
        },
        props: {
            id: {
                type: [String, Number],
                default: ''
            }
        },
        data () {
            return {
                groupId: '',
                isLoading: false,
                tableList: [],
                allTableData: [],
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                currentBackup: 1,
                isShowDeleteDialog: false,
                deleteLoading: false,
                curId: 0,
                deleteSubTitle: '',

                isShowCheckUpdateSildeslider: false,
                checkUpdateSildesliderTitle: '',
                isShowPreviewResourceSildeslider: false,
                previewResourceSildesliderTitle: '',
                checkUpdateParams: {},
                previewResourceParams: [],

                isShowPermSidesilder: false,
                permSidesilderTitle: '',
                curSystemId: '',
                curTemplateId: '',
                curVersion: '',

                previewData: [],
                sidesliderTitle: '',
                isShowSideslider: false,
                renderDetailCom: 'RenderDetail',
                tableLoading: false,

                isShowPermTemplateDialog: false,
                addPermLoading: false,
                permTemplateDialogTitleName: ''
            }
        },
        watch: {
            id: {
                handler (value) {
                    this.groupId = value
                    this.handleInit()
                },
                immediate: true
            },
            'pagination.current' (value) {
                this.currentBackup = value
            }
        },
        methods: {
            async handleInit (isTableLoading = false) {
                this.isLoading = !isTableLoading
                this.tableLoading = isTableLoading
                this.$emit('on-init', true)
                try {
                    const res = await this.$store.dispatch('userGroup/getUserGroupTemplateList', { id: this.groupId })
                    this.pagination.count = res.data.length
                    this.allTableData.splice(0, this.allTableData.length, ...(res.data || []))
                    this.handleTableData()
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.isLoading = false
                    this.tableLoading = false
                    this.$emit('on-init', false)
                }
            },

            handleTableData () {
                const offset = (this.pagination.current - 1) * this.pagination.limit
                const list = this.allTableData.slice(offset, this.pagination.limit + offset)
                this.tableList.splice(0, this.tableList.length, ...list)
            },

            pageChange (page) {
                if (this.currentBackup === page) {
                    return
                }
                this.pagination.current = page
                this.handleTableData()
            },

            limitChange (currentLimit, prevLimit) {
                this.pagination.limit = currentLimit
                this.pagination.current = 1
                this.handleTableData()
            },

            handleAddPerm () {
                const name = window.localStorage.getItem('iam-header-name-cache')
                this.permTemplateDialogTitleName = name
                this.isShowPermTemplateDialog = true
            },

            async handleSumbitSelectTemplate (payload) {
                this.addPermLoading = true
                try {
                    await this.$store.dispatch('userGroup/addUserGroupPerm', {
                        id: this.id,
                        template_ids: payload.map(item => item.id)
                    })
                    this.messageSuccess(this.$t(`m.info['添加权限成功']`), 1000)
                    this.isShowPermTemplateDialog = false
                    this.handleInit(true)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.addPermLoading = false
                }
            },

            handleCancelSelect () {
                this.permTemplateDialogTitleName = ''
                this.isShowPermTemplateDialog = false
            },

            handleView (payload) {
                this.curSystemId = payload.system.id
                this.curTemplateId = payload.id
                this.curVersion = payload.version
                this.permSidesilderTitle = `${payload.name}(${payload.system.name})`
                this.isShowPermSidesilder = true
            },

            handleOnView (payload) {
                const { name, data } = payload
                this.sidesliderTitle = `${this.$t(`m.common['操作']`)}【${name}】${this.$t(`m.common['的资源实例']`)}`
                this.previewData = _.cloneDeep(data)
                this.isShowSideslider = true
            },

            handleAnimationEnd () {
                this.permSidesilderTitle = ''
                this.curSystemId = ''
                this.curTemplateId = ''
                this.curVersion = ''
                this.isShowPermSidesilder = false
            },

            handleViewResourceAnimationEnd () {
                this.previewData = []
                this.sidesliderTitle = ''
                this.isShowSideslider = false
            },

            handleCheckUpdate (payload) {
                this.checkUpdateParams = _.cloneDeep({
                    ...payload,
                    system_id: payload.system.id,
                    templateId: payload.id,
                    type: 'group',
                    id: this.id
                })
                this.checkUpdateSildesliderTitle = `${this.$t(`m.permTemplate['同步权限']`)}-${payload.name}`
                this.isShowCheckUpdateSildeslider = true
            },

            handleSyncAfter () {
                this.handleInit(true)
            },

            handleUpdateSildesliderClose () {
                this.checkUpdateParams = {}
                this.checkUpdateSildesliderTitle = ''
                this.isShowCheckUpdateSildeslider = false
            },

            handleViewResource (payload) {
                this.previewResourceParams = _.cloneDeep(payload.params)
                this.previewResourceSildesliderTitle = `${this.$t(`m.permTemplate['变更对比']`)}-${payload.action_name}`
                this.isShowPreviewResourceSildeslider = true
            },

            handlePreviewSildesliderClose () {
                this.previewResourceParams = []
                this.previewResourceSildesliderTitle = ''
                this.isShowPreviewResourceSildeslider = false
            },

            handleDelete (payload) {
                this.curId = payload.id
                this.deleteSubTitle = `${this.$t(`m.common['删除']`)}【${payload.name}】，${this.$t(`m.info['该组将不再继承该模板的权限']`)}。`
                this.isShowDeleteDialog = true
            },

            handleAfterDeleteLeave () {
                this.deleteSubTitle = ''
                this.curId = 0
            },

            hideCancelDelete () {
                this.isShowDeleteDialog = false
            },

            async handleSumbitDelete () {
                this.deleteLoading = true
                const params = {
                    id: this.curId,
                    members: [
                        {
                            type: 'group',
                            id: this.groupId
                        }
                    ]
                }
                try {
                    await this.$store.dispatch('permTemplate/deleteTemplateMember', params)
                    this.messageSuccess(this.$t(`m.info['删除成功']`), 2000)
                    this.isShowDeleteDialog = false
                    const curDeleteIndex = this.allTableData.findIndex(item => item.id === this.curId)
                    this.allTableData.splice(curDeleteIndex, 1)
                    this.pagination.current = 1
                    this.handleTableData()
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.deleteLoading = false
                }
            }
        }
    }
</script>
<style lang="postcss">
    .iam-user-group-perm-wrapper {
        position: relative;
        min-height: calc(100vh - 145px);
        .bk-table {
            border-right: none;
            border-bottom: none;
            &.is-be-loading {
                border-bottom: 1px solid #dfe0e5;
            }
            .perm-template-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
        }
    }
</style>
