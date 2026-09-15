import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# I want to inject the loading overlay right after `<div className="flex-1 relative overflow-hidden bg-bg-base flex">`
loading_overlay = """
        {isLoading && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-bg-base/80 backdrop-blur-sm">
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 border-4 border-scada-primary border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="font-mono text-scada-primary font-bold tracking-widest text-lg animate-pulse">LOADING FIELD DATA...</p>
            </div>
          </div>
        )}
        
        {!isLoading && mappings.length === 0 && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-bg-base/90 backdrop-blur-md">
            <div className="flex flex-col items-center max-w-lg text-center p-8 border border-border rounded-xl bg-bg-panel shadow-2xl">
              <Layout size={48} className="text-text-secondary mb-4" />
              <h3 className="font-bold text-2xl text-text-primary tracking-widest mb-2">NO SEGMENTS CONFIGURED</h3>
              <p className="text-text-secondary mb-6">Your dashboard is empty because no fiber segments have been mapped yet.</p>
              <button 
                onClick={() => window.location.href = '/settings'}
                className="px-6 py-3 bg-scada-primary text-black font-bold tracking-widest uppercase rounded hover:bg-scada-primary/90 transition-colors"
              >
                Go To Settings & Sync Data
              </button>
            </div>
          </div>
        )}
"""

target = r'<div className="flex-1 relative overflow-hidden bg-bg-base flex">'
replacement = target + loading_overlay
content = content.replace(target, replacement)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

