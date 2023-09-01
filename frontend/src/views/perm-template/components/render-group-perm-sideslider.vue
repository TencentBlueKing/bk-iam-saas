<template>
  <bk-sideslider
    ext-cls="iam-template-group-perm-slider"
    :is-show.sync="visible"
    :width="960"
    :quick-close="true"
    @update:isShow="handleClose">
    <div slot="header">
      <p>{{ $t(`m.perm['组权限']`) }}</p>
      <p class="group-id">ID: {{ groupId }}</p>
    </div>
    <div slot="content" style="padding: 20px;" v-bkloading="{ isLoading, opacity: 1 }">
      <div class="iam-user-group-perm-wrapper">
        <template v-if="!isLoading && !isEmpty">
          <render-perm-item
            v-for="(item, index) in groupSystemList"
            :key="item.id"
            :expanded.sync="item.expanded"
            :ext-cls="index > 0 ? 'iam-perm-ext-cls' : ''"
            :class="index === groupSystemList.length - 1 ? 'iam-perm-ext-reset-cls' : ''"
            :title="item.name"
            :policy-count="item.custom_policy_count"
            :template-count="item.template_count"
            :group-system-list-length="groupSystemListLength"
            :external-custom="externalSystemsLayout.userGroup.groupDetail.hideCustomPerm"
            @on-expanded="handleExpanded(...arguments, item)">
            <div style="min-height: 60px;"
              v-bkloading="{ isLoading: item.loading, opacity: 1 }">
              <div v-if="!item.loading">
                <render-template-item
                  :ref="`rTemplateItem${item.id}`"
                  v-for="(subItem, subIndex) in item.templates"
                  :key="subIndex"
                  :title="subItem.name"
                  :count="subItem.count"
                  :expanded.sync="subItem.expanded"
                  :policy-count="item.custom_policy_count"
                  :template-count="item.template_count"
                  :group-system-list-length="groupSystemListLength"
                  mode="detail"
                  @on-expanded="handleTemplateExpanded(...arguments, subItem)">
                  <div style="min-height: 136px;"
                    v-bkloading="{ isLoading: subItem.loading, opacity: 1 }">
                    <resource-instance-table
                      v-if="!subItem.loading"
                      mode="detail"
                      type="view"
                      :is-custom="subItem.count > 0"
                      :ref="`${index}_${subIndex}_resourceTableRef`"
                      :list="subItem.tableData"
                      :system-id="item.id"
                      :template-id="subItem.id" />
                  </div>
                </render-template-item>
              </div>
            </div>
          </render-perm-item>
        </template>
        <template v-if="!isLoading && isEmpty">
          <div class="empty-wrapper">
            <ExceptionEmpty
              :type="emptyData.type"
              :empty-text="emptyData.text"
              :tip-text="emptyData.tip"
              :tip-type="emptyData.tipType"
              @on-refresh="handleEmptyRefresh"
            />
          </div>
        </template>
      </div>
    </div>
  </bk-sideslider>
