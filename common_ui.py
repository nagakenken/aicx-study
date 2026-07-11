"""
①概要解説・③問題集ページ（build_html.py生成）が共有するCSS/JS定義。
②精読ビューア（reader/配下）とはCSS変数名・localStorageキーの命名を揃え、
ダークモード・文字サイズ設定を3ページ間で共有できるようにしている。
"""

# ─── 認証ゲート ────────────────────────────────────────────────────────
# reader/index.html と同一のパスワードハッシュ・localStorageキーを使う。
AUTH_HASH = 'a18f055ef6aed551b3885777f6582a7b11d281f4ef52542feb8b6e77a4eaca47'
AUTH_EXPIRE_MS = 30 * 24 * 60 * 60 * 1000


def auth_guard_script(redirect_to='index.html'):
    """コンテンツページ先頭に埋め込む認証ガードIIFE。
    未認証ならディープリンク先をsessionStorageに退避してトップページへ。"""
    return f"""(function(){{
  var H='{AUTH_HASH}';
  try{{
    var a=JSON.parse(localStorage.getItem('reader_auth')||'null');
    if(!a||a.h!==H||a.e<Date.now()){{
      try{{ sessionStorage.setItem('auth_return', location.pathname + location.search + location.hash); }}catch(e){{}}
      location.replace('{redirect_to}');
    }}
  }}catch(e){{
    location.replace('{redirect_to}');
  }}
}})();"""


# ─── CSS変数（ダークモード・文字サイズ、readerと共通の命名） ──────────────
THEME_VARS_CSS = """
:root {
  --bg: #f0f2f5; --surface: #ffffff; --surface2: #f5f5f7; --surface3: #e9eaec;
  --text: #1a1a1a; --text2: #444444; --text3: #888888;
  --accent: #2d6a9f; --border: #e5e7eb;
  --font-size: 16px;
}
.dark {
  --bg: #111827; --surface: #1f2937; --surface2: #374151; --surface3: #4b5563;
  --text: #f9fafb; --text2: #d1d5db; --text3: #9ca3af;
  --border: #374151;
}
"""

