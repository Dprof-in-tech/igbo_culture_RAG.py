import type { Message } from './types';

export const PULL_QUOTE =
  '“Hello, I am Achalugo, your closest Igbo elder and onye Amamihe. I am here to help you understand the Igbo culture, tradition, customs and other things pertaining to the Igbo’s.”';

/**
 * Placeholders chosen to show the shape of the feature. Swap these for
 * questions the index answers well once the corpus settles.
 */
export const STARTERS = [
  'Gịnị bụ Igba Nkwu? Explain the wine carrying ceremony',
  'Why do we break kola nut, and who may break it?',
  'What is Chi, and does everyone have one?',
  'How are Igbo names chosen?',
];

/** Seeded so the glossary is never empty on arrival. */
export const GREETING: Message = {
  id: 'greeting',
  role: 'elder',
  answer:
    'Nno, nwa m. I am Achalugo, your closest Igbo elder and onye Amamihe.',
  detail:
    "I am here to help you understand Igbo culture, tradition, customs and other things pertaining to the Igbo's. Juo'm ajuju — ask me your question, and I will answer as I would at my own fireside.",
  terms: [
    { term: 'Onye Amamihe', meaning: 'person of wisdom' },
    { term: 'Juo’m ajuju', meaning: 'ask me a question' },
  ],
  sources: [],
  followups: [],
};

/**
 * Failures stay in character. A red alert would break the voice, so there is
 * deliberately no error chrome and no retry button.
 */
export const ERROR_ANSWER =
  'Forgive me, nwa m — my voice did not carry just then. Juo’m ajuju ọzọ, ask me again.';

/** Turns of context sent alongside each new question. */
export const HISTORY_TURNS = 6;
