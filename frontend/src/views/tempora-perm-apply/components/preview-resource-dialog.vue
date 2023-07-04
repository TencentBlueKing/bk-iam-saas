<template>
  <bk-dialog
    v-model="isShowDialog"
    width="720"
    :title="title"
    :show-footer="false"
    header-position="left"
    ext-cls="iam-resource-preview-dialog"
    @after-leave="handleAfterEditLeave">
    <!-- eslint-disable max-len -->
    <div class="resource-preview-content-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
      <template v-if="!isLoading">
        <div class="compare-header">
          <div class="bk-button-group">
            <!-- <bk-button @click="handleBtnChange('difference')" :class="active === 'difference' ? 'is-selected' : ''">差异对比</bk-button> -->
            <!-- <bk-button @click="handleBtnChange('result')" :class="active === 'result' ? 'is-selected' : ''">结果预览</bk-button> -->
          </div>
          <!-- <div class="resource-total-count">
                        <label>实例总数：</label>
                        {{ total }}&nbsp;个
                    </div> -->
        </div>
        <div class="compare-content">
          <compare-detail :data="conditionData" />
        </div>
      </template>
    </div>
  </bk-dialog>
</template>
<script>
  import _ from 'lodash';
  import CompareCondition from '@/model/compare-condition';
  import CompareDetail from '@/components/render-resource/compare-detail';
  export default {
    name: '',
    components: {
      CompareDetail
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      params: {
        type: Object,
        default: () => {
          return {};
        }
      },
      title: {
        type: String,
        default: '差异对比'
      }
    },
    data () {
      return {
        isShowDialog: false,
        isLoading: false,
        active: 'difference',
        searchParams: {},
        conditionData: [],
        total: 0
      };
    },
    watch: {
      show: {
        handler (value) {
          this.isShowDialog = !!value;
        },
        immediate: true
      },
      params: {
        handler (value) {
          if (value.policy_id) {
            this.searchParams = _.cloneDeep(value);
            if (this.isShowDialog) {
              this.fetchData();
            }
          }
        },
        immediate: true,
        deep: true
      }
    },
    methods: {
      async fetchData () {
        this.isLoading = true;
        try {
          const res = await this.$store.dispatch('permApply/conditionCompare', this.searchParams);
          this.conditionData = res.data.map(item => new CompareCondition(item));
          if (this.conditionData.length > 0) {
            if (this.conditionData[0].hasOwnProperty('instance')) {
              this.conditionData[0].instanceExpanded = true;
            }
            if (this.conditionData[0].hasOwnProperty('attribute')) {
              this.conditionData[0].attributeExpanded = true;
            }
          }
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.isLoading = false;
        }
      },

      handleBtnChange (payload) {
        this.active = payload;
      },

      handleAfterEditLeave () {
        this.$emit('on-after-leave');
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-resource-preview-dialog {
        /* .bk-dialog-header {
            display: none;
        } */
        .bk-dialog-body {
            padding: 0 0 26px 0;
        }
        .resource-preview-content-wrapper {
            min-height: 442px;
            .compare-header {
                display: flex;
                padding: 0 24px;
                justify-content: flex-start;
                .resource-total-count {
                    margin-left: 20px;
                    line-height: 32px;
                }
            }
            .compare-content {
                /* padding: 0 24px 26px 24px; */
                height: 400px;
                overflow-y: auto;
                &::-webkit-scrollbar {
                    width: 4px;
                    background-color: lighten(transparent, 80%);
                }
                &::-webkit-scrollbar-thumb {
                    height: 5px;
                    border-radius: 2px;
                    background-color: #e6e9ea;
                }
            }
        }
    }
</style>
