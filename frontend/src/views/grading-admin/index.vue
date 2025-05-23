<template>
  <div class="iam-grading-admin-wrapper">
    <render-search>
      <bk-button theme="primary" @click="handleCreate" data-test-id="grading_btn_create">
        {{ isStaff ? $t(`m.common['申请新建']`) : $t(`m.common['新建']`) }}
      </bk-button>
      <bk-link class="admin-link" theme="primary" @click="handleOpenDocu">
        <span class="linkText">{{ $t('m.common["什么是管理空间"]') }}</span>
      </bk-link>
      <div slot="right">
        <iam-search-select
          @on-change="handleSelectSearch"
          :data="searchData"
          :value="searchList"
          :placeholder="$t(`m.levelSpace['输入空间名称、管理员名称进行搜索']`)"
          style="width: 500px"
        />
      </div>
    </render-search>
    <bk-table
      ref="spaceTable"
      size="small"
      :ext-cls="isFilter ? 'grading-admin-table search-manage-table' : 'grading-admin-table'"
      :data="tableList"
      :max-height="tableHeight"
      :class="{ 'set-border': tableLoading }"
      :cell-class-name="getCellClass"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @expand-change="handleExpandChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column type="expand" width="30" fixed="left">
        <template slot-scope="{ row }">
          <bk-table
            size="small"
            ext-cls="children-expand-cls"
            :data="row.children"
            :row-key="row.id + '__' + row.name"
            :show-header="false"
            :border="false"
            :cell-class-name="getSubCellClass"
            :max-height="500"
            v-bkloading="{ isLoading: subLoading, opacity: 1 }"
          >
            <bk-table-column width="45" fixed="left" />
            <bk-table-column prop="name" :min-width="190" fixed="left">
              <template slot-scope="child">
                <div class="flex_space_name">
                  <Icon type="level-two-manage-space" :style="{ color: iconColor[1] }" />
                  <iam-edit-input
                    field="name"
                    style="width: 100%;margin-left: 5px;"
                    :placeholder="$t(`m.verify['请输入']`)"
                    :value="child.row.name"
                    :index="child.$index"
                    :remote-hander="handleUpdateSubManageSpace" />
                </div>
              </template>
            </bk-table-column>
            <bk-table-column prop="members" width="300">
              <template slot-scope="child">
                <template v-if="child.row.isEdit || child.row.members.length > 0">
                  <IamEditMemberSelector
                    field="members"
                    width="200"
                    :ref="`subManagerRef${child.$index}`"
                    :placeholder="$t(`m.verify['请输入']`)"
                    :allow-empty="true"
                    :is-edit-allow-empty="false"
                    :value="child.row.members"
                    :index="child.$index"
                    @on-change="handleUpdateSubMembers"
                    @on-empty-change="handleEmptyMemberChange(...arguments, child.row)"
                  />
                </template>
                <template v-else>
                  <IamManagerEditInput
                    field="members"
                    style="width: 100%;"
                    :is-show-other="true"
                    :placeholder="$t(`m.verify['请输入']`)"
                    :value="getMemberFilter(child.row.members)"
                    @handleShow="handleOpenSubManagerEdit(child.row, child.$index)"
                  />
                </template>
              </template>
            </bk-table-column>
            <bk-table-column prop="description" :min-width="200">
              <template slot-scope="child">
                <iam-edit-textarea
                  field="description"
                  width="300"
                  :placeholder="$t(`m.verify['请输入']`)"
                  :value="child.row.description"
                  :index="child.$index"
                  :remote-hander="handleUpdateSubManageSpace" />
              </template>
            </bk-table-column>
            <bk-table-column :label="$t(`m.levelSpace['更新人']`)" prop="updater" />
            <bk-table-column :label="$t(`m.levelSpace['更新时间']`)" prop="updated_time" width="160">
              <template slot-scope="child">
                <span :title="child.row.updated_time">{{ child.row.updated_time }}</span>
              </template>
            </bk-table-column>
            <bk-table-column :width="curLanguageIsCn ? 180 : 210" prop="child-operate">
              <template slot-scope="child">
                <div class="operate_btn">
                  <bk-button
                    theme="primary"
                    text
                    @click.stop="handleSubView(child.row, 'role')"
                  >
                    {{ $t(`m.levelSpace['进入空间']`) }}
                  </bk-button>
                  <bk-button
                    theme="primary"
                    text
                    @click.stop="handleSubView(child.row, 'auth')"
                  >
                    {{ $t(`m.nav['授权边界']`) }}
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
      <bk-table-column :label="$t(`m.levelSpace['名称']`)" prop="name" :min-width="200" fixed="left">
        <template slot-scope="{ row, $index }">
          <div class="flex_space_name">
            <template v-if="isFilter && ['subset_manager'].includes(row.type)">
              <Icon type="level-two-manage-space" :style="{ color: iconColor[1] }" />
              <iam-edit-input
                field="name"
                style="width: 100%;margin-left: 5px;"
                :placeholder="$t(`m.verify['请输入']`)"
                :value="row.name"
                :index="$index"
                :remote-hander="handleUpdateManageSpace" />
            </template>
            <template v-else>
              <Icon
                type="level-one-manage-space"
                :style="{ 'color': iconColor[0] }" />
              <span
                class="grading-admin-name single-hide"
                :title="row.name"
                @click="handleView(row, 'detail')">
                {{ row.name }}
              </span>
            </template>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.levelSpace['管理员']`)" prop="members" width="300">
        <template slot-scope="{ row , $index }">
          <template v-if="row.isEdit || row.members.length > 0">
            <IamEditMemberSelector
              field="members"
              width="200"
              :ref="`managerRef${$index}`"
              :placeholder="$t(`m.verify['请输入']`)"
              :allow-empty="true"
              :is-edit-allow-empty="false"
              :value="row.members"
              :index="$index"
              @on-change="handleUpdateMembers"
              @on-empty-change="handleEmptyMemberChange(...arguments, row)"
            />
          </template>
          <template v-else>
            <IamManagerEditInput
              field="members"
              style="width: 100%;"
              :is-show-other="true"
              :placeholder="$t(`m.verify['请输入']`)"
              :value="getMemberFilter(row.members)"
              @handleShow="handleOpenManagerEdit(row, $index)"
            />
          </template>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['描述']`)" :min-width="200">
        <template slot-scope="{ row, $index }">
          <iam-edit-textarea
            field="description"
            width="300"
            :placeholder="$t(`m.verify['请输入']`)"
            :value="row.description"
            :index="$index"
            :remote-hander="handleUpdateManageSpace" />
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.grading['更新人']`)" prop="updater" />
      <bk-table-column :label="$t(`m.grading['更新时间']`)" prop="updated_time" width="160">
        <template slot-scope="{ row }">
          <span :title="row.updated_time">{{ row.updated_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column
        :label="$t(`m.common['操作-table']`)"
        :width="curLanguageIsCn ? 180 : 210"
        :fixed="tableList.length > 0 ? 'right' : false"
      >
        <template slot-scope="{ row }">
          <div class="operate_btn">
            <bk-button
              theme="primary"
              text
              @click="handleView(row, 'role')"
            >
              {{ $t(`m.levelSpace['进入空间']`) }}
            </bk-button>
            <bk-button
              theme="primary"
              text
              @click.stop="handleView(row, 'auth')"
            >
              {{ $t(`m.nav['授权边界']`) }}
            </bk-button>
            <bk-popover
              class="custom-table-dot-menu"
              ext-cls="custom-table-dot-menu-tipper"
              placement="bottom-start"
              theme="dot-menu light"
              trigger="click"
              :arrow="false"
              :offset="15"
              :distance="0"
            >
              <span class="custom-table-dot-menu-trigger" />
              <ul class="custom-table-dot-menu-list" slot="content">
                <li class="custom-table-dot-menu-item">
                  <bk-button
                    v-if="!['subset_manager'].includes(row.type)"
                    theme="primary"
                    text
                    @click.stop="handleCopy(row)"
                  >
                    {{ $t(`m.levelSpace['克隆']`) }}
                  </bk-button>
                </li>
              </ul>
            </bk-popover>
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

    <confirm-dialog
      :show.sync="isShowConfirmDialog"
      :loading="confirmLoading"
      :title="confirmDialogTitle"
      :sub-title="confirmDialogSubTitle"
      @on-after-leave="handleAfterLeave"
      @on-cancel="handleCancel"
      @on-sumbit="handleSubmit" />

    <apply-dialog
      :show.sync="isShowApplyDialog"
      :loading="applyLoading"
      :name="curName"
      @on-after-leave="handleAfterApplyLeave"
      @on-cancel="handleApplyCancel"
      @on-sumbit="handleApplySumbit" />

    <ManageInterviewDialog
      :show.sync="showImageDialog"
      :show-footer="false"
    />
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import { getWindowHeight, formatCodeData, navDocCenterPath } from '@/common/util';
  import ConfirmDialog from '@/components/iam-confirm-dialog/index';
  import ApplyDialog from './components/apply-join-dialog';
  import IamEditInput from '@/views/my-manage-space/components/iam-edit/input';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  import IamEditTextarea from '@/views/my-manage-space/components/iam-edit/textarea';
  import IamManagerEditInput from '@/components/iam-edit/input';
  import IamSearchSelect from '@/components/iam-search-select';
  import ManageInterviewDialog from '@/components/manage-interview-dialog';

  export default {
    name: '',
    components: {
      ConfirmDialog,
      ApplyDialog,
      IamEditInput,
      IamManagerEditInput,
      IamEditMemberSelector,
      IamEditTextarea,
      IamSearchSelect,
      ManageInterviewDialog
    },
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
        subPagination: {
          current: 1,
          count: 1,
          limit: 10
        },
        formData: {
          name: '',
          description: '',
          members: []
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
        subLoading: false,
        gradingAdminId: 0,
        iconColor: ['#FF9C01', '#9B80FE'],
        expandRowList: [], // 所有展开折叠项
        subTableList: [],
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        searchDefaultData: [
          {
            id: 'name',
            name: this.$t(`m.levelSpace['空间名称']`),
            default: true
          },
          {
            id: 'member',
            name: this.$t(`m.common['管理员']`),
            default: true
          }
        ],
        searchData: [],
        searchList: [],
        language: window.CUR_LANGUAGE,
        tableHeight: getWindowHeight() - 185
      };
    },
    computed: {
      ...mapGetters(['user', 'versionLogs']),
      isStaff () {
        return this.user.role.type === 'staff';
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
        if (newVal === '' && oldVal !== '' && this.isFilter) {
          this.isFilter = false;
          this.resetPagination();
          this.fetchGradingAdmin(true);
        }
      },
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    created () {
      window.addEventListener('resize', () => {
        this.tableHeight = getWindowHeight() - 185;
      });
      this.searchData = _.cloneDeep(this.searchDefaultData);
      const currentQueryCache = this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        if (currentQueryCache.limit) {
          this.pagination.limit = currentQueryCache.limit;
          this.pagination.current = currentQueryCache.current;
        }
        if (currentQueryCache.name) {
          this.searchValue = currentQueryCache.name;
        }
        if (this.searchValue) {
          this.isFilter = true;
        }
      }
    },
    methods: {
      getCellClass ({ row, column, rowIndex, columnIndex }) {
        // if (!row.is_member) {
        //     return 'iam-tag-table-cell-cls iam-tag-table-cell-opacity-cls';
        // }
        if (!row.has_subset_manager && !['right'].includes(column.fixed)) {
          return 'iam-tag-table-cell-cls iam-tag-table-cell-subset-cls';
        }
        if ((columnIndex === 1 || column.type === 'default') && !['right'].includes(column.fixed)) {
          return 'iam-table-cell-1-cls';
        }
        if (columnIndex === 2) {
          return 'iam-tag-table-cell-cls';
        }
        return '';
      },

      getSubCellClass ({ row, column, rowIndex, columnIndex }) {
        return !['child-operate'].includes(column.property) ? 'iam-table-cell-1-cls' : '';
      },

      getMemberFilter (value) {
        if (value.length) {
          return _.isArray(value) ? value.map(item => item.username).join(';') : value;
        }
        return '--';
      },

      handleExpandChange (row, expandedRows) {
        // if (row.id !== this.gradingAdminId) return;
        this.gradingAdminId = row.id;
        expandedRows = expandedRows.filter(e => e.id === this.gradingAdminId);
        if (!expandedRows.length) return;
        console.log('expandedRows', row, expandedRows);
        row.children = [];
        this.resetSubPagination();
        this.tableList.forEach(e => {
          if (e.id !== expandedRows[0].id) {
            this.$refs.spaceTable.toggleRowExpansion(e, false);
          } else {
            this.fetchSubManagerList(row);
          }
        });
      },

      async fetchPageData () {
        await this.fetchGradingAdmin();
      },

      handleCopy (payload) {
        this.$router.push({
          name: 'gradingAdminClone',
          params: {
            id: payload.id
          }
        });
      },

      refreshCurrentQuery () {
        const { limit, current } = this.pagination;
        const queryParams = {
          limit,
          current,
          role_name: this.user.role.name
        };
        if (this.searchValue !== '') {
          queryParams.name = this.searchValue;
        }
        window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        return queryParams;
      },

      setCurrentQueryCache (payload) {
        window.localStorage.setItem('gradeManagerList', JSON.stringify(payload));
      },

      getCurrentQueryCache () {
        return JSON.parse(window.localStorage.getItem('gradeManagerList'));
      },

      handleOpenManagerEdit (payload, index) {
        this.$set(this.tableList[index], 'isEdit', true);
        this.$nextTick(() => {
          const managerRef = this.$refs[`managerRef${index}`];
          if (managerRef) {
            managerRef.isEditable = true;
            if (!payload.members.length) {
              setTimeout(() => {
                this.$refs[`managerRef${index}`].$refs.selector.focus();
              }, 10);
            }
          }
        });
      },

      handleOpenSubManagerEdit (payload, index) {
        this.$set(payload, 'isEdit', true);
        this.$nextTick(() => {
          const subManagerRef = this.$refs[`subManagerRef${index}`];
          if (subManagerRef) {
            subManagerRef.isEditable = true;
            if (!payload.members.length) {
              setTimeout(() => {
                subManagerRef.$refs.selector.focus();
              }, 10);
            }
          }
        });
      },

      handleEmptyMemberChange (index, row) {
        row.isEdit = false;
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
          this.pagination.count = data.count || 0;
          data.results = data.results.map((item) => {
            item = Object.assign(item, {
              isEdit: false,
              children: []
            });
            return item;
          });
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          if (this.isStaff) {
            this.$store.commit('setGuideShowByField', { field: 'role', flag: this.tableList.length > 0 });
          }
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
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
          this.subTableList = [...row.children];
          this.emptyData = formatCodeData(code, this.emptyData, this.subTableList.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          row.children = [];
          this.subTableList = [];
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.curData = row;
          this.subLoading = false;
        }
      },

      async fetchSearchManageList (isTableLoading = false) {
        this.tableLoading = isTableLoading;
        const { current, limit } = this.pagination;
        const params = {
          page_size: limit,
          page: current,
          name: this.searchValue || '',
          member: this.searchMember || ''
        };
        if (this.externalSystemId) {
          params.hidden = false;
        }
        try {
          const { code, data } = await this.$store.dispatch('spaceManage/getSearchManagerList', params);
          this.pagination.count = data.count || 0;
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.emptyData = formatCodeData(
            code,
            this.emptyData,
            this.tableList.length === 0
          );
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.tableList = [];
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },
            
      async fetchManageTable (payload, url, type) {
        const { name, description, members } = payload;
        const params = {
          name: name || this.formData.name,
          description: description || this.formData.description,
          members: members || this.formData.members,
          id: this.formData.id
        };
        try {
          await this.$store.dispatch(url, params);
          this.messageSuccess(this.$t(`m.info['编辑成功']`), 3000);
          if (name || members) {
            const typeMap = {
              'rating_manager': async () => {
                this.resetPagination();
                this.isFilter ? await this.fetchSearchManageList()
                : await this.fetchGradingAdmin(this.formData);
              },
              'subset_manager': async () => {
                this.curData.children = [];
                this.resetSubPagination();
                this.isFilter ? await this.fetchSearchManageList()
                : await this.fetchSubManagerList(this.curData);
              }
            };
            typeMap[type]();
          }
          this.formData = Object.assign(this.formData, {
            name: params.name,
            description: params.description,
            members: [...params.members]
          });
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },
            
      handleUpdateMembers (payload, index) {
        this.handleUpdateManageSpace(payload, index);
      },

      handleUpdateSubMembers (payload, index) {
        this.handleUpdateSubManageSpace(payload, index);
      },
     
      // 一二级存在平铺展示数据
      async handleUpdateManageSpace (payload, index) {
        this.formData = this.tableList.find((e, i) => i === index);
        if (this.isFilter) {
          const typeMap = {
            rating_manager: async () => {
              await this.fetchManageTable(payload, 'role/updateRatingManager', 'rating_manager');
            },
            subset_manager: async () => {
              await this.fetchManageTable(payload, 'spaceManage/updateSecondManager', 'subset_manager');
            }
          };
          return typeMap[this.formData.type] ? typeMap[this.formData.type]() : '';
        } else {
          await this.fetchManageTable(payload, 'role/updateRatingManager', 'rating_manager');
        }
      },

      async handleUpdateSubManageSpace (payload, index) {
        this.formData = this.subTableList.find((e, i) => i === index);
        await this.fetchManageTable(payload, 'spaceManage/updateSecondManager', 'subset_manager');
      },

      async handleLoadMore (payload) {
        if (payload !== this.subPagination.count) {
          const params = {
            current: ++this.subPagination.current,
            limit: 10
          };
          this.subPagination = Object.assign(this.subPagination, params);
          this.fetchSubManagerList(this.curData);
        }
      },

      handleCreate () {
        this.$router.push({
          name: 'gradingAdminCreate'
        });
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
      },

      // handleSearch () {
      //     if (!this.searchValue) {
      //         return;
      //     }
      //     this.isFilter = true;
      //     this.emptyData.tipType = 'search';
      //     this.resetPagination();
      //     this.resetSubPagination();
      //     this.fetchGradingAdmin(true);
      // },

      async handleSelectSearch (payload, result) {
        const {
          name,
          member
        } = payload;
        if (!Object.keys(payload).length) {
          this.resetSearchData();
          return;
        }
        this.isFilter = true;
        this.emptyData.tipType = 'search';
        this.searchMember = member || '';
        this.searchValue = name;
        this.resetPagination();
        this.resetSubPagination();
        await this.fetchSearchManageList();
      },
            
      handleEmptyRefresh () {
        this.resetPagination();
        this.resetSubPagination();
        this.fetchGradingAdmin(true);
      },

      handleEmptyClear () {
        this.resetSearchData();
      },

      resetSearchData () {
        this.isFilter = false;
        this.searchValue = '';
        this.emptyData.tipType = '';
        this.searchList = [];
        this.searchData = _.cloneDeep(this.searchDefaultData);
        this.resetPagination();
        this.resetSubPagination();
        this.fetchGradingAdmin(true);
      },

      handleAfterApplyLeave () {
        this.curName = '';
      },

      handleApplyCancel () {
        this.isShowApplyDialog = false;
      },

      handleApplySumbit () {},

      handleDropOut (payload) {
        this.curOperateType = 'drop';
        this.curId = payload.id;
        this.confirmDialogTitle = this.$t(`m.dialog['确认退出']`);
        this.confirmDialogSubTitle = `${this.$t(`m.common['退出']`)}${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}, ${this.$t(`m.grading['退出提示']`)}`;
        this.isShowConfirmDialog = true;
      },

      handleDelete (payload) {
        this.curOperateType = 'delete';
        this.curId = payload.id;
        this.confirmDialogTitle = this.$t(`m.dialog['确认删除']`);
        this.confirmDialogSubTitle = `${this.$t(`m.common['删除']`)}${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}, ${this.$t(`m.grading['删除提示']`)}`;
        this.isShowConfirmDialog = true;
      },

      handleApplyJoin (payload) {
        this.curName = payload.name;
        this.isShowApplyDialog = true;
      },

      async handleSubmit () {
        this.confirmLoading = true;
        try {
          await this.$store.dispatch('role/deleteRatingManager', { id: this.curId });
          await this.$store.dispatch('roleList');
          this.messageSuccess(this.$t(`m.info['退出成功']`), 3000);
          this.isShowConfirmDialog = false;
          this.resetPagination();
          this.fetchGradingAdmin(true);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.confirmLoading = false;
        }
      },

      handleAfterLeave () {
        this.confirmDialogTitle = '';
        this.confirmDialogSubTitle = '';
        this.curOperateType = '';
        this.curId = -1;
      },

      handleCancel () {
        this.isShowConfirmDialog = false;
      },

      async handleView ({ id, name }, type) {
        window.localStorage.setItem('iam-header-name-cache', name);
        let routerName = 'gradingAdminDetail';
        const navRoute = {
          detail: () => {
            this.$router.push({
              name: routerName,
              params: {
                id
              }
            });
          },
          role: () => {
            routerName = 'userGroup';
          },
          auth: () => {
            routerName = 'authorBoundary';
          }
        };
        navRoute[type]();
        if (!['detail'].includes(type)) {
          await this.$store.dispatch('role/updateCurrentRole', { id });
          await this.$store.dispatch('userInfo');
          const { role } = this.user;
          if (role) {
            this.$store.commit('updateCurRoleId', id);
            this.$store.commit('updateIdentity', { id, type: role.type, name });
            this.$store.commit('updateNavId', id);
            this.$store.commit('updateIndex', 1);
            window.localStorage.setItem('index', 1);
            this.$router.push({
              name: routerName,
              params: {
                id,
                entry: 'super_manager'
              }
            });
          }
        }
      },

      // 二级管理空间
      async handleSubView ({ id, name }, mode) {
        window.localStorage.setItem('iam-header-name-cache', name);
        let routerName = 'userGroup';
        const routerNav = {
          role: () => {
            routerName = 'userGroup';
            this.$store.commit('updateIndex', 1);
            window.localStorage.setItem('index', 1);
          },
          auth: () => {
            routerName = 'authorBoundary';
            this.$store.commit('updateIndex', 1);
            window.localStorage.setItem('index', 1);
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
            entry: 'super_manager'
          }
        });
      },

      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.handleFilterData();
      },

      handleLimitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.handleFilterData();
      },

      handleFilterData () {
        this.isFilter ? this.fetchSearchManageList(true) : this.fetchGradingAdmin(true);
      },

      handleOpenDocu () {
        navDocCenterPath(this.versionLogs, `/UserGuide/Feature/ManagerCreate.md`, true);
      }
    }
  };
</script>

<style lang="postcss">
@import '@/css/mixins/custom-table-dot.css';
</style>

<style lang="postcss" scoped>
.iam-grading-admin-wrapper {
  .detail-link {
    color: #3a84ff;
    cursor: pointer;
    &:hover {
      color: #699df4;
    }
  }
  .grading-admin-table {
    margin-top: 16px;
    border-right: none;
    border-bottom: none;
    &.set-border {
        border-right: 1px solid #dfe0e5;
        border-bottom: 1px solid #dfe0e5;
    }
    .grading-admin-name {
        color: #3a84ff;
        margin-left: 5px;
        cursor: pointer;
        &:hover {
            color: #699df4;
        }
    }
    .bk-table-pagination-wrapper {
        background: #fff;
    }
  }
  .admin-link {
    margin-left: 10px;
    .linkText {
      font-size: 12px
    }
  }
  .iam-tag-table-cell-cls {
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
  .operate_btn {
    .bk-button-text {
      &:nth-child(n + 2) {
          margin-left: 10px;
      }
    }
  }

  .flex_space_name {
    display: flex;
    align-items: center;
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

  /* /deep/ .iam-tag-table-cell-opacity-cls {
      opacity: 0.4;
      .cell {
          padding-left: 0;
          color:#575961;
      }
  } */

/deep/ .iam-table-cell-1-cls,
.iam-tag-table-cell-subset-cls  {
  .cell {
    padding-left: 2px;
  }
}

/deep/ .iam-tag-table-cell-subset-cls {
  .cell {
    padding-left: 2px;
    .bk-table-expand-icon  {
        display: none;
    }
  }
}
/deep/ .bk-table-header-wrapper {
    .cell {
      padding-left: 2px;
    }
}

/deep/ .search-manage-table {
    .bk-table-expand-icon  {
      display: none;
    }
    .bk-table .cell {
      padding-left: 2px;
    }
}
/deep/ .bk-table-fixed,
/deep/ .bk-table-fixed-right {
  border-bottom: 0;
}
/deep/ .children-expand-cls {
  .bk-table-fixed {
    .bk-table-fixed-body-wrapper {
      z-index: 900;
    }
  }
  .bk-table-fixed-right {
    .bk-table__fixed-body-wrapper{
      z-index: 900;
    }
  }
  .bk-table-body-wrapper {
    z-index: 800;
  }
}
</style>
