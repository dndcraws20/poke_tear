# poke_tear — Pokémon Pack Opener

Single-file pack-opening game with a set picker for Mega Evolution — Chaos Rising (ME04), Pitch Black (ME05), Phantasmal Flames (ME02), Scarlet & Violet — Destined Rivals (SV10), and Scarlet & Violet — 151 (SV03.5).

- **Sandbox** — free rips, every card shows its market value.
- **Normal** — start with $60, packs cost $4.99, cards auto-sell at real TCGplayer market prices, buy upgrades, don't go broke.
- **PSA grading** — optionally grade any pulled card once. Grades 1–4 lose value, PSA 5 keeps its value, and grades 6–10 increase it; PSA 10 has a 2% chance and pays 10×.
- **Set switching** — swap between Pitch Black ($4.99), Chaos Rising ($9.99), Destined Rivals ($15.00), Phantasmal Flames ($22.50), and 151 ($35.00) during the same run without losing your bankroll, upgrades, quota, or stats. The premium 151 set receives a 2× game-value boost.
- **Quota challenge** — Normal mode gives you 60 seconds to reach a $50 bankroll quota. Each cleared quota is 1.5× larger; packs and upgrades reduce your bankroll progress. Missing the deadline ends the run, and the game remembers your highest quota.
- **Hard mode** — 30-second rounds begin with a $75 quota, quotas grow by 1.75×, packs cost 25% more, and chase-card odds are cut in half. Missing a quota or running out of money ends the run.
- **Seven upgrades** — improve chase odds, bulk values, reverse slots, pack discounts, PSA grades, holo values, and the chance of pulling a bonus hit card. Upgrades last for the entire run.

**Play it:** https://dndcraws20.github.io/poke_tear/ (GitHub Pages, publishes from `main`)

Mirror: https://preview.sasta.ai/pack-opener/

## Files

| File | What |
|---|---|
| `index.html` | The whole game (generated, do not hand-edit). |
| `build.py` | Generator. Edits to the game go here; run `python build.py` to rebuild `index.html`. |
| `me04-cards.json` | All 122 Chaos Rising cards with rarity + TCGplayer/cardmarket prices (from TCGdex). |
| `me05-cards.json` | All 120 Pitch Black cards with rarity + TCGplayer/cardmarket prices (from TCGdex). |
| `sv10-cards.json` | All 244 Destined Rivals cards with rarity + TCGplayer/cardmarket prices (from TCGdex). |
| `me02-cards.json` | All 130 Phantasmal Flames cards with rarity + TCGplayer/cardmarket prices (from TCGdex). |
| `sv03.5-cards.json` | All 207 Scarlet & Violet—151 cards with rarity + TCGplayer/cardmarket prices (from TCGdex). |
| `chaos-rising-pack.png` | Chaos Rising booster pack art. |
| `destined-rivals-pack.jpg` | Destined Rivals booster pack art. |
| `phantasmal-flames-pack.png` | Phantasmal Flames booster pack art. |
| `pokemon-151-pack.png` | Scarlet & Violet—151 booster pack art. |
| `pack.jpg` | Pitch Black booster pack art. |

`build.py` writes `index.html` next to itself.

## Refresh prices

Re-fetch each card from `https://api.tcgdex.net/v2/en/cards/SET-NNN` (fields `rarity`, `image`, `pricing.tcgplayer`) into the matching set JSON, bump `PRICE_DATE` in `build.py`, and rebuild.

## Deploy

```
scp index.html pack.jpg chaos-rising-pack.png destined-rivals-pack.jpg phantasmal-flames-pack.png pokemon-151-pack.png root@<vps>:/var/www/pack-opener/
```

Card art is hotlinked from `assets.tcgdex.net`; the nginx location block for `/pack-opener/` carries its own CSP allowing that host.
