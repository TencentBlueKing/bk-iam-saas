<template>
  <smart-action class="iam-join-user-group-wrapper">
    <render-horizontal-block :label="$t(`m.permApply['项目']`)" :required="true">
      <bk-select
        v-model="roleId"
        style="width: 250px;"
        ext-cls="select-custom"
        ext-popover-cls="select-popover-custom"
        :placeholder="$t(`m.permApply['请选择项目']`)"
        :searchable="true"
        :clearable="false"
        :enable-scroll-load="enableScrollLoad"
        :remote-method="handleRemoteMethod"
        :scroll-loading="scrollLoadingOptions"
        @scroll-end="handleScrollToBottom"
        @change="handleChangeRole"
        @toggle="handleToggleProject"
      >
        <bk-option
          v-for="option in projectList"
          :key="option.id"
          :id="option.id"
          :name="option.name">
        </bk-option>
      </bk-select>
      <p class="expired-at-error" v-if="isShowProjectError">{{ $t(`m.permApply['请选择项目']`) }}</p>
    </render-horizontal-block>
    <render-horizontal-block :label="$t(`m.permApply['选择用户组']`)" :required="true">
      <div class="user-group-table">
        <div class="search-wrapper">
          <iam-search-select
            @on-change="handleSearch"
            :data="searchData"
            :value="searchValue"
            :placeholder="$t(`m.applyEntrance['请输入条件搜索用户组']`)"
            :quick-search-method="quickSearchMethod"
            clearable />
        </div>
        <bk-table
          ref="groupTableRef"
          size="small"
          ext-cls="user-group-table"
          :data="tableList"
          :max-height="500"
          :class="{ 'set-border': tableLoading }"
          :pagination="pagination"
          :cell-attributes="handleCellAttributes"
          @page-change="pageChange"
          @page-limit-change="limitChange"
          @select="handlerChange"
          @select-all="handlerAllChange"
          v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
          <bk-table-column type="selection" align="center" :selectable="setDefaultSelect"></bk-table-column>
          <bk-table-column :label="$t(`m.userGroup['用户组名']`)">
            <template slot-scope="{ row }">
              <span class="user-group-name" :title="row.name" @click="handleView(row)">
                {{ row.name }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.common['描述']`)">
            <template slot-scope="{ row }">
              <span :title="row.description !== '' ? row.description : ''">
                {{ row.description || '--' }}
              </span>
            </template>
          </bk-table-column>
        </bk-table>
      </div>
      <p class="user-group-error" v-if="isShowGroupError">{{ $t(`m.permApply['请选择用户组']`) }}</p>
    </render-horizontal-block>
    <render-horizontal-block :label="$t(`m.permApply['已选用户组']`)" :required="true">
      <div>
        <bk-tag
          closable
          v-for="tag in currentSelectList"
          :key="tag"
          @close="handleCloseTag(tag)">
          {{tag.name}}
        </bk-tag>
        <bk-button
          v-if="currentSelectList.length"
          style="margin-left: 10px"
          text
          @click="handleRemoveChecked"
        >
          {{ $t(`m.permApply['清空选择']`)}}
        </bk-button>
      </div>
      <p class="user-group-error" v-if="isShowGroupError">{{ $t(`m.permApply['请选择用户组']`) }}</p>
    </render-horizontal-block>
    <render-horizontal-block ext-cls="expired-at-wrapper" :label="$t(`m.common['申请期限']`)" :required="true">
      <section ref="expiredAtRef">
        <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" :cur-role="curRole" />
        <p class="expired-at-error" v-if="isShowExpiredError">{{ $t(`m.permApply['请选择申请期限']`) }}</p>
      </section>
    </render-horizontal-block>
    <render-horizontal-block
      ext-cls="reason-wrapper"
      :label="$t(`m.common['理由']`)"
      :required="true">
      <section ref="reasonRef">
        <bk-input
          type="textarea"
          v-model="reason"
          :maxlength="255"
          :placeholder="$t(`m.verify['请输入']`)"
          :ext-cls="isShowReasonError ? 'join-reason-error' : ''"
          @input="handleReasonInput"
          @blur="handleReasonBlur">
        </bk-input>
        <p class="reason-empty-wrapper" v-if="isShowReasonError">{{ $t(`m.verify['请输入理由']`) }}</p>
      </section>
    </render-horizontal-block>
    <div slot="action">
      <bk-button theme="primary" :loading="submitLoading" @click="handleSubmit">
        {{ $t(`m.common['提交']`) }}
      </bk-button>
      <!-- <bk-button style="margin-left: 10px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button> -->
    </div>

    <render-perm-side-slider
      :show="isShowPermSideSlider"
      :name="curGroupName"
      :group-id="curGroupId"
      :show-member="false"
      @animation-end="handleAnimationEnd" />

    <bk-sideslider
      :is-show.sync="isShowGradeSlider"
      :width="640"
      :title="gradeSliderTitle"
      :quick-close="true"
      @animation-end="gradeSliderTitle === ''">
      <div class="grade-members-content"
        slot="content"
        v-bkloading="{ isLoading: sliderLoading, opacity: 1 }">
        <template v-if="!sliderLoading">
          <div v-for="(item, index) in gradeMembers"
            :key="index"
            class="member-item">
            <span class="member-name">
              {{ item }}
            </span>
          </div>
          <p class="info">{{ $t(`m.info['管理空间成员提示']`) }}</p>
        </template>
      </div>
    </bk-sideslider>
  </smart-action>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { sleep } from '@/common/util';
  import { buildURLParams } from '@/common/url';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import Policy from '@/model/policy';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import IamSearchSelect from '@/components/iam-search-select';
  import RenderPermSideSlider from '../../perm/components/render-group-perm-sideslider';
  export default {
    name: '',
    components: {
      IamDeadline,
      IamSearchSelect,
      RenderPermSideSlider
    },
    data () {
      return {
        reason: '',
        expiredAt: 15552000,
        expiredAtUse: 15552000,
        isShowReasonError: false,
        submitLoading: false,
        isShowExpiredError: false,
        isShowGroupError: false,
        tableList: [],
        currentSelectList: [],
        curUserGroup: [],
        searchParams: {},
        searchList: [],
        searchValue: [],
        tableLoading: false,
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        isShowPermSideSlider: false,
        curGroupName: '',
        curGroupId: '',
        isShowGradeSlider: false,
        sliderLoading: false,
        gradeMembers: [],
        gradeSliderTitle: '',
        curRole: '',
        isShowProjectError: false,
        projectList: [],
        projectPagination: {
          current: 1,
          limit: 30,
          total: 0
        },
        projectKeyWord: '',
        enableScrollLoad: true,
        scrollLoadingOptions: {
          size: 'mini',
          isLoading: false
        },
        system_id: '',
        roleId: '',
        processesList: [],
        resourceActionData: [],
        initSearchData: [
          {
            id: 'name',
            name: this.$t(`m.userGroup['用户组名']`),
            default: true
          },
          {
            id: 'system_id',
            name: this.$t(`m.permApply['选择系统']`),
            remoteMethod: this.handleRemoteSystem
          }
        ],
        searchData: []
      };
    },
    computed: {
            ...mapGetters(['user', 'externalSystemId'])
    },
    watch: {
      reason (value) {
        if (!value) {
          this.isShowReasonError = false;
        }
      },
      '$route': {
        handler (value) {
          if (Object.keys(value.query).length) {
            const { system_id: systemId, role_id: roleId } = value.query;
            this.systemId = systemId;
            this.roleId = +roleId;
          }
        },
        immediate: true
      },
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    created () {
      this.searchParams = this.$route.query;
      delete this.searchParams.limit;
      delete this.searchParams.current;
      this.curRole = this.user.role.type;
      this.searchData = _.cloneDeep(this.initSearchData);
      this.setCurrentQueryCache(this.refreshCurrentQuery());
      const isObject = payload => {
        return Object.prototype.toString.call(payload) === '[object Object]';
      };
      const currentQueryCache = this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        const { current, limit } = this.pagination;
        if (limit) {
          this.pagination = Object.assign(this.pagination, { current, limit });
        }
        for (const key in currentQueryCache) {
          if (key !== 'limit' && key !== 'current') {
            const curData = currentQueryCache[key];
            const tempData = this.searchData.find(item => item.id === key);
            if (isObject(curData)) {
              if (tempData) {
                this.searchValue.push({
                  id: key,
                  name: tempData.name,
                  values: [curData]
                });
                this.searchList.push(..._.cloneDeep(this.searchValue));
                this.searchParams[key] = curData.id;
              }
            } else if (tempData) {
              this.searchValue.push({
                id: key,
                name: tempData.name,
                values: [{
                  id: curData,
                  name: curData
                }]
              });
              this.searchList.push(..._.cloneDeep(this.searchValue));
              this.searchParams[key] = curData;
            } else {
              this.searchParams[key] = curData;
            }
          }
        }
      }
    },
    methods: {
      /**
       * 获取页面数据
       */
      async fetchPageData () {
        await Promise.all([this.fetchProjectData(), this.fetchUserGroupList(), this.fetchCurUserGroup()]);
      },

      handleToCustomApply () {
        this.$router.push({
          name: 'applyCustomPerm'
        });
      },

      refreshCurrentQuery () {
        const { limit, current } = this.pagination;
        const params = {};
        const queryParams = {
          limit,
          current,
          system_id: this.systemId,
          role_id: this.roleId,
                    ...this.searchParams
        };
        window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        for (const key in this.searchParams) {
          const tempObj = this.searchData.find(item => key === item.id);
          if (tempObj && tempObj.remoteMethod && typeof tempObj.remoteMethod === 'function') {
            if (this.searchList.length) {
              const tempData = this.searchList.find(item => item.id === key);
              params[key] = tempData.values[0];
            }
          } else {
            params[key] = this.searchParams[key];
          }
        }
        return {
                    ...params,
                    limit,
                    current
        };
      },

      setCurrentQueryCache (payload) {
        window.localStorage.setItem('roleGroupList', JSON.stringify(payload));
      },

      getCurrentQueryCache () {
        return JSON.parse(window.localStorage.getItem('roleGroupList'));
      },

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      },

      async handleScrollToBottom () {
        const { current, limit, total } = this.projectPagination;
        this.enableScrollLoad = true;
        if (Math.floor((total + limit - 1) / limit) <= current) {
          this.enableScrollLoad = false;
        } else {
          this.scrollLoadingOptions.isLoading = true;
          this.projectPagination.current++;
          await this.fetchProjectData();
          sleep(1000).then(() => {
            this.scrollLoadingOptions.isLoading = false;
          });
        }
      },

      async handleChangeRole (id) {
        this.currentSelectList = [];
        this.roleId = id;
        this.$store.commit('updateCurRoleId', id);
        this.$store.commit('updateIdentity', { id });
        this.$store.commit('updateNavId', id);
        await this.$store.dispatch('role/updateCurrentRole', { id });
        await this.fetchUserGroupList();
        this.resetLocalStorage();
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
      },

      handleToggleProject (value) {
        if (value) {
          this.projectPagination = Object.assign(this.projectPagination, { current: 1 });
          this.fetchProjectData();
        }
      },

      handleCloseTag (value) {
        const index = this.currentSelectList.findIndex(item => item.id === value.id);
        this.currentSelectList.splice(index, 1);
        this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(value, false);
      },

      handleRemoveChecked () {
        this.currentSelectList = [];
        this.$refs.groupTableRef && this.$refs.groupTableRef.clearSelection();
      },
         
      async handleRecursionFunc () {
        try {
          const { data } = await this.$store.dispatch('approvalProcess/getActionGroups', { system_id: this.systemId });
          data && data.forEach(data => {
            if (data.actions && data.actions.length) {
              data.actions.forEach(e => {
                this.resourceActionData.push(e);
              });
            }
            if (data.sub_groups && data.sub_groups.length) {
              data.sub_groups.forEach(item => {
                if (item.actions && item.actions.length) {
                  item.actions.forEach(e => {
                    this.resourceActionData.push(e);
                  });
                }
              });
            }
          });
          this.resourceActionData = this.resourceActionData.filter(
            (e, index, self) => self.indexOf(e) === index);
          this.resourceActionData.forEach(item => {
            if (!item.resource_groups || !item.resource_groups.length) {
              item.resource_groups = item.related_resource_types.length ? [{ id: '', related_resource_types: item.related_resource_types }] : [];
            }
            this.processesList.push(new Policy({ ...item, tag: 'add' }, 'custom'));
          });
          return this.processesList;
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      async handleSearch (payload, result) {
        console.log(payload, result, '选择参数');
        this.searchData = [];
        this.currentSelectList = [];
        this.searchParams = payload;
        this.searchList = result;
        if (result.length === 0) {
          this.searchData.push(..._.cloneDeep(this.initSearchData));
        }
        if (payload.system_id) {
          this.systemId = payload.system_id;
          this.resourceActionData = [];
          this.processesList = [];
          if (!this.systemId) return;
          this.resourceTypeData = { isEmpty: true };
          const searchData = [
            {
              id: 'action_id',
              name: this.$t(`m.permApply['选择操作']`),
              remoteMethod: this.handleRecursionFunc
            }
          ];
          this.searchData.push(..._.cloneDeep(searchData));
          await this.handleRecursionFunc();
        }
        this.resetPagination();
        await this.fetchUserGroupList();
      },

      async handleRemoteMethod (value) {
        this.scrollLoadingOptions.isLoading = false;
        this.projectKeyWord = value;
        this.projectList = [];
        this.projectPagination = Object.assign(this.projectPagination, { current: 1, total: 0 });
        await this.fetchProjectData();
      },

      async fetchRoles (id) {
        this.sliderLoading = true;
        try {
          const res = await this.$store.dispatch('role/getGradeMembers', { id });
          this.gradeMembers = [...res.data];
        } catch (e) {
          console.error(e);
          this.fetchErrorMsg(e);
        } finally {
          this.sliderLoading = false;
        }
      },
            
      async fetchCurUserGroup () {
        try {
          const res = await this.$store.dispatch('perm/getPersonalGroups', {
            page_size: 100,
            page: 1
          });
          this.curUserGroup = res.data.results.filter(item => item.department_id === 0).map(item => item.id);
        } catch (e) {
          this.$emit('toggle-loading', false);
          console.error(e);
          this.fetchErrorMsg(e);
        }
      },

      async fetchProjectData () {
        const { current, limit } = this.projectPagination;
        const params = {
          system_id: this.systemId,
          page: current,
          page_size: limit,
          name: this.projectKeyWord
        };
        try {
          const { data } = await this.$store.dispatch('perm/getPersonalProject', params);
          this.projectPagination.total = data.count;
          this.projectList = [...this.projectList, ...data.results];
        } catch (e) {
          console.error(e);
          this.fetchErrorMsg(e);
        }
      },

      async fetchUserGroupList () {
        if (this.systemId && this.roleId) {
          const { current, limit } = this.pagination;
          const params = {
            page_size: limit,
            page: current,
                        ...this.searchParams,
            system_id: this.systemId,
            role_id: this.roleId
          };
          try {
            this.tableLoading = true;
            this.setCurrentQueryCache(this.refreshCurrentQuery());
            const res = await this.$store.dispatch('perm/getRoleGroups', params);
            this.pagination.count = res.data.count;
            this.tableList.splice(0, this.tableList.length, ...(res.data.results || []));
            this.$nextTick(() => {
              this.tableList.forEach(item => {
                if (this.curUserGroup.includes(item.id.toString())) {
                  this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, true);
                }
              });
            });
          } catch (e) {
            console.error(e);
            this.messageAdvancedError(e);
          } finally {
            this.tableLoading = false;
          }
        }
      },

      // 系统包含数据
      async handleRemoteSystem (value) {
        const params = {};
        if (this.externalSystemId) {
          params.hidden = false;
        }
        const { code, data } = await this.$store.dispatch('system/getSystems', params);
        if (code === 0) {
          return data.map(({ id, name }) => ({ id, name })).filter(item => item.name.indexOf(value) > -1);
        }
      },

      fetchErrorMsg (payload) {
        this.messageAdvancedError(payload);
      },

      handleCellAttributes ({ rowIndex, cellIndex, row, column }) {
        if (cellIndex === 0) {
          if (this.curUserGroup.includes(row.id.toString())) {
            return {
              title: this.$t(`m.info['你已加入该组']`)
            };
          }
          return {};
        }
        return {};
      },

      setDefaultSelect (payload) {
        return !this.curUserGroup.includes(payload.id.toString());
      },

      resetPagination () {
        this.pagination = Object.assign({}, {
          limit: 10,
          current: 1,
          count: 0
        });
      },

      handleView (payload) {
        this.curGroupName = payload.name;
        this.curGroupId = payload.id;
        this.isShowPermSideSlider = true;
      },

      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSideSlider = false;
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.currentSelectList = [];
        this.fetchUserGroupList();
      },

      limitChange (limit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit });
        this.fetchUserGroupList();
      },

      handlerAllChange (selection) {
        this.currentSelectList = selection.filter(item => !this.curUserGroup.includes(item.id.toString()));
        this.isShowGroupError = false;
      },

      handlerChange (selection) {
        this.currentSelectList = selection.filter(item => !this.curUserGroup.includes(item.id.toString()));
        this.isShowGroupError = false;
      },

      handleReasonInput (payload) {
        this.isShowReasonError = false;
      },

      handleReasonBlur (payload) {
        if (!payload) {
          this.isShowReasonError = true;
        }
      },

      handleDeadlineChange (payload) {
        if (payload) {
          this.isShowExpiredError = false;
        }
        if (payload !== PERMANENT_TIMESTAMP && payload) {
          const nowTimestamp = +new Date() / 1000;
          const tempArr = String(nowTimestamp).split('');
          const dotIndex = tempArr.findIndex(item => item === '.');
          const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
          this.expiredAtUse = payload + nowSecond;
          return;
        }
        this.expiredAtUse = payload;
      },

      handleExpiredAt () {
        const nowTimestamp = +new Date() / 1000;
        const tempArr = String(nowTimestamp).split('');
        const dotIndex = tempArr.findIndex(item => item === '.');
        const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
        const expiredAt = this.expiredAtUse + nowSecond;
        return expiredAt;
      },

      handleCancel () {
        this.$router.push({
          name: 'permApply'
        });
      },
            
      async handleSubmit () {
        let validateFlag = true;
        if (!this.reason) {
          this.isShowReasonError = true;
          validateFlag = false;
          this.scrollToLocation(this.$refs.reasonRef);
        }
        if (this.expiredAtUse === 0) {
          this.isShowExpiredError = true;
          this.scrollToLocation(this.$refs.expiredAtRef);
          validateFlag = false;
        }
        if (this.currentSelectList.length < 1) {
          this.isShowGroupError = true;
          validateFlag = false;
        }
        if (!this.roleId) {
          this.isShowProjectError = true;
          validateFlag = false;
        }
        if (!validateFlag) {
          return;
        }
        this.submitLoading = true;
        if (this.expiredAtUse === 15552000) {
          this.expiredAtUse = this.handleExpiredAt();
        }
        const params = {
          expired_at: this.expiredAtUse,
          reason: this.reason,
          source_system_id: this.systemId,
          groups: this.currentSelectList.map(({ id, name, description }) => ({ id, name, description }))
        };
        try {
          await this.$store.dispatch('permApply/applyJoinGroup', params);
          this.messageSuccess(this.$t(`m.info['申请已提交']`), 3000);
          // this.$router.push({
          //     name: 'apply'
          // });
        } catch (e) {
          console.error(e);
          this.fetchErrorMsg(e);
        } finally {
          this.submitLoading = false;
        }
      }
    }
  };
</script>
<style lang="postcss">
@import '@/css/mixins/manage-members-detail-slidesider.css';
.iam-join-user-group-wrapper {
    .user-group-table {
        .user-group-table {
            margin-top: 10px;
            border-right: none;
            border-bottom: none;
            &.set-border {
                border-right: 1px solid #dfe0e5;
                border-bottom: 1px solid #dfe0e5;
            }
            .user-group-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
        }
        .can-view {
            color: #3a84ff;
            cursor: pointer;
            &:hover {
                color: #699df4;
            }
        }
    }
    .search-wrapper {
        .info {
            line-height: 30px;
            font-size: 12px;
        }
    }
    .expired-at-wrapper {
        margin-top: 16px;
    }
    .reason-wrapper {
        margin-top: 16px;
        .join-reason-error {
            .bk-textarea-wrapper {
                border-color: #ff5656;
            }
        }
    }
    .user-group-error,
    .expired-at-error,
    .reason-empty-wrapper {
        margin-top: 5px;
        font-size: 12px;
        color: #ff4d4d;
    }
}
</style>
