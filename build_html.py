# AICX 学習支援 HTML ジェネレータ v4
# Usage: python build_html.py
# v4: ①概要解説／②精読ビューア／③問題集の3ページ構成化、フローティングナビ、
#     文字サイズ・ダークモード共通化、トップページ認証ゲート

import json, re, os, html as htmllib
from common_ui import (
    COMMON_CSS, COMMON_JS, AUTH_HASH, AUTH_EXPIRE_MS,
    auth_guard_script, float_nav_html, theme_toolbar_html,
)

OUT_DIR = r"C:\Users\mikli\Downloads\AICX学習"

CHAPTER_TITLES = {
    1: "生成AIとAIエージェントの基礎",
    2: "業務の基礎",
    3: "AIデータリテラシーとマネジメント",
    4: "自動化レベルとワークフロー設計",
    5: "人と組織から考えるAI時代の組織設計",
    6: "AIエージェントを実装する5Dモデル",
}

# 章別カラーパレット
CH_COLORS = {
    1: {'accent': '#2d6a9f', 'dark': '#1e3a5f', 'light': '#e8f0fe', 'mid': '#5a9fd4'},
    2: {'accent': '#6b4fa8', 'dark': '#4a3070', 'light': '#f0ebff', 'mid': '#9b7ed4'},
    3: {'accent': '#2a8a7a', 'dark': '#1a5e52', 'light': '#e0f5f0', 'mid': '#4db8a6'},
    4: {'accent': '#c45a0a', 'dark': '#8a3e06', 'light': '#fff0e0', 'mid': '#e07a30'},
    5: {'accent': '#a01850', 'dark': '#701035', 'light': '#ffe0ec', 'mid': '#cc4878'},
    6: {'accent': '#2a6e3a', 'dark': '#1a4a26', 'light': '#e0f4e6', 'mid': '#4a9e5c'},
}

# PDF抽出時に欠落した文字を補正
KNOWLEDGE_FIXUPS = {
    'ch06_s01': [('Dモデルの全体像', '5Dモデルの全体像')],
}

CALLOUT_MARKER = '##CALLOUT##'   # POINT行の代替マーカー

# ─── テキスト処理 ─────────────────────────────────────────────────────

NOISE_RE = re.compile(
    r'^nagaken.*$'
    r'|^AIエージェント・ストラテジスト資格$'
    r'|^Chapter\d+.*$'
    r'|^CHAPTER\s*(—|\d+)$'
    r'|^CONTENTS$'
    r'|^判断\s*\d+$'
    r'|^\d{2,}$'
    r'|^知識$|^業務シナリオ$|^学習のポイント$|^理解度チェック$'
)

SENTENCE_END_RE = re.compile(r'[。！？）」』…]$')
BULLET_RE       = re.compile(r'^[・‧•]')
FRAG_START_RE   = re.compile(r'^[がにをはもでとやからまでより]|^[るれりたてて]|^こと|^ため')
FRAG_END_RE     = re.compile(r'[ッが与判化]$')  # カタカナ促音・助詞・動詞語幹で終わる断片


def clean_lines(raw_text: str) -> list[str]:
    """ノイズ除去・POINT→コールアウトマーカー変換"""
    result = []
    for line in raw_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line == 'POINT':
            result.append(CALLOUT_MARKER)  # POINT → コールアウトマーカーに変換
            continue
        if NOISE_RE.match(line):
            continue
        result.append(line)
    return result


def _is_heading(line: str) -> bool:
    """見出し判定: 短い完結した語句かどうか"""
    if line.startswith(CALLOUT_MARKER):
        return False
    if len(line) > 40:
        return False
    if SENTENCE_END_RE.search(line):
        return False
    if BULLET_RE.match(line):
        return False
    if len(line) < 4:
        return False
    if FRAG_START_RE.match(line):
        return False
    # 文中に句点 → 文の途中から切り取られた断片
    if '。' in line:
        return False
    # 助詞・動詞語幹・促音で終わる → 行末で切れた断片
    if FRAG_END_RE.search(line):
        return False
    # 開き括弧があるが閉じ括弧がない → 行途中で切れた断片
    if '「' in line and '」' not in line:
        return False
    return True