</template>
<script>
  import Policy from '@/model/policy';
  import RenderPermItem from '@/views/group/common/render-perm-item-new';
  import RenderTemplateItem from '@/views/group/common/render-template-item';
  import ResourceInstanceTable from '@/views/group/components/render-instance-table';
  import { formatCodeData } from '@/common/util';
  import { mapGetters } from 'vuex';

  const CUSTOM_CUSTOM_TEMPLATE_ID = 0;
  export default {
    name: '',
    components: {
      RenderPermItem,
      RenderTemplateItem,
      ResourceInstanceTable
    },
    props: {
      isShow: {
        type: Boolean,
        default: false
      },
      groupId: {
        type: [String, Number],
        default: ''
      }
    },
    data () {
      return {
        visible: false,
        isLoading: false,
        groupSystemList: [],
        groupSystemListLength: '',
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        }
      };
    },
    computed: {
            ...mapGetters(['externalSystemsLayout', 'externalSystemId']),
            isEmpty () {
                return this.groupSystemList.length < 1;
            }
    },
    watch: {
      isShow: {
        handler (value) {
          this.visible = !!value;
          if (this.visible) {
            this.handleInit();
          }
        },
        immediate: true
      }
    },
    methods: {
      handleClose () {
        this.$emit('update:isShow', false);
      },

      async handleInit () {
        this.isLoading = true;
        try {
          const params = {
            id: this.groupId
          };
          if (this.externalSystemId) {
            params.hidden = false;
          }
          const { code, data } = await this.$store.dispatch('userGroup/getGroupSystems', params);
          (data || []).forEach(item => {
            item.expanded = false;
            item.loading = false;
            item.templates = [];
          });
          this.groupSystemList = data;
          this.groupSystemListLength = data.length;
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      async getGroupTemplateList (payload) {
        payload.loading = true;
        let res;
        try {
          res = await this.$store.dispatch('userGroup/getUserGroupTemplateList', {
            id: this.groupId,
            systemId: payload.id
          });
          const { code, data } = res;
          data.forEach(item => {
            item.loading = false;
            item.tableData = [];
            item.count = 0;
          });
          payload.templates = [...data];
          if (payload.custom_policy_count
            && !this.externalSystemsLayout.userGroup.groupDetail.hideCustomPerm) {
            payload.templates.push({
              name: this.$t(`m.perm['自定义权限']`),
              id: CUSTOM_CUSTOM_TEMPLATE_ID,
              system: {
                id: payload.id,
                name: payload.name
              },
              count: payload.custom_policy_count,
              loading: false,
              tableData: []
            });
          }
          this.emptyData = formatCodeData(code, this.emptyData, data.length === 0);
        } catch (e) {
          console.error(e);
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          payload.loading = false;
          if (res.data.length === 1) {
            this.$nextTick(() => {
              this.$refs[`rTemplateItem${payload.id}`][0].handleExpanded();
            });
          }
        }
      },

      handleExpanded (flag, item) {
        if (!flag) {
          return;
        }
        this.getGroupTemplateList(item);
      },

      async handleTemplateExpanded (flag, item) {
        if (!flag) {
          return;
        }
        if (item.count > 0) {
          this.getGroupCustomPolicy(item);
          return;
        }
        this.getGroupTemplateDetail(item);
      },

      async getGroupTemplateDetail (item) {
        item.loading = true;
        try {
          const res = await this.$store.dispatch('userGroup/getGroupTemplateDetail', {
            id: this.groupId,
            templateId: item.id
          });
          // // mock数据
          // res.data.actions.forEach((element, index) => {
          //     element.resource_groups = [{
          //         id: index,
          //         related_resource_types: element.related_resource_types
          //     }]
          // })
          const tableData = res.data.actions.map(item => new Policy({ ...item, policy_id: 1, mode: 'template' }, 'detail'));
          this.$set(item, 'tableData', tableData);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          item.loading = false;
        }
      },

      async getGroupCustomPolicy (item) {
        item.loading = true;
        try {
          const res = await this.$store.dispatch('userGroup/getGroupPolicy', {
            id: this.groupId,
            systemId: item.system.id
          });
          // // mock数据
          // res.data.forEach((element, index) => {
          //     element.resource_groups = [{
          //         id: index,
          //         related_resource_types: element.related_resource_types
          //     }]
          // })
          const tableData = res.data.map(item => new Policy({ ...item, mode: 'custom' }, 'detail'));
          this.$set(item, 'tableData', tableData);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          item.loading = false;
        }
      }
    }
  };
</script>
<style lang="postcss">
    .iam-template-group-perm-slider {
        .group-id {
            position: relative;
            top: -12px;
            line-height: 0;
            font-size: 12px;
            color: #c4c6cc;
        }
        .iam-user-group-perm-wrapper {
            position: relative;
            min-height: calc(100vh - 101px);
            .iam-perm-ext-cls {
                margin-top: 10px;
            }
            .iam-perm-ext-reset-cls {
                margin-bottom: 20px;
            }
            .empty-wrapper {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                img {
                    width: 160px;
                }
            }
        }
    }
</style>