COMMON_CSS = THEME_VARS_CSS + """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Sans', 'Helvetica Neue', sans-serif;
  font-size: var(--font-size, 16px); line-height: 1.7; color: var(--text);
  background: var(--bg); padding: 12px;
  max-width: 600px; margin: 0 auto;
}

/* ── ヘッダー ───────────────────────────── */
.page-header {
  color: white; border-radius: 12px; padding: 16px 18px; margin-bottom: 12px;
}
.breadcrumb { font-size: 12px; opacity: .75; margin-bottom: 4px; }
.page-title  { font-size: 20px; font-weight: 700; letter-spacing: -.3px; }
.header-meta { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; align-items: center; }
.badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px;
  border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge-ch   { background: rgba(255,255,255,.22); color: white; }
.badge-exam { background: #ff9500; color: white; }

/* ── カード ─────────────────────────────── */
.card {
  background: var(--surface); border-radius: 12px; padding: 18px;
  margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.card-title {
  font-size: calc(var(--font-size) - 2px); font-weight: 700; color: var(--text);
  margin-bottom: 12px; display: flex; align-items: center; gap: 6px;
}
.card-title::before {
  content: ''; display: inline-block; width: 3px; height: 16px;
  background: currentColor; border-radius: 2px; opacity: .6;
}

/* ── 試験ポイント ────────────────────────── */
.exam-point {
  background: #fff8e6; border-left: 3px solid #ff9500;
  border-radius: 0 8px 8px 0; padding: 10px 12px;
  font-size: calc(var(--font-size) - 2px); line-height: 1.75; color: #3a2c00;
}
.dark .exam-point { background: #422006; color: #fde68a; }
.exam-label { font-weight: 700; color: #c67200; font-size: calc(var(--font-size) - 4px); margin-bottom: 5px; }
.dark .exam-label { color: #fbbf24; }

/* ── 概要カード: トピック概要セクション ─── */
.ov-divider { border-top: 1px solid var(--border); margin: 14px 0 10px; }
.ov-section { margin-bottom: 12px; }
.ov-section-title {
  font-size: calc(var(--font-size) - 3px); font-weight: 700;
  border-left: 3px solid #2d6a9f;
  padding: 4px 8px 4px 10px; border-radius: 0 4px 4px 0;
  margin-bottom: 5px; color: var(--text);
}
.ov-section-body {
  font-size: calc(var(--font-size) - 3px); line-height: 1.65; color: var(--text2);
  padding-left: 13px;
}
.ov-body-p { font-size: calc(var(--font-size) - 3px); line-height: 1.65; color: var(--text); margin-bottom: 6px; }

/* ── 学習ステータス ──────────────────────── */
.status-card {
  background: var(--surface); border-radius: 12px; padding: 14px 18px;
  margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.08);
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
}
.status-label { font-size: calc(var(--font-size) - 2px); font-weight: 600; color: var(--text2); flex-shrink: 0; }
.status-btns  { display: flex; gap: 8px; }
.status-btn {
  padding: 8px 18px; border-radius: 8px; font-size: 14px; font-weight: 600;
  cursor: pointer; border: 2px solid transparent; transition: all .15s;
  -webkit-tap-highlight-color: transparent;
}
.btn-done  { background: #e6f4ea; color: #1a7340; border-color: #34a853; }
.btn-later { background: #e8f0fe; color: #1a4bae; border-color: #4285f4; }
.btn-done.active  { background: #34a853; color: white; }
.btn-later.active { background: #4285f4; color: white; }
.dark .btn-done  { background: #052e16; color: #4ade80; }
.dark .btn-later { background: #1e293b; color: #93c5fd; }

/* ── 深掘りノート（アコーディオン） ────────── */
.deepdive-wrap { margin-bottom: 12px; }
.deepdive-btn {
  width: 100%; background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; padding: 13px 16px;
  font-size: calc(var(--font-size) - 2px); font-weight: 600; color: var(--text);
  text-align: left; cursor: pointer;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
  -webkit-tap-highlight-color: transparent;
}
.deepdive-btn .dd-arrow-icon { font-size: 12px; transition: transform .25s; color: #2d6a9f; }
.deepdive-btn.open .dd-arrow-icon { transform: rotate(90deg); }
.deepdive-content {
  display: none; background: var(--surface);
  border: 1px solid var(--border); border-top: none;
  border-radius: 0 0 10px 10px;
  padding: 16px 18px;
}
.deepdive-content.open { display: block; }
.reader-goto-link {
  display: block; margin-top: 14px; padding: 11px 14px;
  background: var(--surface2); border-radius: 8px; text-align: center;
  font-size: calc(var(--font-size) - 3px); font-weight: 600; color: #2d6a9f; text-decoration: none;
}

/* ── 深掘りノート内 コンテンツスタイル ──────── */
.dd-h3 {
  font-size: calc(var(--font-size) - 3px); font-weight: 700;
  border-left: 3px solid #2d6a9f;
  background: var(--surface2);
  padding: 6px 10px; border-radius: 0 6px 6px 0;
  margin: 16px 0 8px; line-height: 1.5; color: var(--text);
}
.dd-h3:first-child { margin-top: 0; }
.dd-p {
  font-size: calc(var(--font-size) - 2px); line-height: 1.8; color: var(--text);
  margin-bottom: 8px;
}
.dd-bullet {
  font-size: calc(var(--font-size) - 2px); line-height: 1.7; color: var(--text);
  margin-bottom: 6px;
  display: flex; align-items: flex-start; gap: 6px;
}
.dd-arrow { font-size: 12px; flex-shrink: 0; margin-top: 4px; }

/* ── コールアウトボックス (POINT) ──────────── */
.callout-box {
  border-left: 3px solid #2d6a9f;
  border-radius: 0 8px 8px 0;
  padding: 10px 12px;
  font-size: calc(var(--font-size) - 2px); line-height: 1.75;
  margin: 10px 0; font-weight: 500;
  display: flex; gap: 8px; align-items: flex-start;
  color: var(--text);
}
.callout-icon { flex-shrink: 0; font-size: 14px; margin-top: 1px; }

/* ── 業務シナリオ ────────────────────────── */
.scenario-section {
  border-left: 3px solid #4285f4;
  border-radius: 0 8px 8px 0;
  background: #f0f4ff;
  padding: 12px 14px; margin-top: 14px; color: #1a1a2e;
}
.dark .scenario-section { background: #1e293b; color: #d1d5db; }
.scenario-label { font-size: calc(var(--font-size) - 4px); font-weight: 700; color: #1a4bae; margin-bottom: 6px; }
.dark .scenario-label { color: #93c5fd; }

/* ── 記憶の鍵 ────────────────────────────── */
.memory-key {
  color: white; border-radius: 10px;
  padding: 14px 16px; margin-top: 16px; text-align: center;
}
.memory-key-label { font-size: 11px; opacity: .75; margin-bottom: 6px; letter-spacing: .5px; }
.memory-key-text  { font-size: calc(var(--font-size) - 2px); font-weight: 700; line-height: 1.6; }

/* ── 理解度チェック ─────────────────────── */
.quiz-hdr {
  font-size: calc(var(--font-size) - 1px); font-weight: 700; color: var(--text);
  margin-bottom: 12px; display: flex; align-items: center; gap: 6px;
}
.quiz-block {
  background: var(--surface); border-radius: 12px; padding: 18px;
  margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.quiz-num      { font-size: calc(var(--font-size) - 4px); font-weight: 700; color: #2d6a9f; margin-bottom: 8px; }
.quiz-question { font-size: calc(var(--font-size) - 1px); font-weight: 600; line-height: 1.6; margin-bottom: 14px; color: var(--text); }
.choices { display: flex; flex-direction: column; gap: 8px; }
.choice-btn {
  background: var(--surface2); border: 2px solid transparent; border-radius: 10px;
  padding: 11px 14px; font-size: calc(var(--font-size) - 2px); text-align: left;
  cursor: pointer; line-height: 1.5; color: var(--text);
  transition: background .15s, border-color .15s;
  -webkit-tap-highlight-color: transparent;
}
.choice-btn:active  { background: var(--surface3); }
.choice-btn.correct { background: #e6f4ea; border-color: #34a853; color: #1a7340; font-weight: 600; }
.choice-btn.wrong   { background: #fce8e6; border-color: #ea4335; color: #b31412; }
.choice-btn.dimmed  { opacity: .4; pointer-events: none; }
.dark .choice-btn.correct { background: #052e16; color: #4ade80; }
.dark .choice-btn.wrong   { background: #450a0a; color: #fca5a5; }
.explanation {
  display: none; background: #e6f4ea; border-radius: 8px;
  padding: 12px 14px; margin-top: 12px; font-size: calc(var(--font-size) - 2px); line-height: 1.6;
  border-left: 3px solid #34a853; color: #14401f;
}
.explanation.show { display: block; }
.ans-label { font-weight: 700; color: #1a7340; font-size: calc(var(--font-size) - 3px); margin-bottom: 5px; }
.explanation.hint { background: #fff8e6; border-left-color: #ff9500; }
.explanation.hint .ans-label { color: #c67200; }
.dark .explanation { background: #052e16; color: #d1fae5; }
.dark .explanation .ans-label { color: #4ade80; }
.dark .explanation.hint { background: #422006; color: #fde68a; }
.dark .explanation.hint .ans-label { color: #fbbf24; }
.action-btns { display: flex; gap: 8px; margin-top: 10px; }
.retry-btn, .next-btn {
  padding: 9px 18px; border-radius: 8px; border: none;
  font-size: 14px; font-weight: 600; cursor: pointer; display: none;
  -webkit-tap-highlight-color: transparent;
}
.retry-btn.show, .next-btn.show { display: inline-block; }
.retry-btn { background: var(--surface2); color: var(--text); }
.next-btn  { background: #34a853; color: white; }
.score-banner {
  display: none; background: linear-gradient(135deg, #34a853, #1a7340);
  color: white; border-radius: 10px; padding: 16px; text-align: center; margin-top: 10px;
}
.score-banner.show { display: block; }
.score-main { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.retake-btn-main {
  display: block; width: 100%; background: #fce8e6; color: #b31412;
  border: 2px solid #ea4335; border-radius: 8px; padding: 10px;
  font-size: 14px; font-weight: 700; cursor: pointer;
  margin-bottom: 12px; -webkit-tap-highlight-color: transparent;
}
.dark .retake-btn-main { background: #450a0a; color: #fca5a5; }
.retake-banner {
  background: #fff3e0; border: 2px solid #ff9500; border-radius: 8px;
  padding: 10px 14px; margin-bottom: 12px;
  font-size: 14px; font-weight: 700; color: #c67200; text-align: center;
}
.dark .retake-banner { background: #422006; color: #fbbf24; }

/* ── ナビ ────────────────────────────────── */
.nav-footer { display: flex; gap: 10px; margin-top: 16px; padding-bottom: 24px; }
.nav-btn {
  flex: 1; padding: 12px; border-radius: 10px; border: 2px solid #2d6a9f;
  background: var(--surface); color: #2d6a9f; font-size: 14px; font-weight: 600;
  cursor: pointer; text-align: center; text-decoration: none;
  display: flex; align-items: center; justify-content: center;
}
.nav-btn.primary { background: #2d6a9f; color: white; }

/* ── 索引 ────────────────────────────────── */
.index-header {
  background: linear-gradient(135deg, #1e3a5f, #2d6a9f); color: white;
  border-radius: 12px; padding: 20px; margin-bottom: 16px; text-align: center;
}
.index-header h1 { font-size: 22px; margin-bottom: 6px; }
.index-header p  { font-size: 13px; opacity: .8; }
.chapter-card { background: var(--surface); border-radius: 12px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,.08); overflow: hidden; }
.chapter-card-header { padding: 14px 18px; font-weight: 700; font-size: 15px;
  color: white; display: flex; align-items: center; gap: 8px; }
.section-link { display: flex; align-items: center; gap: 10px; padding: 11px 18px;
  border-bottom: 1px solid var(--border); text-decoration: none; color: var(--text); font-size: calc(var(--font-size) - 2px); }
.section-link:last-child { border-bottom: none; }
.section-link:active { background: var(--surface2); }
.sec-num { font-weight: 700; font-size: 12px; min-width: 28px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: #ddd; flex-shrink: 0; margin-left: auto; }
.status-dot.done  { background: #34a853; }
.status-dot.later { background: #4285f4; }
.quiz-mini-link {
  flex-shrink: 0; font-size: 15px; text-decoration: none; opacity: .5;
  padding: 4px; margin-left: 4px;
}
.quiz-mini-link:active { opacity: 1; }

/* ── 誤答バッジ ─────────────────────────── */
.fail-badge {
  display: none; margin-left: auto;
  background: #ea4335; color: white;
  font-size: 10px; font-weight: 700;
  border-radius: 10px; padding: 2px 7px;
  flex-shrink: 0; letter-spacing: .2px;
}
.fail-badge.has-fail { display: inline-flex; align-items: center; gap: 2px; }
.section-link.has-fail { background: #fff5f5; }
.dark .section-link.has-fail { background: #1a0f0f; }
.section-link.has-fail:active { background: #fce8e6; }

/* ── 認証パネル ─────────────────────────── */
.auth-card {
  background: var(--surface); border-radius: 12px; padding: 28px 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,.08); margin-bottom: 12px; text-align: center;
}
.auth-icon { font-size: 36px; margin-bottom: 12px; }
.auth-title { font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 6px; }
.auth-desc { font-size: 13px; color: var(--text3); margin-bottom: 20px; }
.auth-input {
  width: 100%; padding: 12px 16px; border: 2px solid var(--border);
  border-radius: 8px; font-size: 16px; outline: none; transition: border-color .2s;
  background: var(--surface); color: var(--text);
}
.auth-input:focus { border-color: #2d6a9f; }
.auth-btn {
  width: 100%; margin-top: 10px; padding: 13px;
  background: #2d6a9f; color: white; border: none;
  border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.auth-btn:active { background: #1e3a5f; }
.auth-error { color: #d32f2f; font-size: 13px; margin-top: 10px; display: none; }
.dark .auth-error { color: #fca5a5; }

/* ── UIツールバー（文字サイズ・ダークモード） ─── */
.ui-toolbar {
  display: flex; align-items: center; gap: 10px; margin-bottom: 12px;
  background: var(--surface); border-radius: 10px; padding: 8px 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.ui-toolbar-label { font-size: 12px; color: var(--text3); flex-shrink: 0; }
.ui-font-slider { flex: 1; accent-color: #2d6a9f; }
.ui-dark-btn {
  flex-shrink: 0; background: var(--surface2); border: none; border-radius: 8px;
  width: 32px; height: 32px; font-size: 15px; cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

/* ── フローティングボタン（目次ドロワー起動） ──── */
.float-home {
  position: fixed; bottom: 22px; right: 14px; z-index: 500;
  background: rgba(26,26,26,.88); color: white !important;
  padding: 9px 16px; border-radius: 22px;
  font-size: 13px; font-weight: 700; border: none; cursor: pointer;
  box-shadow: 0 2px 10px rgba(0,0,0,.25); -webkit-tap-highlight-color: transparent;
}

/* ── 目次ドロワー（全章ツリー、①②③直接遷移） ──── */
.toc-overlay {
  display: none; position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 600;
}
.toc-overlay.open { display: block; }
.toc-drawer {
  position: fixed; left: -300px; top: 0; bottom: 0; width: 280px;
  background: var(--surface); z-index: 601; overflow-y: auto;
  transition: left .22s ease; box-shadow: 2px 0 16px rgba(0,0,0,.25);
}
.toc-drawer.open { left: 0; }
.toc-drawer-header {
  background: #2d6a9f; color: white; padding: 14px 16px;
  font-weight: 700; font-size: 14px; display: flex; align-items: center; justify-content: space-between;
}
.toc-drawer-close { background: none; border: none; color: white; font-size: 18px; cursor: pointer; padding: 2px 6px; }
.toc-ch { border-bottom: 1px solid var(--border); }
.toc-ch-btn {
  display: flex; align-items: center; justify-content: space-between;
  width: 100%; padding: 11px 14px; background: none; border: none;
  color: var(--text); font-size: 13px; font-weight: 700; cursor: pointer; text-align: left;
  -webkit-tap-highlight-color: transparent;
}
.toc-ch-btn:active { background: var(--surface2); }
.toc-ch-arrow { font-size: 11px; color: var(--text3); transition: transform .2s; flex-shrink: 0; margin-left: 6px; }
.toc-ch-btn.open .toc-ch-arrow { transform: rotate(90deg); }
.toc-ch-list { display: none; padding: 2px 0 8px; }
.toc-ch-list.open { display: block; }
.toc-sec-row { display: flex; align-items: center; gap: 4px; padding: 0 8px 0 14px; }
.toc-sec-title {
  flex: 1; display: block; padding: 8px 6px 8px 12px; min-width: 0;
  color: var(--text2); font-size: 12.5px; text-decoration: none;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  -webkit-tap-highlight-color: transparent;
}
.toc-sec-title:active { color: #2d6a9f; }
.toc-sec-title.current { color: #2d6a9f; font-weight: 700; }
.toc-mini {
  flex-shrink: 0; padding: 6px; font-size: 13px; text-decoration: none;
  opacity: .6; border-radius: 6px;
}
.toc-mini:active { opacity: 1; background: var(--surface2); }

/* ── ④ 模擬試験 ─────────────────────────── */
.mex-intro-card {
  background: var(--surface); border-radius: 12px; padding: 22px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,.08); text-align: center; margin-bottom: 12px;
}
.mex-intro-icon { font-size: 40px; margin-bottom: 10px; }
.mex-intro-title { font-size: calc(var(--font-size) + 2px); font-weight: 700; color: var(--text); margin-bottom: 8px; }
.mex-intro-desc { font-size: calc(var(--font-size) - 2px); color: var(--text2); line-height: 1.7; margin-bottom: 18px; }
.mex-last-score {
  background: var(--surface2); border-radius: 10px; padding: 10px 14px;
  font-size: calc(var(--font-size) - 3px); color: var(--text2); margin-bottom: 16px;
}
.mex-start-btn {
  display: block; width: 100%; padding: 14px; border: none; border-radius: 10px;
  background: #2d6a9f; color: white; font-size: calc(var(--font-size) - 1px); font-weight: 700;
  cursor: pointer; -webkit-tap-highlight-color: transparent;
}
.mex-progress-wrap {
  background: var(--surface); border-radius: 10px; padding: 10px 14px;
  margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.mex-progress-label { font-size: calc(var(--font-size) - 4px); color: var(--text3); margin-bottom: 6px; display: flex; justify-content: space-between; }
.mex-progress-bar { height: 6px; background: var(--surface2); border-radius: 3px; overflow: hidden; }
.mex-progress-fill { height: 100%; background: #2d6a9f; transition: width .2s; }
.mex-result-score {
  text-align: center; padding: 20px; background: linear-gradient(135deg, #2d6a9f, #1e3a5f);
  color: white; border-radius: 12px; margin-bottom: 14px;
}
.mex-result-score .big { font-size: 36px; font-weight: 700; }
.mex-result-table { width: 100%; border-collapse: collapse; font-size: calc(var(--font-size) - 3px); }
.mex-result-table th, .mex-result-table td { padding: 7px 8px; text-align: left; border-bottom: 1px solid var(--border); color: var(--text); }
.mex-result-table th { color: var(--text3); font-weight: 600; }
.mex-result-bar-wrap { display: inline-block; width: 60px; height: 6px; background: var(--surface2); border-radius: 3px; overflow: hidden; vertical-align: middle; margin-right: 6px; }
.mex-result-bar { height: 100%; background: #34a853; }
.mex-retry-btn {
  display: block; width: 100%; padding: 13px; border: none; border-radius: 10px;
  background: var(--surface2); color: var(--text); font-size: calc(var(--font-size) - 2px); font-weight: 700;
  cursor: pointer; margin-top: 14px; -webkit-tap-highlight-color: transparent;
}
"""

