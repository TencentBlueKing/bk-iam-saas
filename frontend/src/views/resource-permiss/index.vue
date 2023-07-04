<template>
  <!-- eslint-disable max-len -->
  <div class="iam-system-access-wrapper">
    <render-search>
      <div>
        <bk-form form-type="inline" class="pb10">
          <iam-form-item :label="$t(`m.common['查询类型']`)" class="pb20 form-item-resource">
            <bk-select
              style="width: 504px; background: #fff"
              v-model="searchType"
              :clearable="true"
              :placeholder="$t(`m.verify['请选择']`)"
              @change="handlSearchChange">
              <bk-option v-for="option in searchTypeList"
                :key="option.value"
                :id="option.value"
                :name="option.name">
              </bk-option>
            </bk-select>
            <p class="error-tips" v-if="searchTypeError">{{$t(`m.resourcePermiss['请选择查询类型']`)}}</p>
          </iam-form-item>
        </bk-form>
      </div>
      <div>
        <bk-form form-type="inline" class="pb10">
          <iam-form-item :label="$t(`m.permApply['选择系统']`)" class="pb20 pr20 form-item-resource">
            <bk-select
              style="width: 200px; background: #fff"
              v-model="systemId"
              :clearable="true"
              :placeholder="$t(`m.verify['请选择']`)"
              @change="handleCascadeChange">
              <bk-option v-for="option in systemList"
                :key="option.id"
                :id="option.id"
                :name="`${option.name} (${option.id})`">
              </bk-option>
            </bk-select>
            <p class="error-tips" v-if="systemIdError">{{$t(`m.resourcePermiss['系统必填']`)}}</p>
          </iam-form-item>
          <iam-form-item :label="$t(`m.permApply['选择操作']`)" class="pb20 form-item-resourc">
            <bk-select
              style="width: 200px; background: #fff"
              v-model="actionId"
              :clearable="true"
              :placeholder="$t(`m.verify['请选择']`)"
              @selected="handleSelected"
              searchable>
              <bk-option v-for="option in processesList"
                :key="option.id"
                :id="option.id"
                :name="`${option.name} (${option.id})`">
              </bk-option>
            </bk-select>
            <p class="error-tips" v-if="actionIdError">{{$t(`m.resourcePermiss['操作必填']`)}}</p>
          </iam-form-item>
        </bk-form>
      </div>

      <div v-if="searchType === 'operate'">
        <bk-form form-type="inline">
          <iam-form-item :label="$t(`m.resourcePermiss['权限类型']`)" class="pb20">
            <bk-select
              style="width: 200px; background: #fff"
              v-model="permissionType"
              :placeholder="$t(`m.verify['请选择']`)"
              :clearable="true">
              <bk-option v-for="option in typeList"
                :key="option.value"
                :id="option.value"
                :name="option.name">
              </bk-option>
            </bk-select>
          </iam-form-item>
        </bk-form>
      </div>

      <div v-if="!resourceTypeData.isEmpty && searchType !== 'operate'">
        <bk-form form-type="inline" class="pb10">
          <iam-form-item class="pb20 form-item-resource" :label="$t(`m.common['资源实例']`)">
            <div v-for="(_, _index) in resourceTypeData.resource_groups" :key="_.id" class="resource-container">
              <div class="relation-content-item" v-for="(content, contentIndex) in
                _.related_resource_types" :key="contentIndex">
                <div class="content">
                  <render-condition
                    :ref="`condition_${$index}_${contentIndex}_ref`"
                    :value="content.value"
                    :is-empty="content.empty"
                    :params="curCopyParams"
                    :is-error="content.isLimitExceeded || content.isError"
                    @on-click="showResourceInstance(resourceTypeData, content, contentIndex, _index)" />
                </div>
                <p class="error-tips" v-if="resourceTypeError && content.empty">{{$t(`m.resourcePermiss['请选择资源实例']`)}}</p>
              </div>
            </div>
          </iam-form-item>

        </bk-form>
      </div>

      <div>
        <bk-form form-type="inline">
          <iam-form-item :label="$t(`m.resourcePermiss['条数展示']`)" class="pb20 pr20">
            <bk-select
              style="width: 200px; background: #fff"
              v-model="limit"
              :clearable="true"
              :placeholder="$t(`m.verify['请选择']`)">
              <bk-option v-for="option in limitList"
                :key="option"
                :id="option"
                :name="option">
              </bk-option>
            </bk-select>
          </iam-form-item>
          <bk-button class="mr10 ml10 mb20" theme="primary" @click="handleSearchAndExport(false)">
            {{ $t(`m.common['查询']`) }}</bk-button>
        </bk-form>
      </div>

    </render-search>

    <div class="resource-flex">
      <div>
        <bk-button class="mr10" theme="default" @click="handleReset">{{ $t(`m.common['重置']`) }}</bk-button>
        <bk-button theme="default" @click="handleSearchAndExport(true)" :disabled="!systemId || !actionId">
          {{ $t(`m.common['导出']`) }}</bk-button>
      </div>

      <bk-input
        :clearable="true"
        v-model="searchValue"
        :placeholder="$t(`m.resourcePermiss['请输入用户、用户组，按Enter搜索']`)"
        :right-icon="'bk-icon icon-search'"
        style="width: 420px;"
        @enter="handleSearch">
      </bk-input>
    </div>
        
    <bk-table
      :data="tableList"
      size="small"
      class="mb40"
      :class="{ 'set-border': tableLoading }"
      ext-cls="system-access-table"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
      :pagination="pagination"
      @page-change="pageChange"
      @page-limit-change="limitChange">
      <bk-table-column :label="$t(`m.resourcePermiss['有权限的成员']`)">
        <template slot-scope="{ row }">
          <span :title="row.type === 'user' ? `${row.id} (${row.name})` : `${row.name}`">
            {{row.type === 'user' ? `${row.id} (${row.name})` : `${row.name}`}}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.resourcePermiss['用户类型']`)">
        <template slot-scope="{ row }">
          {{row.type === 'user' ? $t(`m.nav['用户']`) : $t(`m.nav['用户组']`)}}
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

    <bk-sideslider
      :is-show="isShowResourceInstanceSideslider"
      :title="resourceInstanceSidesliderTitle"
      :width="960"
      quick-close
      transfer
      :ext-cls="'relate-instance-sideslider'"
      @update:isShow="handleResourceCancel">
      <div slot="content" class="sideslider-content">
        <render-resource
          ref="renderResourceRef"
          :data="condition"
          :original-data="originalCondition"
          :flag="curFlag"
          :selection-mode="curSelectionMode"
          :params="params"
          @on-limit-change="handleLimitChange"
        />
      </div>
      <div slot="footer" style="margin-left: 25px;">
        <bk-button theme="primary" :loading="sliderLoading" :disabled="disabled" @click="handleResourceSumit">{{ $t(`m.common['保存']`) }}</bk-button>
        <bk-button style="margin-left: 10px;" :disabled="disabled" @click="handleResourceCancel">{{ $t(`m.common['取消']`) }}</bk-button>
      </div>
    </bk-sideslider>
  </div>
</template>
<script>
    // import IamSearchSelect from '@/components/iam-search-select'
  import Policy from '@/model/policy';
  import _ from 'lodash';
  import RenderCondition from './components/render-condition.vue';
  import RenderResource from './components/render-resource.vue';
  import { leaveConfirm } from '@/common/leave-confirm';
  import { fuzzyRtxSearch } from '@/common/rtx';
  import { formatCodeData } from '@/common/util';
  import { mapGetters } from 'vuex';
  // import iamCascade from '@/components/cascade'

  // 单次申请的最大实例数
  // const RESOURCE_MAX_LEN = 20
  export default {
    name: 'resource-permiss',
    components: {
      RenderCondition,
      RenderResource
      // IamSearchSelect
      // iamCascade
    },
    data () {
      return {
        tableList: [],
        tableListClone: [],
        tableLoading: false,
        instanceLoading: false,
        systemList: [],
        resourceList: [],
        systemId: '',
        actionId: '',
        processesList: [],
        typeList: [{ name: this.$t(`m.resourcePermiss['自定义权限']`), value: 'custom' }, { name: this.$t(`m.resourcePermiss['模板权限']`), value: 'template' }],
        permissionType: '',
        groupValue: '1-1',
        limit: 100,
        limitList: [10, 20, 50, 100, 200, 500, 1000],
        resourceActionId: 0,
        resourceActionSystemId: '',
        resourceSystemId: '',
        resourceActionData: [],
        hasMore: false,
        resourceType: '',
        parentId: '',
        resourceListChilder: [],
        resourceTypeData: { isEmpty: true },
        isShowResourceInstanceSideslider: false,
        curResIndex: -1,
        groupIndex: -1,
        params: {},
        resourceInstances: [],
        searchTypeList: [{ name: this.$t(`m.resourcePermiss['实例权限']`), value: 'resource_instance' }, { name: this.$t(`m.resourcePermiss['操作权限']`), value: 'operate' }],
        searchType: '',
        searchValue: '',
        systemIdError: false,
        actionIdError: false,
        searchTypeError: false,
        resourceTypeError: false,
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        emptyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      ...mapGetters(['externalSystemId']),
      condition () {
          if (this.curResIndex === -1 || this.groupIndex === -1) {
              return [];
          }
          const curData = this.resourceTypeData.resource_groups[this.groupIndex]
              .related_resource_types[this.curResIndex];
          if (!curData) {
              return [];
          }
          if (curData.condition.length === 0) curData.condition = ['none'];
          return _.cloneDeep(curData.condition);
      },
      curSelectionMode () {
          if (this.curResIndex === -1 || this.groupIndex === -1) {
              return 'all';
          }
          const curData = this.resourceTypeData.resource_groups[this.groupIndex]
              .related_resource_types[this.curResIndex];
          return curData.selectionMode;
      },
      originalCondition () {
          return _.cloneDeep(this.condition);
      }
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      },
      searchValue (value) {
        if (!value) {
          this.tableList = _.cloneDeep(this.tableListClone);
        }
      }
    },
    created () {
      // this.handleSearchAndExport(false)
      this.fetchSystemList();
      this.searchData = [
        {
          id: 'group',
          name: this.$t(`m.userGroup['用户组名']`),
          default: true
        },
        {
          id: 'user',
          name: this.$t(`m.common['用户']`)
        }
      ];
    },
    methods: {
      async fetchSystemList () {
        try {
          const params = {};
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const res = await this.$store.dispatch('system/getSystems', params);
          this.systemList = res.data;
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
          // this.requestQueue.shift()
        }
      },

      async handleCascadeChange () {
        this.systemIdError = false;
        this.resourceActionData = [];
        this.processesList = [];
        if (!this.systemId) return;
        this.actionId = '';
        this.resourceTypeData = { isEmpty: true };
        const systemId = this.systemId;
        try {
          const res = await this.$store.dispatch('approvalProcess/getActionGroups', { system_id: systemId });
          this.recursionFunc(res.data);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText
          });
        }
      },

      // 查询类型选择
      handlSearchChange (value) {
        this.searchTypeError = false;
        this.resourceTypeData = { isEmpty: true };
        this.systemId = '';
        this.actionId = '';
        this.resourceInstances = [];
        if (value === 'operate') {
          this.permissionType = 'custom';
        }
      },

      // 操作选择
      handleSelected () {
        this.actionIdError = false;
        this.resourceTypeError = false;
        this.resourceInstances = [];
        this.resourceTypeData = this.processesList.find(e => e.id === this.actionId);
      },

      // 查询和导入
      async handleSearchAndExport (isExport = false) {
        if (!this.searchType) {
          this.searchTypeError = true;
          return;
        }
        if (!this.systemId) {
          this.systemIdError = true;
          return;
        }
        if (!this.actionId) {
          this.actionIdError = true;
          return;
        }
        if (!this.resourceTypeData.isEmpty && this.searchType !== 'operate'
          && this.resourceTypeData.resource_groups[this.groupIndex]
          && this.resourceTypeData.resource_groups[this.groupIndex]
            .related_resource_types.some(e => e.empty)) {
          this.resourceTypeError = true;
          return;
        }
        this.tableLoading = !isExport;
        let resourceInstances = _.cloneDeep(this.resourceInstances);
        resourceInstances = resourceInstances.reduce((prev, item) => {
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
        const params = {
          system_id: this.systemId || '',
          action_id: this.actionId,
          resource_instances: resourceInstances || [],
          permission_type: this.searchType === 'resource_instance' ? 'resource_instance' : this.permissionType,
          limit: this.limit
        };
        try {
          const fetchUrl = isExport ? 'resourcePermiss/exportResourceManager' : 'resourcePermiss/getResourceManager';
          const res = await this.$store.dispatch(fetchUrl, params);
          if (isExport) {
            if (res.ok) {
              const blob = await res.blob();
              const url = URL.createObjectURL(blob);
              const elment = document.createElement('a');
              elment.download = '资源权限管理.xlsx';
              elment.href = url;
              elment.click();
              URL.revokeObjectURL(blob);

              this.$bkMessage({
                theme: 'success',
                message: '导出成功！'
              });
            }
          } else {
            this.tableList = res.data || [];
            this.tableListClone = _.cloneDeep(this.tableList);
            this.pagination.count = res.data.length;
            const data = this.getDataByPage();
            this.tableList.splice(0, this.tableList.length, ...data);
            this.emptyData.tipType = 'search';
            this.emptyData = formatCodeData(res.code, this.emptyData, this.tableList.length === 0);
          }
        } catch (e) {
          console.error(e);
          const { code, data, message, statusText } = e;
          this.tableList = [];
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

      // 重置
      handleReset () {
        this.searchType = '';
        this.systemId = '';
        this.actionId = '';
        this.resourceInstances = [];
        this.permissionType = '';
        this.limit = 100;
      },

      // 求值
      recursionFunc (list) {
        list.forEach(data => {
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
        this.resourceActionData = this.resourceActionData.filter((e, index, self) => self.indexOf(e) === index);
        this.resourceActionData.forEach(item => {
          if (!item.resource_groups || !item.resource_groups.length) {
            item.resource_groups = item.related_resource_types.length ? [{ id: '', related_resource_types: item.related_resource_types }] : [];
          }
          this.processesList.push(new Policy({ ...item, tag: 'add' }, 'custom'));
        });
      },

      // 显示资源实例
      showResourceInstance (data, resItem, resIndex, groupIndex) {
        this.params = {
          system_id: this.systemId,
          action_id: data.id,
          resource_type_system: resItem.system_id,
          resource_type_id: resItem.type
        };

        this.curResIndex = resIndex;
        this.groupIndex = groupIndex;
        this.resourceInstanceSidesliderTitle = this.$t(`m.info['关联侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}` });
        window.changeAlert = 'iamSidesider';
        this.isShowResourceInstanceSideslider = true;
      },

      handleResourceCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(() => {
          this.isShowResourceInstanceSideslider = false;
          this.resetDataAfterClose();
        }, _ => _);
      },

      resetDataAfterClose () {
        this.curResIndex = -1;
        this.groupIndex = -1;
        this.params = {};
        this.resourceInstanceSidesliderTitle = '';
      },

      async handleResourceSumit () {
        const conditionData = this.$refs.renderResourceRef.handleGetValue();
        const { isEmpty, data } = conditionData;
        if (isEmpty) {
          return;
        }
        const resItem = this.resourceTypeData.resource_groups[this.groupIndex]
          .related_resource_types[this.curResIndex];
        const isConditionEmpty = data.length === 1 && data[0] === 'none';
        if (isConditionEmpty) {
          resItem.condition = ['none'];
          resItem.isLimitExceeded = false;
          this.resourceInstances = [];
        } else {
          resItem.condition = data;
          if (data.length) {
            data.forEach(item => {
              item.instance.forEach(e => {
                resItem.resourceInstancesPath = e.path[0];
              });
            });
          } else {
            delete resItem.resourceInstancesPath;
          }
          if (this.curResIndex !== -1) {
            this.resourceInstances.splice(this.curResIndex, 1, resItem);
          }
        }
        window.changeAlert = false;
        this.resourceInstanceSidesliderTitle = '';
        this.isShowResourceInstanceSideslider = false;
        this.curResIndex = -1;
        this.resourceTypeError = false;
      },
            
      // 搜索
      handleSearch () {
        if (this.searchValue) {
          this.emptyData = formatCodeData(0, Object.assign(this.emptyData, { tipType: 'search' }));
          this.tableList = _.cloneDeep(this.tableListClone).filter(item =>
            item.name.indexOf(this.searchValue) !== -1);
        }
      },

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      },

      handleEmptyClear () {
        this.searchValue = '';
        this.handleReset();
        this.emptyData = formatCodeData(0, Object.assign(this.emptyData, { type: 'empty', text: '', tipType: '' }));
      },

      handleEmptyRefresh () {
        this.handleSearchAndExport();
      },

      handleRemoteRtx (value) {
        return fuzzyRtxSearch(value)
          .then(data => {
            return data.results;
          });
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        const data = this.getDataByPage(page);
        this.tableList.splice(0, this.tableList.length, ...data);
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        const data = this.getDataByPage(this.pagination.current);
        this.tableList.splice(0, this.tableList.length, ...data);
      },

      getDataByPage (page) {
        if (!page) {
          this.pagination.current = page = 1;
        }
        let startIndex = (page - 1) * this.pagination.limit;
        let endIndex = page * this.pagination.limit;
        if (startIndex < 0) {
          startIndex = 0;
        }
        if (endIndex > this.tableListClone.length) {
          endIndex = this.tableListClone.length;
        }
        return this.tableListClone.slice(startIndex, endIndex);
      }
            
    }
  };
