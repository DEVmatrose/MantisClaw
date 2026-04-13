import json

lines = open('WORKSPACE/WORKING/LOGS/prompt_log.jsonl', 'r', encoding='utf-8').readlines()
for i, l in enumerate(lines):
    e = json.loads(l)
    sys_len = len(e.get('system', ''))
    usr_len = len(e.get('user', ''))
    resp_len = len(e.get('response', ''))
    resp_lines = e.get('response', '').strip().split('\n')
    steps = [r for r in resp_lines if r.strip().startswith('STEP:')]
    goal = [r for r in resp_lines if r.strip().startswith('GOAL:')]
    reasoning = [r for r in resp_lines if r.strip().startswith('REASONING:')]
    print(f'--- Entry {i+1} | {e.get("ts","?")} ---')
    print(f'  Prompt size: system={sys_len}c, user={usr_len}c, response={resp_len}c')
    if goal:
        print(f'  GOAL: {goal[0].strip()[5:].strip()[:120]}')
    if reasoning:
        print(f'  REASONING: {reasoning[0].strip()[10:].strip()[:120]}')
    print(f'  STEPS ({len(steps)}):')
    for s in steps:
        print(f'    {s.strip()[:120]}')
    print()

print(f'Total: {len(lines)} entries')
