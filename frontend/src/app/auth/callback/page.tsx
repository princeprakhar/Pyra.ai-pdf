"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Callback() {
  const router = useRouter();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("access_token");

    if (token) {
      localStorage.setItem("Token", token);
      // Optionally, remove the token from the URL if needed:
      router.replace("/chat");
    } else {
      // Handle error or redirect to login if no token is present
      router.push("/signin");
    }
  }, [router]);

  return <div>Loading...</div>;
}
