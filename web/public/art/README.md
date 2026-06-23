# Hero art

Drop the real pixel-Shiba art here as `hero.png` (transparent PNG, ~square,
e.g. 512×512). The homepage hero (`components/HeroScene.tsx`) renders it on top
of the SVG cube pedestal automatically. If the file is absent, a vector pixel
Shiba is shown as a fallback so the site never looks broken.

You can also add collection preview images later (e.g. `preview-1.png` …) and
wire them into the Collection section of `app/page.tsx`.
