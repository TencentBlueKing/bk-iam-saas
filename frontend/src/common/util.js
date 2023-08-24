/*
 * Tencent is pleased to support the open source community by making
 * 蓝鲸智云-权限中心(BlueKing-IAM) available.
 *
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 *
 * 蓝鲸智云-权限中心(BlueKing-IAM) is licensed under the MIT License.
 *
 * License for 蓝鲸智云-权限中心(BlueKing-IAM):
 *
 * ---------------------------------------------------
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
 * to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of
 * the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
 * THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
*/

/**
 * 函数柯里化
 *
 * @example
 *     function add (a, b) {return a + b}
 *     curry(add)(1)(2)
 *
 * @param {Function} fn 要柯里化的函数
 *
 * @return {Function} 柯里化后的函数
 */
export function curry (fn) {
  const judge = (...args) => {
    return args.length === fn.length
      ? fn(...args)
      : arg => judge(...args, arg);
  };
  return judge;
}

/**
 * 判断是否是对象
 *
 * @param {Object} obj 待判断的
 *
 * @return {boolean} 判断结果
 */
export function isObject (obj) {
  return obj !== null && typeof obj === 'object';
}

/**
 * 规范化参数
 *
 * @param {Object|string} type vuex type
 * @param {Object} payload vuex payload
 * @param {Object} options vuex options
 *
 * @return {Object} 规范化后的参数
 */
export function unifyObjectStyle (type, payload, options) {
  if (isObject(type) && type.type) {
    options = payload;
    payload = type;
    type = type.type;
  }

  if (NODE_ENV !== 'production') {
    if (typeof type !== 'string') {
      console.warn(`expects string as the type, but found ${typeof type}.`);
    }
  }

  return { type, payload, options };
}

/**
 * 以 baseColor 为基础生成随机颜色
 *
 * @param {string} baseColor 基础颜色
 * @param {number} count 随机颜色个数
 *
 * @return {Array} 颜色数组
 */
export function randomColor (baseColor, count) {
  const segments = baseColor.match(/[\da-z]{2}/g);
  // 转换成 rgb 数字
  for (let i = 0; i < segments.length; i++) {
    segments[i] = parseInt(segments[i], 16);
  }
  const ret = [];
  // 生成 count 组颜色，色差 20 * Math.random
  for (let i = 0; i < count; i++) {
    ret[i] = '#'
            + Math.floor(segments[0] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16)
            + Math.floor(segments[1] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16)
            + Math.floor(segments[2] + (Math.random() < 0.5 ? -1 : 1) * Math.random() * 20).toString(16);
  }
  return ret;
}

/**
 * min max 之间的随机整数
 *
 * @param {number} min 最小值
 * @param {number} max 最大值
 *
 * @return {number} 随机数
 */
