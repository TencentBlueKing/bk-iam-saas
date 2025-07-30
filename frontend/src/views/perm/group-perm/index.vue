<template>
  <div class="my-perm-group-perm">
    <div class="my-perm-group-perm-header">
      <bk-button
        :disabled="!currentSelectGroupList.length"
        @click="handleBatchQuit">
        {{ $t(`m.common['批量退出']`) }}
      </bk-button>
    </div>
    <bk-table
      ref="groupPermTableRef"
      data-test-id="myPerm_table_group"
      :data="curPageData"
      :size="'small'"
      :pagination="pageConf"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange"
      @select="handleSelectChange"
      @select-all="handleSelectAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column
        type="selection"
        align="center"
        :selectable="setDefaultSelect"
        :fixed="curPageData.length > 0 ? 'left' : false"
      />
      <bk-table-column
        :label="$t(`m.userGroup['用户组名']`)"
        :min-width="200"
        :fixed="curPageData.length > 0 ? 'left' : false">
        <template slot-scope="{ row }">
          <span class="user-group-name" :title="row.name" @click="goDetail(row)">{{ row.name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['描述']`)" :min-width="200">
        <template slot-scope="{ row }">
          <span :title="row.description !== '' ? row.description : ''">
            {{ row.description !== '' ? row.description : '--'}}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.grading['管理空间']`)" :min-width="200">
        <template slot-scope="{ row }">
          <span
            :title="row.role && row.role.name ? row.role.name : ''"
          >
            {{ row.role ? row.role.name : '--' }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.levelSpace['管理员']`)" width="300">
        <template slot-scope="{ row, $index }">
          <iam-edit-member-selector
            mode="detail"
            field="role_members"
            width="300"
            :placeholder="$t(`m.verify['请输入']`)"
            :value="row.role_members"
            :index="$index"
          />
        </template>
      </bk-table-column>
      <!-- 加入用户组时间 -->
      <bk-table-column :label="$t(`m.perm['加入用户组的时间']`)" width="160">
        <template slot-scope="{ row }">
          <span :title="row.created_time">{{ row.created_time.replace(/T/, ' ') }}</span>
        </template>
      </bk-table-column>
      <!-- 加入方式 -->
      <bk-table-column :label="$t(`m.perm['加入方式']`)">
        <template slot-scope="props">
          <span v-if="props.row.department_id === 0">{{ $t(`m.perm['直接加入']`) }}</span>
          <span v-else :title="`${$t(`m.perm['通过组织加入']`)}: ${props.row.department_name}`">
            {{ $t(`m.perm['通过组织加入']`) }}: {{ props.row.department_name }}
          </span>
        </template>
      </bk-table-column>
      <!-- 有效期 -->
      <bk-table-column :label="$t(`m.common['有效期']`)" prop="expired_at_display" width="120" />
      <!-- 操作 -->
      <bk-table-column
        :label="$t(`m.common['操作-table']`)"
        width="100"
        :fixed="curPageData.length > 0 ? 'right' : false"
      >
        <template slot-scope="props">
          <bk-button disabled text v-if="props.row.department_id !== 0">
            <span :title="$t(`m.perm['通过组织加入的组无法退出']`)">{{ $t(`m.common['退出']`) }}</span>
          </bk-button>
          <bk-button
            v-else
            class="mr10"
            theme="primary"
            text
            :title="isAdminGroup(props.row) ? $t(`m.perm['唯一管理员不可退出']`) : ''"
            :disabled="isAdminGroup(props.row)"
            @click="showQuitTemplates(props.row)">
            {{ $t(`m.common['退出']`) }}
          </bk-button>
        </template>
      </bk-table-column>
      <template slot="empty">
        <ExceptionEmpty
          :type="groupPermEmptyData.type"
          :empty-text="groupPermEmptyData.text"
          :tip-text="groupPermEmptyData.tip"
          :tip-type="groupPermEmptyData.tipType"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </template>
    </bk-table>

    <delete-dialog
      :show.sync="deleteDialogConf.visiable"
      :loading="deleteDialogConf.loading"
      :title="$t(`m.dialog['确认退出']`)"
      :sub-title="deleteDialogConf.msg"
      @on-after-leave="afterLeaveDelete"
      @on-cancel="cancelDelete"
      @on-sumbit="confirmDelete" />

    <render-group-perm-sideslider
      :show="isShowPermSidesilder"
      :name="curGroupName"
      :group-id="curGroupId"
      @animation-end="handleAnimationEnd" />

    <delete-action-dialog
      :show.sync="isShowDeleteDialog"
      :title="delActionDialogTitle"
      :tip="delActionDialogTip"
      :name="currentActionName"
      :loading="batchQuitLoading"
      :related-action-list="delActionList"
      @on-after-leave="handleAfterDeleteLeaveAction"
      @on-cancel="handleCancelDelete"
      @on-submit="handleSubmitDelete"
    />
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { formatCodeData, xssFilter } from '@/common/util';
  import { bus } from '@/common/bus';
  import DeleteDialog from '@/components/iam-confirm-dialog/index.vue';
  import DeleteActionDialog from '@/views/group/components/delete-related-action-dialog.vue';
  import RenderGroupPermSideslider from '../components/render-group-perm-sideslider';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';

  export default {
    name: '',
    components: {
      DeleteDialog,
      DeleteActionDialog,
      RenderGroupPermSideslider,
      IamEditMemberSelector
    },
    props: {
      personalGroupList: {
        type: Array,
        default: () => []
      },
      emptyData: {
        type: Object,
        default: () => {
          return {
            type: '',
            text: '',
            tip: '',
            tipType: ''
          };
        }
      },
      curSearchParams: {
        type: Object
      },
      curSearchPagination: {
        type: Object
      },
      isSearchPerm: {
        type: Boolean,
        default: false
      },
      checkGroupList: {
        type: Array,
        default: () => []
      },
      totalCount: {
        type: Number
      },
      componentLoading: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        dataList: [],
        curPageData: [],
        currentSelectGroupList: [],
        pageConf: {
          current: 1,
          count: 0,
          limit: 10
          // limitList: [5, 10, 20, 50]
        },
        deleteDialogConf: {
          visiable: false,
          loading: false,
          row: {},
          msg: ''
        },
        isShowPermSidesilder: false,
        curGroupName: '',
        curGroupId: '',
        sliderLoading: false,
        tableLoading: false,
        batchQuitLoading: false,
        groupPermEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        isShowDeleteDialog: false,
        delActionDialogTitle: '',
        delActionDialogTip: '',
        currentActionName: '',
        delActionList: []
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId', 'mainContentLoading']),
      isAdminGroup () {
        return (payload) => {
          if (payload) {
            const { attributes, role_members } = payload;
            // eslint-disable-next-line camelcase
            if (attributes && attributes.source_from_role && role_members && role_members.length === 1) {
              return true;
            }
            return false;
          }
        };
      }
    },
    watch: {
      personalGroupList: {
        handler (v) {
          // if (v.length) {
          //   this.dataList.splice(0, this.dataList.length, ...v);
          //   this.initPageConf();
          //   this.curPageData = this.getDataByPage(this.pageConf.current);
          // }
          if (this.pageConf.current === 1) {
            this.pageConf = Object.assign(this.pageConf, { count: this.totalCount });
            if (this.isSearchPerm) {
              this.pageConf.limit = this.curSearchPagination.limit;
            }
            this.curPageData = [...v];
            return;
          }
          this.resetPagination(this.pageConf.limit);
        },
        immediate: true
      },
      emptyData: {
        handler (value) {
          this.groupPermEmptyData = Object.assign({}, value);
        },
        immediate: true
      },
      checkGroupList: {
        handler (value) {
          const list = value.filter(item =>
            !this.currentSelectGroupList.map(v => v.id.toString()).includes(item.id.toString()));
          this.currentSelectGroupList = [...this.currentSelectGroupList, ...list];
        },
        immediate: true
      }
    },
    methods: {
      setDefaultSelect () {
        return this.curPageData.length > 0;
      },

      /**
       * 获取 user 信息
      */
      async fetchUser () {
        try {
          await this.$store.dispatch('userInfo');
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSidesilder = false;
      },

      /**
       * 初始化弹层翻页条
       */
      initPageConf () {
        this.pageConf.current = 1;
        const total = this.dataList.length;
        this.pageConf.count = total;
      },

      /**
       * 翻页回调
       *
       * @param {number} page 当前页
       */
      handlePageChange (page = 1) {
        this.pageConf.current = page;
        this.getDataByPage();
      },

      /**
       * 获取当前这一页的数据
       *
       * @param {number} page 当前页
       *
       * @return {Array} 当前页数据
       */
      async getDataByPage () {
        try {
          let url = '';
          let params = {};
          const { current, limit } = this.pageConf;
          if (!this.mainContentLoading && !this.componentLoading) {
            this.tableLoading = true;
          }
          if (this.isSearchPerm) {
            url = 'perm/getUserGroupSearch';
            params = {
              ...this.curSearchParams,
              limit,
              offset: limit * (current - 1)
            };
          } else {
            url = 'perm/getPersonalGroups';
            params = {
              page_size: limit,
              page: current
            };
          }
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(url, params);
          this.pageConf.count = data.count || 0;
          const currentSelectGroupList = this.currentSelectGroupList.map(item => item.id.toString());
          this.curPageData.splice(0, this.curPageData.length, ...(data.results || []));
          this.groupPermEmptyData = formatCodeData(code, this.groupPermEmptyData, data.count === 0);
          setTimeout(() => {
            if (!this.currentSelectGroupList.length) {
              this.$refs.groupPermTableRef && this.$refs.groupPermTableRef.clearSelection();
            }
            this.curPageData.forEach(item => {
              if (item.role_members && item.role_members.length) {
                const hasName = item.role_members.some((v) => v.username);
                if (!hasName) {
                  item.role_members = item.role_members.map(v => {
                    return {
                      username: v,
                      readonly: false
                    };
                  });
                }
              }
              if (currentSelectGroupList.includes(item.id.toString())) {
                this.$refs.groupPermTableRef && this.$refs.groupPermTableRef.toggleRowSelection(item, true);
              }
            });
          }, 200);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.currentSelectGroupList = [];
          this.groupPermEmptyData = formatCodeData(code, this.groupPermEmptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
          if (this.isSearchPerm) {
            bus.$emit('on-perm-tab-count', { active: 'GroupPerm', count: this.pageConf.count });
          }
        }
        // if (!page) {
        //     this.pageConf.current = page = 1;
        // }
        // let startIndex = (page - 1) * this.pageConf.limit;
        // let endIndex = page * this.pageConf.limit;
        // if (startIndex < 0) {
        //     startIndex = 0;
        // }
        // if (endIndex > this.dataList.length) {
        //     endIndex = this.dataList.length;
        // }
        // return this.dataList.slice(startIndex, endIndex);
      },

      fetchSelectedGroupCount () {
        this.$nextTick(() => {
          const selectionCount = document.getElementsByClassName('bk-page-selection-count');
          if (this.$refs.groupPermTableRef && selectionCount && selectionCount.length && selectionCount[0].children) {
            selectionCount[0].children[0].innerHTML = xssFilter(this.currentSelectGroupList.length);
          }
        });
      },
      
      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectGroupList.push(row);
            } else {
              this.currentSelectGroupList = this.currentSelectGroupList.filter(
                (item) => item.id.toString() !== row.id.toString()
              );
            }
            this.fetchSelectedGroupCount();
            this.$emit('on-select-group', this.currentSelectGroupList);
          },
          all: () => {
            const tableList = _.cloneDeep(this.curPageData);
            const selectGroups = this.currentSelectGroupList.filter(item =>
              !tableList.map(v => v.id.toString()).includes(item.id.toString()));
            this.currentSelectGroupList = [...selectGroups, ...payload];
            this.fetchSelectedGroupCount();
            this.$emit('on-select-group', this.currentSelectGroupList);
          }
        };
        return typeMap[type]();
      },

      /**
       * 每页显示多少条变化的回调
       *
       * @param {number} currentLimit 变化后每页多少条的数量
       * @param {number} prevLimit 变化前每页多少条的数量
       */
      handlePageLimitChange (currentLimit, prevLimit) {
        this.pageConf = Object.assign(this.pageConf, { current: 1, limit: currentLimit });
        this.handlePageChange(this.pageConf.current);
      },

      handleSelectAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handleSelectChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },

      handleBatchQuit () {
        this.handleDeleteActions('quit');
      },

      handleEmptyRefresh () {
        this.resetPagination();
        this.$emit('on-refresh');
      },

      handleEmptyClear () {
        this.resetPagination();
        this.$emit('on-clear');
      },

      /**
       * 跳转到 group-perm 详情
       *
       * @param {Object} row 当前行对象
       */
      goDetail (row) {
        this.curGroupName = row.name;
        this.curGroupId = row.id;
        this.isShowPermSidesilder = true;
        // this.$router.push({
        //     name: 'groupPermDetail',
        //     params: Object.assign({}, { id: row.id, name: row.name }, this.$route.params),
        //     query: this.$route.query
        // })
      },

      /**
       * 显示脱离模板弹框
       *
       * @param {Object} row 当前行对象
       */
      showQuitTemplates (row) {
        this.deleteDialogConf.visiable = true;
        this.deleteDialogConf.row = Object.assign({}, row);
        this.deleteDialogConf.msg = `${this.$t(`m.common['退出']`)}${this.$t(`m.common['【']`)}${row.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['，']`)}${this.$t(`m.info['将不再拥有该用户组的权限']`)}${this.$t(`m.common['。']`)}`;
      },

      /**
       * 脱离模板确认函数
       */
      async confirmDelete () {
        this.deleteDialogConf.loading = true;
        try {
          await this.$store.dispatch('perm/quitGroupPerm', {
            type: 'group',
            id: this.deleteDialogConf.row.id
          });
          this.cancelDelete();
          this.messageSuccess(this.$t(`m.info['退出成功']`), 3000);
          this.currentSelectGroupList = [];
          this.refreshTableData();
        } catch (e) {
          this.deleteDialogConf.loading = false;
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      // 批量操作对应操作项
      handleDeleteActions (type) {
        const typeMap = {
          quit: () => {
            this.isShowDeleteDialog = true;
            this.delActionDialogTitle = this.$t(`m.dialog['确认批量退出所选的用户组吗？']`);
            const adminGroups = this.currentSelectGroupList.filter(item =>
              item.attributes && item.attributes.source_from_role
              && item.role_members.length === 1 && item.department_id === 0
            );
            if (adminGroups.length) {
              this.delActionDialogTip = this.$t(`m.perm['存在用户组不可退出（唯一管理员不能退出）']`);
              this.delActionList = adminGroups;
            }
          }
        };
        return typeMap[type]();
      },

      async handleSubmitDelete () {
        const selectGroups = this.currentSelectGroupList.filter(item =>
          !this.delActionList.map(v => v.id.toString()).includes(item.id.toString()));
        if (!selectGroups.length) {
          this.messageWarn(this.$t(`m.perm['当前勾选项都为不可退出的用户组（唯一管理员不能退出）']`), 3000);
          return;
        }
        this.batchQuitLoading = true;
        try {
          for (let i = 0; i < selectGroups.length; i++) {
            await this.$store.dispatch('perm/quitGroupPerm', {
              type: 'group',
              id: selectGroups[i].id
            });
          }
          this.isShowDeleteDialog = false;
          this.currentSelectGroupList = [];
          this.messageSuccess(this.$t(`m.info['退出成功']`), 3000);
          this.refreshTableData();
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.batchQuitLoading = false;
        }
      },

      handleCancelDelete () {
        this.isShowDeleteDialog = false;
        this.delActionList = [];
      },

      handleAfterDeleteLeaveAction () {
        this.currentActionName = '';
        this.delActionDialogTitle = '';
        this.delActionDialogTip = '';
        this.delActionList = [];
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

      resetPagination (limit = 10) {
        this.pageConf = Object.assign(this.pageConf, { current: 1, limit });
      },

      refreshTableData () {
        const { limit } = this.pageConf;
        this.resetPagination(limit);
        this.getDataByPage();
        this.fetchSelectedGroupCount();
        if (this.isSearchPerm) {
          return;
        }
        this.$emit('refresh', true, limit);
      }
    }
  };
</script>
<style lang="postcss">
    @import './index.css';
</style>
