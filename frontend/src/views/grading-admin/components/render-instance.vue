<template>
  <div class="iam-grade-admin-select-wrapper">
    <div class="action">
      <section class="action-wrapper" @click.stop="handleSelect">
        <Icon bk type="plus-circle-shape" />
        <span>{{ $t(`m.grading['选择操作和资源实例范围']`) }}</span>
      </section>
      <Icon
        type="info-fill"
        class="info-icon"
        v-bk-tooltips.top="{ content: tips, width: 236, extCls: 'iam-tooltips-cls' }" />
    </div>
    <div class="info-wrapper">
      <p class="tips">{{ infoText }}</p>
      <section style="min-width: 108px;">
        <bk-switcher
          v-model="isAllExpanded"
          :disabled="isAggregateDisabled"
          size="small"
          theme="primary"
          @change="handleAggregateAction" />
        <span class="text">{{ expandedText }}</span>
      </section>
    </div>
    <div class="resource-instance-wrapper"
      v-bkloading="{ isLoading, opacity: 1, extCls: 'loading-resource-instance-cls' }">
      <render-instance-table
        ref="resourceInstanceRef"
        :data="policyList"
        :list="policyList"
        @on-delete="handleDelete" />
    </div>
  </div>
</template>
<script>
  import _ from 'lodash';
  import GradeAggregationPolicy from '@/model/grade-aggregation-policy';
  import GradePolicy from '@/model/grade-policy';
  import Condition from '@/model/condition';
  import RenderInstanceTable from './render-instance-table';
  export default {
    name: '',
    components: {
      RenderInstanceTable
    },
    props: {
      data: {
        type: Array,
        default: () => []
      },
      originalData: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        infoText: this.$t(`m.grading['选择提示']`),
        tips: this.$t(`m.grading['添加操作提示']`),
        policyList: [],
        isLoading: false,

        // 默认开始为展开态
        isAllExpanded: true,
        aggregationMap: [],
        aggregations: [],
        aggregationsBackup: [],
        aggregationsTableData: [],
        curSystemId: []
      };
    },
    computed: {
      expandedText () {
        return this.isAllExpanded ? this.$t(`m.grading['逐项编辑']`) : this.$t(`m.grading['展开选择']`);
      },
      isAggregateDisabled () {
        return this.policyList.length < 1
          || this.aggregations.length < 1
          || (this.policyList.length === 1 && !this.policyList[0].isAggregate);
      }
    },
    watch: {
      originalData: {
        handler (value) {
          if (value.length > 0) {
            this.policyList = value.map(item => new GradePolicy(item));
            const params = [...new Set(this.policyList.map(item => item.system_id))];
            // 无新增的的系统时无需请求聚合数据
            const difference = params.filter(item => !this.curSystemId.includes(item));
            if (difference.length > 0) {
              this.curSystemId = [...this.curSystemId.concat(difference)];
              this.resetData();
              if (this.policyList.length > 1) {
                this.fetchAggregationAction(this.curSystemId.join(','));
              }
            } else {
              const data = this.getFilterAggregation(this.aggregationsBackup);
              this.aggregations = _.cloneDeep(data);
            }
          }
        },
        immediate: true
      }
    },
    methods: {
      async fetchAggregationAction (payload) {
        this.isLoading = true;
        try {
          const res = await this.$store.dispatch('aggregate/getAggregateAction', { system_ids: payload });
          const data = this.getFilterAggregation(res.data.aggregations);
          this.aggregationsBackup = _.cloneDeep(res.data.aggregations);
          this.aggregations = _.cloneDeep(data);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          this.isLoading = false;
        }
      },

      getFilterAggregation (payload) {
        const curSelectActions = this.policyList.map(item => `${item.system_id}&${item.id}`);
        const aggregations = []
        ;(payload || []).forEach(item => {
          const { actions, aggregate_resource_type } = item;
          const curActions = actions.filter(_ => curSelectActions.includes(`${aggregate_resource_type.system_id}&${_.id}`));
          if (curActions.length > 0) {
            aggregations.push({
              actions: curActions,
              aggregate_resource_type: Object.assign(aggregate_resource_type, {
                system_name: this.policyList.find(
                  _ => _.system_id === aggregate_resource_type.system_id
                ).system_name
              })
            });
          }
        });
        return aggregations;
      },

      resetData () {
        this.aggregationMap = [];
        this.aggregations = [];
        this.aggregationsBackup = [];
        this.aggregationsTableData = [];
      },

      handleAggregateAction (payload) {
        const aggregationAction = this.aggregations;
        const actionIds = [];
        aggregationAction.forEach(item => {
          actionIds.push(...item.actions.map(_ => `${item.aggregate_resource_type.system_id}&${_.id}`));
        });
        if (!payload) {
          const aggregateArr = [];
          const isHasAggregate = this.aggregationMap.length > 0;
          if (isHasAggregate) {
            for (let k = 0; k < aggregationAction.length; k++) {
              aggregateArr[k] = [];
              const item = aggregationAction[k];
              const filterArray = this.policyList.filter(subItem => item.actions.map(_ => `${item.aggregate_resource_type.system_id}&${_.id}`).includes(`${subItem.system_id}&${subItem.id}`));
              // 缓存新增加的操作权限数据
              const addArray = filterArray.filter(subItem => !this.aggregationsTableData.map(_ => `${_.system_id}&${_.id}`).includes(`${subItem.system_id}&${subItem.id}`));
              if (addArray.length > 0) {
                this.aggregationsTableData.push(...addArray);
              }
              const temAction = filterArray.map(sub => {
                const { id, name, system_id } = sub;
                const curCondition = sub.related_resource_types[0].condition;
                return {
                  id,
                  system_id,
                  name,
                  condition: curCondition.map(v => {
                    const obj = {};
                    if (v.hasOwnProperty('instance')) {
                      obj.instances = _.cloneDeep(v.instance);
                    }
                    if (v.hasOwnProperty('attribute')) {
                      obj.attributes = _.cloneDeep(v.attribute);
                    }
                    return obj;
                  }).filter(_ => Object.keys(_).length > 0)
                };
              });
              for (let i = 0; i < temAction.length; i++) {
                for (let j = i + 1; j < temAction.length; j++) {
                  const origin = temAction[i];
                  const target = temAction[j];
                  // const originObj = {
                  //     expired_at: origin.expired_at,
                  //     expired_display: origin.expired_display,
                  //     condition: origin.condition.map(item => {
                  //         if (item.attributes && item.attributes.length < 1) {
                  //             delete item.attributes
                  //         }
                  //         return item
                  //     })
                  // }
                  // const targetObj = {
                  //     expired_at: target.expired_at,
                  //     expired_display: target.expired_display,
                  //     condition: target.condition.map(item => {
                  //         if (item.attributes && item.attributes.length < 1) {
                  //             delete item.attributes
                  //         }
                  //         return item
                  //     })
                  // }
                  // if (_.isEqual(originObj, targetObj)) {
                  //     aggregateArr[k].push(origin)
                  //     aggregateArr[k].push(target)
                  // }
                  aggregateArr[k].push(_.cloneDeep(origin));
                  aggregateArr[k].push(_.cloneDeep(target));
                }
              }
            }
          }
          // aggregateArr 去重
          const tempAggregateArr = [];
          aggregateArr.forEach((item, index) => {
            tempAggregateArr[index] = [];
            item.forEach(subItem => {
              if (!tempAggregateArr[index].map(v => `${v.system_id}&${v.id}`).includes(`${subItem.system_id}&${subItem.id}`)) {
                tempAggregateArr[index].push(subItem);
              }
            });
          });
          const practicalAggregationAction = isHasAggregate ? aggregationAction.filter((item, index) => {
            return tempAggregateArr[index].length > 0;
          }) : aggregationAction;
          const tempActionIds = [];
          practicalAggregationAction.forEach(item => {
            tempActionIds.push(...item.actions.map(_ => `${item.aggregate_resource_type.system_id}&${_.id}`));
          });
          const aggregations = practicalAggregationAction.filter(item => {
            const target = item.actions.map(v => v.id).sort();
            const existData = this.policyList.find(subItem => {
              return subItem.isAggregate && _.isEqual(target, subItem.actions.map(v => v.id).sort());
            });
            return !existData;
          }).map((item, index) => {
            if (isHasAggregate) {
              const curData = tempAggregateArr[index];
              const actionDifference = item.actions.map(_ => `${item.aggregate_resource_type.system_id}&${_.id}`).filter(_ => !curData.map(sub => `${sub.system_id}&${sub.id}`).includes(_));
              tempActionIds.push(...actionDifference);
              const isAllEqualFlag = (() => {
                let isAllEqual = true;
                for (let i = 0; i < curData.length; i++) {
                  if (i !== curData.length - 1) {
                    const target = curData[i].condition;
                    const origin = curData[i + 1].condition;
                    if (!_.isEqual(target, origin) || target.length < 1 || origin.length < 1) {
                      isAllEqual = false;
                      break;
                    }
                  }
                }
                return isAllEqual;
              })();
              // console.warn('curData[0]: ')
              // console.warn(curData[0])
              // item.isRemoteSucceed = true
              // const tempObj = curData.find(_ => _.tag === 'add')
              // if (tempObj) {
              //     item.expired_at = tempObj.expired_at
              //     item.expired_display = tempObj.expired_display || this.$t(`m.common['6个月']`)
              // } else {
              //     item.expired_at = curData[0].expired_at
              //     item.expired_display = curData[0].expired_display || this.$t(`m.common['6个月']`)
              // }
              if (isAllEqualFlag) {
                // const tempObj = curData.find(_ => _.tag === 'add')
                // if (tempObj) {
                //     item.expired_at = tempObj.expired_at
                //     item.expired_display = tempObj.expired_display
                // } else {
                //     item.expired_at = curData[0].expired_at
                //     item.expired_display = curData[0].expired_display
                // }
                if (curData[0].condition.length > 0 && item.tag === 'add') {
                  const pathData = curData[0].condition[0].instances[0].path;
                  item.instances = pathData.map(v => {
                    return {
                      id: v[0].id,
                      name: v[0].name
                    };
                  });
                  item.selectValue = pathData.map(v => v[0].id);
                } else {
                  item.instances = [];
                  item.selectValue = [];
                }
                const obj = this.aggregationMap.find(
                  v => _.isEqual(v.actions.sort(), item.actions.map(_ => _.id).sort())
                );
                if (obj) {
                  item.selectList = obj.selectList || [];
                }
              } else {
                item.selectValue = [];
                item.instances = [];
              }

              item.isRemoteSucceed = item.isAggregate && item.selectList.length > 0;
            } else {
              // const tempList = this.policyList.filter(v => item.actions.map(_ => _.id).includes(v.id)).map(sub => {
              //     const { expired_at, expired_display, id, name, tag } = sub
              //     const curCondition = sub.related_resource_types[0].condition
              //     return {
              //         expired_at,
              //         expired_display,
              //         id,
              //         name,
              //         tag,
              //         condition: curCondition.map(v => {
              //             const obj = {}
              //             if (v.hasOwnProperty('instance')) {
              //                 obj.instances = v.instance
              //             }
              //             if (v.hasOwnProperty('attribute')) {
              //                 obj.attributes = v.attribute
              //             }
              //             return obj
              //         }).filter(_ => Object.keys(_).length > 0)
              //     }
              // })
              // const tempList = this.policyList.filter(v => item.actions.map(_ => _.id).includes(v.id)).map(sub => {
              //     const { expired_at, expired_display, tag } = sub
              //     return {
              //         expired_at,
              //         expired_display,
              //         tag
              //     }
              // })
              // const tempList = this.policyList.filter(v => item.actions.map(_ => _.id).includes(v.id)).map(sub => sub.tag)
              // const isAllEqualFlagNew = (() => {
              //     let isAllEqual = true
              //     for (let i = 0; i < tempList.length; i++) {
              //         if (i !== tempList.length - 1) {
              //             const target = tempList[i].condition
              //             const origin = tempList[i + 1].condition
              //             if (!_.isEqual(target, origin) || target.length < 1 || origin.length < 1) {
              //                 isAllEqual = false
              //                 break
              //             }
              //         }
              //     }
              //     return isAllEqual
              // })()
              // item.tag = tempList.every(_ => _.tag === 'add') ? 'add' : 'update'
              // const tempObj = tempList.find(_ => _.tag === 'add')
              // if (tempObj) {
              //     item.expired_at = tempObj.expired_at
              //     item.expired_display = tempObj.expired_display || this.$t(`m.common['6个月']`)
              // } else {
              //     item.expired_at = tempList[0].expired_at
              //     item.expired_display = tempList[0].expired_display || this.$t(`m.common['6个月']`)
              // }
              // if (isAllEqualFlagNew) {
              //     const tempObj = tempList.find(_ => _.tag === 'add')
              //     if (tempObj) {
              //         item.expired_at = tempObj.expired_at
              //         item.expired_display = tempObj.expired_display
              //     } else {
              //         item.expired_at = tempList[0].expired_at
              //         item.expired_display = tempList[0].expired_display
              //     }
              //     // item.expired_at = tempList[0].expired_at
              //     // item.expired_display = tempList[0].expired_display
              //     // item.tag = tempList.every(_ => _.tag === 'add') ? 'add' : 'update'
              //     // if (tempList[0].condition.length > 0) {
              //     //     const pathData = tempList[0].condition[0].instances[0].path
              //     //     item.selectValueDisplay = pathData.map(v => v[0].name).join(',')
              //     //     item.selectValue = pathData.map(v => v[0].id)
              //     // }
              // }
            }
            return new GradeAggregationPolicy(item);
          });
          this.policyList = this.policyList.filter(item => !tempActionIds.includes(`${item.system_id}&${item.id}`));
          this.policyList.unshift(...aggregations);
          this.aggregationMap = [];
          return;
        }
        const aggregationData = [];
        const newTableData = [];
        this.policyList.forEach(item => {
          if (!item.isAggregate) {
            newTableData.push(item);
          } else {
            aggregationData.push(_.cloneDeep(item));
            if (
              !this.aggregationMap.some(
                v => _.isEqual(v.actions.sort(), item.actions.map(_ => _.id).sort())
              ) && item.selectList.length > 0
            ) {
              this.aggregationMap.push({
                actions: item.actions.map(_ => _.id),
                selectList: item.selectList
              });
            }
          }
        });
        // console.warn('aggregationMap: ')
        // console.warn(this.aggregationMap)
        this.policyList = _.cloneDeep(newTableData);
        const reallyActionIds = actionIds.filter(item => !this.policyList.map(v => `${v.system_id}&${v.id}`).includes(item));
        reallyActionIds.forEach(item => {
          // 优先从已有权限取值
          const curObj = this.aggregationsTableData.find(_ => _.id === item);
          // const curObj = (() => {
          //     const filterList = this.policyList.filter(v => this.aggregationsTableData.map(_ => _.id).includes(v.id))
          //     return filterList.find(_ => _.id === item)
          // })()
          if (curObj) {
            this.policyList.unshift(curObj);
          } else {
            const curAction = this.policyList.find(_ => `${_.system_id}&${_.id}` === item);
            const curAggregation = aggregationData.find(_ => _.actions.map(v => `${_.system_id}&${v.id}`).includes(item));
            this.policyList.unshift(new GradePolicy({ ...curAction, tag: 'add' }, 'add'));
            if (curAggregation && curAggregation.instances.length > 0) {
              const curData = this.policyList[0];
              const instances = (function () {
                const arr = [];
                const aggregateResourceType = curAggregation.aggregateResourceType;
                const { id, name, system_id } = aggregateResourceType;
                curAggregation.instances.forEach(v => {
                  const curItem = arr.find(_ => _.type === id);
                  if (curItem) {
                    curItem.path.push([{
                      id: v.id,
                      name: v.name,
                      system_id,
                      type: id,
                      type_name: name
                    }]);
                  } else {
                    arr.push({
                      name,
                      type: id,
                      path: [[{
                        id: v.id,
                        name: v.name,
                        system_id,
                        type: id,
                        type_name: name
                      }]]
                    });
                  }
                });
                return arr;
              })();
              if (instances.length > 0) {
                curData.related_resource_types.forEach(subItem => {
                  subItem.condition = [new Condition({ instances }, '', 'add')];
                });
              }
            }
          }
        });
        console.warn(this.policyList);
      },

      handleSelect () {
        this.$emit('on-add');
      },

      handleDelete (payload) {
        this.$emit('on-delete', payload);
      },

      handleGetValue () {
        return this.$refs.resourceInstanceRef && this.$refs.resourceInstanceRef.handleGetValue();
      }
    }
  };
</script>
<style lang="postcss">
    .iam-grade-admin-select-wrapper {
        .action {
            display: flex;
            justify-content: flex-start;
            .action-wrapper {
                font-size: 14px;
                color: #3a84ff;
                cursor: pointer;
                &:hover {
                    color: #699df4;
                }
                i {
                    position: relative;
                    top: -1px;
                    left: 2px;
                }
            }
            .info-icon {
                margin: 2px 0 0 2px;
                color: #c4c6cc;
                &:hover {
                    color: #3a84ff;
                }
            }
        }
        .info-wrapper {
            display: flex;
            justify-content: space-between;
            margin-top: 16px;
            line-height: 24px;
            .tips,
            .text {
                line-height: 20px;
                font-size: 12px;
            }
        }
        .resource-instance-wrapper {
            min-height: 200px;
        }
        .loading-resource-instance-cls {
            border: 1px solid #c4c6cc;
        }
    }
</style>
