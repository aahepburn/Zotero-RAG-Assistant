import React, { useState } from 'react';

interface Props {
  reasoning: string;
  messageId: string;
}

/**
 * A collapsible section that displays AI reasoning steps.
 * Follows industry best practices:
 * - Collapsed by default to reduce cognitive load
 * - Expandable to show full reasoning for transparency
 * - Clean, unobtrusive design
 */
const ReasoningSection: React.FC<Props> = ({ reasoning, messageId }) => {
  const [expanded, setExpanded] = useState(false);

  if (!reasoning) return null;

  return (
    <div className="reasoning-section">
      <button
        className="reasoning-toggle"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
        aria-controls={`reasoning-${messageId}`}
      >
        {expanded ? (
          <>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 15l-6-6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Hide reasoning
          </>
        ) : (
          <>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 9l6 6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Show reasoning
          </>
        )}
      </button>
      
      {expanded && (
        <div 
          id={`reasoning-${messageId}`}
          className="reasoning-content"
        >
          <div className="reasoning-label">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
              <path d="M12 8v4M12 16h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            AI Reasoning Process
          </div>
          <div className="reasoning-text">
            {reasoning.split('\n\n').map((paragraph, idx) => (
              <p key={idx}>{paragraph}</p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ReasoningSection;
