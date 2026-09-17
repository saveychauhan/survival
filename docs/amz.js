// Amazon geo-link: points data-amz shop links at the visitor's country domain.
// No network calls — guesses country from timezone, falls back to language.
// NOTE: tag dexter03d-21 is an Amazon.in ID, so only amazon.in clicks can earn;
// other domains still shop better than a wrong-country storefront.
(function () {
  var TAG = 'dexter03d-21', LINK = '1ad1fede02a40f57a74f102f0a24e3c1';
  var MAP = { IN: 'in', US: 'com', GB: 'co.uk', CA: 'ca', AU: 'com.au', DE: 'de', FR: 'fr', IT: 'it', ES: 'es', NL: 'nl', SE: 'se', PL: 'pl', JP: 'co.jp', AE: 'ae', SA: 'sa', SG: 'sg', BR: 'com.br', MX: 'com.mx', TR: 'com.tr' };
  var CITIES = { kolkata: 'IN', delhi: 'IN', mumbai: 'IN', chennai: 'IN', karachi: 'IN', dhaka: 'IN', colombo: 'IN', kathmandu: 'IN', new_york: 'US', chicago: 'US', denver: 'US', los_angeles: 'US', anchorage: 'US', honolulu: 'US', toronto: 'CA', vancouver: 'CA', london: 'GB', paris: 'FR', berlin: 'DE', rome: 'IT', madrid: 'ES', amsterdam: 'NL', stockholm: 'SE', warsaw: 'PL', tokyo: 'JP', dubai: 'AE', riyadh: 'SA', singapore: 'SG', sao_paulo: 'BR', mexico_city: 'MX', istanbul: 'TR', sydney: 'AU', melbourne: 'AU', auckland: 'AU' };
  function country() {
    try {
      var tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
      var city = (tz.split('/')[1] || '').toLowerCase();
      if (CITIES[city]) return CITIES[city];
    } catch (e) {}
    try {
      var parts = (navigator.language || 'en-IN').split('-');
      if (parts[1]) return parts[1].toUpperCase();
    } catch (e) {}
    return 'IN';
  }
  var tld = MAP[country()] || 'in';
  var url = 'https://www.amazon.' + tld + '/?linkCode=ll2&tag=' + TAG + '&linkId=' + LINK + '&ref_=as_li_ss_tl';
  var els = document.querySelectorAll('a[data-amz]');
  for (var i = 0; i < els.length; i++) els[i].href = url;
})();
