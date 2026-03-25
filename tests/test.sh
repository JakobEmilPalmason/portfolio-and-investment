#!/bin/bash
python3 -c "
import json, os, subprocess, glob

week = subprocess.check_output(['grep', '-m1', 'CURRENT_WEEK=', 'run.sh']).decode().split('\"')[1]
d = f'runs/{week}/reports/ODFL'
checks = []

def check(name, passed, msg):
    checks.append({'name': name, 'passed': passed, 'message': msg})

# 1. Sections 01-08 exist
for i in ['01','02','03','04','05','06','07','08']:
    files = glob.glob(f'{d}/{i}-*.md')
    check(f'section-{i}', len(files)>0, f'Section {i} exists' if files else f'Section {i} missing')

# 2. Section 09
check('checklist', os.path.isfile(f'{d}/09-compact-checklist.md'), '09 exists' if os.path.isfile(f'{d}/09-compact-checklist.md') else '09 missing')

# 3. FINAL-REPORT.md
check('final-md', os.path.isfile(f'{d}/FINAL-REPORT.md'), 'FINAL-REPORT.md exists' if os.path.isfile(f'{d}/FINAL-REPORT.md') else 'missing')

# 4-7. FINAL-REPORT.json checks
try:
    rpt = json.load(open(f'{d}/FINAL-REPORT.json'))
    check('json-valid', True, 'Valid JSON')
    check('ticker', rpt.get('ticker')=='ODFL', f\"Ticker is {rpt.get('ticker')}\")
    v = rpt.get('verdict','')
    check('verdict', v in ['Own','Watch','Pass'], f'Verdict is {v}')
    s = rpt.get('umbrella_scores',{})
    keys = ['circle_of_competence','competitive_advantage','management','business_economics','balance_sheet','valuation','margin_of_safety','temperament']
    sok = all(isinstance(s.get(k),int) and 1<=s[k]<=10 for k in keys) and len(s)>=8
    check('scores', sok, '8 scores valid' if sok else 'Scores invalid')
    cl = rpt.get('compact_checklist',[])
    check('checklist-8', isinstance(cl,list) and len(cl)==8, f'{len(cl)} checklist items')
    c = rpt.get('confidence','')
    check('confidence', c in ['high','medium','low'], f'Confidence: {c}')
except Exception as e:
    check('json-valid', False, str(e))

# 8. Queue updated
try:
    q = json.load(open('queue/queue.json'))
    entry = [e for e in q if e.get('ticker')=='ODFL']
    check('queue', bool(entry and entry[0].get('last_analysis_date')), 'Queue updated' if entry else 'Not in queue')
except:
    check('queue', False, 'queue.json error')

passed = sum(1 for c in checks if c['passed'])
total = len(checks)
score = round(passed/total, 2) if total else 0
print(json.dumps({'score': score, 'details': f'{passed}/{total} checks passed', 'checks': checks}))
"
