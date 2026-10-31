import React, { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float } from '@react-three/drei';
import * as THREE from 'three';
import { avatarVoiceState } from '../utils/avatarState';

// Pre-allocated static Three.js objects to prevent GC frame drops (60fps lock)
const COLOR_CYAN = new THREE.Color('#00f2fe');
const COLOR_BLUE = new THREE.Color('#38bdf8');
const COLOR_VIOLET = new THREE.Color('#8b5cf6');
const VEC3_ONE = new THREE.Vector3(1, 1, 1);

// ---------------------------------------------------------------------------
// 3D Stylized Android Humanoid Bust with Expressive Behavioral Gestures
// ---------------------------------------------------------------------------
function AndroidBust({ mousePos }) {
  const headGroupRef = useRef();
  const jawRef = useRef();
  const neckRef = useRef();
  const eyesRef = useRef();
  const coreRef = useRef();
  const torsoRef = useRef();
  const ringRef = useRef();
  const haloMaterialRef = useRef();

  // Reusable materials with cybernetic glass & emissive aesthetics
  const materials = useMemo(() => {
    const haloMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#00f2fe'),
      emissive: new THREE.Color('#00f2fe'),
      emissiveIntensity: 2.2,
      roughness: 0.1,
    });
    haloMaterialRef.current = haloMat;

    return {
      armorDark: new THREE.MeshStandardMaterial({
        color: new THREE.Color('#0f172a'),
        roughness: 0.25,
        metalness: 0.85,
        flatShading: true,
      }),
      armorPlate: new THREE.MeshStandardMaterial({
        color: new THREE.Color('#1e293b'),
        roughness: 0.3,
        metalness: 0.7,
        flatShading: true,
      }),
      eyesGlow: new THREE.MeshStandardMaterial({
        color: new THREE.Color('#00f2fe'),
        emissive: new THREE.Color('#00f2fe'),
        emissiveIntensity: 2.2,
        roughness: 0.1,
      }),
      haloGlow: haloMat,
      neonViolet: new THREE.MeshStandardMaterial({
        color: new THREE.Color('#8b5cf6'),
        emissive: new THREE.Color('#8b5cf6'),
        emissiveIntensity: 1.8,
        roughness: 0.2,
      }),
      visorGlass: new THREE.MeshPhysicalMaterial({
        color: new THREE.Color('#002233'),
        emissive: new THREE.Color('#00f2fe'),
        emissiveIntensity: 0.6,
        roughness: 0.1,
        metalness: 0.9,
        transparent: true,
        opacity: 0.92,
        reflectivity: 1,
      }),
      chromeJoint: new THREE.MeshStandardMaterial({
        color: new THREE.Color('#64748b'),
        metalness: 0.95,
        roughness: 0.15,
      }),
      wireframeAcc: new THREE.MeshBasicMaterial({
        color: new THREE.Color('#38bdf8'),
        wireframe: true,
        transparent: true,
        opacity: 0.28,
      }),
    };
  }, []);

  useFrame((state, delta) => {
    // Read state from high-performance store directly inside 60fps frame loop
    const { isListening, isSpeaking, audioLevel } = avatarVoiceState;
    const time = state.clock.getElapsedTime();

    // Raw normalized mouse coordinates
    const targetMouseY = mousePos.current.x * 0.55;
    const targetMouseX = -mousePos.current.y * 0.35;

    // -------------------------------------------------------------------------
    // 1. BEHAVIORAL GESTURES: LISTENING vs. SPEAKING vs. IDLE
    // -------------------------------------------------------------------------

    if (isListening) {
      // --- ATTENTIVE TILT & LOCK (Listening to User) ---
      // Head tilts slightly (~4.2 degrees roll on Z) simulating focused human listening
      const targetTiltZ = 0.075;
      if (headGroupRef.current) {
        headGroupRef.current.rotation.z = THREE.MathUtils.lerp(
          headGroupRef.current.rotation.z,
          targetTiltZ,
          delta * 4.0
        );

        // Keep mouse tracking active, but increase dampening prioritizing forward eye contact
        const focusedGazeY = mousePos.current.x * 0.22;
        const focusedGazeX = -mousePos.current.y * 0.15 - 0.02;
        headGroupRef.current.rotation.y = THREE.MathUtils.lerp(
          headGroupRef.current.rotation.y,
          focusedGazeY,
          delta * 3.5
        );
        headGroupRef.current.rotation.x = THREE.MathUtils.lerp(
          headGroupRef.current.rotation.x,
          focusedGazeX,
          delta * 3.5
        );
        headGroupRef.current.position.y = 0.55 + Math.sin(time * 1.5) * 0.02;
      }

      // Rest jaw in closed position
      if (jawRef.current) {
        jawRef.current.position.y = THREE.MathUtils.lerp(jawRef.current.position.y, -0.32, delta * 8);
        jawRef.current.rotation.x = THREE.MathUtils.lerp(jawRef.current.rotation.x, 0.2, delta * 8);
      }

      if (torsoRef.current) {
        torsoRef.current.position.y = -0.55 + Math.sin(time * 1.5) * 0.01;
      }
    } else if (isSpeaking) {
      // --- ORGANIC RHYTHMIC NODDING & ARTICULATION (Assistant Replying) ---
      // Multi-frequency natural head nod oscillation along X-axis (pitch) avoiding robotic rigid loop
      const organicNod =
        Math.sin(time * 9.2) * 0.042 +
        Math.sin(time * 14.7) * 0.018 +
        Math.cos(time * 6.1) * 0.012;

      if (headGroupRef.current) {
        // Roll smoothly returns to upright 0.0
        headGroupRef.current.rotation.z = THREE.MathUtils.lerp(
          headGroupRef.current.rotation.z,
          0.0,
          delta * 4.5
        );
        headGroupRef.current.rotation.x = THREE.MathUtils.lerp(
          headGroupRef.current.rotation.x,
          targetMouseX * 0.35 + organicNod,
          delta * 6.5
        );
        headGroupRef.current.rotation.y = THREE.MathUtils.lerp(
          headGroupRef.current.rotation.y,
          targetMouseY * 0.45,
          delta * 4.0
        );
        headGroupRef.current.position.y = 0.55 + Math.sin(time * 2.8) * 0.025;
      }

      // Rhythmic jaw/mouth articulation simulating syllable cadence
      const syllablePulse = Math.max(
        0,
        Math.sin(time * 17.5) * 0.6 + Math.sin(time * 24.0) * 0.35 + Math.cos(time * 8.0) * 0.15
      );
      if (jawRef.current) {
        const targetJawY = -0.32 - syllablePulse * 0.085;
        const targetJawRotX = 0.2 + syllablePulse * 1.7;
        jawRef.current.position.y = THREE.MathUtils.lerp(jawRef.current.position.y, targetJawY, delta * 16);
        jawRef.current.rotation.x = THREE.MathUtils.lerp(jawRef.current.rotation.x, targetJawRotX, delta * 16);
      }

      // Torso gently breathing & bobbing dynamically
      if (torsoRef.current) {
        torsoRef.current.position.y = -0.55 + Math.sin(time * 3.5) * 0.022 + Math.sin(time * 8.0) * 0.008;
      }
    } else {
      // --- IDLE STATE ---
      // Return smoothly to relaxed idle breathing and 60fps responsive mouse cursor tracking
      if (headGroupRef.current) {
        headGroupRef.current.rotation.z = THREE.MathUtils.lerp(
          headGroupRef.current.rotation.z,
          0.0,
          delta * 4.0
        );
        headGroupRef.current.rotation.y = THREE.MathUtils.lerp(
          headGroupRef.current.rotation.y,
          targetMouseY,
          delta * 4.8
        );
        headGroupRef.current.rotation.x = THREE.MathUtils.lerp(
          headGroupRef.current.rotation.x,
          targetMouseX,
          delta * 4.8
        );
        headGroupRef.current.position.y = 0.55 + Math.sin(time * 1.8) * 0.035;
      }

      if (jawRef.current) {
        jawRef.current.position.y = THREE.MathUtils.lerp(jawRef.current.position.y, -0.32, delta * 8);
        jawRef.current.rotation.x = THREE.MathUtils.lerp(jawRef.current.rotation.x, 0.2, delta * 8);
      }

      if (torsoRef.current) {
        torsoRef.current.rotation.y = THREE.MathUtils.lerp(
          torsoRef.current.rotation.y,
          targetMouseY * 0.18,
          delta * 2.5
        );
        torsoRef.current.position.y = -0.55 + Math.sin(time * 1.8) * 0.015;
      }
    }

    if (neckRef.current) {
      const neckTargetY = (isListening ? targetMouseY * 0.2 : targetMouseY * 0.35);
      neckRef.current.rotation.y = THREE.MathUtils.lerp(neckRef.current.rotation.y, neckTargetY, delta * 3.5);
    }

    // -------------------------------------------------------------------------
    // 2. VISUAL CUES: HALO RINGS, GLOWS & AUDIO ACTIVITY
    // -------------------------------------------------------------------------
    if (ringRef.current) {
      const ringSpeed = isListening ? 1.4 : isSpeaking ? 0.8 : 0.3;
      ringRef.current.rotation.z = time * ringSpeed;
      ringRef.current.rotation.x = Math.PI / 2.3 + Math.sin(time * 0.6) * 0.08;

      const targetScale = isListening ? 1 + (audioLevel / 45) * 0.18 : isSpeaking ? 1.05 : 1.0;
      ringRef.current.scale.set(targetScale, targetScale, 1);
    }

    // Update halo emissive color cleanly without recreating objects
    if (haloMaterialRef.current) {
      if (isListening) {
        haloMaterialRef.current.color.copy(COLOR_CYAN);
        haloMaterialRef.current.emissive.copy(COLOR_CYAN);
        haloMaterialRef.current.emissiveIntensity = 3.5;
      } else if (isSpeaking) {
        haloMaterialRef.current.color.copy(COLOR_BLUE);
        haloMaterialRef.current.emissive.copy(COLOR_BLUE);
        haloMaterialRef.current.emissiveIntensity = 3.8;
      } else {
        haloMaterialRef.current.color.copy(COLOR_CYAN);
        haloMaterialRef.current.emissive.copy(COLOR_CYAN);
        haloMaterialRef.current.emissiveIntensity = 2.2;
      }
    }

    if (eyesRef.current) {
      if (isListening) {
        const listeningPulse = 3.0 + (audioLevel / 18) * 3.5 + Math.sin(time * 9) * 0.8;
        eyesRef.current.material.emissiveIntensity = listeningPulse;
        eyesRef.current.material.emissive.copy(COLOR_CYAN);
      } else if (isSpeaking) {
        const speakingPulse = 3.2 + Math.abs(Math.sin(time * 18)) * 2.5;
        eyesRef.current.material.emissiveIntensity = speakingPulse;
        eyesRef.current.material.emissive.copy(COLOR_BLUE);
      } else {
        eyesRef.current.material.emissiveIntensity = 2.0 + Math.sin(time * 2.5) * 0.5;
        eyesRef.current.material.emissive.copy(COLOR_CYAN);
      }
    }

    if (coreRef.current) {
      const coreSpeed = isSpeaking ? 9 : isListening ? 7 : 3;
      const coreBase = isListening ? 3.0 : isSpeaking ? 3.2 : 1.6;
      coreRef.current.material.emissiveIntensity = coreBase + Math.sin(time * coreSpeed) * 0.8;
    }
  });

  return (
    <group position={[0, -0.15, 0]}>
      {/* Dynamic Cyber Halo Ring Behind Head */}
      <group position={[0, 0.6, -0.45]} ref={ringRef}>
        <mesh material={materials.wireframeAcc}>
          <ringGeometry args={[1.35, 1.45, 36]} />
        </mesh>
        <mesh material={materials.haloGlow}>
          <ringGeometry args={[1.39, 1.42, 36]} />
        </mesh>
      </group>

      {/* ---------------- HEAD & SENSORS GROUP ---------------- */}
      <group ref={headGroupRef} position={[0, 0.55, 0]}>
        {/* Cranium Base */}
        <mesh position={[0, 0, 0]} material={materials.armorDark}>
          <sphereGeometry args={[0.55, 16, 14]} />
        </mesh>

        {/* Wireframe Holographic Overlay */}
        <mesh position={[0, 0, 0]} material={materials.wireframeAcc}>
          <sphereGeometry args={[0.57, 14, 10]} />
        </mesh>

        {/* Articulated Speech Jaw & Chin Guard */}
        <mesh
          ref={jawRef}
          position={[0, -0.32, 0.16]}
          rotation={[0.2, 0, 0]}
          material={materials.armorPlate}
        >
          <boxGeometry args={[0.42, 0.35, 0.45]} />
        </mesh>

        {/* Sleek Cyber Visor */}
        <mesh position={[0, 0.04, 0.44]} rotation={[0.08, 0, 0]} material={materials.visorGlass}>
          <boxGeometry args={[0.62, 0.18, 0.22]} />
        </mesh>

        {/* Glowing Ocular Sensor Core Strip */}
        <mesh ref={eyesRef} position={[0, 0.04, 0.52]} material={materials.eyesGlow}>
          <boxGeometry args={[0.48, 0.045, 0.06]} />
        </mesh>

        {/* Left & Right Audio/Comm Nodes */}
        <mesh position={[-0.56, 0.02, 0.02]} rotation={[0, 0, Math.PI / 2]} material={materials.chromeJoint}>
          <cylinderGeometry args={[0.12, 0.15, 0.12, 12]} />
        </mesh>
        <mesh position={[-0.62, 0.02, 0.02]} rotation={[0, 0, Math.PI / 2]} material={materials.eyesGlow}>
          <cylinderGeometry args={[0.05, 0.05, 0.04, 12]} />
        </mesh>

        <mesh position={[0.56, 0.02, 0.02]} rotation={[0, 0, Math.PI / 2]} material={materials.chromeJoint}>
          <cylinderGeometry args={[0.12, 0.15, 0.12, 12]} />
        </mesh>
        <mesh position={[0.62, 0.02, 0.02]} rotation={[0, 0, Math.PI / 2]} material={materials.eyesGlow}>
          <cylinderGeometry args={[0.05, 0.05, 0.04, 12]} />
        </mesh>

        {/* Temporal Antenna Strips */}
        <mesh position={[-0.38, 0.38, 0.08]} rotation={[0, 0, -0.35]} material={materials.neonViolet}>
          <boxGeometry args={[0.04, 0.32, 0.04]} />
        </mesh>
        <mesh position={[0.38, 0.38, 0.08]} rotation={[0, 0, 0.35]} material={materials.neonViolet}>
          <boxGeometry args={[0.04, 0.32, 0.04]} />
        </mesh>
      </group>

      {/* ---------------- ARTICULATED CERVICAL NECK ---------------- */}
      <group ref={neckRef} position={[0, 0.08, 0]}>
        <mesh material={materials.chromeJoint}>
          <cylinderGeometry args={[0.18, 0.22, 0.38, 12]} />
        </mesh>
        <mesh position={[-0.14, 0, 0.08]} material={materials.armorPlate}>
          <cylinderGeometry args={[0.04, 0.04, 0.32, 8]} />
        </mesh>
        <mesh position={[0.14, 0, 0.08]} material={materials.armorPlate}>
          <cylinderGeometry args={[0.04, 0.04, 0.32, 8]} />
        </mesh>
      </group>

      {/* ---------------- TORSO & BUST ARMOR ---------------- */}
      <group ref={torsoRef} position={[0, -0.55, 0]}>
        <mesh position={[0, 0.15, 0.05]} material={materials.armorDark}>
          <boxGeometry args={[1.25, 0.45, 0.65]} />
        </mesh>

        <mesh position={[-0.32, 0.18, 0.28]} rotation={[0.2, 0.2, 0]} material={materials.armorPlate}>
          <boxGeometry args={[0.48, 0.35, 0.22]} />
        </mesh>
        <mesh position={[0.32, 0.18, 0.28]} rotation={[0.2, -0.2, 0]} material={materials.armorPlate}>
          <boxGeometry args={[0.48, 0.35, 0.22]} />
        </mesh>

        <mesh ref={coreRef} position={[0, 0.18, 0.34]} rotation={[Math.PI / 2, 0, 0]} material={materials.eyesGlow}>
          <cylinderGeometry args={[0.12, 0.12, 0.06, 24]} />
        </mesh>
        <mesh position={[0, 0.18, 0.32]} rotation={[Math.PI / 2, 0, 0]} material={materials.chromeJoint}>
          <torusGeometry args={[0.16, 0.025, 12, 24]} />
        </mesh>

        <mesh position={[0, 0.4, 0.12]} rotation={[-0.2, 0, 0]} material={materials.neonViolet}>
          <boxGeometry args={[0.75, 0.06, 0.06]} />
        </mesh>

        <mesh position={[-0.78, 0.12, 0]} material={materials.armorPlate}>
          <sphereGeometry args={[0.26, 12, 10]} />
        </mesh>
        <mesh position={[0.78, 0.12, 0]} material={materials.armorPlate}>
          <sphereGeometry args={[0.26, 12, 10]} />
        </mesh>
      </group>
    </group>
  );
}

