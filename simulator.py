import subprocess
import threading
import time
import sys

INTERVAL = 5.0
RUNNING = True
MANUAL_OVERRIDES = {}

def db_execute(query):
    try:
        subprocess.run(["mysql", "-u", "root", "dtscontroler", "-e", query], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        pass

def background_task():
    global RUNNING
    while RUNNING:
        # 1. Random fluctuations for all segments (between -0.5C and +0.5C)
        # Temperatures are stored multiplied by 10 (e.g., 35.5C -> 355)
        query = """
        UPDATE opt_fq_list 
        SET TempMax = TempMax + FLOOR(RAND() * 11 - 5), 
            TempAvg = TempAvg + FLOOR(RAND() * 11 - 5);
        """
        db_execute(query)
        
        # 2. Keep temps inside a realistic baseline if they drift too much (e.g., 25C to 40C)
        # Note: We won't cap the high end too aggressively in case user wants to see natural alarms,
        # but let's just keep the natural drift between 250 and 420.
        query_cap = """
        UPDATE opt_fq_list SET TempMax = 420 WHERE TempMax > 420 AND TempMax < 500;
        UPDATE opt_fq_list SET TempMax = 250 WHERE TempMax < 250;
        """
        db_execute(query_cap)
        
        # 3. Apply manual overrides (this overrides the random fluctuations)
        if MANUAL_OVERRIDES:
            for (ch, code), temp in MANUAL_OVERRIDES.items():
                temp_val = int(temp * 10)
                q = f"UPDATE opt_fq_list SET TempMax = {temp_val}, TempAvg = {temp_val} WHERE Ch = {ch} AND Code = {code};"
                db_execute(q)
                
        time.sleep(INTERVAL)

def start_shell():
    global INTERVAL, RUNNING, MANUAL_OVERRIDES
    print("======================================================")
    print(" 🚀 DTS MySQL Live Simulator Started!")
    print("======================================================")
    print(" Commands:")
    print("  interval <sec>         - Change data push interval (e.g. 'interval 2')")
    print("  set <Ch> <Code> <Temp> - Force set Temp for a segment (e.g. 'set 1 3 65.5')")
    print("  clear                  - Clear all overrides (let temps float naturally)")
    print("  quit / exit            - Stop simulator")
    print("======================================================")
    
    t = threading.Thread(target=background_task)
    t.start()
    
    while RUNNING:
        try:
            cmd = input("simulator> ").strip().split()
            if not cmd: continue
            
            action = cmd[0].lower()
            if action in ["quit", "exit"]:
                RUNNING = False
                break
            elif action == "interval" and len(cmd) == 2:
                INTERVAL = float(cmd[1])
                print(f"[*] Interval set to {INTERVAL} seconds.")
            elif action == "set" and len(cmd) == 4:
                ch = int(cmd[1])
                code = int(cmd[2])
                temp = float(cmd[3])
                MANUAL_OVERRIDES[(ch, code)] = temp
                print(f"[*] Override applied: Ch {ch}, Code {code} -> {temp}°C")
                # Apply immediately
                temp_val = int(temp * 10)
                db_execute(f"UPDATE opt_fq_list SET TempMax = {temp_val}, TempAvg = {temp_val} WHERE Ch = {ch} AND Code = {code};")
            elif action == "clear":
                MANUAL_OVERRIDES.clear()
                print("[*] All overrides cleared. Temperatures returning to natural drift.")
            else:
                print("[!] Unknown command or invalid format.")
        except KeyboardInterrupt:
            RUNNING = False
            break
        except Exception as e:
            print(f"[!] Error: {e}")
            
    print("Waiting for background task to finish...")
    t.join()
    print("Simulator stopped.")

if __name__ == '__main__':
    # Initialize some baseline data if needed (optional)
    print("Setting baseline temperatures to ~30C...")
    db_execute("UPDATE opt_fq_list SET TempMax = 300, TempAvg = 290 WHERE TempMax = 0 OR TempMax IS NULL;")
    start_shell()
