<script>
  import _ from 'lodash';
  import Mixin from './mixin';

  export default {
    name: 'BKSearchKey',
    mixins: [Mixin],
    data () {
      return {
        condition: {},
        list: [],
        activeIndex: 0
      };
    },
        
    computed: {
      needRender () {
        // 没有选中key，且输入框中没有输入值
        const { menu, localValue } = this.searchSelect;
        if (!menu.id && !localValue) {
          return true;
        }
        return false;
      },
      isCondition () {
        const searchSelect = this.searchSelect;
        if (searchSelect.chipList.length < 1) {
          // 条件筛选不能作为第一项
          return false;
        }
        if (searchSelect.chipList[searchSelect.chipList.length - 1][searchSelect.primaryKey]
          !== searchSelect.defaultCondition[searchSelect.primaryKey]) {
          // 已选的最后一项是条件筛选，则下一次操作不展示
          return false;
        }
        return this.searchSelect.showCondition;
      }
    },
    created () {
      this.generatorList = _.debounce(this._generatorList, 100);
    },
    mounted () {
      document.body.addEventListener('keydown', this.handleKeydown);
    },
    beforeDestroy () {
      this.activeIndex = -1;
      document.body.removeEventListener('keydown', this.handleKeydown);
    },
    methods: {
      _generatorList () {
        const {
          primaryKey,
          data,
          chipList
        } = this.searchSelect;

        const selectKeyMap = chipList.reduce((result, item) => {
          result[item[primaryKey]] = true;
          return result;
        }, {});

        const stack = [];
        for (let i = 0; i < data.length; i++) {
          if (!selectKeyMap[data[i][primaryKey]]) {
            stack.push(data[i]);
          }
        }
        this.list = Object.freeze(stack);
      },
      handleKeydown (event) {
        if (!this.needRender) {
          return;
        }
        // 取消选中状态
        if (event.keyCode === 27) {
          this.activeIndex = -1;
          return;
        }
        // enter键直接触发选中
        if (event.keyCode === 13 && this.activeIndex > -1) {
          this.handleClick(this.list[this.activeIndex], this.activeIndex);
          return;
        }
        this.scrollActiveToView(event);
      },
            
      handleClick (item, index) {
        this.$emit('select', item, index);
      },
            
      handleCondition () {
        this.$emit('select-conditon', this.condition);
      }
    },
    render (h) {
      if (!this.needRender) {
        return null;
      }

      const {
        condition,
        displayKey
      } = this.searchSelect;

      const renderCondition = () => {
        if (!this.isCondition) {
          return '';
        }
        return (
                    <div class="iam-bk-search-list-condition" onClick={this.handleCondition}>
                        {condition[displayKey]}
                    </div>
        );
      };

      const renderList = () => {
        if (this.list.length < 1) {
          return (
                        <div class="iam-bk-search-list-loading">{ this.searchSelect.remoteEmptyText }</div>
          );
        }
        return (
                    <ul ref="list" class="iam-bk-search-list-menu">
                        { this.list.map((item, index) => {
                            return (
                                <li
                                    class={{
                                    'iam-bk-search-list-menu-item': true,
                                    'active': index === this.activeIndex
                                    }}>
                                    <div class="item-name" onClick={() => this.handleClick(item, index)}>
                                        <span>{ item[displayKey] }</span>
                                        {
                                            item.description ? <span class="item-description">({item.description})</span> : ''
                                        }
                                    </div>
                                </li>
                            );
                        }) }
                    </ul>
        );
      };

      return (
                <div class="iam-bk-search-list" role="key-menu" tabIndex="-1">
                    { renderCondition() }
                    { renderList() }
                </div>
      );
    }
  };
</script>