// ---------------------------------------------------------------------------
// Atmospheric Ground Depth Grid & Ambient Halo
// ---------------------------------------------------------------------------
function CyberGround({ mousePos }) {
  const gridRef = useRef();
  const discRef = useRef();

  useFrame((state, delta) => {
    const { isListening, isSpeaking, audioLevel } = avatarVoiceState;

    if (gridRef.current) {
      gridRef.current.position.x = THREE.MathUtils.lerp(
        gridRef.current.position.x,
        mousePos.current.x * 0.35,
        delta * 3
      );
    }
    if (discRef.current) {
      const scale = isListening ? 1 + (audioLevel / 40) * 0.35 : isSpeaking ? 1.1 : 1.0;
      discRef.current.scale.set(scale, scale, 1);
    }
  });

  return (
    <group ref={gridRef} position={[0, -1.55, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      {/* Grid Pattern */}
      <gridHelper args={[24, 28, '#00f2fe', '#1e293b']} rotation={[Math.PI / 2, 0, 0]} />

      {/* Active Ambient Halo Ring Beneath Figure */}
      <mesh ref={discRef} position={[0, 0, -0.05]}>
        <ringGeometry args={[0.4, 3.8, 36]} />
        <meshBasicMaterial
          color="#00f2fe"
          transparent
          opacity={0.16}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
}

// ---------------------------------------------------------------------------
// Dynamic Lighting responding to Cursor & Voice State
// ---------------------------------------------------------------------------
function DynamicCursorLight({ mousePos }) {
  const lightRef = useRef();

  useFrame(() => {
    const { isListening, isSpeaking } = avatarVoiceState;

    if (lightRef.current) {
      lightRef.current.position.x = mousePos.current.x * 4;
      lightRef.current.position.y = mousePos.current.y * 3 + 1;
      const targetIntensity = isListening ? 4.8 : isSpeaking ? 4.2 : 3.0;
      lightRef.current.intensity = THREE.MathUtils.lerp(
        lightRef.current.intensity,
        targetIntensity,
        0.1
      );
    }
  });

  return (
    <pointLight
      ref={lightRef}
      position={[0, 1.5, 3]}
      intensity={3.0}
      color="#38bdf8"
      distance={9}
      decay={2}
    />
  );
}

// ---------------------------------------------------------------------------
// Main AvatarCanvas Container (Completely decoupled from React re-renders)
// ---------------------------------------------------------------------------
export default function AvatarCanvas() {
  const mousePos = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      const x = (e.clientX / window.innerWidth) * 2 - 1;
      const y = -(e.clientY / window.innerHeight) * 2 + 1;
      mousePos.current = { x, y };
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="relative w-full h-full bg-[#07080d] overflow-hidden select-none">
      {/* Atmospheric Radial Gradient Backdrop */}
      <div
        className="absolute inset-0 pointer-events-none transition-all duration-700"
        style={{
          background: 'radial-gradient(circle at 45% 40%, rgba(6, 182, 212, 0.2) 0%, rgba(14, 116, 144, 0.12) 45%, rgba(7, 8, 13, 1) 85%)',
        }}
      />

      {/* Top Left HUD Telemetry Overlay */}
      <div className="absolute top-5 left-6 z-10 pointer-events-none flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping shadow-[0_0_12px_#00f2fe]" />
          <span className="text-[11px] font-mono tracking-widest uppercase font-semibold text-cyan-300">
            Neural Avatar Link // 60 FPS
          </span>
        </div>
        <div className="text-[12px] text-slate-400 font-mono">
          GAZE TRACKING: <span className="text-slate-200">ACTIVE LERP</span>
        </div>
      </div>

      {/* Subtle Corner Vignette Frame */}
      <div className="absolute inset-0 pointer-events-none border border-cyan-500/20 rounded-2xl m-3" />

      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [0, 0.45, 3.4], fov: 42 }}
        dpr={[1, 2]}
        gl={{ antialias: true, alpha: false, powerPreference: 'high-performance' }}
        onCreated={({ gl, scene }) => {
          gl.setClearColor('#07080d', 1);
          scene.fog = new THREE.FogExp2('#07080d', 0.18);
        }}
      >
        <ambientLight intensity={0.65} color="#0f172a" />
        <directionalLight position={[0, 4, 3]} intensity={1.5} color="#f8fafc" />
        <pointLight position={[-3, 2, -2]} intensity={2.8} color="#8b5cf6" distance={10} />
        <pointLight position={[3, -1, 1]} intensity={3.0} color="#00f2fe" distance={8} />

        <DynamicCursorLight mousePos={mousePos} />

        <Float speed={1.5} rotationIntensity={0.15} floatIntensity={0.25}>
          <AndroidBust mousePos={mousePos} />
        </Float>
        <CyberGround mousePos={mousePos} />
      </Canvas>
    </div>
  );
}
