<template>
  <div class="iam-custom-perm-wrapper" v-bkloading="{ isLoading: pageLoading, opacity: 1 }">
    <template v-if="hasPerm">
      <custom-perm-system-policy
        v-for="(sys, sysIndex) in systemList"
        :key="sys.id"
        :expanded.sync="sys.expanded"
        :ext-cls="sysIndex > 0 ? 'iam-perm-ext-cls' : ''"
        :title="sys.name"
        :one-perm="onePerm"
        :perm-length="sys.count"
        :is-all-delete="true"
        @on-delete-all="handleDeleteAll(sys, sysIndex)"
      >
        <perm-table
          :key="sys.id"
          :system-id="sys.id"
          :params="data"
          :data="data"
          :empty-data="emptyData"
          @after-delete="handleAfterDelete(...arguments, sysIndex)"
        />
      </custom-perm-system-policy>
    </template>
    <template v-if="isEmpty">
      <div class="iam-custom-perm-empty-wrapper">
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
  import { formatCodeData } from '@/common/util';
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
      }
    },
    data () {
      return {
        isExpanded: false,
        detailSideslider: {
          isShow: false,
          title: '查看详情'
        },
        systemList: [],
        onePerm: '',
        pageLoading: false,
        emptyData: {
          type: 'empty',
          text: '',
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
        return this.systemList.length > 0 && !this.pageLoading;
      },

      /**
       * isEmpty
       */
      isEmpty () {
        return this.systemList.length < 1 && !this.pageLoading;
      }
    },
    async created () {
      await this.fetchSystems();
    },
    methods: {
      /**
       * 获取系统列表
       */
      async fetchSystems () {
        this.pageLoading = true;
        const { type } = this.data;
        try {
          const { code, data } = await this.$store.dispatch('organization/getSubjectHasPermSystem', {
            subjectType: type === 'user' ? type : 'department',
            subjectId: type === 'user' ? this.data.username : this.data.id
          });
          this.systemList = (data || []).map(item => new PermSystem(item));
          this.onePerm = this.systemList.length;
          this.systemList.sort((curr, next) => curr.name.localeCompare(next.name));
          this.emptyData = formatCodeData(code, this.emptyData, this.onePerm === 0);
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
        } finally {
          this.pageLoading = false;
        }
      },

      /**
       * handleAfterDelete
       */
      handleAfterDelete (policyListLen, sysIndex) {
        this.$set(this.systemList[sysIndex], 'count', policyListLen);
        if (this.systemList[sysIndex].count < 1) {
          this.systemList.splice(sysIndex, 1);
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
                  this.systemList.splice(sysIndex, 1);
                  this.messageSuccess(this.$t(`m.info['删除成功']`), 2000);
                  return true;
                }
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
      },

      handleEmptyRefresh () {
        this.fetchSystems();
      }
    }
  };
</script>
<style lang="postcss">
  @import '@/css/mixins/custom-delete-action.css';
  .iam-custom-perm-wrapper {
    height: calc(100vh - 204px);
    .iam-perm-ext-cls {
        margin-top: 10px;
    }
  }
</style>
