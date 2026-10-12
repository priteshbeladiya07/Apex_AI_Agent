import {
  Check,
  ChevronRight,
  Plug,
  Plus,
  Server,
  Settings2,
  X,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { getToolServers } from '../lib/api';
import type { ToolServer } from '../types';

export default function IntegrationsPanel({
  onClose,
}: {
  onClose: () => void;
}) {
  const [servers, setServers] = useState<ToolServer[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    getToolServers()
      .then(result => {
        if (active) setServers(result);
      })
      .catch(cause => {
        if (active) {
          setError(
            cause instanceof Error
              ? cause.message
              : 'Could not load MCP integrations.',
          );
        }
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <div
      className="overlay"
      onMouseDown={event => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section className="integration-drawer">
        <div className="drawer-header">
          <div className="drawer-icon">
            <Plug size={20} />
          </div>
          <div>
            <h2>MCP integrations</h2>
            <p>Manage the tools available to Apex AI.</p>
          </div>
          <button className="ghost" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>
        <div className="integration-note">
          <Server size={17} />
          <span>
            Connect and configure MCP servers in your backend. The model can
            use enabled tools without adding app-specific buttons to the chat.
          </span>
        </div>
        {error && <div className="error-message">{error}</div>}
        <div className="server-list">
          {servers.map(server => (
            <div className="server-row" key={server.id}>
              <div className="server-symbol">
                <Plug size={18} />
              </div>
              <div className="server-info">
                <strong>{server.name}</strong>
                <span>{server.description}</span>
              </div>
              <span
                className={`server-status ${server.enabled ? 'enabled' : ''}`}
              >
                {server.enabled && <Check size={12} />}{' '}
                {server.enabled ? 'Enabled' : 'Disabled'}
              </span>
              <button
                className="ghost"
                title="Server configuration"
                aria-label={`${server.name} configuration`}
              >
                <Settings2 size={16} />
              </button>
            </div>
          ))}
        </div>
        <button
          className="add-server"
          onClick={() =>
            window.alert(
              'Add the MCP server in your backend configuration, then expose it through the integrations API.',
            )
          }
        >
          <Plus size={17} />
          Add MCP server
          <ChevronRight size={16} />
        </button>
        <p className="drawer-footnote">
          For security, MCP URLs, tokens, and server credentials should be
          managed on the backend, not stored in browser code.
        </p>
      </section>
    </div>
  );
}