</script>
<style lang="postcss">
    .iam-system-access-wrapper {
        .detail-link {
            color: #3a84ff;
            cursor: pointer;
            &:hover {
                color: #699df4;
            }
            font-size: 12px;
        }
        .system-access-table {
            margin-top: 16px;
            border-right: none;
            border-bottom: none;
            &.set-border {
                border-right: 1px solid #dfe0e5;
                border-bottom: 1px solid #dfe0e5;
            }
            .system-access-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
            .lock-status {
                font-size: 12px;
                color: #fe9c00;
            }
        }
        .link-btn{
            margin: 10px 0 10px 600px;
        }
        .msg-content{
            background: #555555;
            color: #fff;
            margin: 0 0px 0 30px;
            padding: 10px;
            max-height: 1200px;
            overflow-y: scroll;
        }
    }
    .resource-container {
        display: flex;
        justify-content: space-between;
        .relation-content-item{
            display: flex;
            /* width: 220px; */
            .content-name{
                font-size: 14px;
                padding-right: 10px;
            }
            .content{
                width: 200px;
            }
        }

        .relation-content-item:nth-child(2){
            margin-left: 32px;
        }
    }

    .resource-flex {
        display: flex;
        justify-content: space-between;
    }

    .form-item-resource{
        position: relative;
    }

    .error-tips {
        font-size: 12px;
        color: #ff4d4d;
        position: absolute;
        top: 33px;
        height: 20px;
        line-height: 20px;
        &.mt {
            margin-top: 10px;
        }
    }
</style>
