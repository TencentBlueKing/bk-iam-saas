<template>
  <bk-sideslider
    :is-show.sync="isShowSideSlider"
    :title="title"
    :width="width"
    ext-cls="iam-group-perm-slider"
    :quick-close="true"
    @animation-end="handleAnimationEnd"
  >
    <div slot="header">
      <p class="single-hide"
        :title="$t(`m.info['用户组侧边栏的详情']`, { value: `${$t(`m.common['【']`)}${name}${$t(`m.common['】']`)}` })"
      >
        {{ $t(`m.info['用户组侧边栏的详情']`, { value: `${$t(`m.common['【']`)}${name}${$t(`m.common['】']`)}` }) }}
      </p>
      <p class="group-id">ID: {{ groupId }}</p>
    </div>
    <div slot="content" class="content-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
      <div class="iam-group-perm-slider-tab set-tab-margin-bottom" v-if="!isLoading && showMember">
        <section class="tab-item active">{{$t(`m.perm['组权限']`)}}</section>
      </div>
      <section>
        <GroupPermNew :id="groupId" mode="detail" />
      </section>
    </div>
  </bk-sideslider>
</template>

<script>
  import { bus } from '@/common/bus';
  import { sleep } from '@/common/util';
  import GroupPermNew from '@/views/group/detail/group-perm-new.vue';
  export default {
    components: {
      GroupPermNew
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      groupId: {
        type: [String, Number],
        default: ''
      },
      title: {
        type: String,
        default: ''
      },
      name: {
        type: String,
        default: ''
      },
      showMember: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        isShowSideSlider: false,
        isLoading: true,
        tabActive: 'perm',
        width: 960
      };
    },
    watch: {
      show: {
        handler (value) {
          this.isShowSideSlider = !!value;
          if (this.isShowSideSlider) {
            sleep(3000).then(() => {
              this.isLoading = false;
            });
          }
        },
        immediate: true
      }
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-drawer-side');
      });
      bus.$on('on-drawer-side', (payload) => {
        this.width = payload.width;
      });
    },
    methods: {
      handleAnimationEnd () {
        this.width = 960;
        this.$emit('animation-end');
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-group-perm-slider {
  /deep/ .bk-sideslider-content {
    background-color: #f5f6fa;
    .content-wrapper {
      position: relative;
      padding: 30px;
      min-height: calc(100vh - 60px);
    }
    .set-tab-margin-bottom {
      margin-bottom: 10px;
    }
  }
  .group-id {
    position: relative;
    top: -12px;
    line-height: 0;
    font-size: 12px;
    color: #c4c6cc;
  }
  &-tab {
    display: flex;
    justify-content: flex-start;
    padding: 0 20px;
    width: 100%;
    height: 42px;
    line-height: 42px;
    color: #63656e;
    background-color: #ffffff;
    border-radius: 2px;
    box-shadow: 0px 1px 2px 0px rgba(247, 220, 220, .05);
    .tab-item {
      font-size: 14px;
      cursor: pointer;
      &.active {
        color: #3a84ff;
        border-bottom: 2px solid #3a84ff;
      }
    }
  }
}
</style>
