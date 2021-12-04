<template>
    <div class="iam-transfer-group-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="!isLoading && !isEmpty">
            <div class="iam-perm-item">
                <div class="header" @click="handleGroupExpanded">
                    <Icon bk class="expanded-icon" :type="groupExpanded ? 'down-shape' : 'right-shape'" />
                    <label class="title">用户组权限交接</label>
                    <div class="sub-title" v-if="groupNotTransferCount > 0">
                        <i class="iam-icon iamcenter-warning-fill not-transfer-icon"></i>
                        无法交接用户组：{{groupNotTransferCount}}个
                        <span class="reason">（通过组织加入、已过期的组无法交接）</span>
                    </div>
                </div>
                <div class="content" v-if="groupExpanded">
                    <div class="slot-content">
                        <bk-table
                            ref="groupTable"
                            :data="gGroupListRender"
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
                    <p class="expand-action" @click="handleGroupShowAll" v-if="groupListAll.length > 5">
                        <Icon :type="groupShowAll ? 'up-angle' : 'down-angle'" />
                        <template v-if="!groupShowAll">{{ $t(`m.common['点击展开']`) }}</template>
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
                groupListAll: [], // 用户组权限交接所有数据
                gGroupListRender: [], // 用户组权限交接所有数据
                groupExpanded: true,
                groupShowAll: false,
                groupNotTransferCount: 0,
                isSelectAllChecked: false,
                groupSelectData: []
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
                    const groupListAll = res.data || []
                    groupListAll.forEach(item => {
                        if (String(item.department_id) !== '0' || item.expired_at_display === '已过期') {
                            this.groupNotTransferCount += 1
                            item.isNotTransfer = true
                        }
                    })

                    this.groupListAll.splice(0, this.groupListAll.length, ...groupListAll)
                    const gGroupListRender = res.data.slice(0, 5) || []
                    this.gGroupListRender.splice(
                        0,
                        this.gGroupListRender.length,
                        ...gGroupListRender
                    )

                    this.isEmpty = groupListAll.length < 1
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

            handleGroupExpanded () {
                this.groupExpanded = !this.groupExpanded
            },

            handleSelectAll (selection) {
                this.isSelectAllChecked = !!selection.length

                if (this.isSelectAllChecked) {
                    const validGroupList = this.groupListAll.filter(item => !item.isNotTransfer)
                    this.groupSelectData.splice(
                        0,
                        this.groupSelectData.length,
                        ...validGroupList
                    )
                }

                this.$emit('group-selection-change', this.groupSelectData)
            },

            handleGroupShowAll () {
                this.groupShowAll = !this.groupShowAll
                if (this.groupShowAll) {
                    this.gGroupListRender.splice(
                        0,
                        this.gGroupListRender.length,
                        ...this.groupListAll
                    )
                } else {
                    this.gGroupListRender.splice(
                        0,
                        this.gGroupListRender.length,
                        ...this.groupListAll.slice(0, 5)
                    )
                }
                if (this.isSelectAllChecked) {
                    this.$refs.groupTable.clearSelection()
                    this.$refs.groupTable.toggleAllSelection()
                }
            },

            handleSelectionChange (selection) {
                const validGroupList = this.groupListAll.filter(item => !item.isNotTransfer)
                this.isSelectAllChecked = selection.length === validGroupList.length
                this.groupSelectData.splice(0, this.groupSelectData.length, ...selection)
                this.$emit('group-selection-change', this.groupSelectData)
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
