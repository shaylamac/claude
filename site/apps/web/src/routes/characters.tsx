import type { Route } from './+types/characters';
import { seo } from '@/lib/seo';
import { requireAuth } from '@/lib/require-auth';
import { CodexDirectory } from '@/components/codex-directory';

export function meta({ matches, location }: Route.MetaArgs) { return seo({ matches, location }, { title: 'Characters | Marked By Fate', description: 'A private directory of the people and supernatural beings of the Marked By Fate Kingdom.' }); }
export function clientLoader() { return { user: requireAuth() }; }
clientLoader.hydrate = true as const;
export function HydrateFallback() { return <div className="route-fallback">Opening the archive…</div>; }
export default function CharactersPage() { return <CodexDirectory kind="character" />; }
