// AuthContext.tsx
"use client";
import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";

interface AuthContextType {
  isLoggedIn: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router  = useRouter();

  // On mount, check localStorage for a token
  useEffect(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("Token");
      setIsLoggedIn(!!token);
    }
  }, []);

  const login = (token: string) => {
    localStorage.setItem("Token", token);
    setIsLoggedIn(true);
  };

  const logout = () => {
    // Clear all necessary items from localStorage
    localStorage.removeItem("Token");
    localStorage.removeItem("pdfBlobUrl");
    localStorage.removeItem("pdfFileName");
    
    // Update state first
    setIsLoggedIn(false);
    
    // Then redirect to home page
    router.push("/");
    
    // Optionally dispatch an event to notify components about logout
    if (typeof window !== "undefined") {
      window.dispatchEvent(new Event("auth-state-changed"));
    }
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook for consuming the context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};





  

 

  
