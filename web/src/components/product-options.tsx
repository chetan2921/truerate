import type { Product } from "@/lib/api";

// The product list, grouped under the WLDD category each one is priced and fit-checked with.
export default function ProductOptions({ products, categories }: { products: Product[]; categories: string[] }) {
  return categories.map((c) => (
    <optgroup key={c} label={c}>
      {products
        .filter((p) => p.category === c)
        .map((p) => (
          <option key={p.name} value={p.name}>
            {p.name}
          </option>
        ))}
    </optgroup>
  ));
}
