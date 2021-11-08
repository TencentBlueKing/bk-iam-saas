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
                style="margin: 0 0 16px 6px;"
                :disabled="isEmpty || isNoRenewal"
                @click="handleBatchRenewal">
                {{ $t(`m.renewal['批量续期']`) }}
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
            :active.sync="active"
            type="unborder-card"
            ext-cls="iam-my-perm-tab-cls"
            @tab-change="handleTabChange">
            <bk-tab-panel
                v-for="(panel, index) in panels"
                v-bind="panel"
                :key="index">
                <div class="content-wrapper" v-bkloading="{ isLoading: componentLoading, opacity: 1 }">
                    <component
                        v-show="!componentLoading"
                        :is="active"
                        @toggle-loading="toggleLoadingHandler"
                    ></component>
                </div>
            </bk-tab-panel>
        </bk-tab>
    </div>
</template>
<script>
    import { buildURLParams } from '@/common/url'
    import CustomPerm from './custom-perm'
    import GroupPerm from './group-perm'
    export default {
        name: '',
        components: {
            CustomPerm,
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
                    }
                ],
                active: 'GroupPerm',
                isEmpty: false,
                isNoRenewal: false,
                SoonGroupLength: '',
                SoonPermLength: ''

            }
        },
        created () {
            const query = this.$route.query
            if (query.tab) {
                this.componentLoading = true
                this.active = query.tab
            }
        },
        methods: {
            async fetchPageData () {
                await this.fetchData()
            },

            handleTabChange (payload) {
                this.componentLoading = true
                window.history.replaceState({}, '', `?${buildURLParams({ tab: payload })}`)
            },
            async fetchData () {
                try {
                    const [res1, res2, res3, res4] = await Promise.all([
                        this.fetchPermGroups(),
                        this.fetchSystems(),
                        this.fetchSoonGroupWithUser(),
                        this.fetchSoonPerm()
                    ])
                    this.isEmpty = res1.data.length < 1 && res2.data.length < 1
                    this.SoonGroupLength = res3.data.length
                    this.SoonPermLength = res4.data.length
                    this.isNoRenewal = this.SoonGroupLength < 1 && this.SoonPermLength < 1
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
                    })
                }
            },
            fetchSoonGroupWithUser () {
                return this.$store.dispatch('renewal/getExpireSoonGroupWithUser')
            },
            fetchSoonPerm () {
                return this.$store.dispatch('renewal/getExpireSoonPerm')
            },
            fetchSystems () {
                return this.$store.dispatch('permApply/getHasPermSystem')
            },

            fetchPermGroups () {
                return this.$store.dispatch('perm/getPersonalGroups')
            },

            handleGoApply () {
                this.$router.push({
                    name: 'applyJoinUserGroup'
                })
            },

            handleBatchRenewal () {
                if (this.SoonGroupLength > 0 && this.SoonPermLength < 1) {
                    this.$router.push({
                        name: 'permRenewal',
                        query: {
                            tab: 'group'
                        }
                    })
                } else if (this.SoonPermLength > 0 && this.SoonGroupLength < 1) {
                    this.$router.push({
                        name: 'permRenewal',
                        query: {
                            tab: 'custom'
                        }
                    })
                } else if (this.SoonPermLength > 0 && this.SoonGroupLength > 0) {
                    this.$router.push({
                        name: 'permRenewal',
                        query: {
                            tab: this.active === 'GroupPerm' ? 'group' : 'custom'
                        }
                    })
                }
            },

            /**
             * 切换父组件的 loading 状态回调函数
             *
             * @param {boolean} isLoading loading 状态
             */
            toggleLoadingHandler (isLoading) {
                this.componentLoading = isLoading
            }
        }
    }
</script>
<style lang="postcss">
    .iam-my-perm-wrapper {
        position: relative;
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
