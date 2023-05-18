<template>
    <bk-sideslider
        :is-show="isShow"
        :quick-close="true"
        :width="permSideWidth"
        ext-cls="iam-add-group-perm-sideslider"
        :title="$t(`m.userGroup['添加组权限']`)"
        @update:isShow="handleCancel">
        <div slot="content" class="content-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
            <section v-show="!isLoading">
                <div class="template-content-wrapper">
                    <render-search>
                        <div class="search-title">
                            {{ $t(`m.info['从权限模板选择添加：']`) }}{{ $t(`m.common['已选择']`) }}
                            <span style="color: #2dcb56;">{{ currentSelectList.length }}</span>
                            {{ $t(`m.common['条']`) }}
                        </div>
                        <div slot="right">
                            <div class="add-button" v-if="!externalTemplate && !isSubset">
                                <bk-button
                                    size="small"
                                    text
                                    icon="plus"
                                    theme="primary"
                                    @click="handleGoToAdd">
                                    {{ $t(`m.common['新增模板']`) }}
                                </bk-button>
                            </div>
                            <iam-search-select
                                ref="iamSearchSelect"
                                @on-change="handleSearch"
                                :data="searchData"
                                :value="searchValue"
                                :quick-search-method="quickSearchMethod"
                                style="width: 240px; display: inline-block;" />
                            <div class="refresh-wrapper"
                                v-bk-tooltips="$t(`m.common['刷新']`)"
                                @click="handleRefresh">
                                <Icon type="refresh" />
                            </div>
                        </div>
                    </render-search>
                    <!-- eslint-disable max-len -->
                    <bk-table
                        ref="permTemplateTableRef"
                        :data="tableList"
                        size="small"
                        ext-cls="perm-template-table"
                        :outer-border="false"
                        :header-border="false"
                        :pagination="pagination"
                        data-test-id="group_table_selectPermTemplate"
                        @page-change="handlePageChange"
                        @page-limit-change="handleLimitChange"
                        @select="handlerChange"
                        v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
                        <bk-table-column type="selection" align="center" :selectable="getIsSelect"></bk-table-column>
                        <bk-table-column :label="$t(`m.permTemplate['模板名']`)">
                            <template slot-scope="{ row }">
                                <bk-popover placement="top" :delay="[300, 0]" ext-cls="iam-tooltips-cls">
                                    <template>
                                        <Icon v-if="row.need_to_update" type="error-fill" class="error-icon" />
                                    </template>
                                    <div slot="content" class="iam-perm-apply-action-popover-content">
                                        {{ $t(`m.permTemplate['该模板无法选择的原因是：管理空间缩小了授权范围，但是没有同步删除模板里的操作，如需选择请重新编辑模板或者创建新的模板。']`) }}
                                        <bk-button
                                            text
                                            :loading="editLoading"
                                            @click="handleEdit(row)">
                                            {{ $t(`m.common['去编辑']`) }}
                                        </bk-button>
                                    </div>
                                </bk-popover>
                                <span class="perm-template-name" :title="row.name" @click="handleViewTemplateDetail(row)">{{ row.name }}</span>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t(`m.common['所属系统']`)">
                            <template slot-scope="{ row }">
                                <span :title="row.system.name">{{ row.system.name }}</span>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t(`m.common['描述']`)">
                            <template slot-scope="{ row }">
                                <span :title="row.description !== '' ? row.description : ''">{{ row.description || '--' }}</span>
                            </template>
                        </bk-table-column>
                        <template slot="empty">
                            <ExceptionEmpty
                                :type="emptyData.type"
                                :empty-text="emptyData.text"
                                :tip-text="emptyData.tip"
                                :tip-type="emptyData.tipType"
                                @on-clear="handleEmptyClear"
                                @on-refresh="handleRefresh"
                            />
                        </template>
                    </bk-table>
                </div>
                <div class="custom-perm-wrapper">
                    <template v-if="customPerm.length > 0">
                        <label class="title">{{ $t(`m.perm['自定义权限']`) }}</label>
                        <p class="selected-info">
                            {{ $t(`m.common['已选择']`) }}
                            {{ sysCount }}
                            {{ $t(`m.common['个']`) }}
                            {{ $t(`m.common['系统']`) }},
                            {{ actionCount }}
                            {{ $t(`m.common['个']`) }}
                            {{ $t(`m.common['操作']`) }}
                            <bk-button style="margin-left: 5px;" text theme="primary" @click="handleEditCustomPerm" data-test-id="group_btn_editCustomPerm">
                                {{ $t(`m.common['编辑']`) }}
                            </bk-button>
                        </p>
                    </template>
                    <template v-else>
                        {{ $t(`m.info['没有在模板中找到']`) }}, {{ $t(`m.common['也可']`) }}
                        <bk-button style="margin-left: 5px;" text theme="primary" @click="handleAddCustomPerm" data-test-id="group_btn_addCustomPerm">
                            {{ $t(`m.info['添加自定义权限']`) }}
                        </bk-button>
                    </template>
                </div>
            </section>
        </div>
        <div slot="footer" style="padding-left: 22px;">
            <bk-button theme="primary" :disabled="isDisabled" @click="handleSubmit" data-test-id="group_btn_addGroupConfirm">{{ $t(`m.common['确定']`) }}</bk-button>
            <bk-button @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
        </div>
    </bk-sideslider>
