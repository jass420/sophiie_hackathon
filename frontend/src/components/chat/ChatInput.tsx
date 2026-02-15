import { useState, useRef, type KeyboardEvent } from 'react';

interface Props {
  onSend: (content: string, image?: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: Props) {
  const [input, setInput] = useState('');
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    if ((!input.trim() && !imageBase64) || isLoading) return;
    onSend(input.trim() || 'Please analyze this room.', imageBase64 || undefined);
    setInput('');
    setImagePreview(null);
    setImageBase64(null);
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Preview
    const previewReader = new FileReader();
    previewReader.onload = () => setImagePreview(previewReader.result as string);
    previewReader.readAsDataURL(file);

    // Base64 for API
    const base64Reader = new FileReader();
    base64Reader.onload = () => {
      const result = base64Reader.result as string;
      // Remove data URL prefix
      setImageBase64(result.split(',')[1]);
    };
    base64Reader.readAsDataURL(file);
  };

  const removeImage = () => {
    setImagePreview(null);
    setImageBase64(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="border-t border-white/30 bg-white/20 backdrop-blur-xl p-4">
      {/* Image preview */}
      {imagePreview && (
        <div className="mb-3 relative inline-block">
          <img
            src={imagePreview}
            alt="Selected"
            className="h-20 rounded-lg shadow-sm"
          />
          <button
            onClick={removeImage}
            className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full text-xs flex items-center justify-center hover:bg-red-600"
          >
            x
          </button>
        </div>
      )}

      <div className="flex items-end gap-3">
        {/* Image upload button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          className="p-2.5 text-gray-500 hover:text-gray-700 hover:bg-white/40 rounded-xl transition-colors"
          title="Upload room photo"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>
            <circle cx="9" cy="9" r="2"/>
            <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
          </svg>
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageSelect}
          className="hidden"
        />

        {/* Text input */}
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={imageBase64 ? "Add a message about your room..." : "Describe your space or upload a photo..."}
          rows={1}
          className="flex-1 resize-none rounded-xl border border-white/30 bg-white/40 backdrop-blur-xl px-4 py-2.5 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-white/50 focus:border-transparent placeholder:text-gray-500 shadow-lg"
          style={{ minHeight: '44px', maxHeight: '120px' }}
        />

        {/* Send button */}
        <button
          onClick={handleSubmit}
          disabled={isLoading || (!input.trim() && !imageBase64)}
          className="p-2.5 bg-white/40 backdrop-blur-xl text-gray-700 border border-white/30 rounded-xl hover:bg-white/60 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-lg"
        >
          {isLoading ? (
            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}
