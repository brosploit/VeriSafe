import { AlertTriangle, BadgeCheck, CheckCircle2, CircleHelp, ClipboardCheck, Copy, Fingerprint, Info, ShieldAlert, ShieldCheck } from 'lucide-react';
import type { AnalysisResult, RiskLevel } from '../types/api';

const riskData: Record<RiskLevel, { style: string; badge: string; label: string; Icon: typeof ShieldCheck }> = {
  Low: { style: 'risk-low', badge: 'Low risk', label: 'Few suspicious signals detected', Icon: ShieldCheck },
  Medium: { style: 'risk-medium', badge: 'Medium risk', label: 'Some indicators deserve attention', Icon: AlertTriangle },
  High: { style: 'risk-high', badge: 'High risk', label: 'Strong warning signs detected', Icon: ShieldAlert },
  'Needs Review': { style: 'risk-review', badge: 'Needs review', label: 'Insufficient evidence for a conclusion', Icon: CircleHelp },
};

export default function Results({ result, onReset }: { result: AnalysisResult; onReset: () => void }) {
  const risk = riskData[result.risk_level] ?? riskData['Needs Review'];
  const Icon = risk.Icon;
  const confidence = typeof result.confidence_score === 'number' && Number.isFinite(result.confidence_score)
    ? `${Math.round(Math.max(0, Math.min(1, result.confidence_score)) * 100)}%`
    : 'Not provided';
  const indicators = Array.isArray(result.indicators) ? result.indicators : [];
  const recommendations = Array.isArray(result.recommendations) ? result.recommendations : [];

  function copyReport() {
    const text = [
      `VeriSafe analysis ${result.analysis_id}`,
      `Risk: ${result.risk_level} (confidence: ${confidence})`,
      result.summary,
      '',
      'Indicators:',
      ...indicators.map(item => `- [${item.severity}] ${item.signal}: ${item.explanation}`),
      '',
      'Recommendations:',
      ...recommendations.map((item, index) => `${index + 1}. ${item}`),
      '',
      result.assessment_disclaimer,
    ].join('\n');
    if (navigator.clipboard?.writeText) void navigator.clipboard.writeText(text);
  }

  return (
    <section className="space-y-5" aria-live="polite">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div><div className="eyebrow">Analysis complete</div><h2 className="section-title">Your security assessment</h2></div>
        <div className="flex gap-2"><button className="btn-secondary" onClick={copyReport}><Copy size={16} /> Copy report</button><button className="btn-secondary" onClick={onReset}>New scan</button></div>
      </div>
      <div className={`rounded-2xl border p-5 sm:p-6 ${risk.style}`}>
        <div className="flex items-start gap-4"><div className="rounded-xl bg-white/10 p-3"><Icon size={29} /></div><div className="flex-1"><div className="mb-2 flex flex-wrap items-center gap-3"><span className="font-bold text-xl">{risk.badge}</span><span className="rounded-full border border-current/20 px-3 py-1 text-xs font-semibold">Confidence {confidence}</span></div><p className="font-medium">{risk.label}</p><p className="mt-3 text-sm leading-relaxed opacity-90">{result.summary}</p></div></div>
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="panel"><div className="flex items-center gap-2"><Fingerprint className="text-teal" size={19} /><h3 className="font-semibold">Why it was flagged</h3><span className="count-pill">{indicators.length}</span></div>
          <div className="mt-5 space-y-3">{indicators.length ? indicators.map((item, index) => <article className="indicator" key={`${item.category}-${index}`}><div className="flex flex-wrap items-center justify-between gap-2"><h4 className="font-semibold text-sm">{item.signal}</h4><span className={`severity severity-${item.severity}`}>{item.severity}</span></div><p className="mt-2 text-sm text-slate-400 leading-relaxed">{item.explanation}</p>{item.matched_text && <p className="matched">Matched: {item.matched_text}</p>}</article>) : <p className="text-sm text-slate-400">No specific indicators were reported by the analysis engine.</p>}</div>
        </div>
        <div className="panel"><div className="flex items-center gap-2"><ClipboardCheck className="text-teal" size={19} /><h3 className="font-semibold">Recommended next steps</h3></div><div className="mt-5 space-y-4">{recommendations.length ? recommendations.map((item, index) => <div className="flex gap-3" key={index}><span className="step-dot">{index + 1}</span><p className="text-sm leading-relaxed text-slate-300">{item}</p></div>) : <p className="text-sm text-slate-400">Verify important requests using independent official contact information.</p>}</div><div className="mt-6 rounded-xl bg-teal/10 border border-teal/20 p-4 flex gap-3"><BadgeCheck className="shrink-0 text-teal" size={20}/><p className="text-xs leading-relaxed text-slate-300">Never enter passwords, OTPs or financial details on a site you reached through an unverified message.</p></div></div>
      </div>
      <div className="panel flex flex-wrap items-start gap-3"><Info className="text-slate-400 shrink-0" size={19}/><div className="flex-1"><p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Assessment details</p><p className="mt-1 text-xs text-slate-400 break-all">ID: {result.analysis_id} · {result.timestamp ? new Date(result.timestamp).toLocaleString() : 'Time unavailable'}</p><p className="mt-3 text-xs leading-relaxed text-slate-400">{result.assessment_disclaimer || 'This preliminary assessment is not a guarantee of safety. Verify consequential requests independently.'}</p></div><CheckCircle2 size={18} className="text-teal"/></div>
    </section>
  );
}
