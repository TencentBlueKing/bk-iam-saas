<template>
  <div class="my-perm-custom-perm">
    <template v-if="hasPerm">
      <custom-perm-system-policy
        v-for="(sys, sysIndex) in systemPolicyList"
        :key="sys.id"
        :expanded.sync="sys.expanded"
        :ext-cls="sysIndex > 0 ? 'iam-perm-ext-cls' : ''"
        :class="sysIndex === systemPolicyList.length - 1 ? 'iam-perm-ext-reset-cls' : ''"
        :title="sys.name"
        :perm-length="sys.count"
        :one-perm="onePerm"
        :is-all-delete="true"
        @on-expanded="handleExpanded(...arguments, sys)"
        @on-delete-all="handleDeleteAll(sys, sysIndex)"
      >
        <custom-perm-table
          ref="customPermTable"
          :key="sys.id"
          :system-id="sys.id"
          :cur-search-params="curSearchParams"
          :empty-data="emptyPolicyData"
          :is-search-perm="isSearchPerm"
          @after-delete="handleAfterDelete(...arguments, sysIndex)" />
      </custom-perm-system-policy>
    </template>
    <template v-else>
      <div class="my-perm-custom-perm-empty-wrapper">
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
  import CustomPermSystemPolicy from '@/components/custom-perm-system-policy/index.vue';
  import PermSystem from '@/model/my-perm-system';
  import CustomPermTable from './custom-perm-table.vue';
  import { mapGetters } from 'vuex';

  export default {
    name: 'CustomPerm',
    components: {
      CustomPermSystemPolicy,
      CustomPermTable
    },
    props: {
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
      }
    },
    data () {
      return {
        onePerm: 0,
        systemPolicyList: [],
        emptyPolicyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['externalSystemId']),
      hasPerm () {
        return this.systemPolicyList.length > 0;
      }
    },
    watch: {
      systemList: {
        handler (v) {
          this.formatSystemData(v);
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
      }
    },
    methods: {
      // 搜索自定义权限
      fetchSystemSearch () {
        // 过滤掉搜索框的参数, 处理既有筛选系统也有输入名字、描述等仍要展示为空的情况
        const noValue = !this.curSearchParams.id && !this.curSearchParams.name && !this.curSearchParams.description;
        // 筛选搜索的系统id
        const curSystemList
          = this.systemList.filter(item => item.id === this.curSearchParams.system_id && noValue);
        this.formatSystemData(curSystemList || []);
      },

      /**
       * 展开/收起 系统下的权限列表
       *
       * @param {Boolean} value 展开收起标识
       * @param {Object} payload 当前系统
       */
      handleExpanded (value, payload) {},

      handleAfterDelete (policyListLen, sysIndex) {
        // --this.systemPolicyList[sysIndex].count;
        this.$set(this.systemPolicyList[sysIndex], 'count', policyListLen);
        if (this.systemPolicyList[sysIndex].count < 1) {
          this.systemPolicyList.splice(sysIndex, 1);
        }
        if (!this.systemPolicyList.length) {
          this.emptyPolicyData = formatCodeData(0, this.emptyPolicyData, true);
        }
      },

      async handleDeleteAll (payload, sysIndex) {
        const { name, id } = payload;
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
              const { data } = await this.$store.dispatch('permApply/getPolicies', { system_id: id });
              const policyIdList = data.map(item => item.policy_id);
              const { code } = await this.$store.dispatch('permApply/deletePerm', {
                policyIds: policyIdList,
                systemId: id
              });
              if (code === 0) {
                this.systemPolicyList.splice(sysIndex, 1);
                this.messageSuccess(this.$t(`m.info['删除成功']`), 3000);
                if (!this.systemPolicyList.length) {
                  this.emptyPolicyData = formatCodeData(0, this.emptyPolicyData, true);
                }
                return true;
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
        this.emptyPolicyData = formatCodeData(0, this.emptyPolicyData, this.onePerm === 0);
      },

      async handleRefreshSystem () {
        const externalParams = {};
        if (this.externalSystemId) {
          externalParams.system_id = this.externalSystemId;
        }
        const { code, data } = await this.$store.dispatch('permApply/getHasPermSystem', externalParams);
        this.formatSystemData(data || []);
        this.emptyPolicyData = formatCodeData(code, this.emptyPolicyData, data.length === 0);
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
  @import './index.css';
  @import '@/css/mixins/custom-delete-action.css';
</style>
