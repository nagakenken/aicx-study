"""
reader/ch1.html〜ch6.html に対する加算的パッチ:
  1. 認証ガードのリダイレクト先を ./index.html → ../index.html に変更（トップページ認証ゲート対応）
     未認証時はディープリンク復帰用に sessionStorage へ退避
  2. ページロード後、URLのhash（#sec-N）に該当する要素があればスクロール
  3. フローティングナビメニュー（① 概要解説 / ③ 理解度チェック / 全体目次へのリンク）を追加
     現在表示中のセクションをIntersectionObserverで検知し、リンク先を追従させる
"""
import os

READER_DIR = r"C:\Users\mikli\Downloads\AICX学習\reader"

OLD_GUARD = "(function(){var H='a18f055ef6aed551b3885777f6582a7b11d281f4ef52542feb8b6e77a4eaca47';try{var a=JSON.parse(localStorage.getItem('reader_auth')||'null');if(!a||a.h!==H||a.e<Date.now()){location.replace('./index.html');}}catch(e){location.replace('./index.html');}})();"

NEW_GUARD = "(function(){var H='a18f055ef6aed551b3885777f6582a7b11d281f4ef52542feb8b6e77a4eaca47';try{var a=JSON.parse(localStorage.getItem('reader_auth')||'null');if(!a||a.h!==H||a.e<Date.now()){try{sessionStorage.setItem('auth_return', location.pathname + location.search + location.hash);}catch(e){}location.replace('../index.html');}}catch(e){location.replace('../index.html');}})();"

HASH_SCROLL_MARKER = "document.querySelectorAll('.section-block').forEach(el => observer.observe(el));"

HASH_SCROLL_ADDITION = HASH_SCROLL_MARKER + """

if (location.hash) {
  var __target = document.querySelector(location.hash);
  if (__target) setTimeout(function() { __target.scrollIntoView({behavior:'instant', block:'start'}); }, 50);
}"""

FLOAT_NAV_CSS = """
<style>
.float-nav-wrap { position: fixed; bottom: 22px; right: 14px; z-index: 500; }
.float-home {
  background: rgba(26,26,26,.88); color: #fff !important;
  padding: 9px 16px; border-radius: 22px;
  font-size: 13px; font-weight: 700; border: none; cursor: pointer;
  box-shadow: 0 2px 10px rgba(0,0,0,.25);
}
.float-nav-menu {
  display: none; position: absolute; bottom: 46px; right: 0;
  background: var(--surface); border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,.25);
  padding: 8px; min-width: 210px;
}
.float-nav-menu.open { display: block; }
.fnav-sec-label { font-size: 11px; color: var(--text3); padding: 6px 14px 2px; }
.fnav-item {
  display: block; padding: 10px 14px; font-size: 14px; color: var(--text);
  text-decoration: none; border-radius: 8px;
}
.fnav-item:active { background: var(--surface2); }
.fnav-item.current { color: var(--accent); font-weight: 700; }
.fnav-divider { border-top: 1px solid var(--border); margin: 6px 4px; }
</style>
"""

FLOAT_NAV_HTML = """
<div class="float-nav-wrap">
  <button class="float-home" onclick="document.getElementById('floatNavMenu').classList.toggle('open')">📚 目次 ▾</button>
  <div class="float-nav-menu" id="floatNavMenu">
    <div class="fnav-sec-label" id="fnavSecLabel"></div>
    <a class="fnav-item" id="fnavOverview" href="#">① 概要解説</a>
    <a class="fnav-item current">② 精読ビューア</a>
    <a class="fnav-item" id="fnavQuiz" href="#">③ 理解度チェック</a>
    <div class="fnav-divider"></div>
    <a class="fnav-item" href="../index.html">📚 学習マップ（全章目次）</a>
  </div>
</div>
"""

FLOAT_NAV_JS = """
<script>
(function() {
  var __fnavData = JSON.parse(document.getElementById('content').textContent);
  function updateFloatNavLinks(secNum) {
    var overviewEl = document.getElementById('fnavOverview');
    var quizEl     = document.getElementById('fnavQuiz');
    var labelEl    = document.getElementById('fnavSecLabel');
    var chNum = __fnavData.ch;
    var sid = 'ch' + String(chNum).padStart(2,'0') + '_s' + String(secNum).padStart(2,'0');
    if (overviewEl) overviewEl.href = '../ch' + String(chNum).padStart(2,'0') + '_overview.html#' + sid;
    if (quizEl)     quizEl.href     = '../ch' + String(chNum).padStart(2,'0') + '_quiz.html#' + sid;
    if (labelEl)    labelEl.textContent = 'Ch.' + String(chNum).padStart(2,'0') + '-S' + String(secNum).padStart(2,'0');
  }
  document.addEventListener('click', function(e) {
    var wrap = document.querySelector('.float-nav-wrap');
    if (wrap && !wrap.contains(e.target)) {
      var menu = document.getElementById('floatNavMenu');
      if (menu) menu.classList.remove('open');
    }
  });
  var __hashMatch = location.hash.match(/^#sec-(\\d+)$/);
  if (__hashMatch) {
    updateFloatNavLinks(parseInt(__hashMatch[1], 10));
  } else if (__fnavData.sections && __fnavData.sections.length) {
    updateFloatNavLinks(__fnavData.sections[0].s);
  }
  var fnavObserver = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        var m = entry.target.id.match(/^sec-(\\d+)$/);
        if (m) updateFloatNavLinks(parseInt(m[1], 10));
      }
    });
  }, { rootMargin: '-35% 0px -50% 0px' });
  document.querySelectorAll('.section-block').forEach(function(el) { fnavObserver.observe(el); });
})();
</script>
"""


def patch_file(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()

    changed = []

    if OLD_GUARD in content:
        content = content.replace(OLD_GUARD, NEW_GUARD)
        changed.append('auth_guard')
    else:
        print(f'  WARNING: guard marker not found in {path}')

    if HASH_SCROLL_MARKER in content and HASH_SCROLL_ADDITION not in content:
        content = content.replace(HASH_SCROLL_MARKER, HASH_SCROLL_ADDITION, 1)
        changed.append('hash_scroll')
    elif HASH_SCROLL_MARKER not in content:
        print(f'  WARNING: hash-scroll marker not found in {path}')

    if '</body>' in content and 'float-nav-wrap' not in content:
        addition = FLOAT_NAV_CSS + FLOAT_NAV_HTML + FLOAT_NAV_JS + '\n</body>'
        content = content.replace('</body>', addition, 1)
        changed.append('float_nav')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'{os.path.basename(path)}: {", ".join(changed) if changed else "NO CHANGES"}')


def main():
    for n in range(1, 7):
        patch_file(os.path.join(READER_DIR, f'ch{n}.html'))


if __name__ == '__main__':
    main()
