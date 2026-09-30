import type { Route } from './+types/login';
import { seo } from '@/lib/seo';
import { LoginPanel } from '@/components/auth/login-panel';
import pb from '@/lib/pocketbase-client';
import { redirect } from 'react-router';

export function meta({ matches, location }: Route.MetaArgs) { return seo({ matches, location }, { title: 'Enter the Codex | Marked By Fate', description: 'Sign in to access the private Marked By Fate worldbuilding codex.' }); }
export function clientLoader() { return pb.authStore.isValid && pb.authStore.record ? redirect('/characters') : null; }
clientLoader.hydrate = true as const;
export function HydrateFallback() { return <div className="route-fallback">Opening the archive…</div>; }
export default function LoginPage() { return <LoginPanel />; }