# ─── JavaScript ──────────────────────────────────────────────────────
COMMON_JS = """
function saveStatus(k, v) { localStorage.setItem(k, v); }
function loadStatus(k) { return localStorage.getItem(k); }

function setStatus(sid, val, btn) {
  saveStatus('s_' + sid, val);
  btn.closest('.status-btns').querySelectorAll('.status-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

function toggleDeepDive(btn) {
  btn.classList.toggle('open');
  btn.nextElementSibling.classList.toggle('open');
}

var QS = {};

function answer(qid, ci, correct) {
  if (QS[qid] && QS[qid].done) return;
  QS[qid] = { done: true, ok: ci === correct };

  var btns = document.querySelectorAll('#q' + qid + ' .choice-btn');
  btns.forEach(function(b, i) {
    if (i === ci)      b.classList.add(i === correct ? 'correct' : 'wrong');
    else if (i !== correct) b.classList.add('dimmed');
  });

  var expl  = document.getElementById('e' + qid);
  var retry = document.getElementById('r' + qid);
  var next  = document.getElementById('n' + qid);
  expl.classList.add('show');

  var sid      = qid.replace(/_\\d+$/, '');
  var section  = document.getElementById(sid);
  var isRetake = section && section.classList.contains('retake-mode');

  if (ci === correct) {
    if (next) next.classList.add('show');
    localStorage.removeItem('qfail_' + qid);
    if (isRetake) localStorage.removeItem('qwrong_' + qid);
  } else {
    expl.classList.add('hint');
    if (retry) retry.classList.add('show');
    localStorage.setItem('qfail_' + qid, '1');
    localStorage.setItem('qwrong_' + qid, '1');
  }
  updateRetakeBtn(sid);
}

function resetQuizBlock(qid) {
  QS[qid] = null;
  document.querySelectorAll('#q' + qid + ' .choice-btn').forEach(function(b) {
    b.classList.remove('correct', 'wrong', 'dimmed');
  });
  var expl = document.getElementById('e' + qid);
  if (expl) expl.classList.remove('show', 'hint');
  var retry = document.getElementById('r' + qid);
  if (retry) retry.classList.remove('show');
  var next = document.getElementById('n' + qid);
  if (next) next.classList.remove('show');
}

function retryQ(qid) {
  resetQuizBlock(qid);
}

function showNext(nqid) {
  var sid = nqid.replace(/_\\d+$/, '');
  var section = document.getElementById(sid);
  if (section && section.classList.contains('retake-mode')) {
    retakeAdvance(sid);
    return;
  }
  var el = document.getElementById('q' + nqid);
  if (el) { el.style.display = 'block'; el.scrollIntoView({behavior:'smooth', block:'start'}); }
}

function showScore(sid, total) {
  var section = document.getElementById(sid);
  if (section && section.classList.contains('retake-mode')) {
    retakeAdvance(sid);
    return;
  }
  var ok = 0;
  for (var i = 1; i <= total; i++) {
    var st = QS[sid + '_' + i];
    if (st && st.ok) ok++;
  }
  var banner = document.getElementById('sc_' + sid);
  if (banner) {
    banner.querySelector('.score-main').textContent = ok + ' / ' + total + ' 問 正解';
    banner.classList.add('show');
    banner.scrollIntoView({behavior:'smooth', block:'start'});
  }
}

function startRetake(sid) {
  var section = document.getElementById(sid);
  if (!section) return;

  var wrongQids = [];
  for (var i = 0; i < localStorage.length; i++) {
    var key = localStorage.key(i);
    if (key && key.startsWith('qwrong_' + sid + '_')) {
      wrongQids.push(key.replace('qwrong_', ''));
    }
  }
  if (!wrongQids.length) return;
  wrongQids.sort(function(a, b) {
    return parseInt(a.split('_').pop()) - parseInt(b.split('_').pop());
  });

  section.classList.add('retake-mode');
  section.dataset.retakeQueue = JSON.stringify(wrongQids);
  section.dataset.retakeIdx   = '0';

  var score = document.getElementById('sc_' + sid);
  if (score) score.classList.remove('show');

  section.querySelectorAll('.quiz-block').forEach(function(block) {
    block.style.display = 'none';
  });
  wrongQids.forEach(function(qid) { resetQuizBlock(qid); });

  var first = document.getElementById('q' + wrongQids[0]);
  if (first) { first.style.display = 'block'; first.scrollIntoView({behavior:'smooth', block:'start'}); }

  var banner = document.getElementById('rtk_banner_' + sid);
  if (banner) banner.style.display = 'block';

  var btn = document.getElementById('rtk_' + sid);
  if (btn) btn.style.display = 'none';
}

function retakeAdvance(sid) {
  var section = document.getElementById(sid);
  if (!section || !section.classList.contains('retake-mode')) return;
  var queue = JSON.parse(section.dataset.retakeQueue || '[]');
  var idx   = parseInt(section.dataset.retakeIdx || '0');

  var cur = document.getElementById('q' + queue[idx]);
  if (cur) cur.style.display = 'none';

  idx++;
  section.dataset.retakeIdx = String(idx);

  if (idx < queue.length) {
    var nxt = document.getElementById('q' + queue[idx]);
    if (nxt) { nxt.style.display = 'block'; nxt.scrollIntoView({behavior:'smooth', block:'start'}); }
  } else {
    endRetake(sid);
  }
}

function endRetake(sid) {
  var section = document.getElementById(sid);
  if (!section) return;

  section.classList.remove('retake-mode');
  delete section.dataset.retakeQueue;
  delete section.dataset.retakeIdx;

  var banner = document.getElementById('rtk_banner_' + sid);
  if (banner) banner.style.display = 'none';

  section.querySelectorAll('.quiz-block').forEach(function(block, i) {
    var qid = block.id.replace(/^q/, '');
    resetQuizBlock(qid);
    block.style.display = (i === 0) ? 'block' : 'none';
  });

  updateRetakeBtn(sid);
}

function updateRetakeBtn(sid) {
  var count = 0;
  for (var i = 0; i < localStorage.length; i++) {
    var key = localStorage.key(i);
    if (key && key.startsWith('qwrong_' + sid + '_')) count++;
  }
  var btn = document.getElementById('rtk_' + sid);
  if (!btn) return;
  if (count > 0) {
    btn.textContent = '❌ ' + count + '問 再テスト';
    btn.style.display = 'block';
  } else {
    btn.style.display = 'none';
  }
}

function initRetakeBtns() {
  document.querySelectorAll('section[id^="ch"]').forEach(function(sec) {
    updateRetakeBtn(sec.id);
  });
}

/* ── 文字サイズ・ダークモード（readerと共通のlocalStorageキー） ───── */
function applyFontSize(px) {
  document.documentElement.style.setProperty('--font-size', px + 'px');
}

function applyDark(on) {
  document.body.classList.toggle('dark', on);
  var btn = document.getElementById('ui-dark-btn');
  if (btn) btn.textContent = on ? '☀️' : '🌙';
}

function initThemeControls() {
  var fontSize = parseInt(localStorage.getItem('reader_fontSize') || '16', 10);
  var darkMode = localStorage.getItem('reader_dark') === 'true';
  applyFontSize(fontSize);
  applyDark(darkMode);

  var slider = document.getElementById('ui-font-slider');
  if (slider) {
    slider.value = fontSize;
    slider.oninput = function() {
      fontSize = +slider.value;
      applyFontSize(fontSize);
      localStorage.setItem('reader_fontSize', fontSize);
    };
  }
  var darkBtn = document.getElementById('ui-dark-btn');
  if (darkBtn) {
    darkBtn.onclick = function() {
      darkMode = !darkMode;
      applyDark(darkMode);
      localStorage.setItem('reader_dark', darkMode);
    };
  }
}

/* ── 目次ドロワー（フローティングボタンから起動） ───────────── */
function toggleTocDrawer() {
  var d = document.getElementById('tocDrawer');
  var o = document.getElementById('tocOverlay');
  if (d) d.classList.toggle('open');
  if (o) o.classList.toggle('open');
}

function closeTocDrawer() {
  var d = document.getElementById('tocDrawer');
  var o = document.getElementById('tocOverlay');
  if (d) d.classList.remove('open');
  if (o) o.classList.remove('open');
}

function toggleTocCh(btn) {
  btn.classList.toggle('open');
  btn.nextElementSibling.classList.toggle('open');
}

window.addEventListener('load', function() {
  document.querySelectorAll('.status-btns[data-sid]').forEach(function(wrap) {
    var v = loadStatus('s_' + wrap.dataset.sid);
    if (v) {
      var b = wrap.querySelector('[data-val="' + v + '"]');
      if (b) b.classList.add('active');
    }
  });
  initRetakeBtns();
  initThemeControls();
});
"""


