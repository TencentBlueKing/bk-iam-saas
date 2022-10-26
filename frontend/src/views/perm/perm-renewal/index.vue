<template>
    <smart-action class="iam-perm-renewal-wrapper">
        <render-horizontal-block
            :label="$t(`m.renewal['选择权限']`)"
            :required="true">
            <bk-tab
                :key="tabKey"
                :active.sync="active"
                ref="tabRef"
                type="unborder-card"
                ext-cls="iam-renewal-tab-cls"
                @tab-change="handleTabChange">
                <bk-tab-panel
                    v-for="(panel, index) in panels"
                    v-bind="panel"
                    :key="index">
                    <template slot="label">
                        <span class="panel-name">
                            {{ panel.label }}<span style="color:#c4c6cc">({{panel.total}})</span>
                        </span>
                        <!-- <bk-badge :val="panel.count" :theme="curBadgeTheme(panel.name)" /> -->
                    </template>
                </bk-tab-panel>
            </bk-tab>
            <render-table
                :renewal-time="expiredAt"
                :type="active"
                :data="getTableList"
                :loading="tableLoading"
                @on-select="handleSelected" />
        </render-horizontal-block>
        <p class="error-tips" v-if="isShowErrorTips">请选择过期权限</p>
        <render-horizontal-block :label="$t(`m.renewal['续期时长']`)">
            <iam-deadline :value="expiredAt" @on-change="handleDeadlineChange" />
        </render-horizontal-block>
        <div slot="action">
            <bk-button theme="primary" disabled v-if="isEmpty">
                <span v-bk-tooltips="{ content: $t(`m.renewal['暂无将过期的权限']`), extCls: 'iam-tooltips-cls' }">
                    {{ $t(`m.common['提交']`) }}
                </span>
            </bk-button>
            <bk-button theme="primary" :loading="submitLoading" v-else @click="handleSubmit">
                {{ $t(`m.common['提交']`) }}
            </bk-button>
            <bk-button style="margin-left: 6px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
        </div>
    </smart-action>
