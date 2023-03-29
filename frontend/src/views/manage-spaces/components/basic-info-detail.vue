<template>
    <div class="iam-grading-admin-basic-info-wrapper">
        <detail-layout mode="see">
            <render-layout>
                <detail-item :label="`${$t(`m.levelSpace['名称']`)}：`">
                    <iam-edit-input
                        field="name"
                        :mode="mode"
                        :placeholder="$t(`m.verify['请填写名称']`)"
                        :rules="rules"
                        :value="formData.name"
                        :remote-hander="handleUpdateRatingManager" />
                </detail-item>
                <detail-item :label="`${$t(`m.levelSpace['管理员']`)}：`">
                    <iam-edit-member
                        field="members"
                        :mode="mode"
                        :value="formData.members"
                        @on-change="handleUpdateMembers"
                        :remote-hander="handleUpdateRatingManager" />
                </detail-item>
                <detail-item :label="`${$t(`m.common['描述']`)}：`">
                    <iam-edit-textarea
                        field="description"
                        :mode="mode"
                        width="600px"
                        :max-length="100"
                        :value="formData.description"
                        :remote-hander="handleUpdateRatingManager" />
                </detail-item>
            </render-layout>
        </detail-layout>
    </div>
</template>
<script>
    import DetailLayout from '@/components/detail-layout';
    import DetailItem from '@/components/detail-layout/item';
    import IamEditInput from '@/components/iam-edit/input';
    import IamEditTextarea from '@/components/iam-edit/textarea';
    import RenderLayout from '@/views/group/common/render-layout';
    import IamEditMember from './iam-edit-member';

    export default {
        name: '',
        components: {
            DetailLayout,
            DetailItem,
            IamEditInput,
            IamEditTextarea,
            RenderLayout,
            IamEditMember
        },
        props: {
            data: {
                type: Object,
                default () {
                    return {};
                }
            },
            id: {
                type: [String, Number],
                default: ''
            },
            mode: {
                type: String,
                default: 'detail'
            }
        },
        data () {
            return {
                formData: {
                    name: '',
                    description: '',
                    members: [],
                    sync_perm: false
                }
            };
        },
        watch: {
            data: {
                handler (value) {
                    if (Object.keys(value).length) {
                        this.formData = Object.assign({}, value);
                        this.$store.commit('setHeaderTitle', this.formData.name);
                    }
                },
                immediate: true
            }
        },
        created () {
            this.rules = [
                {
                    required: true,
                    message: this.$t(`m.verify['请填写名称']`),
                    trigger: 'blur'
                },
                {
                    validator: (value) => {
                        return value.length <= 32;
                    },
                    message: this.$t(`m.verify['名称最长不超过32个字符']`),
                    trigger: 'blur'
                },
                {
                    validator: (value) => {
                        return /^[^\s]*$/g.test(value);
                    },
                    message: this.$t(`m.verify['名称不允许空格']`),
                    trigger: 'blur'
                }
            ];
        },
        methods: {
            handleUpdateRatingManager (payload) {
                const { name, members, description, sync_perm } = this.formData;
                const params = {
                    name,
                    description,
                    members,
                    sync_perm,
                    ...payload,
                    id: this.id
                };
                return this.$store.dispatch('spaceManage/updateSecondManagerManager', params)
                    .then(async () => {
                        this.messageSuccess(this.$t(`m.info['编辑成功']`), 2000);
                        const { name, description, members } = params;
                        // this.formData.name = params.name;
                        // this.formData.description = params.description;
                        // this.formData.members = [...params.members];
                        this.formData = Object.assign(this.formData, {
                            name,
                            description,
                            members,
                            sync_perm
                        });
                        const headerTitle = params.name;
                        this.$store.commit('setHeaderTitle', headerTitle);
                        await this.$store.dispatch('roleList');
                    }, (e) => {
                        console.warn('error');
                        this.bkMessageInstance = this.$bkMessage({
                            limit: 1,
                            theme: 'error',
                            message: e.message || e.data.msg || e.statusText
                        });
                    });
            },

            handleUpdateMembers (payload) {
                this.handleUpdateRatingManager(payload);
            }
        }
    };
</script>
<style lang="postcss">
    .iam-grading-admin-basic-info-wrapper {
        position: relative;
        top: -6px;
    }
</style>
