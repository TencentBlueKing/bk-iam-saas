<template>
  <bk-search-select
    class="iam-search-select"
    ref="searchSelect"
    v-bind="$attrs"
    v-on="$listeners"
    :placeholder="placeholder"
    :data="data"
    :show-condition="false"
    :popover-zindex="9999"
    :values="searchValue"
    @change="handleChange"
    @input="handleInput"
    @on-click-menu="handleClickMenu"
    @on-tag-delete="handleTagDelete"
  />
</template>
<script>
  import _ from 'lodash';
  import bkSearchSelect from './search-select';
  import il8n from '@/language';

  const filterValue = (payload, quickSearch) => {
    // 过滤空值，保证每项只会筛选一次
    const result = _.cloneDeep(payload);
    const valueMap = {};
    const resultIdSet = new Set();
    for (let i = 0; i < result.length; i++) {
      let value = result[i];
      // 数据为空，通过输入框直接搜索
      if (!value.values && typeof quickSearch === 'function') {
        value = quickSearch(value);
      }
      if (!value) {
        continue;
      }
      if (resultIdSet.has(value.id)) {
        // 删除旧的值，同一个ID再次被添加时保持添加顺序
        resultIdSet.delete(value.id);
      }
      resultIdSet.add(value.id);
      valueMap[value.id] = value;
    }
    return [...resultIdSet].map(key => Object.freeze(valueMap[key]));
  };

  export default {
    name: 'iam-search-select',
    components: {
      bkSearchSelect
    },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      placeholder: {
        type: String,
        default: il8n('verify', '请输入')
      },
      value: {
        type: Array,
        default: () => []
      },
      parseUrl: {
        type: Boolean,
        default: false
      },
      // 外部设置的筛选值添加到已有筛选值后面
      appendValue: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        searchValue: []
      };
    },
    watch: {
      value: {
        handler (val) {
          let oldSearchComponentValue = [];
          if (this.$refs.searchSelect) {
            // eslint-disable-next-line max-len
            oldSearchComponentValue = (this.$refs.searchSelect.chip && this.$refs.searchSelect.chip.list) || [];
          }
          const list = val.hasOwnProperty('length') ? val : [];
          this.searchValue = filterValue([...oldSearchComponentValue, ...list]);
        },
        immediate: true
      },
      appendValue: {
        handler (appendValue) {
          if (!this.$refs.searchSelect) {
            return;
          }
          const appendMap = appendValue.reduce((result, item) => {
            result[item.id] = true;
            return result;
          }, {});
          const value = [];
          for (let i = 0; i < this.$refs.searchSelect.chip.list.length; i++) {
            const currentValue = this.$refs.searchSelect.chip.list[i];
            if (!appendMap[currentValue.id]) {
              value.push(currentValue);
            }
          }

          this.searchValue = Object.freeze([...value, ...appendValue]);
        },
        immediate: true
      }
    },
    created () {
      if (this.parseUrl) {
        this.parseURLData();
      }
    },
    methods: {
      parseURLData  () {
        this.URLQuery = this.$route.query;

        const defaultSearchComponentValue = [];
        // 默认筛选数据
        const defaultSearchValue = {};
        const promiseStack = [];

        for (let i = 0; i < this.data.length; i++) {
          const currentData = this.data[i];

          // 只解析存在于搜索配置中的字段
          if (!this.URLQuery.hasOwnProperty(currentData.id)) {
            continue;
          }
          // 解析url中筛选项的值
          const currentURLParamValue = this.URLQuery[currentData.id];
          if (currentData.multiable) {
            defaultSearchValue[currentData.id] = currentURLParamValue.split(',');
          } else {
            defaultSearchValue[currentData.id] = currentURLParamValue;
          }

          let remoteHandler = Promise.resolve();

          if (currentData.remote) {
            // 远程提供数据
            if (currentData.remoteTrigger === 'key') {
              // 通过key触发——获取整个备选列表
              remoteHandler = currentData.remote(currentURLParamValue);
            } else {
              // 通过value触发——使用value进行搜索（直接使用url中的值）
              remoteHandler = Promise.resolve(currentURLParamValue);
            }
          } else if (currentData.children) {
            remoteHandler = Promise.resolve(currentData.children);
          } else {
            remoteHandler = Promise.resolve(currentURLParamValue);
          }

          const { id, name } = currentData;
          const urlSearchValue = this.URLQuery[id];

          remoteHandler.then(data => {
            let currentSearchComponentValue = {};
            let searchValueArr = [];
            if (currentData.multiable) {
              searchValueArr = urlSearchValue.split(',');
            } else {
              searchValueArr = [urlSearchValue];
            }
            if (_.isArray(data)) {
              // 远程备选列表；本地备选列表
              const valueStack = [];
              searchValueArr.forEach(item => {
                // 兼容筛选值已经被删掉的场景
                const childItem = data.find(_ => `${_.id}` === `${item}`);
                if (childItem) {
                  valueStack.push({
                    id: childItem.id,
                    name: childItem.name
                  });
                }
              });

              if (valueStack.length < 1) {
                return;
              }

              currentSearchComponentValue = {
                id,
                name,
                values: valueStack
              };
            } else {
              // 本地直接输入
              const valueStack = [];
              searchValueArr.forEach(item => {
                // 兼容空值的情况
                if (item) {
                  valueStack.push({
                    id: item,
                    name: item
                  });
                }
              });
              if (valueStack.length < 1) {
                return;
              }
              currentSearchComponentValue = {
                id,
                name,
                values: valueStack
              };
            }
            defaultSearchComponentValue.push(currentSearchComponentValue);
          });
          promiseStack.push(remoteHandler);
        }
        Promise.all(promiseStack).finally(() => {
          let oldSearchComponentValue = [];
          if (this.$refs.searchSelect) {
            oldSearchComponentValue = this.$refs.searchSelect.chip.list;
          }
          this.searchValue = filterValue([...oldSearchComponentValue, ...defaultSearchComponentValue]);
          setTimeout(() => {
            this.$emit('on-change', defaultSearchValue);
            this.$emit('input', defaultSearchValue);
          });
        });
      },
      handleChange (payload) {
        const validValue = payload;
        const result = {};
        const defaultValueMap = val => val.id;
        for (let i = 0; i < validValue.length; i++) {
          const currentValue = validValue[i];
          const valueMap = typeof currentValue.map === 'function' ? currentValue.map : defaultValueMap;
          if (currentValue.multiable) {
            result[currentValue.id] = currentValue.values.map(item => valueMap(item));
          } else if (currentValue.values) {
            result[currentValue.id] = valueMap(currentValue.values[0]);
          } else {
            result[currentValue.id] = valueMap(currentValue);
          }
        }
        this.$emit('on-change', result, validValue);
        this.$emit('input', result, validValue);
      },

      handleInput (payload) {
        this.$emit('on-input', payload);
      },
      handleClickMenu (payload) {
        this.$emit('on-click-menu', payload);
        this.$emit('input', payload);
      }
    }
  };
</script>
<style lang="postcss">
    .iam-search-select{
        background: #fff;
    }
</style>
