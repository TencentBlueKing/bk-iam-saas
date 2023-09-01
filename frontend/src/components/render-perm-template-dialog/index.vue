<template>
  <!-- eslint-disable max-len -->
  <bk-dialog
    v-model="isShowDialog"
    width="700"
    title=""
    :mask-close="false"
    draggable
    header-position="left"
    ext-cls="iam-select-perm-template-dialog"
    @after-leave="handleAfterEditLeave">
    <div slot="header" class="title">
      <a class="target" href="" target="_blank" style="display: none;"></a>
      <template v-if="showExpiredAt">
        <div v-if="isPrev">
          {{ $t(`m.common['添加权限至']`) }}{{ $t(`m.common['【']`) }}<span class="member-title" :title="name">{{ name }}</span>{{ $t(`m.common['】']`) }}
        </div>
        <div v-else :title="`设置${$t(`m.common['【']`)}${name}${$t(`m.common['】']`)}${$t(`m.common['组织继承新权限的有效期']`)}`">
          {{ $t(`m.common['设置']`) }}<span class="expired-at-title" :title="name">{{ $t(`m.common['【']`) }}{{ name }}</span>{{ $t(`m.common['】']`) }}{{ $t(`m.common['组织继承新权限的有效期']`) }}
        </div>
      </template>
      <template v-else>
        <template v-if="name === ''">
          {{ $t(`m.permApply['选择权限模板']`) }}
        </template>
        <template v-else>
          {{ $t(`m.common['添加权限至']`) }}{{ $t(`m.common['【']`) }}<span class="member-title" :title="name">{{ name }}</span>{{ $t(`m.common['】']`) }}
        </template>
      </template>
    </div>
    <div class="perm-template-content-wrapper" :style="style">
      <div class="perm-template-search-wrapper" v-if="isPrev">
        <div class="left">
          <iam-search-select
            ref="searchTemplateRef"
            :data="searchData"
            :popover-zindex="2999"
            :quick-search-method="quickSearchMethod"
            style="width: 420px;"
            @on-change="handleSearch" />
        </div>
        <div class="right">
          <bk-button
            text
            theme="primary"
            size="small"
            style="position: absolute; top: 5px; right: 130px;"
            @click="handleToCreate">
            {{ $t(`m.common['去创建权限模板']`) }}
          </bk-button>
          <template v-if="curLanguageIsCn">
            {{ $t(`m.common['已选择']`) }}
            <span class="count">{{ hasChekedList.length }}</span>
            {{ $t(`m.common['个']`) }}
            {{ $t(`m.myApply['权限模板']`) }}
          </template>
          <template v-else>
            <span class="count">{{ hasChekedList.length }}</span>
            {{ $t(`m.common['已选择']`) }}
          </template>
        </div>
      </div>
      <div class="perm-template-content" v-if="isPrev">
        <table
          class="bk-table perm-template-fixed-table">
          <colgroup>
            <col style="width: 200px;" />
            <col style="width: 200px;" />
            <col />
          </colgroup>
          <thead>
            <tr>
              <th style="padding-left: 20px;">
                {{ $t(`m.common['模板名称']`) }}
              </th><th>{{ $t(`m.common['所属系统']`) }}</th>
              <th>
                {{ $t(`m.common['描述']`) }}
                <span class="refresh" @click.stop="handleRefresh">{{ $t(`m.common['刷新']`) }}</span>
              </th>
            </tr>
          </thead>
        </table>
        <div :class="['perm-template-table',
                      { 'can-not-scroll': isLoading || tableLoading || isEmpty },
                      { 'no-bottom-border': isNoBottomBorder },
                      { 'has-bottom-border': isHasBottomBorder },
                      { 'no-top-border': isEmpty },
                      { 'is-be-loading': isLoading || tableLoading }]"
          ref="permTemplateRef"
          v-bkloading="{ isLoading: isLoading || tableLoading, opacity: 1 }"
          @scroll.stop="handleScroll($event)">
          <table
            class="bk-table has-table-hover">
            <colgroup>
              <col style="width: 200px;" />
              <col style="width: 200px;" />
              <col />
            </colgroup>
            <tbody style="background: #fff;">
              <template v-if="!isEmpty && !isLoading && !tableLoading">
                <tr v-for="(item, index) in permTemplateList"
                  :key="index"
                  :style="{ cursor: item.disabled ? 'not-allowed' : 'pointer' }"
                  @click.stop="handleChecked(item)">
                  <td style="text-align: left; padding-left: 20px;">
                    <div class="node-checkbox-wrapper">
                      <span class="node-checkbox"
                        :class="{
                          'is-disabled': item.disabled,
                          'is-checked': item.checked,
                          'is-indeterminate': item.indeterminate
                        }">
                      </span>
                    </div>
                    <span class="name" :title="item.disabled ? $t(`m.common['该模板已添加']`) : item.name">{{ item.name }}</span>
                  </td>
                  <td>
                    <span class="system-name" :title="item.system.name">{{ item.system.name }}</span>
                  </td>
                  <td>
                    <span class="desc" :title="item.description ? item.description : ''">{{ item.description || '--' }}</span>
                  </td>
                </tr>
                <tr class="loading-tr" v-if="isScrollLoading">
                  <td colspan="3">
                    <div class="loading-row" v-bkloading="{ isLoading: true }"></div>
                  </td>
                </tr>
                <tr class="no-more-data-tr" v-show="isShowNoDataText">
                  <td colspan="3">
                    <div>{{ $t(`m.common['没有更多内容了']`) }}</div>
                  </td>
                </tr>
              </template>
              <template v-if="isEmpty && !isLoading">
                <tr>
                  <td colspan="3">
                    <div class="search-empty-wrapper">
                      <div class="empty-wrapper">
                        <!-- <iam-svg />
                                                <p class="empty-tips">{{ isSearch ? $t(`m.common['搜索无结果']`) : $t(`m.common['暂无数据']`) }}</p> -->
                        <ExceptionEmpty
                          :type="emptyData.type"
                          :empty-text="emptyData.text"
                          :tip-text="emptyData.tip"
                          :tip-type="emptyData.tipType"
                          @on-clear="handleEmptyClear"
                          @on-refresh="handleEmptyRefresh"
                        />
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
      <template v-if="!isPrev">
        <div style="margin-top: 25px;">
          <iam-deadline :value="expiredAt" type="dialog" @on-change="handleDeadlineChange" />
        </div>
      </template>
    </div>
    <template slot="footer">
      <template v-if="showExpiredAt">
        <template v-if="isPrev">
          <bk-button theme="primary" :disabled="isDisabled" @click="handleNextStep">{{ $t(`m.common['下一步']`) }}</bk-button>
        </template>
        <template v-else>
          <bk-button @click="handlePrevStep">{{ $t(`m.common['上一步']`) }}</bk-button>
          <bk-button style="margin-left: 10px;" theme="primary" :disabled="disabled" :loading="loading" @click="handleSumbit">{{ $t(`m.common['确定']`) }}</bk-button>
        </template>
      </template>
      <template v-else>
        <bk-button theme="primary" :disabled="isDisabled" :loading="loading" @click="handleSumbit">{{ $t(`m.common['确定']`) }}</bk-button>
      </template>
      <bk-button style="margin-left: 10px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
    </template>
  </bk-dialog>
