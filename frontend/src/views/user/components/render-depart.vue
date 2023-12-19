<template>
  <div class="iam-depart-perm-wrapper" v-if="isShowPage">
    <div class="header">
      <template v-if="isDepart">
        <span class="display-name">{{ curData.name }}</span>
        <!-- <span class="count">({{ curData.count }})</span> -->
      </template>
      <template v-else>
        <span class="display-name">{{ curData.username }}</span>
        <span class="name" v-if="isExistName">({{ curData.name }})</span>
      </template>
    </div>
    <div>
      <IamResourceCascadeSearch
        ref="iamResourceSearchRef"
        :active="active"
        :custom-select-width="customSelectWidth"
        :min-select-width="'165px'"
        :max-select-width="'200px'"
        @on-remote-table="handleRemoteTable"
        @on-refresh-table="handleRefreshTable"
        @on-input-value="handleInputValue"
      />
    </div>
    <div class="table-list-wrapper">
      <bk-tab
        type="unborder-card"
        ext-cls="iam-user-tab-cls"
        :active.sync="active"
        :key="tabKey"
        @tab-change="handleTabChange"
      >
        <bk-tab-panel v-for="(panel, index) in panels" v-bind="panel" :key="index">
          <template slot="label">
            <span class="panel-name">
              <span>{{ panel.label }}</span>
              <span style="color: ##3a84ff" v-if="curSearchParams && Object.keys(curSearchParams).length">
                ({{ panel.count }})
              </span>
            </span>
          </template>
          <component
            v-if="panel.name === active"
            ref="childPermRef"
            :key="componentsKey"
            :is="curCom"
            :data="curData"
            :total-count="panel.count"
            :personal-group-list="personalGroupList"
            :member-temp-by-user-list="panel.userList"
            :member-temp-by-user-count="panel.userCount"
            :member-temp-by-depart-list="panel.departList"
            :member-temp-by-depart-count="panel.departCount"
            :empty-data="curEmptyData"
            :cur-search-params="curSearchParams"
            :cur-search-pagination="curSearchPagination"
            :is-search-perm="isSearchPerm"
            :is-only-perm="true"
            :check-group-list="panels[0].selectList"
            @on-select-group="handleSelectGroup"
            @on-clear="handleEmptyClear"
            @on-refresh="handleEmptyRefresh"
            @on-init="handleComInit"
          />
        </bk-tab-panel>
      </bk-tab>
    </div>
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import { bus } from '@/common/bus';
  import { formatCodeData } from '@/common/util';
  import JoinedUserGroup from './joined-user-group';
  import MemberTemplateGroupPerm from '@/views/perm/member-template-group-perm/index.vue';
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';
  export default {
    name: '',
    components: {
      JoinedUserGroup,
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
            departList: [],
            selectList: []
          },
          {
            name: 'MemberTemplateGroupPerm',
            label: this.$t(`m.perm['所属人员模板用户组权限']`),
            empty: 'emptyMemberTemplateData',
            count: 0,
            userCount: 0,
            userList: [],
            departCount: 0,
            departList: [],
            selectList: []
          }
        ],
        active: 'GroupPerm',
        curCom: 'JoinedUserGroup',
        componentsKey: -1,
        tabKey: -1,
        isSearchPerm: false,
        actionIdError: false,
        searchTypeError: false,
        resourceTypeError: false,
        resourceInstanceError: false,
        isShowResourceInstanceSideSlider: false,
        resourceInstanceSideSliderTitle: '',
        curSearchParams: {},
        curSearchPagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        emptyMemberTemplateData: {
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
        personalGroupList: [],
        customSelectWidth: window.innerWidth <= 1520 ? '160px' : '240px'
      };
    },
    computed: {
      ...mapGetters(['externalSystemId', 'roleList', 'mainContentLoading']),
      isDepart () {
        return this.curData.type === 'depart';
      },
      isExistName () {
        return this.curData.type === 'user' && this.curData.name !== '';
      },

      isShowPage () {
        return Object.keys(this.params).length > 0;
      }
    },
    watch: {
      params: {
        handler (value) {
          if (Object.keys(value).length > 0) {
            this.fetchDetailData(value);
          }
        },
        immediate: true
      },
      active (value) {
        const comMap = {
          perm: 'DepartPerm',
          GroupPerm: 'JoinedUserGroup',
          MemberTemplateGroupPerm: 'MemberTemplateGroupPerm'
        };
        this.curCom = comMap[value];
        this.componentsKey = +new Date();
        const emptyField = this.panels.find(item => item.name === value);
        if (emptyField) {
          this.curEmptyData = _.cloneDeep(this[emptyField.empty]);
        }
      }
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
        }
      });
    },
    methods: {
      handleComInit (payload) {
        this.$emit('on-init', payload);
      },

      handleSelectGroup (payload) {
        this.$set(this.panels[0], 'selectList', payload);
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
          if (this.panels[1].departList.length) {
            this.panels[1].departList.forEach(item => {
              item.role_members = this.formatRoleMembers(item.role_members);
            });
          }
        }, 0);
      },

      fetchDetailData (value) {
        this.active = 'GroupPerm';
        this.curCom = 'JoinedUserGroup';
        this.curEmptyData.tipType = '';
        this.isSearchPerm = false;
        this.curSearchParams = {};
        this.handleEmptyClear();
        this.componentsKey = +new Date();
        this.curData = _.cloneDeep(value);
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
            'perm/getPermGroupsByTempSearch',
            params
          );
          this.panels[1] = Object.assign(
            this.panels[1],
            {
              departList: data.results || [],
              departCount: data.count || 0
            }
          );
          this.emptyMemberTemplateData = formatCodeData(
            code,
            this.emptyMemberTemplateData,
            this.panels[1].departCount === 0
          );
        } catch (e) {
          console.error(e);
          this.panels[1] = Object.assign(
            this.panels[1],
            {
              departList: [],
              departCount: 0
            }
          );
          this.emptyMemberTemplateData = formatCodeData(e.code, this.emptyMemberTemplateData);
          this.messageAdvancedError(e);
        } finally {
          this.componentLoading = false;
        }
      },

      async fetchMemberTempByWay () {
        await Promise.all([this.fetchMemberTempByDepartSearch()]);
        const { departCount } = this.panels[1];
        this.$set(this.panels[1], 'count', departCount);
        this.formatCheckGroups();
      },

      async fetchRemoteTable (isRefreshCurCount = false) {
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
                this.fetchMemberTempByWay()
              ]);
            }
            this.handleRefreshTabData('emptyData');
          },
          MemberTemplateGroupPerm: async () => {
            this.emptyMemberTemplateData = _.cloneDeep(this.curEmptyData);
            await Promise.all([
              this.fetchMemberTempByWay(),
              this.fetchUserGroupSearch()
            ]);
            this.handleRefreshTabData('emptyMemberTemplateData');
          }
        };
        return typeMap[this.active] ? typeMap[this.active]() : typeMap['GroupPerm']();
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
        this.tabKey = +new Date();
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

<style lang="postcss" scoped>
.iam-depart-perm-wrapper {
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
  .table-list-wrapper {
    /* margin-top: 20px; */
    .iam-user-tab-cls {
      .bk-tab-section {
        padding: 20px 0 0 0;
      }
    }
  }
}
</style>
