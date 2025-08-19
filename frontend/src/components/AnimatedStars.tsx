// AnimatedStars.tsx
import { useEffect, useRef } from "react";

export default function AnimatedStars() {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const createSparkle = () => {
      const sparkle = document.createElement("div");
      sparkle.className = "sparkle";
      sparkle.style.left = `${Math.random() * 100}%`;
      sparkle.style.top = `${Math.random() * 100}%`;
      sparkle.style.animationDuration = `${2 + Math.random() * 3}s`;
      container.appendChild(sparkle);
      setTimeout(() => sparkle.remove(), 5000);
    };

    const interval = setInterval(createSparkle, 200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      ref={containerRef}
      className="starfield-overlay"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        zIndex: 99999, // AUMENTADO para asegurar que esté encima
        pointerEvents: "none",
        overflow: "hidden",
        mixBlendMode: "screen", // mejora el efecto sobre fondos oscuros
      }}
    />
  );
}
