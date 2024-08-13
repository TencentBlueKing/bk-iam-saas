<template>
  <div class="my-perm-right-layout">
    <template v-if="!isHideResourceSearch">
      <IamResourceCascadeSearch
        ref="iamResourceSearchRef"
        :custom-class="'my-perm-resource-search'"
        :is-full-screen="true"
        :is-custom-search="true"
        :cur-search-data="searchData"
        :grid-count="gridCount"
        :form-item-margin="16"
        :nav-stick-padding="16"
        :other-layout-width="leftLayoutWidth"
        @on-remote-table="handleRemoteTable"
        @on-refresh-table="handleRefreshTable"
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
                @clear="handleClearName"
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
              :label="$t(`m.common['描述']`)"
              :style="{ width: formItemWidth }"
              class="custom-form-item"
            >
              <bk-input
                v-model="formData.description"
                :clearable="true"
                :placeholder="$t(`m.verify['请输入']`)"
                :right-icon="'bk-icon icon-search'"
                @right-icon-click="handleSearch"
                @enter="handleSearch"
                @clear="handleClearDescription"
              />
            </iam-form-item>
            <iam-form-item
              :style="{ width: formItemWidth }"
              class="custom-form-item custom-operate-item"
            >
              <bk-button
                theme="primary"
                :outline="true"
                @click="handleSearch">
                {{ $t(`m.common['查询']`) }}
              </bk-button>
              <bk-button
                theme="default"
                @click="handleReset">
                {{ $t(`m.common['重置']`) }}
              </bk-button>
            </iam-form-item>
          </bk-form>
        </div>
      </IamResourceCascadeSearch>
    </template>
    <div
      :class="[
        'flex-between',
        'batch-perm-operate',
        { 'no-resource-search': isHideResourceSearch }
      ]"
    >
      <div class="batch-perm-operate-item">
        <bk-dropdown-menu
          class="operate-dropdown-menu"
          ref="batchDropdown"
          :disabled="isBatchDisabled"
          @show="handleDropdownShow"
          @hide="handleDropdownHide"
        >
          <div
            v-bk-tooltips="{
              placement: 'right',
              content: $t(`m.perm['请先勾选批量操作的对象']`),
              disabled: !isBatchDisabled
            }"
            slot="dropdown-trigger"
            class="group-dropdown-trigger-btn"
          >
            <span class="group-dropdown-text">{{ $t(`m.userOrOrg['批量操作']`) }}</span>
            <i :class="['bk-icon icon-angle-down', { 'icon-flip': isDropdownShow }]" />
          </div>
          <ul class="bk-dropdown-list" slot="dropdown-content">
            <li>
              <a
                v-bk-tooltips="{
                  placement: 'right-start',
                  content: formatOperateTip('quit'),
                  disabled: !isNoBatchQuit
                }"
                :class="[{ 'quit-disabled': isNoBatchQuit }]"
                :title="managerGroupTitle"
                @click.stop="handleBatch('quit')"
              >
                {{ $t(`m.perm['退出（用户组）']`) }}
              </a>
            </li>
            <li>
              <a
                v-bk-tooltips="{
                  placement: 'right-start',
                  content: formatOperateTip('renewal'),
                  disabled: !isNoBatchRenewal
                }"
                :class="[{ 'renewal-disabled': isNoBatchRenewal }]"
                :title="renewalGroupTitle"
                @click.stop="handleBatch('renewal')"
              >
                {{ $t(`m.renewal['续期']`) }}
              </a>
            </li>
            <li>
              <a
                v-bk-tooltips="{
                  placement: 'right-start',
                  content: formatOperateTip('handover'),
                  disabled: !isNoBatchHandover
                }"
                :class="[{ 'handover-disabled': isNoBatchHandover }]"
                @click.stop="handleBatch('handover')"
              >
                {{ $t(`m.perm['交接']`) }}
              </a>
            </li>
            <li>
              <a
                v-bk-tooltips="{
                  placement: 'right-start',
                  content: $t(`m.perm['未勾选自定义操作选择前，无法选择删除']`),
                  disabled: !isNoBatchDelete
                }"
                :class="[{ 'remove-disabled': isNoBatchDelete }]"
                :title="managerGroupTitle"
                @click.stop="handleBatch('deleteAction')"
              >
                {{ $t(`m.perm['删除（自定义操作权限）']`) }}
              </a>
            </li>
          </ul>
        </bk-dropdown-menu>
      </div>
      <div class="batch-perm-operate-search" v-if="isHideResourceSearch">
        <IamSearchSelect
          style="width: 559px;"
          :data="formatSearchData"
          :value="searchList"
          :placeholder="$t(`m.levelSpace['输入管理员名称']`)"
          @on-change="handleSelectSearch"
        />
      </div>
    </div>
    <MultiTypeGroupPerm
      :group-data="groupData"
      @on-selected-group="handleSelectGroupPerm"
      @on-clear="handleClearSearch"
    />
    <!-- 批量操作组件 -->
    <BatchOperateSlider
      :slider-width="batchSliderWidth"
      :is-batch="false"
      :show.sync="isShowBatchSlider"
      :cur-slider-name="curSliderName"
      :title="batchSliderTitle"
      :group-data="groupData"
      :group-list="sliderGroupPermList"
      @on-slider-submit="handleOperateSubmit"
    />

    <RenderGroupPermSideSlider
      :show="isShowPermSideSlider"
      :is-batch-slider="isShowBatchSlider"
      :name="curGroupName"
      :group-id="curGroupId"
      @animation-end="handleAnimationEnd"
    />
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { mapGetters } from 'vuex';
  import { bus } from '@/common/bus';
  import { getNowTimeExpired } from '@/common/util';
  import IamSearchSelect from '@/components/iam-search-select';
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';
  import MultiTypeGroupPerm from './multi-type-group-perm.vue';
  import BatchOperateSlider from './batch-operate-slider.vue';
  import RenderGroupPermSideSlider from '../components/render-group-perm-side-slider';
  export default {
    provide: function () {
      return {
        getResourceSliderWidth: () => this.resourceSliderWidth
      };
    },
    components: {
      IamSearchSelect,
      IamResourceCascadeSearch,
      MultiTypeGroupPerm,
      BatchOperateSlider,
      RenderGroupPermSideSlider
    },
    props: {
      groupData: {
        type: Object
      },
      leftLayoutWidth: {
        type: Number,
        default: 240
      }
    },
    data () {
      return {
        enableGroupInstanceSearch: window.ENABLE_GROUP_INSTANCE_SEARCH.toLowerCase() === 'true',
        isSearchPerm: false,
        isDropdownShow: false,
        isShowBatchSlider: false,
        isShowPermSideSlider: false,
        batchSliderTitle: '',
        curSliderName: '',
        curGroupName: '',
        curGroupId: '',
        formItemWidth: '',
        renewalGroupTitle: '',
        managerGroupTitle: '',
        batchSliderWidth: 960,
        gridCount: 4,
        userOrOrgCount: 0,
        comKey: -1,
        searchData: [
          {
            id: 'name',
            name: this.$t(`m.userGroup['用户/组织名']`),
            default: true
          },
          {
            id: 'id',
            name: this.$t(`m.userOrOrg['用户组 ID']`),
            default: true
          },
          {
            id: 'description',
            name: this.$t(`m.common['描述']`),
            default: true
          }
        ],
        searchList: [],
        currentSelectList: [],
        sliderGroupPermList: [],
        formData: {
          name: '',
          manager_name: '',
          id: '',
          description: ''
        },
        curSearchPagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        curSearchParams: {},
        curSystemAction: {},
        curResourceData: {},
        resourceSliderWidth: Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7)
      };
    },
    computed: {
      ...mapGetters(['navStick']),
      isHideResourceSearch () {
        return ['managerPerm'].includes(this.groupData.value);
      },
      isAdminGroup () {
        return (payload) => {
          if (payload) {
            const { attributes, role_members } = payload;
            if (attributes && attributes.source_from_role && role_members.length === 1) {
              return true;
            }
            return false;
          }
        };
      },
      isBatchDisabled () {
        return !this.currentSelectList.length;
      },
      isNoBatchQuit () {
        // 只有个人用户组可以退出
        const personalPerm = this.currentSelectList.filter((item) => ['personalPerm', 'renewalPersonalPerm'].includes(item.mode_type) && item.department_id === 0 && !this.isAdminGroup(item));
        return !(personalPerm.length > 0);
      },
      isNoBatchDelete () {
        // 只有自定义权限可以删除
        const customPerm = this.currentSelectList.filter((item) => ['customPerm', 'renewalCustomPerm'].includes(item.mode_type));
        return !(customPerm.length > 0);
      },
      isNoBatchHandover () {
        if (this.currentSelectList.length > 0) {
          const expiredGroup = this.currentSelectList.filter((item) =>
            ['personalPerm', 'customPerm', 'renewalPersonalPerm', 'renewalCustomPerm'].includes(item.mode_type) && item.expired_at < getNowTimeExpired()
          );
          return expiredGroup.length === this.currentSelectList.length;
        }
        return !this.currentSelectList.length;
      },
      isNoBatchRenewal () {
        if (this.currentSelectList.length) {
          const expiredGroup = this.currentSelectList.filter((item) =>
            ['personalPerm', 'customPerm', 'renewalPersonalPerm', 'renewalCustomPerm'].includes(item.mode_type) && this.formatExpireSoon(item.expired_at)
          );
          return !(expiredGroup.length > 0);
        }
        return !this.currentSelectList.length;
      },
      formatExpireSoon () {
        return (payload) => {
          const dif = payload - getNowTimeExpired();
          const days = Math.ceil(dif / (24 * 3600));
          return days < 16;
        };
      },
      formatSearchData () {
        const typeMap = {
          managerPerm: () => {
            return [
              {
                id: 'manager_name',
                name: this.$t(`m.permTransfer['管理员名称']`),
                default: true
              }
            ];
          }
        };
        if (typeMap[this.groupData.value]) {
          return typeMap[this.groupData.value]();
        }
        return [];
      },
      formatOperateTip () {
        const renewalTypeList = ['personalPerm', 'customPerm', 'renewalPersonalPerm', 'renewalCustomPerm'];
        return (payload) => {
          const typeMap = {
            quit: () => {
              const personalPerm = this.currentSelectList.filter((item) => ['personalPerm', 'renewalPersonalPerm'].includes(item.mode_type));
              const noQuitList = personalPerm.filter((item) => item.department_id < 1 && this.isAdminGroup(item));
              if (!personalPerm.length || !this.currentSelectList.length) {
                return this.$t(`m.perm['未勾选用户组，无法选择退出']`);
              }
              if (noQuitList.length > 0 && this.currentSelectList.length === noQuitList.length) {
                return this.$t(`m.perm['唯一管理员不可退出']`);
              }
            },
            renewal: () => {
              const isExistRenewal = this.currentSelectList.find((item) => renewalTypeList.includes(item.mode_type));
              const selectGroup = this.currentSelectList.filter((item) =>
                renewalTypeList.includes(item.mode_type) && item.expired_at < getNowTimeExpired()
              );
              if (this.currentSelectList.length) {
                if (!selectGroup.length && !isExistRenewal) {
                  return this.$t(`m.perm['未勾选个人用户组权限或自定义操作选择前，无法去续期']`);
                }
                return this.$t(`m.renewal['没有需要续期的权限']`);
              }
              return this.$t(`m.perm['未勾选用户组，无法去续期']`);
            },
            handover: () => {
              const noHandoverList = this.currentSelectList.filter((item) =>
                renewalTypeList.includes(item.mode_type) && item.expired_at < getNowTimeExpired()
              );
              if (!this.currentSelectList.length) {
                return this.$t(`m.perm['未勾选用户组，无法去交接']`);
              }
              if (noHandoverList.length === this.currentSelectList.length) {
                return this.$t(`m.permTransfer['（通过组织加入、已过期的组无法交接）']`);
              }
            }
          };
          if (typeMap[payload]) {
            return typeMap[payload]();
          }
          return '';
        };
      }
    },
    watch: {
      navStick () {
        this.formatFormItemWidth();
      },
      groupData: {
        handler () {
          this.currentSelectList = [];
          this.sliderGroupPermList = [];
        },
        deep: true
      }
    },
    created () {
      this.formatFormItemWidth();
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
        bus.$off('on-batch-view-group-perm');
      });
      window.addEventListener('resize', this.formatFormItemWidth);
      bus.$on('on-batch-view-group-perm', ({ name, id, show, width }) => {
        this.isShowPermSideSlider = show;
        this.curGroupName = name;
        this.curGroupId = id;
        this.batchSliderWidth = width;
      });
    },
    methods: {
      fetchRemoteTable () {
        const params = {
          ...this.curSearchParams,
          ...this.formData
        };
        bus.$emit('on-refresh-resource-search', {
          isSearchPerm: this.isSearchPerm,
          curSearchParams: params,
          curSearchPagination: this.curSearchPagination
        });
      },

      handleSelectSearch (payload) {
        this.isSearchPerm = true;
        this.curSearchParams = {};
        this.curSearchPagination = Object.assign(this.curSearchPagination, { current: 1, limit: 10 });
        this.formData.manager_name = payload.manager_name || '';
        this.fetchRemoteTable();
      },

      handleRemoteTable (payload) {
        const { pagination, searchParams } = payload;
        const params = {
          ...searchParams,
          ...this.formData
        };
        this.isSearchPerm = !!(searchParams.system_id || Object.values(this.formData).some((v) => v !== ''));
        this.curSearchParams = cloneDeep(params);
        this.curSearchPagination = cloneDeep(pagination);
        this.fetchRemoteTable();
      },

      handleRefreshTable () {
        this.curEmptyData.tipType = '';
        this.isSearchPerm = false;
        this.curSearchParams = {};
        this.fetchRemoteTable();
      },

      handleSelectGroupPerm (payload) {
        this.currentSelectList = [...payload];
      },

      handleClearName () {
        this.formData.name = '';
        this.handleSearch();
      },

      handleClearDescription () {
        this.formData.description = '';
        this.handleSearch();
      },

      handleSearch () {
        this.$nextTick(() => {
          this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleSearchUserGroup(true, true);
        });
      },

      handleClearSearch () {
        this.isSearchPerm = false;
        this.curSearchParams = {};
        this.formData = Object.assign({
          name: '',
          id: '',
          description: ''
        });
        this.searchList = [];
        if (['managerPerm'].includes(this.groupData.value)) {
          this.fetchRemoteTable();
          return;
        }
        this.$nextTick(() => {
          this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyClear();
        });
      },

      handleBatch (payload) {
        const renewalTypeList = ['personalPerm', 'customPerm', 'renewalPersonalPerm', 'renewalCustomPerm'];
        const typeMap = {
          quit: () => {
            if (!this.isNoBatchQuit) {
              this.curSliderName = 'quit';
              this.batchSliderTitle = this.$t(`m.perm['批量退出用户组']`);
              this.sliderGroupPermList = this.currentSelectList.filter((item) => ['personalPerm', 'renewalPersonalPerm'].includes(item.mode_type));
              this.isShowBatchSlider = true;
            }
          },
          renewal: () => {
            const selectGroup = this.currentSelectList.filter((item) =>
              renewalTypeList.includes(item.mode_type) && this.formatExpireSoon(item.expired_at)
            );
            if (!this.isNoBatchRenewal && selectGroup.length > 0) {
              const list = selectGroup.map((item) => {
                if (['customPerm', 'renewalCustomPerm'].includes(item.mode_type)) {
                  this.$set(item, 'policy', { policy_id: item.policy_id, name: item.name });
                }
                return item;
              });
              this.$store.commit('perm/updateRenewalData', list);
              this.$router.push({
                name: 'permRenewal',
                query: {
                  isBatch: true
                }
              });
            }
          },
          handover: () => {
            if (!this.isNoBatchHandover) {
              const list = this.currentSelectList.filter((item) =>
                (renewalTypeList.includes(item.mode_type) && item.expired_at >= getNowTimeExpired())
                || ['managerPerm'].includes(item.mode_type)
              );
              this.$store.commit('perm/updateHandoverData', list);
              this.$router.push({
                name: 'permTransfer',
                query: {
                  isBatch: true
                }
              });
            }
          },
          deleteAction: () => {
            if (!this.isNoBatchDelete) {
              this.curSliderName = 'deleteAction';
              this.batchSliderTitle = this.$t(`m.perm['批量删除操作权限']`);
              this.sliderGroupPermList = this.currentSelectList.filter((item) => ['customPerm', 'renewalCustomPerm'].includes(item.mode_type));
              this.isShowBatchSlider = true;
            }
          }
        };
        return typeMap[payload]();
      },

      handleReset () {
        this.handleRefreshGroup();
        this.$nextTick(() => {
          this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleEmptyClear();
        });
      },

      handleOperateSubmit ({ list, type }) {
        const typeMap = {
          quit: () => {
            this.currentSelectList = this.currentSelectList.filter((v) => list.includes(v.id));
          },
          deleteAction: () => {
            this.currentSelectList = this.currentSelectList.filter((v) => list.includes(v.policy_id));
          }
        };
        return typeMap[type]();
      },

      handleToggleExpand () {
        this.formatFormItemWidth();
        this.$nextTick(() => {
          this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.formatFormItemWidth();
        });
      },
      
      handleDropdownShow () {
        this.isDropdownShow = true;
      },

      handleDropdownHide () {
        this.isDropdownShow = false;
      },

      handleRefreshGroup () {
        this.sliderGroupPermList = [];
        this.curSearchParams = {};
        this.formData = Object.assign(this.formData, {
          name: '',
          manager_name: '',
          id: '',
          description: ''
        });
        this.isSearchPerm = false;
      },
      
      handleAnimationEnd () {
        this.curGroupName = '';
        this.curGroupId = '';
        this.isShowPermSideSlider = false;
        this.batchSliderWidth = 960;
      },

      formatFormItemWidth () {
        this.resourceSliderWidth = Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7);
        this.formItemWidth = `${(window.innerWidth - this.leftLayoutWidth - (this.navStick ? 276 : 76) - this.gridCount * 16) / this.gridCount}px`;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.my-perm-right-layout {
  width: 100%;
  height: calc(100vh - 114px);
  overflow: hidden;
  .batch-perm-operate {
    margin-bottom: 12px;
    &-item {
      margin-right: 8px;
      .operate-dropdown-menu {
        .group-dropdown-trigger-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 32px;
          min-width: 108px;
          border-radius: 2px;
          padding-left: 10px;
          padding-right: 5px;
          color: #ffffff;
          &:hover {
            cursor: pointer;
            border-color: #979ba5;
          }
          .group-dropdown-text {
            font-size: 14px;
          }
          .bk-icon {
            font-size: 22px;
          }
        }
      }
    }
    &.no-resource-search {
      padding-top: 16px;
    }
  }
  /deep/ .operate-dropdown-menu {
    background-color: #3a84ff;
    .group-dropdown-trigger-btn {
      color: #ffffff;
      &:hover {
        border-color: #3a84ff;
      }
    }
    .bk-dropdown-content {
      padding-top: 0;
      cursor: pointer;
    }
    &.disabled,
    &.disabled *,
    .quit-disabled,
    .handover-disabled,
    .remove-disabled,
    .renewal-disabled {
      background-color: #ffffff !important;
      border-color: #dcdee5 !important;
      color: #c4c6cc !important;
      cursor: not-allowed;
    }
    &.disabled,
    &.disabled * {
      background-color: #dcdee5 !important;
      color: #ffffff !important;
      div:nth-child(2) {
        height: 0 !important;
      }
    }
  }
  /deep/ .my-perm-resource-search {
    background-color: #f5f6fa;
    padding: 0;
    padding-top: 12px;
    margin-bottom: 12px;
    .form-item-resource {
      .bk-select {
        background-color: #ffffff;
      }
    }
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
    .custom-content {
      &-form {
        display: flex;
        .custom-form-item {
          margin-top: 12px;
          margin-right: 16px;
          &:last-child {
            margin-right: 0;
          }
          &.custom-operate-item {
            padding-top: 32px;
            font-size: 0;
            .bk-form-content {
              .bk-button {
                font-size: 14px;
                margin-right: 8px;
                &:last-child {
                  margin-right: 0;
                }
              }
            }
          }
        }
      }
      &-no-search {
        .custom-content-form {
          .custom-form-item {
            margin-top: 0;
          }
        }
      }
    }
    &.no-search-data {
      display: none;
    }
  }
}
</style>
