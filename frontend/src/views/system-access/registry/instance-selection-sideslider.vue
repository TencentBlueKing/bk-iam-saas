<template>
  <bk-sideslider
    :is-show="isShow"
    :quick-close="false"
    :width="720"
    ext-cls="resource-type-sideslider"
    :title="$t(`m.access['新增实例视图']`)"
    @update:isShow="hideSideslider">
    <div slot="content" class="content-wrapper" v-bkloading="{ isLoading, opacity: 1 }">
      <template>
        <div id="container-pop">
          <pop-content
            :title="$t(`m.access['什么是实例视图？']`)"
            :desc="$t(`m.access['实例视图代表一种资源类型的实例数据获取途径，一种资源类型的实例视图可以有多种。']`)"
            :image="imageInfo"
          ></pop-content>
        </div>
        <Icon class="icon-info-instance" type="info-new" v-bk-tooltips="htmlConfig" />
      </template>
      <div class="add-resource-type-form-wrapper" v-if="!isLoading">
        <div
          v-for="(item, index) in instanceSelectionList"
          :key="index"
          :class="['action-item', 'set-border', { 'reset-padding-top': index === 0 }]">
          <p class="title-wrapper" @click.stop="handleExpanded(item)">
            <section class="action-group-name">
              <Icon :type="item.expanded ? 'down-angle' : 'right-angle'" />
              <span class="name">{{ item.title || $t(`m.access['新增实例视图']`)}}</span>
            </section>
          </p>
          <div v-if="item.expanded" :class="['btn-wrapper', { 'reset-top': index === 0 }]">
            <template v-if="!item.isEdit">
              <!-- "item.isEdit = true" -->
              <bk-button size="small" @click="editInstanceSelection(item)">
                {{ $t(`m.common['编辑']`) }}
              </bk-button>
              <bk-button size="small" theme="danger" outline :disabled="item.submitLoading"
                @click.stop.prevent="delInstanceSelection(item, index)">
                {{ $t(`m.common['删除']`) }}
              </bk-button>
            </template>
            <template v-else>
              <bk-button size="small" :disabled="item.submitLoading" theme="primary"
                @click.stop.prevent="saveInstanceSelection(item, index)">
                {{ $t(`m.common['保存']`) }}
              </bk-button>
              <bk-button size="small" :disabled="item.submitLoading"
                @click.stop.prevent="cancelEdit(index)">{{ $t(`m.common['取消']`) }}</bk-button>
            </template>
          </div>
          <div class="action-content" v-if="item.expanded">
            <div class="sub-group-action-content">
              <bk-form :ref="`instanceSelectionForm${index}`"
                :model="item" form-type="vertical" :rules="rules"
                v-bkloading="{ isLoading: item.submitLoading, opacity: 1, color: '#f5f6fa' }">
                <iam-form-item :label="$t(`m.access['实例视图ID']`)" :property="'id'" required
                  :desc="$t(`m.access['实例视图的唯一标识']`)">
                  <bk-input :disabled="!item.isNewAdd" v-model="item.id"
                    :placeholder="$t(`m.access['请输入实例视图ID']`)" />
                </iam-form-item>
                <iam-form-item :label="$t(`m.access['实例视图中文名']`)" :property="'name'" required>
                  <bk-input :disabled="!item.isEdit" v-model="item.name"
                    :placeholder="$t(`m.access['请输入实例视图中文名']`)" />
                </iam-form-item>
                <iam-form-item :label="$t(`m.access['实例视图英文名']`)" :property="'name_en'" required>
                  <bk-input :disabled="!item.isEdit" v-model="item.name_en"
                    :placeholder="$t(`m.access['请输入实例视图英文名']`)" />
                </iam-form-item>
                <iam-form-item class="resource-type-chain-form-item"
                  :label="$t(`m.access['选择资源实例层级']`)" required>
                  <div v-for="(chain, chainIndex) in item.resource_type_chain"
                    :key="chainIndex" class="resource-type-chain-wrapper">
                    <iam-cascade
                      :disabled="!item.isEdit"
                      class="resource-type-chain"
                      v-model="chain.chainValue"
                      :list="systemList"
                      :is-remote="true"
                      :remote-method="fetchResourceTypeListBySystem"
                      :separator="' > '"
                      clearable
                      :dropdown-content-cls="'system-access-cascade-dropdown-content'"
                      :placeholder="$t(`m.access['请选择资源实例层级']`)"
                      :empty-text="$t(`m.access['无匹配数据']`)"
                      @change="handleCascadeChange(item, chain, ...arguments)">
                    </iam-cascade>
                    <!-- <template v-if="item.isEdit">
                                            <iam-cascade
                                                class="resource-type-chain"
                                                v-model="chain.chainValue"
                                                :list="systemList"
                                                :is-remote="true"
                                                :remote-method="fetchResourceTypeListBySystem"
                                                :separator="' > '"
                                                clearable
                                                :dropdown-content-cls="'system-access-cascade-dropdown-content'"
                                                :placeholder="$t(`m.access['请选择资源实例层级']`)"
                                                :empty-text="$t(`m.access['无匹配数据']`)"
                                                @change="handleCascadeChange(item, chain, ...arguments)">
                                            </iam-cascade>
                                        </template>
                                        <template v-else>
                                            <div class="resource-type-chain-text">
                                                {{chain.system_name}} > {{chain.name}}
                                            </div>
                                        </template> -->

                    <div class="resource-type-chain-icon-wrapper"
                      :class="!item.isEdit ? 'disabled' : ''"
                      @click="delChain(item, index, chainIndex)">
                      <Icon type="close-small" class="icon" />
                    </div>
                    <span class="split">/</span>
                  </div>
                  <div class="resource-type-chain-icon-wrapper"
                    :class="!item.isEdit ? 'disabled' : ''" @click="addChain(item)">
                    <Icon type="add-small" class="icon" />
                  </div>
                  <p class="error" v-if="item.chainError">{{$t(`m.access['资源实例层级必选']`)}}</p>
                </iam-form-item>
              </bk-form>
            </div>
          </div>
        </div>
        <section class="add-btn" @click="add">
          <Icon bk type="plus-circle-shape" />
          <span>{{ $t(`m.access['新增实例视图']`) }}</span>
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
    // eslint-disable-next-line no-unused-vars
    // import { leaveConfirm } from '@/common/leave-confirm'
  import iamCascade from '@/components/cascade';
  import PopContent from '../common/pop-content';
  import hostImage from '@/images/business-host.png';
  import dynamicsImage from '@/images/business-dynamics.png';

  const getDefaultData = () => ({
    id: '',
    name: '',
    name_en: '',
    resource_type_chain: [{ system_id: '', id: '' }],
    expanded: true,
    title: '',
    isEdit: true,
    submitLoading: false,
    // 添加了还未保存的
    isNewAdd: true,
    chainError: false
  });

  export default {
    components: {
      iamCascade,
      PopContent
    },
    props: {
      isShow: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        isLoading: false,
        instanceSelectionList: [],
        instanceSelectionListBackup: [],

        systemList: [],
        alreadySelecteds: {},
        htmlConfig: {
          allowHtml: true,
          width: 520,
          trigger: 'click',
          theme: 'light',
          content: '#container-pop',
          placement: 'right-start'
        },
        imageInfo: [{ name: '业务主机列表', imageSrc: hostImage }, { name: '业务动态分组列表', imageSrc: dynamicsImage }]
      };
    },
    computed: {
      modelingId () {
        return this.$route.params.id;
      }
    },
    watch: {
      isShow: {
        async handler (value) {
          if (value) {
            this.rules = {
              id: [
                { required: true, message: this.$t(`m.verify['实例视图ID必填']`), trigger: 'blur' },
                {
                  max: 32,
                  message: '不能多于32个字符',
                  trigger: 'blur'
                },
                { regex: /^[a-z][a-z-z0-9_-]*$/, message: this.$t(`m.verify['只允许小写字母开头、包含小写字母、数字、下划线(_)和连接符(-)']`), trigger: 'blur' }
              ],
              name: [
                { required: true, message: this.$t(`m.verify['实例视图中文名称必填']`), trigger: 'blur' }
              ],
              name_en: [
                { required: true, message: this.$t(`m.verify['实例视图英文名称必填']`), trigger: 'blur' },
                { regex: /^[a-zA-Z0-9,.!?\s_]*$/, message: this.$t(`m.verify['只允许输入英文']`), trigger: 'blur' }
              ]
            };

            this.isLoading = true;

            try {
              await Promise.all([
                this.fetchSystemList(),
                this.fetchInstanceSelection()
              ]);
            } catch (e) {
              console.error(e);
              this.bkMessageInstance = this.$bkMessage({
                limit: 1,
                theme: 'error',
                message: e.message || e.data.msg || e.statusText
              });
            } finally {
              this.isLoading = false;
            }
          } else {
            window.changeAlert = this.pageChangeAlertMemo;
          }
        },
        immediate: true
      }
    },
    methods: {
      /**
       * 校验实例视图ID唯一性
       */
      async checkName (val) {
        try {
          const res = await this.$store.dispatch('access/checkResourceId', {
            id: this.modelingId,
            data: {
              type: 'instance_selection',
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
       * addChain
       */
      addChain (item) {
        if (!item.isEdit) {
          return;
        }
        item.resource_type_chain.push({ system_id: '', id: '', chainValue: [] });
      },

      /**
       * 111
       */
      delChain (item, itemIndex, chainIndex) {
        if (!item.isEdit) {
          return;
        }
        if (item.resource_type_chain.length === 1) {
          this.messageError(this.$t(`m.access['至少要有一个资源实例层级']`), 1000);
          return;
        }

        const resourceTypeChain = [];
        resourceTypeChain.splice(0, 0, ...item.resource_type_chain);
        resourceTypeChain.splice(chainIndex, 1);

        item.resource_type_chain = JSON.parse(JSON.stringify(resourceTypeChain));
      },

      /**
       * fetchSystemList
       */
      async fetchSystemList () {
        try {
          const res = await this.$store.dispatch('access/getSystemList', {
            id: this.modelingId
          });
          const systemList = [];
          const list = res.data || [];
          list.forEach(item => {
            systemList.push({
              id: item[0],
              name: item[1],
              // TODO: cascade/caspanel.vue 的 handleItemFn 使用。目的是不允许选中第一层节点中没有子层级的节点，暂时先这么实现
              parent: true
            });
          });
          this.systemList.splice(0, this.systemList.length, ...systemList);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      /**
       * fetchResourceTypeListBySystem
       */
      async fetchResourceTypeListBySystem (sys, resolve) {
        if (sys.isLoading === false) {
          resolve(sys);
          return;
        }
        this.$set(sys, 'isLoading', true);
        try {
          const res = await this.$store.dispatch('access/getResourceTypeListBySystem', {
            id: this.modelingId,
            data: {
              system_id: sys.id
            }
          });
          const list = [];
          res.data.forEach(item => {
            list.push({
                            ...item,
                            isLoading: false
            });
          });
          sys.children = list;
          resolve(sys);
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      /**
       * handleCascadeChange
       */
      handleCascadeChange (item, chain, newValue) {
        item.chainError = false;
        chain.system_id = chain.chainValue[0];
        // 只有一层的情况
        chain.id = chain.chainValue[1] || chain.chainValue[0];
      },

      /**
       * fetchInstanceSelection
       */
      async fetchInstanceSelection () {
        try {
          const resModeling = await this.$store.dispatch('access/getModeling', {
            id: this.modelingId,
            data: {
              type: 'instance_selection'
            }
          });

          const preloadResourceTypeListBySys = [];
          const preloadResourceTypeListBySysParams = [];

          const instanceSelectionList = [];
          instanceSelectionList.splice(0, 0, ...(resModeling.data || []));
          if (!instanceSelectionList.length) {
            instanceSelectionList.push(getDefaultData());
          } else {
            instanceSelectionList.forEach(item => {
              item.expanded = false;
              item.title = item.name;
              item.isEdit = false;
              item.submitLoading = false;
              item.isNewAdd = false;
              item.chainError = false;
              item.resource_type_chain.forEach(c => {
                c.chainValue = [c.system_id, c.id];

                // preloadResourceTypeListBySysParams 和 preloadResourceTypeListBySys 的顺序是一致的
                preloadResourceTypeListBySysParams.push(c.system_id);
                preloadResourceTypeListBySys.push(this.$store.dispatch('access/getResourceTypeListBySystem', {
                  id: this.modelingId,
                  data: {
                    system_id: c.system_id
                  }
                }));
              });
            });
          }
          if (preloadResourceTypeListBySys.length) {
            const resArr = await Promise.all(preloadResourceTypeListBySys);
            resArr.forEach((res, index) => {
              const curSysData = this.systemList.find(
                sys => sys.id === preloadResourceTypeListBySysParams[index]
              );
              if (curSysData) {
                curSysData.children = [];
                (res.data || []).forEach(d => {
                  curSysData.children.push({
                                        ...d,
                                        isLoading: false
                  });
                });
              }
            });
          }

          this.instanceSelectionList.splice(0, this.instanceSelectionList.length, ...instanceSelectionList);
          this.instanceSelectionListBackup = JSON.parse(JSON.stringify(instanceSelectionList));
        } catch (e) {
          console.error(e);
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || e.data.msg || e.statusText,
            ellipsisLine: 2,
            ellipsisCopy: true
          });
        }
      },

      /**
       * saveInstanceSelection
       */
      saveInstanceSelection (item, index) {
        const formComp = this.$refs[`instanceSelectionForm${index}`];
        if (formComp && formComp[0]) {
          item.chainError = item.resource_type_chain.every(item => !item.id);
          if (item.chainError) {
            return;
          }
          formComp[0].validate().then(async validator => {
            const resourceTypeChain = [];
            item.resource_type_chain.forEach(c => {
              resourceTypeChain.push({
                id: c.id,
                system_id: c.system_id
              });
            });
            try {
              item.submitLoading = true;
              await this.$store.dispatch('access/updateModeling', {
                id: this.modelingId,
                data: {
                  type: 'instance_selection',
                  data: {
                    id: item.id,
                    name: item.name,
                    name_en: item.name_en,
                    resource_type_chain: resourceTypeChain
                  }
                }
              });
              item.title = item.name;
              item.isEdit = false;
              item.isNewAdd = false;
              this.messageSuccess(this.$t(`m.access['保存实例视图成功']`), 1000);
              this.$emit('on-refresh-system-list', 'instanceSelection');
              this.addValidatorRules(); // 保存成功重新添加规则
            } catch (e) {
              console.error(e);
              this.bkMessageInstance = this.$bkMessage({
                limit: 1,
                theme: 'error',
                message: e.message || e.data.msg || e.statusText
              });
            } finally {
              item.submitLoading = false;
              this.instanceSelectionListBackup = JSON.parse(JSON.stringify(this.instanceSelectionList));
            }
          }, validator => {
            console.warn(validator);
          });
        }
      },

      /**
       * delInstanceSelection
       */
      async delInstanceSelection (item, index) {
        const directive = {
          name: 'bkTooltips',
          content: item.name,
          placement: 'right'
        };
        const me = this;
        me.$bkInfo({
          title: me.$t(`m.access['确认删除下列实例视图？']`),
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
                  type: 'instance_selection'
                }
              });

              const instanceSelectionList = [];
              instanceSelectionList.splice(0, 0, ...me.instanceSelectionList);
              instanceSelectionList.splice(index, 1);
              me.instanceSelectionList.splice(
                0,
                me.instanceSelectionList.length,
                ...instanceSelectionList
              );

              me.messageSuccess(me.$t(`m.access['删除实例视图成功']`), 1000);
              this.$emit('on-refresh-system-list', 'instanceSelection');
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
              me.instanceSelectionListBackup = JSON.parse(JSON.stringify(me.instanceSelectionList));
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
        const instanceSelectionList = [];
        instanceSelectionList.splice(0, 0, ...(this.instanceSelectionList));
        instanceSelectionList.push(getDefaultData());
        this.instanceSelectionList.splice(0, this.instanceSelectionList.length, ...instanceSelectionList);
        this.instanceSelectionListBackup = JSON.parse(JSON.stringify(instanceSelectionList));
      },

      /**
       * addValidatorRules
       */
      addValidatorRules () {
        const dynamicValidatorRulesLength = this.rules.id.filter(e => e.type === 'dynamicValidator').length;
        if (!dynamicValidatorRulesLength) {
          this.rules.id.push({ type: 'dynamicValidator', validator: this.checkName, message: this.$t(`m.verify['实例视图ID已被占用']`), trigger: 'blur' }); // 需要添加是否被占用规则
        }
      },

      /**
       * cancelEdit
       */
      cancelEdit (index) {
        const formComp = this.$refs[`instanceSelectionForm${index}`];
        if (formComp && formComp[0]) {
          formComp[0].clearError();
        }
        this.addValidatorRules();
        const curItem = this.instanceSelectionList[index];
        // 如果是未保存过的，那么取消的时候直接删除
        if (curItem.isNewAdd) {
          const instanceSelectionList = [];
          instanceSelectionList.splice(0, 0, ...this.instanceSelectionList);
          instanceSelectionList.splice(index, 1);
          this.instanceSelectionList.splice(0, this.instanceSelectionList.length, ...instanceSelectionList);
        } else {
          const originalExpanded = curItem.expanded;
          const originalItem = Object.assign({}, this.instanceSelectionListBackup[index]);
          originalItem.isEdit = false;
          originalItem.expanded = originalExpanded;
          this.$set(this.instanceSelectionList, index, originalItem);
        }
      },

      /**
       * hideSideslider
       */
      hideSideslider () {
        const invalidItemList = this.instanceSelectionList.filter(item => item.isEdit && !item.isNewAdd);
        if (invalidItemList.length) {
          this.$bkInfo({
            title: this.$t(`m.access['请先保存下列实例视图？']`),
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

        // let cancelHandler = Promise.resolve()
        // if (window.changeAlert) {
        //     cancelHandler = leaveConfirm()
        // }
        // cancelHandler.then(() => {
        //     this.$emit('update:isShow', false)
        //     this.$emit('on-cancel')
        // }, _ => _)
      },

      /**
       * handleExpanded
       */
      handleExpanded (item) {
        // window.changeAlert = true
        item.expanded = !item.expanded;
      }
    }
  };
</script>

<style lang="postcss">
    @import './resource-type-sideslider.css';
</style>
