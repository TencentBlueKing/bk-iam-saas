<template>
    <div>
        <div class="iam-transfer-system-wrapper" :style="{ minHeight: isLoading ? '328px' : 0 }"
            v-bkloading="{ isLoading, opacity: 1 }">
            <template v-if="!isLoading && !isEmpty">
                <div class="transfer-system-content" ref="transferSystemContent">
                    <div class="header" @click="handleSystemExpanded">
                        <Icon bk class="expanded-icon" :type="systemExpanded ? 'down-shape' : 'right-shape'" />
                        <label class="title">系统管理员权限交接</label>
                    </div>
                    <div class="content" v-if="systemExpanded">
                        <div class="slot-content">
                            <bk-table
                                :style="{ maxHeight: systemShowAll ? 'none' : '254px' }"
                                border
                                ref="systemTable"
                                :data="sysManagerList"
                                size="small"
                                :class="{ 'set-border': tableLoading }"
                                v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
                                :header-cell-class-name="getCellClass"
                                :cell-class-name="getCellClass"
                                @select="handleSelect"
                                @select-all="handleSelectAll">
                                <bk-table-column type="selection" align="center">
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
                        <p class="expand-action" @click="handleSystemShowAll" v-if="sysManagerList.length > 5">
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
        <div class="iam-transfer-system-wrapper" :style="{ minHeight: isLoading ? '102px' : 0 }"
            v-bkloading="{ isLoading, opacity: 1 }">
            <template v-if="!isLoading && !isEmpty">
                <div class="transfer-system-content">
                    <div class="header" @click="handleSuperExpanded">
                        <Icon bk class="expanded-icon" :type="superExpanded ? 'down-shape' : 'right-shape'" />
                        <label class="title">超级管理员权限交接</label>
                    </div>
                    <div class="content" v-if="superExpanded">
                        <div class="slot-content">
                            <div class="member-item" v-for="(item, index) in superManager.members" :key="index">
                                <span class="member-name">
                                    {{item}}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </div>
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
                systemExpanded: true,
                systemShowAll: false,
                isSelectAllChecked: false,
                sysManagerList: [],
                superManager: {},
                systemSelectData: [],
                superExpanded: true,
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
                    const res = await this.$store.dispatch('getSuperAndSystemManager')
                    const list = res.data || []
                    const sysManagerList = list.filter(item => item.type === 'system_manager')
                    this.sysManagerList.splice(0, this.sysManagerList.length, ...sysManagerList)
                    this.isEmpty = sysManagerList.length < 1

                    this.superManager = Object.assign({}, list.find(item => item.type === 'super_manager') || {
                        members: []
                    })

                    this.$emit('get-super-manager', this.superManager)
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

            handleSuperExpanded () {
                this.superExpanded = !this.superExpanded
            },

            handleSystemExpanded () {
                this.systemExpanded = !this.systemExpanded
            },

            handleSystemShowAll () {
                this.systemShowAll = !this.systemShowAll
                if (!this.systemShowAll) {
                    setTimeout(() => {
                        const top = this.$refs.transferSystemContent.getBoundingClientRect().top
                            + this.pageContainer.scrollTop

                        this.pageContainer.scrollTo({
                            top: top - 61, // 减去顶导的高度 61
                            behavior: 'smooth'
                        })
                        // this.$refs.transferSystemContent.scrollIntoView({
                        //     behavior: 'smooth'
                        // })
                    }, 10)
                }
            },

            handleSelectAll (selection) {
                this.isSelectAllChecked = !!selection.length
                if (this.isSelectAllChecked) {
                    this.systemSelectData.splice(
                        0,
                        this.systemSelectData.length,
                        ...this.sysManagerList
                    )
                } else {
                    this.systemSelectData.splice(0, this.systemSelectData.length, ...[])
                }

                this.$emit('system-selection-change', this.systemSelectData)
            },

            handleSelect (selection) {
                this.isSelectAllChecked = selection.length === this.sysManagerList.length
                this.systemSelectData.splice(0, this.systemSelectData.length, ...selection)

                this.$emit('system-selection-change', this.systemSelectData)
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
    @import './system-super-manager.css';
</style>
