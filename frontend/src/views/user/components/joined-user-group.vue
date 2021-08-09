<template>
    <div class="iam-joined-user-group-wrapper" v-bkloading="{ isLoading: pageLoading, opacity: 1 }">
        <div>
            <bk-table
                :data="curPageData"
                :size="'small'"
                v-if="!pageLoading"
                :pagination="pageConf"
                :ext-cls="tableLoading ? 'is-be-loading' : ''"
                v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
                @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange">
                <bk-table-column :label="$t(`m.userGroup['用户组名']`)">
                    <template slot-scope="{ row }">
                        <span class="user-group-name" :title="row.name" @click="goDetail(row)">{{ row.name }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.common['到期时间']`)" prop="expired_at_display"></bk-table-column>
                <bk-table-column :label="$t(`m.perm['加入用户组的时间']`)">
                    <template slot-scope="{ row }">
                        <span :title="row.created_time">{{ row.created_time.replace(/T/, ' ') }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.common['描述']`)">
                    <template slot-scope="{ row }">
                        <span :title="row.description !== '' ? row.description : ''">
                            {{ row.description !== '' ? row.description : '--'}}
                        </span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.perm['加入方式']`)">
                    <template slot-scope="props">
                        <span v-if="props.row.department_id === 0">{{ $t(`m.perm['直接加入']`) }}</span>
                        <span v-else :title="`${$t(`m.perm['通过组织加入']`)}：${props.row.department_name}`">
                            {{ $t(`m.perm['通过组织加入']`) }}：{{ props.row.department_name }}
                        </span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.common['操作']`)" width="200">
                    <template slot-scope="props">
                        <bk-button disabled text v-if="props.row.department_id !== 0">
                            <span :title="$t(`m.perm['通过组织加入的组无法退出']`)">{{ $t(`m.common['退出']`) }}</span>
                        </bk-button>
                        <bk-button v-else theme="primary" text @click="showQuitTemplates(props.row)">
                            {{ $t(`m.common['退出']`) }}
                        </bk-button>
                    </template>
                </bk-table-column>
            </bk-table>
        </div>

        <delete-dialog
            :show.sync="deleteDialogConf.visiable"
            :loading="deleteDialogConf.loading"
            :title="$t(`m.dialog['确认退出']`)"
            :sub-title="deleteDialogConf.msg"
            @on-after-leave="afterLeaveDelete"
            @on-cancel="cancelDelete"
            @on-sumbit="confirmDelete" />

        <render-perm-sideslider
            :show="isShowPermSidesilder"
            :name="curGroupName"
            :group-id="curGroupId"
            @animation-end="handleAnimationEnd" />
    </div>
</template>
<script>
    import { mapGetters } from 'vuex'
    import DeleteDialog from '@/components/iam-confirm-dialog'
    import RenderPermSideslider from '../../perm/components/render-group-perm-sideslider'

    export default {
        name: '',
        components: {
            DeleteDialog,
            RenderPermSideslider
        },
        props: {
            data: {
                type: Object,
                default: () => {
                    return {}
                }
            }
        },
        data () {
            return {
                dataList: [],
                pageConf: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                curPageData: [],
                deleteDialogConf: {
                    visiable: false,
                    loading: false,
                    row: {},
                    msg: ''
                },
                tableLoading: false,

                isShowPermSidesilder: false,
                curGroupName: '',
                curGroupId: '',

                pageLoading: false
            }
        },
        computed: {
            ...mapGetters(['user'])
        },
        async created () {
            await this.fetchPermGroups(false, true)
        },
        methods: {
            /**
             * handleAnimationEnd
             */
            handleAnimationEnd () {
                this.curGroupName = ''
                this.curGroupId = ''
                this.isShowPermSidesilder = false
            },

            /**
             * 获取权限模板列表
             */
            async fetchPermGroups (isTableLoading = false, isPageLoading = false) {
                this.tableLoading = isTableLoading
                this.pageLoading = isPageLoading
                const { type } = this.data
                try {
                    const res = await this.$store.dispatch('perm/getPermGroups', {
                        subjectType: type === 'user' ? type : 'department',
                        subjectId: type === 'user' ? this.data.username : this.data.id
                    })
                    this.dataList.splice(0, this.dataList.length, ...(res.data || []))
                    this.initPageConf()
                    this.curPageData = this.getDataByPage(this.pageConf.current)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.tableLoading = false
                    this.pageLoading = false
                }
            },

            /**
             * initPageConf
             */
            initPageConf () {
                this.pageConf.current = 1
                const total = this.dataList.length
                this.pageConf.count = total
            },

            /**
             * handlePageChange
             */
            handlePageChange (page = 1) {
                this.pageConf.current = page
                const data = this.getDataByPage(page)
                this.curPageData.splice(0, this.curPageData.length, ...data)
            },

            /**
             * getDataByPage
             */
            getDataByPage (page) {
                if (!page) {
                    this.pageConf.current = page = 1
                }
                let startIndex = (page - 1) * this.pageConf.limit
                let endIndex = page * this.pageConf.limit
                if (startIndex < 0) {
                    startIndex = 0
                }
                if (endIndex > this.dataList.length) {
                    endIndex = this.dataList.length
                }
                return this.dataList.slice(startIndex, endIndex)
            },

            /**
             * handlePageLimitChange
             */
            handlePageLimitChange (currentLimit, prevLimit) {
                this.pageConf.limit = currentLimit
                this.pageConf.current = 1
                this.handlePageChange(this.pageConf.current)
            },

            /**
             * goDetail
             */
            goDetail (row) {
                this.curGroupName = row.name
                this.curGroupId = row.id
                this.isShowPermSidesilder = true
            },

            /**
             * showQuitTemplates
             */
            showQuitTemplates (row) {
                this.deleteDialogConf.visiable = true
                this.deleteDialogConf.row = Object.assign({}, row)
                this.deleteDialogConf.msg = `${this.$t(`m.common['退出']`)}【${row.name}】，${this.$t(`m.info['将不再继承该组的权限']`)}。`
            },

            /**
             * confirmDelete
             */
            async confirmDelete () {
                this.deleteDialogConf.loading = true
                const { type } = this.data
                try {
                    await this.$store.dispatch('perm/quitGroupTemplates', {
                        subjectType: type === 'user' ? type : 'department',
                        subjectId: type === 'user' ? this.data.username : this.data.id,
                        type: 'group',
                        id: this.deleteDialogConf.row.id
                    })
                    this.cancelDelete()
                    this.messageSuccess(this.$t(`m.info['退出成功']`), 2000)
                    await this.fetchPermGroups(true)
                } catch (e) {
                    this.deleteDialogConf.loading = false
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * cancelDelete
             */
            cancelDelete () {
                this.deleteDialogConf.visiable = false
            },

            /**
             * afterLeaveDelete
             */
            afterLeaveDelete () {
                this.deleteDialogConf.row = Object.assign({}, {})
                this.deleteDialogConf.msg = ''
                this.deleteDialogConf.loading = false
            }
        }
    }
</script>
<style lang="postcss">
    .iam-joined-user-group-wrapper {
        height: calc(100vh - 204px);
        .bk-table {
            border-right: none;
            border-bottom: none;
            &.is-be-loading {
                border-bottom: 1px solid #dfe0e5;
            }
            .user-group-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
        }
    }
</style>
