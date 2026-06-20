#!/usr/bin/env python3
# build_ch06.py — Ch06専用高品質HTMLジェネレータ（5セクション）

import json, os, sys, html as htmllib

OUT_DIR   = r"C:\Users\mikli\Downloads\AICX学習"
DATA_PATH = os.path.join(OUT_DIR, 'sections_data.json')

sys.path.insert(0, OUT_DIR)
from build_html import (
    clean_lines, join_sentences, _is_heading, format_deep_dive,
    build_quiz_html, COMMON_JS, COMMON_CSS, CH_COLORS, CHAPTER_TITLES,
    NOISE_RE, CALLOUT_MARKER,
)

C = CH_COLORS[6]  # {'accent':'#2a6e3a','dark':'#1a4a26','light':'#e0f4e6','mid':'#4a9e5c'}

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

/* ── 5Dモデルステップ ───────────────────── */
.five-d {{ display:flex; gap:4px; margin:10px 0; flex-wrap:nowrap; overflow-x:auto; }}
.five-d-step {{
  flex:1; min-width:50px; border-radius:8px; padding:8px 6px; text-align:center;
  box-shadow:0 1px 3px rgba(0,0,0,.1);
  display:flex; flex-direction:column; align-items:center; gap:4px;
}}
.five-d-num {{ font-size:10px; font-weight:700; opacity:.7; }}
.five-d-d   {{ font-size:16px; font-weight:800; }}
.five-d-name {{ font-size:10px; font-weight:600; line-height:1.3; }}
.five-d-step.active {{ outline:2px solid {C['dark']}; outline-offset:2px; }}

