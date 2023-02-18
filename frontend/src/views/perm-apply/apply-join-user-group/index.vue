<template>
    <smart-action class="iam-join-user-group-wrapper">
        <section>
            <!-- <template v-if="isShowMemberAdd">
                <render-action
                    ref="memberRef"
                    :title="addMemberText"
                    :tips="addMemberTips"
                    @on-click="handleAddMember"
                    style="margin-bottom: 16px;">
                    <iam-guide
                        type="rating_manager_authorization_scope"
                        direction="left"
                        :style="{ top: '-25px', left: '440px' }"
                        :content="$t(`m.guide['授权人员范围']`)" />
                </render-action>
            </template> -->
            <!-- <template v-else> -->
            <render-member
                :users="users"
                :departments="departments"
                :is-all="isAll"
                :render-title="addMemberTitle"
                :render-text="addMemberText"
                :tips="addMemberTips"
                @on-add="handleAddMember"
                @on-delete="handleMemberDelete"
            />
            <!-- </template> -->
        </section>
        <p class="action-empty-error" v-if="isShowMemberEmptyError">{{ $t(`m.verify['可授权人员范围不可为空']`) }}</p>
        <div slot="action">
            <bk-button theme="primary" :loading="submitLoading" @click="handleSubmit">
                {{ $t(`m.common['提交']`) }}
            </bk-button>
            <!-- <bk-button style="margin-left: 10px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button> -->
        </div>

        <render-perm-side-slider
            :show="isShowPermSideSlider"
            :name="curGroupName"
            :group-id="curGroupId"
            :show-member="false"
            @animation-end="handleAnimationEnd" />

        <add-member-dialog
            :show.sync="isShowAddMemberDialog"
            :users="users"
            :departments="departments"
            :title="addMemberTitle"
            :all-checked="isAll"
            :show-limit="false"
            @on-cancel="handleCancelAdd"
            @on-sumbit="handleSubmitAdd" />

    </smart-action>
