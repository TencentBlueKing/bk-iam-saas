<template>
  <div class="resource-user-group-perm">
    <div class="resource-user-group-perm-search">
      <IamSearchSelect
        style="width: 400px;"
        :placeholder="$t(`m.resourcePermiss['搜索 系统名、操作名']`)"
        :data="searchData"
        :value="searchValue"
        @on-change="handleSearchSystemAction"
      />
    </div>
    <template v-if="!isLoading && !isEmpty">
      <RenderPermItem
        v-for="(item, index) in groupSystemList"
        :key="item.id"
        :ref="`rPermItem${item.id}`"
        :expanded.sync="item.expanded"
        :ext-cls="index > 0 ? 'iam-perm-ext-cls' : ''"
        :class="index === groupSystemList.length - 1 ? 'iam-perm-ext-reset-cls' : ''"
        :title="item.name"
        :policy-count="item.custom_policy_count"
        :template-count="item.template_count"
        :group-system-list-length="groupSystemList.length"
        @on-expanded="handleExpanded(...arguments, item)">
        <div v-bkloading="{ isLoading: item.loading, opacity: 1 }">
          <div v-if="!item.loading">
            <RenderTemplateItem
              v-for="(subItem, subIndex) in item.templates"
              :key="subIndex"
              :ref="`rTemplateItem${item.id}`"
              :mode="isEditMode ? 'edit' : 'detail'"
              :title="formatSubTitle(subItem)"
              :delete-title="formatDelTitle(subItem)"
              :delete-confirm="formatDelConfirm(subItem)"
              :count="subItem.tableData.length"
              :is-disabled-operate="isDisabledOperate(item)"
              :is-edit="subItem.isEdit"
              :loading="subItem.editLoading"
              :expanded.sync="subItem.expanded"
              :external-delete="['template'].includes(subItem.mode_type)"
              @on-delete="handleDelete(item, subItem)"
              @on-edit="handleEdit(subItem)"
              @on-cancel="handleCancel(subItem)"
              @on-expanded="handleTemplateExpanded(...arguments, subItem, subIndex)">
              <div v-bkloading="{ isLoading: subItem.loading, opacity: 1 }">
                <RenderCustomPermTable
                  v-if="!subItem.loading"
                  mode="detail"
                  :ref="`${index}_${subIndex}_resourceTableRef`"
                  :list="subItem.tableData"
                  :cur-detail-data="curDetailData"
                  :group-id="groupId"
                  :template-id="subItem.id"
                  :is-loading="subItem.loading"
                  :is-edit="subItem.isEdit"
                  :is-custom="isCustom(subItem)"
                  :is-custom-action-button="isCustom(subItem)"
                  :is-disabled-operate="isDisabledOperate(item)"
                  :external-delete="isAdminGroup"
                  :delete-confirm="formatDelConfirm(subItem)"
                  :linear-action-list="linearActionList"
                  :is-show-delete-action="true"
                  :is-show-detail-action="false"
                  @on-delete="handleSingleDelete(...arguments, item)"
                  @on-delete-instances="handleDeleteInstances"
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
        @on-clear="handleEmptyClear"
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
  import RenderCustomPermTable from '../components/group-perm-table.vue';
  import IamSearchSelect from '@/components/iam-search-select';
  import getActionsMixin from '../common/js/getActionsMixin';

  export default {
    components: {
      RenderPermItem,
      RenderTemplateItem,
      RenderCustomPermTable,
      IamSearchSelect
    },
    mixins: [getActionsMixin],
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
        groupSystemList: [],
        groupSystemListBack: [],
        customActionsList: [],
        searchValue: [],
        searchData: [
          {
            id: 'system_id',
            name: this.$t(`m.common['系统名']`),
            remoteMethod: this.handleRemoteSystem
          },
          {
            id: 'action_name',
            name: this.$t(`m.common['操作']`),
            default: true
          }
        ],
        searchParams: {},
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
      isCustom () {
        return (payload) => {
          return ['custom'].includes(payload.mode_type);
        };
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
      },
      isDisabledOperate () {
        return (payload) => {
          if (['super_manager'].includes(this.user.role.type)) {
            return false;
          }
          return payload.id !== this.curDetailData.system_id || this.isAdminGroup;
        };
      }
    },
    watch: {
      curDetailData: {
        handler (value) {
          this.groupId = value.id;
          this.fetchInitData(true);
        },
        immediate: true
      }
    },
    methods: {
      async fetchInitData (isFirst = false) {
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
          [this.groupSystemList, this.groupSystemListBack] = [data, data];
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
        } catch (e) {
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
          // 首次加载需要获取所有系统的操作
          if (isFirst) {
            this.groupSystemList.forEach((item) => {
              if (item.id === this.curDetailData.system_id) {
                this.$nextTick(() => {
                  this.$refs[`rPermItem${item.id}`]
                    && this.$refs[`rPermItem${item.id}`].length
                    && this.$refs[`rPermItem${item.id}`][0].handleExpanded();
                });
              } else {
                this.fetchGroupTemplateList(item, true);
              }
            });
          } else {
            const curSystem = this.groupSystemList.find((item) => item.id === this.curDetailData.system_id);
            if (curSystem) {
              this.$nextTick(() => {
                this.$refs[`rPermItem${curSystem.id}`]
                  && this.$refs[`rPermItem${curSystem.id}`].length
                  && this.$refs[`rPermItem${curSystem.id}`][0].handleExpanded();
              });
            }
          }
        }
      },

      async fetchGroupTemplateList (groupSystem, isFirst = false) {
        groupSystem.loading = true;
        let res;
        try {
          res = await this.$store.dispatch('userGroup/getUserGroupTemplateList', {
            id: this.groupId,
            systemId: groupSystem.id
          });
          res.data.forEach((item) => {
            item.loading = true;
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
              custom_policy_count: groupSystem.custom_policy_count,
              tableData: [],
              tableDataBackup: [],
              loading: false,
              editLoading: false,
              deleteLoading: false
            });
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          groupSystem.loading = false;
          if (isFirst) {
            // 代表是首次加载，需要遍历系统查询操作
            groupSystem.templates && groupSystem.templates.forEach((temp, tempIndex) => {
              this.handleTemplateExpanded(true, temp, tempIndex);
            });
          } else {
            this.$nextTick(() => {
              if (this.$refs[`rTemplateItem${groupSystem.id}`]) {
                this.$refs[`rTemplateItem${groupSystem.id}`].forEach((item) => {
                  item.handleExpanded();
                });
              }
            });
          }
        }
      },
      
      async fetchGroupCustomPolicy (item) {
        item.loading = true;
        try {
          const { data } = await this.$store.dispatch('userGroup/getGroupPolicy', {
            id: this.groupId,
            systemId: item.system.id
          });
          let actionList = data || [];
          if (this.searchParams.action_name) {
            actionList = actionList.filter((v) => v.name.toLowerCase().indexOf(this.searchParams.action_name) > -1);
          }
          const tableData = actionList.map((v) => {
            const linearAction = this.linearActionList.find((sub) => sub.id === v.id);
            v.related_environments = linearAction ? linearAction.related_environments : [];
            v.related_actions = linearAction ? linearAction.related_actions : [];
            return new GroupPolicy(
              v,
              'detail', // 此属性为flag，会在related-resource-types赋值为add
              'custom',
              { system: item.system }
            );
          });
          this.$set(item, 'tableData', cloneDeep(tableData));
          this.$set(item, 'tableDataBackup', cloneDeep(tableData));
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
          let actionList = data.actions || [];
          if (this.searchParams.action_name) {
            actionList = actionList.filter((v) => v.name.toLowerCase().indexOf(this.searchParams.action_name) > -1);
          }
          const tableData = actionList.map((v) => {
            const linearAction = this.linearActionList.find((sub) => sub.id === v.id);
            v.related_environments = linearAction ? linearAction.related_environments : [];
            return new GroupPolicy(
              { ...v, policy_id: 1 },
              'detail',
              'template',
              { system: data.system }
            );
          });
          this.$set(item, 'tableData', tableData);
          this.$set(item, 'tableDataBackup', cloneDeep(tableData));
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          item.loading = false;
        }
      },

      async handleTemplateExpanded (flag, item, index) {
        if (!flag) {
          return;
        }
        // 这里处理接口节流，展开会存在多种类型，但是单个系统操作是共用的
        if (index === 0) {
          await this.fetchActions(item);
        }
        if (['custom'].includes(item.mode_type)) {
          this.fetchGroupCustomPolicy(item);
          return;
        }
        this.getGroupTemplateDetail(item);
      },

      async handleRemoteSystem (value) {
        const params = {};
        if (this.externalSystemId) {
          params.hidden = false;
        }
        return this.$store.dispatch('system/getSystems', params).then(({ data }) => {
          return data.map(({ id, name }) => ({ id, name })).filter((item) => item.name.indexOf(value) > -1);
        });
      },

      async handleDelete (item, subItem) {
        if (subItem.id > 0) {
          await this.handleDeleteTemplate({
            id: subItem.id,
            data: {
              members: [{
                type: 'group',
                id: this.groupId
              }]
            }
          }, item, subItem);
        } else {
          await this.handleDeleteGroupPolicy({
            id: this.groupId,
            data: {
              system_id: item.id,
              ids: subItem.tableData.map(item => item.policy_id).join(',')
            }
          }, item, subItem, true);
        }
      },

      async handleDeleteTemplate (params = {}, item, subItem) {
        subItem.deleteLoading = true;
        try {
          await this.$store.dispatch('permTemplate/deleteTemplateMember', params);
          let filterLen = item.templates.filter(item => item.id !== 0).length;
          const isExistCustom = item.templates.some(item => item.id === 0);
          if (filterLen > 0) {
            --filterLen;
            --item.template_count;
          }
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          if (Object.keys(this.searchParams).length > 0) {
            if (item.custom_policy_count === 0 && item.template_count === 0) {
              this.groupSystemListBack = this.groupSystemListBack.filter((v) => v.id !== item.id);
            }
            const curSystem = this.groupSystemListBack.find((v) => v.id === item.id);
            if (curSystem) {
              curSystem.template_count = item.template_count;
              curSystem.expanded = true;
              curSystem.templates = curSystem.templates.filter((v) => v.id !== subItem.id);
            }
            this.handleGetSearchData();
          } else {
            if (filterLen > 0 || isExistCustom) {
              await this.fetchGroupTemplateList(item, false);
            }
            if (!filterLen && !isExistCustom) {
              await this.fetchInitData(false);
            }
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          subItem.deleteLoading = false;
        }
      },

      async handleDeleteGroupPolicy (params = {}, item, subItem, flag) {
        if (flag) {
          subItem.deleteLoading = true;
        }
        try {
          await this.$store.dispatch('userGroup/deleteGroupPolicy', params);
          const isExistTemplate = item.templates.some((v) => v.id !== 0);
          if (item.custom_policy_count > 0) {
            --item.custom_policy_count;
          } else {
            item.custom_policy_count = 0;
          }
          this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
          if (Object.keys(this.searchParams).length > 0) {
            if (item.custom_policy_count === 0 && item.template_count === 0) {
              this.groupSystemListBack = this.groupSystemListBack.filter((v) => v.id !== item.id);
            }
            const curSystem = this.groupSystemListBack.find((v) => v.id === item.id);
            if (curSystem) {
              curSystem.custom_policy_count = item.custom_policy_count;
              curSystem.expanded = true;
              curSystem.templates.forEach((v) => {
                v.expanded = true;
                v.tableData = v.tableData.filter((v) => !subItem.ids.includes(v.policy_id));
              });
            }
            this.handleGetSearchData();
          } else {
            if (isExistTemplate) {
              this.fetchGroupTemplateList(item, false);
            }
            this.fetchInitData(false);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          if (flag) {
            subItem.deleteLoading = false;
          }
        }
      },

      async handleSingleDelete (payload, item) {
        await this.handleDeleteGroupPolicy({
          id: this.groupId,
          data: {
            system_id: item.id,
            ids: payload.ids ? payload.ids.join(',') : payload.policy_id
          }
        }, item, payload, false);
      },

      async handleDeleteInstances () {
        await this.fetchInitData(false);
      },

      handleSearchSystemAction (payload, result) {
        this.searchParams = payload;
        this.searchValue = result;
        this.handleGetSearchData();
      },

      handleExpanded (flag, item) {
        if (!flag) {
          return;
        }
        this.fetchGroupTemplateList(item);
      },

      handleGetSearchData () {
        let systemList = cloneDeep(this.groupSystemListBack);
        if (this.searchParams.system_id) {
          systemList = systemList.filter(
            (item) => item.id.indexOf(this.searchParams.system_id) > -1);
        }
        if (this.searchParams.action_name) {
          systemList.forEach((item) => {
            if (item.templates && item.templates.length > 0) {
              item.templates.forEach((v) => {
                v.tableData = v.tableData.filter((sub) =>
                  sub.name.toLowerCase().indexOf(this.searchParams.action_name) > -1);
                if (['custom'].includes(v.mode_type)) {
                  item.custom_policy_count = v.tableData.length;
                }
                if (['template'].includes(v.mode_type)) {
                  item.template_count = v.tableData.length;
                }
              });
            }
          });
        }
        systemList = systemList.filter((item) => {
          return item.templates.length > 0 && item.templates.find((v) => v.tableData.length > 0);
        });
        if (!this.searchValue.length) {
          this.handleEmptyClear();
        } else {
          this.emptyData.tipType = 'search';
          this.groupSystemList = cloneDeep(systemList);
          this.emptyData = formatCodeData(0, this.emptyData, true);
        }
      },

      handleEmptyClear () {
        this.searchParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.groupSystemList = cloneDeep(this.groupSystemListBack);
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
