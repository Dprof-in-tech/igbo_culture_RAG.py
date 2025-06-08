"use client";
import {useEffect, useRef, useState} from 'react';
import axios from 'axios';
import update from 'immutability-helper';
import Bubble from './components/Bubble';
import { Plus, SendHorizonalIcon } from 'lucide-react';

export default function Home() {
  const [messages, setMessages] = useState<{ text?: string; isQuestion?: boolean; processing?: boolean; url?: string }[]>([]);

  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e: any) => {
    e.preventDefault();

    if (inputRef.current && inputRef.current.value.trim() !== "") {
      try {
        const question = inputRef.current.value;
        setMessages(prev => [...prev, { text: question, isQuestion: true }]);
        inputRef.current.value = "";
        inputRef.current.focus();
        setMessages(prev => [...prev, { processing: true }]);
        const res = await axios.post(`/api/chat`, {
          prompt: question,
        });
        const reply = res.data;
        setMessages(prev => {
          return update(prev, {
            [prev.length - 1]: {
              text: {$set: reply.text},
              url: {$set: reply.url},
              processing: {$set: false}
            }
          });
        });
      } catch (err) {}
    }
  }

  return (
    <main className="flex h-screen flex-col items-center justify-center px-4 py-4">
  <section className="flex flex-col overflow-y-auto w-full h-full rounded-md p-2 md:p-6">
    {/* Header should scroll along */}
    <div className="flex flex-col items-center w-full h-fit gap-4">
      <h1 className="text-[#A020F0] font-semibold font-serif leading-3 text-[18px]">ACHALUGO</h1>
      <p className="text-white max-w-[85%] md:max-w-1/2 text-center font-serif text-[16px]">
        Hello, I am Achalugo, your closest Igbo elder and onye Amamihe. I am here to help you understand the Igbo culture, tradition, customs and other things pertaining to the Igbo's.
      </p>
      <h3 className="text-[24px] font-semibold mt-4 text-[#A020F0]">JUO'M AJUJU!</h3>
    </div>

    {/* Messages */}
    <div className="relative my-[4rem] md:my-6">
      <div className="w-full">
        {messages.map((message, index) => (
          <Bubble ref={messagesEndRef} key={`message-${index}`} content={message} />
        ))}
      </div>
    </div>

    {/* Input */}
    <form className="flex px-4 py-3 bg-[#0e0e0e] h-fit gap-2 rounded-xl items-center mx-auto absolute bottom-2 w-[93%]" onSubmit={sendMessage}>
      <Plus color="#efefef" opacity={0.5} />
      <input
        ref={inputRef}
        className="chatbot-input flex-1 text-sm md:text-base outline-none bg-transparent rounded-md p-2"
        placeholder="Ask me something..."
      />
      <button type="submit" className="chatbot-send-button flex rounded-md items-center justify-center px-2.5 origin:px-3">
        <SendHorizonalIcon color="#A020F0" fill="#A020F0" />
        <span className="hidden origin:block font-semibold text-sm ml-2">Send</span>
      </button>
    </form>
  </section>
</main>

  )
}