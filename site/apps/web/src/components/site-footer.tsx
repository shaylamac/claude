import { Link } from 'react-router';
import { SpiralSeal } from '@/components/spiral-seal';

export function SiteFooter() {
  return <footer className="site-footer"><div className="footer-top"><div><SpiralSeal className="footer-seal" /><p>EVERY DESTINY BEGINS SOMEWHERE.</p></div><div className="footer-links"><Link to="/characters">Characters</Link><Link to="/families">Families</Link><Link to="/lore">Lore</Link></div></div><div className="footer-bottom"><span>© {new Date().getFullYear()} MARKED BY FATE</span><span>THE KINGDOM REMEMBERS.</span><span>A PRIVATE SERIES CODEX</span></div></footer>;
}
