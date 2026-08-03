type EyebrowProps = {
  children: React.ReactNode;
  /** Section eyebrows are muted ink; bylines are terracotta. */
  tone?: 'muted' | 'terracotta' | 'faint';
  className?: string;
};

const TONES = {
  muted: 'text-ink/[0.45]',
  terracotta: 'text-terracotta',
  faint: 'text-ink/40',
};

export default function Eyebrow({
  children,
  tone = 'muted',
  className = '',
}: EyebrowProps) {
  return (
    <span
      className={`text-[10px] desk:text-[11px] tracking-[.2em] uppercase ${TONES[tone]} ${className}`}
    >
      {children}
    </span>
  );
}
