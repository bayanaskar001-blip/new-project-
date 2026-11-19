import React from 'react';
import {
  AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig,
} from 'remotion';
import words from './thedop_words.json';
import vipWords from './thedop_vip_words.json';

// ---- Бренд ----
const RED = '#FF2338';
const BG = '#0A0A0D';
const WHITE = '#F4F1EE';
const FONT = "'Inter Display', 'Inter', sans-serif";
const FPS = 30;
const VOICE_OFFSET = 0.3; // озвучка стартует через 0.3 сек
// Вставка блока VIP-комнат: всё, что после INS, сдвигается на VIP_DUR
const INS = 8.2;
const VIP_DUR = 5.6;
const END = 24.4; // конец ролика (до вставки)
const sh = (t: number, isEnd = false) => ((isEnd ? t > INS : t >= INS) ? t + VIP_DUR : t);
const f = (sec: number) => Math.round(sec * FPS);
export const DURATION = f(sh(END));
const vf = (voiceSec: number) => f(sh(voiceSec + VOICE_OFFSET));

// ---- Сцены (секунды от начала ролика) ----
// segs — отрезки исходного видео [начало, конец] в секундах
type Scene = {from: number; to: number; kind: string; segs: [number, number][]; tag?: string; zoom?: 'in' | 'out'; origin?: string};
const SCENES: Scene[] = [
  {from: 0, to: 2.1, kind: 'clip', segs: [[19.9, 22.0]], zoom: 'in'},                                   // ночной город — «Бүгін кешке…»
  {from: 2.1, to: 3.9, kind: 'clip', segs: [[2.0, 2.6], [2.62, 3.82]], zoom: 'in', origin: '50% 45%'},    // вход + вывеска THE DOP
  {from: 3.9, to: 4.85, kind: 'clip', segs: [[7.2, 8.15]], tag: '🎮 PlayStation 5', zoom: 'in'},
  {from: 4.85, to: 6.8, kind: 'clip', segs: [[8.3, 10.25]], tag: '📺 85″ ЭКРАН', zoom: 'in', origin: '50% 40%'},
  {from: 6.8, to: INS, kind: 'clip', segs: [[14.1, 15.65]], tag: '🛋️ VIP-БӨЛМЕЛЕР', zoom: 'out'},
  {from: INS, to: 9.2, kind: 'clip', segs: [[12.3, 13.15]], tag: '⚽ LIVE ФУТБОЛ', zoom: 'in', origin: '60% 35%'},
  {from: 9.2, to: 10.75, kind: 'clip', segs: [[3.88, 5.43]], tag: '🎬 NETFLIX · КИНОПОИСК', zoom: 'in'},
  {from: 10.75, to: 13.5, kind: 'offer', segs: [[18.65, 19.9], [16.08, 17.07], [17.07, 17.57]]},
  {from: 13.5, to: 16.15, kind: 'cashback', segs: [[5.92, 7.15], [11.35, 12.27], [13.45, 13.95]]},
  {from: 16.15, to: 18.9, kind: 'address', segs: [[0, 2.0]]},                                            // дрон над зданием
  {from: 18.9, to: END, kind: 'cta', segs: [[22.0, 24.0]]},
];

// ---- Субтитры: как показывать слова на экране ----
const DISPLAY: Record<number, string> = {
  3: 'істейсің?', 4: '', 5: 'THE DOP-қа', 6: 'кел!', 7: 'PlayStation', 9: '85″', 10: '', 15: 'VIP-бөлмелер',
  18: 'Netflix', 34: 'Сәтбаев', 35: '2В', 36: '', 37: 'WhatsApp',
};
const CHUNKS: number[][] = [
  [0, 1, 2, 3], [4, 5, 6], [7, 8], [9, 10, 11, 12], [13, 14, 15], [16, 17], [18, 19, 20],
];
type W = {text: string; start: number; end: number};
const W_ALL = (words as {t: string; text: string; start: number; end: number}[]).filter((w) => w.t === 'WordBoundary') as W[];

