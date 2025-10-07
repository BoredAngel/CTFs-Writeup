import express from "express";
import path from "path";
import { JSDOM } from "jsdom";
import cookieParser from "cookie-parser";
import crypto from "crypto";
import { marked } from "marked";
import csrf from "csurf";
import { RunBot } from "./util/bot";
import createDOMPurify from "dompurify";

const app = express();
const port = process.env.PORT || 1337;

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use(express.static(path.join(__dirname, "public/static")));
app.use(express.json());
app.use(cookieParser());

const window = new JSDOM("").window;
const DOMPurify = createDOMPurify(window);

const csrfProtection = csrf({ cookie: true });

app.use(express.urlencoded({ extended: false }));
app.use((req, res, next) => {
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; " +
      "script-src 'self'; " +
      "style-src 'self' 'unsafe-inline'; " +
      "connect-src 'self'; " +
      "font-src 'self'; https: http:" +
      "media-src 'self'; " +
      "frame-src 'none'; " +
      "img-src 'self' data: https: http:; " +
      "object-src 'none'; " +
      "base-uri 'self'; " +
      "form-action 'self';"
  );
  next();
});

app.get("/dashboard", async (req, res) => {
  if (!req.socket.remoteAddress?.includes("127.0.0.1") && !req.socket.remoteAddress?.includes("::1") && !req.socket.remoteAddress?.includes("172.22.0.1")) {
    console.warn(`[IP] ${req.socket.remoteAddress} accessing dashboard`);
    res.status(400).json({ message: "Invalid IP" });
    return;
  }
  const allowedTags = [
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "div",
    "span",
    "strong",
    "em",
    "b",
    "i",
    "u",
    "ul",
    "ol",
    "li",
    "code",
    "pre",
    "br",
    "blockquote",
    "img",
    "table",
    "thead",
    "tbody",
    "tr",
    "td",
    "th",
    "a",
  ];
  const allowedAttrs = [
    "src",
    "alt",
    "loading",
    "title",
    "href",
    "style",
    "rel",
    "target",
  ];
  const rawQuery = req.query.cok || "zeroDayOnDompurify";
  const rawHTML = await marked.parse(rawQuery.toString());
  const sanitizedMarkdownReadme = DOMPurify.sanitize(rawHTML, {
    ALLOWED_TAGS: allowedTags,
    ALLOWED_ATTR: allowedAttrs,
  });
  res.render("dashboard", {
    data: sanitizedMarkdownReadme,
    username: process.env.USERNAME || "exampleuser",
  });
});

const unique: Record<string, string> = {};

function hashIP(ip: string) {
  return crypto
    .createHash("sha256")
    .update(ip + crypto.randomBytes(32).toString("hex"))
    .digest("hex");
}

app.get("/", csrfProtection, (req, res) => {
  const ip = req.socket.remoteAddress || req.ip;
  if (!ip) {
    res.status(400).json({ message: "Invalid IP" });
    return;
  }
  const hashed = hashIP(ip);
  unique[ip] = hashed;
  res.cookie("hash", hashed);
  res.render("index", { csrfToken: req.csrfToken() });
});

app.get("/csrf-token", csrfProtection, (req, res) => {
  res.json({ csrfToken: req.csrfToken() });
});

app.post("/start-bot", csrfProtection, async (req, res) => {
  const ip = req.socket.remoteAddress || req.ip;
  if (!ip) {
    res.status(400).json({ message: "Invalid IP" });
    return;
  }
  const expected = req.cookies.hash;
  if (unique[ip] !== expected || unique[ip] === undefined) {
    res.status(403).json({ message: "Forbidden. Visit index first." });
    return;
  }
  unique[ip] = hashIP(ip);

  const url = req.body.url;

  if (!url) {
    res.status(400).json({ message: "Missing URL" });
    return;
  }

  const maxTimeout = req.body.timeout
  if (!maxTimeout || isNaN(maxTimeout) || maxTimeout < 1000 || maxTimeout > 5000) {
    res.status(400).json({ message: "Invalid timeout" });
    return;
  }

  const resp = await RunBot(url,maxTimeout);
  if (resp instanceof Error) {
    res.status(500).json({ message: resp.message });
    return;
  }
  res.json({ message: "Crawl complete." });
});

app.listen(port, () => {
  console.log(`Bot listening on port ${port}`);
});

// app.on("close", () => console.log("[server] closed"));