import { PULL_QUOTE } from '../lib/constants';
import type { Term } from '../lib/types';
import Eyebrow from './Eyebrow';
import Glossary from './Glossary';
import StarterQuestions from './StarterQuestions';

type SidebarProps = {
  glossary: Term[];
  onAsk: (question: string) => void;
  busy: boolean;
};

export default function Sidebar({ glossary, onAsk, busy }: SidebarProps) {
  return (
    <aside className="hidden desk:flex flex-col gap-[34px] border-r border-ink/[0.14] px-9 py-10 overflow-y-auto">
      <div className="flex flex-col gap-[14px]">
        <div className="motif-band h-[14px]" aria-hidden="true" />
        <h1 className="m-0 font-serif font-bold text-[40px] leading-[.95] tracking-[.02em]">
          Achalugo
        </h1>
        <p className="m-0 text-[12px] tracking-[.22em] uppercase text-terracotta">
          Onye Amamihe
        </p>
        <p className="m-0 mt-1.5 font-serif italic font-medium text-[18px] leading-[1.45] text-ink/[0.78] text-pretty">
          {PULL_QUOTE}
        </p>
      </div>

      <div className="flex flex-col gap-3">
        <Eyebrow>Juo&rsquo;m ajuju</Eyebrow>
        <StarterQuestions onAsk={onAsk} disabled={busy} />
      </div>

      <Glossary terms={glossary} />
    </aside>
  );
}
