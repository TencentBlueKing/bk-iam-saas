<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :width="width"
      ext-cls="iam-action-template-detail-side"
      :quick-close="true"
      @update:isShow="handleCancel"
    >
      <div slot="header" class="flex-between iam-action-template-detail-side-header">
        <div>
          <span>{{ $t(`m.memberTemplate['模板详情']`) }}</span>
          <span class="custom-header-divider">|</span>
          <span class="single-hide custom-header-name" :title="curDetailData.name">
            {{ curDetailData.name }}
          </span>
        </div>
        <bk-popconfirm
          trigger="click"
          placement="bottom-end"
          ext-popover-cls="actions-template-delete-confirm"
          :width="280"
          :confirm-text="$t(`m.common['确定']`)"
          @confirm="handleTemplateDelete"
        >
          <div slot="content">
            <div class="popover-title">
              <div class="popover-title-text">
                {{ $t(`m.dialog['确认删除该操作模板？']`) }}
              </div>
            </div>
            <div class="popover-content">
              <div class="popover-content-item">
                <span class="popover-content-item-label">{{ $t(`m.memberTemplate['模板名称']`) }}:</span>
                <span class="popover-content-item-value"> {{ curDetailData.name }}</span>
              </div>
              <div class="popover-content-tip">
                {{ $t(`m.actionsTemplate['删除后，无法恢复，请谨慎操作！']`) }}
              </div>
            </div>
          </div>
          <bk-popover
            placement="right-start"
            :content="formatDelAction(curDetailData, 'title')"
            :disabled="!formatDelAction(curDetailData, 'title')">
            <bk-button :disabled="formatDelAction(curDetailData, 'disabled')">
              {{ $t(`m.common['删除']`) }}
            </bk-button>
          </bk-popover>
        </bk-popconfirm>
      </div>
      <div slot="content" class="iam-action-template-detail-side-content">
        <div class="action-template-tab">
          <div class="action-tab-groups">
            <div
              v-for="item in tabList"
              :key="item.id"
              :class="['action-tab-groups-item', { 'is-active': tabActive === item.id }]"
              @click.stop="handleTabChange(item.id, true)"
            >
              <span class="action-tab-groups-item-name">{{ item.name }}</span>
              <span
                v-if="['associate_groups'].includes(item.id)"
                class="action-tab-groups-item-count"
              >
                ({{ item.count }})
              </span>
            </div>
          </div>
        </div>
        <div class="action-template-content">
          <component
            ref="tempDetailComRef"
            :is="curCom"
            :key="comKey"
            :cur-detail-data="curDetailData"
            :tab-active="tabActive"
            @on-associate-change="handleAssociateChange"
          />
        </div>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import AssociateUserGroup from './associate-user-group.vue';
  import BasicInfoDetail from './basic-info-detail.vue';
  import TemplateActionsTable from './template-actions-table.vue';

  export default {
    components: {
      AssociateUserGroup,
      BasicInfoDetail,
      TemplateActionsTable
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      curDetailData: {
        type: Object
      }
    },
    data () {
      return {
        isShowSideSlider: false,
        width: 960,
        tabList: [
          { name: this.$t(`m.common['基本信息']`), id: 'basic_info' },
          { name: this.$t(`m.actionsTemplate['模板操作']`), id: 'template_action' },
          {
            name: this.$t(`m.memberTemplate['关联用户组']`),
            id: 'associate_groups',
            count: 0
          }
        ],
        COM_MAP: Object.freeze(
          new Map([
            [['basic_info'], 'BasicInfoDetail'],
            [['template_action'], 'TemplateActionsTable'],
            [['associate_groups'], 'AssociateUserGroup']
          ])
        ),
        tabActive: 'basic_info',
        comKey: -1
      };
    },
    computed: {
      curCom () {
        let com = '';
        for (const [key, value] of this.COM_MAP.entries()) {
          if (Object.keys(this.curDetailData).length && key.includes(this.tabActive)) {
            com = value;
            break;
          }
        }
        return com;
      },
      formatDelAction () {
        return ({ subject_count: subjectCount }, type) => {
          const typeMap = {
            title: () => {
              if (subjectCount > 0) {
                return this.$t(`m.info['有关联的用户组, 无法删除']`);
              }
              return '';
            },
            disabled: () => {
              if (subjectCount > 0) {
                return true;
              }
              return false;
            }
          };
          return typeMap[type]();
        };
      }
    },
    watch: {
      show: {
        handler (value) {
          this.isShowSideSlider = !!value;
          if (this.curDetailData.tabActive && value) {
            const { tabActive, subject_count: subjectCount } = this.curDetailData;
            const tabIndex = this.tabList.findIndex((item) => item.id === 'associate_groups');
            if (tabIndex > -1) {
              this.$set(this.tabList[tabIndex], 'count', subjectCount || 0);
            }
            this.tabActive = tabActive;
            this.handleTabChange(tabActive, false);
          }
        },
        immediate: true
      }
    },
    methods: {
      handleTabChange (payload, isClick = false) {
        if (payload === this.tabActive && isClick) {
          return;
        }
        this.tabActive = payload;
        const typeMap = {
          basic_info: () => {
            this.$nextTick(() => {
              this.$refs.tempDetailComRef && this.$refs.tempDetailComRef.fetchDetailInfo();
            });
          },
          template_action: () => {
            this.$nextTick(() => {
              this.$refs.tempDetailComRef && this.$refs.tempDetailComRef.fetchDetailInfo();
            });
          },
          associate_groups: () => {
            this.$nextTick(() => {
              this.$refs.tempDetailComRef
                && this.$refs.tempDetailComRef.fetchAssociateGroup(true);
            });
          }
        };
        return typeMap[payload]();
      },

      handleTemplateDelete () {
        this.$emit('on-delete', this.curDetailData);
      },
      
      handleAssociateChange (payload) {
        const { count } = payload;
        const tabIndex = this.tabList.findIndex((item) => ['associate_groups'].includes(item.id));
        if (tabIndex > -1) {
          this.tabList[tabIndex].count = count || 0;
        }
      },

      handleCancel () {
        this.resetData();
        this.$emit('update:show', false);
      },

      resetData () {
        this.width = 960;
        this.tabActive = 'basic_info';
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-action-template-detail-side {
  &-header {
    display: flex;
    font-size: 16px;
    color: #313238;
    .custom-header-divider {
      margin: 0 8px;
      color: #dcdee5;
    }
    .custom-header-name {
      font-size: 12px;
      max-width: 800px;
      color: #979ba5;
      word-break: break-all;
    }
  }
  &-content {
    .action-template-tab {
      padding: 24px 24px 0;
      background-color: #f5f7fa;
      position: sticky;
      top: 0;
      left: 0;
      z-index: 9999;
      .action-tab-groups {
        position: relative;
        display: flex;
        &-item {
          min-width: 96px;
          display: flex;
          font-size: 14px;
          color: #63656e;
          padding: 0 20px;
          margin-right: 8px;
          height: 42px;
          line-height: 42px;
          background-color: #eaebf0;
          border-radius: 4px 4px 0 0;
          cursor: pointer;
          &:last-child {
            margin-right: 0px;
            .action-tab-groups-item-count {
              padding-left: 5px;
            }
          }
          &.is-active {
            color: #3a84ff;
            background: #ffffff;
            border-radius: 4px 4px 0 0;
          }
        }
      }
    }
    .action-template-content {
      padding: 24px 0;
    }
  }
}
</style>
