<template>
    <div class="iam-transfer-rating-wrapper" :style="{ minHeight: isLoading ? '328px' : 0 }"
        v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="!isLoading && !isEmpty">
            <div class="transfer-rating-content">
                <div class="header" @click="handlerateExpanded">
                    <Icon bk class="expanded-icon" :type="rateExpanded ? 'down-shape' : 'right-shape'" />
                    <label class="title">分级管理员权限交接</label>
                </div>
                <div class="content" v-if="rateExpanded">
                    <div class="slot-content">
                        <bk-table
                            border
                            ref="rateTable"
                            :data="rateListRender"
                            size="small"
                            :class="{ 'set-border': tableLoading }"
                            v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
                            :row-key="tableRowKey"
                            :header-cell-class-name="getCellClass"
                            :cell-class-name="getCellClass"
                            @selection-change="handleSelectionChange"
                            @select-all="handleSelectAll">
                            <bk-table-column type="selection" align="center"
                                :reserve-selection="true">
                            </bk-table-column>
                            <bk-table-column :label="$t(`m.grading['分级管理员名称']`)" width="300">
                                <template slot-scope="{ row }">
                                    {{row.name}}
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t(`m.common['描述']`)" width="300">
                                <template slot-scope="{ row }">
                                    {{row.description || '--'}}
                                </template>
                            </bk-table-column>
                        </bk-table>
                    </div>
                    <p class="expand-action" @click="handlerateShowAll" v-if="rateListAll.length > 5">
                        <Icon :type="rateShowAll ? 'up-angle' : 'down-angle'" />
                        <template v-if="!rateShowAll">{{ $t(`m.common['点击展开']`) }}</template>
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
                rateListRender: [],
                rateListAll: [], // 分级管理员权限交接
                rateExpanded: true,
                isSelectAllChecked: false,
                rateSelectData: []
            }
        },
        mounted () {
            this.fetchData()
        },
        methods: {
            // roleList
            async fetchData () {
                this.isLoading = true
                try {
                    const res = await this.$store.dispatch('roleList')
                    console.error(res)
                    const rateListAll = res || []
                    this.rateListAll.splice(0, this.rateListAll.length, ...rateListAll)
                    const rateListRender = rateListAll.length > 5 ? rateListAll.slice(0, 5) : rateListAll
                    this.rateListRender.splice(0, this.rateListRender.length, ...rateListRender)
                    this.isEmpty = rateListAll.length < 1
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

            handlerateExpanded () {
                this.rateExpanded = !this.rateExpanded
            },

            handleSelectAll (selection) {
                this.isSelectAllChecked = !!selection.length

                if (this.isSelectAllChecked) {
                    this.rateSelectData.splice(
                        0,
                        this.rateSelectData.length,
                        ...this.rateListAll
                    )
                }

                this.$emit('rate-selection-change', this.rateSelectData)
            },

            handleSelectionChange (selection) {
                this.isSelectAllChecked = selection.length === this.rateListAll.length
                this.rateSelectData.splice(0, this.rateSelectData.length, ...selection)

                this.$emit('rate-selection-change', this.rateSelectData)
            },

            handlerateShowAll () {
                this.rateShowAll = !this.rateShowAll
                if (this.rateShowAll) {
                    this.rateListRender.splice(
                        0,
                        this.rateListRender.length,
                        ...this.rateListAll
                    )
                } else {
                    this.rateListRender.splice(
                        0,
                        this.rateListRender.length,
                        ...(this.rateListAll.length > 5 ? this.rateListAll.slice(0, 5) : this.rateListAll)
                    )
                }
                if (this.isSelectAllChecked) {
                    this.$refs.rateTable.clearSelection()
                    this.$refs.rateTable.toggleAllSelection()
                }
            },

            tableRowKey (row) {
                return row.id + '__' + row.name
            },

            /**
             * getCellClass
             */
            getCellClass ({ row, column, rowIndex, columnIndex }) {
                if (columnIndex === 0) {
                    return 'checkbox-cell-wrapper'
                }
                return ''
            }
        }
    }
</script>
<style lang="postcss">
    @import './rating-manager.css';
    /* .member-item {
            position: relative;
            display: inline-block;
            margin: 0 6px 6px 0;
            padding: 0 10px;
            line-height: 22px;
            background: #f5f6fa;
            border: 1px solid #dcdee5;
            border-radius: 2px;
            font-size: 12px;
            .member-name {
                display: inline-block;
                max-width: 200px;
                line-height: 17px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                vertical-align: text-top;
                .count {
                    color: #c4c6cc;
                }
            }
        } */
</style>
