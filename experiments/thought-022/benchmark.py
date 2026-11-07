"""Offline reproducible result: classical syntax closure and task evaluation."""
from pathlib import Path
import json
from race import offline_matrix
if __name__=='__main__':
    report=offline_matrix()
    path=Path(__file__).with_name('offline-results.json')
    path.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'distinct_expressible_functions':report['grammar_distinct_functions'],
         'solved':report['solved'],'grammar_inadequate':report['grammar_inadequate'],
         'oracle_queries':report['total_oracle_calls'],'results_written':str(path)},indent=2))
