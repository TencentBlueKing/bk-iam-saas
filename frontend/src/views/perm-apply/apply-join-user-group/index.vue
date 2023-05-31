<template>
  <smart-action class="iam-join-user-group-wrapper">
    <render-horizontal-block :label="$t(`m.permApply['选择用户组']`)" :required="true">
      <div class="user-group-table">
        <div class="search-wrapper">
          <iam-search-select
            @on-change="handleSearch"
            :data="searchData"
            :value="searchValue"
            :placeholder="$t(`m.applyEntrance['申请加入用户组搜索提示']`)"
            :quick-search-method="quickSearchMethod" />
          <div class="info">
            {{ $t(`m.info['如果以下用户组不满足您的权限需求']`) }}
            {{ $t(`m.common['，']`) }}
            {{ $t(`m.common['可以']`) }}
            <bk-button
              text
              theme="primary"
              style="font-size: 12px;"
              @click="handleToCustomApply">
              {{ $t(`m.applyEntrance['申请自定义权限']`) }}
            </bk-button>
          </div>
        </div>
        <bk-table
          ref="groupTableRef"
          size="small"
          ext-cls="user-group-table"
          :class="{ 'set-border': tableLoading }"
          :data="tableList"
          :max-height="pagination.count > 0 ? 500 : 280"
          :cell-attributes="handleCellAttributes"
          :pagination="pagination"
          @page-change="pageChange"
          @page-limit-change="limitChange"
          @select="handlerChange"
          @select-all="handlerAllChange"
          v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
        >
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
          <bk-table-column :label="$t(`m.common['所属管理空间']`)">
            <template slot-scope="{ row }">
              <span
                :class="row.role && row.role.name ? 'can-view' : ''"
                :title="row.role && row.role.name ? row.role.name : ''"
                @click.stop="handleViewDetail(row)"
              >{{ row.role ? row.role.name : '--' }}</span
              >
            </template>
          </bk-table-column>
          <template slot="empty">
            <ExceptionEmpty
              :type="emptyData.type"
              :empty-text="emptyData.text"
              :tip-text="emptyData.tip"
              :tip-type="emptyData.tipType"
              @on-clear="handleEmptyClear"
              @on-refresh="handleEmptyRefresh"
            />
          </template>
        </bk-table>
      </div>
      <p class="user-group-error" v-if="isShowGroupError">{{ $t(`m.permApply['请选择用户组']`) }}</p>
    </render-horizontal-block>
    <section>
      <!-- <template v-if="isShowMemberAdd">
                    <render-action
                        ref="memberRef"
                        :title="addMemberText"
                        :tips="addMemberTips"
                        @on-click="handleAddMember"
                        style="margin-bottom: 16px;">
                        <iam-guide
                            type="rating_manager_authorization_scope"
                            direction="left"
                            :style="{ top: '-25px', left: '440px' }"
                            :content="$t(`m.guide['授权人员范围']`)" />
                    </render-action>
                </template> -->
      <!-- <template v-else> -->
      <render-member
        :required="false"
        :users="users"
        :departments="departments"
        :is-all="isAll"
        :render-title="addMemberTitle"
        :render-text="addMemberText"
        :tips="addMemberTips"
        @on-add="handleAddMember"
        @on-delete="handleMemberDelete"
      />
      <!-- </template> -->
    </section>
    <p class="action-empty-error" v-if="isShowMemberEmptyError">{{ $t(`m.verify['可授权人员边界不可为空']`) }}</p>
    <render-horizontal-block ext-cls="expired-at-wrapper" :label="$t(`m.common['申请期限']`)" :required="true">
      <section ref="expiredAtRef">
        <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" :cur-role="curRole" />
        <p class="expired-at-error" v-if="isShowExpiredError">{{ $t(`m.permApply['请选择申请期限']`) }}</p>
      </section>
    </render-horizontal-block>
    <render-horizontal-block
      ext-cls="reason-wrapper"
      :styles="{ marginBottom: '50px' }"
      :label="$t(`m.common['理由']`)"
      :required="true"
    >
      <section ref="reasonRef">
        <bk-input
          type="textarea"
          v-model="reason"
          :maxlength="255"
          :placeholder="$t(`m.verify['请输入']`)"
          :ext-cls="isShowReasonError ? 'join-reason-error' : ''"
          @input="handleReasonInput"
          @blur="handleReasonBlur"
        >
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
      @animation-end="handleAnimationEnd"
    />

    <add-member-dialog
      :show.sync="isShowAddMemberDialog"
      :users="users"
      :departments="departments"
      :title="addMemberTitle"
      :all-checked="isAll"
      :show-limit="false"
      @on-cancel="handleCancelAdd"
      @on-sumbit="handleSubmitAdd" />

    <bk-sideslider
      :is-show.sync="isShowGradeSlider"
      :width="640"
      :title="gradeSliderTitle"
      :quick-close="true"
      @animation-end="gradeSliderTitle === ''">
      <div class="grade-memebers-content"
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
            
    <confirmDialog
      :width="600"
      :show.sync="isShowConfirmDialog"
      :title="confirmDialogTitle"
      :is-custom-style="true"
      @on-cancel="isShowConfirmDialog = false"
      @on-sumbit="isShowConfirmDialog = false"
    />
  </smart-action>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData } from '@/common/util';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import IamSearchSelect from '@/components/iam-search-select';
  // import IamGuide from '@/components/iam-guide/index.vue';
  import RenderPermSideSlider from '@/views/perm/components/render-group-perm-sideslider';
  // import RenderAction from '@/views/grading-admin/common/render-action';
  import RenderMember from '@/views/grading-admin/components/render-member';
  import AddMemberDialog from '@/views/group/components/iam-add-member';
  import ConfirmDialog from '@/components/iam-confirm-dialog/index';
  // import BkUserSelector from '@blueking/user-selector';

  export default {
    name: '',
    components: {
      // IamGuide,
      IamDeadline,
      IamSearchSelect,
      RenderPermSideSlider,
      // RenderAction,
      RenderMember,
      AddMemberDialog,
      ConfirmDialog
      // BkUserSelector
    },
    data () {
      return {
        userApi: window.BK_USER_API,
        reason: '',
        expiredAt: 15552000,
        expiredAtUse: 15552000,
        isShowReasonError: false,
        submitLoading: false,
        isShowAddMemberDialog: false,
        isShowExpiredError: false,
        isShowGroupError: false,
        isShowMemberError: false,
        isShowMemberAdd: false,
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
        users: [],
        departments: [],
        isAll: false,
        addMemberTitle: this.$t(`m.myApply['权限获得者']`),
        addMemberText: this.$t(`m.permApply['选择权限获得者']`),
        addMemberTips: this.$t(`m.permApply['可代他人申请加入用户组获取权限']`),
        queryParams: {},
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        isShowConfirmDialog: false,
        confirmDialogTitle: this.$t(`m.verify['admin无需申请权限']`)
      };
    },
    computed: {
            ...mapGetters(['user', 'externalSystemId'])
    },
    watch: {
      reason () {
        this.isShowReasonError = false;
      },
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    async created () {
      this.searchParams = this.$route.query;
      // delete this.searchParams.limit;
      // delete this.searchParams.current;
      this.curRole = this.user.role.type;
      this.users = [
        {
          'username': this.user.username,
          'name': this.user.username,
          'showRadio': true,
          'type': 'user',
          'is_selected': true
        }];
      this.searchData = [
        {
          id: 'name',
          name: this.$t(`m.userGroup['用户组名']`),
          default: true
        },
        {
          id: 'id',
          name: 'ID',
          default: true
          // validate (values, item) {
          //     const validate = (values || []).every(_ => /^(\d*)$/.test(_.name))
          //     return !validate ? '' : true
          // }
        },
        {
          id: 'description',
          name: this.$t(`m.common['描述']`),
          disabled: true
        },
        {
          id: 'system_id',
          name: this.$t(`m.common['系统包含']`),
          remoteMethod: this.handleRemoteSystem
        },
        // 管理空间
        {
          id: 'role_id',
          name: this.$t(`m.grading['管理空间']`),
          remoteMethod: this.handleGradeAdmin
        }
      ];
      this.setCurrentQueryCache(this.refreshCurrentQuery());
      const isObject = (payload) => {
        return Object.prototype.toString.call(payload) === '[object Object]';
      };
      const currentQueryCache = await this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        if (currentQueryCache.limit) {
          this.pagination = Object.assign(
            this.pagination,
            { current: Number(currentQueryCache.current), limit: Number(currentQueryCache.limit) }
          );
        }
        for (const key in currentQueryCache) {
          if (key !== 'limit' && key !== 'current') {
            const curData = currentQueryCache[key];
            const tempData = this.searchData.find((item) => item.id === key);
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
                values: [
                  {
                    id: curData,
                    name: curData
                  }
                ]
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
        await this.fetchCurUserGroup();
        await this.fetchUserGroupList();
      },

      handleToCustomApply () {
        this.$router.push({
          name: 'applyCustomPerm'
        });
      },

      handleEmptyRefresh () {
        this.resetPagination();
        this.fetchUserGroupList(true);
      },

      handleEmptyClear () {
        this.searchParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.resetPagination();
        this.fetchUserGroupList(true);
      },

      refreshCurrentQuery () {
        const params = {};
        const queryParams = {
                    ...this.searchParams,
                    ...this.$route.query,
                    ...this.queryParams
        };
        if (Object.keys(queryParams).length) {
          window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        }
        for (const key in this.searchParams) {
          const tempObj = this.searchData.find((item) => key === item.id);
          if (tempObj && tempObj.remoteMethod && typeof tempObj.remoteMethod === 'function') {
            if (this.searchList.length) {
              const tempData = this.searchList.find((item) => item.id === key);
              if (tempData) {
                params[key] = tempData.values[0];
              }
            }
          } else {
            params[key] = this.searchParams[key];
          }
        }
        this.emptyData = Object.assign(this.emptyData, { tipType: Object.keys(this.searchParams).length > 0 ? 'search' : '' });
        return {
                    ...queryParams
        };
      },

      setCurrentQueryCache (payload) {
        window.localStorage.setItem('applyGroupList', JSON.stringify(payload));
      },

      getCurrentQueryCache () {
        return JSON.parse(window.localStorage.getItem('applyGroupList'));
      },

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      },

      async fetchUserGroupList () {
        this.tableLoading = true;
        this.setCurrentQueryCache(this.refreshCurrentQuery());
        const { current, limit } = this.pagination;
        const params = {
                    ...this.searchParams,
                    limit,
                    offset: limit * (current - 1)
        };
        try {
          const { code, data } = await this.$store.dispatch('userGroup/getUserGroupList', params);
          const { count, results } = data;
          this.pagination.count = count || 0;
          this.tableList.splice(0, this.tableList.length, ...(results || []));
          this.$nextTick(() => {
            this.tableList.forEach((item) => {
              if (this.curUserGroup.includes(item.id.toString())) {
                this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, true);
                this.currentSelectList.push(item);
              }
            });
          });
          this.emptyData = formatCodeData(code, this.emptyData, count === 0);
        } catch (e) {
          console.error(e);
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'primary',
            message: e.message || e.data.msg || e.statusText
          });
        } finally {
          this.tableLoading = false;
        }
      },

      async fetchRoles (id) {
        this.sliderLoading = true;
        try {
          const res = await this.$store.dispatch('role/getGradeMembers', { id });
          this.gradeMembers = [...res.data];
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.sliderLoading = false;
        }
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

      handleAddMember () {
        this.isShowAddMemberDialog = true;
      },

      handleCancelAdd () {
        this.isShowAddMemberDialog = false;
      },

      handleMemberDelete (type, payload) {
        window.changeDialog = true;
        type === 'user' ? this.users.splice(payload, 1) : this.departments.splice(payload, 1);
        // this.isShowMemberAdd = this.users.length < 1 && this.departments.length < 1;
      },

      handleSubmitAdd (payload) {
        window.changeDialog = true;
        const { users, departments } = payload;
        this.isAll = false;
        this.users = _.cloneDeep(users);
        this.departments = _.cloneDeep(departments);
        // this.isShowMemberAdd = false;
        this.isShowAddMemberDialog = false;
        this.isShowMemberEmptyError = false;
      },

      setDefaultSelect (payload) {
        return !this.curUserGroup.includes(payload.id.toString());
      },

      resetPagination () {
        this.pagination = Object.assign(
          {},
          {
            limit: 10,
            current: 1,
            count: 0
          }
        );
      },

      // 系统包含数据
      handleRemoteSystem (value) {
        const params = {};
        if (this.externalSystemId) {
          params.hidden = false;
        }
        return this.$store.dispatch('system/getSystems', params).then(({ data }) => {
          return data.map(({ id, name }) => ({ id, name })).filter((item) => item.name.indexOf(value) > -1);
        });
      },

      // 管理空间数据
      handleGradeAdmin (value) {
        return this.$store.dispatch('role/getScopeHasUser').then(({ data }) => {
          const val = value.toLowerCase();
          return !val
            ? data.map(({ id, name }) => ({ id, name }))
            : data.map(({ id, name }) => ({ id, name })).filter(
              (item) => item.name.toLowerCase().indexOf(val) > -1);
        });
      },

      handleSearch (payload, result) {
        this.currentSelectList = [];
        this.searchParams = payload;
        this.searchList = result;
        this.emptyData.tipType = 'search';
        this.resetPagination();
        this.fetchUserGroupList(true);
      },

      handleView (payload) {
        this.curGroupName = payload.name;
        this.curGroupId = payload.id;
        this.isShowPermSideSlider = true;
      },

      handleViewDetail (payload) {
        if (payload.role && payload.role.name) {
          this.isShowGradeSlider = true;
          this.gradeSliderTitle = `${this.$t(`m.common['【']`)}${payload.role.name}${this.$t(`m.common['】']`)}${this.$t(`m.grading['管理空间']`)} ${this.$t(`m.common['成员']`)}`;
          this.fetchRoles(payload.role.id);
        }
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
        this.queryParams = Object.assign(this.queryParams, { current: page });
        this.currentSelectList = [];
        this.fetchUserGroupList(true);
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: currentLimit });
        this.queryParams = Object.assign(this.queryParams, { current: 1, limit: currentLimit });
        this.fetchUserGroupList(true);
      },

      handlerAllChange (selection) {
        this.currentSelectList = selection.filter(item => !this.curUserGroup.includes(item.id.toString()));
        this.isShowGroupError = false;
      },

      handlerChange (selection, row) {
        this.currentSelectList = selection.filter(item => !this.curUserGroup.includes(item.id.toString()));
        this.isShowGroupError = false;
      },

      async fetchCurUserGroup () {
        try {
          const { data, code } = await this.$store.dispatch('perm/getPersonalGroups', {
            page_size: 100,
            page: 1
          });
          this.curUserGroup = data.results && data.results.filter(
            (item) => item.department_id === 0).map((item) => item.id);
          this.emptyData = formatCodeData(code, this.emptyData, this.curUserGroup.length === 0);
        } catch (e) {
          this.$emit('toggle-loading', false);
          this.emptyData = formatCodeData(e.code, this.emptyData);
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

      handleReasonInput (payload) {
        this.isShowReasonError = false;
      },

      handleReasonBlur (payload) {
        if (payload === '') {
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
          const dotIndex = tempArr.findIndex((item) => item === '.');
          const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
          this.expiredAtUse = payload + nowSecond;
          return;
        }
        this.expiredAtUse = payload;
      },

      handleExpiredAt () {
        const nowTimestamp = +new Date() / 1000;
        const tempArr = String(nowTimestamp).split('');
        const dotIndex = tempArr.findIndex((item) => item === '.');
        const nowSecond = parseInt(tempArr.splice(0, dotIndex).join(''), 10);
        const expiredAt = this.expiredAtUse + nowSecond;
        return expiredAt;
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
          validateFlag = false;
          this.scrollToLocation(this.$refs.expiredAtRef);
        }
        if (this.currentSelectList.length < 1) {
          this.isShowGroupError = true;
          validateFlag = false;
        }
        if (!validateFlag) {
          return;
        }
        this.submitLoading = true;
        if (this.expiredAtUse === 15552000) {
          this.expiredAtUse = this.handleExpiredAt();
        }
        const subjects = [];
        // if (this.isAll) {
        //     subjects.push({
        //         id: '*',
        //         type: '*'
        //     });
        // } else {
        this.users.forEach(item => {
          subjects.push({
            type: 'user',
            id: item.username
          });
        });
        this.departments.forEach(item => {
          subjects.push({
            type: 'department',
            id: item.id
          });
        });
        // }
        const params = {
          expired_at: this.expiredAtUse,
          reason: this.reason,
          groups: this.currentSelectList.map(({ id, name, description }) => ({ id, name, description })),
          applicants: subjects
        };
        try {
          await this.$store.dispatch('permApply/applyJoinGroup', params);
          this.messageSuccess(this.$t(`m.info['申请已提交']`), 1000);
          this.$router.push({
            name: 'apply'
          });
        } catch (e) {
          console.error(e);
          if (['admin'].includes(this.user.username)) {
            this.isShowConfirmDialog = true;
          } else {
            this.bkMessageInstance = this.$bkMessage({
              limit: 1,
              theme: 'error',
              message: e.message || e.data.msg || e.statusText,
              ellipsisLine: 2,
              ellipsisCopy: true
            });
          }
        } finally {
          this.submitLoading = false;
        }
      },

      handleCancel () {
        this.$router.push({
          name: 'permApply'
        });
      }
    }
  };
</script>
<style lang="postcss">
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
        .perm-recipient-error,
        .expired-at-error,
        .reason-empty-wrapper {
            margin-top: 5px;
            font-size: 12px;
            color: #ff4d4d;
        }
        .is-member-empty-cls {
            .user-selector-container {
                border-color: #ff4d4d;
            }
        }
    }
    .grade-memebers-content {
        padding: 20px;
        height: calc(100vh - 61px);
        .member-item {
            position: relative;
            display: inline-block;
            margin: 0 6px 6px 0;
            padding: 0 10px;
            line-height: 22px;
            background: #f5f6fa;
            border: 1px solid #dcdee5;
            border-radius: 2px;
            font-size: 12px;
            .member-name {
                display: inline-block;
                max-width: 200px;
                line-height: 17px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                vertical-align: text-top;
                .count {
                    color: #c4c6cc;
                }
            }
        }
        .info {
            margin-top: 5px;
            color: #c4c6cc;
            font-size: 14px;
        }
    }
</style>
