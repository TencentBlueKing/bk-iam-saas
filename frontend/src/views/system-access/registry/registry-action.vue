<template>
  <div :class="['registry-action-item', extCls]">
    <div class="header" @click="handleExpanded" :style="{ position: isExpanded ? 'absolute' : 'relative' }">
      <Icon bk class="expanded-icon" :type="isExpanded ? 'down-shape' : 'right-shape'" />
      <label class="title">{{ title }}</label>
      <div class="sub-title" v-if="!isExpanded">
        <bk-button theme="primary" text @click="test">
          {{ $t(`m.access['查看json源码']`) }}
        </bk-button>
      </div>
    </div>
    <div v-if="isExpanded" class="btn-wrapper">
      <template v-if="!isEdit">
        <bk-button size="small" @click="isEdit = true">{{ $t(`m.common['编辑']`) }}</bk-button>
      </template>
      <template v-else>
        <bk-button size="small" theme="primary">{{ $t(`m.common['保存']`) }}</bk-button>
        <bk-button size="small" @click.stop.prevent="cancelEdit">{{ $t(`m.common['取消']`) }}</bk-button>
        <bk-button size="small">{{ $t(`m.common['删除']`) }}</bk-button>
      </template>
    </div>
    <div class="content" v-if="isExpanded">
      <div class="slot-content">
        <slot />
      </div>
    </div>
  </div>
</template>
<script>
  export default {
    props: {
      // expanded
      expanded: {
        type: Boolean,
        default: false
      },
      // edit
      edit: {
        type: Boolean,
        default: true
      },
      // title
      title: {
        type: String,
        default: ''
      },
      // extCls
      extCls: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        isExpanded: this.expanded,
        isEdit: this.edit
      };
    },
    watch: {
      /**
       * expanded
       */
      expanded (value) {
        this.isExpanded = !!value;
        this.isEdit = !!value;
      }
    },
    methods: {
      /**
       * test
       */
      test (e) {
        e.stopPropagation();
      },

      /**
       * cancelEdit
       */
      cancelEdit () {
        this.isEdit = false;
      },

      /**
       * handlePackup
       */
      handlePackup () {
        this.isEdit = false;
        this.isExpanded = false;
        this.$emit('update:expanded', false);
        this.$emit('on-expanded', false);
      },

      /**
       * handleExpanded
       */
      handleExpanded () {
        this.isExpanded = !this.isExpanded;
        this.$emit('update:expanded', true);
        this.$emit('on-expanded', this.isExpanded);
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .registry-action-item {
        position: relative;
        background: #fff;
        border-radius: 2px;
        border: 1px solid #fff;
        box-shadow: 0px 1px 2px 0px rgba(49, 50, 56, .1);
        &:hover {
            box-shadow: 0px 2px 4px 0px rgba(49, 50, 56, .15);
        }
        &.is-not-expanded:hover {
            .header {
                cursor: pointer;
            }
        }
        .header {
            display: flex;
            justify-content: flex-start;
            padding: 0 30px;
            height: 60px;
            line-height: 60px;
            font-size: 14px;
            color: #63656e;
            border-radius: 2px;
            cursor: pointer;
            .expanded-icon {
                position: absolute;
                top: 23px;
                left: 10px;
            }
            .title {
                font-weight: 600;
                cursor: pointer;
            }
            .sub-title {
                position: absolute;
                right: 18px;
                .bk-link {
                    margin-left: 10px;
                }
            }
        }
        .btn-wrapper {
            position: absolute;
            right: 16px;
            top: 18px;
            z-index: 1;
            .bk-button {
                margin-left: 5px;
            }
        }
        .content {
            position: relative;
            margin-top: 15px;
            width: calc(100% - 100px);
            left: 100px;
            .expand-action {
                padding: 20px 0 5px 0;
                width: 100%;
                line-height: 16px;
                font-size: 12px;
                color: #979ba5;
                text-align: center;
                cursor: pointer;
                i {
                    font-size: 16px;
                }
            }
            .slot-content {
                padding: 0 20px 0 30px;
            }
        }
    }
</style>
