import { Plus, MessageSquare, User } from 'lucide-react';

interface SidebarProps {
  onNewChat: () => void;
}

const recentChats = [
  "Building a React UI",
  "Tailwind vs Vanilla CSS",
  "Explain Quantum Computing",
  "How to cook a perfect steak"
];

function Sidebar({ onNewChat }: SidebarProps) {
  return (
    <div className="sidebar">
      <button className="new-chat-btn" onClick={onNewChat}>
        <Plus size={16} />
        New chat
      </button>

      <div className="chat-history">
        {recentChats.map((chat, idx) => (
          <div key={idx} className="chat-history-item">
            <MessageSquare size={16} />
            {chat}
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="user-avatar">
            <User size={18} />
          </div>
          <span style={{ fontSize: '14px', fontWeight: 500 }}>Akash</span>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
