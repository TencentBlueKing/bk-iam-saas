<template>
  <smart-action class="iam-role-group-perm-renewal-wrapper">
    <div class="group-content-wrapper" v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
      <template v-if="!tableLoading">
        <render-perm
          v-for="(item, index) in tableList"
          :key="item.id"
          :expanded.sync="item.expanded"
          :ext-cls="index > 0 ? 'group-perm-renewal-ext-cls' : ''"
          :class="index === tableList.length - 1 ? 'group-perm-renewal-cls' : ''"
          :title="item.name"
          @on-expanded="handleExpanded(...arguments, item, index)"
        >
          <render-search>
            <bk-button :disabled="formatDisabled(item)" @click="handleBatchDelete(item, index)">
              {{ $t(`m.common['批量移除']`) }}
            </bk-button>
          </render-search>
          <div
            class="group-member-renewal-table-wrapper"
            v-bkloading="{ isLoading: item.loading, opacity: 1 }"
          >
            <div class="group-renewal-member-wrapper">
              <bk-tab
                ref="tabRef"
                type="unborder-card"
                ext-cls="group-tab-wrapper"
                :key="tabKey"
                :active.sync="item.tabActive"
                @tab-change="handleTabChange(item, index, ...arguments)"
              >
                <bk-tab-panel v-for="panel in item.groupTabList" v-bind="panel" :key="panel.name">
                  <template slot="label">
                    <span class="panel-name">{{ panel.label }}</span>
                    <span
                      :class="['panel-count', { 'panel-count-active': item.tabActive === panel.name }]"
                    >
                      {{ panel.pagination.count }}
                    </span>
                  </template>
                </bk-tab-panel>
              </bk-tab>
              <bk-table
                size="small"
                ref="permTableRef"
                ext-cls="perm-renewal-table"
                :outer-border="false"
                :header-border="false"
                :data="getTableList(item)"
                :data-custom-key="`${item.name}&${item.id}-${index}`"
                :pagination="formatPagination(item)"
                @page-change="handleTablePageChange(...arguments, item)"
                @page-limit-change="handleTableLimitChange(...arguments, item)"
                @select="handlerChange(...arguments, index)"
                @select-all="handlerAllChange(...arguments, index)"
                v-bkloading="{ isLoading: item.tableLoading, opacity: 1 }"
              >
                <bk-table-column type="selection" align="center" :selectable="getDefaultSelect" />
                <template v-for="tableItem in item.tableProps">
                  <template v-if="tableItem.prop === 'name'">
                    <bk-table-column
                      :key="tableItem.prop"
                      :label="tableItem.label"
                      :prop="tableItem.prop">
                      <template slot-scope="{ row }">
                        <span v-if="['user'].includes(row.type)">{{ row.id }}({{ row.name }})</span>
                        <span v-if="['depart', 'department'].includes(row.type)">{{ row.name }}({{ row.id }})</span>
                      </template>
                    </bk-table-column>
                  </template>
                  <template v-else-if="tableItem.prop === 'template_name'">
                    <bk-table-column
                      :key="tableItem.prop"
                      :label="tableItem.label"
                      :prop="tableItem.prop">
                      <template slot-scope="{ row }">
                        <div class="member-template" :title="row.name">
                          <Icon type="renyuanmuban" />
                          <span class="name">
                            {{ row.name || "--" }}
                          </span>
                        </div>
                      </template>
                    </bk-table-column>
                  </template>
                  <template
                    v-else-if="tableItem.prop === 'expired_at_display'"
                  >
                    <bk-table-column
                      :key="tableItem.prop"
                      :label="tableItem.label"
                      :prop="tableItem.prop">
                      <template slot-scope="{ row }">
                        <render-expire-display
                          :selected="currentSelectList.map((v) => v.$id).includes(row.$id)"
                          :renewal-time="expiredAt"
                          :cur-time="row.expired_at"
                        />
                      </template>
                    </bk-table-column>
                  </template>
                  <template v-else-if="tableItem.prop === 'description'">
                    <bk-table-column
                      :key="tableItem.prop"
                      :label="tableItem.label"
                      :prop="tableItem.prop">
                      <template slot-scope="{ row }">
                        <span :title="row.description">
                          {{ row.description || '--' }}
                        </span>
                      </template>
                    </bk-table-column>
                  </template>
                  <template v-else-if="tableItem.prop === 'created_time'">
                    <bk-table-column
                      :key="tableItem.prop"
                      :label="tableItem.label"
                      :prop="tableItem.prop">
                      <template slot-scope="{ row }">
                        <span :title="row.created_time.replace(/T/, ' ')">
                          {{ row.created_time.replace(/T/, " ") }}
                        </span>
                      </template>
                    </bk-table-column>
                  </template>
                  <template v-else-if="tableItem.prop === 'operate'">
                    <bk-table-column
                      :key="tableItem.prop"
                      :label="tableItem.label"
                      :prop="tableItem.prop"
                      fixed="right"
                    >
                      <template slot-scope="{ row }">
                        <bk-button theme="primary" text @click.stop="handleDelete(row, index)">
                          {{ $t(`m.common['删除']`) }}
                        </bk-button>
                      </template>
                    </bk-table-column>
                  </template>
                </template>
                <template slot="empty">
                  <ExceptionEmpty />
                </template>
              </bk-table>
            </div>
          </div>
        </render-perm>
      </template>
      <template v-if="tableList.length < 1 && !tableLoading">
        <div class="empty-wrapper">
          <ExceptionEmpty
            :type="emptyData.type"
            :empty-text="emptyData.text"
            :tip-text="emptyData.tip"
            :tip-type="emptyData.tipType"
            @on-refresh="handleEmptyRefresh"
          />
        </div>
      </template>
    </div>
    <div v-if="pagination.count" style="margin: 20px 0">
      <bk-pagination
        size="small"
        align="right"
        :current.sync="pagination.current"
        :count="pagination.count"
        :limit="pagination.limit"
        @change="handlePageChange"
        @limit-change="handleLimitChange"
      >
      </bk-pagination>
    </div>
    <p class="error-tips" v-if="isShowErrorTips">
      {{ $t(`m.renewal['请选择用户/组织或人员模板']`) }}
    </p>
    <render-horizontal-block :label="$t(`m.renewal['续期时长']`)">
      <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" />
      <p class="error-tips expired-at-error" v-if="isShowExpiredError">{{ $t(`m.userOrOrg['请选择续期时长']`) }}</p>
    </render-horizontal-block>
    <div slot="action">
      <bk-button theme="primary" disabled v-if="isEmpty">
        <span
          v-bk-tooltips="{
            content: $t(`m.renewal['暂无将过期的权限']`),
            extCls: 'iam-tooltips-cls'
          }"
        >
          {{ $t(`m.common['提交']`) }}
        </span>
      </bk-button>
      <bk-button theme="primary" :loading="submitLoading" v-else @click="handleSubmit">
        {{ $t(`m.common['提交']`) }}
      </bk-button>
      <bk-button style="margin-left: 6px" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
    </div>

    <delete-dialog
      :show.sync="deleteDialog.visible"
      :loading="deleteDialog.loading"
      :title="deleteDialog.title"
      :sub-title="deleteDialog.subTitle"
      @on-after-leave="handleAfterDeleteLeave"
      @on-cancel="hideCancelDelete"
      @on-submit="handleSubmitDelete" />
            
  </smart-action>
