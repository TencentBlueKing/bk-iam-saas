<template>
  <!-- eslint-disable max-len -->
  <header :class="[
    'header-layout',
    { 'nav-sticked': navStick, 'hide-bread': externalSystemsLayout.hideIamBreadCrumbs && !externalRouter.includes($route.name) },
    { 'external-nav-sticked': isShowExternal }
  ]">
    <div
      class="breadcrumbs fl"
      :class="backRouter ? 'has-cursor' : ''"
      v-show="isShowExternal || (!mainContentLoading && !externalSystemsLayout.hideIamBreadCrumbs)"
    >
      <div v-if="!isHide" class="breadcrumbs-content">
        <Icon type="arrows-left" class="breadcrumbs-back" v-if="backRouter" @click.stop="back" />
        <template v-if="customBreadCrumbTitles.includes(routeName)">
          <h2 v-if="['addGroupPerm'].includes(routeName)" class="breadcrumbs-current single-hide" :style="formatBreadCrumbWidth()">
            {{ $t(`m.info['用户组成员添加权限']`, { value: `${$t(`m.common['【']`)}${userGroupName}${$t(`m.common['】']`)}` }) }}
          </h2>
          <template v-if="['renewalNotice'].includes(routeName)">
            <h2 class="breadcrumbs-current single-hide" :style="formatBreadCrumbWidth()">
              {{ headerTitle }}
            </h2>
            <bk-switcher size="large" theme="primary" v-model="needProvideValue.isShowRenewalNotice" @change="handleChangeRenewalNotice" />
          </template>
          <div v-if="['actionsTemplateEdit'].includes(routeName)" class="breadcrumbs-content-actions-template-edit">
            <div class="breadcrumbs-text">
              <span class="breadcrumbs-text-title">{{ $t(`m.actionsTemplate['编辑模板操作']`) }}</span>
              <span class="vertical-line">|</span>
              <div class="breadcrumbs-text-name">
                <div class="title">{{ $t(`m.common['模板名称']`) }}{{ $t(`m.common['：']`) }}</div>
                <div class="single-hide name" :style="formatBreadCrumbWidth()">{{ headerTitle }}</div>
              </div>
            </div>
            <bk-steps :steps="actionSteps" :cur-step="needProvideValue.curACtionStep" ext-cls="actions-template-edit-step" @step-changed="handleStepChange" />
          </div>
        </template>
        <h2 v-else class="breadcrumbs-current single-hide" :style="formatBreadCrumbWidth()">
          {{ headerTitle }}
        </h2>
      </div>
    </div>
    <div class="page-tab-wrapper" :style="{ top: externalSystemsLayout.hideIamBreadCrumbs ? '0' : '51px' }" v-if="hasPageTab">
      <bk-tab
        :active.sync="active"
        type="unborder-card"
        ext-cls="iam-page-tab-ext-cls"
        @tab-change="handlePageTabChange">
        <bk-tab-panel
          v-for="(panel, index) in panels"
          v-bind="panel"
          :key="index">
        </bk-tab-panel>
      </bk-tab>
    </div>
    <system-log v-model="showSystemLog" />
  </header>
</template>

