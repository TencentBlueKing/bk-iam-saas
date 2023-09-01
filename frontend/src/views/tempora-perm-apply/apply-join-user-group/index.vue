<template>
  <smart-action class="iam-join-user-group-wrapper">
    <render-horizontal-block :label="$t(`m.permApply['选择用户组']`)" :required="true">
      <div class="user-group-table">
        <div class="serch-wrapper">
          <iam-search-select
            @on-change="handleSearch"
            :data="searchData"
            :value="searchValue"
            :placeholder="$t(`m.applyEntrance['申请加入用户组搜索提示']`)"
            :quick-search-method="quickSearchMethod"
          />
          <div class="info">
            {{ $t(`m.info['如果以下用户组不满足您的权限需求']`) }}{{ $t(`m.common['，']`) }}
            {{ $t(`m.common['可以']`) }}
            <bk-button text theme="primary" style="font-size: 12px" @click="handleToCustomApply">
              {{ $t(`m.applyEntrance['申请自定义权限']`) }}
            </bk-button>
          </div>
        </div>
        <bk-table
          ref="groupTableRef"
          :data="tableList"
          size="small"
          :class="{ 'set-border': tableLoading }"
          ext-cls="user-group-table"
          :pagination="pagination"
          :cell-attributes="handleCellAttributes"
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
              <span :title="row.description || ''">
                {{ row.description || '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.grading['管理空间']`)">
            <template slot-scope="{ row }">
              <span
                :title="row.role && row.role.name ? row.role.name : ''"
              >
                {{ row.role ? row.role.name : '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.levelSpace['管理员']`)" width="300">
            <template slot-scope="{ row, $index }">
              <iam-edit-member-selector
                mode="detail"
                field="role_members"
                width="300"
                :placeholder="$t(`m.verify['请输入']`)"
                :value="row.role_members"
                :index="$index"
              />
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
    <render-horizontal-block ext-cls="expired-at-wrapper" :label="$t(`m.common['申请期限']`)" :required="true">
      <section ref="expiredAtRef">
        <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" :cur-role="curRole" />
        <p class="expired-at-error" v-if="isShowExpiredError">{{ $t(`m.permApply['请选择申请期限']`) }}</p>
      </section>
    </render-horizontal-block>
    <render-horizontal-block ext-cls="reason-wrapper" :label="$t(`m.common['理由']`)" :required="true">
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

    <render-perm-sideslider
      :show="isShowPermSidesilder"
      :name="curGroupName"
      :group-id="curGroupId"
      :show-member="false"
      @animation-end="handleAnimationEnd"
    />
  </smart-action>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { formatCodeData } from '@/common/util';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import IamSearchSelect from '@/components/iam-search-select';
  import RenderPermSideslider from '../../perm/components/render-group-perm-sideslider';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';

  export default {
    name: '',
    components: {
      IamDeadline,
      IamSearchSelect,
      RenderPermSideslider,
      IamEditMemberSelector
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
        isShowPermSidesilder: false,
        curGroupName: '',
        curGroupId: '',
        sliderLoading: false,
        curRole: '',
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId'])
    },
    watch: {
      reason (value) {
        this.isShowReasonError = false;
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
      this.searchData = [
        {
          id: 'id',
          name: 'ID'
        // validate (values, item) {
        //     const validate = (values || []).every(_ => /^(\d*)$/.test(_.name))
        //     return !validate ? '' : true
        // }
        },
        {
          id: 'name',
          name: this.$t(`m.userGroup['用户组名']`),
          default: true
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
      const currentQueryCache = this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        if (currentQueryCache.limit) {
          this.pagination.limit = currentQueryCache.limit;
          this.pagination.current = currentQueryCache.current;
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
        const { limit, current } = this.pagination;
        const params = {};
        const queryParams = {
          limit,
          current,
        ...this.searchParams
        };
        window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        for (const key in this.searchParams) {
          const tempObj = this.searchData.find((item) => key === item.id);
          if (tempObj && tempObj.remoteMethod && typeof tempObj.remoteMethod === 'function') {
            if (this.searchList.length > 0) {
              const tempData = this.searchList.find((item) => item.id === key);
              params[key] = tempData.values[0];
            }
          } else {
            params[key] = this.searchParams[key];
          }
        }
        this.emptyData = Object.assign(this.emptyData, {
          tipType: Object.keys(this.searchParams).length > 0 ? 'search' : ''
        });
        return {
        ...params,
        limit,
        current
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
        const params = {
        ...this.searchParams,
        limit: this.pagination.limit,
        offset: this.pagination.limit * (this.pagination.current - 1)
        };
        try {
          const { code, data } = await this.$store.dispatch('userGroup/getUserGroupList', params);
          this.pagination.count = data.count || 0;
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.$nextTick(() => {
            this.tableList.forEach((item) => {
              if (item.role_members && item.role_members.length) {
                item.role_members = item.role_members.map(v => {
                  return {
                    username: v,
                    readonly: false
                  };
                });
              }
              if (this.curUserGroup.includes(item.id.toString())) {
                this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, true);
              }
            });
          });
          this.emptyData = formatCodeData(code, this.emptyData, data.count === 0);
        } catch (e) {
          console.error(e);
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
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
            : data.map(({ id, name }) => ({ id, name })).filter((item) => item.name.toLowerCase().indexOf(val) > -1);
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
        this.isShowPermSidesilder = true;
      },

      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSidesilder = false;
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.currentSelectList = [];
        this.fetchUserGroupList(true);
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.fetchUserGroupList(true);
      },

      handlerAllChange (selection) {
        this.currentSelectList = selection.filter((item) => !this.curUserGroup.includes(item.id.toString()));
        this.isShowGroupError = false;
      },

      handlerChange (selection, row) {
        this.currentSelectList = selection.filter((item) => !this.curUserGroup.includes(item.id.toString()));
        this.isShowGroupError = false;
      },

      async fetchCurUserGroup () {
        try {
          const { code, data } = await this.$store.dispatch('perm/getPersonalGroups', {
            page_size: 100,
            page: 1
          });
          this.curUserGroup = data.results.filter((item) => item.department_id === 0).map((item) => item.id);
          this.emptyData = formatCodeData(code, this.emptyData, this.curUserGroup.length === 0);
        } catch (e) {
          this.$emit('toggle-loading', false);
          this.emptyData = formatCodeData(e.code, this.emptyData);
          console.error(e);
          this.messageAdvancedError(e);
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
        if (this.reason === '') {
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
          groups: this.currentSelectList.map(({ id, name, description }) => ({ id, name, description }))
        };
        try {
          await this.$store.dispatch('permApply/applyJoinGroup', params);
          this.messageSuccess(this.$t(`m.info['申请已提交']`), 3000);
          this.$router.push({
            name: 'apply'
          });
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
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
  .serch-wrapper {
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
