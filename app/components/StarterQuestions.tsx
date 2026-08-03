import { STARTERS } from '../lib/constants';

type StarterQuestionsProps = {
  onAsk: (question: string) => void;
  disabled?: boolean;
  /** Mobile starters sit in the transcript and use tighter padding. */
  compact?: boolean;
};

export default function StarterQuestions({
  onAsk,
  disabled,
  compact,
}: StarterQuestionsProps) {
  return (
    <div className="flex flex-col gap-2">
      {STARTERS.map((question) => (
        <button
          key={question}
          type="button"
          disabled={disabled}
          onClick={() => onAsk(question)}
          className={`text-left bg-transparent border border-ink/[0.16] text-[14px] leading-[1.35] cursor-pointer transition-all duration-[180ms] ease-[ease] hover:bg-ink hover:text-paper hover:border-ink focus-visible:bg-ink focus-visible:text-paper focus-visible:border-ink focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 ${
            compact ? 'px-[13px] py-[11px]' : 'px-[14px] py-3'
          }`}
        >
          {question}
        </button>
      ))}
    </div>
  );
}
