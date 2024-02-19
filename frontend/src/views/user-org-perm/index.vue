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
        <div slot="custom-content" class="custom-content">
          <bk-form form-type="vertical" class="custom-content-form">
            <iam-form-item
              :label="$t(`m.userGroup['用户组名']`)"
              :style="{ width: formItemWidth }"
              class="custom-form-item"
            >
              <bk-input :placeholder="$t(`m.verify['请输入']`)" v-model="formData.group_name" />
            </iam-form-item>
            <iam-form-item
              :label="$t(`m.userOrOrg['用户组 ID']`)"
              :style="{ width: formItemWidth }"
              class="custom-form-item"
            >
              <bk-input :placeholder="$t(`m.verify['请输入']`)" v-model="formData.group_id" />
            </iam-form-item>
            <iam-form-item
              :label="$t(`m.common['用户名']`)"
              :style="{ width: formItemWidth }"
              class="custom-form-item"
            >
              <bk-input :placeholder="$t(`m.verify['请输入']`)" v-model="formData.name" />
            </iam-form-item>
            <iam-form-item
              :label="$t(`m.perm['组织名']`)"
              :style="{ width: formItemWidth }"
              class="custom-form-item"
            >
              <bk-input :placeholder="$t(`m.verify['请输入']`)" v-model="formData.department_name" />
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
              {{ $t(`m.common['取消']`) }}
            </bk-button>
          </div>
        </div>
      </IamResourceCascadeSearch>
    </div>
    <div v-if="isHasDataNoExpand" class="search-data-no-expand">
      <!-- 处理有值的情况下折叠场景 -->
      <div class="no-expand-search-list">
        <div class="search-data-content">
          <div class="funnel">
            <Icon bk type="funnel" class="funnel-icon" />
          </div>
          <div
            v-for="tag in searchTagList"
            :key="tag.id"
            class="tag-list"
          >
            <bk-popconfirm
              v-if="tag.value"
              trigger="click"
              placement="bottom-start"
              :ext-cls="formatPopover(tag)"
              :confirm-text="$t(`m.common['确认']`)"
              :width="320"
              @confirm="handlePopoverChange"
            >
              <div slot="content">
                <div class="popover-title">{{ tag.label }}</div>
                <div class="popover-tag-input">
                  <bk-tag-input
                    :value="[tag.value]"
                    :placeholder="$t(`m.verify['请输入']`)"
                    :has-delete-icon="true"
                    :list="[{ id: tag.value, name: tag.value }]"
                    :max-data="1"
                    :allow-create="true"
                    :allow-auto-match="true"
                    @change="handleInputChange(...arguments, tag.name)"
                  />
                </div>
              </div>
              <bk-tag
                v-if="tag.value"
                :closable="formatAllowClose(tag.name)"
                class="tag-item"
                :key="tag.name"
                @close="handleCloseTag(tag)">
                <div>
                  <span>{{tag.label}}:</span>
                  <span class="tag-item-value">{{ tag.value }}</span>
                </div>
              </bk-tag>
            </bk-popconfirm>
          </div>
          <div
            class="delete-all"
            v-if="hasTagData"
            v-bk-tooltips="{ content: $t(`m.common['清空搜索条件']`) }">
            <Icon
              bk
              type="close-circle-shape"
              class="delete-all-icon"
              @click.stop="handleClearAll"
            />
          </div>
        </div>
      </div>
    </div>
    <div
      :class="[
        'user-org-wrapper-expand',
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
            :loading="listLoading"
            :is-no-expand-no-search-data="isNoSearchData"
            :is-no-expand-has-search-data="isHasDataNoExpand"
            :list="groupList"
            :group-data="currentGroupData"
            :cur-select-active="curSelectActive"
            :can-scroll-load="canScrollLoad"
            :is-search-perm="isHasSearch"
            :cur-search-params="querySearchParams"
            :cur-search-pagination="curSearchPagination"
            :empty-data="emptyData"
            @on-select="handleSelectUser"
            @on-load-more="handleLoadMore"
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
  import { formatCodeData } from '@/common/util';
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';
  import Layout from './components/page-layout';
  import LeftLayout from './components/left-layout.vue';
  import RightLayout from './components/right-layout.vue';

  const COM_MAP = new Map([
    [['user', 'department'], 'RightLayout']
  ]);

  export default {
    inject: ['showNoticeAlert'],
    components: {
      IamResourceCascadeSearch,
      Layout,
      LeftLayout,
      RightLayout
    },

    data () {
      return {
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
          group_name: '',
          group_id: '',
          name: '',
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
            name: 'group_name',
            label: this.$t(`m.userGroup['用户组名']`),
            value: ''
          },
          {
            name: 'group_id',
            label: this.$t(`m.userOrOrg['用户组 ID']`),
            value: ''
          },
          {
            name: 'name',
            label: this.$t(`m.common['用户名']`),
            value: ''
          },
          {
            name: 'department_name',
            label: this.$t(`m.perm['组织名']`),
            value: ''
          }
        ],
        resourceInstances: []
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
          if (['system_id', 'action_id', 'resource_type', 'resource_instance'].includes(name)) {
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

    async created () {
      this.comMap = COM_MAP;
      this.pageConf.limit = Math.ceil(this.listHeight / 36);
      this.formatFormItemWidth();
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
          bus.$emit('on-refresh-resource-search', {
            isSearchPerm: this.isSearchPerm,
            curSearchParams: params,
            curSearchPagination: this.curSearchPagination,
            groupData: this.groupList[0]
          });
        }
      },

      async fetchFirstData () {
        await this.fetchInitData();
        await this.fetchDefaultSelectData();
      },

      async fetchGroupMemberList (isLoading = false, isScrollLoad = false) {
        this.listLoading = isLoading;
        try {
          const { current, limit } = this.pageConf;
          let params = {
            page: current,
            page_size: limit
          };
          if (this.isSearchPerm) {
            params = {
              ...this.formData,
              ...params
            };
          }
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
        await this.fetchRemoteTable();
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
            this.listHeight = this.showNoticeAlert ? distances - 157 - 40 : distances - 157;
          } else {
            this.listHeight = this.showNoticeAlert ? distances - 40 : distances;
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

      handleInputChange (payload, type) {
        console.log(payload, type);
        const text = payload.length ? payload[0] : '';
        this.formData[type] = text;
        const curData = this.searchTagList.find((item) => item.name === type);
        if (curData) {
          curData.value = text;
        }
      },

      async handlePopoverChange () {
        await this.fetchFirstData();
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

      handleSearch () {
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleSearchUserGroup(true, true);
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

      async handleCloseTag (payload) {
        payload.value = '';
        this.pageConf.current = 1;
        if (this.curSystemAction[payload.name]) {
          this.curSystemAction[payload.name] = '';
        }
        if (this.formData[payload.name]) {
          this.formData[payload.name] = '';
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
            if (!['group_name', 'group_id', 'name', 'department_name'].includes(item.name)) {
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
          group_name: '',
          group_id: '',
          name: '',
          department_name: ''
        };
        this.fetchFirstData();
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyClear();
      },

      handleEmptyUserRefresh () {
        this.handleEmptyUserClear();
      },

      async formatFormItemWidth () {
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
.user-org-wrapper {
  padding: 0;
  color: #313238;
  position: relative;
  &-search {
    box-shadow: 0 2px 3px 0 #0000000a;
    position: sticky;
    top: 0;
    z-index: 1;
    .custom-content {
      &-form {
        display: flex;
        .custom-form-item {
          margin-top: 12px;
          &:not(&:last-child) {
            margin-right: 16px;
          }
        }
      }
      &-footer {
        margin-top: 16px;
      }
    }
    &.no-search-data {
      display: none;
    }
  }
  &-expand {
    width: 64px;
    height: 16px;
    background-color: #dcdee5;
    border-radius: 0 4px 4px 0;
    position: absolute;
    top: 223px;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 1;
    cursor: pointer;
    .icon {
      color: #ffffff;
      font-size: 22px !important;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }
    &.no-expand-no-search-data {
      top: 8px;
    }
    &.no-expand-has-search-data {
      top: 50px;
    }
  }
  &-content {
    &-left {
      padding: 0 16px;
      background-color: #FAFBFD;
      border-right: 1px solid#dcdee5;
      height: calc(100vh - 61px);
    }
    &-center {
      width: 16px;
      height: calc(100vh - 234px);
      .expand-icon {
        width: 16px;
        height: 64px;
        background-color: #dcdee5;
        border-radius: 0 4px 4px 0;
        position: relative;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        .icon {
          color: #ffffff;
          font-size: 22px !important;
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
        }
      }
    }
    &-right {
      padding-right: 16px;
      position: relative;
      height: 100%;
      &.no-expand {
        padding-right: 0;
      }
      .right-empty-data {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      }
    }
  }
  .search-data-no-expand {
    min-height: 42px;
    line-height: 42px;
    background-color: #ffffff;
    .no-expand-search-list {
      padding: 0 16px;
      .search-data-content {
        display: flex;
        align-items: center;
        .funnel-icon {
          color: #979BA5;
        }
        .tag-list {
          .tag-item {
            display: flex;
            align-items: center;
            cursor: pointer;
            &-value {
              margin-left: 8px;
            }
          }
        }
        .delete-all {
          margin-left: 8px;
          &-icon {
            color: #C4C6CC;
            font-size: 14px;
            cursor: pointer;
            vertical-align: middle;
            &:hover {
              color: #979BA5;
            }
          }
        }
      }
    }
  }
}
</style>
