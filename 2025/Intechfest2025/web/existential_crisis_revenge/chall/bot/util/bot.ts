import { browserCtx } from "./setup";
import dns from "dns/promises";
import net from "net";

async function isLocalAddress(host: string): Promise<boolean> {
  // n-day seems interesting right?
  console.log(`[${new Date().toISOString()}] Checking if ${host} is local...`);
  const addresses = await dns.lookup(host, { all: true });
  return addresses.some((addr) => {
    return (
      addr.family === 4 &&
      (addr.address.startsWith("127.") ||
        addr.address.startsWith("192.168.") ||
        addr.address === "0.0.0.0")
    );
  });
}

export async function RunBot(urlRaw: string, maxTimeout: number) {
  const context = await browserCtx();
  try {
    const url = new URL(urlRaw);

    console.log(`[${new Date().toISOString()}] Running bot...`);
    const page = await context.newPage();
    if (await isLocalAddress(url.hostname)) {
      throw new Error("Blocked url");
    }
    await page.goto(url.href, {
      waitUntil: "networkidle",
    });
    await page.waitForTimeout(maxTimeout);
    const urlNow = await page.url();
    const hostname = new URL(urlNow).hostname;
    if (await isLocalAddress(hostname)) {
      throw new Error("how did u get here?");
    }
    await page.waitForTimeout(maxTimeout);
    console.log(`[${new Date().toISOString()}] Bot done. ${urlNow}`);
  } catch (error) {
    return error;
  } finally {
    await context.close();
  }
}
