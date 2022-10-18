<template>
    <!-- eslint-disable max-len -->
    <div class="iam-instance-panel">
        <bk-collapse v-model="activePanel">
            <template v-for="(item, index) in instanceData">
                <bk-collapse-item :key="index" :name="item.name" v-if="displayPathList.length">
                    <p class="title">
                        <Icon bk class="expanded-icon" :type="activePanel.includes(item.name) ? 'down-shape' : 'right-shape'" />
                        {{ $t(`m.common['含']`) }}
                        <span class="number">{{ displayPathList.length }}</span
                        >{{ $t(`m.common['个']`) }} {{ item.name }}
                        <template v-if="!curLanguageIsCn"> (s) </template>
                        <span
                            :class="['clear-all', { disabled: displayPathList.every((v) => v.disabled) }]"
                            @click.stop="handleClearAll(item, index)"
                        >{{ $t(`m.common['清空']`) }}</span
                        >
                    </p>
                    <div slot="content" class="instance-content">
                        <p class="instance-item" v-for="(child, childIndex) in displayPathList" :key="childIndex">
                            <span class="name" :title="`ID：${child.id}`">{{ child.display_name }}</span>
                            <bk-button
                                text
                                size="small"
                                :style="buttonStyle"
                                :disabled="child.disabled && item.path[childIndex][0].disabled"
                                @click="handleRemove(child, index, childIndex)"
                            >
                                {{ $t(`m.common['移除']`) }}
                            </bk-button>
                        </p>
                    </div>
                </bk-collapse-item>
            </template>
        </bk-collapse>
    </div>
</template>
<script>
    // import Instance from '@/model/instance';
    export default {
        name: '',
        props: {
            limitValue: {
                type: Array,
                default: () => []
            },
            data: {
                type: Array,
                default: () => []
            }
        },
        data () {
            return {
                activePanel: [],
                instanceData: [],
                parentIds: [],
                displayPathList: []
            };
        },
        computed: {
            buttonStyle () {
                if (this.curLanguageIsCn) {
                    return {
                        'min-width': '48px',
                        'line-height': '42px'
                    };
                }
                return {
                    'min-width': '70px',
                    'line-height': '42px'
                };
            }
        },
        watch: {
            limitValue: {
                handler (value) {
                    value.forEach((item) => {
                        this.parentIds = item.path.map((subItem) => subItem[0].id);
                    });
                },
                immediate: true
            },
            data: {
                handler (value) {
                    console.log(value, 454555);
                    value.forEach((item) => {
                        const isExist = this.instanceData.some((instance) => instance.type === item.type);
                        if (!isExist) {
                            this.activePanel.push(item.name);
                        }
                        if (item.displayPath) {
                            this.displayPathList = item.displayPath.filter((subItem) => {
                                if (subItem.parentChain.length) {
                                    return this.parentIds.includes(subItem.parentChain[0].id);
                                }
                            });
                        }
                    });
                    // new Instance(this.displayPathList);
                    this.instanceData.splice(0, this.instanceData.length, ...value);
                },
                immediate: true
            }
        },
        methods: {
            handleRemove (child, index, childIndex) {
                console.log(child, index, childIndex);
                this.$emit('on-delete', child, index, childIndex);
            },

            handleClearAll (item, index) {
                if (item.displayPath.every((v) => v.disabled)) {
                    return;
                }
                this.$emit('on-clear', item, index);
            }
        }
    };
</script>
<style lang="postcss">
.iam-instance-panel {
  width: 100%;
  .bk-collapse-item-content {
    padding: 0;
  }
  .bk-collapse-item .bk-collapse-item-header {
    border-bottom: 1px solid #dcdee5;
    .fr {
      display: none;
    }
    &:hover {
      color: #63656e;
    }
  }
  .number {
    font-weight: 600;
    padding: 0 4px;
  }
  .title {
    position: relative;
    color: #63656e;
    .expanded-icon {
      margin-right: 5px;
      font-size: 14px;
    }
    .clear-all {
      position: absolute;
      right: 22px;
      font-size: 12px;
      color: #3a84ff;
      cursor: pointer;
      &:hover {
        color: #699df4;
      }
      &.disabled {
        color: #c4c6cc;
        cursor: not-allowed;
      }
    }
  }
  .instance-content {
    background: #fff;
    .instance-item {
      padding: 0 20px;
      display: flex;
      justify-content: space-between;
      line-height: 42px;
      border-bottom: 1px solid #dcdee5;
      .name {
        display: inline-block;
        max-width: 300px;
        font-size: 12px;
        color: #63656e;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
}
</style>
