import { Link } from 'react-router';
import { ArrowUpRight } from 'lucide-react';
import { SpiralSeal } from '@/components/spiral-seal';

export function Closing() {
  return <section className="closing-section"><SpiralSeal className="closing-seal" /><p className="eyebrow">THE KINGDOM IS CALLING</p><h2>Every mark<br />has <em>a meaning.</em></h2><p>Step inside the archive. Follow the threads. Discover what the Moon Goddess set in motion.</p><Link to="/lore" className="primary-link">Enter the library <ArrowUpRight size={17} strokeWidth={1.5} /></Link></section>;
}
