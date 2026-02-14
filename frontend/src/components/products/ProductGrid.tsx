import type { ProductListing } from '../../types';
import { ProductCard } from './ProductCard';

interface Props {
  products: ProductListing[];
  onAddToList?: (product: ProductListing) => void;
}

export function ProductGrid({ products, onAddToList }: Props) {
  return (
    <div className="w-full max-w-2xl">
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
        Found {products.length} listings
      </p>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {products.map(product => (
          <ProductCard
            key={product.id}
            product={product}
            onAddToList={onAddToList}
          />
        ))}
      </div>
    </div>
  );
}
