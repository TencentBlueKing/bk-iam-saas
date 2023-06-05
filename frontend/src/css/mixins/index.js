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

module.exports = {
  /**
     * button mixins
     *
     * @example
     *     @mixin button red, green, #000;
     *     @mixin button red, green;
     * @param {Ojbect} mixin ast 对象
     * @param {[type]} bg [description]
     * @param {[type]} color [description]
     * @param {[type]} bgHover [description]
     */
  button (mixin, bg, color, bgHover = 'blue') {
    return {
      'background': bg,
      'color': color,
      '&:hover, &:focus': {
        'background': bgHover
      }
    };
  },

  /**
     * clearfix mixins
     *
     * @example
     *     @mixin clearfix;
     * @param {Ojbect} mixin ast 对象
     */
  clearfix (mixin) {
    return {
      '&::after': {
        'content': '""',
        'display': 'block',
        'clear': 'both',
        'font-size': 0,
        'visibility': 'hidden'
      }
    };
  },

  /**
     * ellipsis mixins
     *
     * @example
     *     @mixin ellipsis;
     *     @mixin ellipsis 100px;
     * @param {Ojbect} mixin ast 对象
     * @param {string} maxWidth 最大宽度，默认为 auto
     */
  ellipsis (mixin, maxWidth) {
    const ret = {
      'overflow': 'hidden',
      'text-overflow': 'ellipsis',
      'white-space': 'nowrap'
    };

    if (maxWidth) {
      ret['max-width'] = maxWidth;
    }

    return ret;
  },

  /**
     * ellipsis mixins
     *
     * @example
     *     @mixin scroller;
     *     @mixin scroller red;
     *     @mixin scroller green, 2px;
     * @param {Ojbect} mixin ast 对象
     * @param {string} backgroundColor 背景颜色
     * @param {string} width 宽度
     */
  scroller (mixin, backgroundColor = '#e6e9ea', width = '4px') {
    return {
      '&::-webkit-scrollbar': {
        'width': width,
        'background-color': `lighten(${backgroundColor}, 80%)`
      },
      '&::-webkit-scrollbar-thumb': {
        'height': '5px',
        'border-radius': '2px',
        'background-color': backgroundColor
      }
    };
  }
};
