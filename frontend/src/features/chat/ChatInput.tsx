import React, { useState, useEffect } from "react";

interface Props {
  onSend: (content: string) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<Props> = ({ onSend, disabled }) => {
  const [value, setValue] = useState("");

  useEffect(() => {
    function onInsert(e: Event) {
      try {
        // @ts-ignore custom event detail
        const text = (e as CustomEvent).detail?.text;
        if (text) setValue((v) => (v ? v + "\n" + text : text));
      } catch (err) {
        // ignore
      }
    }
    window.addEventListener("zotero:insert-snippet", onInsert as EventListener);
    return () => window.removeEventListener("zotero:insert-snippet", onInsert as EventListener);
  }, []);

  function submit() {
    if (!value.trim()) return;
    onSend(value);
    setValue("");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="chat-view__input">
      <div className="chat-input__wrapper">
        <textarea
          className="chat-input__textarea"
          placeholder="Ask a question about your Zotero library…"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
        />
        <button className="btn btn--primary" onClick={submit} disabled={disabled || !value.trim()}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: "6px" }}>
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
