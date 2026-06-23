const MONO_BG = ["#1e1e22", "#23201d", "#1d2220", "#221d22", "#20211d"];

function hash(s: string) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

function initials(name: string) {
  const parts = name.replace(/[^a-zA-Z0-9 ]/g, "").trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

/**
 * Eligible-collection "game card": PFP (or pixel monogram fallback) + name.
 * `held` highlights the card when the checked wallet owns it.
 */
export function CollectionCard({
  name,
  image,
  held = false,
  count,
}: {
  name: string;
  image?: string | null;
  held?: boolean;
  count?: number;
}) {
  return (
    <div
      className={`group relative overflow-hidden border bg-robark-ink p-1.5 transition ${
        held ? "border-robark-green shadow-[0_0_0_1px_#35d07f]" : "border-robark-line hover:border-robark-soft"
      }`}
    >
      <div className="relative aspect-square overflow-hidden border border-robark-line">
        {image ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={image} alt={name} className="h-full w-full object-cover transition group-hover:scale-105" loading="lazy" />
        ) : (
          <div
            className="grid h-full w-full place-items-center"
            style={{ background: MONO_BG[hash(name) % MONO_BG.length] }}
          >
            <span className="font-pixel text-lg text-robark-fog sm:text-xl">{initials(name)}</span>
          </div>
        )}

        {held && (
          <span className="absolute right-1 top-1 bg-robark-green px-1.5 py-0.5 font-mono text-[9px] font-bold text-robark-black">
            HELD{count ? ` ×${count}` : ""}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between gap-1 px-0.5 pt-2 pb-0.5">
        <span className="truncate font-mono text-[11px] text-robark-fog" title={name}>{name}</span>
        <span className={`shrink-0 text-[9px] ${held ? "text-robark-green" : "text-robark-mute"}`}>●</span>
      </div>
    </div>
  );
}
