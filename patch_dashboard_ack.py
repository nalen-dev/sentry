import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    code = f.read()

# Add the red pulse overlay
pulse_injection = """  return (
    <div className="h-screen bg-bg-base flex flex-col text-text-primary overflow-hidden font-sans">
      
      {/* RED PULSE OVERLAY FOR UNACKED ALARMS */}
      {unackedAlarms.length > 0 && !isPopupMuted && (
        <div className="absolute inset-0 pointer-events-none bg-red-600/15 animate-[pulse_2s_ease-in-out_infinite] z-40 mix-blend-overlay"></div>
      )}

      {/* TOP MENU BAR */}"""

code = code.replace("""  return (
    <div className="h-screen bg-bg-base flex flex-col text-text-primary overflow-hidden font-sans">
      
      {/* TOP MENU BAR */}""", pulse_injection)

# Add invoke to onAck
onack_injection = """            onAck={(ids) => {
              const newAcked = new Set(ackedAlarms);
              ids.forEach(id => newAcked.add(id));
              setAckedAlarms(newAcked);
              
              // Call backend to update MySQL AlarmResetTime
              import('@tauri-apps/api/core').then(({ invoke }) => {
                invoke('ack_all_alarms').catch(console.error);
              });
            }}"""

code = code.replace("""            onAck={(ids) => {
              const newAcked = new Set(ackedAlarms);
              ids.forEach(id => newAcked.add(id));
              setAckedAlarms(newAcked);
            }}""", onack_injection)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(code)

