<template>
    <div>
        <template v-if="['custom'].includes(popoverType)">
            <div :class="['iam-guide-wrapper', { 'has-animation': hasAnimation }]"
                :style="style"
                v-if="!noviceGuide[type] && !loading && flag && isShow">
                <div class="content-wrapper">
                    <section class="content-shade">
                        <div class="text">{{ content }}</div>
                        <div class="knowed-action"
                            @click.stop="handleKnow">
                            {{ $t(`m.guide['我知道了']`) }}
                        </div>
                    </section>
                    <div :class="['triangle', direction]"></div>
                </div>
            </div>
        </template>
        <template v-if="['component'].includes(popoverType) && (!noviceGuide[type] && isShow)">
            <bk-popconfirm
                ref="popconfirmCom"
                v-bind="$attrs"
                v-on="$listeners"
                @confirm="handleKnow"
                width="288">
                <div slot="content">
                    <slot name="popconfirm-header" />
                    <slot name="popconfirm-content" />
                </div>
                <slot name="popconfirm-show" />
            </bk-popconfirm>
        </template>
    </div>
</template>
<script>
    import { mapGetters } from 'vuex';

    export default {
        name: '',
        props: {
            content: {
                type: String,
                default: 'default'
            },
            style: {
                type: Object,
                default: () => {
                    return {};
                }
            },
            type: {
                type: String,
                default: 'create_group'
            },
            direction: {
                type: String,
                default: 'top',
                validator: (value) => {
                    return ['top', 'right', 'bottom', 'left'].includes(value);
                }
            },
            loading: {
                type: Boolean,
                default: false
            },
            flag: {
                type: Boolean,
                default: true
            },
            popoverType: {
                type: String,
                default: 'custom'
            }
        },
        data () {
            return {
                hasAnimation: true
            };
        },
        computed: {
            ...mapGetters(['noviceGuide', 'user']),
            isShow () {
                const types = [
                    'rating_manager_subject_scope',
                    'rating_manager_merge_action',
                    'rating_manager_authorization_scope',
                    'grade_manager_upgrade'
                ];
                if (types.includes(this.type)) {
                    return ['super_manager', 'staff'].includes(this.user.role.type);
                }
                return true;
            }
        },
        created () {
            this.handleInit();
        },
        methods: {
            async handleInit () {
                // 动画显示5秒后关闭
                const popoverItem = {
                    custom: () => {
                        this.timer = setTimeout(() => {
                            this.hasAnimation = false;
                            clearTimeout(this.timer);
                        }, 5000);
                    },
                    component: () => {
                        this.handleShowGuide();
                    }
                };
                return popoverItem[this.popoverType]();
            },

            async handleKnow () {
                try {
                    await this.$store.dispatch('editNoviceGuide', {
                        scene: this.type
                    });
                    const popoverItem = {
                        custom: () => {
                            this.$store.commit('updateNoviceGuide', this.type);
                        },
                        component: () => {
                            this.handleHideGuide();
                            this.showTimer = setTimeout(() => {
                                this.$store.commit('updateNoviceGuide', this.type);
                                clearTimeout(this.showTimer);
                            }, 5 * 1000);
                        }
                    };
                    popoverItem[this.popoverType]();
                } catch (e) {
                    console.error(e);
                }
            },

            handleShowGuide () {
                this.$nextTick(() => {
                    this.$refs.popconfirmCom && this.$refs.popconfirmCom.$refs.popover.showHandler();
                });
            },

            handleHideGuide () {
                this.$refs.popconfirmCom && this.$refs.popconfirmCom.$refs.popover.hideHandler();
            }
        }
    };
</script>
<style lang="postcss" scoped>
    $cubic-bezier: cubic-bezier(0.4, 0, 0.2, 1);
    $duration: 0.3s;
    @keyframes float {
        50% {
            transform: translate(10px, 0);
        }
    }
    .iam-guide-wrapper {
        position: absolute;
        width: 240px;
        border-radius: 2px;
        box-shadow: 0px 3px 6px 0px rgba(0, 0, 0, .1);
        transition: left $duration $cubic-bezier;
        z-index: 10;
        &.has-animation {
            animation: float 1s ease-out infinite;
        }
        .content-wrapper {
            position: relative;
            background: #699df4;
        }
        .content-shade {
            padding: 14px 16px;
            background: #699df4;
        }
        .text {
            line-height: 20px;
            font-size: 12px;
            color: #fff;
            font-weight: normal;
            word-break: break-all;
        }
        .knowed-action {
            position: relative;
            left: 155px;
            margin-top: 5px;
            width: 60px;
            line-height: 20px;
            background: #fff;
            border-radius: 12px;
            font-size: 12px;
            color: #3a84ff;
            text-align: center;
            cursor: pointer;
            &:hover {
                background: #e1ecff;
            }
        }
        .triangle {
            position: absolute;
            width: 10px;
            height: 10px;
            background: #699df4;
            transform: rotate(45deg);
            z-index: -1;
            &.top {
                top: -4px;
                left: 105px;
                border-bottom: none;
                border-right: none;
            }
            &.right {
                top: 50%;
                transform: rotate(45deg) translateY(-50%);
                right: -1px;
                border-bottom: none;
                border-left: none;
            }
            &.bottom {
                bottom: -4px;
                left: 105px;
                border-left: none;
                border-top: none;
            }
            &.left {
                top: 50%;
                transform: rotate(45deg) translateY(-50%);
                left: -8px;
                border-top: none;
                border-right: none;
            }
        }
    }
</style>
