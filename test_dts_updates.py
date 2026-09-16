import time
import subprocess
import json
from datetime import datetime

DB_CMD = ["mysql", "-h", "192.168.1.64", "-P", "58329", "-uroot", "-p'l0mY4cH9H?h9'", "dtscontroler", "-B", "-e"]

def query_live():
    # Poll live temperatures for Ch 2 (Code 1) and Ch 7 (Code 36)
    res = subprocess.check_output(" ".join(DB_CMD + ['"SELECT Ch, Code, TempAvg, TempMax FROM opt_fq_list WHERE (Ch=2 AND Code=1) OR (Ch=7 AND Code=36);"']), shell=True).decode('utf-8')
    lines = res.strip().split('\n')[1:]
    return {f"Ch{l.split()[0]}_C{l.split()[1]}": {"TempAvg": int(l.split()[2]), "TempMax": int(l.split()[3])} for l in lines}

def query_history():
    # Get latest history ID and timestamp for Ch 2 and Ch 7
    res2 = subprocess.check_output(" ".join(DB_CMD + ['"SELECT Ch, Code, MAX(id), MAX(CreationTime) FROM fq_history_list WHERE (Ch=2 AND Code=1) OR (Ch=7 AND Code=36) GROUP BY Ch, Code;"']), shell=True).decode('utf-8')
    lines = res2.strip().split('\n')[1:]
    data = {}
    for l in lines:
        parts = l.split('\t')
        ch, code, max_id, max_time = parts[0], parts[1], parts[2], parts[3]
        data[f"Ch{ch}_C{code}"] = {"LastHistID": max_id, "LastHistTime": max_time}
    return data

results = []
print("Starting 1-minute observation (polling every 10s)...")
for i in range(6):
    now = datetime.now().strftime('%H:%M:%S')
    live = query_live()
    hist = query_history()
    
    snapshot = {"time": now, "live": live, "hist": hist}
    results.append(snapshot)
    print(f"[{now}] Polled data.")
    time.sleep(10)

print("\n--- RESULTS ---")
print(json.dumps(results, indent=2))
