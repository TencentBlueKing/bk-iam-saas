<template>
  <div class="my-perm-right-layout">
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
              @clear="handleClearSearch"
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
              @clear="handleClearSearch"
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
    <div class="batch-perm-operate">
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
                :class="[{ 'quit-disabled': isNoBatchQuit }]"
                :title="managerGroupTitle"
                @click.stop="handleBatch('quit')"
              >
                {{ $t(`m.perm['退出（用户组）']`) }}
              </a>
            </li>
            <li>
              <a
                :class="[{ 'renewal-disabled': isNoBatchRenewal }]"
                :title="renewalGroupTitle"
                @click.stop="handleBatch('renewal')"
              >
                {{ $t(`m.renewal['续期']`) }}
              </a>
            </li>
            <li>
              <a
                :class="[{ 'handover-disabled': isNoBatchHandover }]"
                @click.stop="handleBatch('handover')"
              >
                {{ $t(`m.perm['交接']`) }}
              </a>
            </li>
            <li>
              <a
                :class="[{ 'remove-disabled': isNoBatchDelete }]"
                :title="managerGroupTitle"
                @click.stop="handleBatch('remove')"
              >
                {{ $t(`m.perm['删除（自定义操作权限）']`) }}
              </a>
            </li>
          </ul>
        </bk-dropdown-menu>
      </div>
    </div>
    <MultiTypeGroupPerm
      :group-data="groupData"
      @on-selected-group="handleSelectGroupPerm"
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
      @on-submit="handleOperateSubmit"
    />

    <RenderGroupPermSideSlider
      :show="isShowPermSideSlider"
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
            name: 'ID',
            default: true
          },
          {
            id: 'description',
            name: this.$t(`m.common['描述']`),
            default: true
          }
        ],
        currentSelectList: [],
        sliderGroupPermList: [],
        formData: {
          name: '',
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
        const personalPerm = this.currentSelectList.filter((item) => ['personalPerm'].includes(item.mode_type) && item.department_id === 0 && !this.isAdminGroup(item));
        return !(personalPerm.length > 0);
      },
      isNoBatchDelete () {
        // 只有自定义权限可以删除
        const customPerm = this.currentSelectList.filter((item) => ['customPerm'].includes(item.mode_type));
        return !(customPerm.length > 0);
      },
      isNoBatchHandover () {
        return !this.currentSelectList.length;
      },
      isNoBatchRenewal () {
        const selectGroup = this.currentSelectList.filter((item) =>
          ['personalPerm', 'customPerm'].includes(item.mode_type) && item.expired_at < getNowTimeExpired()
        );
        return !(selectGroup.length > 0);
      }
    },
    watch: {
      navStick () {
        this.formatFormItemWidth();
      }
    },
    created () {
      this.formatFormItemWidth();
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
        bus.$off('on-view-group-perm');
      });
      window.addEventListener('resize', this.formatFormItemWidth);
      bus.$on('on-view-group-perm', ({ name, id, show }) => {
        this.isShowPermSideSlider = show;
        this.curGroupName = name;
        this.curGroupId = id;
        this.batchSliderWidth = show ? 1160 : 960;
      });
    },
    methods: {
      async fetchRemoteTable () {
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

      handleRemoteTable (payload) {
        const { emptyData, pagination, searchParams } = payload;
        const params = {
          ...searchParams,
          ...this.formData
        };
        this.isSearchPerm = emptyData.tipType === 'search';
        this.curSearchParams = cloneDeep(params);
        this.curSearchPagination = cloneDeep(pagination);
        bus.$emit('on-refresh-resource-search', {
          isSearchPerm: this.isSearchPerm,
          curSearchPagination: this.curSearchPagination,
          curSearchParams: params
        });
      },

      handleRefreshTable () {

      },

      handleSelectGroupPerm (payload) {
        this.currentSelectList = [...payload];
      },

      handleSearch () {
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleSearchUserGroup(true, true);
      },

      handleClearSearch () {
        this.handleSearch();
      },

      handleBatch (payload) {
        const typeMap = {
          quit: () => {
            if (!this.isNoBatchQuit) {
              this.curSliderName = 'quit';
              this.batchSliderTitle = this.$t(`m.perm['批量退出用户组']`);
              this.sliderGroupPermList = this.currentSelectList.filter((item) => ['personalPerm'].includes(item.mode_type));
              this.isShowBatchSlider = true;
            }
          },
          renewal: () => {

          },
          handover: () => {

          },
          delete: () => {

          }
        };
        return typeMap[payload]();
      },

      handleReset () {

      },

      handleOperateSubmit () {

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
  }
  /deep/ .operate-dropdown-menu {
    margin-top: 12px;
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
