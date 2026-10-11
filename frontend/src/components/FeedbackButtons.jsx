import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Check, Send } from 'lucide-react';

export default function FeedbackButtons({ eventId, suggestedCause, onSubmitFeedback }) {
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [showNotes, setShowNotes] = useState(false);
  const [notes, setNotes] = useState('');
  const [isConfirmed, setIsConfirmed] = useState(true);

  const handleAction = (confirmed) => {
    setIsConfirmed(confirmed);
    setShowNotes(true);
  };

  const handleSend = () => {
    onSubmitFeedback({
      event_id: eventId || 'EVT-MANUAL',
      suggested_root_cause: suggestedCause || 'Unknown',
      is_confirmed: isConfirmed,
      operator_notes: notes,
    });
    setFeedbackSent(true);
    setShowNotes(false);
  };

  if (feedbackSent) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-emerald)', fontSize: '0.85rem' }}>
        <Check size={16} /> Operator feedback successfully recorded.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Validate Diagnosis:</span>
        <button
          className="btn-outline"
          style={{ padding: '0.35rem 0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          onClick={() => handleAction(true)}
        >
          <ThumbsUp size={14} color="#34d399" /> Confirm
        </button>
        <button
          className="btn-outline"
          style={{ padding: '0.35rem 0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          onClick={() => handleAction(false)}
        >
          <ThumbsDown size={14} color="#f43f5e" /> Reject
        </button>
      </div>

      {showNotes && (
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <input
            type="text"
            placeholder={isConfirmed ? "Add operator observation (optional)..." : "Specify actual cause or explanation..."}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            style={{
              flex: 1,
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              padding: '0.4rem 0.75rem',
              color: '#fff',
              fontSize: '0.82rem',
              outline: 'none',
            }}
          />
          <button
            className="btn-primary"
            style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
            onClick={handleSend}
          >
            <Send size={13} /> Submit
          </button>
        </div>
      )}
    </div>
  );
}
