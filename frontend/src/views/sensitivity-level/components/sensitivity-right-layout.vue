<template>
  <div class="sensitivity-right-layout">
    <bk-tab
      ref="tabRef"
      type="unborder-card"
      :active.sync="tabActive"
      :key="tabKey"
      @tab-change="handleTabChange"
    >
      <bk-tab-panel v-for="(panel, index) in panels" v-bind="panel" :key="index">
        <template slot="label">
          <bk-tag
            v-if="panel.tag"
            type="filled"
            :theme="panel.theme"
            :ext-cls="formatTagClass(panel)"
          >
            {{ $t(`m.sensitivityLevel['${panel.tag}']`) }}
          </bk-tag>
          <span class="panel-label">
            {{ $t(`m.sensitivityLevel['${panel.label}']`) }}
          </span>
          <span class="panel-count">({{ panel.count || 0 }})</span>
        </template>
        <div
          class="content-wrapper"
          v-bkloading="{ isLoading: componentLoading, opacity: 1 }"
        >
          <component
            v-if="tabActive === panel.name"
            ref="sensitivityComRef"
            :is="curCom"
            :key="comKey"
            :cur-system-data="curSystemData"
            :tab-active="tabActive"
          />
        </div>
      </bk-tab-panel>
    </bk-tab>
  </div>
</template>

<script>
  import { bus } from '@/common/bus';
  import SensitivityLevelTable from '@/views/sensitivity-level/components/sensitivity-level-table.vue';
  export default {
    components: {
      SensitivityLevelTable
    },
    props: {
      curSystemData: {
        type: Object
      }
    },
    data () {
      return {
        componentLoading: false,
        tabActive: 'all',
        tabKey: 'tab-key',
        comKey: -1,
        panels: [
          {
            name: 'all',
            tag: '',
            theme: '',
            label: '全部等级',
            count: 0
          },
          {
            name: 'L1',
            tag: '不敏感',
            theme: 'default',
            label: '等级',
            count: 0
          },
          {
            name: 'L2',
            tag: '低',
            theme: 'success',
            label: '等级',
            count: 0
          },
          {
            name: 'L3',
            tag: '中',
            theme: 'warning',
            label: '等级',
            count: 0
          },
          {
            name: 'L4',
            tag: '高',
            theme: 'danger',
            label: '等级',
            count: 0
          },
          {
            name: 'L5',
            tag: '极高',
            theme: 'danger',
            label: '等级',
            count: 0
          }
        ],
        COM_MAP: Object.freeze(
          new Map([[['all', 'L1', 'L2', 'L3', 'L4', 'L5'], 'SensitivityLevelTable']])
        )
      };
    },
    computed: {
      formatTagClass () {
        return (payload) => {
          return ['L5'].includes(payload.name) ? 'panel-tag panel-tag-custom' : 'panel-tag';
        };
      },
      curCom () {
        let com = '';
        for (const [key, value] of this.COM_MAP.entries()) {
          if (Object.keys(this.curSystemData).length && key.includes(this.tabActive)) {
            com = value;
            break;
          }
        }
        return com;
      }
    },
    watch: {
      curSystemData: {
        handler (newVal, oldVal) {
          if (newVal !== oldVal && oldVal) {
            this.tabActive = 'all';
          }
        },
        immediate: true
      }
    },
    mounted () {
      this.$once('hook:beforeDestroy', () => {
        bus.$off('on-systems-level-count');
        bus.$off('on-tab-level-count');
      });
      bus.$on('on-systems-level-count', (payload) => {
        if (payload && Object.keys(payload).length > 0) {
          this.$nextTick(() => {
            this.panels.forEach((item) => {
              this.$set(item, 'count', payload[item.name] || 0);
            });
            this.$refs.tabRef
              && this.$refs.tabRef.$refs.tabLabel
              && this.$refs.tabRef.$refs.tabLabel.forEach((label) => label.$forceUpdate());
            // 首次加载不刷新key
            if (!payload.isFirst) {
              this.comKey = +new Date();
            }
          });
        }
      });
      bus.$on('on-tab-level-count', async (payload) => {
        if (payload && Object.keys(payload).length > 0) {
          this.fetchSystemLevelCount(payload);
        }
      });
    },
    methods: {
      async fetchSystemLevelCount (payload) {
        const { count, name, system_id, isSearch, isTransfer } = payload;
        if (isSearch) {
          const curIndex = this.panels.findIndex((item) => item.name === name);
          if (curIndex > -1) {
            this.$set(this.panels[curIndex], 'count', count);
            this.$nextTick(() => {
              this.$refs.tabRef
                && this.$refs.tabRef.$refs.tabLabel
                && this.$refs.tabRef.$refs.tabLabel.forEach((label) => label.$forceUpdate());
            });
          }
        } else {
          try {
            const { code, data } = await this.$store.dispatch(
              'sensitivityLevel/getSensitivityLevelCount',
              {
                system_id
              }
            );
            if (data && code === 0) {
              this.$nextTick(() => {
                this.panels.forEach((item) => {
                  // 处理搜索之后再单个或批量转移，列表接口与获取数量接口不同步问题
                  if (item.name === name && isTransfer) {
                    this.$set(item, 'count', count || 0);
                  } else {
                    this.$set(item, 'count', data[item.name] || 0);
                  }
                });
                this.$refs.tabRef
                  && this.$refs.tabRef.$refs.tabLabel
                  && this.$refs.tabRef.$refs.tabLabel.forEach((label) => label.$forceUpdate());
              });
            }
          } catch (e) {
            this.messageAdvancedError(e);
          }
        }
      },

      handleTabChange () {
        this.$refs.sensitivityComRef
          && this.$refs.sensitivityComRef.length
          && this.$refs.sensitivityComRef[0].fetchSensitivityLevelList(true);
        this.fetchSystemLevelCount({ system_id: this.curSystemData.id });
      }
    }
  };
</script>

<style lang="postcss" scoped>
.sensitivity-right-layout {
  .panel-tag-custom {
    background-color: #c02121;
  }
}
</style>
