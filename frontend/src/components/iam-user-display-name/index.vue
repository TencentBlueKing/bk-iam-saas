<template>
  <div>
    <div v-if="!htmlConfig.disabled" class="container-user-display-name">
      <bk-user-display-name :user-id="getDisplayTooltip" />
    </div>
    <template v-if="!$slots.customDisplayName">
      <div class="tenant-display-name" v-bk-tooltips="htmlConfig">
        <template v-if="['--'].includes(userId) || !userId">--</template>
        <bk-user-display-name v-else :user-id="userId" />
      </div>
    </template>
    <!-- 处理自定义样式的多租户人员数组 -->
    <template v-if="$slots.customDisplayName">
      <div v-bk-tooltips="htmlConfig">
        <slot name="customDisplayName" />
      </div>
    </template>
  </div>
</template>

<script>
  export default {
    props: {
      userId: {
        type: [Array, String],
        default: ''
      },
      displayValue: {
        type: Array,
        default: () => []
      },
      tooltipConfig: {
        type: Object,
        default: () => {}
      }
    },
    data () {
      return {
        htmlConfig: {
          allowHtml: true,
          theme: 'dark',
          content: '.container-user-display-name',
          placement: 'top-start',
          disabled: false
        }
      };
    },
    computed: {
      getDisplayTooltip () {
        if (this.displayValue.length) {
          const results = [...this.displayValue];
          const isExistUserName = results.some(v => v.username);
          if (isExistUserName) {
            const nameList = results.map(v => v.username);
            return nameList.join();
          }
          return results;
        }
        return this.userId;
      }
    },
    watch: {
      tooltipConfig: {
        handler (value = {}) {
          this.htmlConfig = { ...this.htmlConfig, ...value };
        },
        immediate: true
      }
    }
  };
</script>
