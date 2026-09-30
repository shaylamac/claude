import type { Route } from './+types/home';
import { seo } from '@/lib/seo';
import { Hero } from '@/components/home/hero';
import { Origin } from '@/components/home/origin';
import { World } from '@/components/home/world';
import { Closing } from '@/components/home/closing';

export function meta({ matches, location }: Route.MetaArgs) {
	return seo({ matches, location }, {
		title: 'Marked By Fate | A World Beyond the Veil',
		description: 'Enter the moonlit world of Marked By Fate. Discover the Spiral Mark, the hidden Kingdom, and the lives bound together by destiny.',
	});
}

export default function HomePage() {
	return <main><Hero /><Origin /><World /><Closing /></main>;
}
