<template>
    <div class="iam-depart-perm-wrapper" v-bkloading="{ isLoading: pageLoading, opacity: 1 }">
        <bk-button
            theme="primary"
            style="margin-bottom: 20px;"
            @click="handleAddPerm"
            v-if="!pageLoading">
            {{ $t(`m.userGroup['添加权限']`) }}
        </bk-button>
        <div>
            <bk-table
                :data="curPageData"
                :size="'small'"
                v-if="!pageLoading"
                :pagination="pageConf"
                :ext-cls="tableLoading ? 'is-be-loading' : ''"
                v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
                @page-change="handlePageChange"
                @page-limit-change="handlePageLimitChange">
                <bk-table-column :label="$t(`m.permTemplate['模板名']`)">
                    <template slot-scope="{ row }">
                        <span class="template-name" :title="row.name" @click="goDetail(row)">{{ row.name }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.common['所属系统']`)" prop="system.name"></bk-table-column>
                <bk-table-column :label="$t(`m.common['有效期']`)" prop="expired_at_display"></bk-table-column>
                <bk-table-column :label="$t(`m.perm['最近一次更新时间']`)" width="240">
                    <template slot-scope="{ row }">
                        <span :title="row.updated_time">{{ row.updated_time }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.common['操作']`)" width="200">
                    <template slot-scope="{ row }">
                        <bk-button
                            theme="primary"
                            text
                            :disabled="row.is_latest"
                            @click="handleCheckUpdate(row)">
                            {{ row.is_latest ? $t(`m.permTemplate['最新版本']`) : $t(`m.permTemplate['检查更新']`) }}
                        </bk-button>
                        <bk-button theme="primary" style="margin-left: 10px;" text @click="showQuitTemplates(row)">
                            {{ $t(`m.common['移除']`) }}
                        </bk-button>
                    </template>
                </bk-table-column>
            </bk-table>
        </div>

        <delete-dialog
            :show.sync="deleteDialogConf.visiable"
            :loading="deleteDialogConf.loading"
            :title="$t(`m.dialog['确认移除']`)"
            :sub-title="deleteDialogConf.msg"
            @on-after-leave="afterLeaveDelete"
            @on-cancel="cancelDelete"
            @on-sumbit="confirmDelete" />

        <check-update-sideslider
            :is-show="isShowCheckUpdateSildeslider"
            :title="checkUpdateSildesliderTitle"
            :params="checkUpdateParams"
            @on-view="handleViewResource"
            @on-sync="handleSyncAfter"
            @animation-end="handleUpdateSildesliderClose" />

        <preview-resource-sideslider
            :is-show="isShowPreviewResourceSildeslider"
            :title="previewResourceSildesliderTitle"
            :params="previewResourceParams"
            @animation-end="handlePreviewSildesliderClose" />

        <perm-template-dialog
            :show.sync="isShowPermTemplateDialog"
            :name="permTemplateDialogTitleName"
            :loading="addPermLoading"
            :default-value="defaultValue"
            :show-expired-at="true"
            @on-cancel="handleCancelSelect"
            @on-after-leave="handleAfterLeave"
            @on-sumbit="handleSumbitSelectTemplate" />

        <render-perm-sideslider
            :show="isShowPermSidesilder"
            :title="permSidesilderTitle"
            :template-id="curTemplateId"
            :template-version="curTemplateVersion"
            @on-view="handleOnView"
            @animation-end="handleAnimationEnd" />

        <bk-sideslider
            :is-show.sync="isShowSideslider"
            :title="sidesliderTitle"
            :width="880"
            :quick-close="true"
            @animation-end="handleViewResourceAnimationEnd">
            <div slot="content">
                <component :is="renderDetailCom" :data="previewData" />
            </div>
        </bk-sideslider>
    </div>
