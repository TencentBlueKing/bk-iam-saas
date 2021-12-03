<template>
    <div class="iam-transfer-wrapper">
        <PersonalGroup @personal-group-selection-change="handlePersonalGroupSelection" />
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

    import PersonalGroup from './personal-group.vue'

    export default {
        name: '',
        components: {
            PersonalGroup
        },
        data () {
            return {
                fixedActionPaddingLeft: '284px',
                personalGroupSelectData: []
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
            handlePersonalGroupSelection (list) {
                this.personalGroupSelectData.splice(0, this.personalGroupSelectData.length, ...list)
            },
            submit () {
                console.error(this.personalGroupSelectData)
            }
        }
    }
</script>
<style lang="postcss">
    @import './index.css';
</style>
