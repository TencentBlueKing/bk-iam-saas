<template>
  <bk-dialog
    v-model="isShowDialog"
    width="720"
    :title="title"
    :show-footer="false"
    header-position="left"
    ext-cls="iam-resource-preview-dialog"
    @after-leave="handleAfterEditLeave">
    <div class="resource-preview-content-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
      <template v-if="!isLoading">
        <div class="compare-content">
          <compare-detail :data="conditionData" :is-not-limit="params.isNotLimit" />
        </div>
      </template>
    </div>
  </bk-dialog>
</template>
<script>
  import CompareCondition from '@/model/compare-condition';
  import CompareDetail from '@/components/render-resource/compare-detail';
  export default {
    name: '',
    components: {
      CompareDetail
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      params: {
        type: Object,
        default: () => {
          return {};
        }
      },
      title: {
        type: String,
        default: '差异对比'
      }
    },
    data () {
      return {
        isShowDialog: false,
        isLoading: false,
        searchParams: {},
        conditionData: [],
        total: 0
      };
    },
    watch: {
      show: {
        handler (value) {
          this.isShowDialog = !!value;
        },
        immediate: true
      },
      params: {
        handler (value) {
          this.searchParams = value;
          if (this.isShowDialog) {
            this.fetchData();
          }
        },
        immediate: true,
        deep: true
      }
    },
    methods: {
      async fetchData () {
        // debugger
        this.isLoading = true;
        const isTemplate = this.params.isTemplate;
        const method = isTemplate ? 'groupTemplateCompare' : 'groupPolicyCompare';
        const requestParams = {
          id: this.params.groupId,
          data: {
            related_resource_type: this.params.related_resource_type,
            resource_group_id: this.params.resource_group_id
          }
        };
        if (!isTemplate) {
          requestParams.data.policy_id = this.params.policy_id;
        } else {
          requestParams.templateId = this.params.id;
          requestParams.data.action_id = this.params.action_id;
        }
        try {
          const res = await this.$store.dispatch(`userGroup/${method}`, requestParams);
          this.conditionData = res.data.map(item => new CompareCondition(item));
          if (this.conditionData.length > 0) {
            if (this.conditionData[0].hasOwnProperty('instance')) {
              this.conditionData[0].instanceExpanded = true;
            }
            if (this.conditionData[0].hasOwnProperty('attribute')) {
              this.conditionData[0].attributeExpanded = true;
            }
          }
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.isLoading = false;
        }
      },

      handleAfterEditLeave () {
        this.$emit('on-after-leave');
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-resource-preview-dialog {
        .bk-dialog-body {
            padding: 0 0 26px 0;
        }
        .resource-preview-content-wrapper {
            min-height: 442px;
            .compare-content {
                height: 400px;
                overflow-y: auto;
                &::-webkit-scrollbar {
                    width: 4px;
                    background-color: lighten(transparent, 80%);
                }
                &::-webkit-scrollbar-thumb {
                    height: 5px;
                    border-radius: 2px;
                    background-color: #e6e9ea;
                }
            }
        }
    }
</style>
