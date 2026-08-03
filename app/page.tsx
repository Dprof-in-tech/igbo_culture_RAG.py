'use client';

import Composer from './components/Composer';
import MobileHeader from './components/MobileHeader';
import Sidebar from './components/Sidebar';
import Transcript from './components/Transcript';
import { useChat } from './lib/useChat';

export default function Home() {
  const { messages, glossary, draft, setDraft, busy, ask, submit, showStarters } =
    useChat();

  return (
    <main className="h-[100dvh] w-full bg-paper text-ink overflow-hidden grid grid-rows-[auto_1fr] desk:grid-rows-none desk:grid-cols-[344px_1fr]">
      <MobileHeader />
      <Sidebar glossary={glossary} onAsk={ask} busy={busy} />

      <section className="grid grid-rows-[1fr_auto] min-h-0 bg-paper">
        <Transcript
          messages={messages}
          onAsk={ask}
          busy={busy}
          showStarters={showStarters}
        />
        <Composer
          draft={draft}
          setDraft={setDraft}
          onSubmit={submit}
          busy={busy}
        />
      </section>
    </main>
  );
}
