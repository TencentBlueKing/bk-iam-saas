<template>
  <div class="iam-my-perm-related-content">
    <bk-tab :active.sync="active"
      type="unborder-card">
      <bk-tab-panel
        v-for="(panel, index) in panels"
        v-bind="panel"
        :key="index">
        <template v-if="panel.tabType === 'relate'">
          <tree :data="panel.data" :has-border="true" :is-view="true" />
        </template>
        <template v-else>
          <condition-detail :data="panel.data" />
        </template>
      </bk-tab-panel>
    </bk-tab>
  </div>
</template>
<script>
  import Tree from '@/components/attach-action-preview/attach-action-tree';
  import ConditionDetail from '@/components/render-resource/detail';
  export default {
    name: '',
    components: {
      Tree,
      ConditionDetail
    },
    props: {
      data: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        panels: [
          { name: 'relate', label: this.$t(`m.permApply['关联权限']`), tabType: 'relate' }
        ],
        active: 'relate'
      };
    },
    watch: {
      data: {
        handler (value) {
          if (value.length > 0) {
            this.panels = value;
            this.active = this.panels[0].name;
          }
        },
        immediate: true
      }
    }
  };
</script>
<style lang="postcss">
    .iam-my-perm-related-content {
        .bk-tab-section {
            padding: 20px 0 0 0;
        }
    }
</style>
