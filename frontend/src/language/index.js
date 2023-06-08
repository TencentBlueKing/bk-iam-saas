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
import en from './lang/en';
import cn from './lang/zh';
import magicbox from 'bk-magic-vue';
import { getCookie } from '@/common/util';

const { lang } = magicbox;
const messages = {
  'zh-cn': {
    ...lang.zhCN,
    ...cn
  },
  en: {
    ...lang.enUS,
    ...en
  }
};

const language = getCookie('blueking_language') || 'zh-cn';

// 检测漏掉的翻译
// const cnLan = cn.language;
// const cnLen = Object.keys(cnLan).length;
// const enLan = en.language;
// const enLen = Object.keys(enLan).length;

// for (let i = 0; i < cnLen; i++) {
//     const key = Object.keys(cnLan)[i];
//     for (const label in cnLan[key]) {
//         if (enLan[key][label] === null || enLan[key][label] === undefined) {
//             console.log(key);
//             console.log(label);
//         }
//     }
// }

// for (let i = 0; i < enLen; i++) {
//     const key = Object.keys(enLan)[i];
//     for (const label in enLan[key]) {
//         if (cnLan[key][label] === null || cnLan[key][label] === undefined) {
//             console.log(key);
//             console.log(label);
//         }
//     }
// }

const il8n = (key, subKey) => {
  const local = messages[language]['language'];
  if (!local[key] || !local[key][subKey]) {
    return subKey;
  }
  return local[key][subKey];
};

export default il8n;

export {
  il8n,
  language
};