/* ── マトリクス 2×2 ─────────────────────── */
.matrix-2x2 {{
  display:grid; grid-template-columns:auto 1fr 1fr; margin:10px 0;
  border:1px solid #e0e0e0; border-radius:10px; overflow:hidden; font-size:12px;
}}
.m-blank {{ background:#f5f5f7; }}
.m-col-head {{ padding:7px 10px; background:{C['dark']}; color:white; font-weight:700; text-align:center; }}
.m-row-head {{ padding:8px 10px; background:{C['light']}; font-weight:700; color:{C['dark']}; writing-mode:horizontal-tb; font-size:11px; text-align:center; }}
.m-cell {{ padding:9px 11px; border-left:1px solid #eee; border-top:1px solid #eee; line-height:1.5; }}
.m-cell.hi {{ background:#e8f5eb; font-weight:600; }}

/* ── 要件定義書4要素 ────────────────────── */
.req-cards {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0; }}
.req-card {{ border-radius:10px; border-left:4px solid; padding:10px 13px; }}
.req-head {{ font-size:12.5px; font-weight:700; margin-bottom:4px; }}
.req-body {{ font-size:12px; color:#333; line-height:1.5; }}
.req-ex   {{ font-size:11px; color:#777; margin-top:4px; font-style:italic; }}

/* ── プロンプト技法カード ─────────────────── */
.prompt-cards {{ display:flex; flex-direction:column; gap:8px; margin:10px 0; }}
.prompt-card {{ border-radius:10px; border-left:5px solid; padding:10px 14px; background:#f9fafb; }}
.prompt-head {{ display:flex; align-items:center; gap:8px; margin-bottom:5px; }}
.prompt-name {{ font-size:13px; font-weight:700; }}
.prompt-body {{ font-size:12px; color:#333; line-height:1.55; }}
.prompt-note {{ font-size:11.5px; color:{C['accent']}; margin-top:4px; font-weight:600; }}

/* ── 3用語比較 ──────────────────────────── */
.term-cmp {{ display:flex; flex-direction:column; gap:6px; margin:10px 0; }}
.term-row {{ border-radius:9px; padding:9px 13px; display:flex; gap:10px; align-items:flex-start; }}
.term-badge {{ font-size:10px; font-weight:700; border-radius:5px; padding:2px 7px; flex-shrink:0; color:white; margin-top:2px; }}
.term-content {{ font-size:12px; color:#333; line-height:1.5; }}
.term-content strong {{ color:{C['dark']}; }}

/* ── 展開ステップ ───────────────────────── */
.deploy-steps {{ display:flex; flex-direction:column; gap:6px; margin:10px 0; }}
.deploy-step {{ border-radius:10px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.deploy-step-head {{ padding:9px 14px; font-weight:700; font-size:13px; display:flex; justify-content:space-between; align-items:center; }}
.deploy-step-tag  {{ font-size:10.5px; opacity:.8; background:rgba(255,255,255,.3); border-radius:4px; padding:1px 7px; }}
.deploy-step-body {{ padding:9px 14px; font-size:12.5px; line-height:1.6; color:#333; background:#f9fafb; border-top:1px solid rgba(0,0,0,.06); }}
.deploy-arrow {{ text-align:center; font-size:18px; color:#bbb; line-height:1.2; }}

/* ── AI-SECIモデル ──────────────────────── */
.ai-seci {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0; }}
.ai-seci-cell {{ border-radius:10px; padding:11px 13px; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.ai-seci-head {{ font-size:12.5px; font-weight:700; margin-bottom:4px; color:{C['dark']}; }}
.ai-seci-arrow {{ font-size:10px; opacity:.6; }}
.ai-seci-body {{ font-size:12px; color:#333; line-height:1.5; }}

/* ── 比較テーブル ───────────────────────── */
.cmp-table {{ width:100%; border-collapse:collapse; margin:10px 0; font-size:12.5px; }}
.cmp-table th {{
  padding:7px 10px; color:white; font-size:12px; font-weight:700; text-align:center;
  background:{C['dark']};
}}
.cmp-table td {{ padding:7px 10px; border-bottom:1px solid #eee; vertical-align:top; line-height:1.55; }}
.cmp-table tr:nth-child(even) td {{ background:#f0f9f2; }}
.cmp-table td:first-child {{ font-weight:600; color:#555; font-size:12px; }}
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

def five_d_bar(active_step):
    steps = [
        ('D', 'Discovery', '発見'),
        ('D', 'Definition', '定義'),
        ('D', 'Design', '設計'),
        ('D', 'Development\n&PoC', '開発検証'),
        ('D', 'Deployment\n&Scale', '展開定着'),
    ]
    colors = ['#1a4a26', '#2a6e3a', '#3a8e4a', '#4aae5a', '#5abe6a']
    html = '<div class="five-d">'
    for i, (d, name, jp) in enumerate(steps):
        cls = 'five-d-step active' if i + 1 == active_step else 'five-d-step'
        bg = colors[i] if i + 1 == active_step else f'rgba({int(colors[i][1:3],16)},{int(colors[i][3:5],16)},{int(colors[i][5:7],16)},.35)'
        fg = 'white' if i + 1 == active_step else '#555'
        html += (f'<div class="{cls}" style="background:{bg};color:{fg};">'
                 f'<div class="five-d-num">Step{i+1}</div>'
                 f'<div class="five-d-d">{d}</div>'
                 f'<div class="five-d-name">{jp}</div>'
                 f'</div>')
    html += '</div>'
    return html


# ─── S01: 5DモデルStep1 Discovery ──────────────────────────────────────────
def ov_s01(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">5Dモデル全体像</div>
{five_d_bar(1)}

<div class="ov-subtitle">Discovery：「何を自動化するか」を決める3ステップ</div>
<ul class="point-list">
  <li><strong>① ボトルネック特定</strong>：処理が遅い・ミスが多い・特定担当者に依存・反復的で付加価値が低い業務を洗い出す。Ch02の業務分析手法（SIPOC・HTA）を活用</li>
  <li><strong>② AI適合性診断</strong>：ボトルネックがあってもAI化すべきかは別の問題。2段階フィルタリングが核心</li>
  <li><strong>③ 優先順位マトリクス</strong>：複数候補がある場合「期待効果の大きさ」×「実現のしやすさ」の2軸で整理</li>
</ul>

<div class="ov-subtitle">AI適合性診断：高い vs 低い</div>
<div class="matrix-2x2">
  <div class="m-blank" style="background:{C['light']};padding:7px;font-size:10.5px;font-weight:700;color:{C['dark']};"></div>
  <div class="m-col-head">AI適合性 高</div>
  <div class="m-col-head" style="background:#888;">AI適合性 低</div>
  <div class="m-row-head">条件</div>
  <div class="m-cell hi">非構造化データ処理を含む<br>文脈に応じた判断が必要<br>ある程度のミスが許容できる or HITLで補完</div>
  <div class="m-cell">100%正確性が法的に要求<br>対人共感が本質的<br>機密データの外部送信不可<br>物理的操作が伴う</div>
</div>

<div class="ov-subtitle">優先順位マトリクス</div>
<table class="cmp-table">
  <tr><th></th><th>実現しやすい</th><th>実現が難しい</th></tr>
  <tr><td>効果大</td><td style="background:#e8f5eb;font-weight:700;">★最優先（初期導入の筆頭候補）</td><td>中長期検討対象</td></tr>
  <tr><td>効果小</td><td>余裕があれば対応</td><td>後回しまたは非対象</td></tr>
</table>

{mk_memory_key('Discovery＝ボトルネック特定→AI適合性診断（2段階フィルタ）→優先順位マトリクス。「ボトルネックだからAI化」は誤り')}
"""


# ─── S02: 5DモデルStep2 Definition ────────────────────────────────────────
def ov_s02(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">5Dモデル全体像</div>
{five_d_bar(2)}

<div class="ov-subtitle">Definitionの4つの成果物</div>
<div class="req-cards">
  <div class="req-card" style="border-color:{C['dark']};background:{C['light']};">
    <div class="req-head">① 業務フローチャート</div>
    <div class="req-body">対象業務を詳細に可視化。HTAとIPOを活用。AIと人間の担当範囲を切り分ける。暗黙知を形式知化する</div>
    <div class="req-ex">Ch02で学んだスイムレーン図がここで本格活用</div>
  </div>
  <div class="req-card" style="border-color:{C['accent']};background:#f0faf2;">
    <div class="req-head">② 要件定義書（叩き台）</div>
    <div class="req-body">機能要件（何をするか）・非機能要件（どの水準で）・制約条件（守るべきルール）・前提条件（あらかじめ満たされている条件）の4要素</div>
    <div class="req-ex">ストラテジストは完全な文書でなく「叩き台」を作る役割</div>
  </div>
  <div class="req-card" style="border-color:{C['mid']};background:#f5fbf6;">
    <div class="req-head">③ ペルソナ定義</div>
    <div class="req-body">AIエージェントを使う典型ユーザーの描写。年齢でなく「出力をどう使い・何を判断するか」を定義。直接ユーザーと間接ユーザー（監督者）の両方</div>
    <div class="req-ex">例：「スコアで一次選考する人事担当」vs「根拠を見て絞り込むEM」では必要な出力が異なる</div>
  </div>
  <div class="req-card" style="border-color:#5ab86a;background:#eaf9ec;">
    <div class="req-head">④ 合格基準（事前定義）</div>
    <div class="req-body">PoCでの合否判定に使う定量基準。「なんとなく90%以上」でなく業務要求から逆算した根拠が必要</div>
    <div class="req-ex">合格基準（一回限り）vs KPI（運用中の継続測定）を区別</div>
  </div>
</div>

<ul class="point-list">
  <li>Definition＝「何をやりたいか」を「どう実現するか」に橋渡しするステップ</li>
  <li>曖昧なままDesignに進むと「AIと人間の担当範囲が不明確」→後続で大きな手戻りが発生</li>
</ul>

{mk_memory_key('Definition＝業務フローチャート・要件定義書・ペルソナ・合格基準の4成果物。叩き台で十分。合格基準は事前に数値で定義')}
"""


# ─── S03: 5DモデルStep3 Design ────────────────────────────────────────────
def ov_s03(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">5Dモデル全体像</div>
{five_d_bar(3)}

<div class="ov-subtitle">Designの3領域</div>
<ul class="point-list">
  <li><strong>コンテキスト設計</strong>：AIエージェントへの指示設計（システムプロンプト・Few-shot・Chain-of-Thought）</li>
  <li><strong>I/O設計</strong>：入力と出力の形式設計（JSON等の構造化出力）</li>
  <li><strong>セキュリティ設計</strong>：データマスキング・アクセス権限・ログ設計</li>
</ul>

<div class="ov-subtitle">コンテキスト設計の3技法</div>
<div class="prompt-cards">
  <div class="prompt-card" style="border-color:{C['dark']};">
    <div class="prompt-head">
      <div class="prompt-name">システムプロンプト</div>
    </div>
    <div class="prompt-body">AIエージェントの役割・前提・制約・行動指針を定義する最上位の指示。「あなたはエンジニア採用の一次スクリーニング担当です」のように役割を明示。<strong>設計に最も時間をかけるべき要素</strong></div>
  </div>
  <div class="prompt-card" style="border-color:{C['accent']};">
    <div class="prompt-head">
      <div class="prompt-name">Few-shotプロンプト</div>
    </div>
    <div class="prompt-body">入力例と出力例の組み合わせを複数示すことで、期待する出力形式・判断傾向をAIに示す技法。
      <div class="prompt-note">注意：例の選び方が出力品質を左右。合格例・不合格例・<strong>境界事例</strong>をバランスよく含める。偏った例のみでは精度が下がる</div>
    </div>
  </div>
  <div class="prompt-card" style="border-color:{C['mid']};">
    <div class="prompt-head">
      <div class="prompt-name">Chain-of-Thought（CoT）</div>
    </div>
    <div class="prompt-body">AIに思考過程を段階的に出力させる技法。「まず○○を抽出し、次に照合し、最後にスコアを算出する」と順序を明示。複数の判断を組み合わせる処理に特に有効。
      <div class="prompt-note">注意：トークン消費が増える。すべてのタスクに使わず、複雑な多段判断に限定</div>
    </div>
  </div>
</div>

<div class="ov-subtitle">I/O設計：JSON出力の重要性</div>
<ul class="point-list">
  <li>自然言語のまま出力を受け取ると後続システムへの自動連携が困難。「85点くらい」と返されるとシステムが止まる</li>
  <li><strong>JSON形式</strong>で出力させることで機械的な処理が可能に。スキーマ（構造の事前定義）をシステムプロンプトで指定</li>
  <li>例：<code style="background:#f0f0f0;padding:1px 5px;border-radius:3px;font-size:11px;">{{"overall_score": 85, "recommendation": "通過", "reasons": [...]}}</code></li>
</ul>

{mk_memory_key('Design＝コンテキスト（システムプロンプト・Few-shot・CoT）・I/O（JSON化）・セキュリティの3領域。Few-shotは境界事例を必ず含める')}
"""


# ─── S04: 5DモデルStep4 Development & PoC ────────────────────────────────
def ov_s04(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">5Dモデル全体像</div>
{five_d_bar(4)}

<div class="ov-subtitle">3用語の厳密な違い</div>
<div class="term-cmp">
  <div class="term-row" style="background:{C['light']};">
    <div class="term-badge" style="background:{C['dark']};">プロトタイプ</div>
    <div class="term-content"><strong>設計した仕組みが技術的に動くかを確認する試作品</strong>。対象：開発・設計メンバー。問い：「この設計で本当に動くか」</div>
  </div>
  <div class="term-row" style="background:#e8f5eb;">
    <div class="term-badge" style="background:{C['accent']};">PoC</div>
    <div class="term-content"><strong>業務上・技術上の実現可能性を示す検証</strong>。対象：意思決定者。問い：「この方法で効果が期待できるか」「導入に進む価値があるか」。Go/No-Go/Pivotを判断する</div>
  </div>
  <div class="term-row" style="background:#d5f5e3;">
    <div class="term-badge" style="background:{C['mid']};">MVP</div>
    <div class="term-content"><strong>最小限の価値を提供できる実用品</strong>。対象：実際の業務担当者・顧客。問い：「最小限でも使ってもらえるか」→改善へ</div>
  </div>
</div>

<div class="ov-subtitle">サンドボックス vs パイロットの違い</div>
<table class="cmp-table">
  <tr><th></th><th>サンドボックス</th><th>パイロット</th></tr>
  <tr><td>フェーズ</td><td>Development段階</td><td>Deployment初期</td></tr>
  <tr><td>データ</td><td>テスト用データ</td><td>実データ</td></tr>
  <tr><td>ユーザー</td><td>開発・設計メンバー</td><td>実際の業務担当者</td></tr>
  <tr><td>目的</td><td>安全な動作確認</td><td>実運用の課題確認</td></tr>
</table>

<div class="ov-subtitle">Go / No-Go / Pivot判断</div>
<ul class="point-list">
  <li><strong>Go</strong>：定義済みの合格基準を達成→本番展開へ</li>
  <li><strong>No-Go</strong>：効果が見込めない・技術的に実現不可→中止</li>
  <li><strong>Pivot</strong>：元の方向性は維持しつつ手段・対象・設計を転換→再検証</li>
  <li>判断の根拠は常にDefinitionで設定した<strong>合格基準</strong>。主観的判断を排除</li>
</ul>

{mk_memory_key('プロトタイプ（動くか確認）・PoC（効果があるか確認）・MVP（最小実用品）は別物。Go/No-Go/Pivotは合格基準で機械的に判断')}
"""


# ─── S05: 5DモデルStep5 Deployment & Scale ───────────────────────────────
def ov_s05(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">5Dモデル全体像</div>
{five_d_bar(5)}

<div class="ov-subtitle">段階的展開の3ステップ</div>
<div class="deploy-steps">
  <div class="deploy-step">
    <div class="deploy-step-head" style="background:{C['dark']};color:white;">
      <span>パイロット導入</span>
      <span class="deploy-step-tag">限定範囲・実データ</span>
    </div>
    <div class="deploy-step-body">
      サンドボックスとの違い：<strong>実データ・実ユーザー・本番環境</strong>で動かす。<br>
      目的①実環境でしか見つからない品質問題の発見②運用手順の妥当性確認③小さな成功実績の獲得（次の展開の根拠に）
    </div>
  </div>
  <div class="deploy-arrow">↓</div>
  <div class="deploy-step">
    <div class="deploy-step-head" style="background:{C['accent']};color:white;">
      <span>ロールアウト</span>
      <span class="deploy-step-tag">対象範囲の段階的拡大</span>
    </div>
    <div class="deploy-step-body">
      「<strong>同じ機能を、より多くの人に届ける</strong>」。機能自体は変わらない。<br>
      段階的に広げることでリスクを管理可能な範囲に収める。各段階で問題を検出・修正してから次へ
    </div>
  </div>
  <div class="deploy-arrow">↓</div>
  <div class="deploy-step">
    <div class="deploy-step-head" style="background:{C['mid']};color:white;">
      <span>スケーリング</span>
      <span class="deploy-step-tag">機能・範囲の拡張</span>
    </div>
    <div class="deploy-step-body">
      ロールアウトが「同じ機能を広げる」のに対し、<strong>対象業務の拡大・新機能の追加</strong>など能力そのものを拡張する。エージェント連携・マルチエージェント化など
    </div>
  </div>
</div>

<div class="ov-subtitle">AI-SECIモデル（人間×AIの知識循環）</div>
<div class="ai-seci">
  <div class="ai-seci-cell" style="background:{C['light']};">
    <div class="ai-seci-head">共同化 <span class="ai-seci-arrow">暗→暗</span></div>
    <div class="ai-seci-body">担当者がAI出力を日々確認し、感覚的な判断を蓄積</div>
  </div>
  <div class="ai-seci-cell" style="background:#e8f5eb;">
    <div class="ai-seci-head">表出化 <span class="ai-seci-arrow">暗→形</span></div>
    <div class="ai-seci-body">蓄積した暗黙知がAIへのフィードバックとして言語化・明文化</div>
  </div>
  <div class="ai-seci-cell" style="background:#d5f5e3;">
    <div class="ai-seci-head">連結化 <span class="ai-seci-arrow">形→形</span></div>
    <div class="ai-seci-body">フィードバックが既存のプロンプト・ナレッジベースに統合</div>
  </div>
  <div class="ai-seci-cell" style="background:#c0edd0;">
    <div class="ai-seci-head">内面化 <span class="ai-seci-arrow">形→暗</span></div>
    <div class="ai-seci-body">改善されたAI出力を通じて担当者が新たな判断力を習得</div>
  </div>
</div>

<ul class="point-list">
  <li>このサイクルが回ることで<strong>AIの精度と人間の判断力が同時に向上</strong>。組織の知的資産が増強される</li>
  <li><strong>KPIモニタリング</strong>：アウトプット指標（処理件数）でなくアウトカム指標（処理時間削減・判定一致率・入社後活躍度）を追う。短期・長期に分けて設計</li>
</ul>

{mk_memory_key('展開＝パイロット（実環境検証）→ロールアウト（同機能を広げる）→スケーリング（機能拡張）。AI-SECIで人間とAIが共に成長するサイクルを回せ')}
"""


# ────────────────────────────────────────────────────────────────────────────
OV_BUILDERS = {
    'ch06_s01': ov_s01,
    'ch06_s02': ov_s02,
    'ch06_s03': ov_s03,
    'ch06_s04': ov_s04,
    'ch06_s05': ov_s05,
}


def build_ch06_section(sec, all_sections):
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

    ch06_secs = [s for s in all_sections if s['ch'] == 6]

    body_parts = [build_ch06_section(sec, all_sections) for sec in ch06_secs]

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>Ch.06 | AIエージェントを実装する5Dモデル</title>
  <style>{FULL_CSS}</style>
</head>
<body>
{''.join(body_parts)}
<script>{COMMON_JS}</script>
</body>
</html>'''

    out_path = os.path.join(OUT_DIR, 'ch06.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Written: ch06.html ({len(html):,} chars, {len(ch06_secs)} sections)')


if __name__ == '__main__':
    main()
