<template>
    <bk-sideslider
        :is-show.sync="isShowSideslider"
        :title="title"
        :width="width"
        ext-cls="iam-group-perm-sideslider"
        :quick-close="true"
        @animation-end="handleAnimationEnd">
        <div slot="header">
            <p class="single-hide"
                :title="`${$t(`m.userGroup['用户组']`)}
                ${$t(`m.common['【']`)}${name}${$t(`m.common['】']`)}${$t(`m.common['的详情']`)}`"
            >
                {{ $t(`m.userGroup['用户组']`) }}
                {{$t(`m.common['【']`)}}{{ name }}{{$t(`m.common['】']`)}}{{ $t(`m.common['的详情']`) }}
            </p>
            <p class="group-id">ID: {{ groupId }}</p>
        </div>
        <div slot="content" class="content-wrapper" data-test-id="myPerm_sideslider_groupPermContentWrapper"
            v-bkloading="{ isLoading, opacity: 1 }">
            <div class="iam-group-perm-sideslider-tab set-tab-margin-bottom" v-if="!isLoading && showMember">
                <section class="tab-item active">{{$t(`m.perm['组权限']`)}}</section>
            </div>
            <section>
                <group-perm-new :id="groupId" mode="detail" />
            </section>
        </div>
    </bk-sideslider>
</template>
<script>
    import GroupPermNew from '@/views/group/detail/group-perm-new.vue';

    export default {
        name: '',
        components: {
            GroupPermNew
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
                isLoading: true,
                width: window.innerWidth - 500
            };
        },
        watch: {
            show: {
                handler (value) {
                    this.isShowSideslider = !!value;
                    if (this.isShowSideslider) {
                        setTimeout(() => {
                            this.isLoading = false;
                        }, 300);
                    }
                },
                immediate: true
            }
        },
        methods: {
            handleAnimationEnd () {
                this.$emit('animation-end');
            }
        }
    };
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
        .iam-group-perm-sideslider-tab {
            display: flex;
            justify-content: flex-start;
            padding: 0 20px;
            width: 100%;
            height: 42px;
            line-height: 42px;
            background: #fff;
            border-radius: 2px;
            box-shadow: 0px 1px 2px 0px rgba(247, 220, 220, .05);
            color: #63656e;
            .tab-item {
                font-size: 14px;
                cursor: pointer;
                &.active {
                    color: #3a84ff;
                    border-bottom: 2px solid #3a84ff;
                }
            }
        }
    }
</style>
