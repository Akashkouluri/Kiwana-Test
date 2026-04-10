export interface ChatResponse {
  reply: string;
  path: string;
}

export const registerUser = async (userId: string, name: string, email: string, phone: string): Promise<boolean> => {
  const res = await fetch('/api/users/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, name, email, phone }),
  });
  if (!res.ok) throw new Error('Failed to register user');
  return true;
};

export const createSession = async (userId: string): Promise<string> => {
  const res = await fetch('/api/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId }),
  });
  if (!res.ok) throw new Error('Failed to create session');
  const data = await res.json();
  return data.session_id;
};

export const sendChatMessage = async (userId: string, sessionId: string, message: string): Promise<ChatResponse> => {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, session_id: sessionId, message }),
  });
  if (!res.ok) throw new Error('Failed to process chat');
  return res.json();
};
