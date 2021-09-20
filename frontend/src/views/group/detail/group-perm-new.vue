<template>
    <div class="iam-user-group-perm-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
        <bk-button
            v-if="!isLoading && isEditMode"
            theme="primary"
            style="margin-bottom: 16px"
            @click="handleAddPerm">
            {{ $t(`m.common['添加权限']`) }}
        </bk-button>
        <template v-if="!isLoading && !isEmpty">
            <render-perm-item
                v-for="(item, index) in groupSystemList"
                :key="item.id"
                :expanded.sync="item.expanded"
                :ext-cls="index > 0 ? 'iam-perm-ext-cls' : ''"
                :class="index === groupSystemList.length - 1 ? 'iam-perm-ext-reset-cls' : ''"
                :title="item.name"
                :policy-count="item.custom_policy_count"
                :template-count="item.template_count"
                :group-system-list-length="groupSystemListLength"
                @on-expanded="handleExpanded(...arguments, item)">
                <div style="min-height: 60px;" v-bkloading="{ isLoading: item.loading, opacity: 1 }">
                    <div v-if="!item.loading">
                        <render-template-item
                            :ref="`rTemplateItem${item.id}`"
                            v-for="(subItem, subIndex) in item.templates"
                            :key="subIndex"
                            :title="subItem.name"
                            :count="subItem.count"
                            :is-edit="subItem.isEdit"
                            :loading="subItem.editLoading"
                            :expanded.sync="subItem.expanded"
                            :delete-loading="subItem.deleteLoading"
                            :policy-count="item.custom_policy_count"
                            :template-count="item.template_count"
                            :group-system-list-length="groupSystemListLength"
                            :mode="isEditMode ? 'edit' : 'detail'"
                            @on-delete="handleDelete(item, subItem)"
                            @on-save="handleSave(item, index, subItem, subIndex)"
                            @on-edit="handleEdit(subItem)"
                            @on-cancel="handleCancel(subItem)"
                            @on-expanded="handleTemplateExpanded(...arguments, subItem)">
                            <div style="min-height: 136px;"
                                v-bkloading="{ isLoading: subItem.loading, opacity: 1 }">
                                <resource-instance-table
                                    v-if="!subItem.loading"
                                    mode="detail"
                                    :is-custom="subItem.count > 0"
                                    :ref="`${index}_${subIndex}_resourceTableRef`"
                                    :list="subItem.tableData"
                                    :original-list="subItem.tableDataBackup"
                                    :authorization="authorizationData"
                                    :system-id="item.id"
                                    :group-id="groupId"
                                    :template-id="subItem.id"
                                    :is-edit="subItem.isEdit"
                                    @on-delete="handleSingleDelete(...arguments, item)" />
                            </div>
                        </render-template-item>
                    </div>
                </div>
            </render-perm-item>
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
    // import _ from 'lodash'
    import GroupPolicy from '@/model/group-policy'
    import RenderPermItem from '../common/render-perm-item-new'
    import RenderTemplateItem from '../common/render-template-item'
    import ResourceInstanceTable from '../components/render-instance-table'
    // import GroupAggregationPolicy from '@/model/group-aggregation-policy'
    // import store from '@/store'
    const CUSTOM_CUSTOM_TEMPLATE_ID = 0
    export default {
        name: '',
        components: {
            RenderPermItem,
            RenderTemplateItem,
            ResourceInstanceTable
        },
        props: {
            id: {
                type: [String, Number],
                default: ''
            },
            mode: {
                type: String,
                default: 'edit'
            }
        },
        data () {
            return {
                groupId: '',
                isLoading: false,
                groupSystemList: [],
                authorizationData: {},
                groupSystemListLength: '',
                removingSingle: false,
                isPermTemplateDetail: false,
                role: ''
            }
        },
        computed: {
            isEmpty () {
                return this.groupSystemList.length < 1
            },
            isEditMode () {
                return this.mode === 'edit'
            },
            expandedText () {
                return this.isAllExpanded ? this.$t(`m.grading['逐项编辑']`) : this.$t(`m.grading['批量编辑']`)
            }
        },
        watch: {
            id: {
                handler (value) {
                    this.groupId = value
                    this.handleInit()
                },
                immediate: true
            }
        },
        // created () {
        //     this.role = store.state.user.role.type
        //     if (this.$route.name === 'permTemplateDetail') {
        //         this.isPermTemplateDetail = true
        //     }
        // },
        methods: {
            async handleInit () {
                this.isLoading = true
                this.$emit('on-init', true)
                try {
                    const res = await this.$store.dispatch('userGroup/getGroupSystems', { id: this.groupId })
                    ;(res.data || []).forEach(item => {
                        item.expanded = false // 此处会在子组件更新为true
                        item.loading = false
                        item.templates = [] // 在getGroupTemplateList方法赋值
                    })
                    this.groupSystemList = res.data // groupSystemList会通过handleExpanded调用其他方法做属性的添加
                    this.groupSystemListLength = res.data.length
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.isLoading = false
                    this.$emit('on-init', false)
                }
            },

            handleAddPerm () {
                window.changeAlert = false
                this.$router.push({
                    name: 'addGroupPerm',
                    params: {
                        id: this.id
                    }
                })
            },

            handleEdit (paylaod) {
                this.$set(paylaod, 'isEdit', true) // 事件会冒泡会触发handleExpanded方法
            },

            handleCancel (paylaod) {
                this.$set(paylaod, 'isEdit', false)
            },

            async getGroupTemplateList (payload) {
                payload.loading = true
                let res
                try {
                    res = await this.$store.dispatch('userGroup/getUserGroupTemplateList', {
                        id: this.groupId,
                        systemId: payload.id
                    })
                    res.data.forEach(item => {
                        item.loading = false
                        item.tableData = []
                        item.tableDataBackup = []
                        item.count = 0
                        item.editLoading = false
                        item.deleteLoading = false
                    })
                    payload.templates = res.data // 赋值给展开项
                    if (payload.custom_policy_count) {
                        payload.templates.push({
                            name: this.$t(`m.perm['自定义权限']`),
                            id: CUSTOM_CUSTOM_TEMPLATE_ID,
                            system: {
                                id: payload.id,
                                name: payload.name
                            },
                            count: payload.custom_policy_count,
                            loading: false,
                            tableData: [],
                            tableDataBackup: [],
                            editLoading: false,
                            deleteLoading: false
                        })
                    }
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    payload.loading = false
                    if (res.data.length === 1) {
                        this.$nextTick(() => {
                            this.$refs[`rTemplateItem${payload.id}`][0].handleExpanded()
                        })
                    }
                }
            },

            handleExpanded (flag, item) {
                if (!flag) {
                    return
                }
                this.getGroupTemplateList(item)
                this.fetchAuthorizationScopeActions(item.id)
            },

            async fetchAuthorizationScopeActions (id) {
                if (this.authorizationData[id]) {
                    return
                }
                try {
                    const res = await this.$store.dispatch('permTemplate/getAuthorizationScopeActions', { systemId: id })
                    this.authorizationData[id] = res.data.filter(item => item.id !== '*')
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            /**
             * @description: 子item
             * @param {*} flag
             * @param {*} item
             * @return {*}
             */
            async handleTemplateExpanded (flag, item) {
                if (!flag) {
                    this.$set(item, 'isEdit', false)
                    return
                }
                if (item.count > 0) {
                    this.getGroupCustomPolicy(item)
                    return
                }
                this.getGroupTemplateDetail(item)
            },

            async getGroupTemplateDetail (item) {
                item.loading = true
                try {
                    const res = await this.$store.dispatch('userGroup/getGroupTemplateDetail', {
                        id: this.groupId,
                        templateId: item.id
                    })
                    const tableData = res.data.actions.map(row => new GroupPolicy(
                        { ...row, policy_id: 1 },
                        'detail',
                        'template',
                        { system: res.data.system }
                    ))
                    const tableDataBackup = res.data.actions.map(row => new GroupPolicy(
                        { ...row, policy_id: 1 },
                        'detail',
                        'template',
                        { system: res.data.system }
                    ))
                    this.$set(item, 'tableData', tableData)
                    this.$set(item, 'tableDataBackup', tableDataBackup)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    item.loading = false
                }
            },

            async getGroupCustomPolicy (item) {
                item.loading = true
                try {
                    const res = await this.$store.dispatch('userGroup/getGroupPolicy', {
                        id: this.groupId,
                        systemId: item.system.id
                    })

                    const tableData = res.data.map(row => {
                        return new GroupPolicy(
                            row,
                            'detail', // 此属性为flag，会在related-resource-types赋值为add
                            'custom',
                            { system: item.system }
                        )
                    })
                    const tableDataBackup = res.data.map(row => new GroupPolicy(
                        row,
                        'detail',
                        'custom',
                        { system: item.system }
                    ))
                    this.$set(item, 'tableData', tableData)
                    this.$set(item, 'tableDataBackup', tableDataBackup)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    item.loading = false
                }
            },

            async handleSave (item, index, subItem, subIndex) {
                const $ref = this.$refs[`${index}_${subIndex}_resourceTableRef`][0]
                const { flag, actions } = $ref.getDataByNormal()
                if (flag) {
                    return
                }
                subItem.editLoading = true
                try {
                    await this.$store.dispatch('userGroup/updateGroupPolicy', {
                        id: this.groupId,
                        data: {
                            system_id: item.id,
                            template_id: subItem.id,
                            actions
                        }
                    })
                    if (subItem.count > 0) {
                        this.getGroupCustomPolicy(subItem)
                    } else {
                        this.getGroupTemplateDetail(subItem)
                    }
                    subItem.isEdit = false
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    subItem.editLoading = false
                }
            },
            handleDelete (item, subItem) {
                this.removingSingle = false
                if (subItem.id > 0) {
                    this.deleteTempalte({
                        id: subItem.id,
                        data: {
                            members: [{
                                type: 'group',
                                id: this.groupId
                            }]
                        }
                    }, item, subItem)
                } else {
                    this.deleteGroupPolicy({
                        id: this.groupId,
                        data: {
                            system_id: item.id,
                            ids: subItem.tableData.map(item => item.policy_id).join(',')
                        }
                    }, item, subItem, true)
                }
            },

            async deleteTempalte (params = {}, item, subItem) {
                subItem.deleteLoading = true
                try {
                    await this.$store.dispatch('permTemplate/deleteTemplateMember', params)
                    let filterLen = item.templates.filter(item => item.id !== CUSTOM_CUSTOM_TEMPLATE_ID).length
                    const isExistCustom = item.templates.some(item => item.id === CUSTOM_CUSTOM_TEMPLATE_ID)
                    if (filterLen > 0) {
                        --filterLen
                        --item.template_count
                    }
                    if (filterLen > 0 || isExistCustom) {
                        this.getGroupTemplateList(item)
                    }
                    if (!filterLen && !isExistCustom) {
                        this.handleInit()
                    }
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    subItem.deleteLoading = false
                }
            },

            async deleteGroupPolicy (params = {}, item, subItem, flag) {
                if (flag) {
                    subItem.deleteLoading = true
                }
                try {
                    await this.$store.dispatch('userGroup/deleteGroupPolicy', params)
                    const isExistTemplate = item.templates.some(item => item.id !== CUSTOM_CUSTOM_TEMPLATE_ID)
                    if (item.custom_policy_count > 0 && this.removingSingle) {
                        --item.custom_policy_count
                    } else {
                        item.custom_policy_count = 0
                    }
                    this.policyList = subItem
                    if (isExistTemplate) {
                        this.getGroupTemplateList(item)
                    } else {
                        this.handleInit()
                    }
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    if (flag) {
                        subItem.deleteLoading = false
                    }
                }
            },

            handleSingleDelete (data, item) {
                this.removingSingle = true
                this.deleteGroupPolicy({
                    id: this.groupId,
                    data: {
                        system_id: item.id,
                        ids: data.policy_id
                    }
                }, item, {}, false)
            }
        }
    }
</script>
<style lang="postcss">
    .iam-user-group-perm-wrapper {
        position: relative;
        min-height: calc(100vh - 145px);
        .iam-perm-ext-cls {
            margin-top: 10px;
        }
        .iam-perm-ext-reset-cls {
            margin-bottom: 20px;
        }
        .empty-wrapper {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            img {
                width: 160px;
            }
            .text {
                position: relative;
                top: -30px;
                font-size: 12px;
                color: #979ba5;
                text-align: center;
            }
        }
        .info-wrapper {
                display: flex;
                justify-content: flex-end;
                line-height: 24px;
                .tips,
                .text {
                    line-height: 20px;
                    font-size: 12px;
                }
            }
    }
</style>
