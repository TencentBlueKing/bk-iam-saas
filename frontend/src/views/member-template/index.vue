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
      ext-cls="member-template-table"
      :size="setting.size"
      :data="memberTemplateList"
      :row-class-name="getRowClass"
      :max-height="tableHeight"
      :pagination="pagination"
      :dark-header="true"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
    >
      <bk-table-column type="selection" align="center" :selectable="getDefaultSelect" />
      <bk-table-column
        v-for="field in setting.selectedFields"
        :key="field.id"
        :label="field.label"
        :prop="field.id"
        :sortable="
          ['name', 'member_count', 'created_time', 'updated_time'].includes(field.id)
        "
      >
        <template slot-scope="{ row, $index }">
          <div v-if="['name'].includes(field.id)" class="member-template-name">
            <span
              :class="[
                'single-hide',
                { 'member-template-name-label': isAddRow && $index === 0 }
              ]"
              :title="row.name"
              @click="handleView(row)"
            >
              {{ row.name }}
            </span>
            <bk-tag
              v-if="isAddRow && $index === 0"
              theme="success"
              type="filled"
              class="member-template-name-tag"
            >
              new
            </bk-tag>
          </div>
          <div v-if="['member_count'].includes(field.id)">
            <span
              v-if="row.member_count"
              class="related-group-count"
              @click="handleViewGroup(row)"
            >
              {{ row.member_count }}
            </span>
            <span v-else>--</span>
          </div>
          <span v-if="!['name', 'member_count'].includes(field.id)">
            {{ row[field.id] || "--" }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作-table']`)" fixed="right">
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
      <bk-table-column type="setting" :tippy-options="{ zIndex: 3000 }">
        <bk-table-setting-content
          :fields="setting.fields"
          :selected="setting.selectedFields"
          :size="setting.size"
          @setting-change="handleSettingChange"
        />
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
      :show-limit="false"
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
  import { MEMBERS_TEMPLATE_FIELDS } from '@/common/constants';
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
            name: '11777757sasdddddddddddddddddd57',
            description: '4545',
            member_count: 2,
            creator: 'liu17',
            created_time: '2023-11-03 15:53',
            updated_by: 'liu17',
            updated_time: '2023-11-03 15:53'
          },
          {
            name: '11',
            description: '4545',
            member_count: 2,
            creator: 'liu17',
            created_time: '2023-11-03 15:53',
            updated_by: 'liu17',
            updated_time: '2023-11-03 15:53'
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
        setting: {
          fields: MEMBERS_TEMPLATE_FIELDS,
          selectedFields: MEMBERS_TEMPLATE_FIELDS.filter(
            (item) => !['created_time', 'updated_by'].includes(item.id)
          ),
          size: 'small'
        },
        tableLoading: false,
        memberDialogLoading: false,
        isShowMemberSlider: false,
        isShowAddMemberDialog: false,
        isAddRow: false,
        isBatch: false,
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

      getRowClass ({ row, rowIndex }) {
        if (rowIndex === 0 && this.isAddRow) {
          return 'member-template-table-add';
        }
        return '';
      },

      handleCreate () {
        this.isShowMemberSlider = true;
      },

      handleView () {},

      handleViewGroup () {},

      handleAddMember (payload) {
        console.log(payload, 525);
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

      handleSettingChange ({ fields, size }) {
        this.setting.size = size;
        this.setting.selectedFields = fields;
      },

      async handleTempSubmit () {
        this.isAddRow = true;
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
      display: flex;
      align-items: center;
      color: #3a84ff;
      cursor: pointer;
      &-label {
        max-width: calc(100% - 50px);
        word-break: break-all;
      }
      &-tag {
        background-color: #2dcb56;
        font-size: 10px;
        height: 12px;
        line-height: 1;
        padding: 0 4px;
        margin-left: 5px;
      }
    }
    .related-group-count {
      color: #3a84ff;
      cursor: pointer;
    }
    /deep/ .member-template-table-add {
      background-color: #f2fff4;
    }
  }
}
</style>
