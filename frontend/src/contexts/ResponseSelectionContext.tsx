import React, { createContext, useContext, useState } from "react";

type ResponseSelectionShape = {
  selectedResponseId: string | null;
  setSelectedResponseId: (id: string | null) => void;
};

const ResponseSelectionContext = createContext<ResponseSelectionShape | null>(null);

export const ResponseSelectionProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const [selectedResponseId, setSelectedResponseId] = useState<string | null>(null);

  // Log when selection changes
  React.useEffect(() => {
    console.log("ResponseSelection: selectedResponseId changed to", selectedResponseId);
  }, [selectedResponseId]);

  return (
    <ResponseSelectionContext.Provider value={{ selectedResponseId, setSelectedResponseId }}>
      {children}
    </ResponseSelectionContext.Provider>
  );
};

export function useResponseSelection() {
  const ctx = useContext(ResponseSelectionContext);
  if (!ctx) throw new Error("useResponseSelection must be used within ResponseSelectionProvider");
  return ctx;
}

export default ResponseSelectionContext;
