<template>
    <div class="iam-user-group-perm-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="!groupAttributes.source_from_role">
            <template v-if="externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle">
                <bk-button
                    v-if="!isLoading && isEditMode && !groupAttributes.source_type"
                    theme="primary"
                    style="margin-bottom: 16px"
                    @click="handleAddPerm">
                    {{ $t(`m.common['添加权限']`) }}
                </bk-button>
            </template>
            <template v-if="!externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle">
                <bk-button
                    v-if="!isLoading && isEditMode"
                    theme="primary"
                    style="margin-bottom: 16px"
                    @click="handleAddPerm">
                    {{ $t(`m.common['添加权限']`) }}
                </bk-button>
            </template>
        </template>
        <template v-if="!isLoading && !isEmpty">
            <render-perm-item
                data-test-id="myPerm_list_permItem"
                v-for="(item, index) in groupSystemList"
                :key="item.id"
                :expanded.sync="item.expanded"
                :ext-cls="index > 0 ? 'iam-perm-ext-cls' : ''"
                :class="index === groupSystemList.length - 1 ? 'iam-perm-ext-reset-cls' : ''"
                :title="item.name"
                :policy-count="item.custom_policy_count"
                :template-count="item.template_count"
                :group-system-list-length="groupSystemListLength"
                @on-expanded="handleExpanded(...arguments, item)">
                <div style="min-height: 60px;" v-bkloading="{ isLoading: item.loading, opacity: 1 }">
                    <div v-if="!item.loading">
                        <render-template-item
                            data-test-id="myPerm_list_templateItem"
                            :ref="`rTemplateItem${item.id}`"
                            v-for="(subItem, subIndex) in item.templates"
                            :key="subIndex"
                            :title="subItem.name"
                            :count="subItem.count"
                            :external-edit="formatOperate"
                            :external-delete="formatOperate"
                            :is-edit="subItem.isEdit"
                            :loading="subItem.editLoading"
                            :expanded.sync="subItem.expanded"
                            :mode="isEditMode ? 'edit' : 'detail'"
                            @on-delete="handleDelete(item, subItem)"
                            @on-save="handleSave(item, index, subItem, subIndex)"
                            @on-edit="handleEdit(subItem)"
                            @on-cancel="handleCancel(subItem)"
                            @on-expanded="handleTemplateExpanded(...arguments, subItem)">
                            <div style="min-height: 136px;"
                                v-bkloading="{ isLoading: subItem.loading, opacity: 1 }">
                                <render-instance-table
                                    data-test-id="myPerm_list_instanceTable"
                                    v-if="!subItem.loading"
                                    mode="detail"
                                    :is-custom="subItem.count > 0"
                                    :ref="`${index}_${subIndex}_resourceTableRef`"
                                    :list="subItem.tableData"
                                    :original-list="subItem.tableDataBackup"
                                    :authorization="authorizationData"
                                    :system-id="item.id"
                                    :group-id="groupId"
                                    :template-id="subItem.id"
                                    :is-edit="subItem.isEdit"
                                    :external-delete="!!groupAttributes.source_type"
                                    :linear-action-list="linearActionList"
                                    @on-delete="handleSingleDelete(...arguments, item)" />
                            </div>
                        </render-template-item>
                    </div>
                </div>
            </render-perm-item>
        </template>
        <template v-if="!isLoading && isEmpty">
            <div class="empty-wrapper">
                <!-- <iam-svg />
                <p class="text">{{ $t(`m.common['暂无数据']`) }}</p> -->
                <ExceptionEmpty
                    :type="emptyData.type"
                    :empty-text="emptyData.text"
                    :tip-text="emptyData.tip"
                    :tip-type="emptyData.tipType"
                    @on-refresh="handleEmptyRefresh"
                />
            </div>
        </template>
    </div>
