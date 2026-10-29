import { useEffect, useRef, useState } from 'react';
import { Activity, ArrowRight, Check, ChevronRight, CircleHelp, ClipboardCheck, Fingerprint, Globe2, Info, Link2, LockKeyhole, Mail, Menu, ScanSearch, Shield, ShieldCheck, ShieldQuestion, Sparkles, X } from 'lucide-react';
import Results from './components/Results';
import { analyzeMessage, analyzeUrl, checkHealth } from './services/api';
import type { AnalysisMode, AnalysisResult, Channel } from './types/api';
import { isValidWebUrl } from './utils/validation';

const steps = [
  { number: '01', title: 'Submit', text: 'Paste the suspicious message or URL you want to investigate.', Icon: ClipboardCheck },
  { number: '02', title: 'Detect', text: 'VeriSafe checks for phishing and fraud warning signals.', Icon: Fingerprint },
  { number: '03', title: 'Understand', text: 'Review the evidence behind the risk assessment.', Icon: ScanSearch },
  { number: '04', title: 'Verify', text: 'Use practical recommendations to stay in control.', Icon: ShieldCheck },
];

export default function App() {
  const [mode, setMode] = useState<AnalysisMode>('message');
  const [message, setMessage] = useState('');
  const [sender, setSender] = useState('');
  const [channel, setChannel] = useState<Channel>('email');
  const [url, setUrl] = useState('');
  const [context, setContext] = useState('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [health, setHealth] = useState<'checking' | 'online' | 'offline'>('checking');
  const [mobileMenu, setMobileMenu] = useState(false);
  const controller = useRef<AbortController | null>(null);

  useEffect(() => {
    const abort = new AbortController();
    checkHealth(abort.signal).then(status => { if (!abort.signal.aborted) setHealth(status ? 'online' : 'offline'); });
    return () => abort.abort();
  }, []);
  useEffect(() => () => controller.current?.abort(), []);

  function changeMode(next: AnalysisMode) {
    controller.current?.abort();
    setIsLoading(false);
    setMode(next);
    setError('');
    setResult(null);
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setResult(null);
    if (mode === 'message') {
      if (!message.trim()) return setError('Enter a message to analyze.');
      if (message.length > 50000) return setError('Messages must be 50,000 characters or fewer.');
      if (sender.length > 255) return setError('Sender must be 255 characters or fewer.');
    } else {
      if (!isValidWebUrl(url)) return setError('Enter a valid http:// or https:// URL without embedded credentials.');
      if (url.length > 2048) return setError('URLs must be 2,048 characters or fewer.');
      if (context.length > 500) return setError('Context must be 500 characters or fewer.');
    }
    const nextController = new AbortController();
    controller.current = nextController;
    setIsLoading(true);
    try {
      const output = mode === 'message'
        ? await analyzeMessage({ message_text: message.trim(), sender: sender.trim() || undefined, channel }, nextController.signal)
        : await analyzeUrl({ url: url.trim(), context: context.trim() || undefined }, nextController.signal);
      if (!nextController.signal.aborted) {
        if (!output || typeof output.risk_level !== 'string' || !output.summary) throw new Error('The API returned an incomplete analysis response.');
        setResult(output);
      }
    } catch (err) {
      if (!nextController.signal.aborted) setError(err instanceof Error ? err.message : 'Unable to analyze input.');
    } finally {
      if (!nextController.signal.aborted) setIsLoading(false);
    }
  }

  function fillExample() {
    if (mode === 'message') {
      setMessage('URGENT: Your account will be suspended in 30 minutes. Click http://192.168.1.1/verify immediately and enter your password and OTP to restore access.');
      setSender('account-security@example.invalid');
      setChannel('sms');
    } else {
      setUrl('https://secure-login.paypa1-update.com/account/login');
      setContext('Received in an unexpected account suspension email');
    }
    setError('');
  }

  const doNavigate = (target: string) => {
    setMobileMenu(false);
    document.querySelector(target)?.scrollIntoView({ behavior: 'smooth' });
  };

  return <div className="min-h-screen bg-navy text-slate-100">
    <div className="ambient ambient-one" aria-hidden="true"/><div className="ambient ambient-two" aria-hidden="true"/>
    <header className="header"><div className="container-wrap flex h-20 items-center justify-between gap-4">
      <a href="#top" className="flex items-center gap-3" aria-label="VeriSafe home"><div className="brand-icon"><ShieldCheck size={23}/></div><div className="text-xl font-extrabold tracking-tight">Veri<span className="text-teal">Safe</span><span className="ml-2 hidden text-[9px] font-bold uppercase tracking-[.2em] text-slate-500 sm:inline">Beta</span></div></a>
      <nav className="hidden items-center gap-8 text-sm font-medium text-slate-400 md:flex"><button onClick={() => doNavigate('#analyzer')} className="nav-link">Analyzer</button><button onClick={() => doNavigate('#how-it-works')} className="nav-link">How it works</button><button onClick={() => doNavigate('#about')} className="nav-link">About</button></nav>
      <div className="hidden items-center gap-3 md:flex"><div className="health"><span className={`health-dot ${health}`} />{health === 'checking' ? 'Checking API' : health === 'online' ? 'API connected' : 'API unavailable'}</div><button className="btn-primary !px-4 !py-2.5" onClick={() => doNavigate('#analyzer')}>Start scanning <ArrowRight size={15}/></button></div>
      <button className="md:hidden p-2 text-slate-200" aria-label="Toggle menu" aria-expanded={mobileMenu} onClick={() => setMobileMenu(value => !value)}>{mobileMenu ? <X/> : <Menu/>}</button>
    </div>{mobileMenu && <div className="mobile-menu container-wrap"><button onClick={() => doNavigate('#analyzer')}>Analyzer</button><button onClick={() => doNavigate('#how-it-works')}>How it works</button><button onClick={() => doNavigate('#about')}>About</button></div>}</header>

    <main id="top">
      <section className="container-wrap hero"><div className="flex flex-col items-center text-center"><div className="hero-tag"><Sparkles size={14}/> AI-assisted fraud & phishing protection <ChevronRight size={14}/></div><h1 className="hero-title">Stay one step ahead<br/>of <span>digital threats.</span></h1><p className="hero-subtitle">Analyze suspicious messages and links, understand potential warning signs, and make safer decisions with confidence.</p><div className="flex flex-wrap justify-center gap-3"><button className="btn-primary" onClick={() => doNavigate('#analyzer')}><ScanSearch size={19}/> Analyze a threat <ArrowRight size={18}/></button><button className="btn-secondary" onClick={() => doNavigate('#how-it-works')}>How it works <ChevronRight size={17}/></button></div><div className="hero-trust"><span><Check size={15}/> Explainable risk signals</span><span><Check size={15}/> Actionable guidance</span><span><Check size={15}/> No account required</span></div></div></section>

      <section id="analyzer" className="container-wrap analyzer-section"><div className="scanner-shell"><div className="scanner-title-row"><div><div className="eyebrow"><span className="inline-block h-1.5 w-1.5 rounded-full bg-teal mr-2"/>Threat intelligence workspace</div><h2 className="section-title mt-2">Analyze something suspicious</h2><p className="mt-2 text-sm text-slate-400">Choose an analysis type to get a transparent risk assessment.</p></div><span className="hidden rounded-xl bg-teal/10 p-3 text-teal sm:block"><Shield size={24}/></span></div>
        <div className="mode-switch" role="tablist" aria-label="Analysis type"><button role="tab" aria-selected={mode === 'message'} className={mode === 'message' ? 'selected' : ''} onClick={() => changeMode('message')}><Mail size={17}/> Message analysis</button><button role="tab" aria-selected={mode === 'url'} className={mode === 'url' ? 'selected' : ''} onClick={() => changeMode('url')}><Link2 size={17}/> URL inspection</button></div>
        <div className="scanner-body">{result ? <Results result={result} onReset={() => setResult(null)} /> : <form onSubmit={submit} noValidate>
          {mode === 'message' ? <div className="space-y-5"><div><div className="flex items-center justify-between"><label className="form-label" htmlFor="message">Suspicious message <span className="text-red-400">*</span></label><button className="example-link" type="button" onClick={fillExample}><Sparkles size={14}/> Try an example</button></div><textarea id="message" className="form-field min-h-40 resize-y" value={message} onChange={event => setMessage(event.target.value)} maxLength={50000} placeholder={'Paste an email, SMS, or chat message here...\n\nFor your safety, remove passwords, OTPs and sensitive personal details before submitting.'} required/><div className="text-right text-xs text-slate-500">{message.length.toLocaleString()} / 50,000 characters</div></div><div className="grid gap-4 sm:grid-cols-2"><div><label className="form-label" htmlFor="sender">Sender <span className="text-slate-500 font-normal">(optional)</span></label><input id="sender" className="form-field" placeholder="e.g. alerts@example.com" maxLength={255} value={sender} onChange={event => setSender(event.target.value)} /></div><div><label className="form-label" htmlFor="channel">Message channel</label><select id="channel" className="form-field" value={channel} onChange={event => setChannel(event.target.value as Channel)}><option value="email">Email</option><option value="sms">SMS</option><option value="chat">Chat</option><option value="social">Social media</option><option value="other">Other</option></select></div></div></div> : <div className="space-y-5"><div><div className="flex items-center justify-between"><label className="form-label" htmlFor="url">Suspicious URL <span className="text-red-400">*</span></label><button className="example-link" type="button" onClick={fillExample}><Sparkles size={14}/> Try an example</button></div><div className="relative"><Globe2 size={18} className="absolute left-4 top-4 text-slate-500"/><input id="url" type="url" maxLength={2048} required className="form-field !pl-11" placeholder="https://example.com/verify-account" value={url} onChange={event => setUrl(event.target.value)}/></div><p className="mt-2 text-xs text-slate-500">Only HTTP and HTTPS URLs are supported. The application will not open this link.</p></div><div><label className="form-label" htmlFor="context">Where did you find it? <span className="text-slate-500 font-normal">(optional)</span></label><textarea id="context" className="form-field min-h-24 resize-y" maxLength={500} placeholder="e.g. Received by SMS, claiming to be my bank..." value={context} onChange={event => setContext(event.target.value)}/></div></div>}
          {error && <div className="error-box" role="alert"><CircleHelp className="shrink-0" size={18}/><span>{error}</span></div>}
          <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-white/10 pt-6"><div className="flex items-start gap-2 text-xs text-slate-500"><LockKeyhole size={15} className="mt-0.5 shrink-0"/><span>Please redact sensitive data before submitting. Content is sent to the configured backend.</span></div><button type="submit" className="btn-primary min-w-44 justify-center" disabled={isLoading}>{isLoading ? <><span className="spinner"/> Analyzing...</> : <><ScanSearch size={18}/> Run analysis <ArrowRight size={17}/></>}</button></div>
        </form>}</div></div><div className="mt-4 flex items-start gap-2 text-xs leading-relaxed text-slate-500"><Info size={15} className="shrink-0"/><span>VeriSafe provides preliminary heuristic assessments. Results are not a guarantee of safety or maliciousness. Always verify important requests independently.</span></div></section>

      <section id="how-it-works" className="container-wrap section-space"><div className="text-center"><div className="eyebrow">Simple. Transparent. Actionable.</div><h2 className="section-title mt-3">Security insights in four steps</h2><p className="mx-auto mt-3 max-w-xl text-sm text-slate-400 leading-relaxed">Go from uncertainty to informed action without needing to be a cybersecurity expert.</p></div><div className="mt-10 grid gap-4 md:grid-cols-4">{steps.map(({ number, title, text, Icon }) => <div className="step-card" key={number}><div className="flex items-center justify-between"><div className="step-icon"><Icon size={20}/></div><span className="text-3xl font-bold text-white/10">{number}</span></div><h3 className="mt-6 font-bold text-base">{title}</h3><p className="mt-2 text-sm leading-relaxed text-slate-400">{text}</p></div>)}</div></section>

      <section id="about" className="container-wrap pb-20"><div className="about-panel"><div className="relative z-10 max-w-2xl"><div className="eyebrow">Built for awareness, not guesswork</div><h2 className="section-title mt-3">Know the signs. Take the right action.</h2><p className="mt-4 text-sm leading-7 text-slate-300">Phishing attacks use urgency, impersonation and deceptive links. VeriSafe helps make those warning signs understandable, with evidence-backed findings and concrete recommendations.</p><div className="mt-6 flex flex-wrap gap-5 text-sm text-slate-300"><span className="flex items-center gap-2"><Activity className="text-teal" size={16}/> Clear risk levels</span><span className="flex items-center gap-2"><ShieldQuestion className="text-teal" size={16}/> Transparent explanations</span><span className="flex items-center gap-2"><Check className="text-teal" size={16}/> Safer next steps</span></div></div><ShieldCheck className="about-watermark" size={220}/></div></section>
    </main>
    <footer className="footer"><div className="container-wrap flex flex-col items-start justify-between gap-4 py-7 sm:flex-row sm:items-center"><div className="flex items-center gap-2 font-bold"><ShieldCheck className="text-teal" size={19}/> VeriSafe <span className="ml-2 text-xs font-normal text-slate-500">Detect. Understand. Verify.</span></div><div className="text-xs text-slate-500">Built by Team Shadow Paradox · Preliminary analysis only</div></div></footer>
  </div>;
}
