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
          :empty-data="emptyData"
          @after-delete="handleAfterDelete(...arguments, sysIndex)" />
      </custom-perm-system-policy>
    </template>
    <template v-else>
      <div class="my-perm-custom-perm-empty-wrapper">
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :tip-text="emptyData.tip"
          :tip-type="emptyData.tipType"
          @on-refresh="handleEmptyRefresh"
        />
      </div>
    </template>
  </div>
</template>
<script>
  import CustomPermSystemPolicy from '@/components/custom-perm-system-policy/index.vue';
  import PermSystem from '@/model/my-perm-system';
  import CustomPermTable from './custom-perm-table.vue';

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
            type: '',
            text: '',
            tip: '',
            tipType: ''
          };
        }
      }
    },
    data () {
      return {
        onePerm: 0,
        systemPolicyList: []
      };
    },
    computed: {
      hasPerm () {
        return this.systemPolicyList.length > 0;
      }
    },
    watch: {
      systemList: {
        handler (v) {
          const systemPolicyList = v.map(item => new PermSystem(item));
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
        },
        immediate: true,
        deep: true
      }
    },
    created () {
    },
    methods: {
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
                this.messageSuccess(this.$t(`m.info['删除成功']`), 2000);
                return true;
              }
            } catch (e) {
              console.error(e);
              this.bkMessageInstance = this.$bkMessage({
                limit: 1,
                theme: 'error',
                message: e.message || e.data.msg || e.statusText
              });
              return false;
            }
          }
        });
      }
    }
  };
</script>
<style lang="postcss">
  @import './index.css';
  @import '@/css/mixins/custom-delete-action.css';
</style>
