<template>
  <div class="iam-audit-wrapper">
    <render-search>
      <bk-date-picker
        v-model="initDateTime"
        placeholder=""
        type="month"
        :clearable="false"
        @change="handleDateChange">
      </bk-date-picker>
      <div class="audit-search-select">
        <iam-search-select
          ref="iamSearchSelect"
          style="width: 380px;"
          :data="searchData"
          :value="searchValue"
          @on-change="handleSearch" />
      </div>
    </render-search>
    <bk-table
      :data="tableList"
      size="small"
      :max-height="tableHeight"
      :class="{ 'set-border': tableLoading }"
      ext-cls="audit-table"
      :pagination="pagination"
      ref="tableRef"
      row-key="id"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
      @page-change="pageChange"
      @page-limit-change="limitChange"
      @expand-change="handleExpandChange">
      <bk-table-column type="expand" width="30">
        <template slot-scope="{ row }">
          <section class="audit-detail-wrapper" v-bkloading="{ isLoading: row.loading, opacity: 1 }">
            <template v-if="noDetailType.includes(row.type) || row.type === 'role.group.renew'">
              <!-- <div class="empty-wrapper"> -->
              <ExceptionEmpty />
              <!-- </div> -->
            </template>
            <template v-if="onlyDescriptionType.includes(row.detail.type)">
              <section v-if="!row.loading">
                <p class="description single-hide" :title="row.detail.description">
                  {{ row.detail.description || '--' }}
                </p>
              </section>
            </template>
            <template v-if="onlySubType.includes(row.detail.type)">
              <bk-table
                v-if="!row.loading"
                :data="row.detail.sub_objects"
                ext-cls="audit-detail-table"
                :outer-border="false"
                :header-border="false"
                :header-cell-style="{ background: '#f5f6fa', borderRight: 'none' }">
                <bk-table-column :label="$t(`m.common['类型']`)">
                  <template slot-scope="props">
                    <span>{{ objectMap[props.row.type] || props.row.type }}</span>
                  </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.audit['实例']`)">
                  <template slot-scope="props">
                    <span>{{ props.row.name }}</span>
                  </template>
                </bk-table-column>
                <template slot="empty">
                  <ExceptionEmpty />
                </template>
              </bk-table>
            </template>
            <template v-if="deType.includes(row.detail.type)">
              <section v-if="!row.loading">
                <p class="description">{{ row.detail.description }}</p>
                <p>{{ $t(`m.audit['版本号']`) }}：{{ row.detail.extra_info.version }}</p>
              </section>
            </template>
            <template v-if="dsType.includes(row.detail.type)">
              <bk-table
                v-if="!row.loading"
                :data="row.detail.sub_objects"
                ext-cls="audit-detail-table"
                :outer-border="false"
                :header-border="false"
                :header-cell-style="{ background: '#f5f6fa', borderRight: 'none' }">
                <bk-table-column prop="name" :label="$t(`m.audit['对象实例']`)">
                  <template slot-scope="props">
                    <span :title="objectMap[props.row.type] || props.row.type">
                      {{ objectMap[props.row.type] || props.row.type }}
                    </span>
                  </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.audit['操作对象']`)">
                  <template slot-scope="props">
                    <span :title="props.row.name">{{ props.row.name }}</span>
                  </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.common['描述']`)">
                  <template slot-scope="props">
                    <span :title="props.row.description">{{ props.row.description || '--' }}</span>
                  </template>
                </bk-table-column>
                <template slot="empty">
                  <ExceptionEmpty />
                </template>
              </bk-table>
            </template>
            <template v-if="seType.includes(row.detail.type)">
              <bk-table
                v-if="!row.loading"
                :data="row.detail.sub_objects"
                ext-cls="audit-detail-table"
                :outer-border="false"
                :header-border="false"
                :header-cell-style="{ background: '#f5f6fa', borderRight: 'none' }">
                <bk-table-column prop="name" :label="$t(`m.common['类型']`)">>
                  <template slot-scope="props">
                    <span>{{ objectMap[props.row.type] || props.row.type }}</span>
                  </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.audit['实例']`)">
                  <template slot-scope="props">
                    <span :title="props.row.name">{{ props.row.name }}</span>
                  </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.audit['版本号']`)">
                  <template slot-scope="props">
                    <span>{{ props.row.version || '--' }}</span>
                  </template>
                </bk-table-column>
                <template slot="empty">
                  <ExceptionEmpty />
                </template>
              </bk-table>
            </template>
            <template v-if="onlyExtraInfoType.includes(row.detail.type)">
              <!-- eslint-disable max-len -->
              <template v-if="row.detail.type !== 'role.group.renew' && row.detail.type !== 'template.version.sync'">
                <render-detail-table :actions="row.detail.extra_info.policies" />
              </template>
              <template v-if="row.detail.type === 'template.version.sync'">
                <p>{{ $t(`m.audit['版本号']`) }}：{{ row.detail.extra_info.version }}</p>
              </template>
            </template>
            <template v-if="onlyRoleType.includes(row.detail.type)">
              <p>{{ $t(`m.audit['管理空间']`) }}：{{ row.detail.role_name }}</p>
            </template>
          </section>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['时间']`)" width="180">
        <template slot-scope="{ row }">
          <span :title="row.time">{{ row.time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['操作类型']`)">
        <template slot-scope="{ row }">
          <span :title="typeMap[row.type] || row.type">{{ typeMap[row.type] || row.type }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['对象及类型']`)">
        <template slot-scope="{ row }">
          <span :title="`${objectMap[row.object_type] || row.object_type}：${row.object_name}`">
            {{ objectMap[row.object_type] || row.object_type }}：{{ row.object_name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['操作者']`)">
        <template slot-scope="{ row }">
          <span :title="row.username">{{ row.username }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['操作来源']`)">
        <template slot-scope="{ row }">
          <span :title="sourceMap[row.source_type] || row.source_type">
            {{ sourceMap[row.source_type] || row.source_type }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['操作状态']`)" width="150">
        <template slot-scope="{ row }">
          <render-status :status="row.status" />
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
</template>
<script>
  import _ from 'lodash';
  import IamSearchSelect from '@/components/iam-search-select';
  import { fuzzyRtxSearch } from '@/common/rtx';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData, getWindowHeight } from '@/common/util';
  import RenderStatus from './components/render-status-item';
  import renderDetailTable from './components/render-instance-detail-table';

  const getDate = payload => {
    return payload.split('-').join('');
  };

  const getFormatDate = payload => {
    const now = new Date(payload);
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    return `${year}-${month < 10 ? '0' + month.toString() : month}`;
  };

  // 只显示角色名称的审计类型
  const ONLY_ROLE_TYPE = [
    'template.create'
  ];

  // 没有详情的审计类型
  const NO_DETAIL_TYPE = [
    'group.create',
    'group.delete',
    // 'template.create',
    'template.update',
    'role.create'
  ];

  // 只有描述字段的审计类型
  const ONLY_DESCRIPTION_TYPE = [
    'group.update',
    'role.update',
    'role.member.policy.create',
    'role.member.policy.delete',
    'approval.global.update'
  ];

  // 只有子对象的审计类型
  const ONLY_SUB_TYPE = [
    'group.template.create',
    'group.member.create',
    'group.member.delete',
    'group.member.renew',
    'group.transfer',
    'user.group.delete',
    'department.group.delete',
    'user.role.delete',
    'role.member.create',
    'role.member.delete',
    'role.member.update',
    'role.commonaction.create',
    'role.commonaction.delete'
  ];

  // 只有附加信息的审计类型
  const ONLY_EXTRA_INFO_TYPE = [
    'group.policy.create',
    'group.policy.delete',
    'group.policy.update',
    'user.policy.delete',
    'user.policy.create',
    'user.policy.update',
    'role.group.renew',
    'template.version.sync'
  ];

  // 既有 description 又有 extra_info
  const DE_TYPR = ['template.update'];

  // 既有 sub_objects 又有 extra_info
  const SE_TYPE = [
    'template.member.create',
    'template.member.delete',
    'template.version.update'
  ];

  // 既有 description 又有 sub_objects
  const DS_TYPE = [
    'approval.action.update',
    'approval.group.update'
  ];

  export default {
    name: '',
    components: {
      IamSearchSelect,
      RenderStatus,
      renderDetailTable
    },
    data () {
      return {
        tableList: [],
        tableLoading: false,
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        searchParams: {},
        searchList: [],
        searchValue: [],
        initDateTime: new Date(),
        objectMap: {
          group: this.$t(`m.userGroup['用户组']`),
          system: this.$t(`m.common['系统']`),
          user: this.$t(`m.common['用户']`),
          department: this.$t(`m.common['组织']`),
          role: this.$t(`m.audit['角色']`),
          template: this.$t(`m.myApply['权限模板']`),
          commonaction: this.$t(`m.audit['常用操作']`),
          super_manager: this.$t(`m.myApproval['超级管理员']`),
          system_manager: this.$t(`m.nav['系统管理员']`),
          rating_manager: this.$t(`m.nav['一级空间管理员']`),
          subset_manager: this.$t(`m.nav['二级空间管理员']`)
        },
        sourceMap: {
          web: this.$t(`m.audit['页面']`),
          api: 'API',
          openapi: 'API'
        },
        typeMap: {
          'user.policy.create': this.$t(`m.audit['用户权限增加']`),
          'user.policy.update': this.$t(`m.audit['用户权限更新']`),
          'user.policy.delete': this.$t(`m.audit['用户权限删除']`),
          'user.group.delete': this.$t(`m.audit['用户退出用户组']`),
          'user.role.delete': this.$t(`m.audit['用户退出管理员']`),
          'group.create': this.$t(`m.audit['用户组创建']`),
          'group.update': this.$t(`m.audit['用户组修改']`),
          'group.delete': this.$t(`m.audit['用户组删除']`),
          'group.member.create': this.$t(`m.audit['用户组成员增加']`),
          'group.member.delete': this.$t(`m.audit['用户组成员删除']`),
          'group.member.renew': this.$t(`m.audit['用户组成员续期']`),
          'group.policy.create': this.$t(`m.audit['用户组权限增加']`),
          'group.policy.update': this.$t(`m.audit['用户组权限更新']`),
          'group.policy.delete': this.$t(`m.audit['用户组权限删除']`),
          'group.template.create': this.$t(`m.audit['用户组添加权限模板']`),
          'group.template.delete': this.$t(`m.audit['用户组删除权限模板']`),
          'template.create': this.$t(`m.audit['权限模板创建']`),
          'template.update': this.$t(`m.audit['权限模板修改']`),
          'template.delete': this.$t(`m.audit['权限模板删除']`),
          'template.member.create': this.$t(`m.audit['权限模板成员增加']`),
          'template.member.delete': this.$t(`m.audit['权限模板成员删除']`),
          'template.member.update': this.$t(`m.audit['权限模板成员更新']`),
          'template.preupdate.create': this.$t(`m.audit['权限模板预更新创建']`),
          'template.preupdate.delete': this.$t(`m.audit['权限模板预更新删除']`),
          'template.version.sync': this.$t(`m.audit['权限模板版本全量同步']`),
          'template.version.update': this.$t(`m.audit['权限模板更新同步']`),
          'template.update.commit': this.$t(`m.audit['权限模板更新提交']`),
          'role.create': this.$t(`m.audit['管理员创建']`),
          'role.member.create': this.$t(`m.audit['管理员成员增加']`),
          'role.member.delete': this.$t(`m.audit['管理员成员删除']`),
          'role.member.update': this.$t(`m.audit['管理员成员修改']`),
          'role.member.policy.create': this.$t(`m.audit['管理员成员开启业务权限']`),
          'role.member.policy.delete': this.$t(`m.audit['管理员成员关闭业务权限']`),
          'role.update': this.$t(`m.audit['管理员更新']`),
          'role.group.renew': this.$t(`m.audit['管理员用户组成员续期']`),
          'role.commonaction.create': this.$t(`m.audit['管理员常用操作新建']`),
          'role.commonaction.delete': this.$t(`m.audit['管理员常用操作删除']`),
          'event.rollback': this.$t(`m.audit['回滚事件']`),
          'approval.global.update': this.$t(`m.audit['修改默认审批流程']`),
          'approval.group.update': this.$t(`m.audit['修改用户组审批流程']`),
          'approval.action.update': this.$t(`m.audit['修改操作审批流程']`),
          'department.update': this.$t(`m.audit['组织架构同步']`),
          'department.group.delete': this.$t(`m.audit['删除组织用户组权限']`),
          'admin.api.allow.list.config.create': this.$t(`m.audit['ADMIN-API白名单创建']`),
          'admin.api.allow.list.config.delete': this.$t(`m.audit['ADMIN-API白名单删除']`),
          'authorization.api.allow.list.config.create': this.$t(`m.audit['授权类API白名单创建']`),
          'authorization.api.allow.list.config.delete': this.$t(`m.audit['授权类API白名单删除']`),
          'management.api.allow.list.config.create': this.$t(`m.audit['管理类API白名单创建']`),
          'management.api.allow.list.config.delete': this.$t(`m.audit['管理类API白名单删除']`),
          'group.transfer': this.$t(`m.audit['用户组权限交接']`)
        },
        currentMonth: '',
        noDetailType: NO_DETAIL_TYPE,
        onlyDescriptionType: ONLY_DESCRIPTION_TYPE,
        onlySubType: ONLY_SUB_TYPE,
        onlyExtraInfoType: ONLY_EXTRA_INFO_TYPE,
        deType: DE_TYPR,
        seType: SE_TYPE,
        dsType: DS_TYPE,
        onlyRoleType: ONLY_ROLE_TYPE,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      tableHeight () {
        return getWindowHeight() - 185;
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    created () {
      this.currentMonth = getDate(getFormatDate(this.initDateTime));
      this.searchData = [
        {
          id: 'username',
          name: this.$t(`m.audit['操作者']`),
          remoteMethod: this.handleRemoteRtx
        },
        {
          id: 'type',
          name: this.$t(`m.audit['操作类型']`),
          remoteMethod: this.handleRemoteType
        },
        {
          id: 'object_type',
          name: this.$t(`m.audit['对象及类型']`),
          remoteMethod: this.handleRemoteObjectType
        },
        {
          id: 'source_type',
          name: this.$t(`m.audit['操作来源']`),
          children: [
            {
              name: this.$t(`m.audit['页面']`),
              id: 'web'
            },
            {
              name: 'API',
              id: 'openapi'
            },
            {
              name: this.$t(`m.audit['任务']`),
              id: 'task'
            }
          ],
          remoteMethod: () => {}
        },
        {
          id: 'status',
          name: this.$t(`m.audit['操作状态']`),
          children: [
            {
              name: this.$t(`m.audit['成功']`),
              id: 0
            },
            {
              name: this.$t(`m.audit['失败']`),
              id: 1
            },
            {
              name: this.$t(`m.audit['完成']`),
              id: 2
            },
            {
              name: this.$t(`m.audit['错误']`),
              id: 3
            }
          ],
          remoteMethod: () => {}
        }
      ];
      const isObject = payload => {
        return Object.prototype.toString.call(payload) === '[object Object]';
      };
      const currentQueryCache = this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        if (currentQueryCache.limit) {
          this.pagination.limit = currentQueryCache.limit;
          this.pagination.current = currentQueryCache.current;
        }
        if (currentQueryCache.month) {
          this.currentMonth = currentQueryCache.month;
          this.initDateTime = new Date(`${currentQueryCache.month.slice(0, 4)}-${currentQueryCache.month.slice(4)}`);
        }
        for (const key in currentQueryCache) {
          if (key !== 'limit' && key !== 'current' && key !== 'month') {
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
        await this.fetchAuditList();
      },

      refreshCurrentQuery () {
        const { limit, current } = this.pagination;
        const params = {};
        const queryParams = {
          limit,
          current,
          month: this.currentMonth,
                    ...this.searchParams
        };
        window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        for (const key in this.searchParams) {
          const tempObj = this.searchData.find(item => key === item.id);
          if (tempObj && tempObj.remoteMethod && typeof tempObj.remoteMethod === 'function') {
            if (this.searchList.length > 0) {
              this.emptyData.tipType = 'search';
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
                    current,
                    month: this.currentMonth
        };
      },

      setCurrentQueryCache (payload) {
        window.localStorage.setItem('auditList', JSON.stringify(payload));
      },

      getCurrentQueryCache () {
        return JSON.parse(window.localStorage.getItem('auditList'));
      },

      async fetchAuditList (isLoading = false) {
        this.tableLoading = isLoading;
        this.setCurrentQueryCache(this.refreshCurrentQuery());
        const params = {
          limit: this.pagination.limit,
          offset: this.pagination.limit * (this.pagination.current - 1),
          month: this.currentMonth,
          source_type: '',
          type: '',
          object_type: '',
          object_id: '',
          status: '',
                    ...this.searchParams
        };
        try {
          const { code, data } = await this.$store.dispatch('audit/getAuditList', params);
          this.pagination.count = data.count || 0;
          (data.results || []).forEach(item => {
            item.loading = false;
            item.expanded = false;
            item.detail = {};
          });
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
        } catch (e) {
          console.error(e);
          this.tableList = [];
          const { code, data, message, statusText } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: message || data.msg || statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.tableLoading = false;
        }
      },

      handleRemoteRtx (value) {
        return fuzzyRtxSearch(value)
          .then(data => {
            return data.results;
          });
      },

      handleRemoteObjectType (value) {
        const list = [
          { id: 'group', name: this.$t(`m.myApply['用户组']`) },
          { id: 'user', name: this.$t(`m.common['用户']`) },
          { id: 'department', name: this.$t(`m.common['组织']`) },
          { id: 'template', name: this.$t(`m.myApply['权限模板']`) },
          { id: 'role', name: this.$t(`m.audit['角色']`) },
          { id: 'task', name: this.$t(`m.audit['任务']`) },
          { id: 'event', name: this.$t(`m.audit['审计事件']`) },
          { id: 'commonaction', name: this.$t(`m.audit['常用操作']`) },
          { id: 'action', name: this.$t(`m.common['操作']`) }
        ];
        if (value === '') {
          return Promise.resolve(list);
        }
        return Promise.resolve(list.filter(item => item.name.indexOf(value) > -1));
      },

      handleRemoteType (value) {
        const list = [
          { id: 'user.policy.create', name: this.$t(`m.audit['用户权限增加']`) },
          { id: 'user.policy.update', name: this.$t(`m.audit['用户权限更新']`) },
          { id: 'user.policy.delete', name: this.$t(`m.audit['用户权限删除']`) },
          { id: 'user.group.delete', name: this.$t(`m.audit['用户退出用户组']`) },
          { id: 'user.role.delete', name: this.$t(`m.audit['用户退出管理员']`) },
          { id: 'group.create', name: this.$t(`m.audit['用户组创建']`) },
          { id: 'group.update', name: this.$t(`m.audit['用户组修改']`) },
          { id: 'group.delete', name: this.$t(`m.audit['用户组删除']`) },
          { id: 'group.member.create', name: this.$t(`m.audit['用户组成员增加']`) },
          { id: 'group.member.delete', name: this.$t(`m.audit['用户组成员删除']`) },
          { id: 'group.member.renew', name: this.$t(`m.audit['用户组成员续期']`) },
          { id: 'group.policy.create', name: this.$t(`m.audit['用户组权限增加']`) },
          { id: 'group.policy.update', name: this.$t(`m.audit['用户组权限更新']`) },
          { id: 'group.policy.delete', name: this.$t(`m.audit['用户组权限删除']`) },
          { id: 'group.template.create', name: this.$t(`m.audit['用户组添加权限模板']`) },
          { id: 'group.template.delete', name: this.$t(`m.audit['用户组删除权限模板']`) },
          { id: 'template.create', name: this.$t(`m.audit['权限模板创建']`) },
          { id: 'template.update', name: this.$t(`m.audit['权限模板修改']`) },
          { id: 'template.delete', name: this.$t(`m.audit['权限模板删除']`) },
          { id: 'template.member.create', name: this.$t(`m.audit['权限模板成员增加']`) },
          { id: 'template.member.delete', name: this.$t(`m.audit['权限模板成员删除']`) },
          { id: 'template.member.update', name: this.$t(`m.audit['权限模板更新成员']`) },
          { id: 'template.preupdate.create', name: this.$t(`m.audit['权限模板预更新创建']`) },
          { id: 'template.preupdate.delete', name: this.$t(`m.audit['权限模板预更新删除']`) },
          { id: 'template.version.sync', name: this.$t(`m.audit['权限模板版本全量同步']`) },
          { id: 'template.version.update', name: this.$t(`m.audit['权限模板更新同步']`) },
          { id: 'template.update.commit', name: this.$t(`m.audit['权限模板更新提交']`) },
          { id: 'role.create', name: this.$t(`m.audit['管理员创建']`) },
          { id: 'role.member.create', name: this.$t(`m.audit['管理员成员增加']`) },
          { id: 'role.member.delete', name: this.$t(`m.audit['管理员成员删除']`) },
          { id: 'role.member.update', name: this.$t(`m.audit['管理员成员修改']`) },
          { id: 'role.member.policy.create', name: this.$t(`m.audit['管理员成员开启业务权限']`) },
          { id: 'role.member.policy.delete', name: this.$t(`m.audit['管理员成员关闭业务权限']`) },
          { id: 'role.update', name: this.$t(`m.audit['管理员更新']`) },
          { id: 'role.group.renew', name: this.$t(`m.audit['管理员用户组成员续期']`) },
          { id: 'role.commonaction.create', name: this.$t(`m.audit['管理员常用操作新建']`) },
          { id: 'role.commonaction.delete', name: this.$t(`m.audit['管理员常用操作删除']`) },
          { id: 'event.rollback', name: this.$t(`m.audit['回滚事件']`) },
          { id: 'approval.global.update', name: this.$t(`m.audit['修改默认审批流程']`) },
          { id: 'approval.group.update', name: this.$t(`m.audit['修改用户组审批流程']`) },
          { id: 'approval.action.update', name: this.$t(`m.audit['修改操作审批流程']`) },
          { id: 'department.update', name: this.$t(`m.audit['组织架构同步']`) },
          { id: 'department.group.delete', name: this.$t(`m.audit['删除组织用户组权限']`) },
          { id: 'admin.api.allow.list.config.create', name: this.$t(`m.audit['ADMIN-API白名单创建']`) },
          { id: 'admin.api.allow.list.config.delete', name: this.$t(`m.audit['ADMIN-API白名单删除']`) },
          { id: 'authorization.api.allow.list.config.create', name: this.$t(`m.audit['授权类API白名单创建']`) },
          { id: 'authorization.api.allow.list.config.delete', name: this.$t(`m.audit['授权类API白名单删除']`) },
          { id: 'management.api.allow.list.config.create', name: this.$t(`m.audit['管理类API白名单创建']`) },
          { id: 'management.api.allow.list.config.delete', name: this.$t(`m.audit['管理类API白名单删除']`) },
          { id: 'group.transfer', name: this.$t(`m.audit['用户组权限交接']`) }
        ];
        if (value === '') {
          return Promise.resolve(list);
        }
        return Promise.resolve(list.filter(item => item.name.indexOf(value) > -1));
      },

      resetPagination () {
        this.pagination = Object.assign({}, {
          limit: 10,
          current: 1,
          count: 0
        });
      },

      handleDateChange (date, type) {
        this.resetPagination();
        this.currentMonth = getDate(getFormatDate(date));
        this.fetchAuditList(true);
      },

      handleSearch (payload, result) {
        this.searchParams = payload;
        this.searchList = result;
        this.resetPagination();
        this.fetchAuditList(true);
      },

      handleEmptyClear () {
        this.searchParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.$refs.iamSearchSelect.$refs.searchSelect.isTagMultLine = false;
        this.resetPagination();
        this.fetchAuditList(true);
      },

      handleEmptyRefresh () {
        this.resetPagination();
        this.fetchAuditList(true);
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.fetchAuditList(true);
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.$refs.tableRef.clearFilter();
        this.fetchAuditList(true);
      },

      async handleExpandChange (row, expandedRows) {
        row.expanded = !row.expanded;
        if (this.noDetailType.includes(row.type)) {
          return;
        }
        if (row.expanded && Object.keys(row.detail).length < 1) {
          row.loading = true;
          try {
            const res = await this.$store.dispatch('audit/getAuditDetail', {
              id: row.id,
              month: this.currentMonth
            });
            row.detail = _.cloneDeep(res.data);
            if (this.seType.includes(row.detail.type)) {
              row.detail.sub_objects.forEach(item => {
                this.$set(item, 'version', row.detail.extra_info.version);
              });
            }
            if (this.dsType.includes(row.detail.type)) {
              row.detail.sub_objects.forEach(item => {
                this.$set(item, 'description', row.detail.description);
              });
            }
            if (this.onlyExtraInfoType.includes(row.detail.type)) {
              if (row.detail.type !== 'role.group.renew' && row.detail.type !== 'template.version.sync') {
                row.detail.extra_info.policies.forEach(item => {
                  item.system_id = row.detail.extra_info.system.id;
                  item.system_name = row.detail.extra_info.system.name;
                });
              }
            }
          } catch (e) {
            console.error(e);
            this.bkMessageInstance = this.$bkMessage({
              limit: 1,
              theme: 'error',
              message: e.message || e.data.msg || e.statusText
            });
          } finally {
            row.loading = false;
          }
        }
      }
    }
  };
</script>
<style lang="postcss">
    .iam-audit-wrapper {
        .audit-search-select {
            margin-left: 10px;
            float: right;
        }
        .audit-table {
            margin-top: 16px;
            border-right: none;
            border-bottom: none;
            .bk-table-expanded-cell {
                padding: 0 30px 0 45px !important;
            }
            &.set-border {
                border-right: 1px solid #dfe0e5;
                border-bottom: 1px solid #dfe0e5;
            }
            .audit-detail-wrapper {
                position: relative;
                padding: 16px 50px 16px 165px;
                min-height: 60px;
                p {
                    line-height: 24px;
                }
                .empty-wrapper {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    img {
                        width: 60px;
                    }
                }
            }
            .audit-detail-table {
                border: none;
                .bk-table-row-last {
                    td {
                        border-bottom: 1px solid #dfe0e5 !important;
                    }
                }
            }
        }
    }
</style>
