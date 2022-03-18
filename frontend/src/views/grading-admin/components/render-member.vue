<template>
    <render-horizontal-block
        :label="$t(`m.grading['最大可授权人员范围']`)">
        <section class="action-wrapper" @click.stop="handleAddMember" data-test-id="grading_btn_showAddMember">
            <Icon bk type="plus-circle-shape" />
            <span>{{ $t(`m.grading['选择可授权人员范围']`) }}</span>
        </section>
        <Icon
            type="info-fill"
            class="info-icon"
            v-bk-tooltips.top="{ content: tips, width: 236, extCls: 'iam-tooltips-cls' }" />
        <div style="margin-top: 9px;" v-if="isAll">
            <div class="all-item">
                <span class="member-name">{{ $t(`m.common['全员']`) }}</span>
                <span class="display-name">(All)</span>
                <Icon type="close-fill" class="remove-icon" @click="handleDelete" />
            </div>
        </div>
        <template v-else>
            <render-member-item :data="users" @on-delete="handleDeleteUser" v-if="isHasUser" />
            <render-member-item :data="departments" type="department" v-if="isHasDepartment"
                @on-delete="handleDeleteDepartment" />
        </template>
    </render-horizontal-block>
</template>
<script>
    import RenderMemberItem from '../../group/common/render-member-display'
    export default {
        name: '',
        components: {
            RenderMemberItem
        },
        props: {
            users: {
                type: Array,
                default: () => []
            },
            departments: {
                type: Array,
                default: () => []
            },
            isAll: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                tips: this.$t(`m.grading['添加成员提示']`)
            }
        },
        computed: {
            isHasUser () {
                return this.users.length > 0
            },
            isHasDepartment () {
                return this.departments.length > 0
            }
        },
        methods: {
            handleAddMember () {
                this.$emit('on-add')
            },

            handleDeleteUser (payload) {
                this.$emit('on-delete', 'user', payload)
            },

            handleDeleteDepartment (payload) {
                this.$emit('on-delete', 'department', payload)
            },

            handleDelete () {
                this.$emit('on-delete-all')
            }
        }
    }
</script>
<style lang="postcss" scoped>
    .action-wrapper {
        margin-left: 8px;
        display: inline-block;
        font-size: 14px;
        color: #3a84ff;
        cursor: pointer;
        &:hover {
            color: #699df4;
        }
        i {
            position: relative;
            top: -1px;
            left: 2px;
        }
    }
    .info-icon {
        color: #c4c6cc;
        &:hover {
            color: #3a84ff;
        }
    }
    .all-item {
        position: relative;
        display: inline-block;
        margin: 0 6px 6px 10px;
        padding: 0 10px;
        line-height: 22px;
        background: #f5f6fa;
        border: 1px solid #dcdee5;
        border-radius: 2px;
        font-size: 14px;
        &:hover {
            .remove-icon {
                display: block;
            }
        }
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
        .display_name {
            display: inline-block;
            vertical-align: top;
        }
        .remove-icon {
            display: none;
            position: absolute;
            top: -6px;
            right: -6px;
            cursor: pointer;
        }
    }
</style>
