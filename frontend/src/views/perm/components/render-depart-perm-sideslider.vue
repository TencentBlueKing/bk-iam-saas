<template>
  <bk-sideslider
    :is-show.sync="isShowSideslider"
    :title="title"
    :width="880"
    ext-cls="iam-depart-perm-sideslider"
    :quick-close="true"
    @animation-end="handleAnimationEnd">
    <div
      slot="content"
      class="content-wrapper"
      v-bkloading="{ isLoading, opacity: 1 }">
      <template v-if="orgTemplateList.length && !isLoading">
        <render-perm-item
          v-for="(orgTemplate, orgTemplateIndex) in orgTemplateList"
          :key="orgTemplate.id"
          :expanded.sync="orgTemplate.expanded"
          :ext-cls="orgTemplateIndex > 0 ? 'iam-perm-ext-cls' : ''"
          :title="orgTemplate.displayName">
          <detail-table :template-id="orgTemplate.id" :system-id="orgTemplate.system.id"
            :version="orgTemplate.version" />
        </render-perm-item>
      </template>
      <template v-if="!orgTemplateList.length && !isLoading">
        <div class="iam-my-perm-empty-wrapper">
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
  </bk-sideslider>
</template>
<script>
    // import _ from 'lodash'
  import { formatCodeData } from '@/common/util';
  import RenderPermItem from '../organization-perm/render-perm';
  import DetailTable from '../organization-perm/detail-table';
  export default {
    name: '',
    components: {
      RenderPermItem,
      DetailTable
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      departId: {
        type: [String, Number],
        default: ''
      },
      title: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        orgTemplateList: [],
        isShowSideslider: false,
        requestQueue: ['list'],
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      isLoading () {
        return this.requestQueue.length > 0;
      }
    },
    watch: {
      show: {
        handler (value) {
          this.isShowSideslider = !!value;
          if (this.isShowSideslider) {
            this.fetchData();
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchData () {
        try {
          const { code, data } = await this.$store.dispatch('perm/getOrgTemplates', {
            subjectId: this.departId,
            subjectType: 'department'
          });
          (data || []).forEach(item => {
            item.displayName = `${item.name}（${item.system.name}）`;
            item.expanded = false;
          });
          this.orgTemplateList.splice(0, this.orgTemplateList.length, ...data);
          this.emptyData = formatCodeData(code, this.emptyData, this.orgTemplateList.length === 0);
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
          this.requestQueue.shift();
        }
      },

      async handleEmptyRefresh () {
        await this.fetchData();
      },

      handleAnimationEnd () {
        this.orgTemplateList = [];
        this.requestQueue = ['list'];
        this.$emit('animation-end');
      }
    }
  };
</script>
<style lang="postcss">
    .iam-depart-perm-sideslider {
        .bk-sideslider-content {
            background: #f5f6fa;
        }
        .content-wrapper {
            position: relative;
            padding: 30px;
            min-height: calc(100vh - 60px);
        }
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
