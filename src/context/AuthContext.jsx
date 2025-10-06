// src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

// --- Mock Data ---
// In a real application, this would come from a database/API
const MOCK_USERS = [
    { id: 'u1', name: 'NGO Shanti Seva', email: 'ngo@seva.org', password: '123', role: 'NGO' },
    { id: 'u2', name: 'Donor Priya', email: 'donor@seva.com', password: '123', role: 'Donor' },
];
// -----------------

export const AuthProvider = ({ children }) => {
  // Load user from localStorage for session persistence
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('samaajseva_user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch (error) {
      console.error("Error parsing user from localStorage:", error);
      return null;
    }
  });

  const isLoggedIn = !!user;

  // Login Function
  const login = (email, password) => {
    const foundUser = MOCK_USERS.find(
      u => u.email === email && u.password === password
    );

    if (foundUser) {
      const userData = {
        id: foundUser.id,
        name: foundUser.name,
        role: foundUser.role, // 'NGO' or 'Donor'
      };
      setUser(userData);
      localStorage.setItem('samaajseva_user', JSON.stringify(userData));
      return { success: true, user: userData };
    } else {
      return { success: false, message: 'Invalid credentials or user not found.' };
    }
  };

  // Registration Function (Mocks adding a new user)
  const register = (name, email, password, role) => {
      // Check if user already exists
      if (MOCK_USERS.some(u => u.email === email)) {
          return { success: false, message: 'User already exists.' };
      }
      
      const newUser = { id: Date.now().toString(), name, email, password, role };
      MOCK_USERS.push(newUser); // Add to our mock list
      
      // Log the user in immediately after registration
      const userData = { id: newUser.id, name: newUser.name, role: newUser.role };
      setUser(userData);
      localStorage.setItem('samaajseva_user', JSON.stringify(userData));
      return { success: true, user: userData };
  };

  // Logout Function
  const logout = () => {
    setUser(null);
    localStorage.removeItem('samaajseva_user');
  };

  const value = {
    user,
    isLoggedIn,
    login,
    logout,
    register,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};