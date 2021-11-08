<template>
    <div class="my-perm-custom-perm">
        <template v-if="hasPerm">
            <render-perm-item
                data-test-id="myPerm_list_system"
                v-for="(sys, sysIndex) in systemList"
                :key="sys.id"
                :expanded.sync="sys.expanded"
                :ext-cls="sysIndex > 0 ? 'iam-perm-ext-cls' : ''"
                :class="sysIndex === systemList.length - 1 ? 'iam-perm-ext-reset-cls' : ''"
                :title="sys.name"
                :perm-length="sys.count"
                :one-perm="onePerm"
                @on-expanded="handleExpanded(...arguments, sys)">
                <perm-table
                    data-test-id="myPerm_table_actionPerm"
                    :key="sys.id"
                    :system-id="sys.id"
                    @after-delete="handleAfterDelete(...arguments, sysIndex)" />
            </render-perm-item>
        </template>
        <template v-else>
            <div class="my-perm-custom-perm-empty-wrapper">
                <iam-svg />
                <div class="empty-tips">{{ $t(`m.common['暂无数据']`) }}</div>
            </div>
        </template>
    </div>
</template>
<script>
    import RenderPermItem from '../components/render-perm'
    import PermTable from '../components/perm-table-edit'
    import PermSystem from '@/model/my-perm-system'
    export default {
        name: '',
        components: {
            RenderPermItem,
            PermTable
        },
        data () {
            return {
                systemList: [],
                onePerm: ''
            }
        },
        computed: {
            hasPerm () {
                return this.systemList.length > 0
            }
        },
        async created () {
            await this.fetchSystems()
        },
        methods: {
            /**
             * 展开/收起 系统下的权限列表
             *
             * @param {Boolean} value 展开收起标识
             * @param {Object} payload 当前系统
             */
            handleExpanded (value, payload) {},

            /**
             * 获取系统列表
             */
            async fetchSystems () {
                try {
                    const res = await this.$store.dispatch('permApply/getHasPermSystem')
                    this.systemList = (res.data || []).map(item => new PermSystem(item))
                    this.onePerm = this.systemList.length
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
                    this.$emit('toggle-loading', false)
                }
            },

            handleAfterDelete (payload, sysIndex) {
                --this.systemList[sysIndex].count
                if (this.systemList[sysIndex].count < 1) {
                    this.systemList.splice(sysIndex, 1)
                }
            }
        }
    }
</script>
<style lang="postcss">
    @import './index.css';
</style>
