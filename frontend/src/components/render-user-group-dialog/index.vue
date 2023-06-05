<template>
  <bk-dialog
    v-model="isShowDialog"
    width="700"
    title=""
    :mask-close="false"
    draggable
    header-position="left"
    ext-cls="iam-select-user-group-dialog"
    @after-leave="handleAfterEditLeave">
    <div slot="header" class="title">
      <!-- eslint-disable max-len -->
      <template>
        <span> {{$t(`m.common['将']`)}}{{$t(`m.common['【']`)}}</span>
        <span class="group-title" :title="name">{{ name }}</span>
        <span>{{$t(`m.common['】']`)}}{{$t(`m.common['关联到以下用户组']`)}}</span>
      </template>
    </div>
    <div class="user-group-content-wrapper">
      <div class="user-group-search-wrapper">
        <div class="left">
          <iam-search-select
            @on-change="handleSearch"
            :data="searchData"
            :value="searchValue"
            :quick-search-method="quickSearchMethod"
            style="width: 420px;" />
        </div>
        <div class="right">
          <template v-if="curLanguageIsCn">
            {{ $t(`m.common['已选择']`) }}
            <span class="count">{{ hasChekedList.length }}</span>
            {{ $t(`m.common['个用户组']`) }}
          </template>
          <template v-else>
            <span class="count">{{ hasChekedList.length }}</span>
            {{ $t(`m.common['已选择']`) }}
          </template>
        </div>
      </div>
      <div class="user-group-content">
        <table
          class="bk-table user-group-fixed-table">
          <colgroup>
            <col style="width: 200px;" />
            <col style="width: 200px;" />
            <col />
          </colgroup>
          <thead>
            <tr>
              <th style="padding-left: 20px;">
                {{ $t(`m.common['ID']`) }}
              </th><th>{{ $t(`m.userGroup['用户组名']`) }}</th>
              <th>{{ $t(`m.common['描述']`) }}</th>
            </tr>
          </thead>
        </table>
        <div :class="['user-group-table',
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
                <tr v-for="(item, index) in userGroupList"
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
                    <span class="name" :title="item.disabled ? $t(`m.info['该用户组已关联']`) : ''">{{ '#' + item.id }}</span>
                  </td>
                  <td>
                    <span class="user-group-name" :title="item.name">{{ item.name }}</span>
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
                        <ExceptionEmpty
                          :type="emptyData.type"
                          :empty-text="emptyData.text"
                          :tip-text="emptyData.tip"
                          :tip-type="emptyData.tipType"
                          @on-clear="handleEmptyClear"
                          @on-refresh="handleEmptyRefresh"
                        />
                        <!-- <iam-svg />
                                                <p class="empty-tips">{{ isSearch ? $t(`m.common['搜索无结果']`) : $t(`m.common['暂无数据']`) }}</p> -->
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <template slot="footer">
      <bk-button theme="primary" :disabled="isDisabled" :loading="loading" @click="handleSumbit">{{ $t(`m.common['确定']`) }}</bk-button>
      <bk-button style="margin-left: 10px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
    </template>
  </bk-dialog>