</template>
<script>
    import _ from 'lodash';
    import { mapGetters } from 'vuex';
    import { formatCodeData } from '@/common/util';
    import GroupPolicy from '@/model/group-policy';
    import RenderPermItem from '../common/render-perm-item-new.vue';
    import RenderTemplateItem from '../common/render-template-item.vue';
    import RenderInstanceTable from '../components/render-instance-table.vue';
    // import GroupAggregationPolicy from '@/model/group-aggregation-policy'
    // import store from '@/store'
    const CUSTOM_CUSTOM_TEMPLATE_ID = 0;

    export default {
        name: '',
        components: {
            RenderPermItem,
            RenderTemplateItem,
            RenderInstanceTable
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
                groupSystemListLength: '',
                removingSingle: false,
                isPermTemplateDetail: false,
                role: '',
                // source_type == openapi, 那就是接口创建的, 在蓝盾上面不能修改权限, 如果是空就可以用户编辑权限
                // 只要 source_from_role = true, 不能改权限, 不能添加部门, 不区分是iam的页面还是蓝盾的页面
                groupAttributes: {
                    source_type: '',
                    source_from_role: false
                },
                emptyData: {
                    type: '',
                    text: '',
                    tip: '',
                    tipType: ''
                }
            };
        },
        computed: {
            ...mapGetters(['user', 'externalSystemsLayout', 'externalSystemId']),
            isEmpty () {
                return this.groupSystemList.length < 1;
            },
            isEditMode () {
                return this.mode === 'edit';
            },
            expandedText () {
                return this.isAllExpanded ? this.$t(`m.grading['逐项编辑']`) : this.$t(`m.grading['批量编辑']`);
            },
            canEditGroup () {
                return this.$route.query.edit === 'GroupEdit';
            },
            formatOperate () {
                let result = true;
                if (this.externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle) {
                    result = !(!this.groupAttributes.source_from_role && !this.groupAttributes.source_type);
                } else {
                    result = !!this.groupAttributes.source_from_role;
                }
                return result;
            }
        },
        watch: {
            id: {
                handler (value) {
                    this.groupId = value;
                    this.handleInit();
                    this.fetchDetail(value);
                },
                immediate: true
            },
            mode: {
                handler (value) {
                    console.log('value', value);
                    window.parent.postMessage({ type: 'IAM', data: { tab: 'group_perm' }, code: 'change_group_detail_tab' }, '*');
                },
                immediate: true
            }
        },
        methods: {
            async handleInit () {
                this.isLoading = true;
                this.$emit('on-init', true);
                try {
                    const params = {
                        id: this.groupId
                    };
                    if (this.externalSystemId) {
                        params.hidden = false;
                    }
                    const { code, data } = await this.$store.dispatch('userGroup/getGroupSystems', params);
                    (data || []).forEach(item => {
                        item.expanded = false; // 此处会在子组件更新为true
                        item.loading = false;
                        item.templates = []; // 在getGroupTemplateList方法赋值
                    });
                    this.groupSystemList = data; // groupSystemList会通过handleExpanded调用其他方法做属性的添加
                    this.groupSystemListLength = data.length;
                    this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
                } catch (e) {
                    console.error(e);
                    const { code, data, message, statusText } = e;
                    this.emptyData = formatCodeData(code, this.emptyData);
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: message || data.msg || statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
                    });
                } finally {
                    this.isLoading = false;
                    this.$emit('on-init', false);
                }
            },

            async fetchDetail (payload) {
                if (this.$parent.fetchDetail) {
                    const { data } = await this.$parent.fetchDetail(payload);
                    const { attributes } = data;
                    if (Object.keys(attributes).length) {
                        this.groupAttributes = Object.assign(this.groupAttributes, attributes);
                    }
                }
            },

            handleAddPerm () {
                window.changeAlert = false;
                if (this.externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle) {
                    const { source, role_id, system_id } = this.$route.query;
                    this.$router.push({
                        name: 'addGroupPerm',
                        params: {
                            id: this.id
                        },
                        query: {
                            source,
                            role_id,
                            system_id
                        }
                    });
                } else {
                    this.$router.push({
                        name: 'addGroupPerm',
                        params: {
                            id: this.id
                        }
                    });
                }
            },

            handleEdit (paylaod) {
                this.$set(paylaod, 'isEdit', true); // 事件会冒泡会触发handleExpanded方法
            },

            handleCancel (paylaod) {
                this.$set(paylaod, 'isEdit', false);
            },

            async getGroupTemplateList (groupSystem) {
                groupSystem.loading = true;
                let res;
                try {
                    res = await this.$store.dispatch('userGroup/getUserGroupTemplateList', {
                        id: this.groupId,
                        systemId: groupSystem.id
                    });

                    res.data.forEach(item => {
                        item.loading = false;
                        item.tableData = [];
                        item.tableDataBackup = [];
                        item.count = 0;
                        item.editLoading = false;
                        item.deleteLoading = false;
                    });
                    groupSystem.templates = res.data; // 赋值给展开项
                    if (groupSystem.custom_policy_count
                        && !this.externalSystemsLayout.userGroup.groupDetail.hideCustomPerm) {
                        groupSystem.templates.push({
                            name: this.$t(`m.perm['自定义权限']`),
                            id: CUSTOM_CUSTOM_TEMPLATE_ID, // 自定义权限 id 为 0
                            system: {
                                id: groupSystem.id,
                                name: groupSystem.name
                            },
                            count: groupSystem.custom_policy_count,
                            loading: false,
                            tableData: [],
                            tableDataBackup: [],
                            editLoading: false,
                            deleteLoading: false
                        });
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
                } finally {
                    groupSystem.loading = false;
                    if (!this.externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle) {
                        if (res.data.length === 1) {
                            this.$nextTick(() => {
                                this.$refs[`rTemplateItem${groupSystem.id}`] && this.$refs[`rTemplateItem${groupSystem.id}`][0].handleExpanded();
                            });
                        }
                    } else {
                        this.$nextTick(() => {
                            this.$refs[`rTemplateItem${groupSystem.id}`] && this.$refs[`rTemplateItem${groupSystem.id}`][0].handleExpanded();
                        });
                    }
                }
            },

            // 进入之后会在子组件中触发执行
            handleExpanded (flag, item) {
                if (!flag) {
                    return;
                }
                this.getGroupTemplateList(item);
                this.fetchAuthorizationScopeActions(item.id);
            },

            async fetchAuthorizationScopeActions (id) {
                if (this.authorizationData[id]) {
                    return;
                }
                try {
                    const res = await this.$store.dispatch('permTemplate/getAuthorizationScopeActions', { systemId: id });
                    this.authorizationData[id] = res.data.filter(item => item.id !== '*');
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

            /**
             * @description: 子item
             * @param {*} flag
             * @param {*} item
             * @return {*}
             */
            async handleTemplateExpanded (flag, item) {
                if (!flag) {
                    this.$set(item, 'isEdit', false);
                    return;
                }
                // count > 0 说明是自定义权限
                await this.fetchActions(item);
                if (item.count > 0) {
                    this.getGroupCustomPolicy(item);
                    return;
                }
                this.getGroupTemplateDetail(item);
            },

            /**
             * 获取系统对应的自定义操作
             *
             * @param {String} systemId 系统id
             * 执行handleActionLinearData方法
             */
            async fetchActions (item) {
                const params = {
                    system_id: item.system.id,
                    user_id: this.user.username
                };
                try {
                    const res = await this.$store.dispatch('permApply/getActions', params);
                    this.originalCustomTmplList = _.cloneDeep(res.data);
                    this.handleActionLinearData();
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

            handleActionLinearData () {
                const linearActions = [];
                this.originalCustomTmplList.forEach((item, index) => {
                    item.actions.forEach(act => {
                        linearActions.push(act);
                    });
                    (item.sub_groups || []).forEach(sub => {
                        sub.actions.forEach(act => {
                            linearActions.push(act);
                        });
                    });
                });

                this.linearActionList = _.cloneDeep(linearActions);
                console.log('this.linearActionList', this.linearActionList);
            },

            async getGroupTemplateDetail (item) {
                item.loading = true;
                try {
                    const res = await this.$store.dispatch('userGroup/getGroupTemplateDetail', {
                        id: this.groupId,
                        templateId: item.id
                    });

                    // // mock数据
                    // res.data.actions.forEach(element => {
                    //     element.resource_groups = [{
                    //         id: 1,
                    //         related_resource_types: element.related_resource_types
                    //     }]
                    // })
                    const tableData = res.data.actions.map(row => {
                        const linearActionList = this.linearActionList.find(sub => sub.id === row.id);
                        // eslint-disable-next-line max-len
                        row.related_environments = linearActionList ? linearActionList.related_environments : [];
                        return new GroupPolicy(
                            { ...row, policy_id: 1 },
                            'detail',
                            'template',
                            { system: res.data.system }
                        );
                    });
                    const tableDataBackup = res.data.actions.map(row => {
                        const linearActionList = this.linearActionList.find(sub => sub.id === row.id);
                        // eslint-disable-next-line max-len
                        row.related_environments = linearActionList ? linearActionList.related_environments : [];
                        return new GroupPolicy(
                            { ...row, policy_id: 1 },
                            'detail',
                            'template',
                            { system: res.data.system }
                        );
                    });
                    this.$set(item, 'tableData', tableData);
                    console.log('item.tableData', item.tableData);
                    this.$set(item, 'tableDataBackup', tableDataBackup);
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
                    item.loading = false;
                }
            },

            async getGroupCustomPolicy (item) {
                item.loading = true;
                try {
                    const res = await this.$store.dispatch('userGroup/getGroupPolicy', {
                        id: this.groupId,
                        systemId: item.system.id
                    });
                    const tableData = res.data.map(row => {
                        const linearActionList = this.linearActionList.find(sub => sub.id === row.id);
                        // eslint-disable-next-line max-len
                        row.related_environments = linearActionList ? linearActionList.related_environments : [];
                        return new GroupPolicy(
                            row,
                            'detail', // 此属性为flag，会在related-resource-types赋值为add
                            'custom',
                            { system: item.system }
                        );
                    });
                    const tableDataBackup = res.data.map(row => {
                        const linearActionList = this.linearActionList.find(sub => sub.id === row.id);
                        // eslint-disable-next-line max-len
                        row.related_environments = linearActionList ? linearActionList.related_environments : [];
                        return new GroupPolicy(
                            row,
                            'detail',
                            'custom',
                            { system: item.system }
                        );
                    });
                    this.$set(item, 'tableData', tableData);
                    this.$set(item, 'tableDataBackup', tableDataBackup);

                    console.log('itemTableData', item);
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
                    item.loading = false;
                }
            },

            async handleSave (item, index, subItem, subIndex) {
                const $ref = this.$refs[`${index}_${subIndex}_resourceTableRef`][0];
                const { flag, actions } = $ref.getDataByNormal();
                if (flag) {
                    return;
                }
                subItem.editLoading = true;
                try {
                    await this.$store.dispatch('userGroup/updateGroupPolicy', {
                        id: this.groupId,
                        data: {
                            system_id: item.id,
                            template_id: subItem.id,
                            actions
                        }
                    });
                    if (subItem.count > 0) {
                        this.getGroupCustomPolicy(subItem);
                    } else {
                        this.getGroupTemplateDetail(subItem);
                    }
                    subItem.isEdit = false;
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
                    subItem.editLoading = false;
                }
            },
            handleDelete (item, subItem) {
                this.removingSingle = false;
                if (subItem.id > 0) {
                    this.deleteTempalte({
                        id: subItem.id,
                        data: {
                            members: [{
                                type: 'group',
                                id: this.groupId
                            }]
                        }
                    }, item, subItem);
                } else {
                    this.deleteGroupPolicy({
                        id: this.groupId,
                        data: {
                            system_id: item.id,
                            ids: subItem.tableData.map(item => item.policy_id).join(',')
                        }
                    }, item, subItem, true);
                }
            },

            async deleteTempalte (params = {}, item, subItem) {
                subItem.deleteLoading = true;
                try {
                    await this.$store.dispatch('permTemplate/deleteTemplateMember', params);
                    let filterLen = item.templates.filter(item => item.id !== CUSTOM_CUSTOM_TEMPLATE_ID).length;
                    const isExistCustom = item.templates.some(item => item.id === CUSTOM_CUSTOM_TEMPLATE_ID);
                    if (filterLen > 0) {
                        --filterLen;
                        --item.template_count;
                    }
                    if (filterLen > 0 || isExistCustom) {
                        this.getGroupTemplateList(item);
                    }
                    if (!filterLen && !isExistCustom) {
                        this.handleInit();
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
                } finally {
                    subItem.deleteLoading = false;
                }
            },

            async deleteGroupPolicy (params = {}, item, subItem, flag) {
                if (flag) {
                    subItem.deleteLoading = true;
                }
                try {
                    await this.$store.dispatch('userGroup/deleteGroupPolicy', params);
                    const isExistTemplate = item.templates.some(item => item.id !== CUSTOM_CUSTOM_TEMPLATE_ID);
                    if (item.custom_policy_count > 0 && this.removingSingle) {
                        --item.custom_policy_count;
                    } else {
                        item.custom_policy_count = 0;
                    }
                    this.policyList = subItem;
                    if (isExistTemplate) {
                        this.getGroupTemplateList(item);
                    } else {
                        this.handleInit();
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
                } finally {
                    if (flag) {
                        subItem.deleteLoading = false;
                    }
                }
            },

            handleSingleDelete (data, item) {
                this.removingSingle = true;
                this.deleteGroupPolicy({
                    id: this.groupId,
                    data: {
                        system_id: item.id,
                        ids: data.policy_id
                    }
                }, item, {}, false);
            }
        }
    };
</script>
<style lang="postcss">
    .iam-user-group-perm-wrapper {
        position: relative;
        min-height: calc(100vh - 211px);
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
