<template>
    <div class="my-perm-custom-perm-table" v-bkloading="{ isLoading: sys.loading, opacity: 1 }">
        <bk-table
            v-if="!sys.loading"
            ref="customTable"
            :data="renderPolicyList"
            border
            :header-cell-class-name="getCellClass"
            :cell-class-name="getCellClass"
            @selection-change="handleSelectionChange">
            <bk-table-column type="selection" align="center" :selectable="row => String(row.expired_at) !== '0'">
            </bk-table-column>
            <bk-table-column :label="$t(`m.common['操作']`)">
                <template slot-scope="{ row }">
                    <span :title="row.name">{{ row.name }}</span>
                    <!-- <bk-checkbox v-model="row.transferChecked" @change="handleCheckbox(row)">

                    </bk-checkbox> -->
                </template>
            </bk-table-column>
            <bk-table-column :resizable="false" :label="$t(`m.common['资源实例']`)" width="491">
                <template slot-scope="{ row }">
                    <template v-if="!row.isEmpty">
                        <p class="related-resource-item"
                            v-for="item in row.related_resource_types"
                            :key="item.type">
                            {{`${item.name}：${item.value}`}}
                        </p>
                    </template>
                    <template v-else>
                        {{ $t(`m.common['无需关联实例']`) }}
                    </template>
                </template>
            </bk-table-column>
            <bk-table-column prop="expired_dis" :label="$t(`m.common['到期时间']`)"></bk-table-column>
        </bk-table>
    </div>
</template>
<script>
    export default {
        props: {
            system: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
                renderPolicyList: [],
                sys: null
            }
        },
        watch: {
            system: {
                handler (v) {
                    this.sys = Object.assign({}, v || {})
                    this.renderPolicyList.splice(0, this.renderPolicyList.length, ...(v.policyList || []))
                    this.renderPolicyList.forEach(p => {
                        this.$nextTick(() => {
                            this.$refs.customTable && this.$refs.customTable.toggleRowSelection(p, !!p.transferChecked)
                        })
                    })
                },
                immediate: true,
                deep: true
            }
        },
        methods: {
            // handleCheckbox (row) {
            //     this.$emit('custom-selection-change', this.renderPolicyList)
            // },

            handleSelectionChange (selection) {
                console.warn(selection)
                // const validGroupList = this.renderPolicyList.filter(item => String(item.expired_at) !== '0')
                // this.isSelectAllChecked = selection.length === validGroupList.length
                // this.groupSelectData.splice(0, this.groupSelectData.length, ...selection)
                this.$emit('custom-selection-change', selection)
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
<style lang='postcss'>
    .my-perm-custom-perm-table {
        min-height: 101px;
    }
</style>
