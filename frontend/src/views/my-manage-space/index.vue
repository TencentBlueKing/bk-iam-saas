<template>
    <div class="iam-level-manage-space-wrapper">
        <render-search>
            <bk-button theme="primary" @click="handleCreate" data-test-id="level-manage_space_btn_create">
                {{ $t(`m.common['申请新建']`) }}
            </bk-button>
            <div slot="right">
                <div style="display: flex">
                    <bk-radio-group v-model="radioValue" @change="handlerChange">
                        <bk-radio-button :value="'haveRole'">
                            {{ $t(`m.levelSpace['我有权限']`) }}
                        </bk-radio-button>
                        <bk-radio-button :value="'allSpace'">
                            {{ $t(`m.levelSpace['全部空间']`) }}
                        </bk-radio-button>
                    </bk-radio-group>
                    <bk-input
                        :placeholder="$t(`m.levelSpace['搜索空间名、描述、创建人、创建时间']`)"
                        clearable
                        style="width: 420px"
                        right-icon="bk-icon icon-search"
                        v-model="searchValue"
                        @enter="handleSearch"
                    />
                </div>
            </div>
        </render-search>
        <bk-table
            :data="tableList"
            size="small"
            :class="{ 'set-border': tableLoading }"
            ext-cls="level-manage-table"
            :pagination="pagination"
            @page-change="handlePageChange"
            @page-limit-change="handleLimitChange"
            v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
        >
            <bk-table-column :label="$t(`m.levelSpace['空间名']`)">
                <template slot-scope="{ row }">
                    <span class="first-manage-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
                </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['上级空间']`)">
                <template slot-scope="{ row }">
                    <span class="first-manage-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
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
            <bk-table-column :label="$t(`m.common['操作']`)" width="150">
                <template slot-scope="{ row }">
                    <section>
                        <bk-button theme="primary" text>{{ $t(`m.levelSpace['进入']`) }}</bk-button>
                        <bk-button theme="primary" text @click="handleClone(row)">
                            {{ $t(`m.levelSpace['克隆']`) }}
                        </bk-button>
                        <bk-button theme="primary" text @click="handleDelete(row)">
                            {{ $t(`m.levelSpace['删除']`) }}
                        </bk-button>
                    </section>
                </template>
            </bk-table-column>
        </bk-table>
    </div>
</template>

<script>
    // import { mapGetters } from 'vuex';
    export default {
        name: '',
        data () {
            return {
                searchValue: '',
                isFilter: false,
                tableList: [],
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
        methods: {
            handleCreate () {
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

<style lang="postcss">
.iam-level-manage-space-wrapper {
  .level-manage-table {
    margin-top: 16px;
  }
}
</style>
