<template>
  <div class="iam-personal-user-perm-wrapper" v-if="isShowPage">
    <div class="header">
      <span class="display-name">{{ curData.username }}</span>
      <span class="name" v-if="isExistName">({{ curData.name }})</span>
    </div>
    <div>
      <IamResourceCascadeSearch
        ref="iamResourceSearchRef"
        :active="active"
        :min-select-width="'165px'"
        :max-select-width="'200px'"
        :search-select-place-holder="$t(`m.perm['输入用户组名、描述等按回车键进行搜索']`)"
        @on-remote-table="handleRemoteTable"
        @on-refresh-table="handleRefreshTable"
        @on-input-value="handleInputValue"
      />
    </div>
    <div class="table-list-wrapper">
      <bk-tab
        ref="tabRef"
        type="unborder-card"
        ext-cls="iam-user-tab-cls"
        :active.sync="active"
        :key="tabKey"
      >
        <bk-tab-panel
          v-for="(panel, index) in panels"
          v-bind="panel"
          :key="index"
          @tab-change="handleTabChange"
        >
          <template slot="label">
            <span class="panel-name">
              <span>{{ panel.label }}</span>
              <span v-if="curSearchParams && Object.keys(curSearchParams).length">
                ({{ panel.count }})
              </span>
            </span>
          </template>
          <div class="personal-com-wrapper">
            <component
              v-if="active === panel.name"
              ref="childPermRef"
              :key="componentsKey"
              :is="active"
              :data="curData"
              :total-count="panel.count"
              :personal-group-list="personalGroupList"
              :system-list="systemList"
              :system-list-storage="systemListStorage"
              :tep-system-list="teporarySystemList"
              :department-group-list="departmentGroupList"
              :member-temp-by-user-count="panel.userCount"
              :member-temp-by-depart-count="panel.departCount"
              :member-temp-by-user-list="memberTempByUserList"
              :member-temp-by-depart-list="memberTempByDepartList"
              :empty-data="curEmptyData"
              :cur-search-params="curSearchParams"
              :cur-search-pagination="curSearchPagination"
              :is-search-perm="isSearchPerm"
              :check-group-list="panels[0].selectList"
              @refresh="fetchData"
              @on-select-group="handleSelectGroup"
              @on-clear="handleEmptyClear"
              @on-refresh="handleEmptyRefresh"
            />
          </div>
        </bk-tab-panel>
      </bk-tab>
    </div>
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData } from '@/common/util';
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';
  import CustomPerm from './custom-perm';
  import GroupPerm from './group-perm';
  import MemberTemplateGroupPerm from '@/views/perm/member-template-group-perm/index.vue';
  import TeporaryCustomPerm from './teporary-custom-perm';
  import DepartmentGroupPerm from './department-group-perm';
  export default {
    name: '',
    components: {
      CustomPerm,
      GroupPerm,
      TeporaryCustomPerm,
      DepartmentGroupPerm,
      MemberTemplateGroupPerm,
      IamResourceCascadeSearch
    },
    props: {
      params: {
        type: Object,
        default: () => {
          return {};
        }
      }
    },
    data () {
      return {
        curData: {},
        panels: [
          {
            name: 'GroupPerm',
            label: this.$t(`m.perm['用户组权限']`),
            empty: 'emptyData',
            count: 0,
            selectList: []
          },
          {
            name: 'DepartmentGroupPerm',
            label: this.$t(`m.perm['所属组织用户组权限']`),
            empty: 'emptyDepartmentGroupData',
            count: 0,
            selectList: []
          },
          {
            name: 'MemberTemplateGroupPerm',
            label: this.$t(`m.perm['所属人员模板用户组权限']`),
            empty: 'emptyMemberTemplateData',
            count: 0,
            userCount: 0,
            departCount: 0,
            selectList: []
          },
          {
            name: 'CustomPerm',
            label: this.$t(`m.perm['自定义权限']`),
            empty: 'emptyCustomData',
            count: 0,
            selectList: []
          }
        // { name: 'teporaryCustomPerm', label: this.$t(`m.myApply['临时权限']`) }
        ],
        active: 'GroupPerm',
        componentsKey: -1,
        curCom: 'GroupPerm',
        isShowConfirmDialog: false,
        componentLoading: false,
        isSearchPerm: false,
        actionIdError: false,
        searchTypeError: false,
        resourceTypeError: false,
        resourceInstanceError: false,
        isShowResourceInstanceSideSlider: false,
        resourceInstanceSideSliderTitle: '',
        tabKey: 'tab-key',
        personalGroupList: [],
        systemList: [],
        systemListStorage: [],
        teporarySystemList: [],
        departmentGroupList: [],
        memberTempByUserList: [],
        memberTempByDepartList: [],
        curSearchParams: {},
        curSearchPagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        emptyDepartmentGroupData: {},
        emptyTemporarySystemData: {},
        emptyMemberTemplateData: {},
        emptyCustomData: {},
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        curEmptyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        },
        customSelectWidth: window.innerWidth <= 1520 ? '160px' : '240px'
      };
    },
    computed: {
    ...mapGetters([
      'externalSystemsLayout',
      'externalSystemId',
      'roleList',
      'mainContentLoading'
    ]),
    /**
     * isExistName
     */
    isExistName () {
      return this.curData.name !== '';
    },
    /**
     * isShowPage
     */
    isShowPage () {
      return Object.keys(this.params).length > 0;
    }
    },
    watch: {
      /**
       * params
       */
      params: {
        handler (value) {
          if (Object.keys(value).length > 0) {
            // 切换的时候重置数据
            this.fetchDetailData(value);
          }
        },
        immediate: true
      },
      active: {
        handler (value) {
          // 因为同时调了很多接口，所以需要对应的空配置内容
          const comMap = {
            CustomPerm: 'CustomPerm',
            GroupPerm: 'GroupPerm',
            MemberTemplateGroupPerm: 'MemberTemplateGroupPerm',
            TeporaryCustomPerm: 'TeporaryCustomPerm',
            DepartmentGroupPerm: 'DepartmentGroupPerm'
          };
          this.curCom = comMap[value];
          this.componentsKey = +new Date();
          const emptyField = this.panels.find(item => item.name === value);
          if (emptyField) {
            this.curEmptyData = _.cloneDeep(this[emptyField.empty]);
          }
        },
        immediate: true
      }
    },
    created () {
      this.emptyCustomData = _.cloneDeep(this.emptyData);
      this.emptyTemporarySystemData = _.cloneDeep(this.emptyData);
      this.emptyDepartmentGroupData = _.cloneDeep(this.emptyData);
      this.emptyMemberTemplateData = _.cloneDeep(this.emptyData);
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-perm-tab-count');
      });
      bus.$on('on-perm-tab-count', (payload) => {
        const { active, count } = payload;
        const panelIndex = this.panels.findIndex(item => item.name === active);
        if (panelIndex > -1) {
          if (active === this.active && count !== this.panels[panelIndex].count && this.isSearchPerm) {
            this.fetchRemoteTable(true);
          }
          this.$set(this.panels[panelIndex], 'count', count);
          if (['CustomPerm'].includes(active) && count < 1) {
            this.systemList = [];
          }
        }
      });
    },
    methods: {
      async fetchDetailData (value) {
        this.active = 'GroupPerm';
        this.curCom = 'GroupPerm';
        this.curEmptyData.tipType = '';
        this.isSearchPerm = false;
        this.curSearchParams = {};
        this.handleEmptyClear();
        this.componentsKey = +new Date();
        this.curData = _.cloneDeep(value);
        await this.getHasSystem();
      },
      
      fetchData () {
        this.handleEmptyClear();
      },

      async getHasSystem () {
        try {
          const { id, username, type } = this.curData;
          const { data } = await this.$store.dispatch('organization/getSubjectHasPermSystem', {
            subjectType: type === 'user' ? type : 'department',
            subjectId: type === 'user' ? username : id
          });
          this.systemListStorage = data || [];
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      // 获取搜索的个人用户组
      async fetchUserGroupSearch () {
        try {
          const { current, limit } = this.curSearchPagination;
          const { id, username, type } = this.curData;
          const params = {
            ...this.curSearchParams,
            ...{
              subjectType: type === 'user' ? type : 'department',
              subjectId: type === 'user' ? username : id
            },
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(
            'perm/getPermGroupsSearch',
            params
          );
          this.personalGroupList = data.results || [];
          this.$set(this.panels[0], 'count', data.count || 0);
          this.emptyData = formatCodeData(code, this.emptyData, data.count === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.personalGroupList = [];
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.componentLoading = false;
        }
      },

      // 获取所属组织用户组
      async fetchDepartSearch () {
        const { current, limit } = this.curSearchPagination;
        const { id, username, type } = this.curData;
        const params = {
          ...this.curSearchParams,
          ...{
            subjectType: type === 'user' ? type : 'department',
            subjectId: type === 'user' ? username : id
          },
          limit,
          offset: limit * (current - 1)
        };
        if (this.externalSystemId) {
          params.system_id = this.externalSystemId;
          params.hidden = false;
        }
        try {
          const { code, data } = await this.$store.dispatch(
            'perm/getDepartPermGroupsSearch',
            params
          );
          const { count, results } = data;
          this.departmentGroupList = results || [];
          this.$set(this.panels[1], 'count', count || 0);
          this.emptyDepartmentGroupData = formatCodeData(
            code,
            this.emptyDepartmentGroupData,
            results.length === 0
          );
        } catch (e) {
          const { code } = e;
          this.emptyDepartmentGroupData = formatCodeData(
            code,
            this.emptyDepartmentGroupData
          );
          this.departmentGroupList = [];
          this.messageAdvancedError(e);
        } finally {
          this.componentLoading = false;
        }
      },

      // 获取policy
      async fetchPolicySearch () {
        const customIndex = this.panels.findIndex((item) => item.name === 'CustomPerm');
        if (customIndex > -1 && this.curSearchParams.system_id) {
          try {
            const { id, username, type } = this.curData;
            const params = {
              ...this.curSearchParams,
              ...{
                subjectType: type === 'user' ? type : 'department',
                subjectId: type === 'user' ? username : id
              }
            };
            const { code, data } = await this.$store.dispatch(
              'perm/getPersonalPolicySearch',
              params
            );
            this.systemList = this.systemListStorage.filter((item) => item.id === this.curSearchParams.system_id);
            if (this.systemList.length) {
              this.$set(this.systemList[0], 'count', data.length || 0);
            }
            this.$set(this.panels[customIndex], 'count', data.length || 0);
            this.emptyCustomData = formatCodeData(
              code,
              this.emptyCustomData,
              data.length === 0
            );
          } catch (e) {
            console.error(e);
            this.emptyCustomData = formatCodeData(e.code, this.emptyCustomData);
            this.systemList = [];
            this.messageAdvancedError(e);
          }
        } else {
          this.systemList = [];
        }
      },

      async fetchMemberTempByUserSearch () {
        try {
          const { current, limit } = this.curSearchPagination;
          const { id, username, type } = this.curData;
          const params = {
            ...this.curSearchParams,
            ...{
              subjectType: type === 'user' ? type : 'department',
              subjectId: type === 'user' ? username : id
            },
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(
            'perm/getPermGroupsByTempSearch',
            params
          );
          this.panels[2] = Object.assign(
            this.panels[2],
            {
              userCount: data.count || 0
            }
          );
          this.memberTempByUserList = data.results || [];
          this.emptyMemberTemplateData = formatCodeData(code, this.emptyMemberTemplateData, this.panels[2].count === 0);
        } catch (e) {
          console.error(e);
          this.panels[2] = Object.assign(
            this.panels[2],
            {
              userCount: 0
            }
          );
          this.memberTempByUserList = [];
          this.emptyMemberTemplateData = formatCodeData(e.code, this.emptyMemberTemplateData);
          this.messageAdvancedError(e);
        } finally {
          this.componentLoading = false;
        }
      },

      async fetchMemberTempByDepartSearch () {
        try {
          const { current, limit } = this.curSearchPagination;
          const { id, username, type } = this.curData;
          const params = {
            ...this.curSearchParams,
            ...{
              subjectType: type === 'user' ? type : 'department',
              subjectId: type === 'user' ? username : id
            },
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch(
            'perm/getDepartPermGroupsByTempSearch',
            params
          );
          this.panels[2] = Object.assign(
            this.panels[2],
            {
              departCount: data.count || 0
            }
          );
          this.memberTempByDepartList = data.results || [];
          this.emptyMemberTemplateData = formatCodeData(code, this.emptyMemberTemplateData, this.panels[2].count === 0);
        } catch (e) {
          console.error(e);
          this.panels[2] = Object.assign(
            this.panels[2],
            {
              departCount: 0
            }
          );
          this.memberTempByDepartList = [];
          this.emptyMemberTemplateData = formatCodeData(e.code, this.emptyMemberTemplateData);
          this.messageAdvancedError(e);
        } finally {
          this.componentLoading = false;
        }
      },

      async fetchMemberTempByWay () {
        await Promise.all([this.fetchMemberTempByUserSearch(), this.fetchMemberTempByDepartSearch()]);
        const { userCount, departCount } = this.panels[2];
        this.$set(this.panels[2], 'count', userCount + departCount);
      },

      async fetchRemoteTable (isRefreshCurCount = false) {
        // 这里需要拿到所有tab项的total，所以需要调所有接口, 且需要在当前页动态加载tab的label
        const typeMap = {
          GroupPerm: async () => {
            this.emptyData = _.cloneDeep(this.curEmptyData);
            if (isRefreshCurCount) {
              if (this.$refs.childPermRef && this.$refs.childPermRef.length) {
                this.curSearchPagination.limit = this.$refs.childPermRef[0].pageConf.limit;
                this.$refs.childPermRef[0].$refs.groupPermTableRef.clearSelection();
              }
              await this.fetchUserGroupSearch();
            } else {
              await Promise.all([
                this.fetchUserGroupSearch(),
                this.fetchDepartSearch(),
                this.fetchMemberTempByWay(),
                this.fetchPolicySearch()
              ]);
            }
            this.handleRefreshTabData('emptyData');
          },
          DepartmentGroupPerm: async () => {
            this.emptyDepartmentGroupData = _.cloneDeep(this.curEmptyData);
            if (isRefreshCurCount) {
              await this.fetchDepartSearch();
            } else {
              await Promise.all([
                this.fetchDepartSearch(),
                this.fetchUserGroupSearch(),
                this.fetchMemberTempByWay(),
                this.fetchPolicySearch()
              ]);
            }
            this.handleRefreshTabData('emptyDepartmentGroupData');
          },
          MemberTemplateGroupPerm: async () => {
            this.emptyMemberTemplateData = _.cloneDeep(this.curEmptyData);
            if (isRefreshCurCount) {
              await this.fetchMemberTempByWay();
            } else {
              await Promise.all([
                this.fetchMemberTempByWay(),
                this.fetchUserGroupSearch(),
                this.fetchDepartSearch(),
                this.fetchPolicySearch()
              ]);
            }
            this.handleRefreshTabData('emptyMemberTemplateData');
          },
          CustomPerm: async () => {
            this.emptyCustomData = _.cloneDeep(this.curEmptyData);
            if (isRefreshCurCount) {
              await this.fetchPolicySearch();
            } else {
              await Promise.all([
                this.fetchPolicySearch(),
                this.fetchUserGroupSearch(),
                this.fetchDepartSearch(),
                this.fetchMemberTempByWay()
              ]);
            }
            this.handleRefreshTabData('emptyCustomData');
          }
        };
        return typeMap[this.active] ? typeMap[this.active]() : typeMap['GroupPerm']();
      },

      async handleRemoteTable (payload) {
        if (!this.mainContentLoading) {
          this.componentLoading = true;
        }
        const { emptyData, pagination, searchParams, isNoTag } = payload;
        this.isSearchPerm = emptyData.tipType === 'search';
        this.curSearchParams = _.cloneDeep(searchParams);
        this.curSearchPagination = _.cloneDeep(pagination);
        if (!isNoTag) {
          this.curEmptyData = _.cloneDeep(emptyData);
          await this.fetchRemoteTable();
          this.formatCheckGroups();
        }
      },

      // 处理只输入纯文本，不生成tag情况
      async handleInputValue (payload) {
        this.curEmptyData.tipType = payload ? 'search' : '';
        if (payload && !this.curSearchParams.system_id) {
          this.isSearchPerm = true;
          this.$set(this.curSearchParams, 'name', payload);
          await this.fetchRemoteTable();
          this.formatCheckGroups();
        }
      },

      async handleTabChange (tabName) {
        this.active = tabName;
        // 如果active是同一项目
        const searchParams = {
          ...this.$route.query,
          tab: tabName
        };
        if (!['GroupPerm'].includes(tabName)) {
          this.handleSelectGroup([]);
        }
        window.history.replaceState({}, '', `?${buildURLParams(searchParams)}`);
      },

      handleRefreshTabData (payload) {
        let tipType = '';
        if (this.isSearchPerm) {
          tipType = 'search';
        }
        if (this[payload].type === 500) {
          tipType = 'refresh';
        }
        this.curEmptyData = Object.assign({}, this[payload], { tipType });
        this.tabKey = +new Date();
      },

      handleRefreshTable () {
        this.curEmptyData.tipType = '';
        this.isSearchPerm = false;
        this.curSearchParams = {};
        // 重置搜索参数需要去掉tab上的数量
        this.tabKey = +new Date();
      },

      formatRoleMembers (payload) {
        if (payload && payload.length) {
          const hasName = payload.some((v) => v.username);
          if (!hasName) {
            payload = payload.map(v => {
              return {
                username: v,
                readonly: false
              };
            });
          }
        }
        return payload || [];
      },

      formatCheckGroups () {
        const selectList = this.panels[0].selectList.map((item) => item.id.toString());
        setTimeout(() => {
          this.personalGroupList.length
            && this.personalGroupList.forEach((item) => {
              if (
                selectList.includes(item.id.toString())
                && this.$refs.childPermRef
                && this.$refs.childPermRef.length
              ) {
                this.$refs.childPermRef[0].$refs.groupPermTableRef.toggleRowSelection(
                  item,
                  true
                );
              }
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          if (this.departmentGroupList && this.departmentGroupList.length) {
            this.departmentGroupList.forEach((item) => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          }
          if (this.memberTempByUserList && this.memberTempByUserList.length) {
            this.memberTempByUserList.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          }
          if (this.memberTempByDepartList && this.memberTempByDepartList.length) {
            this.memberTempByDepartList.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          }
        }, 0);
      },

      handleSelectGroup (payload) {
        this.$set(this.panels[0], 'selectList', payload);
      },

      // 显示资源实例
      handleShowResourceInstance (data, resItem, resIndex, groupIndex) {
        this.params = {
          system_id: this.applyGroupData.system_id,
          action_id: data.id,
          resource_type_system: resItem.system_id,
          resource_type_id: resItem.type
        };
        this.curResIndex = resIndex;
        this.groupIndex = groupIndex;
        this.resourceInstanceSidesliderTitle = this.$t(
          `m.info['关联侧边栏操作的资源实例']`,
          {
            value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}`
          }
        );
        window.changeAlert = 'iamSidesider';
        this.isShowResourceInstanceSideSlider = true;
      },

      handleEmptyRefresh () {
        this.isSearchPerm = false;
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyRefresh();
      },

      handleEmptyClear () {
        this.isSearchPerm = false;
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyClear();
      }
    }
  };
</script>

<style lang="postcss">
.iam-personal-user-perm-wrapper {
  background-color: #ffffff;
  height: calc(100vh - 120px);
  overflow-y: auto;
  .header {
     padding: 20px;
    padding-bottom: 0;
    .display-name {
      font-size: 16px;
      color: #313238;
    }
    .count,
    .name {
      font-size: 16px;
      color: #c4c6cc;
    }
  }
}
</style>
