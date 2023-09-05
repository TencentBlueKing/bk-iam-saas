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
        <iam-svg />
      </div>
    </template>
  </div>
</template>
<script>
  import RenderPermItem from './render-perm';
  import DetailTable from './detail-table';

  export default {
    name: '',
    components: {
      RenderPermItem,
      DetailTable
    },
    data () {
      return {
        groupTemplateList: []
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
          const res = await this.$store.dispatch('perm/getGroupTemplates', {
            id: this.groupId
          });
          const data = res.data || [];
          data.forEach(item => {
            console.error(item);
            item.displayName = `${item.name}（${item.system.name}）`;
            item.expanded = false;
          });
          this.groupTemplateList.splice(0, this.groupTemplateList.length, ...data);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
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
