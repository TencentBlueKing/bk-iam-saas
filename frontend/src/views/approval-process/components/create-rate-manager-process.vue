<template>
  <div class="iam-create-rate-manager-process-wrapper">
    <label class="title">{{ $t(`m.approvalProcess['选择审批流程']`) }}</label>
    <bk-select
      :value="value"
      :clearable="false"
      searchable
      style="margin-top: 6px; width: 360px;"
      @selected="handleProcessSelect">
      <bk-option v-for="option in list"
        :key="option.id"
        :id="option.id"
        :name="option.name">
      </bk-option>
    </bk-select>
  </div>
</template>
<script>
  export default {
    name: '',
    props: {
      list: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        value: '0'
      };
    },
    methods: {
      handleProcessSelect (value, option) {
      }
    }
  };
</script>
<style lang="postcss">
    .iam-create-rate-manager-process-wrapper {
        .title {
            display: block;
            line-height: 20px;
            font-size: 12px;
            font-weight: 600;
        }
    }
</style>
