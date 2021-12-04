<template>
    <div class="iam-transfer-custom-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="!isLoading && !isEmpty">
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
                    @after-delete="handleAfterDelete(...arguments, sysIndex)" />
            </custom-perm-system-policy>
        </template>
        <template v-if="!isLoading && isEmpty">
            <div class="empty-wrapper">
                <iam-svg />
                <div class="empty-tips">{{ $t(`m.common['暂无数据']`) }}</div>
            </div>
        </template>
    </div>
</template>
<script>
    /* eslint-disable no-unused-vars */
    import CustomPermSystemPolicy from '@/components/custom-perm-system-policy/index.vue'
    import PermSystem from '@/model/my-perm-system'
    import CustomPermTable from './custom-perm-table.vue'

    export default {
        name: 'CustomPerm',
        components: {
            CustomPermSystemPolicy,
            CustomPermTable
        },
        data () {
            return {
                isEmpty: false,
                isLoading: false,
                onePerm: 0,
                systemPolicyList: []
            }
        },
        mounted () {
            this.fetchData()
        },
        methods: {
            async fetchData () {
                this.isLoading = true
                try {
                    const res = await this.$store.dispatch('permApply/getHasPermSystem')
                    const list = res.data || []
                    const systemPolicyList = list.map(item => new PermSystem(item))
                    this.systemPolicyList.splice(0, this.systemPolicyList.length, ...systemPolicyList)
                    this.onePerm = systemPolicyList.length
                    this.isEmpty = systemPolicyList.length < 1
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
                    })
                } finally {
                    this.isLoading = false
                }
            },

            /**
             * 展开/收起 系统下的权限列表
             *
             * @param {Boolean} value 展开收起标识
             * @param {Object} payload 当前系统
             */
            handleExpanded (value, payload) {},

            handleAfterDelete (policyListLen, sysIndex) {
                --this.systemPolicyList[sysIndex].count
                if (this.systemPolicyList[sysIndex].count < 1) {
                    this.systemPolicyList.splice(sysIndex, 1)
                }
            }
        }
    }
</script>
<style lang="postcss">
    @import './custom.css';
</style>
