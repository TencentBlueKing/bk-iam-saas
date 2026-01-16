<template>
  <!-- eslint-disable max-len -->
  <nav :class="['nav-layout', { sticked: navStick }]" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
    <div :class="['nav-wrapper', { unfold: unfold, flexible: !navStick }]">
      <bk-select
        ref="select"
        v-if="unfold && index === 1"
        :value="navCurRoleId || curRoleId"
        :clearable="false"
        :multiple="false"
        :allow-enter="false"
        :placeholder="$t(`m.common['选择管理空间']`)"
        :search-placeholder="$t(`m.common['搜索管理空间']`)"
        :searchable="true"
        :prefix-icon="formatRoleIcon"
        :remote-method="handleRemoteTree"
        :ext-popover-cls="selectCls"
        ext-cls="iam-nav-select-cls"
        @toggle="handleToggle"
      >
        <bk-big-tree
          ref="selectTree"
          size="small"
          :data="curRoleList"
          :selectable="true"
          :use-default-empty="true"
          :show-checkbox="false"
          :show-link-line="false"
          :default-is-expanded-nodes="[navCurRoleId || curRoleId]"
          :default-selected-node="navCurRoleId || curRoleId"
          :before-select="handleBeforeSelect"
          @expand-change="handleExpandNode"
          @select-change="handleSelectNode"
        >
          <div slot-scope="{ node, data }">
            <div
              :class="[
                'single-hide',
                { 'iam-search-data': isSearch }
              ]"
              :style="[
                { 'max-width': '220px' }
              ]"
              :title="data.name">
              <template v-if="!['loadMore'].includes(data.nodeType)">
                <Icon
                  :type="getRoleIcon(node)"
                  :style="{
                    color: formatColor(data)
                  }"
                />
                <span>{{data.name}}</span>
              </template>
              <div class="tree-load-more" v-else>
                <bk-button
                  size="small"
                  :text="true"
                  @click="handleSubLoadMore(data)"
                >
                  {{ data.name }}
                </bk-button>
              </div>
            </div>
          </div>
        </bk-big-tree>
        <div
          v-if="isSearch ? curRoleList.length < pagination.count : curRoleList.length < roleCount"
          class="tree-load-more">
          <bk-button
            :text="true"
            size="small"
            @click="handleLoadMore">
            {{ $t(`m.common['查看更多']`) }}
          </bk-button>
        </div>
        <div slot="extension" @click="handleToGradingAdmin" style="cursor: pointer">
          <i class="bk-icon icon-cog-shape mr10"></i>{{ $t(`m.common['我的管理空间']`) }}
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
  // import { getTreeNode } from '@/common/util';
  import { getRouterDiff } from '@/common/router-handle';
  import { NEED_CONFIRM_DIALOG_ROUTER, MANAGE_SPACE_REDIRECT_ROUTES, ALL_ROUTES_LIST } from '@/common/constants';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import { buildURLParams } from '@/common/url';
  import IamGuide from '@/components/iam-guide/index.vue';

  export default {
    inject: ['reload'],
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
        routerMap: Object.freeze(ALL_ROUTES_LIST),
        curRoleList: [],
        manageSpaceRoutes: Object.freeze(MANAGE_SPACE_REDIRECT_ROUTES),
        curRoleId: 0,
        hoverId: -1,
        selectValue: '',
        keyWord: '',
        isEmpty: false,
        isSearch: false,
        curRoleData: {},
        pagination: {
          current: 1,
          count: 1,
          limit: 20
        }
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
          'roleCount',
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
      },
      formatRoleIcon () {
        const levelIcon = 'icon iam-icon';
        const roleMap = {
          system_manager: () => {
            return `${levelIcon} iamcenter-guanlikongjian-3`;
          },
          subset_manager: () => {
            return `${levelIcon} iamcenter-level-two-manage-space`;
          },
          other_manager: () => {
            return `${levelIcon} iamcenter-level-one-manage-space`;
          }
        };
        return roleMap[this.user.role.type] ? roleMap[this.user.role.type]() : roleMap['other_manager']();
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
          // 如果不是搜索或者首次调用才获取公共接口数据
          if (value.length && this.pagination.current === 1 && !this.isSearch) {
            value.forEach((item) => {
              item.level = 0;
              if (item.has_subset_manager) {
                // 页面初始化二级管理员设置默认值
                this.$set(item, 'children', [{ name: '' }]);
                this.$set(item, 'pagination', {
                  current: 1,
                  limit: 20,
                  count: 0
                });
              }
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
      bus.$on('theme-change', (payload) => {
        this.curRole = payload;
      });

      bus.$on('nav-change', ({ id }, index) => {
        this.curRoleId = id;
        this.$store.commit('updateCurRoleId', this.curRoleId);
        this.$store.commit('updateNavId', this.curRoleId);
      });
    },
    methods: {
      async fetchDefaultInterface (payload) {
        this.handleSwitchPerm(payload);
        this.fetchSpaceUpdateGuide();
        this.fetchFirstRoleList();
      },
      async fetchFirstRoleList () {
        if (this.index === 1) {
          // 处理刷新后选中角色不在当前分页里，默认回显
          const { id, name, type } = this.user.role;
          const roleData = this.curRoleList.length ? this.curRoleList : await this.$store.dispatch('roleList');
          const hasRole = roleData.find(item => item.id === id);
          if (!hasRole || ['subset_manager'].includes(type)) {
            if (this.$refs.select) {
              this.isSearch = true;
              this.$refs.select.searchValue = name;
            }
            this.resetRoleList();
          }
        }
      },
      async fetchSubManagerList (row) {
        row.subManageLoading = true;
        try {
          const { current, limit } = row.pagination;
          const { data } = await this.$store.dispatch(
            'spaceManage/getStaffSubManagerList',
            {
              limit,
              offset: (current - 1) * limit,
              id: row.id,
              with_super: true
            }
          );
          const results = data.results || [];
          const count = data.count || 0;
          const curPageConfig = { ...row.pagination, ...{ count } };
          results.forEach(item => {
            item.level = 1;
            item.type = 'subset_manager';
          });
          const childNodes = [...row.children, ...results].filter(item => item.name !== '' && item.nodeType !== 'loadMore');
          const loadMore = {
            nodeType: 'loadMore',
            name: this.$t('查看更多'),
            parent: {
              ...row,
              ...{
                children: childNodes,
                pagination: curPageConfig
              }
            }
          };
          row = Object.assign(row, {
            children: childNodes.length >= count ? [...childNodes] : [...childNodes, ...[loadMore]],
            pagination: curPageConfig
          });
          const parenNodeIndex = this.curRoleList.findIndex(v => `${v.name}&${v.id}` === `${row.name}&${row.id}`);
          if (parenNodeIndex > -1) {
            this.$set(this.curRoleList[parenNodeIndex], 'children', row.children);
            this.$refs.selectTree && this.$refs.selectTree.setData(this.curRoleList);
          }
        } catch (e) {
          row = Object.assign(row, {
            children: [],
            pagination: { current: 1, limit: 20, count: 0 }
          });
          this.messageAdvancedError(e);
        } finally {
          row.subManageLoading = false;
        }
      },

      async fetchSearchManageList () {
        const { current, limit } = this.pagination;
        const params = {
          page_size: limit,
          page: current,
          name: this.keyWord,
          with_super: true
        };
        try {
          const { data } = await this.$store.dispatch('spaceManage/getSearchManagerList', params);
          const { count, results } = data;
          this.pagination.count = count || 0;
          this.$store.commit('updateRoleListTotal', count);
          results && results.forEach(item => {
            item.level = !['subset_manager'].includes(item.type) ? 0 : 1;
          });
          if (current === 1) {
            this.curRoleList = [];
          }
          this.curRoleList = [...this.curRoleList, ...results];
        } catch (e) {
          this.curRoleList = [];
          this.messageAdvancedError(e);
        }
      },

      async handleExpandNode (payload) {
        if (payload.state.expanded) {
          this.curRoleData = payload;
          payload.data = Object.assign(
            payload.data,
            {
              children: [],
              pagination: {
                current: 1,
                limit: 20,
                count: 0
              }
            }
          );
          await this.fetchSubManagerList(payload.data);
          if (this.$refs.selectTree) {
            this.$refs.selectTree.setData(this.curRoleList);
            this.$refs.selectTree.setExpanded(payload.id);
          }
        }
      },

      async handleToggle (value) {
        this.selectCls = 'hide-iam-nav-select-cls';
        if (value) {
          this.selectCls = 'iam-nav-select-dropdown-content';
          this.resetPagination();
          await this.resetRoleList('handleClearSearch');
        }
      },

      async handleLoadMore () {
        if (this.isSearch) {
          if (this.curRoleList.length < this.pagination.count) {
            this.pagination.current++;
            this.fetchSearchManageList();
          }
        } else {
          if (this.curRoleList.length < this.roleCount) {
            this.pagination.current++;
            const { current, limit } = this.pagination;
            const params = {
              limit,
              offset: (current - 1) * limit
            };
            const result = await this.$store.dispatch('roleList', params);
            result.forEach(item => {
              this.$set(item, 'level', 0);
              if (item.has_subset_manager) {
                this.$set(item, 'children', [{ name: '' }]);
                this.$set(item, 'pagination', { current: 1, limit: 20, count: 0 });
              }
            });
            this.curRoleList = [...this.curRoleList, ...result];
            this.$nextTick(() => {
              if (this.$refs.selectTree) {
                const { id } = this.user.role;
                const curNode = this.$refs.selectTree.getNodeById(id);
                if ((curNode && curNode.data && curNode.data.has_subset_manager)) {
                  this.handleExpandNode(curNode || this.curRoleData);
                }
              }
            });
          }
        }
      },

      async handleSubLoadMore (payload) {
        if (!payload.parent) {
          return;
        }
        const { children, pagination } = payload.parent;
        if (children.length < pagination.count) {
          const params = {
            current: ++pagination.current,
            limit: pagination.limit
          };
          payload.parent.pagination = Object.assign(payload.parent.pagination, params);
          await this.fetchSubManagerList(payload.parent);
        }
      },

      // 切换身份
      async handleSwitchRole ({ id, type, name }) {
        // const { type, name } = getTreeNode(id, this.curRoleList);
        [this.curRoleId, this.curRole] = [id, type];
        try {
          await this.$store.dispatch('role/updateCurrentRole', { id });
          this.$store.commit('updateCurRoleId', id);
          this.$store.commit('updateIdentity', { id, type, name });
          this.$store.commit('updateNavId', id);
          this.updateRouter(type);
          this.resetLocalStorage();
          if (id > 0) {
            const queryParams = Object.assign({}, {
              ...this.$route.query,
              role_name: name
            });
            window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      // 刷新一、二级管理员列表和设置当前页捕获不到的数据
      async resetRoleList (payload) {
        const { role } = this.user;
        if (payload === 'handleClearSearch') {
          this[payload]();
        }
        if (this.$refs.selectTree) {
          const curNode = this.$refs.selectTree.getNodeById(role.id);
          if (!curNode && this.$refs.select && this.isSearch) {
            this.$refs.select.searchValue = role.name;
            this.resetPagination();
            return;
          }
          if (!this.isSearch && this.$refs.select) {
            this.$refs.select.searchValue = '';
          }
          if (curNode && curNode.data && curNode.data.has_subset_manager) {
            await this.handleExpandNode(curNode || this.curRoleData);
          }
        }
      },
      
      // 监听当前已选中的角色是否有变更
      fetchRoleUpdate ({ role }) {
        const { id, type } = role;
        this.curRole = type;
        this.curRoleId = this.navCurRoleId || id;
        this.$store.commit('updateCurRoleId', this.curRoleId);
        if (this.index === 1) {
          if (this.$refs.selectTree) {
            this.$refs.selectTree.selected = this.curRoleId;
          }
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
        this.fetchDefaultInterface(params);
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
          const hasRole = this.curRoleList.find(item => item.id === Number(id));
          this.isSearch = !hasRole;
          this.resetRoleList();
          // this.handleRemoteTree(role.name);
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
        this.handleToggle(false);
        this.$refs.select.close();
        this.handleSwitchRole(node.data);
      },

      handleBeforeSelect (node) {
        return !['loadMore'].includes(node.data.nodeType);
      },

      async handleRemoteTree  (value) {
        this.keyWord = value.trim();
        if (this.$refs.select) {
          this.$refs.select.searchValue = this.keyWord;
        }
        this.curRoleList = [];
        this.resetPagination();
        if (value) {
          this.isSearch = true;
          await this.fetchSearchManageList(this.keyWord);
        } else {
          this.isSearch = false;
          if (this.$refs.select) {
            this.$refs.select.searchValue = '';
          }
          await this.$store.dispatch('roleList');
          await this.resetRoleList();
        }
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
            const url = `${window.BK_ITSM_APP_URL}/#/workbench/ticket/approval`;
            window.open(url);
            return;
          }
          if (item.path === this.$route.path) {
            // 因为vuex是同步操作，需要从缓存里获取最新的位置处理多个标签页之间不同权限页面之间的切换场景
            const storageNavIndex = window.localStorage.getItem('index');
            if (this.index !== Number(storageNavIndex)) {
              return;
            }
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
            if (['', 'staff'].includes(roleType)) {
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
          let resetRouteName = '';
          for (const [key, value] of this.manageSpaceRoutes.entries()) {
            if (key.includes(curRouterName)) {
              resetRouteName = value;
            }
          }
          if (resetRouteName) {
            this.$router.push({ name: resetRouteName });
            return;
          }
          this.$emit('reload-page', this.$route);
          return;
        }
        this.$emit('reload-page', this.$route);
      },

      getRoleIcon (node) {
        const { level, data } = node;
        const levelMap = {
          0: () => {
            if (['system_manager'].includes(data.type)) {
              return 'guanlikongjian-3';
            }
            return 'level-one-manage-space';
          },
          1: () => {
            return 'level-two-manage-space';
          }
        };
        return levelMap[level] ? levelMap[level]() : levelMap[0]();
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
        const managerMap = {
          system_manager: () => {
            return '#3A84FF';
          },
          subset_manager: () => {
            return '#9B80FE';
          }
        };
        return managerMap[node.type] ? managerMap[node.type]() : '#FF9C01';
      },

      resetPagination () {
        this.pagination = Object.assign(
          {},
          {
            current: 1,
            count: 0,
            limit: 20
          }
        );
      },

      handleClearSearch () {
        this.isSearch = false;
        this.$refs.select.searchValue = '';
        this.keyWord = '';
      }
    }
  };
</script>

<style lang="postcss">
@import './index.css';

  .iam-nav-select-dropdown-content .bk-big-tree {
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
        .iam-search-data {
          .iamcenter-level-two-manage-space {
            margin-left: 0;
          }
        }
    }
    &-empty {
        color: #fff !important;
        opacity: .6;
        font-size: 12px;
    }
  }

  .iam-nav-select-dropdown-content {
    .bk-loading {
      background-color: transparent !important;;
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

  .tree-load-more {
    text-align: center;
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

    .iamcenter-guanlikongjian-3 {
      color: #3A84FF;
    }
}
</style>
