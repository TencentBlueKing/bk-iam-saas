<template>
    <smart-action class="iam-create-user-group-wrapper">
        <render-horizontal-block :label="$t(`m.common['基本信息']`)">
            <section ref="basicInfoContentRef">
                <basic-info
                    :data="formData"
                    ref="basicInfoRef"
                    @on-change="handleBasicInfoChange" />
            </section>
        </render-horizontal-block>
        <!-- <render-horizontal-block
            v-if="!isHasPermTemplate"
            :label="$t(`m.levelSpace['最大可授权操作和资源边界']`)"
            :label-width="renderLabelWidth('resource')"
            :required="true"
        >
            <div class="grade-admin-select-wrapper">
                <div class="action">
                    <section class="action-wrapper" @click.stop="handleAddPerm"
                        data-test-id="grading_btn_showAddAction">
                        <Icon bk type="plus-circle-shape" />
                        <span>{{ $t(`m.levelSpace['选择操作和资源边界']`) }}</span>
                    </section>
                    <Icon
                        type="info-fill"
                        class="info-icon"
                        v-bk-tooltips.top="{ content: tips, width: 236, extCls: 'iam-tooltips-cls' }" />
                </div>
            </div>
        </render-horizontal-block>
        <render-horizontal-block
            :label="$t(`m.levelSpace['最大可授权操作和资源边界']`)"
            :label-width="renderLabelWidth('resource')"
            v-if="isHasPermTemplate">
            <div class="grade-admin-select-wrapper">
                <div class="action">
                    <section class="action-wrapper" @click.stop="handleAddPerm">
                        <Icon bk type="plus-circle-shape" />
                        <span>{{ $t(`m.levelSpace['选择操作和资源边界范围']`) }}</span>
                    </section>
                </div>
                <div class="info-wrapper">
                    <p class="tips">{{ infoText }}</p>
                    <section style="min-width: 108px; position: relative;">
                        <iam-guide
                            type="rating_manager_merge_action"
                            direction="right"
                            :loading="isLoading"
                            :style="renderLabelWidth('rating_manager_merge_action_guide')"
                            :content="$t(`m.guide['聚合操作']`)" />
                        <bk-switcher
                            v-model="isAllExpanded"
                            :disabled="isAggregateDisabled"
                            size="small"
                            theme="primary"
                            @change="handleAggregateAction" />
                        <span class="text">{{ expandedText }}</span>
                    </section>
                </div>
                <section ref="instanceTableContentRef">
                    <render-instance-table
                        is-edit
                        mode="create"
                        ref="resourceInstanceRef"
                        :list="policyList"
                        :authorization="curAuthorizationData"
                        :original-list="tableListBackup"
                        :is-all-expanded="isAllExpanded"
                        :backup-list="aggregationsTableData"
                        :group-id="$route.params.id"
                        @on-delete="handleDelete"
                        @on-aggregate-delete="handleAggregateDelete"
                        @handleAggregateAction="handleAggregateAction"
                        @on-select="handleAttrValueSelected"
                        @on-resource-select="handleResSelect" />
                </section>
            </div>
        </render-horizontal-block>
        <p class="action-empty-error" v-if="isShowActionEmptyError">{{ $t(`m.verify['操作和资源边界不可为空']`) }}</p>
        <section v-if="isShowMemberAdd" ref="memberRef">
            <render-action
                ref="memberRef"
                :title="$t(`m.levelSpace['最大可授权人员边界']`)"
                :label-width="renderLabelWidth('resource')"
                :tips="addMemberTips"
                @on-click="handleAddMember"
            >
                <iam-guide
                    type="rating_manager_authorization_scope"
                    direction="left"
                    :style="{ top: '-25px', left: '440px' }"
                    :content="$t(`m.guide['授权人员范围']`)" />
            </render-action>
        </section>
        <section ref="memberRef">
            <render-member
                :tip="$t(`m.levelSpace['管理空间只能给该范围内的人员授权']`)"
                :users="users"
                :departments="departments"
                :expired-at-error="isShowExpiredError"
                :inherit-subject-scope="inheritSubjectScope"
                :label-width="renderLabelWidth('member')"
                @on-add="handleAddMember"
                @on-delete="handleMemberDelete"
                @on-change="handleChange" />
        </section>
        <p class="action-empty-error" v-if="isShowMemberEmptyError">{{ $t(`m.verify['可授权人员边界不可为空']`) }}</p> -->
        <render-horizontal-block
            :label="$t(`m.nav['授权边界']`)"
            :label-width="renderLabelWidth('resource')"
            :required="false"
        >
            <div class="authorize-boundary-form">
                <div class="authorize-resource-boundary">
                    <div class="resource-boundary-title is-required">
                        {{ $t(`m.levelSpace['最大可授权操作和资源边界']`) }}
                    </div>
                    <div class="resource-boundary-header flex-between">
                        <section>
                            <bk-button
                                theme="default"
                                size="small"
                                icon="plus-circle-shape"
                                class="perm-resource-add"
                                @click.stop="handleAddPerm"
                            >
                                {{ $t(`m.common['添加']`) }}
                            </bk-button>
                        </section>
                        <div
                            v-if="isHasPermTemplate"
                            class="aggregate-action-group"
                            style="min-width: 108px; position: relative;">
                            <iam-guide
                                type="rating_manager_authorization_scope"
                                direction="right"
                                :loading="isLoading"
                                :style="renderLabelWidth('rating_manager_merge_action_guide')"
                                :content="$t(`m.guide['聚合操作']`)" />
                            <div
                                v-for="item in AGGREGATION_EDIT_ENUM"
                                :key="item.value"
                                :class="[
                                    'aggregate-action-btn',
                                    { 'is-active': isAllExpanded === item.value },
                                    { 'is-disabled': isAggregateDisabled }
                                ]"
                                @click.stop="handleAggregateAction(item.value)"
                            >
                                <span>{{ $t(`m.grading['${item.name}']`)}}</span>
                            </div>
                        </div>
                    </div>
                    <div v-if="isHasPermTemplate">
                        <div
                            class="resource-instance-wrapper"
                            ref="instanceTableContentRef"
                            v-bkloading="{
                                isLoading,
                                opacity: 1,
                                zIndex: 1000,
                                extCls: 'loading-resource-instance-cls'
                            }"
                        >
                            <render-instance-table
                                is-edit
                                mode="create"
                                ref="resourceInstanceRef"
                                :list="policyList"
                                :authorization="curAuthorizationData"
                                :original-list="tableListBackup"
                                :total-count="originalList.length"
                                :is-all-expanded="isAllExpanded"
                                :backup-list="aggregationsTableData"
                                :group-id="$route.params.id"
                                @on-delete="handleDelete"
                                @on-aggregate-delete="handleAggregateDelete"
                                @handleAggregateAction="handleAggregateAction"
                                @on-select="handleAttrValueSelected"
                                @on-resource-select="handleResSelect"
                                @on-clear-all="handleDeleteResourceAll" />
                        </div>
                    </div>
                </div>
                <p class="action-empty-error" v-if="isShowActionEmptyError">
                    {{ $t(`m.verify['操作和资源边界不可为空']`) }}
                </p>
                <div ref="memberRef" class="authorize-members-boundary">
                    <render-member
                        :tip="addMemberTips"
                        :users="users"
                        :departments="departments"
                        :expired-at-error="isShowExpiredError"
                        :inherit-subject-scope="inheritSubjectScope"
                        :label-width="renderLabelWidth('member')"
                        @on-add="handleAddMember"
                        @on-delete="handleMemberDelete"
                        @on-change="handleChange"
                        @on-delete-all="handleDeleteAll" />
                </div>
                <p class="action-empty-error" v-if="isShowMemberEmptyError && !inheritSubjectScope">
                    {{ $t(`m.verify['可授权人员边界不可为空']`) }}
                </p>
            </div>
        </render-horizontal-block>
        <template v-if="isStaff">
            <render-horizontal-block
                ext-cls="reason-wrapper"
                :label="$t(`m.common['理由']`)"
                :required="true">
                <section class="content-wrapper" ref="reasonRef">
                    <bk-input
                        type="textarea"
                        :rows="5"
                        :ext-cls="isShowReasonError ? 'join-reason-error' : ''"
                        v-model="reason"
                        @input="handleReasonInput"
                        @blur="handleReasonBlur"
                    />
                </section>
                <p class="reason-empty-error" v-if="isShowReasonError">{{ $t(`m.verify['理由不可为空']`) }}</p>
            </render-horizontal-block>
        </template>
        <div slot="action">
            <bk-button theme="primary" type="button" :loading="submitLoading"
                data-test-id="group_btn_createSubmit"
                @click="handleSubmit">
                {{ $t(`m.common['提交']`) }}
            </bk-button>
            <bk-button style="margin-left: 10px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
        </div>

        <add-member-dialog
            :show.sync="isShowAddMemberDialog"
            :users="users"
            :is-rating-manager="isRatingManager"
            :departments="departments"
            @on-cancel="handleCancelAdd"
            @on-sumbit="handleSubmitAdd" />

        <add-perm-sideslider
            ref="addPermSideslider"
            :is-show.sync="isShowAddSideslider"
            :custom-perm="originalList"
            :template="templateDetailList"
            :aggregation="aggregationData"
            :authorization="authorizationData"
            :external-template="externalSystemsLayout.userGroup.addGroup.hideAddTemplateTextBtn"
            @on-view="handleViewDetail"
            @on-add-custom="handleAddCustom"
            @on-edit-custom="handleEditCustom"
            @on-cancel="handleAddCancel"
            @on-submit="handleSubmitPerm" />

        <add-action-sideslider
            :is-show.sync="isShowAddActionSideslider"
            :default-value="curActionValue"
            :default-data="defaultValue"
            :aggregation="aggregationDataByCustom"
            :authorization="authorizationDataByCustom"
            @on-submit="handleSelectSubmit" />

        <render-template-sideslider
            :is-show.sync="templateDetailSideslider.isShow"
            :id="templateDetailSideslider.id" />
    </smart-action>
