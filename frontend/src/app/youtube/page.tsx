"use client";
import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import { BACKEND_URL } from "@/utils/constant";
import { toast, Toaster } from "react-hot-toast";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";

// Define a type for chat messages
interface ChatMessage {
  sender: "user" | "bot";
  text: string;
}

const Page = () => {
  const router = useRouter();
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [embedUrl, setEmbedUrl] = useState<string>("");
  const [videoTitle, setVideoTitle] = useState<string>("");
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [videoId, setVideoId] = useState<string>("");
  const [showVideoPlayer, setShowVideoPlayer] = useState(false);
  const { fetchWithAuth,isLoggedIn } = useAuth();

  const toggleSidebar = () => {
    setIsOpen((prev) => !prev);
  };

const toastShown = React.useRef(false);

useEffect(() => {
  if (!isLoggedIn && !toastShown.current) {
    toast.error("Signin required to chat with Youtube.");
    toastShown.current = true;
    router.push("/auth/signin");
  }
}, [isLoggedIn, router]);

  // Helper function to convert YouTube URL to embed URL and extract video ID
  // Now it returns values instead of setting state
  const parseYouTubeUrl = (url: string) => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    
    if (match && match[2].length === 11) {
      return {
        videoId: match[2],
        embedUrl: `https://www.youtube.com/embed/${match[2]}`
      };
    }
    
    return {
      videoId: "",
      embedUrl: url
    };
  };

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!videoUrl.trim()) {
      toast.error("Please enter a YouTube URL.");
      return;
    }

    try {
      const { videoId, embedUrl } = parseYouTubeUrl(videoUrl);
      const response = await fetchWithAuth(`${BACKEND_URL}/youtube/upload`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ youtube_url:videoUrl })
      });
      const data = await response.json();
      console.log(data);
      if (!response.ok) {
        throw new Error(data.message || "Failed to load the YouTube video. Please check the URL.");
      }
      if (!videoId) {
        toast.error("Invalid YouTube URL. Please check and try again.");
        return;
      }
      
      setVideoId(videoId);
      setEmbedUrl(embedUrl);
      setVideoTitle(videoUrl); // Use the URL as title for now
      setShowVideoPlayer(true);
      
      // Add welcome message to chat
      setMessages([{ 
        sender: "bot", 
        text: `I've loaded your YouTube video. What would you like to discuss about it?` 
      }]);
    } catch (error) {
      console.error("Error processing YouTube URL:", error);
      toast.error("Failed to load the YouTube video. Please check the URL.");
    }
  };

  const handleSendQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) {
      toast.error("Please enter a question.");
      return;
    }

    // Append user's question to chat
    const userQuestion = question;
    setMessages((prev) => [...prev, { sender: "user", text: userQuestion }]);
    setQuestion("");
    setIsChatLoading(true);

    try {
      // In a real implementation, this would send the video ID to the backend
      // For now, we'll simulate a response
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { 
            sender: "bot", 
            text: `This is a simulated response about the YouTube video (ID: ${videoId}). In a real implementation, you would connect this to a backend that can analyze or discuss the video content.` 
          },
        ]);
        setIsChatLoading(false);
      }, 1000);
      
      // Actual API call commented out for now
      
    } catch (error: any) {
      console.error("Chat error:", error);
      toast.error(error.data?.message || "Error processing your question.");
      
      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Sorry, I encountered an error while processing your question." },
      ]);
      setIsChatLoading(false);
    }
  };

  const handleClearVideo = () => {
    setVideoUrl("");
    setEmbedUrl("");
    setVideoId("");
    setVideoTitle("");
    setMessages([]);
    setShowVideoPlayer(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar toggleSidebar={toggleSidebar} isOpen={isOpen} />

      <div className={`p-4 md:p-8 transition-all duration-300 ${isOpen ? 'ml-64' : 'ml-0'}`}>
        {!showVideoPlayer ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white">Enter YouTube URL</h2>
            <form onSubmit={handleUrlSubmit}>
              <div className="mb-4">
                <input
                  type="text"
                  placeholder="https://www.youtube.com/watch?v=..."
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <button
                type="submit"
                className="bg-slate-950 hover:bg-black text-white p-3 rounded-lg transition-colors w-full"
              >
                Load Video
              </button>
            </form>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* YouTube Video Viewer */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="border border-gray-300 dark:border-gray-700 rounded-lg overflow-hidden shadow-lg"
            >
              <div className="bg-gray-100 dark:bg-gray-800 p-2 border-b border-gray-300 dark:border-gray-700">
                <h2 className="font-medium text-sm truncate">{videoTitle}</h2>
              </div>
              {embedUrl ? (
                <iframe
                  src={embedUrl}
                  className="w-full h-[calc(100vh-20rem)]"
                  title="YouTube Video"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              ) : (
                <div className="flex items-center justify-center h-[calc(100vh-20rem)]">
                  <p>Loading video...</p>
                </div>
              )}
            </motion.div>

            {/* Chat Interface */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg flex flex-col h-[calc(100vh-12rem)]">
              <div className="p-2 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Chat about this video
                </h2>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`p-3 rounded-lg ${
                      msg.sender === "user"
                        ? "bg-blue-100 text-blue-900 ml-auto max-w-[80%]"
                        : "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 mr-auto max-w-[80%]"
                    }`}
                  >
                    {msg.text}
                  </motion.div>
                ))}
                {isChatLoading && (
                  <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg text-gray-800 dark:text-gray-200 mr-auto max-w-[80%]">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                    </div>
                  </div>
                )}
              </div>
              
              <form onSubmit={handleSendQuestion} className="p-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center">
                  <input
                    type="text"
                    placeholder="Ask a question about the video..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    disabled={isChatLoading}
                    className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                  <button
                    type="submit"
                    disabled={isChatLoading}
                    className="bg-slate-950 hover:bg-black text-white p-2 px-4 rounded-r-lg transition-colors disabled:opacity-50"
                  >
                    {isChatLoading ? "..." : "Send"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
      {showVideoPlayer && (
        <div>
          <Button
            onClick={handleClearVideo}
            className="mt-4 ml-10">
            Clear YouTube Video
          </Button>
        </div>
      )}
      <Toaster position="top-right" />
    </div>
  );
}

export default Page;