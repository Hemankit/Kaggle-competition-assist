// Utility functions for interacting with browser localStorage

export const setItem = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.error('Error setting item in localStorage', e);
  }
};

export const getItem = (key) => {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch (e) {
    console.error('Error getting item from localStorage', e);
    return null;
  }
};

export const removeItem = (key) => {
  try {
    localStorage.removeItem(key);
  } catch (e) {
    console.error('Error removing item from localStorage', e);
  }
};

export const clearStorage = () => {
  try {
    localStorage.clear();
  } catch (e) {
    console.error('Error clearing localStorage', e);
  }
};
