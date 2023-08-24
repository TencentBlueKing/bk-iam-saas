<template>
  <bk-dialog
    v-model="isShowDialog"
    width="720"
    :title="title"
    :show-footer="false"
    header-position="left"
    ext-cls="iam-attach-action-preview-dialog"
    @after-leave="handleAfterEditLeave">
    <div class="attach-action-preview-content-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
      <template v-if="!isLoading">
        <div class="compare-content">
          <template v-if="isShow">
            <tree :data="relateActionData" :has-border="true" />
          </template>
          <template v-else>
            <div class="no-change-content-wrapper">
              <iam-svg ext-cls="empty-tree-icon" />
              <p class="empty-tips">{{ $t(`m.related['无变更内容']`) }}</p>
            </div>
          </template>
        </div>
      </template>
    </div>
  </bk-dialog>
</template>
<script>
  import _ from 'lodash';
  import Tree from './attach-action-tree';
  export default {
    name: '',
    components: {
      Tree
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
      curId: {
        type: String,
        default: ''
      },
      title: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        isShowDialog: false,
        isLoading: false,
        relateActionData: [],
        actionTopologiesData: {}
      };
    },
    computed: {
      isShow () {
        return this.relateActionData.length > 0
          && (!this.relateActionData[0].isRelateActionEmpty
            || (this.relateActionData[0].children && this.relateActionData[0].children.some(item => item.tag !== 'unchecked')));
      }
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
          if (Object.keys(value).length > 0) {
            this.fetchData(value);
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchData (params) {
        this.isLoading = true;
        try {
          const res = await this.$store.dispatch('permApply/attachActionCompare', params);
          this.relateActionData = _.cloneDeep(res.data);
          this.handleMatchData(this.relateActionData);
          if (Object.keys(this.actionTopologiesData).length > 0) {
            this.relateActionData = _.cloneDeep([this.actionTopologiesData]);
          }
          this.handleInitData(this.relateActionData);
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

      handleMatchData (payload) {
        payload.forEach(item => {
          if (item.id === this.curId) {
            this.actionTopologiesData = _.cloneDeep(item);
            return true;
          } else {
            if (item.sub_actions && item.sub_actions.length > 0) {
              this.handleMatchData(item.sub_actions);
            }
          }
        });
        return false;
      },

      handleInitData (payload = []) {
        payload.forEach(item => {
          const subflag = item.sub_actions.length > 0;
          const relateActionEmpty = item.related_actions.every(relateItem => relateItem.tag === 'unchecked');
          if (item.id !== this.relateActionData[0].id
            && item.tag === 'unchecked'
            && item.sub_actions.every(subItem => subItem.tag === 'unchecked')
            && relateActionEmpty) {
            this.$set(item, 'visible', false);
          }
          this.$set(item, 'isRelateActionEmpty', relateActionEmpty || item.related_actions.length < 1);
          if (subflag) {
            this.$set(item, 'expanded', subflag);
            this.$set(item, 'children', _.cloneDeep(item.sub_actions));
          }
          if (item.children && item.children.length > 0) {
            this.handleInitData(item.children);
          }
        });
        return payload;
      },

      handleAfterEditLeave () {
        this.$emit('on-after-leave');
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-attach-action-preview-dialog {
        .bk-dialog-body {
            padding: 0 0 26px 0;
        }
        .attach-action-preview-content-wrapper {
            min-height: 442px;
            .compare-content {
                position: relative;
                padding: 0 24px 26px 24px;
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
                .no-change-content-wrapper {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    text-align: center;
                    img {
                        width: 120px;
                    }
                    .empty-tips {
                        position: relative;
                        top: -20px;
                        font-size: 12px;
                        color: #dcdee5;
                    }
                }
            }
        }
    }
</style>
