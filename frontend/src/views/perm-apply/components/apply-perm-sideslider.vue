<template>
  <bk-sideslider
    :is-show.sync="isVisible"
    :quick-close="false"
    :width="720"
    ext-cls="iam-apply-perm-sideslider"
    :title="title"
    @animation-end="handleSliderClose">
    <div slot="content" class="content-wrapper">
      <div class="apply-perm-wrapper">
        <div class="left">
          <template v-if="relateActionData.length > 0">
            <tree
              :data="relateActionData"
              multiple
              :is-broadcast="false"
              :has-border="true"
              :cur-select="curSelectId"
              @on-click="handleTreeClick"
              @on-check="handleTreeChecked">
            </tree>
          </template>
          <template v-else>
            <iam-svg ext-cls="empty-tree-icon" />
          </template>
        </div>
        <div class="right">
          <div class="title">
            {{ $t(`m.related['其它操作权限']`) }}
          </div>
          <template v-if="relateActionList.length > 0">
            <div class="checkbox-inner"
              v-for="(item, index) in relateActionList"
              :key="index">
              <bk-checkbox
                v-model="item.checked"
                :title="item.name"
                @change="handleRelateChange(...arguments, item)">
                {{ item.name }}
              </bk-checkbox>
            </div>
          </template>
          <template v-else>
            <iam-svg ext-cls="empty-icon" />
          </template>
        </div>
      </div>
    </div>
    <div slot="footer">
      <bk-button style="margin-left: 30px;" theme="primary" @click="handleSumbit">
        {{ $t(`m.common['提交']`) }}
      </bk-button>
      <bk-button style="margin-left: 10px;" v-if="canPreview" @click="handlePreview">
        {{ $t(`m.common['预览']`) }}
      </bk-button>
      <bk-button style="margin-left: 10px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
    </div>
  </bk-sideslider>
</template>

<script>
  import _ from 'lodash';
  import Tree from '@/components/tree';
  export default {
    name: '',
    components: {
      Tree
    },
    props: {
      isShow: {
        type: Boolean,
        default: false
      },
      data: {
        type: Array,
        default: () => []
      },
      value: {
        type: Array,
        default: () => []
      },
      title: {
        type: String,
        default: ''
      },
      canPreview: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isVisible: false,
        relateActionData: [],
        initRequestQueue: [],
        curSelectId: '',
        relateActionMap: {},
        curSelectedNodes: [],
        curRemoteValue: [],
        bigData: []
      };
    },
    computed: {
      relateActionList () {
        if (this.curSelectId === '' || !this.relateActionMap[this.curSelectId]) {
          return [];
        }
        return this.relateActionMap[this.curSelectId];
      },
      values () {
        const relateActions = [];
        for (const key in this.relateActionMap) {
          const hasSelecteds = this.relateActionMap[key]
            .filter(item => item.checked)
            .map(({ id, name }) => ({ id, name }));
          relateActions.push(...hasSelecteds);
        }
        return this.curSelectedNodes.concat(relateActions);
      }
    },
    watch: {
      isShow: {
        handler (value) {
          this.isVisible = !!value;
        },
        immediate: true
      },
      data: {
        handler (value) {
          this.relateActionMap = {};
          this.curSelectedNodes = [];
          this.curSelectId = '';
          if (value.length > 0) {
            this.relateActionData = _.cloneDeep(value);
          } else {
            this.relateActionData = [];
          }
        },
        immediate: true
      },
      value: {
        handler (val) {
          this.handleInitData(this.relateActionData, true, val);
        },
        immediate: true
      }
    },
    methods: {
      handleInitData (payload = [], isDisabled = true, selectedValues = []) {
        payload.forEach(item => {
          const subflag = item.sub_actions.length > 0;
          const relateFlag = item.related_actions.length > 0;
          this.$set(item, 'display_name', item.name);
          if (subflag) {
            this.$set(item, 'expanded', subflag);
            this.$set(item, 'children', _.cloneDeep(item.sub_actions));
          }
          this.$set(item, 'count', item.related_actions.length);
          this.$set(item, 'hasSelectCount', 0);
          item.name = `${item.display_name}(${item.hasSelectCount}/${item.count})`;
          if (selectedValues.includes(item.id)) {
            this.curSelectedNodes.push({
              id: item.id,
              name: item.display_name
            });
          }
          this.$set(item, 'checked', selectedValues.includes(item.id) || isDisabled);
          this.$set(item, 'disabled', isDisabled);
          if (relateFlag) {
            const tempRelatedActions = item.related_actions.map(subItem => {
              subItem.checked = selectedValues.includes(subItem.id);
              if (subItem.checked) {
                ++item.hasSelectCount;
                item.name = `${item.display_name}(${item.hasSelectCount}/${item.count})`;
              }
              subItem.parentId = item.id;
              return subItem;
            });
            this.$set(this.relateActionMap, item.id, _.cloneDeep(tempRelatedActions));
            if (this.curSelectId === '') {
              this.curSelectId = item.id;
            }
          }
          if (item.children && item.children.length > 0) {
            this.handleInitData(item.children, false, selectedValues);
          }
        });
        return payload;
      },

      handlePreview () {
        this.$emit('on-preview', this.values);
      },

      handleSliderClose () {
        this.$emit('update:isShow', false);
        this.$emit('animation-end');
      },

      handleCancel () {
        this.$emit('update:isShow', false);
        this.$emit('on-cancel', false);
      },

      handleSumbit () {
        this.$emit('on-sumbit', this.values);
      },

      handleRelateChange (newVal, oldVal, val, payload) {
        this.handleSetNodeNameDisplay(this.relateActionData, payload.parentId, newVal);
      },

      handleSetNodeNameDisplay (payload, id, checked) {
        for (let i = 0; i < payload.length; i++) {
          const node = payload[i];
          if (node.id === id) {
            if (checked) {
              if (node.hasSelectCount < node.count) {
                ++node.hasSelectCount;
              }
            } else {
              if (node.hasSelectCount > 0) {
                --node.hasSelectCount;
              }
            }
            node.name = `${node.display_name}(${node.hasSelectCount}/${node.count})`;
            break;
          } else {
            if (node.children && node.children.length > 0) {
              this.handleSetNodeNameDisplay(node.children, id, checked);
            }
          }
        }
        return false;
      },

      handleTreeClick (payload) {
        this.curSelectId = payload.id;
      },

      handleTreeChecked (node, checked) {
        if (checked) {
          this.curSelectId = node.id;
          this.curSelectedNodes.push({
            id: node.id,
            name: node.display_name
          });
        } else {
          const index = this.curSelectedNodes.findIndex(item => item.id === node.id);
          this.curSelectedNodes.splice(index, 1);
        }
      }
    }
  };
</script>

<style>
    @import './apply-perm-sideslider.css';
</style>
