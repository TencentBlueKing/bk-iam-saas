<template>
  <div class="iam-resource-select">
    <template v-if="isSingle">
      <section class="single-resource-name" :title="list[0].name">{{ list[0].name }}</section>
    </template>
    <bk-select
      :value="value"
      :clearable="false"
      searchable
      v-else
      ext-cls="iam-topology-select-cls"
      @selected="handleSelected">
      <bk-option v-for="option in list"
        :key="`${option.id}&${option.system_id}`"
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
      },
      value: {
        type: String,
        default: ''
      }
    },
    data () {
      return {

      };
    },
    computed: {
      isSingle () {
        // 如果大于1 则为下拉框
        return this.list.length === 1;
      }
    },
    methods: {
      handleSelected (value, option) {
        this.$emit('on-select', value);
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .single-resource-name {
        position: relative;
        padding: 0 36px 0 10px;
        display: block;
        max-width: 100%;
        line-height: 40px;
        border-bottom: 1px solid #c4c6cc;
        font-size: 12px;
        color: #63656e;
        background: #fff;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .iam-resource-select {
        width: 100%;
    }
</style>