</template>
<script>
    import _ from 'lodash';
    import { mapGetters } from 'vuex';
    import DeleteDialog from '@/components/iam-confirm-dialog/index.vue';
    import PermTemplateDialog from '@/components/render-perm-template-dialog';
    import CheckUpdateSideslider from '../../perm-template/components/check-update-sideslider';
    import PreviewResourceSideslider from '../../perm-template/components/preview-resource-sideslider';

    import RenderPermSideslider from '../../perm/components/render-template-perm-sideslider';
    import RenderDetail from '../../perm/components/render-detail';

    export default {
        name: '',
        components: {
            DeleteDialog,
            PermTemplateDialog,
            CheckUpdateSideslider,
            PreviewResourceSideslider,
            RenderPermSideslider,
            RenderDetail
        },
        props: {
            data: {
                type: Object,
                default: () => {
                    return {};
                }
            }
        },
        data () {
            return {
                dataList: [],
                pageConf: {
                    current: 1,
                    count: 0,
                    limit: 10
                },
                curPageData: [],
                deleteDialogConf: {
                    visiable: false,
                    loading: false,
                    row: {},
                    msg: ''
                },

                isShowCheckUpdateSildeslider: false,
                checkUpdateSildesliderTitle: '',
                isShowPreviewResourceSildeslider: false,
                previewResourceSildesliderTitle: '',
                checkUpdateParams: {},
                previewResourceParams: [],
                isShowPermTemplateDialog: false,
                permTemplateDialogTitleName: '',
                addPermLoading: false,
                tableLoading: false,

                isShowPermSidesilder: false,
                permSidesilderTitle: '',
                curTemplateId: '',
                curTemplateVersion: '',

                previewData: [],
                sidesliderTitle: '',
                isShowSideslider: false,
                renderDetailCom: 'RenderDetail',

                pageLoading: false
            };
        },
        computed: {
            ...mapGetters(['user']),
            defaultValue () {
                return this.dataList.map(item => item.id);
            }
        },
        async created () {
            await this.fetchPermTemplates(false, true);
        },
        methods: {
            /**
             * 获取权限模板列表
             */
            async fetchPermTemplates (isTableLoading = false, isPageLoading = false) {
                // if (!isTableLoading) {
                //     this.$emit('on-init', false)
                // }
                this.tableLoading = isTableLoading;
                this.pageLoading = isPageLoading;
                const { type } = this.data;
                try {
                    const res = await this.$store.dispatch('perm/getPermTemplates', {
                        subjectType: type === 'user' ? type : 'department',
                        subjectId: type === 'user' ? this.data.username : this.data.id
                    });
                    this.dataList.splice(0, this.dataList.length, ...(res.data || []));
                    this.initPageConf();
                    this.curPageData = this.getDataByPage(this.pageConf.current);
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
                    // if (!isTableLoading) {
                    //     this.$emit('on-init', true)
                    // }
                    this.tableLoading = false;
                    this.pageLoading = false;
                }
            },

            handleAddPerm () {
                const { type } = this.data;
                if (type === 'user') {
                    this.permTemplateDialogTitleName = this.data.username;
                } else {
                    this.permTemplateDialogTitleName = this.data.name;
                }
                this.isShowPermTemplateDialog = true;
            },

            async handleSumbitSelectTemplate (payload) {
                let expiredAt = payload.expired_at;
                // 4102444800：非永久时需加上当前时间
                if (expiredAt !== 4102444800) {
                    const nowTimestamp = +new Date() / 1000;
                    const tempArr = String(nowTimestamp).split('');
                    const dotIndex = tempArr.findIndex(item => item === '.');
                    const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
                    expiredAt = expiredAt + nowSecond;
                }
                this.addPermLoading = true;
                const { type } = this.data;
                try {
                    await this.$store.dispatch('perm/addDepartTemplates', {
                        subjectType: type === 'user' ? type : 'department',
                        subjectId: type === 'user' ? this.data.username : this.data.id,
                        template_ids: payload.data.map(item => item.id),
                        expired_at: expiredAt
                    });
                    this.isShowPermTemplateDialog = false;
                    this.messageSuccess(this.$t(`m.info['添加权限成功']`), 2000);
                    await this.fetchPermTemplates(true);
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
                    this.addPermLoading = false;
                }
            },

            handleCancelSelect () {
                this.isShowPermTemplateDialog = false;
            },

            handleAfterLeave () {
                this.permTemplateDialogTitleName = '';
            },

            /**
             * 初始化弹层翻页条
             */
            initPageConf () {
                this.pageConf.current = 1;
                const total = this.dataList.length;
                this.pageConf.count = total;
            },

            handleCheckUpdate (payload) {
                const { type } = this.data;
                this.checkUpdateParams = _.cloneDeep({
                    ...payload,
                    system_id: payload.system.id,
                    templateId: payload.id,
                    type: type === 'user' ? type : 'department',
                    id: type === 'user' ? this.data.username : this.data.id
                });
                this.checkUpdateSildesliderTitle = `${this.$t(`m.permTemplate['同步权限']`)}-${payload.name}`;
                this.isShowCheckUpdateSildeslider = true;
            },

            handlePreviewSildesliderClose () {
                this.previewResourceParams = [];
                this.previewResourceSildesliderTitle = '';
                this.isShowPreviewResourceSildeslider = false;
            },

            handleOnView (payload) {
                const { name, data } = payload;
                this.sidesliderTitle = `${this.$t(`m.common['操作']`)}${this.$t(`m.common['【']`)}${name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的资源实例']`)}`;
                this.previewData = _.cloneDeep(data);
                this.isShowSideslider = true;
            },

            handleAnimationEnd () {
                this.permSidesilderTitle = '';
                this.curTemplateVersion = '';
                this.curTemplateId = '';
                this.isShowPermSidesilder = false;
            },

            handleViewResourceAnimationEnd () {
                this.previewData = [];
                this.sidesliderTitle = '';
                this.isShowSideslider = false;
            },

            /**
             * 翻页回调
             *
             * @param {number} page 当前页
             */
            handlePageChange (page = 1) {
                this.pageConf.current = page;
                const data = this.getDataByPage(page);
                this.curPageData.splice(0, this.curPageData.length, ...data);
            },

            /**
             * 获取当前这一页的数据
             *
             * @param {number} page 当前页
             *
             * @return {Array} 当前页数据
             */
            getDataByPage (page) {
                if (!page) {
                    this.pageConf.current = page = 1;
                }
                let startIndex = (page - 1) * this.pageConf.limit;
                let endIndex = page * this.pageConf.limit;
                if (startIndex < 0) {
                    startIndex = 0;
                }
                if (endIndex > this.dataList.length) {
                    endIndex = this.dataList.length;
                }
                return this.dataList.slice(startIndex, endIndex);
            },

            /**
             * 每页显示多少条变化的回调
             *
             * @param {number} currentLimit 变化后每页多少条的数量
             * @param {number} prevLimit 变化前每页多少条的数量
             */
            handlePageLimitChange (currentLimit, prevLimit) {
                this.pageConf.limit = currentLimit;
                this.pageConf.current = 1;
                this.handlePageChange(this.pageConf.current);
            },

            /**
             * 跳转到 template-perm 详情
             *
             * @param {Object} row 当前行对象
             */
            goDetail (row) {
                this.curTemplateId = row.id;
                this.curTemplateVersion = row.version;
                this.permSidesilderTitle = `${row.name}(${row.system.name})`;
                this.isShowPermSidesilder = true;
            },

            /**
             * 显示脱离模板弹框
             *
             * @param {Object} row 当前行对象
             */
            showQuitTemplates (row) {
                this.deleteDialogConf.visiable = true;
                this.deleteDialogConf.row = Object.assign({}, row);
                this.deleteDialogConf.msg = `${this.$t(`m.info['解除与权限模板']`)}${this.$t(`m.common['【']`)}${row.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['的关联']`)}${this.$t(`m.common['，']`)}${this.$t(`m.info['当前用户将不再继承该模板权限']`)}${this.$t(`m.common['。']`)}`;
            },

            /**
             * 脱离模板确认函数
             */
            async confirmDelete () {
                this.deleteDialogConf.loading = true;
                const { type } = this.data;
                try {
                    await this.$store.dispatch('perm/quitPermTemplates', {
                        subjectType: type === 'user' ? type : 'department',
                        subjectId: type === 'user' ? this.data.username : this.data.id,
                        id: this.deleteDialogConf.row.id
                    });
                    this.cancelDelete();
                    this.messageSuccess(this.$t(`m.info['解除成功']`), 2000);
                    await this.fetchPermTemplates(true);
                } catch (e) {
                    this.deleteDialogConf.loading = false;
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
             * 脱离模板取消函数
             */
            cancelDelete () {
                this.deleteDialogConf.visiable = false;
            },

            /**
             * 脱离模板 afterLeave 函数
             */
            afterLeaveDelete () {
                this.deleteDialogConf.row = Object.assign({}, {});
                this.deleteDialogConf.msg = '';
                this.deleteDialogConf.loading = false;
            },

            handleViewResource (payload) {
                this.previewResourceParams = _.cloneDeep(payload.params);
                this.previewResourceSildesliderTitle = `${this.$t(`m.permTemplate['变更对比']`)}-${payload.action_name}`;
                this.isShowPreviewResourceSildeslider = true;
            },

            handleSyncAfter () {
                this.fetchPermTemplates(true);
            },

            handleUpdateSildesliderClose () {
                this.checkUpdateParams = {};
                this.checkUpdateSildesliderTitle = '';
                this.isShowCheckUpdateSildeslider = false;
            }
        }
    };
</script>
<style lang="postcss">
    .iam-depart-perm-wrapper {
        height: calc(100vh - 204px);
        .bk-table {
            border-right: none;
            border-bottom: none;
            &.is-be-loading {
                border-bottom: 1px solid #dfe0e5;
            }
            .template-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
        }
    }
</style>
