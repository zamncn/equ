/* EquipSupply 静态站表单处理
 * 作用：解绑模板自带的 rd-mailform(ajaxForm)，改用 Web3Forms 静态表单服务(免注册)。
 * 配置：仅把下方 ACCESS_KEY 换成你在 web3forms.com 用收信邮箱获取的 access key 即可（全站唯一一处）。
 *       所有表单的 action 已统一为 Web3Forms 提交端点。
 */
(function () {
  'use strict';

  // 默认端点（表单 action 已是 web3forms；此值仅作回退）
  var DEFAULT_ENDPOINT = 'https://api.web3forms.com/submit';
  // ★ 唯一需要替换的地方：去 https://web3forms.com 输入你的收信邮箱获取 access key
  var ACCESS_KEY = '749b6475-0ce6-4b19-8128-0de751d7b217';

  function getEndpoint(form) {
    var a = form.getAttribute('action');
    if (a && /^https?:\/\//i.test(a)) return a;
    return DEFAULT_ENDPOINT;
  }

  function getOutput(form) {
    var id = form.getAttribute('data-form-output');
    return id ? document.getElementById(id) : null;
  }

  function showMessage(output, text, kind) {
    if (!output) return;
    var icon = kind === 'success' ? 'mdi mdi-check icon-xxs' : 'mdi mdi-alert-outline icon-xxs';
    output.innerHTML = '<p><span class="icon text-middle ' + icon + '"></span><span>' + text + '</span></p>';
    output.classList.remove('active', 'success', 'error');
    // 强制重绘，便于连续提交时动画重启
    void output.offsetWidth;
    output.classList.add('active', kind);
    setTimeout(function () {
      output.classList.remove('active', 'success', 'error');
    }, 5000);
  }

  // 依据模板既有 data-constraints 做最小校验（@Required / @Email）
  function validate(form) {
    var inputs = form.querySelectorAll('[data-constraints]');
    for (var i = 0; i < inputs.length; i++) {
      var el = inputs[i];
      var c = el.getAttribute('data-constraints') || '';
      var val = (el.value || '').trim();
      if (c.indexOf('@Required') !== -1 && !val) {
        return { ok: false, el: el, msg: 'Please fill in all required fields.' };
      }
      if (c.indexOf('@Email') !== -1 && val && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
        return { ok: false, el: el, msg: 'Please enter a valid e-mail address.' };
      }
    }
    return { ok: true };
  }

  function handleSubmit(form) {
    return function (e) {
      e.preventDefault();
      var output = getOutput(form);
      var v = validate(form);
      if (!v.ok) {
        showMessage(output, v.msg, 'error');
        if (v.el && v.el.focus) v.el.focus();
        return;
      }

      var endpoint = getEndpoint(form);
      var fd = new FormData(form);
      var type = form.getAttribute('data-form-type') || 'contact';

      // 构造 Web3Forms 接受的 JSON 负载
      var payload = {};
      fd.forEach(function (value, key) {
        if (key === '_subject') return; // 用下方标准 subject 替代
        payload[key] = value;
      });
      payload.access_key = ACCESS_KEY;
      payload.subject = 'EquipSupply ' + type + ' form submission';
      payload.form_type = type;

      if (output) {
        output.innerHTML = '<p><span class="icon text-middle fa fa-circle-o-notch fa-spin icon-xxs"></span><span>Sending…</span></p>';
        output.classList.add('active');
      }

      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      }).then(function (resp) {
        return resp.text().then(function (text) {
          var data = {};
          try { data = JSON.parse(text); } catch (err) { /* 非 JSON 响应 */ }
          if (resp.ok && data.success) {
            showMessage(output, 'Successfully sent!', 'success');
            if (typeof form.reset === 'function') form.reset();
          } else {
            showMessage(output, (data && data.message) ? data.message : 'Something went wrong. Please try again.', 'error');
          }
        });
      }).catch(function () {
        showMessage(output, 'Network error. Please try again.', 'error');
      });
    };
  }

  function init() {
    var forms = document.querySelectorAll('form[data-form-type]');
    for (var i = 0; i < forms.length; i++) {
      var form = forms[i];
      // 解绑模板 rd-mailform 的 ajaxForm，避免重复提交
      try {
        if (window.jQuery && typeof window.jQuery.fn.ajaxFormUnbind === 'function') {
          window.jQuery(form).ajaxFormUnbind();
        }
      } catch (err) { /* noop */ }
      // 移除 rd-mailform class，彻底防止其再次接管
      form.classList.remove('rd-mailform');
      form.addEventListener('submit', handleSubmit(form));
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
