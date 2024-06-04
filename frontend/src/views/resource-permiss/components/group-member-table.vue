<template>
  <div class="iam-user-group-member group-member-table">
    <render-search>
      <div class="group-member-button">
        <div class="group-member-tab">
          <div class="group-member-button">
            <div
              v-for="item in groupTabList"
              :key="item.id"
              :class="['group-member-button-item', { 'is-active': tabActive === item.name }]"
              @click.stop="handleTabChange(item.name, true)"
            >
              <span class="group-member-button-item-name">{{ item.label }}</span>
              <span class="group-member-button-item-count">
                {{ item.count }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div slot="right">
        <bk-button class="batch-delete-btn" :disabled="isNoBatchDelete()" @click.stop="handleBatchDelete">
          {{ $t(`m.common['批量移除']`) }}
        </bk-button>
        <bk-input
          v-model="keyword"
          style="width: 400px"
          :placeholder="tabPlaceHolder"
          :right-icon="'bk-icon icon-search'"
          :clearable="true"
          @right-icon-click="handleKeyWordEnter"
          @enter="handleKeyWordEnter"
          @clear="handleKeyWordClear"
        />
      </div>
    </render-search>
    <bk-table
      ref="groupMemberRef"
      size="small"
      ext-cls="user-group-member-table"
      :data="getTableList()"
      :cell-class-name="getCellClass"
      :outer-border="false"
      :header-border="false"
      :pagination="formatPagination()"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handleChange"
      @select-all="handleAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column type="selection" align="center" :selectable="getDefaultSelect" />
      <template v-for="item in tableProps">
        <template v-if="item.prop === 'name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :show-overflow-tooltip="true">
            <template slot-scope="{ row }">

              <div v-if="row.type === 'user'" class="user"
              >
                <Icon type="personal-user" />
                <span class="name" :style="{ maxWidth: curDisplaySet.customNameWidth }">{{ row.id }}</span>
                <span class="count" v-if="row.name">
                  {{ "(" + row.name + ")" }}
                </span>
              </div>
              <div v-else class="depart">
                <Icon type="organization-fill" />
                <span class="name" :style="{ maxWidth: curDisplaySet.customNameWidth }">
                  {{ row.name || "--" }}
                </span>
                <span class="count" v-if="row.member_count && enableOrganizationCount">
                  ({{ row.member_count }})
                </span>
              </div>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'template_name'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
          >
            <template slot-scope="{ row }">
              <span class="member-template" :title="row.name" @click.stop="handleTempView(row)">
                <Icon type="renyuanmuban" />
                <span class="name">
                  {{ row.name || "--" }}
                </span>
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'user_departments'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <template v-if="row.type === 'user'">
                <template v-if="row.user_departments && row.user_departments.length">
                  <div
                    :title="row.user_departments.join(';')"
                    v-for="(v, i) in row.user_departments"
                    :key="i"
                    class="user_departs"
                  >
                    {{ v }}
                  </div>
                </template>
                <template v-else>
                  <div>--</div>
                </template>
              </template>
              <template v-else>
                {{ row.full_name }}
              </template>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'expired_at_display'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
          />
        </template>
        <template v-else-if="item.prop === 'description'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <span :title="row.description">
                {{ row.description || '--' }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'created_time'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop">
            <template slot-scope="{ row }">
              <span :title="row.created_time.replace(/T/, ' ')">
                {{ row.created_time.replace(/T/, " ") }}
              </span>
            </template>
          </bk-table-column>
        </template>
        <template v-else-if="item.prop === 'operate'">
          <bk-table-column
            :key="item.prop"
            :label="item.label"
            :prop="item.prop"
            :width="80"
          >
            <template slot-scope="{ row }">
              <bk-popconfirm
                trigger="click"
                placement="bottom-end"
                ext-popover-cls="resource-perm-delete-confirm"
                :width="280"
                :confirm-text="$t(`m.common['删除-dialog']`)"
                @confirm="handleDelete(row)"
              >
                <div slot="content">
                  <div class="popover-title">
                    <div class="popover-title-text">
                      {{ deletePopoverConfirm[tabActive].title }}
                    </div>
                  </div>
                  <div class="popover-content">
                    <div class="popover-content-item">
                      <span class="popover-content-item-label">{{ deletePopoverConfirm[tabActive].text }}:</span>
                      <span class="popover-content-item-value"> {{ row.name }}</span>
                    </div>
                    <div class="popover-content-tip">
                      {{ deletePopoverConfirm[tabActive].tip }}
                    </div>
                  </div>
                </div>
                <bk-popover
                  :content="formatDelDisabled('title')"
                  :disabled="!formatDelDisabled('disabled')">
                  <bk-button
                    theme="primary"
                    text
                    class="actions-btn-item"
                    :disabled="formatDelDisabled('disabled')"
                  >
                    {{ $t(`m.common['移除']`) }}
                  </bk-button>
                </bk-popover>
              </bk-popconfirm>
            </template>
          </bk-table-column>
        </template>
      </template>
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

    <DeleteDialog
      :show.sync="deleteDialog.visible"
      :loading="deleteDialog.loading"
      :title="deleteDialog.title"
      :sub-title="deleteDialog.subTitle"
      @on-after-leave="handleAfterDeleteLeave"
      @on-cancel="handleCancelDelete"
      @on-sumbit="handleSubmitDelete"
    />
  </div>
</template>

<script>
  import il8n from '@/language';
  import { mapGetters } from 'vuex';
  import { cloneDeep } from 'lodash';
  import { formatCodeData } from '@/common/util';
  import DeleteDialog from '@/views/group/common/iam-confirm-dialog';
  export default {
    components: {
      DeleteDialog
    },
    props: {
      curDetailData: {
        type: Object,
        default: () => {
          return {};
        }
      },
      groupAttributes: {
        type: Object,
        default: () => {
          return {};
        }
      },
      displaySet: {
        type: Object
      },
      readOnly: {
        type: Boolean,
        default: false
      },
      isShowTab: {
        type: Boolean,
        default: true
      },
      searchPlaceholder: {
        type: String,
        default: il8n('resourcePermiss', '搜索 用户、组织名')
      },
      routeMode: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        enableOrganizationCount: window.ENABLE_ORGANIZATION_COUNT.toLowerCase() === 'true',
        tableLoading: false,
        keyword: '',
        curRouteMode: '',
        tabPlaceHolder: '',
        adminGroupTitle: '',
        tabActive: 'userOrgPerm',
        externalRoutes: ['userGroupDetail', 'memberTemplate', 'resourcePermiss'],
        groupTabList: [
          {
            name: 'userOrgPerm',
            label: this.$t(`m.resourcePermiss['用户 / 组织']`),
            count: 0,
            empty: 'emptyOrgData',
            tableList: []
          },
          {
            name: 'memberTemplate',
            label: this.$t(`m.nav['人员模板']`),
            count: 0,
            empty: 'emptyTempData',
            tableList: []
          }
        ],
        tableProps: [],
        currentSelectList: [],
        deleteDialog: {
          visible: false,
          title: this.$t(`m.dialog['确认移除']`),
          subTitle: '',
          loading: false
        },
        curMember: {},
        curData: {},
        curDisplaySet: {},
        curModeMap: {
          memberTemplate: {
            list: {
              url: 'memberTemplate/getSubjectTemplateMembers',
              params: {}
            },
            removeMember: {
              dialogTitle: '确认移除该用户/组织？',
              url: 'memberTemplate/deleteSubjectTemplateMembers',
              params: {
                subjects: []
              }
            },
            addMember: {
              url: 'memberTemplate/addSubjectTemplateMembers',
              params: {
                subjects: []
              }
            },
            copy: {
              url: 'memberTemplate/getSubjectTemplateMembers'
            }
          }
        },
        deletePopoverConfirm: {
          userOrgPerm: {
            title: this.$t(`m.dialog['确认移除该用户？']`),
            text: this.$t(`m.common['用户名']`),
            tip: this.$t(`m.resourcePermiss['移除后，该用户将不再继承该用户组的权限，请谨慎操作。']`)
          },
          memberTemplate: {
            title: this.$t(`m.dialog['确认移除该人员模板？']`),
            text: this.$t(`m.memberTemplate['人员模板']`),
            tip: this.$t(`m.resourcePermiss['移除后，人员模板里的用户/组织可能会失去关联用户组的权限，请谨慎操作。']`)
          }
        },
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        userOrOrgPagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        memberPagination: {
          current: 1,
          count: 0,
          limit: 10,
          showTotalCount: true
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        emptyOrgData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        emptyTempData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      isShowMemberTemplate () {
        return !['staff'].includes(this.user.role.type);
      },
      // 蓝盾场景
      isShowExternalMemberTemplate () {
        return !['staff', 'rating_manager'].includes(this.user.role.type);
      },
      isExistMemberTemplate () {
        return this.externalSystemId
          ? this.isShowTab && this.isShowExternalMemberTemplate : this.isShowTab && this.isShowMemberTemplate;
      },
      isNoBatchDelete () {
        return () => {
          const hasData = this.currentSelectList.length > 0;
          if (
            hasData
            && ['userOrgPerm'].includes(this.tabActive)
            && this.groupAttributes
            && this.groupAttributes.source_from_role
          ) {
            const isAll = hasData && this.currentSelectList.length === this.userOrOrgCount;
            this.adminGroupTitle = isAll
              ? this.$t(`m.userGroup['管理员组至少保留一条数据']`)
              : '';
            return isAll;
          }
          return !hasData;
        };
      },
      formatDelDisabled () {
        return (payload) => {
          const isAdmin = this.groupAttributes
            && this.groupAttributes.source_from_role
            && (this.userOrOrgCount === 1 || (this.userOrOrgCount === this.userOrOrgPagination.count === 1))
            && (['userOrgPerm'].includes(this.tabActive) && !this.routeMode);
          const typeMap = {
            title: () => {
              if (isAdmin) {
                return this.$t(`m.userGroup['管理员组至少保留一条数据']`);
              }
              return '';
            },
            disabled: () => {
              return isAdmin;
            }
          };
         return typeMap[payload]();
        };
      },
      formatPagination () {
        return () => {
          const typeMap = {
            userOrgPerm: () => {
              return this.userOrOrgPagination;
            },
            memberTemplate: () => {
              return this.memberPagination;
            }
          };
          if (typeMap[this.tabActive]) {
            return typeMap[this.tabActive]();
          }
        };
      },
      getTableList () {
        return () => {
          const typeMap = {
            userOrgPerm: () => {
              return this.groupTabList[0].tableList;
            },
            memberTemplate: () => {
              return this.groupTabList[1].tableList;
            }
          };
          if (typeMap[this.tabActive]) {
            return typeMap[this.tabActive]();
          }
        };
      }
    },
    watch: {
      searchPlaceholder: {
        handler (value) {
          this.tabPlaceHolder = value;
        },
        immediate: true
      },
      tabActive: {
        handler (newValue, oldValue) {
          this.tableProps = this.getTableProps(newValue);
          if (oldValue && oldValue !== newValue) {
            this.resetPagination();
          }
        },
        immediate: true
      },
      displaySet: {
        handler (value) {
          this.curDisplaySet = Object.assign({}, value);
        },
        immediate: true
      }
    },
    created () {
      this.fetchInitData();
    },
    methods: {
      async fetchGroupDetail () {
        console.log();
      },
      async fetchUserOrOrgList () {
        this.tableLoading = true;
        try {
          const { current, limit } = this.userOrOrgPagination;
          const params = {
            id: this.curDetailData.id,
            limit,
            offset: limit * (current - 1),
            keyword: this.keyword
          };
          const url = 'userGroup/getUserGroupMemberList';
          const { code, data } = await this.$store.dispatch(
            url,
            params
          );
          const { count, results } = data;
          this.$set(this.groupTabList[0], 'tableList', results || []);
          this.userOrOrgPagination.count = count || 0;
          // 处理蓝盾管理员组业务，搜索只有一条实际有多条数据
          if (!this.keyword) {
            this.userOrOrgCount = count || 0;
          }
          this.emptyOrgData = formatCodeData(code, this.emptyOrgData, this.groupTabList[0].tableList.length === 0);
          if (this.keyword) {
            if (!data.hasOwnProperty('count')) {
              this.userOrOrgPagination.count = this.groupTabList[0].tableList.length;
            }
            this.emptyOrgData = Object.assign(this.emptyOrgData, { tipType: 'search' });
          }
          this.fetchRefreshSelectList();
        } catch (e) {
          this.$set(this.groupTabList[0], 'tableList', []);
          this.userOrOrgPagination.count = 0;
          this.userOrOrgCount = 0;
          this.emptyOrgData = formatCodeData(e.code, this.emptyOrgData);
          this.handleRefreshTabCount();
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
          const emptyField = this.groupTabList.find((item) => item.name === this.tabActive);
          if (emptyField) {
            this.emptyData = formatCodeData(0, cloneDeep(Object.assign(this[emptyField.empty], { tipType: this.keyword ? 'search' : '' })));
          }
        }
      },

      async fetchMemberTemplateList () {
        this.tableLoading = true;
        try {
          const { current, limit } = this.memberPagination;
          const params = {
            id: this.curDetailData.id,
            page: current,
            page_size: limit,
            name: this.keyword
          };
          const { code, data } = await this.$store.dispatch(
            'memberTemplate/getGroupSubjectTemplate',
            params
          );
          const { count, results } = data;
          this.$set(this.groupTabList[1], 'tableList', results || []);
          this.memberPagination.count = count || 0;
          if (this.keyword) {
            if (!data.hasOwnProperty('count')) {
              this.memberPagination.count = this.groupTabList[1].tableList.length;
            }
            this.emptyOrgData = Object.assign(this.emptyOrgData, { tipType: 'search' });
          }
          this.emptyTempData = formatCodeData(code, this.emptyTempData, this.memberPagination.count === 0);
          this.fetchRefreshSelectList();
        } catch (e) {
          this.$set(this.groupTabList[1], 'tableList', []);
          this.memberPagination.count = 0;
          this.emptyTempData = formatCodeData(e.code, this.emptyTempData);
          this.messageAdvancedError(e);
          this.handleRefreshTabCount();
        } finally {
          this.tableLoading = false;
          const emptyField = this.groupTabList.find((item) => item.name === this.tabActive);
          if (emptyField) {
            this.emptyData = cloneDeep(Object.assign(this[emptyField.empty], { tipType: this.keyword ? 'search' : '' }));
          }
        }
      },

      async fetchRefreshSelectList () {
        const emptyField = this.groupTabList.find((item) => item.name === this.tabActive);
        if (emptyField) {
          this.$nextTick(() => {
            const currentSelectList = this.currentSelectList.map((item) => item.id.toString());
            emptyField.tableList.forEach((item) => {
              if (['memberTemplate'].includes(this.tabActive)) {
                this.$set(item, 'type', 'template');
              }
              if (currentSelectList.includes(item.id.toString())) {
                this.$refs.groupMemberRef
                  && this.$refs.groupMemberRef.toggleRowSelection(item, true);
              }
            });
            if (!this.currentSelectList.length) {
              this.$refs.groupMemberRef && this.$refs.groupMemberRef.clearSelection();
            }
          });
          await this.handleRefreshTabCount();
          await this.fetchCustomTotal();
        }
      },

      async handleKeyWordEnter () {
        this.resetPagination();
        this.fetchInitData();
      },

      async handleKeyWordClear () {
        await this.handleEmptyRefresh();
      },

      fetchInitData () {
        const { id } = this.curDetailData;
        if (!id) {
          return;
        }
        this.fetchUserOrOrgList();
        if (this.isExistMemberTemplate) {
          this.fetchMemberTemplateList();
        }
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectList.push(row);
            } else {
              this.currentSelectList = this.currentSelectList.filter(
                (item) => item.id.toString() !== row.id.toString()
              );
            }
            this.fetchCustomTotal();
          },
          all: () => {
            const emptyField = this.groupTabList.find((item) => item.name === this.tabActive);
            if (emptyField) {
              const tableList = cloneDeep(emptyField.tableList);
              const selectGroups = this.currentSelectList.filter(
                (item) => !tableList.map((v) => v.id.toString()).includes(item.id.toString())
              );
              this.currentSelectList = [...selectGroups, ...payload];
              this.fetchCustomTotal();
            }
          }
        };
        return typeMap[type]();
      },

      handleTabChange (payload, isClick = false) {
        if (payload === this.tabActive && isClick) {
          return;
        }
        this.tabPlaceHolder = ['userOrgPerm'].includes(payload) ? this.$t(`m.resourcePermiss['搜索 用户、组织名']`) : this.$t(`m.resourcePermiss['搜索 人员模板']`);
        this.tabActive = payload;
      },

      handleRefreshTab () {
        this.curMember = {};
        this.currentSelectList = [];
        this.groupTabList.forEach((item) => {
          item.tableList = [];
        });
        this.resetPagination();
        const tabMap = {
          userOrgPerm: async () => {
            await this.fetchUserOrOrgList();
          },
          memberTemplate: async () => {
            await this.fetchMemberTemplateList();
          }
        };
        return tabMap[this.tabActive]();
      },

      handleAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handleChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },

      handlePageChange (current) {
        const tabMap = {
          userOrgPerm: () => {
            this.userOrOrgPagination = Object.assign(this.userOrOrgPagination, { current });
            this.fetchUserOrOrgList();
          },
          memberTemplate: () => {
            this.memberPagination = Object.assign(this.memberPagination, { current });
            this.fetchMemberTemplateList();
          }
        };
        return tabMap[this.tabActive]();
      },

      handleLimitChange (limit) {
        const tabMap = {
          userOrgPerm: () => {
            this.userOrOrgPagination = Object.assign(this.userOrOrgPagination, { current: 1, limit });
            this.fetchUserOrOrgList();
          },
          memberTemplate: () => {
            this.memberPagination = Object.assign(this.memberPagination, { current: 1, limit });
            this.fetchMemberTemplateList();
          }
        };
        return tabMap[this.tabActive]();
      },

      handleBatchDelete () {
        if (this.currentSelectList.length === 1) {
          const payload = this.currentSelectList[0];
          if (this.curModeMap[this.curRouteMode]) {
            this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)}${this.$t(
              `m.common['【']`
            )}${payload.id}(${payload.name})${this.$t(`m.common['】']`)}${this.$t(
              `m.common['，']`
            )}${this.$t(`m.info['该用户/组织可能会失去关联用户组的权限']`)}${this.$t(`m.common['。']`)}`;
          } else {
            this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)}${this.$t(
              `m.common['【']`
            )}${payload.id}(${payload.name})${this.$t(`m.common['】']`)}${this.$t(
              `m.common['，']`
            )}${this.$t(`m.info['该成员将不再继承该组的权限']`)}${this.$t(`m.common['，']`)}${this.$t(`m.info['请谨慎操作']`)}${this.$t(`m.common['。']`)}`;
          }
        } else {
          if (this.curModeMap[this.curRouteMode]) {
            this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)} ${
              this.currentSelectList.length
            } ${this.$t(`m.common['个人员模板']`)}${this.$t(`m.common['，']`)}${this.$t(
              `m.info['相关人员将不再关联该用户组的权限']`
            )}${this.$t(`m.common['。']`)}`;
          } else {
            this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)} ${
              this.currentSelectList.length
            } ${this.$t(`m.common['位成员']`)}${this.$t(`m.common['，']`)}${this.$t(
              `m.info['这些成员将不再继承该组的权限']`
            )}${this.$t(`m.common['。']`)}`;
          }
        }
        this.deleteDialog.visible = true;
      },

      handleDelete (payload) {
        console.log(payload);
        if (this.curModeMap[this.curRouteMode]) {
          this.curMember = Object.assign(
            {},
            {
              id: payload.id,
              type: ['memberTemplate'].includes(this.routeMode) ? payload.type : 'template'
            }
          );
          this.handleSubmitDelete();
        } else {
          this.curMember = Object.assign(
            {},
            {
              id: payload.id,
              type: payload.type
            }
          );
          this.handleSubmitDelete();
        }
      },

      async handleSubmitDelete () {
        this.deleteDialog.loading = true;
        try {
          let url = 'userGroup/deleteUserGroupMember';
          const params = {
            id: this.curDetailData.id,
            members: this.curMember.id
              ? [this.curMember]
              : this.currentSelectList.map(({ id, type }) => ({ id, type }))
          };
          let totalCount = params.members.length;
          if (this.curModeMap[this.routeMode]) {
            url = this.curModeMap[this.routeMode].removeMember.url;
            params.subjects = cloneDeep(params.members);
            totalCount = params.subjects.length;
            delete params.members;
          }
          const { code, data } = await this.$store.dispatch(
            url,
            params
          );
          if (code === 0 && data) {
            const externalParams = {
              ...params,
              count: totalCount
            };
            if (this.externalRoutes.includes(this.$route.name)) {
              window.parent.postMessage(
                {
                  type: 'IAM',
                  data: externalParams,
                  code: ['memberTemplate'].includes(this.tabActive) ? 'remove_template_confirm' : 'remove_user_confirm'
                },
                '*'
              );
            }
            this.messageSuccess(this.$t(`m.info['移除成功']`), 3000);
            this.handleRefreshTab();
            this.fetchMemberListCount();
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.deleteDialog.loading = false;
          this.deleteDialog.visible = false;
        }
      },

      async fetchMemberListCount () {
        // 搜索移除成员后，再去查询当前搜索的数据是不是最后一条
        if (
          (['userOrgPerm'].includes(this.tabActive) && !this.routeMode)
          && this.getGroupAttributes
          && this.getGroupAttributes.source_from_role
          && this.keyword) {
          const selectParams = {
            id: this.id,
            offset: 0,
            limit: 10
          };
          try {
            const { data } = await this.$store.dispatch('userGroup/getUserGroupMemberList', selectParams);
            this.userOrOrgCount = data.count || 0;
          } catch (e) {
            this.messageAdvancedError(e);
          }
        }
      },

      handleEmptyClear () {
        this.handleEmptyRefresh();
      },

      handleEmptyRefresh () {
        this.keyword = '';
        this.emptyData.tipType = '';
        this.groupTabList.forEach((item) => {
          if (this[item.empty]) {
            this[item.empty].tipType = '';
          }
        });
        this.resetPagination();
        this.fetchInitData();
      },

      handleRefreshTabCount () {
        this.$nextTick(() => {
          this.$set(this.groupTabList[0], 'count', this.userOrOrgPagination.count || 0);
          this.$set(this.groupTabList[1], 'count', this.memberPagination.count || 0);
          this.$refs.tabRef
            && this.$refs.tabRef.$refs.tabLabel
            && this.$refs.tabRef.$refs.tabLabel.forEach((label) => label.$forceUpdate());
        });
      },

      handleAfterDeleteLeave () {
        this.deleteDialog.subTitle = '';
        this.curMember = {};
      },

      handleCancelDelete () {
        this.deleteDialog.visible = false;
      },

      fetchCustomTotal () {
        this.$nextTick(() => {
          const selectionCount = document.getElementsByClassName('bk-page-selection-count');
          if (this.$refs.groupMemberRef && selectionCount && selectionCount.length && selectionCount[0].children) {
            selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
          }
        });
      },

      resetPagination () {
        this.userOrOrgPagination = Object.assign(this.userOrOrgPagination, {
          current: 1,
          limit: 10
        });
        this.memberPagination = Object.assign(this.memberPagination, {
          current: 1,
          limit: 10
        });
      },

      getDefaultSelect () {
        const typeMap = {
          userOrgPerm: () => {
            const curData = this.groupTabList.find((item) => ['userOrgPerm'].includes(item.name));
            if (curData) {
              return curData.tableList.length > 0;
            }
            return false;
          },
          memberTemplate: () => {
            const curData = this.groupTabList.find((item) => ['memberTemplate'].includes(item.name));
            if (curData) {
              return curData.tableList.length > 0;
            }
            return false;
          }
        };
        return typeMap[this.tabActive];
      },

      getTableProps (payload) {
        const tabMap = {
          userOrgPerm: () => {
            return [
              { label: this.$t(`m.userGroup['用户/组织']`), prop: 'name' },
              { label: this.$t(`m.userGroupDetail['所属组织架构']`), prop: 'user_departments' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' },
              { label: this.$t(`m.common['加入时间']`), prop: 'created_time' },
              { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
            ];
          },
          memberTemplate: () => {
            return [
              { label: this.$t(`m.memberTemplate['人员模板']`), prop: 'template_name' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' },
              { label: this.$t(`m.common['加入时间']`), prop: 'created_time' },
              { label: this.$t(`m.common['操作-table']`), prop: 'operate' }
            ];
          }
        };
        return tabMap[payload]();
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 2) {
          return 'iam-table-cell-depart-cls';
        }
        return '';
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import '@/css/mixins/member-table.css';
.group-member-table {
  padding: 0 24px;
  &-tip {
    padding-bottom: 20px;
  }
  .batch-delete-btn {
    &.is-disabled {
      background-color: #ffffff;
    }
  }
  .group-member-tab {
    position: sticky;
    top: 0;
    left: 0;
    z-index: 9999;
    .group-member-button {
      display: flex;
      background-color: #F0F1F5;
      &-item {
        min-width: 96px;
        display: flex;
        align-items: center;
        font-size: 12px;
        background: #F0F1F5;
        color: #63656e;
        padding: 0 8px;
        border: 4px solid #F0F1F5;
        line-height: 24px;
        border-radius: 2px;
        cursor: pointer;
        &-count {
          min-width: 16px;
          height: 16px;
          line-height: 16px;
          padding: 0 8px;
          margin-left: 4px;
          border-radius: 8px;
          text-align: center;
          font-size: 12px;
          background-color: #ffffff;
        }
        &:last-child {
          margin-right: 0px;
        }
        &.is-active {
          color: #3a84ff;
          background: #ffffff;
          border-radius: 4px 4px 0 0;
          border: 4px solid #F0F1F5;
          .group-member-button-item-count {
            background-color: #E1ECFF;
            color: #3a84ff;
          }
          &:last-child {
            border-right: 4px solid #F0F1F5;
          }
        }
      }
    }
  }
  /deep/ .user-group-member-table {
  .member-template {
      background-color: #F0F1F5;
      color: #63656E;
      .iamcenter-renyuanmuban {
        color: #C4C6CC;
      }
      &:hover {
        color: #63656E;
        cursor: inherit;
      }
    }
  }
}
</style>

<style lang="postcss">
.resource-perm-delete-confirm {
  .popover-title {
    font-size: 16px;
    padding-bottom: 16px;
  }
  .popover-content {
    color: #63656e;
    .popover-content-item {
      display: flex;
      &-value {
        color: #313238;
        margin-left: 5px;
      }
    }
    &-tip {
      padding: 4px 0 16px 0;
    }
  }
  .popconfirm-operate {
    font-size: 0;
    button {
      min-width: 64px;
      margin-left: 0;
      margin-right: 8px;
      font-size: 12px;
    }
  }
}
</style>
