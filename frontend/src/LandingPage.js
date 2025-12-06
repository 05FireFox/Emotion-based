import React, { useState, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Stars, Sparkles } from "@react-three/drei";
import { motion } from "framer-motion";

function StarField({ active }) {
  const ref = useRef();
  
  useFrame((state, delta) => {
    if (ref.current) {
      // Rotation speed increases if active (clicked)
      const speed = active ? 2 : 0.05;
      ref.current.rotation.y -= delta * speed;
      ref.current.rotation.x -= delta * (speed * 0.5);
      
      // Move camera forward effect if active
      if (active) {
         state.camera.position.z -= delta * 10;
      }
    }
  });

  return (
    <group ref={ref}>
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      <Sparkles count={200} scale={10} size={2} speed={0.4} opacity={0.5} color="#00E0FF" />
    </group>
  );
}

const LandingPage = ({ onEnter }) => {
  const [active, setActive] = useState(false);

  const handleClick = () => {
    setActive(true);
    // Delay actual transition to allow animation to play
    setTimeout(onEnter, 1200);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{ width: "100vw", height: "100vh", position: "relative", background: "black", overflow: "hidden" }}
    >
      <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}>
        <Canvas camera={{ position: [0, 0, 5], fov: 60 }}>
          <StarField active={active} />
          <ambientLight intensity={0.5} />
        </Canvas>
      </div>

      {!active && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            textAlign: "center",
            zIndex: 10,
            color: "white",
            pointerEvents: "none", 
          }}
        >
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 1 }}
          >
            <h1 style={{ fontSize: "5rem", margin: 0, fontWeight: "800", letterSpacing: "-2px" }}>
              EMOTION <span style={{ color: "#00E0FF" }}>SENSE</span>
            </h1>
            <p style={{ letterSpacing: "4px", marginTop: "10px", color: "#aaa" }}>
              GAME RECOMMENDER SYSTEM
            </p>
          </motion.div>

          <motion.button
            style={{
              marginTop: "3rem",
              background: "rgba(0, 224, 255, 0.1)",
              border: "1px solid #00E0FF",
              color: "#00E0FF",
              padding: "15px 50px",
              fontSize: "1.2rem",
              borderRadius: "50px",
              cursor: "pointer",
              pointerEvents: "auto",
              backdropFilter: "blur(5px)",
              letterSpacing: "2px",
            }}
            whileHover={{ scale: 1.1, background: "rgba(0, 224, 255, 0.2)", boxShadow: "0 0 20px rgba(0,224,255,0.4)" }}
            whileTap={{ scale: 0.95 }}
            onClick={handleClick}
          >
            INITIALIZE SYSTEM
          </motion.button>
        </div>
      )}
    </motion.div>
  );
};

export default LandingPage;