</template>

<script>
    import _ from 'lodash';
    import IamSearchSelect from '@/components/iam-search-select';
    import { leaveConfirm } from '@/common/leave-confirm';
    import { fuzzyRtxSearch } from '@/common/rtx';
    import { formatCodeData } from '@/common/util';
    import { mapGetters } from 'vuex';

    export default {
        name: '',
        components: {
            IamSearchSelect
        },
        props: {
            isShow: {
                type: Boolean,
                default: false
            },
            customPerm: {
                type: Array,
                default: () => []
            },
            template: {
                type: Array,
                default: () => []
            },
            aggregation: {
                type: Object,
                default: () => {
                    return {};
                }
            },
            authorization: {
                type: Object,
                default: () => {
                    return {};
                }
            },
            groupId: {
                type: [String, Number],
                default: ''
            },
            externalTemplate: {
                type: Boolean,
                default: false
            },
            permSideWidth: {
                type: Number,
                default: 890
            }
        },
        data () {
            return {
                isLoading: false,
                tableList: [],
                tableLoading: false,
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10,
                    showSelectionCount: false
                },
                currentBackup: 1,
                searchValue: [],
                currentSelectList: [],
                searchParams: {},
                sysCount: 0,
                actionCount: 0,
                curSelectedSystem: [],
                curSelectedTemplate: [],
                tempalteDetailList: [],
                aggregationData: {},
                authorizationScope: {},
                requestQueueBySys: [],
                requestQueueByTemplate: [],
                selectLength: '',
                selection: [],
                emptyData: {
                    type: '',
                    text: '',
                    tip: '',
                    tipType: ''
                }
            };
        },
        computed: {
            ...mapGetters(['user', 'externalSystemId']),
            isSubset () {
                return this.user.role.type === 'subset_manager';
            },
            isDisabled () {
                return this.requestQueueBySys.length > 0 || this.requestQueueByTemplate.length > 0;
            }
        },
        watch: {
            customPerm: {
                handler (value) {
                    this.actionCount = value.length;
                    this.sysCount = [...new Set(value.map(item => item.system_id))].length;
                },
                immediate: true
            },
            aggregation: {
                handler (value) {
                    this.aggregationData = _.cloneDeep(value);
                    this.curSelectedSystem = Object.keys(this.aggregationData);
                },
                immediate: true
            },
            authorization: {
                handler (value) {
                    this.authorizationScope = _.cloneDeep(value);
                },
                immediate: true
            },
            template: {
                handler (value) {
                    this.tempalteDetailList = _.cloneDeep(value);
                    this.curSelectedTemplate = this.tempalteDetailList.map(item => item.id);
                },
                immediate: true
            },
            isShow: {
                handler (value) {
                    if (value) {
                        this.pageChangeAlertMemo = window.changeAlert;
                        window.changeAlert = 'iamSidesider';
                        this.resetData();
                        this.currentSelectList = this.template.map(item => item.id);
                        this.fetchData(false, true);
                    } else {
                        window.changeAlert = this.pageChangeAlertMemo;
                        this.selection = [];
                    }
                },
                immediate: true
            },
            'pagination.current' (value) {
                this.currentBackup = value;
            },
            currentSelectList: {
                handler (value) {
                    this.selectLength = value.length;
                },
                immediate: true
            }
        },
        created () {
            this.pageChangeAlertMemo = false;
            this.searchData = [
                {
                    id: 'name',
                    name: this.$t(`m.permTemplate['模板名']`),
                    default: true
                },
                {
                    id: 'system_id',
                    name: this.$t(`m.common['所属系统']`),
                    remoteMethod: this.handleRemoteSystem
                },
                {
                    id: 'creator',
                    name: this.$t(`m.grading['创建人']`),
                    remoteMethod: this.handleRemoteRtx
                },
                {
                    id: 'description',
                    name: this.$t(`m.common['描述']`),
                    disabled: true
                }
            ];
        },
        methods: {
            async fetchData (tableLoading = false, loading = false) {
                this.tableLoading = tableLoading;
                this.isLoading = loading;
                const params = {
                    ...this.searchParams,
                    limit: this.pagination.limit,
                    offset: this.pagination.limit * (this.pagination.current - 1)
                };
                if (this.groupId) {
                    params.group_id = this.groupId;
                }
                try {
                    const { code, data } = await this.$store.dispatch('permTemplate/getTemplateList', params);
                    this.pagination.count = data.count;
                    this.tableList.splice(0, this.tableList.length, ...(data.results || []));
                    this.$nextTick(() => {
                        this.tableList.forEach(item => {
                            if (this.currentSelectList.includes(item.id)) {
                                this.$refs.permTemplateTableRef.toggleRowSelection(item, true);
                            }
                        });
                    });
                    this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
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
                    this.tableLoading = false;
                    this.isLoading = false;
                }
            },

            getIsSelect (row, index) {
                return row.tag === 'unchecked' && !row.need_to_update && !this.isDisabled;
            },

            handleEmptyClear () {
                this.searchParams = {};
                this.searchValue = [];
                this.searchList = [];
                this.emptyData.tipType = '';
                this.$refs.iamSearchSelect.$refs.searchSelect.isTagMultLine = false;
                this.resetPagination();
                this.fetchData(true);
            },

            handleRefresh () {
                window.changeAlert = true;
                this.pagination = Object.assign({}, {
                    current: 1,
                    count: 0,
                    limit: 10,
                    showSelectionCount: false
                });
                this.currentBackup = 1;
                this.currentSelectList = [];
                this.requestQueueBySys = [];
                this.requestQueueByTemplate = [];
                this.selection = [];
                this.fetchData(true);
            },

            handleGoToAdd () {
                window.open(`${window.SITE_URL}perm-template-create`, '_blank');
            },

            resetData () {
                this.pagination = Object.assign({}, {
                    current: 1,
                    count: 0,
                    limit: 10,
                    showSelectionCount: false
                });
                this.currentBackup = 1;
                this.searchValue = [];
                this.currentSelectList = [];
                this.searchParams = {};
            },

            handleCancel () {
                if (this.selectLength !== 0) {
                    let cancelHandler = Promise.resolve();
                    if (window.changeAlert) {
                        cancelHandler = leaveConfirm();
                    }
                    cancelHandler.then(() => {
                        this.$emit('update:isShow', false);
                        this.resetData();
                    }, _ => _);
                } else {
                    this.$emit('update:isShow', false);
                }
            },

            handleSubmit () {
                this.$emit('update:isShow', false);
                this.$emit('on-submit', this.tempalteDetailList, this.aggregationData, this.authorizationScope);
            },

            handleAddCustomPerm () {
                window.changeAlert = true;
                this.$emit('on-add-custom', '');
            },

            handleEditCustomPerm () {
                window.changeAlert = true;
                this.$emit('on-edit-custom');
            },

            handleViewTemplateDetail (payload) {
                this.$emit('on-view', payload);
            },

            handleRemoteRtx (value) {
                return fuzzyRtxSearch(value)
                    .then(data => {
                        return data.results;
                    });
            },

            handleRemoteSystem (value) {
                const params = {};
                if (this.externalSystemId) {
                    params.hidden = false;
                }
                return this.$store.dispatch('system/getSystems', params)
                    .then(({ data }) => {
                        return data.map(({ id, name }) => ({ id, name })).filter(item => item.name.indexOf(value) > -1);
                    });
            },

            handlePageChange (page) {
                if (this.currentBackup === page) {
                    return;
                }
                window.changeAlert = true;
                this.pagination.current = page;
                this.fetchData(true);
            },

            handleLimitChange (currentLimit, prevLimit) {
                window.changeAlert = true;
                this.pagination.limit = currentLimit;
                this.pagination.current = 1;
                this.fetchData(true);
            },

            async handlerChange (selection, row) {
                window.changeAlert = true;
                if (!this.curSelectedTemplate.includes(row.id)) {
                    const obj = {};
                    this.selection = [...this.selection, ...selection].reduce((pre, item) => {
                        // eslint-disable-next-line no-unused-expressions
                        obj[item.id] ? '' : obj[item.id] = true && pre.push(item);
                        return pre;
                    }, []);
                } else {
                    this.selection = this.selection.filter(item => item.id !== row.id);
                }
                const checked = this.selection.length >= this.currentSelectList.length;
                this.currentSelectList = [...selection.map(item => item.id)];
                if (checked) {
                    if (!this.curSelectedSystem.includes(row.system.id)) {
                        this.curSelectedSystem.push(row.system.id);
                        this.requestQueueBySys = ['aggregation', 'authorization'];
                        this.fetchAggregationAction(row.system.id);
                        this.fetchAuthorizationScopeActions(row.system.id);
                    }
                    if (!this.curSelectedTemplate.includes(row.id)) {
                        this.curSelectedTemplate.push(row.id);
                        this.requestQueueByTemplate = ['templateDetail'];
                        this.fetchTemplateDetail(row.id);
                    }
                } else {
                    this.curSelectedSystem = this.curSelectedSystem.filter(item => item !== row.system.id);
                    this.curSelectedTemplate = this.curSelectedTemplate.filter(item => item !== row.id);

                    this.tempalteDetailList = this.tempalteDetailList.filter(item => item.id !== row.id);
                    delete this.aggregationData[row.id];
                    delete this.authorizationScope[row.id];
                }

                const selected = this.tempalteDetailList.map(item => item.id);
                this.currentSelectList.push(...selected);
                this.currentSelectList = [...new Set(this.currentSelectList)];
            },

            async fetchAuthorizationScopeActions (id) {
                try {
                    const res = await this.$store.dispatch(
                        'permTemplate/getAuthorizationScopeActions',
                        { systemId: id }
                    );
                    this.authorizationScope[id] = res.data.filter(item => item.id !== '*');
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
                    this.requestQueueBySys.shift();
                }
            },

            async fetchTemplateDetail (id) {
                try {
                    const res = await this.$store.dispatch('permTemplate/getTemplateDetail', { id, grouping: false });
                    this.tempalteDetailList.push(res.data);
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
                    this.requestQueueByTemplate.shift();
                }
            },

            async fetchAggregationAction (id) {
                try {
                    const res = await this.$store.dispatch('aggregate/getAggregateAction', { system_ids: id });
                    this.aggregationData[id] = res.data.aggregations;
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
                    this.requestQueueBySys.shift();
                }
            },

            handleSearch (payload, result) {
                window.changeAlert = true;
                this.searchParams = payload;
                this.searchList = result;
                this.emptyData.tipType = 'search';
                this.resetPagination();
                this.fetchData(true);
            },

            resetPagination () {
                this.pagination = Object.assign({}, {
                    limit: 10,
                    current: 1,
                    count: 0
                });
            },

            quickSearchMethod (value) {
                window.changeAlert = true;
                return {
                    name: this.$t(`m.common['关键字']`),
                    id: 'keyword',
                    values: [value]
                };
            },

            handleSliderClose () {
                this.$emit('update:isShow', false);
                this.$emit('animation-end');
            },

            handleEdit (data) {
                window.localStorage.setItem('iam-header-title-cache', `${this.$t(`m.nav['编辑权限模板']`)}(${data.name})`);
                this.$router.push({
                    name: 'permTemplateEdit',
                    params: { id: data.id, systemId: data.system.id }
                });
            }
        }
    };
