import { NextRequest } from "next/server";
import traits from "@/data/robark-traits.json";
import { robarkSvg, type Traits } from "@/lib/robark-art";

const ALL = traits as unknown as Traits[];

// Renders token <id> live as an SVG. id may include a ".svg" suffix (e.g. 5.svg).
export async function GET(_req: NextRequest, { params }: { params: { id: string } }) {
  const id = parseInt(params.id, 10);
  if (!Number.isInteger(id) || id < 0 || id >= ALL.length) {
    return new Response("Not found", { status: 404 });
  }
  return new Response(robarkSvg(ALL[id]), {
    headers: {
      "content-type": "image/svg+xml; charset=utf-8",
      "cache-control": "public, max-age=31536000, immutable",
    },
  });
}
