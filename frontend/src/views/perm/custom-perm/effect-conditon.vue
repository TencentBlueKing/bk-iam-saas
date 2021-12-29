<template>
    <div class="iam-effect-condition"
        @click.stop="handleClick">
        <span class="text">{{ curValue }}</span>
    </div>
</template>
<script>
    export default {
        name: '',
        props: {
            value: {
                type: Array,
                default: []
            },
            isEmpty: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                curValue: '',
                isActive: false,
                immediatelyShow: false,
                effectWeekList: {
                    1: '每周一',
                    2: '每周二',
                    3: '每周三',
                    4: '每周四',
                    5: '每周五',
                    6: '每周六',
                    0: '每周日'
                },
                effectWeekTimeZone: {
                    'Asia/Shanghai': '(GMT+08:00)'
                },
                effectType: {
                    'period_daily': '时间'
                }
            }
        },
        computed: {},
        watch: {
            value: {
                handler (val) {
                    console.log('val111', val)
                    if (this.isEmpty) {
                        this.curValue = '时间: 在每天 00:00:00 - 23:59:59(GMT+08:00)时间生效'
                    } else {
                        this.curValue = val.reduce((p, v) => {
                            let curValue = ''
                            let weekCopy = ''
                            curValue = v.condition.reduce((prev, item) => {
                                let hms = ''
                                let tz = ''
                                let weekday = ''
                                if (item.type === 'weekday') {
                                    weekday = item.values.reduce((pre, e) => {
                                        pre = `${pre} ${this.effectWeekList[e.value]}`
                                        return pre
                                    }, '')
                                    weekCopy = weekday
                                }

                                if (item.type === 'hms') {
                                    hms = item.values.reduce((pre, e) => {
                                        if (pre) {
                                            pre = `${pre} - ${e.value}`
                                        } else {
                                            pre = `${pre} ${e.value}`
                                        }
                                        
                                        return pre
                                    }, '')
                                }

                                if (item.type === 'tz') {
                                    tz = item.values.reduce((pre, e) => {
                                        pre = this.effectWeekTimeZone[e.value]
                                        return pre
                                    }, '')
                                }

                                prev = `${prev}${hms}${tz}${weekday}`
                                return prev
                            }, '')
                            p = `${this.effectType[v.type]}: ${p}${weekCopy ? '' : '每天'}${curValue}${this.effectType[v.type]}生效`
                            return p
                        }, '在')
                    }
                },
                immediate: true
            }
        },
        methods: {

            handleClick () {
                if (this.isDisabled) {
                    return
                }
                this.$emit('on-click')
            }
        }
    }
</script>
<style lang="postcss" scoped>
    .iam-effect-condition {
        position: relative;
        color: #63656e;
        cursor: pointer;
        margin: 20px !important;
        
        &:hover {
            border-color: #3a84ff;
            .operate-icon {
                display: inline-block;
            }
        }
        &.active {
            border-color: #3a84ff;
        }
        &.error {
            border-color: #ff5656;
        }

        .text {
            /* display: inline-block; */
            overflow: hidden;
            /* text-overflow: ellipsis;
            white-space: nowrap;
            vertical-align: middle; */
            height: 30px;
            line-height: 30px;
        }
    }
</style>
