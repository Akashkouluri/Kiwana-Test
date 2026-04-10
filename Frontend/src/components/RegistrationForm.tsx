import React, { useState } from 'react';
import { ArrowRight, UserCircle2 } from 'lucide-react';
import { registerUser } from '../services/api';

interface RegistrationFormProps {
  userId: string;
  onRegistered: () => void;
}

function RegistrationForm({ userId, onRegistered }: RegistrationFormProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('+91 ');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !phone) return;

    setLoading(true);
    setError(null);
    try {
      await registerUser(userId, name, email, phone);
      onRegistered();
    } catch (err) {
      setError('Registration failed. Please double-check your details and connection.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="registration-container">
      <div className="registration-card">
        <div className="registration-header">
          <UserCircle2 size={48} className="registration-icon" />
          <h2>Welcome to KIWANA</h2>
          <p>Please enter your details to gain access to your personalized skincare assistant.</p>
        </div>

        <form onSubmit={handleSubmit} className="registration-form">
          <div className="input-group">
            <label htmlFor="name">Full Name</label>
            <input
              id="name"
              type="text"
              placeholder="E.g. Akash Kouluri"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="phone">Phone Number</label>
            <input
              id="phone"
              type="tel"
              placeholder="+91 98765 43210"
              value={phone}
              onChange={(e) => {
                // Ensure +91 remains at the start
                const val = e.target.value;
                if (val.startsWith('+91 ')) {
                  setPhone(val);
                } else if (val.startsWith('+91')) {
                  setPhone('+91 ' + val.slice(3));
                } else {
                  setPhone('+91 ' + val.replace(/\D/g, ''));
                }
              }}
              maxLength={15}
              required
            />
          </div>

          {error && <div className="error-banner">{error}</div>}

          <button type="submit" disabled={loading || !name || !email || !phone}>
            {loading ? 'Securing Access...' : 'Continue to Chat'}
            {!loading && <ArrowRight size={18} />}
          </button>
        </form>
      </div>
    </div>
  );
}

export default RegistrationForm;
