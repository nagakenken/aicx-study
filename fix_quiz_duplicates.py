"""
理解度チェック問題の重複バグ修正。

過去の抽出/マージ処理で、一部セクションの最後の問題が「1つ前の問題の完全コピー」
になってしまっている（本来の問題を1問失っている）。PDFの該当ページ範囲を
再抽出し、内容ハッシュで重複排除した上で、本来あるべき問題に差し替える。
"""
import fitz, sys, os, re, json, hashlib, shutil, datetime

sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = r"C:\Users\mikli\Downloads\AICX学習"
JSON_PATH = os.path.join(OUT_DIR, 'sections_data.json')

pdf_path = next(
    os.path.join(r'C:\Users\mikli\Downloads', f)
    for f in os.listdir(r'C:\Users\mikli\Downloads')
    if f.endswith('.pdf') and 'AI' in f
)
doc = fitz.open(pdf_path)

NOISE = re.compile(r'^nagaken|盩盨盪盫|AIエージェント・ストラテジスト資格$|^Chapter\d+.*$|^CHAPTER\s*(—|\d+)$')

PUA_MAP = {
    '': '0', '': '1', '': '2', '': '3', '': '4',
    '': '5', '': '6', '': '7', '': '8', '': '9',
}

def clean(text):
    for k, v in PUA_MAP.items():
        text = text.replace(k, v)
    return text

def get_text(pg_start_0idx, pg_end_0idx):
    """0-indexed inclusive page range."""
    out = ''
    for pg in range(pg_start_0idx, pg_end_0idx + 1):
        for l in doc[pg].get_text('text').split('\n'):
            s = l.strip()
            if not s or NOISE.search(s):
                continue
            out += clean(s) + '\n'
    return out


def parse_quiz_block(block_text):
    """理解度チェックブロックから問題群をパースする。"""
    quizzes = []
    q_re = re.compile(r'^問\d*\s*$', re.MULTILINE)
    q_starts = [m.start() for m in q_re.finditer(block_text)]
    if not q_starts:
        return quizzes

    for i, start in enumerate(q_starts):
        end = q_starts[i + 1] if i + 1 < len(q_starts) else len(block_text)
        chunk = block_text[start:end].strip()
        lines = [l.strip() for l in chunk.split('\n') if l.strip()]
        lines = lines[1:]  # drop "問N" marker line

        choice_indices = [j for j, l in enumerate(lines) if l in ('A', 'B', 'C', 'D')]
        if not choice_indices:
            continue

        question_stem = ' '.join(lines[:choice_indices[0]])

        choices = {}
        for k, ci in enumerate(choice_indices):
            letter = lines[ci]
            text_end = choice_indices[k + 1] if k + 1 < len(choice_indices) else len(lines)
            text_lines = []
            for l in lines[ci + 1:text_end]:
                if l == '正解':
                    break
                text_lines.append(l)
            choices[letter] = ' '.join(text_lines)

        answer = ''
        explanation = ''
        correct_idx = None
        for j, l in enumerate(lines):
            if l == '正解':
                correct_idx = j
                break

        if correct_idx is not None:
            expl_lines = lines[correct_idx + 1:]
            if expl_lines:
                first = expl_lines[0]
                m = re.match(r'正解[：:]\s*([A-D])', first)
                if m:
                    answer = m.group(1)
                explanation = ' '.join(expl_lines)

        if question_stem and choices and answer:
            quizzes.append({
                'question': question_stem,
                'choices': choices,
                'correct_letter': answer,
                'explanation': explanation,
                'answer': answer,
            })

    return quizzes


def truncate_explanation_leak(expl, next_section_markers=('CHAPTER', 'Section', 'Chapter')):
    """explanationにページ境界を跨いだ次セクション本文が混入している場合、
    そこで打ち切る。"""
    for marker in next_section_markers:
        idx = expl.find(marker)
        if idx > 20:  # 先頭近くでのマッチは誤検知の可能性が高いので除外
            return expl[:idx].strip()
    return expl


JP = r'[ぁ-ん゛゜ァ-ヶーｦ-ﾟ一-龥々〆〤。、・「」『』【】（）〜…！？：；〇]'
JP_SPACE_RE = re.compile(f'({JP}) ({JP})')

def fix_spaces(text):
    if not text:
        return text
    prev = None
    while prev != text:
        prev = text
        text = JP_SPACE_RE.sub(r'\1\2', text)
    return text


def fix_quiz_spaces(q):
    q['question'] = fix_spaces(q['question'])
    q['explanation'] = fix_spaces(q['explanation'])
    for letter in q['choices']:
        q['choices'][letter] = fix_spaces(q['choices'][letter])
    return q


