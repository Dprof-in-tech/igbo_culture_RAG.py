'use client';

import { useEffect, useRef } from 'react';
import type { Message } from '../lib/types';
import ElderTurn from './ElderTurn';
import PendingTurn from './PendingTurn';
import StarterQuestions from './StarterQuestions';
import UserTurn from './UserTurn';

type TranscriptProps = {
  messages: Message[];
  onAsk: (question: string) => void;
  busy: boolean;
  showStarters: boolean;
};

export default function Transcript({
  messages,
  onAsk,
  busy,
  showStarters,
}: TranscriptProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const frame = requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
    });
    return () => cancelAnimationFrame(frame);
  }, [messages]);

  return (
    <div
      ref={scrollRef}
      aria-live="polite"
      aria-busy={busy}
      className="overflow-auto flex flex-col gap-7 px-5 py-[22px] desk:gap-10 desk:px-[72px] desk:pt-12 desk:pb-8"
    >
      {messages.map((message) => (
        <div key={message.id} className="max-w-[720px] w-full animate-rise">
          {message.role === 'user' ? <UserTurn text={message.text || ''} /> : null}
          {message.role === 'elder' ? (
            <ElderTurn message={message} onAsk={onAsk} busy={busy} />
          ) : null}
          {message.role === 'pending' ? <PendingTurn /> : null}
        </div>
      ))}

      {/* Mobile only: starters live in the sidebar on desktop. */}
      {showStarters ? (
        <div className="desk:hidden">
          <StarterQuestions onAsk={onAsk} disabled={busy} compact />
        </div>
      ) : null}
    </div>
  );
}
