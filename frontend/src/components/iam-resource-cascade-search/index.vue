<template>
  <div>
    <div
      ref="selectTableRef"
      :class="[
        'iam-search-resource-form',
        'iam-search-resource-form-perm',
        { [customClass]: customClass }
      ]">
      <render-search v-if="enableGroupInstanceSearch">
        <div
          :class="[
            'join-user-group-form',
            { 'join-user-group-form-lang': !curLanguageIsCn }
          ]">
          <div>
            <bk-form
              form-type="vertical"
              class="resource-action-form">
              <iam-form-item
                :label="$t(`m.common['系统']`)"
                class="form-item-resource">
                <bk-select
                  :style="{ width: contentWidth }"
                  v-model="applyGroupData.system_id"
                  :clearable="!externalSystemsLayout.myPerm.hideApplyBtn"
                  :allow-enter="false"
                  :placeholder="$t(`m.verify['请选择']`)"
                  @change="handleCascadeChange"
                  @clear="handleClearSearch"
                  searchable>
                  <bk-option v-for="option in systemSelectList"
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
                class="form-item-resource"
              >
                <bk-select
                  :style="{ width: contentWidth }"
                  v-model="applyGroupData.action_id"
                  :clearable="false"
                  :allow-enter="false"
                  :placeholder="$t(`m.verify['请选择']`)"
                  :disabled="!applyGroupData.system_id"
                  :title="!applyGroupData.system_id ? $t(`m.verify['请选择系统']`) : ''"
                  @selected="handleSelectedAction"
                  searchable>
                  <bk-option v-for="option in processesList"
                    :key="option.id"
                    :id="option.id"
                    :name="`${option.name} (${option.id})`">
                  </bk-option>
                </bk-select>
                <p class="error-tips" v-if="actionIdError">
                  {{$t(`m.verify['请选择操作']`)}}
                </p>
              </iam-form-item>
              <template>
                <div
                  v-for="(_, index) in resourceTypeData.resource_groups"
                  :key="_.id"
                  class="resource-group-container">
                  <iam-form-item
                    :label="$t(`m.permApply['资源类型']`)"
                    class="form-item-resource">
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
                  <iam-form-item
                    class="form-item-resource"
                    :label="$t(`m.common['资源实例']`)">
                    <div class="relation-content-item"
                      v-for="(content, contentIndex) in _.related_resource_types"
                      :key="contentIndex">
                      <div class="content"
                        :style="{ width: contentWidth }"
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
          <template>
            <div :class="['custom-slot-content']" v-if="isCustomSearch">
              <slot name="custom-content" />
            </div>
            <div class="group-search-select" v-else>
              <iam-search-select
                style="width: calc(100% - 20px)"
                ref="searchSelectRef"
                :data="searchData"
                :value="searchValue"
                :placeholder="searchSelectPlaceHolder"
                :quick-search-method="handleQuickSearchMethod"
                @on-change="handleSearch"
                @on-click-menu="handleClickMenu"
                @on-input="handleSearchInput"
              />
              <bk-button
                class="ml20"
                theme="primary"
                :outline="true"
                @click="handleSearchUserGroup(true, true)">
                {{ $t(`m.common['查询']`) }}
              </bk-button>
              <bk-button
                class="ml20"
                theme="default"
                @click="handleEmptyClear">
                {{ $t(`m.common['重置']`) }}
              </bk-button>
            </div>
          </template>
        </div>
      </render-search>
      <div
        v-else
        class="no-resource-search-wrapper">
        <template v-if="isCustomSearch">
          <slot name="custom-content" />
        </template>
        <template v-else>
          <iam-search-select
            ref="searchSelectRef"
            @on-change="handleSearch"
            :data="searchData"
            :value="searchValue"
            :placeholder="searchSelectPlaceHolder"
            :quick-search-method="handleQuickSearchMethod"
          />
        </template>
      </div>
    </div>
    
    <bk-sideslider
      :is-show="isShowResourceInstanceSideSlider"
      :title="resourceInstanceSideSliderTitle"
      :width="resourceSliderWidth"
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
        <bk-button theme="primary" @click="handleResourceSubmit">
          {{ $t(`m.common['保存']`) }}
        </bk-button>
        <bk-button style="margin-left: 10px;" @click="handleResourceCancel">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import _ from 'lodash';
  import il8n from '@/language';
  import Policy from '@/model/policy';
  import RenderCondition from '@/views/resource-permiss/components/render-condition';
  import RenderResource from '@/views/resource-permiss/components/render-resource';
  import IamSearchSelect from '@/components/iam-search-select';
  import { mapGetters } from 'vuex';
  import { leaveConfirm } from '@/common/leave-confirm';
  import { delLocationHref } from '@/common/util';
  
  export default {
    provide: function () {
      return {
        getResourceSliderWidth: () => this.resourceSliderWidth
      };
    },
    components: {
      RenderResource,
      RenderCondition,
      IamSearchSelect
    },
    props: {
      active: {
        type: String,
        default: 'GroupPerm'
      },
      minSelectWidth: {
        type: String,
        default: '200px'
      },
      maxSelectWidth: {
        type: String,
        default: '240px'
      },
      customClass: {
        type: String,
        default: ''
      },
      isFullScreen: {
        type: Boolean,
        default: false
      },
      searchSelectPlaceHolder: {
        type: String,
        default: il8n('applyEntrance', '申请加入用户组搜索提示')
      },
      isCustomSearch: {
        type: Boolean,
        default: false
      },
      gridCount: {
        type: Number,
        default: 4
      },
      curSearchData: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        enableGroupInstanceSearch: window.ENABLE_GROUP_INSTANCE_SEARCH.toLowerCase() === 'true',
        CUR_LANGUAGE: window.CUR_LANGUAGE,
        applyGroupData: {
          system_id: '',
          action_id: ''
        },
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
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
        initSearchData: [
          {
            id: 'name',
            name: this.$t(`m.userGroup['用户组名']`),
            default: true
          },
          // {
          //   id: 'id',
          //   name: 'ID',
          //   default: true
          // },
          {
            id: 'description',
            name: this.$t(`m.common['描述']`),
            default: true
          }
        ],
        searchData: [],
        curResourceData: {
          type: ''
        },
        searchParams: {},
        searchList: [],
        searchValue: [],
        curResourceTypeList: [],
        systemSelectList: [],
        processesList: [],
        resourceInstances: [],
        resourceActionData: [],
        isShowConfirmDialog: false,
        confirmDialogTitle: this.$t(`m.verify['admin无需申请权限']`),
        systemIdError: false,
        actionIdError: false,
        searchTypeError: false,
        resourceTypeError: false,
        resourceInstanceError: false,
        isShowResourceInstanceSideSlider: false,
        isSearchSystem: false,
        groupIndex: -1,
        curResIndex: -1,
        curCopyParams: {},
        params: {},
        queryParams: {},
        searchUserGroupList: [],
        searchDepartGroupList: [],
        searchSystemPolicyList: [],
        resourceInstanceSideSliderTitle: '',
        curSelectMenu: '',
        curInputText: '',
        contentWidth: '',
        resourceSliderWidth: Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7)
      };
    },
    computed: {
      ...mapGetters(['externalSystemsLayout', 'externalSystemId', 'navStick']),
      condition () {
          if (this.curResIndex === -1 || this.groupIndex === -1) {
              return [];
          }
          this.curResourceData = this.resourceTypeData.resource_groups[this.groupIndex]
              .related_resource_types[this.curResIndex];
          if (!this.curResourceData) {
              return [];
          }
          // if (this.curResourceData.condition.length === 0) this.curResourceData.condition = ['none'];
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
      active: {
        async handler (newValue, oldValue) {
          if (oldValue && oldValue !== newValue) {
            if (this.searchList.length) {
              await this.handleSearchUserGroup(true, false);
            }
          }
        },
        immediate: true
      },
      externalSystemId: {
        handler (value) {
          if (value) {
            this.applyGroupData.system_id = value;
            this.handleCascadeChange();
          }
        },
        immediate: true
      },
      applyGroupData: {
        handler (value) {
          const params = {};
          if (value.system_id) {
            const curData = this.systemSelectList.find((item) => item.id === value.system_id);
            if (curData) {
              params.system_id = {
                label: curData.name,
                value: curData.id
              };
            }
          }
          if (value.action_id) {
            const curData = this.processesList.find((item) => item.id === value.action_id);
            if (curData) {
              params.action_id = {
                label: curData.name,
                value: curData.id
              };
            }
          }
          // 用于判断自定义slot场景下，同步更新选中值
          this.$emit('on-select-system', params);
        },
        deep: true
      },
      curResourceData: {
        handler (value) {
          // 用于判断自定义slot场景下，同步更新选中值
          // 处理资源类型数据
          let params = {};
          const { type, condition } = value;
          const { resource_groups: resourceGroups } = this.resourceTypeData;
          if (resourceGroups && resourceGroups.length) {
            if (type && resourceGroups[0].related_resource_types_list
              && resourceGroups[0].related_resource_types_list.length
            ) {
              const curData = resourceGroups[0].related_resource_types_list.find((item) => item.type === type);
              if (curData) {
                params.resource_type = {
                  label: curData.name,
                  value: curData.type
                };
              }
            }
          }
          // 处理资源实例数据
          if (condition) {
            params = Object.assign(params, {
              condition
            });
          }
          this.$emit('on-select-resource', params);
        },
        deep: true
      },
      navStick () {
        this.formatFormItemWidth();
      }
    },
    async created () {
      this.formatFormItemWidth();
      this.formatSearchData();
      await this.fetchPermData();
    },
    mounted () {
      window.addEventListener('resize', (this.formatFormItemWidth));
      window.addEventListener('resize', (this.formatResourceSliderWidth));
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
        window.removeEventListener('resize', this.formatResourceSliderWidth);
      });
    },
    methods: {
      formatSearchData () {
        // 处理不同页面自定义搜索字段
        const isOtherRoute = ['userOrgPerm'].includes(this.$route.name);
        const routeMap = {
          true: () => {
            this.searchData = [...this.curSearchData];
          },
          false: () => {
            this.searchData = this.enableGroupInstanceSearch
              ? this.initSearchData.filter(item => ['name', 'id', 'description'].includes(item.id))
              : _.cloneDeep(this.initSearchData);
          }
        };
        return routeMap[isOtherRoute]();
      },

      async fetchPermData () {
        this.fetchSystemList();
        const isSearch = this.applyGroupData.system_id || Object.keys(this.searchParams).length > 0;
        if (isSearch) {
          await this.handleSearchUserGroup(false, false);
        }
      },

      async fetchSystemList () {
        try {
          const params = {};
          if (this.externalSystemId) {
            params.hidden = false;
            params.system_id = this.externalSystemId;
          }
          const { data } = await this.$store.dispatch('system/getSystems', params);
          this.systemSelectList = data || [];
          if (this.externalSystemId) {
            this.systemSelectList = this.systemSelectList.filter(item => item.id === this.externalSystemId);
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      async handleSearchUserGroup (isClick = false, isTagInput = false) {
        // isTagInput是处理未生成tag的内容
        this.systemIdError = false;
        this.handleManualInput(isTagInput);
        let isSearch = this.applyGroupData.system_id || Object.keys(this.searchParams).length > 0;
        // 处理搜索框没有生成tag，下拉框也没有选择任务数据，但实际有输入内容情况
        let isNoTag = isTagInput && this.searchList.length < 1 && !this.applyGroupData.system_id;
        // 处理自定义搜索slot，searchList为空情况
        if (this.isCustomSearch) {
          isSearch = true;
          isNoTag = false;
        }
        if (isSearch) {
          // if (!this.applyGroupData.system_id && ['CustomPerm'].includes(this.active)) {
          //   this.systemIdError = true;
          //   return;
          // }
          let resourceInstances = _.cloneDeep(this.resourceInstances);
          if (this.applyGroupData.system_id) {
            if (!this.applyGroupData.action_id) {
              this.actionIdError = true;
              return;
            }
            if (this.curResourceTypeList.length && !this.curResourceData.type) {
              this.resourceTypeError = true;
              return;
            }
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
            const hasResourceGroup = this.resourceTypeData.resource_groups[this.groupIndex];
            if (this.curResourceData.type
              && !resourceInstances.length
              && hasResourceGroup
              && hasResourceGroup.related_resource_types.some(e => e.empty)) {
              this.resourceInstanceError = true;
              return;
            }
          }
          if (isClick) {
            this.resetPagination();
          }
          await this.fetchSearchUserGroup(resourceInstances, isNoTag);
        } else {
          if (isNoTag) {
            return;
          }
          // 如果没有搜索参数，重置数据
          this.emptyData.tipType = '';
          this.$emit('on-refresh-table');
        }
      },

      async fetchSearchUserGroup (resourceInstances, isNoTag) {
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
            resource_instances: resourceInstances || []
        };
        this.$emit('on-remote-table', {
          searchParams: params,
          pagination: this.pagination,
          emptyData: { ...this.emptyData, ...{ tipType: 'search' } },
          isNoTag
        });
        this.curSelectMenu = '';
        this.curInputText = '';
      },

      async handleCascadeChange () {
        this.systemIdError = false;
        this.actionIdError = false;
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
        this.searchParams = payload;
        this.searchList = [...result];
        this.curSelectMenu = '';
        this.curInputText = '';
        this.emptyData.tipType = 'search';
        if (!result.length) {
          this.resetPagination();
          this.resetLocationHref();
        }
        this.handleSearchUserGroup(true, false);
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
        this.handleSearchUserGroup(false, false);
      },

      handleEmptyRefresh () {
        this.emptyData.tipType = '';
        if (this.$refs.searchSelectRef && this.$refs.searchSelectRef.$refs.searchSelect) {
          this.$refs.searchSelectRef.$refs.searchSelect.localValue = '';
        }
        this.resetPagination();
        this.handleSearchUserGroup(false, false);
      },

      async handleClearSearch () {
        this.applyGroupData.action_id = '';
        this.curResourceData.type = '';
        this.emptyData.tipType = '';
        this.resourceInstances = [];
        this.resetPagination();
        this.handleSearchUserGroup(false, false);
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
            // 如果related_resource_types和related_resource_types_list都为空，则需要填充默认数据显示资源实例下拉框
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

      // 处理手动输入各种场景
      handleManualInput (isTagInput) {
        if (this.curSelectMenu) {
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
          if (!this.searchList.length && isTagInput) {
            // 处理无tag标签，直接输入内容情况
            this.searchParams.name = this.curInputText;
            if (!this.curInputText) {
              delete this.searchParams.name;
            }
            this.$nextTick(() => {
              if (this.$refs.searchSelectRef && this.$refs.searchSelectRef.$refs.searchSelect) {
                const localValue = this.$refs.searchSelectRef.$refs.searchSelect.localValue;
                this.searchParams.name = localValue;
                if (!localValue) {
                  delete this.searchParams.name;
                }
                // 处理切换tab，只输入内容
                this.$emit('on-input-value', localValue);
              }
            });
          }
        }
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
        this.resourceInstanceSideSliderTitle = this.$t(`m.info['关联侧边栏操作的资源实例']`, { value: `${this.$t(`m.common['【']`)}${data.name}${this.$t(`m.common['】']`)}` });
        window.changeAlert = 'iamSidesider';
        this.isShowResourceInstanceSideSlider = true;
      },

      handleResetResourceData () {
        if (this.resourceTypeData.resource_groups && !this.resourceTypeData.resource_groups.length) {
          this.resourceTypeData.resource_groups = [].concat([{ isEmpty: true }]);
        }
        this.$set(this.resourceTypeData.resource_groups[0], 'related_resource_types', this.defaultResourceTypeList);
        this.$set(this.resourceTypeData.resource_groups[0], 'related_resource_types_list', []);
        this.$set(this.resourceTypeData.resource_groups[0], 'isEmpty', true);
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
        // 抛出选择后的实例数据处理自定义组件场景
        if (this.isCustomSearch) {
          this.$emit('on-select-instance', {
            resourceInstances: this.resourceInstances,
            resourceTypeData: this.resourceTypeData
          });
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

      formatResourceSliderWidth () {
        this.resourceSliderWidth = Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7);
      },

      formatFormItemWidth () {
        // 276代表菜单栏展开的宽度加16px内边距， 76代表菜单栏收缩的宽度加16px内边距
        this.defaultWidth = window.innerWidth <= 1520 ? this.minSelectWidth : this.maxSelectWidth;
        this.gridWidth = (window.innerWidth - (this.navStick ? 276 : 76) - this.gridCount * 16) / this.gridCount;
        this.contentWidth = this.isFullScreen ? `${this.gridWidth}px` : this.defaultWidth;
      },

      handleQuickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      },
      
      resetDataAfterClose () {
        this.curResIndex = -1;
        this.groupIndex = -1;
        this.params = {};
        this.resourceInstanceSideSliderTitle = '';
      },

      resetLocationHref () {
        // 需要删除的url上的字段
        const urlFields = [...this.initSearchData.map(item => item.id), ...['current', 'limit']];
        delLocationHref(urlFields);
      },

      resetPagination () {
        this.pagination = Object.assign(
          this.pagination,
          {
            limit: 10,
            current: 1,
            count: 0
          }
        );
      },
      
      resetSearchParams () {
        this.applyGroupData = Object.assign({}, {
          system_id: this.externalSystemId || '',
          action_id: ''
        });
        this.curResourceData = Object.assign({}, {
          type: ''
        });
        this.systemIdError = false;
        this.actionIdError = false;
        this.resourceTypeError = false;
        this.resourceInstanceError = false;
        this.resourceInstances = [];
        this.resetLocationHref();
      }
    }
  };

</script>

<style lang="postcss" scoped>
 @import '@/css/mixins/apply-join-group-search.css';
 .iam-search-resource-form-perm {
    background-color: #ffffff;
    padding: 20px;
    .resource-action-form {
      .form-item-resource {
        margin-right: 16px !important;
      }
    }
    /deep/ .resource-group-container {
      .form-item-resource {
        &:last-child {
          margin-right: 0 !important;
        }
        .relation-content-item {
          .iam-condition-input {
            height: 30px !important;
            line-height: 30px;
          }
        }
      }
    }
    .group-search-select {
      padding-top: 16px;
    }
    &.user-org-resource-perm {
      padding: 16px;
      padding-top: 12px;
      .left {
        .resource-action-form {
          .error-tips {
            position: absolute;
            line-height: 16px;
            font-size: 10px;
            color: #ea3636;
          }
        }
      }
    }
  }
</style>
