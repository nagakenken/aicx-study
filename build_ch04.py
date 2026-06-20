#!/usr/bin/env python3
# build_ch04.py — Ch04専用高品質HTMLジェネレータ（4セクション）

import json, os, sys, html as htmllib

OUT_DIR   = r"C:\Users\mikli\Downloads\AICX学習"
DATA_PATH = os.path.join(OUT_DIR, 'sections_data.json')

sys.path.insert(0, OUT_DIR)
from build_html import (
    clean_lines, join_sentences, _is_heading, format_deep_dive,
    build_quiz_html, COMMON_JS, COMMON_CSS, CH_COLORS, CHAPTER_TITLES,
    NOISE_RE, CALLOUT_MARKER,
)

C = CH_COLORS[4]  # {'accent':'#c45a0a','dark':'#8a3e06','light':'#fff0e0','mid':'#e07a30'}

EXTRA_CSS = f"""
/* ── OVサブタイトル ─────────────────────── */
.ov-subtitle {{
  font-size:13px; font-weight:700; margin:14px 0 8px;
  padding-bottom:4px; border-bottom:1.5px solid {C['light']};
  color:{C['dark']};
}}

/* ── ポイントリスト ──────────────────────── */
.point-list {{ list-style:none; padding:0; margin:10px 0; display:flex; flex-direction:column; gap:5px; }}
.point-list li {{
  font-size:13px; line-height:1.65; color:#333;
  padding-left:16px; position:relative;
}}
.point-list li::before {{
  content:'▸'; position:absolute; left:0;
  color:{C['accent']}; font-size:11px; top:3px;
}}
.point-list li strong {{ color:{C['dark']}; }}

/* ── 自動化ラダー ────────────────────────── */
.auto-ladder {{ display:flex; flex-direction:column; gap:6px; margin:10px 0; }}
.auto-rung {{
  border-radius:10px; padding:10px 14px;
  box-shadow:0 1px 3px rgba(0,0,0,.08);
  border-left:5px solid;
}}
.auto-rung-head {{ display:flex; align-items:center; gap:8px; margin-bottom:4px; }}
.auto-lv {{
  width:26px; height:26px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:11px; font-weight:800; flex-shrink:0; color:white;
}}
.auto-title {{ font-size:13px; font-weight:700; }}
.auto-meta  {{ font-size:11px; color:#888; margin-left:auto; }}
.auto-body  {{ font-size:12px; color:#333; line-height:1.5; }}
.auto-body em {{ font-style:normal; color:{C['dark']}; font-weight:600; }}

/* ── トリガーカード ─────────────────────── */
.trigger-cards {{ display:flex; flex-direction:column; gap:8px; margin:10px 0; }}
.trigger-card {{
  border-radius:10px; overflow:hidden;
  box-shadow:0 1px 3px rgba(0,0,0,.08);
}}
.trigger-card-head {{
  padding:8px 14px; font-size:12.5px; font-weight:700;
}}
.trigger-card-body {{
  padding:9px 14px; background:#f9fafb;
  border-top:1px solid rgba(0,0,0,.06);
  font-size:12px; line-height:1.55; color:#333;
}}
.trigger-examples {{ font-size:11.5px; color:{C['accent']}; margin-top:4px; font-style:italic; }}

/* ── アクション3種類 ─────────────────────── */
.action-cards {{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin:10px 0; }}
.action-card {{ border-radius:10px; padding:11px 10px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.action-icon {{ font-size:22px; margin-bottom:4px; }}
.action-name {{ font-size:12px; font-weight:700; margin-bottom:3px; }}
.action-desc {{ font-size:11px; color:#555; line-height:1.4; }}

/* ── 分岐比較カード ─────────────────────── */
.branch-cards {{ display:flex; flex-direction:column; gap:8px; margin:10px 0; }}
.branch-card {{
  border-radius:10px; border:1.5px solid;
  padding:10px 14px;
}}
.branch-head {{ display:flex; align-items:center; gap:8px; margin-bottom:5px; }}
.branch-icon {{ font-size:18px; }}
.branch-name {{ font-size:13px; font-weight:700; }}
.branch-body {{ font-size:12px; color:#333; line-height:1.55; }}
.branch-usecase {{ font-size:11.5px; color:{C['accent']}; margin-top:4px; font-weight:600; }}

/* ── コンテキスト4課題カード ─────────────── */
.problem-cards {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0; }}
.problem-card {{ border-radius:10px; border:1.5px solid; padding:10px 12px; }}
.problem-head {{ font-size:12.5px; font-weight:700; margin-bottom:5px; color:{C['dark']}; }}
.problem-body {{ font-size:12px; color:#333; line-height:1.5; }}

/* ── 情報種別リスト ─────────────────────── */
.info-types {{ display:flex; flex-direction:column; gap:5px; margin:10px 0; }}
.info-type {{ display:flex; align-items:flex-start; gap:8px; border-radius:8px; padding:8px 12px; background:#fff8f0; }}
.info-badge {{ font-size:10px; font-weight:700; background:{C['dark']}; color:white; border-radius:4px; padding:2px 6px; flex-shrink:0; white-space:nowrap; margin-top:2px; }}
.info-content {{ font-size:12px; color:#333; line-height:1.45; }}
.info-content strong {{ color:{C['dark']}; }}

/* ── 比較テーブル ───────────────────────── */
.cmp-table {{ width:100%; border-collapse:collapse; margin:10px 0; font-size:12.5px; }}
.cmp-table th {{
  padding:7px 10px; color:white; font-size:12px; font-weight:700; text-align:center;
  background:{C['dark']};
}}
.cmp-table td {{ padding:7px 10px; border-bottom:1px solid #eee; vertical-align:top; line-height:1.55; }}
.cmp-table tr:nth-child(even) td {{ background:#f9f9f9; }}
.cmp-table td:first-child {{ font-weight:600; color:#666; font-size:12px; }}
"""

