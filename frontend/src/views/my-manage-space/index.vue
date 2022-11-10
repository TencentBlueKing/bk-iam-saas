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
                    <bk-input :placeholder="$t(`m.levelSpace['搜索空间名、描述、创建人、创建时间']`)" clearable style="width: 420px"
                        right-icon="bk-icon icon-search" v-model="searchValue" @enter="handleSearch" />
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
                    <bk-table size="small" ext-cls="children-expand-cls"
                        :data="row.children" :row-key="row.id"
                        :show-header="false" :border="false"
                        v-bkloading="{ isLoading: subLoading, opacity: 1 }"
                        :pagination="subPagination"
                        @page-change="handleSubPageChange"
                        @page-limit-change="handleSubLimitChange"
                        @row-click="handleRowClick"
                    >
                        <bk-table-column width="30" />
                        <bk-table-column prop="name" min-width="240">
                            <template slot-scope="child">
                                <div class="child_space_name">
                                    <Icon type="level-two" :style="{ color: iconColor[1] }" />
                                    <iam-edit-input field="name" :placeholder="$t(`m.verify['请输入']`)"
                                        :value="child.row.name" style="width: 100%;margin-left: 5px;"
                                        :index="child.$index"
                                        :remote-hander="handleUpdateManageSpace" />
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
                                    @on-change="handleUpdateMembers" />
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
                                    :remote-hander="handleUpdateManageSpace" />
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t(`m.levelSpace['创建人']`)" prop="creator"></bk-table-column>
                        <bk-table-column :label="$t(`m.common['创建时间']`)">
                            <template slot-scope="child">
                                <span :title="row.created_time">{{ child.row.created_time }}</span>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t(`m.levelSpace['更新人']`)" prop="updater"></bk-table-column>
                        <bk-table-column prop="updated_time">
                            <template slot-scope="child">
                                <span :title="row.updated_time">{{ child.row.updated_time }}</span>
                            </template>
                        </bk-table-column>
                        <bk-table-column width="200">
                            <template slot-scope="child">
                                <div class="operate_btn">
                                    <bk-button theme="primary" text @click.stop="handleSubView(child.row)">
                                        {{ $t(`m.levelSpace['进入']`) }}
                                    </bk-button>
                                    <bk-button theme="primary" text @click.stop="handleSubView(child.row)">
                                        {{ $t(`m.nav['授权边界']`) }}
                                    </bk-button>
                                    <bk-button theme="primary" text @click.stop="handleClone(child.row)">
                                        {{ $t(`m.levelSpace['克隆']`) }}
                                    </bk-button>
                                </div>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['空间名']`)" prop="name" min-width="240">
                <template slot-scope="{ row }">
                    <div>
                        <Icon type="level-one" :style="{ color: iconColor[0] }" />
                        <span v-bk-tooltips.right="row.name" class="right-start">
                            {{ row.name }}
                        </span>
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['管理员']`)" prop="members" width="300">
                <template slot-scope="{ row }">
                    <bk-tag v-for="(tag, index) of row.members" :key="index">
                        {{tag.username}}
                    </bk-tag>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['描述']`)" prop="description" width="200">
                <template slot-scope="{ row }">
                    <span
                        v-bk-tooltips.top="{ content: row.description, extCls: 'iam-tooltips-cls' }"
                        :title="row.description">{{ row.description || '--' }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['创建人']`)" prop="creator"></bk-table-column>
            <bk-table-column :label="$t(`m.common['创建时间']`)">
                <template slot-scope="{ row }">
                    <span
                        v-bk-tooltips.top="{ content: row.created_time, extCls: 'iam-tooltips-cls' }"
                        :title="row.created_time">{{ row.created_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['更新人']`)" prop="updater"></bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['更新时间']`)">
                <template slot-scope="{ row }">
                    <span v-bk-tooltips.top="{ content: row.updated_time, extCls: 'iam-tooltips-cls' }"
                        :title="row.updated_time">{{ row.updated_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)" width="200">
                <template slot-scope="{ row }">
                    <div class="operate_btn">
                        <bk-button theme="primary" text
                            @click="handleView(row, 'detail')">{{ $t(`m.levelSpace['进入']`) }}</bk-button>
                        <bk-button theme="primary" text @click.stop="handleView(row, 'edit')">
                            {{ $t(`m.nav['授权边界']`) }}
                        </bk-button>
                        <bk-button theme="primary" text @click="handleClone(row)">
                            {{ $t(`m.levelSpace['克隆']`) }}
                        </bk-button>
                    </div>
                </template>
            </bk-table-column>
        </bk-table>
    </div>
</template>

<script>
    import { mapGetters } from 'vuex';
    import { getWindowHeight } from '@/common/util';
    import IamEditInput from './components/iam-edit/input';
    import IamEditMemberSelector from './components/iam-edit/member-selector';
    import IamEditTextarea from './components/iam-edit/textarea';
    import { buildURLParams } from '@/common/url';
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
                }
            };
        },
        computed: {
            ...mapGetters(['user']),
            tableHeight () {
                return getWindowHeight() - 185;
            }
        },
        methods: {
            async fetchPageData () {
                await this.fetchGradingAdmin();
            },
            getCellClass ({ row, column, rowIndex, columnIndex }) {
                if (!row.is_member) {
                    return 'iam-tag-table-cell-opacity-cls';
                }
                if (!row.has_subset_manager) {
                    return 'iam-tag-table-cell-subset-cls';
                }
                if (columnIndex === 2) {
                    return 'iam-tag-table-cell-cls';
                }
                return '';
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

            handleUpdateManageSpace (payload, index) {
                this.formData = this.subTableList.find((e, i) => i === index);
                const params = {
                    name: payload.name || this.formData.name,
                    description: payload.description || this.formData.description,
                    members: payload.members || this.formData.members,
                    id: this.formData.id
                };
                return this.$store.dispatch('spaceManage/updateSecondManagerManager', params)
                    .then(async () => {
                        this.messageSuccess(this.$t(`m.info['编辑成功']`), 2000);
                        this.formData.name = params.name;
                        this.formData.description = params.description;
                        this.formData.members = [...params.members];
                    }, (e) => {
                        console.warn('error');
                        this.bkMessageInstance = this.$bkMessage({
                            limit: 1,
                            theme: 'error',
                            message: e.message || e.data.msg || e.statusText
                        });
                    });
            },

            handleUpdateMembers (payload, index) {
                this.handleUpdateManageSpace(payload, index);
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
                    } else {
                        this.fetchSubManagerList(row);
                    }
                });
            },

            async fetchSubManagerList (row) {
                this.subLoading = true;
                try {
                    const res = await this.$store.dispatch('spaceManage/getStaffSubManagerList', {
                        limit: this.subPagination.limit,
                        offset: (this.subPagination.current - 1) * this.subPagination.limit,
                        id: row.id
                    });
                    this.subPagination.count = res.data.count;
                    this.subTableList.splice(0, this.subTableList.length, ...(res.data.results || []));
                    row.children = this.subTableList;
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
                    this.curData = row;
                    this.subLoading = false;
                }
            },

            handleCreate () {
                this.$store.commit('updateIndex', 3);
                this.$router.push({
                    name: 'myManageSpaceCreate'
                });
            },
            // 一级管理空间
            handleView ({ id, name }, type) {
                window.localStorage.setItem('iam-header-name-cache', name);
                this.$router.push({
                    name: type === 'detail' ? 'gradingAdminDetail' : 'gradingAdminEdit',
                    params: {
                        id
                    }
                });
            },

            // 二级管理空间
            handleSubView ({ id, name }) {
                window.localStorage.setItem('iam-header-name-cache', name);
                this.$router.push({
                    name: 'myManageSpaceSubDetail',
                    params: {
                        id: id
                    }
                });
            },

            handleClone () {
                console.log(455);
            },

            setCurrentQueryCache (payload) {
                window.localStorage.setItem('gradeManagerList', JSON.stringify(payload));
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

            async fetchGradingAdmin (isTableLoading = false) {
                this.tableLoading = isTableLoading;
                this.setCurrentQueryCache(this.refreshCurrentQuery());
                try {
                    const res = await this.$store.dispatch('role/getRatingManagerList', {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        name: this.searchValue
                    });
                    this.pagination.count = res.data.count;
                    res.data.results = res.data.results.map(e => {
                        e.children = [];
                        return e;
                    });
                    this.tableList.splice(0, this.tableList.length, ...(res.data.results || []));
                    if (this.isStaff) {
                        this.$store.commit('setGuideShowByField', { field: 'role', flag: this.tableList.length > 0 });
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
                    this.tableLoading = false;
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

    .child_space_name {
        display: flex;
        align-items: center;
    }

    .operate_btn {
        .bk-button-text {
            &:nth-child(n + 2) {
                margin-left: 10px;
                ;
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
        opacity: 0.4
    }

    /deep/ .iam-tag-table-cell-subset-cls {
        .cell {
            .bk-table-expand-icon  {
                display: none;
            }
        }
    }
}
</style>
