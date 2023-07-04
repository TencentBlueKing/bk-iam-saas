<template>
  <div class="iam-admin-set-wrapper">
    <bk-tab
      :active.sync="active"
      type="unborder-card"
      ext-cls="iam-set-tab-cls">
      <bk-tab-panel
        v-for="(panel, index) in panels"
        v-bind="panel"
        :key="index">
      </bk-tab-panel>
      <section class="tab-content-wrapper" v-bkloading="{ isLoading: isLoading, zIndex: 1000, opacity: 1 }">
        <component :is="active" @data-ready="handleDataReady" v-show="!isLoading" />
      </section>
    </bk-tab>
  </div>
</template>
<script>
  import { mapGetters } from 'vuex';
  import SuperManager from './components/render-super-manager';
  import SystemManager from './components/render-system-manager';
  export default {
    name: '',
    components: {
      SuperManager,
      SystemManager
    },
    data () {
      return {
        panels: [
          { name: 'SuperManager', label: this.$t(`m.myApproval['超级管理员']`) },
          { name: 'SystemManager', label: this.$t(`m.nav['系统管理员']`) }
        ],
        active: 'SuperManager',
        curRole: 'staff',
        isLoading: true
      };
    },
    computed: {
            ...mapGetters(['user'])
    },
    watch: {
      user: {
        handler (value) {
          const role = value.role.type || 'staff';
          this.handlePanels(role);
        },
        deep: true
      }
    },
    created () {
      const role = this.user.role.type || 'staff';
      this.handlePanels(role);
    },
    methods: {
      handleDataReady (payload) {
        this.isLoading = !payload;
      },

      handlePanels (payload) {
        if (payload === 'system_manager') {
          this.panels = this.panels.filter(item => item.name === 'SystemManager');
          this.active = 'SystemManager';
        }
      }
    }
  };
</script>
<style lang="postcss">
    .iam-admin-set-wrapper {
        padding: 8px 24px 24px 24px;
        .iam-set-tab-cls {
            .bk-tab-section {
                padding: 20px 0 0 0;
            }
        }
        .tab-content-wrapper {
            min-height: 255px;
            background: #fff;
        }
    }
</style>
