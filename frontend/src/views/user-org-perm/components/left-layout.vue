<template>
  <div class="user-org-perm-left-layout" :style="formatDragWidth">
    <div class="title">
      {{ $t(`m.userOrOrg['用户 / 组织列表']`) }}
    </div>
    <div class="group-operate-dropdown">
      <bk-dropdown-menu
        ref="batchDropdown"
        v-bk-tooltips="{ content: $t(`m.userOrOrg['请先勾选用户/组织']`), disabled: currentSelectList.length }"
        :ext-cls="formatDropDownClass"
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
            <a @click.stop="handleBatch('reset')">
              {{ $t(`m.userOrOrg['重置用户组']`) }}
            </a>
          </li>
          <li>
            <a @click.stop="handleBatch('add')">
              {{ $t(`m.userOrOrg['追加用户组']`) }}
            </a>
          </li>
          <li>
            <a @click.stop="handleBatch('clear')">
              {{ $t(`m.userOrOrg['清空用户组']`) }}
            </a>
          </li>
        </ul>
      </bk-dropdown-menu>
    </div>
    <div v-if="list.length" class="group-list">
      <div
        ref="memberRef"
        class="group-list-content"
        :style="formatListHeight"
        @scroll="handleScroll"
      >
        <div
          v-for="item in list"
          :key="item.id"
          :class="['group-list-item', { active: `${item.id}&${item.name}` === selectActive }]"
        >
          <bk-checkbox v-model="item.checked" @change="handleChecked(...arguments, item)" />
          <div class="group-content" @click.stop="handleSelect(item)">
            <Icon
              :type="formatTypeIcon(item.type)"
              :class="['group-type-icon', { active: `${item.id}&${item.name}` === selectActive }]"
            />
            <div
              v-if="['user'].includes(item.type)"
              v-bk-tooltips="{ content: `${item.id} (${item.name})` }"
              class="single-hide group-name"
            >
              <span>{{ item.id }}</span>
              <span style="margin-left: 5px;">({{ item.name }})</span>
            </div>
            <div
              v-if="['department'].includes(item.type)"
              v-bk-tooltips="{ content: item.name }"
              class="single-hide group-name"
            >
              {{ item.name }}
            </div>
          </div>
        </div>
        <div
          v-if="isScrollLoading"
          v-bkloading="{ isLoading: isScrollLoading, opacity: 1, color: '#fff' }"
          class="load-more-wrapper"
        />
      </div>
    </div>
    <div v-else class="user-org-empty-wrapper">
      <ExceptionEmpty
        :type="groupEmptyData.type"
        :empty-text="groupEmptyData.text"
        :tip-text="groupEmptyData.tip"
        :tip-type="groupEmptyData.tipType"
        @on-clear="handleEmptyClear"
        @on-refresh="handleEmptyRefresh"
      />
    </div>

    <JoinUserGroupSlider
      :slider-width="960"
      :show.sync="['clear'].includes(curSliderName) ? false : sliderData[curSliderName].showSlider"
      :cur-slider-name="curSliderName"
      :is-batch="true"
      :user-list="userList"
      :depart-list="departList"
      :title="formatSliderTitle"
      :group-data="queryGroupData"
      @on-submit="handleGroupSubmit"
    />

    <ClearUserGroupSlider
      :slider-width="960"
      :show.sync="sliderData['clear'].showSlider"
      :title="formatSliderTitle"
      :cur-slider-name="curSliderName"
      :user-list="userList"
      :depart-list="departList"
      :group-data="queryGroupData"
      @on-submit="handleGroupSubmit"
    />
  </div>
</template>

