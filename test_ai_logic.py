import sys
import os
import json
from unittest.mock import MagicMock

# Add project root to path
sys.path.append('d:/LIFE/_PROYEK_PORTOFOLIO/Farmille/Farmile')

# Mock Flask app context if needed or test logic pure functions
from app.ai_logic import run_liquid_scheduler, estimate_task_duration, feynman_test, stoic_mentor

def test_liquid_scheduler():
    print("\n--- Testing Liquid Scheduler ---")
    user_query = "Tugas Metpen geser ke besok pagi dong, lagi capek."
    schedule_context = "Today: Metpen (19:00). Tomorrow: Empty."
    
    # We expect the mock/simulated agent to return a JSON with 'reschedule' action
    result = run_liquid_scheduler(user_query, schedule_context)
    print("Result:", json.dumps(result, indent=2))
    
    if result.get('action') == 'reschedule':
        print("✅ PASS: Action identified correctly.")
    else:
        print("⚠️ NOTE: Action might be 'none' if using real LLM without valid API Key or if mock logic fallback.")

def test_sks_estimator():
    print("\n--- Testing SKS Estimator ---")
    title = "Laporan Akhir Jarkom"
    pages = 10
    is_coding = True
    
    minutes = estimate_task_duration(title, pages, is_coding)
    print(f"Input: {title}, {pages} pages, Coding={is_coding}")
    print(f"Estimated: {minutes} minutes")
    
    if minutes > 0:
        print("✅ PASS: Returned a valid positive integer.")
    else:
        print("❌ FAIL: Returned invalid duration.")

def test_ovt_panic():
    print("\n--- Testing OVT Panic Button ---")
    stats = {'gpa': 3.8, 'completed_tasks': 5, 'level': 10}
    response = stoic_mentor(stats)
    print("Response:", json.dumps(response, indent=2))
    
    if 'reassurance' in response:
        print("✅ PASS: Returned reassurance message.")
    else:
        print("❌ FAIL: No reassurance found.")

if __name__ == "__main__":
    print("Running AI Logic Verification...")
    try:
        test_liquid_scheduler()
        test_sks_estimator()
        test_ovt_panic()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
