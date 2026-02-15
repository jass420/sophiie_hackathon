import { useState, useEffect, useRef } from 'react';

interface WorkerPanelProps {
  label: string;
  endpoint: string;
}

function WorkerPanel({ label, endpoint }: WorkerPanelProps) {
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [status, setStatus] = useState<'loading' | 'ok' | 'no_browser'>('loading');
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const fetchScreenshot = async () => {
      try {
        const res = await fetch(endpoint);
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
  }, [endpoint]);

  return (
    <div className="flex flex-col flex-1 min-w-0 rounded-xl overflow-hidden border border-gray-700 bg-gray-900">
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 border-b border-gray-700 shrink-0">
        <div className={`w-2 h-2 rounded-full ${status === 'ok' ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
        <span className="text-xs font-medium text-gray-300">{label}</span>
      </div>

      {/* Screenshot */}
      <div className="aspect-video bg-black flex items-center justify-center overflow-hidden">
        {screenshot ? (
          <img
            src={`data:image/png;base64,${screenshot}`}
            alt={`${label} screenshot`}
            className="w-full h-full object-contain"
          />
        ) : (
          <span className="text-gray-500 text-xs">
            {status === 'loading' ? 'Connecting...' : 'Waiting for agent...'}
          </span>
        )}
      </div>
    </div>
  );
}

interface BrowserViewProps {
  visible?: boolean;
}

export function BrowserView({ visible = true }: BrowserViewProps) {
  if (!visible) return null;

  return (
    <div className="flex gap-3 w-full mt-2">
      <WorkerPanel label="Worker A" endpoint="/api/browser/screenshot" />
      <WorkerPanel label="Worker B" endpoint="/api/browser/screenshot-b" />
    </div>
  );
}