<script>
  import { mapGetters } from 'vuex';
  // import IamGuide from '@/components/iam-guide/index.vue';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import { NEED_CONFIRM_DIALOG_ROUTER } from '@/common/constants';
  import { il8n, language } from '@/language';
  import { bus } from '@/common/bus';
  import { buildURLParams } from '@/common/url';
  import SystemLog from '../system-log';
  import { getRouterDiff } from '@/common/router-handle';

  // 有选项卡的页面，user-group-detail 以及 perm-template-detail
  const getTabData = (routerName) => {
    const map = {
      '': [],
      'permTemplateDetail': [
        {
          name: 'TemplateDetail', label: il8n('permTemplate', '模板详情')
        },
        {
          name: 'AttachGroup', label: il8n('permTemplate', '关联的组')
        }
      ],
      'userGroupDetail': [
        {
          name: 'GroupDetail', label: il8n('userGroup', '组详情')
        },
        {
          name: 'GroupPerm', label: il8n('userGroup', '组权限')
        }
      ]
    };

    return map[routerName];
  };

  const getIdentityIcon = () => {
    const str = language === 'zh-cn' ? '' : '-en';
    return {
      '': `super-admin-new${str}`,
      'super_manager': `super-admin-new${str}`,
      'system_manager': `system-admin-new${str}`,
      'rating_manager': `grade-admin-new${str}`
    };
  };

  const NORMAL_DOCU_LINK = '/IAM/UserGuide/Introduce/README.md';
  // const GRADE_DOCU_LINK = '/权限中心/产品白皮书/场景案例/GradingManager.md';

  const docuLinkMap = new Map([
    // 权限模板
    [['permTemplate', 'permTemplateDetail', 'permTemplateCreate'], NORMAL_DOCU_LINK],
    // 首页
    [['', 'index'], NORMAL_DOCU_LINK],
    // 用户组
    [['userGroup', 'userGroupDetail', 'createUserGroup', 'userGroupPermDetail'], NORMAL_DOCU_LINK],
    // 系统接入
    [['systemAccess'], NORMAL_DOCU_LINK],
    // 我的申请
    [['apply'], NORMAL_DOCU_LINK],
    // 权限申请 'permApply'
    [['applyCustomPerm', 'applyJoinUserGroup'], NORMAL_DOCU_LINK],
    // 我的权限
    [['myPerm', 'templatePermDetail', 'groupPermDetail', 'permRenewal'], NORMAL_DOCU_LINK],
    // 管理空间
    [['ratingManager', 'gradingAdminDetail', 'gradingAdminCreate', 'gradingAdminEdit'], NORMAL_DOCU_LINK],
    // 管理员
    [['administrator'], NORMAL_DOCU_LINK],
    // 审批流程
    [['approvalProcess'], NORMAL_DOCU_LINK],
    // 用户
    [['user'], NORMAL_DOCU_LINK]
  ]);

  export default {
    provide () {
      return {
        needProvideValue: this.needProvideValue
      };
    },
    components: {
      SystemLog
      // IamGuide
    },
    props: {
      routeName: {
        type: String,
        default: ''
      },
      userGroupId: {
        type: [String, Number]
      }
    },
    data () {
      return {
        isShowUserDropdown: false,
        showSystemLog: false,
        isShowGradingWrapper: false,
        curIdentity: '',
        curRole: '',
        curRoleId: 0,
        iconMap: {
          '': 'personal-user',
          'super_manager': 'super-admin',
          'system_manager': 'system-admin',
          'rating_manager': 'grade-admin',
          'staff': 'personal-user'
        },
        identityIconMap: getIdentityIcon(),
        // super_manager: 超级用户, staff: 普通用户, system_manager: 系统管理员, rating_manager: 管理空间
        roleDisplayMap: {
          'super_manager': this.$t(`m.myApproval['超级管理员']`),
          'system_manager': this.$t(`m.nav['系统管理员']`),
          'rating_manager': this.$t(`m.grading['管理空间']`),
          'staff': this.$t(`m.nav['普通用户']`)
        },
        // curHeight: 500,

        hasPageTab: false,
        panels: [
          { name: 'mission', label: '任务报表' }
        ],
        active: 'mission',
        getTabData: getTabData,
        curRoleList: [],
        searchValue: '',
        docuLinkMap: docuLinkMap,
        curDocuLink: `${window.BK_DOCS_URL_PREFIX}${NORMAL_DOCU_LINK}`,
        showGuide: false,
        isShowHeader: false,
        placeholderValue: '',
        userGroupName: '',
        externalRouter: ['permTransfer', 'permRenewal', 'addGroupPerm'], // 开放内嵌页面需要面包屑的页面
        customBreadCrumbTitles: ['addGroupPerm', 'renewalNotice', 'actionsTemplateEdit'],
        // 需要provide的变量
        needProvideValue: {
          isShowRenewalNotice: false,
          curACtionStep: 1
        },
        actionSteps: [
          { title: this.$t(`m.permApply['选择操作']`), icon: 1 },
          { title: this.$t(`m.actionsTemplate['同步用户组']`), icon: 2 }
        ]
      };
    },
    computed: {
      ...mapGetters([
        'navStick',
        'headerTitle',
        'backRouter',
        'user',
        'mainContentLoading',
        'roleList',
        'externalSystemsLayout',
        'externalSystemId'
      ]),
      style () {
        return {
          height: `${this.curHeight}px`
        };
      },
      curAccountLogo () {
        return [].slice.call(this.user.username)[0].toUpperCase() || '-';
      },
      isHide () {
        return this.$route.query.system_id && this.$route.query.tid;
      },
      isShowSearch () {
        return this.searchValue === '';
      },
      isShowExternal () {
        return this.externalRouter.includes(this.$route.name) && this.externalSystemsLayout.hideIamBreadCrumbs;
      },
      formatBreadCrumbWidth () {
        return () => {
          const routeMap = {
            renewalNotice: () => {
              const switchWidth = 52;
              return {
                'max-width': `calc(100vw - ${this.navStick ? 280 - switchWidth : 80 - switchWidth}px)`,
                'margin-right': '10px'
              };
            },
            actionsTemplateEdit: () => {
              return {
                'max-width': `150px`
              };
            }
          };
          if (routeMap[this.$route.name]) {
            return routeMap[this.$route.name]();
          }
          return {
            'max-width': `calc(100vw - ${this.navStick ? 280 : 80}px)`
          };
        };
      }
    },
    watch: {
      '$route': function (to, from) {
        this.hasPageTab = !!to.meta.hasPageTab;
        if (['permTemplateDetail', 'userGroupDetail'].includes(to.name)) {
          this.panels = this.getTabData(to.name);
          let active = to.query.tab || this.panels[0].name;
          if (active === 'group_perm') {
            active = 'GroupPerm';
          }
          this.active = active;
        }
        for (const [key, value] of this.docuLinkMap.entries()) {
          if (key.includes(to.name)) {
            this.curDocuLink = `${window.BK_DOCS_URL_PREFIX}${value}`;
            break;
          }
        }
      },
      user: {
        handler (value) {
          this.curRoleId = value.role.id || 0;
          this.placeholderValue = this.$t(`m.common['切换身份']`);
        },
        deep: true
      },
      roleList: {
        handler (newValue, oldValue) {
          this.curRoleList.splice(0, this.curRoleList.length, ...newValue);
        },
        immediate: true
      },
      isShowGradingWrapper (value) {
        if (!value) {
          this.searchValue = '';
        }
      },
      routeName: {
        handler (value) {
          if (value === 'addGroupPerm') {
            this.fetchUserGroup();
          }
        },
        immediate: true
      },
      'needProvideValue.curStep': {
        handler (value) {
          bus.$emit('on-change-temp-action-step', { step: value });
        },
        deep: true
      }
    },
    created () {
      this.curRole = this.user.role.type;
      this.curIdentity = this.user.role.name;
      bus.$emit('theme-change', this.curRole);
      this.curRoleId = this.user.role.id;
      this.$once('hook:beforeDestroy', () => {
        bus.$off('reload-page');
        bus.$off('refresh-role');
        bus.$off('on-set-tab');
        bus.$off('on-refresh-renewal-status');
      });
    },
    mounted () {
      bus.$on('refresh-role', data => {
        this.handleSwitchRole(data);
      });
      bus.$on('on-set-tab', data => {
        this.active = data;
      });
      bus.$on('on-refresh-renewal-status', (payload) => {
        const isShowRenewalNotice = payload.isShowRenewalNotice || false;
        this.needProvideValue = Object.assign(this.needProvideValue, { isShowRenewalNotice });
      });
    },
    methods: {
      // 获取用户组详情
      async fetchUserGroup () {
        const params = {
          id: this.userGroupId
        };
        if (this.externalSystemId) {
          params.hidden = false;
        }
        try {
          const res = await this.$store.dispatch('userGroup/getUserGroupDetail', params);
          this.$nextTick(() => {
            this.$set(this, 'userGroupName', res.data.name);
          });
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },
      handleClickOutSide (e) {
        this.isShowGradingWrapper = false;
      },

      // super_manager: 超级用户, staff: 普通用户, system_manager: 系统管理员, rating_manager: 管理空间
      isShowSuperManager (value) {
        if (value.type === 'super_manager') {
          return true;
        }
      },
      isShowSystemManager (value) {
        if (value.type === 'system_manager') {
          return true;
        }
      },
      isShowRatingManager (value) {
        if (value.type === 'rating_manager') {
          return true;
        }
      },

      handleChangeRenewalNotice (payload) {
        this.needProvideValue = Object.assign(this.needProvideValue, { isShowRenewalNotice: payload });
        bus.$emit('on-update-renewal-notice', { isShowRenewalNotice: payload });
      },

      handleInput (value) {
        this.curRoleList = this.roleList.filter(item => item.name.indexOf(value) > -1);
      },

      handleOpenVersion () {
        this.showSystemLog = true;
      },

      handleOpenDocu () {
        window.open(this.curDocuLink);
      },

      handleOpenQuestion () {
        window.open(window.CE_URL);
      },

      back () {
        const curRouterName = this.$route.name;
        const needConfirmFlag = NEED_CONFIRM_DIALOG_ROUTER.includes(curRouterName);
        let cancelHandler = Promise.resolve();
        if (window.changeDialog && needConfirmFlag) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(() => {
          if (this.$route.name === 'applyCustomPerm') {
            this.$router.push({
              name: 'applyJoinUserGroup'
            });
          } else if (this.backRouter === -1) {
            history.go(-1);
          } else {
            this.$router.push({
              name: this.backRouter,
              params: this.$route.params,
              query: this.$route.query
            });
          }
        }, _ => _);
      },

      updateRouter (roleType) {
        this.$store.commit('updataRouterDiff', roleType);
        const difference = getRouterDiff(roleType);
        const curRouterName = this.$route.name;
        if (difference.length) {
          if (difference.includes(curRouterName)) {
            this.$store.commit('setHeaderTitle', '');
            window.localStorage.removeItem('iam-header-title-cache');
            window.localStorage.removeItem('iam-header-name-cache');
            if (roleType === 'staff' || roleType === '') {
              this.$router.push({
                name: 'myPerm'
              });
              return;
            }
            this.$router.push({
              // name: 'permTemplate'
              // 切换角色默认跳转到用户组
              name: 'userGroup'
            });
            return;
          }

          const permTemplateRoutes = [
            'permTemplateCreate', 'permTemplateDetail',
            'permTemplateEdit', 'permTemplateDiff'
          ];
          if (permTemplateRoutes.includes(curRouterName)) {
            this.$router.push({ name: 'permTemplate' });
            return;
          }
          if (['createUserGroup', 'userGroupDetail'].includes(curRouterName)) {
            this.$router.push({ name: 'userGroup' });
            return;
          }
          if (['gradingAdminDetail', 'gradingAdminEdit', 'gradingAdminCreate'].includes(curRouterName)) {
            this.$router.push({ name: 'ratingManager' });
            return;
          }
          this.$emit('reload-page', this.$route);
          return;
        }
        this.$emit('reload-page', this.$route);
      },

      async handleSwitchRole ({ id, type, name }) {
        try {
          await this.$store.dispatch('role/updateCurrentRole', { id });
          this.messageSuccess(this.$t(`m.info['切换身份成功']`), 3000);
          this.curIdentity = id === 0 ? 'STAFF' : name;
          this.curRole = type;
          this.curRoleId = id;
          this.$store.commit('updateIdentity', { id, type, name });
          this.updateRouter(type);
          this.resetLocalStorage();
          bus.$emit('theme-change', this.curRole);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      handleSelect (roleData) {
        if (this.curRoleId === roleData.id) {
          return;
        }
        if (this.routeName === 'addGroupPerm') {
          this.$router.push({
            name: 'userGroup'
          });
        }
        this.isShowGradingWrapper = false;
        this.isShowUserDropdown = false;
        this.handleSwitchRole(roleData);
      },

      handleSwitchIdentity () {
        // this.curHeight = document.getElementsByClassName('user-dropdown')[0].offsetHeight
        this.isShowGradingWrapper = !this.isShowGradingWrapper;
      },

      handleBack () {
        this.isShowUserDropdown = false;
        this.isShowGradingWrapper = false;
        this.handleSwitchRole({ id: 0, type: 'staff', name: this.user.role.name });
      },

      handleLogout () {
        window.localStorage.removeItem('iam-header-title-cache');
        window.localStorage.removeItem('iam-header-name-cache');
        window.localStorage.removeItem('applyGroupList');
        window.location = window.LOGIN_SERVICE_URL + '/?c_url=' + window.location.href;
      },

      resetLocalStorage () {
        window.localStorage.removeItem('customPermProcessList');
        window.localStorage.removeItem('gradeManagerList');
        window.localStorage.removeItem('auditList');
        window.localStorage.removeItem('joinGroupProcessList');
        window.localStorage.removeItem('groupList');
        window.localStorage.removeItem('templateList');
        window.localStorage.removeItem('applyGroupList');
        window.localStorage.removeItem('iam-header-title-cache');
        window.localStorage.removeItem('iam-header-name-cache');
      },

      handlePageTabChange (name) {
        bus.$emit('on-tab-change', name);

        let tab = '';
        if (name === 'GroupDetail') {
          tab = 'group_detail';
        } else if (name === 'GroupPerm') {
          tab = 'group_perm';
        }
        if (tab) {
          window.history.replaceState({}, '', `?${buildURLParams(Object.assign({}, this.$route.query, {
            tab: tab
          }))}`);
        }
      },

      handleStepChange (payload) {
        console.log(payload);
      }
    }
  };
</script>

<style>
  @import './index';
</style>