def join_sentences(lines: list[str]) -> list[str]:
    """
    PDF折り返し行を結合して文単位のリストに変換。
    CALLOUT_MARKER直後の文はコールアウトとしてプレフィックスをつける。
    バッファ自身が見出し候補かどうかを最初に判定（→見出し+本文の意図しない結合を防ぐ）。
    """
    result: list[str] = []
    buf = ''
    next_is_callout = False

    for line in lines:
        # コールアウトマーカー処理
        if line == CALLOUT_MARKER:
            if buf:
                result.append(buf)
                buf = ''
            next_is_callout = True
            continue

        if not buf:
            prefix = CALLOUT_MARKER if next_is_callout else ''
            buf = prefix + line
            next_is_callout = False
            continue

        next_is_callout = False

        # ① バッファ自身が見出し → 単独で確定
        if _is_heading(buf):
            result.append(buf)
            buf = line
            continue

        # ② バッファが文末で終了 → 確定
        if SENTENCE_END_RE.search(buf):
            result.append(buf)
            buf = line
            continue

        # ③ バッファが未完文 → 見出しなら切る、短いプレフィックスなら結合
        if _is_heading(line):
            if len(buf) <= 3:
                buf = buf + line
            else:
                result.append(buf)
                buf = line
        else:
            buf = buf + line

    if buf:
        result.append(buf)

    return result


def _extract_sections_from_knowledge(knowledge: str):
    """
    knowledgeテキストを解析してH3見出し別に [(heading, [body_sents])] を返す。
    H3見出しが1つもない場合は [(None, [先頭の非コールアウト文×3])] を返す。
    """
    lines = clean_lines(knowledge)
    sents = join_sentences(lines)

    sections = []
    cur_h, cur_body = None, []
    for sent in sents:
        is_callout = sent.startswith(CALLOUT_MARKER)
        if _is_heading(sent):
            if cur_h is not None or cur_body:
                sections.append((cur_h, cur_body))
            cur_h, cur_body = sent, []
        elif not is_callout:
            cur_body.append(sent)
        # コールアウトはbodyには含めない（概要には不要）

    if cur_h is not None or cur_body:
        sections.append((cur_h, cur_body))

    # H3なしの場合: bodyを先頭から取り出す
    if all(h is None for h, _ in sections):
        body_all = [s for h, bs in sections for s in bs]
        return [(None, body_all[:3])]

    # H3あり・最初の要素がH3なし(intro文)の場合はスキップ
    return [(h, bs) for h, bs in sections if h is not None]


def _extract_memory_key(knowledge_sents: list, quizzes: list, exam_focus: str) -> str:
    """
    記憶の鍵テキスト生成。優先度:
    1. knowledgeの最初のコールアウト（POINT）の先頭文
    2. クイズ1問目解説の先頭文
    3. exam_focusの末尾文
    """
    # 1. 最初のコールアウト
    for sent in knowledge_sents:
        if sent.startswith(CALLOUT_MARKER):
            body = sent[len(CALLOUT_MARKER):]
            m = re.search(r'^.{10,}?[。！？]', body)
            if m and len(m.group(0)) <= 90:
                return m.group(0)
            if 10 < len(body) <= 90:
                return body

    # 2. クイズ解説
    if quizzes:
        expl = re.sub(r'^正解[：:]\s*[ABCD][|｜]?\s*', '',
                      quizzes[0].get('explanation', '')).strip()
        m = re.search(r'^.{10,}?[。！？]', expl)
        if m and len(m.group(0)) <= 90:
            return m.group(0)

    # 3. exam_focus末尾文
    if exam_focus:
        parts = re.split(r'(?<=[。！？])\s*', exam_focus.replace('\n', ' ').strip())
        for p in reversed([x.strip() for x in parts if x.strip()]):
            if 10 < len(p) <= 90:
                return p

    return ''