</template>
<script>
    import { buildURLParams } from '@/common/url';
    import { SIX_MONTH_TIMESTAMP, ONE_DAY_TIMESTAMP } from '@/common/constants';
    import IamDeadline from '@/components/iam-deadline/horizontal';
    import RenderTable from '../components/render-renewal-table';
    import { mapGetters } from 'vuex';

    export default {
        name: '',
        components: {
            IamDeadline,
            RenderTable
        },
        data () {
            return {
                panels: [
                    { name: 'group', label: this.$t(`m.perm['用户组权限']`), count: 0, total: 0, data: [] },
                    { name: 'custom', label: this.$t(`m.perm['自定义权限']`), count: 0, total: 0, data: [] }
                ],
                active: 'group',
                expiredAt: SIX_MONTH_TIMESTAMP,
                submitLoading: false,
                tableList: [],
                tableLoading: false,
                isShowErrorTips: false,
                tabKey: 'tab-key',
                isEmpty: false
            };
        },
        computed: {
            getTableList () {
                return this.panels.find(item => item.name === this.active).data || [];
            },
            curBadgeTheme () {
                return payload => {
                    return payload === this.active ? '#e1ecff' : '#f0f1f5';
                };
            },
            ...mapGetters(['externalSystemsLayout'])
        },
        watch: {
            panels: {
                handler (value) {
                    if (this.active === 'group') {
                        if (value[0].total > 0) {
                            this.isEmpty = false;
                        } else {
                            this.isEmpty = true;
                        }
                    } else if (this.active === 'custom') {
                        if (value[1].total > 0) {
                            this.isEmpty = false;
                        } else {
                            this.isEmpty = true;
                        }
                    }
                },
                immediate: true
            },
            externalSystemsLayout: {
                handler (value) {
                    if (value.myPerm.renewal.hideCustomTab) {
                        this.panels.splice(1, 1);
                    }
                },
                immediate: true,
                deep: true
            }
        },
        async created () {
            this.isEmpty = false;
            this.curSelectedList = [];
            const query = this.$route.query;
            this.active = query.tab || 'group';
            this.fetchData();
        },
        methods: {
            async fetchData () {
                this.tableLoading = true;
                const promiseList = [this.$store.dispatch('renewal/getExpireSoonGroupWithUser', {
                    page_size: 10,
                    page: 1
                }), this.$store.dispatch('renewal/getExpireSoonPerm')];
                const resultList = await Promise.all(promiseList).finally(() => {
                    this.tableLoading = false;
                });
                this.panels[0].total = resultList[0].data.count;
                this.panels[0].data = resultList[0].data.results;
                this.panels[1].total = resultList[1].data.length;
                this.panels[1].data = resultList[1].data;
                this.tabKey = +new Date();
            },
            // async fetchPageData () {
            //     await this.fetchData()
            // },

            // async fetchData (isLoading = false) {
            //     this.tableLoading = isLoading
            //     const dispatchMethod = this.active === 'group' ? 'getExpireSoonGroupWithUser' : 'getExpireSoonPerm'
            //     try {
            //         const res = await this.$store.dispatch(`renewal/${dispatchMethod}`)
            //         this.tableList = res.data || []
            //     } catch (e) {
            //         console.error(e)
            //         this.bkMessageInstance = this.$bkMessage({
            //             limit: 1,
            //             theme: 'error',
            //             message: e.message || e.data.msg || e.statusText
            //         })
            //     } finally {
            //         this.tableLoading = false
            //     }
            // },

            handleTabChange (payload) {
                this.$nextTick(() => {
                    this.$refs.tabRef
                        && this.$refs.tabRef.$refs.tabLabel
                        && this.$refs.tabRef.$refs.tabLabel.forEach(label => label.$forceUpdate());
                });
                window.history.replaceState({}, '', `?${buildURLParams({ tab: payload })}`);
            },

            handleDeadlineChange (payload) {
                this.expiredAt = payload || ONE_DAY_TIMESTAMP;
            },

            handleSelected (type, value) {
                if (type === 'group') {
                    this.panels[0].count = this.panels[0].total;
                    this.curSelectedList = value;
                } else {
                    this.panels[1].count = value.length;
                    this.curSelectedList = value;
                }
                this.isShowErrorTips = false;
                this.$nextTick(() => {
                    this.$refs.tabRef
                        && this.$refs.tabRef.$refs.tabLabel
                        && this.$refs.tabRef.$refs.tabLabel.forEach(label => label.$forceUpdate());
                });
            },

            async handleSubmit () {
                if (this.curSelectedList.length < 1) {
                    this.isShowErrorTips = true;
                    return;
                }
                this.submitLoading = true;
                const isGroup = this.active === 'group';
                const params = {
                    reason: '续期'
                };
                if (isGroup) {
                    params.groups = this.curSelectedList.map(
                        ({ id, name, description, expired_at }) => ({ id, name, description, expired_at })
                    );
                } else {
                    params.policies = this.curSelectedList.map(({ id, expired_at }) => ({ id, expired_at }));
                }
                const dispatchMethod = isGroup ? 'groupPermRenewal' : 'customPermRenewal';
                try {
                    await this.$store.dispatch(`renewal/${dispatchMethod}`, params);
                    this.messageSuccess(this.$t(`m.renewal['批量申请提交成功']`), 1000);
                    this.$router.push({
                        name: 'apply'
                    });
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
                    this.submitLoading = false;
                }
            },

            handleCancel () {
                this.$router.push({
                    name: 'myPerm'
                });
            }
        }
    };
</script>
<style lang="postcss">
    .iam-perm-renewal-wrapper {
        .iam-renewal-tab-cls {
            .bk-tab-section {
                padding: 0;
            }
        }
        .panel-name {
            margin: 0 3px;
            display: inline-block;
            vertical-align: middle;
        }
        .error-tips {
            position: relative;
            top: -10px;
            font-size: 12px;
            color: #ea3636;
        }
    }
</style>
