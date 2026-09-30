import { Link } from 'react-router';
import { ArrowDown, ArrowUpRight } from 'lucide-react';
import { SpiralSeal } from '@/components/spiral-seal';

export function Hero() {
  return <section className="hero" aria-labelledby="hero-title">
    <div className="hero-stars" aria-hidden="true" />
    <div className="hero-overline"><span>THE OFFICIAL WORLD CODEX</span><span>EST. JUNE 03, 2019</span></div>
    <div className="hero-center">
      <div className="celestial-art" aria-hidden="true"><div className="celestial-orbit"><span className="orbit-star orbit-star-one" /><span className="orbit-star orbit-star-two" /></div><div className="moon-disc"><span className="moon-shade" /></div><SpiralSeal className="hero-spiral" /></div>
      <p className="eyebrow hero-kicker"><span className="tiny-diamond" /> AN ARCHIVE OF THE UNSEEN <span className="tiny-diamond" /></p>
      <h1 id="hero-title">Marked <span className="title-by">by</span> Fate<span className="title-period">.</span></h1>
      <p className="hero-description">Some stories are written in the stars. Others begin with a mark on the wrist.</p>
      <Link to="/characters" className="primary-link">Explore the codex <ArrowUpRight size={17} strokeWidth={1.5} /></Link>
    </div>
    <div className="hero-bottom"><span>01 / THE BEGINNING</span><a href="#the-mark" aria-label="Scroll to the story"><ArrowDown size={19} strokeWidth={1.2} /></a><span>SCROLL TO DISCOVER</span></div>
    <div className="hero-cropped" aria-hidden="true">FATE</div>
  </section>;
}