export function randomInt (min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

/**
 * 异常处理
 *
 * @param {Object} err 错误对象
 * @param {Object} ctx 上下文对象，这里主要指当前的 Vue 组件
 */
export function catchErrorHandler (err, ctx) {
  const data = err.data;
  if (data) {
    if (!data.code || data.code === 404) {
      ctx.exceptionCode = {
        code: '404',
        msg: '当前访问的页面不存在'
      };
    } else if (data.code === 403) {
      ctx.exceptionCode = {
        code: '403',
        msg: 'Sorry，您的权限不足!'
      };
    } else {
      console.error(err);
      ctx.bkMessageInstance = ctx.$bkMessage({
        limit: 1,
        theme: 'error',
        message: err.message || err.data.msg || err.statusText
      });
    }
  } else {
    console.error(err);
    ctx.bkMessageInstance = ctx.$bkMessage({
      limit: 1,
      theme: 'error',
      message: err.message || err.data.msg || err.statusText
    });
  }
}

/**
 * 获取字符串长度，中文算两个，英文算一个
 *
 * @param {string} str 字符串
 *
 * @return {number} 结果
 */
export function getStringLen (str) {
  let len = 0;
  for (let i = 0; i < str.length; i++) {
    if (str.charCodeAt(i) > 127 || str.charCodeAt(i) === 94) {
      len += 2;
    } else {
      len++;
    }
  }
  return len;
}

/**
 * 转义特殊字符
 *
 * @param {string} str 待转义字符串
 *
 * @return {string} 结果
 */
export const escape = str => String(str).replace(/([.*+?^=!:${}()|[\]\/\\])/g, '\\$1');

/**
 * 对象转为 url query 字符串
 *
 * @param {*} param 要转的参数
 * @param {string} key key
 *
 * @return {string} url query 字符串
 */
export function json2Query (param, key) {
  const mappingOperator = '=';
  const separator = '&';
  let paramStr = '';
  if (
    param instanceof String
        || typeof param === 'string'
        || param instanceof Number
        || typeof param === 'number'
        || param instanceof Boolean
        || typeof param === 'boolean'
  ) {
    paramStr += separator + key + mappingOperator + encodeURIComponent(param);
  } else {
    if (param) {
      Object.keys(param).forEach((p) => {
        const value = param[p];
        const k
                    = key === null || key === '' || key === undefined
                      ? p
                      : key + (param instanceof Array ? '[' + p + ']' : '.' + p);
        paramStr += separator + json2Query(value, k);
      });
    }
  }
  return paramStr.substr(1);
}

/**
 * 字符串转换为驼峰写法
 *
 * @param {string} str 待转换字符串
 *
 * @return {string} 转换后字符串
 */
export function camelize (str) {
  return str.replace(/-(\w)/g, (strMatch, p1) => p1.toUpperCase());
}

/**
 * 获取元素的样式
 *
 * @param {Object} elem dom 元素
 * @param {string} prop 样式属性
 *
 * @return {string} 样式值
 */
export function getStyle (elem, prop) {
  if (!elem || !prop) {
    return false;
  }

  // 先获取是否有内联样式
  let value = elem.style[camelize(prop)];

  if (!value) {
    // 获取的所有计算样式
    let css = '';
    if (document.defaultView && document.defaultView.getComputedStyle) {
      css = document.defaultView.getComputedStyle(elem, null);
      value = css ? css.getPropertyValue(prop) : null;
    }
  }

  return String(value);
}

/**
 *  获取元素相对于页面的高度
 *
 *  @param {Object} node 指定的 DOM 元素
 */
export function getActualTop (node) {
  let actualTop = node.offsetTop;
  let current = node.offsetParent;

  while (current !== null) {
    actualTop += current.offsetTop;
    current = current.offsetParent;
  }

  return actualTop;
}

/**
 *  获取元素相对于页面左侧的宽度
 *
 *  @param {Object} node 指定的 DOM 元素
 */
export function getActualLeft (node) {
  let actualLeft = node.offsetLeft;
  let current = node.offsetParent;

  while (current !== null) {
    actualLeft += current.offsetLeft;
    current = current.offsetParent;
  }

  return actualLeft;
}

/**
 * document 总高度
 *
 * @return {number} 总高度
 */
export function getScrollHeight () {
  let scrollHeight = 0;
  let bodyScrollHeight = 0;
  let documentScrollHeight = 0;

  if (document.body) {
    bodyScrollHeight = document.body.scrollHeight;
  }

  if (document.documentElement) {
    documentScrollHeight = document.documentElement.scrollHeight;
  }

  scrollHeight = (bodyScrollHeight - documentScrollHeight > 0) ? bodyScrollHeight : documentScrollHeight;

  return scrollHeight;
}

/**
 * 滚动条在 y 轴上的滚动距离
 *
 * @return {number} y 轴上的滚动距离
 */
export function getScrollTop () {
  let scrollTop = 0;
  let bodyScrollTop = 0;
  let documentScrollTop = 0;

  if (document.body) {
    bodyScrollTop = document.body.scrollTop;
  }

  if (document.documentElement) {
    documentScrollTop = document.documentElement.scrollTop;
  }

  scrollTop = (bodyScrollTop - documentScrollTop > 0) ? bodyScrollTop : documentScrollTop;

  return scrollTop;
}

/**
 * 浏览器视口的高度
 *
 * @return {number} 浏览器视口的高度
 */
export function getWindowHeight () {
  const windowHeight = document.compatMode === 'CSS1Compat'
    ? document.documentElement.clientHeight
    : document.body.clientHeight;

  return windowHeight;
}

/**
 * 生成 guid
 *
 * @return {string} guid
 */
export function guid () {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * 时间戳转换 YY-MM-DD hh:mm:ss 格式
 *
 * @param {number} timestamp 13位时间戳
 */
export function timestampToTime (timestamp) {
  let time = '';
  if (timestamp) {
    time = new Date(timestamp);
  } else {
    time = new Date();
  }
  const getStr = (value, type = 'default') => {
    const tempValue = type === 'month' ? value + 1 : value;
    const separator = ['day', 'second'].includes(type) ? '' : ['year', 'month'].includes(type) ? '-' : ':';
    if (tempValue < 10) {
      return `0${tempValue}${separator}`;
    }
    return `${tempValue}${separator}`;
  };
  const Y = getStr(time.getFullYear(), 'year');
  const M = getStr(time.getMonth(), 'month');
  const D = getStr(time.getDate(), 'day');
  const h = getStr(time.getHours());
  const m = getStr(time.getMinutes());
  const s = getStr(time.getSeconds(), 'second');
  return Y + M + D + ' ' + h + m + s;
}

/**
 * 对比两个值是否相等
 *
 * @param {number/string/object} x
 * @param {number/string/object} y
 */
export function deepEquals (x, y) {
  const f1 = x instanceof Object;
  const f2 = y instanceof Object;
  if (!f1 || !f2) {
    return x === y;
  }
  if (Object.keys(x).length !== Object.keys(y).length) {
    return false;
  }
  const newX = Object.keys(x);
  for (let p = 0; p < newX.length; p++) {
    const p2 = newX[p];
    const a = x[p2] instanceof Object;
    const b = y[p2] instanceof Object;
    if (a && b) {
      if (!deepEquals(x[p2], y[p2])) {
        return false;
      }
    } else if (x[p2] !== y[p2]) {
      return false;
    }
  }
  return true;
}

/**
 * 查找地址栏是否有传入的值
 *
 * @param {number/string/object} x
 */
export function existValue (value) {
  // 1、url截取?之后的字符串(不包含?)
  const pathSearch = window.location.search.substr(1);
  const result = [];
  // 2、以&为界截取参数键值对
  const paramItems = pathSearch.split('&');
  // 3、将键值对形式的参数存入数组
  for (let i = 0; i < paramItems.length; i++) {
    const paramKey = paramItems[i].split('=')[0];
    const paramValue = paramItems[i].split('=')[1];
    result.push({
      key: paramKey,
      value: paramValue
    });
  }

  // 4、遍历value值
  for (let j = 0; j < result.length; j++) {
    if (result[j].value === value) {
      return true;
    }
  }
  return false;
}

/**
 * 根据参数key获取地址栏的value
 *
 * @param {number/string/object} x
 */
export function getParamsValue (key) {
  // 1、url截取?之后的字符串(不包含?)
  const pathSearch = window.location.search.substr(1);
  const result = [];
  // 2、以&为界截取参数键值对
  const paramItems = pathSearch.split('&');
  // 3、将键值对形式的参数存入数组
  for (let i = 0; i < paramItems.length; i++) {
    const paramKey = paramItems[i].split('=')[0];
    const paramValue = paramItems[i].split('=')[1];
    result.push({
      key: paramKey,
      value: paramValue
    });
  }

  // 4、遍历value值
  for (let j = 0; j < result.length; j++) {
    if (result[j].key === key) {
      return result[j].value;
    }
  }
}

/**
 * 根据毫秒生成睡眠函数
 *
 * @param number
 */
export function sleep (time) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve();
    }, time);
  });
}

