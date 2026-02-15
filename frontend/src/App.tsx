import { useState, useEffect, useRef } from 'react';
import { ChatPanel } from './components/chat/ChatPanel';
import { ShoppingList } from './components/products/ShoppingList';
import { useChat } from './hooks/useChat';
import * as THREE from 'three';
import FOG from 'vanta/dist/vanta.fog.min';

function App() {
  const { messages, isLoading, sendMessage, resumeWithApproval, shoppingList, addToShoppingList, removeFromShoppingList } = useChat();
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
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
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

        <button
          onClick={() => setShowSidebar(!showSidebar)}
          className="relative px-3 py-1.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Shopping List
          {shoppingList.length > 0 && (
            <span className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-blue-600 text-white text-xs rounded-full flex items-center justify-center">
              {shoppingList.length}
            </span>
          )}
        </button>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
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
          <div className="w-80 border-l border-gray-200 bg-gray-50 shrink-0">
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
