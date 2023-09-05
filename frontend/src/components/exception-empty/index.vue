
<script>
  import il8n from '@/language';
  export default {
    name: 'ExceptionEmpty',
    props: {
      type: {
        type: [String, Number],
        default: 'empty'
      },
      scene: {
        type: String,
        default: 'part'
      },
      emptyText: {
        type: String,
        default: '暂无数据'
      },
      tipType: {
        type: String,
        default: ''
      },
      errorMessage: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        searchTipWidth: 200
      };
    },
    methods: {
      searchTipStyles () {
        this.$nextTick(() => {
          if (this.$parent.tableId) {
            this.searchTipWidth = !['zh-cn'].includes(window.CUR_LANGUAGE) ? 400 : 230;
          }
        });
        return {
          'width': `${this.searchTipWidth}px`
        };
      },
      fetchDefaultOperation (type) {
        const defaultOperation = {
          search: () => {
            return (
              <div
                  class="tip-wrap exception-search-tip"
                  // style={ this.searchTipStyles() }
              >
                  <span class="text-btn">{this.$t(`m.common['可以尝试']`)}</span>
                  <span> {this.$t(`m.common['调整关键词']`)}</span>
                  <span> {this.$t(`m.common['或']`)} </span>
                  <span class="tip-click" onClick={() => this.handleClear()}>
                      {this.$t(`m.common['清空筛选条件']`)}
                  </span>
              </div>
            );
          },
          refresh: () => {
            return (
              <div class="tip-wrap">
                  <div class="tip-click" onClick={() => this.handleRefresh()}>
                      {this.$t(`m.common['刷新']`)}
                  </div>
              </div>
            );
          },
          noPerm: () => {
            return (
                <div class="tip-wrap">
                    <div class="tip-message">
                        {this.errorMessage}
                    </div>
                </div>
            );
          }
        };
        return type && defaultOperation[type] ? defaultOperation[type]() : '';
      },
      handleClear () {
        this.$emit('on-clear', {});
      },
      handleRefresh () {
        this.$emit('on-refresh', {});
      }
    },
    render () {
      const props = {
        ...this.$attrs
      };
      const on = {
        ...this.$listeners
      };
      return (
        <div>
            <bk-exception
                ext-cls={!this.type ? 'exception-wrap exception-no-wrap' : 'exception-wrap'}
                type={this.type || 'empty'}
                scene={this.scene}
                { ...{ props }}
                { ...{ on }}
                
            >
                <span>{ il8n('common', this.emptyText) }</span>
                {this.fetchDefaultOperation(this.tipType)}
            </bk-exception>
        </div>
      );
    }
  };
</script>

<style lang="postcss" scoped>
.exception-wrap {
  /* width: auto !important; */
  margin-top: 0;
  &.exception-gray {
    background-color: #f5f6fa;
  }
  .tip-click {
    color: #3a84ff;
    cursor: pointer;
  }
  .tip-message {
    color: #979ba5;
    font-size: 12px;
  }
  .tip-wrap {
    margin-top: 10px;
  }
  .exception-search-tip {
    font-size: 12px;
    color: #999;
  }
}
/deep/ .bk-exception {
    width: 100%;
    &-img {
      width: 180px !important;
      .exception-image {
        width: 100% !important;
        height: 100% !important;
      }
    }
    .page-text {
      font-size: 16px;
    }
    .page-img {
      width: 400px !important;
      margin-top: 150px;
      height: 100%;
    }
}

/deep/ .exception-no-wrap {
    .bk-exception-img {
      width: 0 !important;
    }
    .bk-exception-text {
      display: none;
    }
}
</style>
