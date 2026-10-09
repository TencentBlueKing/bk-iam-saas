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
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

const getOperatorId = operator => (typeof operator === 'string' ? operator : operator && operator.id);

/**
 * 使用属性接口返回的最新元数据修正回填数据。
 *
 * 历史策略可能没有 operators，且 operator 缺失时模型会回退为 eq；
 * 如果属性实际只支持 starts_with 等操作符，Select 将无法匹配并显示为空。
 */
export const syncAttributeMetadata = (attribute, definitions = []) => {
  const definition = definitions.find(item => item.id === attribute.id);
  if (definition) {
    attribute.name = definition.display_name || attribute.name || '';
    attribute.type = definition.type || attribute.type || 'STRING';
    attribute.operators = definition.operators && definition.operators.length > 0
      ? definition.operators
      : attribute.operators;
  }

  const operators = attribute.operators && attribute.operators.length > 0
    ? attribute.operators
    : ['eq'];
  const operatorIds = operators.map(getOperatorId).filter(Boolean);
  attribute.operators = operators;
  if (!operatorIds.includes(attribute.operator)) {
    attribute.operator = operatorIds[0] || 'eq';
  }
};

/**
 * 将策略中已保存的值合入当前分页结果，保证不在第一页的值也能正常回显。
 */
export const mergeSelectedAttributeValues = (attribute, options = []) => {
  const currentOptions = (options || []).filter(Boolean);
  const optionIds = new Set(currentOptions.map(item => String(item.id)));
  const selectedOptions = (attribute.values || []).reduce((results, item) => {
    if (item.id === undefined || item.id === null || optionIds.has(String(item.id))) {
      return results;
    }
    optionIds.add(String(item.id));
    results.push({
      id: item.id,
      display_name: item.name || item.display_name || String(item.id)
    });
    return results;
  }, []);
  return [...selectedOptions, ...currentOptions];
};
