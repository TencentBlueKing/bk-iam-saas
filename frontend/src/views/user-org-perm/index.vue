<template>
  <div class="user-org-wrapper">
    <div
      :class="[
        'user-org-wrapper-search',
        { 'no-search-data': !expandData['search'].isExpand || isHasDataNoExpand }
      ]"
    >
      <IamResourceCascadeSearch
        ref="iamResourceSearchRef"
        :custom-class="'user-org-resource-perm'"
        :active="active"
        :is-full-screen="true"
        :is-custom-search="true"
        :cur-search-data="searchData"
        :grid-count="gridCount"
        @on-remote-table="handleRemoteTable"
        @on-refresh-table="handleRefreshTable"
        @on-select-system="handleSelectSystemAction"
        @on-select-resource="handleSelectResource"
        @on-select-instance="handleSelectInstance"
      >
        <div
          slot="custom-content"
          :class="['custom-content', { 'custom-content-no-search': !enableGroupInstanceSearch }]"
        >
          <bk-form form-type="vertical" class="custom-content-form">
            <iam-form-item
              :label="$t(`m.userGroup['用户组名']`)"
              :style="{ width: formItemWidth }"
              class="custom-form-item"
            >
              <bk-input
                v-model="formData.name"
                :clearable="true"
                :placeholder="$t(`m.verify['请输入']`)"
                :right-icon="'bk-icon icon-search'"
                @right-icon-click="handleSearch"
                @enter="handleSearch"
                @clear="handleClearSearch"
              />
            </iam-form-item>
            <iam-form-item
              :label="$t(`m.userOrOrg['用户组 ID']`)"
              :style="{ width: formItemWidth }"
              class="custom-form-item"
            >
              <bk-input
                type="number"
                v-model="formData.id"
                :placeholder="$t(`m.verify['请输入']`)"
                :precision="0"
                :show-controls="false"
                @enter="handleSearch"
              />
            </iam-form-item>
            <iam-form-item
              :label="$t(`m.common['用户名']`)"
              :style="{ width: formItemWidth }"
              class="custom-form-item"
            >
              <!-- <bk-input
                v-model="formData.username"
                :clearable="true"
                :show-clear-only-hover="true"
                :placeholder="$t(`m.verify['请输入']`)"
                :right-icon="'bk-icon icon-search'"
                @right-icon-click="handleSearch"
                @enter="handleSearch"
                @clear="handleClearSearch"
              /> -->
              <bk-user-selector
                ref="userSelectorRef"
                :value="permMembers"
                :api="userApi"
                :multiple="false"
                style="width: 100%"
                :placeholder="$t(`m.verify['请输入']`)"
                :empty-text="$t(`m.common['无匹配人员']`)"
                @change="handleMemberChange(...arguments, 'username')"
              />
            </iam-form-item>
            <iam-form-item
              :label="$t(`m.perm['组织名']`)"
              :style="{ width: formItemWidth }"
              class="custom-form-item"
            >
              <bk-input
                v-model="formData.department_name"
                :clearable="true"
                :placeholder="$t(`m.verify['请输入']`)"
                :right-icon="'bk-icon icon-search'"
                @right-icon-click="handleSearch"
                @enter="handleSearch"
                @clear="handleClearSearch"
              />
            </iam-form-item>
          </bk-form>
          <div class="custom-content-footer">
            <bk-button
              theme="primary"
              :outline="true"
              @click="handleSearch">
              {{ $t(`m.common['查询']`) }}
            </bk-button>
            <bk-button
              style="margin-left: 8px;"
              theme="default"
              @click="handleEmptyUserClear">
              {{ $t(`m.common['清空']`) }}
            </bk-button>
          </div>
        </div>
      </IamResourceCascadeSearch>
    </div>
    <div v-if="isHasDataNoExpand" class="search-data-no-expand">
      <!-- 处理有值的情况下折叠场景 -->
      <div class="no-expand-search-list">
        <div class="search-data-content">
          <span class="funnel">
            <Icon bk type="funnel" class="funnel-icon" />
          </span>
          <span
            v-for="tag in searchTagList"
            :key="tag.name"
            class="tag-list"
          >
            <bk-popconfirm
              v-if="tag.value"
              :ref="`popoverConfirm_${tag.name}`"
              trigger="click"
              placement="bottom-start"
              :width="320"
              :ext-cls="formatPopover(tag)"
              :confirm-text="$t(`m.common['确认']`)"
              @confirm="handlePopoverChange"
            >
              <div slot="content">
                <div class="popover-title">{{ tag.label }}</div>
                <div class="popover-tag-input">
                  <!-- <bk-tag-input
                    :value="[tag.value]"
                    :placeholder="$t(`m.verify['请输入']`)"
                    :max-data="1"
                    :has-delete-icon="true"
                    :allow-create="true"
                    @change="handleInputChange(...arguments, tag.name)"
                  /> -->
                  <bk-input
                    v-if="['name', 'department_name'].includes(tag.name)"
                    ref="inputRef"
                    :value="tag.value"
                    :clearable="true"
                    :placeholder="$t(`m.verify['请输入']`)"
                    :right-icon="'bk-icon icon-search'"
                    @right-icon-click="handlePopoverChange"
                    @enter="handlePopoverChange"
                    @clear="handleClearSearch"
                    @input="handleInputChange(tag.name, ...arguments)"
                  />
                  <bk-input
                    v-if="['id'].includes(tag.name)"
                    ref="inputRef"
                    type="number"
                    :precision="0"
                    :value="tag.value"
                    :placeholder="$t(`m.verify['请输入']`)"
                    :show-controls="false"
                    @enter="handlePopoverChange"
                    @input="handleInputChange(tag.name, ...arguments)"
                  />
                  <bk-user-selector
                    v-if="['username'].includes(tag.name)"
                    ref="userSelectorRef"
                    style="width: 100%"
                    :value="permMembers"
                    :api="userApi"
                    :multiple="false"
                    :placeholder="$t(`m.verify['请输入']`)"
                    :empty-text="$t(`m.common['无匹配人员']`)"
                    @change="handleMemberChange(...arguments, tag.name)"
                  />
                </div>
              </div>
              <template v-if="tag.value">
                <bk-tag
                  :closable="formatAllowClose(tag.name)"
                  class="tag-item"
                  :key="tag.name"
                  @close="handleCloseTag(tag)">
                  <div @click.stop="handleShowPopover(tag)">
                    <span>{{tag.label}}:</span>
                    <span class="tag-item-value">{{ tag.value }}</span>
                  </div>
                </bk-tag>
              </template>
            </bk-popconfirm>
          </span>
          <span
            class="delete-all"
            v-if="hasTagData"
            v-bk-tooltips="{ content: $t(`m.common['清空搜索条件']`) }">
            <Icon
              bk
              type="close-circle-shape"
              class="delete-all-icon"
              @click.stop="handleClearAll"
            />
          </span>
        </div>
      </div>
    </div>
    <div
      :class="[
        'user-org-wrapper-expand',
        { 'user-org-wrapper-expand-no-search': !enableGroupInstanceSearch },
        { 'no-expand-no-search-data': isNoSearchData },
        { 'no-expand-has-search-data': isHasDataNoExpand }
      ]"
      @click.stop="handleToggleExpand('search')"
    >
      <bk-icon :type="expandData['search'].isExpand ? 'angle-up' : 'angle-down'" class="icon" />
    </div>
    <div class="user-org-wrapper-content">
      <Layout
        :is-expand="expandData['slider'].isExpand"
        :is-no-expand-no-search-data="isNoSearchData"
        :is-no-expand-has-search-data="isHasDataNoExpand"
      >
        <div class="user-org-wrapper-content-left" :style="leftStyle">
          <LeftLayout
            ref="leftLayoutRef"
            :is-loading="listLoading"
            :is-no-expand-no-search-data="isNoSearchData"
            :is-no-expand-has-search-data="isHasDataNoExpand"
            :list="groupList"
            :page-conf="pageConf"
            :group-data="currentGroupData"
            :cur-select-active="curSelectActive"
            :can-scroll-load="canScrollLoad"
            :is-search-perm="isHasSearch"
            :cur-search-params="querySearchParams"
            :cur-search-pagination="curSearchPagination"
            :empty-data="emptyData"
            @on-select="handleSelectUser"
            @on-load-more="handleLoadMore"
            @on-batch-operate="handleBatchOperate"
            @on-clear="handleEmptyUserClear"
            @on-refresh="handleEmptyUserRefresh"
          />
        </div>
        <div slot="expand-icon" class="user-org-wrapper-content-center">
          <div class="expand-icon" @click.stop="handleToggleExpand('slider')">
            <bk-icon :type="expandData['slider'].isExpand ? 'angle-left' : 'angle-right'" class="icon" />
          </div>
        </div>
        <div
          slot="right"
          :class="[
            'user-org-wrapper-content-right',
            { 'no-expand': !expandData['slider'].isExpand }
          ]">
          <template v-if="groupList.length">
            <component
              :key="comKey"
              :is="curCom"
              :is-search-perm="isHasSearch"
              :group-data="currentGroupData"
              :cur-search-params="querySearchParams"
              :cur-search-pagination="curSearchPagination"
              @on-clear="handleEmptyClear"
              @on-refresh="handleEmptyRefresh"
            />
          </template>
          <div v-else class="right-empty-data">
            <ExceptionEmpty
              :type="emptyData.type"
              :empty-text="emptyData.text"
              :tip-text="emptyData.tip"
              :tip-type="emptyData.tipType"
              @on-clear="handleEmptyUserClear"
              @on-refresh="handleEmptyUserRefresh"
            />
          </div>
        </div>
      </Layout>
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { cloneDeep } from 'lodash';
  import { bus } from '@/common/bus';
  import { delLocationHref, formatCodeData } from '@/common/util';
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';
  import Layout from './components/page-layout';
  import LeftLayout from './components/left-layout.vue';
  import RightLayout from './components/right-layout.vue';
  import BkUserSelector from '@blueking/user-selector';

  const COM_MAP = new Map([
    [['user', 'department'], 'RightLayout']
  ]);

  export default {
    inject: ['showNoticeAlert'],
    components: {
      IamResourceCascadeSearch,
      Layout,
      LeftLayout,
      RightLayout,
      BkUserSelector
    },

    data () {
      return {
        userApi: window.BK_USER_API,
        enableGroupInstanceSearch: window.ENABLE_GROUP_INSTANCE_SEARCH.toLowerCase() === 'true',
        listLoading: false,
        isSearchPerm: false,
        expandData: {
          search: {
            isExpand: true
          },
          slider: {
            isExpand: true
          }
        },
        comKey: -1,
        curSearchParams: {},
        curSearchPagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        active: '',
        curSelectActive: '',
        groupList: [],
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.userGroup['用户/组织名']`),
            default: true
          },
          {
            id: 'id',
            name: 'ID',
            default: true
          },
          {
            id: 'description',
            name: this.$t(`m.common['描述']`),
            default: true
          }
        ],
        formData: {
          name: '',
          id: '',
          username: '',
          department_name: ''
        },
        pageConf: {
          current: 1,
          limit: 10,
          totalPage: 1,
          count: 0
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        curEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        currentGroupData: {},
        curSystemAction: {},
        curResourceData: {
          resource_type: '',
          condition: []
        },
        resourceTypeData: {},
        currentBackup: 1,
        gridCount: 4,
        dragWidth: 224,
        formItemWidth: '',
        listHeight: window.innerHeight - 51 - 51 - 157 - 42 - 8,
        searchTagList: [
          {
            name: 'system_id',
            label: this.$t(`m.common['系统']`),
            value: ''
          },
          {
            name: 'action_id',
            label: this.$t(`m.common['操作']`),
            value: ''
          },
          {
            name: 'resource_type',
            label: this.$t(`m.permApply['资源类型']`),
            value: ''
          },
          {
            name: 'resource_instance',
            label: this.$t(`m.common['资源实例']`),
            value: ''
          },
          {
            name: 'name',
            label: this.$t(`m.userGroup['用户组名']`),
            value: ''
          },
          {
            name: 'id',
            label: this.$t(`m.userOrOrg['用户组 ID']`),
            value: ''
          },
          {
            name: 'username',
            label: this.$t(`m.common['用户名']`),
            value: ''
          },
          {
            name: 'department_name',
            label: this.$t(`m.perm['组织名']`),
            value: ''
          }
        ],
        resourceInstances: [],
        noPopoverList: ['system_id', 'action_id', 'resource_type', 'resource_instance'],
        permMembers: [],
        tagInputValue: {}
      };
    },

    computed: {
      ...mapGetters(['navStick']),
      leftStyle () {
        if (this.dragWidth > 0) {
          return {
            flexBasis: `${this.dragWidth}px`
          };
        }
        return {
          flexBasis: '224px'
        };
      },
      isHasSearch () {
        // 这里之所以把资源类型、实例与系统、操作区分开，是因为有选了操作，但是没有资源数据的业务场景
        const searchParams = { ...this.curSystemAction, ...this.formData };
        const hasData = Object.values(searchParams).filter((item) => item !== '');
        const { condition, resource_type: resourceType } = this.curResourceData;
        return !!(hasData.length > 0 || (condition && condition.length > 0) || resourceType);
      },
      isNoSearchData () {
        const searchParams = { ...this.curSystemAction, ...this.formData };
        const hasData = Object.values(searchParams).filter((item) => item !== '');
        const { condition, resource_type: resourceType } = this.curResourceData;
        return !hasData.length && (!condition || (condition && !condition.length)) && !resourceType && !this.expandData['search'].isExpand;
      },
      isHasDataNoExpand () {
        return this.isHasSearch && !this.expandData['search'].isExpand;
      },
      canScrollLoad () {
        return this.pageConf.totalPage > this.currentBackup;
      },
      curCom () {
        let com = '';
        for (const [key, value] of this.comMap.entries()) {
          if (Object.keys(this.currentGroupData).length && key.includes(this.currentGroupData.type)) {
            com = value;
            break;
          }
        }
        return com;
      },
      querySearchParams () {
        return { ...this.curSearchParams, ...this.formData };
      },
      hasTagData () {
        return this.searchTagList.filter((item) => item.value !== '').length > 0;
      },
      formatPopover () {
        return (payload) => {
          const { name } = payload;
          if (this.noPopoverList.includes(name)) {
            return 'user-org-popover-tag-edit user-org-popover-tag-edit-none';
          }
          return 'user-org-popover-tag-edit';
        };
      },
      formatAllowClose () {
        return (payload) => {
          return !['action_id', 'resource_type', 'resource_instance'].includes(payload);
        };
      }
    },

    watch: {
      formData: {
        handler (value) {
          // 监听表单输入框数据变化，同步删除url上的参数
          const queryParams = { ...this.$route.query, ...this.$route.params };
          Object.keys(this.formData).forEach((item) => {
            if (queryParams[item] && !value[item]) {
              this.formData[item] = queryParams[item];
              delLocationHref([item]);
            }
          });
        },
        deep: true
      },
      navStick () {
        this.formatFormItemWidth();
      }
    },

    async created () {
      this.comMap = COM_MAP;
      this.pageConf.limit = Math.ceil(this.listHeight / 36);
      this.formatFormItemWidth();
      this.getRouteParams();
      await this.fetchFirstData();
    },

    mounted () {
      window.addEventListener('resize', this.formatFormItemWidth);
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
      });
    },

    methods: {
      async fetchInitData () {
        this.pageConf.current = 1;
        this.currentBackup = 1;
        await this.fetchGroupMemberList(true, false);
      },

      async fetchDefaultSelectData () {
        if (this.groupList.length) {
          const { id, name } = this.groupList[0];
          this.curSelectActive = `${id}&${name}`;
          const params = {
            ...this.curSearchParams,
            ...this.formData
          };
          const groupData = { ...this.groupList[0], ...{ isClick: true } };
          bus.$emit('on-refresh-resource-search', {
            isSearchPerm: this.isSearchPerm,
            curSearchParams: params,
            curSearchPagination: this.curSearchPagination,
            groupData
          });
        }
      },

      async fetchFirstData () {
        await this.fetchInitData();
        await this.fetchDefaultSelectData();
      },

      async fetchGroupMemberList (isLoading = true, isScrollLoad = false) {
        this.listLoading = isLoading;
        try {
          const { current, limit } = this.pageConf;
          const params = {
            ...this.curSearchParams,
              ...this.formData,
            page: current,
            page_size: limit,
            apply_disable: false
          };
          const { code, data } = await this.$store.dispatch('userOrOrg/getUserGroupMemberList', params);
          const { count, results } = data;
          const list = results || [];
          this.pageConf.count = count || 0;
          if (!isScrollLoad) {
            this.groupList = [...list];
            this.currentGroupData = this.groupList.length ? this.groupList[0] : {};
            this.pageConf.totalPage = Math.ceil(this.pageConf.count / limit);
          } else {
            this.currentBackup++;
            this.groupList.push(...results);
          }
          this.handleRefreshTipType('emptyData');
          this.emptyData = formatCodeData(code, this.emptyData, this.groupList.length === 0);
        } catch (e) {
          this.groupList = [];
          this.handleRefreshTipType('emptyData');
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.listLoading = false;
        }
      },

      async handleLoadMore () {
        const { totalPage } = this.pageConf;
        if (this.pageConf.current + 1 > totalPage) {
          return;
        }
        this.pageConf.current++;
        await this.fetchGroupMemberList(false, true);
      },

      async handleRemoteTable (payload) {
        const { emptyData, pagination, searchParams } = payload;
        const params = {
          ...searchParams,
          ...this.formData
        };
        this.isSearchPerm = emptyData.tipType === 'search';
        this.curSearchParams = cloneDeep(params);
        this.curSearchPagination = cloneDeep(pagination);
        this.curEmptyData = cloneDeep(emptyData);
        await this.fetchFirstData();
      },

      async fetchRemoteTable () {
        await this.fetchInitData();
        const params = {
          ...this.curSearchParams,
          ...this.formData
        };
        bus.$emit('on-refresh-resource-search', {
          isSearchPerm: true,
          curSearchParams: params,
          curSearchPagination: this.curSearchPagination
        });
      },

      async handleToggleExpand (payload) {
        this.expandData[payload].isExpand = !this.expandData[payload].isExpand;
        const distances = window.innerHeight - 51 - 51 - 42 - 8;
        if (['search'].includes(payload)) {
          if (this.expandData[payload].isExpand) {
            this.listHeight = this.showNoticeAlert && this.showNoticeAlert() ? distances - 157 - 40 : distances - 157;
          } else {
            this.listHeight = this.showNoticeAlert && this.showNoticeAlert() ? distances - 40 : distances;
            this.$refs.leftLayoutRef.currentSelectList = [];
          }
          this.pageConf = Object.assign(this.pageConf, {
            current: 1,
            totalPage: 1,
            limit: Math.ceil(this.listHeight / 36)
          });
          if (this.isHasSearch) {
            this.fetchHasSearchData();
            return;
          }
          this.groupList = [];
          await this.fetchFirstData();
        }
      },

      async handleRefreshTable () {
        this.curEmptyData.tipType = '';
        this.emptyData.tipType = '';
        this.isSearchPerm = false;
        this.pageConf.current = 1;
        this.curSearchParams = {};
        this.formData.name = '';
        await this.fetchInitData();
        bus.$emit('on-refresh-resource-search', {
          isSearchPerm: false
        });
      },

      // 处理折叠有搜索参数的业务场景
      async fetchHasSearchData () {
        this.isSearchPerm = true;
        const searchParams = { ...this.curSystemAction, ...this.curResourceData, ...this.formData };
        const resourceInstances = this.resourceInstances.reduce((prev, item) => {
          const { id, resourceInstancesPath } = this.handlePathData(item, item.type);
          prev.push({
            system_id: item.system_id,
            id: id,
            type: item.type,
            name: item.name,
            path: resourceInstancesPath
          });
          return prev;
        }, []);
        this.curSearchParams.resource_instances = resourceInstances || [];
        // 处理频繁切换展开场景下资源实例搜索值被清空了的业务场景
        if (!this.isHasDataNoExpand) {
          this.$nextTick(async () => {
            Object.keys(searchParams).forEach((item) => {
              const curData = this.searchTagList.find((v) => v.name === item);
              if (curData) {
                if (['system_id', 'action_id'].includes(item)) {
                  // 操作为空时重置关联数据
                  if (!searchParams[item].value) {
                    this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.resetSearchParams();
                  }
                }
              }
            });
            await this.fetchRemoteTable();
          });
        } else {
          Object.keys(searchParams).forEach((item) => {
            const curData = this.searchTagList.find((v) => v.name === item);
            if (curData) {
              if (['system_id', 'action_id', 'resource_type'].includes(item)) {
                curData.value = searchParams[item].label;
              } else {
                curData.value = searchParams[item];
              }
            }
          });
          await this.fetchFirstData();
          const params = {
            ...this.curSearchParams,
            ...this.formData
          };
          bus.$emit('on-refresh-resource-search', {
            isSearchPerm: true,
            curSearchParams: params,
            curSearchPagination: this.curSearchPagination
          });
        }
      },

      handleShowPopover (payload) {
        if (this.noPopoverList.includes(payload.name)) {
          return;
        }
        this.tagInputValue = { ...payload };
        this.$nextTick(() => {
          if (this.$refs[`popoverConfirm_${payload.name}`] && this.$refs[`popoverConfirm_${payload.name}`].length) {
            this.$refs[`popoverConfirm_${payload.name}`][0].$refs.popover.showHandler();
            if (['name', 'depart_name'].includes(payload.name)) {
              if (['name', 'depart_name'].includes(payload.name)
                && this.$refs.inputRef
                && this.$refs.inputRef.length
                && this.$refs.inputRef[0].$refs) {
                this.$refs.inputRef[0].$refs.input.focus();
              }
            }
            if (['username'].includes(payload.name)
              && this.$refs.userSelectorRef
              && this.$refs.userSelectorRef.length) {
              this.$refs.userSelectorRef[0].focus();
            }
          }
        });
      },

      handleHidePopover (payload) {
        this.$nextTick(() => {
          if (this.$refs[`popoverConfirm_${payload.name}`] && this.$refs[`popoverConfirm_${payload.name}`].length) {
            this.$refs[`popoverConfirm_${payload.name}`][0].$refs.popover.hideHandler();
          }
          this.tagInputValue = {};
        });
      },

      async handlePopoverChange () {
        const { name, value } = this.tagInputValue;
        if (name) {
          this.formData[name] = value;
          const curData = this.searchTagList.find((item) => item.name === name);
          if (curData) {
            curData.value = value;
          }
        }
        await this.fetchFirstData();
        const params = {
            ...this.curSearchParams,
            ...this.formData
        };
        bus.$emit('on-refresh-resource-search', {
          isSearchPerm: true,
          curSearchParams: params,
          curSearchPagination: this.curSearchPagination
        });
        this.handleHidePopover(this.tagInputValue);
      },

      // 获取跳转数据
      getRouteParams () {
        const queryParams = { ...this.$route.query, ...this.$route.params };
        Object.keys(this.formData).forEach((item) => {
          if (queryParams[item]) {
            this.formData[item] = queryParams[item];
          }
        });
      },

      handleInputChange (type, payload) {
        this.tagInputValue = {
          name: type,
          value: payload
        };
      },

      handlePathData (data, type) {
        if (data.resourceInstancesPath && data.resourceInstancesPath.length) {
          const lastIndex = data.resourceInstancesPath.length - 1;
          const path = data.resourceInstancesPath[lastIndex];
          let id = '';
          let resourceInstancesPath = [];
          if (type === path.type) {
            id = path.id;
            data.resourceInstancesPath.splice(lastIndex, 1);
          } else {
            id = '*';
          }
          resourceInstancesPath = data.resourceInstancesPath.reduce((p, e) => {
            p.push({
              type: e.type,
              id: e.id,
              name: e.name
            });
            return p;
          }, []);
          return { id, resourceInstancesPath };
        }
        return { id: '*', resourceInstancesPath: [] };
      },

      handleSelectInstance ({ resourceInstances, resourceTypeData }) {
        // 在切换展开收缩时，备份下之前的数据
        this.resourceInstances = cloneDeep(resourceInstances || []);
        this.resourceTypeData = cloneDeep(resourceTypeData);
      },

      handleSelectSystemAction (payload) {
        this.curSystemAction = { ...payload };
        if (this.curSystemAction.system_id) {
          if (this.curSystemAction.system_id.value !== this.curSearchParams.system_id) {
            this.searchTagList.forEach((item) => {
              if (['resource_type', 'resource_instance'].includes(item.name)) {
                item.value = '';
              }
            });
          }
          this.$set(this.curSearchParams, 'system_id', this.curSystemAction.system_id.value);
        }
        if (this.curSystemAction.action_id) {
          if (this.curSystemAction.action_id.value !== this.curSearchParams.action_id) {
            this.searchTagList.forEach((item) => {
              if (['resource_type', 'resource_instance'].includes(item.name)) {
                item.value = '';
              }
            });
          }
          this.$set(this.curSearchParams, 'action_id', this.curSystemAction.action_id.value);
        }
      },

      handleSelectResource (payload) {
        const { condition } = payload;
        this.curResourceData = { ...payload };
        // 处理资源实例数据格式化
        const curData = this.searchTagList.find((v) => v.name === 'resource_instance');
        if (condition) {
          // 如果资源实例为none，则为空
          if (condition.length) {
            if (condition.length === 1 && condition[0] === 'none') {
              curData.value = '';
              if (!this.curResourceData.resource_type) {
                const resourceType = this.searchTagList.find((v) => v.name === 'resource_type');
                resourceType.value = '';
              }
              return;
            }
            if (condition[0].instance && condition[0].instance.length) {
              const list = condition[0].instance[0].path[0] || [];
              list.forEach((item, index) => {
                if (list.length === 1) {
                  curData.value = `${item.name}`;
                } else {
                  curData.value += index !== list.length - 1 ? `${item.name}/` : item.name;
                }
              });
            }
          } else {
            curData.value = this.$t(`m.common['无限制']`);
          }
        } else {
          curData.value = '';
        }
        if (!Object.keys(payload).length) {
          this.searchTagList.forEach((item) => {
            if (['resource_type', 'resource_instance'].includes(item.name)) {
              item.value = '';
            }
          });
        }
      },

      handleMemberChange (payload, name) {
        this.permMembers = [...payload];
        this.$nextTick(() => {
          if (this.$refs.userSelectorRef) {
            this.formData.username = payload.length > 0 ? payload.join() : '';
            this.tagInputValue = {
              name,
              value: this.formData.username
            };
            if (!this.isHasDataNoExpand) {
              this.handleSearch();
            }
          }
        });
      },

      handleSearch () {
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleSearchUserGroup(true, true);
      },

      handleClearSearch () {
        this.handleSearch();
      },

      handleSelectUser (payload) {
        this.curSelectActive = `${payload.id}&${payload.name}`;
        this.currentGroupData = {
          ...payload,
          ...{
            isClick: true
          }
        };
      },

      async handleBatchOperate (payload) {
        const { name, isRefreshUser } = payload;
        if (['clear'].includes(name) && isRefreshUser) {
          await this.fetchFirstData();
        }
        bus.$emit('on-refresh-resource-search', {
          isSearchPerm: this.isSearchPerm,
          curSearchParams: this.curSearchParams,
          curSearchPagination: this.curSearchPagination
        });
      },

      async handleCloseTag (payload) {
        payload.value = '';
        this.pageConf.current = 1;
        if (this.curSystemAction[payload.name]) {
          this.curSystemAction[payload.name] = '';
        }
        if (this.formData[payload.name]) {
          this.formData[payload.name] = '';
          if (['username'].includes(payload.name)) {
            this.permMembers = [];
          }
        }
        if (this.curResourceData[payload.name]) {
          this.curResourceData[payload.name] = '';
        }
        if (this.curSearchParams[payload.name]) {
          this.curSearchParams[payload.name] = '';
        }
        // 删除有关联数据的tag
        if (['system_id', 'action_id'].includes(payload.name)) {
          this.searchTagList.forEach((item) => {
            if (!['name', 'id', 'username', 'department_name'].includes(item.name)) {
              item.value = '';
            }
            this.curSearchParams[item.name] = '';
            this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyClear();
          });
          await this.fetchFirstData();
          return;
        }
        if (['resource_type'].includes(payload.name)) {
          this.$set(this.curSearchParams, 'resource_instances', []);
          this.searchTagList.forEach((item) => {
            if (['resource_type', 'resource_instance'].includes(item.name)) {
              item.value = '';
            }
          });
        }
        await this.fetchFirstData();
      },

      async handleClearAll () {
        this.searchTagList.forEach((item) => {
          if (item.value) {
            item.value = '';
            if (this.curSystemAction[item.name]) {
              this.curSystemAction[item.name] = '';
            }
            if (this.formData[item.name]) {
              this.formData[item.name] = '';
            }
            if (this.curResourceData[item.name]) {
              this.curResourceData[item.name] = '';
            }
          }
        });
        await this.handleEmptyUserClear();
      },

      handleRefreshTipType (payload) {
        let tipType = '';
        if (this.isSearchPerm) {
          tipType = 'search';
        }
        if (this[payload].type === 500) {
          tipType = 'refresh';
        }
        this.emptyData = Object.assign({}, this[payload], { tipType });
      },

      handleEmptyRefresh () {
        if (this.isHasDataNoExpand) {
          this.fetchFirstData();
        } else {
          this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyRefresh();
        }
      },

      handleEmptyClear () {
        this.isSearchPerm = false;
        if (this.isHasDataNoExpand) {
          this.fetchFirstData();
        } else {
          this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyClear();
        }
      },

      handleEmptyUserClear () {
        this.curEmptyData.tipType = '';
        this.emptyData.tipType = '';
        this.isSearchPerm = false;
        this.pageConf.current = 1;
        this.curSearchParams = {};
        this.formData = {
          name: '',
          id: '',
          username: '',
          department_name: ''
        };
        this.permMembers = [];
        this.fetchFirstData();
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyClear();
      },

      handleEmptyUserRefresh () {
        this.handleEmptyUserClear();
      },

      formatFormItemWidth () {
        this.formItemWidth = `${(window.innerWidth - (this.navStick ? 276 : 76) - this.gridCount * 16) / this.gridCount}px`;
      }
    }
  };
</script>
<style lang="postcss">
.user-org-popover-tag-edit {
  color: #63656E;
  .popover-title {
    margin-bottom: 6px;
  }
  .popover-tag-input {
    margin-bottom: 12px;
  }
  &-none {
    display: none;
  }
}
</style>

<style lang="postcss" scoped>
@import './user-org-perm.css';
</style>
