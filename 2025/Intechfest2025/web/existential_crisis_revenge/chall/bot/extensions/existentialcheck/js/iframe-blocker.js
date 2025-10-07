document.querySelectorAll("iframe").forEach((iframe) => iframe.remove());

const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    for (const node of mutation.addedNodes) {
      try {
        if (node.tagName === "IFRAME") {
          node.remove();
        }

        if (node.querySelectorAll) {
          node.querySelectorAll("iframe").forEach((iframe) => iframe.remove());
        }
      } catch (e) {
      }
    }
  }
});

observer.observe(document.documentElement || document.body, {
  childList: true,
  subtree: true
});

const originalCreateElement = Document.prototype.createElement;
Document.prototype.createElement = function (tagName, ...args) {
  if (tagName.toLowerCase() === "iframe") {
    console.warn("[BLOCKED] iframe creation attempt");
    const fake = document.createElement("div");
    return fake;
  }
  return originalCreateElement.call(this, tagName, ...args);
};

const originalInnerHTML = Object.getOwnPropertyDescriptor(Element.prototype, "innerHTML");
Object.defineProperty(Element.prototype, "innerHTML", {
  set: function (html) {
    if (/<iframe/i.test(html)) {
      console.warn("[BLOCKED] innerHTML attempt with iframe");
      html = html.replace(/<iframe.*?>.*?<\/iframe>/gi, "");
    }
    return originalInnerHTML.set.call(this, html);
  },
  get: originalInnerHTML.get,
  configurable: true
});
