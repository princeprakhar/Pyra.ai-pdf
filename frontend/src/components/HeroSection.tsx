"use client";
import { useRouter } from "next/navigation";
import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";

interface HeroSectionProps {
  // Optional: if you want to pass an initial theme prop
  initialTheme?: "light" | "dark";
}

const HeroSection: React.FC<HeroSectionProps> = ({ initialTheme = "light" }) => {
  const router = useRouter();
  const mountRef = useRef<HTMLDivElement>(null);
  const [theme, setTheme] = useState<"light" | "dark">(initialTheme);

  // Observe <html> for .dark class changes
  useEffect(() => {
    const checkTheme = () => {
      const isDark = document.documentElement.classList.contains("dark");
      setTheme(isDark ? "dark" : "light");
    };

    // Check initial
    checkTheme();

    // Watch for changes
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => observer.disconnect();
  }, []);

  // Re-create or update the three.js scene if the theme changes
  useEffect(() => {
    if (!mountRef.current) return;

    // Create scene
    const scene = new THREE.Scene();
    const backgroundColor = theme === "dark" ? 0x0e0e0e : 0xf5f5f5;
    scene.background = new THREE.Color(backgroundColor);

    // Camera
    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 1.5, 5);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    mountRef.current.appendChild(renderer.domElement);

    // Plane geometry in wireframe
    const planeSize = 20;
    const segments = 40;
    const planeGeometry = new THREE.PlaneGeometry(planeSize, planeSize, segments, segments);
    const wireframeColor = theme === "dark" ? 0x555555 : 0x222222;
    const planeMaterial = new THREE.MeshBasicMaterial({
      color: wireframeColor,
      wireframe: true,
    });
    const planeMesh = new THREE.Mesh(planeGeometry, planeMaterial);
    planeMesh.rotation.x = -Math.PI / 2;
    scene.add(planeMesh);

    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
    scene.add(ambientLight);

    // Wave animation
    const positionAttribute = planeGeometry.attributes.position;
    const originalPositions = Float32Array.from(positionAttribute.array);

    let frameId: number;
    const animate = (time: number) => {
      frameId = requestAnimationFrame(animate);
      for (let i = 0; i < positionAttribute.count; i++) {
        const idx = i * 3;
        const x = originalPositions[idx];
        const y = originalPositions[idx + 1];
        const wave = Math.sin(time * 0.001 + x * 0.5 + y * 0.5) * 0.15;
        positionAttribute.setZ(i, wave);
      }
      positionAttribute.needsUpdate = true;

      renderer.render(scene, camera);
    };
    animate(0);

    // Resize handling
    const onWindowResize = () => {
      if (!mountRef.current) return;
      const width = mountRef.current.clientWidth;
      const height = mountRef.current.clientHeight;
      renderer.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    window.addEventListener("resize", onWindowResize);

    // Cleanup
    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener("resize", onWindowResize);
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      planeGeometry.dispose();
      planeMaterial.dispose();
      renderer.dispose();
    };
  }, [theme]);

  return (
    <section className="relative w-full h-screen overflow-hidden bg-white dark:bg-gray-900">
      <div ref={mountRef} className="w-full h-full" />

      {/* Overlay Content */}
      <div className="absolute top-1/2 left-1/2 flex flex-col items-center 
                      -translate-x-1/2 -translate-y-1/2 text-center">
        <h1
          className="
            mb-4 text-5xl font-extrabold 
            bg-gradient-to-r from-violet-600 via-pink-700 to-violet-800
            text-transparent bg-clip-text
          "
        >
          Welcome to Prakhar.ai
        </h1>
        <p className="mb-8 text-lg max-w-xl text-slate-700 dark:text-slate-200">
          A platform to learn and grow together. Explore our application and increase your productivity.
        </p>
        <div className="inline-flex gap-4">
          <button
            onClick={() => router.push("/about")}
            className="
              px-4 py-2 text-sm font-medium rounded-md
              bg-gradient-to-r from-violet-600 via-pink-700 to-violet-800
              text-white hover:from-pink-700 hover:via-violet-800 hover:to-pink-900
              dark:hover:bg-violet-700 transition-colors
            "
          >
            About Us
          </button>
          <button
            onClick={() => router.push("/auth/signup")}
            className="
              px-4 py-2 text-sm font-medium rounded-md
              bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-white
              hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors
            "
          >
            Quick Start
          </button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
