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
    />
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import IamResourceCascadeSearch from '@/components/iam-resource-cascade-search';
  import MultiTypeGroupPerm from './multi-type-group-perm.vue';
  export default {
    provide: function () {
      return {
        getResourceSliderWidth: () => this.resourceSliderWidth
      };
    },
    components: {
      IamResourceCascadeSearch,
      MultiTypeGroupPerm
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
        isDropdownShow: false,
        formItemWidth: '',
        renewalGroupTitle: '',
        managerGroupTitle: '',
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
        selectNoRenewalList: [],
        formData: {
          name: '',
          id: '',
          description: ''
        },
        curSystemAction: {},
        curResourceData: {},
        resourceSliderWidth: Math.ceil(window.innerWidth * 0.67 - 7) < 960
          ? 960 : Math.ceil(window.innerWidth * 0.67 - 7)
      };
    },
    computed: {
      ...mapGetters(['navStick']),
      isBatchDisabled () {
        return !this.currentSelectList.length;
      },
      isNoBatchQuit () {
        return true;
      },
      isNoBatchDelete () {
        const hasData = this.currentSelectList.length > 0;
        if (hasData && ['userOrgPerm'].includes(this.tabActive)
          && this.getGroupAttributes
          && this.getGroupAttributes().source_from_role) {
          const isAll = hasData && this.currentSelectList.length === this.userOrOrgCount;
          this.managerGroupTitle = isAll ? this.$t(`m.userGroup['管理员组至少保留一条数据']`) : '';
          return isAll;
        }
        return !hasData;
      },
      isNoBatchHandover () {
        return false;
      },
      isNoBatchRenewal () {
        const emptyField = this.currentSelectList.find((item) => item.name === this.tabActive);
        if (emptyField) {
          const hasData = emptyField.tableList.length > 0 && this.currentSelectList.length > 0;
          if (hasData) {
            this.selectNoRenewalList = this.currentSelectList.filter(
              (item) => item.expired_at === PERMANENT_TIMESTAMP);
            if (this.currentSelectList.length === this.selectNoRenewalList.length) {
              this.renewalGroupTitle = this.$t(
                `m.userGroup['已选择的用户组成员不需要续期']`
              );
              return true;
            }
          }
          return !hasData;
        }
        return true;
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
      window.addEventListener('resize', this.formatFormItemWidth);
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', this.formatFormItemWidth);
      });
    },
    methods: {
      handleRemoteTable () {
      
      },

      handleRefreshTable () {

      },

      handleSearch () {
        this.$refs.iamResourceSearchRef && this.$refs.iamResourceSearchRef.handleSearchUserGroup(true, true);
      },

      handleClearSearch () {
        this.handleSearch();
      },

      handleBatch () {

      },

      handleReset () {

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
      .group-dropdown-trigger-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #c4c6cc;
        height: 32px;
        min-width: 108px;
        border-radius: 2px;
        padding-left: 10px;
        padding-right: 5px;
        color: #63656e;
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
  .operate-dropdown-menu {
    margin-top: 12px;
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
