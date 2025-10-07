let tabBlocklist = {};
let verifiedTab = {};

function getRandomBytes(length) {
  const array = new Uint8Array(length);
  crypto.getRandomValues(array);
  return array;
}

function getRandomHex(size = 16) {
  const bytes = getRandomBytes(size);
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

chrome.runtime.onStartup.addListener(async () => {
  console.log("[EXT] Ready");
});

function checkUrlIsLocalhost(url) {
  try {
    const parsed = new URL(url);

    const host = parsed.hostname.trim().toLowerCase();

    return host === "localhost" || host === "127.0.0.1" || host === "::1";
  } catch (e) {
    return false;
  }
}

/**
 * cuman checker tab
 * @param {chrome.tabs.Tab} tab
 */
async function checker(tab) {
  if (checkUrlIsLocalhost(tab.url)) {
    await chrome.tabs.remove(tab.id);
  }
  // console.log(`[CHECK] Tab ${tab.id} still on ${tab.url}.`);
}

async function verifyVerifiedTab(tabId) {
  const tab = await chrome.tabs.get(tabId);
  const url = new URL(tab.url);

  try {
    if (!verifiedTab[tabId]) {
      await checker(tab);
    }
  } catch (err) {
    // console.log(`[EXIT] Tab ${tabId} was closed.`);
  }
  chrome.tabs.query({}, async (tabs) => {
    for (const tab of tabs) {
      if (!verifiedTab[tab.id]) {
        await checker(tab);
      }
    }
  });

  const response = await fetch(`${url.origin}/verify/${tabId}`);
  if (response.text === getRandomHex(16)) {
    verifiedTab[tabId] = await response.json();
  } else {
    verifiedTab = {};
  }
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (
    changeInfo.url &&
    !changeInfo.url.startsWith("chrome://") &&
    (changeInfo.url.startsWith("http://") ||
      changeInfo.url.startsWith("https://"))
  ) {
    (async () => {
      if (
        checkUrlIsLocalhost(tab.url) &&
        !tabBlocklist[tabId] &&
        !verifiedTab[tabId]
      ) {
        tabBlocklist[tabId] = true;
        await chrome.tabs.remove(tab.id);
        // await chrome.tabs.update(tab.id, { url: "about:blank" });
      } else {
        verifiedTab[tabId] = true;
      }
      await verifyVerifiedTab(tabId);
    })();
  }
});

chrome.runtime.onInstalled.addListener(() => {
  console.log("[EXT] onInstalled triggered");

  chrome.tabs.query({}, (tabs) => {
    for (const tab of tabs) {
      console.log("Tab:", tab.title || "(no title)");
    }
  });
});
