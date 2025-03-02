"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import axios from "axios";
import toast, { Toaster } from "react-hot-toast";

// Define the props type
interface UserProfileProps {
  onLogout: () => void; 
}

// Define BACKEND_URL (replace with your own or use an environment variable)
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:3000";

const UserProfile: React.FC<UserProfileProps> = ({ onLogout }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [userData, setUserData] = useState<{
    full_name?: string;
    username?: string;
    email?: string;
  }>({});

  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const storedUserData = localStorage.getItem("UserData");
    if (storedUserData) {
      setUserData(JSON.parse(storedUserData));
    }

    // Ensure this runs in the browser
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("Token");
      if (token && !storedUserData) {
        getUserData();
      }
    }

    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const getUserData = async () => {
    try {
      const token = localStorage.getItem("Token");
      if (!token) return;

      const response = await axios.get(`${BACKEND_URL}/get-profile`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setUserData(response.data);
      localStorage.setItem("UserData", JSON.stringify(response.data));
    } catch (error) {
      console.error("Error fetching user data:", error);
    }
  };

  const handleLogout = () => {
    // Ensure this runs in the browser
    if (typeof window !== "undefined") {
      localStorage.removeItem("Token");
      localStorage.removeItem("UserData");
      window.dispatchEvent(new Event("storage"));
    }
    toast.success("Logout successful!");
    setTimeout(() => {
      onLogout();
      router.push("/");
    }, 1000);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 hover:opacity-80 transition-opacity"
      >
        <div className="w-10 h-10 bg-gradient-to-br from-blue-900 to-purple-900 rounded-full flex items-center justify-center">
          <span className="font-semibold text-white">
            {userData.username ? userData.username.charAt(0).toUpperCase() : ""}
          </span>
        </div>
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 bg-black opacity-50 z-10" />
          <div className="absolute right-0 mt-2 w-48 bg-gray-900 rounded-lg shadow-lg py-2 z-20">
            <div className="px-4 py-2 border-b border-gray-700">
              <p className="text-white font-medium truncate">
                {userData.username || "User"}
              </p>
              <p className="text-gray-400 text-sm truncate">
                {userData.email || "user@example.com"}
              </p>
            </div>
            <Link
              href="/profile"
              className="block px-4 py-2 text-white hover:bg-gray-700"
              onClick={() => setIsOpen(false)}
            >
              Profile
            </Link>
            <button
              onClick={handleLogout}
              className="w-full text-left px-4 py-2 text-red-400 hover:bg-gray-700"
            >
              Logout
            </button>
          </div>
        </>
      )}
      <Toaster />
    </div>
  );
};

export default UserProfile;
