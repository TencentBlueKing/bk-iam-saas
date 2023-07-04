<template>
  <bk-sideslider
    :is-show.sync="isShow"
    :width="960"
    :title="$t(`m.permTemplate['模板详情']`)"
    ext-cls="iam-tempate-detail-sideslider"
    :quick-close="true"
    @update:isShow="handleCancel">
    <div slot="content" class="content" v-bkloading="{ isLoading, opacity: 1 }">
      <render-action :actions="actions" mode="detail" v-if="!isLoading" />
    </div>
  </bk-sideslider>
</template>

<script>
  import RenderAction from '@/views/perm-template/components/render-action';

  export default {
    name: '',
    components: {
      RenderAction
    },
    props: {
      isShow: {
        type: Boolean,
        default: false
      },
      id: {
        type: [String, Number],
        default: ''
      }
    },
    data () {
      return {
        isLoading: false,
        actions: [],
        defaultCheckedActions: []
      };
    },
    watch: {
      isShow: {
        handler (value) {
          if (value) {
            this.fetchTemplateDetail();
          }
        },
        immediate: true
      }
    },
    methods: {
      handleCancel () {
        this.$emit('update:isShow', false);
      },

      async fetchTemplateDetail () {
        this.isLoading = true;
        try {
          const res = await this.$store.dispatch('permTemplate/getTemplateDetail', {
            id: this.id,
            grouping: true
          });
          this.actions = res.data.actions;
          this.handleActionData();
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

      handleActionData () {
        this.actions.forEach((item, index) => {
          this.$set(item, 'expanded', false);
          let count = 0;
          let allCount = 0;
          if (!item.actions) {
            this.$set(item, 'actions', []);
          }
          item.actions.forEach(act => {
            this.$set(act, 'checked', ['checked', 'readonly'].includes(act.tag));
            this.$set(act, 'disabled', act.tag === 'readonly');
            if (act.checked) {
              ++count;
              this.defaultCheckedActions.push(act.id);
            }
            ++allCount;
          })
          ;(item.sub_groups || []).forEach(sub => {
            this.$set(sub, 'expanded', false);
            this.$set(sub, 'actionsAllChecked', false);
            if (!sub.actions) {
              this.$set(sub, 'actions', []);
            }
            sub.actions.forEach(act => {
              this.$set(act, 'checked', ['checked', 'readonly'].includes(act.tag));
              this.$set(act, 'disabled', act.tag === 'readonly');
              if (act.checked) {
                ++count;
                this.defaultCheckedActions.push(act.id);
              }
              ++allCount;
            });

            const isSubAllChecked = sub.actions.every(v => v.checked);
            this.$set(sub, 'allChecked', isSubAllChecked);
          });

          this.$set(item, 'count', count);
          this.$set(item, 'allCount', allCount);

          const isAllChecked = item.actions.every(v => v.checked);
          const isAllDisabled = item.actions.every(v => v.disabled);
          this.$set(item, 'allChecked', isAllChecked);
          if (item.sub_groups && item.sub_groups.length > 0) {
            this.$set(item, 'actionsAllChecked', isAllChecked && item.sub_groups.every(v => v.allChecked));
            this.$set(item, 'actionsAllDisabled', isAllDisabled && item.sub_groups.every(v => {
              return v.actions.every(sub => sub.disabled);
            }));
          } else {
            this.$set(item, 'actionsAllChecked', isAllChecked);
            this.$set(item, 'actionsAllDisabled', isAllDisabled);
          }
        });
        if (this.actions.length === 1) {
          this.actions[0].expanded = true;
        }
      }
    }
  };
</script>
<style lang="postcss">
    .iam-tempate-detail-sideslider {
        .content {
            padding: 10px 20px 20px 20px;
            min-height: 255px;
        }
    }
</style>
