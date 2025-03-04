"use client";
import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { BACKEND_URL } from "@/utils/constant";

interface AuthContextType {
  isLoggedIn: boolean;
  login: (token: string) => void;
  logout: () => void;
  fetchWithAuth: (url: string, options?: RequestInit) => Promise<Response>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

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

  const logout = async () => {
    try {
      await fetch(`${BACKEND_URL}/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout failed:", error);
    }

    localStorage.removeItem("Token");
    localStorage.removeItem("pdfBlobUrl");
    localStorage.removeItem("pdfFileName");

    setIsLoggedIn(false);
    router.push("/");

    if (typeof window !== "undefined") {
      window.dispatchEvent(new Event("auth-state-changed"));
    }
  };

  const refreshToken = async (): Promise<string | null> => {
    try {
      const response = await fetch(`${BACKEND_URL}/refresh`, {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        logout();
        return null;
      }

      const data = await response.json();
      localStorage.setItem("Token", data.access_token);
      return data.access_token;
    } catch (error) {
      console.error("Failed to refresh token:", error);
      logout();
      return null;
    }
  };

  const fetchWithAuth = async (url: string, options: RequestInit = {}): Promise<Response> => {
    let token = localStorage.getItem("Token");

    let response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 401) {
      token = await refreshToken();
      if (token) {
        response = await fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            Authorization: `Bearer ${token}`,
          },
        });
      }
    }

    return response;
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout, fetchWithAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
