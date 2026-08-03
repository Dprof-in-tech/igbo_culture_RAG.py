import type { Term } from '../lib/types';
import Eyebrow from './Eyebrow';

export default function Glossary({ terms }: { terms: Term[] }) {
  return (
    // flex-none so the block can never collapse to zero on a short viewport.
    <div className="flex flex-col gap-3 flex-none pb-2">
      <Eyebrow>Okwu &mdash; words you met</Eyebrow>
      {terms.length > 0 ? (
        <dl className="flex flex-col gap-[10px] m-0">
          {terms.map((entry) => (
            <div
              key={entry.term.toLowerCase()}
              className="border-l-2 border-saffron pl-[10px]"
            >
              <dt className="font-serif font-medium text-[17px]">{entry.term}</dt>
              <dd className="m-0 mt-0.5 text-[13px] leading-[1.4] text-ink/60">
                {entry.meaning}
              </dd>
            </div>
          ))}
        </dl>
      ) : (
        <p className="m-0 text-[13px] leading-[1.5] text-ink/[0.45]">
          Igbo words from her answers gather here.
        </p>
      )}
    </div>
  );
}
