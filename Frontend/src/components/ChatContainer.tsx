import { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import { type Message } from '../App';

interface ChatContainerProps {
  messages: Message[];
}

function ChatContainer({ messages }: ChatContainerProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="chat-container" ref={containerRef}>
      {messages.length === 0 ? (
        <div className="welcome-screen">
          <h1>KIWANA</h1>
        </div>
      ) : (
        messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))
      )}
    </div>
  );
}

export default ChatContainer;
