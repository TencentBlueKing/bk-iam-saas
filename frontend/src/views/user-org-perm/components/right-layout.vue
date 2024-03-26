<template>
  <div class="user-org-right-wrapper">
    <div class="user-name">{{ formatUserName }}</div>
    <div class="header-operate">
      <div>
        <bk-button theme="primary" @click="handleAddGroup">
          {{ $t(`m.userOrOrg['加入用户组']`) }}
        </bk-button>
      </div>
      <div class="group-detail-dropdown">
        <bk-dropdown-menu
          ref="batchDropdown"
          v-bk-tooltips="{ content: $t(`m.userOrOrg['请先勾选用户组权限']`), disabled: selectedGroups.length }"
          :disabled="isBatchDisabled"
          @show="handleDropdownShow"
          @hide="handleDropdownHide"
        >
          <div class="group-dropdown-trigger-btn" slot="dropdown-trigger">
            <span class="group-dropdown-text">{{ $t(`m.userOrOrg['批量操作']`) }}</span>
            <i :class="['bk-icon icon-angle-down', { 'icon-flip': isDropdownShow }]" />
          </div>
          <ul class="bk-dropdown-list" slot="dropdown-content">
            <li>
              <a
                :class="[{ 'remove-disabled': isNoBatchRemove() }]"
                v-bk-tooltips="{ content: removeGroupTitle, disabled: !removeGroupTitle, placements: ['right'] }"
                @click.stop="handleBatch('remove')"
              >
                {{ $t(`m.userOrOrg['移出']`) }}
              </a>
            </li>
            <li>
              <a
                :class="[{ 'renewal-disabled': isNoBatchRenewal() }]"
                v-bk-tooltips="{ content: renewalGroupTitle, disabled: !renewalGroupTitle, placements: ['right'] }"
                @click.stop="handleBatch('renewal')">
                {{ $t(`m.renewal['续期']`) }}
              </a>
            </li>
          </ul>
        </bk-dropdown-menu>
      </div>
    </div>
    <div class="group-detail-table">
      <component
        ref="childPermRef"
        :key="componentsKey"
        :is="curCom"
        :group-data="queryGroupData"
        :empty-data="curEmptyData"
        :search-params="curSearchParams"
        :search-pagination="curSearchPagination"
        :is-search-perm="isSearchPerm"
        @on-selected-group="handleSelectedGroup"
        @on-clear="handleEmptyClear"
        @on-refresh="handleEmptyRefresh"
      />
    </div>
    <!-- 加入用户组slider -->
    <JoinUserGroupSlider
      :slider-width="960"
      :show.sync="isShowAddGroupSlider"
      :is-batch="false"
      :cur-slider-name="curSliderName"
      :user-list="userList"
      :depart-list="departList"
      :title="$t(`m.userOrOrg['加入用户组']`)"
      :group-data="queryGroupData"
      @on-submit="handleAddGroupSubmit"
    />

    <BatchOperateSlider
      :slider-width="960"
      :show.sync="isShowBatchSlider"
      :is-batch="false"
      :cur-slider-name="curSliderName"
      :user-list="userList"
      :depart-list="departList"
      :title="batchSliderTitle"
      :group-data="queryGroupData"
      :group-list="selectedGroups"
      @on-submit="handleAddGroupSubmit"
    />
  </div>
</template>

