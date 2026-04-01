'use client';

import { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment, Float, MeshDistortMaterial, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';
import type { TelemetryValue } from '@/lib/types';

function Reactor({ telemetry }: { telemetry: TelemetryValue[] }) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // Find Reactor Temperature in UNS-mapped telemetry
  const tempSignal = telemetry.find(s => s.tagName.includes('Reactor_05') && s.tagName.includes('Temperature'));
  const tempValue = tempSignal?.value ?? 65;
  const isCritical = tempValue > 90;

  useFrame((state) => {
    if (!meshRef.current) return;
    const t = state.clock.getElapsedTime();
    
    // Subtle breathing animation
    const scale = 1 + Math.sin(t * 2) * 0.02;
    meshRef.current.scale.set(scale, scale, scale);
  });

  // Calculate emissive color based on temperature
  // Baseline (65) = cool teal, High (>90) = glowing red
  const heatFactor = Math.max(0, Math.min(1, (tempValue - 65) / 30));
  const color = new THREE.Color().lerpColors(
    new THREE.Color('#2dd4bf'), // Teal-400
    new THREE.Color('#ef4444'), // Red-500
    heatFactor
  );

  return (
    <group position={[-2, 0, 0]}>
      <mesh ref={meshRef} position={[0, 1.5, 0]}>
        <cylinderGeometry args={[1, 1.2, 3, 32]} />
        <meshStandardMaterial 
          color="#1e293b" 
          emissive={color} 
          emissiveIntensity={isCritical ? 2 + Math.sin(Date.now() * 0.01) * 1 : heatFactor * 0.8}
          roughness={0.1}
          metalness={0.8}
        />
      </mesh>
      {/* Label placeholder in 3D */}
      <mesh position={[0, 3.5, 0]}>
        <boxGeometry args={[1.5, 0.2, 0.1]} />
        <meshStandardMaterial color="#0f172a" />
      </mesh>
    </group>
  );
}

function Crusher({ telemetry }: { telemetry: TelemetryValue[] }) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // Find Crusher Vibration in UNS-mapped telemetry
  const vibeSignal = telemetry.find(s => s.tagName.includes('Cement_Crusher') && s.tagName.includes('Vibration'));
  const vibeValue = vibeSignal?.value ?? 2.5;
  const isCritical = vibeValue > 10;

  useFrame((state) => {
    if (!meshRef.current) return;
    if (vibeValue > 3) {
      // Shaking animation proportional to vibration value
      const intensity = (vibeValue - 2.5) * 0.01;
      meshRef.current.position.x = (Math.random() - 0.5) * intensity;
      meshRef.current.position.y = 1 + (Math.random() - 0.5) * intensity;
      meshRef.current.position.z = (Math.random() - 0.5) * intensity;
    } else {
      meshRef.current.position.set(0, 1, 0);
    }
  });

  return (
    <group position={[2, 0, 0]}>
      <mesh ref={meshRef} position={[0, 1, 0]}>
        <boxGeometry args={[2, 2, 2]} />
        <meshStandardMaterial 
          color={isCritical ? "#f59e0b" : "#475569"} 
          roughness={0.3}
          metalness={0.5}
        />
      </mesh>
       {/* Details */}
       <mesh position={[0, 2.2, 0]}>
        <cylinderGeometry args={[0.5, 0.5, 0.5, 16]} />
        <meshStandardMaterial color="#1e293b" />
      </mesh>
    </group>
  );
}

export default function ThreeScene({ telemetry }: { telemetry: TelemetryValue[] }) {
  return (
    <div className="w-full h-full min-h-[400px] bg-slate-950/20 rounded-3xl overflow-hidden relative border border-slate-800/50">
      <div className="absolute top-4 left-6 z-10">
        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">Spatial Projection</h3>
        <p className="text-xs font-bold text-teal-400">Active Real-time Rendering</p>
      </div>

      <Canvas shadows dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[0, 5, 10]} fov={40} />
        <OrbitControls 
          enablePan={false} 
          minDistance={5} 
          maxDistance={15} 
          maxPolarAngle={Math.PI / 2.1}
          autoRotate
          autoRotateSpeed={0.5}
        />
        
        <ambientLight intensity={0.5} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />

        <Suspense fallback={null}>
          <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.5}>
            <Reactor telemetry={telemetry} />
            <Crusher telemetry={telemetry} />
          </Float>
          
          <ContactShadows 
            position={[0, -0.5, 0]} 
            opacity={0.4} 
            scale={20} 
            blur={2} 
            far={4.5} 
          />
          <Environment preset="city" />
        </Suspense>
        
        <gridHelper args={[20, 20, 0x1e293b, 0x0f172a]} position={[0, -0.51, 0]} />
      </Canvas>

      <div className="absolute bottom-4 right-6 text-right pointer-events-none">
        <div className="text-[10px] font-black text-slate-700 uppercase tracking-widest leading-tight">
          Mesh: Industrial-Pack-01<br />
          Engine: WebGL v2.0
        </div>
      </div>
    </div>
  );
}
