(function () {
  if (localStorage.getItem('cookie-ok')) return;
  const el = document.createElement('div');
  el.className = 'cookie-notice';
  el.setAttribute('role', 'region');
  el.setAttribute('aria-label', 'Cookie notice');
  el.innerHTML =
    '<p>This site uses <strong>Google Fonts</strong> (shares your IP with Google) and the <strong>Tally.so</strong> form, which may store cookies. <a href="pravni-informace.html">More information</a></p>' +
    '<button class="cookie-notice__btn" aria-label="Confirm and close notice">I understand</button>';
  el.querySelector('button').addEventListener('click', function () {
    el.remove();
    localStorage.setItem('cookie-ok', '1');
  });
  document.body.appendChild(el);
})();
