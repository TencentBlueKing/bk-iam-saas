<template>
    <div class="iam-user-group-wrapper">
        <render-search>
            <bk-button theme="primary" @click="handleCreate" data-test-id="group_btn_create">
                {{ $t(`m.common['新建']`) }}
            </bk-button>
            <bk-button
                v-if="isSuperManager"
                :disabled="currentSelectList.length < 1"
                style="margin-left: 6px;"
                data-test-id="group_btn_transferOut"
                @click="handleTransferOut">{{ $t(`m.userGroup['转出']`) }}</bk-button>
            <!-- <bk-button :disabled="currentSelectList.length < 1"
                theme="primary" @click="handleBatchAddMember" data-test-id="group_btn_create">
                {{ $t(`m.common['批量添加成员']`) }}
            </bk-button> -->
            <!-- 先屏蔽 -->
            <div slot="right">
                <iam-search-select
                    @on-change="handleSearch"
                    :data="searchData"
                    :value="searchValue"
                    :quick-search-method="quickSearchMethod"
                    style="width: 420px;" />
            </div>
        </render-search>
        <bk-table
            :data="tableList"
            size="small"
            :class="{ 'set-border': tableLoading }"
            ext-cls="user-group-table"
            :pagination="pagination"
            ref="tableRef"
            row-key="id"
            @page-change="pageChange"
            @page-limit-change="limitChange"
            @select="handlerChange"
            @select-all="handlerAllChange"
            v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
            <bk-table-column v-if="isSuperManager" type="selection" align="center" :selectable="getIsSelect"
                reserve-selection></bk-table-column>
            <bk-table-column :label="$t(`m.userGroup['用户组名']`)">
                <template slot-scope="{ row }">
                    <span class="user-group-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.userGroup['用户/组织']`)">
                <template slot-scope="{ row }">
                    <div class="member-wrapper">
                        <span class="user">
                            <Icon type="personal-user" />
                            {{ row.user_count || '--' }}
                        </span>
                        <span class="depart">
                            <Icon type="organization-fill" />
                            {{ row.department_count || '--' }}
                        </span>
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.userGroup['创建人']`)">
                <template slot-scope="{ row }">
                    <span>{{ row.creator || '--' }}</span>
                </template>
            </bk-table-column>
            <!-- 先屏蔽 -->
            <!-- <bk-table-column label="审批流程">
                <template slot-scope="{ row }">
                    <span class="user-group-process" :title="row.approval_process.name">
                        {{ row.approval_process.name }}
                    </span>
                </template>
            </bk-table-column> -->
            <bk-table-column :label="$t(`m.common['创建时间']`)">
                <template slot-scope="{ row }">
                    <span :title="row.created_time">{{ row.created_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['描述']`)">
                <template slot-scope="{ row }">
                    <span :title="row.description !== '' ? row.description : ''">{{ row.description || '--' }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)" width="300">
                <template slot-scope="{ row }">
                    <div>
                        <bk-button theme="primary" text @click="handleAddMember(row)">
                            {{ $t(`m.common['添加成员']`) }}
                        </bk-button>
                        <bk-button theme="primary" text style="margin-left: 10px;" @click="handleAddPerm(row)">
                            {{ $t(`m.common['添加权限']`) }}
                        </bk-button>
                        <bk-button theme="primary" text style="margin-left: 10px;" @click="handleDelete(row)">
                            {{ $t(`m.common['删除']`) }}
                        </bk-button>
                    </div>
                </template>
            </bk-table-column>
        </bk-table>

        <delete-dialog
            :show.sync="isShowDeleteDialog"
            :loading="deleteLoading"
            :name="currentUserGroup.name"
            @on-after-leave="handleAfterDeleteLeave"
            @on-cancel="hideCancelDelete"
            @on-sumbit="handleSumbitDelete" />

        <edit-process-dialog
            :show.sync="isShowEditProcessDialog"
            :loading="editLoading"
            @on-after-leave="handleAfterEditLeave"
            @on-cancel="hideCancelEdit"
            @on-sumbit="handleSumbitEdit" />

        <add-member-dialog
            :show.sync="isShowAddMemberDialog"
            :is-batch="isBatch"
            :loading="loading"
            :name="curName"
            :id="curId"
            :is-rating-manager="isRatingManager"
            show-expired-at
            @on-cancel="handleCancelAdd"
            @on-sumbit="handleSumbitAdd"
            @on-after-leave="handleAddAfterClose" />

        <transfer-out-dialog
            :show.sync="isShowRolloutGroupDialog"
            :group-ids="curSelectIds"
            @on-success="handleTransferOutSuccess"
            @on-cancel="handleTransferOutCancel" />
        <novice-guide :flag="showNoviceGuide" :content="content" />
    </div>
