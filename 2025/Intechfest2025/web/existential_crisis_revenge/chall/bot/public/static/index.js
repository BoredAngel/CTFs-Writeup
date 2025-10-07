const beneathTheMask = document.getElementById("beneathTheMask");
const instrumental = document.getElementById("instrumental");
const colorYourNight = document.getElementById("colorYourNight");
const clickSfx = document.getElementById("click-sfx");

window.addEventListener("DOMContentLoaded", () => {
  beneathTheMask.volume = 0.5;
  beneathTheMask.play().catch(() => {
    const resume = () => {
      beneathTheMask.play();
      document.removeEventListener("click", resume);
      document.removeEventListener("keydown", resume);
    };
    document.addEventListener("click", resume);
    document.addEventListener("keydown", resume);
  });
  const container = document.getElementById("personaTitle");

  putText("Existential");
  putText("Check");


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
  const visitBtn = document.getElementById("visitBtn");
  visitBtn.addEventListener("click", startCrawler);
});

async function startCrawler() {
  if (beneathTheMask.paused) {
    beneathTheMask.play();
  }
  if (!colorYourNight.paused) {
    colorYourNight.pause();
  }

  document.body.classList.remove("persona-bg");
  document.body.classList.add("persona-bg-alt");

  clickSfx.currentTime = 0;
  clickSfx.play();

  const modal = document.getElementById("statusModal");
  modal.style.display = "block";

  const modalStatus = document.getElementById("modalStatus");
  const progressBar = document.getElementById("modalProgressBar");

  modalStatus.innerText = "Sending request to server...";

  const csrfToken = document.getElementById("csrfToken").value;

  progressBar.style.width = "40%";

  const res = await fetch("/start-bot", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "CSRF-Token": csrfToken,
    },
    body: JSON.stringify({
      action: "run",
      url: document.getElementById("urlInput").value,
    }),
  });

  modalStatus.innerText = "Processing response...";
  progressBar.style.width = "70%";

  const json = await res.json();

  modalStatus.innerText = json.message;
  progressBar.style.width = "100%";

  status.innerText = json.message;

  if (json.message === "Crawl complete.") {
    beneathTheMask.pause();
    colorYourNight.volume = 0.5;
    colorYourNight.play();
    document.body.classList.remove("persona-bg-alt");
    document.body.classList.add("persona-bg");
    setTimeout(() => {
      modal.style.display = "none";
      progressBar.style.width = "25%";
      modalStatus.innerText = "Initializing...";
    }, 2000);
  }
}
