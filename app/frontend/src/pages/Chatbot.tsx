import { useState, useRef, useEffect } from 'react';
import { api } from '../api';

interface Message {
  role: 'user' | 'bot';
  text: string;
  source?: string;
}

const SUGGESTIONS = [
  'Quel est le meilleur arrondissement ?',
  'Top 5 arrondissements',
  'Compare le 11e et le 15e',
  'Explique le score du 18e',
  'Résumé général',
];

export default function Chatbot() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', text: 'Bienvenue. Je suis l\'assistant analytique Parkshare.\n\nPosez-moi des questions sur le potentiel commercial des arrondissements de Paris.\n\nExemples :\n  Quel est le meilleur arrondissement ?\n  Compare le 11e et le 15e\n  Explique le score du 18e' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiMode, setAiMode] = useState<string | null>(null);
  const messagesEnd = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async (text?: string) => {
    const query = text || input.trim();
    if (!query || loading) return;
    
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: query }]);
    setLoading(true);
    
    try {
      const res = await api.chatbot(query);
      setAiMode(res.source);
      setMessages(prev => [...prev, { role: 'bot', text: res.response, source: res.source }]);
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: 'Erreur de communication avec le serveur.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Assistant analytique</h2>
        <p>Posez des questions sur le potentiel Parkshare à Paris</p>
      </div>

      <div className="chatbot-panel">
        <div className="chatbot-header">
          Assistant Parkshare <span style={{ fontSize: 10, color: aiMode === 'llm' ? 'var(--primary)' : 'var(--text-disabled)', marginLeft: 8, fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.04em' }}>{aiMode === 'llm' ? 'IA' : 'rule-based'}</span>
        </div>

        <div className="chatbot-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-msg ${msg.role === 'user' ? 'user' : 'bot'}`}>
              {msg.text}
            </div>
          ))}
          {loading && (
            <div className="chat-msg bot" style={{ opacity: 0.6 }}>
              <div className="spinner" />
            </div>
          )}
          <div ref={messagesEnd} />
        </div>

        <div style={{ padding: '8px 16px', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              className="suggestion-chip"
              onClick={() => send(s)}
            >
              {s}
            </button>
          ))}
        </div>

        <div className="chatbot-input">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && send()}
            placeholder="Posez votre question..."
            disabled={loading}
          />
          <button onClick={() => send()} disabled={loading}>
            Envoyer
          </button>
        </div>
      </div>
    </div>
  );
}
