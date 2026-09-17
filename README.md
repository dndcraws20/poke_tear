# poke_tear — Pokémon Pack Opener

Single-file pack-opening game with a set picker for Mega Evolution — Chaos Rising (ME04) and Pitch Black (ME05).

- **Sandbox** — free rips, every card shows its market value.
- **Normal** — start with $60, packs cost $4.99, cards auto-sell at real TCGplayer market prices, buy upgrades, don't go broke.
- **PSA grading** — optionally grade any pulled card once. Grades 1–4 lose value, PSA 5 keeps its value, and grades 6–10 increase it; PSA 10 has a 2% chance and pays 10×.

**Play it:** https://dndcraws20.github.io/poke_tear/ (GitHub Pages, publishes from `main`)

Mirror: https://preview.sasta.ai/pack-opener/

## Files

| File | What |
|---|---|
| `index.html` | The whole game (generated, do not hand-edit). |
| `build.py` | Generator. Edits to the game go here; run `python build.py` to rebuild `index.html`. |
| `me04-cards.json` | All 122 Chaos Rising cards with rarity + TCGplayer/cardmarket prices (from TCGdex). |
| `me05-cards.json` | All 120 Pitch Black cards with rarity + TCGplayer/cardmarket prices (from TCGdex). |
| `chaos-rising-pack.png` | Chaos Rising booster pack art. |
| `pack.jpg` | Pitch Black booster pack art. |

`build.py` writes `index.html` next to itself.

## Refresh prices

Re-fetch each card from `https://api.tcgdex.net/v2/en/cards/SET-NNN` (fields `rarity`, `image`, `pricing.tcgplayer`) into the matching set JSON, bump `PRICE_DATE` in `build.py`, and rebuild.

## Deploy

```
scp index.html pack.jpg chaos-rising-pack.png root@<vps>:/var/www/pack-opener/
```

Card art is hotlinked from `assets.tcgdex.net`; the nginx location block for `/pack-opener/` carries its own CSP allowing that host.
