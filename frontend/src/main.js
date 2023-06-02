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

import './public-path';
import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import { injectCSRFTokenToHeaders } from './api';
import auth from './common/auth';
import Img403 from './images/403.png';
import Exception from './components/exception/index.vue';
import { bus } from './common/bus';
import AuthComponent from './components/auth/index.vue';
import iamFormItem from './components/iam-form/item.vue';
import SmartAction from './components/smart-action/index.vue';
import IamSvg from './components/iam-svg/index.vue';
import ExceptionEmpty from './components/exception-empty';
import IamSpinLoading from './components/iam-spin-loading/index.vue';
import RenderHorizontalBlock from './components/render-block/horizontal.vue';
import RenderVerticalBlock from './components/render-block/vertical.vue';
import RenderSearch from './components/render-search/index.vue';
import Icon from './components/icon';
import VueI18n from 'vue-i18n';
import magicbox from 'bk-magic-vue';
import { language, il8n as il8nNew } from './language';
import './common/bkmagic';
// 全量引入自定义图标
import './assets/iconfont/style.css';
import '@icon-cool/bk-icon-bk-iam';

Vue.component('app-exception', Exception);
Vue.component('app-auth', AuthComponent);
Vue.component('IamFormItem', iamFormItem);
Vue.component('SmartAction', SmartAction);
Vue.component('IamSvg', IamSvg);
Vue.component('spinLoading', IamSpinLoading);
Vue.component('RenderHorizontalBlock', RenderHorizontalBlock);
Vue.component('RenderVerticalBlock', RenderVerticalBlock);
Vue.component('RenderSearch', RenderSearch);
Vue.component('Icon', Icon);
Vue.component('ExceptionEmpty', ExceptionEmpty);

Vue.prototype.scrollToLocation = function ($ref) {
  const distance = ($ref && $ref.getBoundingClientRect().top) || 0;
  const $dom = document.getElementsByClassName('main-scroller')[0];
  $dom.scrollTo(0, distance);
};

Vue.use(VueI18n);
Vue.use(magicbox, {
  i18n: (key, args) => i18n.t(key, args)
});

console.log('start');

const cn = require('./language/lang/zh');

const en = require('./language/lang/en');

const { lang, locale } = magicbox;

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

window.changeAlert = false;
window.changeDialog = false;

const i18n = new VueI18n({
  // 语言标识
  locale: language,
  fallbackLocale: language,
  // this.$i18n.locale 通过切换locale的值来实现语言切换
  messages,
  silentTranslationWarn: true,
  missing (locale, path) {
    const parsedPath = i18n._path.parsePath(path);
    return parsedPath[parsedPath.length - 1];
  }
});

// if (language === 'zh-cn') {
//     locale.use(lang.zhCN);
// } else {
//     console.log(lang.enUS, 6555);
// }
locale.use(language === 'zh-cn' ? lang.zhCN : lang.enUS);

locale.i18n((key, value) => i18n.t(key, value));

Vue.prototype.curLanguageIsCn = language === 'zh-cn';

Vue.mixin(locale.mixin);

if (NODE_ENV === 'development') {
  Vue.config.devtools = true;
}

auth.requestCurrentUser().then(user => {
  injectCSRFTokenToHeaders();
  if (!user.isAuthenticated) {
    auth.redirectToLogin();
  } else {
    global.bus = bus;
    global.mainComponent = new Vue({
      el: '#app',
      i18n,
      router,
      store,
      components: {
        App
      },
      template: '<App/>'
    });
    if (NODE_ENV === 'development') {
      window.__VUE_DEVTOOLS_GLOBAL_HOOK__.Vue = global.mainComponent.constructor;
    }
  }
}, err => {
  let message;
  if (err.status === 403) {
    message = il8nNew('common', '权限不足');
    if (err.data && err.data.msg) {
      message = err.data.msg;
    }
  } else {
    message = il8nNew('info', '无法连接到后端服务');
  }

  const divStyle = ''
        + 'text-align: center;'
        + 'width: 400px;'
        + 'margin: auto;'
        + 'position: absolute;'
        + 'top: 50%;'
        + 'left: 50%;'
        + 'transform: translate(-50%, -50%);';

  const h2Style = 'font-size: 20px;color: #979797; margin: 32px 0;font-weight: normal';

  const content = ``
        + `<div class="bk-exception bk-exception-center" style="${divStyle}">`
        + `<img src="${Img403}"><h2 class="exception-text" style="${h2Style}">${message}</h2>`
        + `</div>`;

  document.write(content);
});
