"""
sections_data.json の97問に、模擬試験と同じ6類型のq_typeを付与する。
sections_data.json 本体は変更せず、{sid}_{idx} -> q_type のマッピングを
sections_quiz_qtype.json として出力する（③問題集の既存挙動には無影響）。
"""
import json, sys

sys.stdout.reconfigure(encoding='utf-8')

DEF = '定義・構成要素の理解'
SCENARIO = '業務シナリオ適用判断'
PREMISE = '前提整理'
WORKFLOW = 'ワークフロー設計妥当性'
ORG = '組織導入・チェンジマネジメント判断'
FIVE_D = '5Dモデル進め方判断'

# sections_data.json の並び順（ch,s昇順、各セクション内はidx昇順）と1:1対応
QTYPES = (
    # ch01_s01 (3)
    [DEF, SCENARIO, SCENARIO] +
    # ch01_s02 (3)
    [SCENARIO, SCENARIO, SCENARIO] +
    # ch01_s03 (3)
    [SCENARIO, SCENARIO, SCENARIO] +
    # ch01_s04 (3)
    [DEF, SCENARIO, SCENARIO] +
    # ch01_s05 (3)
    [SCENARIO, PREMISE, DEF] +
    # ch01_s06 (3)
    [DEF, ORG, DEF] +
    # ch01_s07 (3)
    [DEF, SCENARIO, SCENARIO] +
    # ch01_s08 (3)
    [SCENARIO, SCENARIO, DEF] +
    # ch02_s01 (3)
    [PREMISE, PREMISE, PREMISE] +
    # ch02_s02 (3)
    [PREMISE, PREMISE, PREMISE] +
    # ch02_s03 (3)
    [PREMISE, PREMISE, PREMISE] +
    # ch03_s01 (3)
    [SCENARIO, SCENARIO, SCENARIO] +
    # ch03_s02 (4)
    [DEF, SCENARIO, SCENARIO, SCENARIO] +
    # ch03_s03 (4)
    [DEF, SCENARIO, SCENARIO, DEF] +
    # ch03_s04 (3)
    [ORG, ORG, DEF] +
    # ch03_s05 (4)
    [SCENARIO, SCENARIO, DEF, SCENARIO] +
    # ch03_s06 (3)
    [PREMISE, SCENARIO, PREMISE] +
    # ch03_s07 (4)
    [PREMISE, SCENARIO, SCENARIO, PREMISE] +
    # ch04_s01 (3)
    [SCENARIO, SCENARIO, SCENARIO] +
    # ch04_s02 (3)
    [WORKFLOW, WORKFLOW, WORKFLOW] +
    # ch04_s03 (3)
    [WORKFLOW, WORKFLOW, WORKFLOW] +
    # ch04_s04 (4)
    [DEF, WORKFLOW, WORKFLOW, WORKFLOW] +
    # ch05_s01 (2)
    [ORG, ORG] +
    # ch05_s02 (1)
    [ORG] +
    # ch05_s03 (3)
    [ORG, ORG, ORG] +
    # ch05_s04 (3)
    [ORG, ORG, ORG] +
    # ch05_s05 (3)
    [ORG, ORG, ORG] +
    # ch06_s01 (3)
    [FIVE_D, FIVE_D, FIVE_D] +
    # ch06_s02 (3)
    [FIVE_D, FIVE_D, FIVE_D] +
    # ch06_s03 (3)
    [FIVE_D, FIVE_D, FIVE_D] +
    # ch06_s04 (3)
    [FIVE_D, FIVE_D, FIVE_D] +
    # ch06_s05 (2)
    [FIVE_D, FIVE_D]
)


def main():
    with open('sections_data.json', encoding='utf-8') as f:
        data = json.load(f)
    data_sorted = sorted(data, key=lambda s: (s['ch'], s['s']))

    mapping = {}
    i = 0
    mismatch = []
    for sec in data_sorted:
        sid = f"ch{sec['ch']:02d}_s{sec['s']:02d}"
        for idx in range(len(sec['quizzes'])):
            if i >= len(QTYPES):
                mismatch.append(f'{sid}_{idx}: QTYPES exhausted')
                continue
            mapping[f'{sid}_{idx}'] = QTYPES[i]
            i += 1

    if i != len(QTYPES):
        print(f'WARNING: count mismatch. consumed={i}, QTYPES len={len(QTYPES)}')
    else:
        print(f'OK: {i} questions classified, matches QTYPES length exactly')

    valid_types = {DEF, SCENARIO, PREMISE, WORKFLOW, ORG, FIVE_D}
    bad = [k for k, v in mapping.items() if v not in valid_types]
    if bad:
        print('INVALID TYPES:', bad)
    else:
        print(f'All {len(mapping)} entries have a valid q_type (6 categories)')

    from collections import Counter
    dist = Counter(mapping.values())
    for t, c in dist.items():
        print(f'  {t}: {c}')

    with open('sections_quiz_qtype.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(f'Written: sections_quiz_qtype.json ({len(mapping)} entries)')


if __name__ == '__main__':
    main()
