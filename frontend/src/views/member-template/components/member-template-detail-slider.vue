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
        <div class="member-template-tab">
          <div class="member-tab-groups">
            <div
              v-for="item in tabList"
              :key="item.id"
              :class="['member-tab-groups-item', { 'is-active': tabActive === item.id }]"
              @click.stop="handleTabChange(item.id, true)"
            >
              <span class="member-tab-groups-item-name">{{ item.name }}</span>
              <span
                v-if="['associate_groups'].includes(item.id)"
                class="member-tab-groups-item-count"
              >
                ({{ item.count }})
              </span>
            </div>
          </div>
        </div>
        <div class="member-template-content">
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
  import TemplateMemberTable from './template-member-table.vue';

  export default {
    components: {
      AssociateUserGroup,
      BasicInfoDetail,
      TemplateMemberTable
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
        tabList: [
          { name: this.$t(`m.common['基本信息']`), id: 'basic_info' },
          { name: this.$t(`m.memberTemplate['模板成员']`), id: 'template_member' },
          {
            name: this.$t(`m.memberTemplate['关联用户组']`),
            id: 'associate_groups',
            count: 0
          }
        ],
        COM_MAP: Object.freeze(
          new Map([
            [['basic_info'], 'BasicInfoDetail'],
            [['template_member'], 'TemplateMemberTable'],
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
      }
    },
    watch: {
      show: {
        handler (value) {
          this.isShowSideSlider = !!value;
          if (this.curDetailData.tabActive && value) {
            const { tabActive, group_count: groupCount } = this.curDetailData;
            this.tabActive = tabActive;
            this.$set(this.tabList[2], 'count', groupCount || 0);
            this.handleTabChange(this.tabActive, false);
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
          template_member: () => {
            this.$nextTick(() => {
              this.$refs.tempDetailComRef && this.$refs.tempDetailComRef.fetchTempMemberList();
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
    /* height: calc(100vh - 114px); */
    .member-template-tab {
      padding: 24px 24px 0;
      background-color: #f5f7fa;
      position: sticky;
      top: 0;
      left: 0;
      z-index: 9999;
      .member-tab-groups {
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
            .member-tab-groups-item-count {
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
    .member-template-content {
      padding: 24px 0;
    }
  }
}
</style>
