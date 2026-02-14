import { useState, useCallback } from 'react';
import { ChatMessage, ProductListing } from '../types';

const API_URL = '/api/chat';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [shoppingList, setShoppingList] = useState<ProductListing[]>([]);

  const sendMessage = useCallback(async (content: string, image?: string) => {
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      image: image,
      imagePreview: image ? `data:image/jpeg;base64,${image}` : undefined,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Build message history for API
      const apiMessages = [...messages, userMessage].map(msg => ({
        role: msg.role,
        content: msg.content,
        image: msg.image || null,
      }));

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: apiMessages }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let fullContent = '';
      let toolCalls: ChatMessage['toolCalls'] = [];

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ') && line !== 'data: [DONE]') {
            try {
              const data = JSON.parse(line.slice(6));
              fullContent = data.content || fullContent;
              toolCalls = data.tool_calls || toolCalls;

              // Parse color palette from content
              const colorMatch = fullContent.match(/\[COLOR_PALETTE:\s*(#[0-9a-fA-F]{6}(?:\s*,\s*#[0-9a-fA-F]{6})*)\]/);
              const colorPalette = colorMatch
                ? colorMatch[1].split(',').map((c: string) => c.trim())
                : undefined;

              // Parse products from tool calls
              const products = toolCalls
                ?.filter(tc => tc.tool === 'search_marketplace')
                .flatMap(tc => {
                  try {
                    const result = typeof tc.result === 'string' ? JSON.parse(tc.result as string) : tc.result;
                    return result?.products || [];
                  } catch {
                    return [];
                  }
                });

              setMessages(prev =>
                prev.map(msg =>
                  msg.id === assistantMessage.id
                    ? {
                        ...msg,
                        content: fullContent,
                        toolCalls,
                        colorPalette: colorPalette || undefined,
                        products: products?.length ? products : undefined,
                      }
                    : msg
                )
              );
            } catch {
              // Skip malformed JSON
            }
          }
        }
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  }, [messages]);

  const addToShoppingList = useCallback((product: ProductListing) => {
    setShoppingList(prev => {
      if (prev.some(p => p.id === product.id)) return prev;
      return [...prev, product];
    });
  }, []);

  const removeFromShoppingList = useCallback((productId: string) => {
    setShoppingList(prev => prev.filter(p => p.id !== productId));
  }, []);

  return {
    messages,
    isLoading,
    sendMessage,
    shoppingList,
    addToShoppingList,
    removeFromShoppingList,
  };
}
