<template>
  <div>
    <bk-table
      :data="tableList"
      :key="tableKey"
      :outer-border="false"
      :header-border="false"
      ext-cls="iam-transfer-level-table"
    >
      <bk-table-column :label="$t(`m.common['操作']`)">
        <template slot-scope="{ row }">
          <span :title="row.action_name">{{ row.action_name }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['所属系统']`)" prop="system_id">
        <template slot-scope="{ row }">
          {{ formaSystemText(row.system_id) }}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.sensitivityLevel['当前等级']`)">
        <template slot-scope="{ row }">
          <bk-tag
            type="filled"
            :ext-cls="formatTagCustomClass(row.sensitivity_level)"
            :theme="formatTagContent(row.sensitivity_level, 'theme')"
          >
            {{ formatTagContent(row.sensitivity_level, "name") }}
          </bk-tag>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.sensitivityLevel['目标等级']`)">
        <template>
          <bk-tag
            type="filled"
            :ext-cls="formatTagCustomClass(curTargetLevel.id)"
            :theme="formatTagContent(curTargetLevel.id, 'theme')"
          >
            {{ formatTagContent(curTargetLevel.id, "name") }}
          </bk-tag>
        </template>
      </bk-table-column>
      <!-- <bk-table-column :width="50">
        <template slot-scope="{ row }">
          <Icon
            type="delete-line"
            class="level-delete-icon"
            @click.stop="handleDelete(row)"
          />
        </template>
      </bk-table-column> -->
    </bk-table>
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { il8n } from '@/language';
  import { SENSITIVITY_LEVEL_ENUM } from '@/common/constants';
  export default {
    props: {
      selectTableList: {
        type: Array,
        default: () => []
      },
      levelValue: {
        type: String
      }
    },
    data () {
      return {
        tableList: [],
        initRequestQueue: [],
        curDeleteIds: [],
        systemFilter: [],
        curTargetLevel: {},
        tableKey: -1
      };
    },
    computed: {
    ...mapGetters(['allSystemList']),
    formaSystemText () {
      return (payload) => {
        const curSystem = this.allSystemList.find((item) => item.id === payload);
        if (curSystem) {
          return curSystem.name;
        }
        return '--';
      };
    },
    formatTagCustomClass () {
      return (payload) => {
        return ['L5'].includes(payload)
          ? 'sensitivity-level-select-tag sensitivity-level-select-tag-custom'
          : 'sensitivity-level-select-tag';
      };
    },
    formatTagContent () {
      return (payload, field) => {
        const result = SENSITIVITY_LEVEL_ENUM.find((item) => item.id === payload);
        if (result) {
          if (['name'].includes(field)) {
            return il8n('sensitivityLevel', result[field]);
          }
          return result[field];
        }
        return '--';
      };
    }
    },
    watch: {
      selectTableList: {
        handler (value) {
          this.tableList = [...value];
        },
        immediate: true
      },
      levelValue: {
        handler (newVal, oldVal) {
          if (newVal !== oldVal) {
            this.curTargetLevel = _.cloneDeep(
              SENSITIVITY_LEVEL_ENUM.find((item) => item.id === newVal)
            );
            this.tableKey = +new Date();
          }
        },
        immediate: true
      }
    },
    methods: {
      handleDelete (payload) {
        this.$emit('on-delete', payload);
      }
    }
  };
</script>

<style lang="postcss" scoped>
/deep/ .iam-transfer-level-table {
  border-top: 0;
  border-bottom: 0;
  .bk-table-empty-block {
    border-bottom: 1px solid #e6e6e6;
  }
  .level-delete-icon {
    font-size: 16px;
    cursor: pointer;
    &:hover {
      color: #3a84ff;
    }
  }
}
</style>
