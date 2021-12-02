<template>
    <div class="iam-user-group-perm-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="!isLoading && !isEmpty">
            <render-perm-item
                data-test-id="myPerm_list_permItem"
                expanded="true"
                title="用户组权限交接"
                @on-expanded="handleExpanded">
                <div style="min-height: 60px;">
                    <bk-table
                        :data="personalGroupList"
                        size="small"
                        :class="{ 'set-border': tableLoading }"
                        ext-cls="system-access-table"
                        :pagination="pagination"
                        v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
                        <bk-table-column type="selection" align="center"></bk-table-column>
                        <bk-table-column :label="$t(`m.userGroup['用户组名']`)" :min-width="220">
                            <template slot-scope="{ row }">
                                {{row.name}}
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t(`m.approvalProcess['来源']`)">
                            <template slot-scope="{ row }">
                                <span :title="row.cost_time">{{ row.cost_time | getDuration }}</span>
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
                    </bk-table>
                </div>
            </render-perm-item>
        </template>
        <template v-if="!isLoading && isEmpty">
            <div class="empty-wrapper">
                <iam-svg />
                <p class="text">{{ $t(`m.common['暂无数据']`) }}</p>
            </div>
        </template>
    </div>
</template>
<script>
    import RenderPermItem from './components/render-perm-item.vue'

    export default {
        name: '',
        components: {
            RenderPermItem
        },
        props: {
            id: {
                type: [String, Number],
                default: ''
            },
            mode: {
                type: String,
                default: 'edit'
            }
        },
        data () {
            return {
                groupId: '',
                isLoading: false,
                groupSystemList: [],
                authorizationData: {},
                removingSingle: false,
                isPermTemplateDetail: false,
                role: '',
                personalGroupList: [], // 用户组数据
                systemList: [], // 权限的所有系统列表
                groupList: [] // 用户组数据
            }
        },
        computed: {
        },
        methods: {
            fetchPageData () {
                this.fetchData()
            },
            async fetchData () {
                this.isLoading = true
                try {
                    const [res1, res2, res3, res4] = await Promise.all([
                        this.$store.dispatch('perm/getPersonalGroups'),
                        this.$store.dispatch('permApply/getHasPermSystem')
                        // this.$store.dispatch('permApply/getPolicies', {
                        //     system_id: 123
                        // })
                    ])
                    const personalGroupList = res1.data.slice(0, 5) || []
                    this.personalGroupList.splice(0, this.personalGroupList.length, ...personalGroupList)

                    const systemList = res2.data || []
                    this.systemList.splice(0, this.systemList.length, ...systemList)

                    this.isEmpty = personalGroupList.length < 1 && systemList.length < 1
                    // this.groupList = res3.data || []
                    console.log('this.personalGroupList', this.personalGroupList)
                    console.log('this.systemList', this.systemList)
                    console.log('res3', res3)
                    console.log('res4', res4)
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
                    this.isLoading = false
                }
            },
            handleExpanded () {
                console.log('请求所有数据')
            }

        }
    }
</script>
<style lang="postcss">
    .iam-user-group-perm-wrapper {
        position: relative;
        min-height: calc(100vh - 145px);
        .iam-perm-ext-cls {
            margin-top: 10px;
        }
        .iam-perm-ext-reset-cls {
            margin-bottom: 20px;
        }
        .empty-wrapper {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            img {
                width: 160px;
            }
            .text {
                position: relative;
                top: -30px;
                font-size: 12px;
                color: #979ba5;
                text-align: center;
            }
        }
        .info-wrapper {
                display: flex;
                justify-content: flex-end;
                line-height: 24px;
                .tips,
                .text {
                    line-height: 20px;
                    font-size: 12px;
                }
            }
    }
</style>
