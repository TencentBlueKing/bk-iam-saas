<template>
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
        :disabled="!systemList.length && !teporarySystemList.length"
        data-test-id="myPerm_btn_transferPerm"
        type="button"
        style="margin-bottom: 16px;"
        @click="handleGoPermTransfer">
        {{ $t(`m.permTransfer['权限交接']`) }}
      </bk-button>
      <div
        v-if="!systemList.length && !teporarySystemList.length"
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
            @on-remote-table="handleRemoteTable"
            @on-refresh-table="handleRefreshTable"
          />
        </div>
        <bk-tab
          :active.sync="active"
          type="unborder-card"
          ext-cls="iam-my-perm-tab-cls"
          @tab-change="handleTabChange">
          <bk-tab-panel
            v-for="(panel, index) in panels"
            :data-test-id="`myPerm_tabPanel_${panel.name}`"
            v-bind="panel"
            :label="['search'].includes(curEmptyData.tipType) ? `${panel.label}(${panel.count})` : panel.label "
            :key="index">
            <div class="content-wrapper" v-bkloading="{ isLoading: componentLoading, opacity: 1 }">
              <component
                v-if="!componentLoading && active === panel.name"
                :is="active"
                :personal-group-list="personalGroupList"
                :system-list="systemList"
                :tep-system-list="teporarySystemList"
                :department-group-list="departmentGroupList"
                :ref="panel.name"
                :empty-data="curEmptyData"
                :cur-search-params="curSearchParams"
                :cur-search-pagination="curSearchPagination"
                @refresh="fetchData"
                @on-clear="handleEmptyClear"
                @on-refresh="handleEmptyRefresh"
              ></component>
            </div>
          </bk-tab-panel>
        </bk-tab>
      </template>
    </template>
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
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';

  export default {
    name: 'MyPerm',
    components: {
      CustomPerm,
      TeporaryCustomPerm,
      GroupPerm,
      DepartmentGroupPerm,
      IamResourceCascadeSearch
    },
    data () {
      return {
        componentLoading: true,
        panels: [
          {
            name: 'GroupPerm',
            label: this.$t(`m.perm['用户组权限']`),
            empty: 'emptyData',
            count: 0
          },
          {
            name: 'DepartmentGroupPerm',
            label: this.$t(`m.perm['所属组织用户组权限']`),
            empty: 'emptyDepartmentGroupData',
            count: 0
          },
          {
            name: 'CustomPerm',
            label: this.$t(`m.approvalProcess['自定义权限']`),
            empty: 'emptyCustomData',
            count: 0
          }
          // {
          //     name: 'TeporaryCustomPerm', label: this.$t(`m.myApply['临时权限']`)
          // }
        ],
        active: 'GroupPerm',
        isEmpty: false,
        isNoRenewal: false,
        isNoExternalRenewal: false,
        soonGroupLength: 0,
        soonPermLength: 0,
        personalGroupList: [],
        systemList: [],
        teporarySystemList: [],
        departmentGroupList: [],
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
        emptyDepartmentGroupData: {},
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
        isShowConfirmDialog: false,
        confirmDialogTitle: this.$t(`m.verify['admin无需申请权限']`),
        actionIdError: false,
        searchTypeError: false,
        resourceTypeError: false,
        resourceInstanceError: false,
        isShowResourceInstanceSideSlider: false,
        resourceInstanceSideSliderTitle: '',
        contentWidth: window.innerWidth <= 1440 ? '200px' : '240px'
      };
    },
    computed: {
      ...mapGetters(['externalSystemsLayout', 'externalSystemId'])
    },
    watch: {
      externalSystemsLayout: {
        handler (value) {
          if (value.myPerm.hideCustomTab) {
            this.panels.splice(2, 1);
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
      const query = this.$route.query;
      if (query.tab) {
        this.active = query.tab;
      }
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
          this.$set(this.panels[panelIndex], 'count', count);
        }
      });
    },
    methods: {
      async fetchPageData () {
        await this.fetchData();
      },

      async fetchData () {
        this.componentLoading = true;
        const userGroupParams = {
          page_size: 10,
          page: 1
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
          // this.fetchPermGroups(),
          // this.fetchSystems(),
          // this.fetchSoonGroupWithUser(),
          // this.fetchSoonPerm()
        ];
        try {
          const [
            { code: personalGroupCode, data: personalGroupData },
            { code: emptyCustomCode, data: customData },
            { data: data3 },
            { data: data4 },
            { code: teporarySystemCode, data: teporarySystemData },
            { code: departmentGroupCode, data: departmentGroupData }
          ] = await Promise.all(requestList);
                    
          const personalGroupList = personalGroupData.results || [];
          this.personalGroupList.splice(0, this.personalGroupList.length, ...personalGroupList);
          this.emptyData = formatCodeData(personalGroupCode, this.emptyData, this.personalGroupList.length === 0);
                    
          const systemList = customData || [];
          this.systemList.splice(0, this.systemList.length, ...systemList);
          this.emptyCustomData = formatCodeData(emptyCustomCode, this.emptyCustomData, this.systemList.length === 0);

          const teporarySystemList = teporarySystemData || [];
          this.teporarySystemList.splice(0, this.teporarySystemList.length, ...teporarySystemList);
          this.emptyTemporarySystemData
            = formatCodeData(teporarySystemCode, this.emptyTemporarySystemData, this.teporarySystemList.length === 0);

          const departmentGroupList = departmentGroupData || [];
          this.departmentGroupList.splice(0, this.departmentGroupList.length, ...departmentGroupList);
          this.emptyDepartmentGroupData
            = formatCodeData(departmentGroupCode, this.emptyDepartmentGroupData, this.departmentGroupList.length === 0);

          this.isEmpty = personalGroupData.results.length < 1 && customData.length < 1
            && teporarySystemList.length < 1 && departmentGroupList.length < 1;
          this.soonGroupLength = data3.results.length;
          this.soonPermLength = data4.length;
          this.isNoRenewal = this.soonGroupLength < 1 && this.soonPermLength < 1;
          this.isNoExternalRenewal = this.soonGroupLength < 1;
        } catch (e) {
          console.error(e);
          const { code, data, message, statusText } = e;
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: message || data.msg || statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
          // 获取非阻塞且未报错列表接口信息
          await this.fetchAsyncTable(requestList);
          const emptyField = this.panels.find(item => item.name === this.active);
          if (emptyField) {
            this[emptyField.empty] = formatCodeData(code, this[emptyField.empty]);
          }
        } finally {
          this.componentLoading = false;
        }
      },
            
      async fetchAsyncTable (payload) {
        const errorList = [];
        const res = await Promise.all(payload.map((item, index) => item.catch((e) => {
          errorList.push(index);
        })));
        if (res[0]) {
          const personalGroupList = res[0].data.results || [];
          this.personalGroupList.splice(0, this.personalGroupList.length, ...personalGroupList);
        }

        if (res[1]) {
          const systemList = res[1].data || [];
          this.systemList.splice(0, this.systemList.length, ...systemList);
        }
                    
        if (res[5]) {
          const departmentGroupList = res[5].data || [];
          this.departmentGroupList.splice(0, this.departmentGroupList.length, ...departmentGroupList);
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
          }
          const { code, data } = await this.$store.dispatch('perm/getUserGroupSearch', params);
          this.$set(this.panels[0], 'count', data.count || 0);
          this.emptyData
            = formatCodeData(code, this.emptyData, data.count === 0);
        } catch (e) {
          console.error(e);
          const { code, data, message, statusText } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: message || data.msg || statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
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
        try {
          const { code, data } = await this.$store.dispatch('perm/getDepartGroupSearch', params);
          const { count, results } = data;
          this.$set(this.panels[1], 'count', count || 0);
          this.emptyDepartmentGroupData = formatCodeData(code, this.emptyDepartmentGroupData, results.length === 0);
        } catch (e) {
          const { code, data, message, statusText } = e;
          this.emptyDepartmentGroupData = formatCodeData(code, this.emptyDepartmentGroupData);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: message || data.msg || statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      // 获取policy
      async fetchPolicySearch () {
        try {
          const { code, data } = await this.$store.dispatch('perm/getPoliciesSearch', this.curSearchParams);
          const customIndex = this.panels.findIndex(item => item.name === 'CustomPerm');
          if (customIndex > -1) {
            this.$set(this.panels[customIndex], 'count', data.length || 0);
          }
          this.emptyCustomData = formatCodeData(code, this.emptyCustomData, data.length === 0);
        } catch (e) {
          console.error(e);
          this.emptyCustomData = formatCodeData(e.code, this.emptyCustomData);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      async handleRemoteTable (payload) {
        const { emptyData, pagination, searchParams } = payload;
        this.curSearchParams = _.cloneDeep(searchParams);
        this.curSearchPagination = _.cloneDeep(pagination);
        const typeMap = {
          GroupPerm: async () => {
            this.personalGroupList = [];
            this.emptyData = _.cloneDeep(emptyData);
            await this.fetchDepartSearch();
            await this.fetchPolicySearch();
          },
          DepartmentGroupPerm: async () => {
            this.departmentGroupList = [];
            this.emptyDepartmentGroupData = _.cloneDeep(emptyData);
            await this.fetchUserGroupSearch();
            await this.fetchPolicySearch();
          },
          CustomPerm: async () => {
            this.emptyCustomData = _.cloneDeep(emptyData);
            await this.fetchUserGroupSearch();
            await this.fetchDepartSearch();
          }
        };
        this.curEmptyData = _.cloneDeep(emptyData);
        typeMap[this.active] ? typeMap[this.active]() : typeMap['GroupPerm']();
      },

      async handleRefreshTable () {
        this.curEmptyData.tipType = '';
        this.curSearchParams = {};
        this.fetchData();
      },

      async handleTabChange (tabName) {
        this.active = tabName;
        const searchParams = {
          ...this.$route.query,
          tab: tabName
        };
        window.history.replaceState({}, '', `?${buildURLParams(searchParams)}`);
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
      // fetchSoonGroupWithUser () {
      //     return this.$store.dispatch('renewal/getExpireSoonGroupWithUser')
      // },
      // fetchSoonPerm () {
      //     return this.$store.dispatch('renewal/getExpireSoonPerm')
      // },
      // fetchSystems () {
      //     return this.$store.dispatch('permApply/getHasPermSystem')
      // },

      // fetchPermGroups () {
      //     return this.$store.dispatch('perm/getPersonalGroups')
      // },

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

      formatFormItemWidth () {
        this.contentWidth = window.innerWidth <= 1520 ? '200px' : '240px';
      },
      
      handleEmptyRefresh () {
        // 调用子组件的刷新方法
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyClear();
      },

      handleEmptyClear () {
        // 调用子组件的刷新方法
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
            top: 50%;
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
</style>
