interface Props {
  colors: string[];
}

export function ColorPalette({ colors }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 w-full max-w-md">
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
        Suggested Color Palette
      </p>
      <div className="flex gap-2">
        {colors.map((color, i) => (
          <div key={i} className="flex-1 group cursor-pointer">
            <div
              className="h-12 rounded-lg shadow-sm transition-transform group-hover:scale-105"
              style={{ backgroundColor: color }}
            />
            <p className="text-xs text-center text-gray-400 mt-1.5 font-mono">
              {color}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
