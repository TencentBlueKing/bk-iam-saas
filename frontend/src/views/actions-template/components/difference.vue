<template>
  <div class="related-group-content">
    <template v-if="hasGroup">
      <smart-action class="iam-template-diff-wrapper">
        <render-horizontal-block :label="$t(`m.common['选择实例']`)">
          <render-sync
            ref="syncRef"
            :id="$route.params.id"
            :add-action="addActions"
            :clone-action="cloneActions"
            @on-ready="handleSyncReady"
            @on-all-submit="handleAllSubmit"
          />
        </render-horizontal-block>
        <div slot="action">
          <bk-button
            :loading="prevLoading"
            :disabled="disabled"
            @click.stop="handlePrevStep('prev')"
          >
            {{ $t(`m.common['上一步']`) }}
          </bk-button>
          <bk-button
            theme="primary"
            :loading="isLoading"
            :disabled="(disabled || !isLastPage) && !isNoAddActions"
            @click.stop="handleNextStep">
            <span v-if="!isLastPage && !isNoAddActions" v-bk-tooltips="$t(`m.info['请先确认完所有实例']`)">
              {{ $t(`m.common['提交']`) }}
            </span>
            <span v-else>{{ $t(`m.common['提交']`) }}</span>
          </bk-button>
          <bk-button @click.stop="handlePrevStep('cancel')">
            {{ $t(`m.common['取消']`) }}
          </bk-button>
        </div>
      </smart-action>
    </template>
    <div v-else class="no-related-group">
      <ExceptionEmpty
        :type="emptyGroupData.type"
        :empty-text="emptyGroupData.text"
        :error-message="emptyGroupData.tip"
        :tip-type="emptyGroupData.tipType"
      />
      <div class="no-related-group-btn">
        <bk-button @click.stop="handleNoGroupOperate('prev')">
          {{ $t(`m.common['上一步']`) }}
        </bk-button>
        <bk-button theme="primary" @click.stop="handleNoGroupOperate('submit')"
        >
          {{ $t(`m.common['直接提交']`) }}
        </bk-button>
        <bk-button @click.stop="handleNoGroupOperate('cancel')">
          {{ $t(`m.common['取消']`) }}
        </bk-button>
      </div>
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import RenderSync from './sync.vue';

  export default {
    components: {
      RenderSync
    },
    props: {
      hasGroup: {
        type: Boolean
      },
      id: {
        type: [Number, String],
        default: 0
      },
      selectActions: {
        type: Array,
        default: () => []
      },
      selectActionsBack: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        isLoading: false,
        isOnePage: false,
        isLastPage: false,
        isNoAddActions: false,
        prevLoading: false,
        disabled: true,
        curCom: 'diff',
        emptyGroupData: {
          type: 'empty',
          text: this.$t(`m.actionsTemplate['暂无关联的用户组']`),
          tip: this.$t(`m.actionsTemplate['无须进行操作实例的确认']`),
          tipType: 'noPerm'
        },
        addActions: []
      };
    },
    computed: {
      ...mapGetters('permTemplate', ['preActionIds', 'cloneActions', 'preGroupOnePage'])
    },
    watch: {
      selectActions: {
        handler (value) {
          console.log(value, 5555);
          const tempActions = [];
          value.forEach((item) => {
            if (['added'].includes(item.flag) || (['unchecked'].includes(item.tag) && item.checked)) {
              tempActions.push(item);
            }
          });
          this.addActions = tempActions;
          this.isNoAddActions = this.addActions.length < 1;
        },
        immediate: true
      }
    },
    methods: {
      async handleNextStep () {
        if (this.isNoAddActions) {
          this.handleUpdateCommit();
          return;
        }
        const { flag, groups, isNoAdd } = this.$refs.syncRef.getData();
        groups.forEach(e => {
          e.actions.forEach(_ => {
            if (!_.resource_groups || !_.resource_groups.length) {
              _.resource_groups = (_.related_resource_types && _.related_resource_types.length) ? [{ id: '', related_resource_types: _.related_resource_types }] : [];
            }
          });
        });
        if (flag) {
          return;
        }
        if (this.preGroupOnePage) {
          if (isNoAdd) {
            this.handleUpdateCommit();
            return;
          }
          this.submitPreGroupSync(groups);
          return;
        }
        if (this.isLastPage) {
          this.submitPreGroupSync(groups);
        }
      },

      async preGroupSync (groups) {
        try {
          await this.$store.dispatch('permTemplate/preGroupSync', {
            id: this.$route.params.id,
            data: {
              groups
            }
          });
        } catch (e) {
          this.messageAdvancedError(e);
        }
      },

      async submitPreGroupSync (groups) {
        this.isLoading = true;
        try {
          await this.preGroupSync(groups);
          await this.handleUpdateCommit(false);
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          setTimeout(() => {
            this.isLoading = false;
          }, 300);
        }
      },

      async handleUpdateCommit (isLoading = true) {
        if (isLoading) {
          this.isLoading = true;
        }
        try {
          await this.$store.dispatch('permTemplate/updateCommit', {
            id: this.$route.params.id
          });
          this.messageSuccess(this.$t(`m.info['提交成功']`), 3000);
          this.$router.push({
            name: 'actionsTemplate'
          });
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          if (isLoading) {
            this.isLoading = false;
          }
        }
      },

      handleNoGroupOperate (payload) {
        const typeMap = {
          prev: () => {
            this.$parent.handleSetCurActionStep && this.$parent.handleSetCurActionStep(1);
          },
          submit: async () => {
            try {
              // 如果没有操作变更不需要调用接口
              if (JSON.stringify(this.selectActionsBack) === JSON.stringify(this.selectActions)) {
                this.messageSuccess(this.$t(`m.info['提交成功']`), 3000);
                this.$router.push({
                  name: 'actionsTemplate'
                });
                return;
              }
              const actionIdList = this.selectActions.map((item) => item.id);
              const { data } = await this.$store.dispatch('permTemplate/addPreUpdateInfo', {
                id: this.id,
                data: {
                  action_ids: actionIdList
                }
              });
              if (data) {
                await this.handleUpdateCommit();
              }
            } catch (e) {
              this.messageAdvancedError(e);
            }
          },
          cancel: () => {
            this.$router.push({
              name: 'actionsTemplate'
            });
          }
        };
        return typeMap[payload]();
      },

      handleAllSubmit (payload) {
        this.isLastPage = payload;
      },

      handleSyncReady () {
        this.disabled = false;
      },

      handlePrevStep (payload) {
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(() => {
          const typeMap = {
            prev: async () => {
              this.prevLoading = true;
              try {
                await this.$store.dispatch('permTemplate/cancelPreUpdate', {
                  id: this.$route.params.id
                });
                this.$parent.handleSetCurActionStep && this.$parent.handleSetCurActionStep(1);
              } catch (e) {
                this.messageAdvancedError(e);
              } finally {
                this.prevLoading = false;
              }
            },
            cancel: () => {
              this.$router.push({
                name: 'actionsTemplate'
              });
            }
          };
          typeMap[payload]();
        }, _ => _);
      }
    }
  };
</script>

<style lang="postcss" scoped>
.related-group-content {
  /deep/.no-related-group {
    position: absolute;
    top: 45%;
    left: 50%;
    transform: translate(-50%, -45%);
    .part-img {
      width: 440px !important;
    }
    .part-text {
      .empty-text {
        font-size: 20px;
        color: #63656E;
      }
      .tip-wrap {
        margin-top: 16px;
        .tip-message {
          font-size: 14px;
        }
      }
    }
    &-btn {
      margin-top: 24px;
      text-align: center;
      font-size: 0;
      .bk-button {
        min-width: 88px;
        margin-right: 8px;
      }
    }
  }
}
</style>