def build_overview_card(knowledge: str, exam_focus: str, quizzes: list, ch: int) -> str:
    """
    概要カードのHTMLを生成:
      ① ⚠ 試験ポイント（オレンジボックス）
      ② 区切り → トピック見出し＋1文サマリーカード群（H3単位）
      ③ 🔑 記憶の鍵（グラデーションボックス）

    プロトタイプの「試験ポイント → AIの3フェーズ / LLMの動作原理 / ... → 記憶の鍵」
    という構成を knowledge の H3 構造から自動生成する。
    """
    color = CH_COLORS.get(ch, CH_COLORS[1])
    e = htmllib.escape
    parts = []

    # ① 試験ポイント
    if exam_focus:
        parts.append(
            f'<div class="exam-point">'
            f'<div class="exam-label">⚠ 試験で問われるポイント</div>'
            f'{e(exam_focus)}'
            f'</div>'
        )

    # ② トピック概要（H3見出し + 先頭文）
    if knowledge.strip():
        sections = _extract_sections_from_knowledge(knowledge)

        if sections:
            parts.append('<div class="ov-divider"></div>')

            for heading, body_sents in sections[:5]:  # 最大5トピック
                summary_raw = body_sents[0] if body_sents else ''
                summary = (summary_raw[:100] + '…') if len(summary_raw) > 100 else summary_raw

                if heading:
                    parts.append(
                        f'<div class="ov-section">'
                        f'<div class="ov-section-title"'
                        f' style="border-left-color:{color["accent"]};color:{color["dark"]};">'
                        f'{e(heading)}</div>'
                        + (f'<div class="ov-section-body">{e(summary)}</div>' if summary else '')
                        + f'</div>'
                    )
                else:
                    # H3なし → 本文を直接表示
                    for s in body_sents[:2]:
                        parts.append(f'<p class="ov-body-p">{e(s)}</p>')

    # ③ 記憶の鍵
    knowledge_sents_for_key = join_sentences(clean_lines(knowledge)) if knowledge.strip() else []
    key = _extract_memory_key(knowledge_sents_for_key, quizzes, exam_focus)
    if key:
        parts.append(
            f'<div class="memory-key"'
            f' style="background:linear-gradient(135deg,{color["dark"]},{color["accent"]});">'
            f'<div class="memory-key-label">🔑 記憶の鍵</div>'
            f'<div class="memory-key-text">{e(key)}</div>'
            f'</div>'
        )

    return '\n'.join(parts)


def format_deep_dive(knowledge: str, scenario: str, ch: int) -> str:
    """深掘りノートをHTML整形（見出し・段落・コールアウト・業務シナリオ）"""
    color = CH_COLORS.get(ch, CH_COLORS[1])

    if not knowledge.strip():
        return '<p style="color:#999;text-align:center;">（テキストなし）</p>'

    lines = clean_lines(knowledge)
    sents = join_sentences(lines)

    parts = []
    for sent in sents:
        if sent.startswith(CALLOUT_MARKER):
            body = sent[len(CALLOUT_MARKER):]
            parts.append(
                f'<div class="callout-box"'
                f' style="border-left-color:{color["accent"]};background:{color["light"]};">'
                f'<span class="callout-icon">💡</span>{htmllib.escape(body)}</div>'
            )
        elif _is_heading(sent):
            parts.append(
                f'<h3 class="dd-h3"'
                f' style="border-left-color:{color["accent"]};background:{color["light"]};">'
                f'{htmllib.escape(sent)}</h3>'
            )
        elif BULLET_RE.match(sent):
            parts.append(
                f'<p class="dd-bullet">'
                f'<span class="dd-arrow" style="color:{color["accent"]};">▸</span>'
                f'{htmllib.escape(sent[1:].strip())}</p>'
            )
        else:
            parts.append(f'<p class="dd-p">{htmllib.escape(sent)}</p>')

    # 業務シナリオ
    if scenario and scenario.strip():
        sc_sents = join_sentences(clean_lines(scenario))
        sc_html  = '\n'.join(
            f'<p class="dd-p">{htmllib.escape(s)}</p>'
            for s in sc_sents[:12] if not _is_heading(s)
        )
        parts.append(
            f'<div class="scenario-section" style="border-left-color:{color["accent"]};">'
            f'<div class="scenario-label" style="color:{color["dark"]};">📋 業務シナリオ</div>'
            f'{sc_html}</div>'
        )

    return '\n'.join(parts)


