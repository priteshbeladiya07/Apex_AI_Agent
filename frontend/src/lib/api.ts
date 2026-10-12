import type { ChatMessage, Conversation, ToolServer } from '../types';

const BASE = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
).replace(/\/$/, '');

export const DEMO = import.meta.env.VITE_DEMO_MODE !== 'false';

type ApiConversation = {
  id: number;
  title: string;
  updated_at: string;
};

type ApiMessage = {
  id: number;
  role: string;
  content: string;
  created_at: string;
};

type ApiChatResponse = {
  conversation_id: number;
  reply: string;
};

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  });

  if (!response.ok) {
    const responseText = await response.text();
    let detail = responseText || response.statusText;
    try {
      const body: unknown = JSON.parse(responseText);
      if (
        typeof body === 'object' &&
        body !== null &&
        'detail' in body &&
        typeof body.detail === 'string'
      ) {
        detail = body.detail;
      }
    } catch {}
    throw new Error(`API error ${response.status}: ${detail}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

function mapConversation(conversation: ApiConversation): Conversation {
  return {
    id: String(conversation.id),
    title: conversation.title,
    updatedAt: conversation.updated_at,
  };
}

function mapMessages(messages: ApiMessage[]): ChatMessage[] {
  return messages
    .filter(
      (message): message is ApiMessage & { role: 'user' | 'assistant' } =>
        message.role === 'user' || message.role === 'assistant',
    )
    .map(message => ({
      id: String(message.id),
      role: message.role,
      content: message.content,
      createdAt: message.created_at,
    }));
}

export async function getConversations(): Promise<Conversation[]> {
  if (DEMO) {
    return JSON.parse(
      localStorage.getItem('apex-conversations') || '[]',
    ) as Conversation[];
  }
  const conversations = await request<ApiConversation[]>('/conversations/');
  return conversations.map(mapConversation);
}

export async function getMessages(id: string): Promise<ChatMessage[]> {
  if (DEMO) {
    return JSON.parse(
      localStorage.getItem(`apex-messages-${id}`) || '[]',
    ) as ChatMessage[];
  }
  const history = await request<{ messages: ApiMessage[] }>(
    `/chat/${encodeURIComponent(id)}/history`,
  );
  return mapMessages(history.messages);
}

export async function sendMessage(
  message: string,
  conversationId: string | null,
): Promise<{
  conversationId: string;
  userMessage: ChatMessage;
  assistantMessage: ChatMessage;
}> {
  if (DEMO) {
    await new Promise(resolve => setTimeout(resolve, 650));
    const id = conversationId || crypto.randomUUID();
    const now = new Date().toISOString();
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: message,
      createdAt: now,
    };
    const assistantMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: `I can help with that. This is a demo response because the backend is not connected yet. Once connected, Apex AI will send your message to LangGraph, which can choose from the MCP tools enabled on your backend.\n\nYour question: ${message}`,
      createdAt: now,
    };
    const all = await getMessages(id);
    localStorage.setItem(
      `apex-messages-${id}`,
      JSON.stringify([...all, userMessage, assistantMessage]),
    );
    const conversations = await getConversations();
    const title = message.trim().slice(0, 45) || 'New chat';
    localStorage.setItem(
      'apex-conversations',
      JSON.stringify([
        { id, title, updatedAt: now },
        ...conversations.filter(conversation => conversation.id !== id),
      ]),
    );
    return { conversationId: id, userMessage, assistantMessage };
  }

  const response = await request<ApiChatResponse>('/chat/', {
    method: 'POST',
    body: JSON.stringify({
      message,
      conversation_id: conversationId ? Number(conversationId) : null,
    }),
  });
  const now = new Date().toISOString();
  const id = String(response.conversation_id);

  return {
    conversationId: id,
    userMessage: {
      id: crypto.randomUUID(),
      role: 'user',
      content: message,
      createdAt: now,
    },
    assistantMessage: {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: response.reply,
      createdAt: now,
    },
  };
}

export async function deleteConversation(id: string): Promise<void> {
  if (DEMO) {
    localStorage.removeItem(`apex-messages-${id}`);
    localStorage.setItem(
      'apex-conversations',
      JSON.stringify(
        (await getConversations()).filter(
          conversation => conversation.id !== id,
        ),
      ),
    );
    return;
  }
  await request<void>(`/conversations/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });
}

export async function getToolServers(): Promise<ToolServer[]> {
  if (DEMO) {
    return [
      {
        id: 'expense',
        name: 'Expense Tracker',
        description: 'Example MCP server',
        enabled: true,
      },
      {
        id: 'search',
        name: 'Web Search',
        description: 'Example MCP server',
        enabled: true,
      },
      {
        id: 'manim',
        name: 'Manim',
        description: 'Example MCP server',
        enabled: false,
      },
    ];
  }
  return request<ToolServer[]>('/mcp/servers');
}