FULL_CSS = COMMON_CSS + EXTRA_CSS


def mk_memory_key(text):
    return (f'<div class="memory-key"'
            f' style="background:linear-gradient(135deg,{C["dark"]},{C["accent"]});">'
            f'<div class="memory-key-label">🔑 記憶の鍵</div>'
            f'<div class="memory-key-text">{text}</div>'
            f'</div>')

def mk_exam_point(exam_focus):
    ef = htmllib.escape(exam_focus)
    return (f'<div class="exam-point">'
            f'<div class="exam-label">⚠ 試験で問われるポイント</div>'
            f'{ef}</div>')


# ─── S01: 自動化レベルの進化論 ────────────────────────────────────────────
def ov_s01(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">自動化4レベル（Lv1 → Lv4）</div>
<div class="auto-ladder">
  <div class="auto-rung" style="border-color:#aaa;background:#f9f9f9;">
    <div class="auto-rung-head">
      <div class="auto-lv" style="background:#aaa;">1</div>
      <div class="auto-title">アドホック（一問一答）</div>
      <div class="auto-meta">個別対話</div>
    </div>
    <div class="auto-body">毎回その場で指示を出す使い方。ChatGPT等の一般的な使用。<em>人間が操縦する</em>。生産性向上は個人レベルにとどまる</div>
  </div>
  <div class="auto-rung" style="border-color:{C['mid']};background:#fff5ec;">
    <div class="auto-rung-head">
      <div class="auto-lv" style="background:{C['mid']};">2</div>
      <div class="auto-title">カスタムチャットボット</div>
      <div class="auto-meta">専用設定</div>
    </div>
    <div class="auto-body">業務固有のシステムプロンプト・データソースを設定。社内Q&A・営業支援等。<em>繰り返し使えるが自律実行はしない</em></div>
  </div>
  <div class="auto-rung" style="border-color:{C['accent']};background:#fff0e0;">
    <div class="auto-rung-head">
      <div class="auto-lv" style="background:{C['accent']};">3</div>
      <div class="auto-title">ワークフロー型エージェント</div>
      <div class="auto-meta">電車の比喩</div>
    </div>
    <div class="auto-body"><em>電車＝決まったレール（ワークフロー）を自動で走る</em>。トリガー→処理→出力を自律実行。ただし路線変更は人間が設計する。承認ワークフロー・定期レポート生成等</div>
  </div>
  <div class="auto-rung" style="border-color:{C['dark']};background:#ffe8cc;">
    <div class="auto-rung-head">
      <div class="auto-lv" style="background:{C['dark']};">4</div>
      <div class="auto-title">自律型エージェント</div>
      <div class="auto-meta">自家用車の比喩</div>
    </div>
    <div class="auto-body"><em>自家用車＝目的地を告げると自分でルートを判断して走る</em>。ゴール指示→タスク分解→ツール選択→実行を自律的に行う。最もリスクが高く、ガバナンス設計が最重要</div>
  </div>
</div>

{mk_memory_key('電車（Lv3）＝レール固定・自動走行。自家用車（Lv4）＝目的地だけ伝え自律で走る。今の企業はLv3から始めよ')}
"""


# ─── S02: トリガーとアクション ─────────────────────────────────────────────
def ov_s02(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">トリガー3種類</div>
<div class="trigger-cards">
  <div class="trigger-card">
    <div class="trigger-card-head" style="background:{C['dark']};color:white;">指示型トリガー</div>
    <div class="trigger-card-body">
      人間が能動的に指示・入力することで起動。最も直接的な連携。
      <div class="trigger-examples">例：チャットでの質問送信・ボタンクリック・フォーム送信</div>
    </div>
  </div>
  <div class="trigger-card">
    <div class="trigger-card-head" style="background:{C['accent']};color:white;">定時型トリガー</div>
    <div class="trigger-card-body">
      時刻・スケジュール・期限を条件として自動起動。人間の操作不要。
      <div class="trigger-examples">例：毎朝9時に日報生成・月次決算日に自動集計・契約期限3日前に通知</div>
    </div>
  </div>
  <div class="trigger-card">
    <div class="trigger-card-head" style="background:{C['mid']};color:white;">条件型トリガー</div>
    <div class="trigger-card-body">
      特定のイベント・データ変化・閾値超過で自動起動。最も自律的。
      <div class="trigger-examples">例：フォーム送信→処理開始 / Webhook受信 / 在庫が閾値を下回ったら発注</div>
    </div>
  </div>
</div>

<div class="ov-subtitle">アクション3種類</div>
<div class="action-cards">
  <div class="action-card" style="background:{C['light']};">
    <div class="action-icon">⚙</div>
    <div class="action-name">データ処理<br>アクション</div>
    <div class="action-desc">取得・変換・保存・転送。構造化データの自動操作</div>
  </div>
  <div class="action-card" style="background:#ffe8cc;">
    <div class="action-icon">✨</div>
    <div class="action-name">生成アクション</div>
    <div class="action-desc">テキスト・コード・メール・レポートの生成。LLMの出番</div>
  </div>
  <div class="action-card" style="background:#ffd5b0;">
    <div class="action-icon">🔀</div>
    <div class="action-name">判断アクション</div>
    <div class="action-desc">条件分岐・ルーティング・優先度判断。文脈に応じた処理振り分け</div>
  </div>
</div>

<ul class="point-list">
  <li>ワークフローは「何をきっかけに（トリガー）」「何をするか（アクション）」の組み合わせで設計する</li>
  <li>条件型トリガー＋判断アクションの組み合わせが最も高度で、Lv3〜4エージェントの核心</li>
</ul>

{mk_memory_key('トリガー＝指示型・定時型・条件型。アクション＝データ処理・生成・判断。組み合わせでワークフローが生まれる')}
"""


# ─── S03: 変数と条件分岐 ──────────────────────────────────────────────────
def ov_s03(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">条件分岐の3パターン</div>
<div class="branch-cards">
  <div class="branch-card" style="border-color:{C['dark']};background:#fff5ec;">
    <div class="branch-head">
      <div class="branch-icon">⑆</div>
      <div class="branch-name">If / Else（二択分岐）</div>
    </div>
    <div class="branch-body">条件がTrueなら処理A、FalseならB。最も基本的な分岐。<strong>2択しか存在しない</strong>場合に使う</div>
    <div class="branch-usecase">例：承認か差し戻しか / エラーなら通知・なければ続行</div>
  </div>
  <div class="branch-card" style="border-color:{C['accent']};background:#fff0e0;">
    <div class="branch-head">
      <div class="branch-icon">🔀</div>
      <div class="branch-name">ルーティング（多方向分岐）</div>
    </div>
    <div class="branch-body">条件の内容によって<strong>3方向以上</strong>に振り分け。「どのチームに回すか」「どの処理を適用するか」を決定</div>
    <div class="branch-usecase">例：問い合わせ種別→営業/技術/経理に振り分け / リスクレベル→低中高で処理変更</div>
  </div>
  <div class="branch-card" style="border-color:{C['mid']};background:#fff8f0;">
    <div class="branch-head">
      <div class="branch-icon">🔽</div>
      <div class="branch-name">フィルタリング（通過・遮断）</div>
    </div>
    <div class="branch-body">条件を満たすデータだけを「通過させる」。満たさないものは<strong>除外・遮断・スキップ</strong></div>
    <div class="branch-usecase">例：スコア80以上の候補者のみ次工程へ / 営業部門宛メールのみ転送</div>
  </div>
</div>

<div class="ov-subtitle">変数の概念</div>
<ul class="point-list">
  <li><strong>変数</strong>：ワークフロー内で値を一時保存する「入れ物」。前のステップの出力を後のステップに渡す仕組み</li>
  <li>例：「顧客名」変数にS01で抽出した名前を格納→S03でメール送信の宛名に使う</li>
  <li><strong>エラーハンドリング</strong>：If/Elseの応用。「正常系か異常系か」で分岐し、異常時はフォールバック処理（人間への通知等）を実行。<strong>Human-in-the-Loopの設計と直結</strong></li>
</ul>

<div class="ov-subtitle">エラーハンドリングの設計原則</div>
<ul class="point-list">
  <li>完全自動化を目指しながら、<strong>異常時に人間が介入できる経路</strong>を残す</li>
  <li>「エラーが起きたら全停止」ではなく「担当者にSlackで通知して手動対応を依頼」するフォールバック設計</li>
  <li>ガバナンスの観点からも、AIが処理できない・すべきでないケースを人間に戻すパスを明示的に設計することが必須</li>
</ul>

{mk_memory_key('分岐＝2択(If/Else)・多方向(ルーティング)・除外(フィルタリング)の3種。エラーは「全停止」でなく「人間へ返す」設計で')}
"""


# ─── S04: コンテキストエンジニアリング概論 ─────────────────────────────────
def ov_s04(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">コンテキストエンジニアリングとは</div>
<ul class="point-list">
  <li><strong>定義</strong>：LLMに渡す文脈情報（何を・どのフォーマットで・どのタイミングで・どの順序で）を体系的に設計・管理する技術</li>
  <li><strong>Andrej Karpathy（元OpenAI）の比喩</strong>：LLM＝新種のOS、コンテキストウィンドウ＝RAM。OSがRAMに載せるデータを管理するように、コンテキストウィンドウに載せる情報を設計する行為がコンテキストエンジニアリング</li>
  <li><strong>プロンプトエンジニアリングとの違い</strong>：プロンプト＝指示文の工夫（コンテキストエンジニアリングの一部）。コンテキストエンジニアリング＝指示文＋参考文書＋ツール＋会話履歴など<strong>入力全体の設計</strong></li>
</ul>

<div class="ov-subtitle">LLMが抱える4つの本質的課題</div>
<div class="problem-cards">
  <div class="problem-card" style="border-color:{C['dark']};">
    <div class="problem-head">コンテキストウィンドウ限界</div>
    <div class="problem-body">一度に処理できる情報量の上限。長時間実行で蓄積されたツール結果・履歴が上限を超える。重要情報が除外される</div>
  </div>
  <div class="problem-card" style="border-color:{C['accent']};">
    <div class="problem-head">Lost in the Middle</div>
    <div class="problem-body">スタンフォード研究：LLMはコンテキストの<strong>先頭と末尾は参照しやすく、中間は見落としやすい</strong>。重要情報の配置順が出力品質を左右する</div>
  </div>
  <div class="problem-card" style="border-color:{C['mid']};">
    <div class="problem-head">コンテキスト汚染</div>
    <div class="problem-body">ハルシネーションがコンテキストに混入→後続の判断に悪影響。AIの自己出力が次の入力になるため誤りが連鎖的に拡散</div>
  </div>
  <div class="problem-card" style="border-color:#e0956a;">
    <div class="problem-head">コンテキスト混乱</div>
    <div class="problem-body">無関係・矛盾する情報が混在するとLLMの推論が阻害される。古い情報と最新情報が混在すると正確な判断が困難</div>
  </div>
</div>

<div class="ov-subtitle">LLMに渡す情報7種類</div>
<div class="info-types">
  <div class="info-type">
    <div class="info-badge">①</div>
    <div class="info-content"><strong>システムプロンプト</strong>：役割・前提・制約・行動指針。AIエージェントの「ぶれない軸」</div>
  </div>
  <div class="info-type">
    <div class="info-badge">②</div>
    <div class="info-content"><strong>ユーザープロンプト</strong>：都度の指示・質問。人間からの直接入力</div>
  </div>
  <div class="info-type">
    <div class="info-badge">③</div>
    <div class="info-content"><strong>会話履歴</strong>：過去の対話記録。文脈の継続性を保つ。蓄積管理が必要</div>
  </div>
  <div class="info-type">
    <div class="info-badge">④</div>
    <div class="info-content"><strong>ツール実行結果</strong>：API応答・DB検索結果・計算結果</div>
  </div>
  <div class="info-type">
    <div class="info-badge">⑤</div>
    <div class="info-content"><strong>RAG検索結果</strong>：ナレッジベースから取得した関連文書・参考情報</div>
  </div>
  <div class="info-type">
    <div class="info-badge">⑥</div>
    <div class="info-content"><strong>構造化データ</strong>：テーブル・JSONなど整形された情報</div>
  </div>
  <div class="info-type">
    <div class="info-badge">⑦</div>
    <div class="info-content"><strong>外部コンテキスト</strong>：現在時刻・ユーザー属性・環境情報など</div>
  </div>
</div>

{mk_memory_key('出力品質の問題はモデルでなくコンテキスト設計の問題。何をRAMに載せるかが勝負。LostInMiddle・汚染・混乱の4課題を設計で解決')}
"""


# ────────────────────────────────────────────────────────────────────────────
OV_BUILDERS = {
    'ch04_s01': ov_s01,
    'ch04_s02': ov_s02,
    'ch04_s03': ov_s03,
    'ch04_s04': ov_s04,
}


def build_ch04_section(sec, all_sections):
    e     = htmllib.escape
    ch    = sec['ch']
    s     = sec['s']
    title = sec['title']
    sid   = f'ch{ch:02d}_s{s:02d}'
    color = CH_COLORS[ch]
    ch_title = CHAPTER_TITLES.get(ch, '')

    knowledge = sec.get('knowledge', '')
    scenario  = sec.get('scenario', '')
    quizzes   = sec.get('quizzes', [])

    ov_fn   = OV_BUILDERS.get(sid)
    ov_html = ov_fn(sec) if ov_fn else '<p>（概要カードなし）</p>'

    deep_html = format_deep_dive(knowledge, scenario, ch)
    quiz_html = build_quiz_html(quizzes, sid)

    flat_idx = next((j for j, x in enumerate(all_sections)
                     if x['ch'] == ch and x['s'] == s), None)
    prev_info = next_info = None
    if flat_idx is not None and flat_idx > 0:
        ps = all_sections[flat_idx - 1]
        prev_info = (f'ch{ps["ch"]:02d}.html', f'ch{ps["ch"]:02d}_s{ps["s"]:02d}', ps['title'])
    if flat_idx is not None and flat_idx < len(all_sections) - 1:
        ns = all_sections[flat_idx + 1]
        next_info = (f'ch{ns["ch"]:02d}.html', f'ch{ns["ch"]:02d}_s{ns["s"]:02d}', ns['title'])

    prev_link = (f'<a class="nav-btn" style="border-color:{color["accent"]};color:{color["accent"]};" href="{prev_info[0]}#{prev_info[1]}">&larr; {e(prev_info[2][:16])}</a>'
                 if prev_info else '<span class="nav-btn" style="opacity:.4;">← 前</span>')
    next_link = (f'<a class="nav-btn primary" href="{next_info[0]}#{next_info[1]}" style="background:{color["accent"]};border-color:{color["accent"]};">{e(next_info[2][:16])} &rarr;</a>'
                 if next_info else f'<a class="nav-btn primary" href="index.html" style="background:{color["accent"]};border-color:{color["accent"]};">学習マップへ ✓</a>')

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

<div class="card">
  <div class="card-title" style="color:{color["dark"]};">① 概要カード</div>
  {ov_html}
</div>

<div class="status-card">
  <span class="status-label">② 学習ステータス</span>
  <div class="status-btns" data-sid="{sid}">
    <button class="status-btn btn-done"  data-val="done"  onclick="setStatus('{sid}','done',this)">✓ Done</button>
    <button class="status-btn btn-later" data-val="later" onclick="setStatus('{sid}','later',this)">⏱ 後で確認する</button>
  </div>
</div>

<div class="deepdive-wrap">
  <button class="deepdive-btn" onclick="toggleDeepDive(this)">
    <span>📖 ③ 詳細を確認する（深掘りノート）</span>
    <span class="dd-arrow-icon" style="color:{color["accent"]};">▶</span>
  </button>
  <div class="deepdive-content">
    {deep_html}
  </div>
</div>

<div class="card" style="padding:18px 18px 10px;border-top:3px solid {color["accent"]};">
  <div class="quiz-hdr" style="color:{color["dark"]};">📝 ④ 理解度チェック（公式問題）</div>
  {quiz_html}
</div>

<div class="nav-footer">{prev_link}{next_link}</div>
<hr style="border:none;margin:8px 0 20px;">
</section>
'''


def main():
    with open(DATA_PATH, encoding='utf-8') as f:
        all_sections = json.load(f)

    ch04_secs = [s for s in all_sections if s['ch'] == 4]

    body_parts = [build_ch04_section(sec, all_sections) for sec in ch04_secs]

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>Ch.04 | 自動化レベルとワークフロー設計</title>
  <style>{FULL_CSS}</style>
</head>
<body>
{''.join(body_parts)}
<script>{COMMON_JS}</script>
</body>
</html>'''

    out_path = os.path.join(OUT_DIR, 'ch04.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Written: ch04.html ({len(html):,} chars, {len(ch04_secs)} sections)')


if __name__ == '__main__':
    main()
