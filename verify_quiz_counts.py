"""
sections_data.json の quizzes が、PDF内の「問N」出現数と一致し、
かつセクション内で重複した question が無いことを検証する。
"""
import fitz, sys, os, re, json, hashlib

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
    out = ''
    for pg in range(pg_start_0idx, pg_end_0idx + 1):
        for l in doc[pg].get_text('text').split('\n'):
            s = l.strip()
            if not s or NOISE.search(s):
                continue
            out += clean(s) + '\n'
    return out


def normalize_hash(question):
    key = re.sub(r'\s+', '', question)
    return hashlib.sha256(key.encode('utf-8')).hexdigest()


def main():
    with open(JSON_PATH, encoding='utf-8') as f:
        data = json.load(f)
    data_sorted = sorted(data, key=lambda s: (s['ch'], s['s']))

    q_marker_re = re.compile(r'^問\d*\s*$', re.MULTILINE)

    all_ok = True
    print(f'{"sid":12s} {"pdf_q_count":>11s} {"json_count":>10s} {"dup_in_json":>11s}  status')
    for i, sec in enumerate(data_sorted):
        sid = f"ch{sec['ch']:02d}_s{sec['s']:02d}"
        pg_start = sec['page_start'] - 1
        pg_end = (data_sorted[i + 1]['page_start'] - 2) if i + 1 < len(data_sorted) else doc.page_count - 1
        pg_end = max(pg_end, pg_start)

        text = get_text(pg_start, pg_end)
        pos = text.find('理解度チェック')
        block = text[pos:] if pos != -1 else ''
        pdf_q_count = len(q_marker_re.findall(block))

        json_count = len(sec['quizzes'])

        hashes = [normalize_hash(q['question']) for q in sec['quizzes']]
        dup_count = len(hashes) - len(set(hashes))

        status = 'PASS' if (pdf_q_count == json_count and dup_count == 0) else 'FAIL'
        if status == 'FAIL':
            all_ok = False
        print(f'{sid:12s} {pdf_q_count:>11d} {json_count:>10d} {dup_count:>11d}  {status}')

    print()
    print('ALL PASS' if all_ok else 'SOME FAILURES ABOVE')
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
