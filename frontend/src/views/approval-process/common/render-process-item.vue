<template>
  <div class="iam-approval-process-set-item">
    <section class="header">
      <span class="title">{{ title }}</span>
      <!-- <bk-switcher
                theme="primary"
                size="small"
                :value="curOpenStatus"
                @change="handleStatusChange">
            </bk-switcher> -->
    </section>
    <section
      :class="['process-select-wrapper', { 'is-focus': isToggle }]"
      @click.stop="handleToogleSelect">
      <span class="title">{{ $t(`m.approvalProcess['默认审批流程']`) + ': ' }}</span>
      <!-- eslint-disable max-len -->
      <bk-select
        :value="value"
        :clearable="false"
        searchable
        ref="select"
        :ext-cls="curLanguageIsCn ? 'iam-process-select-cls' : 'iam-process-select-en-cls'"
        @selected="handleProcessSelect"
        @toggle="handleSelectToggle">
        <bk-option v-for="option in list"
          :key="option.id"
          :id="option.id"
          :name="option.name">
          <span style="display: block; line-height: 32px;" :title="`${$t(`m.approvalProcess['审批节点']`)}：${ optionMap(option) }`">{{ option.name }}</span>
        </bk-option>
        <div slot="extension" v-bk-tooltips="{ content: tips, extCls: 'iam-tooltips-cls' }" @click="handleOpenCreateLink" style="cursor: not-allowed;">
          <Icon bk type="plus-circle" />
          <span>{{ $t(`m.common['新增']`) }}</span>
        </div>
        <div slot="trigger" :title="curTitle">
          {{ curSelectName }}
        </div>
      </bk-select>
    </section>
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      list: {
        type: Array,
        default: () => []
      },
      title: {
        type: String,
        default: ''
      },
      curValue: {
        type: [Number, String],
        default: -1
      },
      isOpen: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        curOpenStatus: false,
        isToggle: false,
        tips: this.$t(`m.common['暂未开放']`),
        value: -1
      };
    },
    computed: {
      curSelectName () {
        if (this.list.length > 0 && this.value !== -1) {
          const data = this.list.find(item => item.id === this.value);
          return data ? data.name || '' : '';
        }
        return '';
      },
      curTitle () {
        if (this.list.length > 0 && this.value !== -1) {
          const tempData = this.list.find(item => item.id === this.value);
          if (tempData && tempData.node_names) {
            return `${this.$t(`m.approvalProcess['审批节点']`)}：${tempData.node_names.join(' -> ')}`;
          }
          return '';
        }
        return '';
      }
    },
    watch: {
      isOpen: {
        handler (value) {
          this.curOpenStatus = !!value;
        },
        immediate: true
      },
      curValue: {
        handler (val) {
          this.value = val;
        },
        immediate: true
      }
    },
    methods: {
      handleToogleSelect () {
        if (!this.isToggle) {
          this.isToggle = true;
          this.$refs.select.show();
          return;
        }
        this.isToggle = false;
        this.$refs.select.close();
      },

      handleProcessSelect (value, option) {
        this.$emit('selected', value);
      },

      handleOpenCreateLink () {
        // const url = `${window.BK_ITSM_APP_URL}/#/process/home`
        // window.open(url)
      },

      handleSelectToggle (payload) {
        this.isToggle = payload;
      },

      setValue (payload) {
        this.value = payload;
      },

      handleStatusChange (payload) {
        this.$emit('change', payload);
      },
      optionMap (option) {
        if (option.node_names) {
          return option.node_names.join(' -> ');
        }
      }
    }
  };
</script>
<style lang="postcss">
    .iam-approval-process-set-item {
        padding: 12px 10px 7px 10px;
        /* width: 415px; */
        flex: 0 0 33%;
        height: 64px;
        background: #fff;
        border-radius: 2px;
        box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, .05);
        .header {
            padding-left: 11px;
            display: flex;
            justify-content: space-between;
            .title {
                font-size: 12px;
                font-weight: 600;
            }
        }
        .process-select-wrapper {
            padding-left: 11px;
            display: flex;
            justify-content: flex-start;
            margin-top: 5px;
            width: 100%;
            height: 26px;
            line-height: 24px;
            border: 1px solid transparent;
            border-radius: 2px;
            /* cursor: pointer; */
            &:hover {
                background: #f0f1f5;
                .iam-process-select-en-cls {
                    .bk-select-angle {
                        display: inline-block;
                    }
                }
                .iam-process-select-cls {
                    .bk-select-angle {
                        display: inline-block;
                    }
                }
            }
            &.is-focus {
                background: #fff;
                border-color: #3a84ff;
                box-shadow: 0px 0px 0px 2px #e1ecff;
                .iam-process-select-en-cls {
                    .bk-select-angle {
                        display: inline-block;
                    }
                }
                .iam-process-select-cls {
                    .bk-select-angle {
                        display: inline-block;
                    }
                }
            }
            .title {
                font-size: 12px;
            }
            .iam-process-select-en-cls {
                width: calc(100% - 155px);
                line-height: 26px;
                border: none;
                &.is-focus {
                    box-shadow: none;
                }
                /* &:hover {
                    .bk-select-angle {
                        display: inline-block;
                    }
                } */
                .bk-select-name {
                    height: 26px;
                    padding-left: 0;
                }
                .bk-select-angle {
                    display: none;
                    top: 7px !important;
                }
            }
            .iam-process-select-cls {
                width: calc(100% - 84px);
                line-height: 24px;
                border: none;
                &.is-focus {
                    box-shadow: none;
                }
                /* &:hover {
                    .bk-select-angle {
                        display: inline-block;
                    }
                } */
                .bk-select-name {
                    height: 26px;
                    padding-left: 0;
                }
                .bk-select-angle {
                    display: none;
                    top: 2px !important;
                }
            }
        }
    }
</style>
