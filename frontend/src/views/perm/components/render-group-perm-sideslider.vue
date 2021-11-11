<template>
    <bk-sideslider
        :is-show.sync="isShowSideslider"
        :title="title"
        :width="880"
        ext-cls="iam-group-perm-sideslider"
        :quick-close="true"
        @animation-end="handleAnimationEnd">
        <div slot="header">
            <p>{{ $t(`m.userGroup['用户组']`) }}【{{ name }}】{{ $t(`m.common['的详情']`) }}</p>
            <p class="group-id">ID: {{ groupId }}</p>
        </div>
        <div
            slot="content"
            class="content-wrapper"
            v-bkloading="{ isLoading, opacity: 1 }">
            <render-tab
                v-if="!isLoading && showMember"
                :active="'perm'"
                ext-cls="set-tab-margin-bottom" />
            <section>
                <render-group-perm :id="groupId" mode="detail" @on-init="handleOnInit" />
            </section>
        </div>
    </bk-sideslider>
</template>
<script>
    // import RenderPermItem from '../group-perm/render-perm'
    // import DetailTable from '../group-perm/detail-table'
    import RenderTab from '../group-perm/render-tab'
    import renderGroupPerm from '../../group/detail/group-perm-new'
    export default {
        name: '',
        components: {
            RenderTab,
            renderGroupPerm
        },
        props: {
            show: {
                type: Boolean,
                default: false
            },
            groupId: {
                type: [String, Number],
                default: ''
            },
            title: {
                type: String,
                default: ''
            },
            name: {
                type: String,
                default: ''
            },
            showMember: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                groupTemplateList: [],
                isShowSideslider: false,
                requestQueue: ['list']
            }
        },
        computed: {
            isLoading () {
                return this.requestQueue.length > 0
            }
        },
        watch: {
            show: {
                handler (value) {
                    this.isShowSideslider = !!value
                    if (this.isShowSideslider) {
                        // this.fetchPermList()
                    }
                },
                immediate: true
            }
        },
        methods: {
            async fetchPermList () {
                try {
                    const res = await this.$store.dispatch('perm/getGroupTemplates', {
                        id: this.groupId
                    })
                    const data = res.data || []
                    data.forEach(item => {
                        item.displayName = `${item.name}（${item.system.name}）`
                        item.expanded = false
                    })
                    this.groupTemplateList.splice(0, this.groupTemplateList.length, ...data)
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
                    this.requestQueue.shift()
                }
            },

            handleOnInit (flag) {
                if (!flag) {
                    this.requestQueue.shift()
                }
                // this.isLoading = flag
            },

            handleAnimationEnd () {
                // this.groupTemplateList = []
                this.requestQueue = ['list']
                this.$emit('animation-end')
            }
        }
    }
</script>
<style lang="postcss">
    .iam-group-perm-sideslider {
        .bk-sideslider-content {
            background: #f5f6fa;
        }
        .group-id {
            position: relative;
            top: -12px;
            line-height: 0;
            font-size: 12px;
            color: #c4c6cc;
        }
        .content-wrapper {
            position: relative;
            padding: 30px;
            min-height: calc(100vh - 60px);
        }
        .iam-perm-ext-cls {
            margin-top: 1px;
        }
        .set-tab-margin-bottom {
            margin-bottom: 10px;
        }
        .iam-group-member-empty-wrapper,
        .iam-my-perm-empty-wrapper {
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
