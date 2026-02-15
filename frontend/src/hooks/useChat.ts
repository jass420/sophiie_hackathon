import { useState, useCallback, useRef } from 'react';
import type { ChatMessage, ProductListing } from '../types';

const API_URL = '/api/chat';
const RESUME_URL = '/api/chat/resume';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [shoppingList, setShoppingList] = useState<ProductListing[]>([]);
  const threadIdRef = useRef<string | null>(null);

  const _parseSSE = useCallback(async (
    response: Response,
    assistantMessageId: string,
  ) => {
    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let fullContent = '';
    let toolCalls: ChatMessage['toolCalls'] = [];
    let products: ProductListing[] = [];

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

            // Track thread_id from server
            if (data.thread_id) {
              threadIdRef.current = data.thread_id;
            }

            if (data.products && data.products.length > 0) {
              products = data.products;
            }

            // Parse color palette from content
            const colorMatch = fullContent.match(/\[COLOR_PALETTE:\s*(#[0-9a-fA-F]{6}(?:\s*,\s*#[0-9a-fA-F]{6})*)\]/);
            const colorPalette = colorMatch
              ? colorMatch[1].split(',').map((c: string) => c.trim())
              : undefined;

            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId
                  ? {
                      ...msg,
                      content: fullContent,
                      toolCalls,
                      colorPalette: colorPalette || undefined,
                      products: products.length > 0 ? products : undefined,
                      interrupt: data.interrupt || undefined,
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
  }, []);

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
      const apiMessages = [...messages, userMessage].map(msg => ({
        role: msg.role,
        content: msg.content,
        image: msg.image || null,
      }));

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: apiMessages,
          thread_id: threadIdRef.current,
        }),
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      await _parseSSE(response, assistantMessage.id);
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
  }, [messages, _parseSSE]);

  const resumeWithApproval = useCallback(async (
    action: 'approve_all' | 'approve_selected' | 'reject',
    selectedIds?: string[],
    interruptMessageId?: string,
  ) => {
    if (!threadIdRef.current) return;

    // Mark the interrupt as resolved on the message that had it
    if (interruptMessageId) {
      setMessages(prev =>
        prev.map(msg =>
          msg.id === interruptMessageId
            ? { ...msg, interruptResolved: true }
            : msg
        )
      );
    }

    setIsLoading(true);

    try {
      const response = await fetch(RESUME_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thread_id: threadIdRef.current,
          action,
          selected_ids: selectedIds || null,
        }),
      });

      if (!response.ok) throw new Error(`Resume error: ${response.status}`);

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      await _parseSSE(response, assistantMessage.id);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your decision. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      console.error('Resume error:', error);
    } finally {
      setIsLoading(false);
    }
  }, [_parseSSE]);

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
    resumeWithApproval,
    shoppingList,
    addToShoppingList,
    removeFromShoppingList,
  };
}
