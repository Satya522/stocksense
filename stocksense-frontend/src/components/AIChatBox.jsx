import { useState, useRef, useEffect } from 'react';
import { Send, Bot, Sparkles, Lightbulb } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../lib/api';

const suggestions = [
  'Lowest stock items',
  'Total stock value',
  'Items needing reorder',
  'Out of stock items',
  'Warehouse summary',
  'Recent movements',
];

function formatMessage(text) {
  if (!text) return null;
  const lines = text.split('\n');
  return lines.map((line, idx) => {
    const parts = line.split(/(\*\*.*?\*\*|\*.*?\*)/g);
    const formattedParts = parts.map((part, pIdx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={pIdx} className="font-semibold text-white">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*')) {
        return <em key={pIdx} className="text-white/70 italic">{part.slice(1, -1)}</em>;
      }
      return part;
    });

    return (
      <div key={idx} className={line.startsWith('•') || line.startsWith('-') ? 'pl-2 py-0.5' : 'py-0.5'}>
        {formattedParts}
      </div>
    );
  });
}

export default function AIChatBox() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Namaste! 🙏 Main tumhara stock assistant hoon.\n\nMujhse apne warehouse ke baare mein kuch bhi poocho — Hindi ya English mein. Neeche kuch suggestions hain shuru karne ke liye:' },
    { role: 'user', content: 'Total stock value' },
    { role: 'ai', content: '📊 **Enterprise Stock Summary**:\n\n• **Total Valuation**: ₹149,035.7 Cr\n• **Active Catalog Items**: 427 unique products\n• **Total Units in Circulation**: 2,497,813 units across all warehouses\n\n💡 *All figures verified against live MariaDB tabBin ledger.*' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async (text) => {
    const question = (text || input).trim();
    if (!question) return;
    
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setInput('');
    setIsLoading(true);

    try {
      const data = await api.ask(question);
      setMessages(prev => [...prev, { role: 'ai', content: data.answer || data.error }]);
    } catch {
      setMessages(prev => [...prev, { role: 'ai', content: '⚠️ Server se connect nahi ho paya.\n\nPlease make sure ai_query_api.py chal raha hai:\ncd python && venv\\Scripts\\activate && python src/ai_query_api.py' }]);
    }
    setIsLoading(false);
    inputRef.current?.focus();
  };

  return (
    <div className="glass-panel flex flex-col h-[calc(100vh-6rem)] relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-60 h-60 bg-purple-500/5 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-60 h-60 bg-accent/5 rounded-full blur-[100px] pointer-events-none" />

      {/* Header */}
      <div className="p-6 border-b border-border flex items-center gap-4 bg-panel/40 backdrop-blur-xl relative z-10">
        <div className="relative">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-xl shadow-purple-500/20">
            <Bot className="text-white" size={22} />
          </div>
          <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-emerald-400 rounded-full border-2 border-panel shadow-[0_0_6px_rgba(16,185,129,0.6)]" />
        </div>
        <div>
          <h2 className="text-lg font-bold tracking-tight">StockSense AI</h2>
          <p className="text-xs text-emerald-400 flex items-center gap-1 font-medium">
            <Sparkles size={12} /> Online — Ready to help
          </p>
        </div>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-5 relative z-10">
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div 
              key={i}
              initial={false}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-[85%] p-4 text-sm leading-relaxed ${
                  msg.role === 'user' 
                    ? 'bg-gradient-to-r from-accent to-blue-600 text-white rounded-2xl rounded-br-md shadow-lg shadow-accent/10 font-medium' 
                    : 'bg-[#121624] border border-white/[0.1] text-white/90 rounded-2xl rounded-bl-md shadow-md'
                }`}
              >
                {msg.role === 'user' ? msg.content : formatMessage(msg.content)}
              </div>
            </motion.div>
          ))}
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
              <div className="bg-white/[0.04] border border-white/[0.08] py-4 px-5 rounded-2xl rounded-bl-md flex gap-1.5 items-center">
                <span className="w-2 h-2 bg-accent rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.15s' }} />
                <span className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.3s' }} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />

        {/* Suggestion chips */}
        {messages.length <= 3 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => handleSend(s)}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-white/[0.06] border border-white/[0.12] text-xs font-medium text-white/80 hover:text-white hover:border-accent hover:bg-accent/10 transition-all cursor-pointer shadow-sm"
              >
                <Lightbulb size={12} className="text-amber-400" />
                {s}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-5 border-t border-border bg-panel/30 backdrop-blur-xl relative z-10">
        <div className="relative flex items-center">
          <input 
            ref={inputRef}
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Apna sawal poocho..."
            className="w-full bg-black/30 border border-white/[0.08] text-white placeholder-muted/60 py-4 pl-6 pr-16 rounded-2xl focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent/30 transition-all text-sm shadow-inner"
          />
          <button 
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
            className="absolute right-2 p-3 bg-accent hover:bg-blue-600 disabled:opacity-40 text-white rounded-xl transition-all flex items-center justify-center shadow-lg shadow-accent/20 disabled:shadow-none"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