def build_toc_tree_html(all_sections, chapter_titles, ch_colors, root_prefix='', current_sid=None):
    """全章・全セクションのツリーHTML（章アコーディオン＋各セクションから①②③へのミニリンク）。
    root_prefix: サイトルート直下のページ('' = overview/quiz/index)からの相対パス。
    reader/chN.html から呼ぶ場合は '../' を渡す（②リンクだけは同ディレクトリ相対で別途組む）。
    current_sid: 現在表示中のセクションID。該当章を自動展開しハイライトする。"""
    import html as _htmllib
    e = _htmllib.escape
    by_ch = {}
    for s in all_sections:
        by_ch.setdefault(s['ch'], []).append(s)

    current_ch = int(current_sid.split('_')[0][2:]) if current_sid else None

    chapters_html = ''
    for ch_num in sorted(by_ch):
        color = ch_colors.get(ch_num, ch_colors[1])
        title = chapter_titles.get(ch_num, '')
        is_open = (ch_num == current_ch)

        secs_html = ''
        for sec in by_ch[ch_num]:
            sid = f'ch{sec["ch"]:02d}_s{sec["s"]:02d}'
            is_current = (sid == current_sid)
            reader_href = f'{root_prefix}reader/ch{ch_num}.html#sec-{sec["s"]}'
            secs_html += f'''
        <div class="toc-sec-row">
          <a class="toc-sec-title{' current' if is_current else ''}" href="{root_prefix}ch{ch_num:02d}_overview.html#{sid}">S{sec["s"]:02d}｜{e(sec["title"])}</a>
          <a class="toc-mini" href="{reader_href}" title="精読ビューア">📖</a>
          <a class="toc-mini" href="{root_prefix}ch{ch_num:02d}_quiz.html#{sid}" title="理解度チェック">📝</a>
        </div>'''

        chapters_html += f'''
    <div class="toc-ch">
      <button class="toc-ch-btn{' open' if is_open else ''}" style="border-left:4px solid {color['accent']};" onclick="toggleTocCh(this)">
        <span>Ch.{ch_num:02d}｜{e(title)}</span><span class="toc-ch-arrow">▸</span>
      </button>
      <div class="toc-ch-list{' open' if is_open else ''}">{secs_html}
      </div>
    </div>'''

    return chapters_html


