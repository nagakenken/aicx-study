#!/usr/bin/env python3
# build_ch02.py — Ch02専用高品質HTMLジェネレータ（3セクション）

import json, os, re, sys, html as htmllib

OUT_DIR   = r"C:\Users\mikli\Downloads\AICX学習"
DATA_PATH = os.path.join(OUT_DIR, 'sections_data.json')

sys.path.insert(0, OUT_DIR)
from build_html import (
    clean_lines, join_sentences, _is_heading, format_deep_dive,
    build_quiz_html, COMMON_JS, COMMON_CSS, CH_COLORS, CHAPTER_TITLES,
    NOISE_RE, CALLOUT_MARKER,
)

C = CH_COLORS[2]  # {'accent':'#6b4fa8','dark':'#4a3070','light':'#f0ebff','mid':'#9b7ed4'}

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

/* ── 3層ピラミッド ──────────────────────── */
.layer-diagram {{ display:flex; flex-direction:column; gap:6px; margin:10px 0; }}
.layer-item {{
  border-radius:10px; overflow:hidden;
  box-shadow:0 1px 3px rgba(0,0,0,.08);
}}
.layer-label {{
  display:flex; justify-content:space-between; align-items:center;
  padding:9px 14px; font-weight:700; font-size:13px;
}}
.layer-name {{ font-size:14px; }}
.layer-tag  {{ font-size:11px; opacity:.8; font-weight:600;
  background:rgba(255,255,255,.3); border-radius:4px; padding:1px 6px; }}
