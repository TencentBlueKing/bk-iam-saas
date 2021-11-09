<template>
    <div class="iam-custom-perm-wrapper" v-bkloading="{ isLoading: pageLoading, opacity: 1 }">
        <template v-if="hasPerm">
            <render-perm-item
                v-for="(sys, sysIndex) in systemList"
                :key="sys.id"
                :expanded.sync="sys.expanded"
                :ext-cls="sysIndex > 0 ? 'iam-perm-ext-cls' : ''"
                :title="sys.name"
                :one-perm="onePerm"
                :perm-length="sys.count">
                <perm-table
                    :key="sys.id"
                    :system-id="sys.id"
                    :params="data"
                    :data="data"
                    @after-delete="handleAfterDelete(...arguments, sysIndex)" />
            </render-perm-item>
        </template>
        <template v-if="isEmpty">
            <div class="iam-custom-perm-empty-wrapper">
                <iam-svg />
            </div>
        </template>
    </div>
</template>
<script>
    import RenderPermItem from '../../perm/components/render-perm'
    import PermTable from './perm-table-edit'
    import PermSystem from '@/model/my-perm-system'
    export default {
        name: '',
        components: {
            RenderPermItem,
            PermTable
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
                isExpanded: false,
                detailSideslider: {
                    isShow: false,
                    title: '查看详情'
                },
                systemList: [],
                onePerm: '',
                pageLoading: false
            }
        },
        computed: {
            /**
             * hasPerm
             */
            hasPerm () {
                return this.systemList.length > 0 && !this.pageLoading
            },

            /**
             * isEmpty
             */
            isEmpty () {
                return this.systemList.length < 1 && !this.pageLoading
            }
        },
        async created () {
            await this.fetchSystems()
        },
        methods: {
            /**
             * 获取系统列表
             */
            async fetchSystems () {
                this.pageLoading = true
                const { type } = this.data
                try {
                    const res = await this.$store.dispatch('organization/getSubjectHasPermSystem', {
                        subjectType: type === 'user' ? type : 'department',
                        subjectId: type === 'user' ? this.data.username : this.data.id
                    })
                    this.systemList = (res.data || []).map(item => new PermSystem(item))
                    this.onePerm = this.systemList.length
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
                    this.pageLoading = false
                }
            },

            /**
             * handleAfterDelete
             */
            handleAfterDelete (payload, sysIndex) {
                --this.systemList[sysIndex].count
                if (this.systemList[sysIndex].count < 1) {
                    this.systemList.splice(sysIndex, 1)
                }
            }
        }
    }
</script>
<style lang="postcss">
    .iam-custom-perm-wrapper {
        height: calc(100vh - 204px);
        .iam-perm-ext-cls {
            margin-top: 10px;
        }
        .iam-custom-perm-empty-wrapper {
            img {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 120px;
            }
        }
    }
</style>
