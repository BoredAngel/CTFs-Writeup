window.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("personaTitle");

  putText(document.getElementById("username").innerText);
  // putText("username");

  function putText(text) {
    const emojis = [
      "^_^",
      ">_<",
      "owo",
      ":3",
      "uwu",
      "xD",
      "._.",
      "o_o",
      "T_T",
      "ಠ_ಠ",
      ":D",
      ":)",
      ":P",
      ";)",
      "-_-",
      ">:3",
      "♡",
      "｡^‿^｡",
      "(≧◡≦)",
      "ʕ•ᴥ•ʔ",
    ];

    const line = document.createElement("div");
    line.style.display = "flex";
    line.style.justifyContent = "center";
    line.style.marginBottom = "1rem";
    line.style.flexWrap = "wrap";
    line.style.gap = "0.5rem";

    for (let i = 0; i < text.length; i++) {
      const emoji = emojis[i % emojis.length];
      const char = text[i];

      const box = document.createElement("div");
      box.className = "emoji-char-box";
      box.textContent = `${emoji}\n${char}`;
      box.style.whiteSpace = "pre";
      box.style.display = "inline-block";
      box.style.textAlign = "center";
      box.style.margin = "0 6px";
      box.style.border = "2.5px solid #ff0000";
      box.style.background = "#111";
      box.style.color = "#fff";
      box.style.padding = "10px 12px";
      box.style.fontFamily = "Impact, Arial Black, monospace";
      box.style.fontSize = "1.1rem";
      box.style.lineHeight = "1.4";
      box.style.transform = `rotate(${rand(-5, 5)}deg) skew(${rand(
        -6,
        6
      )}deg, ${rand(-6, 6)}deg) translate(${rand(-2, 2)}px, ${rand(-2, 2)}px)`;

      line.appendChild(box);
    }

    container.appendChild(line);
  }

  function rand(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }
});