</template>
<script>
  import IamDeadline from '@/components/iam-deadline/horizontal';
  import IamSearchSelect from '@/components/iam-search-select';
  import { fuzzyRtxSearch } from '@/common/rtx';
  import { formatCodeData } from '@/common/util';
  import { mapGetters } from 'vuex';

  export default {
    name: '',
    components: {
      IamDeadline,
      IamSearchSelect
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      value: {
        type: Array,
        default: () => []
      },
      loading: {
        type: Boolean,
        default: false
      },
      groupId: {
        type: [String, Number],
        default: ''
      },
      name: {
        type: String,
        default: ''
      },
      defaultValue: {
        type: Array,
        default: () => []
      },
      showExpiredAt: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isShowDialog: false,
        isScrollLoading: false,
        isScrollBottom: false,
        systemList: [],
        permTemplateList: [],
        hasChekedList: [],
        allCheked: false,
        indeterminate: false,
        pagination: {
          totalPage: 1,
          limit: 7,
          current: 1
        },
        searchValue: {},
        requestQueue: ['templateList'],
        defaultTemplateIds: [],
        tableLoading: false,

        isPrev: true,
        expiredAt: 15552000,
        isSearch: false,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
            ...mapGetters(['externalSystemId']),
            isLoading () {
                return this.requestQueue.length > 0 && this.isShowDialog;
            },
            disabled () {
                return this.expiredAt === 0;
            },
            allChekedDisabled () {
                return this.permTemplateList.length < 1 || this.isLoading;
            },
            isEmpty () {
                return this.permTemplateList.length < 1;
            },
            isNoBottomBorder () {
                return !this.isLoading && this.isScrollBottom;
            },
            isHasBottomBorder () {
                return this.permTemplateList.length >= this.pagination.limit && !this.isScrollBottom;
            },
            isShowNoDataText () {
                return this.pagination.current >= this.pagination.totalPage
                    && !this.isScrollLoading
                    && this.pagination.totalPage !== 1;
            },
            isDisabled () {
                return this.hasChekedList.length < 1;
            },
            style () {
                if (this.showExpiredAt) {
                    if (this.isPrev) {
                        return {
                            height: '360px'
                        };
                    }
                    return {
                        height: '35px'
                    };
                }
                return {
                    height: '360px'
                };
            }
    },
    watch: {
      show: {
        handler (value) {
          this.hasChekedList.splice(0, this.hasChekedList.length, ...this.value);
          this.isShowDialog = !!value;
          if (this.isShowDialog) {
            if (this.groupId !== '') {
              this.requestQueue = ['templateList', 'groupTemplate'];
              this.fetchPermTemplate();
            } else {
              this.requestQueue = ['templateList'];
              this.fetchData();
            }
          } else {
            this.requestQueue = ['templateList'];
          }
        },
        immediate: true
      }
    },
    created () {
      this.searchData = [
        {
          id: 'name',
          name: this.$t(`m.permTemplate['模板名']`),
          default: true
        },
        {
          id: 'system_id',
          name: this.$t(`m.common['所属系统']`),
          remoteMethod: this.handleRemoteSystem
        },
        {
          id: 'creator',
          name: this.$t(`m.grading['创建人']`),
          remoteMethod: this.handleRemoteRtx
        },
        {
          id: 'description',
          name: this.$t(`m.common['描述']`),
          disabled: true
        }
      ];
    },
    methods: {
      async fetchPermTemplate () {
        try {
          const res = await this.$store.dispatch('userGroup/getUserGroupTemplateList', { id: this.groupId });
          this.defaultTemplateIds = res.data.map(item => item.id);
          this.fetchData();
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
        }
      },

      handleRefresh () {
        this.resetData();
        this.hasChekedList.splice(0, this.hasChekedList.length, ...this.value);
        if (this.groupId !== '') {
          this.requestQueue = ['templateList', 'groupTemplate'];
          this.fetchPermTemplate();
        } else {
          this.requestQueue = ['templateList'];
          this.fetchData();
        }
      },

      resetData () {
        this.isScrollBottom = false;
        this.expiredAt = 15552000;
        this.defaultTemplateIds.splice(0, this.defaultTemplateIds.length, ...[]);
        this.systemList.splice(0, this.systemList.length, ...[]);
        this.hasChekedList.splice(0, this.hasChekedList.length, ...[]);
        this.permTemplateList.splice(0, this.permTemplateList.length, ...[]);
        this.allCheked = false;
        this.indeterminate = false;
        this.isPrev = true;
        this.pagination.totalPage = 1;
        this.pagination.current = 1;
        this.pagination.limit = 7;
      },

      handleToCreate () {
        const url = this.$router.resolve({
          name: `permTemplateCreate`
        });
        window.open(url.href, '_blank');
      },

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.common['关键字']`),
          id: 'keyword',
          values: [value]
        };
      },

      handleAfterEditLeave () {
        this.$emit('update:show', false);
        this.$emit('on-after-leave');
        this.resetData();
        this.searchValue = [];
      },

      handleNextStep () {
        this.isPrev = false;
      },

      handlePrevStep () {
        this.expiredAt = 15552000;
        this.isPrev = true;
      },

      handleDeadlineChange (payload) {
        this.expiredAt = payload;
      },

      handleSearch (payload) {
        this.isScrollBottom = false;
        this.pagination.limit = 7;
        this.pagination.totalPage = 1;
        this.pagination.current = 1;
        this.searchValue = payload;
        this.isSearch = true;
        this.fetchData(true);
      },

      handleRemoteRtx (value) {
        return fuzzyRtxSearch(value)
          .then(data => {
            return data.results;
          });
      },

      handleRemoteSystem (value) {
        const params = {};
        if (this.externalSystemId) {
          params.hidden = false;
        }
        return this.$store.dispatch('system/getSystems', params)
          .then(({ data }) => {
            return data.map(({ id, name }) => ({ id, name })).filter(item => item.name.indexOf(value) > -1);
          });
      },
            
      handleEmptyClear () {
        this.searchParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 7, totalPage: 1 });
        this.fetchData(true);
      },

      handleEmptyRefresh () {
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 7, totalPage: 1 });
        this.fetchData(true);
      },

      async fetchData (isTableLoading = false) {
        this.tableLoading = isTableLoading;
        const params = {
                    ...this.searchValue,
                    limit: this.pagination.limit,
                    offset: this.pagination.limit * (this.pagination.current - 1)
        };
        const ids = this.hasChekedList.map(item => item.id);
        try {
          const { code, data } = await this.$store.dispatch('permTemplate/getTemplateList', params);
          this.pagination.totalPage = Math.ceil(data.count / this.pagination.limit);
          (data.results || []).forEach(item => {
            if (ids.includes(item.id)) {
              this.$set(item, 'checked', true);
            } else {
              this.$set(item, 'checked', false);
            }

            this.$set(item, 'disabled', false);

            if (this.defaultTemplateIds.includes(item.id) || this.defaultValue.includes(item.id)) {
              this.$set(item, 'checked', true);
              this.$set(item, 'disabled', true);
            }
          });
          // if (this.hasChekedList.length) {
          //     if (this.hasChekedList.length === res.data.count) {
          //         this.allCheked = true
          //         this.indeterminate = false
          //     } else {
          //         this.indeterminate = true
          //         this.allCheked = false
          //     }
          // } else {
          //     this.allCheked = false
          //     this.indeterminate = false
          // }
          this.permTemplateList.splice(0, this.permTemplateList.length, ...(data.results || []));
          this.emptyData = formatCodeData(code, this.emptyData, data.results.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.resetData();
          this.messageAdvancedError(e);
        } finally {
          this.requestQueue.shift();
          this.tableLoading = false;
        }
      },

      async handleScroll (event) {
        if (this.isLoading || this.isScrollLoading) {
          return;
        }
        if (event.target.scrollTop + event.target.offsetHeight >= event.target.scrollHeight) {
          this.isScrollBottom = true;
          this.pagination.current = this.pagination.current + 1;
          if (this.pagination.current <= this.pagination.totalPage) {
            const searchParams = {};
            if (this.searchValue.length > 0) {
              this.searchValue.forEach(item => {
                searchParams[item.id] = item.values[0].id;
              });
            }
            const params = {
                            ...searchParams,
                            limit: this.pagination.limit,
                            offset: this.pagination.limit * (this.pagination.current - 1)
            };
            const ids = this.hasChekedList.map(item => item.id);
            this.isScrollLoading = true;
            try {
              const res = await this.$store.dispatch('permTemplate/getTemplateList', params);
              const list = res.data.results || [];
              // if (this.hasChekedList.length) {
              //     if (this.hasChekedList.length === res.data.count) {
              //         this.allCheked = true
              //         this.indeterminate = false
              //     } else {
              //         this.indeterminate = true
              //         this.allCheked = false
              //     }
              // } else {
              //     this.allCheked = false
              //     this.indeterminate = false
              // }
              list.forEach(item => {
                if (ids.includes(item.id)) {
                  this.$set(item, 'checked', true);
                } else {
                  this.$set(item, 'checked', false);
                }

                this.$set(item, 'disabled', false);

                if (this.defaultTemplateIds.includes(item.id) || this.defaultValue.includes(item.id)) {
                  this.$set(item, 'checked', true);
                  this.$set(item, 'disabled', true);
                }
              });
              this.permTemplateList.push(...list);
            } catch (e) {
              console.error(e);
              this.messageAdvancedError(e);
            } finally {
              this.isScrollLoading = false;
              const curScrollDom = this.$refs.permTemplateRef;
              // 加载完往回滚动的距离，防止无线滚动加载
              const scrollHeight = 2;
              curScrollDom.scrollTo(0, curScrollDom.scrollTop - scrollHeight);
            }
          }
        } else {
          this.isScrollBottom = false;
        }
      },

      handleChecked (item) {
        if (item.disabled) {
          return;
        }
        item.checked = !item.checked;
        if (item.checked) {
          this.hasChekedList.push(item);
        } else {
          for (let i = 0; i < this.hasChekedList.length; i++) {
            if (this.hasChekedList[i].id === item.id) {
              this.hasChekedList.splice(i, 1);
              break;
            }
          }
        }
        this.indeterminate = this.hasChekedList.length
          && this.hasChekedList.length !== this.permTemplateList.length;
        this.allCheked = this.hasChekedList.length === this.permTemplateList.length;
      },

      handleAllChecked (checked) {
        this.allCheked = checked;
        if (checked) {
          this.indeterminate = false;
        }
        for (let i = 0; i < this.permTemplateList.length; i++) {
          this.permTemplateList[i]['checked'] = checked;
        }
        this.hasChekedList = checked ? [...this.permTemplateList] : [];
      },

      handleSumbit () {
        if (this.showExpiredAt) {
          this.$emit('on-sumbit', {
            data: this.hasChekedList.map(({ id, name, system }) => ({ id, name, system })),
            expired_at: this.expiredAt
          });
          return;
        }
        this.$emit('on-sumbit', this.hasChekedList.map(({ id, name, system }) => ({ id, name, system })));
      },

      handleCancel () {
        this.$emit('on-cancel');
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-select-perm-template-dialog {
        .refresh {
            float: right;
            color: #3a84ff;
            cursor: pointer;
            &:hover {
                color: #699df4;
            }
        }
        .title {
            line-height: 26px;
            color: #313238;
            .member-title {
                display: inline-block;
                max-width: 470px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                vertical-align: top;
            }
            .expired-at-title {
                display: inline-block;
                max-width: 290px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                vertical-align: top;
            }
        }
        .perm-template-content-wrapper {
            .perm-template-search-wrapper {
                position: relative;
                width: 100%;
                height: 32px;
                .left {
                    float: left;
                    .perm-template-search-input {
                        display: inline-block;
                        width: 420px;
                        .chip-clear {
                            font-size: 12px !important;
                        }
                    }
                }
                .right {
                    margin-top: 8px;
                    float: right;
                    .count {
                        color: #2dcb56;
                    }
                }
            }
            .perm-template-content {
                position: relative;
                top: 10px;
                min-height: 322px;
            }
            .perm-template-fixed-table {
                width: 100%;
                border-top: 1px solid #e6e6e6;
                border-left: 1px solid #e6e6e6;
                border-right: 1px solid #e6e6e6;
                border-bottom: none;
                thead {
                    tr {
                        th {
                            height: 42px;
                            font-size: 12px;
                            background: #f5f6fa;
                            .bk-form-checkbox .bk-checkbox-text {
                                font-size: 12px;
                            }
                        }
                    }
                }
            }
            .perm-template-table {
                position: relative;
                width: 100%;
                max-height: 277px;
                margin-top: -1px;
                overflow-y: auto;
                border-left: 1px solid #e6e6e6;
                border-right: 1px solid #e6e6e6;
                &.is-be-loading {
                    height: 277px;
                    border-bottom: 1px solid #e6e6e6;
                }
                &.can-not-scroll {
                    border-bottom: 1px solid #e6e6e6;
                    overflow-y: hidden;
                }
                &.no-top-border {
                    border-top: none;
                }
                &.no-bottom-border {
                    border-bottom: none;
                }
                &.has-bottom-border {
                    border-bottom: 1px solid #e6e6e6;
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
                .bk-table {
                    width: 100%;
                    border: none;
                    thead {
                        tr {
                            th {
                                height: 42px;
                                font-size: 12px;
                            }
                        }
                    }
                    tbody {
                        tr {
                            position: relative;
                            td {
                                height: 42px;
                                font-size: 12px;
                            }
                        }
                        tr.loading-tr {
                            td {
                                padding: 0;
                            }
                        }
                        tr.no-more-data-tr {
                            div {
                                color: #979ba5;
                                text-align: center;
                            }
                        }
                        .search-empty-wrapper {
                            position: relative;
                            min-height: 255px;
                            .empty-wrapper {
                                position: absolute;
                                left: 50%;
                                top: 50%;
                                text-align: center;
                                transform: translate(-50%, -50%);
                                img {
                                    width: 120px;
                                }
                                .empty-tips {
                                    position: relative;
                                    top: -20px;
                                    font-size: 12px;
                                    color: #dcdee5;
                                }
                            }
                        }
                    }
                    .node-checkbox-wrapper {
                        float: left;
                        .node-checkbox {
                            display: inline-block;
                            position: relative;
                            top: 3px;
                            width: 16px;
                            height: 16px;
                            margin: 0 6px 0 0;
                            border-radius: 2px;
                            border: 1px solid #979ba5;
                            &.is-checked {
                                border-color: #3a84ff;
                                background-color: #3a84ff;
                                background-clip: border-box;
                                &:after {
                                    content: "";
                                    position: absolute;
                                    top: 1px;
                                    left: 4px;
                                    width: 4px;
                                    height: 8px;
                                    border: 2px solid #fff;
                                    border-left: 0;
                                    border-top: 0;
                                    transform-origin: center;
                                    transform: rotate(45deg) scaleY(1);
                                }
                                &.is-disabled {
                                    background-color: #dcdee5;
                                }
                            }
                            &.is-disabled {
                                border-color: #dcdee5;
                                cursor: not-allowed;
                            }
                            &.is-indeterminate {
                                border-width: 7px 4px;
                                border-color: #3a84ff;
                                background-color: #fff;
                                background-clip: content-box;
                                &:after {
                                    visibility: hidden;
                                }
                            }
                        }
                    }
                    .system-name,
                    .name {
                        display: inline-block;
                        max-width: 140px;
                        font-size: 12px;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                        vertical-align: middle;
                    }
                    .desc {
                        display: inline-block;
                        max-width: 200px;
                        font-size: 12px;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                        vertical-align: middle;
                    }
                }
            }
        }
    }
</style>
