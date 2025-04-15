<template>
  <div class="iam-level-manage-space-wrapper">
    <render-search>
      <bk-button
        theme="primary"
        @click="handleCreate"
        data-test-id="level-manage_space_btn_create"
      >
        {{ $t(`m.common['申请新建']`) }}
      </bk-button>
      <bk-link class="admin-link" theme="primary" @click="handleOpenDocu">
        <span class="linkText">{{ $t('m.common["什么是管理空间"]') }}</span>
      </bk-link>
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
          <!-- <bk-input
                        v-model="searchValue"
                        :placeholder="$t(`m.levelSpace['请输入名称']`)"
                        clearable
                        style="width: 420px"
                        right-icon="bk-icon icon-search"
                        @enter="handleSearch" /> -->
          <iam-search-select
            @on-change="handleSelectSearch"
            :data="searchData"
            :value="searchList"
            :placeholder="
              $t(`m.levelSpace['输入空间名称、管理员名称进行搜索']`)
            "
            style="width: 500px"
            :quick-search-method="quickSearchMethod"
          />
        </div>
      </div>
    </render-search>

    <bk-table
      ref="spaceTable"
      size="small"
      :ext-cls="isFilter ? 'level-manage-table search-manage-table' : 'level-manage-table'"
      :data="tableList"
      :max-height="tableHeight"
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
            :show-header="false"
            :border="false"
            :cell-class-name="getSubCellClass"
            :max-height="500"
            v-bkloading="{ isLoading: subLoading, opacity: 1 }"
            @row-click="handleRowClick"
          >
            <bk-table-column width="45" fixed="left" />
            <bk-table-column prop="name" :min-width="190" fixed="left">
              <template slot-scope="child">
                <div class="flex_space_name">
                  <Icon type="level-two-manage-space" :style="{ color: iconColor[1] }" />
                  <iam-edit-input
                    field="name"
                    :placeholder="$t(`m.verify['请输入']`)"
                    :value="child.row.name"
                    style="width: 100%; margin-left: 5px"
                    :index="child.$index"
                    :remote-hander="handleUpdateSubManageSpace"
                  />
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
                  :remote-hander="handleUpdateSubManageSpace"
                />
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
                    @click.stop="handleSubView(child.row, child.$index, row, 'detail')"
                  >
                    {{ $t(`m.levelSpace['进入空间']`) }}
                  </bk-button>
                  <bk-button
                    theme="primary"
                    text
                    @click.stop="handleSubView(child.row, child.$index, row, 'auth')"
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
                          theme="primary"
                          text
                          :disabled="!!(child.row.members && child.row.members.length < 2)"
                          :title="!!(child.row.members && child.row.members.length < 2)
                            ? $t(`m.perm['唯一管理员不可退出']`) : ''"
                          @click.stop="handleSubView(child.row, child.$index, row, 'quit')"
                        >
                          {{ $t(`m.common['退出']`) }}
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
          <div style="text-align: center">
            <bk-button
              v-if="subPagination.count !== row.children.length"
              text
              theme="primary"
              size="small"
              style="margin: 10px auto"
              @click="handleLoadMore(row.children.length)"
            >
              {{ $t(`m.common['查看更多']`) }}
            </bk-button>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.levelSpace['名称']`)" prop="name" :min-width="200" fixed="left">
        <template slot-scope="{ row, $index }">
          <div class="flex_space_name">
            <Icon
              :type="isFilter && ['subset_manager'].includes(row.type) ?
                'level-two-manage-space' : 'level-one-manage-space'"
              :style="{ color: isFilter && ['subset_manager'].includes(row.type) ?
                iconColor[1] : iconColor[0] }" />
            <iam-edit-input
              field="name"
              mode="edit"
              :placeholder="$t(`m.verify['请输入']`)"
              :value="row.name"
              style="width: 100%; margin-left: 5px"
              :index="$index"
              :remote-hander="handleUpdateManageSpace"
            />
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
      <bk-table-column :label="$t(`m.common['描述']`)" prop="description" :min-width="200">
        <template slot-scope="{ row, $index }">
          <iam-edit-textarea
            field="description"
            width="300"
            mode="edit"
            :placeholder="$t(`m.verify['请输入']`)"
            :value="row.description"
            :index="$index"
            :remote-hander="handleUpdateManageSpace"
          />
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.levelSpace['更新人']`)" prop="updater" />
      <bk-table-column :label="$t(`m.levelSpace['更新时间']`)" prop="updated_time" width="160">
        <template slot-scope="{ row }">
          <span :title="row.updated_time">{{ row.updated_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column
        :label="$t(`m.common['操作-table']`)"
        :width="curLanguageIsCn ? 180 : 210"
        :fixed="tableList.length > 0 ? 'right' : false"
      >
        <template slot-scope="{ row, $index }">
          <div class="operate_btn">
            <bk-button
              theme="primary"
              text
              @click="handleView(row, $index, 'detail')"
            >
              {{ $t(`m.levelSpace['进入空间']`) }}
            </bk-button>
            <bk-button
              theme="primary"
              text
              @click.stop="handleView(row, $index,'auth')"
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
                    theme="primary"
                    text
                    :disabled="!!(row.members && row.members.length < 2)"
                    :title="!!(row.members && row.members.length < 2) ? $t(`m.perm['唯一管理员不可退出']`) : ''"
                    @click.stop="handleView(row, $index, 'quit')"
                  >
                    {{ $t(`m.common['退出']`) }}
                  </bk-button>
                </li>
                <li class="custom-table-dot-menu-item">
                  <bk-button
                    v-if="!['subset_manager'].includes(row.type)"
                    theme="primary"
                    text
                    @click.stop="handleView(row, $index, 'clone')"
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

    <ManageInterviewDialog
      :show.sync="showImageDialog"
      :show-footer="false"
    />
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { getWindowHeight, formatCodeData, navDocCenterPath } from '@/common/util';
  import IamEditInput from './components/iam-edit/input';
  import IamEditMemberSelector from './components/iam-edit/member-selector';
  import IamEditTextarea from './components/iam-edit/textarea';
  import IamSearchSelect from '@/components/iam-search-select';
  import IamManagerEditInput from '@/components/iam-edit/input';
  import { buildURLParams } from '@/common/url';
  import ManageInterviewDialog from '@/components/manage-interview-dialog';
  // import { bus } from '@/common/bus';
  // import { getRouterDiff, getNavRouterDiff } from '@/common/router-handle';

  export default {
    name: 'myManageSpace',
    components: {
      IamEditInput,
      IamEditMemberSelector,
      IamEditTextarea,
      IamSearchSelect,
      IamManagerEditInput,
      ManageInterviewDialog
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
        searchValues: [],
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
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        searchMember: '',
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
        showImageDialog: false
      };
    },
    computed: {
      ...mapGetters(['user', 'roleList', 'externalSystemId', 'versionLogs']),
      tableHeight () {
          return getWindowHeight() - 185;
      },
      disabledPerm () {
        return (payload, roleType) => {
          const { type, members } = payload;
          if (['subset_manager'].includes(type) || roleType) {
            return false;
          } else {
            const result = members.map((item) => item.username).includes(this.user.username);
            return !result;
          }
        };
    },
      isStaff () {
          return this.user.role.type === 'staff';
      }
    },
    watch: {
      searchValue (newVal, oldVal) {
        if (!newVal && oldVal && this.isFilter) {
          this.isFilter = false;
          this.resetPagination();
          this.fetchGradingAdmin(true);
        }
      },
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    methods: {
      async fetchPageData () {
        this.searchData = _.cloneDeep(this.searchDefaultData);
        await this.fetchGradingAdmin();
      },

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

      handleClear () {
        if (this.isFilter) {
          this.isFilter = false;
          this.resetPagination();
          this.fetchGradingAdmin(true);
        }
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
        await this.fetchManageTable(
          payload,
          'spaceManage/updateSecondManager',
          'subset_manager'
        );
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
          this.formData = Object.assign(this.formData, {
            name: params.name,
            description: params.description,
            members: [...params.members]
          });
          if (name || members) {
            this.fetchResetInstanceData(type);
          }
        } catch (e) {
          this.fetchResetInstanceData(type);
          console.error(e);
          const { code, response } = e;
          if ((response && response.status && [401, 404].includes(response.status))
            || [1902000].includes(code)) {
            this.messageSuccess(this.$t(`m.info['您已退出当前管理员授权范围']`), 3000);
          } else {
            this.messageAdvancedError(e);
          }
        }
      },

      async fetchResetInstanceData (payload) {
        const typeMap = {
          rating_manager: async () => {
            this.resetPagination();
            this.isFilter ? await this.fetchSearchManageList() : await this.fetchGradingAdmin();
          },
          subset_manager: async () => {
            this.curData.children = [];
            this.resetSubPagination();
            this.isFilter ? await this.fetchSearchManageList()
            : await this.fetchSubManagerList(this.curData);
          }
        };
        typeMap[payload]();
      },

      handleRowClick (row, column, cell, event, rowIndex, columnIndex) {
        const allNodeId = this.findParentNode(row.id, this.expandRowList);
        if (allNodeId.length) {
          const rowData = this.expandRowList.find((item) => item.id === allNodeId[0]);
          this.$refs.spaceTable.toggleRowExpansion(rowData, false);
        }
      },

      handleExpandChange (row, expandedRows) {
        // if (row.id !== this.gradingAdminId) return;
        this.gradingAdminId = row.id;
        expandedRows = expandedRows.filter((e) => e.id === this.gradingAdminId);
        if (!expandedRows.length) return;
        console.log('expandedRows', row, expandedRows);
        row.children = [];
        this.resetSubPagination();
        this.tableList.forEach((e) => {
          if (e.id !== expandedRows[0].id) {
            this.$refs.spaceTable.toggleRowExpansion(e, false);
          } else {
            this.fetchSubManagerList(row);
          }
        });
        this.$nextTick(() => {
          this.$refs.spaceTable && this.$refs.spaceTable.doLayout();
        });
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
          this.pagination.count = data.count;
          data.results = data.results.map((item) => {
            item = Object.assign(item, {
              isEdit: false,
              children: []
            });
            return item;
          });
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          if (this.isStaff) {
            this.$store.commit('setGuideShowByField', {
              field: 'role',
              flag: this.tableList.length > 0
            });
          }
          this.emptyData = formatCodeData(
            code,
            this.emptyData,
            this.tableList.length === 0
          );
        } catch (e) {
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
          const { code, data } = await this.$store.dispatch(
            'spaceManage/getStaffSubManagerList',
            {
              limit: this.subPagination.limit,
              offset: (this.subPagination.current - 1) * this.subPagination.limit,
              id: row.id
            }
          );
          this.subPagination.count = data.count || 0;
          // this.subTableList.splice(0, this.subTableList.length, ...(data.results || []));
          row.children = [...row.children, ...data.results];
          this.subTableList = [...row.children];
          this.emptyData = formatCodeData(
            code,
            this.emptyData,
            this.subTableList.length === 0
          );
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
          // if (this.isStaff) {
          //     this.$store.commit('setGuideShowByField', {
          //         field: 'role',
          //         flag: this.tableList.length > 0
          //     });
          // }
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

      // 管理空间
      async handleView ({ id, name }, index, mode) {
        window.localStorage.setItem('iam-header-name-cache', name);
        let routerName = 'userGroup';
        const routerNav = {
          detail: () => {
            routerName = 'userGroup';
            this.$store.commit('updateIndex', 1);
            window.localStorage.setItem('index', 1);
          },
          auth: () => {
            routerName = 'authorBoundary';
            this.$store.commit('updateIndex', 1);
            window.localStorage.setItem('index', 1);
          },
          clone: () => {
            routerName = 'myManageSpaceClone';
            this.$store.commit('updateIndex', 0);
            window.localStorage.setItem('index', 0);
          },
          quit: () => {
            this.$store.commit('updateIndex', 0);
            window.localStorage.setItem('index', 0);
          }
        };
        routerNav[mode]();
        if (!['clone', 'quit'].includes(mode)) {
          await this.$store.dispatch('role/updateCurrentRole', { id });
          await this.$store.dispatch('userInfo');
          const { role } = this.user;
          this.$store.commit('updateCurRoleId', id);
          this.$store.commit('updateIdentity', { id, type: role.type, name });
          this.$store.commit('updateNavId', id);
        }
        if (['quit'].includes(mode)) {
          this.$bkInfo({
            title: this.$t(`m.dialog['确认退出']`),
            subHeader: (
              <div class="del-actions-warn-info">
                <bk-icon type="info-circle-shape" class="warn" />
                <span>
                  { `${this.$t(`m.common['退出']`)}${this.$t(`m.common['【']`)}${name}${this.$t(`m.common['】']`)}, ${this.$t(`m.grading['退出提示']`)}` }
                  </span>
              </div>
            ),
            width: this.curLanguageIsCn ? 500 : 700,
            maskClose: true,
            closeIcon: false,
            confirmLoading: true,
            extCls: 'custom-perm-del-info',
            confirmFn: async () => {
              await this.$store.dispatch('role/deleteRatingManager', { id });
              this.messageSuccess(this.$t(`m.info['退出成功']`), 3000);
              this.resetPagination();
              this.handleFilterData();
            }
          });
          return;
        }
        this.$router.push({
          name: routerName,
          params: {
            id,
            role_type: 'staff',
            entry: 'personal'
          }
        });
      },

      // 二级管理空间
      async handleSubView ({ id, name }, index, row, mode) {
        window.localStorage.setItem('iam-header-name-cache', name);
        let routerName = 'userGroup';
        const routerNav = {
          detail: () => {
            routerName = 'userGroup';
            this.$store.commit('updateIndex', 1);
            window.localStorage.setItem('index', 1);
          },
          auth: () => {
            routerName = 'authorBoundary';
            this.$store.commit('updateIndex', 1);
            window.localStorage.setItem('index', 1);
          },
          clone: () => {
            routerName = 'secondaryManageSpaceCreate';
            this.$store.commit('updateIndex', 0);
            window.localStorage.setItem('index', 0);
          },
          quit: () => {
            this.$store.commit('updateIndex', 0);
            window.localStorage.setItem('index', 0);
          }
        };
        routerNav[mode]();
        if (!['clone', 'quit'].includes(mode)) {
          await this.$store.dispatch('role/updateCurrentRole', { id });
          await this.$store.dispatch('userInfo');
          const { role } = this.user;
          this.$store.commit('updateCurRoleId', id);
          this.$store.commit('updateIdentity', { id, type: role.type, name });
          this.$store.commit('updateNavId', id);
        }
        if (['quit'].includes(mode)) {
          this.$bkInfo({
            title: this.$t(`m.dialog['确认退出']`),
            subHeader: (
              <div class="del-actions-warn-info">
                <bk-icon type="info-circle-shape" class="warn" />
                <span>
                  { `${this.$t(`m.common['退出']`)}${this.$t(`m.common['【']`)}${name}${this.$t(`m.common['】']`)}, ${this.$t(`m.grading['退出提示']`)}` }
                  </span>
              </div>
            ),
            width: this.curLanguageIsCn ? 500 : 700,
            maskClose: true,
            closeIcon: false,
            confirmLoading: true,
            extCls: 'custom-perm-del-info',
            confirmFn: async () => {
              await this.$store.dispatch('role/deleteRatingManager', { id });
              this.messageSuccess(this.$t(`m.info['退出成功']`), 3000);
              if (row.children && row.children.length) {
                const childData = row.children.find((item) => item.id === id);
                if (childData) {
                  row.children = [];
                  this.resetSubPagination();
                  this.isFilter ? await this.fetchSearchManageList()
                  : await this.fetchSubManagerList(row);
                }
              }
            }
          });
          return;
        }
        this.$router.push({
          name: routerName,
          params: {
            id,
            role_type: 'staff',
            entry: 'personal'
          }
        });
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

      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.handleFilterData();
      },

      handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { limit, current: 1 });
        this.handleFilterData();
      },

      handleFilterData () {
        this.isFilter ? this.fetchSearchManageList(true) : this.fetchGradingAdmin(true);
      },

      handleCreate () {
        this.$router.push({
          name: 'myManageSpaceCreate'
        });
      },

      setCurrentQueryCache (payload) {
        window.localStorage.setItem('myManagerList', JSON.stringify(payload));
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

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      },

      handleEmptyClear () {
        this.resetSearchData();
      },

      handleEmptyRefresh () {
        this.resetPagination();
        this.resetSubPagination();
        this.fetchGradingAdmin();
      },

      resetSearchData () {
        this.isFilter = false;
        this.searchValue = '';
        this.searchMember = '';
        this.emptyData.tipType = '';
        this.searchList = [];
        this.searchData = _.cloneDeep(this.searchDefaultData);
        this.resetPagination();
        this.resetSubPagination();
        this.fetchGradingAdmin(true);
      },

      resetPagination () {
        this.pagination = Object.assign(
          {},
          {
            current: 1,
            count: 0,
            limit: 10,
            showTotalCount: true
          }
        );
      },

      resetSubPagination () {
        this.subPagination = Object.assign(
          {},
          {
            current: 1,
            count: 0,
            limit: 10
          }
        );
      },

      handleOpenDocu () {
        navDocCenterPath(this.versionLogs, `/UserGuide/Feature/UserApply.md`, true);
      }
    }
  };
