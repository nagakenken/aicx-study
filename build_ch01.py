#!/usr/bin/env python3
# build_ch01.py — Ch01専用高品質HTMLジェネレータ
# 8セクション全て手設計の概要カード（図解・ビジュアル要素つき）

import json, os, re, sys, html as htmllib

OUT_DIR   = r"C:\Users\mikli\Downloads\AICX学習"
DATA_PATH = os.path.join(OUT_DIR, 'sections_data.json')

sys.path.insert(0, OUT_DIR)
from build_html import (
    clean_lines, join_sentences, _is_heading, format_deep_dive,
    build_quiz_html, COMMON_JS, COMMON_CSS, CH_COLORS, CHAPTER_TITLES,
    NOISE_RE, CALLOUT_MARKER,
)

C = CH_COLORS[1]   # {'accent':'#2d6a9f','dark':'#1e3a5f','light':'#e8f0fe','mid':'#5a9fd4'}

# ────────────────────────────────────────────────────────────────────────────
# 追加 CSS（ビジュアル要素）
# ────────────────────────────────────────────────────────────────────────────
EXTRA_CSS = f"""
/* ── フェーズ図 ─────────────────────────── */
.phase-diagram {{ display:flex; flex-direction:column; gap:6px; margin:12px 0; }}
.phase-item {{ border-radius:10px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.phase-label {{
  display:flex; justify-content:space-between; align-items:center;
  padding:8px 12px; font-weight:700; font-size:13px;
}}
.phase-name {{ font-size:14px; }}
.phase-period {{ font-size:11px; opacity:.75; font-weight:500; }}
.phase-body {{
  padding:9px 12px; font-size:13px; line-height:1.65; color:#333;
  background:#f9fafb; border-top:1px solid rgba(0,0,0,.06);
}}
.phase-body strong {{ color:{C['dark']}; }}
.phase-arrow {{ text-align:center; font-size:18px; color:#bbb; line-height:1.2; }}

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

/* ── コスト式 ────────────────────────────── */
.cost-formula {{
  background:#1a1a2e; color:#e8f0fe; border-radius:10px;
  padding:13px 16px; font-family:'Courier New',monospace;
  font-size:12.5px; line-height:2; margin:10px 0;
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

/* ── OVサブタイトル ─────────────────────── */
.ov-subtitle {{
  font-size:13px; font-weight:700; margin:14px 0 8px;
  padding-bottom:4px; border-bottom:1.5px solid {C['light']};
  color:{C['dark']};
}}

/* ── 比較テーブル ───────────────────────── */
.cmp-table {{ width:100%; border-collapse:collapse; margin:10px 0; font-size:12.5px; }}
.cmp-table th {{
  padding:6px 10px; color:white; font-size:12px; font-weight:700; text-align:center;
  background:{C['dark']};
}}
.cmp-table th:nth-child(2) {{ background:#1a5e52; }}
.cmp-table td {{ padding:7px 10px; border-bottom:1px solid #eee; vertical-align:top; line-height:1.55; }}
.cmp-table tr:nth-child(even) td {{ background:#f9f9f9; }}
.cmp-table td:first-child {{ font-weight:600; color:#666; white-space:nowrap; font-size:12px; width:6em; }}

/* ── タイプカード（3列） ─────────────────── */
.type-cards {{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin:10px 0; }}
.type-card {{ border-radius:10px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.type-card-head {{ padding:9px 6px; text-align:center; font-size:12px; font-weight:700; line-height:1.35; }}
.type-card-body {{ padding:8px 8px; font-size:11.5px; line-height:1.55; color:#333; background:#f9fafb; border-top:1px solid rgba(0,0,0,.06); }}
.type-card-trigger {{ font-size:10px; font-weight:600; margin-bottom:3px; opacity:.75; }}

/* ── リスクカード（2×2） ────────────────── */
.risk-cards {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0; }}
.risk-card {{ border-radius:10px; border:1.5px solid; padding:10px 11px; }}
.risk-card-head {{ font-size:12.5px; font-weight:700; margin-bottom:5px; display:flex; align-items:center; gap:5px; }}
.risk-card-body {{ font-size:11.5px; line-height:1.5; color:#555; }}
.risk-card-action {{ font-size:11px; margin-top:5px; font-weight:600; }}

/* ── 3構成要素 ──────────────────────────── */
.three-part {{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin:10px 0; }}
.part-card {{ border-radius:10px; padding:12px 8px; text-align:center; }}
.part-icon {{ font-size:22px; margin-bottom:5px; }}
.part-name {{ font-size:12px; font-weight:700; margin-bottom:2px; }}
.part-sub  {{ font-size:10.5px; color:#888; margin-bottom:4px; }}
.part-desc {{ font-size:11px; color:#555; line-height:1.4; }}

/* ── 自律性ステージ ──────────────────────── */
.stage-list {{ display:flex; flex-direction:column; gap:5px; margin:10px 0; }}
.stage-item {{
  display:flex; align-items:flex-start; gap:8px;
  border-radius:8px; padding:8px 10px; background:#f9fafb;
}}
.stage-item.stage-now {{ background:{C['light']}; border:1.5px solid {C['accent']}; }}
.stage-num {{
  width:22px; height:22px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:11px; font-weight:700; flex-shrink:0; color:white;
}}
.stage-body {{ flex:1; }}
.stage-title {{ font-size:13px; font-weight:700; margin-bottom:2px; }}
.stage-desc {{ font-size:11.5px; color:#555; line-height:1.4; }}

/* ── メリットグリッド ───────────────────── */
.benefit-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0; }}
.benefit-col {{ border-radius:10px; padding:10px 12px; }}
.benefit-head {{ font-size:12px; font-weight:700; margin-bottom:6px; }}
.benefit-list {{ list-style:none; padding:0; display:flex; flex-direction:column; gap:4px; }}
.benefit-list li {{
  font-size:11.5px; line-height:1.5; color:#333;
  padding-left:14px; position:relative;
}}
.benefit-list li::before {{ content:'✓'; position:absolute; left:0; font-size:10px; }}

/* ── ROI/TCO ────────────────────────────── */
.roi-box {{
  background:#f0f4ff; border-radius:10px; border-left:3px solid #4285f4;
  padding:12px 14px; margin:10px 0;
}}
.roi-title {{ font-weight:700; color:#1a4bae; margin-bottom:6px; font-size:12px; }}
.roi-formula {{ font-family:'Courier New',monospace; font-size:12.5px; line-height:1.9; color:#333; }}

/* ── MCP比較 ────────────────────────────── */
.mcp-compare {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0; }}
.mcp-side {{ border-radius:10px; padding:10px 12px; }}
.mcp-side-head {{ font-size:12px; font-weight:700; margin-bottom:6px; text-align:center; }}
.mcp-side ul {{ list-style:none; padding:0; }}
.mcp-side li {{ font-size:11.5px; line-height:1.5; color:#555; padding-left:12px; position:relative; margin-bottom:3px; }}
.mcp-side li::before {{ content:'·'; position:absolute; left:0; font-weight:900; }}
.mn-box {{
  background:#fff0e0; border-radius:8px; padding:8px 12px;
  font-size:12.5px; text-align:center; font-weight:700; color:#8a3e06;
  margin:8px 0;
}}

/* ── トレンドカード ─────────────────────── */
.trend-cards {{ display:flex; flex-direction:column; gap:8px; margin:10px 0; }}
.trend-card {{ border-radius:10px; border-left:4px solid; padding:10px 14px; }}
.trend-head {{ font-size:13px; font-weight:700; margin-bottom:5px; display:flex; align-items:center; gap:6px; }}
.trend-num {{
  width:20px; height:20px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:10px; font-weight:700; flex-shrink:0; color:white;
}}
.trend-body {{ font-size:12.5px; line-height:1.6; color:#333; }}
.trend-tech {{ font-size:11.5px; color:#666; margin-top:4px; }}
.trend-chip {{
  display:inline-block; border-radius:4px;
  padding:1px 6px; font-size:10px; font-weight:700;
  margin-right:3px; margin-bottom:2px;
}}
"""

