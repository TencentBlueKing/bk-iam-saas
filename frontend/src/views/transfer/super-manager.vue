<template>
    <div class="iam-transfer-group-wrapper" :style="{ minHeight: isLoading ? '328px' : 0 }"
        v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="!isLoading && !isEmpty">
            <div class="transfer-group-content">
                <div class="header" @click="handlesuperExpanded">
                    <Icon bk class="expanded-icon" :type="superExpanded ? 'down-shape' : 'right-shape'" />
                    <label class="title">超级管理员权限交接</label>
                </div>
                <div class="content" v-if="superExpanded">
                    <div class="slot-content">
                        <div class="member-item">
                            <span class="member-name">
                                超级管理员
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </div>
</template>
<script>
    export default {
        name: '',
        components: {
        },
        data () {
            return {
                isEmpty: false,
                isLoading: false,
                superListAll: [], // 超级管理员权限交接
                superExpanded: true
            }
        },
        mounted () {
            this.fetchData()
        },
        methods: {
            async fetchData () {
                this.isLoading = true
                try {
                    const res = await this.$store.dispatch('getSuperAndSystemManager') // 普通用户没有获取超级管理员接口数据的权限...需要确认
                    const superListAll = res.data || []
                    this.superListAll.splice(0, this.superListAll.length, ...superListAll)
                    this.isEmpty = superListAll.length < 1
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

            handlesuperExpanded () {
                this.superExpanded = !this.superExpanded
            }
        }
    }
</script>
<style lang="postcss">
    @import './group.css';
</style>
