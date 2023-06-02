<template>
  <div id="app"
    :class="[
      systemCls,
      { 'external-system-layout': externalSystemsLayout.userGroup.groupDetail.setMainLayoutHeight },
      { 'external-app-layout': $route.name === 'addMemberBoundary' }
    ]">
    <!-- <iam-guide
            v-if="groupGuideShow"
            type="create_group"
            direction="left"
            :style="groupGuideStyle"
            :flag="groupGuideShow"
            :content="$t(`m.guide['创建用户组']`)" /> -->
    <iam-guide
      v-if="processGuideShow"
      type="set_group_approval_process"
      direction="left"
      :style="processGuideStyle"
      :flag="processGuideShow"
      :content="$t(`m.guide['创建审批流程']`)" />
    <header-nav
      v-if="!externalSystemsLayout.hideIamHeader"
      @reload-page="handleRefreshPage"
      :route-name="routeName"
      :user-group-id="userGroupId">
    </header-nav>
    <the-header @reload-page="handleRefreshPage"
      :route-name="routeName"
      :user-group-id="userGroupId"
    />
    <the-nav class="nav-layout"
      @reload-page="reloadCurPage"
      v-if="!externalSystemsLayout.hideIamSlider" />
    <main
      :class="[
        'main-layout',
        layoutCls,
        { 'external-main-layout': externalSystemsLayout.userGroup.groupDetail.setMainLayoutHeight }
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
    <app-auth ref="bkAuth"></app-auth>
  </div>
</template>
<script>
    // import Cookie from 'js-cookie';
  import HeaderNav from '@/components/header-nav/index.vue';
  import theHeader from '@/components/header/index.vue';
  import theNav from '@/components/nav/index.vue';
  import IamGuide from '@/components/iam-guide/index.vue';
  import { existValue, getCookie } from '@/common/util';
  import { bus } from '@/common/bus';
  import { mapGetters } from 'vuex';
  import { afterEach } from '@/router';
  import { kebabCase } from 'lodash';
    
  export default {
    name: 'app',
    provide () {
      return {
        reload: this.reload
      };
    },
    components: {
      IamGuide,
      theHeader,
      theNav,
      HeaderNav
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
        isRouterAlive: true
      };
    },
    computed: {
            ...mapGetters(['mainContentLoading', 'user', 'externalSystemsLayout'])
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
      window.CUR_LANGUAGE = getCookie('blueking_language') || 'zh-cn';
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
      const self = this;
      bus.$on('show-login-modal', (payload) => {
        self.$refs.bkAuth.showLoginModal(payload);
      });
      bus.$on('close-login-modal', () => {
        self.$refs.bkAuth.hideLoginModal();
        setTimeout(() => {
          window.location.reload();
        }, 0);
      });
      bus.$on('updatePoll', () => {
        clearInterval(this.timer);
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
          if (status === 'Succeed' || status === 'Failed') {
            if (status === 'Succeed') {
              bus.$emit('sync-success');
            }
            window.localStorage.removeItem('isPoll');
            this.$store.commit('updateSync', false);
            clearInterval(this.timer);
            this.bkMessageInstance = this.$bkMessage({
              limit: 1,
              theme: status === 'Succeed' ? 'success' : 'error',
              message: status === 'Succeed'
                ? this.$t(`m.permTemplate['同步组织架构成功']`)
                : this.$t(`m.permTemplate['同步组织架构失败']`)
            });
          }
        } catch (e) {
          console.error(e);
          window.localStorage.removeItem('isPoll');
          this.$store.commit('updateSync', false);
          clearInterval(this.timer);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
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
        min-width: 1120px;
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

</style>
