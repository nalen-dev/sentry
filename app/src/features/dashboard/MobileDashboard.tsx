// @ts-nocheck
import { useState } from 'react';
import { Layout, Search, Activity, History } from 'lucide-react';
import SegmentStats from './SegmentStats';
import DiagramVisualization from '../map/DiagramVisualization';

interface Props {
  mappings: any[];
  areas: any[]; // filtered areas (SegmentData-like)
  stats: { total: number; normal: number; warning: number; danger: number };
  mainGroups: string[];
  activeMainGroup: string;
  setActiveMainGroup: (g: string) => void;
  searchTerm: string;
  setSearchTerm: (s: string) => void;
  setSelectedSegment: (s: any) => void;
  setCategoryModal: (c: any) => void;
  logs: { id: number; time: string; msg: string; type: string }[];
  warningThreshold: number;
  criticalThreshold: number;
}

const statusColor = (a: any) =>
  !a.isAlarm && a.status === 'Normal'
    ? 'text-scada-success'
    : a.status.includes('WARN') ? 'text-yellow-500' : 'text-red-500';

/**
 * Phone layout of the dashboard: KPI stats, simplified P&ID, filterable segment list, recent logs.
 * The satellite map is intentionally desktop-only.
 */
export default function MobileDashboard({
  mappings, areas, stats, mainGroups, activeMainGroup, setActiveMainGroup,
  searchTerm, setSearchTerm, setSelectedSegment, setCategoryModal, logs,
  warningThreshold, criticalThreshold,
}: Props) {
  const [tab, setTab] = useState<'segments' | 'pid' | 'logs'>('segments');

  const tabBtn = (id: typeof tab, label: string, icon: any) => (
    <button
      onClick={() => setTab(id)}
      className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-bold tracking-widest uppercase border-b-2 transition-colors ${
        tab === id ? 'border-scada-primary text-scada-primary' : 'border-transparent text-text-secondary'
      }`}
    >
      {icon}{label}
    </button>
  );

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-bg-base w-full">
      <div className="p-3 shrink-0">
        <SegmentStats
          totalSegments={stats.total}
          normalSegments={stats.normal}
          warningSegments={stats.warning}
          dangerSegments={stats.danger}
          onCategoryClick={setCategoryModal}
        />
      </div>

      <div className="flex shrink-0 bg-bg-panel border-y border-border">
        {tabBtn('segments', 'Segments', <Activity size={14} />)}
        {tabBtn('pid', 'P&ID', <Layout size={14} />)}
        {tabBtn('logs', 'Logs', <History size={14} />)}
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {tab === 'segments' && (
          <div className="p-3 space-y-3">
            <div className="flex items-center bg-bg-panel border border-border rounded-lg px-3 py-2">
              <Search size={16} className="text-text-secondary mr-2" />
              <input
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                placeholder="Search segment..."
                className="bg-transparent outline-none text-sm flex-1 text-text-primary"
              />
            </div>
            <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
              {['All', ...mainGroups].map(g => (
                <button
                  key={g}
                  onClick={() => setActiveMainGroup(g)}
                  className={`shrink-0 px-3 py-1.5 rounded-full text-[11px] font-bold tracking-wider border ${
                    activeMainGroup === g
                      ? 'bg-scada-primary text-black border-scada-primary'
                      : 'bg-bg-panel text-text-secondary border-border'
                  }`}
                >
                  {g}
                </button>
              ))}
            </div>
            {areas.length === 0 && (
              <p className="text-center text-text-secondary text-sm py-8">No segments found.</p>
            )}
            {areas.map(a => (
              <button
                key={a.id}
                onClick={() => setSelectedSegment(a)}
                className={`w-full text-left bg-bg-panel border rounded-xl p-3 flex items-center justify-between ${
                  a.isAlarm && !a.status.includes('WARN') ? 'border-red-500/70' : 'border-border'
                }`}
              >
                <div className="min-w-0 pr-3">
                  <div className="font-bold text-sm text-text-primary truncate">{a.name}</div>
                  <div className="text-[11px] font-mono text-text-secondary mt-0.5">{a.distance}</div>
                  <div className={`text-[10px] font-bold uppercase tracking-widest mt-1 ${statusColor(a)}`}>{a.status}</div>
                </div>
                <div className={`font-mono font-bold text-xl shrink-0 ${statusColor(a)}`}>
                  {Number(a.temp).toFixed(1)}°C
                </div>
              </button>
            ))}
          </div>
        )}

        {tab === 'pid' && (
          <div className="p-3">
            <p className="text-[11px] text-text-secondary mb-2">Simplified diagram — scroll to pan. Satellite view is available on desktop.</p>
            <div className="h-[340px] rounded-xl overflow-hidden border border-border">
              <DiagramVisualization
                isFullscreen={true}
                hideHeader
                segments={mappings}
                warningThreshold={warningThreshold}
                criticalThreshold={criticalThreshold}
              />
            </div>
          </div>
        )}

        {tab === 'logs' && (
          <div className="p-3 space-y-2">
            {logs.length === 0 && <p className="text-center text-text-secondary text-sm py-8">No recent events.</p>}
            {logs.map(l => (
              <div key={l.id} className="bg-bg-panel border border-border rounded-lg p-2.5">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] font-mono text-text-secondary">{l.time}</span>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                    l.type === 'error' ? 'bg-red-500/20 text-red-400'
                    : l.type === 'warning' || l.type === 'warn' ? 'bg-yellow-500/20 text-yellow-500'
                    : 'bg-scada-primary/20 text-scada-primary'}`}>{l.type}</span>
                </div>
                <p className="text-xs text-text-primary leading-relaxed">{l.msg}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
