"""
reader/ch1.html〜ch6.html:
  1. 旧フローティングポップアップ（float-nav-wrap等）を除去
     （reader既存の左上ハンバーガー(#menu-btn)がドロワーを開ける機能を既に持つため不要）
  2. ドロワー内の「戻る」リンクを、全章・全セクションのツリー（①②③への直接リンク付き）に置き換える
"""
import json, os, sys
sys.path.insert(0, r'C:\Users\mikli\Downloads\AICX学習')
from common_ui import build_toc_tree_html

READER_DIR = r"C:\Users\mikli\Downloads\AICX学習\reader"
JSON_PATH = r"C:\Users\mikli\Downloads\AICX学習\sections_data.json"

CHAPTER_TITLES = {
    1: "生成AIとAIエージェントの基礎",
    2: "業務の基礎",
    3: "AIデータリテラシーとマネジメント",
    4: "自動化レベルとワークフロー設計",
    5: "人と組織から考えるAI時代の組織設計",
    6: "AIエージェントを実装する5Dモデル",
}
CH_COLORS = {
    1: {'accent': '#2d6a9f'}, 2: {'accent': '#6b4fa8'}, 3: {'accent': '#2a8a7a'},
    4: {'accent': '#c45a0a'}, 5: {'accent': '#a01850'}, 6: {'accent': '#2a6e3a'},
}

OLD_BACKLINKS = '''    <a href="./index.html" style="display:block;color:var(--text2);font-size:13px;text-decoration:none;padding:7px 0;border-bottom:1px solid var(--border);">← 精読ビューア 目次へ</a>
    <a href="../index.html" style="display:block;color:var(--text2);font-size:13px;text-decoration:none;padding:7px 0 0;">← 問題集に戻る</a>'''

TOC_TREE_CSS = """<style>
.toc-full-ch { border-bottom: 1px solid var(--border); }
.toc-full-ch-btn {
  display: flex; align-items: center; justify-content: space-between;
  width: 100%; padding: 11px 14px; background: none; border: none;
  color: var(--text); font-size: 13px; font-weight: 700; cursor: pointer; text-align: left;
}
.toc-full-ch-btn:active { background: var(--surface2); }
.toc-full-ch-arrow { font-size: 11px; color: var(--text3); transition: transform .2s; flex-shrink: 0; margin-left: 6px; }
.toc-full-ch-btn.open .toc-full-ch-arrow { transform: rotate(90deg); }
.toc-full-ch-list { display: none; padding: 2px 0 8px; }
.toc-full-ch-list.open { display: block; }
.toc-full-sec-row { display: flex; align-items: center; gap: 4px; padding: 0 8px 0 14px; }
.toc-full-sec-title {
  flex: 1; display: block; padding: 8px 6px 8px 12px; min-width: 0;
  color: var(--text2); font-size: 12.5px; text-decoration: none;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.toc-full-sec-title:active { color: var(--accent); }
.toc-full-sec-title.current { color: var(--accent); font-weight: 700; }
.toc-full-mini { flex-shrink: 0; padding: 6px; font-size: 13px; text-decoration: none; opacity: .6; border-radius: 6px; }
.toc-full-mini:active { opacity: 1; background: var(--surface2); }
.toc-full-label { font-size: 11px; color: var(--text3); padding: 10px 14px 2px; }
</style>"""


def load_sections():
    with open(JSON_PATH, encoding='utf-8') as f:
        return json.load(f)


def build_tree_for_reader(all_sections, ch_num):
    # build_toc_tree_htmlの生成クラス名(toc-ch等)はreader側CSSに無いため、
    # ここではreader専用のクラス名(toc-full-ch等)に置換して使い回す。
    current_sid = f'ch{ch_num:02d}_s01'
    html = build_toc_tree_html(all_sections, CHAPTER_TITLES, CH_COLORS, root_prefix='../', current_sid=current_sid)
    replacements = {
        'toc-ch-btn': 'toc-full-ch-btn',
        'toc-ch-arrow': 'toc-full-ch-arrow',
        'toc-ch-list': 'toc-full-ch-list',
        'toc-ch': 'toc-full-ch',
        'toc-sec-row': 'toc-full-sec-row',
        'toc-sec-title': 'toc-full-sec-title',
        'toc-mini': 'toc-full-mini',
        'toggleTocCh(this)': 'toggleTocFullCh(this)',
    }
    # 長いクラス名から置換（toc-ch-btnがtoc-chの部分置換で壊れないよう順序に注意）
    for old, new in sorted(replacements.items(), key=lambda kv: -len(kv[0])):
        html = html.replace(old, new)
    return html


def patch_file(path, ch_num, all_sections):
    with open(path, encoding='utf-8') as f:
        content = f.read()

    # 1. 旧フローティングポップアップを除去
    start_marker = '<style>\n.float-nav-wrap'
    end_marker = "})();\n</script>\n\n</body>"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    if start_idx != -1 and end_idx != -1:
        content = content[:start_idx] + '</body>' + content[end_idx + len(end_marker):]
        removed_float_nav = True
    else:
        removed_float_nav = False
        print(f'  WARNING: float-nav block markers not found in {path}')

    # 2. 戻るリンク→全章ツリーに置換
    if OLD_BACKLINKS in content:
        tree_html = build_tree_for_reader(all_sections, ch_num)
        toc_full_label = '<div class="toc-full-label">全章から探す</div>'
        content = content.replace(OLD_BACKLINKS, TOC_TREE_CSS + '\n' + toc_full_label + tree_html)
        replaced_tree = True
    else:
        replaced_tree = False
        print(f'  WARNING: back-links marker not found in {path}')

    # 3. toggleTocFullCh 関数を追加（menu-btn配線の直前に挿入）
    marker = "function closeDrawer() {"
    if marker in content and 'function toggleTocFullCh' not in content:
        addition = "function toggleTocFullCh(btn) {\n  btn.classList.toggle('open');\n  btn.nextElementSibling.classList.toggle('open');\n}\n\n" + marker
        content = content.replace(marker, addition, 1)
        added_fn = True
    else:
        added_fn = False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'{os.path.basename(path)}: float_nav_removed={removed_float_nav}, tree_added={replaced_tree}, fn_added={added_fn}')


def main():
    all_sections = load_sections()
    for n in range(1, 7):
        patch_file(os.path.join(READER_DIR, f'ch{n}.html'), n, all_sections)


if __name__ == '__main__':
    main()
