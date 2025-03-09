"use client";
import { motion } from "framer-motion";
import { FcGoogle } from "react-icons/fc";
import { FiUser, FiMail, FiLock, FiUserPlus } from "react-icons/fi";
import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";
import { BACKEND_URL } from "@/utils/constant";
import axios from "axios";
import { useRouter } from "next/navigation";
import { toast, Toaster } from "react-hot-toast";

const SignUp = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    fullName: ""
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check for an existing token on mount
  useEffect(() => {
    try {
      const token = localStorage.getItem("Token");
      setIsLoggedIn(!!token);
    } catch (error) {
      console.error("LocalStorage access error:", error);
    }
  }, []);

  // Redirect to chat page if already logged in
  useEffect(() => {
    if (typeof window !== "undefined" && isLoggedIn) {
      router.push("/");
    }
  }, [isLoggedIn, router]);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await axios.post(`${BACKEND_URL}/signup`, formData);
      console.log("Response:", response);

      if (response.data) {
        toast.success("Account created successfully! Redirecting to Sign In...");
        setTimeout(() => {
          router.push("/auth/signin");
        }, 2000);
      }
    } catch (error: any) {
      console.error("Error during signup:", error);
      toast.error(
        error.response?.data?.message || "An error occurred. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleGoogleOAuth = () => {
    window.location.href = `${BACKEND_URL}/google`;
  };

  return (
    <div className="bg-gradient-to-br bg-white dark:bg-gray-900 min-h-screen">
      <div className="w-full " />
      <Sidebar toggleSidebar={toggleSidebar} isOpen={isOpen} />

      <div className="flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="relative w-full max-w-md"
        >
          {/* Background overlay for a subtle blur effect */}
          <div className="absolute inset-0 rounded-xl blur opacity-30 transition duration-1000"></div>

          <div className="relative p-8 ">
            <form onSubmit={handleSubmit} className="flex flex-col items-center">
              <h1 className="text-3xl font-bold mb-4 bg-gradient-to-r from-purple-700 via-pink-700 to-purple-700 bg-clip-text text-transparent">
                Prakhar.ai
              </h1>

              <div className="w-full space-y-4">
                {/* Full Name */}
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="relative">
                    <FiUserPlus className="absolute left-3 top-1/2 transform-translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      name="fullName"
                      placeholder="Full Name"
                      value={formData.fullName}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-gray-700 dark:text-white rounded-lg placeholder-gray-400 dark:placeholder-gray-300 focus:ring-2 focus:ring-purple-500"
                      required
                    />
                  </div>
                </motion.div>

                {/* Username */}
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.25 }}
                >
                  <div className="relative">
                    <FiUser className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      name="username"
                      placeholder="Username"
                      value={formData.username}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-gray-700 dark:text-white rounded-lg placeholder-gray-400 dark:placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      required
                    />
                  </div>
                </motion.div>

                {/* Email */}
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  <div className="relative">
                    <FiMail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="email"
                      name="email"
                      placeholder="Email"
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-gray-700 dark:text-white rounded-lg placeholder-gray-400 dark:placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      required
                    />
                  </div>
                </motion.div>

                {/* Password */}
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.35 }}
                >
                  <div className="relative">
                    <FiLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="password"
                      name="password"
                      placeholder="Password"
                      value={formData.password}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 bg-slate-50 dark:bg-gray-700 dark:text-white rounded-lg placeholder-gray-400 dark:placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
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
                className="w-full mt-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-250 disabled:opacity-50"
              >
                {isLoading ? "Creating Account..." : "Sign Up"}
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
                Already have an account?{" "}
                <a
                  href="/auth/signin"
                  className="text-purple-400 hover:text-purple-300 transition-colors"
                >
                  Sign In
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

export default SignUp;
