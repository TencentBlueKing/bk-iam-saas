import Vue from 'vue';
import store from '@/store';

export function getActionsData (payload, temps, defaultCheckedActions) {
  // 获取actions和sub_groups所有数据，并根据单双行渲染不同背景颜色
  let colorIndex = 0;
  // 交集
  const intersections = defaultCheckedActions.filter(item => payload.includes(item));
  // 已删除的
  const hasDeleteActions = defaultCheckedActions.filter(item => !intersections.includes(item));
  // 新增的
  const hasAddActions = payload.filter(item => !intersections.includes(item));
  temps.forEach((item, index) => {
    Vue.set(item, 'expanded', index === 0);
    let count = 0;
    let deleteCount = 0;
    if (!item.actions) {
      Vue.set(item, 'actions', []);
    }
    if (!item.sub_groups) {
      Vue.set(item, 'sub_groups', []);
    }
    if (item.actions.length === 1 || !item.sub_groups.length) {
      Vue.set(item, 'bgColor', colorIndex % 2 === 0 ? '#f7f9fc' : '#ffffff');
      colorIndex++;
    }
    item.actions.forEach(act => {
      Vue.set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
      Vue.set(act, 'disabled', act.tag === 'readonly');
      if (hasAddActions.includes(act.id)) {
        Vue.set(act, 'checked', true);
        Vue.set(act, 'flag', 'added');
      }
      if (act.checked && hasDeleteActions.includes(act.id)) {
        act.checked = false;
        Vue.set(act, 'flag', 'cancel');
      }
      if (act.checked) {
        ++count;
      }
      if (act.tag === 'delete') {
        ++deleteCount;
      }
    });
    item.sub_groups.forEach(sub => {
      Vue.set(sub, 'expanded', false);
      Vue.set(sub, 'actionsAllChecked', false);
      Vue.set(sub, 'bgColor', colorIndex % 2 === 0 ? '#f7f9fc' : '#ffffff');
      colorIndex++;
      if (!sub.actions) {
        Vue.set(sub, 'actions', []);
      }
      sub.actions.forEach(act => {
        Vue.set(act, 'checked', ['checked', 'readonly', 'delete'].includes(act.tag));
        Vue.set(act, 'disabled', act.tag === 'readonly');
        if (hasAddActions.includes(act.id)) {
          Vue.set(act, 'checked', true);
          Vue.set(act, 'flag', 'added');
        }
        if (act.checked && hasDeleteActions.includes(act.id)) {
          act.checked = false;
          Vue.set(act, 'flag', 'cancel');
        }
        if (act.checked) {
          ++count;
        }
        if (act.tag === 'delete') {
          ++deleteCount;
        }
      });

      const isSubAllChecked = sub.actions.every(v => v.checked);
      Vue.set(sub, 'allChecked', isSubAllChecked);
    });
    Vue.set(item, 'deleteCount', deleteCount);
    Vue.set(item, 'count', count);
    const isAllChecked = item.actions.every(v => v.checked);
    const isAllDisabled = item.actions.every(v => v.disabled);
    Vue.set(item, 'allChecked', isAllChecked);
    if (item.sub_groups && item.sub_groups.length > 0) {
      Vue.set(item, 'actionsAllChecked', isAllChecked && item.sub_groups.every(v => v.allChecked));
      Vue.set(item, 'actionsAllDisabled', isAllDisabled && item.sub_groups.every(v => {
        return v.actions.every(sub => sub.disabled);
      }));
    } else {
      Vue.set(item, 'actionsAllChecked', isAllChecked);
      Vue.set(item, 'actionsAllDisabled', isAllDisabled);
    }
  });
  return temps;
}

export async function addPreUpdateInfo (payload) {
  const { data } = await store.dispatch('permTemplate/addPreUpdateInfo', payload);
  store.commit('permTemplate/updateCloneActions', data || []);
}
