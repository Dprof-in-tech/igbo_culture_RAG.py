<p align="center">
  <a href="https://your-website-link.com">
    <img src="https://assets.vercel.com/image/upload/v1588805858/repositories/vercel/logo.png" height="96">
    <h3 align="center">Achalugo AI – Your Igbo Cultural Companion</h3>
  </a>
</p>

<p align="center">A warm, intelligent Igbo elder—powered by Next.js and Flask—ready to answer your questions about Igbo language, tradition, proverbs, and more.</p>

<br/>

## 🧕🏾 Introduction

**Achalugo AI** is a hybrid Next.js + Python app designed to feel like a wise, friendly Igbo woman—your personal cultural guide. It uses **Next.js** for the frontend and **Flask** for the API backend. Perfect for conversational apps enriched with Python-based AI logic and deep cultural knowledge.

## 🛠️ How It Works

The Flask API (running Python magic behind the scenes) is accessed via `/api/`, powered by `next.config.js` rewrites. During development, all `/api/:path*` calls are redirected to the Flask server on `localhost:5328`.

In production (on Vercel), the Flask backend is deployed using **Python serverless functions**.

This allows Achalugo to respond gracefully with real-time wisdom, drawing from both static context and Python-powered reasoning.

## 🌍 Demo

Live: [https://your-website-link.com](https://your-website-link.com)

## 🚀 Deploy Your Own Achalugo

Want your own digital elder? Click below to clone & deploy with Vercel:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?demo-title=Achalugo%20AI&demo-description=A%20Next.js%20+%20Flask%20AI%20chatbot%20for%20understanding%20Igbo%20culture%20and%20tradition.&demo-url=https%3A%2F%2Fyour-website-link.com&project-name=achalugo-ai&repository-name=achalugo-ai&repository-url=https%3A%2F%2Fgithub.com%2Fyourusername%2Fachalugo-ai)

## 🧑🏽‍💻 Developing Locally

```bash
npx create-next-app achalugo-ai --example "https://github.com/vercel/examples/tree/main/python/nextjs-flask"
```

Then install dependencies:

```bash
npm install
# or
yarn
# or
pnpm install
```

Start the development servers:

```bash
npm run dev
# Flask runs on 127.0.0.1:5328
# Next.js runs on localhost:3000
```

Make sure both frontend and Flask API are running for full functionality.

## 📚 Learn More

* [Next.js Documentation](https://nextjs.org/docs)
* [Flask Documentation](https://flask.palletsprojects.com/)
* [Vercel Python Serverless Functions](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
