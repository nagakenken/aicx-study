# AICX 学習支援 HTML ジェネレータ v3
# Usage: python build_html.py
# v3: 章別カラー・POINTコールアウト復元・記憶の鍵ボックス・深掘りビジュアル強化

import json, re, os, html as htmllib

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


# ─── CSS ────────────────────────────────────────────────────────────
COMMON_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Sans', 'Helvetica Neue', sans-serif;
  font-size: 16px; line-height: 1.7; color: #1a1a1a;
  background: #f0f2f5; padding: 12px;
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
  background: white; border-radius: 12px; padding: 18px;
  margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.card-title {
  font-size: 14px; font-weight: 700; color: #1e3a5f;
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
  font-size: 14px; line-height: 1.75;
}
.exam-label { font-weight: 700; color: #c67200; font-size: 12px; margin-bottom: 5px; }

/* ── 概要カード: トピック概要セクション ─── */
.ov-divider { border-top: 1px solid #e8e8e8; margin: 14px 0 10px; }
.ov-section { margin-bottom: 12px; }
.ov-section-title {
  font-size: 13px; font-weight: 700;
  border-left: 3px solid #2d6a9f;
  padding: 4px 8px 4px 10px; border-radius: 0 4px 4px 0;
  margin-bottom: 5px;
}
.ov-section-body {
  font-size: 13px; line-height: 1.65; color: #555;
  padding-left: 13px;
}
.ov-body-p { font-size: 13px; line-height: 1.65; color: #333; margin-bottom: 6px; }

/* ── 学習ステータス ──────────────────────── */
.status-card {
  background: white; border-radius: 12px; padding: 14px 18px;
  margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.08);
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
}
.status-label { font-size: 14px; font-weight: 600; color: #555; flex-shrink: 0; }
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

/* ── 深掘りノート（アコーディオン） ────────── */
.deepdive-wrap { margin-bottom: 12px; }
.deepdive-btn {
  width: 100%; background: white; border: 1px solid #d0d7de;
  border-radius: 10px; padding: 13px 16px;
  font-size: 14px; font-weight: 600; color: #1e3a5f;
  text-align: left; cursor: pointer;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
  -webkit-tap-highlight-color: transparent;
}
.deepdive-btn .dd-arrow-icon { font-size: 12px; transition: transform .25s; color: #2d6a9f; }
.deepdive-btn.open .dd-arrow-icon { transform: rotate(90deg); }
.deepdive-content {
  display: none; background: white;
  border: 1px solid #d0d7de; border-top: none;
  border-radius: 0 0 10px 10px;
  padding: 16px 18px;
}
.deepdive-content.open { display: block; }

/* ── 深掘りノート内 コンテンツスタイル ──────── */
.dd-h3 {
  font-size: 13px; font-weight: 700;
  border-left: 3px solid #2d6a9f;
  background: #e8f0fe;
  padding: 6px 10px; border-radius: 0 6px 6px 0;
  margin: 16px 0 8px; line-height: 1.5;
}
.dd-h3:first-child { margin-top: 0; }
.dd-p {
  font-size: 14px; line-height: 1.8; color: #333;
  margin-bottom: 8px;
}
.dd-bullet {
  font-size: 14px; line-height: 1.7; color: #333;
  margin-bottom: 6px;
  display: flex; align-items: flex-start; gap: 6px;
}
.dd-arrow { font-size: 12px; flex-shrink: 0; margin-top: 4px; }

/* ── コールアウトボックス (POINT) ──────────── */
.callout-box {
  border-left: 3px solid #2d6a9f;
  border-radius: 0 8px 8px 0;
  padding: 10px 12px;
  font-size: 14px; line-height: 1.75;
  margin: 10px 0; font-weight: 500;
  display: flex; gap: 8px; align-items: flex-start;
}
.callout-icon { flex-shrink: 0; font-size: 14px; margin-top: 1px; }

/* ── 業務シナリオ ────────────────────────── */
.scenario-section {
  border-left: 3px solid #4285f4;
  border-radius: 0 8px 8px 0;
  background: #f0f4ff;
  padding: 12px 14px; margin-top: 14px;
}
.scenario-label { font-size: 12px; font-weight: 700; color: #1a4bae; margin-bottom: 6px; }

/* ── 記憶の鍵 ────────────────────────────── */
.memory-key {
  color: white; border-radius: 10px;
  padding: 14px 16px; margin-top: 16px; text-align: center;
}
.memory-key-label { font-size: 11px; opacity: .75; margin-bottom: 6px; letter-spacing: .5px; }
.memory-key-text  { font-size: 14px; font-weight: 700; line-height: 1.6; }

/* ── 理解度チェック ─────────────────────── */
.quiz-hdr {
  font-size: 15px; font-weight: 700; color: #1e3a5f;
  margin-bottom: 12px; display: flex; align-items: center; gap: 6px;
}
.quiz-block {
  background: white; border-radius: 12px; padding: 18px;
  margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.quiz-num      { font-size: 12px; font-weight: 700; color: #2d6a9f; margin-bottom: 8px; }
.quiz-question { font-size: 15px; font-weight: 600; line-height: 1.6; margin-bottom: 14px; }
.choices { display: flex; flex-direction: column; gap: 8px; }
.choice-btn {
  background: #f5f5f7; border: 2px solid transparent; border-radius: 10px;
  padding: 11px 14px; font-size: 14px; text-align: left;
  cursor: pointer; line-height: 1.5; color: #1a1a1a;
  transition: background .15s, border-color .15s;
  -webkit-tap-highlight-color: transparent;
}
.choice-btn:active  { background: #e8f0fe; }
.choice-btn.correct { background: #e6f4ea; border-color: #34a853; color: #1a7340; font-weight: 600; }
.choice-btn.wrong   { background: #fce8e6; border-color: #ea4335; color: #b31412; }
.choice-btn.dimmed  { opacity: .4; pointer-events: none; }
.explanation {
  display: none; background: #e6f4ea; border-radius: 8px;
  padding: 12px 14px; margin-top: 12px; font-size: 14px; line-height: 1.6;
  border-left: 3px solid #34a853;
}
.explanation.show { display: block; }
.ans-label { font-weight: 700; color: #1a7340; font-size: 13px; margin-bottom: 5px; }
.explanation.hint { background: #fff8e6; border-left-color: #ff9500; }
.explanation.hint .ans-label { color: #c67200; }
.action-btns { display: flex; gap: 8px; margin-top: 10px; }
.retry-btn, .next-btn {
  padding: 9px 18px; border-radius: 8px; border: none;
  font-size: 14px; font-weight: 600; cursor: pointer; display: none;
  -webkit-tap-highlight-color: transparent;
}
.retry-btn.show, .next-btn.show { display: inline-block; }
.retry-btn { background: #f0f0f0; color: #333; }
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
.retake-banner {
  background: #fff3e0; border: 2px solid #ff9500; border-radius: 8px;
  padding: 10px 14px; margin-bottom: 12px;
  font-size: 14px; font-weight: 700; color: #c67200; text-align: center;
}

/* ── ナビ ────────────────────────────────── */
.nav-footer { display: flex; gap: 10px; margin-top: 16px; padding-bottom: 24px; }
.nav-btn {
  flex: 1; padding: 12px; border-radius: 10px; border: 2px solid #2d6a9f;
  background: white; color: #2d6a9f; font-size: 14px; font-weight: 600;
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
.chapter-card { background: white; border-radius: 12px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,.08); overflow: hidden; }
.chapter-card-header { padding: 14px 18px; font-weight: 700; font-size: 15px;
  color: white; display: flex; align-items: center; gap: 8px; }
.section-link { display: flex; align-items: center; gap: 10px; padding: 11px 18px;
  border-bottom: 1px solid #f0f0f0; text-decoration: none; color: #1a1a1a; font-size: 14px; }
.section-link:last-child { border-bottom: none; }
.section-link:active { background: #f5f5f7; }
.sec-num { font-weight: 700; font-size: 12px; min-width: 28px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: #ddd; flex-shrink: 0; margin-left: auto; }
.status-dot.done  { background: #34a853; }
.status-dot.later { background: #4285f4; }
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

window.addEventListener('load', function() {
  document.querySelectorAll('.status-btns[data-sid]').forEach(function(wrap) {
    var v = loadStatus('s_' + wrap.dataset.sid);
    if (v) {
      var b = wrap.querySelector('[data-val="' + v + '"]');
      if (b) b.classList.add('active');
    }
  });
  initRetakeBtns();
});
"""

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


# ─── セクションHTML ───────────────────────────────────────────────────
def build_section_html(sec, prev_info=None, next_info=None):
    e     = htmllib.escape
    ch    = sec['ch']; s = sec['s']
    title = sec['title']
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
        body_sents = [s for s in k_sents
                      if not _is_heading(s) and not s.startswith(CALLOUT_MARKER)][:3]
        if body_sents:
            exam_focus = (exam_focus + '\n' if exam_focus else '') + '\n'.join(body_sents)

    ov_html   = build_overview_card(knowledge, exam_focus, quizzes, ch)
    deep_html = format_deep_dive(knowledge, scenario, ch)
    quiz_html = build_quiz_html(quizzes, sid)

    prev_link = (f'<a class="nav-btn" href="{prev_info[0]}#{prev_info[1]}">&larr; {e(prev_info[2][:16])}</a>'
                 if prev_info else '<span class="nav-btn" style="opacity:.4;">← 前</span>')
    next_link = (f'<a class="nav-btn primary" href="{next_info[0]}#{next_info[1]}" style="background:{color["accent"]};border-color:{color["accent"]};">{e(next_info[2][:16])} &rarr;</a>'
                 if next_info else f'<a class="nav-btn primary" href="index.html" style="background:{color["accent"]};border-color:{color["accent"]};">学習マップへ ✓</a>')

    # nav-btnのボーダーカラーを章カラーに
    prev_link = prev_link.replace('class="nav-btn"', f'class="nav-btn" style="border-color:{color["accent"]};color:{color["accent"]};"') if prev_info else prev_link

    return f'''
<section id="{sid}" style="scroll-margin-top:12px;">

<div class="page-header" style="background:linear-gradient(135deg,{color["dark"]},{color["accent"]});">
  <div class="breadcrumb">Chapter {ch:02d} ｜ {e(ch_title)}</div>
  <div class="page-title">Section {s:02d} ｜ {e(title)}</div>
  <div class="header-meta">
    <span class="badge badge-ch">Ch.{ch:02d}-S{s:02d}</span>
    <span class="badge badge-exam">⚠ 試験頻出</span>
  </div>
</div>

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
  </div>
</div>

<!-- ④ 理解度チェック -->
<div class="card" style="padding:18px 18px 10px;border-top:3px solid {color["accent"]};">
  <div class="quiz-hdr" style="color:{color["dark"]};">📝 ④ 理解度チェック（公式問題）</div>
  {quiz_html}
</div>

<div class="nav-footer">{prev_link}{next_link}</div>
<hr style="border:none;margin:8px 0 20px;">
</section>
'''


# ─── チャプターページ ─────────────────────────────────────────────────
def build_chapter_page(ch_num, secs, all_sections):
    ch_title = CHAPTER_TITLES.get(ch_num, '')
    color    = CH_COLORS.get(ch_num, CH_COLORS[1])
    body_parts = []

    for sec in secs:
        flat_idx = next((j for j, s in enumerate(all_sections)
                         if s['ch'] == sec['ch'] and s['s'] == sec['s']), None)
        prev_info = next_info = None
        if flat_idx is not None and flat_idx > 0:
            ps = all_sections[flat_idx - 1]
            prev_info = (f'ch{ps["ch"]:02d}.html', f'ch{ps["ch"]:02d}_s{ps["s"]:02d}', ps['title'])
        if flat_idx is not None and flat_idx < len(all_sections) - 1:
            ns = all_sections[flat_idx + 1]
            next_info = (f'ch{ns["ch"]:02d}.html', f'ch{ns["ch"]:02d}_s{ns["s"]:02d}', ns['title'])
        body_parts.append(build_section_html(sec, prev_info, next_info))

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>Ch.{ch_num:02d} | {ch_title}</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
{''.join(body_parts)}
<script>{COMMON_JS}</script>
</body>
</html>'''


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
            href = f'ch{ch_num:02d}.html#{sid}'
            links += f'''
      <a class="section-link" href="{href}">
        <span class="sec-num" style="color:{color["accent"]};">S{sec["s"]:02d}</span>
        <span>{htmllib.escape(sec["title"])}</span>
        <span class="status-dot" id="dot_{sid}"></span>
      </a>'''
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
});
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
<div class="index-header">
  <h1>📚 AICX 学習マップ</h1>
  <p>AIエージェント・ストラテジスト資格 ｜ 全32セクション</p>
  <p style="margin-top:8px;font-size:12px;opacity:.6;">🟢 Done &nbsp;🔵 後で確認する &nbsp;⚪ 未確認</p>
</div>
{cards}
<div style="text-align:center;padding:16px 0;font-size:12px;color:#999;">
  セクション名をタップして学習を開始
</div>
<script>{dot_js}</script>
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
        html = build_chapter_page(ch_num, secs, all_sections)
        path = os.path.join(OUT_DIR, f'ch{ch_num:02d}.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'Written: ch{ch_num:02d}.html ({len(secs)} sections)')

    idx_html = build_index(all_sections)
    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(idx_html)
    print('Written: index.html')
    print(f'Done. {OUT_DIR}')

if __name__ == '__main__':
    main()
