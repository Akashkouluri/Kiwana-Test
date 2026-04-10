import { useState } from 'react';
import ChatContainer from './components/ChatContainer';
import ChatInput from './components/ChatInput';
import RegistrationForm from './components/RegistrationForm';
import { createSession, sendChatMessage } from './services/api';
import './index.css';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

function App() {
  const [isRegistered, setIsRegistered] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [userId] = useState('user123'); // Still static until you add true auth, but allows profiling
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRegistrationComplete = async () => {
    setIsRegistered(true);
    // Secure session immediately upon registration approval
    try {
      const id = await createSession(userId);
      setSessionId(id);
    } catch (err) {
      console.error("Could not obtain session immediately: ", err);
    }
  };

  const handleSendMessage = async (content: string) => {
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      try {
        currentSessionId = await createSession(userId);
        setSessionId(currentSessionId);
      } catch (err) {
        console.error("Session missing and failed to create: ", err);
      }
    }

    // Add user message to UI immediately
    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
    };
    
    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(userId, currentSessionId || 'default-session', content);
      
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.reply,
      };
      
      setMessages((prev) => [...prev, aiResponse]);
    } catch (error) {
      console.error("Chat error: ", error);
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I'm sorry, I was unable to connect to the server.",
      };
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isRegistered) {
    return (
      <div className="app-container">
        <RegistrationForm userId={userId} onRegistered={handleRegistrationComplete} />
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="main-view">
        <ChatContainer messages={messages} />
        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}

export default App;