</template>
<script>
    import _ from 'lodash';
    import { mapGetters } from 'vuex';
    import IamSearchSelect from '@/components/iam-search-select';
    import { fuzzyRtxSearch } from '@/common/rtx';
    import { buildURLParams } from '@/common/url';
    import DeleteDialog from './components/delete-user-group-dialog';
    import AddMemberDialog from './components/iam-add-member';
    import EditProcessDialog from './components/edit-process-dialog';
    import TransferOutDialog from './components/transfer-out-dialog';
    import NoviceGuide from '@/components/iam-novice-guide';
    export default {
        name: '',
        components: {
            DeleteDialog,
            AddMemberDialog,
            EditProcessDialog,
            IamSearchSelect,
            TransferOutDialog,
            NoviceGuide
        },
        data () {
            return {
                isShowAddMemberDialog: false,
                tableList: [],
                tableLoading: false,
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                currentBackup: 1,
                searchParams: {},
                searchList: [],
                searchValue: [],
                currentSelectList: [],
                isShowDeleteDialog: false,
                deleteLoading: false,
                currentUserGroup: {},
                isShowEditProcessDialog: false,
                editLoading: false,

                loading: false,
                departs: [],
                users: [],
                curName: '',
                curId: 0,

                curRole: 'staff',

                isShowRolloutGroupDialog: false,

                isBatch: false,

                content: this.$t('m.nav["【分级管理员】 功能，全面升级为【权限管理空间】啦！"]')
            };
        },
        computed: {
            ...mapGetters(['user', 'showNoviceGuide']),
            isCanEditProcess () {
                return this.currentSelectList.length > 0;
            },
            isRatingManager () {
                return this.curRole === 'rating_manager';
            },
            isSuperManager () {
                return this.curRole === 'super_manager';
            },
            curSelectIds () {
                return this.currentSelectList.map(item => item.id);
            }
        },
        watch: {
            'pagination.current' (value) {
                this.currentBackup = value;
            },
            user: {
                handler (value) {
                    this.curRole = value.role.type || 'staff';
                },
                immediate: true,
                deep: true
            }
        },
        created () {
            this.curRole = this.user.role.type || 'staff';
            this.searchData = [
                {
                    id: 'id',
                    name: 'ID'
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
                    id: 'creator',
                    name: this.$t(`m.grading['创建人']`),
                    remoteMethod: this.handleRemoteRtx
                },
                {
                    id: 'system_id',
                    name: this.$t(`m.common['系统包含']`),
                    remoteMethod: this.handleRemoteSystem
                },
                {
                    id: 'username',
                    name: this.$t(`m.common['用户包含']`),
                    remoteMethod: this.handleRemoteRtx
                },
                {
                    id: 'department_id',
                    name: this.$t(`m.common['组织ID包含']`),
                    disabled: true
                }
            ];
            const isObject = payload => {
                return Object.prototype.toString.call(payload) === '[object Object]';
            };

            const currentQueryCache = this.getCurrentQueryCache();
            if (currentQueryCache && Object.keys(currentQueryCache).length) {
                if (currentQueryCache.limit) {
                    this.pagination.limit = currentQueryCache.limit;
                    this.pagination.current = currentQueryCache.current;
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
            /**
             * 获取页面数据
             */
            async fetchPageData () {
                await this.fetchUserGroupList();
            },

            getIsSelect () {
                return this.tableList.length > 0;
            },

            refreshCurrentQuery () {
                const { limit, current } = this.pagination;
                const params = {};
                const queryParams = {
                    limit,
                    current,
                    ...this.searchParams,
                    ...this.$route.query
                };
                window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
                for (const key in this.searchParams) {
                    const tempObj = this.searchData.find(item => key === item.id);
                    if (tempObj.remoteMethod && typeof tempObj.remoteMethod === 'function') {
                        if (this.searchList.length > 0) {
                            const tempData = this.searchList.find(item => item.id === key);
                            params[key] = tempData.values[0];
                        }
                    } else {
                        params[key] = this.searchParams[key];
                    }
                }
                return {
                    ...params,
                    limit,
                    current
                };
            },

            setCurrentQueryCache (payload) {
                window.localStorage.setItem('groupList', JSON.stringify(payload));
            },

            getCurrentQueryCache () {
                return JSON.parse(window.localStorage.getItem('groupList'));
            },

            quickSearchMethod (value) {
                return {
                    name: this.$t(`m.common['关键字']`),
                    id: 'keyword',
                    values: [value]
                };
            },

            async fetchUserGroupList (isLoading = false) {
                this.tableLoading = isLoading;
                this.setCurrentQueryCache(this.refreshCurrentQuery());
                const params = {
                    ...this.searchParams,
                    limit: this.pagination.limit,
                    offset: this.pagination.limit * (this.pagination.current - 1)
                };
                try {
                    const res = await this.$store.dispatch('userGroup/getUserGroupList', params);
                    this.pagination.count = res.data.count || 0;
                    this.tableList.splice(0, this.tableList.length, ...(res.data.results || []));
                    this.currentSelectList = this.currentSelectList.filter(item => {
                        return this.tableList.map(_ => _.id).includes(item.id);
                    });
                    if (this.currentSelectList.length < 1) {
                        this.$refs.tableRef && this.$refs.tableRef.clearSelection();
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

            handleRemoteRtx (value) {
                console.log('value', value);
                return fuzzyRtxSearch(value)
                    .then(data => {
                        return data.results;
                    });
            },

            handleRemoteSystem (value) {
                return this.$store.dispatch('system/getSystems')
                    .then(({ data }) => {
                        return data.map(({ id, name }) => ({ id, name })).filter(item => item.name.indexOf(value) > -1);
                    });
            },

            handleCreate () {
                this.$router.push({
                    name: 'createUserGroup'
                });
            },

            handleTransferOut () {
                this.isShowRolloutGroupDialog = true;
            },

            handleTransferOutSuccess () {
                this.currentSelectList = [];
                this.handleTransferOutCancel();
                this.resetPagination();
                this.fetchUserGroupList(true);
            },

            handleTransferOutCancel () {
                this.isShowRolloutGroupDialog = false;
            },

            handleEditApprovalProcess () {
                this.isShowEditProcessDialog = true;
            },

            resetPagination () {
                this.pagination = Object.assign({}, {
                    limit: 10,
                    current: 1,
                    count: 0
                });
            },

            handleSearch (payload, result) {
                this.searchParams = payload;
                this.searchList = result;
                this.resetPagination();
                this.fetchUserGroupList(true);
            },

            handleAddMember (payload) {
                this.curName = payload.name;
                this.curId = payload.id;
                this.isShowAddMemberDialog = true;
            },

            handleAddPerm (payload) {
                this.$router.push({
                    name: 'addGroupPerm',
                    params: {
                        id: payload.id
                    }
                });
            },

            handleCancelAdd () {
                this.curId = 0;
                this.isShowAddMemberDialog = false;
            },

            async handleSumbitAdd (payload) {
                this.loading = true;
                const { users, departments, expiredAt } = payload;
                let expired = payload.policy_expired_at;
                // 4102444800：非永久时需加上当前时间
                if (expiredAt !== 4102444800) {
                    const nowTimestamp = +new Date() / 1000;
                    const tempArr = String(nowTimestamp).split('');
                    const dotIndex = tempArr.findIndex(item => item === '.');
                    const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
                    expired = expired + nowSecond;
                }
                const arr = [];
                if (departments.length > 0) {
                    arr.push(...departments.map(item => {
                        return {
                            id: item.id,
                            type: 'department'
                        };
                    }));
                }
                if (users.length > 0) {
                    arr.push(...users.map(item => {
                        return {
                            id: item.username,
                            type: 'user'
                        };
                    }));
                }
                const params = {
                    members: arr,
                    expired_at: expired,
                    id: this.curId
                };
                let fetchUrl = 'userGroup/addUserGroupMember';
                if (this.isBatch) {
                    params.group_ids = this.curSelectIds;
                    delete params.id;
                    fetchUrl = 'userGroup/batchAddUserGroupMember';
                }
                console.log('params', params);
                try {
                    await this.$store.dispatch(fetchUrl, params);
                    this.isShowAddMemberDialog = false;
                    this.messageSuccess(this.$t(`m.info['添加成员成功']`), 2000);
                    this.fetchUserGroupList(true);
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
                    this.loading = false;
                }
            },

            handleAddAfterClose  () {
                this.curName = '';
                this.curId = 0;
            },

            handleDelete (payload) {
                this.currentUserGroup = payload;
                this.isShowDeleteDialog = true;
            },

            pageChange (page) {
                if (this.currentBackup === page) {
                    return;
                }
                this.pagination.current = page;
                this.fetchUserGroupList(true);
            },

            limitChange (currentLimit, prevLimit) {
                this.pagination.limit = currentLimit;
                this.pagination.current = 1;
                this.fetchUserGroupList(true);
            },

            handlerAllChange (selection) {
                this.currentSelectList = [...selection];
            },

            handlerChange (selection, row) {
                this.currentSelectList = [...selection];
            },

            handleView (payload) {
                window.localStorage.setItem('iam-header-title-cache', payload.name);
                window.localStorage.setItem('iam-header-name-cache', payload.name);
                this.$store.commit('setHeaderTitle', payload.name);
                this.$router.push({
                    name: 'userGroupDetail',
                    params: {
                        id: payload.id
                    }
                });
            },

            async handleSumbitDelete () {
                this.deleteLoading = true;
                try {
                    await this.$store.dispatch('userGroup/deleteUserGroup', {
                        id: this.currentUserGroup.id
                    });
                    this.messageSuccess(this.$t(`m.info['删除成功']`), 2000);
                    this.isShowDeleteDialog = false;
                    this.resetPagination();
                    this.fetchUserGroupList(true);
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
                    this.deleteLoading = false;
                }
            },

            handleSumbitEdit () {
                this.isShowEditProcessDialog = false;
            },

            hideCancelDelete () {
                this.isShowDeleteDialog = false;
            },

            hideCancelEdit () {
                this.isShowEditProcessDialog = false;
            },

            handleAfterDeleteLeave () {
                this.currentUserGroup = {};
            },

            handleAfterEditLeave () {},

            handleBatchAddMember () {
                this.isBatch = true;
                this.isShowAddMemberDialog = true;
            }
        }
    };
</script>
<style lang="postcss">
    .iam-user-group-wrapper {
        .user-group-table {
            margin-top: 16px;
            border-right: none;
            border-bottom: none;
            &.set-border {
                border-right: 1px solid #dfe0e5;
                border-bottom: 1px solid #dfe0e5;
            }
            tr:hover {
                .user-group-process {
                    background: #fff;
                }
                .member-wrapper {
                    .user,
                    .depart {
                        background: #fff;
                    }
                }
            }
            .user-group-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
            .member-wrapper {
                display: flex;
                justify-content: flex-start;
                .user,
                .depart {
                    display: inline-block;
                    min-width: 54px;
                    padding: 4px 6px;
                    background: #f0f1f5;
                    border-radius: 2px;
                    i {
                        font-size: 14px;
                        color: #c4c6cc;
                    }
                }
                .depart {
                    margin-left: 2px;
                }
            }
            .user-group-process {
                display: inline-block;
                padding: 4px 10px;
                max-width: 200px;
                background: #f0f1f5;
                border-radius: 2px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        }
    }
</style>
