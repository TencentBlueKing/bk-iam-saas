<template>
  <!-- eslint-disable max-len -->
  <header :class="[
    'header-layout',
    { 'nav-sticked': navStick, 'hide-bread': externalSystemsLayout.hideIamBreadCrumbs && !externalRouter.includes($route.name) },
    { 'external-nav-sticked': isShowExternal }
  ]">
    <!-- <iam-guide
            v-if="showGuide"
            type="switch_role"
            direction="right"
            :flag="showGuide"
            :style="{ top: '5px', right: '125px' }"
            :content="$t(`m.guide['切换管理空间']`)" /> -->
    <div class="breadcrumbs fl"
      :class="backRouter ? 'has-cursor' : ''"
      v-show="isShowExternal || (!mainContentLoading && !externalSystemsLayout.hideIamBreadCrumbs)"
      @click="back">
      <div v-if="!isHide">
        <Icon type="arrows-left" class="breadcrumbs-back" v-if="backRouter" />
        <h2 v-if="customBreadCrumbTitles.includes(routeName)" class="breadcrumbs-current">
          {{ $t(`m.info['用户组成员添加权限']`, { value: `${$t(`m.common['【']`)}${userGroupName}${$t(`m.common['】']`)}` }) }}
        </h2>
        <h2 v-else class="breadcrumbs-current">{{ headerTitle }}</h2>
      </div>
    </div>
    <!-- <div class="user fr">
            <div class="help-flag">
                <Icon type="help-fill-2" />
                <div class="dropdown-panel">
                    <div class="item" @click="handleOpenDocu">{{ $t(`m.common['产品文档']`) }}</div>
                    <div class="item" @click="handleOpenVersion">{{ $t(`m.common['版本日志']`) }}</div>
                    <div class="item" @click="handleOpenQuestion">{{ $t(`m.common['问题反馈']`) }}</div>
                </div>
            </div>
            <p class="user-name" @click.stop="handleSwitchIdentity" data-test-id="header_btn_triggerSwitchRole">
                {{ curIdentity !== 'STAFF' ? curIdentity : user.username }}
                <Icon type="down-angle" :class="['user-name-angle', { dropped: isShowUserDropdown }]" />
            </p>
            <transition name="toggle-slide">
                <section
                    class="iam-grading-admin-list-wrapper"
                    :style="style"
                    v-show="isShowGradingWrapper"
                    v-bk-clickoutside="handleClickOutSide">
                    <div :class="['userInfo',{ 'lineHeight': curRole === 'staff' }]">
                        <p :class="userName">{{ user.username }}</p>
                        <Icon :type="identityIconMap[curRole] || ''" />
                    </div>
                    <div class="search-input">
                        <bk-input
                            :clearable="true"
                            size="small"
                            v-model="searchValue"
                            ext-cls="iam-role-list-seatch-input-cls"
                            :placeholder="placeholderValue"
                            @input="handleInput">
                        </bk-input>
                        <div v-if="isShowSearch" class="search-nextfix">
                            <slot name="nextfix">
                                <i class="bk-icon icon-search search-nextfix-icon" />
                            </slot>
                        </div>
                    </div>
                    <ul>
                        <template v-if="curRoleList.length < 1">
                            <iam-svg ext-cls="rating-empty" />
                        </template>
                        <template v-else>
                            <li class="grading-item"
                                data-test-id="header_btn_switchRole"
                                v-for="item in curRoleList"
                                :key="item.id"
                                :title="item.name"
                                :class="item.id === curRoleId ? 'active' : ''"
                                @click="handleSelect(item)">
                                <i v-if="isShowSuperManager(item)" class="superManagerIcon"></i>
                                <i v-if="isShowSystemManager(item)" class="systemManagerIcon"></i>
                                <i v-if="isShowRatingManager(item)" class="ratingManagerIcon"></i>
                                <span class="name">{{ item.name }}</span>
                                <Icon v-if="item.id === curRoleId" type="check-small" class="checked" />
                            </li>
                            <div :class="['operation', { 'right': curRole === 'staff' }]">
                                <div :class="['user-dropdown-item', { 'marginleft': curRole !== 'staff' }]"
                                    v-if="curIdentity !== '' && curRole !== 'staff'"
                                    @click="handleBack">
                                    <img src="@/images/back.svg" alt="" class="back-staff">
                                    <span>{{ $t(`m.nav['普通成员']`) }}</span>
                                </div>
                            </div>
                        </template>
                        <template>
                            <div class="operation right">
                                <div class="user-dropdown-item " @click="handleLogout">
                                    <Icon type="logout" />
                                    {{ $t(`m.nav['注销']`) }}
                                </div>
                            </div>
                        </template>
                    </ul>
                </section>
            </transition>
        </div> -->
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

  const NORMAL_DOCU_LINK = '/权限中心/产品白皮书/产品简介/README.md';
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
    name: '',
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
        curDocuLink: `${window.PRODUCT_DOC_URL_PREFIX}${NORMAL_DOCU_LINK}`,
        showGuide: false,
        isShowHeader: false,
        placeholderValue: '',
        userGroupName: '',
        externalRouter: ['permTransfer', 'permRenewal', 'addGroupPerm'], // 开放内嵌页面需要面包屑的页面
        customBreadCrumbTitles: ['addGroupPerm']
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
            this.curDocuLink = `${window.PRODUCT_DOC_URL_PREFIX}${value}`;
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
      });
    },
    mounted () {
      bus.$on('refresh-role', data => {
        this.handleSwitchRole(data);
      });
      bus.$on('on-set-tab', data => {
        this.active = data;
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
      }
    }
  };
</script>

<style>
    @import './index';
</style>