# ─── クイズHTML ───────────────────────────────────────────────────────
def build_quiz_html(quizzes, sid):
    e = htmllib.escape
    if not quizzes:
        return '<p style="color:#999;font-size:14px;text-align:center;padding:8px 0;">（理解度チェックなし）</p>'

    total = len(quizzes)
    parts = [f'''  <button class="retake-btn-main" id="rtk_{sid}" onclick="startRetake('{sid}')" style="display:none;">❌ 0問 再テスト</button>
  <div class="retake-banner" id="rtk_banner_{sid}" style="display:none;">🔄 再テストモード ─ 誤答問題を復習中</div>''']

    for idx, q in enumerate(quizzes, 1):
        qid     = f'{sid}_{idx}'
        is_last = (idx == total)
        disp    = 'block' if idx == 1 else 'none'

        letters   = [lt for lt in ['A','B','C','D'] if lt in q.get('choices', {})]
        correct_l = q.get('correct_letter', letters[0] if letters else 'A')
        correct_i = letters.index(correct_l) if correct_l in letters else 0

        choices_html = ''
        for li, lt in enumerate(letters):
            choices_html += f'\n      <button class="choice-btn" onclick="answer(\'{qid}\',{li},{correct_i})">{lt}　{e(q["choices"][lt])}</button>'

        expl_raw  = q.get('explanation', '')
        expl_body = re.sub(r'^正解[：:]\s*[ABCD][|｜]?\s*', '', expl_raw).strip()

        next_call = f"showScore('{sid}',{total})" if is_last else f"showNext('{sid}_{idx+1}')"
        next_btn  = f'<button class="next-btn" id="n{qid}" onclick="{next_call}">{"結果を見る" if is_last else "次の問題へ"} →</button>'

        parts.append(f'''
  <div class="quiz-block" id="q{qid}" style="display:{disp};">
    <div class="quiz-num">問 {idx} ／ {total}</div>
    <div class="quiz-question">{e(q["question"])}</div>
    <div class="choices">{choices_html}
    </div>
    <div class="explanation" id="e{qid}">
      <div class="ans-label">✅ 正解：{e(correct_l)}</div>
      {e(expl_body)}
    </div>
    <div class="action-btns">
      <button class="retry-btn" id="r{qid}" onclick="retryQ('{qid}')">↩ もう一度</button>
      {next_btn}
    </div>
  </div>''')

    parts.append(f'''
  <div class="score-banner" id="sc_{sid}">
    <div class="score-main"></div>
    <div style="font-size:14px;opacity:.85;">理解度チェック完了 ✅</div>
  </div>''')

    return '\n'.join(parts)


