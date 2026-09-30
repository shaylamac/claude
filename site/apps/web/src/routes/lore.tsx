import type { Route } from './+types/lore';
import { seo } from '@/lib/seo';
import { requireAuth } from '@/lib/require-auth';
import { CodexDirectory } from '@/components/codex-directory';

export function meta({ matches, location }: Route.MetaArgs) { return seo({ matches, location }, { title: 'Lore Library | Marked By Fate', description: 'The private Marked By Fate lore library: the Spiral Mark, the Moon Goddess, the Kingdom, and its mysteries.' }); }
export function clientLoader() { return { user: requireAuth() }; }
clientLoader.hydrate = true as const;
export function HydrateFallback() { return <div className="route-fallback">Opening the archive…</div>; }
export default function LorePage() { return <CodexDirectory kind="lore" />; }
