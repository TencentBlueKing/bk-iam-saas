<template>
  <div>
    <div class="attribute-item"
      v-for="(item, index) in attrValues"
      :key="index"
      :class="index !== 0 ? 'set-margin-top' : ''">
      <div class="attribute-select">
        <bk-select
          v-model="item.id"
          :clearable="false"
          :disabled="item.disabled || isDisabledMode"
          searchable
          style="width: 130px;"
          @selected="handleAttributeSelected(...arguments, item)">
          <bk-option v-for="option in list"
            :key="option.id"
            :id="option.id"
            :name="option.display_name">
          </bk-option>
        </bk-select>
        <bk-select
          v-model="item.selecteds"
          :ref="`${item.id}&${index}&valueRef`"
          :multiple="true"
          searchable
          :disabled="item.disabled"
          :loading="item.loading"
          style="position: relative; left: -1px; width: 330px;"
          :remote-method="handleRemoteValue"
          @clear="handleClear(...arguments, item)"
          @toggle="handleAttrValueToggle(...arguments, index, item)"
          @selected="handleAttrValueSelected(...arguments, item)">
          <bk-option v-for="option in attrValueListMap[item.id]"
            :key="option.id"
            :id="option.id"
            :name="option.display_name">
            <template v-if="option.id !== ''">
              <span>{{ option.display_name }}</span>
            </template>
            <template v-else>
              <div v-bkloading="{ isLoading: true, size: 'mini' }"></div>
            </template>
          </bk-option>
        </bk-select>
      </div>
      <div class="attribute-action" v-if="isShowAction(item)">
        <Icon type="add-hollow" @click="addAttribute" />
        <Icon
          type="reduce-hollow"
          :class="attrValues.length === 1 ? 'disabled' : ''"
          style="margin-left: 3px;"
          @click="deleteAttribute(index)" />
      </div>
    </div>
  </div>
