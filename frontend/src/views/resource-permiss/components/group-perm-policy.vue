<template>
  <div class="resource-user-group-perm">
    <div class="resource-user-group-perm-search">
      <bk-input
        clearable
        style="width: 400px"
        :placeholder="$t(`m.resourcePermiss['搜索 系统名、操作名']`)"
        :right-icon="'bk-icon icon-search'"
        v-model="groupValue"
        @enter="handleSearchGroup"
        @clear="handleEmptyClear"
        @right-icon-click="handleSearchGroup"
      />
    </div>
    <template v-if="!isLoading && !isEmpty">
      <RenderPermItem
        v-for="(item, index) in groupSystemList"
        :key="item.id"
        :expanded.sync="item.expanded"
        :ext-cls="index > 0 ? 'iam-perm-ext-cls' : ''"
        :class="index === groupSystemList.length - 1 ? 'iam-perm-ext-reset-cls' : ''"
        :title="item.name"
        :policy-count="item.custom_policy_count"
        :template-count="item.template_count"
        :group-system-list-length="groupSystemListLength"
        @on-expanded="handleExpanded(...arguments, item)">
        <div v-bkloading="{ isLoading: item.loading, opacity: 1 }">
          <div v-if="!item.loading">
            <RenderTemplateItem
              :ref="`rTemplateItem${item.id}`"
              v-for="(subItem, subIndex) in item.templates"
              :key="subIndex"
              :mode="isEditMode ? 'edit' : 'detail'"
              :title="formatSubTitle(subItem)"
              :delete-title="formatDelTitle(subItem)"
              :delete-confirm="formatDelConfirm(subItem)"
              :count="subItem.count"
              :is-edit="subItem.isEdit"
              :loading="subItem.editLoading"
              :expanded.sync="subItem.expanded"
              :external-delete="['template'].includes(subItem.mode_type)"
              @on-delete="handleDelete(item, subItem)"
              @on-save="handleSave(item, index, subItem, subIndex)"
              @on-edit="handleEdit(subItem)"
              @on-cancel="handleCancel(subItem)"
              @on-expanded="handleTemplateExpanded(...arguments, subItem)">
              <div v-bkloading="{ isLoading: subItem.loading, opacity: 1 }">
                <RenderCustomPermTable
                  v-if="!subItem.loading"
                  mode="detail"
                  :ref="`${index}_${subIndex}_resourceTableRef`"
                  :list="subItem.tableData"
                  :original-list="subItem.tableDataBackup"
                  :authorization="authorizationData"
                  :system-id="item.id"
                  :group-id="groupId"
                  :template-id="subItem.id"
                  :is-custom="subItem.count > 0"
                  :is-edit="subItem.isEdit"
                  :external-delete="isAdminGroup"
                  :linear-action-list="linearActionList"
                  :is-custom-action-button="['custom'].includes(subItem.mode_type)"
                  :is-show-delete-action="true"
                  :is-show-detail-action="false"
                  @on-delete="handleSingleDelete(...arguments, item)"
                />
              </div>
            </RenderTemplateItem>
          </div>
        </div>
      </RenderPermItem>
    </template>
    <div v-if="!isLoading && isEmpty" class="empty-data-wrapper">
      <ExceptionEmpty
        :type="emptyData.type"
        :empty-text="emptyData.text"
        :tip-text="emptyData.tip"
        :tip-type="emptyData.tipType"
        @on-refresh="handleEmptyRefresh"
      />
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { cloneDeep } from 'lodash';
  import { formatCodeData } from '@/common/util';
  import GroupPolicy from '@/model/group-policy';
  import RenderPermItem from './render-perm-item.vue';
  import RenderTemplateItem from './render-template-item.vue';
  import RenderCustomPermTable from '../components/custom-perm-table.vue';

  export default {
    components: {
      RenderPermItem,
      RenderTemplateItem,
      RenderCustomPermTable
    },
    props: {
      curDetailData: {
        type: Object
      },
      groupAttributes: {
        type: Object,
        default: () => {
          return {};
        }
      },
      readOnly: {
        type: Boolean,
        default: false
      },
      mode: {
        type: String,
        default: 'edit'
      }
    },
    data () {
      return {
        isLoading: false,
        tableLoading: false,
        groupId: 0,
        groupSystemListLength: 0,
        groupValue: '',
        groupSystemList: [],
        customActionsList: [],
        linearActionList: [],
        authorizationData: {},
        deletePoPoverConfirm: {
          template: {
            title: this.$t(`m.resourcePermiss['确认移除该操作模板？']`),
            label: this.$t(`m.resourcePermiss['操作模板']`),
            tip: this.$t(`m.resourcePermiss['移除后，用户组成员将失去操作模板对应的权限，请谨慎操作。']`)
          },
          custom: {
            title: this.$t(`m.resourcePermiss['确认删除该操作权限？']`),
            label: this.$t(`m.resourcePermiss['操作权限']`),
            tip: this.$t(`m.resourcePermiss['删除后，用户组成员将失去对应的自定义权限，请谨慎操作。']`)
          }
        },
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
        }
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      isEditMode () {
        return this.mode === 'edit';
      },
      isEmpty () {
        return this.groupSystemList.length < 1;
      },
      formatSubTitle () {
        return (payload) => {
          const { name, mode_type } = payload;
          const typeMap = {
            template: () => {
              return this.$t(`m.info['用户组权限操作模板标题']`, { value: name });
            },
            custom: () => {
              return name;
            }
          };
          if (typeMap[mode_type]) {
            return typeMap[mode_type]();
          }
          return '';
        };
      },
      formatDelTitle () {
        return (payload) => {
          const { mode_type } = payload;
          const typeMap = {
            template: () => {
              return this.$t(`m.resourcePermiss['移除模板']`);
            },
            custom: () => {
              return '';
            }
          };
          if (typeMap[mode_type]) {
            return typeMap[mode_type]();
          }
          return '';
        };
      },
      formatDelConfirm () {
        return (payload) => {
          let params = {};
          const { mode_type, name } = payload;
          const typeMap = {
            template: () => {
              params = Object.assign({}, {
                title: this.$t(`m.dialog['确认移除该操作模板？']`),
                tip: this.$t(`m.resourcePermiss['移除后，用户组成员将失去操作模板对应的权限，请谨慎操作。']`),
                label: this.$t(`m.resourcePermiss['操作模板']`),
                value: name
              });
              return params;
            },
            custom: () => {
              params = Object.assign({}, {
                title: this.$t(`m.dialog['确认删除该操作权限？']`),
                tip: this.$t(`m.resourcePermiss['删除后，用户组成员将失去对应的自定义权限，请谨慎操作。']`),
                label: this.$t(`m.resourcePermiss['操作权限']`),
                value: name
              });
              return params;
            }
          };
          if (typeMap[mode_type]) {
            return typeMap[mode_type]();
          }
          return '';
        };
      },
      isAdminGroup () {
        return !this.groupAttributes.source_from_role;
      }
    },
    watch: {
      curDetailData: {
        handler (value) {
          this.groupId = value.id;
          this.fetchInitData();
        },
        immediate: true
      }
    },
    methods: {
      async fetchInitData () {
        this.isLoading = true;
        try {
          const params = {
            id: this.curDetailData.id
          };
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch('userGroup/getGroupSystems', params);
          (data || []).forEach((item) => {
            item = Object.assign(item, {
              expand: false,
              loading: false,
              templates: []
            });
          });
          // 系统按照字典排序
          if (data.length) {
            data.sort((curr, next) => curr.name.localeCompare(next.name));
            if (this.externalSystemId) {
              const externalSystemIndex = data.findIndex((item) => item.id === this.externalSystemId);
              if (externalSystemIndex > -1) {
                data.splice(externalSystemIndex, 1, ...data.splice(0, 1, data[externalSystemIndex]));
              }
            }
          }
          this.groupSystemList = data;
          this.groupSystemListLength = data.length;
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
        } catch (e) {
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      async getGroupTemplateList (groupSystem) {
        groupSystem.loading = true;
        let res;
        try {
          res = await this.$store.dispatch('userGroup/getUserGroupTemplateList', {
            id: this.groupId,
            systemId: groupSystem.id
          });
          res.data.forEach((item) => {
            item.loading = false;
            item.tableData = [];
            item.tableDataBackup = [];
            item.count = 0;
            item.template_count = groupSystem.template_count || 0;
            item.custom_policy_count = groupSystem.custom_policy_count || 0;
            item.mode_type = 'template';
            item.editLoading = false;
            item.deleteLoading = false;
          });
          groupSystem.templates = res.data; // 赋值给展开项
          if (groupSystem.custom_policy_count) {
            groupSystem.templates.push({
              name: this.$t(`m.perm['自定义权限']`),
              id: 0, // 自定义权限 id 为 0
              system: {
                id: groupSystem.id,
                name: groupSystem.name
              },
              mode_type: 'custom',
              count: groupSystem.custom_policy_count,
              loading: false,
              tableData: [],
              tableDataBackup: [],
              editLoading: false,
              deleteLoading: false
            });
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          groupSystem.loading = false;
          if (this.curDetailData.system_id === groupSystem.id) {
            this.$nextTick(() => {
              console.log(this.$refs[`rTemplateItem${groupSystem.id}`]);
              this.$refs[`rTemplateItem${groupSystem.id}`]
                && this.$refs[`rTemplateItem${groupSystem.id}`].length
                && this.$refs[`rTemplateItem${groupSystem.id}`][0].handleExpanded();
            });
          }
        }
      },
      
      async getGroupCustomPolicy (item) {
        item.loading = true;
        try {
          const res = await this.$store.dispatch('userGroup/getGroupPolicy', {
            id: this.groupId,
            systemId: item.system.id
          });
          const tableData = res.data.map(row => {
            const linearActionList = this.linearActionList.find(sub => sub.id === row.id);
            // eslint-disable-next-line max-len
            row.related_environments = linearActionList ? linearActionList.related_environments : [];
            row.related_actions = linearActionList ? linearActionList.related_actions : [];
            return new GroupPolicy(
              row,
              'detail', // 此属性为flag，会在related-resource-types赋值为add
              'custom',
              { system: item.system }
            );
          });
          this.$set(item, 'tableData', cloneDeep(tableData));
          this.$set(item, 'tableDataBackup', cloneDeep(tableData));
          console.log('itemTableData', item);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          item.loading = false;
        }
      },

      async getGroupTemplateDetail (item) {
        item.loading = true;
        try {
          const { data } = await this.$store.dispatch('userGroup/getGroupTemplateDetail', {
            id: this.groupId,
            templateId: item.id
          });
          const tableData = data.actions.map(row => {
            const linearAction = this.linearActionList.find(sub => sub.id === row.id);
            row.related_environments = linearAction ? linearAction.related_environments : [];
            return new GroupPolicy(
              { ...row, policy_id: 1 },
              'detail',
              'template',
              { system: data.system }
            );
          });
          const tableDataBackup = cloneDeep(tableData);
          this.$set(item, 'tableData', tableData);
          this.$set(item, 'tableDataBackup', tableDataBackup);
          console.log('item.tableData', item.tableData);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          item.loading = false;
        }
      },

      async handleTemplateExpanded (flag, item) {
        if (!flag) {
          this.$set(item, 'isEdit', false);
          return;
        }
        // count > 0 说明是自定义权限
        console.log(item, 111);
        await this.fetchActions(item);
        if (item.count > 0) {
          this.getGroupCustomPolicy(item);
          return;
        }
        this.getGroupTemplateDetail(item);
      },

      // 获取系统对应的自定义操作
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
          this.customActionsList = cloneDeep(data || []);
          this.handleActionLinearData();
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      // 获取授权边界数据
      async fetchAuthorizationScopeActions (id) {
        if (this.authorizationData[id]) {
          return;
        }
        try {
          const { data } = await this.$store.dispatch('permTemplate/getAuthorizationScopeActions', { systemId: id });
          this.authorizationData[id] = (data || []).filter(item => item.id !== '*');
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      handleActionLinearData () {
        const linearActions = [];
        this.customActionsList.forEach((item, index) => {
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
        console.log('this.linearActionList', this.linearActionList);
      },

      handleSearchGroup () {
        this.emptyData.tipType = 'search';
        // this.fetchAssociateGroup(true);
      },

      handleClearGroup () {
        this.groupValue = '';
        this.emptyData.tipType = '';
        // this.fetchAssociateGroup(true);
      },

      handleExpanded (flag, item) {
        if (!flag) {
          return;
        }
        this.getGroupTemplateList(item);
        this.fetchAuthorizationScopeActions(item.id);
      },

      handleEmptyClear () {
        this.emptyData.tipType = '';
        this.groupValue = '';
        this.resetPagination();
        this.fetchAssociateGroup(true);
      },

      handleEmptyRefresh () {
        this.resetPagination();
        this.fetchAssociateGroup(true);
      },

      resetPagination () {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 10 });
      }
    }
  };
</script>

<style lang="postcss">
  @import '../common/css/popoverConfirm.css';
</style>

<style lang="postcss" scoped>
.resource-user-group-perm {
  padding: 0 24px;
  &-search {
    position: static;
    top: 0;
  }
  .system-render-perm-item {
    margin-top: 16px;
  }
  .empty-data-wrapper {
    margin-top: 100px;
  }
}
</style>
