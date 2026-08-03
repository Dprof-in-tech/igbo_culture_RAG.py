/** An Igbo word or phrase used in an answer, with its English gloss. */
export type Term = {
  term: string;
  meaning: string;
};

/** A document the answer actually drew on, from the retrieval index. */
export type Source = {
  title: string;
  note?: string;
  url?: string;
};

export type Role = 'user' | 'elder' | 'pending';

export type Message = {
  id: string;
  role: Role;
  /** User turns only. */
  text?: string;
  /** Elder turns only. */
  answer?: string;
  detail?: string;
  terms: Term[];
  sources: Source[];
  followups: string[];
};

/** The answer object `/api/chat` returns for one turn. */
export type AnswerPayload = {
  answer?: string;
  detail?: string;
  terms?: Term[];
  sources?: Source[];
  followups?: string[];
  /** Legacy single-string shape from the previous backend. */
  text?: string;
};

export type HistoryTurn = {
  role: 'user' | 'assistant';
  content: string;
};