</template>
<script>
  import Attribute from '@/model/attribute';

  const ATTRIBUTE_ITEM = {
    id: '',
    name: '',
    values: []
  };

  const LOADING_ITEM = {
    id: '',
    display_name: ''
  };
    
  export default {
    name: '',
    props: {
      list: {
        type: Array,
        default: () => []
      },
      value: {
        type: Array,
        default: () => []
      },
      // 查询参数
      params: {
        type: Object,
        default: () => {
          return {};
        }
      },
      mode: {
        type: String,
        default: 'normal'
      },
      limitValue: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        attrValues: [],
        curOperateData: {},
        pagination: {
          limit: 10,
          current: 1,
          totalPage: 0
        },
        attrValueListMap: {},
        isDisabledMode: false
      };
    },
    computed: {
      // isDisabledMode () {
      //     return this.mode === 'disabled'
      // },
      isShowAction () {
        return payload => {
          if (this.isDisabledMode) {
            return false;
          }
          return !payload.disabled;
        };
      }
    },
    watch: {
      value: {
        handler (val) {
          if (val.length < 1) {
            this.attrValues = [new Attribute(ATTRIBUTE_ITEM)];
            return;
          }
          this.attrValues = val;
          const flag = Object.keys(this.attrValueListMap).length > 0;
          this.attrValues.forEach(async item => {
            if (!flag && item.id) {
              await this.fetchValue(item);
            }
          });
        },
        immediate: true
      },
      limitValue: {
        handler (val) {
          if (val.length > 0) {
            this.isDisabledMode = true;
            this.pagination.limit = 10000;
            let tempArr = [];
            val.map(item => {
              const tempList = item.values.map(v => {
                return {
                  id: v.id,
                  display_name: v.name
                };
              });
              this.$set(this.attrValueListMap, item.id, tempList);
            });
            if (this.value.length < 1) {
              this.attrValues = val.map(item => {
                const { id, name } = item;
                return new Attribute({ id, name, selecteds: [], values: [] });
              });
              tempArr = this.attrValues;
            } else {
              const differenceValue = val.filter(item => !this.value.map(v => v.id).includes(item.id));
              if (differenceValue.length > 0) {
                const tempValues = differenceValue.map(item => {
                  const { id, name } = item;
                  return new Attribute({ id, name, selecteds: [], values: [] });
                });
                tempArr = tempValues;
                this.attrValues.push(...tempValues);
              }
            }
            const flag = Object.keys(this.attrValueListMap).length > 0;
            tempArr.forEach(async item => {
              if (!flag && item.id) {
                await this.fetchValue(item);
              }
            });
          }
        },
        immediate: true
      },
      list: {
        handler (val) {
          if (val.length > 0) {
            val.forEach(item => {
              if (!this.attrValueListMap.hasOwnProperty(item.id)) {
                this.$set(this.attrValueListMap, item.id, []);
              }
            });
          }
        },
        immediate: true
      }
    },
    methods: {
      handleClear (value, payload) {
        payload.values = [];
        this.trigger();
      },
      handleAttrValueSelected (value, options, payload) {
        if (value.length < 1) {
          payload.values = [];
          this.trigger();
          return;
        }
        const tempValues = [];
        value.forEach((item, index) => {
          const attrData = options[index];
          tempValues.push({
            id: item,
            name: attrData.name
          });
        });
        payload.values = [...tempValues];
        this.trigger();
      },
            
      async fetchValue (item) {
        item.loading = true;
        try {
          const res = await this.$store.dispatch('permApply/getResourceAttrValues', {
                        ...this.params,
                        limit: this.pagination.limit,
                        offset: this.pagination.limit * (this.pagination.current - 1),
                        attribute: item.id,
                        keyword: ''
          });
          this.pagination.totalPage = Math.ceil(res.data.count / this.pagination.limit);
          if (this.pagination.totalPage > 1) {
            res.data.results.push(LOADING_ITEM);
          }
          const results = (() => {
            const limitItem = this.limitValue.find(v => v.id === item.id);
            if (this.isDisabledMode && limitItem) {
              return res.data.results.filter(v => limitItem.selecteds.includes(v.id));
            }
            return res.data.results;
          })();
          this.$set(this.attrValueListMap, item.id, results);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          item.loading = false;
        }
      },

      addAttribute () {
        this.attrValues.push(new Attribute(ATTRIBUTE_ITEM));
        this.trigger();
      },

      deleteAttribute (index) {
        if (this.attrValues.length === 1) {
          return;
        }
        this.attrValues.splice(index, 1);
        this.trigger();
      },

      handleAttributeSelected (newVal, option, payload) {
        payload.values = [];
        payload.selecteds = [];
        const curAttr = this.list.find(item => item.id === newVal);
        if (curAttr) {
          payload.name = curAttr.display_name || '';
        }
        if (this.attrValueListMap[payload.id] && this.attrValueListMap[payload.id].length < 1) {
          this.fetchResourceAttrValues(payload, '', true);
        }
      },

      handleAttrValueToggle (val, index, payload) {
        if (this.isDisabledMode) {
          return;
        }
        const curOptionDom = this.$refs[`${payload.id}&${index}&valueRef`][0].$refs.optionList;
        curOptionDom.addEventListener('scroll', this.handleScroll);
        if (val) {
          // 记录当前操作的属性值数据
          this.curOperateData = payload;
        } else {
          this.curOperateData = {};
          curOptionDom.removeEventListener('scroll', this.handleScroll);
        }
      },

      async handleScroll (event) {
        if (this.pagination.current > this.pagination.totalPage) {
          // 删除loading项
          this.attrValueListMap[this.curOperateData.id].shift();
          return;
        }
        if (event.target.scrollTop + event.target.offsetHeight >= event.target.scrollHeight) {
          ++this.pagination.current;
          if (this.pagination.current <= this.pagination.totalPage) {
            await this.fetchResourceAttrValues(this.curOperateData, '', false, true);
            event.target.scrollTo(0, event.target.scrollTop - 10);
          }
        }
      },

      async handleRemoteValue (val) {
        if (this.curOperateData.id) {
          this.pagination.current = 1;
          this.pagination.totalPage = 0;
          // 删除loading项
          this.attrValueListMap[this.curOperateData.id].shift();
          await this.fetchResourceAttrValues(this.curOperateData, val, false);
        }
      },

      async fetchResourceAttrValues (payload, keyword = '', isLoading = true, isScrollRemote = false) {
        payload.loading = isLoading && !isScrollRemote;
        const { limit, current } = this.pagination;
        try {
          const res = await this.$store.dispatch('permApply/getResourceAttrValues', {
                        ...this.params,
                        limit: limit,
                        offset: limit * (current - 1),
                        attribute: payload.id,
                        keyword
          });
          if (isScrollRemote) {
            const len = this.attrValueListMap[payload.id].length;
            this.attrValueListMap[payload.id].splice(len - 2, 0, ...res.data.results);
          } else {
            this.pagination.totalPage = Math.ceil(res.data.count / this.pagination.limit);
            if (this.pagination.totalPage > 1) {
              res.data.results.push(LOADING_ITEM);
            }
            this.attrValueListMap[payload.id] = [...res.data.results];
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          payload.loading = false;
        }
      },

      trigger () {
        this.$emit('on-change', this.attrValues);
      }
    }
  };
</script>
<style lang="postcss">
    .attribute-item {
        display: flex;
        &.set-margin-top {
            margin-top: 8px;
        }
    }
    .attribute-select {
        display: flex;
    }
    .attribute-action {
        margin-left: 12px;
        line-height: 32px;
        i {
            color: #979ba5;
            font-size: 20px;
            cursor: pointer;
            &.disabled {
                color: #c4c6cc;
                cursor: not-allowed;
            }
        }
    }
</style>