# ─── 共通ヘルパー ─────────────────────────────────────────────────────
def _nav_links(sec, all_sections, page_suffix, color):
    """prev/next の nav-footer HTML。page_suffixは'overview'または'quiz'。
    同じページ種別内で前後セクションへ移動する。"""
    e = htmllib.escape
    flat_idx = next((j for j, s in enumerate(all_sections)
                     if s['ch'] == sec['ch'] and s['s'] == sec['s']), None)
    prev_info = next_info = None
    if flat_idx is not None and flat_idx > 0:
        ps = all_sections[flat_idx - 1]
        prev_info = (f'ch{ps["ch"]:02d}_{page_suffix}.html', f'ch{ps["ch"]:02d}_s{ps["s"]:02d}', ps['title'])
    if flat_idx is not None and flat_idx < len(all_sections) - 1:
        ns = all_sections[flat_idx + 1]
        next_info = (f'ch{ns["ch"]:02d}_{page_suffix}.html', f'ch{ns["ch"]:02d}_s{ns["s"]:02d}', ns['title'])

    prev_link = (f'<a class="nav-btn" style="border-color:{color["accent"]};color:{color["accent"]};" '
                 f'href="{prev_info[0]}#{prev_info[1]}">&larr; {e(prev_info[2][:16])}</a>'
                 if prev_info else '<span class="nav-btn" style="opacity:.4;">← 前</span>')
    next_link = (f'<a class="nav-btn primary" href="{next_info[0]}#{next_info[1]}" '
                 f'style="background:{color["accent"]};border-color:{color["accent"]};">{e(next_info[2][:16])} &rarr;</a>'
                 if next_info else
                 f'<a class="nav-btn primary" href="index.html" '
                 f'style="background:{color["accent"]};border-color:{color["accent"]};">学習マップへ ✓</a>')
    return f'<div class="nav-footer">{prev_link}{next_link}</div>'


def _page_header_html(sec, color, ch_title, badge_text):
    e = htmllib.escape
    ch, s, title = sec['ch'], sec['s'], sec['title']
    return f'''<div class="page-header" style="background:linear-gradient(135deg,{color["dark"]},{color["accent"]});">
  <div class="breadcrumb">Chapter {ch:02d} ｜ {e(ch_title)}</div>
  <div class="page-title">Section {s:02d} ｜ {e(title)}</div>
  <div class="header-meta">
    <span class="badge badge-ch">Ch.{ch:02d}-S{s:02d}</span>
    <span class="badge badge-exam">{badge_text}</span>
  </div>
</div>'''


# ─── ①概要解説セクションHTML ───────────────────────────────────────────
def build_overview_section_html(sec, all_sections):
    e     = htmllib.escape
    ch    = sec['ch']; s = sec['s']
    sid   = f'ch{ch:02d}_s{s:02d}'
    color = CH_COLORS.get(ch, CH_COLORS[1])
    ch_title = CHAPTER_TITLES.get(ch, '')

    exam_focus = sec.get('exam_focus', '').strip()
    ef_lines = [l for l in exam_focus.split('\n') if l.strip() and not NOISE_RE.match(l.strip())]
    exam_focus = '\n'.join(ef_lines).strip()
    if len(exam_focus) > 800:
        exam_focus = exam_focus[:800] + '…'
    ef_too_short = len(exam_focus) < 50

    knowledge = sec.get('knowledge', '')
    scenario  = sec.get('scenario', '')
    quizzes   = sec.get('quizzes', [])

    for old, new in KNOWLEDGE_FIXUPS.get(sid, []):
        knowledge = knowledge.replace(old, new)

    if ef_too_short and knowledge.strip():
        k_lines = clean_lines(knowledge)
        k_sents = join_sentences(k_lines)
        body_sents = [s2 for s2 in k_sents
                      if not _is_heading(s2) and not s2.startswith(CALLOUT_MARKER)][:3]
        if body_sents:
            exam_focus = (exam_focus + '\n' if exam_focus else '') + '\n'.join(body_sents)

    ov_html   = build_overview_card(knowledge, exam_focus, quizzes, ch)
    deep_html = format_deep_dive(knowledge, scenario, ch)
    nav_html  = _nav_links(sec, all_sections, 'overview', color)

    return f'''
<section id="{sid}" style="scroll-margin-top:12px;">

{_page_header_html(sec, color, ch_title, '⚠ 試験頻出')}

<!-- ① 概要カード -->
<div class="card">
  <div class="card-title" style="color:{color["dark"]};">① 概要カード</div>
  {ov_html}
</div>

<!-- ② 学習ステータス -->
<div class="status-card">
  <span class="status-label">② 学習ステータス</span>
  <div class="status-btns" data-sid="{sid}">
    <button class="status-btn btn-done"  data-val="done"  onclick="setStatus('{sid}','done',this)">✓ Done</button>
    <button class="status-btn btn-later" data-val="later" onclick="setStatus('{sid}','later',this)">⏱ 後で確認する</button>
  </div>
</div>

<!-- ③ 深掘りノート -->
<div class="deepdive-wrap">
  <button class="deepdive-btn" onclick="toggleDeepDive(this)">
    <span>📖 ③ 詳細を確認する（深掘りノート）</span>
    <span class="dd-arrow-icon" style="color:{color["accent"]};">▶</span>
  </button>
  <div class="deepdive-content">
    {deep_html}
    <a class="reader-goto-link" href="reader/ch{ch}.html#sec-{s}">📖 精読ビューアでさらに詳しく読む →</a>
  </div>
</div>

{nav_html}
<hr style="border:none;margin:8px 0 20px;">
</section>
'''


