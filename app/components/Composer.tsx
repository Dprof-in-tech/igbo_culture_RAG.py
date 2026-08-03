'use client';

import { useIsDesktop } from '../lib/useIsDesktop';

type ComposerProps = {
  draft: string;
  setDraft: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  busy: boolean;
};

export default function Composer({
  draft,
  setDraft,
  onSubmit,
  busy,
}: ComposerProps) {
  const isDesktop = useIsDesktop();

  return (
    <form
      onSubmit={onSubmit}
      className="border-t border-ink/[0.14] bg-paper flex flex-col gap-3 px-5 pt-[14px] pb-[22px] desk:px-[72px] desk:pt-[22px] desk:pb-[30px]"
    >
      <div className="flex items-center gap-[10px] desk:gap-4">
        <label htmlFor="ajuju" className="sr-only">
          Juo&rsquo;m ajuju &mdash; ask Achalugo a question
        </label>
        <input
          id="ajuju"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={
            isDesktop ? 'Juo’m ajuju — ask me anything' : 'Juo’m ajuju'
          }
          autoComplete="off"
          className="flex-1 min-w-0 bg-transparent border-none outline-none font-serif font-medium text-[18px] desk:text-[24px] desk:py-2"
        />
        <button
          type="submit"
          // Only blocked while a request is in flight — an empty draft is
          // silently ignored by `ask`, and the design has no dimmed Send.
          disabled={busy}
          className="bg-terracotta text-paper border-none cursor-pointer uppercase text-[11px] tracking-[.16em] px-4 py-[11px] min-h-[44px] desk:text-[12px] desk:tracking-[.18em] desk:px-[26px] desk:py-[14px] transition-colors duration-[180ms] ease-[ease] hover:bg-ink focus-visible:bg-ink focus-visible:outline-none disabled:cursor-not-allowed"
        >
          Zịpụ
        </button>
      </div>
      <p className="hidden desk:block m-0 text-[12px] text-ink/40">
        She answers from the Igbo corpus indexed here &mdash; oral tradition,
        proverb collections and published scholarship. Ask in English or Igbo.
      </p>
    </form>
  );
}
