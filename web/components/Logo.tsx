import Link from "next/link";

/**
 * ROBARK brand mark — a custom-drawn pixel dog head (droopy ears, snout),
 * designed as a logo, not a generated PFP. Cream silhouette, taupe ears,
 * rust nose, dark eyes — reads clean at any size on a dark surface.
 */
const GRID = [
  "                ",
  "      FFFF      ",
  "    FFFFFFFF    ",
  "  EEFFFFFFFFEE  ",
  " EEEFFFFFFFFEEE ",
  " EEEFFYFFYFFEEE ",
  " EEEFFFFFFFFEEE ",
  " EEEFFFFFFFFEEE ",
  " EEE FFFFFF EEE ",
  "  EE FFNNFF EE  ",
  "     FFNNFF     ",
  "     FFFFFF     ",
  "      FFFF      ",
  "                ",
  "                ",
  "                ",
];

const COLORS: Record<string, string> = {
  F: "#f4f1e8", // face
  E: "#9c6b43", // floppy ears
  N: "#d64a2f", // nose (rust accent)
  Y: "#1b1714", // eyes
};

export function BrandMark({ size = 32 }: { size?: number }) {
  const rects: JSX.Element[] = [];
  for (let y = 0; y < GRID.length; y++) {
    for (let x = 0; x < GRID[y].length; x++) {
      const fill = COLORS[GRID[y][x]];
      if (fill) rects.push(<rect key={`${x}-${y}`} x={x} y={y} width={1.02} height={1.02} fill={fill} />);
    }
  }
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" shapeRendering="crispEdges" aria-hidden="true">
      {rects}
    </svg>
  );
}

export function Logo() {
  return (
    <Link href="/" className="group flex items-center gap-2.5">
      <BrandMark size={32} />
      <span className="font-pixel text-[13px] leading-none tracking-tight text-robark-white">
        ROBARK
      </span>
    </Link>
  );
}