# ─── ③問題集セクションHTML ─────────────────────────────────────────────
def build_quiz_section_html(sec, all_sections):
    ch    = sec['ch']; s = sec['s']
    sid   = f'ch{ch:02d}_s{s:02d}'
    color = CH_COLORS.get(ch, CH_COLORS[1])
    ch_title = CHAPTER_TITLES.get(ch, '')

    quizzes   = sec.get('quizzes', [])
    quiz_html = build_quiz_html(quizzes, sid)
    nav_html  = _nav_links(sec, all_sections, 'quiz', color)

    return f'''
<section id="{sid}" style="scroll-margin-top:12px;">

{_page_header_html(sec, color, ch_title, '📝 理解度チェック')}

<!-- ④ 理解度チェック -->
<div class="card" style="padding:18px 18px 10px;border-top:3px solid {color["accent"]};">
  <div class="quiz-hdr" style="color:{color["dark"]};">📝 理解度チェック（公式問題）</div>
  {quiz_html}
</div>

{nav_html}
<hr style="border:none;margin:8px 0 20px;">
</section>
'''


# ─── ページシェル ─────────────────────────────────────────────────────
def _page_shell(title, body_html, current_page):
    """認証ガード・文字サイズ/ダークモードツールバー・フローティングナビを
    含む共通ページテンプレート。"""
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<script>{auth_guard_script('index.html')}</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>{title}</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
{theme_toolbar_html()}
{body_html}
{float_nav_html(current_page)}
<script>{COMMON_JS}</script>
<script>
(function() {{
  var ret = null;
  try {{ ret = sessionStorage.getItem('auth_return'); }} catch(e) {{}}
  if (ret) {{ try {{ sessionStorage.removeItem('auth_return'); }} catch(e) {{}} }}
}})();
</script>
</body>
</html>'''


# ─── チャプターページ（①概要解説／③問題集） ────────────────────────────
def build_chapter_overview_page(ch_num, secs, all_sections):
    ch_title = CHAPTER_TITLES.get(ch_num, '')
    body_parts = [build_overview_section_html(sec, all_sections) for sec in secs]
    return _page_shell(f'Ch.{ch_num:02d} 概要 | {ch_title}', ''.join(body_parts), 'overview')


def build_chapter_quiz_page(ch_num, secs, all_sections):
    ch_title = CHAPTER_TITLES.get(ch_num, '')
    body_parts = [build_quiz_section_html(sec, all_sections) for sec in secs]
    return _page_shell(f'Ch.{ch_num:02d} 問題集 | {ch_title}', ''.join(body_parts), 'quiz')


# ─── 索引ページ ───────────────────────────────────────────────────────
def build_index(all_sections):
    by_ch = {}
    for s in all_sections:
        by_ch.setdefault(s['ch'], []).append(s)

    cards = ''
    for ch_num in sorted(by_ch):
        ch_title = CHAPTER_TITLES.get(ch_num, '')
        color    = CH_COLORS.get(ch_num, CH_COLORS[1])
        links    = ''
        for sec in by_ch[ch_num]:
            sid  = f'ch{sec["ch"]:02d}_s{sec["s"]:02d}'
            href = f'ch{ch_num:02d}_overview.html#{sid}'
            quiz_href = f'ch{ch_num:02d}_quiz.html#{sid}'
            links += f'''
      <a class="section-link" href="{href}">
        <span class="sec-num" style="color:{color["accent"]};">S{sec["s"]:02d}</span>
        <span>{htmllib.escape(sec["title"])}</span>
        <span class="fail-badge" id="fail_{sid}"></span>
        <span class="status-dot" id="dot_{sid}"></span>
      </a><a class="quiz-mini-link" href="{quiz_href}" title="理解度チェックへ">📝</a>'''
        cards += f'''
  <div class="chapter-card">
    <div class="chapter-card-header" style="background:linear-gradient(135deg,{color["dark"]},{color["accent"]});">
      <span>Ch.{ch_num:02d}</span><span>{htmllib.escape(ch_title)}</span>
    </div>{links}
  </div>'''

    dot_js = '''
