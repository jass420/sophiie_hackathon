export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  image?: string; // base64
  imagePreview?: string; // data URL for display
  toolCalls?: ToolCall[];
  products?: ProductListing[];
  colorPalette?: string[];
  timestamp: Date;
}

export interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
  result?: unknown;
}

export interface ProductListing {
  id: string;
  title: string;
  price: number;
  currency: string;
  image_url: string;
  source: 'ebay' | 'facebook' | 'gumtree';
  url: string;
  seller: string;
  condition: string;
  location: string;
  description?: string;
}

export interface RoomAnalysis {
  roomType: string;
  dimensions: string;
  style: string;
  lighting: string;
  colorPalette: string[];
  recommendations: string[];
}
