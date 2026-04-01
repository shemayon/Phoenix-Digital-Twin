'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import type { ChatMessage } from '@/lib/types';
import { sendChat } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Send, Cpu, User, Loader2 } from 'lucide-react';

const WELCOME: ChatMessage = {
  id: 'welcome',
  role: 'assistant',
  content: 'Hi! I\'m Phoenix AI. System status: Ready. How can I assist with your asset monitoring today?',
};

export default function ChatBot({ selectedAsset }: { selectedAsset?: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    const q = input.trim();
    if (!q || busy) return;

    const userMsg: ChatMessage = { id: `u-${Date.now()}`, role: 'user', content: q };
    setMessages(m => [...m, userMsg]);
    setInput('');
    setBusy(true);

    try {
      const { reply } = await sendChat(q, selectedAsset);
      setMessages(m => [...m, { id: `a-${Date.now()}`, role: 'assistant', content: reply }]);
    } catch {
      setMessages(m => [
        ...m,
        { id: `e-${Date.now()}`, role: 'assistant', content: '🚨 AI core offline. Connection to Phoenix model failed.' },
      ]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex flex-col h-full min-h-0 bg-slate-900/60 rounded-2xl border border-slate-800/80 p-5 shadow-inner">
      <div className="flex items-center gap-2 mb-4">
        <div className="p-2 rounded-xl bg-violet-500/10 border border-violet-500/20 text-violet-400">
          <MessageSquare className="w-4 h-4" />
        </div>
        <div className="flex-1">
          <h2 className="text-xs font-black text-slate-200 uppercase tracking-widest">
            Neural Uplink
          </h2>
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-tighter">
            Phoenix Agent <span className="text-violet-500/60 ml-1">Connected</span>
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pr-2 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
        <AnimatePresence initial={false}>
          {messages.map(msg => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} gap-1.5`}
            >
              <div className={`flex items-center gap-1.5 px-1 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`p-1 rounded-md ${msg.role === 'user' ? 'bg-violet-500/20 text-violet-400' : 'bg-teal-500/20 text-teal-400'}`}>
                  {msg.role === 'user' ? <User className="w-2.5 h-2.5" /> : <Cpu className="w-2.5 h-2.5" />}
                </div>
                <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest">
                  {msg.role === 'user' ? 'Operator' : 'Phoenix'}
                </span>
              </div>
              <div
                className={`max-w-[90%] rounded-2xl px-4 py-3 text-xs leading-relaxed transition-all duration-300 ${
                  msg.role === 'user'
                    ? 'bg-violet-600/20 border border-violet-500/30 text-violet-100 rounded-tr-none'
                    : 'bg-slate-800/80 border border-slate-700 text-teal-50 shadow-sm rounded-tl-none'
                }`}
              >
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {busy && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-start gap-1.5"
          >
            <div className="flex items-center gap-1.5 px-1">
              <div className="p-1 rounded-md bg-teal-500/20 text-teal-400">
                <Cpu className="w-2.5 h-2.5" />
              </div>
              <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest">Phoenix</span>
            </div>
            <div className="bg-slate-800/80 border border-slate-700 rounded-2xl rounded-tl-none px-4 py-3">
              <Loader2 className="w-4 h-4 text-teal-500 animate-spin" />
            </div>
          </motion.div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} className="relative mt-5">
        <input
          id="chat-input"
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Enter command or query..."
          disabled={busy}
          className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-4 pr-12 py-3 text-xs text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-teal-500/30 focus:border-teal-500/50 transition-all shadow-lg"
        />
        <button
          id="chat-send-btn"
          type="submit"
          disabled={busy || !input.trim()}
          className="absolute right-2 top-2 p-2 rounded-lg bg-teal-500/10 text-teal-400 hover:bg-teal-500/20 hover:text-teal-300 disabled:opacity-30 disabled:hover:bg-transparent transition-all"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
      
      <p className="text-[9px] text-slate-600 font-bold uppercase text-center mt-3 tracking-tighter opacity-70">
        End-to-End Encrypted Neural Link
      </p>
    </div>
  );
}
