"""Run from repository root with Browser Harness, not Python directly:
TRIP_TEST_URL=http://127.0.0.1:18081/ browser-harness < tests/ui_trial.py

Synthetic fixture test of the actual UI only; never submits an agent/API job.
"""
import json
import os
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
fixture = runpy.run_path('tests/test_app.py')['itinerary']()
url = os.environ['TRIP_TEST_URL']
tabs = list_tabs()
if any(tab.get('url') == url for tab in tabs):
    raise RuntimeError('A matching tab is already open; identify its ownership before testing')
new_tab(url)
try:
    wait_for_load()
    js('activePlan = ' + json.dumps(fixture) + '; showPlan(activePlan)')
    assert js('document.querySelectorAll(".in-trip").length') == 3
    assert js('stayName.textContent') == 'Example Hotel'
    js('document.querySelector(".budget-trigger").click()')
    assert 'USD 230.00' in js('document.getElementById("modalText").textContent')
    js('closeModal(); document.getElementById("planDetails").click()')
    assert 'Assumptions' in js('document.getElementById("modalText").textContent')
    assert 'https://example.com/hotel' in js('document.getElementById("modalLinks").innerHTML')
    js("closeModal(); activePlan={...activePlan,status:'exploring',days:[],flights:[],lodging:[],budget:null}; showPlan(activePlan)")
    assert js('document.querySelectorAll(".in-trip").length') == 0
    assert js('document.querySelector(".detail-panel").hidden') is True
    print('PASS: synthetic dated/budget/evidence/exploration UI branches')
finally:
    close_tab()
