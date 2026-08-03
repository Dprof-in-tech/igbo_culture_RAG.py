import type { Message, Source, Term } from '../lib/types';
import Diamond from './Diamond';
import Eyebrow from './Eyebrow';

/**
 * Terms are a wrapping row of saffron chips on desktop and a stacked
 * saffron-ruled list on mobile — same data, two treatments.
 */
function Terms({ terms }: { terms: Term[] }) {
  return (
    <div className="flex flex-col gap-1.5 desk:flex-row desk:flex-wrap desk:gap-2 desk:pt-1">
      {terms.map((entry) => (
        <span
          key={entry.term.toLowerCase()}
          title={entry.meaning}
          // pl/pr are set separately on desktop: a `desk:px-*` would lose to
          // the mobile `pl-2` in Tailwind's rule order and zero the left inset.
          className="border-l-2 border-saffron pl-2 text-[13px] leading-[1.45] text-ink/[0.65] desk:border-l-0 desk:border-b desk:inline-flex desk:items-baseline desk:gap-2 desk:bg-saffron/[0.16] desk:pl-[10px] desk:pr-[10px] desk:py-1.5 desk:leading-normal desk:text-ink/[0.62] desk:cursor-help"
        >
          <b className="font-serif font-medium text-[15px] text-ink">
            {entry.term}
          </b>
          <span className="desk:hidden">&nbsp;&mdash;&nbsp;</span>
          <span>{entry.meaning}</span>
        </span>
      ))}
    </div>
  );
}

function Sources({ sources }: { sources: Source[] }) {
  return (
    <div className="flex flex-col gap-1.5 desk:gap-2 border-t border-ink/[0.14] pt-3 desk:pt-4">
      <Eyebrow>
        Ebe o si<span className="hidden desk:inline"> &mdash; where this comes from</span>
      </Eyebrow>
      {sources.map((source, i) => (
        <p
          key={`${source.title}-${i}`}
          className="m-0 text-[12px] leading-[1.45] text-ink/60 desk:text-[13px] desk:leading-[1.5] desk:text-ink/[0.62]"
        >
          {source.url ? (
            <a
              href={source.url}
              target="_blank"
              rel="noreferrer noopener"
              className="font-medium"
            >
              {source.title}
            </a>
          ) : (
            <b className="font-medium text-ink">{source.title}</b>
          )}
          {source.note ? <>&nbsp; {source.note}</> : null}
        </p>
      ))}
    </div>
  );
}

function Followups({
  followups,
  onAsk,
  disabled,
}: {
  followups: string[];
  onAsk: (q: string) => void;
  disabled: boolean;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {followups.map((question) => (
        <button
          key={question}
          type="button"
          disabled={disabled}
          onClick={() => onAsk(question)}
          className="bg-transparent border border-ink/20 rounded-full px-[14px] py-2 text-[13px] cursor-pointer transition-all duration-[180ms] ease-[ease] hover:bg-ink hover:text-paper hover:border-ink focus-visible:bg-ink focus-visible:text-paper focus-visible:border-ink focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        >
          {question} &rarr;
        </button>
      ))}
    </div>
  );
}

type ElderTurnProps = {
  message: Message;
  onAsk: (question: string) => void;
  busy: boolean;
};

export default function ElderTurn({ message, onAsk, busy }: ElderTurnProps) {
  return (
    <div className="flex flex-col gap-[14px] desk:gap-[18px]">
      <div className="hidden desk:flex items-center gap-[10px]">
        <Diamond />
        <Eyebrow tone="terracotta">Achalugo</Eyebrow>
      </div>

      <p className="m-0 font-serif font-medium text-[21px] leading-[1.4] desk:text-[27px] desk:leading-[1.42] text-pretty">
        {message.answer}
      </p>

      {message.detail ? (
        <p className="m-0 text-[15px] leading-[1.65] text-ink/[0.78] desk:text-[16px] desk:leading-[1.72] desk:text-ink/80 max-w-[60ch] text-pretty">
          {message.detail}
        </p>
      ) : null}

      {message.terms.length > 0 ? <Terms terms={message.terms} /> : null}
      {message.sources.length > 0 ? <Sources sources={message.sources} /> : null}
      {message.followups.length > 0 ? (
        <Followups followups={message.followups} onAsk={onAsk} disabled={busy} />
      ) : null}
    </div>
  );
}
