const CHANNELS = {
  pip: "pip install adevkit",
  "pip-cli": 'pip install "adevkit[cli]"',
  winget: "winget install notaayushsrivastava.adevkit",
  apt: "sudo apt update && sudo apt install adevkit",
  macos: "curl -LO https://github.com/notaayushsrivastava/adevkit/releases/latest/download/adevkit-macos.pkg && sudo installer -pkg adevkit-macos.pkg -target /",
};

function setupCopyButtons() {
  document.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const value = btn.getAttribute("data-copy") || "";
      try {
        await navigator.clipboard.writeText(value);
        const prev = btn.textContent;
        btn.textContent = "Copied";
        btn.classList.add("copied");
        setTimeout(() => {
          btn.textContent = prev;
          btn.classList.remove("copied");
        }, 1400);
      } catch {
        // Clipboard API unavailable in restricted contexts
      }
    });
  });
}

function setupChannelTabs() {
  const cmdEl = document.getElementById("channel-cmd");
  const copyBtn = document.getElementById("channel-copy");
  const tabs = document.querySelectorAll("[data-channel]");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const key = tab.getAttribute("data-channel");
      const cmd = CHANNELS[key] || CHANNELS.pip;

      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");

      if (cmdEl) cmdEl.textContent = cmd;
      if (copyBtn) copyBtn.setAttribute("data-copy", cmd);
    });
  });
}

function setupReveals() {
  const nodes = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    nodes.forEach((n) => n.classList.add("visible"));
    return;
  }
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );
  nodes.forEach((n) => io.observe(n));
}

document.addEventListener("DOMContentLoaded", () => {
  setupCopyButtons();
  setupChannelTabs();
  setupReveals();
});
