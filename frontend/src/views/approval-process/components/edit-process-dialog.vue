<template>
  <lower-component>
    <bk-dialog
      v-model="isShowDialog"
      width="480"
      :title="$t(`m.approvalProcess['批量修改审批流程']`)"
      :mask-close="false"
      header-position="left"
      @after-leave="handleAfterLeave">
      <bk-select
        v-model="curProcessValue"
        style="width: 430px;"
        :popover-min-width="430"
        :multiple="false"
        searchable>
        <bk-option v-for="option in list"
          :key="option.id"
          :id="option.id"
          :name="option.name">
        </bk-option>
      </bk-select>
      <template slot="footer">
        <div>
          <bk-button
            theme="primary"
            :disabled="disbaled"
            :loading="loading"
            @click="handleSumbit">
            {{ $t(`m.common['确定']`) }}
          </bk-button>
          <bk-button @click="handleCancel">
            {{ $t(`m.common['取消']`) }}
          </bk-button>
        </div>
      </template>
    </bk-dialog>
  </lower-component>
</template>
<script>
  import lowerComponent from 'lower-component';
  export default {
    name: '',
    components: {
      lowerComponent
    },
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
      },
      list: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        isShowDialog: false,
        curProcessValue: ''
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
      handleSumbit () {
        this.$emit('on-submit', this.curProcessValue);
      },

      handleCancel () {
        this.$emit('on-cancel');
      },
            
      handleAfterLeave () {
        this.curProcessValue = '';
        this.$emit('update:show', false);
        this.$emit('on-after-leave');
      }
    }
  };
</script>
