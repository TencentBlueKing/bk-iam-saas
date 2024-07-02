<template>
  <bk-popconfirm
    ref="iamResourcePopover"
    trigger="mouseenter"
    ext-cls="iam-view-resource-tooltips-cls"
    :confirm-button-is-text="false"
    placement="right"
    :confirm-text="''"
    cancel-text="">
    <div slot="content">
      <template v-if="!isEmpty">
        <p
          style="line-height: 18px;"
          v-for="(item, index) in displayList"
          :title="`ID：${item.id}`"
          :key="index">
          {{ item.display_name }}
        </p>
        <bk-button
          text
          theme="primary"
          size="small"
          v-if="isShowAction"
          style="margin-left: -10px;"
          @click="handleConfirm">
          {{ $t(`m.common['查看更多']`) }}
        </bk-button>
      </template>
      <template v-else>
        {{ value }}
      </template>
    </div>
    <template>
      <span v-if="isHtml" class="text" :style="{ 'max-width': `${maxWidth}px` }" v-html="value" />
      <span v-else class="text" :style="{ 'max-width': `${maxWidth}px` }">
        {{ value }}
      </span>
    </template>
  </bk-popconfirm>
</template>
<script>
  import Instance from '@/model/instance';
  export default {
    props: {
      data: {
        type: Array,
        default: () => []
      },
      value: {
        type: String,
        default: ''
      },
      maxWidth: {
        type: Number,
        default: 500
      },
      isShowPopover: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        displayList: [],
        originList: []
      };
    },
    computed: {
      isShowAction () {
        return this.originList.length > 10;
      },
      isEmpty () {
        return this.displayList.length < 1;
      },
      isHtml () {
        return ['actionsTemplateEdit'].includes(this.$route.name);
      }
    },
    watch: {
      data: {
        handler (value) {
          const arr = [];
          if (value.length > 0) {
            value.forEach(item => {
              (item.instance || []).forEach(subItem => {
                arr.push(...new Instance(subItem).displayPath);
              });
            });
            this.originList.splice(0, this.originList.length, ...arr);
            this.displayList = this.originList.slice(0, 10);
          }
        },
        immediate: true
      },
      isShowPopover: {
        handler (value) {
          if (['audit'].includes(this.$route.name)) {
            this.$nextTick(() => {
              const resourcePopover = this.$refs.iamResourcePopover;
              if (resourcePopover && resourcePopover.$refs.popover) {
                value ? resourcePopover.$refs.popover.showHandler() : resourcePopover.$refs.popover.hideHandler();
              }
            });
          }
        },
        deep: true
      }
    },
    methods: {
      handleConfirm () {
        this.$emit('on-view');
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-view-resource-tooltips-cls {
        width: 300px;
    }
    .text {
        display: inline-block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        vertical-align: middle;
    }
</style>
