<template>
    <div class="iam-transfer-wrapper">
        <Group @group-selection-change="handleGroupSelection" />

        <Custom />

        <RatingManager />

        <SystemManager />

        <SuperManager />

        <div class="iam-transfer-group-wrapper" :style="{ minHeight: isLoading ? '328px' : 0 }"
            v-bkloading="{ isLoading, opacity: 1 }">
            <div class="transfer-group-content">
                <div class="input-header">
                    <label class="title">{{ $t(`m.permTransfer['将以上权限交接给']`) }}</label>
                </div>
                <div class="content">
                    <div class="input-content">
                        <bk-form :model="formData" form-type="vertical" ref="basicInfoForm">
                            <iam-form-item :label="$t(`m.permTransfer['交接人']`)" required>
                                <bk-user-selector
                                    :value="formData.members"
                                    :api="userApi"
                                    :placeholder="$t(`m.verify['请输入']`)"
                                    style="width: 100%;"
                                    :class="isShowMemberError ? 'is-member-empty-cls' : ''"
                                    @focus="handleRtxFocus"
                                    @blur="handleRtxBlur"
                                    @change="handleRtxChange">
                                </bk-user-selector>
                                <p class="name-empty-error" v-if="isShowMemberError">{{ $t(`m.verify['请选择成员']`) }}</p>
                            </iam-form-item>
                            <iam-form-item :label="$t(`m.common['理由']`)" required>
                                <bk-input
                                    type="textarea"
                                    v-model="formData.reason"
                                    :maxlength="100"
                                    :placeholder="$t(`m.verify['请输入']`)">
                                </bk-input>
                            </iam-form-item>
                        </bk-form>
                    </div>
                </div>
            </div>
        </div>

        <!-- <div style="background: red; height: 800px;"></div> -->
        <div class="fixed-action" style="height: 50px;" :style="{ paddingLeft: fixedActionPaddingLeft }">
            <bk-button theme="primary" @click="submit">
                {{ $t(`m.common['提交']`) }}
            </bk-button>
        </div>
    </div>
</template>
<script>
    import { bus } from '@/common/bus'
    import BkUserSelector from '@blueking/user-selector'
    import Group from './group.vue'
    import Custom from './custom.vue'
    import RatingManager from './rating-manager.vue'
    import SystemManager from './system-manager.vue'
    import SuperManager from './super-manager.vue'
    export default {
        name: '',
        components: {
            Group,
            Custom,
            RatingManager,
            SystemManager,
            SuperManager,
            BkUserSelector
        },
        data () {
            return {
                fixedActionPaddingLeft: '284px',
                groupSelectData: [],
                formData: { members: [], reason: '' },
                isShowMemberError: false,
                userApi: window.BK_USER_API
            }
        },
        created () {
        },
        mounted () {
            bus.$on('nav-resize', flag => {
                if (flag) {
                    this.fixedActionPaddingLeft = '284px'
                } else {
                    this.fixedActionPaddingLeft = '84px'
                }
            })
        },
        methods: {
            handleGroupSelection (list) {
                this.groupSelectData.splice(0, this.groupSelectData.length, ...list)
            },
            submit () {
                console.error(this.groupSelectData)
            },
            handleRtxFocus () {
                this.isShowMemberError = false
            },
            handleRtxBlur () {
                this.isShowMemberError = this.formData.members.length < 1
            },
            handleNameInput (payload) {
                this.isShowNameError = false
                this.nameValidateText = ''
            },
            handleRtxChange (payload) {
                this.isShowMemberError = false
                this.formData.members = payload
            }
        }
    }
</script>
<style lang="postcss">
    @import './index.css';
    .input-header{
        position: absolute;
        padding: 0 30px;
        height: 40px;
        line-height: 40px;
        font-size: 14px;
        color: #63656e;
        border-radius: 2px;
        cursor: pointer;
        .title{
           font-weight: 500;
            color: #313238;
        }
    }
    .input-content{
        padding: 5px 30px 20px 180px;
    }
    .name-empty-error {
        font-size: 12px;
        color: #ff4d4d;
    }
    .is-member-empty-cls {
        .user-selector-container {
            border-color: #ff4d4d !important;
        }
    }
</style>
