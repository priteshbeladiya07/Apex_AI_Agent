import { useEffect, useState } from 'react';
import {
  ChevronDown,
  Command,
  Menu,
  Plus,
  Sparkles,
} from 'lucide-react';
import Sidebar from './components/Sidebar';
import ChatMessage from './components/ChatMessage';
import ChatComposer from './components/ChatComposer';
import IntegrationsPanel from './components/IntegrationsPanel';
import SettingsPanel from './components/SettingsPanel';
import {
  deleteConversation,
  getConversations,
  getMessages,
  sendMessage,
  DEMO,
} from './lib/api';
import type { ChatMessage as Message, Conversation } from './types';

const suggestions = [
  {
    icon: '✳',
    title: 'Explain a complex topic',
    text: 'Explain quantum computing in simple terms',
  },
  {
    icon: '⌘',
    title: 'Help me write code',
    text: 'Help me write a Python function to sort a list',
  },
  {
    icon: '⌕',
    title: 'Research something',
    text: 'Give me a balanced overview of renewable energy',
  },
  {
    icon: '↗',
    title: 'Think through an idea',
    text: 'Help me plan a personal learning schedule',
  },
];

function errorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback;
}

export default function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [panel, setPanel] = useState<'integrations' | 'settings' | null>(null);
  const [error, setError] = useState('');

  async function refreshConversations() {
    try {
      setConversations(await getConversations());
    } catch (cause) {
      setError(
        errorMessage(
          cause,
          'Could not load conversation history. Check the backend connection.',
        ),
      );
    }
  }

  useEffect(() => {
    void refreshConversations();
  }, []);

  async function selectConversation(id: string) {
    setActiveId(id);
    setError('');
    try {
      setMessages(await getMessages(id));
    } catch (cause) {
      setMessages([]);
      setError(errorMessage(cause, 'Could not load this conversation.'));
    }
    setMobileOpen(false);
  }

  function newChat() {
    setActiveId(null);
    setMessages([]);
    setError('');
    setMobileOpen(false);
  }

  async function removeConversation(id: string) {
    try {
      await deleteConversation(id);
      if (activeId === id) newChat();
      await refreshConversations();
    } catch (cause) {
      setError(errorMessage(cause, 'Could not delete this conversation.'));
    }
  }

  async function send(content: string) {
    setError('');
    setLoading(true);
    const localUser: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    };
    setMessages(current => [...current, localUser]);

    try {
      const result = await sendMessage(content, activeId);
      setActiveId(result.conversationId);
      setMessages(current => [
        ...current.filter(message => message.id !== localUser.id),
        result.userMessage,
        result.assistantMessage,
      ]);
      await refreshConversations();
    } catch (cause) {
      setMessages(current =>
        current.filter(message => message.id !== localUser.id),
      );
      setError(
        errorMessage(
          cause,
          'Unable to contact Apex AI backend. Check the server and API URL.',
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  const showWelcome = messages.length === 0;

  return (
    <div className="app">
      <div
        className={`mobile-shade ${mobileOpen ? 'visible' : ''}`}
        onClick={() => setMobileOpen(false)}
      />
      <div className={mobileOpen ? 'mobile-sidebar visible' : 'mobile-sidebar'}>
        <Sidebar
          conversations={conversations}
          activeId={activeId}
          onNew={newChat}
          onSelect={selectConversation}
          onDelete={removeConversation}
          onIntegrations={() => setPanel('integrations')}
          onSettings={() => setPanel('settings')}
          collapsed={false}
          onToggle={() => setMobileOpen(false)}
        />
      </div>
      <div className="desktop-sidebar">
        <Sidebar
          conversations={conversations}
          activeId={activeId}
          onNew={newChat}
          onSelect={selectConversation}
          onDelete={removeConversation}
          onIntegrations={() => setPanel('integrations')}
          onSettings={() => setPanel('settings')}
          collapsed={collapsed}
          onToggle={() => setCollapsed(!collapsed)}
        />
      </div>
      <main className="main">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="mobile-menu ghost"
              onClick={() => setMobileOpen(true)}
            >
              <Menu size={19} />
            </button>
            <div className="model-select">
              <span className="model-mark">
                <Sparkles size={15} />
              </span>
              <strong>Apex AI</strong>
              <span className="model-version">Assistant</span>
              <ChevronDown size={14} />
            </div>
          </div>
          <div className="topbar-right">
            <span className="connection-pill">
              <i />
              {DEMO ? 'DEMO MODE' : 'API MODE'}
            </span>
            <button className="top-new-chat" onClick={newChat}>
              <Plus size={15} />
              <span>New chat</span>
            </button>
          </div>
        </header>
        <section className={`chat-area ${showWelcome ? 'welcome-mode' : ''}`}>
          {showWelcome ? (
            <div className="welcome">
              <div className="welcome-orb">
                <div>
                  <Sparkles size={30} />
                </div>
              </div>
              <p className="welcome-kicker">YOUR SPACE TO THINK</p>
              <h1>What can I help with?</h1>
              <p className="welcome-subtitle">
                Ask anything. Explore ideas. Get things done.
              </p>
              <div className="suggestions">
                {suggestions.map(suggestion => (
                  <button
                    key={suggestion.title}
                    className="suggestion"
                    onClick={() => void send(suggestion.text)}
                  >
                    <span className="suggestion-icon">{suggestion.icon}</span>
                    <span>
                      <strong>{suggestion.title}</strong>
                      <small>{suggestion.text}</small>
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map(message => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {loading && (
                <div className="thinking">
                  <span />
                  <span />
                  <span />
                  Apex is thinking…
                </div>
              )}
            </div>
          )}
          {error && <div className="error-message">{error}</div>}
          <ChatComposer onSend={send} disabled={loading} />
        </section>
        <footer className="main-footer">
          <span>
            <Command size={12} /> Apex AI
          </span>
          <span>General-purpose assistant · Extensible with MCP</span>
        </footer>
      </main>
      {panel === 'integrations' && (
        <IntegrationsPanel onClose={() => setPanel(null)} />
      )}
      {panel === 'settings' && <SettingsPanel onClose={() => setPanel(null)} />}
    </div>
  );
}