</template>
<script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { PERMANENT_TIMESTAMP, SIX_MONTH_TIMESTAMP } from '@/common/constants';
  import { formatCodeData, getNowTimeExpired, xssFilter } from '@/common/util';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import renderExpireDisplay from '@/components/render-renewal-dialog/display';
  import renderPerm from '@/components/render-perm';
  import DeleteDialog from '@/views/perm/components/iam-confirm-dialog';

  export default {
    name: '',
    components: {
      IamDeadline,
      renderExpireDisplay,
      renderPerm,
      DeleteDialog
    },
    data () {
      return {
        expiredAt: SIX_MONTH_TIMESTAMP,
        submitLoading: false,
        tableLoading: false,
        isShowErrorTips: false,
        isShowExpiredError: false,
        tableList: [],
        currentSelectList: [],
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        tableIndex: -1,
        pageLoading: false,
        deleteDialog: {
          visible: false,
          title: this.$t(`m.dialog['确认移除']`),
          subTitle: '',
          loading: false
        },
        tableProps: [],
        groupTabList: [
          {
            name: 'userOrgPerm',
            label: this.$t(`m.userGroup['用户/组织']`),
            empty: 'emptyOrgData',
            pagination: {
              current: 1,
              limit: 10,
              count: 0
            },
            children: []
          },
          {
            name: 'memberTemplate',
            label: this.$t(`m.nav['人员模板']`),
            empty: 'emptyTempData',
            pagination: {
              current: 1,
              limit: 10,
              count: 0
            },
            children: []
          }
        ],
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        curDelMember: {},
        tabKey: 'tabKey'
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      isEmpty () {
        return this.tableList.length < 1;
      },
      formatPagination () {
        return (payload) => {
          const tabData = payload.groupTabList.find((item) => item.name === payload.tabActive);
          if (tabData) {
            return tabData.pagination;
          }
          return { current: 1, limit: 10, count: 0 };
        };
      },
      getTableList () {
        return (payload) => {
          const tabData = payload.groupTabList.find((item) => item.name === payload.tabActive);
          if (tabData) {
            return tabData.children;
          }
          return [];
        };
      }
    },
    methods: {
      async fetchPageData () {
        await this.fetchData();
        await this.fetchDefaultCheck();
      },

      async fetchDefaultCheck () {
        for (let i = 0; i < this.tableList.length; i++) {
          const item = this.tableList[i];
          this.$set(item, 'expanded', true);
          this.$set(item, 'checkList', []);
          this.$set(item, 'tabActive', 'userOrgPerm');
          this.$set(item, 'groupTabList', cloneDeep(this.groupTabList));
          await Promise.all([this.fetchMembers(item), this.fetchGroupSubjectTemplate(item)]).then(() => {
            if (item.groupTabList && item.groupTabList.length) {
              const childList = item.groupTabList.map((v) => v.children || []).flat(Infinity);
              const isExistUserOrg = childList.find((v) => ['user', 'department'].includes(v.type));
              const isExistTemp = childList.find((v) => ['template'].includes(v.type));
              if (!isExistUserOrg && isExistTemp) {
                item.tabActive = 'memberTemplate';
                this.$set(item, 'tableProps', this.getTableProps('memberTemplate'));
              }
              this.$nextTick(() => {
                childList && childList.forEach(subItem => {
                  item.checkList.push(subItem);
                  if (this.$refs.permTableRef && this.$refs.permTableRef.length) {
                    this.$refs.permTableRef[i].toggleRowSelection(subItem, true);
                    this.fetchCustomTotal(i);
                  }
                });
              });
            }
          });
        }
        this.currentSelectList = this.tableList.map((item) => item.checkList).flat(Infinity);
      },

      async fetchMembers (item) {
        const tabData = item.groupTabList.find((v) => ['userOrgPerm'].includes(v.name));
        if (!tabData) {
          return;
        }
        item.loading = true;
        try {
          const params = {
            limit: tabData.pagination.limit,
            offset: tabData.pagination.limit * (tabData.pagination.current - 1),
            id: item.id
          };
          const { current_role_id: currentRoleId, source } = this.$route.query;
          if (currentRoleId && ['email', 'notification'].includes(source)) {
            params.hidden = false;
          }
          const { data } = await this.$store.dispatch('renewal/getExpireSoonGroupMembers', params);
          tabData.pagination.count = data.count || 0;
          tabData.children = [...data.results || []];
          tabData.children.forEach((sub) => {
            sub.$id = `${item.id}${sub.type}${sub.id}`;
            sub.parent = item;
            sub.parent_id = item.id;
            sub.parent_type = 'group';
          });
        } catch (e) {
          this.fetchErrorMsg(e);
        } finally {
          item.loading = false;
          this.fetchRefreshSelectList(item);
        }
      },

      // 获取用户组关联模板列表
      async fetchGroupSubjectTemplate (item) {
        const tabData = item.groupTabList.find((v) => ['memberTemplate'].includes(v.name));
        if (!tabData) {
          return;
        }
        item.tableLoading = true;
        try {
          const params = {
            limit: tabData.pagination.limit,
            offset: tabData.pagination.limit * (tabData.pagination.current - 1),
            id: item.id,
            expire_soon: true
          };
          const { current_role_id: currentRoleId, source } = this.$route.query;
          if (currentRoleId && ['email', 'notification'].includes(source)) {
            params.hidden = false;
          }
          const { data } = await this.$store.dispatch('memberTemplate/getGroupSubjectTemplate', params);
          tabData.pagination.count = data.count || 0;
          tabData.children = [...data.results || []];
          tabData.children.forEach((sub) => {
            sub.$id = `${item.id}template${sub.id}`;
            sub.parent = item;
            sub.parent_id = item.id;
            sub.parent_type = 'group';
            sub.type = 'template';
          });
        } catch (e) {
          this.fetchErrorMsg(e);
        } finally {
          item.tableLoading = false;
          this.fetchRefreshSelectList(item);
        }
      },

      async fetchData (isLoading = false) {
        this.tableLoading = isLoading;
        try {
          const params = {
            limit: this.pagination.limit,
            offset: this.pagination.limit * (this.pagination.current - 1)
          };
          const { current_role_id: currentRoleId, source } = this.$route.query;
          if (currentRoleId && ['email', 'notification'].includes(source)) {
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch('renewal/getExpiredGroups', params);
          const total = data.count || 0;
          this.pagination.count = Math.ceil(total / this.pagination.limit);
          this.emptyData = formatCodeData(code, this.emptyData, total === 0);
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.tableList.forEach(async (item, index) => {
            this.$set(item, 'checkList', []);
            this.$set(item, 'groupTabList', cloneDeep(this.groupTabList));
            this.$set(item, 'loading', false);
            this.$set(item, 'tableLoading', false);
            this.$set(item, 'expanded', false);
            this.$set(item, 'tabActive', 'userOrgPerm');
            this.$set(item, 'tableProps', this.getTableProps(item.tabActive));
            item.currentBackup = 1;
            if (index === 0) {
              this.$set(item, 'expanded', true);
            }
          });
          this.handleRefreshTabCount();
        } catch (e) {
          this.fetchErrorMsg(e);
        } finally {
          this.tableLoading = false;
        }
      },

      async handleTabChange (row, index, payload) {
        row = Object.assign(row, { tabActive: payload, tableProps: this.getTableProps(payload) });
        this.getTableAllCustom(row, index);
      },

      async getTableAllCustom (row, index) {
        await this.handleRefreshTab(row);
        this.fetchRefreshSelectList(row);
        this.fetchCustomTotal(index);
      },

      getDefaultSelect (item) {
        const curData = item.parent.groupTabList.find((v) => v.name === item.parent.tabActive);
        if (curData) {
          return curData.children && curData.children.length > 0;
        }
        return false;
      },

      getTableProps (payload) {
        const tabMap = {
          userOrgPerm: () => {
            return [
              { label: this.$t(`m.userGroup['用户/组织']`), prop: 'name' },
              { label: this.$t(`m.common['有效期']`), prop: 'expired_at_display' },
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

      formatDisabled (payload) {
        const { checkList } = payload;
        return !checkList.length;
      },

      handleBatchDelete (payload, index) {
        const { checkList } = payload;
        const userOrgList = checkList.filter((item) => ['user', 'department'].includes(item.type));
        const tempList = checkList.filter((item) => ['template'].includes(item.type));
        let userOrgTip = '';
        let tempTip = '';
        let commaTip = '';
        if (userOrgList.length) {
          userOrgTip = `${this.$t(`m.common['移除']`)} ${userOrgList.length} ${this.$t(`m.common['位成员']`)}${this.$t(`m.common['，']`)}${this.$t(`m.renewal['这些成员在该用户组将不再存在续期']`)}`;
        }
        if (tempList.length) {
          tempTip = `${this.$t(`m.common['移除']`)} ${tempList.length} ${this.$t(`m.common['个人员模板']`)}${this.$t(`m.common['，']`)}${this.$t(`m.info['这些人员模板关联的该用户组将不再存在续期']`)}${this.$t(`m.common['。']`)}`;
        }
        if (userOrgList.length > 0 && tempList.length > 0) {
          commaTip = this.$t(`m.common['。']`);
        }
        this.deleteDialog.subTitle = `${userOrgTip}${commaTip}${tempTip}`;
        this.tableIndex = index;
        this.curDelMember = {};
        this.deleteDialog.visible = true;
      },

      handleDelete (payload, index) {
        this.tableIndex = index;
        const { tabActive } = this.tableList[index];
        const typeMap = {
          userOrgPerm: () => {
            this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)}${this.$t(`m.common['【']`)}${payload.id}(${payload.name})${this.$t(`m.common['】']`)}${this.$t(`m.common['，']`)}${this.$t(`m.renewal['该成员在该用户组将不再存在续期']`)}`;
            this.curDelMember = Object.assign({}, {
              id: payload.id,
              type: payload.type
            });
            this.deleteDialog.visible = true;
          },
          memberTemplate: () => {
            this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)}${this.$t(`m.common['【']`)}${payload.name}${this.$t(`m.common['】']`)}${this.$t(
              `m.common['，']`)}${this.$t(`m.info['人员模板关联的该用户组将不再存在续期']`)}${this.$t(`m.common['。']`)}`;
            this.curDelMember = Object.assign({}, {
              id: payload.id,
              type: 'template'
            });
            this.deleteDialog.visible = true;
          }
        };
        return typeMap[tabActive]();
      },

      handleAfterDeleteLeave () {
        this.deleteDialog.subTitle = '';
        this.curDelMember = {};
      },

      hideCancelDelete () {
        this.deleteDialog.visible = false;
      },

      handleRefreshTabCount () {
        this.$nextTick(() => {
          if (this.$refs.tabRef && this.$refs.tabRef.length) {
            this.$refs.tabRef.forEach((item) => {
              item.$refs.tabLabel.forEach((label) => label.$forceUpdate());
            });
          }
        });
      },
      
      fetchCustomTotal (index) {
        const { checkList, tabActive, name, id } = this.tableList[index];
        this.$nextTick(() => {
          const selectionCount = document.getElementsByClassName('bk-page-selection-count');
          let tableIndex = -1;
          if (this.$refs.permTableRef && this.$refs.permTableRef.length) {
            tableIndex = this.$refs.permTableRef.findIndex((v) => v.$el.dataset.customKey === `${name}&${id}-${index}`);
          }
          if (
            selectionCount
            && selectionCount.length
            && selectionCount[tableIndex]
            && selectionCount[tableIndex].children
          ) {
            const typeMap = {
              userOrgPerm: () => {
                const list = checkList.filter((item) => ['user', 'department'].includes(item.type));
                selectionCount[tableIndex].children[0].innerHTML = xssFilter(list.length);
              },
              memberTemplate: () => {
                const list = checkList.filter((item) => ['template'].includes(item.type));
                selectionCount[tableIndex].children[0].innerHTML = xssFilter(list.length);
              }
            };
            return typeMap[tabActive]();
          }
        });
      },

      fetchRefreshSelectList (payload) {
        const tableIndex = this.tableList.findIndex((item) => item.id === payload.id);
        const emptyField = payload.groupTabList.find(item => item.name === payload.tabActive);
        if (emptyField) {
          this.$nextTick(() => {
            const selectList = payload.checkList.map((item) => String(item.id));
            let curTableRef = null;
            const checkList = payload.checkList.map((v) => `${v.id}&${v.name}`);
            if (this.$refs.permTableRef && this.$refs.permTableRef.length) {
              curTableRef = this.$refs.permTableRef.find((v) => v.$el.dataset.customKey === `${payload.name}&${payload.id}-${tableIndex}`);
            }
            emptyField.children.forEach((item) => {
              if (
                selectList.includes(String(item.id))
                && this.$refs.permTableRef.length
                && tableIndex > -1
                && curTableRef
              ) {
                if (curTableRef && checkList.includes(`${item.id}&${item.name}`)) {
                  curTableRef.toggleRowSelection(item, true);
                }
              }
            });
            if (!payload.checkList.length && this.$refs.permTableRef.length && tableIndex > -1 && curTableRef) {
              curTableRef.clearSelection();
            }
            this.handleRefreshTabCount();
          });
        }
      },

      async handleSubmitDelete () {
        this.deleteDialog.loading = true;
        try {
          const { id, checkList } = this.tableList[this.tableIndex];
          const params = {
            id,
            members: Object.keys(this.curDelMember).length > 0
              ? [this.curDelMember]
              : checkList.map(({ id, type }) => ({ id, type }))
          };
          const { current_role_id: currentRoleId, source } = this.$route.query;
          if (currentRoleId && ['email', 'notification'].includes(source)) {
            params.hidden = false;
          }
          const { code } = await this.$store.dispatch('userGroup/deleteUserGroupMember', params);
          if (code === 0) {
            this.messageSuccess(this.$t(`m.info['移除成功']`), 3000);
            this.currentSelectList = [];
            this.pagination.current = 1;
            this.tableList[this.tableIndex] = Object.assign(this.tableList[this.tableIndex], {
              expanded: true,
              checkList: []
            });
            this.fetchCustomTotal(this.tableIndex);
            await Promise.all([
              this.fetchMembers(this.tableList[this.tableIndex]),
              this.fetchGroupSubjectTemplate(this.tableList[this.tableIndex])
            ]);
          }
        } catch (e) {
          this.fetchErrorMsg(e);
        } finally {
          this.deleteDialog.loading = false;
          this.deleteDialog.visible = false;
          this.tableIndex = -1;
        }
      },

      async handleExpanded (isExpand, payload, index) {
        if (isExpand) {
          this.$nextTick(() => {
            let curTableRef = null;
            const checkList = payload.checkList.map((item) => `${item.id}&${item.name}`);
            if (this.$refs.permTableRef && this.$refs.permTableRef.length) {
              curTableRef = this.$refs.permTableRef.find((v) => v.$el.dataset.customKey === `${payload.name}&${payload.id}-${index}`);
            }
            payload.groupTabList && payload.groupTabList.forEach((item) => {
              if (item.name === payload.tabActive) {
                item.children && item.children.forEach((sub) => {
                  if (curTableRef && checkList.includes(`${sub.id}&${sub.name}`)) {
                    curTableRef.toggleRowSelection(sub, true);
                  }
                });
              }
            });
          });
        }
      },

      async handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        await this.fetchPageData();
      },

      async handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit });
        await this.fetchPageData();
      },

      async handleRefreshTab (payload) {
        payload.currentBackup = 1;
        const tabData = payload.groupTabList.find((v) => v.name === payload.tabActive);
        if (tabData) {
          tabData.pagination = Object.assign(tabData.pagination, { current: 1, limit: 10 });
        }
        const tabMap = {
          userOrgPerm: async () => {
            await this.fetchMembers(payload);
          },
          memberTemplate: async () => {
            await this.fetchGroupSubjectTemplate(payload);
          }
        };
        return tabMap[payload.tabActive]();
      },

      handleTablePageChange (page, prev, payload) {
        if (payload.currentBackup === page) {
          return;
        }
        const curData = payload.groupTabList.find((v) => v.name === payload.tabActive);
        if (curData) {
          payload.currentBackup = page;
          curData.pagination.current = page;
          const typeMap = {
            userOrgPerm: () => {
              this.fetchMembers(payload);
            },
            memberTemplate: () => {
              this.fetchGroupSubjectTemplate(payload);
            }
          };
          typeMap[curData.name]();
        }
      },

      handleTableLimitChange (limit, prevLimit, payload) {
        const curData = payload.groupTabList.find((v) => v.name === payload.tabActive);
        if (curData) {
          curData.pagination = Object.assign(curData.pagination, { current: 1, limit });
          const typeMap = {
            userOrgPerm: () => {
              this.fetchMembers(payload);
            },
            memberTemplate: () => {
              this.fetchGroupSubjectTemplate(payload);
            }
          };
          typeMap[curData.name]();
        }
      },

      setExpiredAt () {
        const getTimestamp = (payload) => {
          if (this.expiredAt === PERMANENT_TIMESTAMP) {
            return this.expiredAt;
          }
          if (payload < getNowTimeExpired()) {
            return getNowTimeExpired() + this.expiredAt;
          }
          return payload + this.expiredAt;
        };
        this.currentSelectList.forEach((item) => {
          // 因默认全选导致当前时间戳累加，这里重新命名一个变量，避免跟其他交互冲突
          item.expired_at_new = getTimestamp(item.expired_at);
        });
      },

      fetchSelectedGroups (type, index, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.tableList[index].checkList.push(row);
            } else {
              this.tableList[index].checkList = this.tableList[index].checkList.filter(
                (item) => item.id.toString() !== row.id.toString()
              );
            }
            this.currentSelectList = this.tableList.map((item) => item.checkList).flat(Infinity);
          },
          all: () => {
            const { groupTabList, tabActive } = this.tableList[index];
            const emptyField = groupTabList.find((item) => item.name === tabActive);
            if (emptyField) {
              const tableList = cloneDeep(emptyField.children);
              const selectGroups = this.tableList[index].checkList.filter(
                (item) => !tableList.map((v) => String(v.id)).includes(String(item.id))
              );
              this.tableList[index].checkList = [...selectGroups, ...payload];
              this.currentSelectList = this.tableList.map((item) => item.checkList).flat(Infinity);
              this.fetchCustomTotal(index);
            }
          }
        };
        return typeMap[type]();
      },

      handlerAllChange (selection, index) {
        this.isShowErrorTips = false;
        this.fetchSelectedGroups('all', index, selection);
      },

      handlerChange (selection, row, index) {
        this.isShowErrorTips = false;
        this.fetchSelectedGroups('multiple', index, selection, row);
      },

      // 同步更新每个表格的续期时间
      handleGetRenewalTime () {
        this.currentSelectList = this.tableList.map((item) => item.checkList).flat(Infinity);
        this.setExpiredAt();
      },

      handleDeadlineChange (payload) {
        if (payload) {
          this.isShowExpiredError = false;
        }
        this.expiredAt = payload;
        this.handleGetRenewalTime();
      },

      async handleSubmit () {
        if (this.currentSelectList.length < 1) {
          this.isShowErrorTips = true;
          return;
        }
        if (!this.expiredAt) {
          this.isShowExpiredError = true;
          return;
        }
        this.submitLoading = true;
        this.handleGetRenewalTime();
        const params = {
          members: this.currentSelectList.map(({ type, id, parent_type, parent_id, expired_at_new }) => ({
            type,
            id,
            parent_type,
            parent_id,
            expired_at: expired_at_new
          }))
        };
        const { current_role_id: currentRoleId, source } = this.$route.query;
        if (currentRoleId && ['email', 'notification'].includes(source)) {
          params.hidden = false;
        }
        console.log(params, '参数');
        try {
          await this.$store.dispatch('renewal/roleGroupsRenewal', params);
          this.messageSuccess(this.$t(`m.renewal['批量申请提交成功']`), 3000);
          this.$router.push({
            name: 'userGroup'
          });
        } catch (e) {
          this.fetchErrorMsg(e);
        } finally {
          this.submitLoading = false;
        }
      },

      resetPagination (payload) {
        payload.currentBackup = 1;
        payload.groupTabList.forEach((item) => {
          item.pagination = Object.assign(item.pagination, {
            current: 1,
            limit: 10,
            count: 0,
            showTotalCount: true
          });
        });
      },

      fetchErrorMsg (payload) {
        this.messageAdvancedError(payload);
      },

      handleCancel () {
        this.$router.push({
          name: 'userGroup'
        });
      },

      handleEmptyRefresh () {
        this.fetchPageData();
      }
    }
  };
