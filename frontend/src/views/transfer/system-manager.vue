<template>
    <div class="iam-transfer-group-wrapper" :style="{ minHeight: isLoading ? '328px' : 0 }"
        v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="!isLoading && !isEmpty">
            <div class="transfer-group-content">
                <div class="header" @click="handlesystemExpanded">
                    <Icon bk class="expanded-icon" :type="systemExpanded ? 'down-shape' : 'right-shape'" />
                    <label class="title">系统管理员权限交接</label>
                </div>
                <div class="content" v-if="systemExpanded">
                    <div class="slot-content">
                        <bk-table
                            border
                            ref="systemTable"
                            :data="systemListRender"
                            size="small"
                            :class="{ 'set-border': tableLoading }"
                            v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
                            :row-key="tableRowKey"
                            @selection-change="handleSelectionChange"
                            @select-all="handleSelectAll">
                            <bk-table-column type="selection" align="center"
                                :reserve-selection="true">
                            </bk-table-column>
                            <bk-table-column :label="$t(`m.grading['系统管理员名称']`)" width="300">
                                <template slot-scope="{ row }">
                                    {{row.name}}
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t(`m.common['成员']`)" width="300">
                                <template slot-scope="{ row }">
                                    {{row.members.join(';')}}
                                </template>
                            </bk-table-column>
                        </bk-table>
                    </div>
                    <p class="expand-action" @click="handlesystemShowAll" v-if="systemListAll.length > 5">
                        <Icon :type="systemShowAll ? 'up-angle' : 'down-angle'" />
                        <template v-if="!systemShowAll">{{ $t(`m.common['点击展开']`) }}</template>
                        <template v-else>{{ $t(`m.common['点击收起']`) }}</template>
                    </p>
                </div>
            </div>
        </template>
        <template v-if="!isLoading && isEmpty">
            <div class="empty-wrapper">
                <iam-svg />
                <p class="text">{{ $t(`m.common['暂无数据']`) }}</p>
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
                systemListRender: [],
                systemListAll: [], // 分级管理员权限交接
                systemExpanded: true,
                isSelectAllChecked: false,
                systemSelectData: []
            }
        },
        mounted () {
            this.fetchData()
        },
        methods: {
            async fetchData () {
                this.isLoading = true
                try {
                    const res = await this.$store.dispatch('role/getSystemManager')
                    const systemListAll = res.data || []
                    this.systemListAll.splice(0, this.systemListAll.length, ...systemListAll)
                    const systemListRender = res.data.length > 5
                        ? res.data.slice(0, 5) : res.data
                    this.systemListRender.splice(0, this.systemListRender.length, ...systemListRender)
                    this.isEmpty = systemListAll.length < 1
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

            handlesystemExpanded () {
                this.systemExpanded = !this.systemExpanded
            },

            handleSelectAll (selection) {
                this.isSelectAllChecked = !!selection.length

                if (this.isSelectAllChecked) {
                    this.systemSelectData.splice(
                        0,
                        this.systemSelectData.length,
                        ...this.systemListAll
                    )
                }
                
                this.$emit('system-selection-change', this.systemSelectData)
            },

            handleSelectionChange (selection) {
                this.isSelectAllChecked = selection.length === this.systemListAll.length
                this.systemSelectData.splice(0, this.systemSelectData.length, ...selection)

                this.$emit('system-selection-change', this.systemSelectData)
            },

            handlesystemShowAll () {
                this.systemShowAll = !this.systemShowAll
                if (this.systemShowAll) {
                    this.systemListRender.splice(
                        0,
                        this.systemListRender.length,
                        ...this.systemListAll
                    )
                } else {
                    this.systemListRender.splice(
                        0,
                        this.systemListRender.length,
                        ...(this.systemListAll.length > 5 ? this.systemListAll.slice(0, 5) : this.systemListAll)
                    )
                }
                if (this.isSelectAllChecked) {
                    this.$refs.systemTable.clearSelection()
                    this.$refs.systemTable.toggleAllSelection()
                }
            },

            tableRowKey (row) {
                return row.id + '__' + row.name
            }
        }
    }
</script>
<style lang="postcss">
    @import './group.css';
</style>
