<template>
  <div class="iam-my-perm">
    <template v-if="groupTemplateList.length">
      <render-perm-item
        v-for="(groupTemplate, groupTemplateIndex) in groupTemplateList"
        :key="groupTemplate.id"
        :expanded.sync="groupTemplate.expanded"
        :ext-cls="groupTemplateIndex > 0 ? 'iam-perm-ext-cls' : ''"
        :title="groupTemplate.displayName"
        @on-expanded="handleExpanded(...arguments, groupTemplate)">
        <detail-table :template-id="groupTemplate.id" :system-id="groupTemplate.system.id"
          :version="groupTemplate.version" />
      </render-perm-item>
    </template>
    <template v-else>
      <div class="iam-my-perm-empty-wrapper">
        <!-- <iam-svg /> -->
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
  import RenderPermItem from './render-perm';
  import DetailTable from './detail-table';
  import { formatCodeData } from '@/common/util';

  export default {
    name: '',
    components: {
      RenderPermItem,
      DetailTable
    },
    data () {
      return {
        groupTemplateList: [],
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      groupId () {
        return this.$route.params.id;
      },
      groupName () {
        return this.$route.params.name;
      }
    },
    created () {
      const params = this.$route.params;
      if (!params.id || !params.name) {
        this.$router.push({
          name: 'myPerm',
          query: this.$route.query,
          params
        });
        return;
      }
      this.$store.commit('setHeaderTitle', `${this.$t(`m.myApply['用户组']`)}${this.$t(`m.common['【']`)}${this.groupName}${this.$t(`m.common['】']`)}${this.$t(`m.common['的权限']`)}`);
      this.$store.commit('setBackRouter', -1);
    },
    methods: {
      /**
       * 获取页面数据
       */
      async fetchPageData () {
        await this.fetchGroupTemplates();
      },

      /**
       * 展开/收起 系统下的权限列表
       *
       * @param {Boolean} value 展开收起标识
       * @param {Object} payload 当前系统
       */
      async handleExpanded (value, payload) { },

      /**
       * 用户组拥有的权限模板列表
       */
      async fetchGroupTemplates () {
        try {
          const { code, data } = await this.$store.dispatch('perm/getGroupTemplates', {
            id: this.groupId
          });
          const list = data || [];
          list.forEach(item => {
            console.error(item);
            item.displayName = `${item.name}（${item.system.name}）`;
            item.expanded = false;
          });
          this.groupTemplateList.splice(0, this.groupTemplateList.length, ...list);
          this.emptyData = formatCodeData(code, this.emptyData, this.groupTemplateList.length === 0);
        } catch (e) {
          console.error(e);
          const { code, data, message, statusText } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.groupTemplateList = [];
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: message || data.msg || statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      }
    }
  };
</script>
<style lang="postcss">
    .iam-my-perm {
        .iam-perm-ext-cls {
            margin-top: 10px;
        }
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
