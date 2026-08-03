'use client';

import { useCallback, useMemo, useRef, useState } from 'react';
import axios from 'axios';
import { ERROR_ANSWER, GREETING, HISTORY_TURNS } from './constants';
import type { AnswerPayload, HistoryTurn, Message, Source, Term } from './types';

const asArray = <T,>(value: unknown): T[] => (Array.isArray(value) ? value : []);

/** Coerce whatever the backend sent into the message shape the UI renders. */
function toElderMessage(id: string, data: AnswerPayload): Message {
  return {
    id,
    role: 'elder',
    // Falling back to `text` keeps the old single-string backend renderable.
    answer: data.answer || data.text || '',
    detail: data.detail || '',
    terms: asArray<Term>(data.terms).filter((t) => t?.term),
    sources: asArray<Source>(data.sources).filter((s) => s?.title),
    followups: asArray<string>(data.followups).filter(Boolean).slice(0, 2),
  };
}

function errorMessage(id: string): Message {
  return {
    id,
    role: 'elder',
    answer: ERROR_ANSWER,
    detail: '',
    terms: [],
    sources: [],
    followups: [],
  };
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([GREETING]);
  const [draft, setDraft] = useState('');
  const [busy, setBusy] = useState(false);

  // A counter rather than Date.now() so server and client render the same ids.
  const nextId = useRef(0);
  // Mirrors `busy` for the guard, since state is stale inside a single tick.
  const inFlight = useRef(false);

  const ask = useCallback(
    async (question: string) => {
      const text = question.trim();
      if (!text || inFlight.current) return;

      inFlight.current = true;
      const turn = nextId.current++;
      const userId = `u${turn}`;
      const pendingId = `p${turn}`;

      let history: HistoryTurn[] = [];
      setMessages((prev) => {
        history = prev
          .filter((m) => m.role === 'user' || m.role === 'elder')
          .slice(-HISTORY_TURNS)
          .map((m) => ({
            role: m.role === 'user' ? 'user' : 'assistant',
            content:
              m.role === 'user'
                ? m.text || ''
                : `${m.answer || ''} ${m.detail || ''}`.trim(),
          }));

        return [
          ...prev,
          { id: userId, role: 'user', text, terms: [], sources: [], followups: [] },
          { id: pendingId, role: 'pending', terms: [], sources: [], followups: [] },
        ];
      });
      setDraft('');
      setBusy(true);

      let answer: Message;
      try {
        const res = await axios.post<AnswerPayload>('/api/chat', {
          prompt: text,
          history,
        });
        answer = toElderMessage(pendingId, res.data ?? {});
        if (!answer.answer) answer = errorMessage(pendingId);
      } catch {
        answer = errorMessage(pendingId);
      }

      setMessages((prev) => prev.map((m) => (m.id === pendingId ? answer : m)));
      setBusy(false);
      inFlight.current = false;
    },
    [],
  );

  const submit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      void ask(draft);
    },
    [ask, draft],
  );

  /** Every unique term met this session, deduped case-insensitively, first-seen order. */
  const glossary = useMemo(() => {
    const seen = new Set<string>();
    const entries: Term[] = [];
    for (const message of messages) {
      for (const term of message.terms) {
        const key = term.term.toLowerCase();
        if (!seen.has(key)) {
          seen.add(key);
          entries.push(term);
        }
      }
    }
    return entries;
  }, [messages]);

  return {
    messages,
    glossary,
    draft,
    setDraft,
    busy,
    ask,
    submit,
    /** Starters show on mobile only until the first question is asked. */
    showStarters: messages.length <= 1,
  };
}
