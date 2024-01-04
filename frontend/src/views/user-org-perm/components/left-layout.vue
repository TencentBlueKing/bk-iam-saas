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
    <div class="group-list">
      <div
        v-if="groupList.length"
        :style="formatSystemsHeight"
        v-bkloading="{
          isLoading: listLoading,
          opacity: 1,
          color: '#f5f6fa'
        }"
        class="group-list-content"
        @scroll="handleScroll"
      >
        <div
          v-for="item in groupList"
          :key="item.id"
          :class="['group-list-item', { active: `${item.id}&${item.name}` === selectActive }]"
          @click.stop="handleSelect(item)"
        >
          <bk-checkbox v-model="item.checked" @change="handleChecked(...arguments, item)" />
          <div class="group-content">
            <Icon
              :type="formatTypeIcon(item.type)"
              :class="['group-type-icon', { active: `${item.id}&${item.name}` === selectActive }]"
            />
            <div class="single-hide group-name" :title="item.name">
              <span>{{ item.name }}</span>
              <span v-if="['user'].includes(item.type)">{{ item.id }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { getWindowHeight } from '@/common/util';
  export default {
    props: {
      currentActive: {
        type: String,
        default: ''
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
        listLoading: false,
        isDropdownShow: false,
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
          minWidth: '240px'
        };
      },
      formatSystemsHeight () {
        return `${getWindowHeight() - 51 - 51 - 157 - 2}px`;
      }
    },
    watch: {
      list: {
        handler (value) {
          if (value.length) {
            if (!value.some(item => item.id === this.currentActive)) {
              this.selectActive = value[0].id;
            }
          } else {
            this.selectActive = -1;
          }
        },
        immediate: true
      }
    },
    async created () {
      this.pageConf.limit = Math.ceil(this.listHeight / 36);
      await this.fetchInitData();
    },
    methods: {
      async fetchInitData () {
        await this.fetchGroupMemberList();
        if (this.groupList.length) {
          this.handleSelect(this.groupList[0]);
        }
      },

      handleChecked (newVal, oldVal, val, row) {
        if (newVal) {
          this.currentSelectList.push(row);
        } else {
          this.currentSelectList = this.currentSelectList.filter((item) => item.id !== row.id);
        }
      },

      handleSelect (payload) {
        this.selectActive = `${payload.id}&${payload.name}`;
      },

      handleBatch (payload) {
        this.sliderData[payload] = Object.assign(this.sliderData[payload], {
          showSlider: true,
          list: this.currentSelectList
        });
      },

      handleDropdownShow () {
        this.isDropdownShow = true;
      },

      handleDropdownHide () {
        this.isDropdownShow = false;
      }
    }
  };
</script>

<style lang="postcss" scoped>
.user-org-perm-left-layout {
  position: relative;
  flex-basis: 240px;
  width: 240px;
  border-right: 1px solid#dcdee5;
  z-index: 1;

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
    &-content {
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
    background-color: #f5f6fa;
    border-color: #dcdee5 !important;
    color: #c4c6cc !important;
    cursor: not-allowed;
  }
}
</style>