</template>
<script>
  import IamSearchSelect from '@/components/iam-search-select';
  import { formatCodeData } from '@/common/util';
  import { mapGetters } from 'vuex';

  export default {
    name: '',
    components: {
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
      templateId: {
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
      }
    },
    data () {
      return {
        isShowDialog: false,
        isScrollLoading: false,
        isScrollBottom: false,
        systemList: [],
        userGroupList: [],
        hasChekedList: [],
        allCheked: false,
        indeterminate: false,
        pagination: {
          totalPage: 1,
          limit: 7,
          current: 1
        },
        searchValue: {},
        requestQueue: ['groupList'],
        defaultGroupIds: [],
        tableLoading: false,
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
            allChekedDisabled () {
                return this.userGroupList.length < 1 || this.isLoading;
            },
            isEmpty () {
                return this.userGroupList.length < 1;
            },
            isNoBottomBorder () {
                return !this.isLoading && this.isScrollBottom;
            },
            isHasBottomBorder () {
                return this.userGroupList.length >= this.pagination.limit && !this.isScrollBottom;
            },
            isShowNoDataText () {
                return this.pagination.current >= this.pagination.totalPage
                    && !this.isScrollLoading
                    && this.pagination.totalPage !== 1;
            },
            isDisabled () {
                return this.hasChekedList.length < 1;
            }
    },
    watch: {
      show: {
        handler (value) {
          this.hasChekedList.splice(0, this.hasChekedList.length, ...this.value);
          this.isShowDialog = !!value;
          if (this.isShowDialog) {
            if (this.templateId !== '') {
              this.requestQueue = ['groupList', 'templateGroup'];
              this.fetchTemplateGroup();
            } else {
              this.requestQueue = ['groupList'];
              this.fetchData();
            }
          } else {
            this.requestQueue = ['groupList'];
          }
        },
        immediate: true
      }
    },
    created () {
      this.searchData = [
        {
          id: 'id',
          name: 'ID'
        },
        {
          id: 'name',
          name: this.$t(`m.userGroup['用户组名']`),
          default: true
        },
        {
          id: 'description',
          name: this.$t(`m.common['描述']`),
          disabled: true
        },
        {
          id: 'system_id',
          name: this.$t(`m.common['系统包含']`),
          remoteMethod: this.handleRemoteSystem
        }
      ];
    },
    methods: {
      async fetchTemplateGroup () {
        const params = {
          limit: 10000,
          offset: 0,
          id: this.templateId,
          types: 'group'
        };
        try {
          const res = await this.$store.dispatch('permTemplate/getTemplateMember', params);
          this.defaultGroupIds = res.data.results.map(item => item.id);
          this.fetchData();
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        } finally {
          this.requestQueue.shift();
        }
      },

      quickSearchMethod (value) {
        return {
          name: this.$t(`m.userGroup['用户组名']`),
          id: 'name',
          values: [value]
        };
      },

      handleAfterEditLeave () {
        this.$emit('update:show', false);
        this.$emit('on-after-leave');
        this.isScrollBottom = false;
        this.searchValue = [];
        this.defaultGroupIds.splice(0, this.defaultGroupIds.length, ...[]);
        this.systemList.splice(0, this.systemList.length, ...[]);
        this.hasChekedList.splice(0, this.hasChekedList.length, ...[]);
        this.userGroupList.splice(0, this.userGroupList.length, ...[]);
        this.allCheked = false;
        this.indeterminate = false;
        this.pagination.totalPage = 1;
        this.pagination.current = 1;
        this.pagination.limit = 7;
      },

      handleSearch (payload) {
        this.isScrollBottom = false;
        this.searchValue = payload;
        this.pagination.limit = 7;
        this.pagination.totalPage = 1;
        this.pagination.current = 1;
        // this.isSearch = true;
        this.emptyData.tipType = 'search';
        this.fetchData(true);
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
          const { code, data } = await this.$store.dispatch('userGroup/getUserGroupList', params);
          this.pagination.totalPage = Math.ceil(data.count / this.pagination.limit);
          (data.results || []).forEach(item => {
            if (ids.includes(item.id)) {
              this.$set(item, 'checked', true);
            } else {
              this.$set(item, 'checked', false);
            }

            this.$set(item, 'disabled', false);

            if (this.defaultGroupIds.includes(String(item.id)) || this.defaultValue.includes(item.id)) {
              this.$set(item, 'checked', true);
              this.$set(item, 'disabled', true);
            }
          });
          this.userGroupList.splice(0, this.userGroupList.length, ...(data.results || []));
          this.emptyData = formatCodeData(code, this.emptyData, data.results.length === 0);
        } catch (e) {
          console.error(e);
          const { code, data, message, statusText } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.userGroupList = [];
          this.bkMessageInstance = this.$bkMessage({
            theme: 'error',
            message: message || data.msg || statusText
          });
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
              const res = await this.$store.dispatch('userGroup/getUserGroupList', params);
              const list = res.data.results || [];
              list.forEach(item => {
                if (ids.includes(item.id)) {
                  this.$set(item, 'checked', true);
                } else {
                  this.$set(item, 'checked', false);
                }

                this.$set(item, 'disabled', false);

                if (this.defaultGroupIds.includes(String(item.id))
                  || this.defaultValue.includes(item.id)
                ) {
                  this.$set(item, 'checked', true);
                  this.$set(item, 'disabled', true);
                }
              });
              this.userGroupList.push(...list);
            } catch (e) {
              console.error(e);
              this.bkMessageInstance = this.$bkMessage({
                theme: 'error',
                message: e.message || e.data.msg || e.statusText
              });
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
          && this.hasChekedList.length !== this.userGroupList.length;
        this.allCheked = this.hasChekedList.length === this.userGroupList.length;
      },

      handleAllChecked (checked) {
        this.allCheked = checked;
        if (checked) {
          this.indeterminate = false;
        }
        for (let i = 0; i < this.userGroupList.length; i++) {
          this.userGroupList[i]['checked'] = checked;
        }
        this.hasChekedList = checked ? [...this.userGroupList] : [];
      },

      handleSumbit () {
        this.$emit('on-sumbit', this.hasChekedList.map(item => {
          return {
            type: 'group',
            id: item.id
          };
        }));
      },

      handleCancel () {
        this.$emit('on-cancel');
      }
    }
  };
</script>
<style lang='postcss'>
    .iam-select-user-group-dialog {
        .title {
            line-height: 26px;
            color: #313238;
            .group-title {
                display: inline-block;
                max-width: 470px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                vertical-align: top;
            }
        }
        .user-group-content-wrapper {
            height: 360px;
            .user-group-search-wrapper {
                width: 100%;
                height: 32px;
                .left {
                    float: left;
                }
                .right {
                    margin-top: 8px;
                    float: right;
                    .count {
                        color: #2dcb56;
                    }
                }
            }
            .user-group-content {
                position: relative;
                top: 10px;
                min-height: 322px;
            }
            .user-group-fixed-table {
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
            .user-group-table {
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
                    .user-group-name,
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
