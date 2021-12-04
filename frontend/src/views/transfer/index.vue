<template>
    <div class="iam-transfer-wrapper">
        <Group @group-selection-change="handleGroupSelection" />

        <Custom />
        <!-- <div style="background: red; height: 800px;"></div> -->
        <div class="fixed-action" style="height: 50px;" :style="{ paddingLeft: fixedActionPaddingLeft }">
            <bk-button theme="primary" @click="submit">
                {{ $t(`m.common['提交']`) }}
            </bk-button>
        </div>
    </div>
</template>
<script>
    import { bus } from '@/common/bus'

    import Group from './group.vue'
    import Custom from './custom.vue'

    export default {
        name: '',
        components: {
            Group,
            Custom
        },
        data () {
            return {
                fixedActionPaddingLeft: '284px',
                groupSelectData: []
            }
        },
        created () {
        },
        mounted () {
            bus.$on('nav-resize', flag => {
                if (flag) {
                    this.fixedActionPaddingLeft = '284px'
                } else {
                    this.fixedActionPaddingLeft = '84px'
                }
            })
        },
        methods: {
            handleGroupSelection (list) {
                this.groupSelectData.splice(0, this.groupSelectData.length, ...list)
            },
            submit () {
                console.error(this.groupSelectData)
            }
        }
    }
</script>
<style lang="postcss">
    @import './index.css';
</style>
