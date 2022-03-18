<template>
    <div class="iam-grading-admin-wrapper">
        <!-- <bk-alert type="info" style="margin-bottom: 16px;">
            <div slot="title">
                {{ $t(`m.grading['页面提示']`) }}
                <span class="detail-link" @click="handleOpenMoreLink">{{ $t(`m.common['更多详情']`) }}</span>
            </div>
        </bk-alert> -->
        <render-search>
            <bk-button theme="primary" @click="handleCreate" data-test-id="grading_btn_create">
                {{ isStaff ? $t(`m.common['申请新建']`) : $t(`m.common['新建']`) }}
            </bk-button>
            <bk-link class="AdminLink" theme="primary" @click="showImgDialog">
                <span class="linkText">{{ $t('m.common["什么是分级管理员"]') }}</span>
            </bk-link>
            <div slot="right">
                <bk-input
                    :placeholder="$t(`m.grading['搜索提示']`)"
                    clearable
                    style="width: 420px;"
                    right-icon="bk-icon icon-search"
                    v-model="searchValue"
                    @enter="handleSearch">
                </bk-input>
            </div>
        </render-search>
        <bk-table
            :data="tableList"
            size="small"
            :class="{ 'set-border': tableLoading }"
            ext-cls="grading-admin-table"
            :pagination="pagination"
            @page-change="handlePageChange"
            @page-limit-change="handleLimitChange"
            v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
            <bk-table-column :label="$t(`m.grading['分级管理员名称']`)">
                <template slot-scope="{ row }">
                    <span class="grading-admin-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.grading['创建人']`)" prop="creator"></bk-table-column>
            <bk-table-column :label="$t(`m.common['创建时间']`)">
                <template slot-scope="{ row }">
                    <span :title="row.created_time">{{ row.created_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.grading['更新人']`)" prop="updater"></bk-table-column>
            <bk-table-column :label="$t(`m.grading['更新时间']`)">
                <template slot-scope="{ row }">
                    <span :title="row.updated_time">{{ row.updated_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['描述']`)">
                <template slot-scope="{ row }">
                    <span :title="row.description !== '' ? row.description : ''">{{ row.description || '--' }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)" width="150">
                <template slot-scope="{ row }">
                    <!-- <section>
                        <bk-button theme="primary" text @click="handleDropOut(row)">
                            {{ $t(`m.common['退出']`) }}
                        </bk-button>
                        <bk-button theme="primary" style="margin-left: 10px;" text @click="handleDelete(row)">
                            {{ $t(`m.common['删除']`) }}
                        </bk-button>
                    </section>
                    <bk-button theme="primary" text @click="handleApplyJoin(row)">
                        {{ $t(`m.myApply['申请加入']`) }}
                    </bk-button> -->
                    <bk-button theme="primary" text @click="handleCopy(row)">{{ $t(`m.grading['克隆']`) }}</bk-button>
                </template>
            </bk-table-column>
        </bk-table>

        <confirm-dialog
            :show.sync="isShowConfirmDialog"
            :loading="confirmLoading"
            :title="confirmDialogTitle"
            :sub-title="confirmDialogSubTitle"
            @on-after-leave="handleAfterLeave"
            @on-cancel="handleCancel"
            @on-sumbit="handleSumbit" />
        <apply-dialog
            :show.sync="isShowApplyDialog"
            :loading="applyLoading"
            :name="curName"
            @on-after-leave="handleAfterApplyLeave"
            @on-cancel="handleApplyCancel"
            @on-sumbit="handleApplySumbit" />
        <bk-dialog
            v-model="showImageDialog"
            :show-footer="noFooter"
            width="820"
            :position="{ top: 50 }"
            ext-cls="showImage">
            <h2>{{ $t('m.common["一"]') }}、{{ $t('m.common["什么是分级管理员"]') }}</h2>
            <p>{{ $t('m.common["分级管理员概念"]') }}</p>
            <img src="../../images/boot-page/one2x2.jpg" alt="" style="width:714px;height:263px">
            <h2>{{ $t('m.common["二"]') }}、{{ $t('m.common["如何使用分级管理员"]') }}</h2>
            <p>1. {{ $t('m.common["我的分级管理员 > 申请新建（已有分级管理员忽略）"]') }}</p>
            <img src="@/images/boot-page/two2x2.png" alt="" style="width:515px;height:208px">
            <p>2. {{ $t('m.common["点击右上角个人信息 > 切换管理员身份"]') }}</p>
            <img src="@/images/boot-page/three2x2.png" alt="" style="width:402px;height:203px">
            <p>3. {{ $t('m.common["点击左侧导航用户组 > 新建，创建用户组，设置权限和成员。"]') }}</p>
            <img src="@/images/boot-page/four2x3.png" alt="" style="width:715px;height:208px">
        </bk-dialog>
    </div>
</template>
<script>
    import { mapGetters } from 'vuex'
    import ConfirmDialog from '@/components/iam-confirm-dialog/index.vue'
    import { buildURLParams } from '@/common/url'
    import ApplyDialog from './components/apply-join-dialog'
    export default {
        name: '',
        components: {
            ConfirmDialog,
            ApplyDialog
        },
        data () {
            return {
                searchValue: '',
                isFilter: false,
                tableList: [],
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                currentBackup: 1,
                tableLoading: false,
                confirmLoading: false,
                confirmDialogTitle: '',
                confirmDialogSubTitle: '',
                isShowConfirmDialog: false,
                curOperateType: '',
                curId: -1,

                isShowApplyDialog: false,
                applyLoading: false,
                curName: '',
                showImageDialog: false,
                noFooter: false
            }
        },
        computed: {
            ...mapGetters(['user']),
            isStaff () {
                return this.user.role.type === 'staff'
            }
        },
        watch: {
            searchValue (newVal, oldVal) {
                if (newVal === '' && oldVal !== '' && this.isFilter) {
                    this.isFilter = false
                    this.resetPagination()
                    this.fetchGradingAdmin(true)
                }
            },
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
                if (currentQueryCache.name) {
                    this.searchValue = currentQueryCache.name
                }
                if (this.searchValue !== '') {
                    this.isFilter = true
                }
            }
        },
        methods: {
            showImgDialog () {
                this.showImageDialog = true
            },
            async fetchPageData () {
                await this.fetchGradingAdmin()
            },

            handleCopy (payload) {
                this.$router.push({
                    name: 'gradingAdminCreate',
                    params: {
                        id: payload.id
                    }
                })
            },

            handleOpenMoreLink () {
                window.open(`${window.PRODUCT_DOC_URL_PREFIX}/权限中心/产品白皮书/场景案例/GradingManager.md`)
            },

            refreshCurrentQuery () {
                const { limit, current } = this.pagination
                const queryParams = {
                    limit,
                    current
                }
                if (this.searchValue !== '') {
                    queryParams.name = this.searchValue
                }
                window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`)
                return queryParams
            },

            setCurrentQueryCache (payload) {
                window.localStorage.setItem('gradeManagerList', JSON.stringify(payload))
            },

            getCurrentQueryCache () {
                return JSON.parse(window.localStorage.getItem('gradeManagerList'))
            },

            async fetchGradingAdmin (isTableLoading = false) {
                this.tableLoading = isTableLoading
                this.setCurrentQueryCache(this.refreshCurrentQuery())
                try {
                    const res = await this.$store.dispatch('role/getRatingManagerList', {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        name: this.searchValue
                    })
                    this.pagination.count = res.data.count
                    this.tableList.splice(0, this.tableList.length, ...(res.data.results || []))
                    if (this.isStaff) {
                        this.$store.commit('setGuideShowByField', { field: 'role', flag: this.tableList.length > 0 })
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

            handleCreate () {
                this.$router.push({
                    name: 'gradingAdminCreate',
                    params: {
                        id: 0
                    }
                })
            },

            resetPagination () {
                this.pagination = Object.assign({}, {
                    current: 1,
                    count: 0,
                    limit: 10
                })
            },

            handleSearch () {
                if (this.searchValue === '') {
                    return
                }
                this.isFilter = true
                this.resetPagination()
                this.fetchGradingAdmin(true)
            },

            handleAfterApplyLeave () {
                this.curName = ''
            },

            handleApplyCancel () {
                this.isShowApplyDialog = false
            },

            handleApplySumbit () {},

            handleDropOut (payload) {
                this.curOperateType = 'drop'
                this.curId = payload.id
                this.confirmDialogTitle = this.$t(`m.dialog['确认退出']`)
                this.confirmDialogSubTitle = `${this.$t(`m.common['退出']`)}【${payload.name}】，${this.$t(`m.grading['退出提示']`)}`
                this.isShowConfirmDialog = true
            },

            handleDelete (payload) {
                this.curOperateType = 'delete'
                this.curId = payload.id
                this.confirmDialogTitle = this.$t(`m.dialog['确认删除']`)
                this.confirmDialogSubTitle = `${this.$t(`m.common['删除']`)}【${payload.name}】，${this.$t(`m.grading['删除提示']`)}`
                this.isShowConfirmDialog = true
            },

            handleApplyJoin (payload) {
                this.curName = payload.name
                this.isShowApplyDialog = true
            },

            async handleSumbit () {
                this.confirmLoading = true
                try {
                    await this.$store.dispatch('role/deleteRatingManager', { id: this.curId })
                    await this.$store.dispatch('roleList')
                    this.messageSuccess(this.$t(`m.info['退出成功']`), 2000)
                    this.isShowConfirmDialog = false
                    this.resetPagination()
                    this.fetchGradingAdmin(true)
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
                    this.confirmLoading = false
                }
            },

            handleAfterLeave () {
                this.confirmDialogTitle = ''
                this.confirmDialogSubTitle = ''
                this.curOperateType = ''
                this.curId = -1
            },

            handleCancel () {
                this.isShowConfirmDialog = false
            },

            handleView (payload) {
                window.localStorage.setItem('iam-header-name-cache', payload.name)
                this.$router.push({
                    name: 'gradingAdminDetail',
                    params: {
                        id: payload.id
                    }
                })
            },

            handlePageChange (page) {
                if (this.currentBackup === page) {
                    return
                }
                this.pagination.current = page
                this.fetchGradingAdmin(true)
            },

            handleLimitChange (currentLimit, prevLimit) {
                this.pagination.limit = currentLimit
                this.pagination.current = 1
                this.fetchGradingAdmin(true)
            }
        }
    }
</script>
<style lang="postcss">
    .iam-grading-admin-wrapper {
        .detail-link {
            color: #3a84ff;
            cursor: pointer;
            &:hover {
                color: #699df4;
            }
        }
        .grading-admin-table {
            margin-top: 16px;
            border-right: none;
            border-bottom: none;
            &.set-border {
                border-right: 1px solid #dfe0e5;
                border-bottom: 1px solid #dfe0e5;
            }
            .grading-admin-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
        }
    }
    .showImage {
            h2 {
                font-size: 16px;
                font-family: PingFangSC, PingFangSC-Medium;
                font-weight: 500;
                color: #63656e;
            }
            p {
                font-size: 14px;
                font-family: PingFangSC, PingFangSC-Regular;
                color: #63656e;
                margin-bottom: 15px;
            }
        }
    .AdminLink {
        margin-left: 10px;
    .linkText {
        font-size: 12px
         }
    }
</style>
