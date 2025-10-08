import React, { createContext, useContext, useState } from 'react';
import mockUsers from '../data/users.json'; // Detailed profile data (for CIS, badges, etc.)
import mockCredentials from '../data/mockCredentials.json'; // Simple login credentials

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

// Utility function to merge registration with mock data for session tracking
const addNewMockUser = (name, email, password, role) => {
    const newId = (mockUsers.length + 1).toString();
    const newUserProfile = {
        id: newId,
        name,
        role,
        email,
        // Default CIS and badge for a new user
        cis: 100,
        current_badge: "New Contributor",
        badges: ["New Contributor"],
        bio: role === 'NGO' ? "A newly registered non-profit organization." : "A community member eager to start contributing.",
    };
    // Add to both lists for immediate session and future logins
    mockUsers.push(newUserProfile); 
    mockCredentials.push({ id: newId, email, password, role });
    
    return newUserProfile;
};


export const AuthProvider = ({ children }) => {
    // Attempt to load user from localStorage for mock session persistence
    const [user, setUser] = useState(() => {
        const savedUser = localStorage.getItem('samaajseva_user');
        return savedUser ? JSON.parse(savedUser) : null;
    });
    const [isLoggedIn, setIsLoggedIn] = useState(!!user);

    // --- Mock Login Function ---
    const login = (email, password) => {
        // 1. Check simple credentials
        const foundCredential = mockCredentials.find(
            u => u.email === email && u.password === password
        );

        if (foundCredential) {
            // 2. Fetch the full personalized profile using the email
            const fullProfile = mockUsers.find(u => u.email === email);
            
            if (!fullProfile) {
                return { success: false, message: 'Profile data incomplete.' };
            }

            // 3. Set the full profile state for personalization across the app (CIS, name, role)
            setUser(fullProfile);
            setIsLoggedIn(true);
            // Store the full profile for persistence
            localStorage.setItem('samaajseva_user', JSON.stringify(fullProfile)); 
            
            return { success: true, user: fullProfile };
        } else {
            return { success: false, message: 'Invalid credentials. Check email or password.' };
        }
    };

    // --- Mock Register Function ---
    const register = (name, email, password, role) => {
        // Check if user already exists
        if (mockCredentials.some(u => u.email === email)) {
            return { success: false, message: 'Account with this email already exists.' };
        }
        
        // Add new user to mock lists and retrieve their profile data
        const newUserProfile = addNewMockUser(name, email, password, role);

        // Immediately log the new user in
        setUser(newUserProfile);
        setIsLoggedIn(true);
        localStorage.setItem('samaajseva_user', JSON.stringify(newUserProfile));
        
        return { success: true, user: newUserProfile };
    };

    // --- Logout Function ---
    const logout = () => {
        setUser(null);
        setIsLoggedIn(false);
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
