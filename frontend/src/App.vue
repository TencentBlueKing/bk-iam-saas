<template>
  <div id="app"
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
    <!-- <iam-guide
            v-if="groupGuideShow"
            type="create_group"
            direction="left"
            :style="groupGuideStyle"
            :flag="groupGuideShow"
            :content="$t(`m.guide['创建用户组']`)" /> -->
    <template v-if="!['403'].includes(routeName)">
      <!-- <iam-guide
        v-if="processGuideShow"
        type="set_group_approval_process"
        direction="left"
        :cur-style="processGuideStyle"
        :flag="processGuideShow"
        :content="$t(`m.guide['创建审批流程']`)" /> -->
      <header-nav
        v-if="!externalSystemsLayout.hideIamHeader"
        @reload-page="handleRefreshPage"
        :route-name="routeName"
        :user-group-id="userGroupId"
      />
      <the-header
        @reload-page="handleRefreshPage"
        :route-name="routeName"
        :user-group-id="userGroupId"
      />
      <the-nav
        class="nav-layout"
        :route-name="routeName"
        @reload-page="reloadCurPage"
        v-if="!externalSystemsLayout.hideIamSlider"
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
      <div ref="mainScroller"
        :class="[
          'main-scroller',
          { 'external-main-scroller': externalSystemsLayout.userGroup.groupDetail.setMainLayoutHeight }
        ]"
        v-if="isShowPage">
        <router-view class="views-layout" :key="routerKey" v-show="!mainContentLoading"></router-view>
      </div>
    </main>
    <!-- <app-auth ref="bkAuth"></app-auth> -->
    <!-- 用户组推荐未开启高级设置改用message提示 -->
    <!-- <template v-if="!enableGroupInstanceSearch && needShowInstanceSearchRoute && noInstanceSearchData.show">
      <FunctionalDependency
        v-model="noInstanceSearchData.show"
        :mode="noInstanceSearchData.mode"
        :show-dialog="['dialog'].includes(noInstanceSearchData.mode)"
        :title="noInstanceSearchData.title"
        :functional-desc="noInstanceSearchData.functionalDesc"
        :guide-title="noInstanceSearchData.guideTitle"
        :guide-desc-list="noInstanceSearchData.guideDescList"
        @gotoMore="handleMoreInfo(noInstanceSearchData.url)"
      />
    </template> -->
  </div>
</template>

<script>
    // import Cookie from 'js-cookie';
  import HeaderNav from '@/components/header-nav/index.vue';
  import theHeader from '@/components/header/index.vue';
  import theNav from '@/components/nav/index.vue';
  import NoticeComponent from '@blueking/notice-component-vue2';
  // import FunctionalDependency from '@blueking/functional-dependency/vue2/index.umd.min.js';
  import '@blueking/functional-dependency/vue2/vue2.css';
  import '@blueking/notice-component-vue2/dist/style.css';
  // import IamGuide from '@/components/iam-guide/index.vue';
  import { existValue, formatI18nKey, navDocCenterPath } from '@/common/util';
  import { bus } from '@/common/bus';
  import { buildURLParams } from '@/common/url';
  import { mapGetters } from 'vuex';
  import { afterEach } from '@/router';
  import { kebabCase } from 'lodash';
    
  export default {
    name: 'app',
    provide () {
      return {
        reload: this.reload,
        reloadCurPage: this.reloadCurPage,
        // 基本类型不具备响应式，这里需要根据异步操作动态计算所以这里返回function
        showNoticeAlert: () => this.isShowNoticeAlert
      };
    },
    components: {
      // IamGuide,
      theHeader,
      theNav,
      HeaderNav,
      NoticeComponent
      // FunctionalDependency
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
        enableNotice: window.ENABLE_BK_NOTICE.toLowerCase() === 'true',
        // enableGroupInstanceSearch: window.ENABLE_GROUP_INSTANCE_SEARCH.toLowerCase() === 'true',
        // 需要展示FunctionalDependency组件的页面
        needShowInstanceSearchRoute: ['applyCustomPerm'],
        noInstanceSearchData: {
          show: false,
          mode: '',
          title: '',
          functionalDesc: '',
          guideTitle: '',
          guideDescList: []
        }
      };
    },
    computed: {
      ...mapGetters(['mainContentLoading', 'user', 'externalSystemsLayout', 'versionLogs']),
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
        if (this.user.role && this.user.role.id > 0) {
          window.history.replaceState({}, '', `?${buildURLParams({
            ...to.query,
             role_name: this.user.role.name
          })}`);
        }
        this.$store.commit('updateRoute', from.name);
        // this.getRouteInstanceSearch({ routeName: to.name });
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
        this.fetchUserGlobalConfig();
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
        bus.$off('show-function-dependency');
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
      });
      bus.$on('show-function-dependency', (payload = {}) => {
        this.getRouteInstanceSearch(payload);
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
      
      /**
       * 获取用户全局配置
       */
      async fetchUserGlobalConfig () {
        await this.$store.dispatch('userGlobalConfig/getCurrentGlobalConfig');
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
      },

      handleMoreInfo (payload) {
        window.open(`${window.BK_DOCS_URL_PREFIX}${payload}`);
      },

      async getRouteInstanceSearch (payload = {}) {
        const { show, routeName } = payload;
        const curPath = await navDocCenterPath(this.versionLogs, `/UserGuide/Feature/PermissionsApply.md`, false);
        const routeMap = {
          applyCustomPerm: () => {
            this.noInstanceSearchData = Object.assign({}, {
              show: show || false,
              mode: 'dialog',
              url: curPath,
              title: this.$t(`m.permApply['未启用用户组自动推荐功能']`),
              functionalDesc: this.t(`m.permApply['该功能可以根据用户当前的权限需求，自动匹配相关的用户组']`),
              guideTitle: this.$t(`m.permApply['如需启用该功能，请联系部署同学部署相关ES服务']`),
              guideDescList: []
            });
            if (this.noInstanceSearchData.show) {
              this.$nextTick(() => {
                const buttonList = document.getElementsByClassName('fuctional-deps-button-text');
                if (buttonList && buttonList.length > 0) {
                  const customButtonList = [this.$t(`m.common['了解更多']`), this.$t(`m.common['取消']`)];
                  for (let i = 0; i < buttonList.length; i++) {
                    buttonList[i].innerText = customButtonList[i];
                  }
                }
              });
            }
          }
        };
        if (routeMap[routeName]) {
          return routeMap[routeName]();
        }
      }
    }
  };
</script>

<style lang="postcss">
    @import './css/index.css';

    .nav-layout {
        position: relative;
        float: left;
        height: calc(100% + 10px);
        margin: -51px 0 0 0;
    }

    .main-layout {
        position: relative;
        height: calc(100% - 41px);
        background-color: #f5f6fa;
        overflow: hidden;
    }

    .main-scroller {
        height: calc(100% + 51px);
        overflow: auto;
    }

    .views-layout {
        min-height: 100%;
        /* min-width: 1120px; */
        padding: 24px;
    }

    .external-system-layout {
        height: calc(100% - 1px) !important;
    }

    .external-main-scroller, .external-main-layout {
        height: 100%;
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

    .user-selector .user-selector-selected .user-selector-selected-clear {
        line-height: 20px !important;
    }

    .flex-between {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .flex-center {
        display: flex;
        align-items: center;
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
      .my-perm-container {
        .main-scroller {
          height: calc(100% + 51px);
        }
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
    
    /* table嵌套多层组件， popover应用样式未穿透 */
    .bk-user-selector-popover {
      visibility: visible !important;
    }
</style>
