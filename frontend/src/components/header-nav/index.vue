<template>
    <!-- eslint-disable max-len -->
    <header class="header-nav-layout">
        <div :class="['logo', 'fl']" @click.stop="handleBackHome">
            <iam-svg name="logo" :alt="$t(`m.nav['蓝鲸权限中心']`)" />
            <span class="text">{{ $t('m.nav["蓝鲸权限中心"]') }}</span>
        </div>
        <div class="header-breadcrumbs fl">
            <div class="nav-container">
                <span v-for="(item, i) in navData" :key="item.id">
                    <h2
                        v-if="item.show"
                        class="heaer-nav-title"
                        @click="handleSelect(item, i)"
                        :class="index === i ? 'active' : ''"
                    >
                        {{ item.text }}
                    </h2>
                </span>
                <!-- <iam-guide
                    v-if="haveManager"
                    type="switch_role"
                    direction="top"
                    :flag="showGuide"
                    :style="{ top: '10px', left: '240px' }"
                    :content="$t(`m.guide['管理空间导航']`)"
                /> -->
            </div>
        </div>
        <div class="user fr">
            <div class="help-flag">
                <Icon type="help-fill" style="color: #979ba5" />
                <div :class="[
                    'dropdown-panel',
                    { 'lang-dropdown-panel': !curLanguageIsCn }
                ]">
                    <div class="item" @click="handleOpenDocu">{{ $t(`m.common['产品文档']`) }}</div>
                    <div class="item" @click="handleOpenVersion">
                        {{ $t(`m.common['版本日志']`) }}
                    </div>
                    <div class="item" @click="handleOpenQuestion">
                        {{ $t(`m.common['问题反馈']`) }}
                    </div>
                </div>
            </div>
            <div class="lang-flag">
                <Icon :type="`icon-${$i18n.locale}`" />
                <div class="dropdown-panel">
                    <div
                        :class="[
                            'item',
                            {
                                'item-active': $i18n.locale === item.value
                            }
                        ]"
                        @click="handleChangeLocale(item.value)"
                        v-for="item in languageList"
                        :key="item.value"
                    >
                        {{ item.label }}
                    </div>
                </div>
            </div>
            <p
                class="user-name"
                @click.stop="handleSwitchIdentity"
                data-test-id="header_btn_triggerSwitchRole"
            >
                {{ user.username }}
                <Icon
                    type="down-angle"
                    :class="['user-name-angle', { dropped: isShowUserDropdown }]"
                />
            </p>
            <transition name="toggle-slide">
                <section
                    class="iam-grading-admin-list-wrapper"
                    :style="style"
                    v-show="isShowGradingWrapper"
                    v-bk-clickoutside="handleClickOutSide"
                >
                    <template>
                        <!-- <div class="operation auth-manager" v-if="roleList.length">
                            <div class="user-dropdown-item " :title="$t(`m.nav['切换管理空间']`)" @click="handleManager">
                                <Icon type="grade-admin" class="iam-manager-icon" />
                                {{ $t(`m.nav['切换管理空间']`) }}
                            </div>
                        </div> -->
                        <div class="operation">
                            <div
                                class="user-dropdown-item"
                                :title="$t(`m.nav['退出登录']`)"
                                @click="handleLogout"
                            >
                                <Icon type="logout" />
                                {{ $t(`m.nav['退出登录']`) }}
                            </div>
                        </div>
                    </template>
                </section>
                <!-- <template>
                    <div class="operation right">
                        <div class="user-dropdown-item " @click="handleLogout">
                            <Icon type="logout" />
                            {{ $t(`m.nav['注销']`) }}
                        </div>
                    </div>
                </template> -->
            </transition>
        </div>
        <system-log v-model="showSystemLog" />
    </header>
</template>

