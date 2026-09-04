import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Torus } from '@react-three/drei';

export default function OrbitingRings({ state }) {
  const outerRing = useRef();
  const innerRing = useRef();

  useFrame(({ clock }) => {
    const speed = state === 'idle' ? 1 : state === 'listening' ? 3 : state === 'thinking' ? 5 : 2;
    outerRing.current.rotation.x = clock.getElapsedTime() * speed * 0.5;
    outerRing.current.rotation.y = clock.getElapsedTime() * speed * 0.3;
    
    innerRing.current.rotation.x = clock.getElapsedTime() * speed * 0.7;
    innerRing.current.rotation.z = clock.getElapsedTime() * speed * 0.4;
  });

  const getColor = () => {
    switch(state) {
      case 'listening': return '#00ffcc';
      case 'thinking': return '#ffaa00';
      case 'speaking': return '#00aaff';
      default: return '#00d2ff';
    }
  };

  return (
    <group>
      <Torus ref={outerRing} args={[2.5, 0.05, 16, 100]} rotation={[Math.PI/2, 0, 0]}>
        <meshStandardMaterial color={getColor()} emissive={getColor()} emissiveIntensity={1} wireframe />
      </Torus>
      <Torus ref={innerRing} args={[1.8, 0.02, 16, 100]} rotation={[0, Math.PI/2, 0]}>
        <meshStandardMaterial color={getColor()} emissive={getColor()} emissiveIntensity={0.8} />
      </Torus>
    </group>
  );
}