</script>

<style lang="postcss">
@import '@/css/mixins/custom-table-dot.css';
</style>

<style lang="postcss" scoped>
@import '@/css/mixins/custom-delete-action.css';
.iam-level-manage-space-wrapper {
  .level-manage-table {
    margin-top: 16px;
  }

  .right-form {
    display: flex;
  }

  .admin-link {
    margin-left: 10px;
    .linkText {
        font-size: 12px
    }
  }

  .operate_btn {
    .bk-button-text {
      &:nth-child(n+2) {
        margin-left: 10px;
      }
    }
  }

  .level-manage-table {
    /deep/ .bk-table-pagination-wrapper {
      background: #fff;
    }
  }

  /deep/ .flex_space_name {
    display: flex;
    align-items: center;
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

  /deep/ .iam-tag-table-cell-subset-cls {
    .cell {
      .bk-table-expand-icon {
        display: none;
      }
    }
  }

  /deep/ .iam-table-cell-1-cls, .iam-tag-table-cell-subset-cls  {
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
    .iam-tag-table-cell-cls {
        .cell {
            padding-left: 0;
        }
    }
    .bk-table .cell {
        padding-left: 2px;
    }
  }
}

/deep/ .custom-perm-del-info {
  .bk-dialog-footer {
    padding: 0 65px 33px !important;
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
