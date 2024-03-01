<template>
  <div class="iam-resource-select">
    <!-- <template v-if="isSingle">
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
    </bk-select> -->
    <bk-tab
      :active.sync="active"
      type="card"
      ext-cls="iam-topology-tab-cls"
      :label-height="48"
      @tab-change="handleSelected"
    >
      <bk-tab-panel
        v-for="panel in list"
        v-bind="panel"
        :label="panel.name"
        :name="panel.id"
        :key="`${panel.id}&${panel.system_id}`"
      />
    </bk-tab>
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
      },
      isShowManual: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        active: '',
        tabList: []
      };
    },
    computed: {
      isSingle () {
        // 如果大于1 则为下拉框
        return this.list.length === 1;
      }
    },
    watch: {
      value: {
        handler (value) {
          if (value) {
            this.active = value;
          }
        },
        immediate: true
      },
      list: {
        handler (value) {
          if (value) {
            this.tabList = value;
            if (['instance:paste'].includes(this.selectionMode)) {
              const hasManual = this.tabList.find((item) => item.id === 'manualInput');
              if (!hasManual) {
                this.tabList.push({
                  name: this.$t(`m.common['手动输入']`),
                  id: 'manualInput',
                  system_id: this.tabList[0].system_id
                });
              }
            }
          }
        },
        immediate: true
      }
    },
    methods: {
      handleSelected (value) {
        this.$emit('on-select', value);
      }
    }
  };
</script>

<style lang="postcss" scoped>
/* .single-resource-name {
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
    } */
.iam-resource-select {
  width: 100%;
  background-color: #f5f7fa;
  color: #313238;
}
/deep/ .iam-topology-tab-cls {
  .bk-tab-section {
    padding: 0;
    border: 0;
  }
  .bk-tab-label-list {
    border-top: 0;
    .bk-tab-label-item {
      &.is-first {
        border-left: 0;
      }
      &.active {
        color: #63656e;
      }
    }
  }
}
</style>
