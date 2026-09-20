# poke_tear — Pokémon Pack Opener

Single-file pack-opening game with a set picker for Mega Evolution — Chaos Rising (ME04), Pitch Black (ME05), Phantasmal Flames (ME02), Scarlet & Violet — Destined Rivals (SV10), Scarlet & Violet — 151 (SV03.5), Sun & Moon (SM1), Sun & Moon—Dragon Majesty (SM7.5), and the original 1999 Base Set First Edition (BASE1).

- **Sandbox** — free rips, every card shows its market value.
- **Chill** — no quota or timer, but packs and upgrades still cost money and the run ends if you cannot afford another pack.
- **Sandbox upgrades** — the full upgrade shop is available for free in Sandbox mode.
- **Normal** — start with $60, packs cost $4.99, cards auto-sell at real TCGplayer market prices, buy upgrades, don't go broke.
- **PSA grading** — optionally grade any pulled card once. Grades 1–4 lose value, PSA 5 keeps its value, and grades 6–10 increase it; PSA 10 has a 2% chance and pays 10×.
- **Set switching** — swap between Pitch Black ($4.99), Chaos Rising ($9.99), Destined Rivals ($15.00), Phantasmal Flames ($22.50), 151 ($35.00), Sun & Moon ($50.00), and Dragon Majesty ($100.00) during the same run without losing your bankroll, upgrades, quota, or stats. Dragon Majesty gets a premium 2.4× card-value boost.
- **Four pack stores** — Pokémon Store packs cost 10% more but give 2× chase luck, better PSA odds, and are always real. Walmart uses normal prices and always-real packs. Temu is 10% cheaper with a 10% fake-pack risk. The Black Market is 30% cheaper with a 30% fake-pack risk. Every card from a fake pack is worth $0, including after grading or Binder growth.
- **Quota challenge** — Normal mode gives you 60 seconds to reach a $50 bankroll quota. Each cleared quota is 1.5× larger; packs and upgrades reduce your bankroll progress. Missing the deadline ends the run, and the game remembers your highest quota.
- **Hard mode** — 30-second rounds begin with a $75 quota, quotas grow by 1.75×, packs cost 25% more, and chase-card odds are cut in half. Missing a quota or running out of money ends the run.
- **Twenty-two upgrades** — alongside the pack, PSA, quota, and Binder upgrades, five new battle upgrades increase deck HP, increase attack damage, reduce permanent training prices, discount Bribe from $300 down to $150, and boost single-battle and tournament rewards by up to 50%. Every upgrade is free in Sandbox and lasts for the entire run.
- **Run missions** — complete three goals by opening packs, grading cards, and finding a $20+ pull. Missions track progress in their own panel and automatically pay cash rewards that can help reach the next quota.
- **Upgradeable card binder** — begin with space for eight cards and upgrade capacity through 11, 14, and 17 to a maximum of 20. Collector Interest upgrades raise the hidden value increase after one minute from 20% to 30%, 40%, and finally 50%, while price text updates without resetting or blinking cards. Binder cards retain large artwork, names, rarities, PSA grading, battle-deck selection, and selling controls.
- **Fresh-run Binder reset** — choosing any new game mode or pressing New Run clears all Binder cards and the three-card battle deck, preventing cards from an earlier run from being sold in a new one. Continuing a saved run keeps its cards.
- **Interactive three-card Binder battles** — build a deck from three Binder cards, train them through ten levels, and enter a full battle screen with both teams visible. Every turn, choose which surviving Pokémon attacks; its strongest-damage move hits the current opponent, then a random enemy strikes back. Single random-trainer battles remain completely free. Best-of-five tournaments charge modest entry fees of $50 Easy, $200 Normal, $500 Hard, or $1,000 Impossible for prizes up to $20,000; Sandbox tournaments remain free practice. The once-per-match Bribe ability costs $300 and makes the next chosen Pokémon attack twice before the opponent responds. The quota clock pauses for the entire active fight, and cooldowns begin after the battle finishes.
- **Two original soundtracks** — switch between the wordless Electronic track and Pixel Calm, a slower ambient track with peaceful piano-like notes. Both are generated live in the browser and include Music On/Off controls.
- **Six-pack boxes** — buy six packs of the selected set together for 10% less than purchasing them one at a time, then open the stored packs individually.
- **Base Set First Edition** — a $10,000 premium pack with all 102 original cards, an authentic 11-card layout, premium First Edition values, and extremely low holographic odds.
- **Kiss the Pack** — activate a 2× chase-card luck boost for the next opened pack, then wait through a visible 30-second cooldown before kissing another pack.
- **Shake the Pack** — risk a forced PSA 1 on every card from the next pack in exchange for 5× chase luck. Upgrades raise the boost to 7× or 10× and reduce its 60-second cooldown.

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
| `sm1-cards.json` | All 172 Sun & Moon cards with rarity + TCGplayer/cardmarket prices (from TCGdex). |
| `sm7.5-cards.json` | All 78 Dragon Majesty cards with rarity + TCGplayer/cardmarket prices. |
| `base1-cards.json` | All 102 original Base Set cards with First Edition variant values (from TCGdex). |
| `chaos-rising-pack.png` | Chaos Rising booster pack art. |
| `destined-rivals-pack.jpg` | Destined Rivals booster pack art. |
| `phantasmal-flames-pack.png` | Phantasmal Flames booster pack art. |
| `pokemon-151-pack.png` | Scarlet & Violet—151 booster pack art. |
| `sun-moon-pack.png` | Authentic-style Lunala Sun & Moon booster pack artwork used by the game. |
| `dragon-majesty-pack.jpg` | Dragon Majesty Salamence booster pack artwork used by the game. |
| `first-edition-pack.jpg` | Classic Charizard Base Set First Edition booster pack artwork used by the game. |
| `pack.jpg` | Pitch Black booster pack art. |

`build.py` writes `index.html` next to itself.

## Refresh prices

Re-fetch each card from `https://api.tcgdex.net/v2/en/cards/SET-NNN` (fields `rarity`, `image`, `pricing.tcgplayer`) into the matching set JSON, bump `PRICE_DATE` in `build.py`, and rebuild.

## Deploy

```
scp index.html pack.jpg chaos-rising-pack.png destined-rivals-pack.jpg phantasmal-flames-pack.png pokemon-151-pack.png sun-moon-pack.png dragon-majesty-pack.jpg first-edition-pack.jpg root@<vps>:/var/www/pack-opener/
```

Card art is hotlinked from `assets.tcgdex.net` and `images.pokemontcg.io`; the nginx location block for `/pack-opener/` must allow both hosts in its CSP.
