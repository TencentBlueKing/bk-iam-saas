<template>
  <div class="iam-custom-perm-wrapper" v-bkloading="{ isLoading: pageLoading, opacity: 1 }">
    <template v-if="hasPerm">
      <custom-perm-system-policy
        v-for="(sys, sysIndex) in systemPolicyList"
        :key="sys.id"
        :expanded.sync="sys.expanded"
        :ext-cls="sysIndex > 0 ? 'iam-perm-ext-cls' : ''"
        :title="sys.name"
        :one-perm="onePerm"
        :perm-length="isSearchPerm ? totalCount : sys.count"
        :is-all-delete="true"
        @on-delete-all="handleDeleteAll(sys, sysIndex)"
      >
        <perm-table
          ref="customPermTable"
          :key="sys.id"
          :system-id="sys.id"
          :params="data"
          :data="data"
          :cur-search-params="curSearchParams"
          :empty-data="emptyPolicyData"
          :is-search-perm="isSearchPerm"
          @after-delete="handleAfterDelete(...arguments, sysIndex)"
        />
      </custom-perm-system-policy>
    </template>
    <template v-if="isEmpty">
      <div>
        <ExceptionEmpty
          :type="emptyPolicyData.type"
          :empty-text="emptyPolicyData.text"
          :tip-text="emptyPolicyData.tip"
          :tip-type="emptyPolicyData.tipType"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </div>
    </template>
  </div>
</template>

