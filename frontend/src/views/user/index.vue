<template>
  <div class="iam-user-wrapper"
    :style="{ minHeight: contentHeight + 'px' }">
    <div class="left-wrapper" :draggable="false" :style="leftStyle">
      <div class="header-wrapper">
        <span class="text">{{ $t(`m.common['组织架构']`) }}</span>
        <div class="icon-content">
          <iam-popover-confirm
            :title="$t(`m.common['确定同步']`)"
            :confirm-handler="() => handleSyncDepartment(row, $index)">
            <div :class="['action-wrapper', { 'is-disabled': isSync }]"
              :title="isSync ? $t(`m.user['正在同步中']`) : $t(`m.user['同步组织']`)"
            >
              <Icon type="refresh" />
            </div>
          </iam-popover-confirm>
          <div class="action-wrapper"
            @click.stop="handleSyncRecordList">
            <Icon type="time-circle-fill" />
          </div>
        </div>
      </div>
      <div :class="['search-wrapper', { 'active': isSerachFocus }]">
        <bk-dropdown-menu
          align="left"
          ref="dropdown"
          trigger="click">
          <template slot="dropdown-trigger">
            <Icon class="search-icon"
              :type="searchConditionValue === 'fuzzy' ? 'fuzzy-search-allow' : 'exact-search-allow'" />
          </template>
          <ul class="bk-dropdown-list" slot="dropdown-content">
            <li
              v-for="item in searchConditionList"
              :key="item.id"
              @click.stop="handleConditionSelcted(item)">
              <a href="javascript:;" :class="{ 'active': item.id === searchConditionValue }">
                <Icon
                  class="search-config-icon"
                  :type="item.id === 'fuzzy' ? 'fuzzy-search-allow' : 'exact-search-allow'"
                  style="font-size: 16px;" />
                {{ item.name }}
              </a>
            </li>
          </ul>
        </bk-dropdown-menu>
        <bk-input
          :placeholder="$t(`m.common['搜索提示1']`)"
          maxlength="64"
          v-model="searchKeyWord"
          clearable
          ext-cls="iam-user-member-search-input-cls"
          @focus="handleSearchInput"
          @blur="handleSearchBlur"
          @keyup.enter.native="handleSearch">
        </bk-input>
      </div>
      <div class="sync-wrapper" v-if="isSync">
        <img src="@/images/circle.png" class="sync-icon" alt="sync">
        {{ $t(`m.user['同步中']`) }}<span class="sync-dot"></span>
      </div>
      <div
        :class="['tree-wrapper', { 'reset-height': isSync }, { 'set-margin-top': !isSync }]"
        v-bkloading="{ isLoading: treeLoading, opacity: 1, color: '#f5f6fa' }">
        <template v-if="!isShowSearchResult">
          <infinite-tree
            ref="infiniteTree"
            :all-data="treeList"
            :style="contentStyle"
            :is-sync="isSync"
            :empty-data="emptyData"
            :has-selected-departments="hasSelectedDeparts"
            location="page"
            @async-load-nodes="handleRemoteLoadNode"
            @expand-node="handleExpanded"
            @on-select="handleOnSelected"
            @on-click="handleOnClick"
            @on-refresh="handleEmptyRefresh"
          />
        </template>
        <template v-else>
          <div class="search-content-wrapper"
            :style="searchStyle">
            <template v-if="searchedResult.length && !treeLoading">
              <dialog-infinite-list
                :all-data="searchedResult"
                :style="contentStyle"
                :has-selected-departments="hasSelectedDeparts"
                @on-checked="handleSearchSelected"
                @on-click="handleSearchClick">
              </dialog-infinite-list>
            </template>
            <template v-if="isSeachResultTooMuch">
              <div class="too-much-wrapper">
                <Icon type="warning" class="much-tips-icon" />
                <p class="text">{{ $t(`m.info['搜索结果']`) }}</p>
              </div>
            </template>
            <template v-if="isSeachResultEmpty">
              <div class="search-empty-wrapper">
                <!-- <iam-svg />
                                <p class="empty-tips">{{ $t(`m.common['搜索无结果']`) }}</p> -->
                <ExceptionEmpty
                  :type="emptyData.type"
                  :empty-text="emptyData.text"
                  :tip-text="emptyData.tip"
                  :tip-type="emptyData.tipType"
                  @on-clear="handleEmptyClear"
                  @on-refresh="handleEmptyRefresh"
                />
              </div>
            </template>
          </div>
        </template>
      </div>
      <div class="has-selected-department-wrapper" v-bk-clickoutside="handleAuthHandleClickOutSide"
        v-if="isShowAuthWrapper">
        <div class="header">
          <div class="has-selected">
            {{ $t(`m.common['已选择']`) }}
            <template v-if="hasSelectedDeparts.length">
              <span class="organization-count">{{ hasSelectedDeparts.length }}</span>
              {{ $t(`m.common['个']`) }}
              {{ $t(`m.common['组织']`) }}
            </template>
            <template v-else><span class="organization-count">0</span></template>
          </div>
          <div class="clear-buttom">
            <bk-button theme="primary" text :disabled="isAuthDisabled" @click="handleClear(true)">
              {{ $t(`m.common['清空']`) }}
            </bk-button>
          </div>
        </div>
        <div class="content">
          <div class="organization-content">
            <div class="organization-item" v-for="item in hasSelectedDeparts" :key="item.id">
              <Icon bk type="folder-open-shape" class="folder-icon" />
              <span class="organization-name" :title="item.department_name">
                {{ item.department_name }}
              </span>
              <span class="user-count" v-if="item.showCount">{{'(' + item.count + ')'}}</span>
              <Icon bk type="close-circle-shape" class="delete-organization"
                :title="$t(`m.common['删除']`)" @click="handleDelete(item)" />
            </div>
          </div>
        </div>
        <div class="operate-button">
          <bk-button theme="primary" :disabled="isAuthDisabled" @click="handleAuth">
            {{ $t(`m.common['授权']`) }}
          </bk-button>
          <bk-button theme="default" @click="handleAuthCancel">{{ $t(`m.common['取消']`) }}</bk-button>
        </div>
      </div>
    </div>
    <div class="drag-dotted-line" v-if="isDrag" :style="dottedLineStyle"></div>
    <div class="drag-line"
      :style="dragStyle">
      <img
        class="drag-bar"
        src="@/images/drag-icon.svg"
        alt=""
        :draggable="false"
        @mousedown="handleDragMouseenter($event)"
        @mouseout="handleDragMouseleave($event)">
    </div>
    <div class="right-wrapper" :draggable="false" :style="rightStyle"
      v-bkloading="{ isLoading: rightLoading, opacity: 1, color: '#f5f6fa' }">
      <template v-if="isDepart">
        <render-depart
          :params="curSelectedData"
          @on-init="handleInitDepartContent" />
      </template>
      <template v-else-if="isRecord">
        <record-list
          :params="curSelectedData"
          @on-init="handleInitRecordContent"
          @handleBack="handleBack" />
      </template>
      <template v-else>
        <render-user
          :params="curSelectedData"
          @on-init="handleInitUserContent" />
      </template>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { formatCodeData, guid } from '@/common/util';
  import { bus } from '@/common/bus';
  import InfiniteTree from '@/components/infinite-tree';
  import dialogInfiniteList from '@/components/dialog-infinite-list';
  import RenderDepart from './components/render-depart';
  import RenderUser from './components/render-user';
  import RecordList from './components/record-list';
  import IamPopoverConfirm from '@/components/iam-popover-confirm';
  export default {
    name: '',
    components: {
      InfiniteTree,
      dialogInfiniteList,
      RenderDepart,
      RenderUser,
      RecordList,
      IamPopoverConfirm
    },
    data () {
      return {
        contentHeight: window.innerHeight - 61,
        searchKeyWord: '',
        isShowAuthWrapper: false,
        hasSelectedDeparts: [],
        treeLoading: false,
        isShowSearchResult: false,
        treeList: [],
        // tree组件节点点击事件 $emit 事件 类型
        // all: 既触发click 也触发 radio 事件
        // only-click: 只触发click 不触发 radio 事件
        // only-radio: 不触发click 只触发 radio 事件
        clickTriggerType: 'only-click',
        curSelectedData: {},
        searchedResult: [],
        searchedDepartment: [],
        searchedUsers: [],
        isShowTooMuch: false,
        isBeingSearch: false,
        rightLoading: false,

        navWidth: 240,
        dragWidth: 280,
        dragRealityWidth: 280,
        isDrag: false,

        searchConditionList: [
          {
            id: 'fuzzy',
            name: this.$t(`m.common['模糊搜索']`)
          },
          {
            id: 'exact',
            name: this.$t(`m.common['精确搜索']`)
          }
        ],
        searchConditionValue: 'fuzzy',
        isSerachFocus: false,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
            ...mapGetters(['user', 'isSync', 'navStick']),
            isAuthDisabled () {
                return this.hasSelectedDeparts.length < 1;
            },
            isSeachResultTooMuch () {
                return !this.treeLoading && this.isShowTooMuch;
            },
            isSeachResultEmpty () {
                return this.searchedResult.length < 1 && !this.treeLoading && !this.isShowTooMuch;
            },
            isDepart () {
                return this.curSelectedData.type && this.curSelectedData.type === 'depart';
            },
            isRecord () {
                return this.curSelectedData.type && this.curSelectedData.type === 'record';
            },
            leftStyle () {
                if (this.dragWidth > 0) {
                    return {
                        'flexBasis': `${this.dragWidth}px`
                    };
                }
                return {
                    'flexBasis': '280px'
                };
            },
            rightStyle () {
                if (this.dragWidth > 0) {
                    return {
                        'width': `calc(100% - ${this.dragWidth}px)`
                    };
                }
                return {
                    'width': `calc(100% - 280px)`
                };
            },
            dragStyle () {
                return {
                    'left': `${this.dragWidth}px`
                };
            },
            dottedLineStyle () {
                return {
                    'left': `${this.dragRealityWidth}px`
                };
            },
            contentStyle () {
                if (this.isSync) {
                    return { height: this.contentHeight - 82 - 17 - 18 + 'px' };
                }
                return { height: this.contentHeight - 82 - 17 + 'px' };
            },
            searchStyle () {
                if (this.isSync) {
                    return { maxHeight: this.contentHeight - 82 - 17 - 18 + 'px' };
                }
                return { maxHeight: this.contentHeight - 82 - 17 + 'px' };
            }
    },
    watch: {
      /**
       * isShowAuthWrapper
       */
      isShowAuthWrapper (value) {
        this.clickTriggerType = value ? 'only-radio' : 'only-click';
      },
      /**
       * searchKeyWord
       */
      searchKeyWord (newVal, oldVal) {
        if (!newVal && oldVal) {
          if (this.isBeingSearch) {
            this.isShowSearchResult = false;
            this.fetchCategories(true);
            this.isBeingSearch = false;
          }
        }
      },
      navStick (value) {
        this.navWidth = value ? 240 : 60;
      }
    },
    created () {
      window.addEventListener('resize', this.windowResize);
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.windowResize);
        bus.$off('sync-success');
      });
    },
    mounted () {
      bus.$on('sync-success', () => {
        this.fetchCategories(true);
      });
    },
    methods: {
      /**
       * windowResize
       */
      windowResize () {
        this.contentHeight = window.innerHeight - 61;
      },

      /**
       * handleSearchInput
       */
      handleSearchInput () {
        this.isSerachFocus = true;
      },

      /**
       * handleSearchBlur
       */
      handleSearchBlur () {
        this.isSerachFocus = false;
      },

      /**
       * handleDragMouseenter
       */
      handleDragMouseenter (e) {
        if (this.isDrag) {
          return;
        }
        this.isDrag = true;
        document.addEventListener('mousemove', this.handleDragMousemove);
        document.addEventListener('mouseup', this.handleDragMouseup);
      },

      handleDragMouseleave (e) {},

      /**
       * handleDragMouseup
       */
      handleDragMouseup (e) {
        this.dragWidth = this.dragRealityWidth;
        this.isDrag = false;
        document.removeEventListener('mousemove', this.handleDragMousemove);
        document.removeEventListener('mouseup', this.handleDragMouseup);
      },

      /**
       * handleDragMousemove
       */
      handleDragMousemove (e) {
        if (!this.isDrag) {
          return;
        }
        // 可拖拽范围
        const minWidth = this.navWidth + 280;
        const maxWidth = this.navWidth + 540;
        if (e.clientX < minWidth || e.clientX >= maxWidth) {
          return;
        }
        this.dragRealityWidth = e.clientX - this.navWidth;
      },

      /**
       * fetchPageData
       */
      async fetchPageData () {
        await this.fetchCategories(false);
      },

      /**
       * fetchCategories
       */
      async fetchCategories (isTreeLoading = false) {
        this.treeLoading = isTreeLoading;
        try {
          const { code, data } = await this.$store.dispatch('organization/getCategories');
          const categories = [...data];
          categories.forEach((item, index) => {
            item.visiable = true;
            item.level = 0;
            item.showRadio = false;
            item.selected = false;
            item.expanded = index === 0;
            item.count = 0;
            item.disabled = !item.departments || item.departments.length < 1;
            item.type = 'depart';
            item.showCount = false;
            item.async = item.departments && item.departments.length > 0;
            item.isNewMember = false;
            item.loading = false;
            item.is_selected = false;
            item.parentNodeId = '';
            item.id = `${item.id}&${item.level}`;
            if (item.departments && item.departments.length > 0) {
              item.departments.forEach((child, childIndex) => {
                child.visiable = false;
                child.level = 1;
                child.loading = false;
                child.showRadio = false;
                if (Object.keys(this.curSelectedData).length > 0
                  && this.curSelectedData.id === child.id
                ) {
                  child.selected = true;
                } else {
                  child.selected = false;
                }
                child.expanded = false;
                child.disabled = false;
                child.type = 'depart';
                child.count = child.recursive_member_count;
                // child.showCount = true;
                child.showCount = false;
                child.async = child.child_count > 0 || child.member_count > 0;
                child.isNewMember = false;
                child.parentNodeId = item.id;
              });
              item.children = _.cloneDeep(item.departments);
            }
          });
          // 默认展开第一个目录下的节点且选中第一个子节点
          const firstIndex = 0;
          const children = categories[firstIndex].children;
          children.forEach(item => {
            item.visiable = true;
          });
          if (Object.keys(this.curSelectedData).length < 1) {
            children[0].selected = true;
            this.curSelectedData = _.cloneDeep(children[0]);
          }
          categories.splice(firstIndex + 1, 0, ...children);
          this.treeList = _.cloneDeep(categories);
          this.emptyData = formatCodeData(code, this.emptyData, this.treeList.length === 0);
        } catch (e) {
          console.error(e);
          const { code, data, message, statusText } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.bkMessageInstance = this.$bkMessage({
            theme: 'error',
            message: message || data.msg || statusText
          });
        } finally {
          this.treeLoading = false;
        }
      },

      /**
       * handleConditionSelcted
       */
      handleConditionSelcted (payload) {
        this.$refs.dropdown.hide();
        this.searchConditionValue = payload.id;
        this.handleSearch();
      },

      /**
       * handleSearch
       */
      async handleSearch () {
        if (!this.searchKeyWord) {
          return;
        }
        this.treeList.splice(0, this.treeList.length, ...[]);
        this.isBeingSearch = true;
        this.treeLoading = true;
        this.isShowSearchResult = true;
        this.searchedResult.splice(0, this.searchedResult.length, ...[]);
        this.searchedDepartment.splice(0, this.searchedDepartment.length, ...[]);
        this.searchedUsers.splice(0, this.searchedUsers.length, ...[]);
        const params = {
          keyword: this.searchKeyWord,
          is_exact: this.searchConditionValue === 'exact'
        };
        try {
          const { code, data } = await this.$store.dispatch('organization/getSearchOrganizations', params);
          const { departments, users } = data;
          if (data.is_too_much) {
            this.isShowTooMuch = true;
            return;
          }
          this.isShowTooMuch = false;
          if (departments.length > 0) {
            departments.forEach(depart => {
              depart.showRadio = false;
              depart.type = 'depart';
              this.$set(depart, 'is_selected', false);
              if (Object.keys(this.curSelectedData).length > 0 && this.curSelectedData.id === depart.id) {
                this.$set(depart, 'selected', true);
              } else {
                this.$set(depart, 'selected', false);
              }
              depart.count = depart.recursive_member_count;
              // depart.showCount = true;
              depart.showCount = false;
            });
            this.searchedDepartment.splice(0, this.searchedDepartment.length, ...departments);
          }
          if (users.length > 0) {
            users.forEach(user => {
              user.id = guid();
              user.showRadio = false;
              user.type = 'user';
              this.$set(user, 'is_selected', false);
              if (Object.keys(this.curSelectedData).length > 0
                && this.curSelectedData.username === user.username
              ) {
                this.$set(user, 'selected', true);
              } else {
                this.$set(user, 'selected', false);
              }
            });
            this.searchedUsers.splice(0, this.searchedUsers.length, ...users);
          }
          this.searchedResult.splice(
            0,
            this.searchedResult.length,
            ...this.searchedDepartment.concat(this.searchedUsers)
          );
          const isEmpty = users.length === 0 && departments.length === 0;
          this.emptyData.tipType = 'search';
          this.emptyData = formatCodeData(code, this.emptyData, isEmpty);
        } catch (e) {
          const { code, data, message, statusText } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.bkMessageInstance = this.$bkMessage({
            theme: 'error',
            message: message || data.msg || statusText
          });
        } finally {
          this.treeLoading = false;
        }
      },

      /**
       * handleEmptyClear
       */
      handleEmptyClear () {
        this.searchKeyWord = '';
        this.emptyData.tipType = '';
      },
            
      /**
       * handleEmptyRefresh
       */
      handleEmptyRefresh () {
        this.fetchPageData();
      },

      /**
       * handleBatchAuth
       */
      handleBatchAuth () {
        this.isShowAuthWrapper = true;
      },

      /**
       * handleSyncDepartment
       */
      async handleSyncDepartment () {
        if (this.isSync) {
          return;
        }
        this.$store.commit('updateSync', true);
        // this.curSelectedData.type = 'depart';
        try {
          const res = await this.$store.dispatch('organization/organizationsSyncTask');
          if (res.result) {
            bus.$emit('updatePoll');
            window.localStorage.setItem('isPoll', true);
          }
        } catch (e) {
          this.$store.commit('updateSync', false);
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            theme: 'error',
            message: e.message || e.data.msg || e.statusText
          });
        }
      },

      /**
       * handleSyncRecordList 展示同步记录
       */
      handleSyncRecordList () {
        this.curSelectedData.type = 'record';
      },

      handleAuthHandleClickOutSide () {},

      handleClear () {},

      handleDelete () {},

      handleAuth () {},

      /**
       * handleAuthCancel
       */
      handleAuthCancel () {
        this.isShowAuthWrapper = false;
      },

      /**
       * handleExpanded
       */
      handleExpanded (payload) {
        const flag = this.treeList.some(item => item.parentNodeId === payload.id);
        if (payload.level === 0 && !flag) {
          const curIndex = this.treeList.findIndex(item => item.id === payload.id);
          if (curIndex !== -1) {
            const children = _.cloneDeep(this.treeList[curIndex].children);
            if (children && children.length > 0) {
              children.forEach(item => {
                if (Object.keys(this.curSelectedData).length > 0
                  && this.curSelectedData.id === item.id
                ) {
                  item.selected = true;
                } else {
                  item.selected = false;
                }
                item.visiable = true;
              });
              this.treeList.splice(curIndex + 1, 0, ...children);
            }
          }
        }
      },

      /**
       * handleRemoteLoadNode
       */
      async handleRemoteLoadNode (payload) {
        if (payload.level === 0) {
          return;
        }
        payload.loading = true;
        try {
          const res = await this.$store.dispatch('organization/getOrganizations', { departmentId: payload.id });
          const { children, members } = res.data;
          if (children.length < 1 && members.length < 1) {
            payload.expanded = false;
            return;
          }

          const curIndex = this.treeList.findIndex(item => item.id === payload.id);

          if (curIndex === -1) {
            return;
          }
          const treeList = [];
          treeList.splice(0, 0, ...this.treeList);
          if (children.length > 0) {
            children.forEach((child, childIndex) => {
              child.visiable = payload.expanded;
              child.level = payload.level + 1;
              child.loading = false;
              child.showRadio = false;

              if (Object.keys(this.curSelectedData).length > 0 && this.curSelectedData.id === child.id) {
                child.selected = true;
              } else {
                child.selected = false;
              }

              child.expanded = false;
              child.disabled = this.disabled;
              child.type = 'depart';
              child.count = child.recursive_member_count;
              // child.showCount = true;
              child.showCount = false;
              child.async = child.child_count > 0 || child.member_count > 0;
              child.isNewMember = false;
              child.parentNodeId = payload.id;
            });
          }

          if (members.length > 0) {
            members.forEach((child, childIndex) => {
              child.visiable = payload.expanded;
              child.level = payload.level + 1;
              child.loading = false;
              child.showRadio = false;

              if (Object.keys(this.curSelectedData).length > 0
                && this.curSelectedData.username === child.username
              ) {
                child.selected = true;
              } else {
                child.selected = false;
              }

              child.expanded = false;
              child.disabled = this.disabled;
              child.type = 'user';
              child.count = 0;
              child.showCount = false;
              child.async = false;
              child.isNewMember = false;
              child.parentNodeId = payload.id;
              child.is_selected = false;

              // parentNodeId + username 组合成id
              child.id = `${child.parentNodeId}${child.username}`;

              const existSelectedNode = this.treeList.find(
                item => item.is_selected && item.username === child.username
              );
              if (existSelectedNode) {
                child.is_selected = true;
                child.disabled = true;
              }
            });
          }

          const loadChildren = children.concat([...members]);

          treeList.splice(curIndex + 1, 0, ...loadChildren);

          this.treeList.splice(0, this.treeList.length, ...treeList);

          if (!payload.children) {
            payload.children = [];
          }

          payload.children.splice(0, payload.children.length, ...loadChildren);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            theme: 'error',
            message: e.message || e.data.msg || e.statusText
          });
        } finally {
          setTimeout(() => {
            payload.loading = false;
          }, 300);
        }
      },

      handleOnSelected () {},

      /**
       * handleOnClick
       */
      handleOnClick (payload) {
        this.treeList.forEach(item => {
          item.selected = false;
        });
        payload.selected = true;
        this.curSelectedData = _.cloneDeep(payload);
      },

      handleSearchSelected () {},

      /**
       * handleSearchClick
       */
      handleSearchClick (payload) {
        this.searchedResult.forEach(item => {
          item.selected = false;
          if ((item.type === 'depart' && item.id === payload.id)
            || (item.type === 'user' && item.username === payload.username)) {
            item.selected = true;
          }
        });
        this.curSelectedData = _.cloneDeep(payload);
      },

      /**
       * handleInitDepartContent
       */
      handleInitDepartContent (payload) {
        this.rightLoading = !payload;
      },

      handleInitUserContent (payload) {
        this.rightLoading = !payload;
      },

      handleInitRecordContent (payload) {
        this.rightLoading = !payload;
      },

      // 子组件emit方法
      handleBack () {
        this.curSelectedData.type = 'depart';
      }

    }
  };
</script>
<style lang="postcss">
    @import './index.css';
</style>
