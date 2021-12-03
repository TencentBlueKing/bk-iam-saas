<template>
    <div class="iam-transfer-personal-group-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="!isLoading && !isEmpty">
            <div class="iam-perm-item">
                <div class="header" @click="handlePersonalGroupExpanded">
                    <Icon bk class="expanded-icon" :type="personalGroupExpanded ? 'down-shape' : 'right-shape'" />
                    <label class="title">用户组权限交接</label>
                    <div class="sub-title" v-if="personalGroupNotTransferCount > 0">
                        <i class="iam-icon iamcenter-warning-fill not-transfer-icon"></i>
                        无法交接用户组：{{personalGroupNotTransferCount}}个
                        <span class="reason">（通过组织加入、已过期的组无法交接）</span>
                    </div>
                </div>
                <div class="content" v-if="personalGroupExpanded">
                    <div class="slot-content">
                        <bk-table
                            ref="personalGroupTable"
                            :data="personalGroupListRender"
                            size="small"
                            :class="{ 'set-border': tableLoading }"
                            v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
                            :row-key="tableRowKey"
                            @selection-change="handleSelectionChange"
                            @select-all="handleSelectAll">
                            <bk-table-column type="selection" align="center" :selectable="row => !row.isNotTransfer"
                                :reserve-selection="true">
                            </bk-table-column>
                            <bk-table-column :label="$t(`m.userGroup['用户组名']`)" width="300">
                                <template slot-scope="{ row }">
                                    <span :style="{ color: row.isNotTransfer ? '#c4c6cc' : '' }">
                                        {{row.name}}
                                        <i class="iam-icon iamcenter-warning-fill not-transfer-icon"
                                            v-if="row.isNotTransfer"></i>
                                    </span>
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t(`m.approvalProcess['来源']`)" width="300">
                                <template slot-scope="{ row }">
                                    <span :style="{ color: row.isNotTransfer ? '#c4c6cc' : '' }"
                                        :title="row.role && row.role.name ? row.role.name : ''">
                                        {{ row.role ? row.role.name : '--' }}
                                    </span>
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t(`m.perm['加入方式']`)" width="350">
                                <template slot-scope="{ row }">
                                    <span :style="{ color: row.isNotTransfer ? '#c4c6cc' : '' }"
                                        v-if="row.department_id === 0">{{ $t(`m.perm['直接加入']`) }}</span>
                                    <span :style="{ color: row.isNotTransfer ? '#c4c6cc' : '' }"
                                        v-else :title="`${$t(`m.perm['通过组织加入']`)}：${row.department_name}`">
                                        {{ $t(`m.perm['通过组织加入']`) }}：{{ row.department_name }}
                                    </span>
                                </template>
                            </bk-table-column>
                        </bk-table>
                    </div>
                    <p class="expand-action" @click="handlePersonalGroupShowAll" v-if="personalGroupListAll.length > 5">
                        <Icon :type="personalGroupShowAll ? 'up-angle' : 'down-angle'" />
                        <template v-if="!personalGroupShowAll">{{ $t(`m.common['点击展开']`) }}</template>
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
                personalGroupListAll: [], // 用户组权限交接所有数据
                personalGroupListRender: [], // 用户组权限交接所有数据
                personalGroupExpanded: true,
                personalGroupShowAll: false,
                personalGroupNotTransferCount: 0,
                isSelectAllChecked: false,
                personalGroupSelectData: []
            }
        },
        mounted () {
            this.fetchData()
        },
        methods: {
            async fetchData () {
                this.isLoading = true
                try {
                    const res = await this.$store.dispatch('perm/getPersonalGroups')
                    const personalGroupListAll = res.data || []
                    personalGroupListAll.forEach(item => {
                        if (String(item.department_id) !== '0' || item.expired_at_display === '已过期') {
                            this.personalGroupNotTransferCount += 1
                            item.isNotTransfer = true
                        }
                    })

                    this.personalGroupListAll.splice(0, this.personalGroupListAll.length, ...personalGroupListAll)
                    const personalGroupListRender = res.data.slice(0, 5) || []
                    this.personalGroupListRender.splice(
                        0,
                        this.personalGroupListRender.length,
                        ...personalGroupListRender
                    )

                    this.isEmpty = personalGroupListAll.length < 1
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

            handlePersonalGroupExpanded () {
                this.personalGroupExpanded = !this.personalGroupExpanded
            },

            handleSelectAll (selection) {
                this.isSelectAllChecked = !!selection.length
                this.personalGroupSelectData.splice(0, this.personalGroupSelectData.length, ...selection)
                this.$emit('personal-group-selection-change', this.personalGroupSelectData)
            },

            handlePersonalGroupShowAll () {
                this.personalGroupShowAll = !this.personalGroupShowAll
                if (this.personalGroupShowAll) {
                    this.personalGroupListRender.splice(
                        0,
                        this.personalGroupListRender.length,
                        ...this.personalGroupListAll
                    )
                } else {
                    this.personalGroupListRender.splice(
                        0,
                        this.personalGroupListRender.length,
                        ...this.personalGroupListAll.slice(0, 5)
                    )
                }
                if (this.isSelectAllChecked) {
                    this.$refs.personalGroupTable.clearSelection()
                    this.$refs.personalGroupTable.toggleAllSelection()
                }
            },

            handleSelectionChange (selection) {
                const validPersonalGroupList = this.personalGroupListAll.filter(item => !item.isNotTransfer)
                this.isSelectAllChecked = selection.length === validPersonalGroupList.length
                this.personalGroupSelectData.splice(0, this.personalGroupSelectData.length, ...selection)
                this.$emit('personal-group-selection-change', this.personalGroupSelectData)
            },

            tableRowKey (row) {
                return row.id + '__' + row.name
            }
        }
    }
</script>
<style lang="postcss">
    @import './personal-group.css';
</style>
