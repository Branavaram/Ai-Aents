"use client";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Text, Html, Grid } from "@react-three/drei";
import { Suspense, useRef, useMemo } from "react";
import * as THREE from "three";
import type { Agent } from "../lib/api";

type Status = "idle" | "waiting" | "working" | "walking" | "done";

type Props = {
  agents: Agent[];
  statuses: Record<string, Status>;
  bubbles: Record<string, string>;
  walkingTo: Record<string, string>;
};

// Convert 2D screen % positions → 3D world coordinates
// desk Y: 0.5 (just above the floor)
// Alex at back of room, team in front
const WORLD = {
  width: 20,     // x-axis span
  depth: 14,     // z-axis span
};

function screenPosToWorld(agent: Agent, isAlex: boolean): [number, number, number] {
  // 0-100% → -half to +half
  const x = (agent.position - 50) / 50 * (WORLD.width / 2 - 2);
  const z = isAlex ? -WORLD.depth / 2 + 2 : WORLD.depth / 2 - 3;
  return [x, 0, z];
}

/** A single robot — capsule body + head + glowing ring */
function Robot({ agent, status, bubble, position }: {
  agent: Agent;
  status: Status;
  bubble?: string;
  position: [number, number, number];
}) {
  const bodyRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const groupRef = useRef<THREE.Group>(null);

  const color = useMemo(() => new THREE.Color(agent.color), [agent.color]);

  // Animate position smoothly (walking)
  useFrame((state, delta) => {
    if (!groupRef.current) return;

    // Smooth position lerp
    const target = new THREE.Vector3(...position);
    groupRef.current.position.lerp(target, 0.05);

    // Bounce when working
    if (status === "working" && bodyRef.current) {
      bodyRef.current.position.y = 1.2 + Math.sin(state.clock.elapsedTime * 4) * 0.15;
    } else if (bodyRef.current) {
      bodyRef.current.position.y = 1.2;
    }

    // Walking wobble
    if (status === "walking" && groupRef.current) {
      groupRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 8) * 0.08;
    } else if (groupRef.current) {
      groupRef.current.rotation.z = THREE.MathUtils.lerp(groupRef.current.rotation.z, 0, 0.1);
    }

    // Rotate ring
    if (ringRef.current && (status === "working" || status === "walking")) {
      ringRef.current.rotation.y += delta * 2;
    }
  });

  const glowIntensity =
    status === "working" ? 1.5 :
    status === "done" ? 0.8 :
    status === "walking" ? 1.0 :
    0.2;

  return (
    <group ref={groupRef} position={position}>
      {/* Floor glow ring */}
      <mesh ref={ringRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}>
        <ringGeometry args={[0.9, 1.2, 32]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.3 + glowIntensity * 0.4}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Robot body (capsule) */}
      <mesh ref={bodyRef} position={[0, 1.2, 0]} castShadow>
        <capsuleGeometry args={[0.5, 1.4, 8, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={glowIntensity * 0.5}
          metalness={0.6}
          roughness={0.3}
        />
      </mesh>

      {/* Robot head (sphere) */}
      <mesh position={[0, 2.6, 0]} castShadow>
        <sphereGeometry args={[0.45, 32, 32]} />
        <meshStandardMaterial
          color="#1a1a2e"
          emissive={color}
          emissiveIntensity={0.3}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* Eyes (glowing dots) */}
      <mesh position={[-0.15, 2.65, 0.4]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshBasicMaterial color={status === "working" ? "#00f0ff" : color} />
      </mesh>
      <mesh position={[0.15, 2.65, 0.4]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshBasicMaterial color={status === "working" ? "#00f0ff" : color} />
      </mesh>

      {/* Name tag + emoji above head */}
      <Html position={[0, 3.6, 0]} center distanceFactor={10}>
        <div className="flex flex-col items-center pointer-events-none select-none">
          <div
            className="text-xs font-bold px-2 py-0.5 rounded-md border backdrop-blur"
            style={{
              color: agent.color,
              borderColor: agent.color,
              background: "rgba(10,10,26,0.9)",
              textShadow: `0 0 8px ${agent.color}`,
            }}
          >
            {agent.emoji} {agent.name}
          </div>
          {bubble && (
            <div
              className="mt-1 text-[10px] px-2 py-1 rounded max-w-[180px] text-center backdrop-blur border"
              style={{
                color: "#e8e8f0",
                borderColor: agent.color,
                background: "rgba(10,10,26,0.95)",
                boxShadow: `0 0 12px ${agent.color}60`,
              }}
            >
              {bubble}
            </div>
          )}
        </div>
      </Html>

      {/* Status indicator (floating ball above) */}
      {status === "working" && (
        <mesh position={[0.6, 2.5, 0]}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshBasicMaterial color="#fff700" />
        </mesh>
      )}
      {status === "done" && (
        <mesh position={[0.6, 2.5, 0]}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshBasicMaterial color="#00ff9f" />
        </mesh>
      )}
    </group>
  );
}

/** The office room — floor, walls, ceiling, desks */
function OfficeRoom() {
  return (
    <group>
      {/* Floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[WORLD.width, WORLD.depth]} />
        <meshStandardMaterial
          color="#0a0a1a"
          metalness={0.4}
          roughness={0.6}
        />
      </mesh>

      {/* Neon grid overlay on floor */}
      <Grid
        args={[WORLD.width, WORLD.depth]}
        position={[0, 0.01, 0]}
        cellColor="#2a2a44"
        sectionColor="#00f0ff"
        sectionSize={5}
        fadeDistance={30}
        fadeStrength={1}
      />

      {/* Back wall (Alex side) */}
      <mesh position={[0, 3, -WORLD.depth / 2]} receiveShadow>
        <planeGeometry args={[WORLD.width, 6]} />
        <meshStandardMaterial color="#10101f" />
      </mesh>

      {/* Side walls */}
      <mesh position={[-WORLD.width / 2, 3, 0]} rotation={[0, Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[WORLD.depth, 6]} />
        <meshStandardMaterial color="#10101f" />
      </mesh>
      <mesh position={[WORLD.width / 2, 3, 0]} rotation={[0, -Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[WORLD.depth, 6]} />
        <meshStandardMaterial color="#10101f" />
      </mesh>

      {/* Neon strip lights along back wall */}
      <mesh position={[0, 5.2, -WORLD.depth / 2 + 0.05]}>
        <boxGeometry args={[WORLD.width - 1, 0.15, 0.1]} />
        <meshBasicMaterial color="#00f0ff" />
      </mesh>
      <mesh position={[0, 0.8, -WORLD.depth / 2 + 0.05]}>
        <boxGeometry args={[WORLD.width - 1, 0.15, 0.1]} />
        <meshBasicMaterial color="#ff00e0" />
      </mesh>

      {/* Central brain pedestal */}
      <mesh position={[0, 0.5, 0]} castShadow>
        <cylinderGeometry args={[1.2, 1.4, 1, 32]} />
        <meshStandardMaterial
          color="#1a1a2e"
          emissive="#a855f7"
          emissiveIntensity={0.4}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* Floating brain sphere */}
      <mesh position={[0, 2, 0]}>
        <sphereGeometry args={[0.8, 32, 32]} />
        <meshStandardMaterial
          color="#a855f7"
          emissive="#a855f7"
          emissiveIntensity={1}
          transparent
          opacity={0.6}
        />
      </mesh>
      <Html position={[0, 3.3, 0]} center distanceFactor={8}>
        <div className="text-[10px] font-bold tracking-widest text-[#c084fc] whitespace-nowrap pointer-events-none select-none"
          style={{ textShadow: "0 0 10px #a855f7" }}>
          🧠 SHARED BRAIN
        </div>
      </Html>
    </group>
  );
}

/** Walking path lines between agents (visualize who's walking where) */
function WalkingPaths({
  walkingTo,
  agents,
}: {
  walkingTo: Record<string, string>;
  agents: Agent[];
}) {
  return (
    <>
      {Object.entries(walkingTo).map(([from, to]) => {
        const fromAgent = agents.find(a => a.key === from);
        const toAgent = agents.find(a => a.key === to);
        if (!fromAgent || !toAgent) return null;
        const src = screenPosToWorld(fromAgent, from === "alex");
        const tgt = screenPosToWorld(toAgent, to === "alex");
        const points = [new THREE.Vector3(...src), new THREE.Vector3(...tgt)];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        return (
          <line key={from}>
            <primitive object={geometry} attach="geometry" />
            <lineDashedMaterial
              color={fromAgent.color}
              dashSize={0.3}
              gapSize={0.2}
              linewidth={2}
            />
          </line>
        );
      })}
    </>
  );
}

/** The main 3D canvas */
export default function Office3D({ agents, statuses, bubbles, walkingTo }: Props) {
  return (
    <div className="w-full h-[600px] bg-[var(--bg-deep)] rounded-2xl border border-[var(--border)] overflow-hidden relative">
      {/* HUD overlay */}
      <div className="absolute top-3 left-1/2 -translate-x-1/2 text-[10px] tracking-[0.4em] font-bold text-[var(--text-muted)] z-10">
        🏢  3D OFFICE FLOOR
      </div>
      <div className="absolute bottom-3 right-3 text-[10px] text-[var(--text-muted)] z-10 bg-[var(--bg-void)]/80 px-2 py-1 rounded border border-[var(--border)]">
        🖱️ Drag to rotate · Scroll to zoom
      </div>

      <Canvas
        shadows
        camera={{ position: [0, 8, 14], fov: 50 }}
        dpr={[1, 2]}
      >
        <Suspense fallback={null}>
          {/* Lighting */}
          <ambientLight intensity={0.3} />
          <directionalLight
            position={[10, 15, 10]}
            intensity={0.8}
            castShadow
            shadow-mapSize={[2048, 2048]}
          />
          <pointLight position={[0, 6, 0]} intensity={0.5} color="#a855f7" />
          <pointLight position={[-8, 4, 4]} intensity={0.3} color="#00f0ff" />
          <pointLight position={[8, 4, 4]} intensity={0.3} color="#ff00e0" />

          {/* Scene */}
          <OfficeRoom />

          {/* Robots */}
          {agents.map(agent => {
            const isAlex = agent.key === "alex";
            const walkTarget = walkingTo[agent.key];
            let pos = screenPosToWorld(agent, isAlex);
            if (walkTarget) {
              const tgt = agents.find(a => a.key === walkTarget);
              if (tgt) {
                const tgtPos = screenPosToWorld(tgt, walkTarget === "alex");
                pos = [tgtPos[0] + 1.5, 0, tgtPos[2] + 1.5];
              }
            }
            return (
              <Robot
                key={agent.key}
                agent={agent}
                status={statuses[agent.key] || "idle"}
                bubble={bubbles[agent.key]}
                position={pos}
              />
            );
          })}

          <WalkingPaths walkingTo={walkingTo} agents={agents} />

          {/* Camera controls */}
          <OrbitControls
            enableDamping
            dampingFactor={0.05}
            minDistance={8}
            maxDistance={30}
            maxPolarAngle={Math.PI / 2.2}
            target={[0, 1, 0]}
          />

          {/* Fog for depth */}
          <fog attach="fog" args={["#050510", 15, 40]} />
        </Suspense>
      </Canvas>
    </div>
  );
}