<script>
  import { cloneDeep } from 'lodash';
  import { PERMANENT_TIMESTAMP } from '@/common/constants';
  import { bus } from '@/common/bus';
  import MultiTypeGroupPerm from './multi-type-group-perm.vue';
  import JoinUserGroupSlider from './join-user-group-slider.vue';
  import BatchOperateSlider from './batch-operate-slider.vue';

  const COM_MAP = new Map([
    [['user', 'department'], 'MultiTypeGroupPerm']
  ]);

  export default {
    components: {
      MultiTypeGroupPerm,
      JoinUserGroupSlider,
      BatchOperateSlider
    },
    props: {
      groupData: {
        type: Object
      },
      isSearchPerm: {
        type: Boolean,
        default: false
      },
      curSearchParams: {
        type: Object,
        default: () => {}
      },
      curSearchPagination: {
        type: Object,
        default: () => {
          return {
            current: 1,
            limit: 10,
            count: 0
          };
        }
      }
    },
    data () {
      return {
        isDropdownShow: false,
        isShowAddGroupSlider: false,
        isShowBatchSlider: false,
        batchSliderTitle: '',
        removeGroupTitle: '',
        renewalGroupTitle: '',
        curSliderName: '',
        componentsKey: -1,
        selectedGroups: [],
        userList: [],
        departList: [],
        queryGroupData: {},
        curEmptyData: {
          type: 'empty',
          text: '暂无数据',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      formatUserName () {
        const { id, name } = this.groupData;
        const typeMap = {
          user: () => {
            return `${id}${this.$t(`m.common['（']`)}${name}${this.$t(`m.common['）']`)}${this.$t(`m.userOrOrg['的用户组']`)}`;
          },
          department: () => {
            return `${name}${this.$t(`m.userOrOrg['的用户组']`)}`;
          }
        };
        if (typeMap[this.groupData.type]) {
          return typeMap[this.groupData.type]();
        }
        return '';
      },
      isBatchDisabled () {
        return !this.selectedGroups.length;
      },
      isNoBatchRemove () {
        return () => {
          const hasData = this.selectedGroups.length > 0;
          if (hasData) {
            const list = this.selectedGroups.filter((item) =>
              item.role_members.length === 1
              && item.attributes
              && item.attributes.source_from_role
            );
            const result = this.selectedGroups.length === list.length;
            this.removeGroupTitle = result ? this.$t(`m.userOrOrg['当前勾选项都为不可移出的管理员组']`) : '';
            return result;
          }
          return !hasData;
        };
      },
      isNoBatchRenewal () {
        return () => {
          const hasData = this.selectedGroups.length > 0;
          if (hasData) {
            const list = this.selectedGroups.filter((item) => item.expired_at === PERMANENT_TIMESTAMP);
            const result = this.selectedGroups.length === list.length;
            this.renewalGroupTitle = result ? this.$t(`m.userOrOrg['当前勾选项都为不可移出的管理员组']`) : '';
            return result;
          }
          return !hasData;
        };
      },
      curCom () {
        let com = '';
        for (const [key, value] of this.comMap.entries()) {
          if (Object.keys(this.groupData).length && key.includes(this.groupData.type)) {
            com = value;
            break;
          }
        }
        return com;
      }
    },
    watch: {
      groupData: {
        handler (value) {
          if (Object.keys(value).length > 0) {
            this.comMap = COM_MAP;
            this.fetchDetailData(value);
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchDetailData (value) {
        this.curEmptyData.tipType = '';
        this.selectedGroups = [];
        // this.handleEmptyClear();
        this.queryGroupData = cloneDeep(value);
      },

      fetchInitInterFace () {
        Promise.all([this.fetchUserGroupSearch(), this.fetchDepartGroupSearch()]);
      },

      handleBatch (payload) {
        this.curSliderName = payload;
        this.handleGetMembers();
        const typeMap = {
          remove: () => {
            if (!this.isNoBatchRemove()) {
              this.batchSliderTitle = this.$t(`m.userOrOrg['批量移出用户组']`);
              this.isShowBatchSlider = true;
            }
          },
          renewal: () => {
            if (!this.isNoBatchRenewal()) {
              this.batchSliderTitle = this.$t(`m.renewal['批量续期']`);
              this.isShowBatchSlider = true;
            }
          }
        };
        typeMap[payload]();
      },

      handleAddGroup () {
        this.handleGetMembers();
        this.curSliderName = 'add';
        this.isShowAddGroupSlider = true;
      },

      handleAddGroupSubmit () {
        this.selectedGroups = [];
        bus.$emit('on-remove-toggle-checkbox', []);
        bus.$emit('on-refresh-resource-search', {
          isSearchPerm: this.isSearchPerm,
          curSearchParams: this.curSearchParams,
          curSearchPagination: this.curSearchPagination
        });
      },

      handleSelectedGroup (payload) {
        this.selectedGroups = [...payload];
      },
      
      handleGetMembers () {
        const userList = [];
        const departList = [];
        const typeMap = {
          user: () => {
            userList.push(this.queryGroupData);
          },
          department: () => {
            departList.push(this.queryGroupData);
          }
        };
        typeMap[this.queryGroupData.type]();
        this.userList = [...userList];
        this.departList = [...departList];
      },

      handleDropdownShow () {
        this.isDropdownShow = true;
      },

      handleDropdownHide () {
        this.isDropdownShow = false;
      },

      handleEmptyRefresh () {
        this.$emit('on-refresh');
      },

      handleEmptyClear () {
        this.$emit('on-clear');
      }
    }
  };
</script>

<style lang="postcss" scoped>
.user-org-right-wrapper {
  height: 100%;
  overflow-y: scroll;
  &::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: #dcdee5;
    border-radius: 3px;
  }
  &::-webkit-scrollbar-track {
    background-color: transparent;
    border-radius: 3px;
  }
  .user-name {
    width: 100%;
    font-size: 14px;
    line-height: 22px;
    word-break: break-all;
  }

  .header-operate {
    display: flex;
    padding: 12px 0;
    .group-detail-dropdown {
      margin-left: 8px;
      .group-dropdown-trigger-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #c4c6cc;
        min-width: 102px;
        height: 32px;
        border-radius: 2px;
        padding-left: 10px;
        padding-right: 5px;
        background-color: #ffffff;
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
}

/deep/ .bk-dropdown-menu {
  .bk-dropdown-content {
    padding-top: 0;
    cursor: pointer;
  }

  &.disabled,
  &.disabled *,
  .remove-disabled,
  .renewal-disabled {
    background-color: #ffffff !important;
    border-color: #dcdee5 !important;
    color: #c4c6cc !important;
    cursor: not-allowed;
    div:nth-child(2) {
      height: 0 !important;
    }
  }
}
</style>
