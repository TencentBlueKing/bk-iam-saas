<template>
  <div :class="['iam-instance-content', { 'set-marging-top': hasGap }]">
    <div class="iam-instance-title">
      <span>{{ title || '--' }}</span>
      <div v-if="canEdit">
        <span>
          <span v-if="curLanguageIsCn">已选 {{ count }} 条</span>
          <span v-else>{{ count }} {{ $t(`m.common['条']`) }} {{ $t(`m.common['已选']`) }} </span>
        </span>
        <bk-button
          theme="primary"
          size="small"
          text
          style="padding: 0;"
          @click="handleSelectAll">
          {{ selectText }}
        </bk-button>
      </div>
    </div>
    <div class="iam-instance-item">
      <p v-for="(item, index) in resourceList"
        :key="index"
        class="value" :title="`ID：${item.id}`">
        <span class="name">{{ item.display_name }}</span>
        <bk-checkbox
          v-if="canEdit"
          :true-value="true"
          :false-value="false"
          v-model="item.checked"
          @change="handleChange">
        </bk-checkbox>
      </p>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  export default {
    name: '',
    props: {
      hasGap: {
        type: Boolean,
        default: false
      },
      title: {
        type: String,
        default: ''
      },
      data: {
        type: Array,
        default: () => []
      },
      canEdit: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        resourceList: [],
        allChecked: false
      };
    },
    computed: {
      count () {
        return this.resourceList.filter(item => item.checked).length;
      },
      selectText () {
        if (this.resourceList.every(item => item.checked)) {
          return this.$t(`m.common['取消全选']`);
        }
        return this.$t(`m.common['全选']`);
      }
    },
    watch: {
      data: {
        handler (value) {
          if (value.length < 1) {
            this.resourceList = [];
            return;
          }

          const tempList = [];
          value.forEach(item => {
            const len = item.length;
            const displayName = item.map(sub => sub.name).join('/');
            tempList.push({
              name: item[len - 1].name,
              id: item[len - 1].id,
              level: len - 1,
              disabled: item.some(subItem => subItem.disabled),
              display_name: displayName,
              checked: false,
              list: item
            });
          });

          this.resourceList = _.cloneDeep(tempList);
        },
        immediate: true
      }
    },
    methods: {
      handleChange (value) {
        this.allChecked = this.resourceList.every(item => item.checked);
        this.trigger(value);
      },

      handleSelectAll () {
        this.allChecked = !this.allChecked;
        this.resourceList.forEach(item => {
          this.$set(item, 'checked', this.allChecked);
          // item.checked = this.allChecked
        });
        this.$emit('on-selelct-all', this.allChecked, this.resourceList.length);
        // this.trigger()
      },

      handleSetChecked (payload) {
        this.allChecked = payload;
        this.resourceList.forEach(item => {
          item.checked = payload;
        });
        // this.trigger()
      },

      handleGetValue () {
        return this.resourceList.filter(item => item.checked);
      },

      trigger (payload) {
        // const arr = this.resourceList.filter(item => item.checked)
        this.$emit('on-change', payload);
      }
    }
  };
</script>
<style lang="postcss" scoped>
    .iam-instance-content {
        position: relative;
        &.set-marging-top {
            margin-top: 15px;
        }
        .iam-instance-title {
            display: flex;
            justify-content: space-between;
            line-height: 26px;
            font-size: 12px;
            /* color: #63656e; */
        }
        .iam-instance-item {
            margin-top: 10px;
            padding: 13px 16px;
            max-height: 186px;
            overflow-y: auto;
            background: #f7f9fb;
            font-size: 12px;
            color: #63656e;
            .value {
                display: flex;
                justify-content: space-between;
                line-height: 24px;
                .name {
                    max-width: 400px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
            }
            &::-webkit-scrollbar {
                width: 4px;
                background-color: lighten(transparent, 80%);
            }
            &::-webkit-scrollbar-thumb {
                height: 5px;
                border-radius: 2px;
                background-color: #e6e9ea;
            }
        }
    }
</style>