/**
 * 根据状态码生成不同提示
 *
 * @param {number/string} type
 * @param {object} payload
 * @param {boolean} isEmpty 为了处理异常数据刷新一次正常，执行正常code，这时候需要清空字段
 */
export function formatCodeData (type, payload, isEmpty = true) {
  type = Number(type);
  const codeData = {
    0: () => {
      const operateEmpty = {
        true: () => {
          return payload.tipType === 'search'
            ? Object.assign(payload, { type: 'search-empty', text: '搜索结果为空', tipType: 'search' })
            : Object.assign(payload, { type: 'empty', text: '暂无数据', tipType: '' });
        },
        false: () => {
          return Object.assign(payload, { type: '', text: '', tipType: '' });
        }
      };
      return operateEmpty[isEmpty]();
    },
    401: () => {
      return Object.assign(payload, { type: 403, text: '没有权限', tipType: 'refresh' });
    },
    403: () => {
      return Object.assign(payload, { type: 403, text: '没有权限', tipType: 'refresh' });
    },
    404: () => {
      return Object.assign(payload, { type: 404, text: '数据不存在', tipType: 'refresh' });
    },
    500: () => {
      return Object.assign(payload, { type: 500, text: '数据获取异常', tipType: 'refresh' });
    },
    1902000: () => {
      return Object.assign(payload, { type: 500, text: '数据获取异常', tipType: 'refresh' });
    },
    1902200: () => {
      return Object.assign(payload, { type: 500, text: '数据获取异常', tipType: 'refresh' });
    },
    1902204: () => {
      return Object.assign(payload, { type: 500, text: '暂不支持搜索', tipType: 'refresh' });
    },
    1902229: () => {
      return Object.assign(payload, { type: 500, text: '搜索过于频繁', tipType: 'refresh' });
    },
    1902222: () => {
      return Object.assign(payload, { type: 500, text: '搜索结果太多', tipType: 'refresh' });
    },
    1302403: () => {
      return Object.assign(payload, { type: 403, text: '无该应用访问权限', tipType: 'noPerm', message: payload.message || '' });
    }
  };
  return codeData[type] ? codeData[type]() : codeData[500]();
}

