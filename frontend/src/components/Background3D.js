import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Stars, Float } from '@react-three/drei';
import * as THREE from 'three';

// Map emotions to colors
const emotionColors = {
  'happy': '#FFD700',    // Gold
  'sad': '#1E90FF',      // Blue
  'angry': '#FF4500',    // Red
  'neutral': '#ffffff',  // White
  'fear': '#800080',     // Purple
  'surprise': '#FF69B4', // Pink
  'disgust': '#00FF00',  // Green
  '': '#00bcd4'          // Default Cyan
};

function Particles({ count = 200, color }) {
  const mesh = useRef();
  
  const particles = useMemo(() => {
    const temp = [];
    for (let i = 0; i < count; i++) {
      const t = Math.random() * 100;
      const factor = 20 + Math.random() * 100;
      const speed = 0.01 + Math.random() / 200;
      const xFactor = -50 + Math.random() * 100;
      const yFactor = -50 + Math.random() * 100;
      const zFactor = -50 + Math.random() * 100;
      temp.push({ t, factor, speed, xFactor, yFactor, zFactor, mx: 0, my: 0 });
    }
    return temp;
  }, [count]);

  const dummy = useMemo(() => new THREE.Object3D(), []);

  useFrame((state) => {
    mesh.current.rotation.y += 0.001;
    mesh.current.rotation.z += 0.0005;

    particles.forEach((particle, i) => {
      let { t, factor, speed, xFactor, yFactor, zFactor } = particle;
      t = particle.t += speed / 2;
      const s = Math.cos(t);
      
      dummy.position.set(
        (particle.mx / 10) * Math.cos(t) + xFactor + Math.cos((t / 10) * factor) + (Math.sin(t * 1) * factor) / 10,
        (particle.my / 10) * Math.sin(t) + yFactor + Math.sin((t / 10) * factor) + (Math.cos(t * 2) * factor) / 10,
        (particle.my / 10) * Math.cos(t) + zFactor + Math.cos((t / 10) * factor) + (Math.sin(t * 3) * factor) / 10
      );
      dummy.scale.set(s, s, s);
      dummy.rotation.set(s * 5, s * 5, s * 5);
      dummy.updateMatrix();
      mesh.current.setMatrixAt(i, dummy.matrix);
    });
    mesh.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={mesh} args={[null, null, count]}>
      <dodecahedronGeometry args={[0.2, 0]} />
      <meshPhongMaterial color={color} transparent opacity={0.8} />
    </instancedMesh>
  );
}

function Scene({ emotion }) {
  const targetColor = emotionColors[emotion?.toLowerCase()] || emotionColors[''];
  
  return (
    <>
      <color attach="background" args={['#050505']} />
      <fog attach="fog" args={['#050505', 5, 30]} />
      
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} color={targetColor} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="white" />
      
      <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
         <Particles count={300} color={targetColor} />
      </Float>
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
    </>
  );
}

export default function Background3D({ emotion }) {
  return (
    <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', zIndex: -1 }}>
      <Canvas camera={{ position: [0, 0, 15], fov: 45 }}>
        <Scene emotion={emotion} />
      </Canvas>
    </div>
  );
}