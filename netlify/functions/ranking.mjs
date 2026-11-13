// ランキングAPI（Netlify Functions + Netlify Blobs）
//   GET  /api/ranking  → 上位の記録を "スコア,名前;スコア,名前;..." の文字列で返す
//   POST /api/ranking  → 本文 "スコア\n名前" を受け取り、ランクインなら登録して "順位|記録の文字列" を返す
//                         順位は0始まり。ランク外なら -1
import { getStore } from "@netlify/blobs";

const RANK_MAX = 10;          // 載せる人数（ゲーム側のRANK_MAXと同じにする）
const NAME_MAX = 8;           // 名前の最大文字数（ゲーム側のNAME_MAXと同じにする）
const SCORE_MAX = 1000000;    // これを超えるスコアは不正とみなして拒否する（実際のプレイに合わせて調整）
const MIN_INTERVAL_MS = 20000; // 同じ接続元からの登録の最短間隔（連続送信の抑制）
const BODY_MAX = 200;         // 受け付ける本文の最大バイト数
const KEY = "top";
const RETRY = 5;

const text = (body, status = 200) =>
  new Response(body, {
    status,
    headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" },
  });

const encode = (list) => list.map((e) => `${e.s},${e.n}`).join(";");

function cleanName(raw) {
  // 制御文字・区切り文字を空白にし、前後の空白を除いて、文字数を制限する
  let n = String(raw).replace(/[\u0000-\u001f\u007f,;|]/g, " ").trim();
  n = Array.from(n).slice(0, NAME_MAX).join("").trim();
  return n === "" ? "NONAME" : n;
}

async function hashIp(ip) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(String(ip)));
  return Array.from(new Uint8Array(buf)).slice(0, 12).map((b) => b.toString(16).padStart(2, "0")).join("");
}

export default async (req, context) => {
  // 本番とプレビュー（deploy preview など）でデータを分け、確認中の書き込みが本番に混ざらないようにする
  const isProd = context.deploy?.context === "production";
  const store = getStore({ name: isProd ? "ranking" : "ranking-dev", consistency: "strong" });

  if (req.method === "GET") {
    const entry = await store.get(KEY, { type: "json", consistency: "strong" });
    return text(encode(Array.isArray(entry) ? entry : []));
  }

  if (req.method !== "POST") return text("method not allowed", 405);

  // 他のサイトのページからの送信を拒否する（同じサイトからの送信だけ受け付ける）
  const origin = req.headers.get("origin");
  if (origin && new URL(origin).host !== new URL(req.url).host) return text("forbidden", 403);

  const raw = await req.text();
  if (raw.length > BODY_MAX) return text("too large", 413);
  const nl = raw.indexOf("\n");
  if (nl < 0) return text("bad request", 400);
  const scoreText = raw.slice(0, nl).trim();
  if (!/^\d{1,7}$/.test(scoreText)) return text("bad score", 400);
  const score = parseInt(scoreText, 10);
  if (score <= 0 || score > SCORE_MAX) return text("bad score", 400);
  const name = cleanName(raw.slice(nl + 1));

  // 連続送信の抑制（接続元ごとに、最後の登録時刻を覚えておく）
  const limiter = getStore({ name: isProd ? "ranking-rl" : "ranking-rl-dev", consistency: "strong" });
  const ipKey = await hashIp(context.ip || "unknown");
  const last = await limiter.get(ipKey, { type: "json", consistency: "strong" });
  const now = Date.now();
  if (last && now - last.t < MIN_INTERVAL_MS) return text("too many requests", 429);

  // 同時に書き込まれても記録が消えないよう、ETagが一致したときだけ書き込み、ダメなら読み直してやり直す
  for (let i = 0; i < RETRY; i++) {
    const cur = await store.getWithMetadata(KEY, { type: "json", consistency: "strong" });
    const list = cur && Array.isArray(cur.data) ? cur.data : [];
    let pos = list.filter((e) => e.s >= score).length; // 同点は先に記録した方が上
    if (pos >= RANK_MAX) return text(`-1|${encode(list)}`);
    const next = list.slice();
    next.splice(pos, 0, { n: name, s: score });
    const trimmed = next.slice(0, RANK_MAX);
    const res = await store.setJSON(KEY, trimmed, cur ? { onlyIfMatch: cur.etag } : { onlyIfNew: true });
    if (res.modified) {
      await limiter.setJSON(ipKey, { t: now });
      return text(`${pos}|${encode(trimmed)}`);
    }
  }
  return text("busy", 503);
};

export const config = { path: "/api/ranking" };