/**
 * 递归查询匹配角色id
 *
 * @param {number} id
 * @param {Array} list
 */
export function getTreeNode (id, list) {
  for (let i = 0; i < list.length; i++) {
    if (list[i].id === id) {
      return list[i];
    } else if (list[i].sub_roles && list[i].sub_roles.length) {
      const result = getTreeNode(id, list[i].sub_roles);
      if (result) {
        return result;
      }
    }
  }
}

/**
 *  处理中英文国际化动态文字渲染宽度
 *
 * @param {payload} str 模块类型
 *
 */
export function renderLabelWidth (payload) {
  const isCN = ['zh-cn'].includes(window.CUR_LANGUAGE);
  const typeMap = {
    resource: () => {
      return isCN ? 120 : 120;
    },
    member: () => {
      return isCN ? 140 : 350;
    },
    rating_manager_merge_action_guide: () => {
      return isCN ? { top: '-25px', right: '260px' } : { top: '-30px', right: '260px' };
    }
  };
  return typeMap[payload]();
}

/**
 *  获取指定cookie的value
 *
 * @param {name} str 名称
 *
 */
export function getCookie (name) {
  const data = document.cookie.split(';');
  const params = {};
  for (let i = 0; i < data.length; i++) {
    params[data[i].split('=')[0].replace(/\s/, '')] = data[i].split('=')[1];
  }
  return params[name];
}

// 兼容外部系统i18的key
export function formatI18nKey () {
  const lang = getCookie('blueking_language') || 'zh-cn';
  const result = ['zh-cn', 'en'].includes(lang) ? lang : 'zh-cn';
  return result;
}

/**
 *  jsonp请求
 *
 * @param {url} str 请求地址
 * @param {params} str 请求参数
 * @param {callback} str 回调名
 *
 */
export function jsonpRequest (url, params, callbackName) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    if (callbackName) {
      callbackName = callbackName + Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
    }
    Object.assign(params, callbackName ? { callback: callbackName } : {});
    const arr = Object.keys(params).map(key => `${key}=${params[key]}`);
    script.src = `${url}?${arr.join('&')}`;
    document.body.appendChild(script);
    window[callbackName] = (data) => {
      resolve(data);
    };
  });
}

/**
 *  删除url上指定参数
 *
 * @param {list} str 需要删除的参数列表
 *
 */
export function delLocationHref (list) {
  const url = window.location.href;
  const params = (window.location.search || '?').substring(1).split('&');
  const prefix = url.substring(0, url.indexOf('?'));
  let suffix = '';
  for (let i = params.length - 1; i >= 0; i--) {
    const param = params[i];
    const key = param && param.split('=', 2)[0];
    if (!param || list.includes(key)) {
      params.splice(i, 1);
    }
  }
  if (params.length) {
    suffix = `?${params.join('&')}`;
  }
  window.history.replaceState({}, '', prefix + suffix);
}
