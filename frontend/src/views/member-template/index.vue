<template>
  <div class="iam-member-template-wrapper">
    <render-search>
      <div class="search_left">
        <bk-button theme="primary" @click="handleCreate">
          {{ $t(`m.common['新建']`) }}
        </bk-button>
        <bk-button :disabled="isBatchDisabled" @click="handleBatchAddMember">
          {{ $t(`m.common['批量添加成员']`) }}
        </bk-button>
      </div>
      <div slot="right">
        <IamSearchSelect
          style="width: 420px"
          :placeholder="$t(`m.memberTemplate['搜索模板名称、描述、创建人']`)"
          :data="searchData"
          :value="searchValue"
          :quick-search-method="quickSearchMethod"
          @on-change="handleSearch"
        />
      </div>
    </render-search>
    <bk-table
      ref="tableRef"
      size="small"
      ext-cls="member-template-table"
      :data="memberTemplateList"
      :max-height="tableHeight"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column type="selection" align="center" :selectable="getDefaultSelect" />
      <bk-table-column :label="$t(`m.memberTemplate['模板名称']`)" :sortable="true">
        <template slot-scope="{ row }">
          <span class="member-template-name" :title="row.name" @click="handleView(row)">
            {{ row.name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['描述']`)">
        <template slot-scope="{ row }">
          <span :title="row.description || ''">{{ row.description || "--" }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.memberTemplate['关联用户组']`)" :sortable="true">
        <template slot-scope="{ row }">
          <span :title="row.member_count">{{ row.member_count || "--" }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.memberTemplate['创建人']`)">
        <template slot-scope="{ row }">
          <span>{{ row.creator || "--" }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.memberTemplate['最近更新时间']`)" width="240">
        <template slot-scope="{ row }">
          <span :title="row.last_updated_time">{{ row.last_updated_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)" width="320" fixed="right">
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
            <bk-button
              theme="primary"
              text
              style="margin-left: 10px"
              @click="handleDelete(row)"
            >
              {{ $t(`m.common['删除']`) }}
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
    <AddMemberTemplateSlider
      :show.sync="isShowMemberSlider"
      @on-submit="handleTempSubmit"
    />

    <AddMemberDialog
      :show.sync="isShowAddMemberDialog"
      :is-batch="isBatch"
      :loading="memberDialogLoading"
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
  import { formatCodeData, getWindowHeight } from '@/common/util';
  import IamSearchSelect from '@/components/iam-search-select';
  import AddMemberTemplateSlider from './components/add-member-template-slider.vue';
  import AddMemberDialog from '@/views/group/components/iam-add-member.vue';
  export default {
    components: {
      IamSearchSelect,
      AddMemberTemplateSlider,
      AddMemberDialog
    },
    data () {
      return {
        memberTemplateList: [
          {
            name: '11',
            description: '4545',
            member_count: 2,
            creator: 'liu17',
            last_updated_time: '2023-11-03 15:53'
          }
        ],
        currentSelectList: [],
        searchList: [],
        searchValue: [],
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.memberTemplate['模板名称']`),
            default: true
          },
          {
            id: 'description',
            name: this.$t(`m.memberTemplate['描述']`),
            default: true
          },
          {
            id: 'creator',
            name: this.$t(`m.grading['创建人']`),
            default: true
          }
        ],
        searchParams: {},
        queryParams: {},
        pagination: {
          current: 1,
          limit: 10,
          count: 0
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        tableLoading: false,
        memberDialogLoading: false,
        isShowMemberSlider: false,
        isShowAddMemberDialog: false,
        curRole: '',
        curName: '',
        curId: 0
      };
    },
    computed: {
    ...mapGetters(['user', 'externalSystemId']),
    isBatchDisabled () {
      return this.currentSelectList.length === 0;
    },
    tableHeight () {
      return getWindowHeight() - 185;
    },
    isRatingManager () {
      return ['rating_manager', 'subset_manager'].includes(this.curRole);
    }
    },
    watch: {
      user: {
        handler (value) {
          this.curRole = value.role.type || 'staff';
        },
        immediate: true
      }
    },
    async created () {
      await this.fetchMemberTemplateList(true);
    },
    methods: {
      async fetchMemberTemplateList (tableLoading = false) {
        try {
          this.emptyData = formatCodeData(0, this.emptyData, true);
        } catch (e) {
          console.error(e);
        }
      },

      async handleSearch (payload, result) {
        this.searchParams = payload;
        this.searchList = result;
        this.emptyData.tipType = 'search';
        this.queryParams = Object.assign(this.queryParams, {
          current: 1,
          limit: 10
        });
        this.resetPagination();
        await this.fetchMemberTemplateList(true);
      },

      handleCreate () {
        this.isShowMemberSlider = true;
      },

      handleAddMember (payload) {
        const { id, name } = payload;
        this.curName = name;
        this.curId = id;
        this.isShowAddMemberDialog = true;
      },

      handleBatchAddMember () {
        const hasDisabledData = this.currentSelectList.filter((item) => item.readonly);
        if (hasDisabledData.length) {
          const disabledNames = hasDisabledData.map((item) => item.name);
          this.messageWarn(
            this.$t(`m.info['用户组为只读用户组不能添加成员']`, {
              value: `${this.$t(`m.common['【']`)}${disabledNames}${this.$t(
                `m.common['】']`
              )}`
            }),
            3000
          );
          return;
        }
        this.isBatch = true;
        this.isShowAddMemberDialog = true;
      },

      fetchSelectedGroups (type, payload, row) {
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectList.push(row);
            } else {
              this.currentSelectList = this.currentSelectList.filter(
                (item) => item.id !== row.id
              );
            }
            this.$nextTick(() => {
              const selectionCount = document.getElementsByClassName(
                'bk-page-selection-count'
              );
              if (this.$refs.sensitivityTableRef && selectionCount) {
                selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
              }
            });
          },
          all: () => {
            const tableList = _.cloneDeep(this.memberTemplateList);
            const selectGroups = this.currentSelectList.filter(
              (item) => !tableList.map((v) => v.id).includes(item.id)
            );
            this.currentSelectList = [...selectGroups, ...payload];
            this.$nextTick(() => {
              const selectionCount = document.getElementsByClassName(
                'bk-page-selection-count'
              );
              if (this.$refs.sensitivityTableRef && selectionCount) {
                selectionCount[0].children[0].innerHTML = this.currentSelectList.length;
              }
            });
          }
        };
        return typeMap[type]();
      },

      handlerAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handlerChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },

      handlePageChange (page) {
        this.pagination.current = page;
        this.fetchMemberTemplateList(true);
      },

      handleLimitChange (limit) {
        this.pagination = Object.assign(this.pagination, { limit });
        this.fetchMemberTemplateList(true);
      },

      async handleTemplateSubmit () {
        this.resetPagination();
        await this.fetchMemberTemplateList();
      },

      handleCancelAdd () {
        this.curId = 0;
        this.isShowAddMemberDialog = false;
      },

      async handleSubmitAdd (payload) {
        const { users, departments, expiredAt } = payload;
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
          params.group_ids = this.curSelectIds;
          delete params.id;
          fetchUrl = 'userGroup/batchAddUserGroupMember';
        }
        console.log('params', params);
        try {
          this.memberDialogLoading = true;
          await this.$store.dispatch(fetchUrl, params);
          this.isShowAddMemberDialog = false;
          this.messageSuccess(this.$t(`m.info['添加成员成功']`), 3000);
          this.fetchUserGroupList(true);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.memberDialogLoading = false;
        }
      },

      handleAddAfterClose () {
        this.curName = '';
        this.curId = 0;
      },

      handleEmptyClear () {
        this.handleEmptyRefresh();
      },

      handleEmptyRefresh () {
        this.queryParams = {};
        this.searchParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.resetPagination();
        this.fetchMemberTemplateList(true);
      },

      resetPagination () {
        this.pagination = Object.assign(
          {},
          {
            limit: 10,
            current: 1,
            count: 0
          }
        );
      },

      getDefaultSelect () {
        return this.memberTemplateList.length > 0;
      },

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-member-template-wrapper {
  .member-template-table {
    margin-top: 20px;
    .member-template-name {
      color: #3a84ff;
      cursor: pointer;
    }
  }
}
</style>
