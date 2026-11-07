"""Deterministic author-owned Boolean domain benchmark: NO LLM inference."""
from pathlib import Path
import json
from tasks import TASKS
from transfer import offline_report

def main(path=None):
    data=offline_report(TASKS)
    if path is None:path=Path(__file__).with_name('offline-results.json')
    Path(path).write_text(json.dumps(data,ensure_ascii=True,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return data

if __name__=='__main__':
    a=main()
    for row in a['results']:
        print(f"{row['task']:30} old={row['old']['status']:35} expanded={row['expanded']['status']}")
