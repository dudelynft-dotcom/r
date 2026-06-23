import { NextRequest } from "next/server";
import traits from "@/data/robark-traits.json";
import { type Traits, TRAIT_ORDER } from "@/lib/robark-art";

const ALL = traits as unknown as Traits[];

// OpenSea-standard metadata for token <id>, with image -> /api/art/<id>.svg
export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  const id = parseInt(params.id, 10);
  if (!Number.isInteger(id) || id < 0 || id >= ALL.length) {
    return new Response("Not found", { status: 404 });
  }
  const t = ALL[id];
  const base = (process.env.NEXT_PUBLIC_SITE_URL || new URL(req.url).origin).replace(/\/$/, "");
  const meta = {
    name: `ROBARK #${id}`,
    description:
      "ROBARK — 5,555 pixel degens who survived the crash. One dog, 5,555 bad days. " +
      "On-chain energy, served live.",
    image: `${base}/api/art/${id}.svg`,
    external_url: `${base}`,
    attributes: TRAIT_ORDER.map((k) => ({ trait_type: k, value: t[k] })),
  };
  return Response.json(meta, {
    headers: { "cache-control": "public, max-age=31536000, immutable" },
  });
}
