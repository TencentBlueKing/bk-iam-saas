<template>
  <div>
    <div class="iam-my-perm-wrapper">
      <div class="header">
        <bk-button
          v-if="!externalSystemsLayout.myPerm.hideApplyBtn"
          data-test-id="myPerm_btn_applyPerm"
          type="button"
          theme="primary"
          style="margin-bottom: 16px;"
          @click="handleGoApply">
          {{ $t(`m.common['申请权限']`) }}
        </bk-button>
        <bk-button
          data-test-id="myPerm_btn_batchRenewal"
          style="margin: 0 6px 16px 6px;"
          :disabled="externalSystemsLayout.myPerm.hideApplyBtn ? isNoExternalRenewal : (isEmpty || isNoRenewal)"
          @click="handleBatchRenewal">
          {{ $t(`m.renewal['权限续期']`) }}
        </bk-button>
        <div
          :class="[
            'info-renewal',
            {
              'external-info-renewal': externalSystemsLayout.myPerm.hideApplyBtn,
              'info-renewal-lang': !['zh-cn'].includes(CUR_LANGUAGE)
            }
          ]"
          style="background: #000"
          v-bk-tooltips="$t(`m.renewal['没有需要续期的权限']`)"
          v-if="externalSystemsLayout.myPerm.hideApplyBtn ? isNoExternalRenewal : (isEmpty || isNoRenewal)"
        >
        </div>
        <bk-button
          v-if="enablePermissionHandover.toLowerCase() === 'true'"
          :disabled="isNoTransfer"
          data-test-id="myPerm_btn_transferPerm"
          type="button"
          style="margin-bottom: 16px;"
          @click="handleGoPermTransfer">
          {{ $t(`m.permTransfer['权限交接']`) }}
        </bk-button>
        <div
          v-if="isNoTransfer"
          :class="[
            'info-sys',
            {
              'external-info-sys': externalSystemsLayout.myPerm.hideApplyBtn,
              'info-sys-lang': !['zh-cn'].includes(CUR_LANGUAGE)
            }
          ]"
          style="background: #000"
          v-bk-tooltips="$t(`m.permTransfer['您还没有权限，无需交接']`)">
        </div>
        <bk-button
          v-if="enableTemporaryPolicy.toLowerCase() === 'true'"
          data-test-id="myPerm_btn_temporaryPerm"
          type="button"
          style="margin-bottom: 16px;"
          @click="handleGoApplyProvisionPerm">
          {{ $t(`m.perm['临时权限申请']`) }}
        </bk-button>
      </div>
      <div
        v-if="externalSystemsLayout.myPerm.hideApplyBtn ? !isNoExternalRenewal : !isNoRenewal"
        :class="[
          'redCircle',
          {
            'redCircle-lang': !['zh-cn'].includes(CUR_LANGUAGE),
            'external-redCircle': externalSystemsLayout.myPerm.hideApplyBtn,
            'external-redCircle-lang': !['zh-cn'].includes(CUR_LANGUAGE)
              && externalSystemsLayout.myPerm.hideApplyBtn
          }
        ]"
      />
      <template>
        <template v-if="isEmpty">
          <div class="empty-wrapper">
            <ExceptionEmpty
              style="background: #f5f6fa"
              :empty-text="$t(`m.common['您还没有任何权限']`)"
            />
          </div>
        </template>
        <template v-else>
          <div>
            <IamResourceCascadeSearch
              ref="iamResourceSearchRef"
              :active="active"
              :search-select-place-holder="$t(`m.perm['输入用户组名、描述等按回车键进行搜索']`)"
              @on-remote-table="handleRemoteTable"
              @on-refresh-table="handleRefreshTable"
              @on-input-value="handleInputValue"
            />
          </div>
          <bk-tab
            ref="tabRef"
            type="unborder-card"
            ext-cls="iam-my-perm-tab-cls"
            :active.sync="active"
            :key="tabKey"
            @tab-change="handleTabChange">
            <bk-tab-panel
              v-for="(panel, index) in panels"
              v-bind="panel"
              :data-test-id="`myPerm_tabPanel_${panel.name}`"
              :key="index">
              <template slot="label">
                <span class="panel-name">
                  <span>{{ panel.label }}</span>
                  <span
                    v-if="curSearchParams && Object.keys(curSearchParams).length">
                    ({{panel.count}})
                  </span>
                </span>
              </template>
              <div
                class="content-wrapper"
                v-bkloading="{ isLoading: componentLoading, opacity: 1 }">
                <component
                  v-if="active === panel.name"
                  ref="childPermRef"
                  :is="active"
                  :component-loading="componentLoading"
                  :total-count="panel.count"
                  :personal-group-list="personalGroupList"
                  :system-list="systemList"
                  :tep-system-list="teporarySystemList"
                  :department-group-list="departmentGroupList"
                  :member-temp-by-user-list="memberTempByUserList"
                  :member-temp-by-depart-list="memberTempByDepartList"
                  :member-temp-by-user-count="panels[2].userCount"
                  :member-temp-by-depart-count="panels[2].departCount"
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
        </template>
      </template>
    </div>
    <div
      :class="[
        'custom-footer-wrapper',
        { 'custom-footer-wrapper-no-perm': isEmpty },
        { 'hidden': isSubEnv || externalSystemsLayout.myPerm.hideApplyBtn }
      ]"
    >
      <the-footer />
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData } from '@/common/util';
  import { bus } from '@/common/bus';
  import CustomPerm from './custom-perm/index.vue';
  import TeporaryCustomPerm from './teporary-custom-perm/index.vue';
  import GroupPerm from './group-perm/index.vue';
  import DepartmentGroupPerm from './department-group-perm/index.vue';
  import MemberTemplateGroupPerm from './member-template-group-perm/index.vue';
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';
  import theFooter from '@/components/footer/index.vue';

  export default {
    name: 'MyPerm',
    components: {
      CustomPerm,
      TeporaryCustomPerm,
      GroupPerm,
      DepartmentGroupPerm,
      MemberTemplateGroupPerm,
      IamResourceCascadeSearch,
      theFooter
    },
    data () {
      return {
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
            userCount: 0,
            departCount: 0,
            selectList: []
          },
          {
            name: 'MemberTemplateGroupPerm',
            label: this.$t(`m.perm['所属人员模板用户组权限']`),
            empty: 'emptyMemberTemplateData',
            count: 0,
            selectList: []
          },
          {
            name: 'CustomPerm',
            label: this.$t(`m.approvalProcess['自定义权限']`),
            empty: 'emptyCustomData',
            count: 0,
            selectList: []
          }
          // {
          //     name: 'TeporaryCustomPerm', label: this.$t(`m.myApply['临时权限']`)
          // }
        ],
        active: 'GroupPerm',
        isEmpty: false,
        isNoRenewal: false,
        isNoExternalRenewal: false,
        isNoTransfer: false,
        soonGroupLength: 0,
        soonPermLength: 0,
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
        emptyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        },
        emptyDepartmentGroupData: {},
        emptyTemporarySystemData: {},
        emptyCustomData: {},
        emptyMemberTemplateData: {},
        curEmptyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        },
        enablePermissionHandover: window.ENABLE_PERMISSION_HANDOVER,
        enableTemporaryPolicy: window.ENABLE_TEMPORARY_POLICY,
        enableGroupInstanceSearch: window.ENABLE_GROUP_INSTANCE_SEARCH.toLowerCase() === 'true',
        CUR_LANGUAGE: window.CUR_LANGUAGE,
        confirmDialogTitle: this.$t(`m.verify['admin无需申请权限']`),
        isShowConfirmDialog: false,
        componentLoading: false,
        isSearchPerm: false,
        actionIdError: false,
        searchTypeError: false,
        resourceTypeError: false,
        resourceInstanceError: false,
        isShowResourceInstanceSideSlider: false,
        resourceInstanceSideSliderTitle: '',
        tabKey: 'tab-key'
      };
    },
    computed: {
      ...mapGetters(['externalSystemsLayout', 'externalSystemId', 'roleList', 'mainContentLoading'])
    },
    watch: {
      '$route': {
        handler (value) {
          const { tab } = value.query;
          if (tab) {
            this.active = tab;
          }
        },
        immediate: true
      },
      externalSystemsLayout: {
        handler (value) {
          if (value.myPerm.hideCustomTab) {
            this.panels.splice(3, 1);
          }
        },
        immediate: true,
        deep: true
      },
      active: {
        handler (value) {
          // 因为同时调了很多接口，所以需要对应的空配置内容
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
      // if (this.enableTemporaryPolicy.toLowerCase() === 'true') {
      //   this.panels.push({
      //     name: 'TeporaryCustomPerm',
      //     label: this.$t(`m.myApply['临时权限']`)
      //   });
      // }
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-perm-tab-count');
      });
      bus.$on('on-perm-tab-count', (payload) => {
        const { active, count } = payload;
        const panelIndex = this.panels.findIndex(item => item.name === active);
        if (panelIndex > -1) {
          if (active === this.active && count !== this.panels[panelIndex].count) {
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
      async fetchPageData () {
        await this.fetchData();
      },

      async fetchData (isLoading = false, limit = 10, page = 1) {
        this.componentLoading = isLoading;
        const hideApplyBtn = this.externalSystemsLayout.myPerm.hideApplyBtn;
        const userGroupParams = {
          page_size: limit,
          page
        };
        if (this.externalSystemId) {
          userGroupParams.system_id = this.externalSystemId;
        }
        const externalParams = userGroupParams.system_id ? { system_id: userGroupParams.system_id } : '';
        const requestList = [
          this.$store.dispatch('perm/getPersonalGroups', userGroupParams),
          this.$store.dispatch('permApply/getHasPermSystem', externalParams),
          this.$store.dispatch('renewal/getExpireSoonGroupWithUser', userGroupParams),
          this.$store.dispatch('renewal/getExpireSoonPerm', externalParams),
          this.$store.dispatch('permApply/getTeporHasPermSystem', externalParams),
          this.$store.dispatch('perm/getDepartMentsPersonalGroups', externalParams)
        ];
        if (hideApplyBtn) {
          requestList[1] = {};
          requestList[4] = {};
        }
        try {
          const [
            { code: personalGroupCode, data: personalGroupData },
            { code: emptyCustomCode, data: customData },
            { data: data3 },
            { data: data4 },
            { code: teporarySystemCode, data: teporarySystemData },
            { code: departmentGroupCode, data: departmentGroupData }
          ] = await Promise.all(requestList);

          const personalGroupList = personalGroupData && personalGroupData.results ? personalGroupData.results : [];
          this.personalGroupList.splice(0, this.personalGroupList.length, ...personalGroupList);
          this.$set(this.panels[0], 'count', personalGroupData.count || 0);
          this.emptyData = formatCodeData(personalGroupCode, this.emptyData, this.personalGroupList.length === 0);

          const systemList = customData || [];
          this.systemList.splice(0, this.systemList.length, ...systemList);
          this.systemListStorage = _.cloneDeep(systemList);
          this.emptyCustomData = formatCodeData(emptyCustomCode, this.emptyCustomData, this.systemList.length === 0);

          const teporarySystemList = teporarySystemData || [];
          this.teporarySystemList.splice(0, this.teporarySystemList.length, ...teporarySystemList);
          this.emptyTemporarySystemData
            = formatCodeData(teporarySystemCode, this.emptyTemporarySystemData, this.teporarySystemList.length === 0);

          const departmentGroupList = departmentGroupData || [];
          this.departmentGroupList.splice(0, this.departmentGroupList.length, ...departmentGroupList);
          this.emptyDepartmentGroupData
            = formatCodeData(departmentGroupCode, this.emptyDepartmentGroupData, this.departmentGroupList.length === 0);

          this.formatCheckGroups();
          this.soonGroupLength = data3 && data3.results ? data3.results.length : 0;
          this.soonPermLength = data4 ? data4.length : 0;
          this.isNoRenewal = this.soonGroupLength < 1 && this.soonPermLength < 1;
          this.isNoExternalRenewal = this.soonGroupLength < 1;
          this.isNoTransfer = hideApplyBtn ? !personalGroupList.length
            : (!personalGroupList.length && !systemList.length && !this.roleList.length);

          await this.fetchMemberTempPermData(userGroupParams);
          this.isEmpty = personalGroupList.length < 1 && systemList.length < 1
            && teporarySystemList.length < 1 && departmentGroupList.length < 1
            && this.memberTempByUserList.length < 1 && this.memberTempByDepartList.length < 1;
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
          const emptyField = this.panels.find(item => item.name === this.active);
          if (emptyField) {
            this[emptyField.empty] = formatCodeData(e.code, this[emptyField.empty]);
          }
        } finally {
          this.componentLoading = false;
        }
      },

      // 获取所属人员模板用户组权限
      async fetchMemberTempPermData (userGroupParams) {
        const { page, page_size } = userGroupParams;
        const params = {
          // eslint-disable-next-line camelcase
          offset: page_size * (page - 1),
          limit: page_size
        };
        if (this.externalSystemId) {
          params.system_id = this.externalSystemId;
          params.hidden = false;
        }
        const list = [
          this.$store.dispatch('perm/getMemberTempByUser', params),
          this.$store.dispatch('perm/getMemberTempByDepart', params)
        ];
        try {
          const [
            { code: memberTempByUserCode, data: memberTempByUserData },
            { code: memberTempByDepartCode, data: memberTempByDepartData }
          ] = await Promise.all(list);

          const memberTempByUserCount = memberTempByUserData.count || 0;
          this.memberTempByUserList = memberTempByUserData.results || [];

          const memberTempByDepartCount = memberTempByDepartData.count || 0;
          this.memberTempByDepartList = memberTempByDepartData.results || [];

          this.panels[2] = Object.assign(this.panels[2], {
            userCount: memberTempByUserCount,
            departCount: memberTempByDepartCount,
            count: memberTempByUserCount + memberTempByDepartCount
          });

          this.emptyDepartmentGroupData = formatCodeData(
            memberTempByUserCode || memberTempByDepartCode,
            this.emptyMemberTemplateData,
            this.panels[2].count === 0
          );

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
        } catch (e) {
          this.messageAdvancedError(e);
          this.memberTempByUserList = [];
          this.memberTempByDepartList = [];
          this.panels[2] = Object.assign(this.panels[2], {
            userCount: 0,
            departCount: 0,
            count: 0
          });
          this.emptyDepartmentGroupData = formatCodeData(e.code, this.emptyMemberTemplateData);
          if (['MemberTemplateGroupPerm'].includes(this.active)) {
            this.curEmptyData = _.cloneDeep(this.emptyMemberTemplateData);
          }
        }
      },

      // 获取搜索的个人用户组
      async fetchUserGroupSearch () {
        try {
          const { current, limit } = this.curSearchPagination;
          const params = {
            ...this.curSearchParams,
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch('perm/getUserGroupSearch', params);
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
        const params = {
          ...this.curSearchParams,
          limit,
          offset: limit * (current - 1)
        };
        if (this.externalSystemId) {
          params.system_id = this.externalSystemId;
          params.hidden = false;
        }
        try {
          const { code, data } = await this.$store.dispatch('perm/getDepartGroupSearch', params);
          const { count, results } = data;
          this.departmentGroupList = results || [];
          this.$set(this.panels[1], 'count', count || 0);
          this.emptyDepartmentGroupData = formatCodeData(code, this.emptyDepartmentGroupData, results.length === 0);
        } catch (e) {
          const { code } = e;
          this.emptyDepartmentGroupData = formatCodeData(code, this.emptyDepartmentGroupData);
          this.departmentGroupList = [];
          this.messageAdvancedError(e);
        } finally {
          this.componentLoading = false;
        }
      },

      // 获取policy
      async fetchPolicySearch () {
        const customIndex = this.panels.findIndex(item => item.name === 'CustomPerm');
        if (customIndex > -1 && this.curSearchParams.system_id) {
          try {
            const { code, data } = await this.$store.dispatch('perm/getPoliciesSearch', this.curSearchParams);
            this.systemList = this.systemListStorage.filter((item) => item.id === this.curSearchParams.system_id);
            this.$set(this.panels[customIndex], 'count', data.length || 0);
            this.emptyCustomData = formatCodeData(code, this.emptyCustomData, data.length === 0);
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

      // 获取通过用户加入的人员模块的用户组权限
      async fetchMemberTempByUserSearch () {
        try {
          const { current, limit } = this.curSearchPagination;
          const params = {
            ...this.curSearchParams,
            limit,
            offset: limit * (current - 1)
          };
          if (this.externalSystemId) {
            params.system_id = this.externalSystemId;
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch('perm/getMemberTempByUserSearch', params);
          this.memberTempByUserList = data.results || [];
          this.$set(this.panels[2], 'userCount', data.count || 0);
          this.emptyMemberTemplateData = formatCodeData(code, this.emptyMemberTemplateData, data.count === 0);
        } catch (e) {
          console.error(e);
          this.memberTempByUserList = [];
          this.$set(this.panels[2], 'userCount', 0);
          this.emptyMemberTemplateData = formatCodeData(e.code, this.emptyMemberTemplateData);
          this.messageAdvancedError(e);
        } finally {
          this.componentLoading = false;
        }
      },

      // 获取通过组织加入的人员模块的用户组权限
      async fetchMemberTempByDepartSearch () {
        const { current, limit } = this.curSearchPagination;
        const params = {
          ...this.curSearchParams,
          limit,
          offset: limit * (current - 1)
        };
        if (this.externalSystemId) {
          params.system_id = this.externalSystemId;
          params.hidden = false;
        }
        try {
          const { code, data } = await this.$store.dispatch('perm/getMemberTempByDepartSearch', params);
          const { count, results } = data;
          this.memberTempByDepartList = results || [];
          this.$set(this.panels[2], 'departCount', count || 0);
          this.emptyMemberTemplateData = formatCodeData(code, this.emptyMemberTemplateData, results.length === 0);
        } catch (e) {
          this.messageAdvancedError(e);
          this.emptyMemberTemplateData = formatCodeData(e.code, this.emptyMemberTemplateData);
          this.memberTempByDepartList = [];
          this.$set(this.panels[2], 'departCount', 0);
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
            if (this.$refs.childPermRef && this.$refs.childPermRef.length) {
              this.$nextTick(() => {
                this.$refs.childPermRef[0].$refs.groupPermTableRef.clearSelection();
              });
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
        this.fetchData(true);
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
        const selectList = this.panels[0].selectList.map(item => item.id.toString());
        setTimeout(() => {
          this.personalGroupList.length && this.personalGroupList.forEach(item => {
            item.role_members = this.formatRoleMembers(item.role_members);
            if (selectList.includes(item.id.toString())
              && this.$refs.childPermRef
              && this.$refs.childPermRef.length) {
              this.$refs.childPermRef[0].$refs.groupPermTableRef.toggleRowSelection(item, true);
            }
          });
          if (this.departmentGroupList && this.departmentGroupList.length) {
            this.departmentGroupList.forEach(item => {
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
        this.resourceInstanceSidesliderTitle = this.$t(`m.info['关联侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}` });
        window.changeAlert = 'iamSidesider';
        this.isShowResourceInstanceSideSlider = true;
      },

      handleGoApply () {
        this.$router.push({
          name: 'applyJoinUserGroup'
        });
      },

      handleBatchRenewal () {
        if (this.soonGroupLength > 0 && this.soonPermLength < 1) {
          this.$router.push({
            name: 'permRenewal',
            query: {
              tab: 'group'
            }
          });
        } else if (this.soonPermLength > 0 && this.soonGroupLength < 1) {
          this.$router.push({
            name: 'permRenewal',
            query: {
              tab: 'custom'
            }
          });
        } else if (this.soonPermLength > 0 && this.soonGroupLength > 0) {
          this.$router.push({
            name: 'permRenewal',
            query: {
              tab: this.active === 'GroupPerm' ? 'group' : 'custom'
            }
          });
        }
      },

      // 权限交接
      handleGoPermTransfer () {
        this.$router.push({
          name: 'permTransfer'
        });
      },

      handleGoApplyProvisionPerm () {
        this.$router.push({
          name: 'applyProvisionPerm'
        });
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
    .iam-my-perm-wrapper {
        position: relative;
        .header {
            position: relative;
        }
        .content-wrapper {
            /* 20 + 20 + 42 + 24 + 24 + 61 + 48 */
            min-height: calc(100vh - 325px);
        }
        .empty-wrapper {
            position: absolute;
            top: 200px;
            left: 50%;
            transform: translate(-50%, -50%);
            img {
                width: 120px;
            }
            .empty-tips {
                position: relative;
                top: -25px;
                font-size: 12px;
                color: #c4c6cc;
                text-align: center;
            }
        }
        .redCircle {
            position: relative;
            top: -50px;
            right: -180px;
            width: 10px;
            height: 10px;
            background-color: red;
            border-radius: 50%;
            &-lang {
                right: -340px;
            }
            &.external-redCircle {
                right: -90px;
                &-lang {
                  right: -160px;
                }
            }
        }
    }
    .iam-my-perm-tab-cls {
        background: #ffffff;
        margin-bottom: 50px;
    }
    .icon-info-renewal {
        position: absolute;
        top: -5px;
        left: 176px;
    }
    .info-renewal {
        top: -5px;
        left: 100px;
        position: absolute;
        width: 90px;
        height: 40px;
        opacity: 0;
        cursor: no-drop;
        &.info-renewal-lang {
            left: 200px;
        }
        &.external-info-renewal {
            left: 0;
            &.info-renewal-lang {
                left: 50px;
            }
        }
    }
    .info-sys {
        top: -5px;
        left: 198px;
        position: absolute;
        width: 90px;
        height: 40px;
        opacity: 0;
        cursor: no-drop;
        &.info-sys-lang {
            left: 400px;
        }
    }

    .external-info-sys {
        left: 100px;
        &.info-sys-lang {
            left: 200px;
        }
    }

    .custom-footer-wrapper {
      &.custom-footer-wrapper-no-perm {
        .footer-content {
          position: absolute;
          left: 50%;
          bottom: 30px;
          transform: translate(-50%, 0px);
        }
      }
      &.hidden {
        display: none;
      }
    }
</style>
