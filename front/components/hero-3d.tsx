"use client";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Line, Sphere, MeshDistortMaterial } from "@react-three/drei";
import { Suspense, useMemo, useRef } from "react";
import * as THREE from "three";

const GOLD = "#daa112";
const GOLD_SOFT = "#f0c755";
const DEEP = "#10383a";
const CREAM = "#f7f1e0";

/* Logistics network nodes positioned on a sphere */
const NODE_COUNT = 14;
function fibonacciSphere(samples: number, radius = 1.9) {
  const points: THREE.Vector3[] = [];
  const phi = Math.PI * (Math.sqrt(5) - 1);
  for (let i = 0; i < samples; i++) {
    const y = 1 - (i / (samples - 1)) * 2;
    const r = Math.sqrt(1 - y * y);
    const theta = phi * i;
    points.push(
      new THREE.Vector3(Math.cos(theta) * r, y, Math.sin(theta) * r).multiplyScalar(radius),
    );
  }
  return points;
}

function Globe() {
  const meshRef = useRef<THREE.Mesh>(null!);
  useFrame((_, dt) => {
    if (meshRef.current) meshRef.current.rotation.y += dt * 0.08;
  });
  return (
    <mesh ref={meshRef}>
      <icosahedronGeometry args={[1.6, 3]} />
      <meshStandardMaterial
        color={DEEP}
        wireframe
        emissive={GOLD}
        emissiveIntensity={0.15}
        transparent
        opacity={0.55}
      />
    </mesh>
  );
}

function Core() {
  const ref = useRef<THREE.Mesh>(null!);
  useFrame((_, dt) => {
    if (ref.current) {
      ref.current.rotation.y -= dt * 0.2;
      ref.current.rotation.x += dt * 0.05;
    }
  });
  return (
    <Sphere ref={ref} args={[1.15, 64, 64]}>
      <MeshDistortMaterial
        color={DEEP}
        emissive={GOLD}
        emissiveIntensity={0.25}
        distort={0.35}
        speed={1.2}
        roughness={0.2}
        metalness={0.8}
      />
    </Sphere>
  );
}

function Nodes() {
  const points = useMemo(() => fibonacciSphere(NODE_COUNT, 1.9), []);
  const group = useRef<THREE.Group>(null!);
  useFrame((_, dt) => {
    if (group.current) group.current.rotation.y += dt * 0.08;
  });
  return (
    <group ref={group}>
      {points.map((p, i) => (
        <Float
          key={i}
          speed={1.5 + (i % 3) * 0.5}
          rotationIntensity={0.4}
          floatIntensity={0.5}
        >
          <mesh position={[p.x, p.y, p.z]}>
            <sphereGeometry args={[0.06, 16, 16]} />
            <meshStandardMaterial
              color={GOLD}
              emissive={GOLD_SOFT}
              emissiveIntensity={1.2}
            />
          </mesh>
        </Float>
      ))}
      {/* arcs between selected nodes */}
      {points.slice(0, NODE_COUNT - 1).map((p, i) => {
        const q = points[(i + 3) % points.length];
        const mid = p.clone().add(q).multiplyScalar(0.5).multiplyScalar(1.25);
        const curve = new THREE.QuadraticBezierCurve3(p, mid, q);
        const vertices = curve.getPoints(24);
        return (
          <Line
            key={`arc-${i}`}
            points={vertices.map((v) => [v.x, v.y, v.z])}
            color={GOLD}
            transparent
            opacity={0.35}
            lineWidth={1}
          />
        );
      })}
    </group>
  );
}

function Particles() {
  const ref = useRef<THREE.Points>(null!);
  const positions = useMemo(() => {
    const arr = new Float32Array(400 * 3);
    for (let i = 0; i < 400; i++) {
      const r = 3 + Math.random() * 2;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      arr[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      arr[i * 3 + 2] = r * Math.cos(phi);
    }
    return arr;
  }, []);
  useFrame((_, dt) => {
    if (ref.current) ref.current.rotation.y += dt * 0.03;
  });
  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        color={CREAM}
        size={0.015}
        sizeAttenuation
        transparent
        opacity={0.5}
      />
    </points>
  );
}

export default function Hero3D() {
  return (
    <Canvas
      camera={{ position: [0, 0, 5.5], fov: 45 }}
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true }}
      className="!absolute inset-0"
    >
      <Suspense fallback={null}>
        <ambientLight intensity={0.35} />
        <directionalLight position={[5, 5, 5]} intensity={1.1} color={GOLD_SOFT} />
        <pointLight position={[-5, -3, -5]} intensity={0.6} color={GOLD} />
        <Core />
        <Globe />
        <Nodes />
        <Particles />
      </Suspense>
    </Canvas>
  );
}
