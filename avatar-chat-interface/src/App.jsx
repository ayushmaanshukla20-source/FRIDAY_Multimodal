import React from 'react';
import AvatarCanvas from './components/AvatarCanvas';
import ChatPanel from './components/ChatPanel';

export default function App() {
  return (
    <div className="relative w-screen h-screen flex flex-col md:flex-row bg-[#07080d] overflow-hidden">
      {/* ---------------- LEFT / CENTER MAIN 3D CANVAS (~68% width) ---------------- */}
      <main className="relative flex-1 md:w-[68%] h-[50vh] md:h-full overflow-hidden">
        <AvatarCanvas />
      </main>

      {/* ---------------- RIGHT CONVERSATION SIDEBAR (~32% width, min 380px) ---------------- */}
      <aside className="w-full md:w-[32%] md:min-w-[380px] md:max-w-[480px] h-[50vh] md:h-full flex flex-col shadow-2xl relative z-20">
        <ChatPanel />
      </aside>
    </div>
  );
}
