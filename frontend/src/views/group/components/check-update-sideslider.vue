<template>
  <bk-sideslider
    :is-show.sync="isVisible"
    :quick-close="false"
    :width="881"
    ext-cls="iam-check-update-sideslider"
    :title="title"
    @animation-end="handleSliderClose">
    <div slot="content" class="content-wrapper">
      <render-search>
        <bk-button
          theme="primary"
          :disabled="syncDisabled"
          :loading="syncLoading"
          @click="handleSync">
          {{ $t(`m.permTemplate['同步模板权限']`) }}
        </bk-button>
        <div slot="right" class="action-status-wrapper">
          <div class="action-status-item set-margin-right">
            <iam-svg name="icon-new" v-if="curLanguageIsCn" />
            <iam-svg name="icon-new-en" v-else />
            {{ $t(`m.permTemplate['模板中新增的内容']`) }}
          </div>
          <div class="action-status-item set-margin-right">
            <iam-svg name="icon-changed" v-if="curLanguageIsCn" />
            <iam-svg name="icon-changed-en" v-else />
            {{ $t(`m.permTemplate['模板中存在变动的内容']`) }}
          </div>
          <div class="action-status-item">
            <iam-svg name="has-delete" v-if="curLanguageIsCn" />
            <iam-svg name="has-delete-en" v-else />
            {{ $t(`m.permTemplate['模板中已删除的内容']`) }}
          </div>
        </div>
      </render-search>
      <div class="compare-perm-table" v-bkloading="{ isLoading, opacity: 1 }">
        <compare-perm-table
          :data="tableList"
          v-if="!isLoading"
          @on-compare="handleOnCompare" />
      </div>
    </div>
  </bk-sideslider>
</template>

<script>
  import Policy from '@/model/policy';
  import ComparePermTable from './compare-perm-table';

  export default {
    name: '',
    components: {
      ComparePermTable
    },
    props: {
      isShow: {
        type: Boolean,
        default: false
      },
      title: {
        type: String,
        default: ''
      },
      params: {
        type: Object,
        default: () => {
          return {};
        }
      }
    },
    data () {
      return {
        isVisible: false,
        syncLoading: false,
        tableList: [],
        curId: '',
        initRequestQueue: ['policy']
      };
    },
    computed: {
      syncDisabled () {
        return this.initRequestQueue.length > 0;
      },
      isLoading () {
        return this.initRequestQueue.length > 0;
      }
    },
    watch: {
      isShow: {
        handler (value) {
          this.isVisible = !!value;
        },
        immediate: true
      },
      params: {
        handler (value) {
          if (value.version) {
            this.initRequestQueue = ['policy'];
            this.fetchData();
          } else {
            this.initRequestQueue = [];
            this.tableList = [];
            this.curId = '';
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchData (payload) {
        const { templateId, version } = this.params;
        try {
          const res = await this.$store.dispatch('permTemplate/templateCompare', { templateId, version });
          this.tableList = res.data.map(item => new Policy(item));
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.initRequestQueue.shift();
        }
      },

      handleOnCompare (payload) {
        const { action_id, related_resource_types, action_name, tag } = payload;
        this.curId = payload.action_id;
        const paramsList = [];
        related_resource_types.forEach(item => {
          const condition = [];
          item.condition.forEach(item => {
            const { id, attribute, instance } = item;
            condition.push({
              id,
              attributes: attribute ? attribute.filter(item => item.values.length > 0) : [],
              instances: instance ? instance.filter(item => item.path.length > 0) : []
            });
          });
          paramsList.push({
            id: this.params.templateId,
            action_id,
            tag,
            reverse: false,
            related_resource_type: {
              system_id: item.system_id,
              type: item.type,
              name: item.name,
              condition: tag === 'add' ? [] : condition
            },
            tabType: 'resource'
          });
        });
        this.$emit('on-view', {
          action_name,
          params: paramsList
        });
      },

      async handleSync () {
        this.syncLoading = true;
        const { id, type, templateId } = this.params;
        try {
          await this.$store.dispatch('permTemplate/templateAuthObjectSync', { id, type, templateId });
          this.messageSuccess(this.$t(`m.permTemplate['同步成功']`), 3000);
          this.isVisible = false;
          this.$emit('animation-end');
          this.$emit('on-sync');
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.syncLoading = false;
        }
      },

      handleSliderClose () {
        this.$emit('animation-end');
      }
    }
  };
</script>

<style lang="postcss">
    .iam-check-update-sideslider {
        z-index: 2502;
        .content-wrapper {
            position: relative;
            padding: 20px 32px;
            height: 100%;
            .action-status-wrapper {
                line-height: 32px;
                .action-status-item {
                    display: inline-block;
                    font-size: 12px;
                    vertical-align: bottom;
                    &.set-margin-right {
                        margin-right: 40px;
                    }
                    img {
                        width: 28px;
                        vertical-align: sub;
                    }
                }
            }
            .compare-perm-table {
                margin-top: 16px;
                min-height: 245px;
            }
        }
    }
</style>
