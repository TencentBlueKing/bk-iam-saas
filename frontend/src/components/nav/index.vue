<template>
    <!-- eslint-disable max-len -->
    <nav :class="['nav-layout', { 'sticked': navStick }]"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave">
        <div :class="['nav-wrapper', { unfold: unfold, flexible: !navStick, 'dark-theme': isDarklyTheme }]">
            <div :class="['logo', { 'dark-theme': isDarklyTheme }]">
                <iam-svg name="logo" :alt="$t(`m.nav['蓝鲸权限中心']`)" v-if="curRole === '' || curRole === 'staff'" />
                <iam-svg name="logo-primary" :alt="$t(`m.nav['蓝鲸权限中心']`)" v-else />
                <span class="text">{{ $t('m.nav["蓝鲸权限中心"]') }}</span>
            </div>
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
                                :class="['iam-menu-item', { active: openedItem === child.id }, { 'has-darkly-theme': isDarklyTheme }]"
                                @click.stop="handleSwitchNav(child.id, child)">
                                <Icon :type="child.icon" class="iam-menu-icon" />
                                <span class="iam-menu-text">{{ child.name }}</span>
                            </div>
                        </template>
                    </template>
                    <template v-else>
                        <div
                            v-show="!routerDiff.includes(item.rkey)"
                            :class="['iam-menu-item', { active: openedItem === item.id }, { 'has-darkly-theme': isDarklyTheme }]"
                            @click.stop="handleSwitchNav(item.id, item)">
                            <Icon :type="item.icon" class="iam-menu-icon" />
                            <span class="iam-menu-text" v-if="item.name === '分级管理员' && curRole === 'staff'">我的{{ item.name }}</span>
                            <span class="iam-menu-text" v-else>{{ item.name }}</span>
                        </div>
                    </template>
                </div>
            </div>
            <div
                :class="['nav-stick-wrapper', { 'dark-theme': isDarklyTheme }]"
                :title="navStick ? $t(`m.nav['收起导航']`) : $t(`m.nav['固定导航']`)"
                @click="toggleNavStick">
                <Icon type="shrink-line" :class="['nav-stick', { 'sticked': navStick }, { 'primary': curRole !== 'staff' }]" />
            </div>
        </div>
    </nav>
</template>

<script>
    import { mapGetters } from 'vuex'
    import { bus } from '@/common/bus'
    import { getRouterDiff } from '@/common/router-handle'

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
    ])

    export default {
        inject: ['reload'],
        name: '',
        data () {
            return {
                openedItem: '',
                timer: null,
                curRole: 'staff',
                isUnfold: true,
                routerMap: routerMap
            }
        },
        computed: {
            ...mapGetters(['user', 'navStick', 'navFold', 'currentNav', 'routerDiff']),
            unfold () {
                return this.navStick || !this.navFold
            },
            isDarklyTheme () {
                return ['super_manager', 'system_manager', 'rating_manager'].includes(this.curRole)
            },
            isShowRouterGroup () {
                return payload => {
                    const allRouter = getRouterDiff('all')
                    const curRouter = allRouter.filter(item => !this.routerDiff.includes(item))
                    return curRouter.filter(item => payload.children.map(_ => _.rkey).includes(item)).length > 0
                }
            }
        },
        watch: {
            '$route': {
                handler: 'routeChangeHandler',
                immediate: true
            },
            user: {
                handler (newValue, oldValue) {
                    this.curRole = newValue.role.type || 'staff'
                    if (newValue.role.id !== oldValue.role.id) {
                        this.reload()
                    }
                },
                deep: true
            }
        },
        created () {
            this.curRole = this.user.role.type
            this.isUnfold = this.navStick || !this.navFold
            this.$once('hook:beforeDestroy', () => {
                bus.$off('theme-change')
            })
        },
        mounted () {
            bus.$on('theme-change', payload => {
                this.curRole = payload
            })
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
                const pathName = to.name
                for (const [key, value] of this.routerMap.entries()) {
                    if (key.includes(pathName)) {
                        this.openedItem = value
                        break
                    }
                }
            },

            handleMouseEnter () {
                if (this.timer) {
                    clearTimeout(this.timer)
                }
                this.$store.commit('setNavStatus', { fold: false })
                if (!this.navStick) {
                    this.isUnfold = true
                }
            },

            handleMouseLeave () {
                this.timer = setTimeout(() => {
                    this.$store.commit('setNavStatus', { fold: true })
                }, 300)
                if (!this.navStick) {
                    this.isUnfold = false
                }
            },

            // 切换导航展开固定
            toggleNavStick () {
                bus.$emit('nav-resize', !this.navStick)
                this.$store.commit('setNavStatus', {
                    fold: !this.navFold,
                    stick: !this.navStick
                })
                this.isUnfold = this.navStick
            },

            handleSwitchNav (id, item) {
                this.$nextTick(() => {
                    if (item.rkey === 'approval') {
                        const url = `${window.BK_ITSM_APP_URL}/#/ticket/my/approval`
                        window.open(url)
                        return
                    }
                    if (item.path === this.$route.path) {
                        bus.$emit('reload-page', item)
                        this.$emit('reload-page', this.$route)
                        return
                    }
                    if (item.hasOwnProperty('path')) {
                        this.$router.push(item.path)
                    }
                    this.openedItem = item.id === this.openedItem ? '' : item.id
                })
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
