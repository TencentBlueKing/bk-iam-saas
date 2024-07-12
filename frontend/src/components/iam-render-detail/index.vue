<template>
  <div class="iam-my-perm-related-wrapper">
    <bk-tab :active.sync="active" type="unborder-card">
      <bk-tab-panel
        v-for="(panel, index) in panels"
        v-bind="panel"
        :key="index"
      >
        <template v-if="panel.tabType === 'relate'">
          <AttachActionTree :data="panel.data" :has-border="true" />
        </template>
        <template v-else>
          <ConditionDetail :data="panel.data" />
        </template>
      </bk-tab-panel>
    </bk-tab>
  </div>
</template>

<script>
  import AttachActionTree from '@/components/attach-action-preview/attach-action-tree';
  import ConditionDetail from '@/components/render-resource/detail';
  export default {
    components: {
      AttachActionTree,
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
          { name: 'relate', label: '关联权限', tabType: 'relate' }
        ],
        active: 'relate'
      };
    },
    watch: {
      data: {
        handler (value) {
          if (value.length > 0) {
            this.panels = value;
            const { name, tabActive } = value[0];
            this.active = tabActive || name;
          }
        },
        immediate: true
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-my-perm-related-wrapper {
  .bk-tab-section {
    padding: 20px 0 0 0;
  }
}
</style>
