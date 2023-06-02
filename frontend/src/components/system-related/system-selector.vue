<template>
  <div class="iam-system-selector-wrapper">
    <bk-dropdown-menu
      @show="handleDropdownShow"
      @hide="handleDropdownHide"
      ref="dropdown"
      trigger="click"
      :disabled="disabled">
      <div :class="['system-trigger', { active: isDropdownShow }]" slot="dropdown-trigger">
        <div :class="['system-text', { 'isPlaceholder': valueDisplay === '请选择' }]">
          {{ valueDisplay }}
        </div>
        <Icon bk :type="isDropdownShow ? 'flip' : 'angle-down'" />
      </div>
      <ul class="bk-dropdown-list" slot="dropdown-content">
        <section class="iam-system-search" v-if="searchable" @click.stop>
          <bk-input v-model="filter" placeholder="输入关键字搜索" @input="handleSearchInput" />
        </section>
        <li
          v-for="item in systemListDisplay"
          :key="item.system_id"
          :class="{ 'active': currentValue.includes(item.system_id) }">
          <a @click.stop="handleChange(item)" :title="item.system_name">
            <span>{{ item.system_name }}</span>
          </a>
          <Icon type="check-small" class="check-icon" />
        </li>
      </ul>
    </bk-dropdown-menu>
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      value: {
        type: Array,
        default: () => ['paasV3', 'job']
      },
      disabled: {
        type: Boolean,
        default: false
      },
      searchable: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        isDropdownShow: false,
        currentValue: this.value,
        filter: '',
        systemList: [
          {
            system_name: '作业平台',
            system_id: 'job'
          },
          {
            system_name: 'V3',
            system_id: 'paasV3'
          },
          {
            system_name: '配置平台',
            system_id: 'CMDB'
          }
        ]
      };
    },
    computed: {
      valueDisplay () {
        if (this.currentValue.length) {
          const selected = this.systemList.filter(
            item => this.currentValue.includes(item.system_id)
          ).map(item => item.system_name);
          return selected.join('，');
        }
        return '请选择';
      },
      systemListDisplay () {
        if (this.filter === '') {
          return this.systemList;
        }
        return this.systemList.filter(item => item.system_name.indexOf(this.filter) > -1);
      }
    },
    watch: {
      value (val) {
        if (val.length) {
          this.currentValue = val;
        }
      }
    },
    methods: {
      handleDropdownShow () {
        this.isDropdownShow = true;
      },
      handleDropdownHide () {
        this.isDropdownShow = false;
      },
      handleSearchInput (e) {
        console.warn(e);
      },
      handleFocus (e) {
        console.warn(e);
      },
      handleChange (payload) {
        if (this.currentValue.includes(payload.system_id)) {
          const index = this.currentValue.findIndex(item => item === payload.system_id);
          this.currentValue.splice(index, 1);
          return;
        }
        this.currentValue.push(payload.system_id);
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-system-selector-wrapper {
        .bk-dropdown-content {
            width: 120px;
            .bk-dropdown-list {
                max-height: 192px;
            }
            li {
                position: relative;
                cursor: pointer;
                .iam-icon {
                    /* display: none; */
                    position: absolute;
                    top: 8px;
                    right: 10px;
                }
                &:hover {
                    .iam-icon {
                        /* display: inline-block; */
                        color: #3a84ff;
                    }
                }
            }
            li.active {
                > a {
                    background-color: #eaf3ff;
                    color: #3a84ff;
                }
                .iam-icon {
                    color: #3a84ff;
                }
            }
            .check-icon {
                font-size: 24px;
            }
        }

        .iam-system-search {
            padding: 0 6px 6px 6px;
        }

        .system-trigger {
            position: relative;
            width: 460px;
            height: 32px;
            color: #63656e;
            background-color: #fff;
            border-radius: 2px;
            font-size: 12px;
            box-sizing: border-box;
            border: 1px solid #c4c6cc;
            padding: 0 10px;
            text-align: left;
            vertical-align: middle;
            outline: none;
            resize: none;
            transition: border .2s linear;
            &.active {
                border-color: #3a84ff;
            }
            .system-text {
                position: absolute;
                line-height: 30px;
                &.isPlaceholder {
                    color: #c4c6cc;
                }
            }
            i {
                position: absolute;
                top: 10px;
                right: 10px;
            }
        }
    }
</style>