</script>

<style lang="postcss">
    .iam-add-group-perm-sideslider {
        z-index: 2503;
        .content-wrapper {
            position: relative;
            padding: 13px 22px;
            height: calc(100vh - 61px)
        }
        .template-content-wrapper {
            border-bottom: 1px solid #dcdee5;
        }
        .search-title {
            line-height: 32px;
            font-size: 14px;
        }
        .perm-template-table {
            margin-top: 8px;
            border: none;
            .perm-template-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
            .bk-table-header-wrapper {
                .bk-table-column-selection {
                    .cell {
                        visibility: hidden !important;
                    }
                }
            }
        }
        .custom-perm-wrapper {
            line-height: 42px;
            font-size: 14px;
            .title {
                color: #313238;
            }
            .title,
            .selected-info {
                line-height: 1;
            }
        }
        .add-button {
            display: inline-block;
            vertical-align: top;
            line-height: 30px;
            button {
                padding: 0;
                .left-icon {
                    top: -1px;
                    margin-right: 0;
                }
            }
        }
        .refresh-wrapper {
            width: 32px;
            height: 32px;
            display: inline-block;
            vertical-align: top;
            line-height: 28px;
            border: 1px solid #c4c6cc;
            text-align: center;
            cursor: pointer;
            &:hover {
                border-color: #3a84ff;
                color: #3a84ff;
            }
        }
        .error-icon {
            font-size: 14px;
            color: #ffb400;
            position: absolute;
            left: -15px;
            top: -11px;
        }
    }
</style>
