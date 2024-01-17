<template>
  <div class="user-org-perm-left-layout" :style="formatDragWidth">
    <div class="group-operate-dropdown">
      <bk-dropdown-menu
        ref="batchDropdown"
        v-bk-tooltips="{ content: $t(`m.userOrOrg['请先勾选用户/组织']`), disabled: currentSelectList.length }"
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
              {{ $t(`m.userOrOrg['清空用户组并移出（管理空间）']`) }}
            </a>
          </li>
        </ul>
      </bk-dropdown-menu>
    </div>
    <div v-if="list.length" class="group-list">
      <div
        v-bkloading="{
          isLoading: loading,
          opacity: 1,
          color: '#f5f6fa'
        }"
        class="group-list-content"
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
              class="single-hide group-name">
              {{ item.name }}
            </div>
          </div>
        </div>
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
    
    <!-- 加入用户组slider -->
    <JoinUserGroupSlider
      :slider-width="960"
      :show.sync="sliderData[curSliderName].showSlider"
      :is-batch="true"
      :user-list="userList"
      :depart-list="departList"
      :title="formatSliderTitle"
      :group-data="queryGroupData"
    />
  </div>
</template>

<script>
  import JoinUserGroupSlider from './join-user-group-slider.vue';

  export default {
    components: {
      JoinUserGroupSlider
    },
    props: {
      loading: {
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
        pageConf: {
          current: 1,
          limit: 18,
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
          }
        };
        return nameMap[this.curSliderName]();
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
        if (['add', 'reset'].includes(payload)) {
          this.userList = this.currentSelectList.filter((item) => ['user'].includes(item.type));
          this.departList = this.currentSelectList.filter((item) => ['department'].includes(item.type));
        }
        this.sliderData[payload] = Object.assign(this.sliderData[payload], {
          showSlider: true,
          list: this.currentSelectList
        });
      },

      handleResetScrollLoading () {
        this.isShowNoDataTips = false;
        this.isScrollLoading = false;
      },

      handleScroll (event) {
        if (this.isLoading) {
          this.handleResetScrollLoading();
          return;
        }
        if (!this.canScrollLoad) {
          this.isShowNoDataTips = true;
          this.isScrollLoading = false;
          return;
        }
        const { offsetHeight, scrollTop, scrollHeight } = event.target;
        console.log(scrollTop, offsetHeight, scrollHeight);
        if (scrollTop + offsetHeight >= scrollHeight) {
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
  .group-operate-dropdown {
    padding-top: 16px;
    margin-bottom: 8px;

    .group-dropdown-trigger-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid #c4c6cc;
      min-width: 92px;
      height: 26px;
      border-radius: 2px;
      padding-left: 10px;
      padding-right: 5px;
      color: #63656e;

      &:hover {
        cursor: pointer;
        border-color: #979ba5;
      }

      .group-dropdown-text {
        font-size: 12px;
      }

      .bk-icon {
        font-size: 22px;
      }
    }
  }

  .group-list {
    padding-right: 16px;
    position: relative;
    &-content {
      height: calc(100vh - 310px);
      overflow-x: hidden;
      overflow-y: auto;
      &::-webkit-scrollbar {
        width: 6px;
        height: 6px;
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
        width: calc(100% - 10px);
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
          max-width: 140px;
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

/deep/ .bk-dropdown-menu {
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
