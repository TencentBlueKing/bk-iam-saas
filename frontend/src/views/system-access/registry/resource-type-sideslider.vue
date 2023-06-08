<template>
  <bk-sideslider
    :is-show="isShow"
    :quick-close="false"
    :width="720"
    ext-cls="resource-type-sideslider"
    :title="$t(`m.access['新增资源类型']`)"
    @update:isShow="hideSideslider">
    <div slot="content" class="content-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
      <div class="add-resource-type-form-wrapper" v-if="!isLoading">
        <div
          v-for="(item, index) in resourceTypeList"
          :key="index"
          :class="['action-item', 'set-border', { 'reset-padding-top': index === 0 }]">
          <p class="title-wrapper" @click.stop="handleExpanded(item)">
            <section class="action-group-name">
              <Icon :type="item.expanded ? 'down-angle' : 'right-angle'" />
              <span class="name">{{ item.title || $t(`m.access['新增资源类型']`)}}</span>
            </section>
          </p>
          <div v-if="item.expanded" :class="['btn-wrapper', { 'reset-top': index === 0 }]">
            <template v-if="!item.isEdit">
              <bk-button size="small" @click="editInstanceSelection(item)">
                {{ $t(`m.common['编辑']`) }}
              </bk-button>
              <bk-button size="small" theme="danger" outline :disabled="item.submitLoading"
                @click.stop.prevent="delResourceType(item, index)">
                {{ $t(`m.common['删除']`) }}
              </bk-button>
            </template>
            <template v-else>
              <bk-button size="small" :disabled="item.submitLoading" theme="primary"
                @click.stop.prevent="saveResourceType(item, index)">
                {{ $t(`m.common['保存']`) }}
              </bk-button>
              <bk-button size="small" :disabled="item.submitLoading"
                @click.stop.prevent="cancelEdit(index)">
                {{ $t(`m.common['取消']`) }}
              </bk-button>
            </template>
          </div>
          <div class="action-content" v-if="item.expanded">
            <div class="sub-group-action-content">
              <bk-form :ref="`resourceTypeForm${index}`" :model="item" form-type="vertical" :rules="rules"
                v-bkloading="{ isLoading: item.submitLoading, opacity: 1, color: '#f5f6fa' }">
                <iam-form-item :label="$t(`m.access['资源类型ID']`)" :property="'id'" required
                  :desc="$t(`m.access['资源类型的唯一标识']`)">
                  <bk-input :disabled="!item.isNewAdd" v-model="item.id"
                    :placeholder="$t(`m.access['请输入资源类型ID']`)" />
                </iam-form-item>
                <iam-form-item :label="$t(`m.access['资源类型中文名']`)" :property="'name'" required
                  :desc="$t(`m.access['资源类型的名称']`)">
                  <bk-input :disabled="!item.isEdit" v-model="item.name"
                    :placeholder="$t(`m.access['请输入资源类型中文名']`)" />
                </iam-form-item>
                <iam-form-item :label="$t(`m.access['资源类型英文名']`)" :property="'name_en'" required>
                  <bk-input :disabled="!item.isEdit" v-model="item.name_en"
                    :placeholder="$t(`m.access['请输入资源类型英文名']`)" />
                </iam-form-item>
                <iam-form-item :label="$t(`m.access['回调接口']`)" :property="'provider_config.path'"
                  required :desc="$t(`m.access['权限中心会通过该接口拉取对应资源类型的实例数据']`)">
                  <bk-input :disabled="!item.isEdit" v-model="item.provider_config.path"
                    :placeholder="$t(`m.access['请输入回调接口']`)">
                    <template slot="prepend">
                      <div class="group-text">{{$store.state.host}}</div>
                    </template>
                  </bk-input>
                </iam-form-item>
              </bk-form>
            </div>
          </div>
        </div>
        <section class="add-btn" @click="add">
          <Icon bk type="plus-circle-shape" />
          <span>{{ $t(`m.access['新增资源类型']`) }}</span>
        </section>
      </div>
    </div>
    <div slot="footer" style="padding-left: 22px;">
      <bk-button theme="primary" @click="hideSideslider">{{ $t(`m.common['确定']`) }}</bk-button>
      <bk-button @click="hideSideslider">{{ $t(`m.common['取消']`) }}</bk-button>
    </div>
  </bk-sideslider>
</template>