FULL_CSS = COMMON_CSS + EXTRA_CSS


# ────────────────────────────────────────────────────────────────────────────
# カスタム概要カード（8セクション手設計）
# ────────────────────────────────────────────────────────────────────────────

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


# ─── S01: 生成AIの基礎 ────────────────────────────────────────────────────
def ov_s01(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">AIの進化 3フェーズ</div>
<div class="phase-diagram">
  <div class="phase-item">
    <div class="phase-label" style="background:{C['light']};color:{C['dark']};">
      <span class="phase-name">フェーズ1 ｜ 作るAI</span>
      <span class="phase-period">〜2022年</span>
    </div>
    <div class="phase-body">主役：研究者・AIエンジニア。AIを使うには開発者を介する必要があった。壁＝<strong>技術の壁</strong>。経営層にとってAIは「IT投資の一種」</div>
  </div>
  <div class="phase-arrow">↓</div>
  <div class="phase-item">
    <div class="phase-label" style="background:#e6f4ea;color:#1a7340;">
      <span class="phase-name">フェーズ2 ｜ 使うAI</span>
      <span class="phase-period">2022〜現在</span>
    </div>
    <div class="phase-body">ChatGPT登場で「誰でも使える」時代へ転換。主役はビジネスパーソン。競争優位＝<strong>いかに使いこなすか</strong>。多くの組織が今ここ</div>
  </div>
  <div class="phase-arrow">↓</div>
  <div class="phase-item">
    <div class="phase-label" style="background:#fff0e0;color:#8a3e06;">
      <span class="phase-name">フェーズ3 ｜ 任せるAI</span>
      <span class="phase-period">2024〜進行中</span>
    </div>
    <div class="phase-body">目標を与えればAIが自律的にタスク分解・実行。「回答ツール」から「行動する存在」へ。ストラテジストの役割＝<strong>何を任せ・人が何を担うかを設計</strong></div>
  </div>
</div>

<div class="ov-subtitle">LLMの動作原理</div>
<div class="flow-diagram">
  <div class="flow-box">テキスト<br>入力</div>
  <div class="flow-arrow">→</div>
  <div class="flow-box">トークン<br>分割</div>
  <div class="flow-arrow">→</div>
  <div class="flow-box flow-hi" style="background:{C['light']};border-color:{C['accent']};">次トークンを<br>確率的に予測</div>
  <div class="flow-arrow">→</div>
  <div class="flow-box">文章<br>完成</div>
</div>
<ul class="point-list">
  <li><strong>ハルシネーション</strong>：確率的に「自然な言葉」をつなぐ構造的特性。事実と異なる内容を自信満々に生成する</li>
  <li>非構造化データ（議事録・メール等）の処理がLLM最大の強み。企業データの8割以上が非構造化</li>
</ul>

<div class="ov-subtitle">トークン・コスト・コンテキストウィンドウ</div>
<div class="cost-formula">API利用料 = 入力トークン数 × 単価<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;＋ 出力トークン数 × 単価<br><br>個人向けサブスク ≠ 業務組込みの従量課金</div>
<ul class="point-list">
  <li><strong>コンテキストウィンドウ</strong>：一度に渡せるトークンの上限。必要部分だけ渡すRAG設計が合理的</li>
  <li>AIエージェントのコストはAPI費用より<strong>構築・運用・保守費用が大きい</strong>（TCO視点）</li>
</ul>

{mk_memory_key('AIの進化3フェーズ（作る→使う→任せる）。ストラテジストの役割＝「何をAIに任せ、人が何を担うか」を設計する')}
"""


# ─── S02: AIエージェントの定義と構成要素 ─────────────────────────────────
def ov_s02(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">ツール活用 vs エージェント活用</div>
<table class="cmp-table">
  <thead><tr><th style="width:5.5em;">観点</th><th>ツールとしての活用</th><th style="background:{C['accent']};">エージェントとしての活用</th></tr></thead>
  <tbody>
    <tr><td>関わり方</td><td>人間が1往復ずつ指示</td><td>目標を与えれば自律実行</td></tr>
    <tr><td>スコープ</td><td>1タスクを手伝う</td><td>業務プロセス全体を推進</td></tr>
    <tr><td>後続作業</td><td>人間が次の手を考える</td><td>AIが計画→実行→修正</td></tr>
    <tr><td>例</td><td>「領収書を分類して」</td><td>申請書作成まで自動完結</td></tr>
  </tbody>
</table>

<div class="ov-subtitle">AIエージェントの三位一体</div>
<div class="three-part">
  <div class="part-card" style="background:{C['light']};">
    <div class="part-icon">🧠</div>
    <div class="part-name" style="color:{C['dark']};">頭脳</div>
    <div class="part-sub">LLM</div>
    <div class="part-desc">指示を理解し判断・推論するエンジン。モデル選択がコスト・精度・速度を決める</div>
  </div>
  <div class="part-card" style="background:#e6f4ea;">
    <div class="part-icon">📚</div>
    <div class="part-name" style="color:#1a7340;">記憶</div>
    <div class="part-sub">ナレッジベース</div>
    <div class="part-desc">社内マニュアル・FAQ・対応履歴。なければ汎用回答しかできない</div>
  </div>
  <div class="part-card" style="background:#fff0e0;">
    <div class="part-icon">🤝</div>
    <div class="part-name" style="color:#8a3e06;">手足</div>
    <div class="part-sub">ツール連携</div>
    <div class="part-desc">メール送信・DB更新・ファイル生成。なければ「考えて終わり」になる</div>
  </div>
</div>

<div class="ov-subtitle">自律性の4段階</div>
<div class="stage-list">
  <div class="stage-item">
    <div class="stage-num" style="background:#aaa;">1</div>
    <div class="stage-body">
      <div class="stage-title">反応型</div>
      <div class="stage-desc">入力に即座に反応するのみ。過去から学ばず自発的な提案もなし（例：翻訳ツール）</div>
    </div>
  </div>
  <div class="stage-item">
    <div class="stage-num" style="background:{C['mid']};">2</div>
    <div class="stage-body">
      <div class="stage-title">支援型</div>
      <div class="stage-desc">AIが回答案を提示し、<strong>最終判断は必ず人間</strong>が行う。選択・承認は人の手に残る</div>
    </div>
  </div>
  <div class="stage-item stage-now">
    <div class="stage-num" style="background:{C['accent']};">3</div>
    <div class="stage-body">
      <div class="stage-title">協働型 ← 現在の主流</div>
      <div class="stage-desc">定型問い合わせはAI自律対応、複雑ケースだけ人間にエスカレーション。一部の判断をAIが自律実行</div>
    </div>
  </div>
  <div class="stage-item">
    <div class="stage-num" style="background:{C['dark']};">4</div>
    <div class="stage-body">
      <div class="stage-title">自律型</div>
      <div class="stage-desc">目標を与えれば計画から実行まで自律完遂。技術的に可能だが、判断ミスリスクから段階的に移行</div>
    </div>
  </div>
</div>

{mk_memory_key('AIエージェント＝頭脳（LLM）・記憶（KB）・手足（ツール）の三位一体。どれが欠けても「物足りない」エージェントになる')}
"""


# ─── S03: AIエージェントの起動タイプ ─────────────────────────────────────
def ov_s03(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">起動タイプ 3分類</div>
<div class="type-cards">
  <div class="type-card">
    <div class="type-card-head" style="background:{C['light']};color:{C['dark']};">
      <div class="type-card-trigger">きっかけ：人の指示</div>
      💬 指示型
    </div>
    <div class="type-card-body">人がチャットやボタンで明示的に依頼。ChatGPT・Claudeへのプロンプト入力が典型。<strong>基本形</strong></div>
  </div>
  <div class="type-card">
    <div class="type-card-head" style="background:#e6f4ea;color:#1a7340;">
      <div class="type-card-trigger">きっかけ：時刻・日時</div>
      ⏰ 定時型
    </div>
    <div class="type-card-body">毎朝8時にニュース要約・毎週月曜にレポート生成。効果が見えやすく<strong>初期導入に向く</strong></div>
  </div>
  <div class="type-card">
    <div class="type-card-head" style="background:#fff0e0;color:#8a3e06;">
      <div class="type-card-trigger">きっかけ：システム検知</div>
      ⚡ 条件型
    </div>
    <div class="type-card-body">在庫低下で発注書生成、エラー検知でチケット起票。<strong>現場に追加負荷をかけない</strong>設計</div>
  </div>
</div>

<div class="callout-box" style="border-left-color:{C['accent']};background:{C['light']};">
  <span class="callout-icon">💡</span>
  <div>
    <strong>指示型 vs 条件型 — 見分けポイント</strong><br>
    「AIエージェントに直接依頼したか？」が判別の鍵。<br>
    営業担当者がCRMにリードを登録したことをきっかけに自動でメールを作成する場合、担当者はAIに直接依頼していない → <strong>条件型</strong>。<br>
    条件型は現場の通常業務フローをそのまま変えずにAIを組み込めるため、形骸化リスクを下げる効果がある。
  </div>
</div>

<ul class="point-list">
  <li>1つのエージェントが複数の起動タイプを持つことも可能（場面ごとに適切なタイプを組み合わせる）</li>
  <li>定時型は導入効果の測定がしやすく（実行前後の比較が明確）、初期PoC向き</li>
</ul>

{mk_memory_key('指示型 vs 条件型の見分けポイント＝「AIエージェントに直接依頼したか」。CRMへのデータ登録をきっかけとした自動起動は条件型')}
"""


# ─── S04: RPAとAIエージェントの違い ─────────────────────────────────────
def ov_s04(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">RPA vs AIエージェント</div>
<table class="cmp-table">
  <thead><tr><th>観点</th><th>RPA</th><th style="background:{C['accent']};">AIエージェント</th></tr></thead>
  <tbody>
    <tr><td>動き方</td><td>ルール通りに自動実行</td><td>状況を理解して判断</td></tr>
    <tr><td>入力</td><td>定型データ・定型操作が前提</td><td>非構造化データにも対応</td></tr>
    <tr><td>例外</td><td>想定外の入力で処理停止</td><td>文脈から推測して継続</td></tr>
    <tr><td>精度</td><td>ルールが正しければ100%正確</td><td>確率的動作（ハルシ有）</td></tr>
    <tr><td>比喩</td><td>融通は利かないが<br>頼んだことは完璧にやる職人</td><td>状況判断ができる<br>インテリジェントな助手</td></tr>
  </tbody>
</table>

<div class="ov-subtitle">定型 vs 判断 — 3つの選択基準</div>
<ul class="point-list">
  <li><strong>① 例外的な判断が必要か</strong>：手順が完全に定義でき例外処理が不要 → ルールベース。文脈判断が必要 → LLM</li>
  <li><strong>② 入力が定型か</strong>：CSV・帳票など形式固定 → ルールベース。メール・チャット・自由記述 → LLM</li>
  <li><strong>③ 例外の頻度</strong>：例外がほぼゼロ → ルールベース安定。例外が頻発 → 人間介入コストが増えルールベース不向き</li>
</ul>

<div class="ov-subtitle">ハイパーオートメーション（定型＋AIの「いいとこ取り」）</div>
<div class="callout-box" style="border-left-color:{C['accent']};background:{C['light']};">
  <span class="callout-icon">⚙️</span>
  <div>
    <strong>受注処理の例：</strong><br>
    STEP1 添付ファイル取得 → <span style="color:#1a7340;font-weight:600;">定型処理</span><br>
    STEP2 発注書の品目・数量・納期を読み取り → <span style="color:{C['accent']};font-weight:600;">AI処理（フォーマット多様）</span><br>
    STEP3 在庫と照合し納期判断 → <span style="color:{C['accent']};font-weight:600;">AI処理（総合判断）</span><br>
    STEP4 受注管理システムへ登録 → <span style="color:#1a7340;font-weight:600;">定型処理</span><br>
    STEP5 確認メール送信 → <span style="color:#1a7340;font-weight:600;">定型処理</span>
  </div>
</div>

{mk_memory_key('手順が完全に決まっている→RPA、文脈判断が必要→AIエージェント。ハイパーオートメーションで「いいとこ取り」の業務設計を')}
"""


# ─── S05: エージェントの接続標準 MCP ─────────────────────────────────────
def ov_s05(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">なぜ「接続標準」が必要か — M×N問題</div>
<div class="mn-box">
  AIモデル3種 × 接続ツール5種 = 15通りの個別API連携が必要<br>
  モデルが増え、ツールが増えるほど開発・保守コストが爆増 → M×N問題
</div>

<div class="ov-subtitle">MCP = AIとツールを接続する「USB標準」</div>
<div class="mcp-compare">
  <div class="mcp-side" style="background:#fff0e0;border:1.5px solid #e07a30;">
    <div class="mcp-side-head" style="color:#8a3e06;">❌ 個別API連携</div>
    <ul>
      <li>ツールごとに異なる「注文の書き方」</li>
      <li>どのAPIを呼ぶか開発者が事前設計</li>
      <li>ツールが増えるたびに開発コスト増</li>
      <li>M×N通りの連携処理が必要</li>
    </ul>
  </div>
  <div class="mcp-side" style="background:{C['light']};border:1.5px solid {C['accent']};">
    <div class="mcp-side-head" style="color:{C['dark']};">✅ MCP標準化</div>
    <ul>
      <li>共通の窓口フォーマットに統一</li>
      <li>LLMが使えるツールを<strong>自動認識・選択</strong></li>
      <li>M＋N通りの対応で済む</li>
      <li>将来の拡張コストが大幅に削減</li>
    </ul>
  </div>
</div>

<div class="callout-box" style="border-left-color:{C['accent']};background:{C['light']};">
  <span class="callout-icon">💡</span>
  <div>
    <strong>MCP最大の変化：ツール選択の自動化</strong><br>
    「来週の会議を設定して、参加者にSlackで通知して、議題をドキュメントに残して」と指示するだけで、AIがカレンダー・Slack・ドキュメントを自動選択して実行。<strong>開発者がルーティングのロジックを書く必要がない</strong>。
  </div>
</div>

<ul class="point-list">
  <li><strong>接続方式の判断基準</strong>：今後の拡張計画があるか。拡張が見込まれるなら初期コストがやや高くてもMCPを選択</li>
  <li>MCPは誰でも作成・公開できるオープン仕様。信頼できない提供元のMCPはセキュリティリスクになる</li>
</ul>

{mk_memory_key('MCPはAIとツールを接続する「USB標準」。拡張計画があればMCPを選択し、M×N問題によるコスト増大を回避する')}
"""


# ─── S06: AIエージェント導入の価値 ──────────────────────────────────────
def ov_s06(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">定量的 vs 定性的メリット</div>
<div class="benefit-grid">
  <div class="benefit-col" style="background:#e8f0fe;border:1.5px solid {C['accent']};">
    <div class="benefit-head" style="color:{C['dark']};">📊 定量的メリット</div>
    <ul class="benefit-list">
      <li>月間工数削減（例: 75時間）</li>
      <li>年間人件費削減（例: 511万円）</li>
      <li>エラー率の低下（5% → 1%）</li>
      <li>処理速度の向上</li>
    </ul>
    <div style="margin-top:8px;font-size:11px;color:{C['dark']};font-weight:600;">→ 経営層への説明で説得力を持つ</div>
  </div>
  <div class="benefit-col" style="background:#e6f4ea;border:1.5px solid #34a853;">
    <div class="benefit-head" style="color:#1a7340;">✨ 定性的メリット</div>
    <ul class="benefit-list">
      <li>顧客体験：24時間365日即時対応</li>
      <li>対応品質の均一化</li>
      <li>従業員体験：定型業務から解放</li>
      <li>創造的な業務への集中</li>
    </ul>
    <div style="margin-top:8px;font-size:11px;color:#1a7340;font-weight:600;">→ 現場担当者に響くメリット</div>
  </div>
</div>

<div class="ov-subtitle">ROIとTCO — 投資判断の基本</div>
<div class="roi-box">
  <div class="roi-title">💰 ROI（Return on Investment）= 投資対効果</div>
  <div class="roi-formula">ROI正確計算には TCO（総所有コスト）が必要<br><br>TCO = API利用料<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;＋ 初期構築費用<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;＋ ナレッジベース整備・更新費<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;＋ プロンプト改善・監視・保守の工数</div>
</div>

<div class="callout-box" style="border-left-color:{C['accent']};background:{C['light']};">
  <span class="callout-icon">💡</span>
  <div>
    <strong>ROIの数字だけで投資判断を完結させない</strong><br>
    定量的メリット＋定性的メリット＋リスク（S07）の<strong>3面を総合評価</strong>するのがストラテジストの姿勢。API費用だけを見て「安い」と判断すると運用開始後に「こんなにかかるとは」となる。
  </div>
</div>

{mk_memory_key('ROIはTCO（API費用＋構築・運用費用）で正確に計算。定量・定性・リスクの3面を総合評価する')}
"""


# ─── S07: AIエージェントのリスクと対策 ──────────────────────────────────
def ov_s07(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">4カテゴリのリスクと判別観点</div>
<div class="risk-cards">
  <div class="risk-card" style="border-color:#ea4335;background:#fef8f8;">
    <div class="risk-card-head" style="color:#b31412;">🎯 信頼性リスク</div>
    <div class="risk-card-body">出力・判断が正確でないリスク。代表例：<strong>ハルシネーション</strong>（もっともらしい誤情報の生成）</div>
    <div class="risk-card-action" style="color:#b31412;">判別：回答・判断そのものが誤っている</div>
    <div class="risk-card-action" style="color:#1a7340;">対策：RAG（社内文書を参照して回答）</div>
  </div>
  <div class="risk-card" style="border-color:#ff9500;background:#fffbf0;">
    <div class="risk-card-head" style="color:#c67200;">😴 形骸化リスク</div>
    <div class="risk-card-body">導入しても現場で使われないリスク。原因：操作性・精度・業務フロー不適合・目的不明確</div>
    <div class="risk-card-action" style="color:#c67200;">判別：現場での利用率が低い</div>
    <div class="risk-card-action" style="color:#1a7340;">対策：条件型で業務に自然に組み込む。利用状況のモニタリング</div>
  </div>
  <div class="risk-card" style="border-color:#6b4fa8;background:#f9f5ff;">
    <div class="risk-card-head" style="color:#4a3070;">🔲 ブラックボックス化</div>
    <div class="risk-card-body">管理されないまま「野良エージェント」が増え、誰が何を管理しているか不明な状態</div>
    <div class="risk-card-action" style="color:#4a3070;">判別：管理実態・責任者が不明</div>
    <div class="risk-card-action" style="color:#1a7340;">対策：管理台帳（目的・参照データ・責任者・更新状況）の整備</div>
  </div>
  <div class="risk-card" style="border-color:#1a5e52;background:#f0faf8;">
    <div class="risk-card-head" style="color:#1a5e52;">🔐 セキュリティ・倫理</div>
    <div class="risk-card-body">情報漏えい・不正利用・偏り・不適切な判断。例：<strong>プロンプトインジェクション</strong>・バイアス</div>
    <div class="risk-card-action" style="color:#1a5e52;">判別：安全性・公平性・法令の問題</div>
    <div class="risk-card-action" style="color:#1a7340;">対策：入力検査＋出力制限＋アクセス権管理の多層的対策</div>
  </div>
</div>

<div class="callout-box" style="border-left-color:{C['accent']};background:{C['light']};">
  <span class="callout-icon">💡</span>
  <div>
    <strong>「リスクがあるから導入しない」ではなく「リスクを管理しながら段階的に導入する」</strong><br>
    各リスクに対して判別ポイントと対策をセットで理解することが試験のポイント。
  </div>
</div>

{mk_memory_key('リスク判別4軸：精度→信頼性、利用定着→形骸化、管理体制→ブラックボックス化、安全性・公平性→セキュリティ倫理')}
"""


# ─── S08: 生成AIの発展トレンド ───────────────────────────────────────────
def ov_s08(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">3つの進化軸（2026年以降のトレンド）</div>
<div class="trend-cards">
  <div class="trend-card" style="border-left-color:{C['accent']};">
    <div class="trend-head" style="color:{C['dark']};">
      <div class="trend-num" style="background:{C['accent']};">1</div>
      エージェント化 — AIを「実行できる存在」に
    </div>
    <div class="trend-body">「回答する存在」から「業務を進める存在」へ。人がシステムを操作しなければ進まなかった業務の一部を自動化の対象として再検討できる</div>
    <div class="trend-tech">
      <span class="trend-chip" style="background:{C['light']};color:{C['dark']};">API連携</span>
      <span class="trend-chip" style="background:{C['light']};color:{C['dark']};">MCP</span>
      <span class="trend-chip" style="background:{C['light']};color:{C['dark']};">ブラウザ操作</span>
      <span class="trend-chip" style="background:{C['light']};color:{C['dark']};">フィジカルAI</span>
    </div>
  </div>
  <div class="trend-card" style="border-left-color:#2a8a7a;">
    <div class="trend-head" style="color:#1a5e52;">
      <div class="trend-num" style="background:#2a8a7a;">2</div>
      ドメイン特化 — AIを「専門家」にする
    </div>
    <div class="trend-body">汎用AIに「専門家としての深さ」を持たせる動き。医療・法律・金融・製造など領域ごとの深い知識が必要な場面で活躍</div>
    <div class="trend-tech">
      <span class="trend-chip" style="background:#e0f5f0;color:#1a5e52;">RAG（専門DB参照）</span>
      <span class="trend-chip" style="background:#e0f5f0;color:#1a5e52;">ファインチューニング</span>
      <span class="trend-chip" style="background:#e0f5f0;color:#1a5e52;">パーソナライズ</span>
      <span class="trend-chip" style="background:#e0f5f0;color:#1a5e52;">検索連携</span>
    </div>
  </div>
  <div class="trend-card" style="border-left-color:#6b4fa8;">
    <div class="trend-head" style="color:#4a3070;">
      <div class="trend-num" style="background:#6b4fa8;">3</div>
      モデル強化 — AIの「基礎能力」を上げる
    </div>
    <div class="trend-body">エージェント化・特化の基盤となるモデルの性能向上。マルチモーダル化により文字以外（画像・音声・動画）も処理可能に</div>
    <div class="trend-tech">
      <span class="trend-chip" style="background:#f0ebff;color:#4a3070;">モデル規模拡大</span>
      <span class="trend-chip" style="background:#f0ebff;color:#4a3070;">マルチモーダル化</span>
      <span class="trend-chip" style="background:#f0ebff;color:#4a3070;">小型・軽量化</span>
      <span class="trend-chip" style="background:#f0ebff;color:#4a3070;">推論能力強化</span>
    </div>
  </div>
</div>

<ul class="point-list">
  <li>トレンドを用語で暗記するのでなく「<strong>自社の業務や導入判断に本当に必要か</strong>」を見極める視点が重要</li>
  <li>マルチモーダル導入の判断基準：「自社の業務に画像・音声・動画の入力場面があるか」で判断</li>
  <li>ドメイン特化：汎用AIと特化型AIをどう使い分けるか、自社で特化が必要な領域を整理することが求められる</li>
</ul>

{mk_memory_key('トレンドの本質：AIは「回答する存在」から「業務を進める存在」へ。エージェント化・特化・モデル強化の3軸で把握')}
"""


# ────────────────────────────────────────────────────────────────────────────
# Section HTML builder (Ch01 専用)
# ────────────────────────────────────────────────────────────────────────────

OV_BUILDERS = {
    'ch01_s01': ov_s01,
    'ch01_s02': ov_s02,
    'ch01_s03': ov_s03,
    'ch01_s04': ov_s04,
    'ch01_s05': ov_s05,
    'ch01_s06': ov_s06,
    'ch01_s07': ov_s07,
    'ch01_s08': ov_s08,
}


def build_ch01_section(sec, all_sections):
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

    # カスタム概要カード
    ov_fn   = OV_BUILDERS.get(sid)
    ov_html = ov_fn(sec) if ov_fn else '<p>（概要カードなし）</p>'

    # 深掘りノート・クイズ（共通関数を流用）
    deep_html = format_deep_dive(knowledge, scenario, ch)
    quiz_html = build_quiz_html(quizzes, sid)

    # ナビゲーション
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


# ────────────────────────────────────────────────────────────────────────────
# メイン
# ────────────────────────────────────────────────────────────────────────────

def main():
    with open(DATA_PATH, encoding='utf-8') as f:
        all_sections = json.load(f)

    ch01_secs = [s for s in all_sections if s['ch'] == 1]

    body_parts = [build_ch01_section(sec, all_sections) for sec in ch01_secs]

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>Ch.01 | 生成AIとAIエージェントの基礎</title>
  <style>{FULL_CSS}</style>
</head>
<body>
{''.join(body_parts)}
<script>{COMMON_JS}</script>
</body>
</html>'''

    out_path = os.path.join(OUT_DIR, 'ch01.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Written: ch01.html ({len(html):,} chars, {len(ch01_secs)} sections)')


if __name__ == '__main__':
    main()
