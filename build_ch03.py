#!/usr/bin/env python3
# build_ch03.py — Ch03専用高品質HTMLジェネレータ（7セクション）

import json, os, sys, html as htmllib

OUT_DIR   = r"C:\Users\mikli\Downloads\AICX学習"
DATA_PATH = os.path.join(OUT_DIR, 'sections_data.json')

sys.path.insert(0, OUT_DIR)
from build_html import (
    clean_lines, join_sentences, _is_heading, format_deep_dive,
    build_quiz_html, COMMON_JS, COMMON_CSS, CH_COLORS, CHAPTER_TITLES,
    NOISE_RE, CALLOUT_MARKER,
)

C = CH_COLORS[3]  # {'accent':'#2a8a7a','dark':'#1a5e52','light':'#e0f5f0','mid':'#4db8a6'}

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

/* ── SECIモデル 2×2 ───────────────────── */
.seci-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0; }}
.seci-cell {{ border-radius:10px; padding:11px 13px; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.seci-head {{ font-size:12.5px; font-weight:700; margin-bottom:4px; display:flex; align-items:center; gap:5px; }}
.seci-body {{ font-size:12px; color:#333; line-height:1.5; }}
.seci-arrow {{ font-size:10px; opacity:.6; margin-left:auto; }}

/* ── データ種類カード（3列） ─────────────── */
.data-cards {{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin:10px 0; }}
.data-card {{ border-radius:10px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.data-card-head {{ padding:9px 8px; text-align:center; font-size:12px; font-weight:700; line-height:1.35; }}
.data-card-body {{ padding:9px 9px; font-size:11.5px; line-height:1.5; color:#333; background:#f9fafb; border-top:1px solid rgba(0,0,0,.06); }}

/* ── RAGフェーズ図 ───────────────────────── */
.rag-phase {{ border-radius:10px; overflow:hidden; margin:8px 0; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.rag-phase-head {{ padding:8px 14px; font-size:12.5px; font-weight:700; }}
.rag-phase-body {{ padding:10px 14px; background:#f9fafb; }}
.rag-steps {{ display:flex; align-items:center; gap:6px; flex-wrap:wrap; }}
.rag-step {{ background:white; border:1.5px solid; border-radius:7px; padding:6px 9px; font-size:11.5px; text-align:center; line-height:1.35; }}
.rag-step strong {{ display:block; font-size:10px; font-weight:600; opacity:.7; margin-bottom:2px; }}

/* ── 法的リスクカード ────────────────────── */
.risk-cards {{ display:flex; flex-direction:column; gap:8px; margin:10px 0; }}
.risk-card {{ border-radius:10px; border-left:4px solid; padding:10px 14px; }}
.risk-card-head {{ font-size:13px; font-weight:700; margin-bottom:5px; display:flex; align-items:center; gap:6px; }}
.risk-card-body {{ font-size:12px; line-height:1.55; color:#333; }}
.risk-card-action {{ font-size:11.5px; margin-top:5px; font-weight:600; color:{C['dark']}; }}

/* ── 7つの習慣リスト ────────────────────── */
.habit-list {{ display:flex; flex-direction:column; gap:6px; margin:10px 0; }}
.habit-item {{ display:flex; align-items:flex-start; gap:10px; border-radius:9px; padding:9px 13px; background:#f5fbf9; }}
.habit-num {{
  width:24px; height:24px; border-radius:50%; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-size:11px; font-weight:700; color:white; background:{C['accent']};
}}
.habit-body {{ flex:1; }}
.habit-title {{ font-size:13px; font-weight:700; margin-bottom:2px; color:{C['dark']}; }}
.habit-desc  {{ font-size:12px; color:#555; line-height:1.45; }}

/* ── フェーズゲート図 ────────────────────── */
.phase-gate {{ display:flex; flex-direction:column; gap:6px; margin:10px 0; }}
.phase-block {{ border-radius:10px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.phase-block-head {{ display:flex; justify-content:space-between; align-items:center; padding:9px 14px; font-weight:700; font-size:13px; }}
.phase-block-body {{ padding:9px 14px; font-size:12.5px; line-height:1.6; color:#333; background:#f9fafb; border-top:1px solid rgba(0,0,0,.06); }}
.gate-badge {{ background:white; border-radius:5px; padding:2px 8px; font-size:11px; font-weight:700; }}

/* ── 3層フレームワーク ──────────────────── */
.three-layer {{ display:flex; flex-direction:column; gap:6px; margin:10px 0; }}
.tlayer-item {{ border-radius:10px; padding:11px 14px; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.tlayer-head {{ display:flex; align-items:center; gap:8px; margin-bottom:5px; }}
.tlayer-num {{ width:22px; height:22px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:white; flex-shrink:0; }}
.tlayer-title {{ font-size:13px; font-weight:700; }}
.tlayer-dir {{ font-size:10.5px; opacity:.7; margin-left:auto; }}
.tlayer-body {{ font-size:12.5px; color:#333; line-height:1.55; }}
.tlayer-kpi {{ font-size:11.5px; color:{C['accent']}; margin-top:4px; font-weight:600; }}

/* ── 比較テーブル ───────────────────────── */
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


# ─── S01: ナレッジマネジメント ──────────────────────────────────────────────
def ov_s01(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">暗黙知と形式知の変換サイクル</div>
<div class="flow-diagram">
  <div class="flow-box flow-hi" style="background:{C['light']};border-color:{C['accent']};">暗黙知<br><span style="font-size:10px;font-weight:400;">経験・勘・コツ</span></div>
  <div class="flow-arrow">⇄</div>
  <div class="flow-box flow-hi" style="background:#e0f0f8;border-color:#2a7a8a;">形式知<br><span style="font-size:10px;font-weight:400;">文書・手順書・DB</span></div>
</div>
<ul class="point-list">
  <li><strong>暗黙知</strong>：言葉にしにくいノウハウ・勘。熟練者の頭の中に眠っている知識。AIは読めない</li>
  <li><strong>形式知</strong>：文書化・構造化されて他者と共有できる知識。AIが活用できる形式</li>
</ul>

<div class="ov-subtitle">SECIモデル（知識変換の4象限）</div>
<div class="seci-grid">
  <div class="seci-cell" style="background:{C['light']};">
    <div class="seci-head" style="color:{C['dark']};">共同化 <span class="seci-arrow">暗→暗</span></div>
    <div class="seci-body">体験・観察で暗黙知を共有。OJT・見習い・現場同行。AIは介在不可</div>
  </div>
  <div class="seci-cell" style="background:#e8f8f5;">
    <div class="seci-head" style="color:{C['dark']};">表出化 <span class="seci-arrow">暗→形</span></div>
    <div class="seci-body">暗黙知を言語化・文書化。ナレッジDB作成。<strong>AIが活用できる形への変換</strong></div>
  </div>
  <div class="seci-cell" style="background:#e0f5ee;">
    <div class="seci-head" style="color:{C['dark']};">連結化 <span class="seci-arrow">形→形</span></div>
    <div class="seci-body">形式知同士を統合・体系化。マニュアル整理・DB統合。<strong>RAGの土台</strong></div>
  </div>
  <div class="seci-cell" style="background:#d5f5ec;">
    <div class="seci-head" style="color:{C['dark']};">内面化 <span class="seci-arrow">形→暗</span></div>
    <div class="seci-body">形式知を実践で身体化。学習・トレーニング。AI出力を見て担当者が判断力を磨く</div>
  </div>
</div>

<div class="ov-subtitle">RAGとの接続</div>
<ul class="point-list">
  <li><strong>RAG（Retrieval-Augmented Generation）</strong>：ナレッジベース（形式知の集積）から必要な情報を検索し、LLMに与えて回答生成させる技術</li>
  <li>暗黙知を形式知化→ナレッジベース化→RAGで活用、という流れが組織のAI活用の基本戦略</li>
</ul>

{mk_memory_key('暗黙知→形式知→RAG活用が組織AI化の本質。SECIの「表出化」が最重要ステップ')}
"""


# ─── S02: データの種類と特性 ────────────────────────────────────────────────
def ov_s02(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">3種類のデータ</div>
<div class="data-cards">
  <div class="data-card">
    <div class="data-card-head" style="background:{C['light']};color:{C['dark']};">構造化データ</div>
    <div class="data-card-body">表形式。DB・スプレッドシート。<br>SQL等で処理可能。<br>全体の約20%</div>
  </div>
  <div class="data-card">
    <div class="data-card-head" style="background:#e8f8f5;color:#1a6050;">非構造化データ</div>
    <div class="data-card-body">メール・文書・音声・画像。<br><strong>企業データの約80%</strong>。<br>LLMの強みが活きる</div>
  </div>
  <div class="data-card">
    <div class="data-card-head" style="background:#d5f5ec;color:#155040;">半構造化データ</div>
    <div class="data-card-body">JSON・XML・HTML。<br>規則性はあるが表形式でない。<br>APIレスポンス等</div>
  </div>
</div>

<div class="ov-subtitle">メタデータと処理担い手</div>
<ul class="point-list">
  <li><strong>メタデータ</strong>：データについてのデータ。ファイルの作成日時・作者・タグ等。AIが「どのデータを参照すべきか」を判断する手がかりになる</li>
  <li><strong>処理担い手マッピング</strong>：構造化データ→従来DB/RPA、非構造化データ→LLM/AIエージェント、という適材適所の設計が重要</li>
</ul>

<table class="cmp-table">
  <tr><th>データ種別</th><th>処理担い手</th><th>AIエージェントへの適合性</th></tr>
  <tr><td>構造化</td><td>DB・RPA・従来システム</td><td>低（既存ツールで十分）</td></tr>
  <tr><td>非構造化</td><td>LLM・AIエージェント</td><td>高（LLMの最大の強み）</td></tr>
  <tr><td>半構造化</td><td>パーサー＋LLM組合せ</td><td>中（変換後に活用）</td></tr>
</table>

{mk_memory_key('企業データの8割は非構造化。そこにLLMの価値がある。構造化はDBとRPAに任せよ')}
"""


# ─── S03: RAGの仕組み ────────────────────────────────────────────────────
def ov_s03(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">RAGの2フェーズ</div>

<div class="rag-phase">
  <div class="rag-phase-head" style="background:{C['dark']};color:white;">
    フェーズ1：保存フェーズ（オフライン事前処理）
  </div>
  <div class="rag-phase-body">
    <div class="rag-steps">
      <div class="rag-step" style="border-color:{C['accent']};">
        <strong>① 文書取込</strong>PDF・Word・メール等
      </div>
      <div class="flow-arrow">→</div>
      <div class="rag-step" style="border-color:{C['accent']};">
        <strong>② チャンク分割</strong>適切な粒度に分割
      </div>
      <div class="flow-arrow">→</div>
      <div class="rag-step" style="border-color:{C['accent']};">
        <strong>③ ベクトル化</strong>意味を数値に変換
      </div>
      <div class="flow-arrow">→</div>
      <div class="rag-step" style="border-color:{C['accent']};">
        <strong>④ インデックス化</strong>ベクトルDBに格納
      </div>
    </div>
  </div>
</div>

<div class="rag-phase">
  <div class="rag-phase-head" style="background:{C['accent']};color:white;">
    フェーズ2：検索・生成フェーズ（リアルタイム）
  </div>
  <div class="rag-phase-body">
    <div class="rag-steps">
      <div class="rag-step" style="border-color:{C['mid']};">
        <strong>① クエリ</strong>ユーザーの質問
      </div>
      <div class="flow-arrow">→</div>
      <div class="rag-step" style="border-color:{C['mid']};">
        <strong>② セマンティック<br>検索</strong>意味で類似文書検索
      </div>
      <div class="flow-arrow">→</div>
      <div class="rag-step" style="border-color:{C['mid']};">
        <strong>③ コンテキスト<br>注入</strong>検索結果をプロンプトに付加
      </div>
      <div class="flow-arrow">→</div>
      <div class="rag-step" style="border-color:{C['mid']};">
        <strong>④ 回答生成</strong>LLMが応答
      </div>
    </div>
  </div>
</div>

<ul class="point-list">
  <li><strong>セマンティック検索</strong>：キーワード一致ではなく「意味の近さ」で検索。「売上が下がる」＝「収益減少」も拾える</li>
  <li><strong>グラウンディング</strong>：LLMの回答を外部の事実データに根拠づけること。ハルシネーション抑制の主要手段</li>
  <li>RAGは「検索精度」と「生成品質」の両方が必要。片方が弱いと全体が崩れる</li>
</ul>

{mk_memory_key('RAG＝保存(分割→ベクトル化→インデックス)＋検索・生成(セマンティック検索→コンテキスト注入→回答)の2フェーズ')}
"""


# ─── S04: AIガバナンスと法務 ────────────────────────────────────────────────
def ov_s04(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">3つの法的リスク</div>
<div class="risk-cards">
  <div class="risk-card" style="border-color:#c0392b;background:#fff5f5;">
    <div class="risk-card-head">⚖ 著作権リスク</div>
    <div class="risk-card-body">LLMが学習データの著作物をそのまま再現する可能性。生成物の著作権帰属も未解決（国・ケース依存）</div>
    <div class="risk-card-action">→ 生成物の社外公開前に確認プロセスを設ける</div>
  </div>
  <div class="risk-card" style="border-color:#e67e22;background:#fff8f0;">
    <div class="risk-card-head">🔐 個人情報保護法リスク</div>
    <div class="risk-card-body">顧客・従業員データをAIに入力する際の目的外利用・越境移転問題。クラウドAPIに送信するだけで違反になりうる</div>
    <div class="risk-card-action">→ マスキング処理・データの最小化・契約確認</div>
  </div>
  <div class="risk-card" style="border-color:#8e44ad;background:#fdf5ff;">
    <div class="risk-card-head">⚡ 責任分界点リスク</div>
    <div class="risk-card-body">AIの出力による損害の責任は誰が負うか？ベンダー・開発者・利用者間の責任が曖昧になりやすい</div>
    <div class="risk-card-action">→ 利用規約・契約でAI出力の最終確認責任を明記</div>
  </div>
</div>

<div class="ov-subtitle">AIポリシーの構成要素</div>
<ul class="point-list">
  <li><strong>利用ガイドライン</strong>：何に使っていいか・何に使ってはいけないか。禁止事項（機密情報の入力禁止等）を具体的に列挙</li>
  <li><strong>データ取扱いルール</strong>：社内データをAIに渡す際の分類・マスキング・保存ルール</li>
  <li><strong>承認プロセス</strong>：新規AIツール導入時の審査手順（IT・法務・経営の承認フロー）</li>
  <li><strong>モニタリング</strong>：AI出力品質の定期確認・インシデント発生時の報告ライン</li>
</ul>

{mk_memory_key('3大法的リスク＝著作権・個人情報・責任分界点。ガバナンスは「使う前」に設計する')}
"""


# ─── S05: AIエージェントが読みやすいデータを作る ─────────────────────────────
def ov_s05(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">AI Readyデータの7つの習慣</div>
<div class="habit-list">
  <div class="habit-item">
    <div class="habit-num">1</div>
    <div class="habit-body">
      <div class="habit-title">固有名詞を正確に表記</div>
      <div class="habit-desc">商品名・人名・部署名を略称・通称ではなく正式名称で統一。「営推」ではなく「営業推進部」</div>
    </div>
  </div>
  <div class="habit-item">
    <div class="habit-num">2</div>
    <div class="habit-body">
      <div class="habit-title">構造化して書く</div>
      <div class="habit-desc">見出し・箇条書き・テーブルを使う。AIは構造から情報の重要度を判断する</div>
    </div>
  </div>
  <div class="habit-item">
    <div class="habit-num">3</div>
    <div class="habit-body">
      <div class="habit-title">入力環境を統一</div>
      <div class="habit-desc">フォーマットばらつき（全角/半角混在・改行ルール不統一）はAIの解析精度を下げる</div>
    </div>
  </div>
  <div class="habit-item">
    <div class="habit-num">4</div>
    <div class="habit-body">
      <div class="habit-title">画像・図表にキャプション・注釈</div>
      <div class="habit-desc">画像だけではAIは読めない。テキストで補足説明を付ける（Alt属性・キャプション）</div>
    </div>
  </div>
  <div class="habit-item">
    <div class="habit-num">5</div>
    <div class="habit-body">
      <div class="habit-title">日付・期間を明示タグ</div>
      <div class="habit-desc">「先月」「最近」ではなく「2025年4月」と絶対表記。時制の曖昧さはRAG検索精度を下げる</div>
    </div>
  </div>
  <div class="habit-item">
    <div class="habit-num">6</div>
    <div class="habit-body">
      <div class="habit-title">バージョン管理</div>
      <div class="habit-desc">旧バージョンの文書とAIが混同しないよう、廃止文書は明示的に削除・アーカイブ</div>
    </div>
  </div>
  <div class="habit-item">
    <div class="habit-num">7</div>
    <div class="habit-body">
      <div class="habit-title">置き場所の一元化</div>
      <div class="habit-desc">ナレッジが散在すると検索漏れが起きる。RAGのインデックス対象を一箇所に集約</div>
    </div>
  </div>
</div>

{mk_memory_key('AIに見えないものは存在しないと同じ。7つの習慣で「AIが読める」データを作る')}
"""


# ─── S06: AIプロジェクトの進め方 ───────────────────────────────────────────
def ov_s06(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">AIプロジェクト特有の3つの不確実性</div>
<div class="seci-grid" style="grid-template-columns:1fr 1fr 1fr;">
  <div class="seci-cell" style="background:{C['light']};">
    <div class="seci-head" style="color:{C['dark']};">技術的不確実性</div>
    <div class="seci-body">「そもそもAIで解けるか」。精度・処理速度が要件を満たせるか、PoCで確認が必要</div>
  </div>
  <div class="seci-cell" style="background:#e8f8f5;">
    <div class="seci-head" style="color:{C['dark']};">業務適合性不確実性</div>
    <div class="seci-body">「現場の業務に馴染むか」。UI・フローが現場の実態に合うか、パイロットで検証</div>
  </div>
  <div class="seci-cell" style="background:#d5f5ec;">
    <div class="seci-head" style="color:{C['dark']};">効果不確実性</div>
    <div class="seci-body">「投資対効果が出るか」。ROIは導入前には確定できない。前提条件付きで試算し検証</div>
  </div>
</div>

<div class="ov-subtitle">A/Bフェーズ＋判断ゲート</div>
<div class="phase-gate">
  <div class="phase-block">
    <div class="phase-block-head" style="background:{C['dark']};color:white;">
      <span>フェーズA：PoC・概念実証</span>
      <span class="gate-badge" style="color:{C['dark']};">探索フェーズ</span>
    </div>
    <div class="phase-block-body">小規模・限定範囲で実施。「技術的に実現できるか」「期待効果が出るか」を仮説検証。目標：Go/No-Go/Pivotを判断できる根拠の収集</div>
  </div>
  <div style="text-align:center;font-size:20px;color:#bbb;">↓ 判断ゲート</div>
  <div style="text-align:center;background:#fff8dc;border-radius:8px;padding:8px 14px;font-size:12.5px;font-weight:700;color:#7a5500;">
    経営層の意思決定：Go → フェーズB / No-Go → 中止 / Pivot → 方向転換
  </div>
  <div style="text-align:center;font-size:20px;color:#bbb;">↓</div>
  <div class="phase-block">
    <div class="phase-block-head" style="background:{C['accent']};color:white;">
      <span>フェーズB：本格導入・展開</span>
      <span class="gate-badge" style="color:{C['accent']};">実装フェーズ</span>
    </div>
    <div class="phase-block-body">パイロット→ロールアウト→スケーリングの順で段階的に範囲拡大。KPI継続モニタリング</div>
  </div>
</div>

{mk_memory_key('AIプロジェクトは3種の不確実性を持つ。PoCで検証→判断ゲート→本格展開の順序を守る')}
"""


# ─── S07: AIプロジェクトの成功の定義（3層フレームワーク） ─────────────────────
def ov_s07(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">成功の3層フレームワーク（ボトムアップで達成・トップダウンで定義）</div>
<div class="three-layer">
  <div class="tlayer-item" style="background:#e0f5f0;">
    <div class="tlayer-head">
      <div class="tlayer-num" style="background:{C['accent']};">1</div>
      <div class="tlayer-title">精度層（土台）</div>
      <div class="tlayer-dir">まず達成すべき基盤</div>
    </div>
    <div class="tlayer-body">AIエージェントの出力品質が業務に使えるレベルに達しているか。<br>「正答率90%以上」「処理速度30秒以内」などの技術的合格基準</div>
    <div class="tlayer-kpi">計測：正答率・エラー率・処理時間</div>
  </div>
  <div style="text-align:center;font-size:18px;color:#aaa;">↑ 精度があって初めて定着を問える</div>
  <div class="tlayer-item" style="background:#c8ede6;">
    <div class="tlayer-head">
      <div class="tlayer-num" style="background:{C['dark']};">2</div>
      <div class="tlayer-title">定着層（中間）</div>
      <div class="tlayer-dir">現場が使い続けているか</div>
    </div>
    <div class="tlayer-body">現場担当者がAIエージェントを日常業務に組み込んで使い続けているか。導入直後だけ使われて形骸化していないか</div>
    <div class="tlayer-kpi">計測：継続利用率・DAU/MAU・ユーザー満足度</div>
  </div>
  <div style="text-align:center;font-size:18px;color:#aaa;">↑ 定着して初めて効果を問える</div>
  <div class="tlayer-item" style="background:#b0e5da;">
    <div class="tlayer-head">
      <div class="tlayer-num" style="background:#1a4a40;">3</div>
      <div class="tlayer-title">効果層（頂点）</div>
      <div class="tlayer-dir">経営が最重視する層</div>
    </div>
    <div class="tlayer-body">業務効率・コスト削減・売上など経営指標への貢献が出ているか。KGIとの接続が必要</div>
    <div class="tlayer-kpi">計測：工数削減・コスト削減・ROI・NPS</div>
  </div>
</div>

<ul class="point-list">
  <li><strong>ボトムアップで達成</strong>：精度が整ってから定着を問い、定着してから効果を測る。下層が崩れたまま上層は成立しない</li>
  <li><strong>トップダウンで定義</strong>：効果（KGI）から逆算してKPI・合格基準を設定する。ゴールから設計する</li>
</ul>

{mk_memory_key('成功＝精度（技術的合格）→定着（現場が使う）→効果（経営貢献）の3層。下から達成し、上から設計する')}
"""


# ────────────────────────────────────────────────────────────────────────────
OV_BUILDERS = {
    'ch03_s01': ov_s01,
    'ch03_s02': ov_s02,
    'ch03_s03': ov_s03,
    'ch03_s04': ov_s04,
    'ch03_s05': ov_s05,
    'ch03_s06': ov_s06,
    'ch03_s07': ov_s07,
}


def build_ch03_section(sec, all_sections):
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

    ch03_secs = [s for s in all_sections if s['ch'] == 3]

    body_parts = [build_ch03_section(sec, all_sections) for sec in ch03_secs]

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>Ch.03 | AIデータリテラシーとマネジメント</title>
  <style>{FULL_CSS}</style>
</head>
<body>
{''.join(body_parts)}
<script>{COMMON_JS}</script>
</body>
</html>'''

    out_path = os.path.join(OUT_DIR, 'ch03.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Written: ch03.html ({len(html):,} chars, {len(ch03_secs)} sections)')


if __name__ == '__main__':
    main()
