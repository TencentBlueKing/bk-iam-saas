<template>
  <div class="iam-my-perm-related-wrapper">
    <bk-tab :active.sync="active" type="unborder-card" @tab-change="handleTabChange">
      <bk-tab-panel
        v-for="(panel, index) in panels"
        v-bind="panel"
        :key="index"
      >
        <template v-if="panel.tabType === 'relate'">
          <AttachActionTree :data="panel.data" :has-border="true" />
        </template>
        <template v-else>
          <ConditionDetail
            ref="conditionRef"
            :data="panel.data"
            :can-edit="canEdit"
            @on-change="handleChange"
            @on-select-all="handleSelectAll"
          />
        </template>
      </bk-tab-panel>
    </bk-tab>
  </div>
</template>

<script>
  import AttachActionTree from '@/components/attach-action-preview/attach-action-tree';
  import ConditionDetail from '@/components/render-resource/edit';
  export default {
    components: {
      AttachActionTree,
      ConditionDetail
    },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      canEdit: {
        type: Boolean,
        default: false
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
    },

    methods: {
      handleTabChange (payload) {
        const curActiveData = this.panels.find(item => item.name === payload);
        if (curActiveData.tabType === 'relate') {
          this.$emit('tab-change', {
            disabled: true,
            canDelete: false
          });
          return;
        }
        this.$emit('tab-change', {
          disabled: curActiveData.data.length < 1
            || curActiveData.data.every(item => !item.instance || item.instance.length < 1),
          canDelete: true
        });
      },

      handleChange () {
        this.$emit('on-change');
      },
      
      handleSelectAll (isAll, payload) {
        this.$emit('on-select-all', isAll, payload);
      },

      handleGetValue () {
        const data = this.$refs.conditionRef[0].handleGetValue();
        const curActiveData = this.panels.find(item => item.name === this.active);
        if (curActiveData.tabType !== 'relate') {
          return {
            ...data,
            system_id: curActiveData.systemId,
            type: this.active,
            resource_group_id: curActiveData.resource_group_id
          };
        }
        return { ...data, resource_group_id: curActiveData.resource_group_id };
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