<script>
  import JoinUserGroupSlider from './join-user-group-slider.vue';
  import ClearUserGroupSlider from './clear-user-group-slider.vue';

  export default {
    inject: ['showNoticeAlert'],
    components: {
      JoinUserGroupSlider,
      ClearUserGroupSlider
    },
    props: {
      loading: {
        type: Boolean,
        default: false
      },
      isNoExpandNoSearchData: {
        type: Boolean,
        default: false
      },
      isNoExpandHasSearchData: {
        type: Boolean,
        default: false
      },
      canScrollLoad: {
        type: Boolean,
        default: false
      },
      curSelectActive: {
        type: String,
        default: ''
      },
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
      },
      emptyData: {
        type: Object
      },
      list: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        selectActive: '',
        curSliderName: 'add',
        listLoading: false,
        isDropdownShow: false,
        isScrollLoading: false,
        isShowNoDataTips: false,
        currentSelectList: [],
        sliderData: {
          reset: {
            type: 'reset',
            showSlider: false,
            list: []
          },
          add: {
            type: 'add',
            showSlider: false,
            list: []
          },
          clear: {
            type: 'clear',
            showSlider: false,
            list: []
          }
        },
        groupList: [],
        userList: [],
        departList: [],
        queryGroupData: {},
        pageConf: {
          current: 1,
          limit: 1,
          count: 0
        },
        groupEmptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
      isBatchDisabled () {
        return !this.currentSelectList.length;
      },
      formatTypeIcon () {
        return (payload) => {
          const typeMap = {
            user: () => {
              return 'personal-user';
            },
            department: () => {
              return 'organization-fill';
            }
          };
          return typeMap[payload]();
        };
      },
      formatDragWidth () {
        return {
          minWidth: '224px'
        };
      },
      formatSliderTitle () {
        const nameMap = {
          add: () => {
            return this.$t(`m.userOrOrg['批量追加用户组']`);
          },
          reset: () => {
            return this.$t(`m.userOrOrg['批量重置用户组']`);
          },
          clear: () => {
            return this.$t(`m.userOrOrg['清空用户组']`);
          }
        };
        return nameMap[this.curSliderName]();
      },
      formatListHeight () {
        if (this.showNoticeAlert) {
          if (this.isNoExpandNoSearchData) {
            return {
              height: 'calc(100vh - 225px)'
            };
          }
          if (this.isNoExpandHasSearchData) {
            return {
              height: 'calc(100vh - 268px)'
            };
          }
          return {
            height: 'calc(100vh - 450px)'
          };
        }
        if (this.isNoExpandNoSearchData) {
          return {
            height: 'calc(100vh - 186px)'
          };
        }
        if (this.isNoExpandHasSearchData) {
          return {
            height: 'calc(100vh - 228px)'
          };
        }
        return {
          height: 'calc(100vh - 400px)'
        };
      },
      formatDropDownClass () {
        if (!this.curLanguageIsCn) {
          return 'drop-down-operate drop-down-operate-lang';
        }
        return 'drop-down-operate';
      }
    },
    watch: {
      curSelectActive: {
        handler (value) {
          this.selectActive = value;
        },
        immediate: true
      },
      groupData: {
        handler (value) {
          this.queryGroupData = Object.assign({}, value);
        },
        immediate: true
      },
      emptyData: {
        handler (value) {
          this.groupEmptyData = Object.assign({}, value);
        },
        deep: true
      }
    },
    methods: {
      handleChecked (newVal, oldVal, val, row) {
        row.checked = newVal;
        if (newVal) {
          this.currentSelectList.push(row);
        } else {
          this.currentSelectList = this.currentSelectList.filter((item) => item.id !== row.id);
        }
      },

      handleSelect (payload) {
        this.selectActive = `${payload.id}&${payload.name}`;
        this.$emit('on-select', payload);
      },

      handleBatch (payload) {
        this.curSliderName = payload;
        this.userList = this.currentSelectList.filter((item) => ['user'].includes(item.type));
        this.departList = this.currentSelectList.filter((item) => ['department'].includes(item.type));
        this.sliderData[payload] = Object.assign(this.sliderData[payload], {
          showSlider: true,
          list: this.currentSelectList
        });
      },

      async handleGroupSubmit (payload) {
        if (['clear'].includes(this.curSliderName)) {
          if (payload && payload.isRefreshUser) {
            this.currentSelectList = [];
            this.$nextTick(() => {
              if (this.$refs.memberRef) {
                this.$refs.memberRef.scrollTop = 0;
              }
            });
          }
        }
        this.$emit('on-batch-operate', {
          name: this.curSliderName,
          isRefreshUser: payload.isRefreshUser || false
        });
      },

      handleResetScrollLoading () {
        this.isShowNoDataTips = false;
        this.isScrollLoading = false;
      },

      handleScroll (event) {
        if (!this.canScrollLoad) {
          this.isShowNoDataTips = true;
          this.isScrollLoading = false;
          return;
        }
        const { offsetHeight, scrollTop, scrollHeight } = event.target;
        console.log(scrollTop, offsetHeight, scrollHeight);
        if (scrollTop + offsetHeight >= scrollHeight - 5) {
          this.isScrollLoading = true;
          this.isShowNoDataTips = false;
          this.$emit('on-load-more');
        }
      },

      handleDropdownShow () {
        this.isDropdownShow = true;
      },

      handleDropdownHide () {
        this.isDropdownShow = false;
      },

      handleEmptyClear () {
        this.groupEmptyData.tipType = '';
        this.$emit('on-clear');
      },

      handleEmptyRefresh () {
        this.$emit('on-refresh');
      }
    }
  };
</script>

<style lang="postcss" scoped>
.user-org-perm-left-layout {
  position: relative;
  .title {
    font-size: 14px;
    color: #313238;
    padding-top: 16px;
    padding-left: 8px;
  }
  .group-operate-dropdown {
    padding-top: 12px;
    padding-left: 8px;
    margin-bottom: 8px;

    .group-dropdown-trigger-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid #c4c6cc;
      min-width: 92px;
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

  .group-list {
    /* padding-right: 16px; */
    position: relative;
    &-content {
      overflow-x: hidden;
      overflow-y: auto;
      &::-webkit-scrollbar {
        width: 3px;
        height: 3px;
      }
      &::-webkit-scrollbar-thumb {
        background: #dcdee5;
        border-radius: 3px;
      }
      &::-webkit-scrollbar-track {
        background: transparent;
        border-radius: 3px;
      }
    }
    &-item {
      display: flex;
      align-items: center;
      line-height: 36px;
      font-size: 13px;
      padding: 0 8px;
      cursor: pointer;

      .group-content {
        width: calc(100% - 20px);
        display: flex;
        align-items: center;

        .group-type-icon {
          font-size: 14px;
          color: #c4c6cc;
          margin-left: 10px;
          margin-right: 8px;
          &.active {
            color: #3a84ff;
          }
        }

        .group-name {
          max-width: 168px;
          word-break: break-all;
        }
      }

      &.active {
        background-color: #e1ecff;
        color: #3a84ff;
        border-radius: 2px;
      }
    }
  }

  .user-org-empty-wrapper  {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, 50%);
  }
}

/deep/ .drop-down-operate {
  .bk-dropdown-content {
    padding-top: 0;
    cursor: pointer;
  }

  &.disabled,
  &.disabled * {
    background-color: #f5f6fa;
    border-color: #dcdee5 !important;
    color: #c4c6cc !important;
    cursor: not-allowed;
  }
}
</style>
