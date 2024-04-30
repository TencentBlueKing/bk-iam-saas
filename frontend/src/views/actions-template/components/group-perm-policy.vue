<template>
  <div class="group-perm-policy-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
    <div class="group-perm-policy-wrapper-input">
      <bk-input
        v-model="keyword"
        :placeholder="$t(`m.actionsTemplate['搜索 系统名、操作名']`)"
        :clearable="true"
        :right-icon="'bk-icon icon-search'"
        @right-icon-click="handleTableSearch"
        @enter="handleTableSearch"
        @clear="handleClear"
      />
    </div>
    <div v-if="!isLoading && !isEmpty" class="group-perm-policy-wrapper-content">
      <!-- <render-perm-item
        data-test-id="myPerm_list_permItem"
        v-for="(item, index) in groupSystemList"
        :key="item.id"
        :expanded.sync="item.expanded"
        :ext-cls="index > 0 ? 'iam-perm-ext-cls' : ''"
        :class="index === groupSystemList.length - 1 ? 'iam-perm-ext-reset-cls' : ''"
        :title="item.name"
        :policy-count="item.custom_policy_count"
        :template-count="item.template_count"
        :group-system-list-length="groupSystemListLength"
        @on-expanded="handleExpanded(...arguments, item)"
        @on-set-external="handleSetExternal">
        <div style="min-height: 60px;" v-bkloading="{ isLoading: item.loading, opacity: 1 }">
          <div v-if="!item.loading">
            <render-template-item
              data-test-id="myPerm_list_templateItem"
              :ref="`rTemplateItem${item.id}`"
              v-for="(subItem, subIndex) in item.templates"
              :key="subIndex"
              :title="subItem.name"
              :count="subItem.count"
              :external-edit="formatOperate"
              :external-delete="formatOperate"
              :is-edit="subItem.isEdit"
              :loading="subItem.editLoading"
              :expanded.sync="subItem.expanded"
              :mode="isEditMode ? 'edit' : 'detail'"
              :external-header-width="externalHeaderWidth"
              @on-delete="handleDelete(item, subItem)"
              @on-save="handleSave(item, index, subItem, subIndex)"
              @on-edit="handleEdit(subItem)"
              @on-cancel="handleCancel(subItem)"
              @on-expanded="handleTemplateExpanded(...arguments, subItem)">
              <div style="min-height: 136px;"
                v-bkloading="{ isLoading: subItem.loading, opacity: 1 }">
                <render-instance-table
                  data-test-id="myPerm_list_instanceTable"
                  v-if="!subItem.loading"
                  mode="detail"
                  :is-custom="subItem.count > 0"
                  :ref="`${index}_${subIndex}_resourceTableRef`"
                  :list="subItem.tableData"
                  :original-list="subItem.tableDataBackup"
                  :authorization="authorizationData"
                  :system-id="item.id"
                  :group-id="groupId"
                  :template-id="subItem.id"
                  :is-edit="subItem.isEdit"
                  :external-delete="formatOperate"
                  :linear-action-list="linearActionList"
                  :is-custom-action-button="true"
                  @on-delete="handleSingleDelete(...arguments, item)"
                />
              </div>
            </render-template-item>
          </div>
        </div>
      </render-perm-item> -->
      <GroupPermTable
        mode="detail"
        :list="groupSystemList"
      />
    </div>
    <template v-if="isEmpty">
      <div class="empty-wrapper">
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :tip-text="emptyData.tip"
          :tip-type="emptyData.tipType"
        />
      </div>
    </template>
  </div>
