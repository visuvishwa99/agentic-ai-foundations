import requests
import json
import time
import uuid

API_URL = "http://127.0.0.1:8000"

def run_simulation(num_requests=5):
    print("[INFO] Starting API Client Simulation...")
    print(f"[INFO] Target: {API_URL}")
    
    # 1. Health Check
    try:
        health = requests.get(f"{API_URL}/health")
        print(f"[INFO] Health Status: {health.json()}")
    except Exception as e:
        print(f"[ERROR] API Connection Failed: {e}")
        return

    # 2. Burst Traffic
    queries = [
        "Show me total sales for 2024",
        "Who is the top customer?",
        "List all product categories",
        "Count active users",
        "Generate a revenue report"
    ]
    
    start_time = time.time()
    
    for i, q in enumerate(queries[:num_requests]):
        user_id = f"user_{uuid.uuid4().hex[:4]}"
        payload = {"query": q, "user_id": user_id}
        
        print(f"[REQ {i+1}] Sending: '{q}' (User: {user_id})")
        try:
            # POST Request
            resp = requests.post(f"{API_URL}/chat", json=payload)
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"[RES {i+1}] Status: {data['status']} | Trace: {data['trace_id']}")
                print(f"        Answer: {data['response'][:60]}...")
            else:
                 print(f"[ERR {i+1}] Status: {resp.status_code} | Detail: {resp.text}")
                 
        except Exception as e:
             print(f"[ERR {i+1}] Request Failed: {e}")
             
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n[INFO] Simulation Complete.")
    print(f"       Total Requests: {num_requests}")
    print(f"       Total Time: {duration:.2f}s")
    if num_requests > 0:
        print(f"       Avg Latency: {duration/num_requests:.2f}s/req")

if __name__ == "__main__":
    run_simulation()
