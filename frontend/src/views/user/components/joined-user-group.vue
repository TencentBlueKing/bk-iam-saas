<template>
  <div class="iam-joined-user-group-wrapper" v-bkloading="{ isLoading: pageLoading, opacity: 1 }">
    <div class="mb20 iam-joined-user-group-button">
      <bk-button
        theme="primary" @click="handleBatchAddUserGroup" data-test-id="group_btn_create">
        {{ $t(`m.permTemplate['添加用户组']`) }}
      </bk-button>
      <bk-button
        :disabled="!currentSelectGroupList.length"
        @click="handleBatchQuit">
        {{ $t(`m.common['批量退出']`) }}
      </bk-button>
      <bk-button
        :disabled="isBatchDisabled"
        @click="handleBatchAddMember"
        data-test-id="group_btn_create"
      >
        {{ $t(`m.common['批量添加成员']`) }}
      </bk-button>
    </div>
    <div>
      <bk-table
        v-if="!pageLoading"
        ref="groupPermTableRef"
        :data="curPageData"
        :size="'small'"
        :pagination="pageConf"
        :ext-cls="tableLoading ? 'is-be-loading' : ''"
        :max-height="tableHeight"
        v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
        @page-change="handlePageChange"
        @page-limit-change="handlePageLimitChange"
        @select="handleGroupChange"
        @select-all="handleAllGroupChange">
        <bk-table-column
          type="selection"
          align="center"
          :selectable="setDefaultSelect"
          :fixed="curPageData.length > 0 ? 'left' : false"
        />
        <bk-table-column
          :label="$t(`m.userGroup['用户组名']`)"
          :min-width="200"
          :fixed="curPageData.length > 0 ? 'left' : false"
        >
          <template slot-scope="{ row }">
            <span class="user-group-name" :title="row.name" @click="goDetail(row)">
              {{ row.name }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.userGroup['用户/组织']`)" :min-width="200">
          <template slot-scope="{ row }">
            <div
              v-if="row.user_count > 0 || row.department_count > 0 || row.subject_template_count > 0"
              class="member-wrapper"
            >
              <span class="user" v-if="row.user_count > 0">
                <Icon type="personal-user" />
                {{ row.user_count }}
              </span>
              <span class="depart" v-if="row.department_count > 0">
                <Icon type="organization-fill" />
                {{ row.department_count }}
              </span>
              <span class="template" v-if="row.subject_template_count > 0">
                <Icon type="renyuanmuban" />
                {{ row.subject_template_count }}
              </span>
            </div>
            <div v-else>--</div>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.common['有效期']`)" prop="expired_at_display" width="120" />
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
        <bk-table-column :label="$t(`m.perm['加入用户组的时间']`)" width="160">
          <template slot-scope="{ row }">
            <span :title="row.created_time">{{ row.created_time.replace(/T/, ' ') }}</span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.common['描述']`)" width="200">
          <template slot-scope="{ row }">
            <span :title="row.description !== '' ? row.description : ''">
              {{ row.description !== '' ? row.description : '--'}}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t(`m.perm['加入方式']`)" :min-width="200">
          <template slot-scope="props">
            <span v-if="props.row.department_id === 0">{{ $t(`m.perm['直接加入']`) }}</span>
            <span v-else :title="`${$t(`m.perm['通过组织加入']`)}: ${props.row.department_name}`">
              {{ $t(`m.perm['通过组织加入']`) }}: {{ props.row.department_name }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t(`m.common['操作-table']`)"
          :width="curLanguageIsCn ? 120 : 160"
          :fixed="curPageData.length > 0 ? 'right' : ''"
        >
          <template slot-scope="{ row }">
            <bk-button
              theme="primary"
              text
              :disabled="row.readonly"
              @click="handleAddMember(row)"
              style="margin-right: 5px;"
            >
              {{ $t(`m.common['添加成员']`) }}
            </bk-button>
            <template>
              <bk-button disabled text v-if="row.department_id !== 0">
                <span :title="$t(`m.perm['通过组织加入的组无法退出']`)">{{ $t(`m.common['退出']`) }}</span>
              </bk-button>
              <bk-button
                v-else
                theme="primary"
                text
                :title="isAdminGroup(row) ? $t(`m.perm['唯一管理员不可退出']`) : ''"
                :disabled="isAdminGroup(row)"
                @click="showQuitTemplates(row)">
                {{ $t(`m.common['退出']`) }}
              </bk-button>
            </template>
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
    </div>

    <bk-dialog
      v-model="isShowUserGroupDialog"
      width="1220"
      :show-footer="false"
      header-position="left"
      ext-cls="iam-attach-action-preview-dialog"
      @after-leave="handleAfterEditLeave">
      <div class="attach-action-preview-content-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="!isLoading">
          <div class="user-group-table">
            <div class="search-wrapper mb20">
              <iam-search-select
                @on-change="handleSearch"
                :data="searchData"
                :value="searchValue"
                :placeholder="$t(`m.applyEntrance['超级管理员申请加入用户组搜索提示']`)"
                :quick-search-method="quickSearchMethod" />
            </div>
            <bk-table
              size="small"
              ref="groupTableRef"
              ext-cls="user-group-table"
              :max-height="400"
              :data="tableList"
              :class="{ 'set-border': tableLoading }"
              :pagination="pagination"
              @page-change="pageChange"
              @page-limit-change="limitChange"
              @select="handlerChange"
              @select-all="handlerAllChange"
              v-bkloading="{ isLoading: tableDialogLoading, opacity: 1 }">
              <bk-table-column type="selection" align="center"></bk-table-column>
              <bk-table-column :label="$t(`m.userGroup['用户组名']`)">
                <template slot-scope="{ row }">
                  <span class="user-group-name" :title="row.name">
                    {{ row.name }}
                  </span>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.common['描述']`)">
                <template slot-scope="{ row }">
                  <span :title="row.description !== '' ? row.description : ''">
                    {{ row.description || '--' }}
                  </span>
                </template>
              </bk-table-column>
              <template slot="empty">
                <ExceptionEmpty
                  :type="emptyDialogData.type"
                  :empty-text="emptyDialogData.text"
                  :tip-text="emptyDialogData.tip"
                  :tip-type="emptyDialogData.tipType"
                  @on-clear="handleEmptyDialogClear"
                  @on-refresh="handleEmptyDialogRefresh"
                />
              </template>
            </bk-table>
          </div>
          <p class="user-group-error" v-if="isShowGroupError">{{ $t(`m.permApply['请选择用户组']`) }}</p>
        </template>
        <section ref="expiredAtRef" class="mt20">
          <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" :cur-role="curRole" />
        </section>

        <section class="button-warp">
          <bk-button
            class="mb20"
            :disabled="currentSelectList.length < 1"
            theme="primary" @click="handleBatchUserGroupSubmit" data-test-id="group_btn_create">
            {{ $t(`m.common['提交']`) }}
          </bk-button>
          <bk-button
            class="mb20"
            theme="default" @click="handleBatchUserGroupCancel" data-test-id="group_btn_create">
            {{ $t(`m.common['取消']`) }}
          </bk-button>
        </section>
      </div>
    </bk-dialog>

    <delete-dialog
      :show.sync="deleteDialogConf.visiable"
      :loading="deleteDialogConf.loading"
      :title="$t(`m.dialog['确认退出']`)"
      :sub-title="deleteDialogConf.msg"
      @on-after-leave="afterLeaveDelete"
      @on-cancel="cancelDelete"
      @on-sumbit="confirmDelete" />

    <render-perm-sideslider
      :show="isShowPermSidesilder"
      :name="curGroupName"
      :group-id="curGroupId"
      @animation-end="handleAnimationEnd" />

    <delete-action-dialog
      :show.sync="isShowDeleteDialog"
      :title="delActionDialogTitle"
      :tip="delActionDialogTip"
      :name="currentActionName"
      :related-action-list="delActionList"
      @on-after-leave="handleAfterDeleteLeaveAction"
      @on-cancel="handleCancelDelete"
      @on-submit="handleSubmitDelete"
    />

    <add-member-dialog
      :show.sync="isShowAddMemberDialog"
      :is-batch="isBatch"
      :loading="memberLoading"
      :name="curName"
      :id="curId"
      :is-rating-manager="isRatingManager"
      show-expired-at
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd"
      @on-after-leave="handleAddAfterClose"
    />
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { formatCodeData, getWindowHeight, xssFilter } from '@/common/util';
  import DeleteDialog from '@/components/iam-confirm-dialog/index.vue';
  import DeleteActionDialog from '@/views/group/components/delete-related-action-dialog.vue';
  import IamSearchSelect from '@/components/iam-search-select';
  import RenderPermSideslider from '../../perm/components/render-group-perm-sideslider';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  import AddMemberDialog from '@/views/group/components/iam-add-member.vue';

  export default {
    name: '',
    components: {
      IamSearchSelect,
      IamDeadline,
      DeleteDialog,
      DeleteActionDialog,
      RenderPermSideslider,
      IamEditMemberSelector,
      AddMemberDialog
    },
    props: {
      data: {
        type: Object,
        default: () => {
          return {};
        }
      },
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
        curGroupName: '',
        curGroupId: '',
        gradeSliderTitle: '',
        sliderLoading: false,
        tableLoading: false,
        isShowPermSidesilder: false,
        pageLoading: false,
        isShowUserGroupDialog: false,
        isLoading: false,
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.userGroup['用户组名']`),
            default: true
          },
          {
            id: 'description',
            name: this.$t(`m.common['描述']`),
            disabled: true
          }
        ],
        searchValue: [],
        tableList: [],
        gradeMembers: [],
        tableDialogLoading: false,
        expiredAt: 15552000,
        isShowExpiredError: false,
        expiredAtUse: 15552000,
        curRoleId: -1,
        currentSelectList: [],
        currentBackup: 1,
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        searchParams: {},
        groupPermEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        emptyDialogData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        isShowGroupError: false,
        isShowDeleteDialog: false,
        delActionDialogTitle: '',
        delActionDialogTip: '',
        currentActionName: '',
        delActionList: [],
        currentSelectGroupList: [],
        isShowAddMemberDialog: false,
        isBatch: false,
        memberLoading: false,
        curName: '',
        curId: 0,
        groupAttributes: {
          source_type: '',
          source_from_role: false
        },
        tableHeight: getWindowHeight() - 290
      };
    },
    computed: {
      ...mapGetters(['user']),
      curSelectIds () {
        return this.currentSelectList.map(item => item.id);
      },
      curSelectMemberIds () {
        return this.currentSelectGroupList.map(item => item.id);
      },
      isAdminGroup () {
        return (payload) => {
          if (payload) {
            const { attributes, role_members } = payload;
            if (attributes && attributes.source_from_role && role_members.length === 1) {
              return true;
            }
            return false;
          }
        };
      },
      curRole () {
        return this.user.role.type;
      },
      isRatingManager () {
        return ['rating_manager', 'subset_manager'].includes(this.curRole);
      },
      isBatchDisabled () {
        if (this.currentSelectGroupList.length) {
          const isDisabled = this.currentSelectGroupList.every(item => item.readonly);
          return isDisabled;
        } else {
          return true;
        }
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      },
      personalGroupList: {
        handler (v) {
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
          const list = value.filter(
            (item) =>
              !this.currentSelectGroupList
                .map((v) => v.id.toString())
                .includes(item.id.toString())
          );
          this.currentSelectGroupList = [...this.currentSelectGroupList, ...list];
        },
        immediate: true
      }
    },
    async created () {
      window.addEventListener('resize', () => {
        this.tableHeight = getWindowHeight() - 290;
      });
      if (!this.isSearchPerm) {
        await this.fetchPermGroups(false, true);
      }
    },
    methods: {
      setDefaultSelect () {
        return this.curPageData.length > 0;
      },

      /**
       * handleAnimationEnd
       */
      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSidesilder = false;
      },

      async fetchPermGroups (isTableLoading = false, isPageLoading = false) {
        try {
          this.tableLoading = isTableLoading;
          this.pageLoading = isPageLoading;
          let url = '';
          let params = {};
          const { current, limit } = this.pageConf;
          if (this.isSearchPerm) {
            url = 'perm/getPermGroupsSearch';
            params = {
              ...this.curSearchParams,
              limit,
              offset: limit * (current - 1)
            };
          } else {
            url = 'perm/getPermGroups';
            params = {
              limit: this.pageConf.limit,
              offset: this.pageConf.current
            };
          }
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { id, type, username } = this.data;
          const { code, data } = await this.$store.dispatch(url, {
            ...params,
            ...{
              subjectType: type === 'user' ? type : 'department',
              subjectId: type === 'user' ? username : id
            }
          });
          const currentSelectGroupList = this.currentSelectGroupList.map((item) =>
            item.id.toString()
          );
          this.pageConf.count = data.count || 0;
          this.dataList = data.results || [];
          this.curPageData = [...this.dataList];
          this.$nextTick(() => {
            this.curPageData.forEach((item) => {
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
                this.$refs.groupPermTableRef
                  && this.$refs.groupPermTableRef.toggleRowSelection(item, true);
              }
            });
            if (this.currentSelectGroupList.length < 1) {
              this.$refs.groupPermTableRef && this.$refs.groupPermTableRef.clearSelection();
            }
          });
          this.groupPermEmptyData = formatCodeData(code, this.emptyData, data.results.length === 0);
        } catch (e) {
          this.$emit('toggle-loading', false);
          console.error(e);
          this.currentSelectGroupList = [];
          this.pageConf.count = 0;
          this.groupPermEmptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
          this.pageLoading = false;
          if (this.isSearchPerm) {
            bus.$emit('on-perm-tab-count', { active: 'GroupPerm', count: this.pageConf.count });
          }
        }
      },

      /**
       * initPageConf
       */
      initPageConf () {
        this.pageConf.current = 1;
        const total = this.dataList.length;
        this.pageConf.count = total;
      },

      /**
       * handlePageChange
       */
      handlePageChange (page = 1) {
        this.pageConf.current = page;
        this.fetchPermGroups(true, false);
      },
      /**
       * handlePageLimitChange
       */
      handlePageLimitChange (currentLimit, prevLimit) {
        this.pageConf.limit = currentLimit;
        this.pageConf.current = 1;
        this.handlePageChange(this.pageConf.current);
      },

      /**
       * goDetail
       */
      goDetail (row) {
        this.curGroupName = row.name;
        this.curGroupId = row.id;
        this.isShowPermSidesilder = true;
      },

      /**
       * showQuitTemplates
       */
      showQuitTemplates (row) {
        this.deleteDialogConf.visiable = true;
        this.deleteDialogConf.row = Object.assign({}, row);
        this.deleteDialogConf.msg = `${this.$t(`m.common['退出']`)}${this.$t(`m.common['【']`)}${row.name}${this.$t(`m.common['】']`)}${this.$t(`m.common['，']`)}${this.$t(`m.info['将不再继承该组的权限']`)}${this.$t(`m.common['。']`)}`;
      },

      /**
       * confirmDelete
       */
      async confirmDelete () {
        this.deleteDialogConf.loading = true;
        const { type } = this.data;
        try {
          await this.$store.dispatch('perm/quitGroupTemplates', {
            subjectType: type === 'user' ? type : 'department',
            subjectId: type === 'user' ? this.data.username : this.data.id,
            type: 'group',
            id: this.deleteDialogConf.row.id
          });
          this.cancelDelete();
          this.messageSuccess(this.$t(`m.info['退出成功']`), 3000);
          await this.fetchPermGroups(true);
        } catch (e) {
          this.deleteDialogConf.loading = false;
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      /**
       * cancelDelete
       */
      cancelDelete () {
        this.deleteDialogConf.visiable = false;
      },

      /**
       * afterLeaveDelete
       */
      afterLeaveDelete () {
        this.deleteDialogConf.row = Object.assign({}, {});
        this.deleteDialogConf.msg = '';
        this.deleteDialogConf.loading = false;
      },

      async handleBatchAddUserGroup () {
        this.isShowUserGroupDialog = true;
        this.searchValue = [];
        this.searchParams = {};
        await this.fetchUserGroupList();
      },

      handleAfterEditLeave () {
                
      },

      handleSearch (payload, result) {
        this.currentSelectList = [];
        this.searchParams = payload;
        this.emptyDialogData.tipType = 'search';
        this.resetDialogPagination();
        this.fetchUserGroupList(true);
      },

      async handleEmptyDialogClear () {
        this.searchParams = {};
        this.searchValue = [];
        this.emptyDialogData.tipType = '';
        this.resetDialogPagination();
        await this.fetchUserGroupList();
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
            this.$nextTick(() => {
              const selectionCount = document.getElementsByClassName('bk-page-selection-count');
              if (this.$refs.groupPermTableRef
                && selectionCount
                && selectionCount.length
                && selectionCount[0].children
              ) {
                selectionCount[0].children[0].innerHTML = xssFilter(this.currentSelectGroupList.length);
              }
            });
          },
          all: () => {
            const tableList = _.cloneDeep(this.curPageData);
            const selectGroups = this.currentSelectGroupList.filter(item =>
              !tableList.map(v => v.id.toString()).includes(item.id.toString()));
            this.currentSelectGroupList = [...selectGroups, ...payload];
            this.$nextTick(() => {
              const selectionCount = document.getElementsByClassName('bk-page-selection-count');
              if (this.$refs.groupPermTableRef && selectionCount) {
                selectionCount[0].children[0].innerHTML = xssFilter(this.currentSelectGroupList.length);
              }
            });
          }
        };
        return typeMap[type]();
      },

      handleAllGroupChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handleGroupChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },

      handleBatchQuit () {
        this.handleDeleteActions('quit');
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

      handleBatchAddMember () {
        const hasDisabledData = this.currentSelectGroupList.filter(item => item.readonly);
        if (hasDisabledData.length) {
          const disabledNames = hasDisabledData.map(item => item.name);
          this.messageWarn(this.$t(`m.info['用户组为只读用户组不能添加成员']`, { value: `${this.$t(`m.common['【']`)}${disabledNames}${this.$t(`m.common['】']`)}` }), 3000);
          return;
        }
        this.isBatch = true;
        this.isShowAddMemberDialog = true;
      },

      handleAddAfterClose () {
        this.curName = '';
        this.curId = 0;
      },

      handleCancelAdd () {
        this.curId = 0;
        this.curName = '';
        this.isShowAddMemberDialog = false;
      },

      handleAddMember (payload) {
        const { id, name, attributes } = payload;
        this.curName = name;
        this.curId = id;
        this.groupAttributes = Object.assign(this.groupAttributes, attributes);
        this.isBatch = false;
        this.isShowAddMemberDialog = true;
      },

      async handleSubmitAdd (payload) {
        const { users, departments, expiredAt } = payload;
        // 判断批量选择的用户组里是否包含管理员组
        const hasAdminGroups = this.currentSelectGroupList.filter(item =>
          item.attributes && item.attributes.source_from_role && departments.length > 0);
        if (hasAdminGroups.length) {
          const adminGroupNames = hasAdminGroups.map(item => item.name).join();
          this.messageWarn(this.$t(`m.info['用户组为管理员组，不能添加部门']`, { value: `${this.$t(`m.common['【']`)}${adminGroupNames}${this.$t(`m.common['】']`)}` }), 3000);
          return;
        }
        let expired = payload.policy_expired_at;
        // 4102444800：非永久时需加上当前时间
        if (expiredAt !== 4102444800) {
          const nowTimestamp = +new Date() / 1000;
          const tempArr = String(nowTimestamp).split('');
          const dotIndex = tempArr.findIndex((item) => item === '.');
          const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
          expired = expired + nowSecond;
        }
        const arr = [];
        if (departments.length > 0) {
          arr.push(
            ...departments.map((item) => {
              return {
                id: item.id,
                type: 'department'
              };
            })
          );
        }
        if (users.length > 0) {
          arr.push(
            ...users.map((item) => {
              return {
                id: item.username,
                type: 'user'
              };
            })
          );
        }
        const params = {
          members: arr,
          expired_at: expired,
          id: this.curId
        };
        let fetchUrl = 'userGroup/addUserGroupMember';
        if (this.isBatch) {
          params.group_ids = this.curSelectMemberIds;
          delete params.id;
          fetchUrl = 'userGroup/batchAddUserGroupMember';
        }
        console.log('params', params);
        try {
          this.memberLoading = true;
          await this.$store.dispatch(fetchUrl, params);
          this.isShowAddMemberDialog = false;
          this.currentSelectGroupList = [];
          this.pageConf = Object.assign(this.pageConf, { current: 1, limit: 10 });
          this.messageSuccess(this.$t(`m.info['添加成员成功']`), 3000);
          this.fetchPermGroups(true);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.memberLoading = false;
        }
      },

      async handleSubmitDelete () {
        const selectGroups = this.currentSelectGroupList.filter(item =>
          !this.delActionList.map(v => v.id.toString()).includes(item.id.toString()));
        if (!selectGroups.length) {
          this.messageWarn(this.$t(`m.perm['当前勾选项都为不可退出的用户组（唯一管理员不能退出）']`), 3000);
          return;
        }
        const { id, username, type } = this.data;
        try {
          for (let i = 0; i < selectGroups.length; i++) {
            await this.$store.dispatch('perm/quitGroupTemplates', {
              subjectType: type === 'user' ? type : 'department',
              subjectId: type === 'user' ? username : id,
              type: 'group',
              id: selectGroups[i].id
            });
          }
          this.isShowDeleteDialog = false;
          this.currentSelectGroupList = [];
          this.messageSuccess(this.$t(`m.info['退出成功']`), 3000);
          this.resetPagination();
          await this.fetchPermGroups(true);
        } catch (e) {
          this.deleteDialogConf.loading = false;
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      async handleEmptyDialogRefresh () {
        this.resetDialogPagination();
        await this.fetchUserGroupList(true);
      },

      async handleEmptyRefresh () {
        this.resetPagination();
        await this.fetchPermGroups(false, true);
      },

      handleEmptyClear () {
        this.searchParams = {};
        this.searchValue = [];
        this.groupPermEmptyData.tipType = '';
        this.resetPagination();
        this.$emit('on-clear');
      },

      resetPagination (limit = 10) {
        this.pageConf = Object.assign(this.pageConf, { current: 1, limit });
      },

      resetDialogPagination () {
        this.pagination = Object.assign({}, {
          current: 1,
          limit: 10,
          count: 0,
          showTotalCount: true
        });
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.currentSelectList = [];
        this.fetchUserGroupList();
      },

      limitChange (currentLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.fetchUserGroupList();
      },

      handleDeadlineChange (payload) {
        if (payload) {
          this.isShowExpiredError = false;
        }
        if (payload !== PERMANENT_TIMESTAMP && payload) {
          const nowTimestamp = +new Date() / 1000;
          const tempArr = String(nowTimestamp).split('');
          const dotIndex = tempArr.findIndex(item => item === '.');
          const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
          this.expiredAtUse = payload + nowSecond;
          return;
        }
        this.expiredAtUse = payload;
      },

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      },

      // 获取列表数据
      async fetchUserGroupList () {
        this.tableDialogLoading = true;
        const params = {
          ...this.searchParams,
          limit: this.pagination.limit,
          offset: this.pagination.limit * (this.pagination.current - 1)
        };
        try {
          const { code, data } = await this.$store.dispatch('userGroup/getUserGroupList', params);
          this.pagination.count = data.count || 0;
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.emptyDialogData = formatCodeData(code, this.emptyDialogData, this.tableList.length === 0);
        } catch (e) {
          console.error(e);
          this.emptyDialogData = formatCodeData(e.code, this.emptyDialogData);
          this.messageAdvancedError(e);
        } finally {
          this.tableDialogLoading = false;
        }
      },
      // 选择checkbox
      handlerChange (selection, row) {
        this.currentSelectList = selection;
        this.isShowGroupError = false;
      },

      handlerAllChange (selection) {
        this.currentSelectList = [...selection];
        this.isShowGroupError = false;
      },

      handleExpiredAt () {
        const nowTimestamp = +new Date() / 1000;
        const tempArr = String(nowTimestamp).split('');
        const dotIndex = tempArr.findIndex(item => item === '.');
        const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
        const expiredAt = this.expiredAtUse + nowSecond;
        return expiredAt;
      },

      // 提交
      async handleBatchUserGroupSubmit () {
        if (this.expiredAtUse === 15552000) {
          this.expiredAtUse = this.handleExpiredAt();
        }
        const { type, username, id } = this.data;
        const members = [];
        if (type === 'user') {
          members.push({
            id: username,
            type
          });
        }
        if (type === 'depart') {
          members.push({
            id,
            type: 'department'
          });
        }
        const params = {
          members,
          group_ids: this.curSelectIds,
          expired_at: this.expiredAtUse
        };
        try {
          await this.$store.dispatch('userGroup/batchAddUserGroupMember', params);
          this.isShowUserGroupDialog = false;
          this.messageSuccess(this.$t(`m.info['添加用户组成功']`), 3000);
          await this.fetchPermGroups(true);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.loading = false;
        }
      },

      handleBatchUserGroupCancel () {
        this.isShowUserGroupDialog = false;
      }
    }
  };
</script>

<style lang="postcss">
  .iam-joined-user-group-wrapper {
      height: calc(100vh - 204px);
      .bk-table {
        border-right: none;
        border-bottom: none;
        &.is-be-loading {
            border-bottom: 1px solid #dfe0e5;
        }
        .user-group-name,
        .can-view {
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
          .depart,
          .template {
            display: inline-block;
            min-width: 54px;
            padding: 4px 6px;
            background: #f0f1f5;
            border-radius: 2px;
            margin-right: 2px;
  
            i {
              font-size: 14px;
              color: #c4c6cc;
            }
          }
        }

        tr {
          &:hover {
            .member-wrapper {
              .user,
              .depart,
              .template {
                background: #ffffff;
              }
            }
          }
        }
      }
  }
</style>

<style lang="postcss" scoped>
  @import '@/css/mixins/manage-members-detail-slidesider.css';
  .search-wrapper {
    width: 500px;
  }
  .button-warp {
    margin-top: 30px;
    text-align: center;
  }
  .iam-joined-user-group-button {
    display: flex;
    align-items: center;
    .bk-button {
      &:not(&:first-child) {
        margin-left: 10px;
      }
    }
  }
</style>
