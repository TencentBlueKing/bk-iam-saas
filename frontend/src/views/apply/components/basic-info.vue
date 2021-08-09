<template>
    <div :class="[
        'iam-apply-basic-info-wrapper',
        { 'is-en-large': !curLanguageIsCn && isShowExpired },
        { 'is-en-middle': !curLanguageIsCn && !isShowExpired }
    ]">
        <div class="title">{{ $t(`m.common['基本信息']`) }}</div>
        <div class="item">
            <label class="label">{{ $t(`m.myApply['申请单号']`) }}：</label>
            <div class="content">{{ data.sn }}</div>
        </div>
        <div class="item">
            <label class="label">{{ $t(`m.myApply['申请类型']`) }}：</label>
            <div class="content">{{ getApplyTypeDisplay(data.type) }}</div>
        </div>
        <div class="item">
            <label class="label">{{ $t(`m.myApply['申请人']`) }}：</label>
            <div class="content">{{ data.applicant }}</div>
        </div>
        <div class="item" v-if="isShowExpired">
            <label class="label">{{ $t(`m.common['申请期限']`) }}：</label>
            <div class="content">{{ data.expiredDisplay }}</div>
        </div>
        <div class="item">
            <label class="label">{{ $t(`m.myApply['申请时间']`) }}：</label>
            <div class="content">{{ data.created_time }}</div>
        </div>
        <div class="item">
            <label class="label">{{ $t(`m.myApply['所在组织']`) }}：</label>
            <div class="content">
                <template v-if="isHasOrg">
                    <p v-for="(org, orgIndex) in data.organizations" :key="orgIndex">{{ org.full_name }}</p>
                </template>
                <template v-else>--</template>
            </div>
        </div>
        <div class="item">
            <label class="label">{{ $t(`m.common['理由']`) }}：</label>
            <div class="content" :title="data.reason !== '' ? data.reason : ''">{{ data.reason || '--' }}</div>
        </div>
    </div>
</template>
<script>
    export default {
        name: '',
        props: {
            /**
             * data props
             */
            data: {
                type: Object,
                default: () => {
                    return {}
                }
            },
            /**
             * isShowExpired props
             */
            isShowExpired: {
                type: Boolean,
                default: false
            }
        },
        computed: {
            /**
             * isHasOrg
             */
            isHasOrg () {
                return this.data.organizations && this.data.organizations.length > 0
            }
        },
        methods: {
            /**
             * getApplyTypeDisplay
             */
            getApplyTypeDisplay (payload) {
                let str = ''
                switch (payload) {
                    case 'grant_action':
                        str = this.$t(`m.myApply['自定义权限申请']`)
                        break
                    case 'renew_action':
                        str = this.$t(`m.myApply['自定义权限申请']`)
                        break
                    case 'join_group':
                        str = this.$t(`m.myApply['加入用户组']`)
                        break
                    case 'renew_group':
                        str = this.$t(`m.myApply['加入用户组']`)
                        break
                    case 'create_rating_manager':
                        str = this.$t(`m.myApply['创建分级管理员']`)
                        break
                    case 'update_rating_manager':
                        str = this.$t(`m.myApply['编辑分级管理员']`)
                        break
                    default:
                        str = ''
                }

                return str
            }
        }
    }
</script>
<style lang="postcss" scoped>
    @import './basic-info.css';
</style>
