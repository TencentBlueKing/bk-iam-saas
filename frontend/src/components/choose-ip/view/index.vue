<template>
  <!-- eslint-disable max-len -->
  <div class="iam-instance-panel">
    <bk-collapse v-model="activePanel">
      <template v-for="(item, index) in instanceData">
        <bk-collapse-item
          v-if="item.displayPath.length"
          :key="index"
          :name="item.name"
          :hide-arrow="true"
          :ext-cls="formatCollapseCls(item, index)"
        >
          <div class="title flex-between">
            <div class="single-hide">
              <Icon bk class="expanded-icon" :type="activePanel.includes(item.name) ? 'down-shape' : 'right-shape'" />
              <!-- <span>{{ formatChain(item) }}: </span> -->
              <span>{{ $t(`m.common['已选']`) }}</span>
              <span class="number">{{ item.displayPath.length }}</span>
              <span>{{ $t(`m.common['个']`) }}{{ item.name }}</span>
            </div>
            <div
              :class="[
                'clear-all',
                { 'disabled': formatClearDisabled(item) }
              ]"
              @click.stop="handleClearItem(item, index)"
            >
              <Icon
                type="delete-line"
                v-bk-tooltips="{ content: $t(`m.common['清空']`) }"
              />
            </div>
          </div>
          <div slot="content" class="instance-content">
            <p class="instance-item" v-for="(child, childIndex) in item.displayPath" :key="childIndex">
              <!-- <span class="name" :title="`ID: ${child.id}`">{{ child.display_name }}</span> -->
              <span class="name" :title="`ID: ${child.id}; ${$t(`m.levelSpace['名称']`)}: ${child.display_name}`">{{ child.display_name }}</span>
              <bk-button
                text
                size="small"
                class="instance-item-btn"
                :style="buttonStyle"
                :disabled="child.disabled && item.path[childIndex][0].disabled"
                @click="handleRemove(child, index, childIndex)">
                <Icon bk type="close" />
              </bk-button>
            </p>
          </div>
        </bk-collapse-item>
      </template>
    </bk-collapse>
  </div>
</template>

<script>
  import _ from 'lodash';
  export default {
    name: '',
    props: {
      data: {
        type: Array,
        default: () => []
      },
      selectList: {
        type: Array,
        default: () => []
      },
      selectValue: {
        type: String
      }
    },
    data () {
      return {
        activePanel: [],
        instanceData: [],
        // 当前选择的链路
        curChain: [],
        ignorePathFlag: false
      };
    },
    computed: {
      buttonStyle () {
        if (this.curLanguageIsCn) {
          return {
            // 'min-width': '48px',
            'line-height': '32px'
          };
        }
        return {
          // 'min-width': '70px',
          'line-height': '32px'
        };
      },
      formatChain () {
        return (payload) => {
          let curChainItem = {};
          this.selectList.forEach((item) => {
            if (item.resource_type_chain && item.resource_type_chain.length) {
              if (item.resource_type_chain.map((v) => v.id).includes(payload.type)) {
                curChainItem = _.cloneDeep(item);
              }
            }
          });
          return curChainItem.name || '';
        };
      },
      formatClearDisabled () {
        return (payload) => {
          return payload.displayPath.every(v => v.disabled);
        };
      },
      formatCollapseCls () {
        return (payload, index) => {
          return !this.activePanel.includes(payload.name) && this.instanceData.length - 1 !== index
            ? 'iam-instance-panel-collapse is-shrink'
            : 'iam-instance-panel-collapse';
        };
      }
    },
    watch: {
      data: {
        handler (value) {
          value.forEach(item => {
            const isExist = this.instanceData.some(instance => instance.type === item.type);
            if (!isExist) {
              this.activePanel.push(item.name);
            }
          });
          this.instanceData.splice(0, this.instanceData.length, ...value);
        },
        immediate: true
      }
    },
    methods: {
      handleRemove (child, index, childIndex) {
        this.$emit('on-delete', child, index, childIndex);
      },

      handleClearItem (item, index) {
        if (item.displayPath.every(v => v.disabled)) {
          return;
        }
        this.$emit('on-clear', item, index);
      }
    }
  };
</script>

<style lang="postcss" scoped>
  .iam-instance-panel {
      width: 100%;
      .bk-collapse-item-content {
          padding: 0;
      }
      /deep/ .bk-collapse-item {
        .bk-collapse-item-header {
            font-size: 12px;
            /* border-bottom: 1px solid #dcdee5; */
            .fr {
              display: none;
            }
            &:hover {
              color: #63656e;
            }
        }
        &.is-shrink {
          margin-bottom: 8px;
        }
      }
      .number {
        color: #3A84FF;
        font-weight: 700;
        /* padding: 0 4px; */
      }
      .title {
          position: relative;
          color: #63656e;
          background-color: #fafbfd;
          .expanded-icon {
              /* margin-right: 5px; */
              font-size: 12px;
          }
          .clear-all {
              position: absolute;
              right: 0;
              .iamcenter-delete-line {
                font-size: 15px;
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
              }
              &.disabled {
                cursor: not-allowed;
                .iamcenter-delete-line {
                  font-size: 15px;
                  color: #c4c6cc;
                  cursor: not-allowed;
                }
              }
          }
      }
      .instance-content {
          padding-bottom: 16px;
          .instance-item {
              padding: 0 20px;
              display: flex;
              justify-content: space-between;
              line-height: 32px;
              border-bottom: 1px solid #F4F4F4;
              border-radius: 2px;
              background: #ffffff;
              box-shadow: 0 1px 5px 0 #0000000f;
              .name {
                  display: inline-block;
                  max-width: 300px;
                  font-size: 12px;
                  color: #63656e;
                  overflow: hidden;
                  text-overflow: ellipsis;
                  white-space: nowrap;
              }
              &-btn {
                display: none;
              }
              &:last-child {
                border-bottom: 0;
              }
              &:hover {
                cursor: pointer;
                background-color:#E3EBFE;
                .instance-item-btn {
                  display: block;
                  font-size: 20px;
                  color: #3A84FF;
                  padding: 0;
                  &.is-disabled {
                    color: #c4c6cc;
                  }
                }
              }
          }
      }
  }
</style>
