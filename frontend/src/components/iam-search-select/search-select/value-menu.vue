<script>
  import _ from 'lodash';
  // import { debounce } from 'throttle-debounce'
  // import locale from 'bk-magic-vue/lib/locale'
  import locale from './locale';
  import Mixin from './mixin';
  import { encodeRegexp } from './helper';

  export default {
    name: 'BKSearchValue',
    mixins: [Mixin],
    data () {
      return {
        activeIndex: -1, // 上下键选中项索引，多选时不支持上下键位操作
        list: [],
        search: '', // 输入框的键入的筛选值
        currentItem: {}, // 当前key
        menu: {},
        error: '',
        loading: false,
        checkeMap: {}, // 多选已选中的项
        cacheList: [],
        searchValue: ''
      };
    },
    computed: {
      // 是否弹出面板
      needRender () {
        const currentItem = this.currentItem;
        // 未选中key
        if (!currentItem.id) {
          return false;
        }
        // 已选中key
        // 有配置 conditions，并且没有选中 conditions
        if (currentItem.conditions
          && currentItem.conditions.length
          && !this.menu.condition[this.searchSelect.primaryKey]) {
          return true;
        }
        // 已选中key
        // 但没有配置children && remoteMethod
        if (!(currentItem.children && currentItem.children.length > 0)
          && typeof currentItem.remoteMethod !== 'function') {
          return false;
        }
        return true;
      },
      // 是否多选
      isMultiable () {
        const currentItem = this.currentItem;
        // 1，如果是条件筛选则只支持单选
        if (currentItem.conditions && currentItem.conditions.length) {
          return false;
        }
        // 2，非条件筛选根据用户配置
        return currentItem.multiable;
      },
      // 是否展示conditions
      isCondition () {
        // 1，有配置conditions
        // 2，未选择conditions
        const currentItem = this.currentItem;
        return currentItem.conditions && currentItem.conditions.length > 0;
      }
    },
    watch: {
      // 处理默认选中、筛选选中状态
      list (list) {
        this.activeIndex = -1;
        if (this.isMultiable) {
          // 多选
                        
          // 没有过滤项默认不选中——不做选中处理
          if (!this.search) {
            return;
          }
          const {
            primaryKey,
            displayKey
          } = this.searchSelect;
          const checked = {};
          const searchKeys = this.search.split(/[｜|]/);
          for (let i = 0; i < searchKeys.length; i++) {
            const currentKey = searchKeys[i];
            // 过滤空值
            if (!currentKey.replace(/[ {2}\n]/, '')) {
              continue;
            }
            const realSearch = currentKey.trim();
            // 忽律大小写精确匹配
            const regx = new RegExp(`^${encodeRegexp(realSearch)}$`, 'i');
            for (let i = 0; i < list.length; i++) {
              const currentValue = list[i];
              if (regx.test(currentValue[displayKey])) {
                checked[currentValue[primaryKey]] = currentValue;
              }
            }
          }
          this.checkeMap = Object.freeze(checked);
        } else {
          // 单选

          // 没有过滤项——默认选中第一个
          if (!this.search) {
            this.activeIndex = 0;
            return;
          }
          // 默认选中模糊匹配的第一个
          const regx = new RegExp(encodeRegexp(this.search), 'i');
          for (let i = 0; i < list.length; i++) {
            if (regx.test(list[i][this.searchSelect.displayKey])) {
              this.activeIndex = i;
              return;
            }
          }
        }
      }
    },
    created () {
      setTimeout(() => {
        const checkMap = this.menu.checked.reduce((result, item) => {
          result[item.id] = item;
          return result;
        }, {});
        this.checkeMap = Object.freeze(checkMap);
      });
      this.generatorList = _.debounce(this._generatorList, 200);
    },
    mounted () {
      document.body.addEventListener('keydown', this.handleKeydown);
    },
    beforeDestroy () {
      document.body.removeEventListener('keydown', this.handleKeydown);
    },
    methods: {
      async _generatorList () {
        const currentItem = this.currentItem;
        this.error = false;

        if (!this.needRender) {
          return;
        }

        // 本地配置condition
        // 没有选择condition 优先选择condition
        if (this.isCondition && !this.menu.condition[this.searchSelect.primaryKey]) {
          this.loading = false;
          this.list = Object.freeze([...currentItem.conditions]);
          this.cacheList = _.cloneDeep(this.list);
          return;
        }

        // 本地配置children
        if (currentItem.children && currentItem.children.length > 0) {
          this.loading = false;
          this.list = Object.freeze([...currentItem.children]);
          return;
        }

        // 远程获取value列表
        let remoteMethod = '';
        if (typeof currentItem.remoteMethod === 'function') {
          const {
            _remoteKeyImmediateChildrenMap,
            primaryKey
          } = this.searchSelect;
          // remoteMethod 是立即执行的——从缓存中取值
          const children = _remoteKeyImmediateChildrenMap[currentItem[primaryKey]];
          if (children) {
            this.list = Object.freeze([...children]);
            return;
          }
          remoteMethod = currentItem.remoteMethod;
        }
        if (remoteMethod) {
          this.loading = true;
          try {
            const list = await remoteMethod(this.search, currentItem, 0);
            this.list = Object.freeze([...list]);
            this.cacheList = _.cloneDeep(this.list);
          } catch {
            this.error = true;
          } finally {
            this.loading = false;
          }
        }
      },
            
      handleClick (item) {
        // 禁用
        if (item.disabled) {
          return false;
        }
        // 条件筛选
        if (this.isCondition && Object.keys(this.menu.condition).length < 1) {
          this.$emit('select-condition', item);
          return;
        }
        const primaryKey = this.searchSelect.primaryKey;
                
        // 多选
        if (this.isMultiable) {
          const checkeMap = { ...this.checkeMap };
          const key = item[primaryKey];
          if (checkeMap[key]) {
            delete checkeMap[key];
          } else {
            checkeMap[key] = item;
          }
          this.checkeMap = Object.freeze(checkeMap);
          this.$emit('select-check', Object.values(this.checkeMap));
        } else {
          // 单选
          const checkeMap = {
            [item[primaryKey]]: item
          };
          this.checkeMap = Object.freeze(checkeMap);
          this.handleSubmit();
        }
      },
            
      handleKeydown (e) {
        if (!this.needRender) {
          return;
        }
        // 多选不支持上下移动选中
        if (this.isMultiable || this.list.length < 1) {
          return;
        }
        // enter键直接触发选中
        if (event.keyCode === 13) {
          if (this.activeIndex < 0) {
            return;
          }
          this.handleClick(this.list[this.activeIndex], this.activeIndex);
          return;
        }
        this.scrollActiveToView(event);
      },
            
      handleSubmit (e) {
        this.$emit('select-check', Object.values(this.checkeMap));
                
        this.$emit('change');
      },
            
      handleCancel () {
        this.$emit('cancel');
      },

      handleInput (value) {
        this.list = this.cacheList.filter(item => `${item.name}(${item.id})`.toLowerCase().indexOf(value) > -1);
      },

      renderContent () {
        // 显示错误
        if (this.error) {
          return (
                        <div class="iam-bk-search-list-error">{ this.error }</div>
          );
        }
        // 显示loading
        if (this.loading) {
          return (
                        <div class="iam-bk-search-list-loading">{ this.searchSelect.remoteLoadingText }</div>
          );
        }
        // 列表为空
        if (this.needRender && !this.list.length && !['action_id'].includes(this.currentItem.id)) {
          return (
                        <div class="iam-bk-search-list-loading">{ this.searchSelect.remoteEmptyText }</div>
          );
        }

        const renderList = () => {
          const displayKey = this.searchSelect.displayKey;
          const primaryKey = this.searchSelect.primaryKey;
          if (['action_id'].includes(this.currentItem.id)) {
            return (
                        <div style="width: 240px;">
                            <div style="padding: 0 10px; margin-bottom: 10px;">
                                <bk-input
                                        clearable={true}
                                        right-icon="bk-icon icon-search"
                                        value={this.searchValue}
                                        onInput={($event) => this.handleInput($event)}
                                    />
                            </div>
                            <ul ref="list" class="iam-bk-search-list-menu">
                                {
                                    this.list.length
                                    ? this.list.map((item, index) => {
                                        const id = item[primaryKey];
                                        return (
                                            <li class={{
                                                'iam-bk-search-list-menu-item': true,
                                                'is-group': !!item.isGroup,
                                                'is-disabled': item.disabled,
                                                'active': this.activeIndex === index
                                                }}>
                                                <div
                                                    class="item-name"
                                                    onClick={e => this.handleClick(item, index, id)}>
                                                    { item[displayKey] }({item[primaryKey]})
                                                </div>
                                                { this.isMultiable && !!this.checkeMap[item.id]
                                                    ? <i class="bk-icon icon-check-1 item-icon" />
                                                    : '' }
                                            </li>
                                        );
                                })
                                : (<div class="iam-bk-search-list-loading">{ this.searchSelect.remoteEmptyText }</div>)
                            }
                            </ul>
                        </div>
            );
          } else {
            return (
                        <div>
                            <ul ref="list" class="iam-bk-search-list-menu">
                                { this.list.map((item, index) => {
                                    const id = item[primaryKey];
                                    
                                    return (
                                        <li class={{
                                            'iam-bk-search-list-menu-item': true,
                                            'is-group': !!item.isGroup,
                                            'is-disabled': item.disabled,
                                            'active': this.activeIndex === index
                                            }}>
                                            <div
                                                class="item-name"
                                                onClick={e => this.handleClick(item, index, id)}>
                                                { item[displayKey] }
                                            </div>
                                            { this.isMultiable && !!this.checkeMap[item.id]
                                                ? <i class="bk-icon icon-check-1 item-icon" />
                                                : '' }
                                        </li>
                                    );
                                }) }
                            </ul>
                            
                        </div>
            );
          }
        };

        const renderFooter = () => {
          // 多选的时候显示底部操作按钮
          if (!this.isMultiable) {
            return '';
          }

          const submitBtnClasses = {
            'footer-btn': true,
            disabled: Object.keys(this.checkeMap).length < 1
          };
          return (
                        <div class="iam-bk-search-list-footer">
                            <div class={submitBtnClasses} onClick={this.handleSubmit}>
                                {locale.t('bk.searchSelect.ok')}
                            </div>
                            <div class="footer-btn" onClick={this.handleCancel}>
                                {locale.t('bk.searchSelect.cancel')}
                            </div>
                        </div>
          );
        };
        return (
                    <div>
                        { renderList() }
                        { renderFooter() }
                    </div>
        );
      }
    },
        
    render (h) {
      if (!this.needRender) {
        return null;
      }
      return (
                <div class="iam-bk-search-list" tabIndex="-1" role="search-value">
                    { this.renderContent() }
                </div>
      );
    }
  };
</script>