<script>
    /**
     * 获取 default data
     */
  const getDefaultData = () => ({
    id: '',
    name: '',
    name_en: '',
    provider_config: {
      path: ''
    },
    expanded: true,
    title: '',
    isEdit: true,
    submitLoading: false,
    // 添加了还未保存的
    isNewAdd: true
  });

  export default {
    props: {
      isShow: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isLoading: false,
        resourceTypeList: [],
        resourceTypeListBackup: []
      };
    },
    computed: {
      /**
       * modelingId
       */
      modelingId () {
        return this.$route.params.id;
      }
    },
    watch: {
      /**
       * isShow
       */
      isShow: {
        async handler (value) {
          // 侧边栏开启时设置 form rules
          if (value) {
            this.rules = {
              id: [
                { required: true, message: this.$t(`m.verify['资源类型ID必填']`), trigger: 'blur' },
                {
                  max: 32,
                  message: '不能多于32个字符',
                  trigger: 'blur'
                },
                { regex: /^[a-z][a-z-z0-9_-]*$/, message: this.$t(`m.verify['只允许小写字母开头、包含小写字母、数字、下划线(_)和连接符(-)']`), trigger: 'blur' }
              ],
              name: [
                { required: true, message: this.$t(`m.verify['资源类型中文名必填']`), trigger: 'blur' }
              ],
              name_en: [
                { required: true, message: this.$t(`m.verify['资源类型英文名必填']`), trigger: 'blur' },
                { regex: /^[a-zA-Z0-9,.!?\s_]*$/, message: this.$t(`m.verify['只允许输入英文']`), trigger: 'blur' }
              ],
              'provider_config.path': [
                { required: true, message: this.$t(`m.verify['回调接口必填']`), trigger: 'blur' },
                { regex: /^(\/[A-Za-z0-9_-]+(\/?))+$/, message: this.$t(`m.verify['请输入正确的系统回调接口']`), trigger: 'blur' }

              ]
            };
            this.isLoading = true;
            await this.fetchResourceType();
          } else {
            window.changeAlert = this.pageChangeAlertMemo;
          }
        },
        immediate: true
      }
    },
    methods: {
      /**
       * 获取资源类型数据
       */
      async fetchResourceType () {
        try {
          const res = await this.$store.dispatch('access/getModeling', {
            id: this.modelingId,
            data: {
              type: 'resource_type'
            }
          });
          const resourceTypeList = [];
          resourceTypeList.splice(0, 0, ...(res.data || []));
          if (!resourceTypeList.length) {
            resourceTypeList.push(getDefaultData());
          } else {
            resourceTypeList.forEach(item => {
              item.expanded = false;
              item.title = item.name;
              item.isEdit = false;
              item.submitLoading = false;
              item.isNewAdd = false;
            });
          }
          this.resourceTypeList.splice(0, this.resourceTypeList.length, ...resourceTypeList);
          this.resourceTypeListBackup = JSON.parse(JSON.stringify(resourceTypeList));
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
          this.isLoading = false;
        }
      },

      /**
       * 校验资源类型ID唯一性
       */
      async checkName (val) {
        try {
          const res = await this.$store.dispatch('access/checkResourceId', {
            id: this.modelingId,
            data: {
              type: 'resource_type',
              id: val.trim()

            }
          });
          return !res.data.exists;
        } catch (e) {
          console.error(e);
          return false;
        }
      },

      /**
       * 保存资源类型
       */
      saveResourceType (item, index) {
        const formComp = this.$refs[`resourceTypeForm${index}`];
        if (formComp && formComp[0]) {
          formComp[0].validate().then(async validator => {
            try {
              this.rules.id = this.rules.id.filter(t => t.type !== 'dynamicValidator'); // 校验通过重置规则
              item.submitLoading = true;
              await this.$store.dispatch('access/updateModeling', {
                id: this.modelingId,
                data: {
                  type: 'resource_type',
                  data: {
                    id: item.id,
                    name: item.name,
                    name_en: item.name_en,
                    provider_config: {
                      path: item.provider_config.path
                    }
                  }
                }
              });
              item.title = item.name;
              item.isEdit = false;
              item.isNewAdd = false;
              this.messageSuccess(this.$t(`m.access['保存资源类型成功']`), 1000);
              this.$emit('on-refresh-system-list', 'resourceType');
              this.addValidatorRules();
            } catch (e) {
              console.error(e);
              this.bkMessageInstance = this.$bkMessage({
                limit: 1,
                theme: 'error',
                message: e.message || e.data.msg || e.statusText
              });
            } finally {
              item.submitLoading = false;
              this.resourceTypeListBackup = JSON.parse(JSON.stringify(this.resourceTypeList));
            }
          }, validator => {
            console.warn(validator);
          });
        }
      },

      /**
       * 删除资源类型
       */
      async delResourceType (item, index) {
        const directive = {
          name: 'bkTooltips',
          content: item.name,
          placement: 'right'
        };
        const me = this;
        me.$bkInfo({
          title: this.$t(`m.access['确认删除下列资源类型？']`),
          confirmLoading: true,
          subHeader: (
                        <div class="add-resource-type-warn-info">
                            <p>
                                <span title={ item.name } v-bk-tooltips={ directive }>{ item.name }</span>
                            </p>
                        </div>
                    ),
          confirmFn: async () => {
            try {
              item.submitLoading = true;
              await me.$store.dispatch('access/deleteModeling', {
                id: me.modelingId,
                data: {
                  id: item.id,
                  type: 'resource_type'
                }
              });

              const resourceTypeList = [];
              resourceTypeList.splice(0, 0, ...me.resourceTypeList);
              resourceTypeList.splice(index, 1);
              me.resourceTypeList.splice(0, me.resourceTypeList.length, ...resourceTypeList);

              me.messageSuccess(me.$t(`m.access['删除资源类型成功']`), 1000);
              this.$emit('on-refresh-system-list', 'resourceType');
              return true;
            } catch (e) {
              console.error(e);
              me.bkMessageInstance = me.$bkMessage({
                limit: 1,
                theme: 'error',
                message: e.message || e.data.msg || e.statusText
              });
              return false;
            } finally {
              item.submitLoading = false;
              me.resourceTypeListBackup = JSON.parse(JSON.stringify(me.resourceTypeList));
            }
          }
        });
      },

      /**
       * edit
       */
      editInstanceSelection (item) {
        item.isEdit = true;
        this.rules.id = this.rules.id.filter(t => t.type !== 'dynamicValidator'); // 编辑时实例ID不可编辑不校验规则
      },

      /**
       * add
       */
      add () {
        this.addValidatorRules();
        const resourceTypeList = [];
        resourceTypeList.splice(0, 0, ...(this.resourceTypeList));
        resourceTypeList.push(getDefaultData());
        this.resourceTypeList.splice(0, this.resourceTypeList.length, ...resourceTypeList);
        this.resourceTypeListBackup = JSON.parse(JSON.stringify(resourceTypeList));
      },

      /**
       * addValidatorRules
       */
      addValidatorRules () {
        const dynamicValidatorRulesLength = this.rules.id.filter(e => e.type === 'dynamicValidator').length;
        if (!dynamicValidatorRulesLength) {
          this.rules.id.push({ type: 'dynamicValidator', validator: this.checkName, message: this.$t(`m.verify['资源类型ID已被占用']`), trigger: 'blur' }); // 需要添加是否被占用规则
        }
      },

      /**
       * 取消编辑
       */
      cancelEdit (index) {
        const formComp = this.$refs[`resourceTypeForm${index}`];
        if (formComp && formComp[0]) {
          formComp[0].clearError();
        }
        this.addValidatorRules();
        const curItem = this.resourceTypeList[index];
        // 如果是未保存过的，那么取消的时候直接删除
        if (curItem.isNewAdd) {
          const resourceTypeList = [];
          resourceTypeList.splice(0, 0, ...this.resourceTypeList);
          resourceTypeList.splice(index, 1);
          this.resourceTypeList.splice(0, this.resourceTypeList.length, ...resourceTypeList);
        } else {
          const originalExpanded = curItem.expanded;
          const originalItem = Object.assign({}, this.resourceTypeListBackup[index]);
          originalItem.isEdit = false;
          originalItem.expanded = originalExpanded;
          this.$set(this.resourceTypeList, index, originalItem);
        }
      },

      /**
       * 隐藏侧边栏
       */
      hideSideslider () {
        const invalidItemList = this.resourceTypeList.filter(item => item.isEdit && !item.isNewAdd);
        if (invalidItemList.length) {
          this.$bkInfo({
            title: this.$t(`m.access['请先保存下列资源类型']`),
            subHeader: (
                            <div class="add-resource-type-warn-info">
                                {
                                    invalidItemList.map(invalidItem => {
                                        const directive = {
                                            name: 'bkTooltips',
                                            content: invalidItem.name,
                                            placement: 'right'
                                        };
                                        return (
                                            <p>
                                                <span title={ invalidItem.name } v-bk-tooltips={ directive }>
                                                    { invalidItem.name }
                                                </span>
                                            </p>
                                        );
                                    })
                                }
                            </div>
                        )
          });
          return;
        }
        this.$emit('update:isShow', false);
        this.$emit('on-cancel');
      },

      /**
       * 展开
       */
      handleExpanded (item) {
        item.expanded = !item.expanded;
      }
    }
  };
</script>

<style lang="postcss">
    @import './resource-type-sideslider.css';
</style>
