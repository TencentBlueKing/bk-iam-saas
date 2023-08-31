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
        :perm-length="sys.count">
        <perm-table
          :key="sys.id"
          :system-id="sys.id"
          :params="data"
          :data="data"
          @after-delete="handleAfterDelete(...arguments, sysIndex)" />
      </custom-perm-system-policy>
    </template>
    <template v-if="isEmpty">
      <div class="iam-custom-perm-empty-wrapper">
        <!-- <iam-svg /> -->
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
  import PermTable from './teporary-perm-table-edit';
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
          type: '',
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
          const { code, data } = await this.$store.dispatch('organization/getSubjectTemporaryHasPermSystem', {
            subjectType: type === 'user' ? type : 'department',
            subjectId: type === 'user' ? this.data.username : this.data.id
          });
          this.systemList = (data || []).map(item => new PermSystem(item));
          this.onePerm = this.systemList.length;
          this.emptyData = formatCodeData(code, this.emptyData, this.onePerm === 0);
        } catch (e) {
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.pageLoading = false;
        }
      },

      /**
       * handleAfterDelete
       */
      handleAfterDelete (payload, sysIndex) {
        --this.systemList[sysIndex].count;
        if (this.systemList[sysIndex].count < 1) {
          this.systemList.splice(sysIndex, 1);
        }
      },

      handleEmptyRefresh () {
        this.fetchSystems();
      }
    }
  };
</script>
<style lang="postcss">
    .iam-custom-perm-wrapper {
        height: calc(100vh - 204px);
        .iam-perm-ext-cls {
            margin-top: 10px;
        }
        .iam-custom-perm-empty-wrapper {
            img {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 120px;
            }
        }
    }
</style>
