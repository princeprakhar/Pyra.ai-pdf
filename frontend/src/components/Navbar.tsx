// "use client";
// import { useState, useEffect } from "react";
// import Link from "next/link";
// import Image from "next/image";
// import { Menu, X, ArrowRight, Sun, Moon } from "lucide-react";
// import MaxWidthWrapper from "./MaxWidthWrapper";
// import { buttonVariants } from "./ui/button";
// import { useAuth } from "@/contexts/AuthContext"; // adjust the path accordingly

// interface NavbarProps {
//   toggleSidebar?: () => void;
//   isOpen?: boolean;
// }

// const Navbar: React.FC<NavbarProps> = ({ toggleSidebar, isOpen = false }) => {
//   const [isMenuOpen, setIsMenuOpen] = useState(false);
//   const [theme, setTheme] = useState<"light" | "dark">("light");
//   const { isLoggedIn, logout } = useAuth();

//   const toggleMenu = () => setIsMenuOpen((prev) => !prev);
//   const toggleTheme = () => setTheme((prev) => (prev === "light" ? "dark" : "light"));

//   useEffect(() => {
//     if (typeof window !== "undefined") {
//       const savedTheme =
//         localStorage.getItem("theme") ||
//         (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
//       setTheme(savedTheme as "light" | "dark");
//     }
//   }, []);

//   useEffect(() => {
//     if (typeof window !== "undefined") {
//       localStorage.setItem("theme", theme);
//       if (theme === "dark") {
//         document.documentElement.classList.add("dark");
//       } else {
//         document.documentElement.classList.remove("dark");
//       }
//     }
//   }, [theme]);

//   return (
//     <nav className="sticky top-0 z-50 border-b bg-white dark:bg-gray-900/75 backdrop-blur-lg transition-colors">
//       <MaxWidthWrapper>
//         <div className="flex h-16 items-center justify-between">
//           <div className="flex items-center">
//             {toggleSidebar && (
//               <button onClick={toggleSidebar} aria-label="Toggle sidebar" className="mr-4">
//                 <Image
//                   src="/sidebar.png"
//                   alt="Toggle Sidebar"
//                   width={30}
//                   height={30}
//                   className={`w-auto h-auto bg-white dark:bg-gray-800 rounded-lg transition-transform duration-300 ${
//                     isOpen ? "rotate-180" : ""
//                   }`}
//                 />
//               </button>
//             )}
//             <Link href="/" className="flex items-center space-x-2">
//               <span className="text-2xl font-bold bg-gradient-to-r from-purple-700 via-pink-700 to-purple-700 bg-clip-text text-transparent">
//                 Prakhar.ai
//               </span>
//             </Link>
//           </div>
//           <div className="hidden md:flex items-center space-x-4">
//             <Link href="/" className={buttonVariants({ variant: "ghost", size: "sm" })}>
//               Home
//             </Link>
//             <Link href="/about" className={buttonVariants({ variant: "ghost", size: "sm" })}>
//               About ✨
//             </Link>
//             <Link
//               href="/pdf/upload"
//               className={buttonVariants({
//                 variant: "ghost",
//                 size: "sm",
//                 className: "bg-slate-200 text-black items-center gap-1",
//               })}
//             >
//               Chat with PDF 📄
//             </Link>
//             <Link
//               href="/youtube"
//               className={buttonVariants({
//                 variant: "ghost",
//                 size: "sm",
//                 className: "bg-slate-200 items-center text-black gap-1",
//               })}
//             >
//               Chat with{" "}
//               <Image
//                 src="/youtube.png"
//                 alt="YouTube"
//                 width={20}
//                 height={20}
//                 className="h-5"
//               />
//             </Link>
//             {isLoggedIn ? (
//               <button
//                 onClick={logout}
//                 className={buttonVariants({ variant: "ghost", size: "sm", className: "text-red-600 border-2" })}
//               >
//                 Logout
//               </button>
//             ) : (
//               <>
//                 <Link
//                   href="/auth/signin"
//                   className={buttonVariants({ size: "sm", className: "items-center gap-1" })}
//                 >
//                   Sign In
//                 </Link>
//                 <Link
//                   href="/auth/signup"
//                   className={buttonVariants({ size: "sm", className: "items-center gap-1" })}
//                 >
//                   Sign Up <ArrowRight className="ml-1.5 h-5 w-5" />
//                 </Link>
//               </>
//             )}
//             <button onClick={toggleTheme} aria-label="Toggle dark/light theme" className="p-2 rounded-full border">
//               {theme === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
//             </button>
//           </div>
//           <div className="md:hidden flex items-center">
//             <button onClick={toggleMenu} aria-label="Toggle mobile menu" className="text-black dark:text-white">
//               {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
//             </button>
//           </div>
//         </div>
//         {isMenuOpen && (
//           <div className="md:hidden mt-2 bg-white dark:bg-gray-800 rounded shadow-lg p-4 flex flex-col space-y-2">
//             <Link
//               href="/"
//               onClick={() => setIsMenuOpen(false)}
//               className={buttonVariants({ variant: "ghost", size: "sm" })}
//             >
//               Home
//             </Link>
//             <Link
//               href="/about"
//               onClick={() => setIsMenuOpen(false)}
//               className={buttonVariants({ variant: "ghost", size: "sm" })}
//             >
//               About ✨
//             </Link>
//             <Link
//               href="/pdf/upload"
//               onClick={() => setIsMenuOpen(false)}
//               className={buttonVariants({
//                 variant: "ghost",
//                 size: "sm",
//                 className: "bg-slate-400 items-center gap-1",
//               })}
//             >
//               Chat with PDF 📄
//             </Link>
//             <Link
//               href="/youtube"
//               onClick={() => setIsMenuOpen(false)}
//               className={buttonVariants({
//                 variant: "ghost",
//                 size: "sm",
//                 className: "bg-slate-200 items-center gap-1",
//               })}
//             >
//               Chat with{" "}
//               <Image
//                 src="/youtube-icon.png"
//                 alt="YouTube"
//                 width={20}
//                 height={20}
//                 className="h-5"
//               />
//             </Link>
//             {isLoggedIn ? (
//               <button
//                 onClick={() => {
//                   logout();
//                   setIsMenuOpen(false);
//                 }}
//                 className={buttonVariants({ variant: "ghost", size: "sm", className: "text-red-600" })}
//               >
//                 Logout
//               </button>
//             ) : (
//               <div className="flex flex-col space-y-2">
//                 <Link href="/auth/signin" onClick={() => setIsMenuOpen(false)}>
//                   <button className="bg-black hover:bg-white hover:text-black text-white font-bold py-2 px-4 rounded-lg w-full">
//                     Sign In
//                   </button>
//                 </Link>
//                 <Link href="/auth/signup" onClick={() => setIsMenuOpen(false)}>
//                   <button className="bg-black hover:bg-white hover:text-black text-white font-bold py-2 px-4 rounded-lg w-full">
//                     Sign Up
//                   </button>
//                 </Link>
//               </div>
//             )}
//             <button onClick={toggleTheme} aria-label="Toggle dark/light theme" className="p-2 rounded-full border mt-2 self-center">
//               {theme === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
//             </button>
//           </div>
//         )}
//       </MaxWidthWrapper>
//     </nav>
//   );
// };

