import { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router';
import { Menu, X, ArrowUpRight } from 'lucide-react';
import { useAuth } from '@/hooks/use-auth';
import { SpiralSeal } from '@/components/spiral-seal';

const links = [{ to: '/', label: 'Home' }, { to: '/characters', label: 'Characters' }, { to: '/families', label: 'Families' }, { to: '/lore', label: 'Lore' }];

export function SiteHeader() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { isAuthed, isLoading, logout } = useAuth();
  function signOut() { logout(); setOpen(false); navigate('/login', { replace: true }); }
  return (
    <header className="site-header">
      <Link to="/" className="brand" onClick={() => setOpen(false)} aria-label="Marked By Fate home"><SpiralSeal className="brand-mark" /><span>MARKED <em>BY</em> FATE</span></Link>
      <nav className={`main-nav ${open ? 'is-open' : ''}`} aria-label="Main navigation">
        {links.map(link => <NavLink key={link.to} to={link.to} end={link.to === '/'} onClick={() => setOpen(false)} className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>{link.label}</NavLink>)}
        <div className="mobile-account">{!isLoading && (isAuthed ? <button onClick={signOut} className="nav-link">Sign out</button> : <Link to="/login" onClick={() => setOpen(false)} className="nav-link">Enter the codex</Link>)}</div>
      </nav>
      <div className="header-account">{isLoading ? <span className="account-loading" /> : isAuthed ? <button className="header-enter" onClick={signOut}>Sign out <ArrowUpRight size={15} /></button> : <Link className="header-enter" to="/login">Enter the codex <ArrowUpRight size={15} /></Link>}</div>
      <button className="menu-toggle" aria-label={open ? 'Close menu' : 'Open menu'} aria-expanded={open} onClick={() => setOpen(!open)}>{open ? <X size={23} /> : <Menu size={23} />}</button>
    </header>
  );
}
