import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router';
import { ArrowUpRight, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '@/hooks/use-auth';
import { SpiralSeal } from '@/components/spiral-seal';

export function LoginPanel() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setPending(true); setError('');
    try { await login(email.trim(), password); navigate('/characters', { replace: true }); }
    catch { setError('The email or password could not be verified. Please try again.'); setPending(false); }
  }
  return <main className="login-page"><div className="login-orbit" aria-hidden="true"><SpiralSeal /></div><div className="login-panel"><span className="eyebrow"><span className="tiny-diamond" /> PRIVATE ACCESS <span className="tiny-diamond" /></span><SpiralSeal className="login-seal" /><h1>The archive<br /><em>awaits you.</em></h1><p className="login-intro">The Kingdom keeps its stories close. Sign in to enter the private codex.</p><form onSubmit={submit} className="login-form"><label htmlFor="email">EMAIL ADDRESS</label><input id="email" type="email" autoComplete="email" placeholder="Your email address" value={email} onChange={event => setEmail(event.target.value)} required /><label htmlFor="password">PASSWORD</label><div className="password-wrap"><input id="password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" placeholder="Your password" value={password} onChange={event => setPassword(event.target.value)} required /><button type="button" aria-label={showPassword ? 'Hide password' : 'Show password'} onClick={() => setShowPassword(!showPassword)}>{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button></div>{error && <p className="form-error" role="alert">{error}</p>}<button className="login-submit" type="submit" disabled={pending}>{pending ? 'Opening the archive…' : 'Enter the codex'} <ArrowUpRight size={17} /></button></form><p className="login-note">Access is by invitation only. No public registration.</p></div><div className="login-aside"><span>THE KINGDOM REMEMBERS.</span><span>JUNE 03, 2019</span></div></main>;
}