def toc_drawer_html(tree_html, index_href='index.html', mock_exam_href='mock_exam.html'):
    return f'''
<div class="toc-overlay" id="tocOverlay" onclick="closeTocDrawer()"></div>
<nav class="toc-drawer" id="tocDrawer">
  <div class="toc-drawer-header">
    <span>📚 目次</span>
    <button class="toc-drawer-close" onclick="closeTocDrawer()">✕</button>
  </div>
  <div style="padding:8px 14px;border-bottom:1px solid var(--border);">
    <a href="{index_href}" style="display:block;color:var(--text2);font-size:13px;text-decoration:none;padding:6px 0;">🏠 学習マップ（全体トップ）</a>
    <a href="{mock_exam_href}" style="display:block;color:var(--text2);font-size:13px;text-decoration:none;padding:6px 0;">🎯 ④ 模擬試験</a>
  </div>
  {tree_html}
</nav>'''


def float_nav_html():
    """目次ドロワーを開くフローティングボタン。"""
    return '<button class="float-home" onclick="toggleTocDrawer()">☰ 目次</button>'


def theme_toolbar_html():
    return '''
<div class="ui-toolbar">
  <span class="ui-toolbar-label">文字サイズ</span>
  <input type="range" class="ui-font-slider" id="ui-font-slider" min="13" max="22" step="1" value="16">
  <button class="ui-dark-btn" id="ui-dark-btn">🌙</button>
</div>'''


