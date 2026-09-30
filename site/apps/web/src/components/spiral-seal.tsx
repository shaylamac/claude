export function SpiralSeal({ className = '', decorative = true }: { className?: string; decorative?: boolean }) {
  return (
    <svg className={className} viewBox="0 0 100 100" fill="none" aria-hidden={decorative} role={decorative ? undefined : 'img'} aria-label={decorative ? undefined : 'Spiral Mark'}>
      <circle cx="50" cy="50" r="47" stroke="currentColor" strokeOpacity=".22" strokeWidth=".7" />
      <circle cx="50" cy="50" r="41" stroke="currentColor" strokeOpacity=".38" strokeWidth=".55" strokeDasharray="1 4" />
      <path d="M51 17c-20-2-35 14-35 33 0 22 16 37 36 37 20 0 34-15 34-34 0-18-13-31-30-31-16 0-27 12-27 27 0 14 10 24 23 24 12 0 21-9 21-20 0-10-7-17-16-17-8 0-14 6-14 13 0 6 4 11 10 11 5 0 9-4 9-8 0-3-2-6-5-6-2 0-4 2-4 4" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" />
      <path d="M50 3v8M50 89v8M3 50h8M89 50h8" stroke="currentColor" strokeOpacity=".6" strokeWidth=".7" />
      <circle cx="50" cy="3" r="1.5" fill="currentColor" /><circle cx="97" cy="50" r="1.5" fill="currentColor" /><circle cx="3" cy="50" r="1.5" fill="currentColor" />
    </svg>
  );
}
