import React, { useState } from "react";
import { motion } from "framer-motion";

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
      style={{ width: "100vw", height: "100vh", position: "relative", background: "#F9F9F9", overflow: "hidden" }}
    >

      {!active && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            textAlign: "center",
            zIndex: 10,
            color: "#2D2D2D",
            pointerEvents: "none", 
          }}
        >
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 1 }}
          >
            <h1 style={{ fontSize: "5rem", margin: 0, fontWeight: "900", letterSpacing: "-2px", color: "#2D2D2D" }}>
              EMOTION <span style={{ color: "#007BFF" }}>SENSE</span>
              <span style={{ 
                background: "#FFD700", 
                color: "#2D2D2D", 
                fontSize: "1rem", 
                padding: "4px 10px", 
                borderRadius: "12px", 
                marginLeft: "15px", 
                verticalAlign: "super", 
                fontWeight: "bold",
                letterSpacing: "0px",
                display: "inline-block",
                transform: "translateY(-15px)"
              }}>LIVE</span>
            </h1>
            <p style={{ letterSpacing: "4px", marginTop: "10px", color: "#2D2D2D" }}>
              GAME RECOMMENDER SYSTEM
            </p>
          </motion.div>

          <motion.button
            style={{
              marginTop: "3rem",
              background: "#007BFF",
              border: "none",
              color: "#F9F9F9",
              padding: "15px 50px",
              fontSize: "1.2rem",
              fontWeight: "bold",
              borderRadius: "50px",
              cursor: "pointer",
              pointerEvents: "auto",
              letterSpacing: "2px",
              boxShadow: "0 6px 15px rgba(0, 123, 255, 0.3)",
              transition: "background 0.3s ease"
            }}
            whileHover={{ scale: 1.05, background: "#0056b3", boxShadow: "0 10px 25px rgba(0, 123, 255, 0.5)" }}
            whileTap={{ scale: 0.95, background: "#003d82" }}
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