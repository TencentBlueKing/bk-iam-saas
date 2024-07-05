<template>
  <div class="group-perm-policy-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
    <div class="group-perm-policy-wrapper-input">
      <iam-search-select
        :placeholder="$t(`m.actionsTemplate['搜索 系统名、操作名']`)"
        :data="searchData"
        :value="searchValue"
        @on-change="handleTableSearch"
      />
    </div>
    <div
      v-if="!isLoading && !isEmpty"
      :class="[
        'group-perm-policy-wrapper-content',
        { 'is-show-notice': showNoticeAlert && showNoticeAlert() }
      ]"
    >
      <GroupPermTable
        mode="detail"
        :is-loading="isLoading"
        :group-id="groupId"
        :is-search="['search'].includes(emptyData.tipType)"
        :list="groupSystemList"
      />
    </div>
    <div v-if="isEmpty" class="empty-wrapper">
      <ExceptionEmpty
        :type="emptyData.type"
        :empty-text="emptyData.text"
        :tip-text="emptyData.tip"
        :tip-type="emptyData.tipType"
        @on-clear="handleTableClear"
      />
    </div>
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { formatCodeData } from '@/common/util';
  import GroupPolicy from '@/model/group-policy';
  import GroupPermTable from '@/views/actions-template/components/group-perm-table.vue';
  import IamSearchSelect from '@/components/iam-search-select';

  const CUSTOM_CUSTOM_TEMPLATE_ID = 0;

  export default {
    inject: ['showNoticeAlert'],
    components: {
      IamSearchSelect,
      GroupPermTable
    },
    props: {
      curDetailData: {
        type: Object
      },
      mode: {
        type: String,
        default: 'edit'
      }
    },
    data () {
      return {
        keyword: '',
        groupId: '',
        isLoading: false,
        searchValue: [],
        searchData: [
          {
            id: 'system_id',
            name: this.$t(`m.actionsTemplate['系统名']`),
            remoteMethod: this.handleRemoteSystem
          },

          {
            id: 'action_id',
            name: this.$t(`m.common['操作']`),
            default: true
          }
        ],
        linearActionList: [],
        groupSystemList: [],
        groupSystemListBack: [],
        actionPermList: [],
        policyList: [],
        searchParams: {},
        authorizationData: {},
        groupAttributes: {
          source_type: '',
          source_from_role: false
        },
        emptyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        },
        externalHeaderWidth: 0,
        readonly: false
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemsLayout', 'externalSystemId']),
      isEmpty () {
        if (this.groupSystemList.length < 1) {
          return true;
        }
        const noData = this.groupSystemList.every((item) => {
          if (item.templates && item.templates.length > 0) {
            item.templates.every((v) => v.tableData.length === 0);
          }
        });
        return noData;
      },
      isEditMode () {
        return this.mode === 'edit';
      },
      canEditGroup () {
        return this.$route.query.edit === 'GroupEdit';
      },
      formatOperate () {
        let result = true;
        if (this.externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle) {
            result = !(!this.groupAttributes.source_from_role && !this.groupAttributes.source_type);
        } else {
            result = !!this.groupAttributes.source_from_role;
        }
        return result;
      }
    },
    watch: {
      curDetailData: {
        handler (value) {
          if (Object.keys(value).length) {
            this.groupId = value.id;
            this.handleInit();
            // this.fetchDetail(value.id);
          } else {
            this.emptyData = Object.assign(this.emptyData, { type: 'empty', text: '暂无数据' });
          }
        },
        immediate: true
      }
    },
    methods: {
      async handleInit () {
        this.isLoading = true;
        this.$emit('on-init', true);
        try {
          const params = {
            id: this.groupId
          };
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch('userGroup/getGroupSystems', params);
          const list = data || [];
          for (let item of list) {
            item = Object.assign(item, {
              loading: false,
              expand: false,
              templates: []
            });
            await this.fetchGroupTemplateList(item);
            await this.fetchActions(item);
            if (item.templates.length) {
              item.templates.forEach((v) => {
                this.handleTemplateExpanded(true, v);
              });
            }
          }
          [this.groupSystemList, this.groupSystemListBack] = [list, list];
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
        } catch (e) {
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
          this.$emit('on-init', false);
        }
      },

      async fetchGroupTemplateList (groupSystem) {
        try {
          const { data } = await this.$store.dispatch('userGroup/getUserGroupTemplateList', {
            id: this.groupId,
            systemId: groupSystem.id
          });
          data.forEach(item => {
            item = Object.assign(item, {
              count: 0,
              loading: false,
              editLoading: false,
              deleteLoading: false,
              tableData: [],
              tableDataBackup: []
            });
          });
          groupSystem.templates = data;
          if (groupSystem.custom_policy_count > 0) {
            groupSystem.templates.push({
              name: this.$t(`m.actionsTemplate['自定义操作']`),
              id: CUSTOM_CUSTOM_TEMPLATE_ID, // 自定义权限 id 为 0
              system: {
                id: groupSystem.id,
                name: groupSystem.name
              },
              count: groupSystem.custom_policy_count,
              loading: false,
              editLoading: false,
              deleteLoading: false,
              tableData: [],
              tableDataBackup: []
            });
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async fetchActions (item) {
        const params = {
          system_id: item.id,
          user_id: this.user.username
        };
        if (this.externalSystemId) {
          params.hidden = false;
        }
        try {
          const { data } = await this.$store.dispatch('permApply/getActions', params);
          this.actionPermList = cloneDeep(data || []);
          this.handleActionLinearData();
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async getGroupTemplateDetail (item) {
        try {
          const { data } = await this.$store.dispatch('userGroup/getGroupTemplateDetail', {
            id: this.groupId,
            templateId: item.id
          });
          const tableData = data.actions.map(row => {
            const linearActionList = this.linearActionList.find(sub => sub.id === row.id);
            row.related_environments = linearActionList ? linearActionList.related_environments : [];
            return new GroupPolicy(
              { ...row, policy_id: 1 },
              'detail',
              'template',
              { system: data.system }
            );
          });
          const tableDataBackup = data.actions.map(row => {
            const linearActionList = this.linearActionList.find(sub => sub.id === row.id);
            row.related_environments = linearActionList ? linearActionList.related_environments : [];
            return new GroupPolicy(
              { ...row, policy_id: 1 },
              'detail',
              'template',
              { system: data.system }
            );
          });
          this.$set(item, 'tableData', tableData);
          this.$set(item, 'tableDataBackup', tableDataBackup);
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async getGroupCustomPolicy (item) {
        try {
          const { data } = await this.$store.dispatch('userGroup/getGroupPolicy', {
            id: this.groupId,
            systemId: item.system.id
          });
          const tableData = (data || []).map(row => {
            const linearActionList = this.linearActionList.find(sub => sub.id === row.id);
            row.related_environments = linearActionList ? linearActionList.related_environments : [];
            row.related_actions = linearActionList ? linearActionList.related_actions : [];
            return new GroupPolicy(
              row,
              'detail',
              'custom',
              { system: item.system }
            );
          });
          this.$set(item, 'tableData', cloneDeep(tableData));
          this.$set(item, 'tableDataBackup', cloneDeep(tableData));
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },
      
      async handleExpanded (flag, item) {
        if (!flag) {
          return;
        }
        await Promise.all([this.fetchGroupTemplateList(item), this.fetchAuthorizationScopeActions(item.id)]);
        if (item.templates.length) {
          item.templates.forEach((v) => {
            this.handleTemplateExpanded(flag, v);
          });
        }
      },

      async handleTemplateExpanded (flag, item) {
        if (!flag) {
          this.$set(item, 'isEdit', false);
          return;
        }
        // count > 0 说明是自定义权限
        item.count > 0 ? await this.getGroupCustomPolicy(item) : this.getGroupTemplateDetail(item);
      },

      async handleRemoteSystem (value) {
        const params = {};
        if (this.externalSystemId) {
          params.hidden = false;
        }
        const { data } = await this.$store.dispatch('system/getSystems', params);
        return data.map(({ id, name }) => ({ id, name })).filter(item => item.name.indexOf(value) > -1);
      },
      
      handleActionLinearData () {
        const linearActions = [];
        this.actionPermList.forEach((item) => {
          item.actions = item.actions.filter(v => !v.hidden);
          item.actions.forEach(act => {
            linearActions.push(act);
          });
          (item.sub_groups || []).forEach(sub => {
            sub.actions = sub.actions.filter(v => !v.hidden);
            sub.actions.forEach(act => {
              linearActions.push(act);
            });
          });
        });
        this.linearActionList = cloneDeep(linearActions);
      },

      handleTableSearch (payload, result) {
        this.searchParams = payload;
        this.searchValue = result;
        let list = cloneDeep(this.groupSystemListBack);
        if (payload.hasOwnProperty('system_id')) {
          list = list.filter((item) => item.id.indexOf(payload.system_id) > -1);
        }
        if (payload.hasOwnProperty('action_id')) {
          list.forEach((item) => {
            if (item.templates && item.templates.length > 0) {
              item.templates.forEach((v) => {
                v.tableData = v.tableData.filter((sub) => sub.name.indexOf(payload.action_id) > -1);
              });
            }
          });
        }
        list = list.filter((item) => {
          return item.templates.length > 0
            && item.templates.find((v) => v.tableData.length > 0);
        });
        if (!result.length) {
          this.handleTableClear();
        } else {
          this.groupSystemList = cloneDeep(list);
          this.emptyData.tipType = 'search';
          this.emptyData = formatCodeData(0, this.emptyData, true);
        }
      },

      handleTableClear () {
        this.emptyData.tipType = '';
        this.searchValue = [];
        this.groupSystemList = cloneDeep(this.groupSystemListBack);
      }
    }
  };
</script>

<style lang="postcss" scoped>
.group-perm-policy-wrapper {
  position: relative;
  height: 100%;
  &-content {
    margin-top: 18px;
    max-height: calc(100vh - 323px);
    overflow-y: auto;
    &::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    &::-webkit-scrollbar-thumb {
      background: #dcdee5;
      border-radius: 3px;
    }
    &::-webkit-scrollbar-track {
      background: transparent;
      border-radius: 3px;
    }
    &.is-show-notice {
      max-height: calc(100vh - 363px);
    }
  }
  .empty-wrapper {
    position: absolute;
    top: 45%;
    left: 50%;
    transform: translate(-50%, -45%);
  }
}
</style>
