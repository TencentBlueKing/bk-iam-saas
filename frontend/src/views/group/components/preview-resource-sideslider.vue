<template>
  <bk-sideslider
    :is-show.sync="isVisible"
    :quick-close="true"
    :width="881"
    ext-cls="iam-preview-resource-sideslider"
    :title="title"
    @animation-end="handleSliderClose">
    <div slot="content" class="content-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
      <bk-tab
        v-if="!isLoading"
        :active.sync="active"
        ext-cls="resource-compare-tab-cls"
        type="unborder-card">
        <bk-tab-panel
          v-for="(panel, index) in panels"
          v-bind="panel"
          :key="index">
          <template v-if="panel.tabType === 'resource'">
            <template v-if="['update', 'delete', 'add'].includes(panel.tag)">
              <compare-detail :data="panel.data" />
            </template>
            <template v-else>
              <condition-detail :data="panel.data" />
            </template>
          </template>
          <template v-else>
            <div class="relate-resource-wrapper">
              <tree :data="panel.data" :has-border="true" :is-view="true" />
            </div>
          </template>
        </bk-tab-panel>
      </bk-tab>
    </div>
  </bk-sideslider>
</template>

<script>
  import _ from 'lodash';
  import CompareCondition from '@/model/compare-condition';
  import CompareDetail from '@/components/render-resource/compare-detail';
  import ConditionDetail from '@/components/render-resource/detail';
  import Tree from '@/components/attach-action-preview/attach-action-tree';
  export default {
    name: '',
    components: {
      CompareDetail,
      ConditionDetail,
      Tree
    },
    props: {
      isShow: {
        type: Boolean,
        default: false
      },
      title: {
        type: String,
        default: ''
      },
      params: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        isVisible: false,
        isLoading: false,
        conditionData: [],
        requestFunQueue: [],
        panels: [
          { name: 'host', label: '主机实例', data: [], tag: 'unchanged', tabType: 'resource' }
        ],
        active: 'host'
      };
    },
    computed: {
    },
    watch: {
      isShow: {
        handler (value) {
          this.isVisible = !!value;
        },
        immediate: true
      },
      params: {
        handler (value) {
          if (value.length > 0) {
            const panels = [];
            value.forEach(item => {
              if (item.tabType === 'resource') {
                if (['update', 'delete', 'add'].includes(item.tag)) {
                  const requestParams = Object.assign({}, item);
                  delete requestParams.tag;
                  delete requestParams.tabType;
                  this.requestFunQueue.push(this.fetchConditionCompare(requestParams));
                  panels.push({
                    label: `${item.related_resource_type.name} ${this.$t(`m.common['实例']`)}`,
                    name: item.related_resource_type.type,
                    data: [],
                    tag: item.tag,
                    tabType: item.tabType
                  });
                } else {
                  panels.push({
                    label: `${item.related_resource_type.name} ${this.$t(`m.common['实例']`)}`,
                    name: item.related_resource_type.type,
                    data: item.related_resource_type.condition,
                    tag: item.tag,
                    tabType: item.tabType
                  });
                }
              } else {
                panels.push({
                  label: this.$t(`m.permApply['关联权限']`),
                  name: 'relate',
                  data: item.data,
                  tabType: item.tabType
                });
              }
            });
            this.panels = _.cloneDeep(panels);
            this.active = this.panels[0].name;
            if (this.requestFunQueue.length > 0) {
              this.fetchData();
            }
          } else {
            this.conditionData = [];
            this.requestFunQueue = [];
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchData () {
        this.isLoading = true;
        try {
          const res = await Promise.all(this.requestFunQueue);
          const panels = [];
          res.forEach((item, index) => {
            const conditionData = item.data.map(subItem => new CompareCondition(subItem));
            panels.push({
              name: this.params[index].related_resource_type.type,
              label: `${this.params[index].related_resource_type.name} ${this.$t(`m.common['实例']`)}`,
              data: conditionData
            });
            const curPanel = this.panels.find(
              panel => panel.name === this.params[index].related_resource_type.type
            );
            curPanel.data = _.cloneDeep(conditionData);
          });
          if (this.panels[0].data.length > 0) {
            if (this.panels[0].data[0].hasOwnProperty('instance')) {
              this.panels[0].data[0].instanceExpanded = true;
            }
            if (this.panels[0].data[0].hasOwnProperty('attribute')) {
              this.panels[0].data[0].attributeExpanded = true;
            }
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      handleMatchCondition (payload) {
      },

      fetchConditionCompare (payload) {
        return this.$store.dispatch('permTemplate/templateConditionCompare', { ...payload });
      },

      handleSliderClose () {
        this.$emit('update:isShow', false);
        this.$emit('animation-end');
      }
    }
  };
</script>

<style lang="postcss">
    .iam-preview-resource-sideslider {
        z-index: 2503;
        .content-wrapper {
            position: relative;
            height: calc(100vh - 61px);
            .resource-compare-tab-cls {
                .bk-tab-section {
                    padding: 20px 0 0 0;
                }
            }
            .relate-resource-wrapper {
                padding: 0 24px;
            }
        }
    }
</style>
