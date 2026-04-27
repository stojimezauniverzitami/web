(function () {
  if (localStorage.getItem('cookie-ok')) return;
  const el = document.createElement('div');
  el.className = 'cookie-notice';
  el.setAttribute('role', 'region');
  el.setAttribute('aria-label', 'Informace o cookies');
  el.innerHTML =
    '<p>Web používá <strong>Google Fonts</strong> (sdílení IP s Googlem) a formulář ' +
    '<strong>Tally.so</strong>, který může ukládat cookies. ' +
    '<a href="pravni-informace.html">Více informací</a></p>' +
    '<button class="cookie-notice__btn" aria-label="Potvrdit a zavřít upozornění">Rozumím</button>';
  el.querySelector('button').addEventListener('click', function () {
    el.remove();
    localStorage.setItem('cookie-ok', '1');
  });
  document.body.appendChild(el);
})();