// export default Navbar;







"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { Menu, X, ArrowRight, Sun, Moon } from "lucide-react";
import MaxWidthWrapper from "./MaxWidthWrapper"; // Example wrapper component
import { buttonVariants } from "./ui/button";    // Example Tailwind variant helper
import { useAuth } from "@/contexts/AuthContext"; // Adjust path as needed

interface NavbarProps {
  toggleSidebar?: () => void;
  isOpen?: boolean;
}

const Navbar: React.FC<NavbarProps> = ({ toggleSidebar, isOpen = false }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const { isLoggedIn, logout } = useAuth(); // If you have an auth context

  const toggleMenu = () => setIsMenuOpen((prev) => !prev);
  const toggleTheme = () => setTheme((prev) => (prev === "light" ? "dark" : "light"));

  // On initial load, check localStorage or system preference
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedTheme =
        localStorage.getItem("theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      setTheme(savedTheme as "light" | "dark");
    }
  }, []);

  // Whenever theme changes, store it and toggle .dark class on <html>
  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem("theme", theme);
      if (theme === "dark") {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    }
  }, [theme]);

  return (
    <nav className="sticky top-0 z-50 border-b bg-white dark:bg-gray-900/75 backdrop-blur-lg transition-colors">
      <MaxWidthWrapper>
        <div className="flex h-16 items-center justify-between">
          {/* Left Side: Logo + Sidebar Toggle (if any) */}
          <div className="flex items-center">
            {toggleSidebar && (
              <button onClick={toggleSidebar} aria-label="Toggle sidebar" className="mr-4">
                <Image
                  src="/sidebar.png"
                  alt="Toggle Sidebar"
                  width={30}
                  height={30}
                  className={`w-auto h-auto bg-white dark:bg-gray-800 rounded-lg transition-transform duration-300 ${
                    isOpen ? "rotate-180" : ""
                  }`}
                />
              </button>
            )}
            <Link href="/" className="flex items-center space-x-2">
              <span className="text-2xl font-bold bg-gradient-to-r from-purple-700 via-pink-700 to-purple-700 bg-clip-text text-transparent">
                Prakhar.ai
              </span>
            </Link>
          </div>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center space-x-4">
            <Link href="/" className={buttonVariants({ variant: "ghost", size: "sm" })}>
              Home
            </Link>
            <Link href="/about" className={buttonVariants({ variant: "ghost", size: "sm" })}>
              About ✨
            </Link>
            <Link
              href="/pdf/upload"
              className={buttonVariants({
                variant: "ghost",
                size: "sm",
                className: "bg-slate-200 text-black items-center gap-1",
              })}
            >
              Chat with PDF 📄
            </Link>
            <Link
              href="/youtube"
              className={buttonVariants({
                variant: "ghost",
                size: "sm",
                className: "bg-slate-200 text-black items-center gap-1",
              })}
            >
              Chat with{" "}
              <Image
                src="/youtube.png"
                alt="YouTube"
                width={20}
                height={20}
                className="h-5"
              />
            </Link>

            {isLoggedIn ? (
              <button
                onClick={logout}
                className={buttonVariants({
                  variant: "ghost",
                  size: "sm",
                  className: "text-red-600 border-2",
                })}
              >
                Logout
              </button>
            ) : (
              <>
                <Link
                  href="/auth/signin"
                  className={buttonVariants({ size: "sm", className: "items-center gap-1" })}
                >
                  Sign In
                </Link>
                <Link
                  href="/auth/signup"
                  className={buttonVariants({ size: "sm", className: "items-center gap-1" })}
                >
                  Sign Up <ArrowRight className="ml-1.5 h-5 w-5" />
                </Link>
              </>
            )}

            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              aria-label="Toggle dark/light theme"
              className="p-2 rounded-full border"
            >
              {theme === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
            </button>
          </div>

          {/* Mobile Menu Toggle */}
          <div className="md:hidden flex items-center">
            <button onClick={toggleMenu} aria-label="Toggle mobile menu" className="text-black dark:text-white">
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu Dropdown */}
        {isMenuOpen && (
          <div className="md:hidden mt-2 bg-white dark:bg-gray-800 rounded shadow-lg p-4 flex flex-col space-y-2">
            <Link
              href="/"
              onClick={() => setIsMenuOpen(false)}
              className={buttonVariants({ variant: "ghost", size: "sm" })}
            >
              Home
            </Link>
            <Link
              href="/about"
              onClick={() => setIsMenuOpen(false)}
              className={buttonVariants({ variant: "ghost", size: "sm" })}
            >
              About ✨
            </Link>
            <Link
              href="/pdf/upload"
              onClick={() => setIsMenuOpen(false)}
              className={buttonVariants({
                variant: "ghost",
                size: "sm",
                className: "bg-slate-400 items-center gap-1",
              })}
            >
              Chat with PDF 📄
            </Link>
            <Link
              href="/youtube"
              onClick={() => setIsMenuOpen(false)}
              className={buttonVariants({
                variant: "ghost",
                size: "sm",
                className: "bg-slate-200 items-center gap-1",
              })}
            >
              Chat with{" "}
              <Image
                src="/youtube-icon.png"
                alt="YouTube"
                width={20}
                height={20}
                className="h-5"
              />
            </Link>
            {isLoggedIn ? (
              <button
                onClick={() => {
                  logout();
                  setIsMenuOpen(false);
                }}
                className={buttonVariants({ variant: "ghost", size: "sm", className: "text-red-600" })}
              >
                Logout
              </button>
            ) : (
              <div className="flex flex-col space-y-2">
                <Link href="/auth/signin" onClick={() => setIsMenuOpen(false)}>
                  <button className="bg-black hover:bg-white hover:text-black text-white font-bold py-2 px-4 rounded-lg w-full">
                    Sign In
                  </button>
                </Link>
                <Link href="/auth/signup" onClick={() => setIsMenuOpen(false)}>
                  <button className="bg-black hover:bg-white hover:text-black text-white font-bold py-2 px-4 rounded-lg w-full">
                    Sign Up
                  </button>
                </Link>
              </div>
            )}
            {/* Theme Toggle in mobile dropdown */}
            <button
              onClick={toggleTheme}
              aria-label="Toggle dark/light theme"
              className="p-2 rounded-full border mt-2 self-center"
            >
              {theme === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
            </button>
          </div>
        )}
      </MaxWidthWrapper>
    </nav>
  );
};

export default Navbar;
