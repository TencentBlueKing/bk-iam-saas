<template>
    <div class="iam-my-perm-wrapper">
        <div class="header">
            <bk-button
                data-test-id="myPerm_btn_applyPerm"
                type="button"
                theme="primary"
                style="margin-bottom: 16px;"
                @click="handleGoApply">
                {{ $t(`m.common['申请权限']`) }}
            </bk-button>
            <bk-button
                data-test-id="myPerm_btn_batchRenewal"
                style="margin: 0 6px 16px 6px;"
                :disabled="isEmpty || isNoRenewal"
                @click="handleBatchRenewal">
                {{ $t(`m.renewal['批量续期']`) }}
            </bk-button>
            <bk-button
                v-if="enablePermissionHandover.toLowerCase() === 'true'"
                data-test-id="myPerm_btn_transferPerm"
                type="button"
                style="margin-bottom: 16px;"
                @click="handleGoPermTransfer">
                {{ $t(`m.permTransfer['权限交接']`) }}
            </bk-button>
        </div>
        <div class="redCircle" v-if="!isNoRenewal"></div>
        <template v-if="isEmpty">
            <div class="empty-wrapper">
                <iam-svg />
                <div class="empty-tips">{{ $t(`m.common['您还没有任何权限']`) }}</div>
            </div>
        </template>
        <bk-tab
            v-else
            :active="active"
            type="unborder-card"
            ext-cls="iam-my-perm-tab-cls"
            @tab-change="handleTabChange">
            <bk-tab-panel
                v-for="(panel, index) in panels"
                :data-test-id="`myPerm_tabPanel_${panel.name}`"
                v-bind="panel"
                :key="index">
                <div class="content-wrapper" v-bkloading="{ isLoading: componentLoading, opacity: 1 }">
                    <component
                        v-if="!componentLoading && active === panel.name"
                        :is="active"
                        :personal-group-list="personalGroupList"
                        :system-list="systemList"
                        @refresh="fetchData"
                    ></component>
                </div>
            </bk-tab-panel>
        </bk-tab>
    </div>
</template>
<script>
    import { buildURLParams } from '@/common/url';
    import CustomPerm from './custom-perm/index.vue';
    import TeporaryCustomPerm from './teporary-custom-perm/index.vue';
    import GroupPerm from './group-perm/index.vue';

    export default {
        name: 'MyPerm',
        components: {
            CustomPerm,
            TeporaryCustomPerm,
            GroupPerm
        },
        data () {
            return {
                componentLoading: true,
                panels: [
                    {
                        name: 'GroupPerm', label: this.$t(`m.perm['用户组权限']`)
                    },
                    {
                        name: 'CustomPerm', label: this.$t(`m.approvalProcess['自定义权限']`)
                    },
                    {
                        name: 'TeporaryCustomPerm', label: this.$t(`m.myApply['临时权限']`)
                    }
                ],
                active: 'GroupPerm',
                isEmpty: false,
                isNoRenewal: false,
                soonGroupLength: 0,
                soonPermLength: 0,
                personalGroupList: [],
                systemList: [],
                enablePermissionHandover: window.ENABLE_PERMISSION_HANDOVER
            };
        },
        created () {
            const query = this.$route.query;
            if (query.tab) {
                this.active = query.tab;
            }
        },
        methods: {
            async fetchPageData () {
                await this.fetchData();
            },

            async handleTabChange (tabName) {
                this.active = tabName;
                await this.fetchData();
                window.history.replaceState({}, '', `?${buildURLParams({ tab: tabName })}`);
            },

            async fetchData () {
                this.componentLoading = true;
                try {
                    const [res1, res2, res3, res4] = await Promise.all([
                        this.$store.dispatch('perm/getPersonalGroups'),
                        this.$store.dispatch('permApply/getHasPermSystem'),
                        this.$store.dispatch('renewal/getExpireSoonGroupWithUser'),
                        this.$store.dispatch('renewal/getExpireSoonPerm')
                        // this.fetchPermGroups(),
                        // this.fetchSystems(),
                        // this.fetchSoonGroupWithUser(),
                        // this.fetchSoonPerm()
                    ]);
                    const personalGroupList = res1.data || [];
                    this.personalGroupList.splice(0, this.personalGroupList.length, ...personalGroupList);

                    const systemList = res2.data || [];
                    this.systemList.splice(0, this.systemList.length, ...systemList);

                    this.isEmpty = personalGroupList.length < 1 && systemList.length < 1;
                    this.soonGroupLength = res3.data.length;
                    this.soonPermLength = res4.data.length;
                    this.isNoRenewal = this.soonGroupLength < 1 && this.soonPermLength < 1;
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
                    this.componentLoading = false;
                }
            },
            // fetchSoonGroupWithUser () {
            //     return this.$store.dispatch('renewal/getExpireSoonGroupWithUser')
            // },
            // fetchSoonPerm () {
            //     return this.$store.dispatch('renewal/getExpireSoonPerm')
            // },
            // fetchSystems () {
            //     return this.$store.dispatch('permApply/getHasPermSystem')
            // },

            // fetchPermGroups () {
            //     return this.$store.dispatch('perm/getPersonalGroups')
            // },

            handleGoApply () {
                this.$router.push({
                    name: 'applyJoinUserGroup'
                });
            },

            handleBatchRenewal () {
                if (this.soonGroupLength > 0 && this.soonPermLength < 1) {
                    this.$router.push({
                        name: 'permRenewal',
                        query: {
                            tab: 'group'
                        }
                    });
                } else if (this.soonPermLength > 0 && this.soonGroupLength < 1) {
                    this.$router.push({
                        name: 'permRenewal',
                        query: {
                            tab: 'custom'
                        }
                    });
                } else if (this.soonPermLength > 0 && this.soonGroupLength > 0) {
                    this.$router.push({
                        name: 'permRenewal',
                        query: {
                            tab: this.active === 'GroupPerm' ? 'group' : 'custom'
                        }
                    });
                }
            },
            // 权限交接
            handleGoPermTransfer () {
                this.$router.push({
                    name: 'permTransfer'
                });
            }
        }
    };
</script>
<style lang="postcss">
    .iam-my-perm-wrapper {
        position: relative;
        .header {
            position: relative;
        }
        .content-wrapper {
            /* 20 + 20 + 42 + 24 + 24 + 61 + 48 */
            min-height: calc(100vh - 239px);
        }
        .empty-wrapper {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            img {
                width: 120px;
            }
            .empty-tips {
                position: relative;
                top: -25px;
                font-size: 12px;
                color: #c4c6cc;
                text-align: center;
            }
        }
        .redCircle {
            position: relative;
            top: -50px;
            right: -180px;
            width:10px;
            height:10px;
            background-color: red;
            border-radius: 50%;

        }
    }
    .iam-my-perm-tab-cls {
        background: #fff;
    }
</style>
