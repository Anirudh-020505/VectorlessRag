import { Canvas, useFrame } from "@react-three/fiber";
import { Float, RoundedBox, Text } from "@react-three/drei";
import { useRef, useMemo } from "react";
import * as THREE from "three";

/** A single floating card with levitation animation */
function LevitatingCard({ position, color, label }: { position: [number, number, number]; color: string; label: string }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const mat = useMemo(() => new THREE.MeshStandardMaterial({ color, roughness: 0.3, metalness: 0.1 }), [color]);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.5 + position[0]) * 0.15;
      meshRef.current.rotation.x = Math.cos(clock.elapsedTime * 0.4 + position[2]) * 0.08;
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.3} floatIntensity={1.2} floatingRange={[-0.15, 0.15]}>
      <group position={position}>
        <RoundedBox ref={meshRef} args={[1.8, 1.2, 0.08]} radius={0.1} smoothness={4} material={mat} castShadow />
        <Text
          position={[0, 0, 0.05]}
          fontSize={0.15}
          color="#333"
          anchorX="center"
          anchorY="middle"
          maxWidth={1.5}
        >
          {label}
        </Text>
      </group>
    </Float>
  );
}

/** Platform base under the cards */
function Platform() {
  return (
    <mesh position={[0, -1.2, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <cylinderGeometry args={[2.5, 2.5, 0.15, 32]} />
      <meshStandardMaterial color="hsl(30 30% 80%)" roughness={0.6} />
    </mesh>
  );
}

export function NodeSceneCanvas() {
  return (
    <div className="w-full h-48 rounded-xl overflow-hidden" style={{ background: "linear-gradient(180deg, hsl(200 40% 85%), hsl(180 30% 90%))" }}>
      <Canvas shadows camera={{ position: [0, 1.5, 4.5], fov: 40 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[3, 5, 3]} intensity={0.8} castShadow />
        <pointLight position={[-2, 2, 1]} intensity={0.3} color="#88ccff" />

        <Platform />

        <LevitatingCard position={[-1.5, 0.2, 0]} color="#a8d8ea" label="Scene A" />
        <LevitatingCard position={[0, 0.5, -0.5]} color="#c4e0c4" label="Scene B" />
        <LevitatingCard position={[1.5, 0.3, 0.3]} color="#e8d5b7" label="Scene C" />
      </Canvas>
    </div>
  );
}
