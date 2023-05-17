<template>
    <div class="my-perm-custom-perm">
        <template v-if="hasPerm">
            <custom-perm-system-policy
                v-for="(sys, sysIndex) in systemPolicyList"
                :key="sys.id"
                :expanded.sync="sys.expanded"
                :ext-cls="sysIndex > 0 ? 'iam-perm-ext-cls' : ''"
                :class="sysIndex === systemPolicyList.length - 1 ? 'iam-perm-ext-reset-cls' : ''"
                :title="sys.name"
                :perm-length="sys.count"
                :one-perm="onePerm"
                @on-expanded="handleExpanded(...arguments, sys)">
                <custom-perm-table
                    :key="sys.id"
                    :system-id="sys.id"
                    :empty-data="emptyData"
                    @after-delete="handleAfterDelete(...arguments, sysIndex)" />
            </custom-perm-system-policy>
        </template>
        <template v-else>
            <div class="my-perm-custom-perm-empty-wrapper">
                <ExceptionEmpty
                    :type="emptyData.type"
                    :empty-text="emptyData.text"
                    :tip-text="emptyData.tip"
                    :tip-type="emptyData.tipType"
                    @on-refresh="handleEmptyRefresh"
                />
            </div>
        </template>
    </div>
</template>
<script>
    import CustomPermSystemPolicy from '@/components/custom-perm-system-policy/index.vue';
    import PermSystem from '@/model/my-perm-system';
    import CustomPermTable from './custom-perm-table.vue';

    export default {
        name: 'CustomPerm',
        components: {
            CustomPermSystemPolicy,
            CustomPermTable
        },
        props: {
            systemList: {
                type: Array,
                default: () => []
            },
            emptyData: {
                type: Object,
                default: () => {
                    return {
                        type: '',
                        text: '',
                        tip: '',
                        tipType: ''
                    };
                }
            }
        },
        data () {
            return {
                onePerm: 0,
                systemPolicyList: []
            };
        },
        computed: {
            hasPerm () {
                return this.systemPolicyList.length > 0;
            }
        },
        watch: {
            systemList: {
                handler (v) {
                    const systemPolicyList = v.map(item => new PermSystem(item));
                    this.systemPolicyList.splice(0, this.systemPolicyList.length, ...systemPolicyList);
                    this.onePerm = systemPolicyList.length;
                },
                immediate: true,
                deep: true
            }
        },
        created () {
        },
        methods: {
            /**
             * 展开/收起 系统下的权限列表
             *
             * @param {Boolean} value 展开收起标识
             * @param {Object} payload 当前系统
             */
            handleExpanded (value, payload) {},

            handleAfterDelete (policyListLen, sysIndex) {
                --this.systemPolicyList[sysIndex].count;
                if (this.systemPolicyList[sysIndex].count < 1) {
                    this.systemPolicyList.splice(sysIndex, 1);
                }
            }
        }
    };
</script>
<style lang="postcss">
    @import './index.css';
</style>
