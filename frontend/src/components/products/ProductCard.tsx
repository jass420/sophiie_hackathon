import { ProductListing } from '../../types';

interface Props {
  product: ProductListing;
  onAddToList?: (product: ProductListing) => void;
}

const SOURCE_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  ebay: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'eBay' },
  facebook: { bg: 'bg-indigo-100', text: 'text-indigo-700', label: 'FB Marketplace' },
  gumtree: { bg: 'bg-green-100', text: 'text-green-700', label: 'Gumtree' },
};

export function ProductCard({ product, onAddToList }: Props) {
  const source = SOURCE_STYLES[product.source] || SOURCE_STYLES.ebay;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow">
      {/* Image */}
      {product.image_url && (
        <div className="aspect-square bg-gray-100">
          <img
            src={product.image_url}
            alt={product.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
        </div>
      )}

      <div className="p-3">
        {/* Source badge */}
        <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${source.bg} ${source.text} mb-2`}>
          {source.label}
        </span>

        {/* Title */}
        <h3 className="text-sm font-medium text-gray-800 line-clamp-2 mb-1">
          {product.title}
        </h3>

        {/* Price */}
        <p className="text-lg font-bold text-gray-900 mb-1">
          ${product.price.toFixed(2)}
          <span className="text-xs font-normal text-gray-400 ml-1">{product.currency}</span>
        </p>

        {/* Condition & location */}
        <div className="flex items-center gap-2 text-xs text-gray-400 mb-3">
          {product.condition && <span>{product.condition}</span>}
          {product.condition && product.location && <span>·</span>}
          {product.location && <span>{product.location}</span>}
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          {product.url && (
            <a
              href={product.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 text-center py-1.5 text-xs font-medium text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
            >
              View Listing
            </a>
          )}
          {onAddToList && (
            <button
              onClick={() => onAddToList(product)}
              className="flex-1 py-1.5 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add to List
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
