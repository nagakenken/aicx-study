#!/usr/bin/env python3
# build_ch05.py — Ch05専用高品質HTMLジェネレータ（5セクション）

import json, os, sys, html as htmllib

OUT_DIR   = r"C:\Users\mikli\Downloads\AICX学習"
DATA_PATH = os.path.join(OUT_DIR, 'sections_data.json')

sys.path.insert(0, OUT_DIR)
from build_html import (
    clean_lines, join_sentences, _is_heading, format_deep_dive,
    build_quiz_html, COMMON_JS, COMMON_CSS, CH_COLORS, CHAPTER_TITLES,
    NOISE_RE, CALLOUT_MARKER,
)

C = CH_COLORS[5]  # {'accent':'#a01850','dark':'#701035','light':'#ffe0ec','mid':'#cc4878'}

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

/* ── 変化比較（道具→同僚） ─────────────── */
.vs-compare {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin:10px 0; }}
.vs-col {{ border-radius:10px; padding:12px 13px; }}
.vs-head {{ font-size:12.5px; font-weight:700; margin-bottom:8px; text-align:center; padding-bottom:6px; border-bottom:2px solid rgba(255,255,255,.4); }}
.vs-list {{ list-style:none; padding:0; display:flex; flex-direction:column; gap:5px; }}
.vs-list li {{ font-size:11.5px; color:#333; padding-left:12px; position:relative; line-height:1.45; }}
.vs-list li::before {{ content:'·'; position:absolute; left:0; font-weight:900; font-size:14px; }}

/* ── デリゲーション3段階 ─────────────────── */
.deleg-table {{ width:100%; border-collapse:collapse; margin:10px 0; font-size:12px; }}
.deleg-table th {{
  padding:7px 10px; color:white; font-size:12px; font-weight:700; text-align:center;
  background:{C['dark']};
}}
.deleg-table td {{ padding:8px 10px; border-bottom:1px solid #eee; vertical-align:top; line-height:1.55; }}
.deleg-table tr:nth-child(even) td {{ background:#fff5f8; }}
.deleg-table td:first-child {{ font-weight:700; text-align:center; font-size:12px; }}
.risk-low  {{ color:#2a7a3a; }}
.risk-mid  {{ color:#c45a0a; }}
.risk-high {{ color:{C['dark']}; }}

/* ── 組織類型カード ─────────────────────── */
.org-cards {{ display:flex; flex-direction:column; gap:8px; margin:10px 0; }}
.org-card {{ border-radius:10px; border-left:5px solid; padding:10px 14px; }}
.org-card-head {{ display:flex; align-items:center; gap:8px; margin-bottom:5px; }}
.org-icon {{ font-size:18px; }}
.org-name {{ font-size:13px; font-weight:700; }}
.org-type {{ font-size:11px; color:#888; margin-left:auto; }}
.org-strong {{ font-size:12px; font-weight:600; color:#333; margin-bottom:3px; }}
.org-weak   {{ font-size:12px; color:#666; }}

/* ── 指標体系 ───────────────────────────── */
.metric-frame {{ display:flex; flex-direction:column; gap:6px; margin:10px 0; }}
.metric-row {{ border-radius:9px; padding:10px 14px; border-left:4px solid; }}
.metric-head {{ font-size:13px; font-weight:700; margin-bottom:3px; }}
.metric-body {{ font-size:12px; color:#333; line-height:1.5; }}
.metric-ex   {{ font-size:11.5px; color:{C['accent']}; margin-top:3px; font-style:italic; }}

/* ── 抵抗3段階 ──────────────────────────── */
.resist-stages {{ display:flex; flex-direction:column; gap:6px; margin:10px 0; }}
.resist-stage {{ border-radius:10px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.resist-stage-head {{ padding:9px 14px; font-weight:700; font-size:13px; display:flex; justify-content:space-between; align-items:center; }}
.resist-stage-tag  {{ font-size:10.5px; opacity:.8; background:rgba(255,255,255,.3); border-radius:4px; padding:1px 6px; }}
.resist-stage-body {{ padding:9px 14px; font-size:12.5px; line-height:1.6; color:#333; background:#f9fafb; border-top:1px solid rgba(0,0,0,.06); }}
.resist-stage-body strong {{ color:{C['dark']}; }}
.resist-arrow {{ text-align:center; font-size:18px; color:#bbb; line-height:1.2; }}

/* ── 5問答カード ────────────────────────── */
.qa-cards {{ display:flex; flex-direction:column; gap:8px; margin:10px 0; }}
.qa-card {{ border-radius:10px; border:1.5px solid {C['light']}; overflow:hidden; }}
.qa-q {{ padding:9px 14px; background:{C['light']}; font-size:12.5px; font-weight:700; color:{C['dark']}; }}
.qa-a {{ padding:9px 14px; font-size:12px; line-height:1.6; color:#333; }}
.qa-a strong {{ color:{C['dark']}; }}
.qa-key {{ font-size:11.5px; color:{C['accent']}; margin-top:4px; font-weight:600; border-top:1px solid {C['light']}; padding-top:5px; }}
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


# ─── S01: AIエージェント導入と組織文化の変革 ─────────────────────────────────
def ov_s01(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">AIの位置づけの変化：道具 → 同僚</div>
<div class="vs-compare">
  <div class="vs-col" style="background:#f0f0f0;">
    <div class="vs-head" style="color:#444;border-bottom-color:rgba(0,0,0,.2);">従来のITツール<br>（Excel・RPA等）</div>
    <ul class="vs-list">
      <li>人間が操作方法を覚える</li>
      <li>指示した通りにだけ動く</li>
      <li>判断しない・文脈を読まない</li>
      <li>責任は操作者にある</li>
      <li>導入＝操作習得</li>
    </ul>
  </div>
  <div class="vs-col" style="background:{C['light']};">
    <div class="vs-head" style="color:{C['dark']};border-bottom-color:rgba(112,16,53,.3);">AIエージェント<br>（同僚に近い存在）</div>
    <ul class="vs-list">
      <li>文脈を解釈・自ら判断</li>
      <li>状況に応じて異なる行動を選択</li>
      <li>「どこまで任せるか」を設計</li>
      <li>責任分界点の再定義が必要</li>
      <li>導入＝役割と権限の再設計</li>
    </ul>
  </div>
</div>

<div class="ov-subtitle">デリゲーション（権限委譲）の3段階設計</div>
<table class="deleg-table">
  <tr><th>リスクレベル</th><th>デリゲーション範囲</th><th>設計パターン</th></tr>
  <tr>
    <td class="risk-low">低リスク</td>
    <td>判断＋実行の両方をAIに委譲</td>
    <td>完全自動化（Full Automation）</td>
  </tr>
  <tr>
    <td class="risk-mid">中リスク</td>
    <td>AIが判断案を出し、人間が実行前に承認</td>
    <td>Human-in-the-Loop（HITL）</td>
  </tr>
  <tr>
    <td class="risk-high">高リスク</td>
    <td>AIは情報提供のみ。判断・実行は人間</td>
    <td>Human-in-Command</td>
  </tr>
</table>

<ul class="point-list">
  <li><strong>HITL（Human-in-the-Loop）</strong>：AIエージェントの処理の中に人間の確認・承認ステップを組み込む設計。安全装置＋AIを育てるフィードバック収集機構</li>
  <li>同じ「メール送信」でも社内連絡（低リスク）と契約変更通知（高リスク）では全く異なる設計が必要。<strong>文脈依存性</strong>を見落とさない</li>
</ul>

{mk_memory_key('AIは「道具」でなく「同僚」。導入＝権限設計。リスク別に低→HITL→人間判断の3段階でデリゲーションを設計する')}
"""


# ─── S02: AIエージェント推進の組織類型 ──────────────────────────────────────
def ov_s02(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">3つの推進体制類型</div>
<div class="org-cards">
  <div class="org-card" style="border-color:{C['dark']};background:#fff5f8;">
    <div class="org-card-head">
      <div class="org-icon">🏛</div>
      <div class="org-name">中央集権型（CoE主導）</div>
      <div class="org-type">統制重視</div>
    </div>
    <div class="org-strong">強み：ガバナンス統一・ナレッジ集約・野良エージェント防止・標準化</div>
    <div class="org-weak">弱み：CoEがボトルネックに。現場スピードに追いつけず、現場の当事者意識が薄れる</div>
    <div class="org-weak" style="margin-top:4px;color:{C['dark']};">向く組織：金融・医療等コンプライアンス重視の大企業</div>
  </div>
  <div class="org-card" style="border-color:{C['accent']};background:#fff8fa;">
    <div class="org-card-head">
      <div class="org-icon">🌐</div>
      <div class="org-name">分散型（各部署自律）</div>
      <div class="org-type">俊敏性重視</div>
    </div>
    <div class="org-strong">強み：現場ニーズへの即応・当事者意識・部署特性への最適化が速い</div>
    <div class="org-weak">弱み：ツール乱立・野良エージェント多発・車輪の再発明・セキュリティリスク</div>
    <div class="org-weak" style="margin-top:4px;color:{C['dark']};">向く組織：創業3〜5年SaaS・急成長スタートアップ</div>
  </div>
  <div class="org-card" style="border-color:{C['mid']};background:#fff5f8;">
    <div class="org-card-head">
      <div class="org-icon">⚖</div>
      <div class="org-name">ハイブリッド型（両立）</div>
      <div class="org-type">バランス型</div>
    </div>
    <div class="org-strong">中央（CoE）がルール・基準・共通基盤を整備し、各部署はその枠内で自律的に展開</div>
    <div class="org-weak">設計の核心：枠組みの厳格度のバランス。「全承認必須」なら実質中央集権型に</div>
    <div class="org-weak" style="margin-top:4px;color:{C['dark']};">見分け方：「部署の実質的な裁量が確保されているか」で判断</div>
  </div>
</div>

<div class="ov-subtitle">中央集権型 ⇔ 分散型の逆転関係</div>
<ul class="point-list">
  <li>中央集権型の強み＝分散型の弱み（統制・ナレッジ集約）。分散型の強み＝中央集権型の弱み（速さ・当事者意識）</li>
  <li><strong>CoE（Center of Excellence）</strong>の3機能：ガバナンス（ポリシー策定）・技術支援（設計レビュー）・ナレッジ共有（成功/失敗事例の全社展開）</li>
</ul>

{mk_memory_key('3類型：中央（CoE統制・遅いが安全）・分散（速いが管理不能）・ハイブリッド（枠内自律）。逆転関係を即対応できるように')}
"""


# ─── S03: 人材評価と指標の再設計 ────────────────────────────────────────────
def ov_s03(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">アウトカム指標 vs アウトプット指標</div>
<div class="metric-frame">
  <div class="metric-row" style="border-color:#e74c3c;background:#fff5f5;">
    <div class="metric-head" style="color:#c0392b;">アウトプット指標（活動量）— 補助的に使う</div>
    <div class="metric-body">DAU/MAU・処理件数など「使われているか」を示す指標。形骸化を見逃しやすい。高くても成果とは限らない</div>
    <div class="metric-ex">例：「毎日100人がAIエージェントを使っている」→ 成果に結びつかない使い方が横行する危険</div>
  </div>
  <div class="metric-row" style="border-color:{C['dark']};background:{C['light']};">
    <div class="metric-head" style="color:{C['dark']};">アウトカム指標（価値）— 主軸に置く</div>
    <div class="metric-body">AIがもたらした「実際の価値」を測る指標。創出された時間・解決された課題数・従業員満足度</div>
    <div class="metric-ex">例：「担当者の定型業務時間が月20時間→10時間に削減」「仕訳ミス率5%→1%以下」</div>
  </div>
</div>

<div class="ov-subtitle">KGI・KPI・OKRの体系</div>
<div class="metric-frame">
  <div class="metric-row" style="border-color:{C['dark']};background:#fff5f8;">
    <div class="metric-head">KGI（最終ゴール指標）</div>
    <div class="metric-body">プロジェクト最終目標の達成度。数値＋期限で定義。<br>例：「顧客対応コストを年間30%削減」</div>
  </div>
  <div class="metric-row" style="border-color:{C['accent']};background:#fff8fa;">
    <div class="metric-head">KPI（中間指標）</div>
    <div class="metric-body">KGI達成に向けたマイルストーン。3〜5個選ぶ。アウトカム指標を最低2個含める。<br>例：「AI正答率90%以上」「対応時間50%短縮」</div>
  </div>
  <div class="metric-row" style="border-color:{C['mid']};background:#fff5f8;">
    <div class="metric-head">OKR（目標と主要結果）</div>
    <div class="metric-body">定性的なObjective（ありたい姿）＋定量的KR（測定基準）。探索的・挑戦的目標に最適。<br>初期フェーズ（PoC）に向く</div>
  </div>
</div>

<ul class="point-list">
  <li><strong>フェーズ別使い分け</strong>：Discovery〜PoCはOKR（方向性探索）、Deployment以降はKGI/KPI（数値管理）</li>
  <li>KGIかKPIかは文脈で変わる。QA部門にとっての正答率95%はKGI、全社から見ればKPI</li>
</ul>

{mk_memory_key('アウトカム指標（価値）を主軸に。KGI→KPI→OKR。探索期はOKR、展開期はKPI。DAU/MAUだけ追うと形骸化する')}
"""


# ─── S04: チェンジマネジメント ───────────────────────────────────────────────
def ov_s04(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">変革に対する心理的抵抗の3段階</div>
<div class="resist-stages">
  <div class="resist-stage">
    <div class="resist-stage-head" style="background:#e0e0e0;color:#444;">
      第1段階：否認
      <span class="resist-stage-tag">変革の必要性を認めない</span>
    </div>
    <div class="resist-stage-body">「自分たちの業務にAIは関係ない」「今のやり方で十分」。悪意でなく<strong>自然な防衛反応</strong>。<br>対応：なぜ変革が必要かを数値・事例で具体的に示す（認知形成）</div>
  </div>
  <div class="resist-arrow">↓</div>
  <div class="resist-stage">
    <div class="resist-stage-head" style="background:{C['light']};color:{C['dark']};">
      第2段階：抵抗
      <span class="resist-stage-tag">感情的に受け入れられない</span>
    </div>
    <div class="resist-stage-body">「仕事を奪われる」「スキルが無意味になる」という不安・怒り。論理では解決しない。<br><strong>対応：変化の先に自分の役割が残ることを具体的に示す。恐怖で動かさない</strong></div>
  </div>
  <div class="resist-arrow">↓</div>
  <div class="resist-stage">
    <div class="resist-stage-head" style="background:#ffe0ec;color:{C['dark']};">
      第3段階：受容
      <span class="resist-stage-tag">試み始める</span>
    </div>
    <div class="resist-stage-body">「意外と便利だ」という前向きな反応が出る段階。<strong>クイックウィン（小さな成功体験）を積み重ねる</strong>ことで定着を促進</div>
  </div>
</div>

<div class="ov-subtitle">抵抗曲線と「谷」の意味</div>
<ul class="point-list">
  <li><strong>抵抗曲線</strong>：変革導入直後に生産性・モチベーションが一時的に低下（谷）し、その後回復・向上するU字型の推移</li>
  <li>谷は異常ではなく<strong>変革に伴う通常の反応</strong>。谷だけを見て「失敗」と判断しない</li>
  <li>重要：谷を「避けること」より、谷が来ることを前提に<strong>浅く・短くする施策</strong>（研修・相談体制・段階的導入）を事前設計</li>
  <li><strong>心理的安全性</strong>：「失敗を報告しても・意見を言っても罰せられない」という組織文化。チェンジマネジメントの土台</li>
</ul>

{mk_memory_key('変革の心理：否認→抵抗（最難関）→受容。谷はU字で正常。恐怖でなく役割の見通しで動かせ')}
"""


# ─── S05: AIエージェント推進者が現場で直面する5つの問いと答え方 ─────────────
def ov_s05(sec):
    ef = sec.get('exam_focus', '').strip()
    return f"""{mk_exam_point(ef)}

<div class="ov-divider"></div>
<div class="ov-subtitle">現場で直面する5つの問いと答え方の核心</div>
<div class="qa-cards">
  <div class="qa-card">
    <div class="qa-q">Q1：「AIエージェントは間違えるのではないか」</div>
    <div class="qa-a">
      <strong>NG</strong>：「間違えません」（断言）。<br>
      <strong>OK</strong>：比較対象を「完璧」でなく「現状の人間のミス率」にする。<br>
      「現状の仕訳ミス率は5%。AIは1%未満に抑え、最終確認を人間が行えば現状より安全」
      <div class="qa-key">核心：間違え方を設計する。低リスク業務から導入・HITL・ミス率の定量測定の3点セット</div>
    </div>
  </div>
  <div class="qa-card">
    <div class="qa-q">Q2：「デモはうまく動いたが本番も同じか」</div>
    <div class="qa-a">
      <strong>NG</strong>：「同じです」（断言）<br>
      <strong>OK</strong>：デモと本番の差を正直に伝え、PoCで検証する。期間と件数を具体的に示す<br>
      「まず50件で2週間検証し、精度を測定してから判断しましょう」
      <div class="qa-key">核心：PoCは「成功しなければならない工程」でなく「本番前に有効性を確認する工程」と経営層に事前理解を得る</div>
    </div>
  </div>
  <div class="qa-card">
    <div class="qa-q">Q3：「自社データを入れても問題ないか」</div>
    <div class="qa-a">
      <strong>OK</strong>：「何のデータを・どこに・どう渡すかを設計で制御できる」と説明<br>
      ①個人情報はマスキング②オンプレ or クラウドAPIを選べる③学習利用は契約で制御
      <div class="qa-key">核心：「何を渡し何を渡さないか」を具体的に示し、IT部門と一緒に確認すると持ちかける</div>
    </div>
  </div>
  <div class="qa-card">
    <div class="qa-q">Q4：「投資対効果（ROI）は見込めるか」</div>
    <div class="qa-a">
      <strong>NG</strong>：「必ず出ます」or「やってみないと分かりません」<br>
      <strong>OK</strong>：前提条件付きでROIを試算し、PoCでその前提を検証する形で提示<br>
      「定型請求書の70%をAI処理できれば年間420万円削減。この前提をPoC50件で検証、費用50万円・1ヶ月」
      <div class="qa-key">核心：ROIの成立条件と検証方法をセットで提示。いきなり大きな予算を求めない</div>
    </div>
  </div>
  <div class="qa-card">
    <div class="qa-q">Q5：「責任は誰が負うのか」</div>
    <div class="qa-a">
      <strong>NG</strong>：「最終的にはすべて人の責任です」（これだけ伝えると現場の抵抗が強まる）<br>
      <strong>OK</strong>：責任を役割ごとに分けて整理し、Human-in-the-Loopで設計する<br>
      ・設計者の責任：ルール・判断基準の誤り<br>
      ・承認者の責任：確認すべき内容の見逃し<br>
      ・経営の責任：導入判断と許容リスクの設定<br>
      <div class="qa-key">核心：AIエージェントに法的責任主体の地位はない。役割ごとの責任分担を明確化することで現場の不安を解消する</div>
    </div>
  </div>
</div>

{mk_memory_key('5つの問い：①間違え方を設計②PoC検証を提案③データ設計で制御④前提条件付きROI⑤責任構造を役割ごとに設計')}
"""


# ────────────────────────────────────────────────────────────────────────────
OV_BUILDERS = {
    'ch05_s01': ov_s01,
    'ch05_s02': ov_s02,
    'ch05_s03': ov_s03,
    'ch05_s04': ov_s04,
    'ch05_s05': ov_s05,
}


def build_ch05_section(sec, all_sections):
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

    ch05_secs = [s for s in all_sections if s['ch'] == 5]

    body_parts = [build_ch05_section(sec, all_sections) for sec in ch05_secs]

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>Ch.05 | 人と組織から考えるAI時代の組織設計</title>
  <style>{FULL_CSS}</style>
</head>
<body>
{''.join(body_parts)}
<script>{COMMON_JS}</script>
</body>
</html>'''

    out_path = os.path.join(OUT_DIR, 'ch05.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Written: ch05.html ({len(html):,} chars, {len(ch05_secs)} sections)')


if __name__ == '__main__':
    main()
