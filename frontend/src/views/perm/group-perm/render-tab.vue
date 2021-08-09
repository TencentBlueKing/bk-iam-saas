<template>
    <div :class="['iam-group-perm-sideslider-tab', extCls]">
        <section
            v-for="(item, index) in panels"
            :key="item.name"
            :class="['tab-item', { active: item.name === curActive }, { 'set-margin-left': index !== 0 }]"
            @click="handleChangeTab(item)">
            {{ item.label }}
        </section>
    </div>
</template>
<script>
    export default {
        name: '',
        props: {
            extCls: {
                type: String,
                default: ''
            },
            active: {
                type: String,
                default: 'perm'
            }
        },
        data () {
            return {
                panels: [
                    {
                        label: this.$t(`m.perm['组权限']`),
                        name: 'perm'
                    }
                    // {
                    //     label: this.$t(`m.userGroup['组成员']`),
                    //     name: 'member'
                    // }
                ],
                curActive: this.active
            }
        },
        watch: {
            active (value) {
                if (['perm', 'member'].includes(value)) {
                    this.curActive = value
                }
            }
        },
        methods: {
            handleChangeTab ({ name }) {
                this.curActive = name
                this.$emit('on-change', name)
                this.$emit('update:active', name)
            }
        }
    }
</script>
<style lang="postcss" scoped>
    .iam-group-perm-sideslider-tab {
        display: flex;
        justify-content: flex-start;
        padding: 0 20px;
        width: 100%;
        height: 42px;
        line-height: 42px;
        background: #fff;
        border-radius: 2px;
        box-shadow: 0px 1px 2px 0px rgba(247, 220, 220, .05);
        color: #63656e;
        .tab-item {
            font-size: 14px;
            cursor: pointer;
            &.active {
                color: #3a84ff;
                border-bottom: 2px solid #3a84ff;
            }
            &.set-margin-left {
                margin-left: 20px;
            }
        }
    }
</style>
