<template>
  <div class="iam-system-access-wrapper">
    <render-search>
      <bk-button theme="primary" @click="goCreate">{{ $t(`m.common['新增']`) }}</bk-button>
      <div slot="right" class="right">
        <bk-button theme="primary" class="right" text @click="showHelpDialog">
          {{ $t(`m.access['接入帮助']`) }}
        </bk-button>
      </div>
    </render-search>
    <bk-table
      :data="tableList"
      size="small"
      :class="{ 'set-border': tableLoading }"
      ext-cls="system-access-table"
      :pagination="pagination"
      @page-change="handlePageChange"
      @page-limit-change="handleLimitChange"
      @select="handlerChange"
      @select-all="handlerAllChange"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }">
      <!-- <bk-table-column type="selection" align="center"></bk-table-column> -->
      <bk-table-column :label="$t(`m.access['系统名称']`)" :min-width="220">
        <template slot-scope="{ row }">
          <span class="system-access-name" :title="row.system.name" @click="goDetail(row)">
            {{ row.system.name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.access['系统ID']`)">
        <template slot-scope="{ row }">
          <span :title="row.system.id">{{ row.system.id }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.access['创建者']`)">
        <template slot-scope="{ row }">
          <span :title="row.owner">{{ row.owner }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['创建时间']`)" width="240" :sortable="true" sort-by="created_time">
        <template slot-scope="{ row }">
          <span :title="row.created_time">{{ row.created_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.access['更新时间']`)" :sortable="true" sort-by="updated_time" width="240">
        <template slot-scope="{ row }">
          <span :title="row.updated_time">{{ row.updated_time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.common['操作']`)" width="270">
        <template slot-scope="{ row }">
          <section>
            <bk-button theme="primary" text @click="goDetail(row)">
              {{ $t(`m.common['编辑']`) }}
            </bk-button>
            <!-- <bk-button
                            theme="primary"
                            text
                            v-if="row.subject_count < 1"
                            @click="handleTemplateDelete(row)">
                            {{ $t(`m.access['查看']`) }}
                        </bk-button>
                        <bk-button
                            theme="primary"
                            text
                            v-if="row.subject_count < 1"
                            @click="handleTemplateDelete(row)">
                            {{ $t(`m.access['访问']`) }}
                        </bk-button>
                        <bk-button
                            theme="primary"
                            disabled
                            text
                            v-else>
                            <span v-bk-tooltips.bottom="$t(`m.access['有关联的组时不能删除']`)">
                                {{ $t(`m.common['删除']`) }}
                            </span>
                        </bk-button> -->
          </section>
        </template>
      </bk-table-column>
      <template slot="empty">
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :tip-text="emptyData.tip"
          :tip-type="emptyData.tipType"
          @on-refresh="handleEmptyRefresh"
        />
      </template>
    </bk-table>
    <bk-dialog
      v-model="helpDialog"
      :show-footer="noFooter"
      :title="$t(`m.access['接入帮助']`)"
      width="1000"
      header-position="left"
      ext-cls="showHelp">
      <div class="help-main">
        <div class="help-info">
          <div class="info-right ml20">
            <p class="info-title">{{$t(`m.nav['系统接入']`)}}</p>
            <p class="info">{{$t(`m.access['蓝鲸权限中心提供了体验DEMO、接入文档、多语言SDK、接入视频，帮助开发者更快地实现权限接入。']`)}}</p>
            <bk-button theme="primary" @click="goCreate">{{$t(`m.access['去接入']`)}}</bk-button>
          </div>
        </div>
        <div class="help-list">
          <div v-for="item in helpList" :key="item.name">
            <div>{{item.name}}</div>
            <p class="pt10" v-for="e in item.urlInfo" :key="e.text">
              <bk-link theme="primary" :href="e.url" target="_blank">
                {{$t(`m.access['${e.text}']`) }}
              </bk-link>
            </p>
          </div>
        </div>
      </div>
    </bk-dialog>
  </div>
</template>
<script>
  import { buildURLParams } from '@/common/url';
  import { formatCodeData } from '@/common/util';

  export default {
    name: 'system-access-index',
    data () {
      return {
        tableList: [],
        tableLoading: false,
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        currentSelectList: [],
        helpDialog: false,
        noFooter: false,
        helpList: [
          {
            name: this.$t(`m.access['接入前准备']`),
            urlInfo: [
              {
                'text': '什么是蓝鲸权限中心', url: 'https://bk.tencent.com/docs/document/6.0/131/7337'
              },
              {
                'text': '工作原理', url: 'https://bk.tencent.com/docs/document/6.0/131/8381'
              },
              {
                'text': '了解概念', url: 'https://bk.tencent.com/docs/document/6.0/131/7343'
              }
            ]
          },
          {
            name: this.$t(`m.access['接入教程']`),
            urlInfo: [
              {
                'text': '开发接入文档', url: 'https://bk.tencent.com/docs/document/6.0/160/8391'
              },
              {
                'text': '开发接入实战视频', url: 'https://bkvideos-1252002024.cos.ap-guangzhou.myqcloud.com/bkiam/quanxianzhognxinkaifajierushizhan.MP4'
              }
            ]
          },
          // {
          //     name: 'DEMO',
          //     urlInfo: [
          //         {
          //             'text': '立即体验', url: 'http://www.qq.com'
          //         },
          //         {
          //             'text': '源码下载', url: 'http://www.qq.com'
          //         }
          //     ]
          // },
          {
            name: this.$t(`m.access['鉴权SDK']`),
            urlInfo: [
              {
                'text': 'Python', url: 'https://github.com/TencentBlueKing/iam-python-sdk'
              },
              {
                'text': 'Go', url: 'https://github.com/TencentBlueKing/iam-go-sdk'
              },
              {
                'text': 'PHP', url: 'https://github.com/TencentBlueKing/iam-php-sdk'
              },
              {
                'text': this.$t(`m.common['更多']`), url: 'https://bk.tencent.com/docs/document/6.0/160/8470'
              }
            ]
          }
        ],
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    created () {
      const currentQueryCache = this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        if (currentQueryCache.limit) {
          this.pagination.limit = currentQueryCache.limit;
          this.pagination.current = currentQueryCache.current;
        }
      }
    },
    methods: {
      async fetchPageData () {
        await this.fetchModelingList();
      },

      handleOpenMoreLink () {
        window.open(`${window.PRODUCT_DOC_URL_PREFIX}/权限中心/产品白皮书/场景案例/GradingManager.md`);
      },

      refreshCurrentQuery () {
        const { limit, current } = this.pagination;
        const queryParams = { limit, current };
        window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        return queryParams;
      },

      setCurrentQueryCache (payload) {
        window.localStorage.setItem('templateList', JSON.stringify(payload));
      },

      getCurrentQueryCache () {
        return JSON.parse(window.localStorage.getItem('templateList'));
      },

      resetPagination () {
        this.pagination = Object.assign({}, {
          limit: 10,
          current: 1,
          count: 0
        });
      },

      async fetchModelingList (isLoading = false) {
        this.tableLoading = isLoading;
        this.setCurrentQueryCache(this.refreshCurrentQuery());
        const params = {
          limit: this.pagination.limit,
          offset: this.pagination.limit * (this.pagination.current - 1)
        };
        try {
          const { code, data } = await this.$store.dispatch('access/getModelingList', params);
          this.pagination.count = data.count;
          data.results = data.results.length && data.results.sort(
            (a, b) => new Date(b.updated_time) - new Date(a.updated_time));
                        
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      goDetail (payload) {
        this.$router.push({
          name: 'systemAccessAccess',
          params: {
            id: payload.id
          }
        });
      },

      goCreate () {
        this.$router.push({
          name: 'systemAccessCreate'
        });
      },

      handlePageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.fetchModelingList(true);
      },

      handleLimitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.fetchModelingList(true);
      },

      handlerAllChange (selection) {
        this.currentSelectList = [...selection];
      },

      handlerChange (selection, row) {
        this.currentSelectList = [...selection];
      },

      showHelpDialog () {
        this.helpDialog = true;
      },

      handleEmptyRefresh () {
        this.currentSelectList = [];
        this.resetPagination();
        this.fetchModelingList(true);
      }
    }
  };
</script>
<style lang="postcss">
    .iam-system-access-wrapper {
        .right {
            height: 32px;
            line-height: 32px;
        }
        .detail-link {
            color: #3a84ff;
            cursor: pointer;
            &:hover {
                color: #699df4;
            }
            font-size: 12px;
        }
        .system-access-table {
            margin-top: 16px;
            border-right: none;
            border-bottom: none;
            &.set-border {
                border-right: 1px solid #dfe0e5;
                border-bottom: 1px solid #dfe0e5;
            }
            .system-access-name {
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
            }
            .lock-status {
                font-size: 12px;
                color: #fe9c00;
            }
        }
    }
    .showHelp {
        .help-main{
            .help-info{
                display: flex;
                justify-content: space-between;
                padding-bottom: 28px;
                border-bottom: 1px solid #DCDEE5;
                .info-title{
                    color: #313238;
                    font-size: 18px;
                    font-weight: 700;
                }
                .info{
                    padding: 17px 0 40px 0;
                }
            }
            .help-list{
                padding-top: 28px;
                display: flex;
                justify-content: space-between;
                width: 70%;
            }
        }
    }
</style>
