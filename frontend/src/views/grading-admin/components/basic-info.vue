<template>
    <div class="iam-grading-admin-basic-info-wrapper">
        <bk-form
            :model="formData"
            form-type="vertical"
            ref="basicInfoForm">
            <iam-form-item :label="$t(`m.grading['分级管理员名称']`)" required>
                <bk-input
                    :value="formData.name"
                    style="width: 450px;"
                    clearable
                    :placeholder="$t(`m.verify['请输入']`)"
                    :ext-cls="isShowNameError ? 'group-name-error' : ''"
                    data-test-id="grading_input_name"
                    @input="handleNameInput"
                    @blur="handleNameBlur"
                    @change="handleNameChange" />
                <p class="name-empty-error" v-if="isShowNameError">{{ nameValidateText }}</p>
            </iam-form-item>
            <iam-form-item :label="$t(`m.set['成员列表']`)" required>
                <bk-user-selector
                    :value="formData.members"
                    :api="userApi"
                    :placeholder="$t(`m.verify['请输入']`)"
                    style="width: 100%;"
                    :class="isShowMemberError ? 'is-member-empty-cls' : ''"
                    data-test-id="grading_userSelector_member"
                    @focus="handleRtxFocus"
                    @blur="handleRtxBlur"
                    @change="handleRtxChange">
                </bk-user-selector>
                <p class="name-empty-error" v-if="isShowMemberError">{{ $t(`m.verify['请选择成员']`) }}</p>
            </iam-form-item>
            <iam-form-item :label="$t(`m.common['描述']`)">
                <bk-input :value="formData.description"
                    type="textarea" maxlength="255"
                    data-test-id="grading_input_desc"
                    @change="handleDescChange" />
            </iam-form-item>
        </bk-form>
    </div>
</template>
<script>
    import BkUserSelector from '@blueking/user-selector'
    const getDefaultData = () => ({
        name: '',
        description: '',
        members: []
    })

    export default {
        name: '',
        components: {
            BkUserSelector
        },
        props: {
            data: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                formData: getDefaultData(),
                isShowNameError: false,
                isShowMemberError: false,
                nameValidateText: '',
                userApi: window.BK_USER_API
            }
        },
        watch: {
            data: {
                handler (value) {
                    if (Object.keys(value).length) {
                        const { name, description, members } = value
                        this.formData = Object.assign({}, {
                            name,
                            description,
                            members
                        })
                    }
                },
                deep: true,
                immediate: true
            }
        },
        methods: {
            handleRtxFocus () {
                this.isShowMemberError = false
            },

            handleRtxBlur () {
                this.isShowMemberError = this.formData.members.length < 1
            },

            handleNameInput (payload) {
                this.isShowNameError = false
                this.nameValidateText = ''
            },

            handleNameBlur (payload) {
                const maxLength = 32
                if (payload === '') {
                    this.nameValidateText = this.$t(`m.verify['分级管理员名称必填']`)
                    this.isShowNameError = true
                }
                if (!this.isShowNameError) {
                    if (payload.trim().length > maxLength) {
                        this.nameValidateText = this.$t(`m.verify['分级管理员名称最长不超过32个字符']`)
                        this.isShowNameError = true
                    }
                    if (!/^[^\s]*$/g.test(payload)) {
                        this.nameValidateText = this.$t(`m.verify['分级管理员名称不允许空格']`)
                        this.isShowNameError = true
                    }
                }
            },

            handleRtxChange (payload) {
                this.isShowMemberError = false
                this.$emit('on-change', 'members', payload)
            },

            handleNameChange (value) {
                this.formData.name = value
                this.$emit('on-change', 'name', value)
            },

            handleDescChange (value) {
                this.formData.description = value
                this.$emit('on-change', 'description', value)
            },

            submit () {
                return this.$refs.basicInfoForm.validate().then(validator => {
                    return Promise.resolve(this.formData)
                }, validator => {
                    return Promise.reject(validator.content)
                })
            },

            handleValidator () {
                const maxLength = 32
                const { name, members } = this.formData
                if (name === '') {
                    this.nameValidateText = this.$t(`m.verify['分级管理员名称必填']`)
                    this.isShowNameError = true
                }
                if (!this.isShowNameError) {
                    if (name.trim().length > maxLength) {
                        this.nameValidateText = this.$t(`m.verify['分级管理员名称最长不超过32个字符']`)
                        this.isShowNameError = true
                    }
                    if (!/^[^\s]*$/g.test(name)) {
                        this.nameValidateText = this.$t(`m.verify['分级管理员名称不允许空格']`)
                        this.isShowNameError = true
                    }
                }

                this.isShowMemberError = members.length < 1

                return this.isShowNameError || this.isShowMemberError
            },

            reset () {
                this.$refs.basicInfoForm.formItems.forEach(item => {
                    item.validator.content = ''
                    item.validator.state = ''
                })
            }
        }
    }
</script>
<style lang="postcss">
    .iam-grading-admin-basic-info-wrapper {
        position: relative;
        top: -6px;
        .group-name-error {
            .bk-form-input {
                border-color: #ff5656;
            }
        }
        .name-empty-error {
            font-size: 12px;
            color: #ff4d4d;
        }
        .is-member-empty-cls {
            .user-selector-container {
                border-color: #ff4d4d;
            }
        }
    }
</style>
