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
          @expand-change="handleExpandNode"
          @select-change="handleSelectNode"
        >
          <div slot-scope="{ node,data }">
            <!-- <div
              class="single-hide"
              :style="[
                { 'max-width': '220px' },
                { opacity: data.is_member ? '1' : '0.4' }
              ]"
              :title="data.name"> -->
            <div
              :class="[
                'single-hide',
                { 'iam-search-data': isSearch }
              ]"
              :style="[
                { 'max-width': '220px' }
              ]"
              :title="data.name">
              <Icon
                :type="data.level > 0 ? 'level-two-manage-space' : 'level-one-manage-space'"
                :style="{
                  color: formatColor(data)
                }"
              />
              <span>{{data.name}}</span>
            </div>
            <div
              v-if="node.level > 0 && subRoleList.length < subPagination.count"
              class="tree-load-more">
              <bk-button
                :text="true"
                size="small"
                @click="handleSubLoadMore">
                {{ $t(`m.common['查看更多']`) }}
              </bk-button>
            </div>
            <!-- <bk-star
                                v-if="(node.children && node.level > 0) || (node.children.length === 0 && node.level === 0)"
                                :rate="node.id === curRoleId" :max-stars="1" /> -->
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
    [['audit'], 'auditNav'],
    // 用户组设置
    [['userGroupSetting'], 'userGroupSettingNav']
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
        subRoleList: [],
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
        },
        subPagination: {
          current: 1,
          count: 0,
          limit: 100
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
          const { role } = this.user;
          const levelIcon = 'icon iam-icon';
          if (role && ['subset_manager'].includes(role.type)) {
            return `${levelIcon} iamcenter-level-two-manage-space`;
          } else {
            return `${levelIcon} iamcenter-level-one-manage-space`;
          }
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
            value.forEach((e) => {
              e.level = 0;
              // if (e.sub_roles && e.sub_roles.length) {
              //   e.sub_roles.forEach(sub => {
              //     sub.level = 1;
              //   });
              //   e.children = e.sub_roles;
              // }
              if (e.has_subset_manager) {
                this.$set(e, 'children', [{ name: '' }]);
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
        try {
          const { data } = await this.$store.dispatch(
            'spaceManage/getStaffSubManagerList',
            {
              limit: this.subPagination.limit,
              offset: (this.subPagination.current - 1) * this.subPagination.limit,
              id: row.id,
              with_super: true
            }
          );
          data && data.results.forEach(item => {
            item.level = 1;
            item.type = 'subset_manager';
          });
          this.subPagination.count = data.count || 0;
          row.children = [...row.children, ...data.results].filter(item => item.name);
          this.subRoleList = [...row.children];
        } catch (e) {
          console.error(e);
          row.children = [];
          this.subRoleList = [];
          this.messageAdvancedError(e);
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
          console.error(e);
          this.curRoleList = [];
          this.messageAdvancedError(e);
        }
      },

      async handleExpandNode (payload) {
        if (payload.state.expanded) {
          this.resetSubPagination();
          this.subRoleList = [];
          this.curRoleData = payload;
          payload.data = Object.assign(payload.data, { children: [] });
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
          this.resetSubPagination();
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

      async handleSubLoadMore () {
        if (this.subRoleList.length < this.subPagination.count) {
          const params = {
            current: ++this.subPagination.current,
            limit: this.subPagination.limit
          };
          this.subPagination = Object.assign(this.subPagination, params);
          this.fetchSubManagerList(this.curData);
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
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      // 刷新一、二级管理员列表和设置当前页捕获不到的数据
      async resetRoleList (payload) {
        const { role } = this.user;
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
          if (payload === 'handleClearSearch') {
            this[payload]();
          }
        }
      },
      
      // 监听当前已选中的角色是否有变更
      fetchRoleUpdate ({ role }) {
        const { id, type } = role;
        // console.log(role, '变更');
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
        // if (!node.data.is_member) return;
        this.handleToggle(false);
        this.$refs.select.close();
        // this.handleSwitchRole(node.id);
        this.handleSwitchRole(node.data);
      },

      async handleRemoteTree  (value) {
        this.keyWord = value;
        if (this.$refs.select) {
          this.$refs.select.searchValue = value;
        }
        this.curRoleList = [];
        this.resetPagination();
        this.resetSubPagination();
        if (value) {
          this.isSearch = true;
          await this.fetchSearchManageList(value);
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
          if (['createUserGroup', 'cloneUserGroup', 'userGroupDetail', 'addGroupPerm'].includes(curRouterName)) {
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

      resetSubPagination () {
        this.subPagination = Object.assign(
          {},
          {
            current: 1,
            count: 0,
            limit: 100
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
}
</style>
