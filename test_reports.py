# test_report.py
import json
from reports import get_report_data
print(json.dumps(get_report_data(), indent=2))