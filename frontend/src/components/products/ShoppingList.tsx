import { ProductListing } from '../../types';

interface Props {
  items: ProductListing[];
  onRemove: (productId: string) => void;
}

export function ShoppingList({ items, onRemove }: Props) {
  const total = items.reduce((sum, item) => sum + item.price, 0);

  if (items.length === 0) {
    return (
      <div className="p-4 text-center text-gray-400 text-sm">
        <p>No items yet</p>
        <p className="text-xs mt-1">Items you approve will appear here</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {items.map(item => (
          <div
            key={item.id}
            className="flex items-center gap-3 bg-white rounded-lg p-2 border border-gray-100"
          >
            {item.image_url && (
              <img
                src={item.image_url}
                alt={item.title}
                className="w-12 h-12 rounded-md object-cover"
              />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-800 truncate">{item.title}</p>
              <p className="text-sm font-bold text-gray-900">${item.price.toFixed(2)}</p>
            </div>
            <button
              onClick={() => onRemove(item.id)}
              className="text-gray-300 hover:text-red-500 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        ))}
      </div>

      {/* Total */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex justify-between items-center mb-3">
          <span className="text-sm font-medium text-gray-600">Total ({items.length} items)</span>
          <span className="text-lg font-bold text-gray-900">${total.toFixed(2)}</span>
        </div>
        <button className="w-full py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors">
          Contact All Sellers
        </button>
      </div>
    </div>
  );
}
