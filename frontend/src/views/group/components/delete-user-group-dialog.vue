<template>
    <bk-dialog
        v-model="isShowDialog"
        width="400"
        :title="$t(`m.dialog['确认删除用户组']`)"
        :mask-close="false"
        :close-icon="false"
        header-position="center"
        :show-footer="false"
        ext-cls="iam-delete-user-group-dialog"
        @after-leave="handleAfterDeleteLeave">
        <div class="delete-content-wrapper">
            <div class="delete-tips">
                <p>
                    {{ `${$t(`m.common['删除']`)}${$t(`m.common['【']`)}${name}${$t(`m.common['】']`)},
                    ${$t(`m.dialog['将产生以下影响']`)}: `}}
                </p>
                <p><Icon bk type="info-circle-shape" class="warn" /> {{ $t(`m.dialog['组内用户和组织将被全部移除']`) }}</p>
                <p><Icon bk type="info-circle-shape" class="warn" /> {{ $t(`m.dialog['组权限将被全部移除']`) }}</p>
                <p><Icon bk type="info-circle-shape" class="warn" /> {{ $t(`m.dialog['组内用户继承该组的权限将失效']`) }}</p>
            </div>
            <div class="operate-buttons">
                <bk-button theme="primary" :loading="loading" @click="handleSubmitDelete">
                    {{ $t(`m.common['确定']`) }}
                </bk-button>
                <bk-button theme="default" style="margin-left: 10px;" @click="hideCancelDelete">
                    {{ $t(`m.common['取消-dialog']`) }}
                </bk-button>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
    export default {
        name: '',
        props: {
            show: {
                type: Boolean,
                default: false
            },
            name: {
                type: String,
                default: ''
            },
            loading: {
                type: Boolean,
                default: false
            }
        },
        computed: {
            isShowDialog: {
                get () {
                    return this.show;
                },
                set (value) {
                    this.$emit('update:show', value);
                }
            }
        },
        methods: {
            handleSubmitDelete () {
                this.$emit('on-submit');
            },

            hideCancelDelete () {
                this.$emit('update:show', false);
            },

            handleAfterDeleteLeave () {
                this.$emit('update:show', false);
                this.$emit('on-after-leave');
            }
        }
    };
</script>
<style lang='postcss'>
    .iam-delete-user-group-dialog {
        .delete-content-wrapper {
            .delete-tips {
                padding-left: 44px;
                text-align: left;
                word-break: break-all;
                .warn {
                    color: #ffb848;
                }
            }
            .operate-buttons {
                margin-top: 34px;
                text-align: center;
            }
        }
    }
</style>
