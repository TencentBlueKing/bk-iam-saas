<template>
    <!-- eslint-disable max-len -->
    <nav :class="['nav-layout', { sticked: navStick }]" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
        <div :class="['nav-wrapper', { unfold: unfold, flexible: !navStick }]">
            <!-- <bk-select
                v-if="unfold && index === 1"
                :value="navCurRoleId || curRoleId"
                :clearable="false"
                placeholder="选择分级管理员"
                :search-placeholder="$t(`m.common['切换身份']`)"
                searchable
                ext-cls="iam-nav-select-cls"
                ext-popover-cls="iam-nav-select-dropdown-content"
                @change="handleSwitchRole"
            >
                <bk-option
                    v-for="item in curRoleList"
                    :key="item.id"
                    :id="item.id"
                    :name="item.name"
                >
                </bk-option>
                <div slot="extension" @click="handleToGradingAdmin" style="cursor: pointer;">
                    <i class="bk-icon icon-plus-circle mr10"></i>管理我的分级管理员
                </div>
            </bk-select> -->
            <bk-select
                ref="select"
                v-if="unfold && index === 1"
                :value="navCurRoleId || curRoleId"
                :clearable="false"
                :multiple="false"
                :placeholder="$t(`m.common['选择管理空间']`)"
                :search-placeholder="$t(`m.common['搜索管理空间']`)"
                :searchable="true"
                :allow-enter="false"
                :prefix-icon="user.role && ['subset_manager'].includes(user.role.type) ?
                    'icon iam-icon iamcenter-level-two-manage-space' : 'icon iam-icon iamcenter-level-one-manage-space'"
                :remote-method="handleRemoteTree"
                :ext-popover-cls="selectCls"
                ext-cls="iam-nav-select-cls"
                @toggle="handleToggle">
                <bk-big-tree
                    ref="selectTree"
                    size="small"
                    :data="curRoleList"
                    :selectable="true"
                    :use-default-empty="true"
                    :show-checkbox="false"
                    :show-link-line="false"
                    :default-expanded-nodes="[navCurRoleId || curRoleId]"
                    :default-selected-node="navCurRoleId || curRoleId"
                    @expand-on-click="handleExpandClick"
                    @select-change="handleSelectNode">
                    <div slot-scope="{ node,data }">
                        <div
                            class="single-hide"
                            :style="[
                                { 'max-width': '220px' },
                                { opacity: data.is_member ? '1' : '0.4' }
                            ]"
                            :title="data.name">
                            <Icon :type="node.level === 0 ? 'level-one-manage-space' : 'level-two-manage-space'" :style="{ color: formatColor(node) }" />
                            <span>{{data.name}}</span>
                        </div>
                        <!-- <bk-star
                                v-if="(node.children && node.level > 0) || (node.children.length === 0 && node.level === 0)"
                                :rate="node.id === curRoleId" :max-stars="1" /> -->
                    </div>
                </bk-big-tree>
                <div slot="extension" @click="handleToGradingAdmin" style="cursor: pointer">
                    <i class="bk-icon icon-cog-shape mr10"></i>{{ $t(`m.nav['我的管理空间']`) }}
                </div>
            </bk-select>
            <div class="nav-slider-list">
                <div class="iam-menu" v-for="item in [...currentNav]" :key="item.id">
                    <template v-if="item.children && item.children.length > 0">
                        <div class="iam-menu-parent-title" v-show="isShowRouterGroup(item)">
                            <template v-if="item.rkey === 'set'">
                                {{ item.name }}
                            </template>
                            <template v-else>
                                {{ curLanguageIsCn ? (isUnfold ? item.name : item.name.substr(0, 2)) : isUnfold ?
                                    item.name : `${item.name.substr(0, 2)}.` }}
                            </template>
                        </div>
                        <template>
                            <div v-for="child in item.children" v-show="!routerDiff.includes(child.rkey)"
                                :key="child.id" :class="['iam-menu-item', { active: openedItem === child.id }]"
                                @click.stop="handleSwitchNav(child.id, child)"
                                :data-test-id="`nav_menu_switchNav_${child.id}`">
                                <Icon :type="child.icon" class="iam-menu-icon" />
                                <span
                                    v-if="child.name === $t(`m.common['管理员']`) && curRole === 'system_manager'"
                                    class="iam-menu-text single-hide"
                                    :title="`${t(`m.common['系统']`)}${child.name}`"
                                >
                                    <span>{{$t(`m.common['系统']`)}}{{child.name}}</span>
                                </span>
                                <span v-else class="iam-menu-text single-hide" :title="child.name">{{ child.name }}</span>
                                <span v-if="['myManageSpace'].includes(child.rkey) && index === 0" @click.stop>
                                    <iam-guide
                                        ref="popconfirm"
                                        type="grade_manager_upgrade"
                                        placement="left-end"
                                        popover-type="component"
                                        trigger="click"
                                        ext-cls="space-popconfirm"
                                        cancel-text=""
                                        :confirm-text="$t(`m.info['知道了']`)"
                                    >
                                        <div slot="popconfirm-header">
                                            <div class="content-header">
                                                <span class="content-title">{{ $t(`m.info['功能升级!']`) }}</span>
                                                <img src="@/images/boot-page/Upgrade@2x.png" width="50px" alt="">
                                            </div>
                                        </div>
                                        <div slot="popconfirm-content">
                                            <div class="content-desc">
                                                <span>{{ $t(`m.info['原来的']`) }}</span>
                                                <strong>{{ $t(`m.info['分级管理员']`) }}</strong>
                                                <span>{{ $t(`m.info['升级为']`) }}</span>
                                                <strong>{{ $t(`m.info['管理空间']`) }},</strong>
                                            </div>
                                            <div class="content-desc">
                                                {{ $t(`m.info['支持一级、二级管理空间，更加精细化管理。']`) }}
                                            </div>
                                        </div>
                                        <div slot="popconfirm-show">
                                            <img src="@/images/boot-page/Upgrade@2x.png" width="50px" style="vertical-align: middle;" alt="">
                                        </div>
                                    </iam-guide>
                                </span>
                            </div>
                        </template>
                    </template>
                    <template v-else>
                        <div v-show="!routerDiff.includes(item.rkey)"
                            :class="['iam-menu-item', { active: openedItem === item.id }]"
                            @click.stop="handleSwitchNav(item.id, item)"
                            :data-test-id="`nav_menu_switchNav_${item.id}`">
                            <Icon :type="item.icon" class="iam-menu-icon" />
                            <span :title="item.name" class="iam-menu-text single-hide" v-if="item.name === $t(`m.grading['管理空间']`) && curRole === 'staff'">
                                {{item.name }}
                            </span>
                            <span :title="item.name" class="iam-menu-text single-hide" v-else>{{ item.name }}</span>
                        </div>
                    </template>
                </div>
            </div>
            <div :class="['nav-stick-wrapper']" :title="navStick ? $t(`m.nav['收起导航']`) : $t(`m.nav['固定导航']`)"
                @click="toggleNavStick">
                <Icon type="shrink-line" :class="['nav-stick', { sticked: navStick }]" />
            </div>
        </div>
    </nav>
