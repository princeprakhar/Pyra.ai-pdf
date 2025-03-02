"use client";
import { motion } from "framer-motion";
import { FcGoogle } from "react-icons/fc";
import { FiUser, FiLock } from "react-icons/fi";
import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";
import axios from "axios";
import { BACKEND_URL } from "@/utils/constant";
import { toast } from "react-hot-toast";
import { Toaster } from "react-hot-toast";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext"; // Import your AuthContext hook

const SignIn = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();
  
  // Use the global auth state
  const { isLoggedIn, login } = useAuth();

  // Redirect to chat page when user is logged in
  useEffect(() => {
    if (isLoggedIn) {
      router.push("/chat");
    }
  }, [isLoggedIn, router]);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    if (!username || !password) {
      toast.error("Please enter both username and password.");
      setIsLoading(false);
      return;
    }

    try {
      const response = await axios.post(`${BACKEND_URL}/signin`, {
        username,
        password,
      });

      if (response.status === 200) {
        toast.success("Sign in successful!");
        if (typeof window !== "undefined") {
          localStorage.setItem("Token", response.data.access_token);
        }
        // Call the global login function to update auth state
        login(response.data.access_token);
        // Optionally, redirect after login (this effect will handle redirection)
        router.push("/pdf/upload");
      } else {
        toast.error(`Unexpected response: ${response.status}`);
      }
    } catch (error: any) {
      console.error("Error during signin:", error);
      if (error.response) {
        if (error.response.status === 400) {
          toast.error("Invalid username or password. Please try again.");
        } else if (error.response.status === 500) {
          toast.error("Server error. Please try again later.");
        } else {
          toast.error(error.response.data.message || "An unknown error occurred.");
        }
      } else {
        toast.error("Please check your connection.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleOAuth = () => {
    window.location.href = `${BACKEND_URL}/google`;
  };

  return (
    <div className="bg-gradient-to-br dark:bg-gray-900 bg-white">
      <div className="w-full border-t border-gray-200 dark:border-gray-900" />
      <Sidebar toggleSidebar={toggleSidebar} isOpen={isOpen} />

      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="relative w-full max-w-md"
        >
          <div className="relative p-8">
            <form onSubmit={handleSubmit} className="flex flex-col items-center">
              <h1 className="text-3xl font-bold mb-4 bg-gradient-to-r from-purple-700 via-pink-700 to-purple-700 bg-clip-text text-transparent">
                Prakhar.ai
              </h1>

              <div className="w-full space-y-4">
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="relative">
                    <FiUser className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 bg-slate-200 rounded-lg text-black placeholder-gray-400 focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                </motion.div>

                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  <div className="relative">
                    <FiLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="password"
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 bg-slate-50 rounded-lg text-black placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                </motion.div>
              </div>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit"
                disabled={isLoading}
                className="w-full mt-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-250 disabled:opacity-50"
              >
                {isLoading ? "Signing In..." : "Sign In"}
              </motion.button>

              <div className="w-full flex items-center my-6">
                <div className="flex-1 border-t border-gray-600"></div>
                <span className="px-4 text-gray-400 text-sm">OR</span>
                <div className="flex-1 border-t border-gray-600"></div>
              </div>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="button"
                onClick={handleGoogleOAuth}
                className="w-full flex items-center justify-center space-x-3 bg-gray-200 hover:bg-gray-300 text-black font-semibold py-3 px-6 rounded-lg transition-all duration-250"
              >
                <FcGoogle className="w-6 h-6" />
                <span>Continue with Google</span>
              </motion.button>

              <div className="mt-6 text-sm text-gray-400">
                Don&apos;t have an account?{" "}
                <a href="/auth/signup" className="text-blue-400 hover:text-blue-300 transition-colors">
                  Sign Up
                </a>
              </div>
            </form>
          </div>
        </motion.div>
      </div>
      <Toaster />
    </div>
  );
};

export default SignIn;
