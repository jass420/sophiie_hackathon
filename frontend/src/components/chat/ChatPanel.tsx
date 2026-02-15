import { useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { BrowserView } from '../browser/BrowserView';
import type { ChatMessage as ChatMessageType, ProductListing } from '../../types';

interface Props {
  messages: ChatMessageType[];
  isLoading: boolean;
  onSend: (content: string, image?: string) => void;
  onAddToList?: (product: ProductListing) => void;
  onApproveAll?: (messageId: string) => void;
  onApproveSelected?: (messageId: string, ids: string[]) => void;
  onReject?: (messageId: string) => void;
}

export function ChatPanel({ messages, isLoading, onSend, onAddToList, onApproveAll, onApproveSelected, onReject }: Props) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-white/30 backdrop-blur-sm">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-violet-500/20 backdrop-blur-xl border border-violet-300/30 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Welcome to Roomie</h2>
            <p className="text-gray-500 max-w-md mb-6">
              Upload a photo of your room and I'll help you find the perfect furniture
              from Facebook Marketplace, eBay, and more.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => document.querySelector<HTMLInputElement>('input[type="file"]')?.click()}
                className="px-4 py-2 bg-blue-600/50 backdrop-blur-xl text-white border border-blue-400/30 rounded-xl text-sm font-medium hover:bg-blue-600/70 transition-colors shadow-lg"
              >
                Upload Room Photo
              </button>
              <button
                onClick={() => onSend("Hi! I need help furnishing my room.")}
                className="px-4 py-2 bg-white/40 backdrop-blur-xl text-gray-700 rounded-xl text-sm font-medium border border-white/30 hover:bg-white/60 transition-colors shadow-lg"
              >
                Start Chatting
              </button>
            </div>
          </div>
        )}

        {messages.map(message => (
          <ChatMessage
            key={message.id}
            message={message}
            onAddToList={onAddToList}
            onApproveAll={onApproveAll}
            onApproveSelected={onApproveSelected}
            onReject={onReject}
          />
        ))}

        {isLoading && (
          <div className="mb-4">
            <div className="flex justify-start">
              <div className="flex items-start gap-3">
                <div className="flex flex-col gap-3">
                  <div className="px-4 py-3 rounded-2xl bg-white/40 backdrop-blur-xl shadow-lg border border-white/30 rounded-bl-md">
                    <div className="flex gap-1.5">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                  <BrowserView />
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <ChatInput onSend={onSend} isLoading={isLoading} />
    </div>
  );
}
