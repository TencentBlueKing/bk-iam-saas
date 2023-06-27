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
      <div :class="[
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
      <bk-tab
        v-else
        :active="active"
        type="unborder-card"
        ext-cls="iam-my-perm-tab-cls"
        @tab-change="handleTabChange">
        <bk-tab-panel
          v-for="(panel, index) in panels"
          :data-test-id="`myPerm_tabPanel_${panel.name}`"
          v-bind="panel"
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
              @refresh="fetchData"
            ></component>
          </div>
        </bk-tab-panel>
      </bk-tab>
    </template>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData } from '@/common/util';
  import CustomPerm from './custom-perm/index.vue';
  import TeporaryCustomPerm from './teporary-custom-perm/index.vue';
  import GroupPerm from './group-perm/index.vue';
  import { mapGetters } from 'vuex';
  import DepartmentGroupPerm from './department-group-perm/index.vue';

  export default {
    name: 'MyPerm',
    components: {
      CustomPerm,
      TeporaryCustomPerm,
      GroupPerm,
      DepartmentGroupPerm
    },
    data () {
      return {
        componentLoading: true,
        panels: [
          {
            name: 'GroupPerm',
            label: this.$t(`m.perm['用户组权限']`),
            empty: 'emptyData'
          },
          {
            name: 'DepartmentGroupPerm',
            label: this.$t(`m.perm['所属组织用户组权限']`),
            empty: 'emptyData6'
          },
          {
            name: 'CustomPerm',
            label: this.$t(`m.approvalProcess['自定义权限']`),
            empty: 'emptyData2'
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
        enablePermissionHandover: window.ENABLE_PERMISSION_HANDOVER,
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
        enableTemporaryPolicy: window.ENABLE_TEMPORARY_POLICY,
        CUR_LANGUAGE: window.CUR_LANGUAGE
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
            this.curEmptyData = this[emptyField.empty];
          }
        },
        immediate: true
      }
    },
    created () {
      this.emptyData2 = _.cloneDeep(this.emptyData);
      this.emptyData5 = _.cloneDeep(this.emptyData);
      this.emptyData6 = _.cloneDeep(this.emptyData);
      const query = this.$route.query;
      if (query.tab) {
        this.active = query.tab;
      }
      if (this.enableTemporaryPolicy.toLowerCase() === 'true') {
        this.panels.push({
          name: 'TeporaryCustomPerm',
          label: this.$t(`m.myApply['临时权限']`)
        });
      }
    },
    methods: {
      async fetchPageData () {
        await this.fetchData();
      },

      async handleTabChange (tabName) {
        this.active = tabName;
        await this.fetchData();
        const searchParams = {
                    ...this.$route.query,
                    tab: tabName
        };
        window.history.replaceState({}, '', `?${buildURLParams(searchParams)}`);
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
            { code: code1, data: data1 },
            { code: code2, data: data2 },
            { data: data3 },
            { data: data4 },
            { code: code5, data: data5 },
            { code: code6, data: data6 }
          ] = await Promise.all(requestList);
                    
          const personalGroupList = data1.results || [];
          this.personalGroupList.splice(0, this.personalGroupList.length, ...personalGroupList);
          this.emptyData = formatCodeData(code1, this.emptyData, this.personalGroupList.length === 0);
                    
          const systemList = data2 || [];
          this.systemList.splice(0, this.systemList.length, ...systemList);
          this.emptyData2 = formatCodeData(code2, this.emptyData2, this.systemList.length === 0);

          const teporarySystemList = data5 || [];
          this.teporarySystemList.splice(0, this.teporarySystemList.length, ...teporarySystemList);
          this.emptyData5 = formatCodeData(code5, this.emptyData5, this.teporarySystemList.length === 0);

          const departmentGroupList = data6 || [];
          this.departmentGroupList.splice(0, this.departmentGroupList.length, ...departmentGroupList);
          this.emptyData6 = formatCodeData(code6, this.emptyData6, this.departmentGroupList.length === 0);

          this.isEmpty = personalGroupList.length < 1 && systemList.length < 1
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
        background: #fff;
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