.layer-body {{
  padding:9px 14px; font-size:13px; line-height:1.65; color:#333;
  background:#f9fafb; border-top:1px solid rgba(0,0,0,.06);
}}
.layer-body strong {{ color:{C['dark']}; }}
.layer-arrow {{ text-align:center; font-size:18px; color:#bbb; line-height:1.2; }}

/* ── フロー図 ────────────────────────────── */
.flow-diagram {{
  display:flex; align-items:center; gap:5px; margin:10px 0;
  flex-wrap:wrap; justify-content:center;
}}
.flow-box {{
  background:#f5f5f7; border:1.5px solid #d0d7de; border-radius:8px;
  padding:8px 10px; font-size:12px; text-align:center; line-height:1.4; min-width:58px;
}}
.flow-box.flow-hi {{ font-weight:700; border-width:2px; }}
.flow-arrow {{ font-size:16px; color:#aaa; flex-shrink:0; }}

/* ── ECRSラダー ─────────────────────────── */
.ecrs-list {{ display:flex; flex-direction:column; gap:6px; margin:10px 0; }}
.ecrs-item {{
  display:flex; align-items:flex-start; gap:10px;
  border-radius:10px; padding:10px 14px;
  box-shadow:0 1px 3px rgba(0,0,0,.08);
}}
.ecrs-badge {{
  width:28px; height:28px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:13px; font-weight:800; flex-shrink:0; color:white;
}}
.ecrs-body {{ flex:1; }}
.ecrs-title {{ font-size:13px; font-weight:700; margin-bottom:2px; }}
.ecrs-desc  {{ font-size:12px; color:#555; line-height:1.45; }}
.ecrs-ex    {{ font-size:11.5px; color:{C['accent']}; margin-top:3px; font-style:italic; }}

/* ── 警告ボックス ────────────────────────── */
.warn-box {{
  border-radius:10px; background:#fff3cd; border-left:4px solid #e6a800;
  padding:12px 14px; margin:10px 0;
}}
.warn-title {{ font-weight:700; color:#7a5500; margin-bottom:5px; font-size:13px; }}
.warn-body  {{ font-size:12.5px; color:#5a4000; line-height:1.6; }}

/* ── 4手法カード ────────────────────────── */
.method-cards {{ display:flex; flex-direction:column; gap:8px; margin:10px 0; }}
.method-card {{
  border-radius:10px; border-left:4px solid;
  padding:10px 14px; background:#f9fafb;
}}
.method-head {{
  display:flex; align-items:center; gap:8px; margin-bottom:5px;
}}
.method-num {{
  width:22px; height:22px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:10px; font-weight:700; flex-shrink:0; color:white;
}}
.method-title {{ font-size:13px; font-weight:700; }}
.method-grain {{ font-size:11px; color:#888; margin-left:auto; }}
.method-body  {{ font-size:12px; line-height:1.55; color:#333; }}
.method-body strong {{ color:{C['dark']}; }}

/* ── 用途比較テーブル ───────────────────── */
.cmp-table {{ width:100%; border-collapse:collapse; margin:10px 0; font-size:12.5px; }}
.cmp-table th {{
  padding:7px 10px; color:white; font-size:12px; font-weight:700; text-align:center;
  background:{C['dark']};
}}
.cmp-table td {{ padding:7px 10px; border-bottom:1px solid #eee; vertical-align:top; line-height:1.55; }}
.cmp-table tr:nth-child(even) td {{ background:#f9f9f9; }}
.cmp-table td:first-child {{ font-weight:600; color:#666; font-size:12px; width:5em; }}
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


# ─── S01: 業務の構造的理解 ──────────────────────────────────────────────────
def ov_s01(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">業務の3層構造</div>
<div class="layer-diagram">
  <div class="layer-item">
    <div class="layer-label" style="background:{C['light']};color:{C['dark']};">
      <span class="layer-name">仕事（Work）</span>
      <span class="layer-tag">最大粒度</span>
    </div>
    <div class="layer-body">組織が果たすべき<strong>ミッション・目的</strong>の単位。例：「顧客満足度を向上させる」「新規顧客を獲得する」。AIエージェントが最終的に貢献する価値の軸</div>
  </div>
  <div class="layer-arrow">↓</div>
  <div class="layer-item">
    <div class="layer-label" style="background:#e8e0ff;color:{C['dark']};">
      <span class="layer-name">業務（Process）</span>
      <span class="layer-tag">中粒度</span>
    </div>
    <div class="layer-body"><strong>Input → Process → Output</strong> で構造化できる反復的な活動のまとまり。例：「受注処理」「採用スクリーニング」。AIエージェントが担う単位</div>
  </div>
  <div class="layer-arrow">↓</div>
  <div class="layer-item">
    <div class="layer-label" style="background:#d4c8f8;color:{C['dark']};">
      <span class="layer-name">作業（Task）</span>
      <span class="layer-tag">最小粒度</span>
    </div>
    <div class="layer-body">業務を構成する<strong>個別の手順・操作</strong>。例：「メール開封」「フォームへの入力」「確認ボタンのクリック」。RPAや個別ツールが担う単位</div>
  </div>
</div>

<div class="ov-subtitle">IPO（Input / Process / Output）モデル</div>
<div class="flow-diagram">
  <div class="flow-box flow-hi" style="background:{C['light']};border-color:{C['accent']};">Input<br><span style="font-size:10px;font-weight:400;">トリガー・入力データ</span></div>
  <div class="flow-arrow">→</div>
  <div class="flow-box flow-hi" style="background:#e8e0ff;border-color:{C['mid']};">Process<br><span style="font-size:10px;font-weight:400;">変換・判断・加工</span></div>
  <div class="flow-arrow">→</div>
  <div class="flow-box flow-hi" style="background:#d4c8f8;border-color:{C['dark']};">Output<br><span style="font-size:10px;font-weight:400;">成果物・後続へ</span></div>
</div>
<ul class="point-list">
  <li><strong>境界の明確化</strong>が重要：Inputは何か？Outputは誰が使うか？が曖昧なまま自動化すると「ゴミin・ゴミout」になる</li>
  <li><strong>As-Is分析</strong>：現状業務をIPOで構造化し、ボトルネックを可視化する出発点。プロセスウォークスルー（実際に手順を追う）と5W1Hヒアリングで情報収集</li>
</ul>

{mk_memory_key('仕事＝ミッション、業務＝AIが担うIPO単位、作業＝ツールが担う最小操作。3層で分けて設計せよ')}
"""


# ─── S02: BPR（業務改革）の基礎 ────────────────────────────────────────────
def ov_s02(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">BPRとは：改善ではなく「再設計」</div>
<ul class="point-list">
  <li><strong>BPR（Business Process Re-engineering）</strong>：既存プロセスを継続的に改善するのではなく、白紙から<strong>根本的に再設計</strong>する考え方</li>
  <li>既存の手順・組織・ルールをいったん「ゼロリセット」し「本来の目的に最適な業務とは何か」を問い直す</li>
  <li>AIエージェント導入は技術投資ではなくBPR実践の機会。まずプロセスを正しく設計してから自動化する</li>
</ul>

<div class="ov-subtitle">ECRS原則 — 優先順位つきの改善フレームワーク</div>
<div class="ecrs-list">
  <div class="ecrs-item" style="background:#f3efff;">
    <div class="ecrs-badge" style="background:{C['dark']};">E</div>
    <div class="ecrs-body">
      <div class="ecrs-title">Eliminate（排除）★最優先</div>
      <div class="ecrs-desc">その業務・作業は<strong>本当に必要か？</strong>なくせるなら最大の効果。</div>
      <div class="ecrs-ex">例：承認フローを廃止 / 重複入力の除去</div>
    </div>
  </div>
  <div class="ecrs-item" style="background:#e8e0ff;">
    <div class="ecrs-badge" style="background:{C['accent']};">C</div>
    <div class="ecrs-body">
      <div class="ecrs-title">Combine（結合）</div>
      <div class="ecrs-desc">複数の手順・担当者・作業を<strong>まとめて効率化</strong>できないか。</div>
      <div class="ecrs-ex">例：入力と確認を1ステップに統合</div>
    </div>
  </div>
  <div class="ecrs-item" style="background:#f0ebff;">
    <div class="ecrs-badge" style="background:{C['mid']};">R</div>
    <div class="ecrs-body">
      <div class="ecrs-title">Rearrange（順序変更）</div>
      <div class="ecrs-desc">処理の<strong>順番を変える</strong>ことで待ち時間・手戻りを削減できないか。</div>
      <div class="ecrs-ex">例：確認を後回しにせず前工程で実施</div>
    </div>
  </div>
  <div class="ecrs-item" style="background:#f5f2ff;">
    <div class="ecrs-badge" style="background:#b09ed8;">S</div>
    <div class="ecrs-body">
      <div class="ecrs-title">Simplify（簡素化）</div>
      <div class="ecrs-desc">残った作業を<strong>単純化・標準化</strong>して自動化のしやすさを高める。</div>
      <div class="ecrs-ex">例：入力フォームの選択肢化 / ルールの文書化</div>
    </div>
  </div>
</div>

<div class="warn-box">
  <div class="warn-title">⚠ 「汚いプロセスを自動化」という罠</div>
  <div class="warn-body">非効率・複雑・矛盾を含む現行プロセスをそのままAI化すると、問題を高速化するだけ。BPRでプロセスを整理してからAIエージェントを乗せることが鉄則</div>
</div>

{mk_memory_key('BPR＝白紙から再設計。ECRS順（排除→結合→順序→簡素化）。汚いプロセスの自動化は禁忌')}
"""


# ─── S03: 業務可視化の手法 ────────────────────────────────────────────────
def ov_s03(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">4手法の粒度マップ（粗→細）</div>
<div class="method-cards">
  <div class="method-card" style="border-color:{C['dark']};">
    <div class="method-head">
      <div class="method-num" style="background:{C['dark']};">1</div>
      <div class="method-title">IPOモデル</div>
      <div class="method-grain">粒度：最粗</div>
    </div>
    <div class="method-body"><strong>Input→Process→Output</strong> の3ボックスで業務を一言把握。AIエージェントの担当範囲の外枠を決める出発点。「何を受け取って何を返すか」を定義</div>
  </div>
  <div class="method-card" style="border-color:{C['accent']};">
    <div class="method-head">
      <div class="method-num" style="background:{C['accent']};">2</div>
      <div class="method-title">SIPOC分析</div>
      <div class="method-grain">粒度：粗</div>
    </div>
    <div class="method-body">IPOを拡張し <strong>Supplier（入力提供者） → Input → Process → Output → Customer（出力受取者）</strong> の5要素で整理。関係者の漏れを防ぐ。誰がデータを渡し誰が使うかを明確化</div>
  </div>
  <div class="method-card" style="border-color:{C['mid']};">
    <div class="method-head">
      <div class="method-num" style="background:{C['mid']};">3</div>
      <div class="method-title">HTA（階層的タスク分析）</div>
      <div class="method-grain">粒度：中〜細</div>
    </div>
    <div class="method-body">業務を<strong>目標→サブ目標→タスク→サブタスク</strong>と階層的に分解。暗黙知として処理されている「なぜその順番か」を可視化。AIエージェントに渡す作業の粒度を揃えるのに有効</div>
  </div>
  <div class="method-card" style="border-color:#9b7ed4;">
    <div class="method-head">
      <div class="method-num" style="background:#9b7ed4;">4</div>
      <div class="method-title">業務フロー図（スイムレーン）</div>
      <div class="method-grain">粒度：最細</div>
    </div>
    <div class="method-body">担当者（人間・AI・システム）を<strong>横レーン</strong>に分けて処理の流れを矢印で可視化。条件分岐・待ち時間・ボトルネックが一目で分かる。AIエージェントの設計書として最も詳細な成果物</div>
  </div>
</div>

<div class="ov-subtitle">使い分けのポイント</div>
<table class="cmp-table">
  <tr><th>手法</th><th>目的</th></tr>
  <tr><td>IPO</td><td>業務範囲の確定・スコープ合意</td></tr>
  <tr><td>SIPOC</td><td>関係者・データの洗い出し</td></tr>
  <tr><td>HTA</td><td>暗黙知の言語化・タスク粒度の整理</td></tr>
  <tr><td>フロー図</td><td>設計・開発チームへの引き渡し仕様書</td></tr>
</table>

{mk_memory_key('IPO→SIPOC→HTA→フロー図。粒度は粗→細。DiscoveryはIPO/SIPOCで把握し、DefinitionでHTAとフロー図に詳細化')}
"""


# ────────────────────────────────────────────────────────────────────────────
OV_BUILDERS = {
    'ch02_s01': ov_s01,
    'ch02_s02': ov_s02,
    'ch02_s03': ov_s03,
}


def build_ch02_section(sec, all_sections):
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


def main():
    with open(DATA_PATH, encoding='utf-8') as f:
        all_sections = json.load(f)

    ch02_secs = [s for s in all_sections if s['ch'] == 2]

    body_parts = [build_ch02_section(sec, all_sections) for sec in ch02_secs]

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>Ch.02 | 業務の基礎</title>
  <style>{FULL_CSS}</style>
</head>
<body>
{''.join(body_parts)}
<script>{COMMON_JS}</script>
</body>
</html>'''

    out_path = os.path.join(OUT_DIR, 'ch02.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Written: ch02.html ({len(html):,} chars, {len(ch02_secs)} sections)')


if __name__ == '__main__':
    main()
