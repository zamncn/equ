/* EquipSupply 静态站表单处理
 * 作用：解绑模板自带的 rd-mailform(ajaxForm)，改用 Formspree / 任意接受 POST 的静态表单服务。
 * 配置：把下方 DEFAULT_ENDPOINT 与每个 <form action> 里的占位 token
 *       REPLACE_WITH_YOUR_FORM_ID 换成你的真实表单地址即可（换服务商也只改这一处）。
 */
(function () {
  'use strict';

  // 默认端点：当表单 action 不是 http(s) 时回退使用
  var DEFAULT_ENDPOINT = 'https://formspree.io/f/REPLACE_WITH_YOUR_FORM_ID';

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
      fd.append('form_type', type);
      fd.append('_subject', 'EquipSupply ' + type + ' form submission');

      if (output) {
        output.innerHTML = '<p><span class="icon text-middle fa fa-circle-o-notch fa-spin icon-xxs"></span><span>Sending…</span></p>';
        output.classList.add('active');
      }

      fetch(endpoint, {
        method: 'POST',
        body: fd,
        headers: { 'Accept': 'application/json' }
      }).then(function (resp) {
        if (resp.ok) {
          showMessage(output, 'Successfully sent!', 'success');
          if (typeof form.reset === 'function') form.reset();
        } else {
          showMessage(output, 'Something went wrong. Please try again.', 'error');
        }
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