</template>

<script>
    import { mapGetters } from 'vuex';
    import { bus } from '@/common/bus';
    import { getTreeNode } from '@/common/util';
    import { getRouterDiff } from '@/common/router-handle';
    import { NEED_CONFIRM_DIALOG_ROUTER } from '@/common/constants';
    import { leavePageConfirm } from '@/common/leave-page-confirm';
    import IamGuide from '@/components/iam-guide/index.vue';

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
            ['userGroup', 'userGroupDetail', 'createUserGroup', 'cloneUserGroup', 'userGroupPermDetail', 'groupPermRenewal', 'addGroupPerm'],
            'userGroupNav'
        ],
        // 系统接入
        [
            [
                'systemAccess',
                'systemAccessCreate',
                'systemAccessAccess',
                'systemAccessRegistry',
                'systemAccessOptimize',
                'systemAccessComplete'
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
                'myPerm',
                'templatePermDetail',
                'groupPermDetail',
                'permRenewal',
                'groupPermRenewal',
                'permTransfer',
                'permTransferHistory',
                'applyPerm'
            ],
            'myPermNav'
        ],
        // 我的管理空间
        [['myManageSpace', 'myManageSpaceCreate', 'gradingAdminDetail', 'gradingAdminEdit', 'gradingAdminCreate', 'myManageSpaceSubDetail', 'secondaryManageSpaceEdit'], 'myManageSpaceNav'],
        // 分级管理员
        [['ratingManager', 'gradingAdminDetail', 'gradingAdminCreate', 'gradingAdminEdit'], 'gradingAdminNav'],
        // 管理空间
        [['firstManageSpace', 'firstManageSpaceCreate'], 'firstManageSpaceNav'],
        // 二级管理空间
        [['secondaryManageSpace', 'secondaryManageSpaceCreate', 'secondaryManageSpaceDetail'], 'secondaryManageSpaceNav'],
        // 授权边界
        [['authorBoundary', 'authorBoundaryEditFirstLevel', 'authorBoundaryEditSecondLevel'], 'authorBoundaryNav'],
        // 最大可授权人员边界
        [['addMemberBoundary'], 'addMemberBoundaryNav'],
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
        components: {
            IamGuide
        },
        data () {
            return {
                selectCls: 'iam-nav-select-dropdown-content',
                openedItem: '',
                timer: null,
                curRole: 'staff',
                isUnfold: true,
                routerMap: routerMap,
                curRoleList: [],
                curRoleId: 0,
                hoverId: -1,
                selectValue: '',
                isEmpty: false
            };
        },
        computed: {
            ...mapGetters([
                'user',
                'navStick',
                'navFold',
                'currentNav',
                'routerDiff',
                'roleList',
                'navData',
                'index',
                'navCurRoleId'
            ]),
            unfold () {
                return this.navStick || !this.navFold;
            },
            isShowRouterGroup () {
                return (payload) => {
                    const allRouter = getRouterDiff('all');
                    const curRouter = allRouter.filter((item) => !this.routerDiff.includes(item));
                    return curRouter.filter((item) => payload.children.map((_) => _.rkey).includes(item)).length > 0;
                };
            }
        },
        watch: {
            $route: {
                handler: 'routeChangeHandler',
                immediate: true
            },
            user: {
                handler (newValue, oldValue) {
                    this.curRole = newValue.role.type || 'staff';
                    if (newValue.role.id !== oldValue.role.id) {
                        this.reload();
                        this.curRoleId = newValue.role.id;
                    }
                },
                deep: true
            },
            roleList: {
                handler (value) {
                    if (value.length) {
                        value = value.map((e) => {
                            e.level = 0;
                            if (e.sub_roles.length) {
                                e.sub_roles.forEach(sub => {
                                    sub.level = 1;
                                });
                                e.children = e.sub_roles;
                            }
                            return e;
                        });
                        this.curRoleList.splice(0, this.curRoleList.length, ...value);
                    }
                },
                immediate: true
            },
            curRole: {
                handler () {
                    this.fetchSpaceUpdateGuide();
                },
                immediate: true
            }
        },
        created () {
            this.fetchRoleUpdate(this.user);
            this.isUnfold = this.navStick || !this.navFold;
            this.$once('hook:beforeDestroy', () => {
                bus.$off('theme-change');
                bus.$off('nav-change');
            });
        },
        mounted () {
            this.index = this.index || Number(window.localStorage.getItem('index') || 0);
            bus.$on('theme-change', (payload) => {
                this.curRole = payload;
            });

            bus.$on('nav-change', ({ id }, index) => {
                this.curRoleId = id;
                this.$store.commit('updateCurRoleId', this.curRoleId);
            });
        },
        methods: {
            // 监听当前已选中的角色是否有变更
            fetchRoleUpdate ({ role }) {
                const { id, type } = role;
                // console.log(role, '变更');
                this.curRole = type;
                this.curRoleId = this.navCurRoleId || id;
                this.$store.commit('updateCurRoleId', this.curRoleId);
                if (this.index === 1 && this.$refs.selectTree) {
                    this.$refs.selectTree.selected = this.curRoleId;
                }
            },
            fetchSpaceUpdateGuide () {
                if (['staff'].includes(this.curRole) && this.index === 0) {
                    this.$nextTick(() => {
                        this.$refs.popconfirm && this.$refs.popconfirm.length
                            && this.$refs.popconfirm[0].$refs.popconfirmCom
                            && this.$refs.popconfirm[0].$refs.popconfirmCom.$refs.popover.showHandler();
                    });
                }
            },
            initTree (parentId, list) {
                if (!parentId) {
                    return list.filter(item => !item.parentId).map(item => {
                        item.children = this.initTree(item.id, list);
                        return item;
                    });
                } else {
                    return list.filter(item => item.parentId === parentId).map(item => {
                        item.children = this.initTree(item.id, list);
                        return item;
                    });
                }
            },

            /**
             * route change 回调
             * 此方法在 created 之前执行
             *
             * @param {Object} to to route
             * @param {Object} from from route
             */
            routeChangeHandler (to, from) {
                const { params, name } = to;
                const pathName = name;
                this.handleSwitchPerm(params);
                this.fetchSpaceUpdateGuide();
                for (const [key, value] of this.routerMap.entries()) {
                    if (key.includes(pathName)) {
                        this.openedItem = value;
                        // if (this.openedItem === 'myManageSpaceNav' && this.curRole === 'super_manager') {
                        //     this.openedItem = 'gradingAdminNav';
                        // }
                        // 如果是从我的管理空间页面过来的，激活menu选中状态
                        if (this.openedItem === 'myManageSpaceNav') {
                            const menuActive = {
                                rating_manager: () => {
                                    this.openedItem = 'gradingAdminNav';
                                },
                                subset_manager: () => {
                                    this.openedItem = 'secondaryManageSpaceNav';
                                },
                                super_manager: () => {
                                    this.openedItem = 'gradingAdminNav';
                                }
                            };
                            return menuActive[this.curRole]
                                ? menuActive[this.curRole]()
                                : 'myManageSpaceNav';
                        }
                        break;
                    }
                }
            },

            // 从其他菜单进入管理空间选择角色
            handleSwitchPerm ({ id, entry }) {
                if (entry && this.$refs.selectTree) {
                    this.$refs.selectTree.selected = Number(id);
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

            handleSelectNode (node) {
                if (!node.data.is_member) return;
                this.$refs.select.close();
                this.handleToggle(false);
                this.handleSwitchRole(node.id);
            },

            handleRemoteTree  (value) {
                this.$refs.selectTree && this.$refs.selectTree.filter(value);
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
                if (window.changeDialog && NEED_CONFIRM_DIALOG_ROUTER.includes(this.$route.name)) {
                    const cancelHandler = leavePageConfirm();
                    cancelHandler.then(
                        () => {
                            this.handleNavMenu(item);
                        },
                        (_) => _
                    );
                } else {
                    this.handleNavMenu(item);
                }
            },

            // 校验切换侧边栏其他菜单
            handleNavMenu (item) {
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
                        this.$store.commit('setNavStatus', {
                            stick: !!this.unfold
                        });
                        this.$router.push(item.path);
                    }
                    this.openedItem = item.id === this.openedItem ? '' : item.id;
                });
            },

            handleToggle (value) {
                this.selectCls = value ? 'iam-nav-select-dropdown-content' : 'hide-iam-nav-select-cls';
            },

            // 切换身份
            async handleSwitchRole (id) {
                const { type, name } = getTreeNode(id, this.curRoleList);
                [this.curRoleId, this.curRole] = [id, type];
                try {
                    await this.$store.dispatch('role/updateCurrentRole', { id });
                    this.$store.commit('updateCurRoleId', id);
                    this.$store.commit('updateIdentity', { id, type, name });
                    this.$store.commit('updateNavId', id);
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

                    const permTemplateRoutes = ['permTemplateCreate', 'permTemplateDetail', 'permTemplateEdit', 'permTemplateDiff'];
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
            },

            formatColor (node) {
                // if (node.id === this.curRoleId) {
                switch (node.level) {
                    case 0: {
                        return '#FF9C01';
                    }
                    case 1: {
                        return '#9B80FE';
                    }
                }
                // }
            }
        }
    };
</script>

<style lang="postcss">
@import './index.css';

.iam-select-collection {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.iam-nav-select-dropdown-content
 .bk-big-tree {
    &-node {
        padding: 0 16px;
        .node-options {
            .node-folder-icon {
                font-size: 14px;
                margin: 0 0 0 -20px;
            }
        }
        .iamcenter-level-two-manage-space {
            margin-left: 15px;
        }
    }
    &-empty {
        color: #fff !important;
        opacity: .6;
    }
}

.space-popconfirm {
    .content-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        .content-title {
            font-size: 15px;
            margin-right: 5px;
        }
    }
    .content-desc {
        margin-bottom: 10px;
        word-break: break-all;
    }
    .tippy-tooltip.light-border-theme {
        box-shadow: 0 0 2px 0 #dcdee5;
    }
    /* .tippy-arrow {
        top: 120px !important;
    } */
 }
</style>

<style lang="postcss" scoped>
/deep/ .iam-nav-select-cls {
    .iamcenter-level-one-manage-space {
        color: #FF9C01;
    }

    .iamcenter-level-two-manage-space {
        color: #9B80FE;
    }
}
</style>
