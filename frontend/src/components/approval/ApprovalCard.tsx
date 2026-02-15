import { useState } from 'react';

export interface ProposalItem {
  id: string;
  title: string;
  price: number;
  source: string;
  url: string;
  image_url?: string;
  seller?: string;
  draft_message?: string;
}

interface Props {
  type: 'shortlist' | 'contact_sellers';
  items: ProposalItem[];
  onApproveAll: () => void;
  onApproveSelected: (ids: string[]) => void;
  onReject: () => void;
  resolved?: boolean;
}

export function ApprovalCard({ type, items, onApproveAll, onApproveSelected, onReject, resolved }: Props) {
  const [selected, setSelected] = useState<Set<string>>(new Set(items.map(i => i.id)));

  const toggle = (id: string) => {
    setSelected(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  if (resolved) {
    return (
      <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 text-sm text-gray-500">
        Decision submitted.
      </div>
    );
  }

  const isContact = type === 'contact_sellers';
  const heading = isContact ? 'Approve messages to sellers?' : 'Approve these picks?';

  return (
    <div className="rounded-xl border border-white/30 bg-white/40 backdrop-blur-xl shadow-lg overflow-hidden max-w-lg">
      <div className="px-4 py-3 bg-white/50 border-b border-gray-200/30">
        <h3 className="text-sm font-semibold text-gray-800">{heading}</h3>
        <p className="text-xs text-gray-500 mt-0.5">{items.length} item{items.length !== 1 ? 's' : ''} proposed</p>
      </div>

      <div className="divide-y divide-gray-200/30 max-h-72 overflow-y-auto">
        {items.map(item => (
          <label
            key={item.id}
            className="flex items-center gap-3 px-4 py-3 hover:bg-white/30 cursor-pointer transition-colors"
          >
            <input
              type="checkbox"
              checked={selected.has(item.id)}
              onChange={() => toggle(item.id)}
              className="w-4 h-4 rounded border-gray-300 text-gray-600 focus:ring-gray-400"
            />
            {item.image_url && (
              <img
                src={item.image_url}
                alt={item.title}
                className="w-12 h-12 rounded-lg object-cover bg-gray-100/50 shrink-0"
                onError={e => { (e.target as HTMLImageElement).style.display = 'none'; }}
              />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{item.title}</p>
              <p className="text-xs text-gray-500">
                ${item.price} &middot; {item.source}
                {item.seller && ` &middot; ${item.seller}`}
              </p>
              {isContact && item.draft_message && (
                <p className="text-xs text-gray-400 mt-1 italic truncate">"{item.draft_message}"</p>
              )}
            </div>
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-gray-500 hover:text-gray-700 hover:underline shrink-0"
              onClick={e => e.stopPropagation()}
            >
              View
            </a>
          </label>
        ))}
      </div>

      <div className="flex gap-2 px-4 py-3 bg-white/30 border-t border-gray-200/30">
        <button
          onClick={onApproveAll}
          className="flex-1 px-3 py-2 text-sm font-medium text-white bg-gray-700 rounded-lg hover:bg-gray-800 transition-colors shadow-sm"
        >
          Approve All
        </button>
        {selected.size < items.length && selected.size > 0 && (
          <button
            onClick={() => onApproveSelected(Array.from(selected))}
            className="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-white/50 border border-gray-300/40 rounded-lg hover:bg-white/70 transition-colors"
          >
            Approve {selected.size} Selected
          </button>
        )}
        <button
          onClick={onReject}
          className="px-3 py-2 text-sm font-medium text-gray-600 bg-white/50 border border-gray-300/40 rounded-lg hover:bg-white/70 transition-colors"
        >
          Reject
        </button>
      </div>
    </div>
  );
}