def normalize_hash(question, choices):
    key = re.sub(r'\s+', '', question) + '|' + '|'.join(
        f'{k}:{re.sub(chr(92)+"s+", "", v)}' for k, v in sorted(choices.items())
    )
    return hashlib.sha256(key.encode('utf-8')).hexdigest()


AFFECTED_SIDS = {
    'ch01_s01', 'ch01_s02', 'ch01_s03', 'ch01_s05', 'ch01_s06', 'ch01_s07', 'ch01_s08',
    'ch02_s01', 'ch02_s02',
    'ch03_s01', 'ch03_s02', 'ch03_s03', 'ch03_s04', 'ch03_s05', 'ch03_s06',
    'ch04_s01', 'ch04_s03', 'ch04_s04',
    'ch05_s01', 'ch05_s03', 'ch05_s04', 'ch05_s05',
    'ch06_s01', 'ch06_s02', 'ch06_s03', 'ch06_s04', 'ch06_s05',
}


def main():
    with open(JSON_PATH, encoding='utf-8') as f:
        data = json.load(f)

    # backup
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = f'{JSON_PATH}.bak.{ts}'
    shutil.copy(JSON_PATH, bak)
    print(f'Backup saved: {bak}')

    data_sorted = sorted(data, key=lambda s: (s['ch'], s['s']))

    report = []
    for i, sec in enumerate(data_sorted):
        sid = f"ch{sec['ch']:02d}_s{sec['s']:02d}"
        if sid not in AFFECTED_SIDS:
            continue

        pg_start = sec['page_start'] - 1  # 0-indexed
        pg_end = (data_sorted[i + 1]['page_start'] - 2) if i + 1 < len(data_sorted) else doc.page_count - 1
        pg_end = max(pg_end, pg_start)

        text = get_text(pg_start, pg_end)
        pos = text.find('理解度チェック')
        if pos == -1:
            report.append((sid, 'NO_QUIZ_BLOCK_FOUND', 0, 0))
            continue
        block = text[pos:]
        extracted = parse_quiz_block(block)

        # dedup extracted by content hash, preserve order
        seen = set()
        uniq_extracted = []
        for q in extracted:
            h = normalize_hash(q['question'], q['choices'])
            if h in seen:
                continue
            seen.add(h)
            q['explanation'] = truncate_explanation_leak(q['explanation'])
            uniq_extracted.append(q)

        existing = sec['quizzes']
        existing_count = len(existing)

        # 既存の問題群のうち「PDFのuniq_extractedと内容一致するもの」を数え、
        # 一致しない・または同一extracted問題を2回以上主張している（=重複バグ）
        # ものを特定する
        existing_hashes = [normalize_hash(q['question'], q.get('choices', {})) for q in existing]
        extracted_hashes = [normalize_hash(q['question'], q['choices']) for q in uniq_extracted]

        used_extracted_idx = set()
        new_quizzes = []
        broken_positions = []
        for idx, (eq, eh) in enumerate(zip(existing, existing_hashes)):
            if eh in extracted_hashes:
                match_idx = extracted_hashes.index(eh)
                if match_idx not in used_extracted_idx:
                    used_extracted_idx.add(match_idx)
                    new_quizzes.append(eq)
                    continue
            # 一致するextractedが無い、またはそのextractedが既に別の既存問題に
            # 使われている（=このエントリは重複コピー） → 壊れているとみなす
            new_quizzes.append(None)
            broken_positions.append(idx)

        # 未使用のextracted問題を、壊れていた位置に順番に充填
        unused = [uniq_extracted[j] for j in range(len(uniq_extracted)) if j not in used_extracted_idx]
        for pos_idx, slot in enumerate(broken_positions):
            if pos_idx < len(unused):
                new_quizzes[slot] = fix_quiz_spaces(unused[pos_idx])
            else:
                new_quizzes[slot] = existing[slot]  # フォールバック: 置換候補がなければ既存のまま残す

        # Noneが残っていないか確認（あれば既存のまま）
        new_quizzes = [nq if nq is not None else existing[k] for k, nq in enumerate(new_quizzes)]

        sec['quizzes'] = new_quizzes
        report.append((sid, 'OK', existing_count, len(broken_positions)))

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"{'sid':12s} {'status':10s} {'count':>6s} {'fixed':>6s}")
    for sid, status, count, fixed in report:
        print(f'{sid:12s} {status:10s} {count:>6d} {fixed:>6d}')


if __name__ == '__main__':
    main()