<script>
  import { formatCodeData } from '@/common/util';
  import { bus } from '@/common/bus';
  import CustomPermSystemPolicy from '@/components/custom-perm-system-policy/index.vue';
  import PermTable from './perm-table-edit';
  import PermSystem from '@/model/my-perm-system';
  export default {
    name: '',
    components: {
      CustomPermSystemPolicy,
      PermTable
    },
    props: {
      data: {
        type: Object,
        default: () => {
          return {};
        }
      },
      systemList: {
        type: Array,
        default: () => []
      },
      emptyData: {
        type: Object,
        default: () => {
          return {
            type: 'empty',
            text: '暂无数据',
            tip: '',
            tipType: ''
          };
        }
      },
      curSearchParams: {
        type: Object,
        default: () => {}
      },
      curSearchPagination: {
        type: Object,
        default: () => {
          return {
            current: 1,
            count: 0,
            limit: 10
          };
        }
      },
      isSearchPerm: {
        type: Boolean,
        default: false
      },
      totalCount: {
        type: Number
      }
    },
    data () {
      return {
        isExpanded: false,
        pageLoading: false,
        detailSideslider: {
          isShow: false,
          title: '查看详情'
        },
        onePerm: 0,
        systemPolicyList: [],
        systemListStorage: [],
        emptyPolicyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      /**
       * hasPerm
       */
      hasPerm () {
        return this.systemPolicyList.length > 0 && !this.pageLoading;
      },

      /**
       * isEmpty
       */
      isEmpty () {
        return this.systemPolicyList.length < 1 && !this.pageLoading;
      }
    },
    watch: {
      systemList: {
        handler (v) {
          let list = [...v];
          if (this.isSearchPerm) {
            list = this.systemListStorage.filter((item) => item.id === this.curSearchParams.system_id);
          }
          this.formatSystemData(list);
        },
        immediate: true,
        deep: true
      },
      emptyData: {
        handler (value) {
          this.emptyPolicyData = Object.assign({}, value);
          if (this.isSearchPerm || ['search'].includes(value.tipType)) {
            this.fetchSystemSearch();
          }
        },
        immediate: true
      },
      totalCount: {
        handler (value) {
          if (this.isSearchPerm && this.systemList.length) {
            this.$set(this.systemPolicyList[0], 'count', value);
          }
        },
        immediate: true
      }
    },
    async created () {
      await this.handleRefreshSystem();
    },
    methods: {
      /**
       * 获取系统列表
       */
      async fetchSystems () {
        this.pageLoading = true;
        const { id, username, type } = this.data;
        try {
          const { data } = await this.$store.dispatch('organization/getSubjectHasPermSystem', {
            subjectType: type === 'user' ? type : 'department',
            subjectId: type === 'user' ? username : id
          });
          this.systemListStorage = data || [];
          this.formatSystemData(data || []);
        } catch (e) {
          console.error(e);
          this.emptyPolicyData = formatCodeData(e.code, this.emptyPolicyData);
          this.messageAdvancedError(e);
        } finally {
          this.pageLoading = false;
        }
      },

      // 搜索自定义权限
      fetchSystemSearch () {
        // 过滤掉搜索框的参数, 处理既有筛选系统也有输入名字、描述等仍要展示为空的情况
        const { id, description, name, system_id: systemId } = this.curSearchParams;
        const noValue = !id && !name && !description;
        // 筛选搜索的系统id
        const curSystemList = this.systemListStorage.filter(item => item.id === systemId && noValue);
        this.formatSystemData(curSystemList || []);
      },

      handleAfterDelete (policyListLen, sysIndex) {
        this.$set(this.systemPolicyList[sysIndex], 'count', policyListLen);
        if (this.systemPolicyList[sysIndex].count < 1) {
          this.systemPolicyList.splice(sysIndex, 1);
        }
        if (!this.systemPolicyList.length) {
          this.handleRefreshSystem();
          if (this.isSearchPerm) {
            bus.$emit('on-perm-tab-count', { active: 'CustomPerm', count: this.systemPolicyList.length });
          }
        }
      },

      async handleDeleteAll (payload, sysIndex) {
        const { name, id } = payload;
        const { id: subjectId, type, username } = this.data;
        this.$bkInfo({
          subHeader: (
            <div class="del-actions-warn-info">
              <bk-icon type="info-circle-shape" class="warn" />
              <span>{ this.$t(`m.dialog['确定要删除系统下的所有操作权限？']`, { value: name }) }</span>
            </div>
          ),
          width: this.curLanguageIsCn ? 500 : 700,
          maskClose: true,
          closeIcon: false,
          confirmLoading: true,
          extCls: 'custom-perm-del-info',
          confirmFn: async () => {
            try {
              const personalParams = {
                systemId: id,
                subjectType: type,
                subjectId: username
              };
              const { code: personalCode, data } = await this.$store.dispatch('perm/getPersonalPolicy', personalParams);
              if (personalCode === 0) {
                const policyIdList = data.map(item => item.policy_id);
                const deleParams = {
                  policyIds: policyIdList,
                  systemId: id,
                  subjectType: type === 'user' ? type : 'department',
                  subjectId: type === 'user' ? username : subjectId
                };
                const { code } = await this.$store.dispatch('permApply/deleteSubjectPerm', deleParams);
                if (code === 0) {
                  this.systemPolicyList.splice(sysIndex, 1);
                  this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
                  if (!this.systemPolicyList.length) {
                    this.handleRefreshSystem();
                    if (this.isSearchPerm) {
                      bus.$emit('on-perm-tab-count', { active: 'CustomPerm', count: this.systemPolicyList.length });
                    }
                  }
                  return true;
                }
              }
            } catch (e) {
              console.error(e);
              this.messageAdvancedError(e);
              return false;
            }
          }
        });
      },

      // 格式化系统列表数据
      formatSystemData (payload) {
        const systemPolicyList = payload.map(item => new PermSystem(item));
        this.systemPolicyList.splice(0, this.systemPolicyList.length, ...systemPolicyList);
        this.systemPolicyList.sort((curr, next) => curr.name.localeCompare(next.name));
        if (this.externalSystemId && this.systemPolicyList.length > 1) {
          const externalSystemIndex = this.systemPolicyList.findIndex(item => item.id === this.externalSystemId);
          if (externalSystemIndex > -1) {
            this.systemPolicyList.splice(
              externalSystemIndex,
              1,
              ...this.systemPolicyList.splice(0, 1, this.systemPolicyList[externalSystemIndex])
            );
          }
        }
        this.onePerm = systemPolicyList.length;
        if (this.isSearchPerm) {
          this.emptyPolicyData.tipType = 'search';
        }
        this.emptyPolicyData = formatCodeData(0, this.emptyPolicyData, this.onePerm === 0);
      },

      async handleRefreshSystem () {
        if (this.isSearchPerm && this.curSearchParams.system_id) {
          this.formatSystemData(this.systemPolicyList || []);
          this.emptyPolicyData = formatCodeData(0, this.emptyPolicyData, this.systemPolicyList.length === 0);
        } else {
          const externalParams = {};
          if (this.externalSystemId) {
            externalParams.system_id = this.externalSystemId;
          }
          this.emptyPolicyData.tipType = '';
          this.fetchSystems();
        }
      },

      async handleEmptyClear () {
        await this.handleRefreshSystem();
        this.$emit('on-clear');
      },

      async handleEmptyRefresh () {
        await this.handleRefreshSystem();
        this.$emit('on-refresh');
      }
    }
  };
</script>
<style lang="postcss">
  @import '@/css/mixins/custom-delete-action.css';
  .iam-custom-perm-wrapper {
    /* height: calc(100vh - 204px); */
    .iam-perm-ext-cls {
        margin-top: 10px;
    }
  }
</style>
