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
            @page-limit-change="handleLimitChange" @expand-change="handleExpandChange"
            v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
            <bk-table-column type="expand" width="30">
                <template slot-scope="{ row }">
                    <bk-table size="small" ext-cls="children-expand-cls" :data="row.children" :row-key="row.id"
                        :show-header="false" :border="false" :cell-class-name="getCellClass" @row-click="handleRowClick"
                    >
                        <bk-table-column width="40" />
                        <bk-table-column prop="name" width="130">
                            <template slot-scope="child">
                                <div class="child_space_name">
                                    <Icon type="level-two" :style="{ color: iconColor[1] }" />
                                    <iam-edit-input field="name" :placeholder="$t(`m.verify['请输入']`)"
                                        :value="child.row.name" style="width: 100%;margin-left: 5px;"
                                        :remote-hander="handleUpdateManageSpace" />
                                </div>
                            </template>
                        </bk-table-column>
                        <bk-table-column prop="members" width="305">
                            <template slot-scope="child">
                                <iam-edit-member-selector
                                    field="members"
                                    width="200"
                                    :placeholder="$t(`m.verify['请输入']`)"
                                    :value="child.row.members"
                                    :remote-handler="handleUpdateManageSpace" />
                            </template>
                        </bk-table-column>
                        <bk-table-column prop="description" width="200">
                            <template slot-scope="child">
                                <iam-edit-textarea
                                    field="description"
                                    width="200"
                                    :placeholder="$t(`m.verify['用户组描述提示']`)"
                                    :value="child.row.description"
                                    :remote-hander="handleUpdateGroup" />
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
                        <bk-table-column width="300">
                            <template slot-scope="child">
                                <div class="operate_btn">
                                    <bk-button theme="primary" text @click.stop="handleClone(child.row)">
                                        {{ $t(`m.levelSpace['进入']`) }}
                                    </bk-button>
                                    <bk-button theme="primary" text @click.stop="handleClone(child.row)">
                                        {{ $t(`m.nav['授权边界']`) }}
                                    </bk-button>
                                    <bk-button theme="primary" text @click.stop="handleClone(child.row)">
                                        {{ $t(`m.levelSpace['克隆']`) }}
                                    </bk-button>
                                    <bk-button theme="primary" text @click.stop="handleClone(child.row)">
                                        {{ $t(`m.levelSpace['释放']`) }}
                                    </bk-button>
                                </div>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['空间名']`)" prop="name" width="145">
                <template slot-scope="{ row }">
                    <div>
                        <Icon type="level-one" :style="{ color: iconColor[0] }" />
                        <span v-bk-tooltips.right="row.name" class="right-start">
                            <bk-button theme="primary" text @click="handleView(row)">
                                {{ row.name }}
                            </bk-button>
                        </span>
                    </div>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['管理员']`)" prop="members" width="300">
                <template slot-scope="{ row }">
                    <bk-tag v-for="(tag, index) of row.members" :key="index">
                        {{tag}}
                    </bk-tag>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['描述']`)" prop="description" width="200">
                <template slot-scope="{ row }">
                    <span :title="row.description">{{ row.description || '--' }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['创建人']`)" prop="creator"></bk-table-column>
            <bk-table-column :label="$t(`m.common['创建时间']`)">
                <template slot-scope="{ row }">
                    <span :title="row.created_time">{{ row.created_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['更新人']`)" prop="updater"></bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['更新时间']`)">
                <template slot-scope="{ row }">
                    <span :title="row.updated_time">{{ row.updated_time }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)" width="300">
                <template slot-scope="{ row }">
                    <div class="operate_btn">
                        <bk-button theme="primary" text>{{ $t(`m.levelSpace['进入']`) }}</bk-button>
                        <bk-button theme="primary" text @click.stop="handleClone(row)">
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
    import IamEditInput from '@/components/iam-edit/input';
    import IamEditMemberSelector from '@/components/iam-edit/member-selector';
    import IamEditTextarea from '@/components/iam-edit/textarea';
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
                tableList: [
                    {
                        id: 46,
                        name: 'admin',
                        created_time: '2022-10-13 14:53:36',
                        creator: 'admin',
                        updated_time: '2022-10-26 10:12:21',
                        updater: 'admin',
                        description: '管理员可授予他人xxx的权限',
                        members: ['admin', 'liu0742666', 'gc_lihao'],
                        children: [
                            {
                                id: 47,
                                name: 'admin',
                                created_time: '2022-10-13 14:53:36',
                                creator: 'admin',
                                updated_time: '2022-10-26 10:12:21',
                                updater: 'admin',
                                description: '测试',
                                members: ['admin', 'liu07']
                            },
                            {
                                id: 48,
                                name: 'admin',
                                created_time: '2022-10-13 14:53:36',
                                creator: 'admin',
                                updated_time: '2022-10-26 10:12:21',
                                updater: 'admin',
                                description: '测试',
                                members: ['admin', 'liu07', 'gc_lihao', 'gc_lihao', 'gc_lihao']
                            }
                        ]
                    },
                    {
                        id: 49,
                        name: 'admin2',
                        created_time: '2022-10-13 14:53:36',
                        creator: 'admin',
                        updated_time: '2022-10-26 10:12:21',
                        updater: 'admin',
                        description: '管理员可授予他人xxx的权限',
                        members: ['admin', 'liu0742666', 'gc_lihao'],
                        children: [
                            {
                                id: 50,
                                name: 'admin',
                                created_time: '2022-10-13 14:53:36',
                                creator: 'admin',
                                updated_time: '2022-10-26 10:12:21',
                                updater: 'admin',
                                description: '管理员可授予他人xxx的权限',
                                members: ['admin', 'liu07']
                            },
                            {
                                id: 51,
                                name: 'admin',
                                created_time: '2022-10-13 14:53:36',
                                creator: 'admin',
                                updated_time: '2022-10-26 10:12:21',
                                updater: 'admin',
                                description: '测试',
                                members: ['admin', 'liu07', 'gc_lihao']
                            }
                        ]
                    }
                ],
                pagination: {
                    current: 1,
                    count: 1,
                    limit: 10
                },
                currentBackup: 1,
                searchValue: '',
                radioValue: 'haveRole',
                iconColor: ['#FF9C01', '#9B80FE'],
                expandRowList: [] // 所有展开折叠项
            };
        },
        computed: {
            ...mapGetters(['user']),
            tableHeight () {
                return getWindowHeight() - 185;
            }
        },
        methods: {
            getCellClass ({ row, column, rowIndex, columnIndex }) {
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

            handleUpdateManageSpace (payload) {
                console.log(payload, 555);
            },

            handleRowClick (row, column, cell, event, rowIndex, columnIndex) {
                const allNodeId = this.findParentNode(row.id, this.expandRowList);
                if (allNodeId.length) {
                    const rowData = this.expandRowList.find(item => item.id === allNodeId[0]);
                    this.$refs.spaceTable.toggleRowExpansion(rowData, false);
                }
            },

            handleExpandChange (row, expandedRows) {
                this.expandRowList = expandedRows;
            },

            handleCreate () {
                this.$store.commit('updateIndex', 3);
                this.$router.push({
                    name: 'myManageSpaceCreate'
                });
            },
            handleView ({ id, name }) {
                window.localStorage.setItem('iam-header-name-cache', name);
                this.$store.commit('updateIndex', 1);
                this.$router.push({
                    name: 'authorBoundary',
                    params: {
                        id
                    }
                });
            },

            handleClone () {
                console.log(455);
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
}
</style>