</template>
<script>
    import _ from 'lodash';
    import { mapGetters } from 'vuex';
    import { guid, renderLabelWidth } from '@/common/util';
    import { CUSTOM_PERM_TEMPLATE_ID, PERMANENT_TIMESTAMP, SIX_MONTH_TIMESTAMP, AGGREGATION_EDIT_ENUM } from '@/common/constants';
    // import { leavePageConfirm } from '@/common/leave-page-confirm';
    import IamGuide from '@/components/iam-guide/index.vue';
    import AddMemberDialog from '../components/iam-add-member';
    import RenderMember from '@/views/manage-spaces/components/render-member';
    import basicInfo from '@/views/manage-spaces/components/basic-info';
    // import renderAction from '@/views/manage-spaces/common/render-action';
    import AddPermSideslider from '../components/add-group-perm-sideslider';
    import AddActionSideslider from '../components/add-action-sideslider';
    import RenderInstanceTable from '../components/render-instance-table';
    import RenderTemplateSideslider from '../components/render-template-detail-sideslider';
    // import GroupPolicy from '@/model/grade-policy';
    import GroupPolicy from '@/model/group-policy';
    import GroupAggregationPolicy from '@/model/group-aggregation-policy';
    import Condition from '@/model/condition';

    export default {
        name: '',
        components: {
            AddMemberDialog,
            basicInfo,
            // renderAction,
            RenderMember,
            IamGuide,
            AddPermSideslider,
            AddActionSideslider,
            RenderTemplateSideslider,
            RenderInstanceTable
        },
        props: {
            id: {
                type: [String, Number],
                default: 0
            }
        },
        data () {
            return {
                formData: {
                    name: '',
                    description: '',
                    members: [],
                    sync_perm: true
                },
                isShowAddMemberDialog: false,
                isShowMemberAdd: false,
                expired_at: SIX_MONTH_TIMESTAMP,
                users: [],
                departments: [],
                submitLoading: false,
                isShowActionEmptyError: false,
                isShowExpiredError: false,
                isShowAddSideslider: false,
                isShowAddActionSideslider: false,
                curActionValue: [],
                originalList: [],
                policyList: [],
                tableListBackup: [],
                templateDetailList: [],
                aggregationData: {},
                aggregations: [],
                aggregationsBackup: [],
                aggregationsTableData: [],
                authorizationData: {},
                aggregationDataByCustom: {},
                authorizationDataByCustom: {},
                allAggregationData: {},
                isLoading: false,
                isAllExpanded: false,
                isShowMemberEmptyError: false,
                isShowReasonError: false,
                hasDeleteCustomList: [],
                hasAddCustomList: [],
                templateDetailSideslider: {
                    isShow: false,
                    id: ''
                },
                curMap: null,
                tips: this.$t(`m.grading['添加操作提示']`),
                infoText: this.$t(`m.grading['选择提示']`),
                addMemberTips: this.$t(`m.levelSpace['管理空间可以编辑、管理二级管理空间的权限']`),
                addMemberTitle: this.$t(`m.levelSpace['最大可授权人员边界']`),
                inheritSubjectScope: true,
                curSystemId: [],
                renderLabelWidth,
                AGGREGATION_EDIT_ENUM
            };
        },
        computed: {
            ...mapGetters(['user', 'externalSystemsLayout']),
            /**
             * isAggregateDisabled
             */
            isAggregateDisabled () {
                const aggregationIds = this.policyList.reduce((counter, item) => {
                    return item.aggregationId ? counter.concat(item.aggregationId) : counter;
                }, []);
                const temps = [];
                aggregationIds.forEach(item => {
                    if (!temps.some(sub => sub.includes(item))) {
                        temps.push([item]);
                    } else {
                        const tempObj = temps.find(sub => sub.includes(item));
                        tempObj.push(item);
                    }
                });
                return !temps.some(item => item.length > 1) && !this.isAllExpanded;
            },

            /**
             * expandedText
             */
            expandedText () {
                return this.isAllExpanded ? this.$t(`m.grading['逐项编辑']`) : this.$t(`m.grading['批量编辑']`);
            },
            members () {
                const arr = [];
                if (this.departments.length > 0) {
                    arr.push(...this.departments.map(item => {
                        return {
                            id: item.id,
                            type: 'department'
                        };
                    }));
                }
                if (this.users.length > 0) {
                    arr.push(...this.users.map(item => {
                        return {
                            id: item.username,
                            type: 'user'
                        };
                    }));
                }
                return arr;
            },
            defaultValue () {
                if (this.originalList.length < 1) {
                    return [];
                }
                const tempList = [];
                this.originalList.forEach(item => {
                    if (!tempList.some(sys => sys.system_id === item.system_id)) {
                        tempList.push({
                            system_id: item.system_id,
                            system_name: item.system_name,
                            list: [item]
                        });
                    } else {
                        const curData = tempList.find(sys => sys.system_id === item.system_id);
                        curData.list.push(item);
                    }
                });
                return tempList;
            },
            isHasPermTemplate () {
                return this.policyList.length > 0;
            },
            isRatingManager () {
                return ['rating_manager', 'subset_manager'].includes(this.user.role.type);
            },
            isSuperManager () {
                return this.user.role.type === 'super_manager';
            },
            curAuthorizationData () {
                const data = Object.assign(this.authorizationData, this.authorizationDataByCustom);
                return data;
            }
        },
        watch: {
            reason () {
                this.isShowReasonError = false;
            },
            originalList: {
                handler (value) {
                    this.setPolicyList(value);
                    const uniqueList = [...new Set(this.policyList.map(item => item.system_id))];
                    // 无新增的的系统时无需请求聚合数据
                    const difference = uniqueList.filter(item => !this.curSystemId.includes(item));
                    if (difference.length > 0) {
                        this.curSystemId = [...this.curSystemId.concat(difference)];
                        this.resetData();
                        if (this.policyList.length) {
                            this.fetchAggregationAction(this.curSystemId.join(','));
                        }
                    } else {
                        const data = this.getFilterAggregation(this.aggregationsBackup);
                        this.aggregations = _.cloneDeep(data);
                    }
                },
                deep: true
            }
        },
        methods: {
            async fetchPageData () {
                const propsId = Number(this.id);
                const headerTitle = this.$t(propsId ? `m.nav['克隆二级管理空间']` : `m.nav['新建二级管理空间']`);
                this.$store.commit('setHeaderTitle', headerTitle);
                if (propsId) {
                    await this.fetchDetail();
                } else {
                    const { username } = this.user;
                    this.formData.members = [
                        { username, readonly: true }
                    ];
                }
            },

            async fetchDetail () {
                try {
                    const res = await this.$store.dispatch('spaceManage/getSecondManagerDetail', { id: this.id });
                    if (res.code === 0) {
                        this.getDetailData(res.data);
                    }
                } catch (e) {
                    console.error(e);
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
                    });
                }
            },

            getDetailData (payload) {
                const tempActions = [];
                const {
                    name,
                    description,
                    members,
                    sync_perm,
                    inherit_subject_scope: inheritSubjectScope,
                    subject_scopes, authorization_scopes
                } = payload;
                this.inheritSubjectScope = inheritSubjectScope;
                this.formData = Object.assign({}, {
                    name: `${name}_${this.$t(`m.grading['克隆']`)}`,
                    members,
                    description,
                    sync_perm: sync_perm
                });
                this.isAll = subject_scopes.some(item => item.type === '*' && item.id === '*');
                this.users = subject_scopes.filter(item => item.type === 'user').map(item => {
                    return {
                        name: item.name,
                        username: item.id,
                        type: item.type
                    };
                });
                this.departments = subject_scopes.filter(item => item.type === 'department').map(item => {
                    return {
                        name: item.name,
                        count: item.member_count,
                        type: item.type,
                        id: item.id
                    };
                });
                authorization_scopes.forEach(item => {
                    item.actions.forEach(act => {
                        const tempResource = _.cloneDeep(act.resource_groups);
                        tempResource.forEach(groupItem => {
                            // groupItem.related_resource_types.forEach(subItem => {
                            //     subItem.condition = null;
                            // });
                            groupItem.related_resource_types.forEach(resourceTypeItem => {
                                resourceTypeItem.id = resourceTypeItem.type;
                                resourceTypeItem.condition = null;
                            });
                        });
                        tempActions.push({
                            description: act.description,
                            expired_at: act.expired_at,
                            id: act.id,
                            name: act.name,
                            system_id: item.system.id,
                            system_name: item.system.name,
                            $id: `${item.system.id}&${act.id}`,
                            tag: act.tag,
                            type: act.type,
                            resource_groups: tempResource
                        });
                    });
                });
                this.isShowMemberAdd = false;
                this.originalList = _.cloneDeep(tempActions);
            },

            setPolicyList (payload) {
                if (this.policyList.length < 1) {
                    // this.policyList = payload.map(item => new GroupPolicy(item));
                    this.policyList = payload.map(item => {
                        return new GroupPolicy(
                            item,
                            'add', // 此属性为flag，会在related-resource-types赋值为add
                            'custom',
                            {
                                system: {
                                    id: item.system_id,
                                    name: item.system_name
                                }
                            }
                        );
                    });
                    return;
                }
                const isAddIds = payload.map(item => `${item.system_id}&${item.id}`);
                const isExistIds = [];
                this.policyList.forEach(item => {
                    if (item.isAggregate) {
                        item.actions.forEach(subItem => {
                            isExistIds.push(`${item.system_id}&${subItem.id}`);
                        });
                    } else {
                        isExistIds.push(`${item.system_id}&${item.id}`);
                    }
                });
                // 下一次选择的与现存的交集
                const intersectionIds = isExistIds.filter(item => isAddIds.includes(item));
                // 下一次选择所删除的操作
                const existRestIds = isExistIds.filter(item => !intersectionIds.includes(item));
                // 下一次选择所新增的操作
                const newRestIds = isAddIds.filter(item => !intersectionIds.includes(item));
                if (existRestIds.length > 0) {
                    const tempData = [];
                    this.policyList.forEach(item => {
                        if (!item.isAggregate && !existRestIds.includes(`${item.system_id}&${item.id}`)) {
                            tempData.push(item);
                        }
                        if (item.isAggregate) {
                            const tempList = existRestIds.filter(act => item.actions.map(v => `${item.system_id}&${v.id}`).includes(act));
                            if (tempList.length > 0) {
                                item.actions = item.actions.filter(act => !tempList.includes(`${item.system_id}&${act.id}`));
                            }
                            tempData.push(item);
                        }
                    });
                    this.policyList = tempData.filter(
                        item => !item.isAggregate || (item.isAggregate && item.actions.length > 0)
                    );
                }

                if (newRestIds.length > 0) {
                    newRestIds.forEach(item => {
                        const curSys = payload.find(sys => `${sys.system_id}&${sys.id}` === item);
                        this.policyList.unshift(new GroupPolicy(curSys));
                    });
                }
            },
            
            /**
             * handleBasicInfoChange
             */
            handleBasicInfoChange (field, value) {
                window.changeDialog = true;
                this.formData[field] = value;
            },

            /**
             * handleAddCancel
             */
            handleAddCancel () {
                this.isShowAddSideslider = false;
            },

            /**
             * handleAddCustom
             */
            handleAddCustom () {
                this.curActionValue = this.originalList.map(item => item.$id);
                this.isShowAddActionSideslider = true;
            },

            /**
             * handleViewDetail
             */
            handleViewDetail ({ id }) {
                this.templateDetailSideslider.id = id;
                this.templateDetailSideslider.isShow = true;
            },

            /**
             * handleSubmitPerm
             */
            handleSubmitPerm (templates, aggregation, authorization) {
                console.log('handleSubmitPerm');
                // debugger
                if (this.isAllExpanded) {
                    this.handleAggregateAction(false);
                    this.isAllExpanded = false;
                }
                this.aggregationData = aggregation;
                this.authorizationData = authorization;
                let hasDeleteTemplateList = [];
                let hasAddTemplateList = [];
                if (this.templateDetailList.length > 0) {
                    const intersection = templates.filter(
                        item => this.templateDetailList.map(sub => sub.id).includes(item.id)
                    );
                    hasDeleteTemplateList = this.templateDetailList.filter(
                        item => !intersection.map(sub => sub.id).includes(item.id)
                    );
                    hasAddTemplateList = templates.filter(item => !intersection.map(sub => sub.id).includes(item.id));
                } else {
                    hasAddTemplateList = templates;
                }
                this.templateDetailList = _.cloneDeep(templates);

                if (hasDeleteTemplateList.length > 0) {
                    this.policyList = this.policyList.filter(
                        item => !hasDeleteTemplateList.map(sub => sub.id).includes(item.detail.id)
                    );
                }

                if (this.hasDeleteCustomList.length > 0) {
                    this.policyList = this.policyList.filter(item => {
                        return item.detail.id === CUSTOM_PERM_TEMPLATE_ID
                            && !this.hasDeleteCustomList
                                .map(sub => sub.$id).includes(`${item.detail.system.id}&${item.id}`);
                    });
                }

                const tempList = [];
                hasAddTemplateList.forEach(item => {
                    const temp = _.cloneDeep(item);
                    delete temp.actions;
                    item.actions.forEach(sub => {
                        if (!sub.resource_groups || !sub.resource_groups.length) {
                            sub.resource_groups = sub.related_resource_types.length ? [{ id: '', related_resource_types: sub.related_resource_types }] : [];
                        }
                        tempList.push(new GroupPolicy(sub, 'add', 'template', temp));
                    });
                });
                this.hasAddCustomList.forEach(item => {
                    if (!item.resource_groups || !item.resource_groups.length) {
                        item.resource_groups = item.related_resource_types.length ? [{ id: '', related_resource_types: item.related_resource_types }] : [];
                    }
                    tempList.push(new GroupPolicy(item, 'add', 'custom', {
                        system: {
                            id: item.system_id,
                            name: item.system_name
                        },
                        id: CUSTOM_PERM_TEMPLATE_ID
                    }));
                });

                if (this.policyList.length < 1) {
                    this.policyList = _.cloneDeep(tempList);
                } else {
                    this.policyList.push(..._.cloneDeep(tempList));
                }
                this.tableListBackup = _.cloneDeep(this.policyList);
                // 处理聚合的数据，将表格数据按照相同的聚合id分配好
                this.handleAggregateData();
                this.$nextTick(() => {
                    if (hasDeleteTemplateList.length > 0 || this.hasDeleteCustomList.length > 0) {
                        this.setCurMapData(hasDeleteTemplateList);
                    }
                });
            },

            /**
             * handleResSelect
             */
            handleResSelect (index, resIndex, condition, groupIndex, resItem) {
                // debugger
                if (this.curMap && this.curMap.size > 0) {
                    const item = this.policyList[index];
                    const actions = this.curMap.get(item.aggregationId) || [];
                    const len = actions.length;
                    if (len > 0) {
                        for (let i = 0; i < len; i++) {
                            if (actions[i].id === item.id) {
                                // eslint-disable-next-line max-len
                                if (!actions[i].resource_groups[groupIndex]) {
                                    actions[i].resource_groups.push({ id: '', related_resource_types: resItem });
                                } else {
                                    // eslint-disable-next-line max-len
                                    actions[i].resource_groups[groupIndex].related_resource_types[resIndex].condition = _.cloneDeep(condition);
                                }
                                break;
                            }
                        }
                    }
                }
            },

            /**
             * handleAttrValueSelected
             */
            handleAttrValueSelected (payload) {
                window.changeDialog = true;
                const instances = (function () {
                    const arr = [];
                    payload.aggregateResourceType.forEach(resourceItem => {
                        const { id, name, system_id } = resourceItem;
                        payload.instancesDisplayData[id] && payload.instancesDisplayData[id].forEach(v => {
                            const curItem = arr.find(_ => _.type === id);
                            if (curItem) {
                                curItem.path.push([{
                                    id: v.id,
                                    name: v.name,
                                    system_id,
                                    type: id,
                                    type_name: name
                                }]);
                            } else {
                                arr.push({
                                    name,
                                    type: id,
                                    path: [[{
                                        id: v.id,
                                        name: v.name,
                                        system_id,
                                        type: id,
                                        type_name: name
                                    }]]
                                });
                            }
                        });
                    });
                    return arr;
                })();
                const curAction = payload.actions.map(item => `${payload.system_id}&${item.id}`);
                if (instances.length > 0) {
                    this.aggregationsTableData.forEach(item => {
                        if (curAction.includes(`${item.system_id}&${item.id}`)) {
                            item.resource_groups.forEach(groupItem => {
                                groupItem.related_resource_types
                                    && groupItem.related_resource_types.forEach(subItem => {
                                        subItem.condition = [new Condition({ instances }, '', 'add')];
                                    });
                            });
                        }
                    });
                }
            },

            /**
             * handleAggregateData
             */
            handleAggregateData () {
                // debugger
                this.allAggregationData = Object.assign(this.aggregationData, this.aggregationDataByCustom);
                const keys = Object.keys(this.allAggregationData);
                const data = {};
                keys.forEach(item => {
                    if (this.allAggregationData[item] && this.allAggregationData[item].length > 0) {
                        data[item] = this.allAggregationData[item];
                    }
                });
                this.allAggregationData = data;
                this.policyList.forEach(item => {
                    const aggregationData = this.allAggregationData[item.detail.system.id];
                    if (aggregationData && aggregationData.length) {
                        aggregationData.forEach(aggItem => {
                            if (aggItem.actions.map(act => act.id).includes(item.id)) {
                                // const existDatas = this.policyList.filter(sub => sub.judgeId === item.judgeId)
                                // const existDatas = this.policyList.filter(
                                //     sub => aggItem.actions.find(act => act.id === sub.id)
                                // )
                                const existDatas = this.policyList.filter(
                                    sub => aggItem.actions.find(act => act.id === sub.id)
                                        && sub.judgeId === item.judgeId
                                );
                                if (existDatas.length > 1) {
                                    const temp = existDatas.find(sub => sub.aggregationId !== '') || {};
                                    item.aggregationId = temp.aggregationId || guid();
                                    item.aggregateResourceType = aggItem.aggregate_resource_types;
                                }
                            }
                        });
                    }
                });
                const aggregationIds = this.policyList.reduce((counter, item) => {
                    return item.aggregationId !== '' ? counter.concat(item.aggregationId) : counter;
                }, []);
                console.warn('aggregationIds:');
                console.warn([...new Set(aggregationIds)]);
                if (!this.curMap) {
                    this.curMap = new Map();
                }
                this.policyList.forEach(item => {
                    if (item.aggregationId !== '') {
                        if (!this.curMap.has(item.aggregationId)) {
                            this.curMap.set(item.aggregationId, [_.cloneDeep(item)]);
                        } else {
                            const temps = this.curMap.get(item.aggregationId);
                            if (!temps.map(sub => sub.id).includes(item.id)) {
                                temps.push(_.cloneDeep(item));
                            }
                        }
                    }
                });
            },

            /**
             * setCurMapData
             */
            setCurMapData (payload = []) {
                const flag = String(Number(payload.length > 0)) + String(Number(this.hasDeleteCustomList.length > 0));
                const hasDeleteIds = payload.map(item => item.id);
                const hasDeleteIdsTemp = this.hasDeleteCustomList.map(_ => _.$id);
                const tempData = {};
                if (!this.curMap) {
                    this.curMap = new Map();
                }
                for (const [key, value] of this.curMap.entries()) {
                    tempData[key] = value;
                }
                const tempDataBackup = {};
                switch (flag) {
                    case '11':
                        for (const key in tempData) {
                            const value = tempData[key];
                            if (value[0].detail.id !== CUSTOM_PERM_TEMPLATE_ID) {
                                const tempValue = _.cloneDeep(value);
                                if (!value.every(item => hasDeleteIds.includes(item.detail.id))) {
                                    tempDataBackup[key] = tempValue;
                                }
                            }
                        }
                        for (const key in tempData) {
                            const value = tempData[key];
                            if (value[0].detail.id === CUSTOM_PERM_TEMPLATE_ID) {
                                let tempValue = _.cloneDeep(value);
                                tempValue = tempValue.filter(item => !hasDeleteIdsTemp.includes(`${item.detail.system.id}&${item.id}`));
                                if (tempValue.length > 0) {
                                    tempDataBackup[key] = tempValue;
                                }
                            }
                        }
                        break;
                    case '10':
                        for (const key in tempData) {
                            const value = tempData[key];
                            if (value[0].detail.id !== CUSTOM_PERM_TEMPLATE_ID) {
                                if (!value.every(item => hasDeleteIds.includes(item.detail.id))) {
                                    tempDataBackup[key] = value;
                                }
                            } else {
                                tempDataBackup[key] = value;
                            }
                        }
                        break;
                    case '01':
                        for (const key in tempData) {
                            const value = tempData[key];
                            if (value[0].detail.id === CUSTOM_PERM_TEMPLATE_ID) {
                                let tempValue = _.cloneDeep(value);
                                tempValue = tempValue.filter(item => !hasDeleteIdsTemp.includes(`${item.detail.system.id}&${item.id}`));
                                if (tempValue.length > 0) {
                                    tempDataBackup[key] = tempValue;
                                }
                            } else {
                                tempDataBackup[key] = value;
                            }
                        }
                        break;
                }
                this.curMap.clear();
                for (const key in tempDataBackup) {
                    this.curMap.set(key, _.cloneDeep(tempDataBackup[key]));
                }

                console.warn('curMap:', this.curMap);
                console.warn('policyList:', this.policyList);
            },

            async fetchAggregationAction (payload) {
                this.isLoading = true;
                try {
                    const res = await this.$store.dispatch('aggregate/getAggregateAction', { system_ids: payload });
                    (res.data.aggregations || []).forEach(item => {
                        item.$id = guid();
                    });
                    const data = this.getFilterAggregation(res.data.aggregations);
                    this.aggregationsBackup = _.cloneDeep(res.data.aggregations);
                    this.aggregations = _.cloneDeep(data);
                } catch (e) {
                    console.error(e);
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
                    });
                } finally {
                    this.isLoading = false;
                }
            },

            getFilterAggregation (payload) {
                const curSelectActions = [];
                this.policyList.forEach(item => {
                    if (item.isAggregate) {
                        curSelectActions.push(...item.actions.map(v => `${item.system_id}&${v.id}`));
                    } else {
                        curSelectActions.push(`${item.system_id}&${item.id}`);
                    }
                });
                const aggregations = [];
                (payload || []).forEach(item => {
                    const { actions, aggregate_resource_types, $id } = item;
                    const curActions = actions.filter(_ => curSelectActions.includes(`${_.system_id}&${_.id}`));
                    if (curActions.length > 0) {
                        aggregations.push({
                            actions: curActions,
                            aggregate_resource_types,
                            $id,
                            system_name: this.policyList.find(
                                _ => _.system_id === curActions[0].system_id
                            ).system_name
                        });
                    }
                });
                // aggregations = aggregations.filter(item => item.actions.length > 1);
                return aggregations;
            },

            resetData () {
                this.aggregations = [];
                this.aggregationsBackup = [];
            },

            /**
             * handleAggregateAction
             */

            handleAggregateAction (payload) {
                if (this.isAggregateDisabled) {
                    return;
                }
                this.isAllExpanded = payload;
                const tempData = [];
                let templateIds = [];
                let instancesDisplayData = {};
                if (payload) {
                    // debugger
                    this.policyList.forEach(item => {
                        if (!item.aggregationId) {
                            tempData.push(item);
                            templateIds.push(item.detail.id);
                        }
                    });
                    for (const [key, value] of this.curMap.entries()) {
                        if (value.length === 1) {
                            tempData.push(...value);
                        } else {
                            let curInstances = [];
                            const conditions = value.map(subItem =>
                                subItem.resource_groups && subItem.resource_groups[0]
                                    .related_resource_types[0].condition);
                            // 是否都选择了实例
                            const isAllHasInstance = conditions.every(subItem => subItem.length > 0 && subItem[0] !== 'none');
                            if (isAllHasInstance) {
                                const instances = conditions.map(subItem => subItem.map(v => v.instance));
                                let isAllEqual = true;
                                for (let i = 0; i < instances.length - 1; i++) {
                                    if (!_.isEqual(instances[i], instances[i + 1])) {
                                        isAllEqual = false;
                                        break;
                                    }
                                }
                                console.log('instances: ');
                                console.log(instances);
                                console.log('isAllEqual: ' + isAllEqual);
                                console.log('value', value);
                                if (isAllEqual) {
                                    // const instanceData = instances[0][0][0];
                                    // curInstances = instanceData.path.map(pathItem => {
                                    //     return {
                                    //         id: pathItem[0].id,
                                    //         name: pathItem[0].name
                                    //     };
                                    // });
                                    const instanceData = instances[0][0];
                                    console.log('instanceData', instanceData);
                                    curInstances = [];
                                    instanceData.forEach(pathItem => {
                                        const instance = pathItem.path.map(e => {
                                            return {
                                                id: e[0].id,
                                                name: e[0].name,
                                                type: e[0].type
                                            };
                                        });
                                        curInstances.push(...instance);
                                    });
                                    instancesDisplayData = this.setInstancesDisplayData(curInstances);
                                    console.log('instancesDisplayData', instancesDisplayData);
                                } else {
                                    curInstances = [];
                                }
                            } else {
                                curInstances = [];
                            }
                            tempData.push(new GroupAggregationPolicy({
                                aggregationId: key,
                                aggregate_resource_types: value[0].aggregateResourceType,
                                actions: value,
                                instances: curInstances,
                                instancesDisplayData
                            }));
                        }
                        templateIds.push(value[0].detail.id);
                    }
                } else {
                    this.policyList.forEach(item => {
                        if (item.hasOwnProperty('isAggregate') && item.isAggregate) {
                            const actions = this.curMap.get(item.aggregationId);
                            tempData.push(...actions);
                            templateIds.push(actions[0].detail.id);
                        } else {
                            tempData.push(item);
                            templateIds.push(item.detail.id);
                        }
                    });
                }
                // 为了合并单元格的计算，需将再次展开后的数据按照相同模板id重新排序组装一下
                const tempList = [];
                templateIds = [...new Set(templateIds)];
                templateIds.forEach(item => {
                    const list = tempData.filter(subItem => subItem.detail.id === item);
                    tempList.push(...list);
                });
                this.policyList = _.cloneDeep(tempList);
            },

            setInstancesDisplayData (data) {
                const instancesDisplayData = data.reduce((p, v) => {
                    if (!p[v['type']]) {
                        p[v['type']] = [];
                    }
                    p[v['type']].push({
                        id: v.id,
                        name: v.name
                    });
                    return p;
                }, {});
                return instancesDisplayData;
            },

            /**
             * handleEditCustom
             */
            handleEditCustom () {
                this.curActionValue = this.originalList.map(item => item.$id);
                this.isShowAddActionSideslider = true;
            },

            /**
             * handleSelectSubmit
             */
            handleSelectSubmit (payload, aggregation, authorization) {
                // debugger
                if (this.originalList.length > 0) {
                    const intersection = payload.filter(
                        item => this.originalList.map(sub => sub.$id).includes(item.$id)
                    );
                    this.hasDeleteCustomList = this.originalList.filter(
                        item => !intersection.map(sub => sub.$id).includes(item.$id)
                    );
                    // eslint-disable-next-line max-len
                    this.hasAddCustomList = payload.filter(item => !intersection.map(sub => sub.$id).includes(item.$id));
                } else {
                    this.hasAddCustomList = payload;
                }
                payload.forEach(item => {
                    if (!item.resource_groups || !item.resource_groups.length) {
                        item.resource_groups = item.related_resource_types.length ? [{ id: '', related_resource_types: item.related_resource_types }] : [];
                    }
                });
                this.originalList = _.cloneDeep(payload);
                this.aggregationDataByCustom = _.cloneDeep(aggregation);
                this.authorizationDataByCustom = _.cloneDeep(authorization);
                this.isShowActionEmptyError = false;
                this.$refs.addPermSideslider.handleSubmit();
                // this.handleSubmitPerm()
            },

            async handleSubmit () {
                const validatorFlag = this.$refs.basicInfoRef.handleValidator();
                let data = [];
                let flag = false;
                this.isShowActionEmptyError = this.originalList.length < 1;
                this.isShowReasonError = !this.reason;
                this.isShowMemberEmptyError = this.inheritSubjectScope ? false
                    : (this.users.length < 1 && this.departments.length < 1) && !this.isAll;
                if (!this.isShowActionEmptyError) {
                    data = this.$refs.resourceInstanceRef.handleGetValue().actions;
                    flag = this.$refs.resourceInstanceRef.handleGetValue().flag;
                }
                if (validatorFlag || flag || this.isShowActionEmptyError
                    || this.isShowMemberEmptyError) {
                    if (validatorFlag) {
                        this.scrollToLocation(this.$refs.basicInfoContentRef);
                    } else if (flag) {
                        this.scrollToLocation(this.$refs.instanceTableContentRef);
                    } else if (this.isShowMemberEmptyError) {
                        this.scrollToLocation(this.$refs.memberRef);
                    }
                    return;
                }
                if (this.isStaff) {
                    if (!this.reason) {
                        this.isShowReasonError = true;
                        this.scrollToLocation(this.$refs.reasonRef);
                        return;
                    }
                    this.submitLoading = true;
                    this.handleSubmitWithReason();
                    // this.isShowReasonDialog = true;
                    return;
                }
                const subjects = [];
                if (this.isAll) {
                    subjects.push({
                        id: '*',
                        type: '*'
                    });
                } else {
                    this.users.forEach(item => {
                        subjects.push({
                            type: 'user',
                            id: item.username
                        });
                    });
                    this.departments.forEach(item => {
                        subjects.push({
                            type: 'department',
                            id: item.id
                        });
                    });
                }
                const { name, description, members, sync_perm } = this.formData;
                const params = {
                    name,
                    description,
                    members,
                    subject_scopes: subjects,
                    authorization_scopes: data,
                    sync_perm: sync_perm,
                    inherit_subject_scope: this.inheritSubjectScope
                };
                // 如果是动态继承上级空间 组织架构可为空
                if (this.inheritSubjectScope) {
                    this.isShowMemberEmptyError = false;
                    params.subject_scopes = [];
                }
                window.changeDialog = false;
                this.submitLoading = true;
                console.log('params', params);
                // debugger;
                try {
                    await this.$store.dispatch('spaceManage/addSecondManager', params);
                    await this.$store.dispatch('roleList');
                    this.messageSuccess(this.$t(+this.id > 0 ? `m.info['克隆二级管理空间成功']` : `m.info['新建二级管理空间成功']`), 1000);
                    this.$router.go(-1);
                } catch (e) {
                    console.error(e);
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
                    });
                } finally {
                    this.submitLoading = false;
                }
            },

            /**
             * handleCancel
             */
            handleCancel () {
                // let cancelHandler = Promise.resolve();
                // if (window.changeDialog) {
                //     cancelHandler = leavePageConfirm();
                // }
                // cancelHandler.then(() => {
                //     this.$router.go(-1);
                // }, _ => _);
                this.$router.go(-1);
            },

            /**
             * handleAddMember
             */
            handleAddMember () {
                this.isShowAddMemberDialog = true;
            },

            /**
             * handleExpiredAtChange
             */
            handleExpiredAtChange (payload) {
                window.changeDialog = true;
                if (payload) {
                    this.isShowExpiredError = false;
                }
                if (payload !== PERMANENT_TIMESTAMP && payload) {
                    const nowTimestamp = +new Date() / 1000;
                    const tempArr = String(nowTimestamp).split('');
                    const dotIndex = tempArr.findIndex(item => item === '.');
                    const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
                    this.expired_at = payload + nowSecond;
                    return;
                }
                this.expired_at = payload;
            },

            /**
             * handleMemberDelete
             */
            handleMemberDelete (type, payload) {
                window.changeDialog = true;
                if (type === 'user') {
                    this.users.splice(payload, 1);
                } else {
                    this.departments.splice(payload, 1);
                }
                this.isShowMemberAdd = this.users.length < 1 && this.departments.length < 1;
            },

            /**
             * handleAddPerm
             */
            handleAddPerm () {
                this.handleAddCustom();
                // this.isShowAddSideslider = true;
            },

            /**
             * handleCancelAdd
             */
            handleCancelAdd () {
                this.isShowAddMemberDialog = false;
            },

            setAggregateExpanded () {
                const flag = this.policyList.every(item => !item.isAggregate);
                if (flag) {
                    this.isAllExpanded = false;
                }
            },

            handleDelete (systemId, actionId, payload, index) {
                window.changeDialog = true;
                this.originalList = this.originalList.filter(item => payload !== item.$id);
                this.policyList.splice(index, 1);
                for (let i = 0; i < this.aggregations.length; i++) {
                    const item = this.aggregations[i];
                    if (item.actions[0].system_id === systemId) {
                        item.actions = item.actions.filter(subItem => subItem.id !== actionId);
                        break;
                    }
                }
                this.aggregations = this.aggregations.filter(item => item.actions.length > 1);
                this.setAggregateExpanded();
            },

            handleDeleteResourceAll () {
                this.originalList = [];
                this.policyList = [];
                this.isAllExpanded = false;
            },

            handleAggregateDelete (systemId, actions, index) {
                window.changeDialog = true;
                this.policyList.splice(index, 1);
                const deleteAction = actions.map(item => `${systemId}&${item.id}`);
                this.originalList = this.originalList.filter(item => !deleteAction.includes(item.$id));
                this.aggregations = this.aggregations.filter(item =>
                    !(item.actions[0].system_id === systemId
                        && _.isEqual(item.actions.map(_ => _.id).sort(), actions.map(_ => _.id).sort()))
                );
                this.setAggregateExpanded();
            },

            /**
             * handleSubmitAdd
             */
            handleSubmitAdd (payload) {
                window.changeDialog = true;
                const { users, departments } = payload;
                this.users = _.cloneDeep(users);
                this.departments = _.cloneDeep(departments);
                this.isShowMemberAdd = false;
                this.isShowMemberEmptyError = false;
                this.isShowAddMemberDialog = false;
            },

            handleChange (payload) {
                this.inheritSubjectScope = payload;
                if (payload) {
                    this.users = [];
                    this.departments = [];
                }
            },

            handleReasonInput () {
                this.isShowReasonError = false;
            },

            handleReasonBlur (payload) {
                if (!payload) {
                    this.isShowReasonError = true;
                }
            }
        }
    };
