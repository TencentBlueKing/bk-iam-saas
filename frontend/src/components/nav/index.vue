<template>
    <!-- eslint-disable max-len -->
    <nav :class="['nav-layout', { 'sticked': navStick }]"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave">
        <div :class="['nav-wrapper', { unfold: unfold, flexible: !navStick }]">
            <bk-select
                v-if="unfold && index === 1"
                :value="curRoleId"
                :clearable="false"
                placeholder="选择分级管理员"
                :search-placeholder="$t(`m.common['切换身份']`)"
                searchable
                ext-cls="iam-nav-select-cls"
                ext-popover-cls="iam-nav-select-dropdown-content"
                @change="handleSwitchRole">
                <bk-option
                    v-for="item in curRoleList"
                    :key="item.id"
                    :id="item.id"
                    :name="item.name">
                </bk-option>
                <div slot="extension" @click="handleToGradingAdmin" style="cursor: pointer;">
                    <i class="bk-icon icon-plus-circle"></i>管理我的分级管理员
                </div>
            </bk-select>
            <div class="nav-slider-list">
                <div class="iam-menu"
                    v-for="item in [...currentNav]"
                    :key="item.id">
                    <template v-if="item.children && item.children.length > 0">
                        <div class="iam-menu-parent-title" v-show="isShowRouterGroup(item)">
                            <template v-if="item.rkey === 'set'">
                                {{ item.name }}
                            </template>
                            <template v-else>
                                {{ curLanguageIsCn ? isUnfold ? item.name : item.name.substr(0, 2) : isUnfold ? item.name : 'MP' }}
                            </template>
                        </div>
                        <template>
                            <div v-for="child in item.children"
                                v-show="!routerDiff.includes(child.rkey)"
                                :key="child.id"
                                :class="['iam-menu-item', { active: openedItem === child.id }]"
                                @click.stop="handleSwitchNav(child.id, child)" :data-test-id="`nav_menu_switchNav_${child.id}`">
                                <Icon :type="child.icon" class="iam-menu-icon" />
                                <span class="iam-menu-text">{{ child.name }}</span>
                            </div>
                        </template>
                    </template>
                    <template v-else>
                        <div
                            v-show="!routerDiff.includes(item.rkey)"
                            :class="['iam-menu-item', { active: openedItem === item.id }]"
                            @click.stop="handleSwitchNav(item.id, item)" :data-test-id="`nav_menu_switchNav_${item.id}`">
                            <Icon :type="item.icon" class="iam-menu-icon" />
                            <span class="iam-menu-text" v-if="item.name === '分级管理员' && curRole === 'staff'">我的{{ item.name }}</span>
                            <span class="iam-menu-text" v-else>{{ item.name }}</span>
                        </div>
                    </template>
                </div>
            </div>
            <div
                :class="['nav-stick-wrapper']"
                :title="navStick ? $t(`m.nav['收起导航']`) : $t(`m.nav['固定导航']`)"
                @click="toggleNavStick">
                <Icon type="shrink-line" :class="['nav-stick', { 'sticked': navStick }]" />
            </div>
        </div>
    </nav>
</template>

