<template>
    <div class="my-perm-custom-perm">
        <template v-if="hasPerm">
            <custom-perm-item
                v-for="(sys, sysIndex) in dataList"
                :key="sys.id"
                :expanded.sync="sys.expanded"
                :ext-cls="sysIndex > 0 ? 'iam-perm-ext-cls' : ''"
                :class="sysIndex === dataList.length - 1 ? 'iam-perm-ext-reset-cls' : ''"
                :title="sys.name"
                :perm-length="sys.count"
                :one-perm="onePerm"
                @on-expanded="handleExpanded(...arguments, sys)">
                <perm-table
                    :key="sys.id"
                    :system-id="sys.id"
                    @after-delete="handleAfterDelete(...arguments, sysIndex)" />
            </custom-perm-item>
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
    import CustomPermItem from '@/components/custom-perm-item/index.vue'
    import PermTable from '../components/perm-table-edit'
    import PermSystem from '@/model/my-perm-system'
    export default {
        name: '',
        components: {
            CustomPermItem,
            PermTable
        },
        props: {
            systemList: {
                type: Array,
                default: () => []
            }
        },
        data () {
            return {
                onePerm: '',
                dataList: []
            }
        },
        computed: {
            hasPerm () {
                return this.dataList.length > 0
            }
        },
        watch: {
            systemList: {
                handler (v) {
                    const dataList = v.map(item => new PermSystem(item))
                    this.dataList.splice(0, this.dataList.length, ...dataList)
                    this.onePerm = dataList.length
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

            handleAfterDelete (payload, sysIndex) {
                --this.dataList[sysIndex].count
                if (this.dataList[sysIndex].count < 1) {
                    this.dataList.splice(sysIndex, 1)
                }
            }
        }
    }
</script>
<style lang="postcss">
    @import './index.css';
</style>
