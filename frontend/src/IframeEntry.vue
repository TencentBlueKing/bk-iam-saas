<template>
  <div
    id="app"
    :class="[
      systemCls,
      { 'external-system-layout': externalSystemsLayout.userGroup.groupDetail.setMainLayoutHeight },
      { 'external-app-layout': $route.name === 'addMemberBoundary' },
      { 'notice-app-layout': isShowNoticeAlert },
      { 'no-perm-app-layout': ['403'].includes(routeName) }
    ]">
    <NoticeComponent
      v-if="isEnableNoticeAlert"
      :api-url="noticeApi"
      @show-alert-change="handleShowAlertChange"
    />
    <template v-if="!['403'].includes(routeName)">
      <the-header
        @reload-page="handleRefreshPage"
        :route-name="routeName"
        :user-group-id="userGroupId"
      />
    </template>
    <main
      :class="[
        'main-layout',
        layoutCls,
        { 'external-main-layout': externalSystemsLayout.userGroup.groupDetail.setMainLayoutHeight },
        { 'no-perm-main-layout': ['403'].includes(routeName) }
      ]"
      v-bkloading="{ isLoading: mainContentLoading, opacity: 1, zIndex: 1000 }">
      <div
        v-if="isShowPage"
        ref="mainScroller"
        :class="[
          'main-scroller',
          { 'external-main-scroller': externalSystemsLayout.userGroup.groupDetail.setMainLayoutHeight }
        ]"
      >
        <router-view class="views-layout" :key="routerKey" v-show="!mainContentLoading" />
      </div>
    </main>
  </div>
</template>

