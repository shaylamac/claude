import { useEffect, useMemo, useState } from 'react';
import { Search, ArrowUpRight, RotateCcw } from 'lucide-react';
import type { RecordModel } from 'pocketbase';
import pb from '@/lib/pocketbase-client';
import { Dialog, DialogContent, DialogDescription, DialogTitle } from '@/components/ui/dialog';
import { SpiralSeal } from '@/components/spiral-seal';

type Kind = 'character' | 'family' | 'lore';
type Entry = RecordModel & { kind: Kind; title: string; category: string; subtitle: string; summary: string; body: string; note: string; association: string; position: number };
const settings = {
  character: { eyebrow: 'THE PEOPLE OF THE KINGDOM', title: 'The Characters', italic: 'behind the story.', description: 'Meet the lives shaped by the Spiral Mark, and the people who knew the hidden world long before it appeared.', index: 'I', search: 'Search characters…' },
  family: { eyebrow: 'BONDS WRITTEN IN TIME', title: 'The Families', italic: 'of the Kingdom.', description: 'Lineages, circles, courts, and chosen kin. Discover the bonds that hold the hidden world together.', index: 'II', search: 'Search families…' },
  lore: { eyebrow: 'AN ARCHIVE OF THE UNSEEN', title: 'The Lore', italic: 'of the world.', description: 'Every secret has a beginning. Trace the mark, the Moon Goddess, and the mysteries beyond the veil.', index: 'III', search: 'Search the library…' },
};

export function CodexDirectory({ kind }: { kind: Kind }) {
  const config = settings[kind];
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('All');
  const [selected, setSelected] = useState<Entry | null>(null);

  useEffect(() => {
    let active = true;
    pb.collection('codex_entries').getFullList<Entry>({ filter: pb.filter('kind = {:kind}', { kind }), sort: 'position' })
      .then(data => { if (active) { setEntries(data); setLoading(false); } })
      .catch(() => { if (active) { setError('The archive could not be opened. Please try again.'); setLoading(false); } });
    return () => { active = false; };
  }, [kind]);

  const categories = useMemo(() => ['All', ...new Set(entries.map(item => item.category))], [entries]);
  const filtered = useMemo(() => entries.filter(item => (category === 'All' || item.category === category) && `${item.title} ${item.category} ${item.subtitle} ${item.summary}`.toLowerCase().includes(query.trim().toLowerCase())), [entries, category, query]);
  return <main className="directory-page">
    <div className="directory-ornament" aria-hidden="true"><SpiralSeal /></div>
    <div className="directory-container">
      <div className="directory-topline"><span>THE MARKED BY FATE CODEX</span><span>ARCHIVE / {config.index}</span></div>
      <div className="directory-heading"><div><p className="eyebrow"><span className="tiny-diamond" /> {config.eyebrow}</p><h1>{config.title}<br /><em>{config.italic}</em></h1></div><p>{config.description}</p></div>
      <div className="directory-controls"><div className="filter-tabs" role="group" aria-label="Filter by category">{categories.map(item => <button key={item} type="button" className={category === item ? 'filter active' : 'filter'} onClick={() => setCategory(item)}>{item}</button>)}</div><label className="directory-search"><Search size={16} strokeWidth={1.5} /><span className="sr-only">{config.search}</span><input value={query} onChange={event => setQuery(event.target.value)} placeholder={config.search} type="search" /></label></div>
      {loading ? <div className="directory-status"><SpiralSeal className="status-seal" /><p>Opening the archive…</p></div> : error ? <div className="directory-status"><p>{error}</p><button onClick={() => window.location.reload()} className="status-action"><RotateCcw size={15} /> Try again</button></div> : filtered.length ? <><div className="results-count">SHOWING {String(filtered.length).padStart(2, '0')} {filtered.length === 1 ? 'ENTRY' : 'ENTRIES'} <span>✧</span> {category === 'All' ? 'COMPLETE ARCHIVE' : category.toUpperCase()}</div><div className="entry-list">{filtered.map((entry, index) => <button className="entry-row" key={entry.id} onClick={() => setSelected(entry)}><span className="entry-index">{String(index + 1).padStart(2, '0')}</span><span className="entry-symbol" aria-hidden="true">{kind === 'lore' ? '✦' : kind === 'family' ? '◇' : '☾'}</span><span className="entry-primary"><span className="entry-category">{entry.category}</span><strong>{entry.title}</strong><small>{entry.subtitle}</small></span><span className="entry-summary">{entry.summary}</span><ArrowUpRight className="entry-arrow" size={22} strokeWidth={1.2} /></button>)}</div></> : <div className="directory-status"><SpiralSeal className="status-seal" /><p>No entries match your search.</p><button className="status-action" onClick={() => { setQuery(''); setCategory('All'); }}>Clear filters <ArrowUpRight size={15} /></button></div>}
      <div className="directory-end"><span>END OF ARCHIVE / {config.index}</span><SpiralSeal /></div>
    </div>
    <Dialog open={Boolean(selected)} onOpenChange={open => { if (!open) setSelected(null); }}><DialogContent className="entry-dialog"><div className="dialog-meta"><span>THE MARKED BY FATE CODEX</span><span>ARCHIVE / {config.index}</span></div><div className="dialog-symbol"><SpiralSeal /></div><p className="eyebrow">{selected?.category}</p><DialogTitle className="dialog-title">{selected?.title}</DialogTitle><DialogDescription className="dialog-subtitle">{selected?.subtitle}</DialogDescription><div className="dialog-rule" /><p className="dialog-summary">{selected?.summary}</p><p className="dialog-body">{selected?.body}</p><div className="dialog-foot"><span>{selected?.note}</span><span>{selected?.association}</span></div></DialogContent></Dialog>
  </main>;
}
