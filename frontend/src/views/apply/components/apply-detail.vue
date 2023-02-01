<template>
    <div class="iam-apply-detail-wrapper" v-bkloading="{ isLoading, opacity: 1, zIndex: 1000 }">
        <template v-if="isShowPage">
            <basic-info :data="basicInfo" />
            <perm-table
                :system="system"
                :data="tableList" />
            <render-process :link="basicInfo.ticket_url" />
            <div class="action" v-if="isShowAction">
                <bk-button :loading="loading" @click="handleCancel">{{ $t(`m.common['撤销']`) }}</bk-button>
            </div>
        </template>
        <template v-if="isEmpty">
            <div class="apply-content-empty-wrapper">
                <iam-svg />
            </div>
        </template>
    </div>
</template>
<script>
    import BasicInfo from './basic-info';
    import PermTable from './perm-table';
    import PermPolicy from '@/model/my-perm-policy';
    import RenderProcess from '../common/render-process';
    export default {
        name: '',
        components: {
            BasicInfo,
            PermTable,
            RenderProcess
        },
        props: {
            params: {
                type: Object,
                default: () => {
                    return {};
                }
            },
            loading: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                tableList: [],
                basicInfo: {},
                initRequestQueue: ['detail'],
                systemName: '',
                systemId: '',
                status: ''
            };
        },
        computed: {
            isLoading () {
                return this.initRequestQueue.length > 0;
            },
            isShowAction () {
                return this.status === 'pending';
            },
            isShowPage () {
                return !this.isLoading && this.tableList.length > 0;
            },
            isEmpty () {
                return !this.isLoading && this.tableList.length < 1;
            },
            system () {
                if (this.systemName !== '' && this.systemId !== '') {
                    return {
                        system_name: this.systemName,
                        system_id: this.systemId
                    };
                }
                return {};
            }
        },
        watch: {
            params: {
                handler (value) {
                    if (Object.keys(value).length > 0) {
                        this.initRequestQueue = ['detail'];
                        this.fetchData(value.id);
                    } else {
                        this.initRequestQueue = [];
                        this.status = '';
                        this.basicInfo = {};
                        this.tableList = [];
                        this.systemName = '';
                        this.systemId = '';
                    }
                },
                immediate: true
            }
        },
        methods: {
            async fetchData (id) {
                try {
                    const res = await this.$store.dispatch('myApply/getApplyDetail', { id });
                    const {
                        sn, type, applicant, organizations, reason, data,
                        status, created_time, ticket_url
                    } = res.data;
                    this.basicInfo = {
                        sn,
                        type,
                        organizations,
                        applicant,
                        reason,
                        created_time,
                        ticket_url,
                        applicants: data.applicants || []
                    };
                    this.systemName = data.system.name;
                    this.systemId = data.system.id;
                    this.status = status;
                    this.tableList = data.actions.map(item => new PermPolicy(item));
                } catch (e) {
                    console.error(e);
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText,
                        ellipsisLine: 2,
                        ellipsisCopy: true
                    });
                } finally {
                    this.initRequestQueue.shift();
                }
            },

            handleCancel () {
                this.$emit('on-cancel');
            }
        }
    };
</script>
<style lang="postcss" scoped>
    .iam-apply-detail-wrapper {
        height: calc(100vh - 121px);
        .action {
            padding-bottom: 50px;
        }
        .apply-content-empty-wrapper {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            img {
                width: 120px;
            }
        }
    }
</style>
