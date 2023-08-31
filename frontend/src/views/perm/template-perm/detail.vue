<template>
  <div class="iam-my-perm">
    <template v-if="actions.length">
      <detail-table :table-list="actions" :system-id="systemId" />
    </template>
    <template v-else>
      <div class="iam-my-perm-empty-wrapper">
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :tip-text="emptyData.tip"
          :tip-type="emptyData.tipType"
          @on-refresh="fetchPageData"
        />
      </div>
    </template>
  </div>
</template>
<script>
  import DetailTable from './detail-table';
  import PermPolicy from '@/model/my-perm-policy';
  import { formatCodeData } from '@/common/util';

  export default {
    name: '',
    components: {
      DetailTable
    },
    data () {
      return {
        actions: [],
        systemId: '',
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      templateId () {
        return this.$route.params.id;
      },
      templateVersion () {
        return this.$route.query.version;
      }
    },
    created () {
      const params = this.$route.params;
      if (!params.id) {
        this.$router.push({
          name: 'myPerm',
          query: this.$route.query,
          params
        });
        return;
      }
      this.$store.commit('setBackRouter', -1);
    },
    methods: {
      /**
       * 获取页面数据
       */
      async fetchPageData () {
        await this.fetchTemplateDetail();
      },

      /**
       * 获取模板详情
       */
      async fetchTemplateDetail () {
        try {
          const params = {
            id: this.templateId
          };
          if (this.templateVersion !== undefined) {
            params.version = this.templateVersion;
          }

          const { code, data } = await this.$store.dispatch('perm/getTemplateDetail', params);
          const detail = data || {};
          this.systemId = data.system.id;
          this.actions.splice(0, this.actions.length, ...detail.actions.map(item => new PermPolicy(item)));
          this.$store.commit('setHeaderTitle', `${this.$t(`m.myApply['权限模板']`)}：${detail.name}(${detail.system.name})`);
          this.emptyData = formatCodeData(code, this.emptyData, this.actions.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        }
      }
    }
  };
</script>
<style lang="postcss">
    .iam-my-perm {
        .iam-my-perm-empty-wrapper {
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