<script>
    import { mapGetters } from 'vuex';
    import { bus } from '@/common/bus';
    import { getRouterDiff } from '@/common/router-handle';

    const routerMap = new Map([
        // 权限模板
        [
            ['permTemplate', 'permTemplateDetail', 'permTemplateCreate', 'permTemplateEdit', 'permTemplateDiff'],
            'permTemplateNav'
        ],
        // 首页
        [['', 'index'], 'indexNav'],
        // 用户组
        [
            [
                'userGroup', 'userGroupDetail', 'createUserGroup', 'userGroupPermDetail',
                'groupPermRenewal', 'addGroupPerm'
            ],
            'userGroupNav'
        ],
        // 系统接入
        [
            [
                'systemAccess', 'systemAccessCreate', 'systemAccessAccess',
                'systemAccessRegistry', 'systemAccessOptimize', 'systemAccessComplete'
            ],
            'systemAccessNav'
        ],
        // 我的申请
        [['apply'], 'applyNav'],
        // 权限申请 'permApply'
        [['applyCustomPerm', 'applyJoinUserGroup'], 'permApplyNav'],
        // 临时权限申请 'provisionPermApply'
        [['applyProvisionPerm'], 'provisionPermApplyNav'],
        // 我的权限
        [
            [
                'myPerm', 'templatePermDetail', 'groupPermDetail', 'permRenewal',
                'groupPermRenewal', 'permTransfer', 'permTransferHistory'
            ],
            'myPermNav'
        ],
        // 分级管理员
        [['ratingManager', 'gradingAdminDetail', 'gradingAdminCreate', 'gradingAdminEdit'], 'gradingAdminNav'],
        // 资源权限
        [['resourcePermiss'], 'resourcePermissNav'],
        // 管理员
        [['administrator'], 'settingNav'],
        // 审批流程
        [['approvalProcess'], 'approvalProcessNav'],
        // 用户
        [['user'], 'userNav'],
        // 审计
        [['audit'], 'auditNav']
    ]);

    export default {
        inject: ['reload'],
        name: '',
        data () {
            return {
                openedItem: '',
                timer: null,
                curRole: 'staff',
                isUnfold: true,
                routerMap: routerMap,
                curRoleList: [],
                curRoleId: 0
            };
        },
        computed: {
            ...mapGetters(['user', 'navStick', 'navFold', 'currentNav', 'routerDiff', 'roleList', 'navData', 'index']),
            unfold () {
                return this.navStick || !this.navFold;
            },
            isShowRouterGroup () {
                return payload => {
                    const allRouter = getRouterDiff('all');
                    const curRouter = allRouter.filter(item => !this.routerDiff.includes(item));
                    return curRouter.filter(item => payload.children.map(_ => _.rkey).includes(item)).length > 0;
                };
            }
        },
        watch: {
            '$route': {
                handler: 'routeChangeHandler',
                immediate: true
            },
            user: {
                handler (newValue, oldValue) {
                    this.curRole = newValue.role.type || 'staff';
                    if (newValue.role.id !== oldValue.role.id) {
                        this.reload();
                    }
                },
                deep: true
            },
            roleList: {
                handler (newValue, oldValue) {
                    this.curRoleList.splice(0, this.curRoleList.length, ...newValue);
                },
                immediate: true
            }
        },
        created () {
            this.curRole = this.user.role.type;
            this.curRoleId = this.user.role.id;
            this.isUnfold = this.navStick || !this.navFold;
            this.$once('hook:beforeDestroy', () => {
                bus.$off('theme-change');
                bus.$off('nav-change');
            });
        },
        mounted () {
            this.index = this.index || Number(window.localStorage.getItem('index') || 0);
            bus.$on('theme-change', payload => {
                this.curRole = payload;
            });

            bus.$on('nav-change', ({ id }, index) => {
                this.curRoleId = id;
            });
        },
        methods: {
            /**
             * route change 回调
             * 此方法在 created 之前执行
             *
             * @param {Object} to to route
             * @param {Object} from from route
             */
            routeChangeHandler (to, from) {
                const pathName = to.name;
                for (const [key, value] of this.routerMap.entries()) {
                    if (key.includes(pathName)) {
                        this.openedItem = value;
                        break;
                    }
                }
            },

            handleMouseEnter () {
                if (this.timer) {
                    clearTimeout(this.timer);
                }
                this.$store.commit('setNavStatus', { fold: false });
                if (!this.navStick) {
                    this.isUnfold = true;
                }
            },

            handleMouseLeave () {
                this.timer = setTimeout(() => {
                    this.$store.commit('setNavStatus', { fold: true });
                }, 300);
                if (!this.navStick) {
                    this.isUnfold = false;
                }
            },

            // 切换导航展开固定
            toggleNavStick () {
                bus.$emit('nav-resize', !this.navStick);
                this.$store.commit('setNavStatus', {
                    fold: !this.navFold,
                    stick: !this.navStick
                });
                this.isUnfold = this.navStick;
            },

            handleSwitchNav (id, item) {
                this.$nextTick(() => {
                    if (item.rkey === 'approval') {
                        const url = `${window.BK_ITSM_APP_URL}/#/ticket/my/approval`;
                        window.open(url);
                        return;
                    }
                    if (item.path === this.$route.path) {
                        bus.$emit('reload-page', item);
                        this.$emit('reload-page', this.$route);
                        return;
                    }
                    if (item.hasOwnProperty('path')) {
                        this.$router.push(item.path);
                    }
                    this.openedItem = item.id === this.openedItem ? '' : item.id;
                });
            },

            // 切换身份
            async handleSwitchRole (id) {
                const { type, name } = this.curRoleList.find(e => e.id === id);
                try {
                    await this.$store.dispatch('role/updateCurrentRole', { id });
                    this.curRoleId = id;
                    this.curRole = type;
                    this.$store.commit('updateIdentity', { id, type, name });
                    this.updateRouter(type);
                    this.resetLocalStorage();
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

            // 更新路由
            updateRouter (roleType) {
                console.log(111, roleType);
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

            // 清除页面localstorage
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

            handleToGradingAdmin () {
                bus.$emit('rating-admin-change');
            }
        }
    };
</script>

<style>
    @import './index.css';
</style>