# ─── ④ 模擬試験 ────────────────────────────────────────────────────────
# 章別出題数（README_mock_exam.md の配分提案。合計50問）
MOCK_EXAM_QUOTA = {1: 12, 2: 5, 3: 11, 4: 6, 5: 8, 6: 8}

MOCK_EXAM_JS = """
var MEX_QUOTA = """ + str(MOCK_EXAM_QUOTA) + """;
var MEX_DATA = null;
var MEX_SESSION = null;

function mexLoadData() {
  if (MEX_DATA) return MEX_DATA;
  var raw = JSON.parse(document.getElementById('mock-exam-data').textContent);
  var flat = [];
  raw.forEach(function(sec) {
    sec.quizzes.forEach(function(q, idx) {
      var qq = {};
      for (var k in q) qq[k] = q[k];
      qq.meid = 'm_ch' + sec.ch + '_s' + sec.s + '_' + idx;
      qq.ch = sec.ch; qq.s = sec.s; qq.secTitle = sec.title;
      flat.push(qq);
    });
  });
  MEX_DATA = flat;
  return flat;
}

function mexGetResult(meid) { return localStorage.getItem('mex_result_' + meid); }

function mexShuffle(arr) {
  var a = arr.slice();
  for (var i = a.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = a[i]; a[i] = a[j]; a[j] = t;
  }
  return a;
}

/* 弱点演習モードの拡張ポイント: filterFn(q)->bool を渡せば章配分の代わりに
   q_type/ch 等での絞り込み出題に流用できる（未実装、後日対応）。 */
function mexSelectQuestions() {
  var all = mexLoadData();
  var selected = [];
  Object.keys(MEX_QUOTA).forEach(function(chStr) {
    var ch = parseInt(chStr, 10);
    var quota = MEX_QUOTA[ch];
    var pool = all.filter(function(q) { return q.ch === ch; });
    var unseen  = mexShuffle(pool.filter(function(q) { return mexGetResult(q.meid) === null; }));
    var wrong   = mexShuffle(pool.filter(function(q) { return mexGetResult(q.meid) === 'wrong'; }));
    var correct = mexShuffle(pool.filter(function(q) { return mexGetResult(q.meid) === 'correct'; }));
    var picked = unseen.concat(wrong).concat(correct).slice(0, quota);
    selected = selected.concat(picked);
  });
  return mexShuffle(selected);
}

function mexEsc(str) {
  var d = document.createElement('div');
  d.textContent = str == null ? '' : str;
  return d.innerHTML;
}

function mexExplBody(expl) {
  return (expl || '').replace(/^\\u6b63\\u89e3[\\uff1a:]\\s*[ABCD][|\\uff5c]?\\s*/, '');
}

function mexTodayStr() {
  var d = new Date();
  return d.getFullYear() + '/' + (d.getMonth() + 1) + '/' + d.getDate();
}

function mexRenderIntro() {
  var app = document.getElementById('mexApp');
  if (!app) return;
  var lastRaw = localStorage.getItem('mex_last_score');
  var lastHtml = '';
  if (lastRaw) {
    try {
      var last = JSON.parse(lastRaw);
      lastHtml = '<div class="mex-last-score">前回スコア：' + last.correct + ' / ' + last.total + '（' + last.date + '）</div>';
    } catch (e) {}
  }
  app.innerHTML =
    '<div class="mex-intro-card">' +
      '<div class="mex-intro-icon">\\ud83c\\udfaf</div>' +
      '<div class="mex-intro-title">模擬試験</div>' +
      '<div class="mex-intro-desc">全128問の中から章別配分で50問を出題します。<br>未回答・誤答だった問題を優先的に出題します。</div>' +
      lastHtml +
      '<button class="mex-start-btn" onclick="mexStart()">模擬試験を始める</button>' +
    '</div>';
}

function mexStart() {
  MEX_SESSION = { questions: mexSelectQuestions(), idx: 0, correctCount: 0, answers: [] };
  mexRenderQuestion();
}

function mexRenderQuestion() {
  var s = MEX_SESSION;
  var q = s.questions[s.idx];
  var letters = ['A', 'B', 'C', 'D'].filter(function(l) { return q.choices[l]; });
  var correctIdx = letters.indexOf(q.correct_letter);
  var choicesHtml = letters.map(function(lt, li) {
    return '<button class="choice-btn" onclick="mexAnswer(' + li + ')">' + lt + '\\u3000' + mexEsc(q.choices[lt]) + '</button>';
  }).join('');
  var pct = Math.round((s.idx / s.questions.length) * 100);

  document.getElementById('mexApp').innerHTML =
    '<div class="mex-progress-wrap">' +
      '<div class="mex-progress-label"><span>問 ' + (s.idx + 1) + ' ／ ' + s.questions.length + '</span><span>Ch.' + q.ch + '</span></div>' +
      '<div class="mex-progress-bar"><div class="mex-progress-fill" style="width:' + pct + '%;"></div></div>' +
    '</div>' +
    '<div class="quiz-block" id="mexQBlock">' +
      '<div class="quiz-question">' + mexEsc(q.question) + '</div>' +
      '<div class="choices">' + choicesHtml + '</div>' +
      '<div class="explanation" id="mexExpl"><div class="ans-label">✅ 正解：' + q.correct_letter + '</div>' + mexEsc(mexExplBody(q.explanation)) + '</div>' +
      '<div class="action-btns"><button class="next-btn" id="mexNextBtn" onclick="mexNext()">' + ((s.idx + 1 === s.questions.length) ? '結果を見る' : '次の問題へ') + ' →</button></div>' +
    '</div>';

  window.__mexCorrectIdx = correctIdx;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function mexAnswer(ci) {
  var s = MEX_SESSION;
  var q = s.questions[s.idx];
  var correctIdx = window.__mexCorrectIdx;
  var btns = document.querySelectorAll('#mexQBlock .choice-btn');
  btns.forEach(function(b, i) {
    b.style.pointerEvents = 'none';
    if (i === ci) b.classList.add(i === correctIdx ? 'correct' : 'wrong');
    else if (i !== correctIdx) b.classList.add('dimmed');
  });
  var ok = (ci === correctIdx);
  var expl = document.getElementById('mexExpl');
  expl.classList.add('show');
  if (!ok) expl.classList.add('hint');
  localStorage.setItem('mex_result_' + q.meid, ok ? 'correct' : 'wrong');
  s.answers.push({ meid: q.meid, ch: q.ch, q_type: q.q_type, ok: ok });
  if (ok) s.correctCount++;
  document.getElementById('mexNextBtn').classList.add('show');
}

function mexNext() {
  var s = MEX_SESSION;
  s.idx++;
  if (s.idx < s.questions.length) {
    mexRenderQuestion();
  } else {
    mexShowResults();
  }
}

function mexShowResults() {
  var s = MEX_SESSION;
  var byCh = {}, byType = {};
  s.answers.forEach(function(a) {
    byCh[a.ch] = byCh[a.ch] || { ok: 0, total: 0 };
    byCh[a.ch].total++; if (a.ok) byCh[a.ch].ok++;
    var t = a.q_type || '(未分類)';
    byType[t] = byType[t] || { ok: 0, total: 0 };
    byType[t].total++; if (a.ok) byType[t].ok++;
  });

  var chRows = Object.keys(byCh).sort(function(a, b) { return a - b; }).map(function(ch) {
    var d = byCh[ch]; var pct = Math.round(d.ok / d.total * 100);
    return '<tr><td>Ch.' + ch + '</td><td><span class="mex-result-bar-wrap"><span class="mex-result-bar" style="width:' + pct + '%;"></span></span>' + d.ok + '/' + d.total + '</td></tr>';
  }).join('');

  var typeRows = Object.keys(byType).map(function(t) {
    var d = byType[t]; var pct = Math.round(d.ok / d.total * 100);
    return '<tr><td>' + mexEsc(t) + '</td><td><span class="mex-result-bar-wrap"><span class="mex-result-bar" style="width:' + pct + '%;"></span></span>' + d.ok + '/' + d.total + '</td></tr>';
  }).join('');

  var total = s.questions.length;
  var scorePct = Math.round(s.correctCount / total * 100);

  localStorage.setItem('mex_last_score', JSON.stringify({ correct: s.correctCount, total: total, date: mexTodayStr() }));

  document.getElementById('mexApp').innerHTML =
    '<div class="mex-result-score"><div class="big">' + s.correctCount + ' / ' + total + '</div><div>正答率 ' + scorePct + '%</div></div>' +
    '<div class="card"><div class="card-title">章別正答率</div><table class="mex-result-table">' + chRows + '</table></div>' +
    '<div class="card"><div class="card-title">出題タイプ別正答率</div><table class="mex-result-table">' + typeRows + '</table></div>' +
    '<button class="mex-retry-btn" onclick="mexRenderIntro()">もう一度挑戦する</button>';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

window.addEventListener('load', function() {
  if (document.getElementById('mexApp')) mexRenderIntro();
});
"""


def build_mock_exam_page_body():
    return '<div class="card" id="mexApp"></div>'
