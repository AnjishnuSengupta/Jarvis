import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';

export default function VoiceWaveform({ state, amplitude = 0 }) {
  const group = useRef();
  const numBars = 32;

  const bars = useMemo(() => {
    return new Array(numBars).fill(0).map((_, i) => {
      const angle = (i / numBars) * Math.PI * 2;
      return { angle, index: i };
    });
  }, [numBars]);

  useFrame(({ clock }) => {
    if (state !== 'speaking' && state !== 'listening') {
      group.current.scale.setScalar(0.01);
      return;
    }
    
    // Animate the bars
    const time = clock.getElapsedTime();
    group.current.children.forEach((child, i) => {
      const targetScale = 1 + amplitude * 5 * Math.sin(time * 10 + i);
      child.scale.y += (targetScale - child.scale.y) * 0.2;
    });
    
    group.current.scale.setScalar(1);
    group.current.rotation.y = time * 0.5;
  });

  const getColor = () => {
    return state === 'listening' ? '#00ffcc' : '#00aaff';
  };

  return (
    <group ref={group}>
      {bars.map((bar) => (
        <mesh 
          key={bar.index}
          position={[Math.cos(bar.angle) * 3, 0, Math.sin(bar.angle) * 3]}
          rotation={[0, -bar.angle, 0]}
        >
          <boxGeometry args={[0.1, 1, 0.1]} />
          <meshBasicMaterial color={getColor()} />
        </mesh>
      ))}
    </group>
  );
}