</template>
<script>
    import _ from 'lodash';
    import { mapGetters } from 'vuex';
    import { PERMANENT_TIMESTAMP } from '@/common/constants';
    // import IamGuide from '@/components/iam-guide/index.vue';
    import RenderPermSideSlider from '@/views/perm/components/render-group-perm-sideslider';
    // import RenderAction from '@/views/grading-admin/common/render-action';
    import RenderMember from '@/views/grading-admin/components/render-member';
    import AddMemberDialog from '@/views/group/components/iam-add-member';
    // import BkUserSelector from '@blueking/user-selector';
    export default {
        name: '',
        components: {
            // IamGuide,
            RenderPermSideSlider,
            // RenderAction,
            RenderMember,
            AddMemberDialog
            // BkUserSelector
        },
        data () {
            return {
                userApi: window.BK_USER_API,
                reason: '',
                searchValue: [],
                tableLoading: false,
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                currentBackup: 1,
                isShowPermSideSlider: false,
                curGroupName: '',
                curGroupId: '',
                isShowGradeSlider: false,
                sliderLoading: false,
                gradeMembers: [],
                gradeSliderTitle: '',
                curRole: '',
                users: [],
                departments: [],
                isAll: false,
                addMemberTitle: this.$t(`m.myApply['权限获得者']`),
                addMemberText: this.$t(`m.permApply['选择权限获得者']`),
                addMemberTips: this.$t(`m.permApply['可代他人申请加入用户组获取权限']`)
            };
        },
        computed: {
            ...mapGetters(['user'])
        },
        watch: {
            reason (value) {
                this.isShowReasonError = false;
            },
            'pagination.current' (value) {
                this.currentBackup = value;
            }
        },
        created () {
            this.searchParams = this.$route.query;
            delete this.searchParams.limit;
            delete this.searchParams.current;
            this.curRole = this.user.role.type;
            this.searchData = [
                {
                    id: 'id',
                    name: 'ID',
                    default: true
                    // validate (values, item) {
                    //     const validate = (values || []).every(_ => /^(\d*)$/.test(_.name))
                    //     return !validate ? '' : true
                    // }
                },
                {
                    id: 'name',
                    name: this.$t(`m.userGroup['用户组名']`),
                    default: true
                },
                {
                    id: 'description',
                    name: this.$t(`m.common['描述']`),
                    disabled: true
                },
                {
                    id: 'system_id',
                    name: this.$t(`m.common['系统包含']`),
                    remoteMethod: this.handleRemoteSystem
                },
                // 一级管理空间
                {
                    id: 'role_id',
                    name: this.$t(`m.grading['一级管理空间']`),
                    remoteMethod: this.handleGradeAdmin
                }
            ];
            this.setCurrentQueryCache(this.refreshCurrentQuery());
            const isObject = payload => {
                return Object.prototype.toString.call(payload) === '[object Object]';
            };
            const currentQueryCache = this.getCurrentQueryCache();
            if (currentQueryCache && Object.keys(currentQueryCache).length) {
                if (currentQueryCache.limit) {
                    const { current, limit } = currentQueryCache;
                    this.pagination = Object.assign(this.pagination, { current, limit });
                }
                for (const key in currentQueryCache) {
                    if (key !== 'limit' && key !== 'current') {
                        const curData = currentQueryCache[key];
                        const tempData = this.searchData.find(item => item.id === key);
                        if (isObject(curData)) {
                            if (tempData) {
                                this.searchValue.push({
                                    id: key,
                                    name: tempData.name,
                                    values: [curData]
                                });
                                this.searchList.push(..._.cloneDeep(this.searchValue));
                                this.searchParams[key] = curData.id;
                            }
                        } else if (tempData) {
                            this.searchValue.push({
                                id: key,
                                name: tempData.name,
                                values: [{
                                    id: curData,
                                    name: curData
                                }]
                            });
                            this.searchList.push(..._.cloneDeep(this.searchValue));
                            this.searchParams[key] = curData;
                        } else {
                            this.searchParams[key] = curData;
                        }
                    }
                }
            }
        },
        methods: {

            setDefaultSelect (payload) {
                return !this.curUserGroup.includes(payload.id.toString());
            },

            handleAnimationEnd () {
                this.curGroupName = '';
                this.curGroupId = '';
                this.isShowPermSideSlider = false;
            },

            handleDeadlineChange (payload) {
                if (payload) {
                    this.isShowExpiredError = false;
                }
                if (payload !== PERMANENT_TIMESTAMP && payload) {
                    const nowTimestamp = +new Date() / 1000;
                    const tempArr = String(nowTimestamp).split('');
                    const dotIndex = tempArr.findIndex(item => item === '.');
                    const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
                    this.expiredAtUse = payload + nowSecond;
                    return;
                }
                this.expiredAtUse = payload;
            },

            handleExpiredAt () {
                const nowTimestamp = +new Date() / 1000;
                const tempArr = String(nowTimestamp).split('');
                const dotIndex = tempArr.findIndex(item => item === '.');
                const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
                const expiredAt = this.expiredAtUse + nowSecond;
                return expiredAt;
            },

            handleCancel () {
                this.$router.push({
                    name: 'permApply'
                });
            }
        }
    };
</script>
<style lang="postcss">
    .iam-join-user-group-wrapper {
        .user-group-table {
            .user-group-table {
                margin-top: 10px;
                border-right: none;
                border-bottom: none;
                &.set-border {
                    border-right: 1px solid #dfe0e5;
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
            .can-view {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
        }
        .search-wrapper {
            .info {
                line-height: 30px;
                font-size: 12px;
            }
        }
        .expired-at-wrapper {
            margin-top: 16px;
        }
        .reason-wrapper {
            margin-top: 16px;
            .join-reason-error {
                .bk-textarea-wrapper {
                    border-color: #ff5656;
                }
            }
        }
        .user-group-error,
        .perm-recipient-error,
        .expired-at-error,
        .reason-empty-wrapper {
            margin-top: 5px;
            font-size: 12px;
            color: #ff4d4d;
        }
        .is-member-empty-cls {
            .user-selector-container {
                border-color: #ff4d4d;
            }
        }
    }
    .grade-memebers-content {
        padding: 20px;
        height: calc(100vh - 61px);
        .member-item {
            position: relative;
            display: inline-block;
            margin: 0 6px 6px 0;
            padding: 0 10px;
            line-height: 22px;
            background: #f5f6fa;
            border: 1px solid #dcdee5;
            border-radius: 2px;
            font-size: 12px;
            .member-name {
                display: inline-block;
                max-width: 200px;
                line-height: 17px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                vertical-align: text-top;
                .count {
                    color: #c4c6cc;
                }
            }
        }
        .info {
            margin-top: 5px;
            color: #c4c6cc;
            font-size: 14px;
        }
    }
</style>