window.addEventListener('load', function() {
  document.querySelectorAll('.status-dot[id]').forEach(function(dot) {
    var sid = dot.id.replace('dot_','');
    var v = localStorage.getItem('s_' + sid);
    dot.className = 'status-dot' + (v ? ' ' + v : '');
  });

  // 誤答バッジ: qwrong_ch01_s01_1 形式のキーを集計（一度でも誤答した問題を永続追跡）
  var failCounts = {};
  for (var i = 0; i < localStorage.length; i++) {
    var key = localStorage.key(i);
    if (!key || !key.startsWith('qwrong_')) continue;
    var parts = key.replace('qwrong_', '').split('_');
    var sid = parts[0] + '_' + parts[1];
    failCounts[sid] = (failCounts[sid] || 0) + 1;
  }
  Object.keys(failCounts).forEach(function(sid) {
    var badge = document.getElementById('fail_' + sid);
    var link  = badge && badge.closest('.section-link');
    if (badge) {
      badge.textContent = '\\u2717 ' + failCounts[sid];
      badge.classList.add('has-fail');
    }
    if (link) link.classList.add('has-fail');
  });
});
'''
    auth_html = '''
<div class="auth-card" id="auth-panel" style="display:none;">
  <div class="auth-icon">🔒</div>
  <div class="auth-title">パスワードを入力してください</div>
  <div class="auth-desc">このコンテンツはパスワードで保護されています</div>
  <input type="password" class="auth-input" id="pw-input" placeholder="パスワード" autocomplete="current-password" />
  <button class="auth-btn" onclick="doLogin()">ログイン</button>
  <div class="auth-error" id="auth-error">パスワードが正しくありません</div>
</div>'''

    content_html = f'''
<div id="content-panel" style="display:none;">
<div class="index-header">
  <h1>📚 AICX 学習マップ</h1>
  <p>AIエージェント・ストラテジスト資格 ｜ 全32セクション</p>
  <p style="margin-top:8px;font-size:12px;opacity:.6;">🟢 Done &nbsp;🔵 後で確認する &nbsp;⚪ 未確認</p>
</div>
{theme_toolbar_html()}
{cards}
<a href="reader/index.html" style="display:block;margin:16px 0;padding:14px 18px;background:linear-gradient(135deg,#1e3a5f,#2d6a9f);color:white;border-radius:12px;text-decoration:none;text-align:center;font-size:15px;font-weight:700;box-shadow:0 1px 4px rgba(0,0,0,.12);">
  📖 精読ビューアを開く
