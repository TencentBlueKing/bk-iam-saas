<template>
    <div class="iam-level-manage-space-wrapper">
        <render-search>
            <bk-button theme="primary" @click="handleCreate" data-test-id="level-manage_space_btn_create">
                {{ $t(`m.common['申请新建']`) }}
            </bk-button>
            <div slot="right">
                <div class="right-form">
                    <!-- <bk-radio-group v-model="radioValue" @change="handlerChange" style="width: 200px">
                        <bk-radio-button :value="'haveRole'">
                            {{ $t(`m.levelSpace['我有权限']`) }}
                        </bk-radio-button>
                        <bk-radio-button :value="'allSpace'">
                            {{ $t(`m.levelSpace['全部空间']`) }}
                        </bk-radio-button>
                    </bk-radio-group> -->
                    <bk-input
                        v-model="searchValue"
                        :placeholder="$t(`m.levelSpace['请输入名称']`)"
                        clearable
                        style="width: 420px"
                        right-icon="bk-icon icon-search"
                        @enter="handleSearch" />
                </div>
            </div>
        </render-search>
        <bk-table ref="spaceTable" size="small" ext-cls="level-manage-table" :data="tableList" :max-height="tableHeight"
            :cell-class-name="getCellClass" :pagination="pagination" @page-change="handlePageChange"
            @page-limit-change="handleLimitChange"
            @expand-change="handleExpandChange"
            v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
            <bk-table-column type="expand" width="30">
                <template slot-scope="{ row }">
                    <!-- <bk-table
                        size="small"
                        ext-cls="children-expand-cls"
                        :data="row.children"
                        :row-key="row.id"
                        :show-header="false"
                        :border="false"
                        :cell-class-name="getSubCellClass"
                        v-bkloading="{ isLoading: subLoading, opacity: 1 }"
                        :pagination="subPagination"
                        @page-change="handleSubPageChange"
                        @page-limit-change="handleSubLimitChange"
                        @row-click="handleRowClick"
                    > -->
                    <bk-table
                        size="small"
                        ext-cls="children-expand-cls"
                        :data="row.children"
                        :row-key="row.id"
                        :show-header="false"
                        :border="false"
                        :cell-class-name="getSubCellClass"
                        :max-height="500"
                        v-bkloading="{ isLoading: subLoading, opacity: 1 }"
                        @row-click="handleRowClick"
                    >
                        <bk-table-column width="30" />
                        <bk-table-column prop="name" width="240">
                            <template slot-scope="child">
                                <div class="flex_space_name">
                                    <Icon type="level-two-manage-space" :style="{ color: iconColor[1] }" />
                                    <iam-edit-input field="name" :placeholder="$t(`m.verify['请输入']`)"
                                        :value="child.row.name" style="width: 100%;margin-left: 5px;"
                                        :index="child.$index"
                                        :remote-hander="handleUpdateSubManageSpace" />
                                </div>
                            </template>
                        </bk-table-column>
                        <bk-table-column prop="members" width="300">
                            <template slot-scope="child">
                                <iam-edit-member-selector
                                    field="members"
                                    width="200"
                                    :placeholder="$t(`m.verify['请输入']`)"
                                    :value="child.row.members"
                                    :index="child.$index"
                                    @on-change="handleUpdateSubMembers" />
                            </template>
                        </bk-table-column>
                        <bk-table-column prop="description" width="200">
                            <template slot-scope="child">
                                <iam-edit-textarea
                                    field="description"
                                    width="200"
                                    :placeholder="$t(`m.verify['用户组描述提示']`)"
                                    :value="child.row.description"
                                    :index="child.$index"
                                    :remote-hander="handleUpdateSubManageSpace" />
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t(`m.levelSpace['更新人']`)" prop="updater"></bk-table-column>
                        <bk-table-column :label="$t(`m.levelSpace['更新时间']`)" prop="updated_time">
                            <template slot-scope="child">
                                <span :title="child.row.updated_time">{{ child.row.updated_time }}</span>
                            </template>
                        </bk-table-column>
                        <bk-table-column width="200">
                            <template slot-scope="child">
                                <div class="operate_btn">
                                    <bk-button
                                        theme="primary"
                                        text
                                        :disabled="disabledPerm(child.row)"
                                        @click.stop="handleSubView(child.row, 'detail')">
                                        {{ $t(`m.levelSpace['进入']`) }}
                                    </bk-button>
                                    <bk-button
                                        theme="primary"
                                        text
                                        :disabled="disabledPerm(child.row)"
                                        @click.stop="handleSubView(child.row, 'auth')">
                                        {{ $t(`m.nav['授权边界']`) }}
                                    </bk-button>
                                    <!--<bk-button theme="primary" text @click.stop="handleSubView(child.row, 'clone')">
                                        {{ $t(`m.levelSpace['克隆']`) }}
                                    </bk-button> -->
                                </div>
                            </template>
                        </bk-table-column>
                        <template slot="empty">
                            <ExceptionEmpty
                                style="background: #ffffff"
                                :type="emptyData.type"
                                :empty-text="emptyData.text"
                                :tip-text="emptyData.tip"
                                :tip-type="emptyData.tipType"
                                @on-clear="handleEmptyClear"
                                @on-refresh="handleEmptyRefresh"
                            />
                        </template>
                    </bk-table>
                    <div style="text-align: center">
                        <bk-button
                            v-if="subPagination.count !== row.children.length"
                            text
                            theme="primary"
                            size="small"
                            style="margin: 10px auto"
                            @click="handleLoadMore(row.children.length)">
                            {{ $t(`m.common['查看更多']`) }}
                        </bk-button>
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['名称']`)" prop="name" width="240">
                <template slot-scope="{ row, $index }">
                    <div class="flex_space_name">
                        <Icon type="level-one-manage-space" :style="{ color: iconColor[0] }" />
                        <!-- <span :title="row.name" class="right-start">
                            {{ row.name }}
                        </span> -->
                        <iam-edit-input field="name" :placeholder="$t(`m.verify['请输入']`)"
                            :value="row.name" style="width: 100%;margin-left: 5px;"
                            :index="$index"
                            :remote-hander="handleUpdateManageSpace" />
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['管理员']`)" prop="members" width="300">
                <template slot-scope="{ row, $index }">
                    <!-- <bk-tag v-for="(tag, index) of row.members" :key="index">
                        {{tag.username}}
                    </bk-tag> -->
                    <iam-edit-member-selector
                        field="members"
                        width="200"
                        :placeholder="$t(`m.verify['请输入']`)"
                        :value="row.members"
                        :index="$index"
                        @on-change="handleUpdateMembers" />
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['描述']`)" prop="description" width="200">
                <template slot-scope="{ row, $index }">
                    <!-- <span
                        v-bk-tooltips.top="{ content: row.description, extCls: 'iam-tooltips-cls' }"
                        :title="row.description">{{ row.description || '--' }}</span> -->
                    <iam-edit-textarea
                        field="description"
                        width="200"
                        :placeholder="$t(`m.verify['用户组描述提示']`)"
                        :value="row.description"
                        :index="$index"
                        :remote-hander="handleUpdateManageSpace" />
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['更新人']`)" prop="updater"></bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['更新时间']`)" prop="updated_time">
                <template slot-scope="{ row }">
                    <span :title="row.updated_time">{{ row.updated_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)" width="200">
                <template slot-scope="{ row }">
                    <div class="operate_btn">
                        <bk-button
                            theme="primary"
                            text
                            :disabled="disabledPerm(row)"
                            @click="handleView(row, 'detail')">
                            {{ $t(`m.levelSpace['进入']`) }}
                        </bk-button>
                        <bk-button
                            theme="primary"
                            text
                            :disabled="disabledPerm(row)"
                            @click.stop="handleView(row, 'auth')">
                            {{ $t(`m.nav['授权边界']`) }}
                        </bk-button>
                        <bk-button theme="primary" text @click="handleView(row, 'clone')">
                            {{ $t(`m.levelSpace['克隆']`) }}
                        </bk-button>
                    </div>
                </template>
            </bk-table-column>
            <template slot="empty">
                <ExceptionEmpty
                    :type="emptyData.type"
                    :empty-text="emptyData.text"
                    :tip-text="emptyData.tip"
                    :tip-type="emptyData.tipType"
                    @on-clear="handleEmptyClear"
                    @on-refresh="handleEmptyRefresh"
                />
            </template>
        </bk-table>
    </div>
</template>

<script>
    import { mapGetters } from 'vuex';
    import { getWindowHeight, formatCodeData } from '@/common/util';
    import IamEditInput from './components/iam-edit/input';
    import IamEditMemberSelector from './components/iam-edit/member-selector';
    import IamEditTextarea from './components/iam-edit/textarea';
    import { buildURLParams } from '@/common/url';
    // import { bus } from '@/common/bus';
    // import { getRouterDiff, getNavRouterDiff } from '@/common/router-handle';

    export default {
        name: 'myManageSpace',
        components: {
            IamEditInput,
            IamEditMemberSelector,
            IamEditTextarea
        },
        data () {
            return {
                tableLoading: false,
                isFilter: false,
                tableList: [],
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                subPagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                currentBackup: 1,
                searchValue: '',
                radioValue: 'haveRole',
                iconColor: ['#FF9C01', '#9B80FE'],
                expandRowList: [], // 所有展开折叠项
                subLoading: false,
                subTableList: [],
                gradingAdminId: 0,
                curData: {},
                formData: {
                    name: '',
                    description: '',
                    members: []
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
            ...mapGetters(['user', 'roleList']),
            tableHeight () {
                return getWindowHeight() - 185;
            },
            disabledPerm () {
                return (payload) => {
                    const result = payload.members.map(item => item.username).includes(this.user.username);
                    return !result;
                };
            }
        },
        watch: {
            searchValue (newVal, oldVal) {
                if (!newVal && oldVal && this.isFilter) {
                    this.isFilter = false;
                    this.resetPagination();
                    this.fetchGradingAdmin(true);
                }
            },
            'pagination.current' (value) {
                this.currentBackup = value;
            }
        },
        methods: {
            async fetchPageData () {
                await this.fetchGradingAdmin();
            },
            
            getCellClass ({ row, column, rowIndex, columnIndex }) {
                if (!row.is_member) {
                    return 'iam-tag-table-cell-cls iam-tag-table-cell-opacity-cls';
                }
                if (!row.has_subset_manager) {
                    return 'iam-tag-table-cell-cls iam-tag-table-cell-subset-cls';
                }
                if (columnIndex === 1 || column.type === 'default') {
                    return 'iam-table-cell-1-cls';
                }
                if (columnIndex === 2) {
                    return 'iam-tag-table-cell-cls';
                }
                return '';
            },

            getSubCellClass ({ row, column, rowIndex, columnIndex }) {
                return 'iam-table-cell-1-cls';
            },

            // 通过子集id找父级数据
            findParentNode (id, list = [], result = []) {
                for (let i = 0; i < list.length; i += 1) {
                    const item = list[i];
                    if (item.id === id) {
                        result.push(item.id);
                        if (result.length === 1) return result;
                        return true;
                    }
                    if (item.children) {
                        result.push(item.id);
                        const isFind = this.findParentNode(id, item.children, result);
                        if (isFind) {
                            return result;
                        }
                        result.pop();
                    }
                }
                return false;
            },

            handleSearch () {
                if (!this.searchValue) {
                    return;
                }
                this.isFilter = true;
                this.emptyData.tipType = 'search';
                this.resetPagination();
                this.resetSubPagination();
                this.fetchGradingAdmin(true);
            },

            handleClear () {
                if (this.isFilter) {
                    this.isFilter = false;
                    this.resetPagination();
                    this.fetchGradingAdmin(true);
                }
            },

            handleUpdateMembers (payload, index) {
                this.handleUpdateManageSpace(payload, index);
            },

            handleUpdateSubMembers (payload, index) {
                this.handleUpdateSubManageSpace(payload, index);
            },

            async handleUpdateManageSpace (payload, index) {
                this.formData = this.tableList.find((e, i) => i === index);
                await this.fetchManageTable(payload, 'role/updateRatingManager');
            },

            async handleUpdateSubManageSpace (payload, index) {
                this.formData = this.subTableList.find((e, i) => i === index);
                await this.fetchManageTable(payload, 'spaceManage/updateSecondManagerManager');
            },

            async fetchManageTable (payload, url) {
                const { name, description, members } = payload;
                const params = {
                    name: name || this.formData.name,
                    description: description || this.formData.description,
                    members: members || this.formData.members,
                    id: this.formData.id
                };
                try {
                    await this.$store.dispatch(url, params);
                    this.messageSuccess(this.$t(`m.info['编辑成功']`), 2000);
                    this.formData = Object.assign(this.formData, {
                        name: params.name,
                        description: params.description,
                        members: [...params.members]
                    });
                } catch (e) {
                    console.error(e);
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText,
                        ellipsisCopy: true
                    });
                }
            },

            handleRowClick (row, column, cell, event, rowIndex, columnIndex) {
                const allNodeId = this.findParentNode(row.id, this.expandRowList);
                if (allNodeId.length) {
                    const rowData = this.expandRowList.find(item => item.id === allNodeId[0]);
                    this.$refs.spaceTable.toggleRowExpansion(rowData, false);
                }
            },

            handleExpandChange (row, expandedRows) {
                // if (row.id !== this.gradingAdminId) return;
                this.gradingAdminId = row.id;
                expandedRows = expandedRows.filter(e => e.id === this.gradingAdminId);
                if (!expandedRows.length) return;
                console.log('expandedRows', row, expandedRows);
                this.tableList.forEach(e => {
                    if (e.id !== expandedRows[0].id) {
                        this.$refs.spaceTable.toggleRowExpansion(e, false);
                        row.children = [];
                        this.resetSubPagination();
                    } else {
                        this.fetchSubManagerList(row);
                    }
                });
            },

            async fetchGradingAdmin (isTableLoading = false) {
                this.tableLoading = isTableLoading;
                this.setCurrentQueryCache(this.refreshCurrentQuery());
                try {
                    const { code, data } = await this.$store.dispatch('role/getRatingManagerList', {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        name: this.searchValue
                    });
                    this.pagination.count = data.count;
                    data.results = data.results.map(e => {
                        e.children = [];
                        return e;
                    });
                    this.tableList.splice(0, this.tableList.length, ...(data.results || []));
                    if (this.isStaff) {
                        this.$store.commit('setGuideShowByField', { field: 'role', flag: this.tableList.length > 0 });
                    }
                    this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
                } catch (e) {
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
                }
            },

            async fetchSubManagerList (row) {
                this.subLoading = true;
                try {
                    const { code, data } = await this.$store.dispatch('spaceManage/getStaffSubManagerList', {
                        limit: this.subPagination.limit,
                        offset: (this.subPagination.current - 1) * this.subPagination.limit,
                        id: row.id
                    });
                    this.subPagination.count = data.count;
                    // this.subTableList.splice(0, this.subTableList.length, ...(data.results || []));
                    row.children = [...row.children, ...data.results];
                    this.emptyData = formatCodeData(code, this.emptyData, this.subTableList.length === 0);
                } catch (e) {
                    console.error(e);
                    const { code, data, message, statusText } = e;
                    row.children = [];
                    this.emptyData = formatCodeData(code, this.emptyData);
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: message || data.msg || statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
                    });
                } finally {
                    this.curData = row;
                    this.subLoading = false;
                }
            },
            
            // 管理空间
            async handleView ({ id, name }, mode) {
                window.localStorage.setItem('iam-header-name-cache', name);
                let routerName = 'userGroup';
                const routerNav = {
                    detail: () => {
                        routerName = 'userGroup';
                        this.$store.commit('updateIndex', 1);
                        window.localStorage.setItem('index', 1);
                    },
                    auth: () => {
                        routerName = 'authorBoundary';
                        this.$store.commit('updateIndex', 1);
                        window.localStorage.setItem('index', 1);
                    },
                    clone: () => {
                        routerName = 'gradingAdminCreate';
                        this.$store.commit('updateIndex', 0);
                        window.localStorage.setItem('index', 0);
                    }
                };
                routerNav[mode]();
                if (!['clone'].includes(mode)) {
                    await this.$store.dispatch('role/updateCurrentRole', { id });
                    await this.$store.dispatch('userInfo');
                    const { role } = this.user;
                    this.$store.commit('updateCurRoleId', id);
                    this.$store.commit('updateIdentity', { id, type: role.type, name });
                    this.$store.commit('updateNavId', id);
                }
                this.$router.push({
                    name: routerName,
                    params: {
                        id,
                        role_type: 'staff'
                    }
                });
            },

            // 二级管理空间
            async handleSubView ({ id, name }, mode) {
                // let routerName = 'myManageSpaceSubDetail';
                // switch (type) {
                //     case 'detail':
                //         routerName = 'myManageSpaceSubDetail';
                //         break;
                //     case 'edit':
                //         routerName = 'myManageSpaceSubDetail';
                //         break;
                //     case 'clone':
                //         routerName = 'secondaryManageSpaceCreate';
                //         break;
                //     default:
                //         break;
                // }
                // const currentRole = getTreeNode(id, this.roleList);
                window.localStorage.setItem('iam-header-name-cache', name);
                let routerName = 'userGroup';
                const routerNav = {
                    detail: () => {
                        routerName = 'userGroup';
                        this.$store.commit('updateIndex', 1);
                        window.localStorage.setItem('index', 1);
                    },
                    auth: () => {
                        routerName = 'authorBoundary';
                        this.$store.commit('updateIndex', 1);
                        window.localStorage.setItem('index', 1);
                    },
                    clone: () => {
                        routerName = 'secondaryManageSpaceCreate';
                        this.$store.commit('updateIndex', 0);
                        window.localStorage.setItem('index', 0);
                    }
                };
                routerNav[mode]();
                if (!['clone'].includes(mode)) {
                    await this.$store.dispatch('role/updateCurrentRole', { id });
                    await this.$store.dispatch('userInfo');
                    const { role } = this.user;
                    this.$store.commit('updateCurRoleId', id);
                    this.$store.commit('updateIdentity', { id, type: role.type, name });
                    this.$store.commit('updateNavId', id);
                }
                this.$router.push({
                    name: routerName,
                    params: {
                        id,
                        role_type: 'staff'
                    }
                });
            },

            async handleLoadMore (payload) {
                if (payload !== this.subPagination.count) {
                    const params = {
                        current: ++this.subPagination.current,
                        limit: 10
                    };
                    console.log(params, 555);
                    this.subPagination = Object.assign(this.subPagination, params);
                    this.fetchSubManagerList(this.curData);
                }
            },
            
            handleSubPageChange (page) {
                this.subPagination.current = page;
                this.fetchSubManagerList(this.curData);
            },

            handleSubLimitChange (limit) {
                this.subPagination = Object.assign(this.subPagination, { limit, current: 1 });
                this.fetchSubManagerList(this.curData);
            },
 
            handlePageChange (page) {
                if (this.currentBackup === page) {
                    return;
                }
                this.pagination.current = page;
                this.fetchGradingAdmin(true);
            },

            handleLimitChange (limit) {
                this.pagination = Object.assign(this.pagination, { limit, current: 1 });
                this.fetchGradingAdmin(true);
            },
            
            handleCreate () {
                this.$router.push({
                    name: 'myManageSpaceCreate'
                });
            },

            setCurrentQueryCache (payload) {
                window.localStorage.setItem('myManagerList', JSON.stringify(payload));
            },

            refreshCurrentQuery () {
                const { limit, current } = this.pagination;
                const queryParams = {
                    limit,
                    current
                };
                if (this.searchValue !== '') {
                    queryParams.name = this.searchValue;
                }
                window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
                return queryParams;
            },

            handleEmptyClear () {
                this.searchValue = '';
                this.emptyData.tipType = '';
                this.resetPagination();
                this.resetSubPagination();
                this.fetchGradingAdmin();
            },

            handleEmptyRefresh () {
                this.resetPagination();
                this.resetSubPagination();
                this.fetchGradingAdmin();
            },
            
            resetPagination () {
                this.pagination = Object.assign({}, {
                    current: 1,
                    count: 0,
                    limit: 10
                });
            },

            resetSubPagination () {
                this.subPagination = Object.assign({}, {
                    current: 1,
                    count: 0,
                    limit: 10
                });
            }
        }
    };
