<template>
  <div :class="['system-render-perm-item', extCls]">
    <div
      class="header"
      @click="handleExpanded">
      <Icon bk class="expanded-icon" :type="isExpanded ? 'down-shape' : 'right-shape'" />
      <template v-if="!externalSystemsLayout.userGroup.groupDetail.hideGroupPermExpandTitle">
        <label class="title">{{ title }}</label>
        <div class="sub-title">
          <div v-if="templateCount > 0 || policyCount > 0">
            <span>(</span><span>{{ $t(`m.common['关联']`) }}</span>
          </div>
          <div v-if="templateCount > 0">
            <span class="number">{{ templateCount }}</span>
            <span>{{ $t(`m.common['个']`) }}{{ $t(`m.nav['权限模板']`)}}<span v-if="policyCount === 0 && !externalCustom">)
            </span>
            </span>
          </div>
          <template v-if="templateCount > 0 && policyCount > 0 && !externalCustom">{{ $t(`m.common['，']`) }}</template>
          <div v-if="policyCount > 0 && !externalCustom">
            <span class="number">{{ policyCount }}</span>
            <span>{{ $t(`m.common['个']`)}}{{ $t(`m.perm['自定义权限']`) }})</span>
          </div>
        </div>
      </template>
      <div
        v-else
        ref="externalCustomContent"
        class="flex-between"
      >
        <span class="title">{{ title }}</span>
        <div class="external-custom-count">
          <span :class="
            [
              { 'external-perm-text': !['zh-cn'].includes(language) }
            ]"
          >
            {{ $t(`m.info['权限个数']`, { value: templateCount + policyCount }) }}
          </span>
        </div>
      </div>
    </div>
    <div class="content" v-if="isExpanded">
      <div class="slot-content">
        <slot />
      </div>
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex';
  export default {
    name: '',
    props: {
      expanded: {
        type: Boolean,
        default: false
      },
      title: {
        type: String,
        default: ''
      },
      policyCount: {
        type: Number,
        default: 0
      },
      templateCount: {
        type: Number,
        default: 0
      },
      extCls: {
        type: String,
        default: ''
      },
      groupSystemListLength: {
        type: Number,
        default: 0
      },
      externalCustom: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isExpanded: false,
        role: '',
        language: window.CUR_LANGUAGE
      };
    },
    computed: {
      ...mapGetters(['externalSystemsLayout'])
    },
    watch: {
      expanded (value) {
        this.isExpanded = !!value;
      }
    },
    created () {
      // this.isShowTable();
    },
    methods: {
      isShowTable () {
        if (this.groupSystemListLength === 1 && this.templateCount >= 1) {
          this.handleExpanded();
        } else if (this.groupSystemListLength === 1 && this.templateCount === 0 && this.policyCount >= 1) {
          this.handleExpanded();
        }
      },
      handlePackUp () {
        this.isExpanded = false;
        this.$emit('update:expanded', false);
        this.$emit('on-expanded', false);
      },

      handleExpanded () {
        this.isExpanded = !this.isExpanded;
        console.log(this.isExpanded);
        this.$emit('update:expanded', true); // 更新expanded
        this.$emit('on-expanded', this.isExpanded); // 执行on-expanded
        this.$nextTick(() => {
          if (this.$refs.externalCustomContent) {
            this.$emit('on-set-external', { width: this.$refs.externalCustomContent.offsetWidth });
          }
        });
      }
    }
  };
</script>

<style lang="postcss" scoped>
.system-render-perm-item {
  background-color: #DCDEE5;
  min-height: 40px;
  .header {
    display: flex;
    justify-content: flex-start;
    position: relative;
    padding: 0 28px;
    height: 40px;
    line-height: 40px;
    font-size: 12px;
    color: #63656e;
    border-radius: 2px;
    cursor: pointer;
    .expanded-icon {
      position: absolute;
      top: 15px;
      left: 10px;
      color: #979BA5;
    }
    .title {
      font-weight: 700;
      font-size: 12px;
      color: #313238;
    }
    .sub-title {
      display: flex;
      margin-left: 8px;
      color: #63656E;
      &.no-margin {
        margin-left: 0;
      }
      &.set-margin {
        margin-left: 42px;
      }
      .number {
        font-weight: 600;
        color: #3A84FF;
      }
    }
    .external-perm-text {
      padding-left: 5px;
    }
    .external-custom-count {
      margin-left: 5px;
    }
  }
  .content {
    position: relative;
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
  }
  &.is-not-expanded {
    &:hover {
      .header {
        cursor: pointer;
      }
    }
  }
}
</style>
