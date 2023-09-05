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
          @on-expanded="handleExpanded(...arguments, item)"
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
            <bk-table
              v-if="!item.loading"
              :data="item.children"
              size="small"
              ref="permTableRef"
              ext-cls="perm-renewal-table"
              :outer-border="false"
              :header-border="false"
              :pagination="item.pagination"
              @page-change="pageChange(...arguments, item)"
              @page-limit-change="limitChange(...arguments, item)"
              @select="handlerChange(...arguments, index)"
              @select-all="handlerAllChange(...arguments, index)"
            >
              <bk-table-column type="selection" align="center" :selectable="getIsSelect" />
              <bk-table-column :label="$t(`m.renewal['即将过期的用户/组织']`)">
                <template slot-scope="{ row }">
                  <span>{{ row.id }}({{ row.name }})</span>
                </template>
              </bk-table-column>
              <bk-table-column :label="$t(`m.common['有效期']`)">
                <template slot-scope="{ row }">
                  <render-expire-display
                    :selected="currentSelectList.map((v) => v.$id).includes(row.$id)"
                    :renewal-time="expiredAt"
                    :cur-time="row.expired_at"
                  />
                </template>
              </bk-table-column>
              <bk-table-column :resizable="false" :label="$t(`m.common['操作']`)">
                <template slot-scope="{ row }">
                  <bk-button theme="primary" @click.stop="handleDelete(row, index)" text>
                    {{ $t(`m.common['删除']`) }}
                  </bk-button>
                </template>
              </bk-table-column>
            </bk-table>
          </div>
        </render-perm>
      </template>
      <template v-if="tableList.length < 1 && !tableLoading">
        <div class="empty-wrapper">
          <!-- <img src="@/images/empty-display.svg" alt="" /> -->
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
      {{ $t(`m.renewal['请选择即将过期的用户/组织']`) }}
    </p>
    <render-horizontal-block :label="$t(`m.renewal['续期时长']`)">
      <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" />
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
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { PERMANENT_TIMESTAMP, SIX_MONTH_TIMESTAMP, ONE_DAY_TIMESTAMP } from '@/common/constants';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import renderExpireDisplay from '@/components/render-renewal-dialog/display';
  import renderPerm from '@/components/render-perm';
  import DeleteDialog from '@/views/perm/components/iam-confirm-dialog';
  import { formatCodeData } from '@/common/util';

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
        tableList: [],
        tableLoading: false,
        isShowErrorTips: false,
        currentSelectList: [],
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        pageLoading: false,
        deleteDialog: {
          visible: false,
          title: this.$t(`m.dialog['确认移除']`),
          subTitle: '',
          loading: false
        },
        tableIndex: -1,
        curDelMember: {},
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      isEmpty () {
          return this.tableList.length < 1;
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    methods: {
      async fetchPageData () {
        await this.fetchData();
        await this.fetchDefaultCheck();
      },

      async fetchDefaultCheck () {
        if (this.pagination.current === 1) {
          for (let i = 0; i < this.tableList.length; i++) {
            const item = this.tableList[i];
            this.$set(item, 'expanded', true);
            this.$set(item, 'checkList', []);
            await this.fetchMembers(item, i);
            if (item.children && item.children.length) {
              item.children.forEach(subItem => {
                this.currentSelectList.push(subItem);
                item.checkList.push(subItem);
                this.$refs.permTableRef
                  && this.$refs.permTableRef[i].toggleRowSelection(subItem, true);
              });
            }
          }
          this.setExpiredAt();
        }
      },

      getIsSelect (item, index) {
        return item.parent.children.length > 0;
      },

      formatDisabled (payload) {
        const { checkList, children } = payload;
        return !(checkList.length && children.length);
      },

      handleBatchDelete (payload, index) {
        const { checkList } = payload;
        const deleteContent = checkList.length === 1
          ? `${this.$t(`m.common['【']`)}${checkList[0].id}(${checkList[0].name})${this.$t(`m.common['】']`)}${this.$t(`m.common['，']`)}${this.$t(`m.renewal['该成员在该用户组将不再存在续期']`)}`
          : `${checkList.length} ${this.$t(`m.common['位成员']`)}${this.$t(`m.common['，']`)}${this.$t(`m.renewal['这些成员在该用户组将不再存在续期']`)}`;
        this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)}${deleteContent}`;
        this.tableIndex = index;
        this.curDelMember = {};
        this.deleteDialog.visible = true;
      },

      handleDelete (payload, index) {
        this.deleteDialog.subTitle = `${this.$t(`m.common['移除']`)}${this.$t(`m.common['【']`)}${payload.id}(${payload.name})${this.$t(`m.common['】']`)}${this.$t(`m.common['，']`)}${this.$t(`m.renewal['该成员在该用户组将不再存在续期']`)}`;
        this.curDelMember = Object.assign({}, {
          id: payload.id,
          type: payload.type
        });
        this.tableIndex = index;
        this.deleteDialog.visible = true;
      },

      handleAfterDeleteLeave () {
        this.deleteDialog.subTitle = '';
        this.curDelMember = {};
      },

      hideCancelDelete () {
        this.deleteDialog.visible = false;
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
          if (currentRoleId && source === 'email') {
            params.hidden = false;
          }
          const { code } = await this.$store.dispatch('userGroup/deleteUserGroupMember', params);
          if (code === 0) {
            this.messageSuccess(this.$t(`m.info['移除成功']`), 3000);
            this.currentSelectList = [];
            this.tableList[this.tableIndex].checkList = [];
            this.pagination.current = 1;
            this.tableIndex = -1;
            await this.fetchData(true);
          }
        } catch (e) {
          console.error(e);
          this.fetchErrorMsg(e);
        } finally {
          this.deleteDialog.loading = false;
          this.deleteDialog.visible = false;
        }
      },

      async fetchMembers (item) {
        item.loading = true;
        try {
          const params = {
            limit: item.pagination.limit,
            offset: item.pagination.limit * (item.pagination.current - 1),
            id: item.id
          };
          const { current_role_id: currentRoleId, source } = this.$route.query;
          if (currentRoleId && source === 'email') {
            params.hidden = false;
          }
          const { data } = await this.$store.dispatch('renewal/getExpireSoonGroupMembers', params);
          this.$set(item, 'children', []);
          item.pagination.count = data.count || 0;
          item.children.splice(0, item.children.length, ...(data.results || []));
          item.children.forEach((sub) => {
            sub.$id = `${item.id}${sub.type}${sub.id}`;
            sub.parent = item;
            sub.parent_id = item.id;
            sub.parent_type = 'group';
          });
        } catch (e) {
          console.error(e);
          this.fetchErrorMsg(e);
        } finally {
          item.loading = false;
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
          if (currentRoleId && source === 'email') {
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch('renewal/getExpiredGroups', params);
          const total = data.count || 0;
          this.pagination.count = Math.ceil(total / this.pagination.limit);
          this.emptyData = formatCodeData(code, this.emptyData, total === 0);
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.tableList.forEach(async (item, index) => {
            this.$set(item, 'checkList', []);
            this.$set(item, 'children', []);
            this.$set(item, 'loading', false);
            this.$set(item, 'expanded', false);
            this.$set(item, 'pagination', {
              current: 1,
              limit: 10,
              count: 0
            });
            item.currentBackup = 1;
            if (index === 0) {
              this.$set(item, 'expanded', true);
              await this.fetchMembers(item);
            }
          });
        } catch (e) {
          console.error(e);
          this.fetchErrorMsg(e);
        } finally {
          this.tableLoading = false;
        }
      },

      async handleExpanded (payload, item) {
        item.pagination.current = 1;
        item.pagination.limit = 10;
        item.pagination.count = 0;
        await this.fetchMembers(item);
      },

      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.fetchData(true);
      },

      handleLimitChange (currentLimit, prevLimit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: currentLimit });
        this.fetchData(true);
      },

      pageChange (page, payload) {
        if (payload.currentBackup === page) {
          return;
        }
        payload.pagination.current = page;
        payload.currentBackup = page;
        this.fetchMembers(payload);
      },

      limitChange (currentLimit, prevLimit, payload) {
        payload.pagination = Object.assign(payload.pagination, { current: 1, limit: currentLimit });
        this.fetchMembers(payload);
      },

      setExpiredAt () {
        const getTimestamp = (payload) => {
          if (this.expiredAt === PERMANENT_TIMESTAMP) {
            return this.expiredAt;
          }
          if (payload < this.user.timestamp) {
            return this.user.timestamp + this.expiredAt;
          }
          return payload + this.expiredAt;
        };
        this.currentSelectList.forEach((item) => {
          // 因默认全选导致当前时间戳累加，这里重新命名一个变量，避免跟其他交互冲突
          item.expired_at_new = getTimestamp(item.expired_at);
        });
      },

      handlerAllChange (selection, index) {
        this.isShowErrorTips = false;
        this.currentSelectList = _.cloneDeep(selection);
        this.tableList[index].checkList = _.cloneDeep(selection);
        this.setExpiredAt();
      },

      handlerChange (selection, row, index) {
        this.isShowErrorTips = false;
        this.currentSelectList = _.cloneDeep(selection);
        this.tableList[index].checkList = _.cloneDeep(selection);
        this.setExpiredAt();
      },

      handleDeadlineChange (payload) {
        this.expiredAt = payload || ONE_DAY_TIMESTAMP;
        this.setExpiredAt();
      },

      async handleSubmit () {
        if (this.currentSelectList.length < 1) {
          this.isShowErrorTips = true;
          return;
        }
        this.submitLoading = true;
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
        if (currentRoleId && source === 'email') {
          params.hidden = false;
        }
        try {
          await this.$store.dispatch('renewal/roleGroupsRenewal', params);
          this.messageSuccess(this.$t(`m.renewal['批量申请提交成功']`), 3000);
          this.$router.push({
            name: 'userGroup'
          });
        } catch (e) {
          console.error(e);
          this.fetchErrorMsg(e);
        } finally {
          this.submitLoading = false;
        }
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
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 10 });
        this.fetchData(true);
      }
    }
  };
</script>
<style lang="postcss">
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
  .group-member-renewal-table-wrapper {
    min-height: 200px;
    margin-top: 16px;
    .perm-renewal-table {
      border: none;
    }
  }
  .error-tips {
    position: relative;
    top: -10px;
    font-size: 12px;
    color: #ea3636;
  }
}
</style>
