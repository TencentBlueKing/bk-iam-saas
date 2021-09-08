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
            <!-- 组权限 -->
            <render-tab
                v-if="!isLoading && showMember"
                :active.sync="tabActive"
                ext-cls="set-tab-margin-bottom" />
            <section>
                <render-group-perm :id="groupId" mode="detail" />
            </section>
        </div>
    </bk-sideslider>
</template>
<script>
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
                tabActive: 'perm',
                isShowSideslider: false,
                isLoading: true
            }
        },
        watch: {
            show: {
                handler (value) {
                    this.isShowSideslider = !!value
                    if (this.isShowSideslider) {
                        setTimeout(() => {
                            this.isLoading = false
                        }, 300)
                    }
                },
                immediate: true
            }
        },
        methods: {
            handleAnimationEnd () {
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
        .set-tab-margin-bottom {
            margin-bottom: 10px;
        }
    }
</style>