</template>
<script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { formatCodeData } from '@/common/util';
  import GroupPolicy from '@/model/group-policy';
  // import RenderPermItem from '@/views/group/common/render-perm-item-new.vue';
  // import RenderTemplateItem from '@/views/group/common/render-template-item.vue';
  import GroupPermTable from '@/views/actions-template/components/group-perm-table.vue';

  const CUSTOM_CUSTOM_TEMPLATE_ID = 0;

  export default {
    components: {
      // RenderPermItem,
      // RenderTemplateItem,
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
        linearActionList: [],
        groupSystemList: [],
        actionPermList: [],
        policyList: [],
        authorizationData: {},
        removingSingle: false,
        isPermTemplateDetail: false,
        role: '',
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
        groupSystemListLength: 0,
        externalHeaderWidth: 0,
        readonly: false
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemsLayout', 'externalSystemId']),
      isEmpty () {
        return this.groupSystemList.length < 1;
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
            this.fetchAuthorizationScopeActions(item.id);
            await this.getGroupTemplateList(item);
            if (item.templates.length) {
              item.templates.forEach((v) => {
                this.handleTemplateExpanded(true, v);
              });
            }
          }
          this.groupSystemList = list;
          this.groupSystemListLength = list.length;
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
        } catch (e) {
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
          this.$emit('on-init', false);
        }
      },

      async getGroupTemplateList (groupSystem) {
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

      async fetchAuthorizationScopeActions (id) {
        if (this.authorizationData[id]) {
          return;
        }
        try {
          const res = await this.$store.dispatch('permTemplate/getAuthorizationScopeActions', { systemId: id });
          this.authorizationData[id] = res.data.filter(item => item.id !== '*');
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async fetchActions (item) {
        const params = {
          system_id: item.system.id,
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
        await Promise.all([this.getGroupTemplateList(item), this.fetchAuthorizationScopeActions(item.id)]);
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
        await this.fetchActions(item);
        item.count > 0 ? await this.getGroupCustomPolicy(item) : this.getGroupTemplateDetail(item);
      },

      async handleSave (item, index, subItem, subIndex) {
        const $ref = this.$refs[`${index}_${subIndex}_resourceTableRef`][0];
        const { flag, actions } = $ref.getDataByNormal();
        if (flag) {
          return;
        }
        subItem.editLoading = true;
        try {
          await this.$store.dispatch('userGroup/updateGroupPolicy', {
            id: this.groupId,
            data: {
              system_id: item.id,
              template_id: subItem.id,
              actions
            }
          });
          if (subItem.count > 0) {
            this.getGroupCustomPolicy(subItem);
          } else {
            this.getGroupTemplateDetail(subItem);
          }
          subItem.isEdit = false;
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          subItem.editLoading = false;
        }
      },

      async deleteTemplate (params = {}, item, subItem) {
        subItem.deleteLoading = true;
        try {
          await this.$store.dispatch('permTemplate/deleteTemplateMember', params);
          let filterLen = item.templates.filter(item => item.id !== CUSTOM_CUSTOM_TEMPLATE_ID).length;
          const isExistCustom = item.templates.some(item => item.id === CUSTOM_CUSTOM_TEMPLATE_ID);
          if (filterLen > 0) {
            --filterLen;
            --item.template_count;
          }
          if (filterLen > 0 || isExistCustom) {
            this.getGroupTemplateList(item);
          }
          if (!filterLen && !isExistCustom) {
            this.handleInit();
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          subItem.deleteLoading = false;
        }
      },

      async deleteGroupPolicy (params = {}, item, subItem, flag) {
        if (flag) {
          subItem.deleteLoading = true;
        }
        try {
          await this.$store.dispatch('userGroup/deleteGroupPolicy', params);
          const isExistTemplate = item.templates.some(item => item.id !== CUSTOM_CUSTOM_TEMPLATE_ID);
          if (item.custom_policy_count > 0 && this.removingSingle) {
            --item.custom_policy_count;
          } else {
            item.custom_policy_count = 0;
          }
          this.policyList = subItem;
          if (isExistTemplate) {
            this.getGroupTemplateList(item);
          }
          this.handleInit();
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          if (flag) {
            subItem.deleteLoading = false;
          }
        }
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

      handleDelete (item, subItem) {
        this.removingSingle = false;
        if (subItem.id > 0) {
          this.deleteTemplate({
            id: subItem.id,
            data: {
              members: [{
                type: 'group',
                id: this.groupId
              }]
            }
          }, item, subItem);
        } else {
          this.deleteGroupPolicy({
            id: this.groupId,
            data: {
              system_id: item.id,
              ids: subItem.tableData.map(item => item.policy_id).join(',')
            }
          }, item, subItem, true);
        }
      },

      handleSingleDelete (data, item) {
        this.removingSingle = true;
        this.deleteGroupPolicy({
          id: this.groupId,
          data: {
            system_id: item.id,
            ids: data.ids ? data.ids.join(',') : data.policy_id
          }
        }, item, {}, false);
      },

      handleTableSearch () {},

      handleClear () {},
      
      handleEmptyRefresh () {
        this.handleInit();
      }
    }
  };
</script>

<style lang="postcss" scoped>
.group-perm-policy-wrapper {
  &-input {

  }
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
  }
}
</style>
