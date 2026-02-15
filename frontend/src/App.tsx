import { useState, useEffect, useRef } from 'react';
import { ChatPanel } from './components/chat/ChatPanel';
import { ShoppingList } from './components/products/ShoppingList';
import { useChat } from './hooks/useChat';
import * as THREE from 'three';
import FOG from 'vanta/dist/vanta.fog.min';

function App() {
  const { messages, isLoading, sendMessage, resumeWithApproval, shoppingList, addToShoppingList, removeFromShoppingList, voiceEnabled, toggleVoice, isSpeaking, stopSpeaking } = useChat();
  const [showSidebar, setShowSidebar] = useState(false);
  const vantaRef = useRef<HTMLDivElement>(null);
  const vantaEffect = useRef<ReturnType<typeof FOG> | null>(null);

  useEffect(() => {
    if (!vantaEffect.current && vantaRef.current) {
      vantaEffect.current = FOG({
        el: vantaRef.current,
        THREE,
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 200.00,
        minWidth: 200.00,
        highlightColor: 0x20abf7,
        midtoneColor: 0xf2e00c,
        blurFactor: 0.59,
        speed: 0.40,
        zoom: 1.30,
      });
    }
    return () => {
      if (vantaEffect.current) {
        vantaEffect.current.destroy();
        vantaEffect.current = null;
      }
    };
  }, []);

  return (
    <div ref={vantaRef} className="h-screen flex flex-col relative">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 px-6 py-3 flex items-center justify-between shrink-0 relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Roomie</h1>
            <p className="text-xs text-gray-400">AI-powered home furnishing</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {isSpeaking && (
            <button
              onClick={stopSpeaking}
              className="p-2 rounded-lg transition-colors shadow-lg border bg-red-500/50 backdrop-blur-xl text-white border-red-400/30 animate-pulse"
              title="Stop speaking"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <rect x="6" y="6" width="12" height="12" rx="2" />
              </svg>
            </button>
          )}
          <button
            onClick={toggleVoice}
            className={`p-2 rounded-lg transition-colors shadow-lg border ${
              voiceEnabled
                ? 'bg-violet-500/50 backdrop-blur-xl text-white border-violet-400/30'
                : 'bg-white/40 backdrop-blur-xl text-gray-700 border-white/30 hover:bg-white/60'
            }`}
            title={voiceEnabled ? 'Disable voice responses' : 'Enable voice responses'}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {voiceEnabled ? (
                <>
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                  <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
                </>
              ) : (
                <>
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                  <line x1="23" y1="9" x2="17" y2="15" />
                  <line x1="17" y1="9" x2="23" y2="15" />
                </>
              )}
            </svg>
          </button>

          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="relative px-3 py-1.5 text-sm font-medium text-gray-700 bg-white/40 backdrop-blur-xl border border-white/30 rounded-lg hover:bg-white/60 transition-colors shadow-lg"
          >
            Shopping List
            {shoppingList.length > 0 && (
              <span className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-blue-600 text-white text-xs rounded-full flex items-center justify-center">
                {shoppingList.length}
              </span>
            )}
          </button>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden relative z-10">
        {/* Chat */}
        <div className="flex-1">
          <ChatPanel
            messages={messages}
            isLoading={isLoading}
            onSend={sendMessage}
            onAddToList={addToShoppingList}
            onApproveAll={(msgId) => resumeWithApproval('approve_all', undefined, msgId)}
            onApproveSelected={(msgId, ids) => resumeWithApproval('approve_selected', ids, msgId)}
            onReject={(msgId) => resumeWithApproval('reject', undefined, msgId)}
          />
        </div>

        {/* Shopping list sidebar */}
        {showSidebar && (
          <div className="w-80 border-l border-gray-200/50 bg-white/30 backdrop-blur-sm shrink-0">
            <div className="p-4 border-b border-gray-200 bg-white">
              <h2 className="text-sm font-semibold text-gray-800">Shopping List</h2>
            </div>
            <ShoppingList items={shoppingList} onRemove={removeFromShoppingList} />
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
