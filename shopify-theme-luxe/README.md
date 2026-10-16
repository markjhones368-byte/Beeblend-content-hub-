# BeeBlend Luxe — Shopify homepage redesign

Design layer for the BeeBlend Refresh theme. Deployed to the **unpublished** theme
"BeeBlend Luxe Redesign (Preview)" — the live theme is untouched.

| File | What it is |
|---|---|
| `assets/bb-luxe.css` | Design system: charcoal / gold / honey / ivory, Bodoni Moda + Jost, cards, motion, header/footer restyle |
| `assets/bb-luxe.js` | Scroll reveal (IntersectionObserver), reduced-motion handling, quick-add into the native cart drawer |
| `sections/bb-hero.liquid` | Cinematic hero using the existing store video |
| `sections/bb-products.liquid` | Live product grid from any collection, size quick-add, sold-out handling |
| `sections/bb-collections.liquid` | Shop-by-collection cards (skips missing collections) |
| `sections/bb-story.liquid` | Editorial image + text, links to existing pages |
| `sections/bb-hive-to-jar.liquid` | Three-stage process + verified attribute pills |
| `sections/bb-ribbon.liquid` | Slow italic text ribbon |
| `templates/index.json` | New homepage order; every old section kept (disabled) so nothing is lost |
| `layout/theme.liquid` | Only additions: fonts, bb-luxe.css/js, two body classes |

No products, collections, handles, SEO metadata, apps or checkout settings are changed.