</script>
<style lang="postcss" scoped>
    .iam-create-user-group-wrapper {
        /* padding-bottom: 68px; */
        margin-bottom: 36px;
        .add-perm-action {
            margin: 16px 0 20px 0;
        }
    }
    .grade-admin-select-wrapper {

        .action {
            position: relative;
            display: flex;
            justify-content: flex-start;
            .action-wrapper {
                font-size: 14px;
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
                i {
                    position: relative;
                    top: -1px;
                    left: 2px;
                }
            }
            .info-icon {
                margin: 2px 0 0 2px;
                color: #c4c6cc;
                &:hover {
                    color: #3a84ff;
                }
            }
        }
        .info-wrapper {
            display: flex;
            justify-content: flex-end;
            margin-top: 16px;
            line-height: 24px;
            .tips,
            .text {
                line-height: 20px;
                font-size: 12px;
            }
        }
    }

    .iam-create-user-group-wrapper {
        .grading-admin-render-perm-cls {
            margin-bottom: 16px;
        }
        .action-empty-error {
            position: relative;
            top: -40px;
            left: 160px;
            font-size: 12px;
            color: #ff4d4d;
        }

        .grade-admin-select-wrapper {
            .action {
                position: relative;
                display: flex;
                justify-content: flex-start;
                .action-wrapper {
                    margin-left: 8px;
                    font-size: 14px;
                    color: #3a84ff;
                    cursor: pointer;
                    &:hover {
                        color: #699df4;
                    }
                    i {
                        position: relative;
                        top: -1px;
                        left: 2px;
                    }
                }
                .info-icon {
                    margin: 2px 0 0 2px;
                    color: #c4c6cc;
                    &:hover {
                        color: #3a84ff;
                    }
                }
            }
            .sub-title {
                margin-top:10px;
                margin-left:10px;
                font-size:14px;
                color: #979ba5;
                .number {
                    font-weight: 600;
                }
            }
            .info-wrapper {
                display: flex;
                justify-content: space-between;
                margin-top: 16px;
                margin-left: 8px;
                line-height: 24px;
                .tips,
                .text {
                    line-height: 20px;
                    font-size: 12px;
                }
            }
            .resource-instance-wrapper {
                margin-left: 8px;
                min-height: 200px;
            }
            .loading-resource-instance-cls {
                border: 1px solid #c4c6cc;
            }
        }
    }
    .iam-create-rate-manager-reason-dialog {
        .content-wrapper {
            display: flex;
            justify-content: flex-start;
            label {
                display: block;
                width: 70px;
                span {
                    color: #ea3636;
                }
            }
        }
    }
</style>

<style lang="postcss" scoped>
@import '@/css/mixins/authorize-boundary.css';
</style>
