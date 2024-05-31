<template>
  <div class="iam-user-group-member group-member-table">
    <render-search>
      <div class="flex-between group-member-button">
        <div class="group-member-button-item">
          
        </div>
      </div>
      <div slot="right">
        <bk-input
          v-model="keyword"
          style="width: 400px"
          :placeholder="searchPlaceholder"
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
            :prop="item.prop">
            <template slot-scope="{ row }">

              <div
                v-if="row.type === 'user'"
                class="user"
                :title="`${row.id}(${row.name})`"
              >
                <Icon type="personal-user" />
                <span class="name" :style="{ maxWidth: curDisplaySet.customNameWidth }">{{ row.id }}</span>
                <span class="count" v-if="row.name">
                  {{ "(" + row.name + ")" }}
                </span>
              </div>
              <div v-else
                class="depart"
                :title="row.full_name"
              >
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
            :prop="item.prop">
            <template slot-scope="{ row }">
              <div class="member-template" :title="row.name" @click.stop="handleTempView(row)">
                <Icon type="renyuanmuban" />
                <span class="name">
                  {{ row.name || "--" }}
                </span>
              </div>
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
            :width="['memberTemplate'].includes(tabActive) ? 180 : 'auto'">
            <template slot-scope="{ row }">
              <template v-if="['memberTemplate'].includes(routeMode)">
                <bk-button
                  text
                  theme="primary"
                  @click="handleDelete(row)"
                >
                  {{ $t(`m.common['移除']`) }}
                </bk-button>
              </template>
              <template v-else>
                <bk-button
                  text
                  theme="primary"
                  @click="handleDelete(row)"
                >
                  {{ $t(`m.common['移除']`) }}
                </bk-button>
              </template>
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
      displaySet: {
        type: Object
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
        tabActive: 'userOrgPerm',
        groupTabList: [
          {
            name: 'userOrgPerm',
            label: this.$t(`m.userGroup['用户/组织']`),
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
      tabActive: {
        handler (newValue, oldValue) {
          this.curRouteMode = ['userOrgPerm'].includes(newValue) ? 'userGroupDetail' : newValue;
          if (this.routeMode) {
            this.curRouteMode = cloneDeep(this.routeMode);
          }
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
          const emptyField = this.groupTabList.find(item => item.name === this.tabActive);
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
          const emptyField = this.groupTabList.find(item => item.name === this.tabActive);
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
          multiple: async () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectList.push(row);
            } else {
              this.currentSelectList = this.currentSelectList.filter(
                (item) => item.id.toString() !== row.id.toString()
              );
            }
            await this.fetchCustomTotal();
          },
          all: async () => {
            const emptyField = this.groupTabList.find((item) => item.name === this.tabActive);
            if (emptyField) {
              const tableList = cloneDeep(emptyField.tableList);
              const selectGroups = this.currentSelectList.filter(
                (item) => !tableList.map((v) => v.id.toString()).includes(item.id.toString())
              );
              this.currentSelectList = [...selectGroups, ...payload];
              await this.fetchCustomTotal();
            }
          }
        };
        return typeMap[type]();
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
            )}${this.$t(`m.info['该成员将不再继承该组的权限']`)}${this.$t(`m.common['。']`)}`;
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
        if (this.curModeMap[this.curRouteMode]) {
          this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)}${this.$t(
            `m.common['【']`
          )}${payload.id}(${payload.name})${this.$t(`m.common['】']`)}${this.$t(
            `m.common['，']`
          )}${this.$t(`m.info['该用户/组织可能会失去关联用户组的权限']`)}${this.$t(`m.common['。']`)}`;
          this.deleteDialog.visible = true;
          this.curMember = Object.assign(
            {},
            {
              id: payload.id,
              type: ['memberTemplate'].includes(this.routeMode) ? payload.type : 'template'
            }
          );
        } else {
          this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)}${this.$t(
            `m.common['【']`
          )}${payload.id}(${payload.name})${this.$t(`m.common['】']`)}${this.$t(
            `m.common['，']`
          )}${this.$t(`m.info['该成员将不再继承该组的权限']`)}${this.$t(`m.common['。']`)}`;
          this.deleteDialog.visible = true;
          this.curMember = Object.assign(
            {},
            {
              id: payload.id,
              type: payload.type
            }
          );
        }
      },

      async handleSubmitDelete () {
        this.deleteDialog.loading = true;
        try {
          let url = 'userGroup/deleteUserGroupMember';
          const params = {
            id: this.id,
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
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.deleteDialog.loading = false;
          this.deleteDialog.visible = false;
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
            return this.groupTabList[0].tableList.length > 0;
          },
          memberTemplate: () => {
            return this.groupTabList[1].tableList.length > 0;
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
              { label: this.$t(`m.common['备注']`), prop: 'description' },
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
}
</style>
