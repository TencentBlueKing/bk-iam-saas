<template>
  <smart-action class="iam-join-user-group-wrapper">
    <render-horizontal-block :label="$t(`m.permApply['选择用户组']`)" :required="true">
      <div
        ref="selectTableRef"
        class="iam-search-resource-form">
        <div class="search-wrapper">
          <render-search v-if="enableGroupInstanceSearch">
            <div
              :class="[
                'join-user-group-form',
                { 'join-user-group-form-lang': !curLanguageIsCn }
              ]">
              <div>
                <bk-form
                  form-type="vertical"
                  class="pb30 resource-action-form">
                  <iam-form-item
                    :label="$t(`m.common['系统']`)"
                    class="pr20 form-item-resource">
                    <bk-select
                      :style="{ width: contentWidth }"
                      v-model="applyGroupData.system_id"
                      :clearable="true"
                      :allow-enter="false"
                      :placeholder="$t(`m.verify['请选择']`)"
                      @change="handleCascadeChange"
                      @clear="handleClearSearch"
                      searchable>
                      <bk-option v-for="option in systemList"
                        :key="option.id"
                        :id="option.id"
                        :name="`${option.name} (${option.id})`">
                      </bk-option>
                    </bk-select>
                    <p class="error-tips" v-if="systemIdError">
                      {{$t(`m.verify['请选择系统']`)}}
                    </p>
                  </iam-form-item>
                  <iam-form-item
                    :label="$t(`m.common['操作']`)"
                    class="pr20"
                  >
                    <bk-select
                      :style="{ width: contentWidth }"
                      v-model="applyGroupData.action_id"
                      :clearable="false"
                      :allow-enter="false"
                      :placeholder="$t(`m.verify['请选择']`)"
                      :disabled="!applyGroupData.action_id"
                      :title="!applyGroupData.system_id ?
                        $t(`m.verify['请选择系统']`) : ''"
                      @selected="handleSelectedAction"
                      searchable>
                      <bk-option v-for="option in processesList"
                        :key="option.id"
                        :id="option.id"
                        :name="`${option.name} (${option.id})`">
                      </bk-option>
                    </bk-select>
                    <p class="error-tips" v-if="actionError">
                      {{$t(`m.verify['请选择操作']`)}}
                    </p>
                  </iam-form-item>
                  <template>
                    <div
                      v-for="(_, index) in resourceTypeData.resource_groups"
                      :key="_.id"
                      class="resource-group-container">
                      <div>
                        <iam-form-item
                          :label="$t(`m.permApply['资源类型']`)"
                          class="pr20 form-item-resource">
                          <bk-select
                            :style="{ width: contentWidth }"
                            v-model="curResourceData.type"
                            :clearable="false"
                            :allow-enter="false"
                            :placeholder="$t(`m.verify['请选择']`)"
                            :disabled="!applyGroupData.action_id"
                            :title="!applyGroupData.action_id ?
                              $t(`m.verify['请选择操作']`) : ''"
                            @change="handleResourceTypeChange(index)"
                          >
                            <bk-option
                              v-for="related in _.related_resource_types_list"
                              :key="related.type"
                              :id="related.type"
                              :name="related.name">
                            </bk-option>
                          </bk-select>
                          <p class="error-tips" v-if="resourceTypeError">
                            {{$t(`m.verify['请选择资源类型']`)}}
                          </p>
                        </iam-form-item>
                      </div>
                      <iam-form-item
                        :style="{ width: contentWidth }"
                        class="form-item-resource"
                        :label="$t(`m.common['资源实例']`)">
                        <div class="relation-content-item"
                          v-for="(content, contentIndex) in _.related_resource_types"
                          :key="contentIndex">
                          <div class="content"
                          >
                            <render-condition
                              :ref="`condition_${index}_${contentIndex}_ref`"
                              :value="curResourceData.type ?
                                content.value : $t(`m.verify['请选择']`)"
                              :hover-title="!curResourceData.type ?
                                $t(`m.verify['请选择资源类型']`) : ''"
                              :is-empty="content.empty"
                              :params="curCopyParams"
                              :disabled="!curResourceData.type"
                              :is-error="content.isLimitExceeded || content.isError"
                              @on-click="handleShowResourceInstance(
                                resourceTypeData,
                                content, contentIndex, index)"
                            />
                            <p class="error-tips" v-if="resourceInstanceError">
                              {{$t(`m.resourcePermiss['请选择资源实例']`)}}
                            </p>
                          </div>
                        </div>
                      </iam-form-item>
                    </div>
                  </template>
                </bk-form>
              </div>
              <div class="group-search-select pb20">
                <iam-search-select
                  style="width: calc(100% - 20px)"
                  ref="searchSelectRef"
                  :data="searchData"
                  :value="searchValue"
                  :placeholder="$t(`m.applyEntrance['申请加入用户组搜索提示']`)"
                  :quick-search-method="quickSearchMethod"
                  @on-change="handleSearch"
                  @on-click-menu="handleClickMenu"
                  @on-input="handleSearchInput"
                />
                <bk-button
                  class="ml20"
                  theme="primary"
                  @click="handleSearchUserGroup(true)">
                  {{ $t(`m.common['查询']`) }}
                </bk-button>
                <bk-button
                  class="ml20"
                  theme="default"
                  @click="handleEmptyClear">
                  {{ $t(`m.common['重置']`) }}
                </bk-button>
              </div>
            </div>
          </render-search>
          <div v-else>
            <iam-search-select
              ref="searchSelectRef"
              @on-change="handleSearch"
              :data="searchData"
              :value="searchValue"
              :placeholder="$t(`m.applyEntrance['申请加入用户组搜索提示']`)"
              :quick-search-method="quickSearchMethod" />
          </div>
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
          <bk-table-column type="selection" align="center" :selectable="setDefaultSelect" />
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
          <bk-table-column :label="$t(`m.grading['管理空间']`)">
            <template slot-scope="{ row }">
              <span
                :title="row.role && row.role.name ? row.role.name : ''"
              >
                {{ row.role ? row.role.name : '--' }}
              </span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t(`m.levelSpace['管理员']`)">
            <template slot-scope="{ row, $index }">
              <iam-edit-member-selector
                mode="detail"
                field="members"
                width="200"
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
        <div class="apply-selected-groups">
          <div
            v-if="currentSelectedGroups.length"
            class="apply-selected-groups-header"
          >
            <span>{{ $t(`m.common['已选择']`) }}</span>
            <span class="apply-selected-groups-header-count">{{ currentSelectedGroups.length }}</span>
            <span>{{ $t(`m.common['个用户组#']`) }}</span>
            <span>{{ $t(`m.common['，']`) }}</span>
            <span
              class="apply-selected-groups-header-clear"
              @click.stop="handleClearGroups">
              {{ $t(`m.permApply['清空选择']`) }}:
            </span>
          </div>
          <bk-tag
            class="group-tag-close"
            v-for="item in currentSelectedGroups"
            :key="item.id"
            :closable="true"
            @close="handleCloseTag(item)"
          >
            {{ item.name }}
          </bk-tag>
        </div>
      </div>
      <p class="user-group-error" v-if="isShowGroupError">{{ $t(`m.permApply['请选择用户组']`) }}</p>
    </render-horizontal-block>
    <section>
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
      :is-show="isShowResourceInstanceSideSlider"
      :title="resourceInstanceSideSliderTitle"
      :width="960"
      quick-close
      transfer
      :ext-cls="'relate-instance-sideslider'"
      @update:isShow="handleResourceCancel">
      <div slot="content"
        class="sideslider-content">
        <render-resource
          ref="renderResourceRef"
          :data="condition"
          :original-data="originalCondition"
          :selection-mode="curSelectionMode"
          :params="params"
        />
      </div>
      <div slot="footer" style="margin-left: 25px;">
        <bk-button theme="primary" :loading="sliderLoading" @click="handleResourceSubmit">
          {{ $t(`m.common['保存']`) }}
        </bk-button>
        <bk-button style="margin-left: 10px;" @click="handleResourceCancel">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
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
  import Policy from '@/model/policy';
  import { mapGetters } from 'vuex';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData, delLocationHref } from '@/common/util';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { leaveConfirm } from '@/common/leave-confirm';
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import IamSearchSelect from '@/components/iam-search-select';
  // import IamGuide from '@/components/iam-guide/index.vue';
  import RenderPermSideSlider from '@/views/perm/components/render-group-perm-sideslider';
  // import RenderAction from '@/views/grading-admin/common/render-action';
  import RenderMember from '@/views/grading-admin/components/render-member';
  import AddMemberDialog from '@/views/group/components/iam-add-member';
  import ConfirmDialog from '@/components/iam-confirm-dialog/index';
  import IamEditMemberSelector from '@/views/my-manage-space/components/iam-edit/member-selector';
  import RenderCondition from '@/views/resource-permiss/components/render-condition';
  import RenderResource from '@/views/resource-permiss/components/render-resource';
  // import BkUserSelector from '@blueking/user-selector';

  export default {
    name: '',
    components: {
      // IamGuide,
      IamDeadline,
      IamSearchSelect,
      IamEditMemberSelector,
      RenderPermSideSlider,
      // RenderAction,
      RenderMember,
      AddMemberDialog,
      ConfirmDialog,
      RenderCondition,
      RenderResource
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
        isShowMemberEmptyError: false,
        tableList: [],
        currentSelectList: [],
        curUserGroup: [],
        currentSelectedGroups: [],
        defaultSelectedGroups: [],
        defaultSelectedIds: [],
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
        sliderLoading: false,
        curRole: '',
        users: [],
        departments: [],
        isAll: false,
        addMemberTitle: this.$t(`m.myApply['权限获得者']`),
        addMemberText: this.$t(`m.permApply['选择权限获得者']`),
        addMemberTips: this.$t(`m.permApply['可代他人申请加入用户组获取权限']`),
        curCopyParams: {},
        queryParams: {},
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        applyGroupData: {
          system_id: '',
          action_id: ''
        },
        systemList: [],
        processesList: [],
        resourceInstances: [],
        isShowConfirmDialog: false,
        confirmDialogTitle: this.$t(`m.verify['admin无需申请权限']`),
        actionIdError: false,
        searchTypeError: false,
        resourceTypeError: false,
        resourceInstanceError: false,
        isShowResourceInstanceSideSlider: false,
        resourceTypeData: {
          resource_groups: [{
            'related_resource_types': [{
              'type': '',
              'system_id': '',
              'name': '',
              'canPaste': false,
              'action': {
                'name': '',
                'type': ''
              },
              'isError': false,
              'tag': '',
              'flag': '',
              'isChange': false,
              'isNew': true,
              'selectionMode': '',
              'condition': [],
              'conditionBackup': []
            }],
            'related_resource_types_list': []
          }],
          isEmpty: true
        },
        defaultResourceTypeList: [{
          'type': '',
          'system_id': '',
          'name': '',
          'canPaste': false,
          'action': {
            'name': '',
            'type': ''
          },
          'isError': false,
          'tag': '',
          'flag': '',
          'isChange': false,
          'isNew': true,
          'selectionMode': '',
          'condition': [],
          'conditionBackup': []
        }],
        curResourceData: {
          type: ''
        },
        curResourceTypeList: [],
        resourceInstanceSideSliderTitle: '',
        params: {},
        curResIndex: -1,
        groupIndex: -1,
        systemIdError: false,
        actionError: false,
        isSearchSystem: false,
        initSearchData: [
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
        ],
        enableGroupInstanceSearch: window.ENABLE_GROUP_INSTANCE_SEARCH.toLowerCase() === 'true',
        curSelectMenu: '',
        curInputText: '',
        contentWidth: window.innerWidth <= 1440 ? '200px' : '240px'
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemId']),
      condition () {
          if (this.curResIndex === -1 || this.groupIndex === -1) {
              return [];
          }
          this.curResourceData = this.resourceTypeData.resource_groups[this.groupIndex]
              .related_resource_types[this.curResIndex];
          if (!this.curResourceData) {
              return [];
          }
          if (this.curResourceData.condition.length === 0) this.curResourceData.condition = ['none'];
          return _.cloneDeep(this.curResourceData.condition);
      },
      curSelectionMode () {
          if (this.curResIndex === -1 || this.groupIndex === -1) {
              return 'all';
          }
          this.curResourceData = this.resourceTypeData.resource_groups[this.groupIndex]
              .related_resource_types[this.curResIndex];
          return this.curResourceData.selectionMode;
      },
      originalCondition () {
          return _.cloneDeep(this.condition);
      }
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
      const { role, name, username } = this.user;
      this.curRole = role.type;
      this.users = [
        {
          'username': username,
          'name': name || username,
          'showRadio': true,
          'type': 'user',
          'is_selected': true
        }
      ];
      this.searchData = this.enableGroupInstanceSearch ? this.initSearchData.filter(item => ['name', 'id', 'description'].includes(item.id)) : this.initSearchData;
      this.setCurrentQueryCache(this.refreshCurrentQuery());
      const isObject = (payload) => {
        return Object.prototype.toString.call(payload) === '[object Object]';
      };
      const currentQueryCache = await this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        this.pagination = Object.assign(
          this.pagination,
          {
            current: currentQueryCache.current ? Number(currentQueryCache.current) : this.pagination.current,
            limit: currentQueryCache.limit ? Number(currentQueryCache.limit) : this.pagination.limit
          }
        );
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
                if (this.applyGroupData.hasOwnProperty(key)) {
                  this.applyGroupData[key] = curData.id;
                }
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
              if (this.applyGroupData.hasOwnProperty(key)) {
                this.applyGroupData[key] = curData;
              }
            } else {
              this.searchParams[key] = curData;
              if (this.applyGroupData.hasOwnProperty(key)) {
                this.applyGroupData[key] = curData;
              }
            }
          }
        }
      }
      this.fetchDefaultData();
    },
    mounted () {
      window.addEventListener('resize', (this.formatFormItemWidth));
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
      });
    },
    methods: {
      formatFormItemWidth () {
        this.contentWidth = window.innerWidth <= 1520 ? '200px' : '240px';
      },
      /**
       * 获取页面数据
       */
      async fetchDefaultData () {
        this.fetchSystemList();
        await this.fetchCurUserGroup();
        await this.fetchUserGroupList();
        const { system_id } = this.applyGroupData;
        // eslint-disable-next-line camelcase
        if (system_id) {
          await this.handleSearchUserGroup();
        }
      },

      async handleCascadeChange () {
        this.systemIdError = false;
        this.actionError = false;
        this.resourceTypeError = false;
        this.resourceInstanceError = false;
        this.resourceActionData = [];
        this.processesList = [];
        this.applyGroupData.action_id = '';
        this.curResourceData.type = '';
        this.handleResetResourceData();
        if (this.applyGroupData.system_id) {
          try {
            const { data } = await this.$store.dispatch('approvalProcess/getActionGroups', { system_id: this.applyGroupData.system_id });
            this.handleFormatRecursion(data || []);
          } catch (e) {
            console.error(e);
            this.messageAdvancedError(e);
          }
        }
      },

      handleResourceTypeChange (index) {
        this.resourceTypeError = false;
        this.groupIndex = index;
        this.resourceInstances = [];
        if (this.resourceTypeData
          && this.resourceTypeData.resource_groups
          && this.resourceTypeData.resource_groups.length) {
          const resourceGroups = this.resourceTypeData.resource_groups[index];
          const typesList = _.cloneDeep(resourceGroups.related_resource_types_list);
          resourceGroups.related_resource_types
            = typesList.filter(item => item.type === this.curResourceData.type);
          if (typesList.length && !resourceGroups.related_resource_types.length) {
            this.$set(this.resourceTypeData.resource_groups[index], 'related_resource_types', this.defaultResourceTypeList);
          }
        }
        if (!this.applyGroupData.system_id || !this.resourceTypeData.resource_groups.length) {
          this.handleResetResourceData();
        }
      },

      handleSelectedAction () {
        this.actionIdError = false;
        this.resourceTypeError = false;
        this.resourceInstanceError = false;
        this.curResourceData.type = '';
        this.resourceInstances = [];
        // 处理操作下是否有无关联资源
        this.curResourceTypeList = [];
        this.resourceTypeData = _.cloneDeep(this.processesList.find(e => e.id === this.applyGroupData.action_id));
        if (this.resourceTypeData && this.resourceTypeData.resource_groups) {
          if (this.resourceTypeData.resource_groups.length) {
            const resourceGroups = this.resourceTypeData.resource_groups;
            this.resourceTypeData.resource_groups.forEach(item => {
              // 避免切换操作时，把默认数据代入，从而导致下拉框出现空白项
              if (item.related_resource_types.length && item.related_resource_types[0].system_id) {
                this.$set(item, 'related_resource_types_list', _.cloneDeep(item.related_resource_types));
                this.curResourceTypeList = _.cloneDeep(item.related_resource_types);
                // 默认选中只有一条资源类型数据，改变当前索引值
                if (item.related_resource_types.length === 1) {
                  this.curResourceData.type = item.related_resource_types[0].type;
                  this.handleResourceTypeChange(0);
                }
              }
            });
            if (!this.curResourceData.type) {
              this.$set(this.resourceTypeData.resource_groups[0], 'related_resource_types', []);
            }
            // 如果related_resource_types和related_resource_types_list都为空，则需要填充默认数据显示资源实例下路拉框
            if ((resourceGroups[0].related_resource_types_list
              && resourceGroups[0].related_resource_types_list.length
              && !resourceGroups[0].related_resource_types.length)
              || (!resourceGroups[0].related_resource_types.length
                && !resourceGroups[0].related_resource_types_list.length)
            ) {
              this.$set(this.resourceTypeData.resource_groups[0], 'related_resource_types', this.defaultResourceTypeList);
            }
          } else {
            this.handleResetResourceData();
          }
        }
      },
            
      handleFormatRecursion (list) {
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
        if (this.processesList.length) {
          this.applyGroupData.action_id = this.processesList[0].id;
          this.handleSelectedAction();
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

      // 显示资源实例
      handleShowResourceInstance (data, resItem, resIndex, groupIndex) {
        this.params = {
          system_id: this.applyGroupData.system_id,
          action_id: data.id,
          resource_type_system: resItem.system_id,
          resource_type_id: resItem.type
        };
        this.curResIndex = resIndex;
        this.groupIndex = groupIndex;
        this.resourceInstanceSidesliderTitle = this.$t(`m.info['关联侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}` });
        window.changeAlert = 'iamSidesider';
        this.isShowResourceInstanceSideSlider = true;
      },

      handleToCustomApply () {
        this.$router.push({
          name: 'applyCustomPerm'
        });
      },

      handleEmptyRefresh () {
        this.searchParams = {};
        this.queryParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.resetPagination();
        this.resetSearchParams();
        this.fetchUserGroupList(false);
      },

      handleEmptyClear () {
        this.searchParams = {};
        this.queryParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        if (this.$refs.searchSelectRef && this.$refs.searchSelectRef.$refs.searchSelect) {
          this.$refs.searchSelectRef.$refs.searchSelect.localValue = '';
        }
        this.resetPagination();
        this.resetSearchParams();
        this.fetchUserGroupList(false);
      },

      // 处理手动输入各种场景
      handleManualInput () {
        if (this.curSelectMenu) {
          // let inputText = _.cloneDeep(this.curInputText);
          // const curItem = this.initSearchData.find(item => item.id === this.curSelectMenu);
          // const isHasName = this.curInputText.indexOf(`${curItem.name}：`) > -1;
          // if (isHasName) {
          //   inputText = this.curInputText.split(`${curItem.name}：`);
          // }
          // const textValue = _.isArray(inputText) ? inputText[1] : inputText;
          // this.$set(this.searchParams, this.curSelectMenu, textValue);
          // this.searchList.push({
          //   id: this.curSelectMenu,
          //   name: curItem.name,
          //   values: [
          //     {
          //       id: textValue,
          //       name: textValue
          //     }
          //   ]
          // });
          // this.searchValue = _.cloneDeep(this.searchList);
          // 转换为tag标签后,需要清空输入框的值
          if (this.$refs.searchSelectRef && this.$refs.searchSelectRef.$refs.searchSelect) {
            this.$refs.searchSelectRef.$refs.searchSelect.keySubmit();
            this.$refs.searchSelectRef.$refs.searchSelect.localValue = '';
          }
          this.curSelectMenu = '';
          this.curInputText = '';
        } else {
          // 如果当前已有tag，后面如果只输入文字没生成tag自动过滤掉
          if (this.searchList.length
            && this.$refs.searchSelectRef
            && this.$refs.searchSelectRef.$refs.searchSelect
            && this.curInputText) {
            this.$refs.searchSelectRef.$refs.searchSelect.localValue = '';
          }
          if (!this.searchList.length) {
            // 处理无tag标签，直接输入内容情况
            this.searchParams.name = this.curInputText;
            if (!this.curInputText) {
              delete this.searchParams.name;
            }
          }
        }
      },

      async handleSearchUserGroup (isClick = false) {
        this.handleManualInput();
        if (this.applyGroupData.system_id && this.enableGroupInstanceSearch) {
          if (!this.applyGroupData.system_id) {
            this.systemIdError = true;
            return;
          }
          if (!this.applyGroupData.action_id) {
            this.actionError = true;
            return;
          }
          if (this.curResourceTypeList.length && !this.curResourceData.type) {
            this.resourceTypeError = true;
            return;
          }
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
          if (this.curResourceData.type
            && !resourceInstances.length
            && this.resourceTypeData.resource_groups[this.groupIndex]
              .related_resource_types.some(e => e.empty)) {
            this.resourceInstanceError = true;
            return;
          }
          this.isSearchSystem = true;
          if (isClick) {
            this.resetPagination();
          }
          await this.fetchSearchUserGroup(resourceInstances, true);
        } else {
          this.isSearchSystem = false;
          await this.fetchUserGroupList(true);
        }
      },

      async fetchSearchUserGroup (resourceInstances, isTableLoading = true) {
        this.tableLoading = isTableLoading;
        const { current, limit } = this.pagination;
        if (this.searchParams.hasOwnProperty('id')) {
          if (!isNaN(Number(this.searchParams.id))) {
            this.searchParams.id = Number(this.searchParams.id);
          }
        }
        const params = {
            ...this.applyGroupData,
            ...this.searchParams,
            limit,
            offset: limit * (current - 1),
            resource_instances: resourceInstances || [],
            apply_disable: false
        };
        try {
          const { code, data } = await this.$store.dispatch('permApply/getJoinGroupSearch', params);
          const { count, results } = data;
          this.pagination.count = count || 0;
          this.tableList.splice(0, this.tableList.length, ...(results || []));
          this.emptyData.tipType = 'search';
          this.$nextTick(() => {
            const currentSelectedGroups = this.currentSelectedGroups.length
              ? this.currentSelectedGroups.map(item => item.id.toString()) : [];
            this.tableList.forEach((item) => {
              if (item.role_members && item.role_members.length) {
                item.role_members = item.role_members.map(v => {
                  return {
                    username: v,
                    readonly: false
                  };
                });
              }
              if (currentSelectedGroups.includes(item.id.toString())
                || this.curUserGroup.includes(item.id.toString())) {
                this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, true);
                this.currentSelectList.push(item);
              }
            });
          });
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.tableList = [];
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
          this.curSelectMenu = '';
          this.curInputText = '';
        }
      },

      async fetchUserGroupList (isTableLoading = true) {
        this.tableLoading = isTableLoading;
        this.setCurrentQueryCache(this.refreshCurrentQuery());
        const { current, limit } = this.pagination;
        // 删除接口无用字段
        delete this.searchParams.current;
        const params = {
            ...this.searchParams,
            limit,
            offset: limit * (current - 1),
            apply_disable: false
        };
        try {
          const { code, data } = await this.$store.dispatch('userGroup/getUserGroupList', params);
          const { count, results } = data;
          this.pagination.count = count || 0;
          this.tableList.splice(0, this.tableList.length, ...(results || []));
          this.$nextTick(() => {
            const currentSelectedGroups = this.currentSelectedGroups.length
              ? this.currentSelectedGroups.map(item => item.id.toString()) : [];
            this.tableList.forEach((item) => {
              if (item.role_members && item.role_members.length) {
                item.role_members = item.role_members.map(v => {
                  return {
                    username: v,
                    readonly: false
                  };
                });
              }
              if (currentSelectedGroups.includes(item.id.toString())
                || this.curUserGroup.includes(item.id.toString())) {
                this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, true);
                this.currentSelectList.push(item);
              }
            });
          });
          this.emptyData = formatCodeData(code, this.emptyData, count === 0);
        } catch (e) {
          console.error(e);
          this.emptyData = formatCodeData(e.code, this.emptyData);
          this.tableList = [];
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
        // 先注释掉此方法，新版交互用得到
        // this.formatCheckedUserGroup();
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
        // this.formatCheckedUserGroup();
      },

      // 处理权限获得者是非空并且不包含自己，不勾选个人已申请的用户组
      formatCheckedUserGroup () {
        const allList = [...this.users, ...this.departments];
        const isMine = allList.find(item => item.username === this.user.username);
        const currentSelectedGroups = this.currentSelectedGroups.map(item => item.id.toString());
        this.curUserGroup = _.cloneDeep(this.defaultSelectedIds);
        this.tableList.forEach(item => {
          if (isMine || !allList.length) {
            this.currentSelectedGroups = this.currentSelectedGroups.filter(
              v => !this.curUserGroup.includes(v.id.toString()));
            if (currentSelectedGroups.includes(item.id.toString())
              || this.curUserGroup.includes(item.id.toString())) {
              this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, true);
            }
          } else {
            if (this.curUserGroup.includes(item.id.toString())) {
              this.$refs.groupTableRef && this.$refs.groupTableRef.toggleRowSelection(item, false);
            }
          }
        });
        // 处理有选择权限获得者并不包含自己的情况
        if (!isMine && allList.length) {
          this.curUserGroup = [];
        }
      },

      setDefaultSelect (payload) {
        return !this.curUserGroup.includes(payload.id.toString());
      },

      resetPagination () {
        this.currentSelectList = [];
        this.pagination = Object.assign(
          {},
          {
            limit: 10,
            current: 1,
            count: 0
          }
        );
      },

      resetSearchParams () {
        this.applyGroupData = Object.assign({}, {
          system_id: '',
          action_id: ''
        });
        this.curResourceData = Object.assign({}, {
          type: ''
        });
        this.systemIdError = false;
        this.actionError = false;
        this.resourceTypeError = false;
        this.resourceInstanceError = false;
        this.isSearchSystem = false;
        this.resourceInstances = [];
        this.resetLocationHref();
      },

      resetLocationHref () {
        // 需要删除的url上的字段
        const urlFields = [...this.initSearchData.map(item => item.id), ...['current', 'limit']];
        delLocationHref(urlFields);
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination = Object.assign(this.pagination, { current: page });
        this.queryParams = Object.assign(this.queryParams, { current: page });
        this.handleSearchUserGroup();
        // this.isSearchSystem ? this.fetchSearchUserGroup() : this.fetchUserGroupList(true);
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: currentLimit });
        this.queryParams = Object.assign(this.queryParams, { current: 1, limit: currentLimit });
        this.handleSearchUserGroup();
        // this.isSearchSystem ? this.fetchSearchUserGroup() : this.fetchUserGroupList(true);
      },

      async fetchSystemList () {
        try {
          const params = {};
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const { data } = await this.$store.dispatch('system/getSystems', params);
          this.systemList = data || [];
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          // this.requestQueue.shift()
        }
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
      
      handleClickMenu (payload) {
        const { menu } = payload;
        if (menu.id) {
          this.curSelectMenu = menu.id;
        }
      },

      handleSearchInput (payload) {
        const { text } = payload;
        this.curInputText = text;
      },

      handleSearch (payload, result) {
        this.currentSelectList = [];
        this.searchParams = payload;
        this.searchList = [...result];
        this.curSelectMenu = '';
        this.curInputText = '';
        this.emptyData.tipType = 'search';
        this.resetPagination();
        this.handleSearchUserGroup();
        if (!result.length) {
          this.resetLocationHref();
        }
      },

      async handleClearSearch () {
        this.applyGroupData.action_id = '';
        this.curResourceData.type = '';
        this.resourceInstances = [];
        this.emptyData.tipType = '';
        this.resetPagination();
        this.handleSearchUserGroup();
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

      fetchSelectedGroups (type, payload, row) {
        this.isShowGroupError = false;
        const typeMap = {
          multiple: () => {
            const isChecked = payload.length && payload.indexOf(row) !== -1;
            if (isChecked) {
              this.currentSelectedGroups.push(row);
            } else {
              this.currentSelectedGroups = this.currentSelectedGroups.filter(
                (item) => item.id.toString() !== row.id.toString()
              );
            }
          },
          all: () => {
            const list = payload.filter(item => !this.curUserGroup.includes(item.id.toString()));
            this.currentSelectList = _.cloneDeep(list);
            const tableList = _.cloneDeep(this.tableList);
            const selectGroups = this.currentSelectedGroups.filter(item =>
              !tableList.map(v => v.id.toString()).includes(item.id.toString()));
            this.currentSelectedGroups = [...selectGroups, ...list];
          }
        };
        return typeMap[type]();
      },

      handlerAllChange (selection) {
        this.fetchSelectedGroups('all', selection);
      },

      handlerChange (selection, row) {
        this.fetchSelectedGroups('multiple', selection, row);
      },

      handleClearGroups () {
        this.tableList.forEach((item) => {
          if (!this.curUserGroup.includes(item.id.toString())) {
            this.$refs.groupTableRef
              && this.$refs.groupTableRef.toggleRowSelection(item, false);
          }
        });
        this.currentSelectedGroups = [];
      },

      handleCloseTag (payload) {
        const index = this.currentSelectedGroups.findIndex(item => item.id === payload.id);
        const tableIndex = this.tableList.findIndex(item => item.id === payload.id);
        this.$refs.groupTableRef
          && this.$refs.groupTableRef.toggleRowSelection(this.tableList[tableIndex], false);
        this.currentSelectedGroups.splice(index, 1);
      },

      async fetchCurUserGroup () {
        try {
          const { data, code } = await this.$store.dispatch('perm/getPersonalGroups', {
            page_size: 10000,
            page: 1
          });
          if (data.results && data.results.length) {
            const groupIdList = [];
            const tableData = data.results.filter((item) => item.department_id === 0);
            tableData.forEach((item) => {
              groupIdList.push(item.id);
              if (item.role_members && item.role_members.length) {
                item.role_members = item.role_members.map((v) => {
                  return {
                    username: v,
                    readonly: false
                  };
                });
              }
            });
            this.curUserGroup = _.cloneDeep(groupIdList);
            this.defaultSelectedIds = _.cloneDeep(groupIdList);
            this.defaultSelectedGroups = _.cloneDeep(tableData || []);
          }
          this.emptyData = formatCodeData(code, this.emptyData, this.curUserGroup.length === 0);
        } catch (e) {
          this.$emit('toggle-loading', false);
          this.emptyData = formatCodeData(e.code, this.emptyData);
          console.error(e);
          this.curUserGroup = [];
          this.currentSelectedGroups = [];
          this.defaultSelectedGroups = [];
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
            
      async handleResourceSubmit () {
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
        this.resourceInstanceSideSliderTitle = '';
        this.isShowResourceInstanceSideSlider = false;
        this.curResIndex = -1;
        this.resourceInstanceError = false;
      },

      async handleSubmit () {
        const subjects = [];
        const groupsList = [...this.currentSelectedGroups];
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
        // 新版交互前，先采取只提交手动勾选的数据的临时方案
        // if (subjects.length) {
        //   const isOther = subjects.filter(item => item.id !== this.user.username);
        //   if (isOther.length) {
        //     // 如果权限获得者既包含了自己也包含了他人，就提交已申请过的加上勾选的
        //     const isMine = subjects.find(item => item.id === this.user.username);
        //     if (isMine) {
        //       // 这里需要产品优化既包含了自己也包含了他人，单独提交已申请过了的用户组会报错，所以这里还需要判断下有没有勾选
        //       if (!this.currentSelectedGroups.length) {
        //         this.isShowGroupError = true;
        //         this.scrollToLocation(this.$refs.selectTableRef);
        //         return;
        //       }
        //       groupsList = [...this.defaultSelectedGroups, ...this.currentSelectedGroups];
        //     }
        //   }
        // }
        if (!groupsList.length) {
          this.isShowGroupError = true;
          this.scrollToLocation(this.$refs.selectTableRef);
          return;
        }
        if (!this.reason) {
          this.isShowReasonError = true;
          this.scrollToLocation(this.$refs.reasonRef);
          return;
        }
        if (this.expiredAtUse === 0) {
          this.isShowExpiredError = true;
          this.scrollToLocation(this.$refs.expiredAtRef);
          return;
        }
        this.submitLoading = true;
        if (this.expiredAtUse === 15552000) {
          this.expiredAtUse = this.handleExpiredAt();
        }
        const params = {
          expired_at: this.expiredAtUse,
          reason: this.reason,
          groups: groupsList.map(({ id, name, description }) => ({ id, name, description })),
          // groups: this.currentSelectList.map(({ id, name, description }) => ({ id, name, description })),
          applicants: subjects
        };
        try {
          await this.$store.dispatch('permApply/applyJoinGroup', params);
          this.messageSuccess(this.$t(`m.info['申请已提交']`), 3000);
          this.$router.push({
            name: 'apply'
          });
        } catch (e) {
          console.error(e);
          if (['admin'].includes(this.user.username)) {
            this.isShowConfirmDialog = true;
          } else {
            this.messageAdvancedError(e);
          }
        } finally {
          this.submitLoading = false;
        }
      },

      handleResourceCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(() => {
          this.isShowResourceInstanceSideSlider = false;
          this.resetDataAfterClose();
        }, _ => _);
      },

      resetDataAfterClose () {
        this.curResIndex = -1;
        this.groupIndex = -1;
        this.params = {};
        this.resourceInstanceSideSliderTitle = '';
      },
            
      refreshCurrentQuery () {
        const params = {};
        const queryParams = {
          ...this.searchParams,
          // ...this.$route.query,
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

      handleCancel () {
        this.$router.push({
          name: 'permApply'
        });
      },

      handleResetResourceData () {
        if (this.resourceTypeData.resource_groups && !this.resourceTypeData.resource_groups.length) {
          this.resourceTypeData.resource_groups = [].concat([{ isEmpty: true }]);
        }
        this.$set(this.resourceTypeData.resource_groups[0], 'related_resource_types', this.defaultResourceTypeList);
        this.$set(this.resourceTypeData.resource_groups[0], 'related_resource_types_list', []);
        this.$set(this.resourceTypeData.resource_groups[0], 'isEmpty', true);
      }
    }
  };
</script>
<style lang="postcss">
  @import '@/css/mixins/manage-members-detail-slidesider.css';
  @import '@/css/mixins/apply-join-group-search.css';
  .iam-join-user-group-wrapper {
    .user-group-table {
        margin-top: 10px;
        border-right: none;
        border-bottom: none;
        &-selected {
          margin-top: 0;
        }
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
    .apply-selected-groups {
      padding: 10px 0;
      &-header {
        font-size: 12px;
        &-count {
          color: #3a84ff;
        }
        &-clear {
          color: #3a84ff;
          cursor: pointer;
        }
      }
      .group-tag-close {
        margin: 10px 6px 0 0;
        background: #f5f6fa;
        border: 1px solid #dcdee5;
      }
    }
    /* .can-view {
        color: #3a84ff;
        cursor: pointer;
        &:hover {
            color: #699df4;
        }
    } */
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
</style>

<style lang="postcss" scoped>
/deep/ .bk-page.bk-page-align-right {
  .bk-page-selection-count-left {
    display: none;
  }
}
</style>
