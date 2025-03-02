"use client";
import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import axios from "axios";
import { BACKEND_URL } from "@/utils/constant";
import { toast, Toaster } from "react-hot-toast";

// Define a type for chat messages
interface ChatMessage {
  sender: "user" | "bot";
  text: string;
}

const ChatPage: React.FC = () => {
  const router = useRouter();
  const [pdfUrl, setPdfUrl] = useState<string>("");
  const [pdfName, setPdfName] = useState<string>("");
  const [documentId, setDocumentId] = useState<string>("");  
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);

  // On mount, retrieve the PDF information from localStorage
useEffect(() => {
  const storedPdfName = localStorage.getItem("pdfFileName");
  
  if (storedPdfName) {
    setPdfName(storedPdfName);
    // Fetch the PDF from the backend using the filename
    const fetchPdf = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/get-doc/?filename=${encodeURIComponent(storedPdfName)}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("Token")}`
          }
        });
        
        if (response.data && response.data.presigned_url) {
          setPdfUrl(response.data.presigned_url);
          // Add welcome message to chat
          setMessages([{ 
            sender: "bot", 
            text: `I've analyzed your PDF "${storedPdfName}". What would you like to know about it?` 
          }]);
        }
      } catch (error) {
        console.error("Error fetching PDF:", error);
        toast.error("Failed to load the PDF document.");
      }
    };
    
    fetchPdf();
  } else {
    toast.error("No PDF file found. Please upload a PDF first.");
    router.push("/pdf/upload");
  }
}, [router]);
  // useEffect(() => {
  //   const storedPdfUrl = localStorage.getItem("pdfBlobUrl");
  //   const storedPdfName = localStorage.getItem("pdfFileName");
  //   const storedDocumentId = localStorage.getItem("documentId");
    
  //   if (storedPdfUrl) {
  //     setPdfUrl(storedPdfUrl);
  //     setPdfName(storedPdfName || "Uploaded PDF");
  //     setDocumentId(storedDocumentId || "");
      
  //     // Add welcome message to chat
  //     setMessages([{ 
  //       sender: "bot", 
  //       text: `I've analyzed your PDF "${storedPdfName}". What would you like to know about it?` 
  //     }]);
  //   } else {
  //     toast.error("No PDF file found. Please upload a PDF first.");
  //     router.push("/pdf/upload");
  //   }
    
  //   // Clean up function to revoke blob URL when component unmounts
  //   return () => {
  //     if (storedPdfUrl && storedPdfUrl.startsWith('blob:')) {
  //       URL.revokeObjectURL(storedPdfUrl);
  //     }
  //   };
  // }, [router]);


  const toggleSidebar = () => {
    setIsOpen((prev) => !prev);
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
      // Send question to the backend chat endpoint
      const response = await axios.post(
        `${BACKEND_URL}/generate-response`,
        { 
          query:question // Include the document ID if available
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("Token")}`,
          },
        }
      );
      // Add bot's response to chat
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: response.data.response || "I couldn't find information about that in the document." },
      ]);
    } catch (error: any) {
      console.error("Chat error:", error);
      toast.error(error.response?.data?.message || "Error processing your question.");
      
      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Sorry, I encountered an error while processing your question." },
      ]);
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar toggleSidebar={toggleSidebar} isOpen={isOpen} />

      <div className={`p-4 md:p-8 transition-all duration-300 ${isOpen ? 'ml-64' : 'ml-0'}`}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* PDF Viewer */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="border border-gray-300 dark:border-gray-700 rounded-lg overflow-hidden shadow-lg"
          >
            <div className="bg-gray-100 dark:bg-gray-800 p-2 border-b border-gray-300 dark:border-gray-700">
              <h2 className="font-medium text-sm truncate">{pdfName}</h2>
            </div>
            {pdfUrl ? (
              <iframe
                src={pdfUrl}
                className="w-full h-[calc(100vh-20rem)]"
                title="Uploaded PDF"
              />
            ) : (
              <div className="flex items-center justify-center h-96">
                <p>Loading PDF...</p>
              </div>
            )}
          </motion.div>

          {/* Chat Interface */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg flex flex-col h-[calc(100vh-12rem)]">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                Chat with your PDF
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
                  placeholder="Ask a question about the PDF..."
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
      </div>

      <Toaster position="top-right" />
    </div>
  );
};

export default ChatPage;