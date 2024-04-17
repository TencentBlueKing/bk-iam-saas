<template>
  <div class="template-actions-table">
    <div class="template-actions-table-header">
      <render-search>
        <bk-button theme="primary" @click="handleEdit">
          {{ $t(`m.common['编辑']`) }}
        </bk-button>
        <bk-checkbox v-model="isShowAllAction" :true-value="false" :false-value="true" class="is-show-action">
          {{ $t(`m.actionsTemplate['仅展示已勾选的操作']`) }}
        </bk-checkbox>
        <div slot="right">
          <bk-input
            style="width: 540px"
            v-model="keyWord"
            :placeholder="$t(`m.actionsTemplate['搜索 模板名称']`)"
            :clearable="true"
            @enter="handleTableSearch"
            @right-icon-click="handleTableSearch"
            @clear="handleClear"
          />
        </div>
      </render-search>
    </div>
  </div>
</template>

<script>
  // import _ from 'lodash';
  // import MemberTable from '@/views/group/components/member-table';
  export default {
    components: {
      // MemberTable
    },
    props: {
      curDetailData: {
        type: Object,
        default: () => {
          return {};
        }
      }
    },
    data () {
      return {
        isShowAllAction: true,
        keyWord: ''
      };
    },
    methods: {
      handleEdit () {
        
      },

      handleTableSearch () {

      },

      handleClear () {

      }
    }
  };
</script>
<style lang="postcss" scoped>
.template-actions-table {
  padding: 0 24px;
  .is-show-action {
    margin-left: 12px;
  }
}
</style>
