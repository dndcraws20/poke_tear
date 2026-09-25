import json, os
here = os.path.dirname(os.path.abspath(__file__))
sets = {}
for set_id in ("30th", "me04", "me05", "me03", "me02.5", "me01", "swsh1", "sv10", "me02", "sv03.5", "sm1", "sm7.5", "base1"):
    cards = json.load(open(os.path.join(here, f"{set_id}-cards.json"), encoding="utf-8"))
    series_id = "me" if set_id == "30th" else "".join(ch for ch in set_id if ch.isalpha())
    pre = f"https://assets.tcgdex.net/en/{series_id}/{set_id}/"
    sets[set_id] = [
        {"id": c["id"], "n": c["n"], "r": c["r"], "img": c["img"][len(pre):] if c.get("img", "").startswith(pre) else c.get("img", ""), "p": c["p"], "pr": c["pr"], "ph": c["ph"]}
        for c in cards
    ]
data = json.dumps(sets, separators=(",", ":"), ensure_ascii=False)

html = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Pokémon Pack Opener</title>
  <style>
    * { box-sizing: border-box; }
    [hidden] { display: none !important; }
    body { margin: 0; background: radial-gradient(circle at top, #2b1050, #08050d 65%); color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; min-height: 100vh; }
    .wrap { max-width: 1000px; margin: auto; padding: 14px 14px 60px; text-align: center; }
    h1 { font-size: 30px; margin: 6px 0; }
    h2 { font-size: 22px; margin: 6px 0; }
    .sub { opacity: .78; margin: 6px 0; }
    .screen { display: none; }
    .screen.on { display: block; }
    #home.on { min-height: 92vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .pack { width: min(260px, 64vw); border-radius: 14px; box-shadow: 0 20px 40px #000b; }
    .set-picker { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin: 14px 0 2px; }
    .set-choice { width: 190px; min-height: 92px; padding: 10px; background: #151020; color: #fff; border: 2px solid #3d2a57; }
    .set-choice.on { border-color: #ffe066; box-shadow: 0 0 18px #ffb30055; }
    .set-choice img { width: 100%; height: 45px; object-fit: contain; display: block; margin-bottom: 5px; }
    .set-choice small { display: block; opacity: .72; }
    .store-picker { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin: 12px 0; }
    .store-choice { width: 190px; min-height: 86px; padding: 10px; background: #151020; color: #fff; border: 2px solid #3d2a57; text-align: left; }
    .store-choice.on { border-color: #65e6ff; box-shadow: 0 0 18px #22d3ee55; }
    .store-choice b, .store-choice small { display: block; }
    .store-choice small { margin-top: 4px; opacity: .72; line-height: 1.25; font-weight: 500; }
    .mystery-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin: 16px 0; }
    .mystery-item { background: #1c1529; border: 1px solid #654d83; border-radius: 16px; padding: 12px; text-align: left; display: flex; align-items: center; gap: 12px; }
    .mystery-item img { width: 112px; height: 168px; object-fit: contain; border-radius: 8px; flex: none; }
    .mystery-item .body { min-width: 0; }
    .mystery-item b, .mystery-item small { display: block; }
    .mystery-item small { margin: 5px 0; opacity: .8; line-height: 1.35; }
    .mystery-item button { padding: 10px 12px; margin: 7px 0 0; font-size: 13px; width: 100%; }
    @media (max-width: 700px) { .mystery-grid { grid-template-columns: 1fr; } .mystery-item img { width: 96px; height: 145px; } }
    button, .btn { display: inline-block; border-radius: 14px; text-decoration: none; font-weight: 900; cursor: pointer; border: 0; font-family: inherit; font-size: 16px; padding: 14px 22px; margin: 6px 4px; color: #180b00; background: #ffe066; -webkit-tap-highlight-color: transparent; }
    button:disabled { opacity: .35; cursor: not-allowed; }
    .primary { padding: 18px 36px; background: linear-gradient(#ffe66b, #ff9800); font-size: 20px; box-shadow: 0 7px #985500; }
    .primary:active:not(:disabled) { transform: translateY(5px); box-shadow: 0 2px #985500; }
    .ghost { background: #332744; color: #fff; }
    .modes { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; margin-top: 18px; }
    .mode { background: #151020; border: 1px solid #654d83; border-radius: 16px; padding: 14px 16px; width: 250px; text-align: left; color: #fff; }
    .mode b { display: block; font-size: 18px; margin-bottom: 4px; }
    .mode small { opacity: .75; line-height: 1.35; display: block; font-weight: 400; }
    .mode:active { transform: scale(.98); }
    .hud { display: flex; justify-content: space-between; align-items: center; gap: 8px; background: #120c1c; border: 1px solid #3d2a57; border-radius: 14px; padding: 10px 14px; margin-bottom: 10px; position: sticky; top: 8px; z-index: 5; box-shadow: 0 8px 20px #0009; text-align: left; }
    .hud .bank { font-size: 24px; font-weight: 900; color: #8dffb0; }
    .hud .bank.low { color: #ff6b6b; }
    .hud small { opacity: .7; display: block; font-size: 11px; }
    .hud .r { text-align: right; }
    .quota { background: #151020; border: 1px solid #ffd54a; border-radius: 14px; padding: 10px 14px; margin: 0 auto 10px; max-width: 620px; text-align: left; }
    .quota-top { display: flex; justify-content: space-between; gap: 12px; font-weight: 900; }
    .quota-time { color: #ffe066; }
    .quota-time.danger { color: #ff6b6b; animation: glow 1s ease-in-out infinite alternate; }
    .quota-track { height: 10px; margin-top: 8px; background: #08050d; border-radius: 999px; overflow: hidden; }
    .quota-fill { height: 100%; width: 0; background: linear-gradient(90deg, #ff9800, #ffe66b, #8dffb0); transition: width .25s; }
    .quota small { opacity: .72; display: block; margin-top: 6px; }
    .cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; max-width: 900px; margin: 16px auto; }
    .card { position: relative; background: #151020; border: 1px solid #654d83; border-radius: 14px; padding: 8px; box-shadow: 0 12px 24px #0008; animation: pop .45s both; }
    .card.r2 { border-color: #7fb8ff; }
    .card.r3 { border-color: #ffd54a; box-shadow: 0 0 22px #ffb30088, 0 12px 24px #0008; }
    .card.r4 { border-color: #ff5ce0; box-shadow: 0 0 30px #ff4fd0aa, 0 12px 24px #0008; animation: pop .6s both, glow 1.6s ease-in-out infinite alternate; }
    .card img { width: 100%; display: block; border-radius: 9px; background: #222; aspect-ratio: 63/88; object-fit: contain; }
    .name { font-weight: 900; font-size: 14px; margin-top: 7px; }
    .rarity { font-size: 11px; opacity: .7; margin-top: 2px; }
    .val { position: absolute; top: 12px; right: 12px; background: #05240fdd; color: #8dffb0; font-weight: 900; font-size: 13px; padding: 4px 8px; border-radius: 999px; border: 1px solid #22c55e; animation: pop .4s both; }
    .val.big { background: #3a0b30dd; color: #ffb3f0; border-color: #ff5ce0; font-size: 15px; }
    .val.rev { color: #c9b6ff; border-color: #a78bfa; background: #1d1040dd; }
    .tag { position: absolute; top: 12px; left: 12px; font-size: 10px; font-weight: 900; padding: 3px 7px; border-radius: 999px; background: #a78bfa; color: #14092e; }
    .grade-btn { width: 100%; margin: 8px 0 0; padding: 8px 6px; border-radius: 9px; font-size: 12px; background: linear-gradient(#e8f2ff, #77aee8); color: #071b31; }
    .grade-btn:disabled { opacity: 1; cursor: default; background: #25364a; color: #d6e9ff; }
    .keep-btn { width: 100%; margin: 6px 0 0; padding: 8px 6px; border-radius: 9px; font-size: 12px; background: linear-gradient(#b7ffd0, #38c76f); color: #052612; }
    .grade-result { margin-top: 6px; padding: 6px; border-radius: 8px; background: #0b2138; color: #bdddff; font-size: 11px; font-weight: 800; }
    .summary { background: #151020; border: 1px solid #3d2a57; border-radius: 14px; padding: 10px 14px; margin: 8px auto; max-width: 520px; font-size: 15px; }
    .summary .delta { font-size: 24px; font-weight: 900; }
    .delta.up { color: #8dffb0; } .delta.down { color: #ff6b6b; }
    .note { font-size: 12px; opacity: .6; margin-top: 12px; }
    .actions { position: sticky; bottom: 0; padding: 10px 0 12px; background: linear-gradient(transparent, #08050d 40%); }
    .pack-opening { position: fixed; inset: 0; z-index: 60; display: none; overflow: hidden; background: radial-gradient(circle at 50% 45%, #43205f 0, #13091f 48%, #050308 100%); }
    .pack-opening.on { display: block; }
    .opening-stage { position: relative; width: 100%; height: 100%; padding: max(18px, env(safe-area-inset-top)) 14px max(18px, env(safe-area-inset-bottom)); }
    .opening-title { position: absolute; left: 0; right: 0; top: max(24px, env(safe-area-inset-top)); color: #ffe066; font-size: clamp(19px, 5vw, 30px); font-weight: 1000; text-align: center; text-shadow: 0 3px 16px #000; }
    .opening-pack { position: absolute; left: 50%; top: 50%; width: min(48vw, 230px); transform: translate(-50%, -50%) scale(.65); filter: drop-shadow(0 24px 25px #000b); animation: packArrive .42s cubic-bezier(.2,.8,.2,1) forwards; }
    .opening-pack img { display: block; width: 100%; max-height: 52vh; object-fit: contain; }
    .opening-pack.opened img { clip-path: inset(13% 0 0 0); }
    .pack-rip { position: absolute; inset: 0; overflow: hidden; clip-path: inset(0 0 86% 0); opacity: 0; pointer-events: none; }
    .pack-rip img { width: 100%; }
    .pack-rip.tear { opacity: 1; animation: tearTop .62s cubic-bezier(.2,.7,.3,1) forwards; }
    .flying-cards { position: absolute; inset: 14% 4% 5%; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); align-content: center; justify-items: center; gap: 7px; pointer-events: none; }
    .flying-card { width: min(31vw, 116px); max-height: 23vh; aspect-ratio: 63/88; object-fit: contain; border-radius: 7px; opacity: 0; filter: drop-shadow(0 8px 8px #000b); will-change: transform, opacity; }
    .overlay { position: fixed; inset: 0; background: #000a; display: none; align-items: flex-end; justify-content: center; z-index: 20; }
    .overlay.on { display: flex; }
    .sheet { background: #14101f; border: 1px solid #654d83; border-radius: 20px 20px 0 0; width: min(560px, 100%); max-height: 88vh; overflow: auto; padding: 16px 16px 26px; text-align: left; }
    .up { display: flex; gap: 12px; align-items: center; background: #1c1529; border: 1px solid #3d2a57; border-radius: 14px; padding: 12px; margin: 10px 0; }
    .up .ico { font-size: 30px; width: 40px; text-align: center; }
    .up .body { flex: 1; }
    .up b { display: block; font-size: 15px; }
    .up small { opacity: .75; display: block; line-height: 1.35; margin-top: 2px; }
    .up .tier { font-size: 11px; color: #ffd54a; margin-top: 4px; font-weight: 900; }
    .up button { margin: 0; padding: 10px 14px; font-size: 14px; white-space: nowrap; }
    .up.max button { background: #2a3d2e; color: #8dffb0; }
    .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; max-width: 460px; margin: 14px auto; }
    .stat { background: #151020; border: 1px solid #3d2a57; border-radius: 12px; padding: 10px; }
    .stat b { display: block; font-size: 20px; }
    .stat small { opacity: .7; font-size: 11px; }
    .best { max-width: 220px; margin: 10px auto; }
    .binder-sheet { width: min(820px, 100%); }
    .binder-cards { display: grid; grid-template-columns: 1fr; gap: 20px; margin: 16px auto; }
    .binder-card { width: 100%; max-width: 360px; margin: auto; padding: 12px; }
    .binder-card img { cursor: zoom-in; }
    .trade-grid { display: grid; grid-template-columns: 1fr 48px 1fr; gap: 10px; align-items: center; margin: 16px 0; }
    .trade-card { background: #1c1529; border: 2px solid #654d83; border-radius: 14px; padding: 10px; text-align: center; }
    .trade-card img { width: 100%; max-height: 330px; aspect-ratio: 63/88; object-fit: contain; border-radius: 9px; background: #222; }
    .trade-card b { display: block; margin-top: 7px; }
    .trade-card small { display: block; opacity: .72; margin-top: 3px; }
    .trade-vs { text-align: center; font-size: 24px; font-weight: 1000; color: #ffe066; }
    .zoom-card { max-width: min(440px, 94vw); max-height: 88vh; border-radius: 16px; box-shadow: 0 20px 60px #000; }
    .battle-sheet { width: min(920px, 100%); }
    .battle-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 12px 0; }
    .battle-choice { background: #1c1529; border: 2px solid #3d2a57; border-radius: 14px; padding: 8px; text-align: center; }
    .battle-choice.selected { border-color: #ffe066; box-shadow: 0 0 18px #ffb30055; }
    .battle-choice img { width: 100%; max-height: 210px; aspect-ratio: 63/88; object-fit: contain; border-radius: 9px; background: #222; }
    .battle-choice button { width: 100%; margin: 5px 0 0; padding: 8px 5px; font-size: 12px; }
    .battle-stats { color: #8dffb0; font-size: 12px; font-weight: 900; margin: 6px 0; }
    .battle-modes { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
    .battle-modes button { margin: 0; padding: 11px 6px; font-size: 13px; }
    .battle-result { margin-top: 14px; padding: 12px; background: #0d0915; border: 1px solid #654d83; border-radius: 14px; }
    .battle-result.win { border-color: #22c55e; }
    .battle-result.loss { border-color: #ef4444; }
    .battle-log { max-height: 260px; overflow: auto; margin-top: 10px; padding: 9px; background: #08050d; border-radius: 10px; font-size: 12px; line-height: 1.5; }
    .battle-log b { color: #ffe066; }
    .battle-arena { display: grid; grid-template-columns: 1fr 42px 1fr; gap: 8px; align-items: center; margin: 12px 0; }
    .battle-lineup { display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; }
    .battle-fighter { min-width: 0; text-align: center; padding: 5px; background: #1c1529; border: 1px solid #3d2a57; border-radius: 10px; }
    button.battle-fighter { margin: 0; color: #fff; cursor: pointer; }
    button.battle-fighter:not(:disabled):active { transform: scale(.96); }
    .battle-fighter.ready { border-color: #ffe066; box-shadow: 0 0 15px #ffb30055; }
    .battle-fighter.target { border-color: #ff5c5c; box-shadow: 0 0 16px #ff333355; }
    .battle-fighter.ko { opacity: .35; filter: grayscale(1); }
    .battle-fighter img { width: 100%; aspect-ratio: 63/88; object-fit: contain; background: #222; border-radius: 6px; }
    .battle-fighter b { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 10px; margin-top: 3px; }
    .battle-fighter small { display: block; color: #8dffb0; font-size: 9px; }
    .battle-vs { text-align: center; color: #ffe066; font-size: 20px; font-weight: 1000; }
    .health-track { height: 7px; background: #09060d; border-radius: 99px; overflow: hidden; margin: 4px 0; }
    .health-fill { height: 100%; background: linear-gradient(90deg, #ef4444, #facc15, #22c55e); transition: width .25s; }
    .battle-prompt { text-align: center; color: #ffe066; font-size: 18px; font-weight: 1000; margin: 10px 0; }
    .main-tools { display: grid; grid-template-columns: repeat(2, 1fr); gap: 7px; margin: 10px 0 14px; }
    .main-tools .ghost { margin: 0; padding: 9px 6px; font-size: 11px; }
    @keyframes pop { from { opacity: 0; transform: scale(.7) translateY(25px); } to { opacity: 1; transform: none; } }
    @keyframes glow { from { box-shadow: 0 0 18px #ff4fd088; } to { box-shadow: 0 0 44px #ff4fd0ee, 0 0 80px #ff9800aa; } }
    @keyframes flash { 0% { background: #22c55e66; } 100% { background: #120c1c; } }
    @keyframes packArrive { to { transform: translate(-50%, -50%) scale(1); } }
    @keyframes tearTop { 0% { transform: none; } 35% { transform: translateY(-8px) rotate(-5deg); } 100% { transform: translate(70vw, -35vh) rotate(42deg); opacity: 0; } }
    .flash { animation: flash .8s; }
    @media (min-width: 700px) { .cards { grid-template-columns: repeat(5, 1fr); } .binder-cards { grid-template-columns: repeat(2, 1fr); } .battle-grid { grid-template-columns: repeat(4, 1fr); } .battle-modes { grid-template-columns: repeat(4, 1fr); } .overlay { align-items: center; } .sheet { border-radius: 20px; } .flying-cards { grid-template-columns: repeat(5, minmax(0, 1fr)); inset: 16% 5% 5%; gap: 10px; } .flying-card { width: min(14vw, 125px); max-height: 34vh; } }
    @media (prefers-reduced-motion: reduce) { .opening-pack, .pack-rip.tear { animation-duration: .01ms; } }
  </style>
</head>
<body>
  <div class="pack-opening" id="packOpening" aria-hidden="true">
    <div class="opening-stage">
      <div class="opening-title" id="openingTitle">OPENING PACK…</div>
      <div class="opening-pack" id="openingPack"><img id="openingPackImage" src="pack.jpg" alt=""><div class="pack-rip" id="packRip"><img id="openingPackTop" src="pack.jpg" alt=""></div></div>
      <div class="flying-cards" id="flyingCards"></div>
    </div>
  </div>
  <div class="wrap">

    <section id="home" class="screen on">
      <h1>🎴 Pokémon Pack Opener</h1>
      <p class="sub" id="setTitle"></p>
      <img class="pack" id="packArt" src="pack.jpg" alt="Selected Pokémon set">
      <div class="set-picker" id="setPicker"></div>
      <h2>Choose a store</h2>
      <div class="store-picker" id="storePicker"></div>
      <div class="modes">
        <button class="mode" id="btnNormal"><b>💸 Normal</b><small>Start with <span id="startBank"></span>. Packs cost real money, cards sell at live market value. Buy upgrades, don't go broke.</small></button>
        <button class="mode" id="btnChill"><b>😌 Chill</b><small>No quota or timer. Packs and upgrades still cost money, and the run ends if you go broke.</small></button>
        <button class="mode" id="btnHard"><b>🔥 Hard</b><small>30-second quotas, faster quota growth, packs cost 25% more, and valuable cards are harder to pull. Losing ends the run.</small></button>
        <button class="mode" id="btnSandbox"><b>🧪 Sandbox</b><small>Free packs and free upgrades forever. Still shows what every card is worth.</small></button>
      </div>
      <button class="ghost" id="btnContinue" hidden>▶ Continue run</button>
      <button class="ghost" id="btnBinderHome">📚 Binder</button>
      <button class="ghost" id="btnBattleHome">⚔️ Battles</button>
      <button class="ghost" id="btnAchievementsHome">🏆 Achievements</button>
      <button class="ghost" id="btnMuseumHome">🏛️ Museum</button>
      <button class="ghost" id="btnAlbumsHome">🗂️ Set Albums</button>
      <button class="ghost" id="btnAuctionHome">🔨 Auction House</button>
      <button class="ghost music-toggle">🔇 Music: Off</button>
      <button class="ghost track-toggle">🎼 Track: Electronic</button>
      <p class="note">Prices: TCGplayer market (USD), updated <span id="priceDate"></span>.</p>
    </section>

    <section id="game" class="screen">
      <div class="hud" id="hud">
        <div><div class="bank" id="bank"></div><small id="hudSub"></small></div>
        <div class="r"><button class="ghost" id="btnMissions" style="margin:0;padding:10px 12px">🎯 Missions</button><button class="ghost" id="btnRelics" style="margin:0;padding:10px 12px">🧿 Relics</button><button class="ghost" id="btnShop" style="margin:0;padding:10px 12px">🛒 Upgrades</button><small id="hudUp"></small></div>
      </div>
      <div class="main-tools" aria-label="Music and collection controls">
        <button class="ghost music-toggle">🔇 MUSIC: OFF</button>
        <button class="ghost track-toggle">🎼 ELECTRONIC</button>
        <button class="ghost" id="btnAchievements">🏆 ACHIEVEMENTS</button>
        <button class="ghost" id="btnMuseum">🏛️ MUSEUM</button>
      </div>
      <div class="quota" id="quotaBox" hidden>
        <div class="quota-top"><span id="quotaLabel"></span><span class="quota-time" id="quotaTime"></span></div>
        <div class="quota-track"><div class="quota-fill" id="quotaFill"></div></div>
        <small id="quotaProgress"></small>
      </div>
      <h2 id="title">🔥 PACK OPENED!</h2>
      <div class="summary" id="summary"></div>
      <div class="cards" id="cards"></div>
      <div class="actions">
        <button class="primary" id="btnOpen">OPEN PACK</button>
        <button class="ghost" id="btnMysteryShop">🎲 MYSTERY PACK SHOP</button>
        <button class="ghost" id="btnPokemonShow" hidden>🎪 VISIT POKÉMON SHOW</button>
        <button class="ghost" id="btnKiss">💋 KISS THE PACK</button>
        <button class="ghost" id="btnShake">🫨 SHAKE THE PACK</button>
        <button class="ghost" id="btnBox">BUY 6-PACK BOX</button>
        <button class="ghost" id="btnBinder">📚 BINDER</button>
        <button class="ghost" id="btnBattle">⚔️ BATTLES</button>
        <button class="ghost" id="btnAlbums">🗂️ SET ALBUMS</button>
        <button class="ghost" id="btnAuction">🔨 AUCTIONS</button>
        <button class="ghost" id="btnSwitchStore">🏪 SWITCH STORE</button>
        <button class="ghost" id="btnSwitchSet">SWITCH SET</button>
        <button class="ghost" id="btnHome">HOME</button>
      </div>
    </section>

    <section id="over" class="screen">
      <h1 id="overTitle">💀 BUSTED</h1>
      <p class="sub">You can't afford another pack.</p>
      <div class="stats" id="overStats"></div>
      <div id="overBest"></div>
      <button class="primary" id="btnRestart">NEW RUN</button>
      <button class="ghost" id="btnOverHome">HOME</button>
    </section>
  </div>

  <div class="overlay" id="shop">
    <div class="sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🛒 Upgrades</h2><button class="ghost" id="btnShopClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" style="font-size:13px">Bankroll: <b id="shopBank"></b></p>
      <div id="shopList"></div>
      <p class="note">Upgrades last for the whole run. Pick a strategy: chase the big hits, or farm bulk.</p>
    </div>
  </div>

  <div class="overlay" id="mysteryShop">
    <div class="sheet" style="width:min(900px,100%)">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🎲 Mystery Pack Shop</h2><button class="ghost" id="btnMysteryClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" style="font-size:13px">Bankroll: <b id="mysteryBank"></b> • Set revealed after the pack opens. Your chosen store's perks and fake risk still apply.</p>
      <div class="mystery-grid" id="randomPackList"></div>
      <div class="mystery-item"><img src="mystery-box.webp" alt="Sealed six-pack mystery box"><div class="body"><b>🎁 Six-Pack Mystery Box</b><small>One hidden set, six packs, each with 3× chase luck. Chaos Rising 50% · Sword &amp; Shield 25% · Destined Rivals 15% · Phantasmal Flames 8% · 151 2%. The set is saved when bought and revealed when you choose.</small><button id="btnMysteryBox">BUY MYSTERY BOX</button><button class="ghost" id="btnRevealMystery" hidden>REVEAL SEALED BOX</button></div></div>
      <p class="sub" id="mysteryStatus" style="font-size:13px"></p>
    </div>
  </div>

  <div class="overlay" id="relicShop">
    <div class="sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🧿 Relic Shop</h2><button class="ghost" id="btnRelicsClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" style="font-size:13px">Bankroll: <b id="relicBank"></b> • Equipped: <b id="relicCount">0/3</b> • New offers in <b id="relicRefresh">0:30</b></p>
      <div id="equippedRelics"></div>
      <div class="summary" style="max-width:none"><b>✨ Relic Fusion</b><br><small>Select two equipped relics to destroy them and create one stronger fusion relic.</small><div id="fusionStatus" style="margin-top:6px">Select 2 relics</div><button id="btnFuseRelics" disabled>FUSE SELECTED RELICS</button></div>
      <h3>Current offers</h3>
      <div id="relicList"></div>
      <p class="note">You can equip only three relics. Destroying a relic permanently removes it and gives no refund.</p>
    </div>
  </div>

  <div class="overlay" id="setSwitch">
    <div class="sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🎴 Switch set</h2><button class="ghost" id="btnSetClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" style="font-size:13px">Your bankroll, upgrades, stats, and save stay the same.</p>
      <div class="set-picker" id="gameSetPicker"></div>
    </div>
  </div>

  <div class="overlay" id="storeSwitch">
    <div class="sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🏪 Choose a pack store</h2><button class="ghost" id="btnStoreClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" style="font-size:13px">Cheaper stores carry a risk of fake packs. Cards from fake packs are worth $0.</p>
      <div class="store-picker" id="gameStorePicker"></div>
    </div>
  </div>

  <div class="overlay" id="missions">
    <div class="sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🎯 Run Missions</h2><button class="ghost" id="btnMissionsClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" style="font-size:13px">Finish goals during this run. Cash rewards are collected automatically.</p>
      <div id="missionList"></div>
    </div>
  </div>

  <div class="overlay" id="binder">
    <div class="sheet binder-sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">📚 Card Binder <small id="binderCount"></small></h2><button class="ghost" id="btnBinderClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" style="font-size:13px">Keep up to eight cards. Tap a card to inspect it, or choose three cards for your battle deck.</p>
      <div class="summary" style="max-width:none">⚔️ Battle deck: <b id="binderDeckCount">0/3</b> selected <button class="ghost" id="btnBattleFromBinder" style="padding:8px 12px;font-size:12px">OPEN BATTLES</button></div>
      <div class="binder-cards" id="binderList"></div>
    </div>
  </div>

  <div class="overlay" id="cardZoom">
    <div style="position:relative;padding:12px"><img class="zoom-card" id="zoomImage" alt="Enlarged card"><button class="ghost" id="btnZoomClose" style="position:absolute;right:14px;top:14px;padding:8px 13px">✕</button></div>
  </div>

  <div class="overlay" id="cardTrade">
    <div class="sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🔄 Card Trade</h2><button class="ghost" id="btnTradeClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" id="tradePrompt" style="font-size:13px">The offered card’s normal value is within 50% below or above yours. Prices are hidden. There is a secret 10% chance that the offered card is fake.</p>
      <div class="trade-grid" id="tradeComparison"></div>
      <div id="tradeResult"></div>
      <div id="tradeActions" style="text-align:center"><button class="primary" id="btnAcceptTrade">ACCEPT TRADE</button><button class="ghost" id="btnDeclineTrade">DECLINE</button></div>
      <div id="tradeContinue" style="text-align:center" hidden><button class="primary" id="btnTradeContinue">CONTINUE</button></div>
    </div>
  </div>

  <div class="overlay" id="achievements">
    <div class="sheet binder-sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🏆 Achievements</h2><button class="ghost" id="btnAchievementsClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" id="achievementSummary"></p><div id="achievementList"></div>
    </div>
  </div>

  <div class="overlay" id="museum">
    <div class="sheet binder-sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🏛️ Collection Museum</h2><button class="ghost" id="btnMuseumClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub">Your permanent collection survives new runs.</p><div id="museumContent"></div>
    </div>
  </div>

  <div class="overlay" id="setAlbums">
    <div class="sheet binder-sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🗂️ Set Albums</h2><button class="ghost" id="btnAlbumsClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub">Discover cards from real packs to complete sets. Each completed album gives one cash prize and a permanent +2% card-value bonus.</p><div id="albumList"></div>
    </div>
  </div>

  <div class="overlay" id="auctionHouse">
    <div class="sheet binder-sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🔨 Auction House</h2><button class="ghost" id="btnAuctionClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub">Choose one Binder card. Five AI collectors make offers one at a time. Accept an offer or risk waiting; the fifth and usually worst offer is mandatory.</p><div id="auctionStatus" class="summary" style="max-width:none"></div><div id="auctionLots"></div>
    </div>
  </div>

  <div class="overlay" id="battle">
    <div class="sheet battle-sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">⚔️ Binder Battles</h2><button class="ghost" id="btnBattleClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" style="font-size:13px">Choose exactly three Binder cards. During battle, tap any Pokémon that still has HP to make it attack. The trainer strikes back after every move. Knocked-out cards always stay in your Binder.</p>
      <div id="battleStatus" class="summary" style="max-width:none"></div>
      <h3>Your deck <small id="battleDeckCount"></small></h3>
      <div class="battle-grid" id="battleCards"></div>
      <h3>Single battle</h3>
      <p class="sub" style="font-size:12px">One random trainer. Single battles are always free; win once and collect cash.</p>
      <div class="battle-modes" id="singleBattles"></div>
      <h3>Tournament</h3>
      <p class="sub" style="font-size:12px">Pay a small entry fee for a best-of-five tournament. Higher difficulties cost a little more and award much larger prizes.</p>
      <div class="battle-modes" id="tournamentBattles"></div>
      <div id="battleResult"></div>
    </div>
  </div>

  <script>
    // p = normal, pr = reverse holo, ph = holofoil. Recent 30th, ME03, ME02.5, and ME01 values are in-game estimates; other sets use imported market data.
    const SET_DATA = __DATA__;
    const SET_META = {
      '30th': { name: '30th Celebration', series: 'Mega Evolution', code: '30C', official: 128, art: 'https://cdn.shopify.com/s/files/1/0865/2816/4189/files/Pokemon_TCG_30th_Celebration_Booster_Pack-English_480x480.webp?v=1780494124', price: 18, valueMult: 1.2, estimated: true },
      me04: { name: 'Chaos Rising', series: 'Mega Evolution', code: 'ME04', official: 86, art: 'chaos-rising-pack.png', price: 9.99, valueMult: 1.2 },
      me05: { name: 'Pitch Black', series: 'Mega Evolution', code: 'ME05', official: 84, art: 'pack.jpg', price: 4.99, valueMult: 1 },
      me03: { name: 'Perfect Order', series: 'Mega Evolution', code: 'ME03', official: 88, art: 'https://www.tcgreus.nl/cdn/shop/files/Pokemon_TCG_-_Perfect_Order_Booster_Pack_Zygarde_ex.png?v=1769676500', price: 8.99, valueMult: 1.2, estimated: true },
      'me02.5': { name: 'Ascended Heroes', series: 'Mega Evolution', code: 'ASC', official: 217, art: 'https://vendingwholesale.com/cdn/shop/files/pokemon-tcg-mega-evolution-ascended-heroes-booster-pack-dragonite-charizard-10-cards.jpg?v=1780067940&width=533', price: 22, valueMult: 1.65, estimated: true },
      me01: { name: 'Mega Evolution', series: 'Mega Evolution', code: 'ME01', official: 132, art: 'https://rhydonmycards.com.au/cdn/shop/files/asdasdasdasdaszxczxc.png?v=1769515939&width=533', price: 8.5, valueMult: 1.2, estimated: true },
      swsh1: { name: 'Sword & Shield', series: 'Sword & Shield', code: 'SWSH1', official: 202, art: 'sword-shield-pack.jpg', price: 12, valueMult: 1.35 },
      sv10: { name: 'Destined Rivals', series: 'Scarlet & Violet', code: 'SV10', official: 182, art: 'destined-rivals-pack.jpg', price: 15, valueMult: 1.3 },
      me02: { name: 'Phantasmal Flames', series: 'Mega Evolution', code: 'ME02', official: 94, art: 'phantasmal-flames-pack.png', price: 22.5, valueMult: 1.6 },
      'sv03.5': { name: '151', series: 'Scarlet & Violet', code: 'SV03.5', official: 165, art: 'pokemon-151-pack.png', price: 35, valueMult: 2 },
      sm1: { name: 'Sun & Moon', series: 'Sun & Moon', code: 'SM1', official: 149, art: 'sun-moon-pack.png', price: 50, valueMult: 1.25 },
      'sm7.5': { name: 'Dragon Majesty', series: 'Sun & Moon', code: 'SM7.5', official: 70, art: 'dragon-majesty-pack.jpg', price: 100, valueMult: 2.4 },
      base1: { name: 'Base Set First Edition', series: '1999 Original', code: 'BASE1', official: 102, art: 'first-edition-pack.jpg', price: 10000, valueMult: 3 },
    };
    const STORES = {
      pokemon: { name: 'Pokémon Store', icon: '✨', priceMult: 1.10, fakeChance: 0, luckMult: 2, psaRerolls: 1, desc: '10% more expensive • 2× luck • better PSA grades • always real' },
      walmart: { name: 'Walmart', icon: '🏪', priceMult: 1, fakeChance: 0, luckMult: 1, psaRerolls: 0, desc: 'Normal price • normal luck • always real' },
      collector: { name: 'Collector’s Club', icon: '🎟️', priceMult: 1.05, fakeChance: 0, luckMult: 1.4, psaRerolls: 0, desc: '5% more expensive • 1.4× chase luck • always real' },
      temu: { name: 'Temu', icon: '📦', priceMult: .90, fakeChance: .10, luckMult: 1, psaRerolls: 0, desc: '10% cheaper • 10% chance of a fake pack' },
      black: { name: 'Black Market', icon: '🕶️', priceMult: .70, fakeChance: .30, luckMult: 1, psaRerolls: 0, desc: '30% cheaper • 30% chance of a fake pack' },
      show: { name: 'Pokémon Show', icon: '🎪', priceMult: 2.5, fakeChance: 0, luckMult: 5, psaRerolls: 2, desc: '2.5× price • 5× chase luck • two PSA rerolls • always real' },
    };
    const RANDOM_PACKS = {
      poor: { name: 'Scrappy', price: 25, luck: 1.4, fake: .05, art: 'random-scrappy.webp', sets: ['me05', 'me04', 'swsh1'] },
      okay: { name: 'Solid', price: 65, luck: 2.2, fake: .02, art: 'random-solid.webp', sets: ['me04', 'me01', 'swsh1', 'sv10', 'me02'] },
      good: { name: 'Premium', price: 150, luck: 4, fake: 0, art: 'random-premium.webp', sets: ['sv10', 'me02', 'me02.5', 'sv03.5', 'sm1', 'me03', '30th'] },
      elite: { name: 'Elite', price: 400, luck: 7, fake: 0, extraHit: .25, art: 'random-elite.webp', sets: ['sv03.5', 'sm1', 'sm7.5', '30th'] },
    };
    const PRICE_DATE = '__DATE__';

    const START_BANK = 60;
    const QUOTA_START = 50;
    const QUOTA_MULT = 1.5;
    const QUOTA_SECONDS = 60;
    const HARD_QUOTA_START = 75;
    const HARD_QUOTA_MULT = 1.75;
    const HARD_QUOTA_SECONDS = 30;
    const HARD_PACK_MULT = 1.25;
    const HARD_CHASE_MULT = 0.5;
    const DOUBLE_HIT_CHANCE = .10;
    const KISS_LUCK_MULT = 2;
    const KISS_COOLDOWN_SECONDS = 30;
    const BOX_PACKS = 6;
    // The cheapest possible result is Chaos Rising. More expensive sets are rarer.
    const MYSTERY_SETS = [
      { id: 'me04', weight: 50 }, { id: 'swsh1', weight: 25 },
      { id: 'sv10', weight: 15 }, { id: 'me02', weight: 8 }, { id: 'sv03.5', weight: 2 },
    ];
    const SAVE_KEY = 'poke-tear-run-v2';
    const QUOTA_RECORD_KEY = 'poke-tear-quota-record-v1';
    const BINDER_KEY = 'poke-tear-binder-v1';
    const BATTLE_DECK_KEY = 'poke-tear-battle-deck-v1';
    const BATTLE_COOLDOWN_KEY = 'poke-tear-battle-cooldowns-v1';
    const PROFILE_KEY = 'poke-tear-collection-profile-v1';
    const SINGLE_BATTLE_COOLDOWN_MS = 10 * 1000;
    const TOURNAMENT_COOLDOWN_MS = 30 * 1000;
    const BRIBE_BASE_COST = 300;
    const BINDER_GROW_MS = 60 * 1000;
    const BINDER_CAPACITY_LEVELS = [8, 11, 14, 17, 20];
    const BINDER_GROWTH_LEVELS = [1.2, 1.3, 1.4, 1.5];

    // More cards lose value than gain it: 55% below PSA 5, 12% PSA 5, 33% above PSA 5.
    const GRADES = [
      { grade: 10, chance: 2,  mult: 10 },
      { grade: 9,  chance: 5,  mult: 7 },
      { grade: 8,  chance: 7,  mult: 4 },
      { grade: 7,  chance: 9,  mult: 2 },
      { grade: 6,  chance: 10, mult: 1.25 },
      { grade: 5,  chance: 12, mult: 1 },
      { grade: 4,  chance: 14, mult: .75 },
      { grade: 3,  chance: 15, mult: .5 },
      { grade: 2,  chance: 14, mult: .25 },
      { grade: 1,  chance: 12, mult: 0 },
    ];

    // rank: 0 common · 1 uncommon · 2 rare/double rare · 3 ultra/illustration · 4 special illustration/hyper
    const RANK = r => { r = r.toLowerCase(); if (r === 'common') return 0; if (r === 'uncommon') return 1; if (r.includes('holo rare') || r.includes('special') || r.includes('secret') || r.includes('hyper') || r.includes('futuristic') || r.includes('rgb') || r.includes('mega attack')) return 4; if (r.includes('ultra') || r.includes('illustration') || r.includes('pikachu rare')) return 3; return 2; };
    let selectedSet = 'me05';
    let selectedStore = 'walmart';
    let SET = [];
    let BY = {};

    // Hit-slot base weights (roughly real pull rates). Luck multiplies the chase tiers.
    const HIT_W = { 'Rare': 55, 'Holo Rare': .8, 'Double rare': 22, 'Illustration rare': 10, 'Ultra Rare': 5, 'Secret Rare': 1, 'Special illustration rare': 2, 'Mega Hyper Rare': 0.4, 'Mega Attack Rare': .8, 'Hyper rare': 0.4, 'Futuristic Rare': .2, 'RGB Rare': .3 };
    const CHASE = new Set(['Holo Rare', 'Illustration rare', 'Ultra Rare', 'Secret Rare', 'Special illustration rare', 'Mega Hyper Rare', 'Mega Attack Rare', 'Hyper rare', 'Futuristic Rare', 'RGB Rare', 'Pikachu Rare']);

    const UPGRADES = [
      { k: 'luck',  ico: '🍀', name: 'Lucky Charm', desc: 'Boosts the odds of the hit slot being an Illustration / Ultra / Special / Hyper rare.', tiers: [15, 40, 100], fx: ['1.6×', '2.6×', '4.5×'], mult: [1, 1.6, 2.6, 4.5] },
      { k: 'bulk',  ico: '📦', name: 'Bulk Baron', desc: 'Commons, uncommons, rares and double rares sell for a modest multiple of market price.', tiers: [12, 30, 75], fx: ['1.25×', '1.5×', '2×'], mult: [1, 1.25, 1.5, 2] },
      { k: 'rev',   ico: '✨', name: 'Reverse Radar', desc: 'Every pack gets a third reverse-holo slot (11 cards per pack).', tiers: [20], fx: ['+1 slot'], mult: [0, 1] },
      { k: 'whole', ico: '🏷️', name: 'Wholesale', desc: 'Packs cost less.', tiers: [25, 60], fx: ['-10%', '-20%'], mult: [1, 0.9, 0.8] },
      { k: 'mint',  ico: '🧤', name: 'Mint Condition Kit', desc: 'Careful handling raises every PSA result, up to PSA 10.', tiers: [35, 90], fx: ['+1 PSA grade', '+2 PSA grades'], mult: [0, 1, 2] },
      { k: 'shine', ico: '🌟', name: 'Holo Amplifier', desc: 'Reverse-holo and hit cards sell for more.', tiers: [30, 80], fx: ['1.25× value', '1.6× value'], mult: [1, 1.25, 1.6] },
      { k: 'bonus', ico: '🎁', name: 'Bonus Hit', desc: 'Adds to the natural 10% chance for a second hit card.', tiers: [50, 140], fx: ['25% total chance', '40% total chance'], mult: [0, .15, .3] },
      { k: 'clock', ico: '⏱️', name: 'Time Bank', desc: 'Adds more time to every quota, including the current one.', tiers: [25, 70], fx: ['+5 seconds', '+10 seconds'], mult: [0, 5, 10] },
      { k: 'cover', ico: '🛡️', name: 'PSA Insurance', desc: 'PSA 2–4 cards keep a minimum percentage of their ungraded value. PSA 1 is still worth one cent.', tiers: [30, 85], fx: ['50% minimum', '75% minimum'], mult: [0, .5, .75] },
      { k: 'jackpot', ico: '💰', name: 'Big Hit Bonus', desc: 'Cards worth at least $20 receive an extra value multiplier.', tiers: [45, 120], fx: ['1.25× value', '1.5× value'], mult: [1, 1.25, 1.5] },
      { k: 'boxdeal', ico: '📦', name: 'Box Boss', desc: 'Increases the discount on every six-pack box.', tiers: [60, 150], fx: ['15% box discount', '20% box discount'], mult: [.10, .15, .20] },
      { k: 'recheck', ico: '🔍', name: 'PSA Recheck', desc: 'Rolls multiple PSA grades and automatically keeps the highest result.', tiers: [70, 180], fx: ['best of 2', 'best of 3'], mult: [1, 2, 3] },
      { k: 'extras', ico: '🃏', name: 'Pack Stretcher', desc: 'Adds extra common or uncommon cards to every opened pack.', tiers: [40, 110], fx: ['+1 card', '+2 cards'], mult: [0, 1, 2] },
      { k: 'shakepower', ico: '🫨', name: 'Shake Power', desc: 'Makes Shake the Pack give an even larger chase-card luck boost.', tiers: [90, 240], fx: ['7× shake luck', '10× shake luck'], mult: [5, 7, 10] },
      { k: 'shakecool', ico: '⏳', name: 'Fast Hands', desc: 'Reduces the cooldown before Shake the Pack can be used again.', tiers: [65, 170], fx: ['45s cooldown', '30s cooldown'], mult: [60, 45, 30] },
      { k: 'binderspace', ico: '📚', name: 'Bigger Binder', desc: 'Increases the maximum number of cards your Binder can hold.', tiers: [50, 150, 400, 1000], fx: ['11 cards', '14 cards', '17 cards', '20 cards'], mult: BINDER_CAPACITY_LEVELS },
      { k: 'bindergrowth', ico: '📈', name: 'Collector Interest', desc: 'Raises the hidden value bonus that Binder cards receive after one minute.', tiers: [75, 250, 750], fx: ['30% bonus', '40% bonus', '50% bonus'], mult: BINDER_GROWTH_LEVELS },
      { k: 'battlearmor', ico: '🛡️', name: 'Battle Armor', desc: 'Gives every Pokémon in your battle deck more maximum HP.', tiers: [200, 700, 2000], fx: ['+10% HP', '+20% HP', '+35% HP'], mult: [1, 1.1, 1.2, 1.35] },
      { k: 'battlepower', ico: '💥', name: 'Power Training', desc: 'Increases the maximum damage dealt by every Pokémon in your battle deck.', tiers: [250, 850, 2400], fx: ['+10% damage', '+20% damage', '+35% damage'], mult: [1, 1.1, 1.2, 1.35] },
      { k: 'traincoach', ico: '🏋️', name: 'Training Coach', desc: 'Reduces the cash price of every permanent Pokémon training level.', tiers: [120, 400, 1100], fx: ['15% cheaper', '30% cheaper', '50% cheaper'], mult: [1, .85, .7, .5] },
      { k: 'bribedeal', ico: '🤝', name: 'Shady Deal', desc: 'Reduces the cost of the once-per-match Bribe ability.', tiers: [175, 650], fx: ['$225 Bribe', '$150 Bribe'], mult: [1, .75, .5] },
      { k: 'battleprize', ico: '🏆', name: 'Prize Booster', desc: 'Increases cash rewards from single battles and tournaments.', tiers: [500, 2000, 6000], fx: ['+10% rewards', '+25% rewards', '+50% rewards'], mult: [1, 1.1, 1.25, 1.5] },
      { k: 'auctionfloor', ico: '📣', name: 'Auction Hype', desc: 'Raises the lowest offer the first four AI auction buyers can make. The maximum stays at 175% of card value.', tiers: [125, 400, 1200], fx: ['65% minimum', '80% minimum', '100% minimum'], mult: [.5, .65, .8, 1] },
      { k: 'finaloffer', ico: '🧾', name: 'Final Offer Insurance', desc: 'Raises the minimum price of the mandatory fifth auction offer.', tiers: [175, 550], fx: ['65% minimum', '80% minimum'], mult: [.5, .65, .8] },
      { k: 'kisscool', ico: '💄', name: 'Quick Kiss', desc: 'Reduces the cooldown for Kiss the Pack.', tiers: [80, 250, 700], fx: ['25s cooldown', '20s cooldown', '15s cooldown'], mult: [30, 25, 20, 15] },
      { k: 'baseboost', ico: '🧺', name: 'Bulk Binder', desc: 'Raises the sale value of common and uncommon cards in regular pack slots.', tiers: [35, 100], fx: ['1.15× base value', '1.3× base value'], mult: [1, 1.15, 1.3] },
      { k: 'rareboost', ico: '💎', name: 'Rare Resale', desc: 'Raises the value of rare and double-rare hit cards.', tiers: [75, 220], fx: ['1.2× rare hits', '1.4× rare hits'], mult: [1, 1.2, 1.4] },
      { k: 'marketboost', ico: '📊', name: 'Market Mentor', desc: 'Raises the value of every real card in newly opened packs.', tiers: [250, 750, 1800], fx: ['+5% value', '+10% value', '+15% value'], mult: [1, 1.05, 1.10, 1.15] },
    ];
    const RELIC_REFRESH_MS = 30 * 1000;
    const RELIC_RARITIES = {
      common: { name: 'COMMON', color: '#cbd5e1', weight: 50 },
      rare: { name: 'RARE', color: '#60a5fa', weight: 20 },
      legendary: { name: 'LEGENDARY', color: '#facc15', weight: 10 },
      cursed: { name: 'CURSED', color: '#c084fc', weight: 20 },
      fused: { name: 'FUSED', color: '#67e8f9', weight: 0 },
    };
    const RELICS = [
      { k: 'coupon', ico: '🎟️', name: 'Coupon Book', rarity: 'common', cost: 80, desc: 'Makes every single pack 5% cheaper.' },
      { k: 'boxcutter', ico: '✂️', name: 'Lucky Box Cutter', rarity: 'common', cost: 85, desc: 'Adds another 5% discount to six-pack boxes.' },
      { k: 'binderclock', ico: '🕰️', name: 'Collector Clock', rarity: 'common', cost: 90, desc: 'Binder growth bonuses become 10% stronger.' },
      { k: 'quotawatch', ico: '⌚', name: 'Quota Watch', rarity: 'common', cost: 75, desc: 'Adds five seconds to every quota.' },
      { k: 'luckycoin', ico: '🪙', name: 'Lucky Coin', rarity: 'rare', cost: 100, desc: 'Raises chase-card luck by 50%.' },
      { k: 'prism', ico: '🔮', name: 'Holo Prism', rarity: 'rare', cost: 110, desc: 'Reverse and hit cards are worth 25% more.' },
      { k: 'sleeve', ico: '🟨', name: 'Golden Sleeve', rarity: 'legendary', cost: 120, desc: 'All real cards are worth 20% more.' },
      { k: 'loupe', ico: '🔎', name: 'Master Grading Loupe', rarity: 'legendary', cost: 120, desc: 'PSA grading rolls two extra results and keeps the best.' },
      { k: 'crown', ico: '👑', name: 'Counterfeit Crown', rarity: 'cursed', cost: 70, desc: 'Real cards are worth 35% more, but fake-pack risk rises by 15 percentage points.' },
      { k: 'idol', ico: '🗿', name: 'Greedy Idol', rarity: 'cursed', cost: 70, desc: 'Battle rewards are 50% larger, but every pack costs 15% more.' },
      { k: 'cursedclover', ico: '☘️', name: 'Cursed Clover', rarity: 'cursed', cost: 75, desc: 'Doubles chase-card luck, but every real card is worth 20% less.' },
      { k: 'smugglermap', ico: '🗺️', name: 'Smuggler’s Map', rarity: 'cursed', cost: 65, desc: 'Makes packs 20% cheaper, but fake-pack risk rises by 20 percentage points.' },
      { k: 'darkmirror', ico: '🪞', name: 'Dark Mirror', rarity: 'cursed', cost: 80, desc: 'Hit cards are worth 75% more, but every non-hit card is worth 40% less.' },
      { k: 'warchain', ico: '⛓️', name: 'War Chain', rarity: 'cursed', cost: 80, desc: 'Battle rewards are 75% larger, but enemy Pokémon gain 25% HP and damage.' },
      { k: 'starcore', ico: '🌠', name: 'Collector’s Star', rarity: 'fused', fusionOnly: true, desc: 'Raises chase-card luck by 35% and all real-card values by 20%.' },
      { k: 'merchantseal', ico: '🪬', name: 'Merchant’s Seal', rarity: 'fused', fusionOnly: true, desc: 'Makes packs 12% cheaper and adds 8% to every box discount.' },
      { k: 'guardianeye', ico: '👁️', name: 'Guardian Eye', rarity: 'fused', fusionOnly: true, desc: 'Reduces fake-pack risk by 10 percentage points and adds one PSA reroll.' },
      { k: 'arenacrown', ico: '🏆', name: 'Arena Crown', rarity: 'fused', fusionOnly: true, desc: 'Raises battle rewards by 35% and your battle Pokémon’s HP and damage by 15%.' },
    ];
    const RANDOM_EVENTS = [
      { k: 'sale', ico: '🏷️', name: 'Flash Sale', desc: 'The next single pack costs 25% less.' },
      { k: 'boom', ico: '📈', name: 'Market Boom', desc: 'Cards in the next pack are worth 50% more.' },
      { k: 'crash', ico: '📉', name: 'Market Crash', desc: 'Cards in the next pack are worth 40% less.' },
      { k: 'restock', ico: '🍀', name: 'Lucky Restock', desc: 'The next pack gets 2× chase-card luck.' },
      { k: 'counterfeit', ico: '🚨', name: 'Counterfeit Wave', desc: 'The next pack has 20 percentage points more fake risk.' },
      { k: 'show', ico: '🎪', name: 'Pokémon Show', desc: 'A pop-up store is here! Its next pack costs 2.5× as much, but has 5× chase luck, two PSA rerolls, and no fake risk. Tap VISIT POKÉMON SHOW.' },
    ];
    const RANDOM_EVENT_CHANCE = .25;
    const SET_REWARDS = { '30th': 2400, me05: 500, me04: 750, me03: 900, 'me02.5': 2100, me01: 900, swsh1: 1800, sv10: 1000, me02: 1500, 'sv03.5': 2500, sm1: 3500, 'sm7.5': 5000, base1: 25000 };
    const AUCTION_BUYERS = [
      { name: 'Mia the Collector', ico: '🧢' }, { name: 'Dexter Deals', ico: '🤓' }, { name: 'Team Rocket Ron', ico: '🥷' }, { name: 'Professor Penny', ico: '🧑‍🔬' }, { name: 'Last-Chance Larry', ico: '😈' },
    ];
    const ACHIEVEMENTS = [
      { k: 'firstpack', ico: '🎴', name: 'First Rip', desc: 'Open your first pack.', test: p => p.stats.packs >= 1 },
      { k: 'pack50', ico: '📦', name: 'Pack Veteran', desc: 'Open 50 packs across all runs.', test: p => p.stats.packs >= 50 },
      { k: 'gemmint', ico: '💎', name: 'Gem Mint', desc: 'Grade a card PSA 10.', test: p => p.stats.psa10 >= 1 },
      { k: 'quota5', ico: '⏱️', name: 'Quota Climber', desc: 'Clear five quotas in one run.', test: p => p.stats.bestQuota >= 5 },
      { k: 'champion', ico: '⚔️', name: 'Battle Champion', desc: 'Win a tournament.', test: p => p.stats.tournamentWins >= 1 },
      { k: 'tradeup', ico: '🔄', name: 'Trade Up', desc: 'Accept a trade that gains card value.', test: p => p.stats.tradeWins >= 1 },
      { k: 'alchemist', ico: '✨', name: 'Relic Alchemist', desc: 'Fuse two relics.', test: p => p.stats.fusions >= 1 },
      { k: 'counterfeit', ico: '🚨', name: 'Counterfeit Victim', desc: 'Open a fake pack.', test: p => p.stats.fakePacks >= 1 },
      { k: 'collector100', ico: '🏛️', name: 'Master Collector', desc: 'Discover 100 different cards.', test: p => museumUniqueCards(p) >= 100 },
      { k: 'setmaster', ico: '👑', name: 'Set Master', desc: 'Complete every card in one set.', test: p => completedMuseumSets(p).length >= 1 },
    ];
    const MISSIONS = [
      { k: 'packs', ico: '🎴', name: 'Pack Rookie', desc: 'Open 3 packs in this run.', goal: 3, reward: 10 },
      { k: 'grades', ico: '🏅', name: 'PSA Apprentice', desc: 'Grade 2 cards in this run.', goal: 2, reward: 12 },
      { k: 'big', ico: '💎', name: 'Treasure Hunter', desc: 'Pull a card worth at least $20.', goal: 1, reward: 15 },
    ];

    let S = null; // run state
    let ACTIVE_TRADE = null;
    let FUSION_SELECTION = [];
    let quotaTimer = null;
    let binderTimer = null;
    let relicTimer = null;
    let kissTimer = null;
    let audioCtx = null, musicTimer = null, musicOn = false, musicStyle = 'electronic', musicStep = 0, nextMusicStep = 0, packAnimating = false;
    const $ = id => document.getElementById(id);
    const money = v => (v < 0 ? '-' : '') + '$' + Math.abs(v).toFixed(2);
    const rand = a => a[Math.floor(Math.random() * a.length)];
    const loadBinder = () => { try { return JSON.parse(localStorage.getItem(BINDER_KEY)) || []; } catch (e) { return []; } };
    const saveBinder = () => { try { localStorage.setItem(BINDER_KEY, JSON.stringify(BINDER)); } catch (e) {} };
    let BINDER = loadBinder();
    const loadBattleDeck = () => { try { return JSON.parse(localStorage.getItem(BATTLE_DECK_KEY)) || []; } catch (e) { return []; } };
    const saveBattleDeck = () => { try { localStorage.setItem(BATTLE_DECK_KEY, JSON.stringify(BATTLE_DECK)); } catch (e) {} };
    let BATTLE_DECK = loadBattleDeck();
    const loadBattleCooldowns = () => { try { return { single: 0, tournament: 0, ...(JSON.parse(localStorage.getItem(BATTLE_COOLDOWN_KEY)) || {}) }; } catch (e) { return { single: 0, tournament: 0 }; } };
    const saveBattleCooldowns = () => { try { localStorage.setItem(BATTLE_COOLDOWN_KEY, JSON.stringify(BATTLE_COOLDOWNS)); } catch (e) {} };
    let BATTLE_COOLDOWNS = loadBattleCooldowns(), battleCooldownTimer = null, ACTIVE_BATTLE = null, battleQuotaPausedAt = 0;
    const emptyProfile = () => ({ stats: { packs: 0, psa10: 0, bestQuota: 0, tournamentWins: 0, tradeWins: 0, fusions: 0, fakePacks: 0 }, achievements: {}, stars: 0, cards: [], psa10: [], relics: [], trophies: {}, setSeen: {}, setRewards: {} });
    const loadProfile = () => { try { const p = JSON.parse(localStorage.getItem(PROFILE_KEY)) || {}, base = emptyProfile(); return { ...base, ...p, stats: { ...base.stats, ...(p.stats || {}) }, achievements: { ...(p.achievements || {}) }, trophies: { ...(p.trophies || {}) }, setSeen: { ...(p.setSeen || {}) }, setRewards: { ...(p.setRewards || {}) }, cards: p.cards || [], psa10: p.psa10 || [], relics: p.relics || [] }; } catch (e) { return emptyProfile(); } };
    const saveProfile = () => { try { localStorage.setItem(PROFILE_KEY, JSON.stringify(PROFILE)); } catch (e) {} };
    let PROFILE = loadProfile();
    const BATTLE_LEVELS = {
      easy: { label: 'Easy', ico: '🌱', hp: [110, 190], dmg: [40, 75], single: 250, tournament: 1000, entry: 50, rank: [0, 1] },
      medium: { label: 'Normal', ico: '⚡', hp: [180, 280], dmg: [75, 125], single: 750, tournament: 5000, entry: 200, rank: [1, 2] },
      hard: { label: 'Hard', ico: '🔥', hp: [280, 410], dmg: [125, 190], single: 1500, tournament: 10000, entry: 500, rank: [2, 4] },
      impossible: { label: 'Impossible', ico: '☠️', hp: [450, 650], dmg: [220, 330], single: 3000, tournament: 20000, entry: 1000, rank: [3, 4] },
    };

    // Original procedural instrumental: 108 BPM drums, bass, and atmospheric synth pads.
    const MUSIC_BPM = 108;
    const MUSIC_STEP = 60 / MUSIC_BPM / 4;
    const MUSIC_CHORDS = [[220, 261.63, 329.63], [174.61, 220, 261.63], [261.63, 329.63, 392], [196, 246.94, 293.66]];
    const MUSIC_BASS = [110, 87.31, 130.81, 98];
    const MUSIC_MELODY = [[440, 523.25, 659.25, 523.25], [349.23, 440, 523.25, 440], [523.25, 659.25, 783.99, 659.25], [392, 493.88, 587.33, 493.88]];
    const PIXEL_BPM = 68;
    const PIXEL_STEP = 60 / PIXEL_BPM / 4;
    const PIXEL_CHORDS = [[146.83, 220, 293.66], [123.47, 185, 246.94], [164.81, 246.94, 329.63], [110, 164.81, 220]];
    const PIXEL_NOTES = [[293.66, 369.99, 440, 329.63], [246.94, 293.66, 369.99, 277.18], [329.63, 440, 493.88, 369.99], [220, 277.18, 329.63, 246.94]];
    function musicTone(freq, time, duration, type, volume, destination) {
      const osc = audioCtx.createOscillator(), gain = audioCtx.createGain();
      osc.type = type; osc.frequency.setValueAtTime(freq, time);
      gain.gain.setValueAtTime(0.0001, time);
      gain.gain.exponentialRampToValueAtTime(volume, time + .02);
      gain.gain.exponentialRampToValueAtTime(0.0001, time + duration);
      osc.connect(gain).connect(destination || audioCtx.destination);
      osc.start(time); osc.stop(time + duration + .03);
    }
    function musicKick(time) {
      const osc = audioCtx.createOscillator(), gain = audioCtx.createGain();
      osc.frequency.setValueAtTime(145, time); osc.frequency.exponentialRampToValueAtTime(45, time + .16);
      gain.gain.setValueAtTime(.22, time); gain.gain.exponentialRampToValueAtTime(.0001, time + .22);
      osc.connect(gain).connect(audioCtx.destination); osc.start(time); osc.stop(time + .23);
    }
    function musicNoise(time, volume, duration) {
      const size = Math.max(1, Math.floor(audioCtx.sampleRate * duration)), buffer = audioCtx.createBuffer(1, size, audioCtx.sampleRate), data = buffer.getChannelData(0);
      for (let i = 0; i < size; i++) data[i] = Math.random() * 2 - 1;
      const source = audioCtx.createBufferSource(), filter = audioCtx.createBiquadFilter(), gain = audioCtx.createGain();
      source.buffer = buffer; filter.type = 'highpass'; filter.frequency.value = 5000;
      gain.gain.setValueAtTime(volume, time); gain.gain.exponentialRampToValueAtTime(.0001, time + duration);
      source.connect(filter).connect(gain).connect(audioCtx.destination); source.start(time);
    }
    function scheduleMusicStep(time, step) {
      const beat = step % 16, bar = Math.floor(step / 16) % 4, secondPhrase = Math.floor(step / 64) % 2;
      if (beat % 4 === 0) musicKick(time);
      if (beat === 4 || beat === 12) musicNoise(time, .045, .12);
      if (beat % 2 === 0) musicNoise(time, .018, .035);
      if (secondPhrase && beat === 14) musicNoise(time, .026, .09);
      if (beat % 4 === 0) musicTone(MUSIC_BASS[bar], time, MUSIC_STEP * 2.7, 'sawtooth', .035);
      if (secondPhrase && beat === 8) musicTone(MUSIC_BASS[bar] * 2, time, MUSIC_STEP * 1.8, 'triangle', .016);
      if (beat === 0) MUSIC_CHORDS[bar].forEach((f, i) => musicTone(f, time + i * .015, MUSIC_STEP * 14, 'sine', .018));
      if (beat === 2 || beat === 6 || beat === 10 || beat === 14) {
        let note = MUSIC_MELODY[bar][(beat - 2) / 4];
        if (secondPhrase && beat === 14) note *= 1.125;
        musicTone(note, time, MUSIC_STEP * 1.5, 'triangle', .02);
      }
    }
    function schedulePixelStep(time, step) {
      const beat = step % 16, bar = Math.floor(step / 16) % 4, phrase = Math.floor(step / 64) % 2;
      if (beat === 0) PIXEL_CHORDS[bar].forEach((f, i) => musicTone(f, time + i * .04, PIXEL_STEP * 15, 'sine', .014));
      if (beat === 0 || beat === 4 || beat === 8 || beat === 12) {
        const note = PIXEL_NOTES[bar][beat / 4] * (phrase && beat === 12 ? 2 : 1);
        musicTone(note, time, PIXEL_STEP * 3.2, 'triangle', .026);
        musicTone(note * 2, time + .025, PIXEL_STEP * 2.2, 'sine', .008);
      }
      if (phrase && beat === 10) musicTone(PIXEL_NOTES[bar][2] * 1.5, time, PIXEL_STEP * 2.5, 'sine', .009);
    }
    function pumpMusic() {
      if (!musicOn || !audioCtx) return;
      while (nextMusicStep < audioCtx.currentTime + .2) {
        if (musicStyle === 'pixel') schedulePixelStep(nextMusicStep, musicStep++);
        else scheduleMusicStep(nextMusicStep, musicStep++);
        nextMusicStep += musicStyle === 'pixel' ? PIXEL_STEP : MUSIC_STEP;
      }
    }
    function updateMusicButtons() {
      document.querySelectorAll('.music-toggle').forEach(b => b.textContent = musicOn ? '🔊 MUSIC: ON' : '🔇 MUSIC: OFF');
      document.querySelectorAll('.track-toggle').forEach(b => b.textContent = musicStyle === 'pixel' ? '🎹 PIXEL CALM' : '🎼 ELECTRONIC');
    }
    function toggleTrack() {
      musicStyle = musicStyle === 'electronic' ? 'pixel' : 'electronic';
      musicStep = 0;
      if (audioCtx) nextMusicStep = audioCtx.currentTime + .25;
      updateMusicButtons();
    }
    async function toggleMusic() {
      if (musicOn) {
        musicOn = false; clearInterval(musicTimer);
        if (audioCtx) await audioCtx.close();
        audioCtx = null; updateMusicButtons(); return;
      }
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      await audioCtx.resume();
      musicOn = true; musicStep = 0; nextMusicStep = audioCtx.currentTime + .05;
      pumpMusic(); musicTimer = setInterval(pumpMusic, 50); updateMusicButtons();
    }

    const meta = () => SET_META[selectedSet];
    const store = (id = selectedStore) => STORES[id] || STORES.walmart;
    const paidMode = () => S && !S.ended && (S.mode === 'normal' || S.mode === 'hard' || S.mode === 'chill');
    const auctionMode = () => S && !S.ended;
    const quotaMode = () => S && (S.mode === 'normal' || S.mode === 'hard');
    const quotaStart = () => S.mode === 'hard' ? HARD_QUOTA_START : QUOTA_START;
    const quotaMult = () => S.mode === 'hard' ? HARD_QUOTA_MULT : QUOTA_MULT;
    const hasRelic = k => !!(S && Array.isArray(S.relics) && S.relics.includes(k));
    const quotaSeconds = () => (S.mode === 'hard' ? HARD_QUOTA_SECONDS : QUOTA_SECONDS) + UPGRADES[7].mult[S.up.clock] + (hasRelic('quotawatch') ? 5 : 0);
    const CARD_IMAGE_FIXES = { 'sv03.5-163': 'https://images.pokemontcg.io/sv3pt5/163_hires.png' };
    const cardUrl = c => { if (CARD_IMAGE_FIXES[c.id]) return CARD_IMAGE_FIXES[c.id]; if (/^https?:\/\//.test(c.img || '')) return c.img; const id = c.id.split('-')[0], series = id === '30th' ? 'me' : (id.match(/^[a-z]+/) || [''])[0]; return `https://assets.tcgdex.net/en/${series}/${id}/${c.img}/high.webp`; };
    function activateSet(id) {
      selectedSet = SET_DATA[id] ? id : 'me05';
      SET = SET_DATA[selectedSet]; BY = {};
      SET.forEach(c => (BY[c.r] = BY[c.r] || []).push(c));
      document.querySelectorAll('.set-choice').forEach(b => b.classList.toggle('on', b.dataset.set === selectedSet));
      $('setTitle').textContent = `${meta().series} — ${meta().name} • ${meta().code}`;
      $('packArt').src = meta().art; $('packArt').alt = `${meta().name} pack`;
    }

    function activateStore(id) {
      selectedStore = STORES[id] ? id : 'walmart';
      document.querySelectorAll('.store-choice').forEach(b => b.classList.toggle('on', b.dataset.store === selectedStore));
      if (S) { S.store = selectedStore; save(); hud(); }
    }

    function switchSet(id) {
      if (!S || !SET_DATA[id]) return;
      activateSet(id);
      S.set = selectedSet;
      S.last = null;
      save();
      $('cards').innerHTML = '';
      $('title').textContent = `🎴 ${meta().name}`;
      $('summary').innerHTML = `Now opening <b>${meta().name}</b>. Your bankroll, upgrades, and stats are unchanged.`;
      $('setSwitch').classList.remove('on');
      hud();
    }

    function newState(mode) {
      return { mode, set: selectedSet, store: selectedStore, bank: START_BANK, packs: 0, spent: 0, earned: 0, peak: START_BANK, best: null, up: Object.fromEntries(UPGRADES.map(u => [u.k, 0])), relics: [], relicOffers: [], relicRefreshAt: 0, event: null, cardAuction: null, auctionMessage: '', boxes: {}, boxStores: {}, mysteryBoxes: [], kissBoost: false, kissReadyAt: 0, shakeBoost: false, shakeReadyAt: 0, missions: { packs: 0, grades: 0, big: 0, claimed: {} }, last: null,
        quota: mode === 'normal' || mode === 'hard' ? { number: 1, cleared: 0, target: mode === 'hard' ? HARD_QUOTA_START : QUOTA_START, endsAt: Date.now() + (mode === 'hard' ? HARD_QUOTA_SECONDS : QUOTA_SECONDS) * 1000 } : null };
    }
    function save() { try { if (paidMode()) localStorage.setItem(SAVE_KEY, JSON.stringify(S)); } catch (e) {} }
    function load() { try { return JSON.parse(localStorage.getItem(SAVE_KEY)); } catch (e) { return null; } }
    function binderSellRun() {
      if (S && !S.ended) return S;
      const saved = load();
      return saved && !saved.ended && ['normal', 'hard', 'chill'].includes(saved.mode) ? saved : null;
    }
    function saveSpecificRun(run) { try { localStorage.setItem(SAVE_KEY, JSON.stringify(run)); } catch (e) {} }
    function clearSave() { try { localStorage.removeItem(SAVE_KEY); } catch (e) {} }
    function quotaRecord() { try { return +(localStorage.getItem(QUOTA_RECORD_KEY) || 0); } catch (e) { return 0; } }
    function saveQuotaRecord(n) { try { localStorage.setItem(QUOTA_RECORD_KEY, String(Math.max(n, quotaRecord()))); } catch (e) {} }

    const museumUniqueCards = p => Object.values(p.setSeen || {}).reduce((sum, ids) => sum + ids.length, 0);
    const completedMuseumSets = p => Object.entries(SET_DATA).filter(([setId, cards]) => ((p.setSeen || {})[setId] || []).length >= cards.length).map(([setId]) => setId);
    function checkAchievements() {
      let changed = false;
      ACHIEVEMENTS.forEach(a => { if (!PROFILE.achievements[a.k] && a.test(PROFILE)) { PROFILE.achievements[a.k] = Date.now(); PROFILE.stars++; changed = true; } });
      if (changed) saveProfile();
    }
    function recordMuseumCard(c, value, setId, grade = null) {
      if (!c || value <= 0) return;
      const exhibit = { id: c.id, n: c.n, r: c.r, img: c.img, v: +value.toFixed(2), set: setId, grade };
      const old = PROFILE.cards.findIndex(x => x.id === c.id);
      if (old < 0) PROFILE.cards.push(exhibit); else if (PROFILE.cards[old].v < exhibit.v) PROFILE.cards[old] = exhibit;
      PROFILE.cards.sort((a, b) => b.v - a.v); PROFILE.cards = PROFILE.cards.slice(0, 12);
      if (grade === 10) {
        const psaOld = PROFILE.psa10.findIndex(x => x.id === c.id);
        if (psaOld < 0) PROFILE.psa10.push(exhibit); else if (PROFILE.psa10[psaOld].v < exhibit.v) PROFILE.psa10[psaOld] = exhibit;
        PROFILE.psa10.sort((a, b) => b.v - a.v); PROFILE.psa10 = PROFILE.psa10.slice(0, 12);
      }
      saveProfile();
    }
    function recordPackMuseum(pull, setId, fake) {
      PROFILE.stats.packs++;
      if (fake) PROFILE.stats.fakePacks++;
      if (!fake) {
        const seen = new Set(PROFILE.setSeen[setId] || []);
        pull.forEach(p => { seen.add(p.c.id); recordMuseumCard(p.c, p.v, setId); });
        PROFILE.setSeen[setId] = [...seen];
      }
      saveProfile(); checkAchievements();
    }
    function recordPSA10(c, value, setId) { PROFILE.stats.psa10++; recordMuseumCard(c, value, setId, 10); saveProfile(); checkAchievements(); }
    function recordRelicDiscovery(k) { const r = RELICS.find(x => x.k === k); if (r && ['rare', 'legendary', 'cursed', 'fused'].includes(r.rarity) && !PROFILE.relics.includes(k)) { PROFILE.relics.push(k); saveProfile(); } }
    function showAchievements() {
      checkAchievements(); const unlocked = ACHIEVEMENTS.filter(a => PROFILE.achievements[a.k]).length;
      $('achievementSummary').innerHTML = `<b>${unlocked}/${ACHIEVEMENTS.length}</b> unlocked • ⭐ ${PROFILE.stars} Museum Stars`;
      $('achievementList').innerHTML = ACHIEVEMENTS.map(a => `<div class="up ${PROFILE.achievements[a.k] ? 'max' : ''}"><div class="ico">${PROFILE.achievements[a.k] ? a.ico : '🔒'}</div><div class="body"><b>${a.name}</b><small>${a.desc}</small><div class="tier">${PROFILE.achievements[a.k] ? 'UNLOCKED • +1 MUSEUM STAR' : 'LOCKED'}</div></div></div>`).join('');
      $('achievements').classList.add('on');
    }
    function museumCardHtml(x) { const c = Object.values(SET_DATA).flat().find(card => card.id === x.id) || x; return `<div class="card r${RANK(x.r)}"><span class="val ${x.v >= 5 ? 'big' : ''}">${money(x.v)}</span>${x.grade === 10 ? '<span class="tag">PSA 10</span>' : ''}<img src="${cardUrl(c)}" alt="${x.n}" loading="lazy"><div class="name">${x.n}</div><div class="rarity">${tradeSetName(x.set)}</div></div>`; }
    function showMuseum() {
      checkAchievements();
      const sets = Object.entries(SET_DATA).map(([id, cards]) => { const seen = (PROFILE.setSeen[id] || []).length, done = seen >= cards.length; return `<div class="up ${done ? 'max' : ''}"><div class="ico">${done ? '✅' : '🗂️'}</div><div class="body"><b>${SET_META[id].name}</b><small>${seen}/${cards.length} different cards discovered</small><div class="quota-track"><div class="quota-fill" style="width:${seen / cards.length * 100}%"></div></div></div></div>`; }).join('');
      const trophies = Object.entries(PROFILE.trophies).map(([k, n]) => `<span class="tag" style="position:static;display:inline-block;margin:4px">🏆 ${k.replace('-', ' ')} ×${n}</span>`).join('') || '<p class="sub">No battle trophies yet.</p>';
      const relics = PROFILE.relics.map(k => RELICS.find(r => r.k === k)).filter(Boolean).map(r => `<span class="tag" style="position:static;display:inline-block;margin:4px">${r.ico} ${r.name}</span>`).join('') || '<p class="sub">No rare relic discoveries yet.</p>';
      $('museumContent').innerHTML = `<div class="summary">⭐ ${PROFILE.stars} Museum Stars • ${museumUniqueCards(PROFILE)} unique cards • ${completedMuseumSets(PROFILE).length} completed sets</div><h3>Best Pulls</h3><div class="cards">${PROFILE.cards.length ? PROFILE.cards.map(museumCardHtml).join('') : '<p class="sub">Open real packs to create exhibits.</p>'}</div><h3>PSA 10 Gallery</h3><div class="cards">${PROFILE.psa10.length ? PROFILE.psa10.map(museumCardHtml).join('') : '<p class="sub">No PSA 10 cards yet.</p>'}</div><h3>Battle Trophies</h3>${trophies}<h3>Rare Relics Discovered</h3>${relics}<h3>Set Completion</h3>${sets}`;
      $('museum').classList.add('on');
    }
    function showSetAlbums() {
      const active = paidMode(), claimed = Object.values(PROFILE.setRewards).filter(Boolean).length;
      $('albumList').innerHTML = Object.entries(SET_DATA).map(([id, cards]) => {
        const seen = (PROFILE.setSeen[id] || []).length, complete = seen >= cards.length, rewarded = !!PROFILE.setRewards[id], reward = SET_REWARDS[id] || 1000;
        return `<div class="up ${rewarded ? 'max' : ''}"><div class="ico">${rewarded ? '🏆' : complete ? '🎁' : '🗂️'}</div><div class="body"><b>${SET_META[id].name}</b><small>${seen}/${cards.length} cards • reward ${money(reward)} + permanent 2% card value</small><div class="quota-track"><div class="quota-fill" style="width:${seen / cards.length * 100}%"></div></div><div class="tier">${rewarded ? 'REWARD CLAIMED' : complete ? active ? 'SET COMPLETE!' : 'START A MONEY RUN TO CLAIM' : `${cards.length - seen} cards remaining`}</div></div><button data-claim-set="${id}" ${!complete || rewarded || !active ? 'disabled' : ''}>${rewarded ? '✓' : 'CLAIM'}</button></div>`;
      }).join('') + `<div class="summary">Permanent album bonus: <b>+${claimed * 2}% real-card value</b></div>`;
      $('albumList').querySelectorAll('[data-claim-set]').forEach(b => b.onclick = () => claimSetReward(b.dataset.claimSet));
      $('setAlbums').classList.add('on');
    }
    function claimSetReward(setId) {
      if (!paidMode() || PROFILE.setRewards[setId] || (PROFILE.setSeen[setId] || []).length < SET_DATA[setId].length) return;
      const reward = SET_REWARDS[setId] || 1000;
      PROFILE.setRewards[setId] = true; S.bank = +(S.bank + reward).toFixed(2); S.earned = +(S.earned + reward).toFixed(2); S.peak = Math.max(S.peak, S.bank);
      saveProfile(); save(); hud(); showSetAlbums();
    }
    function startCardAuction(uid) {
      if (!auctionMode() || S.cardAuction) return;
      const item = BINDER.find(x => x.uid === uid); if (!item) return;
      const value = binderValue(item);
      const offerFloor = upgradeMultiplier('auctionfloor'), finalFloor = upgradeMultiplier('finaloffer');
      const offers = AUCTION_BUYERS.map((buyer, i) => {
        const mult = i === 4
          ? (Math.random() < .75 ? finalFloor + Math.random() * (.9 - finalFloor) : .9 + Math.random() * .3)
          : offerFloor + Math.random() * (1.75 - offerFloor);
        return { ...buyer, amount: +Math.max(.01, value * mult).toFixed(2) };
      });
      S.cardAuction = { uid, value, offerIndex: 0, offers }; S.auctionMessage = ''; save(); renderAuctions();
    }
    function declineAuctionOffer() {
      if (!S || !S.cardAuction || S.cardAuction.offerIndex >= 4) return;
      S.cardAuction.offerIndex++; save(); renderAuctions();
    }
    function acceptAuctionOffer() {
      if (!S || !S.cardAuction) return;
      const auction = S.cardAuction, itemIndex = BINDER.findIndex(x => x.uid === auction.uid); if (itemIndex < 0) { S.cardAuction = null; save(); return renderAuctions(); }
      const item = BINDER[itemIndex], offer = auction.offers[auction.offerIndex];
      BINDER.splice(itemIndex, 1); BATTLE_DECK = BATTLE_DECK.filter(uid => uid !== auction.uid);
      S.bank = +(S.bank + offer.amount).toFixed(2); S.earned = +(S.earned + offer.amount).toFixed(2); S.peak = Math.max(S.peak, S.bank);
      S.auctionMessage = `${offer.ico} ${offer.name} bought ${item.c.n} for ${money(offer.amount)} on offer ${auction.offerIndex + 1}/5.`; S.cardAuction = null;
      saveBinder(); saveBattleDeck(); save(); hud(); renderBinder(); renderAuctions();
    }
    function renderAuctions() {
      if (!auctionMode()) { $('auctionStatus').innerHTML = 'Start any game mode to auction Binder cards.'; $('auctionLots').innerHTML = ''; return; }
      $('auctionStatus').innerHTML = S.auctionMessage || (S.cardAuction ? 'Your card is locked into this auction. You must accept one of the five offers.' : 'Choose a Binder card to begin. Once started, the card cannot leave the auction.');
      if (!S.cardAuction) {
        $('auctionLots').innerHTML = BINDER.length ? `<div class="binder-cards">${BINDER.map(item => `<div class="card binder-card r${RANK(item.c.r)}"><span class="val ${binderValue(item) >= 5 ? 'big' : ''}">${money(binderValue(item))}</span><img src="${cardUrl(item.c)}" alt="${item.c.n}" loading="lazy"><div class="name">${item.c.n}</div><div class="rarity">${tradeSetName(item.set || item.c.id.split('-')[0])}</div><button data-start-auction="${item.uid}">AUCTION THIS CARD</button></div>`).join('')}</div>` : '<p class="sub">Your Binder is empty. Keep a card before starting an auction.</p>';
        $('auctionLots').querySelectorAll('[data-start-auction]').forEach(b => b.onclick = () => startCardAuction(b.dataset.startAuction)); return;
      }
      const auction = S.cardAuction, item = BINDER.find(x => x.uid === auction.uid); if (!item) { S.cardAuction = null; save(); return renderAuctions(); }
      const i = auction.offerIndex, offer = auction.offers[i], final = i === 4;
      $('auctionLots').innerHTML = `<div class="trade-grid"><div class="trade-card"><img src="${cardUrl(item.c)}" alt="${item.c.n}"><b>${item.c.n}</b><small>Your card value</small><strong style="display:block;color:#8dffb0;margin-top:7px">${money(auction.value)}</strong></div><div class="trade-vs">→</div><div class="trade-card"><div style="font-size:70px">${offer.ico}</div><b>${offer.name}</b><small>AI buyer ${i + 1} of 5</small><strong style="display:block;color:${offer.amount >= auction.value ? '#8dffb0' : '#ffb36b'};margin-top:7px">OFFERS ${money(offer.amount)}</strong></div></div><div class="summary" style="text-align:center">${final ? '<b>FINAL OFFER — YOU MUST ACCEPT</b><br>The fifth buyer is usually the worst deal.' : `<b>Accept now, or decline and hope buyer ${i + 2} pays more.</b>`}</div><div style="text-align:center"><button class="primary" id="btnAcceptAuction">ACCEPT ${money(offer.amount)}</button>${final ? '' : '<button class="ghost" id="btnDeclineAuction">DECLINE & WAIT</button>'}</div>`;
      $('btnAcceptAuction').onclick = acceptAuctionOffer; if ($('btnDeclineAuction')) $('btnDeclineAuction').onclick = declineAuctionOffer;
    }
    function showAuctionHouse() { renderAuctions(); $('auctionHouse').classList.add('on'); }

    function binderUpgradeLevel(key) {
      const run = S && !S.ended ? S : load();
      return run && run.up ? run.up[key] || 0 : 0;
    }
    function upgradeMultiplier(key) {
      const upgrade = UPGRADES.find(item => item.k === key);
      return upgrade.mult[Math.min(upgrade.mult.length - 1, binderUpgradeLevel(key))];
    }
    const binderCapacity = () => BINDER_CAPACITY_LEVELS[Math.min(BINDER_CAPACITY_LEVELS.length - 1, binderUpgradeLevel('binderspace'))];
    const binderGrowthMult = () => BINDER_GROWTH_LEVELS[Math.min(BINDER_GROWTH_LEVELS.length - 1, binderUpgradeLevel('bindergrowth'))];
    const binderValue = item => item.fake ? 0 : +(item.value * (Date.now() - item.keptAt >= BINDER_GROW_MS ? binderGrowthMult() * (hasRelic('binderclock') ? 1.1 : 1) : 1)).toFixed(2);
    function keepCard(index) {
      const p = S.last && S.last.pull[index];
      if (!p || p.kept || BINDER.length >= binderCapacity()) return;
      const value = p.grade ? p.grade.value : p.v;
      if (paidMode() && S.bank < value) return;
      if (paidMode()) {
        S.bank = +(S.bank - value).toFixed(2);
        S.earned = +(S.earned - value).toFixed(2);
      }
      S.last.total = +(S.last.total - value).toFixed(2);
      p.kept = true;
      BINDER.unshift({ uid: `${Date.now()}-${Math.random()}`, c: p.c, value, keptAt: Date.now(), grade: p.grade ? p.grade.n : null, shaken: !!p.shaken, fake: !!p.fake, store: p.store || selectedStore, set: selectedSet });
      saveBinder(); save();
      render(S.last.pull, S.last.cost, S.last.total);
    }
    function sellBinder(uid) {
      if (S && S.cardAuction && S.cardAuction.uid === uid) return showAuctionHouse();
      const run = binderSellRun();
      if (!run) return;
      const index = BINDER.findIndex(item => item.uid === uid);
      if (index < 0) return;
      const value = binderValue(BINDER[index]);
      BINDER.splice(index, 1);
      BATTLE_DECK = BATTLE_DECK.filter(cardUid => cardUid !== uid);
      run.bank = +(run.bank + value).toFixed(2);
      run.earned = +(run.earned + value).toFixed(2);
      run.peak = Math.max(run.peak || 0, run.bank);
      saveBinder();
      saveBattleDeck();
      if (run === S) {
        const clearedQuota = checkQuotaProgress();
        save(); hud();
        if (clearedQuota) $('title').textContent = '✅ QUOTA CLEARED!';
      } else {
        saveSpecificRun(run);
        $('btnContinue').hidden = false;
      }
      renderBinder();
    }
    function tradeCardValue(c, setId) {
      const rank = RANK(c.r);
      const raw = rank >= 2 ? (c.ph || c.p || c.pr || 0) : (c.p || c.pr || c.ph || 0);
      return +(raw * ((SET_META[setId] && SET_META[setId].valueMult) || 1)).toFixed(2);
    }
    function tradeSetName(setId) { return SET_META[setId] ? `${SET_META[setId].series} — ${SET_META[setId].name}` : setId; }
    function findTradeOffer(item) {
      const ownValue = Math.max(.01, tradeCardValue(item.c, item.set || item.c.id.split('-')[0]));
      const all = Object.entries(SET_DATA).flatMap(([setId, cards]) => cards.map(c => ({ c, set: setId, value: tradeCardValue(c, setId) }))).filter(x => x.c.id !== item.c.id);
      let choices = all.filter(x => x.value >= ownValue * .5 && x.value <= ownValue * 1.5);
      if (!choices.length) choices = all.sort((a, b) => Math.abs(a.value - ownValue) - Math.abs(b.value - ownValue)).slice(0, 20);
      const offer = rand(choices);
      return { ...offer, fake: Math.random() < .10 };
    }
    function openTrade(uid) {
      if (S && S.cardAuction && S.cardAuction.uid === uid) return showAuctionHouse();
      const item = BINDER.find(card => card.uid === uid);
      if (!item) return;
      ACTIVE_TRADE = { uid, offer: findTradeOffer(item) };
      const offer = ACTIVE_TRADE.offer;
      $('tradeComparison').innerHTML = `<div class="trade-card"><img src="${cardUrl(item.c)}" alt="${item.c.n}"><b>${item.c.n}</b><small>${tradeSetName(item.set || item.c.id.split('-')[0])}</small></div><div class="trade-vs">⇄</div><div class="trade-card"><img src="${cardUrl(offer.c)}" alt="${offer.c.n}"><b>${offer.c.n}</b><small>${tradeSetName(offer.set)}</small></div>`;
      $('tradePrompt').textContent = 'The offered card’s normal value is within 50% below or above yours. Prices are hidden. There is a secret 10% chance that the offered card is fake.';
      $('tradeResult').innerHTML = '';
      $('tradeActions').hidden = false;
      $('tradeContinue').hidden = true;
      $('cardTrade').classList.add('on');
    }
    function closeTrade() { ACTIVE_TRADE = null; $('cardTrade').classList.remove('on'); }
    function revealTrade(accepted) {
      if (!ACTIVE_TRADE || ACTIVE_TRADE.resolved) return;
      const item = BINDER.find(card => card.uid === ACTIVE_TRADE.uid);
      if (!item) return closeTrade();
      const offer = ACTIVE_TRADE.offer, ownValue = binderValue(item), offerValue = offer.fake ? 0 : offer.value;
      const difference = +(offerValue - ownValue).toFixed(2);
      ACTIVE_TRADE.resolved = true;
      ACTIVE_TRADE.accepted = accepted;
      ACTIVE_TRADE.ownValue = ownValue;
      ACTIVE_TRADE.offerValue = offerValue;
      if (accepted && difference > 0) { PROFILE.stats.tradeWins++; saveProfile(); checkAchievements(); }
      $('tradeComparison').innerHTML = `<div class="trade-card"><img src="${cardUrl(item.c)}" alt="${item.c.n}"><b>${item.c.n}</b><small>${tradeSetName(item.set || item.c.id.split('-')[0])}</small><strong style="display:block;color:#8dffb0;margin-top:7px">${money(ownValue)}</strong></div><div class="trade-vs">⇄</div><div class="trade-card"><img src="${cardUrl(offer.c)}" alt="${offer.c.n}"><b>${offer.c.n}</b><small>${tradeSetName(offer.set)}</small><strong style="display:block;color:${offer.fake ? '#ff6b6b' : '#8dffb0'};margin-top:7px">${offer.fake ? 'FAKE • ' : ''}${money(offerValue)}</strong></div>`;
      let verdict;
      if (offer.fake) verdict = accepted ? '😱 The offered card was fake. You accepted a terrible trade!' : '🕵️ Great decline—the offered card was fake and worth nothing.';
      else if (difference > 0) verdict = accepted ? `🎉 Great trade! You gained ${money(difference)} in card value.` : `😭 Ouch! You declined a great trade and missed ${money(difference)} in extra value.`;
      else if (difference < 0) verdict = accepted ? `😬 Bad trade. Your new card is worth ${money(Math.abs(difference))} less.` : `😌 Good decline. The offered card was worth ${money(Math.abs(difference))} less.`;
      else verdict = accepted ? '⚖️ Perfectly even trade.' : '⚖️ You declined a perfectly even trade.';
      $('tradePrompt').textContent = accepted ? 'TRADE ACCEPTED — VALUES REVEALED' : 'TRADE DECLINED — VALUES REVEALED';
      $('tradeResult').innerHTML = `<div class="summary" style="max-width:none;text-align:center"><b>${verdict}</b></div>`;
      $('tradeActions').hidden = true;
      $('tradeContinue').hidden = false;
    }
    function declineTrade() { revealTrade(false); }
    function acceptTrade() {
      if (!ACTIVE_TRADE || ACTIVE_TRADE.resolved) return;
      const index = BINDER.findIndex(item => item.uid === ACTIVE_TRADE.uid);
      if (index < 0) return closeTrade();
      const old = BINDER[index], offer = ACTIVE_TRADE.offer;
      revealTrade(true);
      BATTLE_DECK = BATTLE_DECK.filter(uid => uid !== old.uid);
      BINDER[index] = { uid: old.uid, c: offer.c, value: offer.fake ? 0 : offer.value, keptAt: Date.now(), grade: null, shaken: false, fake: offer.fake, store: 'trade', set: offer.set, training: 0 };
      saveBinder(); saveBattleDeck(); renderBinder();
    }
    function gradeBinderCard(uid) {
      if (S && S.cardAuction && S.cardAuction.uid === uid) return showAuctionHouse();
      const item = BINDER.find(item => item.uid === uid);
      if (!item || item.grade) return;
      const result = item.shaken ? GRADES.find(g => g.grade === 1) : rollGrade(item.store);
      let value = item.fake ? 0 : result.grade === 1 ? .01 : +(item.value * result.mult).toFixed(2);
      const coverLevel = S && S.up ? S.up.cover || 0 : 0;
      if (result.grade >= 2 && result.grade <= 4) value = Math.max(value, +(item.value * UPGRADES[8].mult[coverLevel]).toFixed(2));
      item.value = value;
      item.grade = result.grade;
      if (result.grade === 10) recordPSA10(item.c, value, item.set || item.c.id.split('-')[0]);
      saveBinder();
      if (paidMode()) {
        missionStep('grades');
        const clearedQuota = checkQuotaProgress();
        save(); hud();
        if (clearedQuota) $('title').textContent = '✅ QUOTA CLEARED!';
      }
      renderBinder();
    }
    function zoomBinderCard(uid) {
      const item = BINDER.find(item => item.uid === uid);
      if (!item) return;
      $('zoomImage').src = cardUrl(item.c);
      $('zoomImage').alt = item.c.n;
      $('cardZoom').classList.add('on');
    }
    function closeCardZoom() { $('cardZoom').classList.remove('on'); }
    function renderBinder() {
      const canSell = !!binderSellRun();
      cleanBattleDeck();
      $('binderCount').textContent = `${BINDER.length}/${binderCapacity()}`;
      $('binderDeckCount').textContent = `${BATTLE_DECK.length}/3`;
      $('binderList').innerHTML = BINDER.length ? BINDER.map(item => {
        const stats = battleStats(item);
        const selected = BATTLE_DECK.includes(item.uid);
        const locked = !!(S && S.cardAuction && S.cardAuction.uid === item.uid);
        const pickText = locked ? '🔒 LOCKED IN AUCTION' : selected ? '✓ IN BATTLE DECK' : BATTLE_DECK.length >= 3 ? 'DECK FULL • REMOVE ONE FIRST' : '⚔️ ADD TO BATTLE DECK';
        const tag = locked ? '<span class="tag">IN AUCTION</span>' : item.fake ? '<span class="tag">FAKE • $0</span>' : item.grade ? `<span class="tag">PSA ${item.grade}</span>` : selected ? '<span class="tag">BATTLE DECK</span>' : '';
        return `<div class="card binder-card r${RANK(item.c.r)}"><span class="val ${binderValue(item) >= 5 ? 'big' : ''}" data-binder-price="${item.uid}">${money(binderValue(item))}</span>${tag}<img data-view="${item.uid}" src="${cardUrl(item.c)}" alt="${item.c.n}" loading="lazy"><div class="name">${item.c.n}</div><div class="rarity">${item.c.r}</div><div class="battle-stats">❤️ ${stats.hp} HP • 💥 ${stats.dmg} MAX DMG • 🏋️ ${stats.training}/10</div><button class="keep-btn" data-binder-deck="${item.uid}" ${locked ? 'disabled' : ''}>${pickText}</button><button class="ghost" style="width:100%;padding:8px 6px;font-size:12px" data-trade="${item.uid}" ${locked ? 'disabled' : ''}>🔄 TRADE CARD</button><button class="ghost" style="width:100%;padding:8px 6px;font-size:12px" data-auction-card="${item.uid}">${locked ? '🔨 CONTINUE AUCTION' : '🔨 AUCTION CARD'}</button>${item.grade ? '' : `<button class="grade-btn" data-binder-grade="${item.uid}" ${locked ? 'disabled' : ''}>${item.shaken ? 'GRADE WITH PSA • FORCED PSA 1' : 'GRADE WITH PSA'}</button>`}<button class="grade-btn" data-sell="${item.uid}" ${canSell && !locked ? '' : 'disabled'}>${locked ? 'LOCKED IN AUCTION' : canSell ? `${selected ? 'SELL & REMOVE FROM DECK' : 'SELL'} • ${money(binderValue(item))}` : 'START ANY GAME TO SELL'}</button></div>`;
      }).join('') : '<p class="sub" style="grid-column:1/-1">Your binder is empty. Open a pack and press KEEP IN BINDER on any card.</p>';
      $('binderList').querySelectorAll('[data-sell]').forEach(b => b.onclick = () => sellBinder(b.dataset.sell));
      $('binderList').querySelectorAll('[data-binder-grade]').forEach(b => b.onclick = () => gradeBinderCard(b.dataset.binderGrade));
      $('binderList').querySelectorAll('[data-binder-deck]').forEach(b => b.onclick = () => toggleBattleCard(b.dataset.binderDeck));
      $('binderList').querySelectorAll('[data-trade]').forEach(b => b.onclick = () => openTrade(b.dataset.trade));
      $('binderList').querySelectorAll('[data-auction-card]').forEach(b => b.onclick = () => {
        if (S && S.cardAuction) showAuctionHouse();
        else { startCardAuction(b.dataset.auctionCard); showAuctionHouse(); }
      });
      $('binderList').querySelectorAll('[data-view]').forEach(img => img.onclick = () => zoomBinderCard(img.dataset.view));
    }
    function refreshBinderPrices() {
      document.querySelectorAll('[data-binder-price]').forEach(el => {
        const item = BINDER.find(item => item.uid === el.dataset.binderPrice);
        if (!item) return;
        const value = binderValue(item);
        el.textContent = money(value);
        el.classList.toggle('big', value >= 5);
      });
      document.querySelectorAll('#binderList [data-sell]').forEach(button => {
        const item = BINDER.find(item => item.uid === button.dataset.sell);
        if (item && binderSellRun()) button.textContent = `${BATTLE_DECK.includes(item.uid) ? 'SELL & REMOVE FROM DECK' : 'SELL'} • ${money(binderValue(item))}`;
      });
    }
    function showBinder() {
      clearInterval(binderTimer);
      renderBinder();
      $('binder').classList.add('on');
      binderTimer = setInterval(() => { if ($('binder').classList.contains('on')) refreshBinderPrices(); }, 1000);
    }
    function closeBinder() { clearInterval(binderTimer); $('binder').classList.remove('on'); }

    const roundBattle = (n, step = 5) => Math.max(step, Math.round(n / step) * step);
    function battleStats(item) {
      const rank = RANK(item.c.r), grade = item.grade || 0, training = item.training || 0;
      const value = Math.max(.01, binderValue(item));
      const fusionBoost = hasRelic('arenacrown') ? 1.15 : 1;
      const hp = (70 + rank * 30 + Math.min(120, Math.log2(value + 1) * 18) + grade * 3 + training * 12) * fusionBoost;
      const dmg = (20 + rank * 22 + Math.min(100, Math.sqrt(value) * 10) + grade * 2 + training * 7) * fusionBoost;
      return {
        name: item.c.n,
        image: cardUrl(item.c),
        hp: roundBattle(hp * upgradeMultiplier('battlearmor'), 10),
        dmg: roundBattle(dmg * upgradeMultiplier('battlepower')),
        training,
      };
    }
    function cleanBattleDeck() {
      const valid = new Set(BINDER.map(item => item.uid));
      BATTLE_DECK = BATTLE_DECK.filter(uid => valid.has(uid)).slice(0, 3);
      saveBattleDeck();
    }
    function toggleBattleCard(uid) {
      if (S && S.cardAuction && S.cardAuction.uid === uid) return showAuctionHouse();
      cleanBattleDeck();
      const index = BATTLE_DECK.indexOf(uid);
      if (index >= 0) BATTLE_DECK.splice(index, 1);
      else if (BATTLE_DECK.length < 3) BATTLE_DECK.push(uid);
      saveBattleDeck();
      if ($('battle').classList.contains('on')) renderBattle();
      else renderBinder();
    }
    function trainingCost(item) {
      const level = item.training || 0;
      return Math.round(25 * Math.pow(level + 1, 1.45) * upgradeMultiplier('traincoach'));
    }
    const bribeCost = () => Math.round(BRIBE_BASE_COST * upgradeMultiplier('bribedeal'));
    const battleReward = (level, type) => Math.round(level[type] * upgradeMultiplier('battleprize') * (hasRelic('idol') ? 1.5 : 1) * (hasRelic('warchain') ? 1.75 : 1) * (hasRelic('arenacrown') ? 1.35 : 1));
    function trainBattleCard(uid) {
      const item = BINDER.find(card => card.uid === uid);
      if (!item || !S || S.ended || (item.training || 0) >= 10) return;
      const free = S.mode === 'sandbox', cost = free ? 0 : trainingCost(item);
      if (!free && (!paidMode() || S.bank < cost)) return;
      if (!free) S.bank = +(S.bank - cost).toFixed(2);
      item.training = (item.training || 0) + 1;
      saveBinder(); save();
      if (S && !S.ended) hud();
      renderBattle();
    }
    const battleReady = () => S && !S.ended && BATTLE_DECK.length === 3;
    const randomBetween = ([min, max]) => Math.round(min + Math.random() * (max - min));
    function enemyTeam(difficulty) {
      const level = BATTLE_LEVELS[difficulty];
      const all = Object.values(SET_DATA).flat();
      let pool = all.filter(card => { const rank = RANK(card.r); return rank >= level.rank[0] && rank <= level.rank[1]; });
      if (!pool.length) pool = all;
      const used = new Set();
      return Array.from({ length: 3 }, (_, i) => {
        let card, guard = 0;
        do { card = rand(pool); } while (used.has(card.id) && guard++ < 30);
        used.add(card.id);
        const ramp = 1 + i * .05;
        const curse = hasRelic('warchain') ? 1.25 : 1;
        return { name: card.n, image: cardUrl(card), hp: roundBattle(randomBetween(level.hp) * ramp * curse, 10), dmg: roundBattle(randomBetween(level.dmg) * ramp * curse) };
      });
    }
    function awardBattleCash(amount) {
      if (!paidMode() || !amount) return 0;
      S.bank = +(S.bank + amount).toFixed(2);
      S.earned = +(S.earned + amount).toFixed(2);
      S.peak = Math.max(S.peak, S.bank);
      const cleared = checkQuotaProgress();
      save(); hud();
      if (cleared) $('title').textContent = '✅ QUOTA CLEARED!';
      return amount;
    }
    const battleCooldownLeft = type => Math.max(0, (BATTLE_COOLDOWNS[type] || 0) - Date.now());
    function startBattleCooldown(type) {
      BATTLE_COOLDOWNS[type] = Date.now() + (type === 'single' ? SINGLE_BATTLE_COOLDOWN_MS : TOURNAMENT_COOLDOWN_MS);
      saveBattleCooldowns();
      updateBattleModeButtons();
    }
    function updateBattleModeButtons() {
      const ready = battleReady() && !(ACTIVE_BATTLE && !ACTIVE_BATTLE.finished);
      document.querySelectorAll('[data-single]').forEach(button => {
        const level = BATTLE_LEVELS[button.dataset.single], seconds = Math.ceil(battleCooldownLeft('single') / 1000);
        button.disabled = !ready || seconds > 0;
        button.innerHTML = `${level.ico} ${level.label}<br><small>${seconds ? `READY IN ${seconds}s` : `Win ${money(battleReward(level, 'single'))}`}</small>`;
      });
      document.querySelectorAll('[data-tournament]').forEach(button => {
        const level = BATTLE_LEVELS[button.dataset.tournament], seconds = Math.ceil(battleCooldownLeft('tournament') / 1000);
        const lacksEntry = paidMode() && S.bank < level.entry;
        button.disabled = !ready || seconds > 0 || lacksEntry;
        button.innerHTML = `${level.ico} ${level.label}<br><small>${seconds ? `READY IN ${seconds}s` : lacksEntry ? `NEED ${money(level.entry)}` : `Entry ${paidMode() ? money(level.entry) : 'FREE'} • Prize ${money(battleReward(level, 'tournament'))}`}</small>`;
      });
    }
    function startInteractiveMatch() {
      ACTIVE_BATTLE.player = BATTLE_DECK.map(uid => ({ ...battleStats(BINDER.find(item => item.uid === uid)), uid })).map(card => ({ ...card, left: card.hp }));
      ACTIVE_BATTLE.enemy = enemyTeam(ACTIVE_BATTLE.difficulty).map((card, index) => ({ ...card, uid: `enemy-${index}`, left: card.hp }));
      ACTIVE_BATTLE.log = [`Match ${ACTIVE_BATTLE.match}: choose one of your three Pokémon to attack.`];
      ACTIVE_BATTLE.waitingNext = false;
      ACTIVE_BATTLE.bribeUsed = false;
      ACTIVE_BATTLE.bribeReady = false;
      renderInteractiveBattle();
    }
    function beginInteractiveBattle(type, difficulty) {
      if (!battleReady() || battleCooldownLeft(type)) return;
      const level = BATTLE_LEVELS[difficulty];
      const entryFee = type === 'tournament' && paidMode() ? level.entry : 0;
      if (entryFee && S.bank < entryFee) return;
      ACTIVE_BATTLE = { type, difficulty, match: 1, wins: 0, losses: 0, finished: false, waitingNext: false };
      if (entryFee) {
        S.bank = +(S.bank - entryFee).toFixed(2);
        S.spent = +(S.spent + entryFee).toFixed(2);
        ACTIVE_BATTLE.entryFee = entryFee;
        save(); hud();
      }
      pauseQuotaForBattle();
      startInteractiveMatch();
      if (entryFee) {
        ACTIVE_BATTLE.log.unshift(`🎟️ Tournament entry paid: <b>${money(entryFee)}</b>.`);
        renderInteractiveBattle();
      }
      renderBattleCardsOnly();
    }
    function living(cards) { return cards.filter(card => card.left > 0); }
    function useBattleBribe() {
      const cost = bribeCost();
      if (!ACTIVE_BATTLE || ACTIVE_BATTLE.finished || ACTIVE_BATTLE.waitingNext || ACTIVE_BATTLE.bribeUsed || !paidMode() || S.bank < cost) return;
      S.bank = +(S.bank - cost).toFixed(2);
      S.spent = +(S.spent + cost).toFixed(2);
      ACTIVE_BATTLE.bribeUsed = true;
      ACTIVE_BATTLE.bribeReady = true;
      ACTIVE_BATTLE.log.push(`💵 You paid ${money(cost)}. Your next chosen Pokémon attacks twice before the trainer can respond.`);
      save(); hud(); renderInteractiveBattle();
    }
    function playerBattleAttack(uid) {
      if (!ACTIVE_BATTLE || ACTIVE_BATTLE.finished || ACTIVE_BATTLE.waitingNext) return;
      const attacker = ACTIVE_BATTLE.player.find(card => card.uid === uid && card.left > 0);
      if (!attacker) return;
      const attackCount = ACTIVE_BATTLE.bribeReady ? 2 : 1;
      if (ACTIVE_BATTLE.bribeReady) ACTIVE_BATTLE.log.push(`⚡ Bribe activated: ${attacker.name} gets two attacks!`);
      ACTIVE_BATTLE.bribeReady = false;
      for (let attack = 0; attack < attackCount; attack++) {
        const target = living(ACTIVE_BATTLE.enemy)[0];
        if (!target) return finishInteractiveMatch(true);
        target.left = Math.max(0, target.left - attacker.dmg);
        ACTIVE_BATTLE.log.push(`${attacker.name} attacks ${target.name} for <b>${attacker.dmg}</b> damage. ${target.name}: ${target.left}/${target.hp} HP`);
        if (target.left <= 0) ACTIVE_BATTLE.log.push(`⭐ ${target.name} is knocked out!`);
        if (!living(ACTIVE_BATTLE.enemy).length) return finishInteractiveMatch(true);
      }
      const enemyAttacker = rand(living(ACTIVE_BATTLE.enemy));
      const playerTarget = rand(living(ACTIVE_BATTLE.player));
      playerTarget.left = Math.max(0, playerTarget.left - enemyAttacker.dmg);
      ACTIVE_BATTLE.log.push(`${enemyAttacker.name} strikes back at ${playerTarget.name} for <b>${enemyAttacker.dmg}</b> damage. ${playerTarget.name}: ${playerTarget.left}/${playerTarget.hp} HP`);
      if (playerTarget.left <= 0) ACTIVE_BATTLE.log.push(`💥 ${playerTarget.name} is knocked out!`);
      if (!living(ACTIVE_BATTLE.player).length) return finishInteractiveMatch(false);
      renderInteractiveBattle();
    }
    function finishInteractiveMatch(won) {
      if (won) ACTIVE_BATTLE.wins++;
      else ACTIVE_BATTLE.losses++;
      ACTIVE_BATTLE.log.push(won ? '✅ You won this match!' : '❌ The trainer won this match.');
      if (ACTIVE_BATTLE.type === 'single') return finishInteractiveBattle(won);
      if (ACTIVE_BATTLE.wins >= 3 || ACTIVE_BATTLE.losses >= 3 || ACTIVE_BATTLE.match >= 5) return finishInteractiveBattle(ACTIVE_BATTLE.wins >= 3);
      ACTIVE_BATTLE.waitingNext = true;
      renderInteractiveBattle();
    }
    function nextTournamentMatch() {
      if (!ACTIVE_BATTLE || !ACTIVE_BATTLE.waitingNext) return;
      ACTIVE_BATTLE.match++;
      startInteractiveMatch();
    }
    function finishInteractiveBattle(won) {
      const level = BATTLE_LEVELS[ACTIVE_BATTLE.difficulty];
      const rewardAmount = battleReward(level, ACTIVE_BATTLE.type === 'single' ? 'single' : 'tournament');
      ACTIVE_BATTLE.finished = true;
      ACTIVE_BATTLE.won = won;
      resumeQuotaAfterBattle();
      const reward = won ? awardBattleCash(rewardAmount) : 0;
      ACTIVE_BATTLE.reward = reward;
      if (won) { const key = `${ACTIVE_BATTLE.type}-${ACTIVE_BATTLE.difficulty}`; PROFILE.trophies[key] = (PROFILE.trophies[key] || 0) + 1; if (ACTIVE_BATTLE.type === 'tournament') PROFILE.stats.tournamentWins++; saveProfile(); checkAchievements(); }
      startBattleCooldown(ACTIVE_BATTLE.type);
      hud();
      renderInteractiveBattle();
      renderBattleCardsOnly();
    }
    function interactiveFighterHtml(card, playerCard, currentTarget) {
      const percent = Math.max(0, card.left / card.hp * 100), knockedOut = card.left <= 0;
      const classes = `battle-fighter ${knockedOut ? 'ko' : playerCard ? 'ready' : currentTarget ? 'target' : ''}`;
      const body = `<img src="${card.image}" alt="${card.name}" loading="lazy"><b>${card.name}</b><div class="health-track"><div class="health-fill" style="width:${percent}%"></div></div><small>${card.left}/${card.hp} HP</small><small>${card.dmg} DMG</small>${playerCard && !knockedOut ? '<small>👆 TAP TO ATTACK</small>' : ''}`;
      return playerCard ? `<button class="${classes}" data-player-attack="${card.uid}" ${knockedOut ? 'disabled' : ''}>${body}</button>` : `<div class="${classes}">${body}</div>`;
    }
    function renderInteractiveBattle() {
      const battle = ACTIVE_BATTLE;
      if (!battle) { $('battleResult').innerHTML = ''; return; }
      const level = BATTLE_LEVELS[battle.difficulty], target = living(battle.enemy)[0];
      const score = battle.type === 'tournament' ? `Tournament match ${battle.match}/5 • You ${battle.wins}–${battle.losses} Trainer` : `${level.label} single battle`;
      let heading = battle.finished ? (battle.won ? '🏆 YOU WON!' : '💀 YOU LOST') : battle.waitingNext ? (battle.log[battle.log.length - 1]) : 'CHOOSE A POKÉMON TO ATTACK';
      let action = '';
      let bribeAction = '';
      if (battle.waitingNext) action = '<button class="primary" id="btnNextBattleMatch">NEXT MATCH</button>';
      if (battle.finished) action = `<p>${battle.won ? (paidMode() ? `Reward: <b>${money(battle.reward)}</b>` : 'Sandbox victory — no cash reward.') : 'Your cards are safe. Train or change your deck and try again.'}</p>`;
      if (!battle.finished && !battle.waitingNext) {
        const canBribe = paidMode() && S.bank >= bribeCost() && !battle.bribeUsed;
        const bribeText = battle.bribeReady ? '⚡ EXTRA ATTACK READY' : battle.bribeUsed ? '💵 BRIBE USED THIS MATCH' : paidMode() ? `💵 BRIBE TRAINER • ${money(bribeCost())}` : '💵 BRIBE REQUIRES MONEY MODE';
        bribeAction = `<button class="ghost" id="btnBattleBribe" ${canBribe ? '' : 'disabled'}>${bribeText}</button>`;
      }
      $('battleResult').innerHTML = `<div class="battle-result ${battle.finished ? battle.won ? 'win' : 'loss' : ''}"><h2>${heading}</h2><div class="battle-prompt">${score}</div>${bribeAction}<div class="battle-arena"><div><b>Your team</b><div class="battle-lineup">${battle.player.map(card => interactiveFighterHtml(card, true, false)).join('')}</div></div><div class="battle-vs">VS</div><div><b>Trainer team</b><div class="battle-lineup">${battle.enemy.map(card => interactiveFighterHtml(card, false, target === card)).join('')}</div></div></div>${action}<div class="battle-log">${battle.log.slice(-12).join('<br>')}</div></div>`;
      $('battleResult').querySelectorAll('[data-player-attack]').forEach(button => button.onclick = () => playerBattleAttack(button.dataset.playerAttack));
      if ($('btnBattleBribe')) $('btnBattleBribe').onclick = useBattleBribe;
      if ($('btnNextBattleMatch')) $('btnNextBattleMatch').onclick = nextTournamentMatch;
    }
    function runSingleBattle(difficulty) { beginInteractiveBattle('single', difficulty); }
    function runTournament(difficulty) { beginInteractiveBattle('tournament', difficulty); }
    function renderBattleCardsOnly() {
      cleanBattleDeck();
      const locked = ACTIVE_BATTLE && !ACTIVE_BATTLE.finished;
      $('battleDeckCount').textContent = `(${BATTLE_DECK.length}/3 selected)`;
      $('battleCards').innerHTML = BINDER.length ? BINDER.map(item => {
        const stats = battleStats(item), selected = BATTLE_DECK.includes(item.uid), maxed = stats.training >= 10;
        const free = S && S.mode === 'sandbox', cost = free ? 0 : trainingCost(item);
        const canTrain = !locked && S && !S.ended && !maxed && (free || (paidMode() && S.bank >= cost));
        return `<div class="battle-choice ${selected ? 'selected' : ''}"><img src="${stats.image}" alt="${item.c.n}" loading="lazy"><b>${item.c.n}</b><div class="battle-stats">❤️ ${stats.hp} HP<br>💥 ${stats.dmg} MAX DMG<br>🏋️ Training ${stats.training}/10</div><button data-battle-pick="${item.uid}" ${locked ? 'disabled' : ''}>${locked ? 'BATTLE IN PROGRESS' : selected ? '✓ IN DECK' : BATTLE_DECK.length >= 3 ? 'DECK FULL' : 'ADD TO DECK'}</button><button class="ghost" data-battle-train="${item.uid}" ${canTrain ? '' : 'disabled'}>${maxed ? 'MAX TRAINED' : locked ? 'BATTLE IN PROGRESS' : free ? 'TRAIN • FREE' : `TRAIN • ${money(cost)}`}</button></div>`;
      }).join('') : '<p class="sub" style="grid-column:1/-1">Your Binder is empty. Keep cards from opened packs before battling.</p>';
      $('battleCards').querySelectorAll('[data-battle-pick]').forEach(button => button.onclick = () => toggleBattleCard(button.dataset.battlePick));
      $('battleCards').querySelectorAll('[data-battle-train]').forEach(button => button.onclick = () => trainBattleCard(button.dataset.battleTrain));
      updateBattleModeButtons();
    }
    function renderBattle() {
      const active = S && !S.ended;
      $('battleStatus').innerHTML = !active ? 'Start or continue a run before battling.' : S.mode === 'sandbox' ? '<b>Sandbox practice:</b> training is free, but battles do not award cash.' : `<b>Bankroll: ${money(S.bank)}</b> • Training permanently improves Binder cards.`;
      $('singleBattles').innerHTML = Object.entries(BATTLE_LEVELS).map(([key, level]) => `<button data-single="${key}">${level.ico} ${level.label}<br><small>Win ${money(battleReward(level, 'single'))}</small></button>`).join('');
      $('tournamentBattles').innerHTML = Object.entries(BATTLE_LEVELS).map(([key, level]) => `<button data-tournament="${key}">${level.ico} ${level.label}<br><small>Entry ${paidMode() ? money(level.entry) : 'FREE'} • Prize ${money(battleReward(level, 'tournament'))}</small></button>`).join('');
      $('singleBattles').querySelectorAll('[data-single]').forEach(button => button.onclick = () => runSingleBattle(button.dataset.single));
      $('tournamentBattles').querySelectorAll('[data-tournament]').forEach(button => button.onclick = () => runTournament(button.dataset.tournament));
      renderBattleCardsOnly();
      updateBattleModeButtons();
    }
    function showBattle() {
      closeBinder();
      $('battleResult').innerHTML = '';
      renderBattle();
      $('battle').classList.add('on');
      clearInterval(battleCooldownTimer);
      battleCooldownTimer = setInterval(updateBattleModeButtons, 250);
    }
    function closeBattle() { clearInterval(battleCooldownTimer); resumeQuotaAfterBattle(); ACTIVE_BATTLE = null; $('battle').classList.remove('on'); }

    function missionStep(k, amount = 1) {
      if (!paidMode()) return [];
      S.missions[k] = (S.missions[k] || 0) + amount;
      const completed = [];
      MISSIONS.forEach(m => {
        if (!S.missions.claimed[m.k] && S.missions[m.k] >= m.goal) {
          S.missions.claimed[m.k] = true;
          S.bank = +(S.bank + m.reward).toFixed(2);
          completed.push(`${m.ico} ${m.name} +${money(m.reward)}`);
        }
      });
      return completed;
    }

    function showMissions() {
      $('missionList').innerHTML = MISSIONS.map(m => {
        const progress = Math.min(m.goal, S.missions[m.k] || 0), done = !!S.missions.claimed[m.k];
        return `<div class="up ${done ? 'max' : ''}"><div class="ico">${m.ico}</div><div class="body"><b>${m.name}</b><small>${m.desc}</small><div class="quota-track"><div class="quota-fill" style="width:${progress / m.goal * 100}%"></div></div><div class="tier">${done ? 'COMPLETED' : `${progress}/${m.goal}`} • reward ${money(m.reward)}</div></div></div>`;
      }).join('');
      $('missions').classList.add('on');
    }

    function ensureQuota() {
      if (quotaMode() && !S.quota) S.quota = { number: 1, cleared: 0, target: quotaStart(), endsAt: Date.now() + quotaSeconds() * 1000 };
    }
    function pauseQuotaForBattle() {
      if (quotaMode() && S.quota && !battleQuotaPausedAt) {
        battleQuotaPausedAt = Date.now();
        updateQuotaHud();
      }
    }
    function resumeQuotaAfterBattle() {
      if (!battleQuotaPausedAt) return;
      if (quotaMode() && S.quota) {
        S.quota.endsAt += Date.now() - battleQuotaPausedAt;
        save();
      }
      battleQuotaPausedAt = 0;
      updateQuotaHud();
    }
    function updateQuotaHud() {
      const active = quotaMode() && S.quota;
      $('quotaBox').hidden = !active;
      if (!active) return;
      const left = Math.max(0, S.quota.endsAt - (battleQuotaPausedAt || Date.now()));
      const seconds = Math.ceil(left / 1000);
      $('quotaLabel').textContent = `QUOTA ${S.quota.number} • ${money(S.quota.target)}`;
      $('quotaTime').textContent = `${battleQuotaPausedAt ? '⏸ ' : ''}0:${String(seconds).padStart(2, '0')}`;
      $('quotaTime').classList.toggle('danger', seconds <= 10);
      $('quotaFill').style.width = Math.min(100, S.bank / S.quota.target * 100) + '%';
      $('quotaProgress').textContent = `${money(S.bank)} / ${money(S.quota.target)} • ${S.quota.cleared} cleared • highest quota ${Math.max(S.quota.number, quotaRecord())}`;
    }
    function advanceQuota() {
      S.quota.cleared++;
      S.quota.number++;
      PROFILE.stats.bestQuota = Math.max(PROFILE.stats.bestQuota, S.quota.cleared); saveProfile(); checkAchievements();
      S.quota.target = +(quotaStart() * Math.pow(quotaMult(), S.quota.number - 1)).toFixed(2);
      S.quota.endsAt = Date.now() + quotaSeconds() * 1000;
      saveQuotaRecord(S.quota.number);
      save(); updateQuotaHud();
    }
    function checkQuotaProgress() {
      if (!quotaMode() || !S.quota || S.bank < S.quota.target) return false;
      advanceQuota();
      return true;
    }
    function startQuotaTimer() {
      clearInterval(quotaTimer);
      if (!quotaMode()) { updateQuotaHud(); return; }
      ensureQuota(); saveQuotaRecord(S.quota.number); updateQuotaHud();
      quotaTimer = setInterval(() => {
        if (!quotaMode() || !S.quota) return;
        if (battleQuotaPausedAt) { updateQuotaHud(); return; }
        if (Date.now() >= S.quota.endsAt) {
          if (S.bank >= S.quota.target) {
            advanceQuota();
            $('title').textContent = '✅ QUOTA CLEARED!';
          } else {
            bust('⏰ QUOTA FAILED');
          }
        }
        updateQuotaHud();
      }, 250);
    }

    const packCost = (storeId = selectedStore, useEvent = true, basePrice = meta().price) => paidMode() ? +(basePrice * store(storeId).priceMult * UPGRADES[3].mult[S.up.whole] * (hasRelic('coupon') ? .95 : 1) * (hasRelic('merchantseal') ? .88 : 1) * (hasRelic('smugglermap') ? .8 : 1) * (hasRelic('idol') ? 1.15 : 1) * (useEvent && S.event && S.event.k === 'sale' ? .75 : 1) * (S.mode === 'hard' ? HARD_PACK_MULT : 1)).toFixed(2) : 0;
    const boxDiscount = () => Math.min(.5, UPGRADES[10].mult[S.up.boxdeal] + (hasRelic('boxcutter') ? .05 : 0) + (hasRelic('merchantseal') ? .08 : 0));
    const boxCost = () => +(packCost(selectedStore, false) * BOX_PACKS * (1 - boxDiscount())).toFixed(2);
    const mysteryDiscount = () => Math.min(.5, boxDiscount() + .05);
    const mysteryBoxCost = () => paidMode() ? +(SET_META.me04.price * 5 * store().priceMult * UPGRADES[3].mult[S.up.whole] * (hasRelic('coupon') ? .95 : 1) * (hasRelic('merchantseal') ? .88 : 1) * (hasRelic('smugglermap') ? .8 : 1) * (hasRelic('idol') ? 1.15 : 1) * (S.mode === 'hard' ? HARD_PACK_MULT : 1) * BOX_PACKS * (1 - mysteryDiscount())).toFixed(2) : 0;
    function rollMysterySet() {
      let roll = Math.random() * MYSTERY_SETS.reduce((sum, choice) => sum + choice.weight, 0);
      for (const choice of MYSTERY_SETS) { roll -= choice.weight; if (roll < 0) return choice.id; }
      return MYSTERY_SETS[MYSTERY_SETS.length - 1].id;
    }
    const currentBoxPacks = () => (S.boxes && S.boxes[selectedSet]) || 0;
    const totalBoxPacks = () => Object.values(S.boxes || {}).reduce((sum, n) => sum + n, 0);
    const minPackCost = () => Math.min(...Object.values(SET_META).map(s => +(s.price * STORES.black.priceMult * UPGRADES[3].mult[S.up.whole] * (hasRelic('coupon') ? .95 : 1) * (hasRelic('merchantseal') ? .88 : 1) * (hasRelic('smugglermap') ? .8 : 1) * (hasRelic('idol') ? 1.15 : 1) * (S.event && S.event.k === 'sale' ? .75 : 1) * (S.mode === 'hard' ? HARD_PACK_MULT : 1)).toFixed(2)));
    const bulkMult = () => UPGRADES[1].mult[S.up.bulk];
    const luckMult = () => UPGRADES[0].mult[S.up.luck];
    const shakeLuckMult = () => UPGRADES[13].mult[S.up.shakepower];
    const shakeCooldownSeconds = () => UPGRADES[14].mult[S.up.shakecool];

    function rollHitRarity(storeId = selectedStore, extraLuck = 1) {
      const entries = Object.entries(HIT_W).filter(([r]) => BY[r] && BY[r].length).map(([r, w]) => [r, CHASE.has(r) ? w * luckMult() * extraLuck * (hasRelic('luckycoin') ? 1.5 : 1) * (hasRelic('starcore') ? 1.35 : 1) * (hasRelic('cursedclover') ? 2 : 1) * (S.event && S.event.k === 'restock' ? 2 : 1) * store(storeId).luckMult * (S.kissBoost ? KISS_LUCK_MULT : 1) * (S.shakeBoost ? shakeLuckMult() : 1) * (S.mode === 'hard' ? HARD_CHASE_MULT : 1) : w]);
      const total = entries.reduce((a, e) => a + e[1], 0);
      let x = Math.random() * total;
      for (const [r, w] of entries) { x -= w; if (x <= 0) return r; }
      return 'Rare';
    }
    function cardValue(c, slot) {
      const rk = RANK(c.r);
      let v = slot === 'rev' ? (c.pr || c.p || c.ph || 0) : rk >= 2 ? (c.ph || c.p || c.pr || 0) : (c.p || c.pr || c.ph || 0);
      v *= meta().valueMult;
      if (!CHASE.has(c.r)) v *= bulkMult();
      if (slot === 'base') v *= UPGRADES[25].mult[S.up.baseboost];
      if (slot === 'hit' && rk === 2) v *= UPGRADES[26].mult[S.up.rareboost];
      v *= UPGRADES[27].mult[S.up.marketboost];
      if (slot === 'rev' || slot === 'hit') v *= UPGRADES[5].mult[S.up.shine];
      if (v >= 20) v *= UPGRADES[9].mult[S.up.jackpot];
      v *= hasRelic('sleeve') ? 1.2 : 1;
      v *= hasRelic('crown') ? 1.35 : 1;
      v *= hasRelic('starcore') ? 1.2 : 1;
      v *= hasRelic('cursedclover') ? .8 : 1;
      if (hasRelic('darkmirror')) v *= slot === 'hit' ? 1.75 : .6;
      if (slot === 'rev' || slot === 'hit') v *= hasRelic('prism') ? 1.25 : 1;
      if (S.event && S.event.k === 'boom') v *= 1.5;
      if (S.event && S.event.k === 'crash') v *= .6;
      v *= 1 + Object.values(PROFILE.setRewards || {}).filter(Boolean).length * .02;
      return +v.toFixed(2);
    }

    function rollGradeOnce() {
      const mintLevel = S && S.up ? S.up.mint || 0 : 0;
      let x = Math.random() * 100;
      for (const result of GRADES) {
        x -= result.chance;
        if (x < 0) return GRADES.find(g => g.grade === Math.min(10, result.grade + mintLevel));
      }
      return GRADES[GRADES.length - 1];
    }
    function rollGrade(storeId = selectedStore) {
      const recheckLevel = S && S.up ? S.up.recheck || 0 : 0;
      let best = rollGradeOnce();
      const rolls = UPGRADES[11].mult[recheckLevel] + store(storeId).psaRerolls + (hasRelic('loupe') ? 2 : 0) + (hasRelic('guardianeye') ? 1 : 0);
      for (let i = 1; i < rolls; i++) {
        const result = rollGradeOnce();
        if (result.grade > best.grade) best = result;
      }
      return best;
    }

    function gradeCard(index) {
      const p = S.last && S.last.pull[index];
      if (!p || p.grade || p.kept) return;
      const result = p.shaken ? GRADES.find(g => g.grade === 1) : rollGrade(p.store);
      let value = p.fake ? 0 : result.grade === 1 ? .01 : +(p.v * result.mult).toFixed(2);
      if (result.grade >= 2 && result.grade <= 4) value = Math.max(value, +(p.v * UPGRADES[8].mult[S.up.cover]).toFixed(2));
      const delta = +(value - p.v).toFixed(2);
      p.grade = { n: result.grade, mult: result.mult, value, delta };
      if (result.grade === 10) recordPSA10(p.c, value, selectedSet);
      S.last.total = +(S.last.total + delta).toFixed(2);
      S.earned = +(S.earned + delta).toFixed(2);
      if (paidMode()) S.bank = +(S.bank + delta).toFixed(2);
      const missionRewards = missionStep('grades');
      if (missionRewards.length) S.last.mission = [...(S.last.mission || []), ...missionRewards];
      if (!S.best || value > S.best.v) S.best = { id: p.c.id, n: p.c.n, r: p.c.r, v: value, img: p.c.img };
      const clearedQuota = checkQuotaProgress();
      save();
      render(S.last.pull, S.last.cost, S.last.total);
      if (clearedQuota) $('title').textContent = '✅ QUOTA CLEARED!';
    }

    function pullPack(storeId = selectedStore, fake = false, extraLuck = 1, extraHit = 0) {
      const used = new Set();
      const take = (pool, slot) => { let c, n = 0; do { c = rand(pool); } while (used.has(c.id) && n++ < 50); used.add(c.id); return { c, slot, v: 0 }; };
      const base = [...(BY['Common'] || []), ...(BY['Uncommon'] || []), ...(BY['Rare'] || [])];
      const pull = [];
      const firstEdition = selectedSet === 'base1';
      const celebration = selectedSet === '30th';
      if (celebration) {
        // Official five-card foil format: one of the 30 Pikachu rares in every pack.
        for (let i = 0; i < 2; i++) pull.push(take(BY['Common'], 'rev'));
        pull.push(take([...BY['Common'], ...BY['Rare'], ...BY['Double rare']], 'rev'));
        pull.push(take(BY[rollHitRarity(storeId, extraLuck)], 'hit'));
        pull.push(take(BY['Pikachu Rare'], 'hit'));
        for (let i = 0; i < S.up.rev; i++) pull.push(take(BY['Common'], 'rev'));
      } else {
        for (let i = 0; i < (firstEdition ? 7 : 4); i++) pull.push(take(BY['Common'], 'base'));
        for (let i = 0; i < 3; i++) pull.push(take(BY['Uncommon'], 'base'));
        if (!firstEdition) for (let i = 0; i < 2 + S.up.rev; i++) pull.push(take(base, 'rev'));
        pull.push(take(BY[rollHitRarity(storeId, extraLuck)], 'hit'));
      }
      for (let i = 0; i < UPGRADES[12].mult[S.up.extras]; i++) pull.push(take(celebration ? BY['Common'] : [...BY['Common'], ...BY['Uncommon']], celebration ? 'rev' : 'base'));
      if (!firstEdition && Math.random() < Math.min(1, DOUBLE_HIT_CHANCE + UPGRADES[6].mult[S.up.bonus] + extraHit)) {
        const replaceable = pull.map((p, i) => p.slot !== 'hit' ? i : -1).filter(i => i >= 0);
        pull[rand(replaceable)] = take(BY[rollHitRarity(storeId, extraLuck)], 'hit');
      }
      for (let i = pull.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [pull[i], pull[j]] = [pull[j], pull[i]];
      }
      pull.forEach(p => { p.store = storeId; p.fake = fake; p.v = fake ? 0 : cardValue(p.c, p.slot); });
      return pull;
    }

    const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
    async function playPackOpening(pull, mysteryArt = null) {
      const overlay = $('packOpening'), pack = $('openingPack'), rip = $('packRip'), cards = $('flyingCards');
      const art = mysteryArt || meta().art;
      $('openingPackImage').src = art;
      $('openingPackTop').src = art;
      $('openingTitle').textContent = mysteryArt ? 'OPENING MYSTERY PACK…' : `OPENING ${meta().name.toUpperCase()}…`;
      cards.innerHTML = '';
      pack.classList.remove('opened');
      rip.classList.remove('tear');
      overlay.classList.add('on');
      overlay.setAttribute('aria-hidden', 'false');
      await wait(520);
      rip.classList.add('tear');
      pack.classList.add('opened');
      await wait(480);
      pull.forEach(p => {
        const img = document.createElement('img');
        img.className = 'flying-card';
        img.src = cardUrl(p.c);
        img.alt = p.c.n;
        cards.appendChild(img);
      });
      await new Promise(requestAnimationFrame);
      const packRect = pack.getBoundingClientRect();
      const originX = packRect.left + packRect.width / 2;
      const originY = packRect.top + packRect.height * .45;
      const animations = [...cards.children].map((card, i) => {
        const rect = card.getBoundingClientRect();
        const dx = originX - (rect.left + rect.width / 2);
        const dy = originY - (rect.top + rect.height / 2);
        return card.animate([
          { opacity: 0, transform: `translate(${dx}px, ${dy}px) scale(.16) rotate(${i % 2 ? 14 : -14}deg)` },
          { opacity: 1, transform: 'translate(0, 0) scale(1.06) rotate(0deg)', offset: .82 },
          { opacity: 1, transform: 'translate(0, 0) scale(1) rotate(0deg)' },
        ], { duration: 620, delay: i * 85, easing: 'cubic-bezier(.18,.78,.24,1)', fill: 'forwards' }).finished.catch(() => {});
      });
      await Promise.all(animations);
      $('openingTitle').textContent = 'PACK OPENED!';
      await wait(260);
      overlay.classList.remove('on');
      overlay.setAttribute('aria-hidden', 'true');
      cards.innerHTML = '';
    }

    async function openPack(randomTier = null, showPack = false) {
      if (packAnimating || !S || S.ended) return;
      const tier = randomTier && RANDOM_PACKS[randomTier];
      if (randomTier && !tier) return;
      if (showPack && S.event?.k !== 'show') return;
      const fromBox = !tier && !showPack && currentBoxPacks() > 0;
      const boxQueue = (S.boxStores && S.boxStores[selectedSet]) || [];
      const boxEntry = fromBox ? boxQueue[0] : null;
      const storeId = showPack ? 'show' : fromBox ? (typeof boxEntry === 'object' ? boxEntry?.store : boxEntry) || selectedStore : selectedStore;
      const cost = fromBox ? 0 : packCost(storeId, true, tier ? tier.price : meta().price);
      if (paidMode() && S.bank < cost) return;
      $('mysteryShop').classList.remove('on');
      if (tier) {
        const setId = rand(tier.sets);
        activateSet(setId);
        S.set = setId;
      }
      if (fromBox) { boxQueue.shift(); S.boxes[selectedSet]--; }
      const fakeChance = showPack ? 0 : Math.max(0, Math.min(1, store(storeId).fakeChance + (tier ? tier.fake : 0) + (hasRelic('crown') ? .15 : 0) + (hasRelic('smugglermap') ? .20 : 0) + (S.event && S.event.k === 'counterfeit' ? .20 : 0) - (hasRelic('guardianeye') ? .10 : 0)));
      const fake = Math.random() < fakeChance;
      const usedEvent = S.event && (S.event.k !== 'show' || showPack) ? S.event : null;
      const pull = pullPack(storeId, fake, tier ? tier.luck : fromBox && typeof boxEntry === 'object' ? boxEntry.luck || 1 : 1, tier ? tier.extraHit || 0 : 0);
      recordPackMuseum(pull, selectedSet, fake);
      if (S.shakeBoost) pull.forEach(p => p.shaken = true);
      S.kissBoost = false;
      S.shakeBoost = false;
      const total = +pull.reduce((a, p) => a + p.v, 0).toFixed(2);
      S.bank = +(S.bank - cost + total).toFixed(2);
      S.packs++; S.spent = +(S.spent + cost).toFixed(2); S.earned = +(S.earned + total).toFixed(2);
      S.peak = Math.max(S.peak, S.bank);
      const hit = pull.reduce((a, p) => p.v > a.v ? p : a, pull[0]);
      if (!S.best || hit.v > S.best.v) S.best = { id: hit.c.id, n: hit.c.n, r: hit.c.r, v: hit.v, img: hit.c.img };
      S.last = { pull, cost, total, store: storeId, fake, eventUsed: usedEvent, randomTier: tier ? tier.name : null };
      S.last.fromBox = fromBox;
      if (usedEvent) S.event = null;
      if (!S.event && Math.random() < RANDOM_EVENT_CHANCE) S.event = rand(RANDOM_EVENTS);
      const missionRewards = [
        ...missionStep('packs'),
        ...(pull.some(p => p.v >= 20) ? missionStep('big') : []),
      ];
      if (missionRewards.length) S.last.mission = missionRewards;
      const clearedQuota = checkQuotaProgress();
      save();
      packAnimating = true;
      $('btnOpen').disabled = true;
      try { await playPackOpening(pull, tier ? tier.art : null); }
      finally { packAnimating = false; }
      render(pull, cost, total);
      if (usedEvent) $('summary').innerHTML += `<div style="margin-top:8px;color:#67e8f9;font-weight:900">${usedEvent.ico} ${usedEvent.name} affected this pack.</div>`;
      if (S.event) $('summary').innerHTML += `<div style="margin-top:8px;color:#ffe066;font-weight:900">NEW EVENT: ${S.event.ico} ${S.event.name}<br><small>${S.event.desc}</small></div>`;
      if (clearedQuota) $('title').textContent = '✅ QUOTA CLEARED!';
    }

    function updateKissButton() {
      if (!S) return;
      const left = Math.max(0, Math.ceil(((S.kissReadyAt || 0) - Date.now()) / 1000));
      $('btnKiss').disabled = !!S.kissBoost || left > 0;
      $('btnKiss').textContent = S.kissBoost ? '💋 2× LUCK READY' : left > 0 ? `💋 KISS AGAIN IN ${left}s` : '💋 KISS THE PACK';
    }
    function kissPack() {
      if (!S || S.kissBoost || Date.now() < (S.kissReadyAt || 0)) return;
      S.kissBoost = true;
      S.kissReadyAt = Date.now() + upgradeMultiplier('kisscool') * 1000;
      save(); updateKissButton();
      $('title').textContent = '💋 PACK KISSED!';
      $('summary').innerHTML = 'Your next pack has <b>2× chase-card luck</b>. The luck is used when you open the pack.';
    }
    function updateShakeButton() {
      if (!S) return;
      const left = Math.max(0, Math.ceil(((S.shakeReadyAt || 0) - Date.now()) / 1000));
      $('btnShake').disabled = !!S.shakeBoost || left > 0;
      $('btnShake').textContent = S.shakeBoost ? `🫨 ${shakeLuckMult()}× LUCK READY • PSA 1` : left > 0 ? `🫨 SHAKE AGAIN IN ${left}s` : '🫨 SHAKE THE PACK';
    }
    function shakePack() {
      if (!S || S.shakeBoost || Date.now() < (S.shakeReadyAt || 0)) return;
      S.shakeBoost = true;
      S.shakeReadyAt = Date.now() + shakeCooldownSeconds() * 1000;
      save(); updateShakeButton();
      $('title').textContent = '🫨 PACK SHAKEN!';
      $('summary').innerHTML = `Your next pack has <b>${shakeLuckMult()}× chase-card luck</b>, but every card from it will receive <b>PSA 1</b> if graded.`;
    }

    function render(pull, cost, total) {
      const cardsEl = $('cards'); cardsEl.innerHTML = '';
      pull.forEach((p, i) => {
        const c = p.c, rk = RANK(c.r);
        const d = document.createElement('div');
        d.className = 'card r' + rk;
        d.style.animationDelay = (i * 0.14) + 's';
        const shownValue = p.grade ? p.grade.value : p.v;
        const big = shownValue >= 5;
        const binderFull = BINDER.length >= binderCapacity();
        const canKeep = !binderFull && (!paidMode() || S.bank >= shownValue);
        const keepText = binderFull ? `BINDER FULL • ${BINDER.length}/${binderCapacity()}` : canKeep ? 'KEEP IN BINDER' : 'NOT ENOUGH MONEY TO KEEP';
        const gradeText = p.grade ? `PSA ${p.grade.n} • ${money(p.v)} → ${money(p.grade.value)} (${p.grade.delta >= 0 ? '+' : ''}${money(p.grade.delta)})` : '';
        d.innerHTML = `${p.fake ? '<span class="tag">FAKE • $0</span>' : p.grade ? `<span class="tag">PSA ${p.grade.n}</span>` : p.shaken ? '<span class="tag">SHAKEN</span>' : p.slot === 'rev' ? '<span class="tag">REVERSE</span>' : ''}
          <span class="val ${big ? 'big' : p.slot === 'rev' ? 'rev' : ''}" style="animation-delay:${i * 0.14 + 0.3}s">${money(shownValue)}</span>
          <img src="${cardUrl(c)}" alt="${c.n}" loading="lazy">
          <div class="name">${c.n}</div>
          <div class="rarity">${c.r} • #${c.id.split('-')[1]}/${meta().official}</div>
          ${p.kept ? '<div class="grade-result">📚 SAVED IN BINDER</div>' : `${p.grade ? `<div class="grade-result">${gradeText}</div>` : `<button class="grade-btn" data-grade="${i}">${p.shaken ? 'GRADE WITH PSA • FORCED PSA 1' : 'GRADE WITH PSA'}</button>`}<button class="keep-btn" data-keep="${i}" ${canKeep ? '' : 'disabled'}>${keepText}</button>`}`;
        cardsEl.appendChild(d);
      });
      cardsEl.querySelectorAll('[data-grade]').forEach(b => b.onclick = () => gradeCard(+b.dataset.grade));
      cardsEl.querySelectorAll('[data-keep]').forEach(b => b.onclick = () => keepCard(+b.dataset.keep));
      const delta = +(total - cost).toFixed(2);
      const hit = pull.reduce((best, p) => p.v > best.v ? p : best, pull[0]);
      const purchaseStore = store((S.last && S.last.store) || selectedStore);
      const fakeWarning = S.last && S.last.fake ? '<div style="color:#ff6969;font-weight:1000">⚠️ FAKE PACK — EVERY CARD IS WORTH $0</div>' : '';
      $('summary').innerHTML = paidMode()
        ? `${purchaseStore.icon} ${purchaseStore.name} • ${S.last && S.last.randomTier ? `${S.last.randomTier} random ${meta().name} pack` : S.last && S.last.fromBox ? 'Box pack' : `Pack ${money(cost)}`} → cards sold ${money(total)} ${fakeWarning}<div class="delta ${delta >= 0 ? 'up' : 'down'}">${delta >= 0 ? '+' : ''}${money(delta)}</div><small style="opacity:.7">hit: ${hit.c.n} (${hit.c.r})</small>`
        : `Pack value ${money(total)} <small style="opacity:.7;display:block">hit: ${hit.c.n} (${hit.c.r})</small>`;
      if (S.last && S.last.mission && S.last.mission.length) $('summary').innerHTML += `<div style="margin-top:8px;color:#ffe066;font-weight:900">MISSION COMPLETE<br>${S.last.mission.join('<br>')}</div>`;
      $('title').textContent = delta >= 20 ? '💎 BIG HIT!' : '🔥 PACK OPENED!';
      $('hud').classList.remove('flash'); void $('hud').offsetWidth; $('hud').classList.add('flash');
      hud();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function hud() {
      const paid = paidMode();
      $('bank').textContent = paid ? money(S.bank) : 'SANDBOX';
      $('bank').classList.toggle('low', paid && S.bank < packCost() * 2);
      $('hudSub').textContent = `${S.mode === 'hard' ? '🔥 HARD • ' : ''}${meta().name} • ${store().icon} ${store().name} • ` + (paid ? `${S.packs} opened • ${currentBoxPacks()} box packs • spent ${money(S.spent)} • pulled ${money(S.earned)}` : `${S.packs} packs • pulled ${money(S.earned)}`);
      if (S.event) $('hudSub').textContent += ` • EVENT: ${S.event.ico} ${S.event.name} — ${S.event.desc}`;
      const ups = UPGRADES.filter(u => S.up[u.k]).map(u => u.ico + (u.tiers.length > 1 ? S.up[u.k] : '')).join(' ');
      const relicIcons = RELICS.filter(r => hasRelic(r.k)).map(r => r.ico).join('');
      $('hudUp').textContent = [ups, relicIcons].filter(Boolean).join(' ') || 'no upgrades or relics';
      $('btnShop').hidden = false;
      $('btnMissions').hidden = !paid;
      $('btnOpen').textContent = paid ? `BUY & OPEN • ${money(packCost())}` : 'OPEN PACK';
      if (paid && currentBoxPacks()) $('btnOpen').textContent = `OPEN BOX PACK • ${currentBoxPacks()} LEFT`;
      $('btnOpen').disabled = paid && !currentBoxPacks() && S.bank < packCost();
      $('btnMysteryShop').textContent = '🎲 MYSTERY PACK SHOP';
      $('btnPokemonShow').hidden = S.event?.k !== 'show';
      $('btnPokemonShow').textContent = `🎪 POKÉMON SHOW • ${paid ? money(packCost('show')) : 'FREE'} • 5× LUCK`;
      $('btnPokemonShow').disabled = paid && S.bank < packCost('show');
      $('btnBox').hidden = !paid;
      $('btnBox').textContent = `BUY 6-PACK BOX • ${money(boxCost())} (SAVE ${Math.round(boxDiscount() * 100)}%)`;
      $('btnBox').disabled = paid && S.bank < boxCost();
      updateKissButton();
      updateShakeButton();
      updateQuotaHud();
      if ($('mysteryShop').classList.contains('on')) renderMysteryShop();
      if (paid && !totalBoxPacks() && !S.mysteryBoxes.length && S.bank < Math.min(minPackCost(), ...Object.values(RANDOM_PACKS).map(t => packCost('black', true, t.price))) && !(ACTIVE_BATTLE && !ACTIVE_BATTLE.finished)) setTimeout(bust, 1200);
    }

    function renderMysteryShop() {
      const paid = paidMode();
      $('mysteryBank').textContent = paid ? money(S.bank) : 'SANDBOX • FREE';
      $('randomPackList').innerHTML = Object.entries(RANDOM_PACKS).map(([key, tier]) => {
        const cost = packCost(selectedStore, true, tier.price);
        const pool = tier.sets.map(id => SET_META[id].name).join(', ');
        return `<div class="mystery-item"><img src="${tier.art}" alt="${tier.name} sealed mystery booster"><div class="body"><b>${tier.name} Random Pack</b><small>${pool}</small><small>${tier.luck}× chase luck${tier.extraHit ? ' • +25% double-hit chance' : ''} • ${tier.fake ? `+${Math.round(tier.fake * 100)}% fake risk` : 'no added fake risk'} • store effects apply</small><button data-random="${key}" ${paid && S.bank < cost ? 'disabled' : ''}>${paid ? `BUY & OPEN • ${money(cost)}` : 'OPEN FREE'}</button></div></div>`;
      }).join('');
      $('randomPackList').querySelectorAll('[data-random]').forEach(b => b.onclick = () => openPack(b.dataset.random));
      $('btnMysteryBox').hidden = !paid;
      $('btnMysteryBox').textContent = `BUY SIX-PACK BOX • ${money(mysteryBoxCost())}`;
      $('btnMysteryBox').disabled = paid && S.bank < mysteryBoxCost();
      $('btnRevealMystery').hidden = !paid || !S.mysteryBoxes.length;
      $('btnRevealMystery').textContent = `REVEAL SEALED BOX • ${S.mysteryBoxes.length} LEFT`;
    }
    function openMysteryShop() {
      if (!S || S.ended) return;
      $('mysteryStatus').textContent = '';
      $('mysteryShop').classList.add('on');
      renderMysteryShop();
    }

    function buyBox() {
      if (!paidMode()) return;
      const cost = boxCost();
      if (S.bank < cost) return;
      S.bank = +(S.bank - cost).toFixed(2);
      S.spent = +(S.spent + cost).toFixed(2);
      S.boxes[selectedSet] = currentBoxPacks() + BOX_PACKS;
      S.boxStores = S.boxStores || {};
      S.boxStores[selectedSet] = [...(S.boxStores[selectedSet] || []), ...Array(BOX_PACKS).fill(selectedStore)];
      save(); hud();
      $('title').textContent = '📦 BOX PURCHASED!';
      $('summary').innerHTML = `You bought <b>${BOX_PACKS} ${meta().name} packs</b> from <b>${store().name}</b> for ${money(cost)}, saving ${Math.round(boxDiscount() * 100)}% compared with single packs.`;
    }

    function buyMysteryBox() {
      if (!paidMode() || packAnimating) return;
      const cost = mysteryBoxCost();
      if (S.bank < cost) return;
      const hiddenSet = rollMysterySet();
      S.bank = +(S.bank - cost).toFixed(2);
      S.spent = +(S.spent + cost).toFixed(2);
      S.mysteryBoxes.push({ set: hiddenSet, store: selectedStore });
      save(); hud();
      $('mysteryStatus').textContent = 'Box purchased and saved. Reveal it whenever you are ready.';
      $('title').textContent = '🎁 MYSTERY BOX PURCHASED!';
      $('summary').innerHTML = `Six packs from one secret set are sealed inside, each with 3× chase luck. Tap <b>REVEAL MYSTERY BOX</b> in the Mystery Pack Shop to find out what you got. Possible sets: Chaos Rising (50%), Sword & Shield (25%), Destined Rivals (15%), Phantasmal Flames (8%), or 151 (2%). Store perks and fake-pack risk apply when the packs are opened.`;
    }

    function revealMysteryBox() {
      if (!paidMode() || packAnimating || !S.mysteryBoxes.length) return;
      const sealed = S.mysteryBoxes.shift();
      const setId = SET_META[sealed.set] ? sealed.set : 'me04';
      const storeId = STORES[sealed.store] ? sealed.store : 'walmart';
      $('mysteryShop').classList.remove('on');
      activateSet(setId);
      S.set = selectedSet;
      S.last = null;
      S.boxes[setId] = (S.boxes[setId] || 0) + BOX_PACKS;
      S.boxStores[setId] = [...(S.boxStores[setId] || []), ...Array.from({ length: BOX_PACKS }, () => ({ store: storeId, luck: 3 }))];
      save();
      $('cards').innerHTML = '';
      $('title').textContent = `🎉 ${meta().name.toUpperCase()}!`;
      $('summary').innerHTML = `Your mystery box contains <b>${BOX_PACKS} ${meta().name} packs</b> from <b>${store(storeId).name}</b>! Open them with the OPEN BOX PACK button. Your money, upgrades, and other saved boxes are unchanged.`;
      hud();
    }

    function bust(reason = '💀 BUSTED') {
      clearInterval(quotaTimer);
      if (S.quota) saveQuotaRecord(S.quota.number);
      S.ended = true;
      show('over');
      $('overTitle').textContent = reason;
      $('overStats').innerHTML = [
        ['Packs opened', S.packs], ['Peak bankroll', money(S.peak)], ['Spent', money(S.spent)], ['Pulled', money(S.earned)],
        ['Quotas cleared', S.quota ? S.quota.cleared : 0], ['Highest quota', S.quota ? Math.max(S.quota.number, quotaRecord()) : quotaRecord()],
      ].map(([l, v]) => `<div class="stat"><b>${v}</b><small>${l}</small></div>`).join('');
      $('overBest').innerHTML = S.best ? `<p class="sub">Best pull</p><div class="card r${RANK(S.best.r)} best"><span class="val big">${money(S.best.v)}</span><img src="${cardUrl(S.best)}" alt=""><div class="name">${S.best.n}</div><div class="rarity">${S.best.r}</div></div>` : '';
      clearSave();
    }

    function shop() {
      const free = S.mode === 'sandbox';
      $('shopBank').textContent = free ? 'FREE' : money(S.bank);
      $('shopList').innerHTML = UPGRADES.map(u => {
        const t = S.up[u.k], max = t >= u.tiers.length, cost = max || free ? 0 : u.tiers[t];
        return `<div class="up ${max ? 'max' : ''}"><div class="ico">${u.ico}</div><div class="body"><b>${u.name} ${u.tiers.length > 1 ? `<span style="opacity:.6;font-weight:400">tier ${t}/${u.tiers.length}</span>` : ''}</b><small>${u.desc}</small><div class="tier">${max ? 'MAXED: ' + u.fx[t - 1] : (t ? 'now ' + u.fx[t - 1] + ' → ' : '') + 'next ' + u.fx[t]}</div></div>
          <button data-k="${u.k}" ${max || (!free && S.bank < cost) ? 'disabled' : ''}>${max ? '✓' : free ? 'FREE' : money(cost)}</button></div>`;
      }).join('');
      $('shopList').querySelectorAll('button').forEach(b => b.onclick = () => buy(b.dataset.k));
      $('shop').classList.add('on');
    }
    function buy(k) {
      const u = UPGRADES.find(u => u.k === k), t = S.up[k];
      const cost = S.mode === 'sandbox' ? 0 : u.tiers[t];
      if (t >= u.tiers.length || S.bank < cost) return;
      S.bank = +(S.bank - cost).toFixed(2); S.up[k]++;
      if (k === 'clock' && S.quota) S.quota.endsAt += 5000;
      save(); hud(); shop();
    }

    function rollRelicRarity() {
      let x = Math.random() * 100;
      for (const [key, rarity] of Object.entries(RELIC_RARITIES)) { x -= rarity.weight; if (x < 0) return key; }
      return 'common';
    }
    function refreshRelicOffers() {
      const offers = [];
      while (offers.length < 5) {
        const rarity = rollRelicRarity();
        let choices = RELICS.filter(r => !r.fusionOnly && r.rarity === rarity && !offers.includes(r.k));
        if (!choices.length) choices = RELICS.filter(r => !r.fusionOnly && !offers.includes(r.k));
        offers.push(rand(choices).k);
      }
      S.relicOffers = offers;
      S.relicRefreshAt = Date.now() + RELIC_REFRESH_MS;
      save();
    }
    function ensureRelicOffers() {
      if (!Array.isArray(S.relicOffers) || S.relicOffers.length !== 5 || Date.now() >= (S.relicRefreshAt || 0)) refreshRelicOffers();
    }
    function relicCard(r, owned, equipped) {
      const rarity = RELIC_RARITIES[r.rarity], free = S.mode === 'sandbox', full = equipped >= 3;
      const selected = FUSION_SELECTION.includes(r.k);
      return `<div class="up ${owned ? 'max' : ''}" style="border-color:${selected ? '#67e8f9' : rarity.color}"><div class="ico">${r.ico}</div><div class="body"><b>${r.name} <span style="color:${rarity.color};font-size:11px">${rarity.name}</span></b><small>${r.desc}</small><div class="tier">${owned ? 'EQUIPPED' : free ? 'FREE IN SANDBOX' : money(r.cost)}</div></div>${owned ? `<button data-fuse-select="${r.k}">${selected ? '✓ FUSION' : 'SELECT'}</button><button class="ghost" data-destroy-relic="${r.k}">DESTROY</button>` : `<button data-buy-relic="${r.k}" ${full || (!free && S.bank < r.cost) ? 'disabled' : ''}>${full ? '3/3 FULL' : free ? 'FREE' : money(r.cost)}</button>`}</div>`;
    }
    function relicShop() {
      ensureRelicOffers();
      const free = S.mode === 'sandbox', equipped = S.relics.length;
      $('relicBank').textContent = free ? 'FREE' : money(S.bank);
      $('relicCount').textContent = `${equipped}/3`;
      $('equippedRelics').innerHTML = S.relics.length ? S.relics.map(k => relicCard(RELICS.find(r => r.k === k), true, equipped)).join('') : '<p class="sub">No relics equipped.</p>';
      $('relicList').innerHTML = S.relicOffers.map(k => relicCard(RELICS.find(r => r.k === k), hasRelic(k), equipped)).join('');
      $('relicList').querySelectorAll('[data-buy-relic]').forEach(b => b.onclick = () => buyRelic(b.dataset.buyRelic));
      document.querySelectorAll('#relicShop [data-destroy-relic]').forEach(b => b.onclick = () => destroyRelic(b.dataset.destroyRelic));
      document.querySelectorAll('#relicShop [data-fuse-select]').forEach(b => b.onclick = () => selectRelicForFusion(b.dataset.fuseSelect));
      $('fusionStatus').textContent = FUSION_SELECTION.length ? `${FUSION_SELECTION.length}/2 selected: ${FUSION_SELECTION.map(k => RELICS.find(r => r.k === k).name).join(' + ')}` : 'Select 2 relics';
      $('btnFuseRelics').disabled = FUSION_SELECTION.length !== 2;
      $('relicShop').classList.add('on');
      updateRelicCountdown();
    }
    function updateRelicCountdown() {
      if (!S || !$('relicShop').classList.contains('on')) return;
      if (Date.now() >= (S.relicRefreshAt || 0)) { refreshRelicOffers(); relicShop(); return; }
      const seconds = Math.max(0, Math.ceil((S.relicRefreshAt - Date.now()) / 1000));
      $('relicRefresh').textContent = `0:${String(seconds).padStart(2, '0')}`;
    }
    function buyRelic(k) {
      const relic = RELICS.find(r => r.k === k), free = S.mode === 'sandbox';
      if (!relic || hasRelic(k) || S.relics.length >= 3 || (!free && S.bank < relic.cost)) return;
      if (!free) { S.bank = +(S.bank - relic.cost).toFixed(2); S.spent = +(S.spent + relic.cost).toFixed(2); }
      S.relics.push(k);
      recordRelicDiscovery(k);
      if (k === 'quotawatch' && S.quota) S.quota.endsAt += 5000;
      save(); hud(); relicShop();
    }
    function destroyRelic(k) {
      if (!hasRelic(k)) return;
      S.relics = S.relics.filter(id => id !== k);
      FUSION_SELECTION = FUSION_SELECTION.filter(id => id !== k);
      save(); hud(); relicShop();
    }
    function selectRelicForFusion(k) {
      if (!hasRelic(k)) return;
      FUSION_SELECTION = FUSION_SELECTION.includes(k) ? FUSION_SELECTION.filter(id => id !== k) : FUSION_SELECTION.length < 2 ? [...FUSION_SELECTION, k] : FUSION_SELECTION;
      relicShop();
    }
    function fuseRelics() {
      if (FUSION_SELECTION.length !== 2 || !FUSION_SELECTION.every(hasRelic)) return;
      const pool = RELICS.filter(r => r.fusionOnly && !hasRelic(r.k));
      const result = rand(pool.length ? pool : RELICS.filter(r => r.fusionOnly));
      S.relics = S.relics.filter(k => !FUSION_SELECTION.includes(k));
      S.relics.push(result.k);
      PROFILE.stats.fusions++; recordRelicDiscovery(result.k); saveProfile(); checkAchievements();
      FUSION_SELECTION = [];
      save(); hud(); relicShop();
      $('fusionStatus').innerHTML = `✨ Created <b>${result.ico} ${result.name}</b>!`;
    }

    function show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.toggle('on', s.id === id)); window.scrollTo(0, 0); }
    function start(mode, resume) {
      if (resume) activateSet(resume.set || 'me05');
      S = resume || newState(mode);
      activateStore(S.store || selectedStore || 'walmart');
      S.up = { ...Object.fromEntries(UPGRADES.map(u => [u.k, 0])), ...(S.up || {}) };
      S.relics = Array.isArray(S.relics) ? S.relics.map(k => k === 'detector' ? 'crown' : k === 'medal' ? 'idol' : k).filter((k, i, all) => RELICS.some(r => r.k === k) && all.indexOf(k) === i).slice(0, 3) : [];
      S.relicOffers = Array.isArray(S.relicOffers) ? S.relicOffers.filter(k => RELICS.some(r => r.k === k)).slice(0, 5) : [];
      S.relicRefreshAt = S.relicRefreshAt || 0;
      S.event = S.event && RANDOM_EVENTS.some(e => e.k === S.event.k) ? S.event : null;
      S.cardAuction = S.cardAuction && BINDER.some(item => item.uid === S.cardAuction.uid) ? S.cardAuction : null;
      S.auctionMessage = S.auctionMessage || '';
      S.boxes = { ...(S.boxes || {}) };
      S.boxStores = { ...(S.boxStores || {}) };
      S.mysteryBoxes = Array.isArray(S.mysteryBoxes) ? S.mysteryBoxes.filter(box => box && SET_META[box.set] && STORES[box.store]) : [];
      S.kissBoost = !!S.kissBoost;
      S.kissReadyAt = S.kissReadyAt || 0;
      S.shakeBoost = !!S.shakeBoost;
      S.shakeReadyAt = S.shakeReadyAt || 0;
      const oldMissions = S.missions || {};
      S.missions = { packs: 0, grades: 0, big: 0, ...oldMissions, claimed: { ...(oldMissions.claimed || {}) } };
      ensureQuota();
      show('game');
      $('cards').innerHTML = '';
      $('title').textContent = mode === 'hard' ? '🔥 HARD MODE' : mode === 'normal' ? '💸 NORMAL MODE' : mode === 'chill' ? '😌 CHILL MODE' : '🧪 SANDBOX';
      $('summary').innerHTML = mode === 'hard' ? `You have <b>${money(S.bank)}</b>. Reach <b>${money(S.quota.target)}</b> in 30 seconds. Packs cost 25% more and chase cards are harder to pull.` : mode === 'normal' ? `You have <b>${money(S.bank)}</b>. Packs cost <b>${money(packCost())}</b>. Every card auto-sells at market value. Don't go broke.` : mode === 'chill' ? `No quota and no timer. You have <b>${money(S.bank)}</b>; keep buying packs and upgrades, but don't go broke.` : 'Free packs and free upgrades forever. Values shown for fun.';
      hud();
      save(); startQuotaTimer();
      clearInterval(kissTimer); kissTimer = setInterval(() => { updateKissButton(); updateShakeButton(); }, 250);
      clearInterval(relicTimer); relicTimer = setInterval(updateRelicCountdown, 250);
      if (S.last) render(S.last.pull, S.last.cost, S.last.total);
    }
    function startNewGame(mode) {
      clearSave();
      BINDER = [];
      BATTLE_DECK = [];
      ACTIVE_BATTLE = null;
      battleQuotaPausedAt = 0;
      saveBinder();
      saveBattleDeck();
      start(mode);
    }
    function home() { show('home'); $('btnContinue').hidden = !load(); }

    const setButtons = target => {
      $(target).innerHTML = Object.entries(SET_META).map(([id, s]) => `<button class="set-choice" data-set="${id}"><img src="${s.art}" alt=""><b>${s.name}</b><small>${s.code} • ${money(s.price)} • ${SET_DATA[id].length} cards${id === '30th' ? ' • 5-card foil packs' : ''}${s.estimated ? ' • estimated card values' : ''}</small></button>`).join('');
    };
    const storeButtons = target => {
      $(target).innerHTML = Object.entries(STORES).filter(([id]) => id !== 'show').map(([id, s]) => `<button class="store-choice" data-store="${id}"><b>${s.icon} ${s.name}</b><small>${s.desc}</small></button>`).join('');
    };
    setButtons('setPicker'); setButtons('gameSetPicker');
    storeButtons('storePicker'); storeButtons('gameStorePicker');
    $('setPicker').querySelectorAll('button').forEach(b => b.onclick = () => activateSet(b.dataset.set));
    $('gameSetPicker').querySelectorAll('button').forEach(b => b.onclick = () => switchSet(b.dataset.set));
    document.querySelectorAll('.store-choice').forEach(b => b.onclick = () => { activateStore(b.dataset.store); $('storeSwitch').classList.remove('on'); });
    activateSet(selectedSet);
    activateStore(selectedStore);
    $('startBank').textContent = money(START_BANK);
    $('priceDate').textContent = PRICE_DATE;
    $('btnNormal').onclick = () => startNewGame('normal');
    $('btnChill').onclick = () => startNewGame('chill');
    $('btnHard').onclick = () => startNewGame('hard');
    $('btnSandbox').onclick = () => startNewGame('sandbox');
    $('btnContinue').onclick = () => { const s = load(); if (s) start(s.mode || 'normal', s); };
    $('btnOpen').onclick = () => openPack();
    $('btnMysteryShop').onclick = openMysteryShop;
    $('btnMysteryClose').onclick = () => $('mysteryShop').classList.remove('on');
    $('mysteryShop').onclick = e => { if (e.target === $('mysteryShop')) $('mysteryShop').classList.remove('on'); };
    $('btnPokemonShow').onclick = () => openPack(null, true);
    $('btnKiss').onclick = kissPack;
    $('btnShake').onclick = shakePack;
    $('btnBox').onclick = buyBox;
    $('btnMysteryBox').onclick = buyMysteryBox;
    $('btnRevealMystery').onclick = revealMysteryBox;
    $('btnSwitchSet').onclick = () => $('setSwitch').classList.add('on');
    $('btnSwitchStore').onclick = () => $('storeSwitch').classList.add('on');
    $('btnStoreClose').onclick = () => $('storeSwitch').classList.remove('on');
    $('storeSwitch').onclick = e => { if (e.target === $('storeSwitch')) $('storeSwitch').classList.remove('on'); };
    $('btnSetClose').onclick = () => $('setSwitch').classList.remove('on');
    $('setSwitch').onclick = e => { if (e.target === $('setSwitch')) $('setSwitch').classList.remove('on'); };
    $('btnHome').onclick = home;
    $('btnBinder').onclick = showBinder;
    $('btnBinderHome').onclick = showBinder;
    $('btnAchievementsHome').onclick = showAchievements;
    $('btnMuseumHome').onclick = showMuseum;
    $('btnAlbumsHome').onclick = showSetAlbums;
    $('btnAuctionHome').onclick = showAuctionHouse;
    $('btnBattle').onclick = showBattle;
    $('btnBattleHome').onclick = showBattle;
    $('btnAchievements').onclick = showAchievements;
    $('btnMuseum').onclick = showMuseum;
    $('btnAlbums').onclick = showSetAlbums;
    $('btnAuction').onclick = showAuctionHouse;
    $('btnAchievementsClose').onclick = () => $('achievements').classList.remove('on');
    $('achievements').onclick = e => { if (e.target === $('achievements')) $('achievements').classList.remove('on'); };
    $('btnMuseumClose').onclick = () => $('museum').classList.remove('on');
    $('museum').onclick = e => { if (e.target === $('museum')) $('museum').classList.remove('on'); };
    $('btnAlbumsClose').onclick = () => $('setAlbums').classList.remove('on');
    $('setAlbums').onclick = e => { if (e.target === $('setAlbums')) $('setAlbums').classList.remove('on'); };
    $('btnAuctionClose').onclick = () => $('auctionHouse').classList.remove('on');
    $('auctionHouse').onclick = e => { if (e.target === $('auctionHouse')) $('auctionHouse').classList.remove('on'); };
    $('btnBinderClose').onclick = closeBinder;
    $('binder').onclick = e => { if (e.target === $('binder')) closeBinder(); };
    $('btnBattleFromBinder').onclick = showBattle;
    $('btnBattleClose').onclick = closeBattle;
    $('battle').onclick = e => { if (e.target === $('battle')) closeBattle(); };
    $('btnZoomClose').onclick = closeCardZoom;
    $('cardZoom').onclick = e => { if (e.target === $('cardZoom')) closeCardZoom(); };
    $('btnTradeClose').onclick = () => ACTIVE_TRADE && ACTIVE_TRADE.resolved ? null : declineTrade();
    $('btnDeclineTrade').onclick = declineTrade;
    $('btnAcceptTrade').onclick = acceptTrade;
    $('btnTradeContinue').onclick = closeTrade;
    $('cardTrade').onclick = e => { if (e.target === $('cardTrade') && ACTIVE_TRADE && !ACTIVE_TRADE.resolved) declineTrade(); };
    document.querySelectorAll('.music-toggle').forEach(b => b.onclick = toggleMusic);
    document.querySelectorAll('.track-toggle').forEach(b => b.onclick = toggleTrack);
    $('btnShop').onclick = shop;
    $('btnShopClose').onclick = () => $('shop').classList.remove('on');
    $('shop').onclick = e => { if (e.target === $('shop')) $('shop').classList.remove('on'); };
    $('btnRelics').onclick = relicShop;
    $('btnFuseRelics').onclick = fuseRelics;
    $('btnRelicsClose').onclick = () => $('relicShop').classList.remove('on');
    $('relicShop').onclick = e => { if (e.target === $('relicShop')) $('relicShop').classList.remove('on'); };
    $('btnMissions').onclick = showMissions;
    $('btnMissionsClose').onclick = () => $('missions').classList.remove('on');
    $('missions').onclick = e => { if (e.target === $('missions')) $('missions').classList.remove('on'); };
    $('btnRestart').onclick = () => startNewGame(S && ['hard', 'chill'].includes(S.mode) ? S.mode : 'normal');
    $('btnOverHome').onclick = home;
    home();
  </script>
</body>
</html>
'''.replace("__DATA__", data).replace("__DATE__", "2026-09-16")
out_path = os.path.join(here, "index.html")
open(out_path, "w", encoding="utf-8").write(html)
print(len(html))
