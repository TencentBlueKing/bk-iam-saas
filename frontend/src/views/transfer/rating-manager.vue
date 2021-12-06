<template>
    <div class="iam-transfer-rating-wrapper" :style="{ minHeight: isLoading ? '328px' : 0 }"
        v-bkloading="{ isLoading, opacity: 1 }">
        <template v-if="!isLoading && !isEmpty">
            <div class="transfer-rating-content" ref="transferRatingContent">
                <div class="header" @click="handleRateExpanded">
                    <Icon bk class="expanded-icon" :type="rateExpanded ? 'down-shape' : 'right-shape'" />
                    <label class="title">分级管理员权限交接</label>
                </div>
                <div class="content" v-if="rateExpanded">
                    <div class="slot-content">
                        <bk-table
                            :style="{ maxHeight: rateShowAll ? 'none' : '254px' }"
                            border
                            ref="rateTable"
                            :data="rateList"
                            size="small"
                            :class="{ 'set-border': tableLoading }"
                            v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
                            :header-cell-class-name="getCellClass"
                            :cell-class-name="getCellClass"
                            @select="handleSelect"
                            @select-all="handleSelectAll">
                            <bk-table-column type="selection" align="center">
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
                    <p class="expand-action" @click="handleRateShowAll" v-if="rateList.length > 5">
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
                rateList: [], // 分级管理员权限交接
                rateExpanded: true,
                rateShowAll: false,
                isSelectAllChecked: false,
                rateSelectData: [],
                pageContainer: null
            }
        },
        mounted () {
            this.pageContainer = document.querySelector('.main-scroller')
            this.fetchData()
        },
        methods: {
            async fetchData () {
                this.isLoading = true
                try {
                    const res = await this.$store.dispatch('roleList')
                    const rateList = res || []
                    this.rateList.splice(0, this.rateList.length, ...rateList)

                    this.isEmpty = rateList.length < 1
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

            handleRateExpanded () {
                this.rateExpanded = !this.rateExpanded
            },

            handleRateShowAll () {
                this.rateShowAll = !this.rateShowAll
                if (!this.rateShowAll) {
                    setTimeout(() => {
                        const top = this.$refs.transferRatingContent.getBoundingClientRect().top
                            + this.pageContainer.scrollTop

                        this.pageContainer.scrollTo({
                            top: top - 61, // 减去顶导的高度 61
                            behavior: 'smooth'
                        })
                        // this.$refs.transferRatingContent.scrollIntoView({
                        //     behavior: 'smooth'
                        // })
                    }, 10)
                }
            },

            handleSelectAll (selection) {
                this.isSelectAllChecked = !!selection.length
                if (this.isSelectAllChecked) {
                    this.rateSelectData.splice(
                        0,
                        this.rateSelectData.length,
                        ...this.rateList
                    )
                } else {
                    this.rateSelectData.splice(0, this.rateSelectData.length, ...[])
                }

                this.$emit('rate-selection-change', this.rateSelectData)
            },

            handleSelect (selection) {
                this.isSelectAllChecked = selection.length === this.rateList.length
                this.rateSelectData.splice(0, this.rateSelectData.length, ...selection)

                this.$emit('rate-selection-change', this.rateSelectData)
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
