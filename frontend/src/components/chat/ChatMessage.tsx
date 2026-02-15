import type { ChatMessage as ChatMessageType } from '../../types';
import { ColorPalette } from '../room/ColorPalette';
import { ProductGrid } from '../products/ProductGrid';
import { ApprovalCard } from '../approval/ApprovalCard';

interface Props {
  message: ChatMessageType;
  onAddToList?: (product: any) => void;
  onApproveAll?: (messageId: string) => void;
  onApproveSelected?: (messageId: string, ids: string[]) => void;
  onReject?: (messageId: string) => void;
}

export function ChatMessage({ message, onAddToList, onApproveAll, onApproveSelected, onReject }: Props) {
  const isUser = message.role === 'user';

  // Remove COLOR_PALETTE tags from displayed content
  let displayContent = message.content.replace(
    /\[COLOR_PALETTE:\s*#[0-9a-fA-F]{6}(?:\s*,\s*#[0-9a-fA-F]{6})*\]/g,
    ''
  ).trim();

  // Hide raw JSON content when an approval card is showing
  if (message.interrupt && displayContent.startsWith('{')) {
    displayContent = '';
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar */}
        <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
              isUser ? 'bg-gray-600' : 'bg-violet-600'
            }`}
          >
            {isUser ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
            )}
          </div>

          <div className={`flex flex-col gap-2 ${isUser ? 'items-end' : 'items-start'}`}>
            {/* User's uploaded image */}
            {message.imagePreview && (
              <img
                src={message.imagePreview}
                alt="Uploaded room"
                className="max-w-sm rounded-lg shadow-md"
              />
            )}

            {/* Message bubble */}
            {displayContent && (
              <div
                className={`px-4 py-3 rounded-2xl whitespace-pre-wrap leading-relaxed ${
                  isUser
                    ? 'bg-gray-500/30 backdrop-blur-xl text-gray-800 border border-gray-300/30 shadow-lg rounded-br-md'
                    : 'bg-white/40 backdrop-blur-xl text-gray-800 shadow-lg border border-white/30 rounded-bl-md'
                }`}
              >
                {displayContent}
              </div>
            )}

            {/* Color palette */}
            {message.colorPalette && message.colorPalette.length > 0 && (
              <ColorPalette colors={message.colorPalette} />
            )}

            {/* Product results */}
            {message.products && message.products.length > 0 && (
              <ProductGrid products={message.products} onAddToList={onAddToList} />
            )}

            {/* Approval card */}
            {message.interrupt && (
              <ApprovalCard
                type={message.interrupt.type}
                items={message.interrupt.items}
                resolved={message.interruptResolved}
                onApproveAll={() => onApproveAll?.(message.id)}
                onApproveSelected={(ids) => onApproveSelected?.(message.id, ids)}
                onReject={() => onReject?.(message.id)}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
