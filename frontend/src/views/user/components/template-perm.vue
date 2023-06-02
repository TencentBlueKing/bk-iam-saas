<template>
  <div class="iam-template-perm-wrapper" v-bkloading="{ isLoading: pageLoading, opacity: 1 }">
    <!-- <bk-button type="button" theme="primary" title="申请模板权限" style="margin-bottom: 20px;">申请模板权限</bk-button> -->
    <div class="iam-template-perm-list" v-if="!pageLoading">
      <bk-table
        :data="curPageData"
        :size="'small'"
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
            <bk-button theme="primary" style="margin-left: 10px;" text
              @click="showQuitTemplates(row)">{{ $t(`m.common['移除']`) }}</bk-button>
          </template>
        </bk-table-column>
        <template slot="empty">
          <ExceptionEmpty
            :type="emptyData.type"
            :empty-text="emptyData.text"
            :tip-text="emptyData.tip"
            :tip-type="emptyData.tipType"
            @on-refresh="handleEmptyRefresh"
          />
        </template>
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

    <!-- <bk-dialog v-model="deleteDialogConf.visiable"
            :loading="deleteDialogConf.loading"
            :mask-close="false"
            :esc-close="false"
            :close-icon="false"
            @confirm="confirmDelete"
            @cancel="cancelDelete"
            @after-leave="afterLeaveDelete"
            title="脱离模板">
            <p style="text-align: center;">{{deleteDialogConf.msg}}</p>
        </bk-dialog> -->

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
        <!-- style="padding: 0 30px 17px 30px;" -->
        <component :is="renderDetailCom" :data="previewData" />
      </div>
    </bk-sideslider>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import DeleteDialog from '@/components/iam-confirm-dialog/index.vue';
  import CheckUpdateSideslider from '../../perm-template/components/check-update-sideslider';
  import PreviewResourceSideslider from '../../perm-template/components/preview-resource-sideslider';
  import RenderPermSideslider from '../../perm/components/render-template-perm-sideslider';
  import RenderDetail from '../../perm/components/render-detail';
  import { formatCodeData } from '@/common/util';

  export default {
    name: '',
    components: {
      DeleteDialog,
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
          // limitList: [5, 10, 20, 50]
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

        isShowPermSidesilder: false,
        permSidesilderTitle: '',
        curTemplateId: '',
        curTemplateVersion: '',

        previewData: [],
        sidesliderTitle: '',
        isShowSideslider: false,
        renderDetailCom: 'RenderDetail',

        pageLoading: false,
        tableLoading: false,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
            ...mapGetters(['user'])
    },
    async created () {
      await this.fetchPermTemplates(false, true);
    },
    methods: {
      /**
       * 获取权限模板列表
       */
      async fetchPermTemplates (isTableLoading = false, isPageLoading = false) {
        this.tableLoading = isTableLoading;
        this.pageLoading = isPageLoading;
        const { type } = this.data;
        try {
          const { code, data } = await this.$store.dispatch('perm/getPermTemplates', {
            subjectType: type === 'user' ? type : 'department',
            subjectId: type === 'user' ? this.data.username : this.data.id
          });
          this.dataList.splice(0, this.dataList.length, ...(data || []));
          this.initPageConf();
          this.curPageData = this.getDataByPage(this.pageConf.current);
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
          this.tableLoading = false;
          this.pageLoading = false;
        }
      },

      /**
       * 初始化弹层翻页条
       */
      initPageConf () {
        this.pageConf.current = 1;
        const total = this.dataList.length;
        this.pageConf.count = total;
      },

      async handleEmptyRefresh () {
        await this.fetchPermTemplates(false, true);
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
        // this.$router.push({
        //     name: 'templatePermDetail',
        //     params: Object.assign({}, { id: row.id }, this.$route.params),
        //     query: Object.assign({}, { version: row.version }, this.$route.query)
        // })
      },

      handleOnView (payload) {
        const { name, data } = payload;
        this.sidesliderTitle = `${this.$t(`m.common['操作']`)}${this.$t(`m.common['【']`)}${name}${this.$t(`m.common['【']`)}${this.$t(`m.common['的资源实例']`)}`;
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
      },

      handlePreviewSildesliderClose () {
        this.previewResourceParams = [];
        this.previewResourceSildesliderTitle = '';
        this.isShowPreviewResourceSildeslider = false;
      }
    }
  };
</script>
<style lang="postcss">
    .iam-template-perm-wrapper {
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
