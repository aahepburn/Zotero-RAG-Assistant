import React from 'react';
import '../../styles/semantic-scholar-modal.css';

export interface SemanticScholarPaper {
  title: string;
  abstract: string;
  year?: number;
  authors: string[];
  citation_count: number;
  citations: any[];
  references: any[];
  url: string;
  doi?: string;
}

interface SemanticScholarModalProps {
  paper: SemanticScholarPaper;
  onClose: () => void;
}

const SemanticScholarModal: React.FC<SemanticScholarModalProps> = ({ paper, onClose }) => {
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="semantic-modal-overlay" onClick={handleOverlayClick}>
      <div className="semantic-modal-content">
        <header className="semantic-modal-header">
          <div>
            <h2 className="semantic-modal-title">{paper.title}</h2>
            {paper.year && (
              <div className="semantic-modal-year">{paper.year}</div>
            )}
          </div>
          <button className="semantic-modal-close" onClick={onClose} aria-label="Close">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </header>
        
        <div className="semantic-modal-body">
          {/* Authors */}
          {paper.authors && paper.authors.length > 0 && (
            <section className="semantic-section">
              <h3 className="semantic-section-title">Authors</h3>
              <div className="semantic-authors">
                {paper.authors.join(', ')}
              </div>
            </section>
          )}

          {/* Abstract */}
          <section className="semantic-section">
            <h3 className="semantic-section-title">Abstract</h3>
            <p className="semantic-abstract">
              {paper.abstract || "No abstract available"}
            </p>
          </section>
          
          {/* Metadata */}
          <section className="semantic-section">
            <h3 className="semantic-section-title">Metadata</h3>
            <div className="semantic-metadata">
              <div className="semantic-metadata-item">
                <span className="semantic-metadata-label">Citations:</span>
                <span className="semantic-metadata-value">{paper.citation_count.toLocaleString()}</span>
              </div>
              {paper.doi && (
                <div className="semantic-metadata-item">
                  <span className="semantic-metadata-label">DOI:</span>
                  <span className="semantic-metadata-value">{paper.doi}</span>
                </div>
              )}
              <div className="semantic-metadata-item">
                <span className="semantic-metadata-label">References:</span>
                <span className="semantic-metadata-value">{paper.references?.length || 0}</span>
              </div>
            </div>
          </section>
          
          {/* Citations Preview */}
          {paper.citations && paper.citations.length > 0 && (
            <section className="semantic-section">
              <h3 className="semantic-section-title">
                Recent Citations ({paper.citations.length > 10 ? '10 of ' : ''}{paper.citations.length})
              </h3>
              <ul className="semantic-citation-list">
                {paper.citations.slice(0, 10).map((citation, i) => (
                  <li key={i} className="semantic-citation-item">
                    <div className="semantic-citation-title">{citation.title || 'Untitled'}</div>
                    {citation.year && (
                      <div className="semantic-citation-year">({citation.year})</div>
                    )}
                  </li>
                ))}
              </ul>
              {paper.citations.length > 10 && (
                <p className="semantic-more-info">
                  ... and {paper.citations.length - 10} more citations
                </p>
              )}
            </section>
          )}
          
          {/* References Preview */}
          {paper.references && paper.references.length > 0 && (
            <section className="semantic-section">
              <h3 className="semantic-section-title">
                References ({paper.references.length > 10 ? '10 of ' : ''}{paper.references.length})
              </h3>
              <ul className="semantic-citation-list">
                {paper.references.slice(0, 10).map((ref, i) => (
                  <li key={i} className="semantic-citation-item">
                    <div className="semantic-citation-title">{ref.title || 'Untitled'}</div>
                    {ref.year && (
                      <div className="semantic-citation-year">({ref.year})</div>
                    )}
                  </li>
                ))}
              </ul>
              {paper.references.length > 10 && (
                <p className="semantic-more-info">
                  ... and {paper.references.length - 10} more references
                </p>
              )}
            </section>
          )}
        </div>
        
        {/* Footer Actions */}
        <div className="semantic-modal-footer">
          <a 
            href={paper.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="semantic-link-button"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            View on Semantic Scholar
          </a>
        </div>
      </div>
    </div>
  );
};

export default SemanticScholarModal;
