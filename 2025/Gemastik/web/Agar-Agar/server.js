import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import path from 'path';
import fsp from 'fs/promises';
import grpc from '@grpc/grpc-js';
import protoLoader from '@grpc/proto-loader';
 
import { execFile } from 'child_process';

// --- App
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: '*' },
});

app.use(express.static('static'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// ---- Skins fetch endpoint
const skinsDir = path.join(process.cwd(), 'static', 'skins');
async function ensureSkinsDir() {
  try {
    await fsp.mkdir(skinsDir, { recursive: true });
  } catch {}
}

const mimeToExt = {
  'image/png': 'png',
  'image/jpeg': 'jpg',
  'image/jpg': 'jpg',
  'image/webp': 'webp',
  'image/gif': 'gif',
};

app.post('/skins/fetch', async (req, res) => {
  try {
    const url = (req.body && req.body.url) || '';
    if (typeof url !== 'string' || url.length < 8) {
      return res.status(400).json({ ok: false, error: 'Invalid url' });
    }
    await ensureSkinsDir();

    // Prefer system curl if available; fallback to fetch()
    function runCurl(args) {
      return new Promise((resolve, reject) => {
        const child = execFile('curl', args, { encoding: 'buffer', maxBuffer: 25 * 1024 * 1024 }, (err, stdout, stderr) => {
          if (err) {
            return reject(new Error(stderr?.toString() || err.message));
          }
          resolve(stdout);
        });
      });
    }

    async function getContentTypeWithCurl(targetUrl) {
      const headerOut = await runCurl(['-sSLI', '-A', 'agar-agar-curl/1.0', '--max-time', '20', targetUrl]);
      const text = headerOut.toString();
      // consider last header block if redirects occurred
      const blocks = text.split(/\r?\n\r?\n/).filter(Boolean);
      const last = blocks[blocks.length - 1] || '';
      const lines = last.split(/\r?\n/);
      for (const line of lines) {
        const idx = line.indexOf(':');
        if (idx > 0 && line.slice(0, idx).trim().toLowerCase() === 'content-type') {
          return line.slice(idx + 1).trim().toLowerCase();
        }
      }
      return '';
    }

    try {
      const contentType = await getContentTypeWithCurl(url);
      const pureType = (contentType || '').split(';')[0].trim();
      if (!pureType || !pureType.startsWith('image/')) {
        return res.status(400).json({ ok: false, error: 'URL did not return an image' });
      }
      const ext = mimeToExt[pureType] || 'png';
      const fileName = `skin_${Date.now()}_${Math.random().toString(36).slice(2, 8)}.${ext}`;
      const outPath = path.join(skinsDir, fileName);
      const body = await runCurl(['-sSL', '-A', 'agar-agar-curl/1.0', '--max-time', '20', url]);
      await fsp.writeFile(outPath, body);
      return res.json({ ok: true, name: fileName, url: `/skins/${fileName}` });
    } catch (curlErr) {
      // Fallback to fetch()
      const controller = new AbortController();
      const t = setTimeout(() => controller.abort(), 20000);
      let resp;
      try {
        resp = await fetch(url, { redirect: 'follow', signal: controller.signal });
      } finally {
        clearTimeout(t);
      }
      if (!resp.ok) {
        return res.status(400).json({ ok: false, error: `HTTP ${resp.status}` });
      }
      const ct = (resp.headers.get('content-type') || '').toLowerCase();
      const pure = ct.split(';')[0].trim();
      if (!pure.startsWith('image/')) {
        return res.status(400).json({ ok: false, error: 'URL did not return an image' });
      }
      const ext = mimeToExt[pure] || 'png';
      const fileName = `skin_${Date.now()}_${Math.random().toString(36).slice(2, 8)}.${ext}`;
      const outPath = path.join(skinsDir, fileName);
      const buf = Buffer.from(await resp.arrayBuffer());
      await fsp.writeFile(outPath, buf);
      return res.json({ ok: true, name: fileName, url: `/skins/${fileName}` });
    }
  } catch (e) {
    return res.status(500).json({ ok: false, error: e?.message || 'Fetch failed' });
  }
});

app.get('/healthz', (_req, res) => {
  res.json({ ok: true });
});

// --- gRPC client to Go server
const goProtoPath = path.join(process.cwd(), 'ctf', 'game.proto');
const pkgDef = protoLoader.loadSync(goProtoPath, { 
  keepCase: true, 
  longs: String, 
  enums: String, 
  defaults: true, 
  oneofs: true 
});
const goPkg = grpc.loadPackageDefinition(pkgDef).game;
const GRPC_ADDR = process.env.GRPC_ADDR || '127.0.0.1:50051';

let goClient = null;
try {
  goClient = new goPkg.GameService(GRPC_ADDR, grpc.credentials.createInsecure());
  console.log('Connected gRPC client to', GRPC_ADDR);
} catch (e) {
  console.warn('gRPC client init failed:', e?.message || e);
}

// Map socket IDs to Go player IDs
const socketToGoId = new Map();
const goIdToSocket = new Map();

// Track player skins (socketId -> skinUrl)
const playerSkins = new Map();

// --- Sockets (bridge to gRPC)
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  if (!goClient) {
    console.warn('No gRPC client available for', socket.id);
    socket.disconnect();
    return;
  }

  // Welcome and get Go player ID
  goClient.Welcome({}, (err, reply) => {
    if (err) {
      console.warn('gRPC Welcome failed:', err.message);
      socket.disconnect();
      return;
    }
    
    const goId = reply.id;
    socketToGoId.set(socket.id, goId);
    goIdToSocket.set(goId, socket.id);
    
    // Send welcome to client (JSON)
    socket.emit('welcome', { id: socket.id, world: { size: reply.world?.size || 2500 } });
    
    // Send respawn to client (initial spawn, JSON)
    socket.emit('respawn', { x: 0, y: 0, protected_for: 5.0 });
    
    // Send current skin data to new client
    const skinData = {};
    for (const [sockId, skinUrl] of playerSkins) {
      skinData[sockId] = skinUrl;
    }
    socket.emit('skins_data', skinData);
  });

  // Set up state streaming from Go server
  const stateStream = goClient.StreamState({});
  stateStream.on('data', (state) => {
    // Convert gRPC state to client format
    const payload = {
      players: (state.players || []).map(p => ({
        id: goIdToSocket.get(p.id) || p.id,
        name: p.name,
        x: p.x,
        y: p.y,
        mass: p.mass,
        color: p.color,
        protected: p.protected,
      })),
      pellets: (state.pellets || []).map(p => ({ x: p.x, y: p.y })),
      stars: (state.stars || []).map(m => ({ x: m.x, y: m.y, mass: m.mass })),
      galaxies: (state.galaxies || []).map(m => ({ x: m.x, y: m.y, mass: m.mass })),
      blackholes: (state.blackholes || []).map(m => ({ x: m.x, y: m.y, mass: m.mass })),
      leaderboard: (state.leaderboard || []).map(p => ({ name: p.name, mass: p.mass })),
      world: { size: state.world?.size || 2500 },
    };
    socket.emit('state', payload);

    // Send individual boost status
    const playerInState = (state.players || []).find(p => p.id === socketToGoId.get(socket.id));
    if (playerInState) {
      socket.emit('boost_status', {
        fuel: playerInState.fuel || 0,
        boosting: playerInState.boosting || false,
      });
    }
  });
  
  stateStream.on('error', (err) => {
    console.warn('gRPC state stream error:', err.message);
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
    const goId = socketToGoId.get(socket.id);
    if (goId && goClient) {
      goClient.Disconnect({ id: goId }, () => {});
      goIdToSocket.delete(goId);
    }
    socketToGoId.delete(socket.id);
    playerSkins.delete(socket.id);
    stateStream.cancel();
  });

  socket.on('input', (data) => {
    const goId = socketToGoId.get(socket.id);
    if (!goId || !goClient) return;
    if (!data || typeof data !== 'object') return;
    const tx = Number(data.tx);
    const ty = Number(data.ty);
    if (!Number.isFinite(tx) || !Number.isFinite(ty)) return;
    goClient.SendInput({ id: goId, tx, ty }, () => {});
  });

  socket.on('boost_start', (data) => {
    const goId = socketToGoId.get(socket.id);
    if (!goId || !goClient) return;
    if (!data || typeof data !== 'object') return;
    const tx = Number(data.tx);
    const ty = Number(data.ty);
    if (!Number.isFinite(tx) || !Number.isFinite(ty)) return;
    goClient.StartBoost({ id: goId, tx, ty }, () => {});
  });

  socket.on('boost_end', () => {
    const goId = socketToGoId.get(socket.id);
    if (!goId || !goClient) return;
    goClient.EndBoost({ id: goId }, () => {});
  });

  socket.on('set_name', (data) => {
    const goId = socketToGoId.get(socket.id);
    if (!goId || !goClient) return;
    if (!data || typeof data !== 'object') return;
    const nameRaw = (typeof data.name === 'string') ? data.name : '';
    const name = nameRaw.trim().slice(0, 20);
    goClient.SetName({ id: goId, name: name || `Player-${socket.id.slice(0, 4)}` }, () => {});
  });

  socket.on('set_skin', (data) => {
    if (!data || typeof data !== 'object') return;
    const skinUrl = (typeof data.url === 'string') ? data.url.trim() : '';
    if (skinUrl) {
      playerSkins.set(socket.id, skinUrl);
    } else {
      playerSkins.delete(socket.id);
    }
    // Broadcast skin change to all clients
    io.emit('skin_set', { playerId: socket.id, url: skinUrl });
  });
});

// --- Start
const port = Number(process.env.PORT || 5000);
server.listen(port, () => {
  console.log(`Bridge server listening on http://0.0.0.0:${port}`);
  console.log(`Connecting to gRPC server at ${GRPC_ADDR}`);
});