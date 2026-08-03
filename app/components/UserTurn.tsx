import Eyebrow from './Eyebrow';

export default function UserTurn({ text }: { text: string }) {
  return (
    <div className="flex flex-col gap-1.5 items-end text-right">
      <Eyebrow tone="faint" className="hidden desk:inline">
        Gị
      </Eyebrow>
      <p className="m-0 font-serif font-medium text-[20px] leading-[1.35] text-ink/[0.85] desk:text-[26px] desk:leading-[1.3] desk:text-ink text-pretty">
        {text}
      </p>
    </div>
  );
}
