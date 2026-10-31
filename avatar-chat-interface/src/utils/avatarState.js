/**
 * Mutable high-performance state store for 3D Avatar telemetry.
 * Read directly inside Three.js useFrame loop to guarantee smooth 60fps
 * animations without triggering expensive React component tree re-renders.
 */
export const avatarVoiceState = {
  isListening: false,
  isSpeaking: false,
  audioLevel: 0,
};

export function setAvatarVoiceState(updates) {
  Object.assign(avatarVoiceState, updates);
}