<script>
    import { mapGetters } from 'vuex';
    // import IamGuide from '@/components/iam-guide/index.vue';
    import { leavePageConfirm } from '@/common/leave-page-confirm';
    import { il8n, language } from '@/language';
    import { bus } from '@/common/bus';
    import { buildURLParams } from '@/common/url';
    import { getCookie } from '@/common/util';
    import { NEED_CONFIRM_DIALOG_ROUTER } from '@/common/constants';
    import SystemLog from '../system-log';
    import { getRouterDiff, getNavRouterDiff } from '@/common/router-handle';
    import Cookie from 'js-cookie';
    import magicbox from 'bk-magic-vue';

    // 有选项卡的页面，user-group-detail 以及 perm-template-detail
    const getTabData = (routerName) => {
        const map = {
            '': [],
            permTemplateDetail: [
                {
                    name: 'TemplateDetail',
                    label: il8n('permTemplate', '模板详情')
                },
                {
                    name: 'AttachGroup',
                    label: il8n('permTemplate', '关联的组')
                }
            ],
            userGroupDetail: [
                {
                    name: 'GroupDetail',
                    label: il8n('userGroup', '组详情')
                },
                {
                    name: 'GroupPerm',
                    label: il8n('userGroup', '组权限')
                }
            ]
        };

        return map[routerName];
    };

    const getIdentityIcon = () => {
        const str = language === 'zh-cn' ? '' : '-en';
        return {
            '': `super-admin-new${str}`,
            super_manager: `super-admin-new${str}`,
            system_manager: `system-admin-new${str}`,
            rating_manager: `grade-admin-new${str}`
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
        [
            ['userGroup', 'userGroupDetail', 'createUserGroup', 'userGroupPermDetail'],
            NORMAL_DOCU_LINK
        ],
        // 系统接入
        [['systemAccess'], NORMAL_DOCU_LINK],
        // 我的申请
        [['apply'], NORMAL_DOCU_LINK],
        // 权限申请 'permApply'
        [['applyCustomPerm', 'applyJoinUserGroup'], NORMAL_DOCU_LINK],
        // 我的权限
        [['myPerm', 'templatePermDetail', 'groupPermDetail', 'permRenewal'], NORMAL_DOCU_LINK],
        // 管理空间
        [
            ['ratingManager', 'gradingAdminDetail', 'gradingAdminCreate', 'gradingAdminEdit'],
            NORMAL_DOCU_LINK
        ],
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
                type: String
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
                    super_manager: 'super-admin',
                    system_manager: 'system-admin',
                    rating_manager: 'grade-admin',
                    staff: 'personal-user'
                },
                identityIconMap: getIdentityIcon(),
                // super_manager: 超级用户, staff: 普通用户, system_manager: 系统管理员, rating_manager: 管理空间
                roleDisplayMap: {
                    super_manager: this.$t(`m.myApproval['超级管理员']`),
                    system_manager: this.$t(`m.nav['系统管理员']`),
                    rating_manager: this.$t(`m.grading['管理空间']`),
                    staff: this.$t(`m.nav['普通用户']`)
                },
                // curHeight: 500,

                hasPageTab: false,
                panels: [{ name: 'mission', label: '任务报表' }],
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
                navData: [
                    { text: this.$t(`m.nav['个人工作台']`), id: 0, show: true, type: 'staff' },
                    { text: this.$t(`m.nav['管理空间']`), id: 1, show: true, type: 'all_manager' },
                    { text: this.$t(`m.nav['统计分析']`), id: 2, show: false, type: 'super_manager' },
                    { text: this.$t(`m.nav['平台管理']`), id: 3, show: false, type: 'super_manager' }
                ],
                defaultRouteList: ['myPerm', 'userGroup', 'audit', 'user', 'addGroupPerm'],
                isRatingChange: false,
                haveManager: false,
                showNavDataLength: 0,
                curHeight: 78,
                languageList: [
                    {
                        label: '中文',
                        value: 'zh-cn'
                    },
                    {
                        label: 'English',
                        value: 'en'
                    }
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
            'index',
            'navCurRoleId',
            'externalSystemId'
            ]),
            style () {
                return {
                    // height: `${this.roleList.length ? this.curHeight : 46}px`
                    height: `46px`
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
            }
        },
        watch: {
            $route: function (to, from) {
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
                    this.curRole = value.role.type || 'staff';
                    this.placeholderValue = this.$t(`m.common['切换身份']`);
                },
                deep: true
            },
            roleList: {
                handler (newValue, oldValue) {
                    this.curRoleList.splice(0, this.curRoleList.length, ...newValue);
                    if (this.curRoleList.length) {
                        this.setTabRoleData();
                    }
                    this.setNavData();
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
                    const index = this.defaultRouteList.findIndex((item) => item === value);
                    if (index > -1) {
                        ['addGroupPerm'].includes(value)
                            ? this.fetchUserGroup()
                            : this.$store.commit('updateIndex', index);
                    }
                },
                immediate: true
            },
            navData: {
                handler (newValue, oldValue) {
                    if ((!oldValue || (oldValue && oldValue.length < 1)) && newValue.length > 0) {
                        this.showGuide = true;
                    }
                    this.showNavDataLength = newValue.filter((e) => e.show).length;
                    this.haveManager
                        = this.showNavDataLength
                            && this.showGuide
                            && newValue.find((item) => ['all_manager'].includes(item.type) && item.show);
                },
                immediate: true,
                deep: true
            }
        },
        created () {
            const { id, name, type } = this.user.role;
            this.curRole = type;
            this.curIdentity = name;
            this.curRoleId = id;
            this.$once('hook:beforeDestroy', () => {
                bus.$off('reload-page');
                bus.$off('refresh-role');
                bus.$off('on-set-tab');
                bus.$off('rating-admin-change');
            });
            this.setNavData();
        },
        mounted () {
            bus.$on('on-set-tab', (data) => {
                this.active = data;
            });

            bus.$on('rating-admin-change', () => {
                const data = this.navData.find((e) => e.type === 'staff');
                this.isRatingChange = true;
                this.handleSelect(data, 0);
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
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
                    });
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
                this.curRoleList = this.roleList.filter((item) => item.name.indexOf(value) > -1);
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
                cancelHandler.then(
                    () => {
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
                    },
                    (_) => _
                );
            },

            async updateRouter (navIndex = 0) {
                let difference = [];
                if (navIndex === 1) {
                    await this.$store.dispatch('userInfo');
                    const type = this.curRole;
                    difference = getRouterDiff(type);
                    this.$store.commit('updataRouterDiff', type);
                } else {
                    difference = getNavRouterDiff(navIndex);
                    this.$store.commit('updataNavRouterDiff', navIndex);
                }
                const curRouterName = this.$route.name;
                if (difference.length) {
                    if (difference.includes(curRouterName)) {
                        this.$store.commit('setHeaderTitle', '');
                        window.localStorage.removeItem('iam-header-title-cache');
                        window.localStorage.removeItem('iam-header-name-cache');
                        this.$router.push({
                            name: this.isRatingChange ? 'myManageSpace' : this.defaultRouteList[navIndex],
                            params: navIndex === 1 ? { id: this.user.role.id, entry: 'updateRole' } : {}
                        });
                    } else {
                        // if (navIndex === 0 && ['gradingAdminDetail', 'gradingAdminCreate', 'gradingAdminEdit'].includes(curRouterName)) {
                        //     this.$router.push({
                        //         name: 'myPerm'
                        //     });
                        // } else if (navIndex === 3 && ['gradingAdminDetail', 'gradingAdminCreate', 'gradingAdminEdit', 'myManageSpaceCreate', 'myManageSpaceSubDetail'].includes(curRouterName)) {
                        //     this.$router.push({
                        //         name: 'user'
                        //     });
                        // }
                        // 修复当前是添加组权限页面点击其他角色菜单会再次跳到权限管理
                        // 处理二级管理空间点击staff菜单不刷新路由问题
                        // 处理超级管理员账号下头部导航没选择默认路由问题
                        const OtherRoute = [
                            'gradingAdminDetail',
                            'gradingAdminCreate',
                            'gradingAdminEdit',
                            'myManageSpaceCreate',
                            'secondaryManageSpaceCreate',
                            'secondaryManageSpaceDetail',
                            'addGroupPerm',
                            'authorBoundaryEditFirstLevel'
                        ];
                        if (OtherRoute.includes(curRouterName)) {
                            this.$router.push({
                                name: this.defaultRouteList[navIndex]
                            });
                        }
                    }
                }
            },

            async handleSelect (roleData, index) {
                if (window.changeDialog && NEED_CONFIRM_DIALOG_ROUTER.includes(this.$route.name)) {
                    const cancelHandler = leavePageConfirm();
                    cancelHandler.then(
                        () => {
                            this.handleHeaderNav(roleData, index);
                        },
                        (_) => _
                    );
                } else {
                    this.handleHeaderNav(roleData, index);
                }
            },

            // 处理当前页未保存信息切换头部导航栏校验
            async handleHeaderNav (roleData, index) {
                const currentData = { ...roleData };
                this.navData.forEach((e) => {
                    e.active = false;
                });
                this.$set(currentData, 'active', true);
                this.$store.commit('updateIndex', index);
                window.localStorage.setItem('index', index);
                // if (this.routeName === 'addGroupPerm') {
                //     this.$router.push({
                //         name: 'userGroup'
                //     });
                // }
                this.isShowGradingWrapper = false;
                this.isShowUserDropdown = false;
                try {
                    await this.$store.dispatch('role/updateCurrentRole', { id: currentData.id });
                    bus.$emit('nav-change', { id: currentData.id }, index);
                    this.updateRouter(index);
                } catch (err) {
                    if (index === 1 && this.curRoleList.length) {
                        this.resetLocalStorage();
                        const { id, type, name } = this.curRoleList[0];
                        this.$set(currentData, 'id', id);
                        this.navCurRoleId = id;
                        this.curRoleId = id;
                        this.curRole = type;
                        this.$store.commit('updateCurRoleId', id);
                        this.$store.commit('updateIdentity', { id, type, name });
                        this.$store.commit('updateNavId', id);
                        this.$store.commit('updateIndex', index);
                        window.localStorage.setItem('index', index);
                        bus.$emit('nav-change', { id: currentData.id }, index);
                        await this.$store.dispatch('role/updateCurrentRole', { id });
                        this.updateRouter(index, type);
                    }
                }
            },

            async handleBackHome () {
                await this.$store.dispatch('role/updateCurrentRole', { id: 0 });
                await this.$store.dispatch('userInfo');
                this.$store.commit('updateIndex', 0);
                window.localStorage.setItem('index', 0);
                this.$router.push({ name: 'myPerm' });
            },

            setMagicBoxLocale (targetLocale) {
                const { lang, locale } = magicbox;
                const magicBoxLanguageMap = {
                    'zh-cn': lang.zhCN,
                    en: lang.enUS
                };
                locale.use(magicBoxLanguageMap[getCookie('blueking_language')]);
                window.CUR_LANGUAGE = getCookie('blueking_language');
                this.$i18n.locale = getCookie('blueking_language');
                window.location.reload();
            },
        
            handleChangeLocale (payload) {
                this.setCookie('blueking_language', payload);
                Cookie.set('blueking_language', payload, {
                    domain: window.location.hostname.split('.').slice(1).join('.')
                });
                this.setMagicBoxLocale(payload);
            },

            setCookie (name, value) {
                const date = new Date();
                date.setTime(date.getTime() - 10000);
                document.cookie = name + '=' + value + ';' + 'expire=' + date.toGMTString() + '; path=/';
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
                window.localStorage.removeItem('index');
                window.location = window.LOGIN_SERVICE_URL + '/?c_url=' + window.location.href;
            },

            handleManager () {
                const data = this.navData.find((e) => e.type !== 'staff');
                this.handleSelect(data, 1);
                this.$store.commit('updateSelectManager', true);
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
                window.localStorage.removeItem('index');
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
                    window.history.replaceState(
                        {},
                        '',
                        `?${buildURLParams(
                            Object.assign({}, this.$route.query, {
                                tab: tab
                            })
                        )}`
                    );
                }
            },

            // 根据角色设置
            setTabRoleData () {
                const superManager = this.curRoleList.find((e) => e.type === 'super_manager');
                const allManager = this.curRoleList.find((e) => e.type !== 'staff');
                this.navData.forEach((element, i) => {
                    element.active = i === this.index;
                    if (element.type === 'super_manager' && superManager) {
                        element.id = superManager.id;
                        element.show = true;
                    } else if (element.type === 'all_manager' && allManager) {
                        element.id = this.navCurRoleId || allManager.id;
                        // element.id = allManager.id;
                    }
                });
                this.$store.commit('updateNavData', this.navData);
            },

            setNavData () {
                this.$nextTick(() => {
                    for (let i = 0; i < this.navData.length; i++) {
                        if (this.navData[i].type === 'all_manager') {
                            this.navData[i].show = !!this.roleList.length;
                            break;
                        }
                    }
                });
            }
        }
    };
</script>

<style>
@import "./index";
</style>
