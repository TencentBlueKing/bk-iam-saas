<template>
    <div class="iam-transfer-custom-wrapper" :style="{ minHeight: isLoading ? '328px' : 0 }"
        v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="!isLoading && !isEmpty">
            <div class="transfer-custom-content">
                <div class="header" @click="handleCustomExpanded">
                    <Icon bk class="expanded-icon" :type="customExpanded ? 'down-shape' : 'right-shape'" />
                    <label class="title">{{$t(`m.permTransfer['自定义权限交接']`)}}</label>
                    <div class="sub-title" v-if="customNotTransferCount > 0">
                        <i class="iam-icon iamcenter-warning-fill not-transfer-icon"></i>
                        {{$t(`m.permTransfer['无法交接自定义权限：']`)}}{{customNotTransferCount}}个
                        <span class="reason">{{$t(`m.permTransfer['（已过期的自定义权限无法交接）']`)}}</span>
                    </div>
                </div>
                <div class="content" v-show="customExpanded">
                    <div class="slot-content">
                        <template v-for="(sys, sysIndex) in systemPolicyList">
                            <div class="system-list-wrapper" :class="sysIndex > 0 ? 'iam-perm-ext-cls' : ''"
                                :key="sys.id">
                                <div class="system-list-item-header" @click="handleSystemExpanded(sys)">
                                    <Icon bk class="system-list-item-expanded"
                                        :type="sys.expanded ? 'angle-down' : 'angle-right'" />
                                    <label class="system-list-item-title">{{ sys.name }}</label>
                                    <div class="system-list-item-sub-title" v-if="sys.count > 0">
                                        {{ $t(`m.common['共']`) }}
                                        <span style="font-weight: 700;">{{ sys.count }}</span>
                                        {{ $t(`m.common['个']`) }}
                                        {{ $t(`m.perm['操作权限']`) }}
                                    </div>
                                </div>
                                <div class="system-list-item-content" v-if="sys.expanded">
                                    <custom-perm-table
                                        :key="sys.id"
                                        :policy-list="sys.policyList"
                                        :loading="sys.loading"
                                        @custom-selection-change="handleCustomSelection(...arguments, sys)" />
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        </template>
        <!-- <template v-if="!isLoading && isEmpty">
            <div class="empty-wrapper">
                <iam-svg />
                <div class="empty-tips">{{ $t(`m.common['暂无数据']`) }}</div>
            </div>
        </template> -->
    </div>
</template>
<script>
    import { mapGetters } from 'vuex';

    import PermPolicy from '@/model/my-perm-policy';
    import PermSystem from '@/model/my-perm-system';
    import CustomPermTable from './custom-perm-table.vue';

    export default {
        name: 'CustomPerm',
        components: {
            CustomPermTable
        },
        data () {
            return {
                isEmpty: false,
                isLoading: false,
                systemPolicyList: [],
                customExpanded: true,
                customNotTransferCount: 0,
                customSelectDataMap: {}
            };
        },
        computed: {
            ...mapGetters(['user', 'externalSystemId'])
        },
        mounted () {
            this.fetchData();
        },
        methods: {
            async fetchData () {
                this.isLoading = true;
                try {
                    const externalSystemParams = this.externalSystemId ? { system_id: this.externalSystemId } : '';
                    const res = await this.$store.dispatch('permApply/getHasPermSystem', externalSystemParams);
                    const list = res.data || [];
                    const systemPolicyList = list.map(item => {
                        const sys = new PermSystem(item);
                        sys.loading = false;
                        sys.policyList = [];
                        return sys;
                    });
                    this.systemPolicyList.splice(0, this.systemPolicyList.length, ...systemPolicyList);
                    this.isEmpty = systemPolicyList.length < 1;
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
                    this.isLoading = false;
                }
            },

            handleCustomExpanded () {
                this.customExpanded = !this.customExpanded;
            },

            async handleSystemExpanded (sys) {
                sys.expanded = !sys.expanded;
                if (sys.expanded) {
                    try {
                        sys.loading = true;
                        const res = await this.$store.dispatch('permApply/getPolicies', { system_id: sys.id });
                        const alreadyLoadedList = sys.policyList;
                        sys.policyList = res.data.map(item => {
                            const policy = new PermPolicy(item);
                            if (policy.expired_at < this.user.timestamp) {
                                this.customNotTransferCount += 1;
                                policy.isExpired = true;
                            }
                            const foundPolicy = alreadyLoadedList.find(
                                p => p.id === policy.id && p.policy_id === policy.policy_id
                            );
                            policy.transferChecked = foundPolicy ? foundPolicy.transferChecked : false;

                            // test
                            // if (policy.policy_id % 2 === 0) {
                            //     policy.expired_at = 0
                            // }
                            return policy;
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
                        sys.loading = false;
                    }
                }
            },

            handleCustomSelection (policySelectionList, sys) {
                const policyList = [];
                policyList.splice(0, 0, ...sys.policyList);

                if (policySelectionList.length === 0) {
                    policyList.forEach(p => {
                        p.transferChecked = false;
                    });
                } else {
                    policyList.forEach(p => {
                        p.transferChecked = false;
                        const foundPolicy = policySelectionList.find(
                            policy => policy.id === p.id && policy.policy_id === p.policy_id
                        );
                        if (foundPolicy) {
                            p.transferChecked = true;
                        }
                    });
                }
                sys.policyList.splice(0, sys.policyList.length, ...policyList);

                // 组装 customSelectData
                const customSelectDataMap = Object.assign({}, this.customSelectDataMap);
                const key = sys.id; // + '|||' + sys.name
                if (!customSelectDataMap[key]) {
                    customSelectDataMap[key] = [];
                }
                const selectedPolicyList = policyList.filter(p => p.transferChecked);
                if (selectedPolicyList.length) {
                    customSelectDataMap[key].splice(0, customSelectDataMap[key].length, ...selectedPolicyList);
                } else {
                    delete customSelectDataMap[key];
                }
                this.customSelectDataMap = Object.assign({}, customSelectDataMap);
                // const customSelectData = []
                // Object.values(this.customSelectDataMap).forEach(v => {
                //     customSelectData.push(...v)
                // })
                this.$emit('custom-selection-change', customSelectDataMap);
            }
        }
    };
</script>
<style lang="postcss">
    @import './custom.css';
</style>
