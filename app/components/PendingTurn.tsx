import Diamond from './Diamond';

export default function PendingTurn() {
  return (
    <div className="flex items-center gap-[10px]">
      <span className="hidden desk:block">
        <Diamond pulsing />
      </span>
      <span className="font-serif italic font-medium text-[17px] desk:text-[20px] text-ink/50 animate-breathe desk:animate-none">
        Achalugo is thinking&hellip;
      </span>
    </div>
  );
}