// ---- Общие элементы ----
const PunchIn: React.FC<{children: React.ReactNode}> = ({children}) => {
  const fr = useCurrentFrame();
  const s = interpolate(fr, [0, 6], [1.18, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const blur = interpolate(fr, [0, 5], [14, 0], {extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{transform: `scale(${s})`, filter: `blur(${blur}px)`}}>{children}</AbsoluteFill>;
};

const Photo: React.FC<{src: string; zoom?: 'in' | 'out'; origin?: string; dur: number; dim?: number}> = ({src, zoom = 'in', origin = '50% 50%', dur, dim = 0}) => {
  const fr = useCurrentFrame();
  const p = interpolate(fr, [0, dur], [0, 1], {extrapolateRight: 'clamp'});
  const s = zoom === 'in' ? 1.02 + 0.22 * p : 1.24 - 0.2 * p;
  return (
    <AbsoluteFill style={{background: BG}}>
      <Img src={staticFile(`thedop/${src}`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${s})`, transformOrigin: origin}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,10,13,.75) 0%, rgba(10,10,13,0) 30%, rgba(10,10,13,0) 55%, rgba(10,10,13,.85) 100%)'}} />
      {dim > 0 && <AbsoluteFill style={{background: `rgba(10,10,13,${dim})`}} />}
    </AbsoluteFill>
  );
};

const Clip: React.FC<{segs: [number, number][]; dur: number; zoom?: 'in' | 'out'; origin?: string; blur?: number; dim?: number}> = ({segs, dur, zoom = 'in', origin = '50% 50%', blur = 0, dim = 0}) => {
  const fr = useCurrentFrame();
  const total = segs.reduce((a, [x, y]) => a + (y - x), 0);
  const rate = total / (dur / FPS);
  const p = interpolate(fr, [0, dur], [0, 1], {extrapolateRight: 'clamp'});
  const sc = zoom === 'in' ? 1.0 + 0.16 * p : 1.16 - 0.14 * p;
  let acc = 0;
  return (
    <AbsoluteFill style={{background: BG}}>
      <AbsoluteFill style={{transform: `scale(${sc + blur / 200})`, transformOrigin: origin, filter: blur ? `blur(${blur}px)` : undefined}}>
        {segs.map(([x, y], i) => {
          const start = Math.round((acc / rate) * FPS); acc += y - x;
          const end = i === segs.length - 1 ? dur : Math.round((acc / rate) * FPS);
          return (
            <Sequence key={i} from={start} durationInFrames={end - start}>
              <OffthreadVideo src={staticFile('thedop/club.mp4')} trimBefore={Math.round(x * FPS)} playbackRate={rate} muted
                style={{width: '100%', height: '100%', objectFit: 'cover'}} />
            </Sequence>
          );
        })}
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,10,13,0) 45%, rgba(10,10,13,.55) 70%, rgba(10,10,13,0) 100%)'}} />
      {dim > 0 && <AbsoluteFill style={{background: `rgba(10,10,13,${dim})`}} />}
    </AbsoluteFill>
  );
};

const Tag: React.FC<{text: string}> = ({text}) => {
  const fr = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: fr - 2, fps, config: {damping: 11, stiffness: 180}});
  return (
    <div style={{position: 'absolute', top: 500, width: '100%', display: 'flex', justifyContent: 'center'}}>
      <div style={{
        background: RED, color: WHITE, fontFamily: FONT, fontWeight: 900, fontSize: 64, padding: '18px 40px',
        borderRadius: 22, transform: `scale(${s}) rotate(-2deg)`, boxShadow: `0 0 40px ${RED}aa, 0 10px 30px rgba(0,0,0,.5)`,
        letterSpacing: 1, whiteSpace: 'nowrap',
      }}>{text}</div>
    </div>
  );
};

const NeonText: React.FC<{children: React.ReactNode; size: number; color?: string; style?: React.CSSProperties}> = ({children, size, color = WHITE, style}) => (
  <div style={{
    fontFamily: FONT, fontWeight: 900, fontSize: size, color, lineHeight: 1, textAlign: 'center',
    textShadow: `0 0 18px ${RED}, 0 0 50px ${RED}, 0 0 90px ${RED}88`, ...style,
  }}>{children}</div>
);

const Glow: React.FC = () => {
  const fr = useCurrentFrame();
  const o = 0.55 + 0.15 * Math.sin(fr / 6);
  return <AbsoluteFill style={{background: `radial-gradient(circle at 50% 45%, ${RED}${Math.round(o * 160).toString(16).padStart(2, '0')} 0%, rgba(10,10,13,.82) 62%)`}} />;
};

// ---- Сцены ----
const LogoScene: React.FC<{dur: number}> = ({dur}) => {
  const fr = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: fr, fps, config: {damping: 9, stiffness: 140}});
  const scale = interpolate(s, [0, 1], [3, 1]);
  const shake = fr < 8 ? Math.sin(fr * 3) * (8 - fr) * 2 : 0;
  const sub = spring({frame: fr - 8, fps});
  return (
    <AbsoluteFill>
      <Photo src="red1.jpg" dur={dur} dim={0.55} />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', transform: `translate(${shake}px, ${-shake}px)`}}>
        <NeonText size={210} style={{transform: `scale(${scale})`, letterSpacing: 6}}>THE DOP</NeonText>
        <div style={{marginTop: 40, fontFamily: FONT, fontWeight: 800, fontSize: 52, color: WHITE, opacity: sub, transform: `translateY(${(1 - sub) * 40}px)`, letterSpacing: 8}}>
          PS5 CLUB · АТЫРАУ
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const OfferScene: React.FC<{bg: React.ReactNode}> = ({bg}) => {
  const fr = useCurrentFrame();
  const {fps} = useVideoConfig();
  const a = spring({frame: fr, fps, config: {damping: 12}});
  const big = spring({frame: fr - 6, fps, config: {damping: 8, stiffness: 160}});
  const giftAt = vf(12.16) - f(sh(10.75));
  const g = spring({frame: fr - giftAt, fps, config: {damping: 7, stiffness: 200}});
  return (
    <AbsoluteFill>
      {bg}
      <Glow />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 30}}>
        <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 76, color: WHITE, opacity: a, transform: `translateY(${(1 - a) * -60}px)`}}>
          3 САҒАТ ТӨЛЕ
        </div>
        <NeonText size={330} style={{transform: `scale(${big})`}}>3+1</NeonText>
        <div style={{
          background: WHITE, color: BG, fontFamily: FONT, fontWeight: 900, fontSize: 56, padding: '20px 36px', borderRadius: 26, whiteSpace: 'nowrap',
          transform: `scale(${g}) rotate(-3deg)`,
        }}>4-ші сағат СЫЙЛЫҚ 🎁</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const CashbackScene: React.FC<{bg: React.ReactNode}> = ({bg}) => {
  const fr = useCurrentFrame();
  const {fps} = useVideoConfig();
  const n = Math.round(interpolate(fr, [0, 20], [0, 10], {extrapolateRight: 'clamp'}));
  const a = spring({frame: fr, fps, config: {damping: 10}});
  const coinAt = vf(14.68) - f(sh(13.5));
  const c = spring({frame: fr - coinAt, fps, config: {damping: 8, stiffness: 180}});
  return (
    <AbsoluteFill>
      {bg}
      <Glow />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 20}}>
        <NeonText size={300} style={{transform: `scale(${a})`}}>{n}%</NeonText>
        <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 110, color: WHITE, transform: `scale(${c})`, letterSpacing: 4}}>КЭШБЭК 💸</div>
        <div style={{marginTop: 30, fontFamily: FONT, fontWeight: 800, fontSize: 58, color: WHITE, opacity: interpolate(fr, [8, 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
          әр 1 000 ₸ → <span style={{color: RED}}>100 ₸</span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const AddressScene: React.FC<{bg: React.ReactNode}> = ({bg}) => {
  const fr = useCurrentFrame();
  const {fps} = useVideoConfig();
  const a = spring({frame: fr - 2, fps, config: {damping: 12}});
  const b = spring({frame: fr - 10, fps, config: {damping: 12}});
  const row: React.CSSProperties = {fontFamily: FONT, fontWeight: 900, color: WHITE, background: 'rgba(10,10,13,.82)', borderLeft: `14px solid ${RED}`, borderRadius: 20, padding: '26px 40px'};
  return (
    <AbsoluteFill>
      {bg}
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 28}}>
        <div style={{...row, fontSize: 76, transform: `translateX(${(1 - a) * -1100}px)`}}>📍 Атырау, Сәтбаев 2В</div>
        <div style={{...row, fontSize: 62, transform: `translateX(${(1 - b) * 1100}px)`}}>🕐 Күн сайын 14:00 – 04:00</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const CtaScene: React.FC<{bg: React.ReactNode}> = ({bg}) => {
  const fr = useCurrentFrame();
  const {fps} = useVideoConfig();
  const logo = spring({frame: fr, fps, config: {damping: 10}});
  const btn = spring({frame: fr - 6, fps, config: {damping: 9, stiffness: 160}});
  const pulse = 1 + 0.04 * Math.sin(fr / 4);
  const fire = spring({frame: fr - (vf(20.19) - f(sh(18.9))), fps, config: {damping: 10}});
  return (
    <AbsoluteFill>
      {bg}
      <Glow />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 34, paddingBottom: 120}}>
        <NeonText size={170} style={{transform: `scale(${logo})`, letterSpacing: 5}}>THE DOP</NeonText>
        <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 50, color: WHITE, letterSpacing: 4, opacity: logo}}>Ойна. Қара. Демал.</div>
        <div style={{
          marginTop: 30, background: '#25D366', color: 'white', fontFamily: FONT, fontWeight: 900, fontSize: 64,
          padding: '30px 56px', borderRadius: 999, transform: `scale(${btn * pulse})`, boxShadow: '0 0 50px #25D36699',
        }}>WhatsApp арқылы брондау</div>
        <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 70, color: WHITE, opacity: btn}}>+7 702 918 87 88</div>
        <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 52, color: WHITE, opacity: btn * 0.85}}>@thedopkz</div>
        <div style={{
          marginTop: 30, fontFamily: FONT, fontWeight: 900, fontSize: 54, color: WHITE, background: RED, padding: '16px 34px', borderRadius: 18,
          transform: `scale(${fire})`,
        }}>Демалыс күндері орын тез бітеді 🔥</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};


// ---- Блок VIP-комнат (анимированные карточки) ----
const VIP_LEAD = 0.2; // голос в блоке начинается через 0.2 сек
const VW = (vipWords as {text: string; start: number}[]);
const BLUE = '#4D5BFF';
type Card = {n: string; img: string; screen: string; price: number; color: string; at: number; hit?: boolean; slot: 'full' | 'top' | 'bottom'};
const VIP_CARDS: Card[] = [
  {n: 'VIP 1', img: 'football.png', screen: '85″', price: 2500, color: BLUE, at: 0, hit: true, slot: 'full'},
  {n: 'VIP 2', img: 'red2.jpg', screen: '71″', price: 2000, color: RED, at: VIP_LEAD + VW[5].start - 0.15, slot: 'full'},
  {n: 'VIP 3', img: 'red3.jpg', screen: '55″', price: 1500, color: RED, at: VIP_LEAD + VW[9].start - 0.15, slot: 'top'},
  {n: 'VIP 4', img: 'red1.jpg', screen: '55″', price: 1500, color: RED, at: VIP_LEAD + VW[9].start - 0.05, slot: 'bottom'},
];

const VipCard: React.FC<{c: Card; exitAt?: number}> = ({c, exitAt}) => {
  const fr = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = fr - f(c.at);
  if (local < 0) return null;
  const dir = c.slot === 'bottom' ? -1 : 1;
  const inS = spring({frame: local, fps, config: {damping: 14, stiffness: 120}});
  const outP = exitAt === undefined ? 0 : interpolate(fr, [f(exitAt) - 2, f(exitAt) + 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic)});
  if (outP >= 1) return null;
  const x = (1 - inS) * 1100 * dir - outP * 1200;
  const rotY = (1 - inS) * -55 * dir + outP * 45;
  const full = c.slot === 'full';
  const W = full ? 860 : 820, H = full ? 1140 : 540;
  const top = full ? 400 : c.slot === 'top' ? 400 : 990;
  const kb = 1.06 + 0.1 * Math.min(local / (fps * 3), 1);
  // неон: мягкая пульсация + короткое «мигание» в начале
  const flicker = local < 10 ? (local % 3 === 0 ? 0.3 : 1) : 0.8 + 0.2 * Math.sin(local / 3.5);
  const glare = interpolate(local, [4, 20], [-120, 220], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const price = Math.round(interpolate(local, [6, 22], [0, c.price], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) / 100) * 100;
  const lbl = spring({frame: local - 6, fps, config: {damping: 10, stiffness: 160}});
  return (
    <div style={{position: 'absolute', left: (1080 - W) / 2, top, width: W, height: H, perspective: 1600}}>
      <div style={{
        width: '100%', height: '100%', borderRadius: 36, overflow: 'hidden', position: 'relative',
        transform: `translateX(${x}px) rotateY(${rotY}deg)`,
        border: `6px solid ${c.color}`,
        boxShadow: `0 0 ${40 * flicker}px ${c.color}, 0 0 ${110 * flicker}px ${c.color}99, 0 30px 60px rgba(0,0,0,.6)`,
      }}>
        <Img src={staticFile(`thedop/${c.img}`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${kb})`}} />
        <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(10,10,13,.0) 45%, rgba(10,10,13,.92) 100%)`}} />
        <AbsoluteFill style={{background: `linear-gradient(105deg, transparent ${glare - 20}%, rgba(255,255,255,.35) ${glare}%, transparent ${glare + 15}%)`}} />
        <div style={{position: 'absolute', left: 40, bottom: full ? 44 : 30, right: 40, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', transform: `translateY(${(1 - lbl) * 60}px)`, opacity: lbl}}>
          <div>
            <div style={{fontFamily: FONT, fontWeight: 900, fontSize: full ? 130 : 96, color: WHITE, lineHeight: 0.95, textShadow: `0 0 30px ${c.color}`}}>{c.n}</div>
            <div style={{fontFamily: FONT, fontWeight: 800, fontSize: full ? 58 : 44, color: WHITE, marginTop: 10}}>
              {price.toLocaleString('ru-RU').replace(/ /g, ' ')} ₸<span style={{opacity: 0.7, fontSize: '0.7em'}}> / сағ</span>
            </div>
          </div>
          <div style={{background: c.color, color: WHITE, fontFamily: FONT, fontWeight: 900, fontSize: full ? 72 : 56, padding: '10px 26px', borderRadius: 20, boxShadow: `0 0 30px ${c.color}`}}>📺 {c.screen}</div>
        </div>
        {c.hit && (
          <div style={{position: 'absolute', top: 36, right: 36, background: RED, color: WHITE, fontFamily: FONT, fontWeight: 900, fontSize: 52, padding: '10px 24px', borderRadius: 16, transform: `rotate(6deg) scale(${lbl})`}}>ХИТ 🔥</div>
        )}
      </div>
    </div>
  );
};

const VipBlock: React.FC = () => {
  const fr = useCurrentFrame();
  const {fps} = useVideoConfig();
  const head = spring({frame: fr, fps, config: {damping: 12}});
  return (
    <AbsoluteFill>
      <Clip segs={[[8.3, 10.25]]} dur={f(VIP_DUR)} blur={18} dim={0.55} />
      <Glow />
      <div style={{position: 'absolute', top: 250, width: '100%', textAlign: 'center', transform: `translateY(${(1 - head) * -80}px)`, opacity: head}}>
        <NeonText size={84} style={{letterSpacing: 4}}>4 VIP-БӨЛМЕ</NeonText>
      </div>
      <VipCard c={VIP_CARDS[0]} exitAt={VIP_CARDS[1].at} />
      <VipCard c={VIP_CARDS[1]} exitAt={VIP_CARDS[2].at} />
      <VipCard c={VIP_CARDS[2]} />
      <VipCard c={VIP_CARDS[3]} />
    </AbsoluteFill>
  );
};

// ---- Субтитры (караоке: активное слово красное) ----
const Captions: React.FC = () => {
  const fr = useCurrentFrame();
  let abs = fr / FPS;
  if (abs >= INS + VIP_DUR) abs -= VIP_DUR; else if (abs >= INS) return null;
  const t = abs - VOICE_OFFSET;
  const chunk = CHUNKS.find((c) => t >= W_ALL[c[0]].start - 0.05 && t <= W_ALL[c[c.length - 1]].end + 0.25);
  if (!chunk) return null;
  const start = W_ALL[chunk[0]].start;
  const appear = interpolate(t, [start - 0.05, start + 0.1], [0.7, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', top: 1180, width: '100%', display: 'flex', justifyContent: 'center', padding: '0 70px', boxSizing: 'border-box'}}>
      <div style={{textAlign: 'center', lineHeight: 1.15, transform: `scale(${appear})`}}>
        {chunk.map((i) => {
          const w = W_ALL[i];
          const txt = DISPLAY[i] ?? w.text;
          if (!txt) return null;
          let j = i + 1; while (j < W_ALL.length && DISPLAY[j] === '') j++;
          const next = W_ALL[j];
          const active = t >= w.start && (next ? t < next.start : true);
          const said = t >= w.start;
          return (
            <span key={i} style={{
              fontFamily: FONT, fontWeight: 900, fontSize: 92, textTransform: 'uppercase',
              color: active ? RED : WHITE, opacity: said ? 1 : 0.55,
              transform: `scale(${active ? 1.06 : 1})`, display: 'inline-block', margin: '0 26px',
              WebkitTextStroke: '3px #000', paintOrder: 'stroke fill',
              textShadow: '0 6px 18px rgba(0,0,0,.8)',
            }}>{txt}</span>
          );
        })}
      </div>
    </div>
  );
};

// ---- Звук ----
const sfx = (name: string, atSec: number, vol = 0.6) => (
  <Sequence key={`${name}${atSec}`} from={f(sh(atSec))} durationInFrames={f(2)}>
    <Audio src={staticFile(`thedop/${name}.wav`)} volume={vol} />
  </Sequence>
);

export const TheDopAd: React.FC = () => {
  const voiceEnd = vf(21.85);
  return (
    <AbsoluteFill style={{background: BG}}>
      {SCENES.map((s, i) => {
        const dur = f(sh(s.to, true)) - f(sh(s.from));
        let body: React.ReactNode = null;
        const bgBlur = <Clip segs={s.segs} dur={dur} blur={8} />;
        if (s.kind === 'clip') body = <><Clip segs={s.segs} dur={dur} zoom={s.zoom} origin={s.origin} />{s.tag && <Tag text={s.tag} />}</>;
        if (s.kind === 'offer') body = <OfferScene bg={bgBlur} />;
        if (s.kind === 'cashback') body = <CashbackScene bg={bgBlur} />;
        if (s.kind === 'address') body = <AddressScene bg={<Clip segs={s.segs} dur={dur} zoom="in" dim={0.15} />} />;
        if (s.kind === 'cta') body = <CtaScene bg={<Clip segs={s.segs} dur={dur} blur={14} />} />;
        return (
          <Sequence key={i} from={f(sh(s.from))} durationInFrames={dur}>
            {i === 0 ? body : <PunchIn>{body}</PunchIn>}
          </Sequence>
        );
      })}
      <Sequence from={f(INS)} durationInFrames={f(VIP_DUR)}>
        <PunchIn><VipBlock /></PunchIn>
      </Sequence>
      <Captions />

      {/* Озвучка */}
      <Sequence from={f(VOICE_OFFSET)} durationInFrames={f(INS - VOICE_OFFSET)}>
        <Audio src={staticFile('thedop/voice.mp3')} volume={1} />
      </Sequence>
      <Sequence from={f(INS + VIP_DUR)}>
        <Audio src={staticFile('thedop/voice.mp3')} trimBefore={f(INS - VOICE_OFFSET)} volume={1} />
      </Sequence>
      <Sequence from={f(INS + VIP_LEAD)}>
        <Audio src={staticFile('thedop/voice_vip.mp3')} volume={1} />
      </Sequence>
      {/* Музыка: тише под голосом, громче в конце */}
      <Audio
        src={staticFile('thedop/music.wav')}
        volume={(fr) => interpolate(fr, [0, 10, voiceEnd, voiceEnd + 15, DURATION - 20, DURATION], [0, 0.2, 0.2, 0.45, 0.45, 0], {extrapolateRight: 'clamp'})}
      />
      {/* Эффекты */}
      {sfx('riser', 0.3, 0.35)}
      {sfx('impact', 2.68, 0.8)}
      {SCENES.slice(2).map((s) => sfx('whoosh', s.from - 0.12, 0.5))}
      {VIP_CARDS.filter((c, i) => i !== 3).map((c) => (
        <Sequence key={c.n} from={f(INS + c.at)} durationInFrames={f(1)}>
          <Audio src={staticFile('thedop/whoosh_card.wav')} volume={0.55} />
        </Sequence>
      ))}
      {sfx('pop', 12.46 + VOICE_OFFSET - 0.1, 0.6)}
      {sfx('coin', 14.68 + VOICE_OFFSET, 0.6)}
      {sfx('impact', 18.9, 0.5)}
    </AbsoluteFill>
  );
};
