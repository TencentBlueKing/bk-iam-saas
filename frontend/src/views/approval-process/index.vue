<template>
  <div class="iam-approval-process-set-wrapper">
    <section class="iam-approval-process-set-item-wrapper" v-if="isShowProcessSelect">
      <render-set-item
        v-for="(item, index) in processSetList"
        :key="index"
        :ref="`${index}SetRef`"
        :class="index > 0 ? 'set-margin-left' : ''"
        :cur-value="item.process_id"
        :title="item.title"
        :list="processData[item.type]"
        @selected="handleSelected(...arguments, item, index)" />
    </section>
    <section
      :class="[
        'iam-approval-process-set-content-wrapper',
        { 'set-style': isShowProcessSelect },
        { 'hide-process-table': isShowProcessTable },
        { 'show-notice-alert': showNoticeAlert && showNoticeAlert() }
      ]"
    >
      <bk-tab
        :active.sync="active"
        type="unborder-card"
        ext-cls="iam-approval-process-set-tab-cls">
        <bk-tab-panel
          v-for="(panel, index) in panels"
          v-bind="panel"
          :key="index">
        </bk-tab-panel>
        <component
          :is="active"
          :list="processData[activeMap[active]]" />
      </bk-tab>
    </section>
  </div>
</template>
<script>
  import { bus } from '@/common/bus';
  import { mapGetters } from 'vuex';
  import RenderSetItem from './common/render-process-item';
  import JoinRateManagerProcess from './components/join-rate-manager-process';
  import JoinGroupProcess from './components/join-group-process';
  import CustomPermProcess from './components/custom-perm-process';
  import CreateRateManagerProcess from './components/create-rate-manager-process';
  import { formatCodeData } from '@/common/util';

  /**
   * ACTIVE_COMPONENT_MAP
   */
  const ACTIVE_COMPONENT_MAP = {
    'CustomPermProcess': 'grant_action',
    'JoinGroupProcess': 'join_group',
    'JoinRateManagerProcess': 'create_rating_manager',
    'CreateRateManagerProcess': 'alter_rating_manager'
  };

  export default {
    inject: ['reload', 'showNoticeAlert'],
    components: {
      RenderSetItem,
      JoinRateManagerProcess,
      JoinGroupProcess,
      CustomPermProcess,
      CreateRateManagerProcess
    },
    data () {
      return {
        processSetList: [
          {
            title: this.$t(`m.approvalProcess['自定义权限']`),
            isOpen: false,
            process_id: '',
            type: 'grant_action'
          },
          {
            title: this.$t(`m.approvalProcess['加入用户组']`),
            isOpen: false,
            process_id: '',
            type: 'join_group'
          },
          {
            title: this.$t(`m.approvalProcess['创建管理空间']`),
            isOpen: false,
            value: '3',
            type: 'create_rating_manager'
          }
        ],
        panels: [
          { name: 'CustomPermProcess', label: this.$t(`m.approvalProcess['自定义权限审批流程']`) },
          { name: 'JoinGroupProcess', label: this.$t(`m.approvalProcess['加入用户组审批流程']`) }
        ],
        active: 'JoinGroupProcess',
        curRole: 'staff',
        processData: {
          'grant_action': [],
          'join_group': [],
          'create_rating_manager': []
          // 'alter_rating_manager': []
        },
        activeMap: ACTIVE_COMPONENT_MAP,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['user', 'index']),
      isSuperManager () {
        return ['super_manager'].includes(this.curRole);
      },
      isShowProcessSelect () {
        if (this.index !== 1 && this.isSuperManager) {
          return true;
        }
        return false;
      },
      isShowProcessTable () {
        return ![1].includes(Number(this.index));
      }
    },
    watch: {
      /**
       * user
       */
      user: {
        handler (value) {
          this.curRole = value.role.type || 'staff';
          this.getFilterPanels();
        },
        immediate: true
      },
      index: {
        async handler (newValue, oldValue) {
          // 处理不同导航栏下相同路由切换不刷新
          if (newValue !== oldValue) {
            this.curRole = this.user.role.type || 'staff';
            this.getFilterPanels();
            await this.fetchPageData();
          }
        },
        deep: true
      }
    },
    created () {
      this.curRole = this.user.role.type || 'staff';
      this.getFilterPanels();
    },
    methods: {
      async fetchPageData () {
        const roleItem = {
          system_manager: async () => {
            await Promise.all([
              this.fetchProcesses('grant_action'),
              this.fetchProcesses('join_group')
            ]);
          },
          rating_manager: async () => {
            await this.fetchProcesses('join_group');
          },
          subset_manager: async () => {
            await this.fetchProcesses('join_group');
          }
        };
        return roleItem[this.curRole] ? roleItem[this.curRole]() : this.fetchAllRequest();
      },

      async fetchAllRequest () {
        const allReq = [
          this.fetchProcesses('grant_action'),
          this.fetchProcesses('join_group'),
          this.fetchProcesses('create_rating_manager'),
          this.fetchDefaultProcesses()
        ];
        await Promise.all(allReq);
      },

      /**
       * fetchProcesses
       */
      async fetchProcesses (type) {
        try {
          const { code, data } = await this.$store.dispatch('approvalProcess/getProcessesList', { type });
          this.processData[type] = Object.freeze(data);
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        }
      },

      /**
       * fetchDefaultProcesses
       */
      async fetchDefaultProcesses () {
        try {
          const { code, data } = await this.$store.dispatch('approvalProcess/getDefaultProcesses');
          const defaultProcesses = data || [];
          const grantAction = defaultProcesses.find(item => item.type === 'grant_action');
          const joinGroup = defaultProcesses.find(item => item.type === 'join_group');
          const createRatingManager = defaultProcesses.find(item => item.type === 'create_rating_manager');
          if (grantAction) {
            this.processSetList[0].process_id = grantAction.process_id;
          }
          if (joinGroup) {
            this.processSetList[1].process_id = joinGroup.process_id;
          }
          if (createRatingManager) {
            this.processSetList[2].process_id = createRatingManager.process_id;
          }
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        }
      },

      /**
       * getFilterPanels
       */
      getFilterPanels () {
        const roleItem = {
          super_manager: () => {
            this.panels = this.panels.filter(item => ['CustomPermProcess', 'JoinRateManagerProcess', 'JoinGroupProcess'].includes(item.name));
            this.active = 'CustomPermProcess';
          },
          system_manager: () => {
            this.panels = this.panels.filter(item => ['CustomPermProcess', 'JoinGroupProcess'].includes(item.name));
            this.active = 'CustomPermProcess';
          },
          rating_manager: () => {
            this.panels = this.panels.filter(item => ['JoinRateManagerProcess', 'JoinGroupProcess'].includes(item.name));
            this.active = 'JoinGroupProcess';
          },
          subset_manager: () => {
            this.panels = this.panels.filter(item => ['JoinRateManagerProcess', 'JoinGroupProcess'].includes(item.name));
            this.active = 'JoinGroupProcess';
          }
        };
        if (roleItem[this.curRole]) {
          roleItem[this.curRole]();
        }
      },

      /**
       * handleSelected
       */
      async handleSelected (payload, item, index) {
        try {
          const { code } = await this.$store.dispatch('approvalProcess/updateDefaultProcesses', {
            type: item.type,
            process_id: payload
          });
          item.process_id = payload;
          this.$refs[`${index}SetRef`][0] && this.$refs[`${index}SetRef`][0].setValue(item.process_id);
          if (code === 0) {
            bus.$emit('update-tab-table-list', { type: this.active, process_id: payload });
            this.messageSuccess(this.$t(`m.common['操作成功']`));
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      }
    }
  };
</script>
<style lang="postcss">
    .iam-approval-process-set-wrapper {
        padding: 24px;
        .iam-approval-process-set-item-wrapper {
            display: flex;
            justify-content: flex-start;
            .set-margin-left {
                margin-left: 16px;
            }
        }
        .iam-approval-process-set-content-wrapper {
            min-height: calc(100vh - 150px);
            background: #ffffff;
            border-radius: 2px;
            box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, .05);
            &.set-style {
                margin-top: 20px;
                min-height: calc(100vh - 250px);
            }
            &.hide-process-table {
              display: none;
            }
            &.show-notice-alert {
              min-height: calc(100vh - 190px);
            }
            .iam-approval-process-set-tab-cls {
                .bk-tab-header {
                    height: 60px;
                    background-image: linear-gradient(transparent 59px, #dcdee5 0);
                    .bk-tab-header-setting {
                        height: 60px;
                        line-height: 60px;
                    }
                    .bk-tab-label-list {
                        height: 60px;
                        .bk-tab-label-item {
                            line-height: 60px;
                        }
                    }
                }
            }
        }
    }
</style>
