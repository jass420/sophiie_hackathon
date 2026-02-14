import { ChatMessage as ChatMessageType } from '../../types';
import { ColorPalette } from '../room/ColorPalette';
import { ProductGrid } from '../products/ProductGrid';

interface Props {
  message: ChatMessageType;
  onAddToList?: (product: any) => void;
}

export function ChatMessage({ message, onAddToList }: Props) {
  const isUser = message.role === 'user';

  // Remove COLOR_PALETTE tags from displayed content
  const displayContent = message.content.replace(
    /\[COLOR_PALETTE:\s*#[0-9a-fA-F]{6}(?:\s*,\s*#[0-9a-fA-F]{6})*\]/g,
    ''
  ).trim();

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar */}
        <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium shrink-0 ${
              isUser ? 'bg-blue-600' : 'bg-violet-600'
            }`}
          >
            {isUser ? 'U' : 'R'}
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
                    ? 'bg-blue-600 text-white rounded-br-md'
                    : 'bg-white text-gray-800 shadow-sm border border-gray-100 rounded-bl-md'
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
          </div>
        </div>
      </div>
    </div>
  );
}
