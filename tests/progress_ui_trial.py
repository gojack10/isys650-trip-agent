"""Synthetic public-progress UI check; no paid/model request.
TRIP_TEST_URL=http://127.0.0.1:18082/ browser-harness < tests/progress_ui_trial.py
"""
import os
import time


def until(expression, expected, seconds=20):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        observed = js(expression)
        if observed == expected:
            return
        time.sleep(0.5)
    raise AssertionError(f'{expression}: expected {expected!r}, got {observed!r}')


url = os.environ['TRIP_TEST_URL']
if any(tab.get('url') == url for tab in list_tabs()):
    raise RuntimeError('Identify the existing matching tab before testing')
new_tab(url)
try:
    wait_for_load()
    js("""(() => {
      window.testPoll = 0;
      window.testFailure = false;
      window.fetch = async (url, options) => {
        if (options?.method === 'POST') return new Response(JSON.stringify({job_id:'synthetic',status:'researching'}),{status:202});
        window.testPoll++;
        const progress={title: testPoll === 1 ? 'Checking hotel options' : 'Checking hotel options — some evidence is unavailable', next:'Building the budget', state:'working', elapsed_seconds:100+testPoll, quiet_seconds:50, activity:'tool', history:[{elapsed_seconds:60,title:'Checking hotel options'}]};
        if (testPoll < 3) return new Response(JSON.stringify({status:'researching',progress}),{status:202});
        if (testFailure) return new Response(JSON.stringify({error:'Research reached its time limit. Try a narrower request.',progress}),{status:502});
        return new Response(JSON.stringify({question:'Which airport?',progress}),{status:200});
      };
      setChat(true);
      submitChat('Test progress, no network request');
    })()""")
    wait(3)
    assert js("document.querySelector('.progress-title').textContent") == 'Checking hotel options'
    assert 'No new activity' in js("document.querySelector('.progress-meta').textContent")
    assert js("document.querySelector('.progress-card details').open") is False
    assert js("document.querySelector('.progress-card').getAttribute('aria-live')") == 'off'
    assert js("document.querySelector('.chat-send').disabled") is True
    until("document.querySelector('.progress-title').textContent", 'One detail needed')
    assert js("document.querySelector('.chat-send').disabled") is False
    elapsed = js("document.querySelector('.progress-meta').textContent")
    wait(1)
    assert js("document.querySelector('.progress-meta').textContent") == elapsed
    js("testPoll=0; testFailure=true; void submitChat('Test timeout, no network request')")
    until("[...document.querySelectorAll('.progress-title')].at(-1).textContent", 'No result received')
    assert 'time limit' in js("document.getElementById('chatMessages').textContent")
    assert js("document.querySelector('.chat-send').disabled") is False
    assert js("[...document.querySelectorAll('.progress-card')].at(-1).querySelectorAll('li').length") == 1
    print('PASS: live status before completion, honest silence, collapsed history, stopped clock and timeout UI')
finally:
    close_tab()
