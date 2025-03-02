"use client";
import Image from "next/image";
import { Box, Button } from "@mui/material";
import Link from "next/link";
import {
  IconLayoutDashboard,
  IconMessage,
  IconPhone,
} from "@tabler/icons-react";

interface SidebarProps {
  isOpen: boolean;
  toggleSidebar: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, toggleSidebar }) => {
  return (
    <div className="flex">
      <div
        className={`fixed inset-y-0 left-0 w-64 bg-white text-black transition-transform duration-300 ease-in-out border-r-1 border-gray-200 shadow-md ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="p-4 flex justify-between items-center">
          <button onClick={toggleSidebar} className="ml-auto">
            <Image
              src="/sidebar.png"
              alt="Close Sidebar"
              width={30}
              height={30}
              className="w-auto bg-white rounded-lg h-auto max-w-[30px]"
            />
          </button>
        </div>
        <Box
          sx={{
            border: "1px solid rgba(255, 255, 255, 0.2)",
            borderRadius: "8px",
            padding: "16px",
            color: "white",
            marginTop: "16px",
            backgroundColor: "rgba(255, 255, 255, 0.1)",
            backdropFilter: "blur(6px)",
            opacity: 0.7,
          }}
        >
          <ul className="mt-4">
            <li className="py-2 flex items-center">
              <IconLayoutDashboard className="mr-2 bg-black rounded-lg" />
              <Link href="/" passHref>
                <Button
                  variant="outlined"
                  color="primary"
                  sx={{ border: "none", color: "black" }}
                  fullWidth
                >
                  Home
                </Button>
              </Link>
            </li>
            <li className="py-2 flex items-center">
              <IconMessage className="mr-2 bg-black rounded-lg" />
              <Link href="/chat" passHref>
                <Button
                  variant="outlined"
                  color="primary"
                  sx={{ border: "none", color: "black" }}
                  fullWidth
                >
                  Chat
                </Button>
              </Link>
            </li>
            <li className="py-2 flex items-center">
              <IconPhone className="mr-2 bg-black rounded-lg" />
              <Link href="/contact" passHref>
                <Button
                  variant="outlined"
                  color="primary"
                  sx={{ border: "none", color: "black" }}
                  fullWidth
                >
                  Call
                </Button>
              </Link>
            </li>
          </ul>
        </Box>
      </div>
    </div>
  );
};

export default Sidebar;
