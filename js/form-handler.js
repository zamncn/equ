/* EquipSupply static-site form handler
 * Purpose: unbind the template's built-in rd-mailform (ajaxForm) and submit
 *          through the Web3Forms static form service instead (no signup needed).
 * Config:  replace ACCESS_KEY below with the access key you obtain at
 *          web3forms.com for your receiving mailbox (the only place site-wide).
 *          All form actions are unified to the Web3Forms submit endpoint.
 */
(function () {
  'use strict';

  // Default endpoint (form actions already point to web3forms; fallback only)
  var DEFAULT_ENDPOINT = 'https://api.web3forms.com/submit';
  // ★ The only value to replace: enter your receiving mailbox at https://web3forms.com
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
    // force reflow so the animation restarts on consecutive submits
    void output.offsetWidth;
    output.classList.add('active', kind);
    setTimeout(function () {
      output.classList.remove('active', 'success', 'error');
    }, 5000);
  }

  // minimal validation based on the template's existing data-constraints (@Required / @Email)
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

      // build a JSON payload accepted by Web3Forms
      var payload = {};
      fd.forEach(function (value, key) {
        if (key === '_subject') return; // replaced by the standard subject below
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
          try { data = JSON.parse(text); } catch (err) { /* non-JSON response */ }
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
      // unbind the template's rd-mailform ajaxForm to avoid double submission
      try {
        if (window.jQuery && typeof window.jQuery.fn.ajaxFormUnbind === 'function') {
          window.jQuery(form).ajaxFormUnbind();
        }
      } catch (err) { /* noop */ }
      // remove the rd-mailform class so it can never take over again
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
