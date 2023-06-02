<template>
  <bk-dialog
    v-model="isShowDialog"
    width="480"
    title="修改审批流程"
    :mask-close="false"
    header-position="left"
    ext-cls="iam-edit-process-dialog"
    @after-leave="handleAfterEditLeave">
    <bk-select
      placeholder="请选择"
      v-model="curProcessValue"
      style="width: 430px;"
      :popover-min-width="430"
      :multiple="false"
      searchable>
      <bk-option v-for="option in processList"
        :key="option.process_id"
        :id="option.process_id"
        :name="option.process_name">
      </bk-option>
    </bk-select>
    <template slot="footer">
      <div>
        <bk-button theme="primary" :disabled="disbaled" :loading="loading" @click="handleSumbitEdit">
          确定
        </bk-button>
        <bk-button @click="hideCancelEdit">取消</bk-button>
      </div>
    </template>
  </bk-dialog>
</template>
<script>
  export default {
    name: '',
    props: {
      show: {
        type: Boolean,
        default: false
      },
      name: {
        type: String,
        default: ''
      },
      procssValue: {
        type: [String, Number],
        default: ''
      },
      loading: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isShowDialog: false,
        curProcessValue: '',
        processList: [
          {
            process_id: '1',
            process_name: '测试审批流程1'
          },
          {
            process_id: '2',
            process_name: '测试审批流程'
          }
        ]
      };
    },
    computed: {
      disbaled () {
        return this.curProcessValue === '';
      }
    },
    watch: {
      show: {
        handler (value) {
          this.isShowDialog = !!value;
        },
        immediate: true
      },
      procssValue: {
        handler (value) {
          this.curProcessValue = value;
        },
        immediate: true
      }
    },
    methods: {
      handleSumbitEdit () {
        this.$emit('on-sumbit', this.curProcessValue);
      },

      hideCancelEdit () {
        this.$emit('on-cancel');
      },

      handleAfterEditLeave () {
        this.$emit('update:show', false);
        this.$emit('on-after-leave');
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-edit-process-dialog {}
</style>