</script>

<style lang="postcss" scoped>
.iam-level-manage-space-wrapper {
    .level-manage-table {
        margin-top: 16px;
    }

    .right-form {
        display: flex;
    }

    .flex_space_name {
        display: flex;
        align-items: center;
    }

    .operate_btn {
        .bk-button-text {
            &:nth-child(n + 2) {
                margin-left: 10px;
            }
        }
    }

    .level-manage-table {

        /deep/ .bk-table-pagination-wrapper {
            background: #fff;
        }
    }

    /deep/ .bk-table-expanded-cell {
        padding: 0 !important;

        &:hover {
            cursor: pointer;
        }

        .bk-table {
            border: 0;
        }
    }

    /deep/ .iam-tag-table-cell-cls {
        .cell {
            .bk-tag {
                &:first-of-type {
                    margin-left: 0;
                }

                &:hover {
                    cursor: pointer;
                }
            }
        }
    }

    /deep/ .iam-tag-table-cell-opacity-cls {
        opacity: 0.4;
        .cell {
            padding-left: 0;
        }
    }

    /deep/ .iam-tag-table-cell-subset-cls {
        .cell {
            .bk-table-expand-icon  {
                display: none;
            }
        }
    }

     /deep/ .iam-table-cell-1-cls, .iam-tag-table-cell-subset-cls  {
        .cell {
            padding-left: 2px;
        }
    }

    /deep/ .iam-tag-table-cell-subset-cls {
        .cell {
            padding-left: 2px;
        }
    }

    /deep/ .bk-table-header-wrapper {
        .cell {
            padding-left: 2px;
        }
    }
}
</style>
