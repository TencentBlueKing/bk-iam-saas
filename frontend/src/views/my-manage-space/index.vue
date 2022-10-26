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
        <bk-table :data="tableList" size="small" :class="{ 'set-border': tableLoading }" ext-cls="level-manage-table"
            :pagination="pagination" @page-change="handlePageChange" @page-limit-change="handleLimitChange"
            v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
            <bk-table-column type="expand" width="60">
                <template slot-scope="{ row }">
                    <bk-table size="small" :data="row.children" :outer-border="false" :row-border="false"
                        :col-border="false" :header-cell-style="{ background: '#fff', border: 'none' }">
                        <bk-table-column prop="name" label="任务名称"></bk-table-column>
                        <bk-table-column prop="count" label="节点数量"></bk-table-column>
                        <bk-table-column prop="creator" label="创建人"></bk-table-column>
                        <bk-table-column prop="create_time" label="创建时间"></bk-table-column>
                        <bk-table-column prop="desc" label="描述"></bk-table-column>
                    </bk-table>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['空间名']`)">
                <template slot-scope="{ row }">
                    <span class="first-manage-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['管理员']`)">
                <template slot-scope="{ row }">
                    <span class="first-manage-name" :title="row.name" @click="handleView(row)">
                        {{ row.members.length ? row.members.join(',') : '-' }}
                    </span>
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
            <bk-table-column :label="$t(`m.common['描述']`)">
                <template slot-scope="{ row }">
                    <span :title="row.description !== '' ? row.description : ''">{{ row.description || '--' }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)" width="300" fixed="right">
                <template slot-scope="{ row }">
                    <div class="operate_btn">
                        <bk-button theme="primary" text>{{ $t(`m.levelSpace['进入']`) }}</bk-button>
                        <bk-button theme="primary" text @click="handleClone(row)">
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
    export default {
        name: '',
        data () {
            return {
                searchValue: '',
                isFilter: false,
                tableList: [
                    {
                        id: 46,
                        name: 'admin',
                        created_time: '2022-10-13 14:53:36',
                        creator: 'admin',
                        updated_time: '2022-10-26 10:12:21',
                        updater: 'admin',
                        description: '测试',
                        members: ['admin', 'liu07'],
                        children: [
                            {
                                id: 46,
                                created_time: '2022-10-13 14:53:36',
                                creator: 'admin',
                                description: '测试',
                                members: ['admin', 'liu07']
                            },
                            {
                                id: 46,
                                created_time: '2022-10-13 14:53:36',
                                creator: 'admin',
                                description: '测试',
                                members: ['admin', 'liu07']
                            }
                        ]
                    }
                ],
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                currentBackup: 1,
                tableLoading: false,
                confirmLoading: false,
                confirmDialogTitle: '',
                confirmDialogSubTitle: '',
                isShowConfirmDialog: false,
                curOperateType: '',
                curId: -1,
                isShowApplyDialog: false,
                applyLoading: false,
                curName: '',
                showImageDialog: false,
                noFooter: false,
                radioValue: 'haveRole'
            };
        },
        computed: {
            ...mapGetters(['user'])
        },
        methods: {
            handleCreate () {
                console.log(this.user);
                this.$store.commit('updateIndex', 3);
                this.$router.push({
                    name: 'firstManageSpaceCreate',
                    params: {
                        id: 0
                    }
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

     .operate_btn {
        .bk-button-text {
            &:nth-child(n + 2) {
                margin-left: 10px;;
            }
        }
    }
}
</style>
