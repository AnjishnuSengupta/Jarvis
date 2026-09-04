import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { MeshDistortMaterial, Sphere } from '@react-three/drei';

export default function ArcReactorCore({ state }) {
  const meshRef = useRef();

  useFrame(({ clock }) => {
    // Pulse faster when thinking or speaking
    const speed = state === 'idle' ? 1 : state === 'listening' ? 2 : 4;
    meshRef.current.rotation.y = clock.getElapsedTime() * speed;
    
    // Slight breathing effect
    const scale = 1 + Math.sin(clock.getElapsedTime() * speed) * 0.05;
    meshRef.current.scale.set(scale, scale, scale);
  });

  const getCoreColor = () => {
    switch(state) {
      case 'listening': return '#00ffcc';
      case 'thinking': return '#ffaa00';
      case 'speaking': return '#00aaff';
      default: return '#00d2ff'; // idle blue
    }
  };

  return (
    <Sphere ref={meshRef} args={[1, 64, 64]}>
      <MeshDistortMaterial
        color={getCoreColor()}
        attach="material"
        distort={state === 'thinking' ? 0.6 : 0.3}
        speed={state === 'idle' ? 1 : 3}
        roughness={0}
        metalness={0.8}
        emissive={getCoreColor()}
        emissiveIntensity={1.5}
      />
    </Sphere>
  );
}