</script>
<style lang="postcss" scoped>
.iam-role-group-perm-renewal-wrapper {
  .group-content-wrapper {
    position: relative;
    min-height: 150px;
    .empty-wrapper {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      
    }
  }
  .group-perm-renewal-ext-cls {
    margin-top: 16px;
  }
  .group-perm-renewal-cls {
    margin-bottom: 16px;
  }
  /deep/.group-member-renewal-table-wrapper {
    min-height: 200px;
    margin-top: 16px;
    .perm-renewal-table {
      border: none;
      .bk-table-fixed,
      .bk-table-fixed-right {
        border-bottom: 0;
      }
    }
  }
  .error-tips {
    position: relative;
    top: -10px;
    font-size: 12px;
    color: #ea3636;
    &.expired-at-error {
      top: 4px;
    }
  }
  .member-template {
    padding: 4px 6px;
    width: max-content;
    color: #313238;
    i {
      color: #979ba5;
    }
  }
  /deep/ .group-renewal-member-wrapper {
    .group-tab-wrapper {
      margin-top: 16px;
      .bk-tab-section {
        display: none;
      }
      .panel-count {
        min-width: 16px;
        height: 16px;
        line-height: 16px;
        padding: 0 8px;
        border-radius: 8px;
        text-align: center;
        font-size: 12px;
        color: #979ba5;
        background-color: #f0f1f5;
        &-active {
          background-color: #e1ecff;
          color: #3a84ff;
        }
      }
    }
  }
}
</style>
