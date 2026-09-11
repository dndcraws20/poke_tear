# poke_tear — Pokémon Pack Opener (Pitch Black · ME05)

Single-file pack-opening game for the Mega Evolution — Pitch Black set.

- **Sandbox** — free rips, every card shows its market value.
- **Normal** — start with $60, packs cost $4.99, cards auto-sell at real TCGplayer market prices, buy upgrades, don't go broke.

Live: https://preview.sasta.ai/pack-opener/

## Files

| File | What |
|---|---|
| `index.html` | The whole game (generated, do not hand-edit). |
| `build.py` | Generator. Edits to the game go here; run `python build.py` to rebuild `index.html`. |
| `me05-cards.json` | All 120 ME05 cards with rarity + TCGplayer/cardmarket prices (from TCGdex, 2026-09-10). |
| `pack.jpg` | Booster pack art. |

`build.py` writes `index.html` next to itself.

## Refresh prices

Re-fetch each card from `https://api.tcgdex.net/v2/en/cards/me05-NNN` (fields `rarity`, `image`, `pricing.tcgplayer`) into `me05-cards.json`, bump `PRICE_DATE` in `build.py`, rebuild.

## Deploy

```
scp index.html pack.jpg root@<vps>:/var/www/pack-opener/
```

Card art is hotlinked from `assets.tcgdex.net`; the nginx location block for `/pack-opener/` carries its own CSP allowing that host.
