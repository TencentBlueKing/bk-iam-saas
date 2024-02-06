<template>
  <div class="user-org-wrapper">
    <div
      v-if="!isHasDataNoExpand"
      :class="[
        'user-org-wrapper-search',
        { 'no-search-data': !expandData['search'].isExpand }
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
        @on-select-system="handleSelectSystem"
        @on-select-resource="handleSelectResource"
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
            :key="tag"
            class="tag-list"
          >
            <bk-tag
              closable
              :key="tag"
              @close="handleCloseTag(tag)">
              {{tag}}
            </bk-tag>
          </div>
          <div
            class="delete-all"
            v-if="searchTagList.length"
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
          type: '',
          condition: []
        },
        currentBackup: 1,
        gridCount: 4,
        dragWidth: 224,
        formItemWidth: '',
        listHeight: window.innerHeight - 51 - 51 - 157 - 42 - 8,
        searchTagList: []
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
        const searchParams = { ...this.curSystemAction, ...this.formData };
        const hasData = Object.values(searchParams).filter((item) => item !== '');
        const { condition, type } = this.curResourceData;
        console.log(555);
        if (hasData.length) {
          console.log(hasData);
        }
        return !!(hasData.length > 0 || (condition && condition.length > 0) || type);
      },
      isNoSearchData () {
        const searchParams = { ...this.curSystemAction, ...this.formData };
        const hasData = Object.values(searchParams).filter((item) => item !== '');
        const { condition, type } = this.curResourceData;
        return !hasData.length && (condition && !condition.length) && !type && !this.expandData['search'].isExpand;
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
      }
    },

    async created () {
      this.comMap = COM_MAP;
      this.pageConf.limit = Math.ceil(this.listHeight / 36);
      this.formatFormItemWidth();
      await this.fetchInitData();
      await this.fetchDefaultSelectData();
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
        if (this.groupList.length) {
          const { id, name } = this.groupList[0];
          this.curSelectActive = `${id}&${name}`;
        }
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
              ...params,
              ...this.formData
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
        this.pageConf.current++;
        await this.fetchGroupMemberList(false, true);
      },

      async handleRemoteTable (payload) {
        const { emptyData, pagination, searchParams } = payload;
        this.isSearchPerm = emptyData.tipType === 'search';
        const params = {
          ...searchParams,
          ...this.formData
        };
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
        if (['search'].includes(payload)) {
          this.listHeight = this.expandData[payload].isExpand
            ? window.innerHeight - 51 - 51 - 157 - 42 - 8
            : window.innerHeight - 51 - 51 - 42 - 8;
          this.pageConf = Object.assign(this.pageConf, {
            current: 1,
            totalPage: 1,
            limit: Math.ceil(this.listHeight / 36)
          });
          this.groupList = [];
          await this.fetchInitData();
          await this.fetchDefaultSelectData();
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

      handleSelectSystem (payload) {
        this.curSystemAction = { ...payload };
      },

      handleSelectResource (payload) {
        this.curResourceData = { ...payload };
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

      handleCloseTag () {

      },

      handleClearAll () {},

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
        this.isSearchPerm = false;
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyRefresh();
      },

      handleEmptyClear () {
        this.isSearchPerm = false;
        // this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyClear();
      },

      handleEmptyUserClear () {
        this.curEmptyData.tipType = '';
        this.emptyData.tipType = '';
        this.isSearchPerm = false;
        this.pageConf.current = 1;
        this.curSearchParams = {};
        this.formData.name = '';
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
      padding: 0 24px;
      .search-data-content {
        display: flex;
        align-items: center;
        .funnel-icon {
          color: #979BA5;
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
