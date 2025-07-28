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
import Vue from 'vue';
import VueI18n from 'vue-i18n';
import magicbox from 'bk-magic-vue';
import { language } from '@/language';

const cn = require('./lang/zh');
const en = require('./lang/en');
const ja = require('./lang/ja');

const { lang, locale } = magicbox;
const messages = {
  'zh-cn': {
    ...lang.zhCN,
    ...cn
  },
  en: {
    ...lang.enUS,
    ...en
  },
  ja: {
    ...lang.jaJP,
    ...ja
  }
};

function getMagicBoxLang () {
  const isEN = language.toLowerCase().indexOf('en') > -1;
  const isJP = language.toLowerCase().indexOf('ja') > -1 || language.toLowerCase().indexOf('jp') > -1;
  if (isEN) {
    return lang.enUS;
  }
  if (isJP) {
    return lang.jaJP;
  }
  return lang.zhCN;
}

Vue.use(VueI18n);

const i18n = new VueI18n({
  locale: language,
  fallbackLocale: language,
  messages,
  silentTranslationWarn: true,
  missing (_locale, path) {
    const parsedPath = i18n._path.parsePath(path);
    return parsedPath[parsedPath.length - 1];
  }
});

locale.use(getMagicBoxLang());
locale.i18n((key, value) => i18n.t(key, value));

Vue.use(magicbox, {
  i18n: (key, args) => i18n.t(key, args)
});
Vue.mixin(locale.mixin);

export {
  i18n
};
