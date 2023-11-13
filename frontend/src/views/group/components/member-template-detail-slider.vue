<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :width="width"
      ext-cls="iam-member-template-detail-side"
      :quick-close="true"
      @update:isShow="handleCancel"
    >
      <div slot="header" class="iam-member-template-detail-side-header">
        <span>{{ $t(`m.memberTemplate['模板详情']`) }}</span>
        <span class="custom-header-divider">|</span>
        <span class="single-hide custom-header-name" :title="curDetailData.name">
          {{ curDetailData.name }}
        </span>
      </div>
      <div slot="content" class="iam-member-template-detail-side-content">
        <div class="member-template-content">
          <component
            ref="tempDetailComRef"
            :is="curCom"
            :key="comKey"
            :cur-detail-data="curDetailData"
            :tab-active="tabActive"
          />
        </div>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { leaveConfirm } from '@/common/leave-confirm';
  import TemplateMemberDetailTable from './group-member-template-detail-table.vue';

  export default {
    components: {
      TemplateMemberDetailTable
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      curDetailData: {
        type: Object,
        default: () => {
          return {};
        }
      }
    },
    data () {
      return {
        isShowSideSlider: false,
        width: 960,
        COM_MAP: Object.freeze(
          new Map([
            [['template_member'], 'TemplateMemberDetailTable']
          ])
        ),
        tabActive: 'template_member',
        tabActiveStorage: '',
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
      }
    },
    watch: {
      show: {
        handler (value) {
          this.isShowSideSlider = !!value;
        },
        immediate: true
      }
    },
    methods: {
      handleCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(
          () => {
            this.$emit('update:show', false);
            this.resetData();
          },
          (_) => _
        );
      },

      resetData () {
        this.width = 960;
        this.tabActive = 'template_member';
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-member-template-detail-side {
  &-header {
    display: flex;
    .custom-header-divider {
      margin: 0 8px;
      color: #dcdee5;
    }
    .custom-header-name {
      max-width: 800px;
      color: #979ba5;
      word-break: break-all;
    }
  }
  &-content {
    .member-template-content {
      padding: 24px 0;
    }
  }
}
</style>
