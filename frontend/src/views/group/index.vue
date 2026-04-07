<template>
  <div class="iam-user-group-wrapper">
    <render-search>
      <!-- <bk-button v-if="isSuperManager" :disabled="currentSelectList.length < 1" style="margin-left: 6px"
                data-test-id="group_btn_transferOut" @click="handleTransferOut">
                {{ $t(`m.userGroup['转出']`) }}
            </bk-button>
            <bk-button
                :disabled="currentSelectList.length < 1"
                theme="primary"
                @click="handleBatchAddMember"
                data-test-id="group_btn_create"
            >
                {{ $t(`m.common['批量添加成员']`) }}
            </bk-button>
            <bk-button
                v-if="isRatingManager"
                :disabled="currentSelectList.length < 1"
                style="margin-left: 6px"
                data-test-id="group_btn_distribute"
                @click="handleDistribute"
            >
                {{ $t(`m.userGroup['分配']`) }}
            </bk-button> -->
      <div class="search_left">
        <bk-button theme="primary" @click="handleCreate" data-test-id="group_btn_create">
          {{ $t(`m.common['新建']`) }}
        </bk-button>
        <bk-button v-if="isSuperManager" :disabled="currentSelectList.length < 1"
          data-test-id="group_btn_transferOut" @click="handleTransferOut">
          {{ $t(`m.userGroup['转出']`) }}
        </bk-button>
        <bk-button
          :disabled="isBatchDisabled"
          @click="handleBatchAddMember"
          data-test-id="group_btn_create"
        >
          {{ $t(`m.common['批量添加成员']`) }}
        </bk-button>
        <!-- <bk-button
                    v-if="isRatingManager"
                    :disabled="currentSelectList.length < 1"
                    style="margin-left: 6px"
                    data-test-id="group_btn_distribute"
                    @click="handleDistribute"
                >
                    {{ $t(`m.userGroup['分配']`) }}
                </bk-button> -->
        <!-- 注释掉下拉选择，采取button -->
        <!-- <bk-select
                    ref="userGroupSelect"
                    v-model="selectKeyword"
                    :searchable="true"
                    :placeholder="$t(`m.userGroup['批量']`)"
                    :search-placeholder="$t(`m.approvalProcess['请输入关键字搜索']`)"
                    ext-cls="select-custom"
                    ext-popover-cls="select-popover-custom"
                    @toggle="handleToggle">
                    <bk-option
                        v-for="option in batchOptions"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name"
                        :disabled="option.disabled"
                    >
                        <div @click.stop="handleSelect(option)">
                            {{option.name}}
                        </div>
                    </bk-option>
                </bk-select> -->
      </div>
      <!-- 先屏蔽 -->
      <div slot="right">
        <iam-search-select
          ref="iamSearchSelect"
          style="width: 420px;"
          :placeholder="$t(`m.userGroup['搜索用户组名、描述、管理空间、创建人']`)"
          :data="searchData"
          :value="searchValue"
          :quick-search-method="quickSearchMethod"
          @on-click-menu="handleClickSearchMenu"
          @on-change="handleSearch"
        />
      </div>
    </render-search>
    <bk-table
      size="small" :data="tableList"
      :resize="true"
      :max-height="tableHeight" :class="{ 'set-border': tableLoading }" ext-cls="user-group-table"
      :pagination="pagination" ref="tableRef" row-key="id" @page-change="pageChange"
      @page-limit-change="limitChange" @select="handlerChange" @select-all="handlerAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
      <bk-table-column type="selection" align="center" :selectable="getIsSelect" reserve-selection fixed="left" />
      <bk-table-column :label="$t(`m.userGroup['用户组名']`)" :min-width="240" fixed="left">
        <template slot-scope="{ row }">
          <span class="user-group-name" :title="row.name" @click="handleView(row)">{{ row.name }}</span>
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
      <template v-if="['rating_manager'].includes(curRole)">
        <bk-table-column :label="$t(`m.info['二级管理空间']`)" :min-width="200">
          <template slot-scope="{ row }">
            <div class="user-group-space">
              <Icon
                v-if="['subset_manager'].includes(row.role.type)"
                type="level-two-manage-space"
                :style="{ color: '#9B80FE' }"
              />
              <iam-edit-input
                field="name"
                style="width: 100%; margin-left: 5px;"
                :placeholder="$t(`m.verify['请输入']`)"
                :is-show-other="true"
                :value="['subset_manager'].includes(row.role.type) ? row.role.name : '--'"
                @handleShow="handleDistribute(row)" />
            </div>

          </template>
        </bk-table-column>
      </template>
      <bk-table-column :label="$t(`m.userGroup['用户组属性']`)" width="200">
        <template slot-scope="{ row, $index }">
          <IamGroupAttribute
            style="width: 200px"
            :value="row.apply_disable ? ['apply_disable'] : []"
            :list="userGroupAttributesList"
            :attributes="userGroupAttributes"
            :index="$index"
            @on-change="handleChangeAttributes"
          />
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.userGroup['创建人']`)">
        <template slot-scope="{ row }">
          <IamUserDisplayName :user-id="row.creator" />
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
      <bk-table-column :label="$t(`m.common['创建时间']`)" width="160">
        <template slot-scope="{ row }">
          <span :title="row.created_time">{{ row.created_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['描述']`)" :min-width="100">
        <template slot-scope="{ row }">
          <span :title="row.description || ''">{{ row.description || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)" :width="curLanguageIsCn ? 180 : 260" fixed="right">
        <template slot-scope="{ row }">
          <div>
            <bk-button
              theme="primary"
              text
              :disabled="row.readonly"
              @click="handleAddMember(row)"
            >
              {{ $t(`m.common['添加成员']`) }}
            </bk-button>
            <bk-popover
              :content="formatDisabledAddPerm(row, 'title')"
              :disabled="!formatDisabledAddPerm(row, 'disabled')"
            >
              <bk-button
                text
                theme="primary"
                style="margin-left: 10px"
                :disabled="formatDisabledAddPerm(row, 'disabled')"
                @click="handleAddPerm(row)">
                {{ $t(`m.common['添加权限']`) }}
              </bk-button>
            </bk-popover>
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
                  <bk-button theme="primary" text @click="handleClone(row)">
                    {{ $t(`m.grading['克隆']`) }}
                  </bk-button>
                </li>
                <li class="custom-table-dot-menu-item">
                  <bk-button theme="primary" text @click="handleDelete(row)">
                    {{ $t(`m.common['删除']`) }}
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

    <delete-dialog
      :show.sync="isShowDeleteDialog"
      :loading="deleteLoading"
      :name="currentUserGroup.name"
      @on-after-leave="handleAfterDeleteLeave"
      @on-cancel="hideCancelDelete"
      @on-submit="handleSubmitDelete"
    />

    <edit-process-dialog
      :show.sync="isShowEditProcessDialog"
      :loading="editLoading"
      @on-after-leave="handleAfterEditLeave"
      @on-cancel="hideCancelEdit"
      @on-submit="handleSubmitEdit"
    />

    <add-member-dialog
      :show.sync="isShowAddMemberDialog"
      :is-batch="isBatch"
      :loading="loading"
      :name="curName"
      :id="curId"
      :is-rating-manager="isRatingManager"
      show-expired-at
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd"
      @on-after-leave="handleAddAfterClose"
    />

    <transfer-out-dialog
      :show.sync="isShowRolloutGroupDialog"
      :group-ids="curSelectIds"
      @on-success="handleTransferOutSuccess"
    />

    <DistributeToDialog
      :show.sync="isShowDistributeDialog"
      :group-ids="curSelectIds"
      :distribute-detail="distributeDetail"
      @on-success="handleDistributeSuccess"
    />

    <!-- <novice-guide :flag="showNoviceGuide" :content="content" /> -->
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { il8n } from '@/language';
  import { getWindowHeight, formatCodeData } from '@/common/util';
  import { fuzzyRtxSearch } from '@/common/rtx';
  import { buildURLParams } from '@/common/url';
  import { USER_GROUP_ATTRIBUTES } from '@/common/constants';
  import IamSearchSelect from '@/components/iam-search-select';
  import DeleteDialog from './components/delete-user-group-dialog';
  import AddMemberDialog from './components/iam-add-member';
  import EditProcessDialog from './components/edit-process-dialog';
  import TransferOutDialog from './components/transfer-out-dialog';
  import DistributeToDialog from './components/distribute-to-dialog';
  // import NoviceGuide from '@/components/iam-novice-guide';
  import IamEditInput from '@/components/iam-edit/input';
  import IamGroupAttribute from './components/iam-group-attribute.vue';

  export default {
    name: '',
    provide: function () {
      return {
        getGroupAttributes: () => this.groupAttributes
      };
    },
    components: {
      DeleteDialog,
      AddMemberDialog,
      EditProcessDialog,
      TransferOutDialog,
      DistributeToDialog,
      IamSearchSelect,
      // NoviceGuide,
      IamEditInput,
      IamGroupAttribute
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
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.userGroup['用户组名']`),
            default: true
          },
          {
            id: 'id',
            name: 'ID',
            // validate (values, item) {
            //     const validate = (values || []).every(_ => /^(\d*)$/.test(_.name))
            //     return !validate ? '' : true
            // }
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
        ],
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
        content: this.$t('m.nav["【管理空间】 功能，全面升级为【权限管理空间】啦！"]'),
        il8n,
        selectKeyword: '',
        isShowDistributeDialog: false,
        batchOptions: [
          {
            id: 0,
            name: this.$t(`m.common['添加成员']`),
            method: 'handleBatchAddMember',
            roles: ['allManager']
          },
          // 暂不支持批量，后期迭代再开放该选项
          // {
          //     id: 1,
          //     name: this.$t(`m.userGroup['分配 (二级管理空间)']`),
          //     method: 'handleDistribute',
          //     roles: ['rating_manager']
          // },
          {
            id: 2,
            name: this.$t(`m.userGroup['转出']`),
            method: 'handleTransferOut',
            roles: ['super_manager']
          }
        ],
        distributeDetail: null,
        queryParams: {},
        groupAttributes: {
          source_type: '',
          source_from_role: false
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        userGroupAttributes: {
          apply_disable: false
        },
        userGroupAttributesList: USER_GROUP_ATTRIBUTES,
        tableHeight: getWindowHeight() - 185
      };
    },
    computed: {
      ...mapGetters(['user', 'showNoviceGuide', 'externalSystemId']),
      isCanEditProcess () {
        return this.currentSelectList.length > 0;
      },
      isRatingManager () {
        return ['rating_manager', 'subset_manager'].includes(this.curRole);
      },
      isSuperManager () {
        return this.curRole === 'super_manager';
      },
      curSelectIds () {
        return this.currentSelectList.map((item) => item.id);
      },
      isBatchDisabled () {
        if (this.currentSelectList.length) {
          const isDisabled = this.currentSelectList.every(item => item.readonly);
          return isDisabled;
        } else {
          return true;
        }
      },
      formatDisabledAddPerm () {
        return (payload, type) => {
          const typeMap = {
            title: () => {
              if (payload.attributes && payload.attributes.source_from_role) {
                return this.$t(`m.userGroup['管理员组无法添加权限']`);
              }
              if (payload.readonly) {
                return this.$t(`m.userGroup['只读用户组无法添加权限']`);
              }
              return '';
            },
            disabled: () => {
              if (payload.readonly || (payload.attributes && payload.attributes.source_from_role)) {
                return true;
              }
              return false;
            }
          };
          if (typeMap[type]) {
            return typeMap[type]();
          }
        };
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
      },
      currentSelectList: {
        handler (value) {
          if (!value.length) {
            this.selectKeyword = '';
          }
        },
        immediate: true,
        deep: true
      }
    },
    async created () {
      window.addEventListener('resize', () => {
        this.tableHeight = getWindowHeight() - 185;
      });
      this.curRole = this.user.role.type || 'staff';
      this.searchParams = this.$route.query;
      this.setCurrentQueryCache(this.refreshCurrentQuery());
      const isObject = (payload) => {
        return Object.prototype.toString.call(payload) === '[object Object]';
      };
      const currentQueryCache = await this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        this.pagination = Object.assign(
          this.pagination,
          {
            current: currentQueryCache.current ? Number(currentQueryCache.current) : this.pagination.current,
            limit: currentQueryCache.limit ? Number(currentQueryCache.limit) : this.pagination.limit
          }
        );
        for (const key in currentQueryCache) {
          if (key !== 'limit' && key !== 'current') {
            const curData = currentQueryCache[key];
            const tempData = this.searchData.find((item) => item.id === key);
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
                values: [
                  {
                    id: curData,
                    name: curData
                  }
                ]
              });
              this.searchList.push(..._.cloneDeep(this.searchValue));
              this.searchParams[key] = curData;
            } else {
              this.searchParams[key] = curData;
            }
          }
        }
      }
      await this.fetchUserGroupSet();
    },
    beforeDestroy () {
      window.localStorage.removeItem('groupList');
    },
    methods: {
      /**
       * 获取页面数据
       */
      async fetchPageData () {
        await this.fetchUserGroupList();
      },

      // 获取分级管理员用户组配置
      async fetchUserGroupSet () {
        if (!['subset_manager', 'staff', ''].includes(this.curRole)) {
          try {
            const { data } = await this.$store.dispatch('userGroupSetting/getUserGroupSetConfig');
            if (data) {
              this.userGroupAttributes = Object.assign({}, { apply_disable: data.apply_disable });
            }
          } catch (e) {
            console.error(e);
            this.messageAdvancedError(e);
          }
        }
      },

      getIsSelect () {
        return this.tableList.length > 0;
      },

      refreshCurrentQuery () {
        const params = {};
        let queryParams = {
          ...this.searchParams,
          ...this.queryParams,
          role_name: this.user.role.name
        };
        const groupStorage = localStorage.getItem('groupList') ? JSON.parse(localStorage.getItem('groupList')) : {};
        if (!Object.keys(queryParams).length && Object.keys(groupStorage).length > 0) {
          queryParams = Object.assign(queryParams, groupStorage);
        }
        if (Object.keys(queryParams).length) {
          window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        }
        for (const key in this.searchParams) {
          const tempObj = this.searchData.find((item) => key === item.id);
          if (tempObj && tempObj.remoteMethod && typeof tempObj.remoteMethod === 'function') {
            if (this.searchList.length) {
              const tempData = this.searchList.find((item) => item.id === key);
              if (tempData) {
                params[key] = tempData.values[0];
              }
            }
          } else {
            params[key] = this.searchParams[key];
          }
        }
        this.emptyData = Object.assign(this.emptyData, { tipType: Object.keys(this.searchParams).length > 0 ? 'search' : '' });
        return {
            ...queryParams
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
        await this.setCurrentQueryCache(this.refreshCurrentQuery());
        const params = {
          ...this.searchParams,
          limit: this.pagination.limit,
          offset: this.pagination.limit * (this.pagination.current - 1)
        };
        delete params.current;
        try {
          const { code, data } = await this.$store.dispatch('userGroup/getUserGroupList', params);
          this.pagination.count = data.count || 0;
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.currentSelectList = this.currentSelectList.filter((item) => {
            return this.tableList.map((_) => _.id).includes(item.id);
          });
          if (this.currentSelectList.length < 1) {
            this.$refs.tableRef && this.$refs.tableRef.clearSelection();
          }
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
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

      async handleChangeAttributes (payload, index) {
        const { id, name, description } = this.tableList[index];
        const params = {
          id,
          name,
          description,
          apply_disable: !!payload.includes('apply_disable')
        };
        const { code } = await this.$store.dispatch('userGroup/editUserGroup', params);
        if (code === 0) {
          this.$set(this.tableList[index], 'apply_disable', !!payload.includes('apply_disable'));
          this.messageSuccess(this.$t(`m.info['编辑成功']`), 3000);
        }
      },

      handleRemoteRtx (value) {
        return fuzzyRtxSearch(value).then((data) => {
          return data.results;
        });
      },

      handleRemoteSystem (value) {
        const params = {};
        if (this.externalSystemId) {
          params.hidden = false;
        }
        return this.$store.dispatch('system/getSystems', params).then(({ data }) => {
          return data.map(({ id, name }) => ({ id, name })).filter((item) => item.name.indexOf(value) > -1);
        });
      },

      handleCreate () {
        this.$router.push({
          name: 'createUserGroup'
        });
      },

      handleClone (payload) {
        const { id } = payload;
        this.$router.push({
          name: 'cloneUserGroup',
          query: {
            id
          }
        });
      },

      handleTransferOut () {
        this.isShowRolloutGroupDialog = true;
      },

      handleTransferOutSuccess () {
        this.isShowRolloutGroupDialog = false;
        this.currentSelectList = [];
        this.resetPagination();
        this.fetchUserGroupList(true);
      },

      handleDistribute ({ id, role }) {
        this.isShowDistributeDialog = true;
        this.distributeDetail = Object.assign({}, { id, role });
      },

      handleDistributeSuccess () {
        this.isShowDistributeDialog = false;
        this.currentSelectList = [];
        this.resetPagination();
        this.fetchUserGroupList(true);
      },

      handleEditApprovalProcess () {
        this.isShowDistributeDialog = true;
      },

      resetPagination () {
        this.pagination = Object.assign(
          {},
          {
            limit: 10,
            current: 1,
            count: 0,
            showTotalCount: true
          }
        );
      },

      handleClickSearchMenu (payload) {
        // 单独对人员筛选相关的字段做处理
        const searchSelectRef = this.$refs.iamSearchSelect.$refs.searchSelect;
        const keywordValue = searchSelectRef.localValue.replace(`${this.$t(`m.grading['创建人']`)}${this.$t(`m.common['：']`)}`, '');
        const isEmpty = ['creator'].includes(payload.menu.id) && !keywordValue;
        if (isEmpty) {
          searchSelectRef.hidePopper();
        }
      },

      handleSearch (payload, result) {
        this.searchParams = payload;
        this.searchList = result;
        this.emptyData.tipType = 'search';
        this.queryParams = Object.assign(this.queryParams, { current: 1, limit: 10 });
        this.resetPagination();
        this.fetchUserGroupList(true);
      },

      handleEmptyClear () {
        this.queryParams = {};
        this.searchParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.queryParams = Object.assign(this.queryParams, { current: 1, limit: 10 });
        this.resetPagination();
        this.fetchUserGroupList(true);
      },

      handleEmptyRefresh () {
        this.queryParams = Object.assign(this.queryParams, { current: 1, limit: 10 });
        this.resetPagination();
        this.fetchUserGroupList(true);
      },

      handleAddMember (payload) {
        const { id, name, attributes } = payload;
        this.curName = name;
        this.curId = id;
        this.groupAttributes = Object.assign(this.groupAttributes, attributes);
        this.isBatch = false;
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

      async handleSubmitAdd (payload) {
        const { users, departments, templates, expiredAt } = payload;
        // 判断批量选择的用户组里是否包含管理员组
        const hasAdminGroups = this.currentSelectList.filter(item =>
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
        if (templates.length > 0) {
          arr.push(
            ...templates.map((item) => {
              return {
                id: item.id,
                type: 'template'
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
          params.group_ids = this.curSelectIds;
          delete params.id;
          fetchUrl = 'userGroup/batchAddUserGroupMember';
        }
        console.log('params', params);
        try {
          this.loading = true;
          await this.$store.dispatch(fetchUrl, params);
          this.isShowAddMemberDialog = false;
          this.currentSelectList = [];
          this.messageSuccess(this.$t(`m.info['添加成员成功']`), 3000);
          this.fetchUserGroupList(true);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.loading = false;
        }
      },

      handleAddAfterClose () {
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
        this.queryParams = Object.assign(this.queryParams, { current: page });
        this.fetchUserGroupList(true);
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: currentLimit });
        this.queryParams = Object.assign(this.queryParams, { current: 1, limit: currentLimit });
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

      async handleSubmitDelete () {
        this.deleteLoading = true;
        try {
          await this.$store.dispatch('userGroup/deleteUserGroup', {
            id: this.currentUserGroup.id
          });
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          this.isShowDeleteDialog = false;
          this.resetPagination();
          this.fetchUserGroupList(true);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.deleteLoading = false;
        }
      },

      handleSubmitEdit () {
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

      handleAfterEditLeave () { },

      handleBatchAddMember () {
        const hasDisabledData = this.currentSelectList.filter(item => item.readonly);
        if (hasDisabledData.length) {
          const disabledNames = hasDisabledData.map(item => item.name);
          this.messageWarn(this.$t(`m.info['用户组为只读用户组不能添加成员']`, { value: `${this.$t(`m.common['【']`)}${disabledNames}${this.$t(`m.common['】']`)}` }), 3000);
          return;
        }
        this.isBatch = true;
        this.isShowAddMemberDialog = true;
      },

      handleSelect (value) {
        const { id, disabled, method } = value;
        if (!disabled) {
          this.selectKeyword = id;
          this.$refs.userGroupSelect.close();
          this[method]();
        }
      },
            
      handleToggle (value) {
        if (value) {
          this.formatOption();
        }
      },

      formatOption () {
        const batchItem = [false, !this.isRatingManager, !this.isSuperManager];
        this.batchOptions = this.batchOptions.reduce((current, next) => {
          return next.roles.includes('allManager') || next.roles.includes(this.curRole)
            ? current.concat(Object.assign({}, next, {
              disabled: this.isCanEditProcess ? batchItem[next.id] : true
            })) : current;
        }, []);
      }
    }
  };
</script>
<style lang="postcss">
@import '@/css/mixins/custom-table-dot.css';
.iam-user-group-wrapper {
    .search_left {
      display: flex;
      align-items: center;
      .bk-button {
        margin-right: 6px;
      }
    }

    .select-custom {
        width: 220px;
        background-color: #fff;
        margin-left: 20px;
    }

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
                .depart,
                .template {
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

        .user-group-space {
            display: flex;
            align-items: center;
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

                i {
                    font-size: 14px;
                    color: #c4c6cc;
                }
            }

            .depart,
            .template {
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

        .bk-table-pagination-wrapper {
            background-color: #ffffff;
        }

        .bk-table-fixed, .bk-table-fixed-right {
            border-bottom: 0;
        }
    }
}
</style>
