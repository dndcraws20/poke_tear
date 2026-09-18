import json, os
here = os.path.dirname(os.path.abspath(__file__))
sets = {}
for set_id in ("me04", "me05", "sv10", "me02", "sv03.5"):
    cards = json.load(open(os.path.join(here, f"{set_id}-cards.json"), encoding="utf-8"))
    series_id = "".join(ch for ch in set_id if ch.isalpha())
    pre = f"https://assets.tcgdex.net/en/{series_id}/{set_id}/"
    sets[set_id] = [
        {"id": c["id"], "n": c["n"], "r": c["r"], "img": c["img"][len(pre):] if c["img"].startswith(pre) else c["img"], "p": c["p"], "pr": c["pr"], "ph": c["ph"]}
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
    @keyframes pop { from { opacity: 0; transform: scale(.7) translateY(25px); } to { opacity: 1; transform: none; } }
    @keyframes glow { from { box-shadow: 0 0 18px #ff4fd088; } to { box-shadow: 0 0 44px #ff4fd0ee, 0 0 80px #ff9800aa; } }
    @keyframes flash { 0% { background: #22c55e66; } 100% { background: #120c1c; } }
    .flash { animation: flash .8s; }
    @media (min-width: 700px) { .cards { grid-template-columns: repeat(5, 1fr); } .overlay { align-items: center; } .sheet { border-radius: 20px; } }
  </style>
</head>
<body>
  <div class="wrap">

    <section id="home" class="screen on">
      <h1>🎴 Pokémon Pack Opener</h1>
      <p class="sub" id="setTitle"></p>
      <img class="pack" id="packArt" src="pack.jpg" alt="Selected Pokémon set">
      <div class="set-picker" id="setPicker"></div>
      <div class="modes">
        <button class="mode" id="btnNormal"><b>💸 Normal</b><small>Start with <span id="startBank"></span>. Packs cost real money, cards sell at live market value. Buy upgrades, don't go broke.</small></button>
        <button class="mode" id="btnChill"><b>😌 Chill</b><small>No quota or timer. Packs and upgrades still cost money, and the run ends if you go broke.</small></button>
        <button class="mode" id="btnHard"><b>🔥 Hard</b><small>30-second quotas, faster quota growth, packs cost 25% more, and valuable cards are harder to pull. Losing ends the run.</small></button>
        <button class="mode" id="btnSandbox"><b>🧪 Sandbox</b><small>Free packs and free upgrades forever. Still shows what every card is worth.</small></button>
      </div>
      <button class="ghost" id="btnContinue" hidden>▶ Continue run</button>
      <button class="ghost" id="btnBinderHome">📚 Binder</button>
      <button class="ghost music-toggle">🔇 Music: Off</button>
      <button class="ghost track-toggle">🎼 Track: Electronic</button>
      <p class="note">Prices: TCGplayer market (USD), updated <span id="priceDate"></span>.</p>
    </section>

    <section id="game" class="screen">
      <div class="hud" id="hud">
        <div><div class="bank" id="bank"></div><small id="hudSub"></small></div>
        <div class="r"><button class="ghost" id="btnMissions" style="margin:0;padding:10px 12px">🎯 Missions</button><button class="ghost" id="btnShop" style="margin:0;padding:10px 12px">🛒 Upgrades</button><small id="hudUp"></small></div>
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
        <button class="ghost" id="btnBox">BUY 6-PACK BOX</button>
        <button class="ghost music-toggle">🔇 MUSIC: OFF</button>
        <button class="ghost track-toggle">🎼 ELECTRONIC</button>
        <button class="ghost" id="btnBinder">📚 BINDER</button>
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

  <div class="overlay" id="setSwitch">
    <div class="sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">🎴 Switch set</h2><button class="ghost" id="btnSetClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" style="font-size:13px">Your bankroll, upgrades, stats, and save stay the same.</p>
      <div class="set-picker" id="gameSetPicker"></div>
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
    <div class="sheet">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">📚 Card Binder</h2><button class="ghost" id="btnBinderClose" style="margin:0;padding:8px 14px">✕</button></div>
      <p class="sub" style="font-size:13px">Kept cards gain 20% value after one minute. Selling adds the money to your active Normal, Hard, or Chill run.</p>
      <div class="cards" id="binderList"></div>
    </div>
  </div>

  <script>
    // TCGplayer market prices: p = normal, pr = reverse holo, ph = holofoil. Source: TCGdex.
    const SET_DATA = __DATA__;
    const SET_META = {
      me04: { name: 'Chaos Rising', series: 'Mega Evolution', code: 'ME04', official: 86, art: 'chaos-rising-pack.png', price: 9.99, valueMult: 1.2 },
      me05: { name: 'Pitch Black', series: 'Mega Evolution', code: 'ME05', official: 84, art: 'pack.jpg', price: 4.99, valueMult: 1 },
      sv10: { name: 'Destined Rivals', series: 'Scarlet & Violet', code: 'SV10', official: 182, art: 'destined-rivals-pack.jpg', price: 15, valueMult: 1.3 },
      me02: { name: 'Phantasmal Flames', series: 'Mega Evolution', code: 'ME02', official: 94, art: 'phantasmal-flames-pack.png', price: 22.5, valueMult: 1.6 },
      'sv03.5': { name: '151', series: 'Scarlet & Violet', code: 'SV03.5', official: 165, art: 'pokemon-151-pack.png', price: 35, valueMult: 2 },
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
    const BOX_PACKS = 6;
    const BOX_DISCOUNT = .10;
    const SAVE_KEY = 'poke-tear-run-v2';
    const QUOTA_RECORD_KEY = 'poke-tear-quota-record-v1';
    const BINDER_KEY = 'poke-tear-binder-v1';
    const BINDER_GROW_MS = 60 * 1000;

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
    const RANK = r => { r = r.toLowerCase(); if (r === 'common') return 0; if (r === 'uncommon') return 1; if (r.includes('special') || r.includes('hyper')) return 4; if (r.includes('ultra') || r.includes('illustration')) return 3; return 2; };
    let selectedSet = 'me05';
    let SET = [];
    let BY = {};

    // Hit-slot base weights (roughly real pull rates). Luck multiplies the chase tiers.
    const HIT_W = { 'Rare': 55, 'Double rare': 22, 'Illustration rare': 10, 'Ultra Rare': 5, 'Special illustration rare': 2, 'Mega Hyper Rare': 0.4, 'Hyper rare': 0.4 };
    const CHASE = new Set(['Illustration rare', 'Ultra Rare', 'Special illustration rare', 'Mega Hyper Rare', 'Hyper rare']);

    const UPGRADES = [
      { k: 'luck',  ico: '🍀', name: 'Lucky Charm', desc: 'Boosts the odds of the hit slot being an Illustration / Ultra / Special / Hyper rare.', tiers: [15, 40, 100], fx: ['1.6×', '2.6×', '4.5×'], mult: [1, 1.6, 2.6, 4.5] },
      { k: 'bulk',  ico: '📦', name: 'Bulk Baron', desc: 'Commons, uncommons, rares and double rares sell for a multiple of market price.', tiers: [12, 30, 75], fx: ['2×', '3×', '5×'], mult: [1, 2, 3, 5] },
      { k: 'rev',   ico: '✨', name: 'Reverse Radar', desc: 'Every pack gets a third reverse-holo slot (11 cards per pack).', tiers: [20], fx: ['+1 slot'], mult: [0, 1] },
      { k: 'whole', ico: '🏷️', name: 'Wholesale', desc: 'Packs cost less.', tiers: [25, 60], fx: ['-10%', '-20%'], mult: [1, 0.9, 0.8] },
      { k: 'mint',  ico: '🧤', name: 'Mint Condition Kit', desc: 'Careful handling raises every PSA result, up to PSA 10.', tiers: [35, 90], fx: ['+1 PSA grade', '+2 PSA grades'], mult: [0, 1, 2] },
      { k: 'shine', ico: '🌟', name: 'Holo Amplifier', desc: 'Reverse-holo and hit cards sell for more.', tiers: [30, 80], fx: ['1.25× value', '1.6× value'], mult: [1, 1.25, 1.6] },
      { k: 'bonus', ico: '🎁', name: 'Bonus Hit', desc: 'Adds to the natural 10% chance for a second hit card.', tiers: [50, 140], fx: ['25% total chance', '40% total chance'], mult: [0, .15, .3] },
      { k: 'clock', ico: '⏱️', name: 'Time Bank', desc: 'Adds more time to every quota, including the current one.', tiers: [25, 70], fx: ['+5 seconds', '+10 seconds'], mult: [0, 5, 10] },
      { k: 'cover', ico: '🛡️', name: 'PSA Insurance', desc: 'PSA 2–4 cards keep a minimum percentage of their ungraded value. PSA 1 is still worth one cent.', tiers: [30, 85], fx: ['50% minimum', '75% minimum'], mult: [0, .5, .75] },
      { k: 'jackpot', ico: '💰', name: 'Big Hit Bonus', desc: 'Cards worth at least $20 receive an extra value multiplier.', tiers: [45, 120], fx: ['1.25× value', '1.5× value'], mult: [1, 1.25, 1.5] },
    ];
    const MISSIONS = [
      { k: 'packs', ico: '🎴', name: 'Pack Rookie', desc: 'Open 3 packs in this run.', goal: 3, reward: 10 },
      { k: 'grades', ico: '🏅', name: 'PSA Apprentice', desc: 'Grade 2 cards in this run.', goal: 2, reward: 12 },
      { k: 'big', ico: '💎', name: 'Treasure Hunter', desc: 'Pull a card worth at least $20.', goal: 1, reward: 15 },
    ];

    let S = null; // run state
    let quotaTimer = null;
    let binderTimer = null;
    let audioCtx = null, musicTimer = null, musicOn = false, musicStyle = 'electronic', musicStep = 0, nextMusicStep = 0;
    const $ = id => document.getElementById(id);
    const money = v => (v < 0 ? '-' : '') + '$' + Math.abs(v).toFixed(2);
    const rand = a => a[Math.floor(Math.random() * a.length)];
    const loadBinder = () => { try { return JSON.parse(localStorage.getItem(BINDER_KEY)) || []; } catch (e) { return []; } };
    const saveBinder = () => { try { localStorage.setItem(BINDER_KEY, JSON.stringify(BINDER)); } catch (e) {} };
    let BINDER = loadBinder();

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
    const paidMode = () => S && !S.ended && (S.mode === 'normal' || S.mode === 'hard' || S.mode === 'chill');
    const quotaMode = () => S && (S.mode === 'normal' || S.mode === 'hard');
    const quotaStart = () => S.mode === 'hard' ? HARD_QUOTA_START : QUOTA_START;
    const quotaMult = () => S.mode === 'hard' ? HARD_QUOTA_MULT : QUOTA_MULT;
    const quotaSeconds = () => (S.mode === 'hard' ? HARD_QUOTA_SECONDS : QUOTA_SECONDS) + UPGRADES[7].mult[S.up.clock];
    const cardUrl = c => { const id = c.id.split('-')[0], series = (id.match(/^[a-z]+/) || [''])[0]; return `https://assets.tcgdex.net/en/${series}/${id}/${c.img}/high.webp`; };
    function activateSet(id) {
      selectedSet = SET_DATA[id] ? id : 'me05';
      SET = SET_DATA[selectedSet]; BY = {};
      SET.forEach(c => (BY[c.r] = BY[c.r] || []).push(c));
      document.querySelectorAll('.set-choice').forEach(b => b.classList.toggle('on', b.dataset.set === selectedSet));
      $('setTitle').textContent = `${meta().series} — ${meta().name} • ${meta().code}`;
      $('packArt').src = meta().art; $('packArt').alt = `${meta().name} pack`;
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
      return { mode, set: selectedSet, bank: START_BANK, packs: 0, spent: 0, earned: 0, peak: START_BANK, best: null, up: { luck: 0, bulk: 0, rev: 0, whole: 0, mint: 0, shine: 0, bonus: 0, clock: 0, cover: 0, jackpot: 0 }, boxes: {}, missions: { packs: 0, grades: 0, big: 0, claimed: {} }, last: null,
        quota: mode === 'normal' || mode === 'hard' ? { number: 1, cleared: 0, target: mode === 'hard' ? HARD_QUOTA_START : QUOTA_START, endsAt: Date.now() + (mode === 'hard' ? HARD_QUOTA_SECONDS : QUOTA_SECONDS) * 1000 } : null };
    }
    function save() { try { if (paidMode()) localStorage.setItem(SAVE_KEY, JSON.stringify(S)); } catch (e) {} }
    function load() { try { return JSON.parse(localStorage.getItem(SAVE_KEY)); } catch (e) { return null; } }
    function clearSave() { try { localStorage.removeItem(SAVE_KEY); } catch (e) {} }
    function quotaRecord() { try { return +(localStorage.getItem(QUOTA_RECORD_KEY) || 0); } catch (e) { return 0; } }
    function saveQuotaRecord(n) { try { localStorage.setItem(QUOTA_RECORD_KEY, String(Math.max(n, quotaRecord()))); } catch (e) {} }

    const binderValue = item => +(item.value * (Date.now() - item.keptAt >= BINDER_GROW_MS ? 1.2 : 1)).toFixed(2);
    function keepCard(index) {
      const p = S.last && S.last.pull[index];
      if (!p || p.kept) return;
      const value = p.grade ? p.grade.value : p.v;
      if (paidMode() && S.bank < value) return;
      if (paidMode()) {
        S.bank = +(S.bank - value).toFixed(2);
        S.earned = +(S.earned - value).toFixed(2);
      }
      S.last.total = +(S.last.total - value).toFixed(2);
      p.kept = true;
      BINDER.unshift({ uid: `${Date.now()}-${Math.random()}`, c: p.c, value, keptAt: Date.now(), grade: p.grade ? p.grade.n : null, set: selectedSet });
      saveBinder(); save();
      render(S.last.pull, S.last.cost, S.last.total);
    }
    function sellBinder(uid) {
      if (!paidMode()) return;
      const index = BINDER.findIndex(item => item.uid === uid);
      if (index < 0) return;
      const value = binderValue(BINDER[index]);
      BINDER.splice(index, 1);
      S.bank = +(S.bank + value).toFixed(2);
      S.earned = +(S.earned + value).toFixed(2);
      saveBinder();
      const clearedQuota = checkQuotaProgress();
      save(); hud(); renderBinder();
      if (clearedQuota) $('title').textContent = '✅ QUOTA CLEARED!';
    }
    function renderBinder() {
      const canSell = paidMode();
      $('binderList').innerHTML = BINDER.length ? BINDER.map(item => {
        const grown = Date.now() - item.keptAt >= BINDER_GROW_MS;
        const left = Math.max(0, Math.ceil((BINDER_GROW_MS - (Date.now() - item.keptAt)) / 1000));
        return `<div class="card r${RANK(item.c.r)}"><span class="val ${binderValue(item) >= 5 ? 'big' : ''}">${money(binderValue(item))}</span>${item.grade ? `<span class="tag">PSA ${item.grade}</span>` : ''}<img src="${cardUrl(item.c)}" alt="${item.c.n}" loading="lazy"><div class="name">${item.c.n}</div><div class="rarity">${item.c.r}</div><div class="grade-result">${grown ? '📈 20% growth unlocked' : `📈 +20% in ${left}s`}</div><button class="grade-btn" data-sell="${item.uid}" ${canSell ? '' : 'disabled'}>${canSell ? `SELL • ${money(binderValue(item))}` : 'START A MONEY RUN TO SELL'}</button></div>`;
      }).join('') : '<p class="sub" style="grid-column:1/-1">Your binder is empty. Open a pack and press KEEP IN BINDER on any card.</p>';
      $('binderList').querySelectorAll('[data-sell]').forEach(b => b.onclick = () => sellBinder(b.dataset.sell));
    }
    function showBinder() {
      clearInterval(binderTimer);
      renderBinder();
      $('binder').classList.add('on');
      binderTimer = setInterval(() => { if ($('binder').classList.contains('on')) renderBinder(); }, 1000);
    }
    function closeBinder() { clearInterval(binderTimer); $('binder').classList.remove('on'); }

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
    function updateQuotaHud() {
      const active = quotaMode() && S.quota;
      $('quotaBox').hidden = !active;
      if (!active) return;
      const left = Math.max(0, S.quota.endsAt - Date.now());
      const seconds = Math.ceil(left / 1000);
      $('quotaLabel').textContent = `QUOTA ${S.quota.number} • ${money(S.quota.target)}`;
      $('quotaTime').textContent = `0:${String(seconds).padStart(2, '0')}`;
      $('quotaTime').classList.toggle('danger', seconds <= 10);
      $('quotaFill').style.width = Math.min(100, S.bank / S.quota.target * 100) + '%';
      $('quotaProgress').textContent = `${money(S.bank)} / ${money(S.quota.target)} • ${S.quota.cleared} cleared • highest quota ${Math.max(S.quota.number, quotaRecord())}`;
    }
    function advanceQuota() {
      S.quota.cleared++;
      S.quota.number++;
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

    const packCost = () => paidMode() ? +(meta().price * UPGRADES[3].mult[S.up.whole] * (S.mode === 'hard' ? HARD_PACK_MULT : 1)).toFixed(2) : 0;
    const boxCost = () => +(packCost() * BOX_PACKS * (1 - BOX_DISCOUNT)).toFixed(2);
    const currentBoxPacks = () => (S.boxes && S.boxes[selectedSet]) || 0;
    const totalBoxPacks = () => Object.values(S.boxes || {}).reduce((sum, n) => sum + n, 0);
    const minPackCost = () => Math.min(...Object.values(SET_META).map(s => +(s.price * UPGRADES[3].mult[S.up.whole] * (S.mode === 'hard' ? HARD_PACK_MULT : 1)).toFixed(2)));
    const bulkMult = () => UPGRADES[1].mult[S.up.bulk];
    const luckMult = () => UPGRADES[0].mult[S.up.luck];

    function rollHitRarity() {
      const entries = Object.entries(HIT_W).filter(([r]) => BY[r] && BY[r].length).map(([r, w]) => [r, CHASE.has(r) ? w * luckMult() * (S.mode === 'hard' ? HARD_CHASE_MULT : 1) : w]);
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
      if (slot === 'rev' || slot === 'hit') v *= UPGRADES[5].mult[S.up.shine];
      if (v >= 20) v *= UPGRADES[9].mult[S.up.jackpot];
      return +v.toFixed(2);
    }

    function rollGrade() {
      let x = Math.random() * 100;
      for (const result of GRADES) {
        x -= result.chance;
        if (x < 0) return GRADES.find(g => g.grade === Math.min(10, result.grade + S.up.mint));
      }
      return GRADES[GRADES.length - 1];
    }

    function gradeCard(index) {
      const p = S.last && S.last.pull[index];
      if (!p || p.grade || p.kept) return;
      const result = rollGrade();
      let value = result.grade === 1 ? .01 : +(p.v * result.mult).toFixed(2);
      if (result.grade >= 2 && result.grade <= 4) value = Math.max(value, +(p.v * UPGRADES[8].mult[S.up.cover]).toFixed(2));
      const delta = +(value - p.v).toFixed(2);
      p.grade = { n: result.grade, mult: result.mult, value, delta };
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

    function pullPack() {
      const used = new Set();
      const take = (pool, slot) => { let c, n = 0; do { c = rand(pool); } while (used.has(c.id) && n++ < 50); used.add(c.id); return { c, slot, v: 0 }; };
      const base = [...BY['Common'], ...BY['Uncommon'], ...BY['Rare']];
      const pull = [];
      for (let i = 0; i < 4; i++) pull.push(take(BY['Common'], 'base'));
      for (let i = 0; i < 3; i++) pull.push(take(BY['Uncommon'], 'base'));
      for (let i = 0; i < 2 + S.up.rev; i++) pull.push(take(base, 'rev'));
      pull.push(take(BY[rollHitRarity()], 'hit'));
      if (Math.random() < DOUBLE_HIT_CHANCE + UPGRADES[6].mult[S.up.bonus]) pull.push(take(BY[rollHitRarity()], 'hit'));
      for (let i = pull.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [pull[i], pull[j]] = [pull[j], pull[i]];
      }
      pull.forEach(p => p.v = cardValue(p.c, p.slot));
      return pull;
    }

    function openPack() {
      const fromBox = currentBoxPacks() > 0;
      const cost = fromBox ? 0 : packCost();
      if (paidMode() && S.bank < cost) return;
      if (fromBox) S.boxes[selectedSet]--;
      const pull = pullPack();
      const total = +pull.reduce((a, p) => a + p.v, 0).toFixed(2);
      S.bank = +(S.bank - cost + total).toFixed(2);
      S.packs++; S.spent = +(S.spent + cost).toFixed(2); S.earned = +(S.earned + total).toFixed(2);
      S.peak = Math.max(S.peak, S.bank);
      const hit = pull.reduce((a, p) => p.v > a.v ? p : a, pull[0]);
      if (!S.best || hit.v > S.best.v) S.best = { id: hit.c.id, n: hit.c.n, r: hit.c.r, v: hit.v, img: hit.c.img };
      S.last = { pull, cost, total };
      S.last.fromBox = fromBox;
      const missionRewards = [
        ...missionStep('packs'),
        ...(pull.some(p => p.v >= 20) ? missionStep('big') : []),
      ];
      if (missionRewards.length) S.last.mission = missionRewards;
      const clearedQuota = checkQuotaProgress();
      save();
      render(pull, cost, total);
      if (clearedQuota) $('title').textContent = '✅ QUOTA CLEARED!';
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
        const canKeep = !paidMode() || S.bank >= shownValue;
        const gradeText = p.grade ? `PSA ${p.grade.n} • ${money(p.v)} → ${money(p.grade.value)} (${p.grade.delta >= 0 ? '+' : ''}${money(p.grade.delta)})` : '';
        d.innerHTML = `${p.grade ? `<span class="tag">PSA ${p.grade.n}</span>` : p.slot === 'rev' ? '<span class="tag">REVERSE</span>' : ''}
          <span class="val ${big ? 'big' : p.slot === 'rev' ? 'rev' : ''}" style="animation-delay:${i * 0.14 + 0.3}s">${money(shownValue)}</span>
          <img src="${cardUrl(c)}" alt="${c.n}" loading="lazy">
          <div class="name">${c.n}</div>
          <div class="rarity">${c.r} • #${c.id.split('-')[1]}/${meta().official}</div>
          ${p.kept ? '<div class="grade-result">📚 SAVED IN BINDER</div>' : `${p.grade ? `<div class="grade-result">${gradeText}</div>` : `<button class="grade-btn" data-grade="${i}">GRADE WITH PSA</button>`}<button class="keep-btn" data-keep="${i}" ${canKeep ? '' : 'disabled'}>${canKeep ? 'KEEP IN BINDER' : 'NOT ENOUGH MONEY TO KEEP'}</button>`}`;
        cardsEl.appendChild(d);
      });
      cardsEl.querySelectorAll('[data-grade]').forEach(b => b.onclick = () => gradeCard(+b.dataset.grade));
      cardsEl.querySelectorAll('[data-keep]').forEach(b => b.onclick = () => keepCard(+b.dataset.keep));
      const delta = +(total - cost).toFixed(2);
      const hit = pull.reduce((best, p) => p.v > best.v ? p : best, pull[0]);
      $('summary').innerHTML = paidMode()
        ? `${S.last && S.last.fromBox ? 'Box pack' : `Pack ${money(cost)}`} → cards sold ${money(total)} <div class="delta ${delta >= 0 ? 'up' : 'down'}">${delta >= 0 ? '+' : ''}${money(delta)}</div><small style="opacity:.7">hit: ${hit.c.n} (${hit.c.r})</small>`
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
      $('hudSub').textContent = `${S.mode === 'hard' ? '🔥 HARD • ' : ''}${meta().name} • ` + (paid ? `${S.packs} opened • ${currentBoxPacks()} box packs • spent ${money(S.spent)} • pulled ${money(S.earned)}` : `${S.packs} packs • pulled ${money(S.earned)}`);
      const ups = UPGRADES.filter(u => S.up[u.k]).map(u => u.ico + (u.tiers.length > 1 ? S.up[u.k] : '')).join(' ');
      $('hudUp').textContent = ups || 'no upgrades';
      $('btnShop').hidden = false;
      $('btnMissions').hidden = !paid;
      $('btnOpen').textContent = paid ? `BUY & OPEN • ${money(packCost())}` : 'OPEN PACK';
      if (paid && currentBoxPacks()) $('btnOpen').textContent = `OPEN BOX PACK • ${currentBoxPacks()} LEFT`;
      $('btnOpen').disabled = paid && !currentBoxPacks() && S.bank < packCost();
      $('btnBox').hidden = !paid;
      $('btnBox').textContent = `BUY 6-PACK BOX • ${money(boxCost())} (SAVE 10%)`;
      $('btnBox').disabled = paid && S.bank < boxCost();
      updateQuotaHud();
      if (paid && !totalBoxPacks() && S.bank < minPackCost()) setTimeout(bust, 1200);
    }

    function buyBox() {
      if (!paidMode()) return;
      const cost = boxCost();
      if (S.bank < cost) return;
      S.bank = +(S.bank - cost).toFixed(2);
      S.spent = +(S.spent + cost).toFixed(2);
      S.boxes[selectedSet] = currentBoxPacks() + BOX_PACKS;
      save(); hud();
      $('title').textContent = '📦 BOX PURCHASED!';
      $('summary').innerHTML = `You bought <b>${BOX_PACKS} ${meta().name} packs</b> for ${money(cost)}, saving 10% compared with single packs.`;
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

    function show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.toggle('on', s.id === id)); window.scrollTo(0, 0); }
    function start(mode, resume) {
      if (resume) activateSet(resume.set || 'me05');
      S = resume || newState(mode);
      S.up = { luck: 0, bulk: 0, rev: 0, whole: 0, mint: 0, shine: 0, bonus: 0, clock: 0, cover: 0, jackpot: 0, ...(S.up || {}) };
      S.boxes = { ...(S.boxes || {}) };
      const oldMissions = S.missions || {};
      S.missions = { packs: 0, grades: 0, big: 0, ...oldMissions, claimed: { ...(oldMissions.claimed || {}) } };
      ensureQuota();
      show('game');
      $('cards').innerHTML = '';
      $('title').textContent = mode === 'hard' ? '🔥 HARD MODE' : mode === 'normal' ? '💸 NORMAL MODE' : mode === 'chill' ? '😌 CHILL MODE' : '🧪 SANDBOX';
      $('summary').innerHTML = mode === 'hard' ? `You have <b>${money(S.bank)}</b>. Reach <b>${money(S.quota.target)}</b> in 30 seconds. Packs cost 25% more and chase cards are harder to pull.` : mode === 'normal' ? `You have <b>${money(S.bank)}</b>. Packs cost <b>${money(packCost())}</b>. Every card auto-sells at market value. Don't go broke.` : mode === 'chill' ? `No quota and no timer. You have <b>${money(S.bank)}</b>; keep buying packs and upgrades, but don't go broke.` : 'Free packs and free upgrades forever. Values shown for fun.';
      hud();
      save(); startQuotaTimer();
      if (S.last) render(S.last.pull, S.last.cost, S.last.total);
    }
    function home() { show('home'); $('btnContinue').hidden = !load(); }

    const setButtons = target => {
      $(target).innerHTML = Object.entries(SET_META).map(([id, s]) => `<button class="set-choice" data-set="${id}"><img src="${s.art}" alt=""><b>${s.name}</b><small>${s.code} • ${money(s.price)} • ${SET_DATA[id].length} cards</small></button>`).join('');
    };
    setButtons('setPicker'); setButtons('gameSetPicker');
    $('setPicker').querySelectorAll('button').forEach(b => b.onclick = () => activateSet(b.dataset.set));
    $('gameSetPicker').querySelectorAll('button').forEach(b => b.onclick = () => switchSet(b.dataset.set));
    activateSet(selectedSet);
    $('startBank').textContent = money(START_BANK);
    $('priceDate').textContent = PRICE_DATE;
    $('btnNormal').onclick = () => { clearSave(); start('normal'); };
    $('btnChill').onclick = () => { clearSave(); start('chill'); };
    $('btnHard').onclick = () => { clearSave(); start('hard'); };
    $('btnSandbox').onclick = () => start('sandbox');
    $('btnContinue').onclick = () => { const s = load(); if (s) start(s.mode || 'normal', s); };
    $('btnOpen').onclick = openPack;
    $('btnBox').onclick = buyBox;
    $('btnSwitchSet').onclick = () => $('setSwitch').classList.add('on');
    $('btnSetClose').onclick = () => $('setSwitch').classList.remove('on');
    $('setSwitch').onclick = e => { if (e.target === $('setSwitch')) $('setSwitch').classList.remove('on'); };
    $('btnHome').onclick = home;
    $('btnBinder').onclick = showBinder;
    $('btnBinderHome').onclick = showBinder;
    $('btnBinderClose').onclick = closeBinder;
    $('binder').onclick = e => { if (e.target === $('binder')) closeBinder(); };
    document.querySelectorAll('.music-toggle').forEach(b => b.onclick = toggleMusic);
    document.querySelectorAll('.track-toggle').forEach(b => b.onclick = toggleTrack);
    $('btnShop').onclick = shop;
    $('btnShopClose').onclick = () => $('shop').classList.remove('on');
    $('shop').onclick = e => { if (e.target === $('shop')) $('shop').classList.remove('on'); };
    $('btnMissions').onclick = showMissions;
    $('btnMissionsClose').onclick = () => $('missions').classList.remove('on');
    $('missions').onclick = e => { if (e.target === $('missions')) $('missions').classList.remove('on'); };
    $('btnRestart').onclick = () => start(S && ['hard', 'chill'].includes(S.mode) ? S.mode : 'normal');
    $('btnOverHome').onclick = home;
    home();
  </script>
</body>
</html>
'''.replace("__DATA__", data).replace("__DATE__", "2026-09-16")
out_path = os.path.join(here, "index.html")
open(out_path, "w", encoding="utf-8").write(html)
print(len(html))