<script>
  // import HeaderNav from '@/components/header-nav/index.vue';
  import theHeader from '@/components/header/index.vue';
  // import theNav from '@/components/nav/index.vue';
  import NoticeComponent from '@blueking/notice-component-vue2';
  import '@blueking/notice-component-vue2/dist/style.css';
  import { existValue, formatI18nKey } from '@/common/util';
  import { bus } from '@/common/bus';
  import { mapGetters } from 'vuex';
  import { afterEach } from '@/router';
  import { kebabCase } from 'lodash';
    
  export default {
    name: 'iframe-entry',
    provide () {
      return {
        reload: this.reload,
        reloadCurPage: this.reloadCurPage,
        showNoticeAlert: () => this.isShowNoticeAlert
      };
    },
    components: {
      theHeader,
      NoticeComponent
    },
    data () {
      return {
        routerKey: +new Date(),
        systemCls: 'mac',
        timer: null,
        layoutCls: '',
        isShowPage: true,
        groupGuideStyle: {
          top: '140px',
          left: '270px'
        },
        processGuideStyle: {
          position: 'absolute',
          top: '342px',
          left: '270px'
        },
        processGuideShow: true,
        groupGuideShow: false,
        routeName: '',
        userGroupId: '',
        isRouterAlive: true,
        showNoticeAlert: false,
        noticeApi: `${window.AJAX_URL_PREFIX}/notice/announcements/`,
        enableNotice: window.ENABLE_BK_NOTICE.toLowerCase() === 'true'
      };
    },
    computed: {
      ...mapGetters(['mainContentLoading', 'user', 'externalSystemsLayout']),
      isShowNoticeAlert () {
        return this.showNoticeAlert && this.isEnableNoticeAlert;
      },
      isEnableNoticeAlert () {
        return this.enableNotice && !this.externalSystemsLayout.hideNoticeAlert;
      }
    },
    watch: {
      '$route' (to, from) {
        this.layoutCls = kebabCase(to.name) + '-container';
        this.routeName = to.name;
        this.userGroupId = to.params.id;
        this.$store.commit('updateRoute', from.name);
      },
      user: {
        handler (value) {
          const roleMap = {
            super_manager: () => {
              this.processGuideStyle.top = '255px';
            },
            system_manager: () => {
              this.processGuideStyle.top = '305px';
            },
            rating_manager: () => {
              this.processGuideStyle.top = '385px';
            },
            subset_manager: () => {
              this.processGuideStyle.top = '305px';
            }
          };
          return roleMap[value.role.type] ? roleMap[value.role.type]() : '';
        },
        immediate: true,
        deep: true
      }
    },
    created () {
      const platform = window.navigator.platform.toLowerCase();
      window.CUR_LANGUAGE = formatI18nKey();
      this.$i18n.locale = window.CUR_LANGUAGE;
      if (platform.indexOf('win') === 0) {
        this.systemCls = 'win';
      }
      if (!existValue('externalApp')) {
        this.fetchVersionLog();
        this.fetchNoviceGuide();
      }

      const isPoll = window.localStorage.getItem('isPoll');
      if (isPoll) {
        this.$store.commit('updateSync', true);
        this.timer = setInterval(() => {
          this.fetchSyncStatus();
        }, 15000);
      }

      this.$once('hook:beforeDestroy', () => {
        bus.$off('show-login-modal');
        bus.$off('close-login-modal');
        bus.$off('updatePoll');
        bus.$off('nav-resize');
        bus.$off('show-guide');
      });
    },
    mounted () {
      bus.$on('updatePoll', (payload) => {
        clearInterval(this.timer);
        if (payload && payload.isStop) {
          return;
        }
        this.timer = setInterval(() => {
          this.fetchSyncStatus();
        }, 15000);
      });
      bus.$on('nav-resize', flag => {
        this.groupGuideStyle.left = flag ? '270px' : '90px';
        this.processGuideStyle.left = flag ? '270px' : '90px';
      });
      bus.$on('show-guide', payload => {
        const guideMap = {
          group: () => {
            this.groupGuideShow = true;
          },
          process: () => {
            this.processGuideShow = true;
          }
        };
        if (guideMap[payload]) {
          guideMap[payload]();
        }
        // if (payload === 'group') {
        //     this.groupGuideShow = true;
        // }
        // if (payload === 'process') {
        //     this.processGuideShow = true;
        // }
      });
    },
    methods: {
      reload () {
        this.isRouterAlive = false;
        this.$nextTick(() => {
          this.isRouterAlive = true;
        });
      },

      /**
       * 刷新当前 route，这个刷新和 window.location.reload 不同，这个刷新会保持 route.params
       *
       * @param {Object} route 要刷新的 route
       */
      reloadCurPage (route) {
        this.routerKey = +new Date();
        afterEach(route);
      },

      handleRefreshPage (route) {
        this.isShowPage = false;
        this.$nextTick(() => {
          this.isShowPage = true;
          this.routerKey = +new Date();
          afterEach(route);
        });
      },

      /**
       * 获取版本日志。header -> system-log
       * version_log/
       */
      async fetchVersionLog () {
        try {
          await this.$store.dispatch('versionLogInfo');
        } catch (e) {
          console.error(e);
        }
      },

      /**
       * 获取 guide 数据。iam-guide
       * users/profile/newbie/
       */
      async fetchNoviceGuide () {
        try {
          await this.$store.dispatch('getNoviceGuide');
        } catch (e) {
          console.error(e);
        }
      },

      /**
       * 获取同步组织架构的状态
       * views/user/index.vue 发出同步组织架构的请求
       */
      async fetchSyncStatus () {
        try {
          const res = await this.$store.dispatch('organization/getOrganizationsSyncTask');
          const status = res.data.status;
          if (['Succeed', 'Failed'].includes(status)) {
            if (['Succeed'].includes(status)) {
              bus.$emit('sync-success');
              this.messageSuccess(this.$t(`m.permTemplate['同步组织架构成功']`), 3000);
            }
            if (['Failed'].includes(status)) {
              this.messageAdvancedError({
                code: 0,
                limit: 1,
                theme: 'error',
                message: this.$t(`m.permTemplate['同步组织架构失败']`)
              });
            }
            window.localStorage.removeItem('isPoll');
            this.$store.commit('updateSync', false);
            clearInterval(this.timer);
            bus.$emit('on-sync-record-status');
          }
        } catch (e) {
          console.error(e);
          window.localStorage.removeItem('isPoll');
          this.$store.commit('updateSync', false);
          clearInterval(this.timer);
          this.messageAdvancedError(e);
        }
      },

      // 是否存在key
      existKey (value) {
        // 1、url截取?之后的字符串(不包含?)
        const pathSearch = window.location.search.substr(1);
        const result = [];
        // 2、以&为界截取参数键值对
        const paramItems = pathSearch.split('&');
        // 3、将键值对形式的参数存入数组
        for (let i = 0; i < paramItems.length; i++) {
          const paramKey = paramItems[i].split('=')[0];
          const paramValue = paramItems[i].split('=')[1];
          result.push({
            key: paramKey,
            value: paramValue
          });
        }
        // 4、遍历key值
        for (let j = 0; j < result.length; j++) {
          if (result[j].value === value) {
            return true;
          }
        }
        return false;
      },

      handleShowAlertChange (isShow) {
        console.log(isShow, '跑马灯回调');
        this.showNoticeAlert = isShow;
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import './css/index.css';
#app {
  .header-layout {
    padding-left: 0;
  }
  /deep/ .main-layout {
    height: 100%;
    /* height: calc(100% - 41px); */
    position: relative;
    background-color: #f5f6fa;
    overflow: hidden;
    .main-scroller {
      /* height: calc(100% + 51px); */
      height: 100%;
      overflow: auto;
    }
    .fixed,
    .fixed-action {
      padding-left: 24px !important;
    }
  }
}

.views-layout {
    min-height: 100%;
    /* min-width: 1120px; */
    padding: 24px;
}

.external-system-layout {
    height: calc(100% - 1px) !important;
}

.add-member-boundary-container {
    .external-main-scroller {
        overflow: hidden;
    }
}

.single-hide {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.external-app-layout {
  min-width: 0 !important;
  max-width: 900px !important;
}

.user-selector .user-selector-selected
.user-selector-selected-clear {
  line-height: 20px !important;
}

.flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;

}

.user-org-perm-container {
  .main-scroller {
    height: calc(100% + 278px);
  }
  .views-layout {
    min-width: 100%;
    overflow: hidden;
  }
}

.notice-app-layout {
  height: calc(100% - 101px) !important;
  .main-scroller {
    height: calc(100% + 91px);
  }
  .user-org-perm-container {
    .main-scroller {
      height: calc(100% + 312px);
    }
  }
}

.no-perm {
  &-app-layout,
  &-main-layout {
    height: 100% !important;
    background-color: #ffffff;
  }
}
</style>