</a>
<div style="text-align:center;padding:12px 0 4px;font-size:12px;color:#999;">
  セクション名をタップして概要へ、📝アイコンで問題集へ
</div>
<button class="logout-btn" onclick="doLogout()" style="display:block;margin:8px auto 0;background:none;border:none;color:#bbb;font-size:12px;cursor:pointer;padding:4px 12px;">ログアウト</button>
</div>'''

    auth_js = f'''
var AUTH_HASH_JS = '{AUTH_HASH}';
var AUTH_EXPIRE_JS = {AUTH_EXPIRE_MS};

async function sha256(str) {{
  var buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(function(b){{ return b.toString(16).padStart(2,'0'); }}).join('');
}}

function checkAuth() {{
  try {{
    var a = JSON.parse(localStorage.getItem('reader_auth') || 'null');
    return a && a.h === AUTH_HASH_JS && a.e > Date.now();
  }} catch(e) {{ return false; }}
}}

function showAuthedContent() {{
  document.getElementById('auth-panel').style.display = 'none';
  document.getElementById('content-panel').style.display = 'block';
  var ret = null;
  try {{ ret = sessionStorage.getItem('auth_return'); }} catch(e) {{}}
  if (ret) {{
    try {{ sessionStorage.removeItem('auth_return'); }} catch(e) {{}}
    location.href = ret;
  }}
}}

async function doLogin() {{
  var pw = document.getElementById('pw-input').value;
  var h = await sha256(pw);
  if (h === AUTH_HASH_JS) {{
    localStorage.setItem('reader_auth', JSON.stringify({{h: AUTH_HASH_JS, e: Date.now() + AUTH_EXPIRE_JS}}));
    showAuthedContent();
  }} else {{
    document.getElementById('auth-error').style.display = 'block';
  }}
}}

function doLogout() {{
  localStorage.removeItem('reader_auth');
  location.reload();
}}

window.addEventListener('load', function() {{
  var pwInput = document.getElementById('pw-input');
  if (pwInput) {{
    pwInput.addEventListener('keydown', function(e) {{ if (e.key === 'Enter') doLogin(); }});
  }}
  if (checkAuth()) {{
    showAuthedContent();
  }} else {{
    document.getElementById('auth-panel').style.display = 'block';
  }}
}});
'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>AICX 学習マップ</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
{auth_html}
{content_html}
<script>{dot_js}</script>
<script>{auth_js}</script>
</body>
</html>'''


# ─── メイン ──────────────────────────────────────────────────────────
def main():
    json_path = os.path.join(OUT_DIR, 'sections_data.json')
    with open(json_path, encoding='utf-8') as f:
        all_sections = json.load(f)

    by_ch = {}
    for s in all_sections:
        by_ch.setdefault(s['ch'], []).append(s)

    for ch_num, secs in sorted(by_ch.items()):
        ov_html = build_chapter_overview_page(ch_num, secs, all_sections)
        ov_path = os.path.join(OUT_DIR, f'ch{ch_num:02d}_overview.html')
        with open(ov_path, 'w', encoding='utf-8') as f:
            f.write(ov_html)

        qz_html = build_chapter_quiz_page(ch_num, secs, all_sections)
        qz_path = os.path.join(OUT_DIR, f'ch{ch_num:02d}_quiz.html')
        with open(qz_path, 'w', encoding='utf-8') as f:
            f.write(qz_html)

        print(f'Written: ch{ch_num:02d}_overview.html, ch{ch_num:02d}_quiz.html ({len(secs)} sections)')

    idx_html = build_index(all_sections)
    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(idx_html)
    print('Written: index.html')
    print(f'Done. {OUT_DIR}')

if __name__ == '__main__':
    main()
