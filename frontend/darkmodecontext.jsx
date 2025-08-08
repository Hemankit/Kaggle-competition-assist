// context/DarkModeContext.js
import React, { createContext, useContext, useState } from 'react';

// Create context
const DarkModeContext = createContext();

// Custom hook for easier access
export const useDarkMode = () => useContext(DarkModeContext);

// Provider component
export const DarkModeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => setDarkMode((prev) => !prev);

  return (
    <DarkModeContext.Provider value={{ darkMode, toggleDarkMode }}>
      {children}
    </DarkModeContext.Provider>
  );
};