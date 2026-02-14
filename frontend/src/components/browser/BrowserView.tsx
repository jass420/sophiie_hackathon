import { useState, useEffect, useRef } from 'react';

export function BrowserView() {
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [status, setStatus] = useState<'loading' | 'ok' | 'no_browser'>('loading');
  const [collapsed, setCollapsed] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const fetchScreenshot = async () => {
      try {
        const res = await fetch('/api/browser/screenshot');
        const data = await res.json();
        if (data.status === 'ok' && data.screenshot) {
          setScreenshot(data.screenshot);
          setStatus('ok');
        } else {
          setStatus('no_browser');
        }
      } catch {
        setStatus('no_browser');
      }
    };

    fetchScreenshot();
    intervalRef.current = setInterval(fetchScreenshot, 2000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  if (collapsed) {
    return (
      <button
        onClick={() => setCollapsed(false)}
        className="absolute bottom-4 right-4 z-10 px-3 py-2 bg-violet-600 text-white text-sm font-medium rounded-lg shadow-lg hover:bg-violet-700 transition-colors"
      >
        Show Browser
      </button>
    );
  }

  return (
    <div className="flex flex-col h-full border-l border-gray-200 bg-gray-900">
      {/* Header bar */}
      <div className="flex items-center justify-between px-3 py-2 bg-gray-800 border-b border-gray-700 shrink-0">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${status === 'ok' ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
          <span className="text-xs font-medium text-gray-300">
            {status === 'ok' ? 'Live Browser' : status === 'loading' ? 'Connecting...' : 'No Browser'}
          </span>
        </div>
        <button
          onClick={() => setCollapsed(true)}
          className="text-gray-400 hover:text-white text-xs transition-colors"
        >
          Minimize
        </button>
      </div>

      {/* Screenshot display */}
      <div className="flex-1 overflow-hidden bg-black flex items-center justify-center">
        {screenshot ? (
          <img
            src={`data:image/png;base64,${screenshot}`}
            alt="Browser screenshot"
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="text-gray-500 text-sm text-center px-4">
            {status === 'loading' ? 'Loading browser view...' : 'Browser will appear here when the agent starts browsing'}
          </div>
        )}
      </div>
    </div>
  );
}
