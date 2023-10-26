<template>
  <div>
    <bk-sideslider
      :is-show="isShowSideSlider"
      :title="title"
      :width="width"
      ext-cls="iam-level-transfer-side"
      :quick-close="true"
      @update:isShow="handleCancel"
    >
      <div slot="content" class="iam-level-transfer-side-content">
        <div class="level-transfer-content">
          <bk-form form-type="vertical">
            <bk-form-item
              :label="$t(`m.sensitivityLevel['转移到目标等级']`)"
              :label-width="300"
              :required="true"
            >
              <bk-select
                ref="sensitivityLevelSelect"
                style="width: 400px"
                v-model="levelValue"
                :searchable="false"
                :clearable="false"
                :show-select-all="false"
                @change="handleChange"
              >
                <bk-option
                  v-for="item in SENSITIVITY_LEVEL_ENUM"
                  :key="item.id"
                  :id="item.id"
                  :name="$t(`m.sensitivityLevel['${item.name}']`)"
                  :disabled="item.disabled"
                >
                  <bk-tag
                    type="filled"
                    :ext-cls="formatTagCustomClass(item)"
                    :theme="item.theme"
                  >
                    {{ $t(`m.sensitivityLevel['${item.name}']`) }}
                  </bk-tag>
                </bk-option>
              </bk-select>
            </bk-form-item>
            <bk-form-item class="level-transfer-preview">
              <RenderPermBoundary
                ref="renderPermBoundaryRef"
                :modules="['transferPreview']"
                :members-title="$t(`m.sensitivityLevel['转移预览']`)"
                :perm-length="selectTableList.length"
                :is-custom-title-style="true"
                @on-clear="handleClearAll"
              >
                <div slot="transferPreview" class="resources-transfer-level-table">
                  <IamTransferLevelTable
                    :select-table-list="selectTableList"
                    :level-value="levelValue"
                    @on-delete="handleDeleteAction"
                  />
                </div>
              </RenderPermBoundary>
            </bk-form-item>
          </bk-form>
        </div>
      </div>
      <div slot="footer">
        <div class="iam-level-transfer-side-footer">
          <bk-button
            class="level-footer-btn"
            theme="primary"
            :loading="submitLoading"
            @click="handleConfirmTransfer"
          >
            {{ $t(`m.sensitivityLevel['确认转移']`) }}
          </bk-button>
          <bk-button class="level-footer-btn" theme="default" @click="handleCancel">
            {{ $t(`m.common['取消']`) }}
          </bk-button>
        </div>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
  import { SENSITIVITY_LEVEL_ENUM } from '@/common/constants';
  import { leaveConfirm } from '@/common/leave-confirm';
  import RenderPermBoundary from '@/components/render-perm-boundary';
  import IamTransferLevelTable from './iam-transfer-level-table.vue';
  export default {
    components: {
      RenderPermBoundary,
      IamTransferLevelTable
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      title: {
        type: String
      },
      curSelectData: {
        type: Object
      }
    },
    data () {
      return {
        SENSITIVITY_LEVEL_ENUM,
        levelValue: 'L2',
        width: 960,
        isShowSideSlider: false,
        submitLoading: false,
        selectTableList: []
      };
    },
    computed: {
      formatTagCustomClass () {
        return (payload) => {
          return ['L5'].includes(payload.id)
            ? 'sensitivity-level-select-tag sensitivity-level-select-tag-custom'
            : 'sensitivity-level-select-tag';
        };
      }
    },
    watch: {
      show: {
        handler (value) {
          this.isShowSideSlider = !!value;
          if (this.isShowSideSlider) {
            this.$nextTick(() => {
              this.$refs.renderPermBoundaryRef
                && this.$refs.renderPermBoundaryRef.handleExpanded('transferPreview');
            });
          }
        },
        immediate: true
      },
      curSelectData: {
        handler (value) {
          if (value && value.tableList) {
            this.selectTableList = [...value.tableList];
          }
        },
        immediate: true
      }
    },
    methods: {
      handleChange (payload) {
        this.levelValue = payload;
      },

      handleDeleteAction (payload) {
        window.changeAlert = true;
        this.selectTableList.splice(this.selectTableList.indexOf(payload), 1);
      },

      handleClearAll () {
        window.changeAlert = true;
        this.selectTableList = [];
      },

      async handleConfirmTransfer () {
        if (!this.selectTableList.length) {
          return this.$t(`m.sensitivityLevel['转移预览的内容不能为空']`);
        }
        window.changeAlert = false;
        this.submitLoading = true;
        try {
          const params = {
            actions: this.selectTableList.map(({ action_id, system_id }) => ({
              id: action_id,
              system_id
            })),
            sensitivity_level: this.levelValue
          };
          const { code } = await this.$store.dispatch(
            'sensitivityLevel/updateActionsSensitivityLevel',
            params
          );
          if (code === 0) {
            this.$emit('on-confirm');
            this.messageSuccess(this.$t(`m.info['编辑成功']`), 3000);
          }
        } catch (e) {
          this.messageAdvancedError(e);
        } finally {
          this.submitLoading = false;
        }
      },

      handleCancel () {
        let cancelHandler = Promise.resolve();
        if (window.changeAlert) {
          cancelHandler = leaveConfirm();
        }
        cancelHandler.then(
          () => {
            this.$emit('update:show', false);
            this.resetData();
          },
          (_) => _
        );
      },

      resetData () {
        this.width = 960;
        this.selectTableList = [];
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-level-transfer-side {
  .level-transfer-content {
    padding: 0 40px;
  }
  &-content {
    height: calc(100vh - 114px);
    .level-transfer-content {
      padding-top: 4px;
      .bk-form-item {
        margin-top: 24px;
      }
    }
  }
  &-footer {
    margin-left: 40px;
    .level-footer-btn {
      margin-right: 8px;
    }
  }
}

/deep/ .level-transfer-preview {
  .horizontal-item {
    width: 100%;
    padding: 0;
    box-shadow: none;
    display: inline-block;
  }
}
</style>
