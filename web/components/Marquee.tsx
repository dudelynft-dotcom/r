/**
 * Infinite scrolling strip of live ROBARK dogs (from /api/art).
 * Duplicated track so the loop is seamless.
 */
export function Marquee({
  ids,
  reverse = false,
  size = 96,
}: {
  ids: number[];
  reverse?: boolean;
  size?: number;
}) {
  const track = [...ids, ...ids];
  return (
    <div className="relative overflow-hidden">
      <div
        className={`flex w-max gap-3 ${reverse ? "animate-marquee-rev" : "animate-marquee"}`}
      >
        {track.map((id, i) => (
          <span
            key={`${id}-${i}`}
            className="tile shrink-0"
            style={{ width: size, height: size }}
          >
            <img src={`/api/art/${id}.svg`} alt={`ROBARK #${id}`} width={size} height={size} />
          </span>
        ))}
      </div>
      {/* edge fades */}
      <div className="pointer-events-none absolute inset-y-0 left-0 w-24 bg-gradient-to-r from-robark-black to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-24 bg-gradient-to-l from-robark-black to-transparent" />
    </div>
  );
}
