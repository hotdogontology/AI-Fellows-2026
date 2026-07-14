"use strict";

const STORAGE_KEY = "marketQuestPortfolioV1";
const STARTING_CASH = 10000;

const freshState = () => ({
  version: 1,
  studentName: "",
  classPeriod: "",
  startingCash: STARTING_CASH,
  cash: STARTING_CASH,
  holdings: [],
  records: []
});

let state = loadState();

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const money = (value) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value) || 0);
const shortMoney = (value) => {
  const amount = Number(value) || 0;
  return Math.abs(amount) >= 1000 ? `$${(amount / 1000).toFixed(1)}k` : `$${Math.round(amount)}`;
};
const formatDate = (date) => date ? new Date(`${date}T12:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) : "";
const today = () => new Date().toLocaleDateString("en-CA");
const roundMoney = (value) => Math.round((Number(value) + Number.EPSILON) * 100) / 100;
const uniqueId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`;

function loadState() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (saved && saved.version === 1 && Array.isArray(saved.holdings) && Array.isArray(saved.records)) return saved;
  } catch (error) {
    console.warn("Could not load saved portfolio", error);
  }
  return freshState();
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function latestPrice(holding) {
  const records = [...state.records].sort((a, b) => b.date.localeCompare(a.date));
  for (const record of records) {
    const entry = record.entries.find((item) => item.holdingId === holding.id);
    if (entry) return entry.closePrice;
  }
  return holding.purchasePrice;
}

function currentTotals() {
  const active = state.holdings.filter((holding) => holding.status === "active");
  const stocks = active.reduce((sum, holding) => sum + holding.shares * latestPrice(holding), 0);
  const total = state.cash + stocks;
  return { active, stocks: roundMoney(stocks), total: roundMoney(total), gain: roundMoney(total - state.startingCash) };
}

function render() {
  const isSetup = Boolean(state.studentName);
  $("#welcomeCard").hidden = isSetup;
  $("#appContent").hidden = !isSetup;
  $("#settingsButton").hidden = !isSetup;
  if (!isSetup) return;

  const totals = currentTotals();
  $("#studentLabel").textContent = [state.studentName, state.classPeriod].filter(Boolean).join(" • ");
  $("#totalValue").textContent = money(totals.total);
  $("#cashValue").textContent = money(state.cash);
  $("#investedValue").textContent = money(totals.stocks);
  $("#holdingCount").textContent = totals.active.length;
  const percent = (totals.gain / state.startingCash) * 100;
  const returnNode = $("#totalReturn");
  returnNode.textContent = `${totals.gain >= 0 ? "+" : "−"}${money(Math.abs(totals.gain))} (${percent >= 0 ? "+" : ""}${percent.toFixed(2)}%)`;
  returnNode.className = totals.gain > 0 ? "positive" : totals.gain < 0 ? "negative" : "neutral";
  const latest = [...state.records].sort((a, b) => b.date.localeCompare(a.date))[0];
  $("#asOfLabel").textContent = latest ? `Updated through ${formatDate(latest.date)}` : "Add your investments, then complete a daily check-in.";

  renderHoldings();
  renderDailyForm();
  renderHistory();
  renderResults();
}

function renderHoldings() {
  const container = $("#holdingsList");
  if (!state.holdings.length) {
    container.innerHTML = '<div class="empty-state"><strong>No stocks yet</strong><br />Tap “Add a stock” to build your portfolio.</div>';
    return;
  }
  const sorted = [...state.holdings].sort((a, b) => (a.status === b.status ? a.ticker.localeCompare(b.ticker) : a.status === "active" ? -1 : 1));
  container.innerHTML = sorted.map((holding) => {
    const price = holding.status === "sold" ? holding.salePrice : latestPrice(holding);
    const value = holding.shares * price;
    const gain = value - holding.shares * holding.purchasePrice;
    return `<article class="panel holding-card ${holding.status === "sold" ? "status-sold" : ""}">
      <div><span class="ticker">${escapeHtml(holding.ticker)}</span><strong>${escapeHtml(holding.companyName)}</strong><p>${holding.shares} share${holding.shares === 1 ? "" : "s"} • ${holding.status === "sold" ? `Sold ${formatDate(holding.saleDate)}` : "Currently owned"}</p></div>
      <div class="holding-stat"><span>${holding.status === "sold" ? "Sale price" : "Latest price"}</span><strong>${money(price)}</strong></div>
      <div class="holding-stat"><span>${holding.status === "sold" ? "Sale value" : "Market value"}</span><strong>${money(value)}</strong></div>
      <div class="holding-stat"><span>Gain / loss</span><strong class="${gain > 0 ? "positive" : gain < 0 ? "negative" : "neutral"}">${gain >= 0 ? "+" : "−"}${money(Math.abs(gain))}</strong></div>
    </article>`;
  }).join("");
}

function renderDailyForm() {
  const active = state.holdings.filter((holding) => holding.status === "active");
  const container = $("#dailyStocks");
  $("#saveDailyButton").disabled = !active.length;
  if (!active.length) {
    container.innerHTML = '<div class="empty-state">Add a stock in the Portfolio tab before recording prices.</div>';
    return;
  }
  container.innerHTML = active.map((holding) => `<div class="daily-row" data-holding-id="${holding.id}" data-cost="${holding.purchasePrice}">
    <div><span class="ticker">${escapeHtml(holding.ticker)}</span><strong>${escapeHtml(holding.companyName)}</strong><p class="muted">Bought at ${money(holding.purchasePrice)}</p></div>
    <label>Closing price<input class="close-price" type="number" min="0.01" step="0.01" inputmode="decimal" required placeholder="${latestPrice(holding).toFixed(2)}" /></label>
    <label>Decision<select class="decision"><option value="keep">Keep</option><option value="sell">Sell all shares</option></select></label>
    <div class="change-preview neutral">Enter price</div>
  </div>`).join("");
}

function renderHistory() {
  const container = $("#historyList");
  if (!state.records.length) {
    container.innerHTML = '<div class="empty-state">Your saved daily check-ins will appear here.</div>';
    return;
  }
  container.innerHTML = [...state.records].sort((a, b) => b.date.localeCompare(a.date)).map((record) => {
    const gain = record.totalValue - state.startingCash;
    const sold = record.entries.filter((entry) => entry.decision === "sell").map((entry) => entry.ticker).join(", ");
    return `<article class="panel history-card"><div><strong>${formatDate(record.date)}</strong><p>${record.entries.length} price${record.entries.length === 1 ? "" : "s"} recorded${sold ? ` • Sold ${escapeHtml(sold)}` : ""}</p>${record.reflection ? `<p>“${escapeHtml(record.reflection)}”</p>` : ""}</div><div class="history-total"><span>Total value</span><strong>${money(record.totalValue)}</strong><small class="${gain > 0 ? "positive" : gain < 0 ? "negative" : "neutral"}">${gain >= 0 ? "+" : "−"}${money(Math.abs(gain))}</small></div></article>`;
  }).join("");
}

function renderResults() {
  const chart = $("#chart");
  const records = [...state.records].sort((a, b) => a.date.localeCompare(b.date));
  if (!records.length) {
    chart.innerHTML = '<div class="empty-state">Complete at least one daily check-in to make your graph.</div>';
    $("#resultsSummary").innerHTML = "";
    return;
  }

  const points = [{ date: state.holdings[0]?.purchaseDate || records[0].date, value: state.startingCash, label: "Start" }, ...records.map((record) => ({ date: record.date, value: record.totalValue }))];
  chart.innerHTML = buildChart(points);
  const end = records.at(-1).totalValue;
  const gain = roundMoney(end - state.startingCash);
  const best = records.reduce((winner, record) => record.totalValue > winner.totalValue ? record : winner, records[0]);
  $("#resultsSummary").innerHTML = `
    <article class="panel result-card"><span>Overall gain / loss</span><strong class="${gain >= 0 ? "positive" : "negative"}">${gain >= 0 ? "+" : "−"}${money(Math.abs(gain))}</strong></article>
    <article class="panel result-card"><span>Percent return</span><strong>${gain >= 0 ? "+" : ""}${((gain / state.startingCash) * 100).toFixed(2)}%</strong></article>
    <article class="panel result-card"><span>Highest portfolio value</span><strong>${money(best.totalValue)}</strong><small>${formatDate(best.date)}</small></article>`;
}

function buildChart(points) {
  const width = 900, height = 330, left = 64, right = 18, top = 24, bottom = 48;
  const values = points.map((point) => point.value).concat([state.startingCash]);
  let min = Math.min(...values), max = Math.max(...values);
  const padding = Math.max((max - min) * .2, 300);
  min = Math.floor((min - padding) / 500) * 500;
  max = Math.ceil((max + padding) / 500) * 500;
  const x = (index) => points.length === 1 ? (left + width - right) / 2 : left + index * ((width - left - right) / (points.length - 1));
  const y = (value) => top + (max - value) * ((height - top - bottom) / (max - min));
  const path = points.map((point, index) => `${index ? "L" : "M"}${x(index).toFixed(1)},${y(point.value).toFixed(1)}`).join(" ");
  const area = `${path} L${x(points.length - 1)},${height - bottom} L${x(0)},${height - bottom} Z`;
  const ticks = Array.from({ length: 5 }, (_, index) => min + (index * (max - min) / 4));
  const labelEvery = Math.max(1, Math.ceil(points.length / 6));
  return `<svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-hidden="true">
    <defs><linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2367d1" stop-opacity=".24"/><stop offset="1" stop-color="#2367d1" stop-opacity=".02"/></linearGradient></defs>
    ${ticks.map((tick) => `<line x1="${left}" x2="${width - right}" y1="${y(tick)}" y2="${y(tick)}" stroke="#e1e7ef"/><text x="${left - 9}" y="${y(tick) + 4}" text-anchor="end">${shortMoney(tick)}</text>`).join("")}
    <line x1="${left}" x2="${width - right}" y1="${y(state.startingCash)}" y2="${y(state.startingCash)}" stroke="#93a0b4" stroke-width="2" stroke-dasharray="7 6"/>
    <path d="${area}" fill="url(#areaFill)"/><path d="${path}" fill="none" stroke="#2367d1" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    ${points.map((point, index) => `<circle cx="${x(index)}" cy="${y(point.value)}" r="5" fill="white" stroke="#2367d1" stroke-width="3"><title>${formatDate(point.date)}: ${money(point.value)}</title></circle>${(index % labelEvery === 0 || index === points.length - 1) ? `<text x="${x(index)}" y="${height - 20}" text-anchor="middle">${point.label || new Date(`${point.date}T12:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</text>` : ""}`).join("")}
  </svg>`;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

function activateTab(tabName) {
  $$(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === tabName));
  $$(".tab-panel").forEach((panel) => { panel.hidden = panel.id !== `${tabName}Tab`; });
  if (tabName === "results") renderResults();
}

$("#setupForm").addEventListener("submit", (event) => {
  event.preventDefault();
  state.studentName = $("#studentName").value.trim();
  state.classPeriod = $("#classPeriod").value.trim();
  saveState();
  render();
});

$("#settingsButton").addEventListener("click", () => {
  const name = prompt("Student or team name:", state.studentName);
  if (name === null || !name.trim()) return;
  const period = prompt("Class period (optional):", state.classPeriod);
  if (period === null) return;
  state.studentName = name.trim();
  state.classPeriod = period.trim();
  saveState();
  render();
});

$$(".tab").forEach((tab) => tab.addEventListener("click", () => activateTab(tab.dataset.tab)));
$("#showAddStock").addEventListener("click", () => { $("#stockForm").hidden = false; $("#ticker").focus(); });
$("#cancelAddStock").addEventListener("click", () => { $("#stockForm").hidden = true; $("#stockError").textContent = ""; });

function updatePurchaseCost() {
  const cost = (Number($("#shares").value) || 0) * (Number($("#purchasePrice").value) || 0);
  $("#purchaseCost").textContent = money(cost);
}
$("#shares").addEventListener("input", updatePurchaseCost);
$("#purchasePrice").addEventListener("input", updatePurchaseCost);

$("#stockForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const shares = Number($("#shares").value), purchasePrice = Number($("#purchasePrice").value);
  const cost = roundMoney(shares * purchasePrice);
  if (cost > state.cash) {
    $("#stockError").textContent = `That costs ${money(cost)}, but you have ${money(state.cash)} available.`;
    return;
  }
  state.holdings.push({ id: uniqueId(), ticker: $("#ticker").value.trim().toUpperCase(), companyName: $("#companyName").value.trim(), shares, purchasePrice, purchaseDate: $("#purchaseDate").value, status: "active" });
  state.cash = roundMoney(state.cash - cost);
  saveState();
  event.target.reset();
  $("#purchaseDate").value = today();
  updatePurchaseCost();
  $("#stockError").textContent = "";
  $("#stockForm").hidden = true;
  render();
});

$("#dailyStocks").addEventListener("input", (event) => {
  if (!event.target.classList.contains("close-price")) return;
  const row = event.target.closest(".daily-row");
  const price = Number(event.target.value), cost = Number(row.dataset.cost);
  const percent = ((price - cost) / cost) * 100;
  const preview = row.querySelector(".change-preview");
  preview.textContent = price ? `${percent >= 0 ? "+" : ""}${percent.toFixed(2)}%` : "Enter price";
  preview.className = `change-preview ${price > cost ? "positive" : price < cost ? "negative" : "neutral"}`;
});

$("#dailyForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const date = $("#recordDate").value;
  if (state.records.some((record) => record.date === date)) {
    $("#dailyError").textContent = "A check-in already exists for this date. Choose a different date.";
    return;
  }
  const rows = $$(".daily-row");
  const entries = rows.map((row) => {
    const holding = state.holdings.find((item) => item.id === row.dataset.holdingId);
    return { holdingId: holding.id, ticker: holding.ticker, shares: holding.shares, purchasePrice: holding.purchasePrice, closePrice: Number(row.querySelector(".close-price").value), decision: row.querySelector(".decision").value };
  });
  let cashAfter = state.cash;
  entries.forEach((entry) => {
    if (entry.decision !== "sell") return;
    const holding = state.holdings.find((item) => item.id === entry.holdingId);
    holding.status = "sold";
    holding.salePrice = entry.closePrice;
    holding.saleDate = date;
    cashAfter += holding.shares * entry.closePrice;
  });
  state.cash = roundMoney(cashAfter);
  const activeValue = state.holdings.filter((holding) => holding.status === "active").reduce((sum, holding) => {
    const todayEntry = entries.find((entry) => entry.holdingId === holding.id);
    return sum + holding.shares * (todayEntry?.closePrice ?? latestPrice(holding));
  }, 0);
  state.records.push({ id: uniqueId(), date, entries, reflection: $("#dailyReflection").value.trim(), cashAfter: state.cash, totalValue: roundMoney(state.cash + activeValue) });
  state.records.sort((a, b) => a.date.localeCompare(b.date));
  saveState();
  event.target.reset();
  $("#recordDate").value = today();
  $("#dailyError").textContent = "";
  render();
});

function downloadFile(filename, contents, type) {
  const url = URL.createObjectURL(new Blob([contents], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

$("#exportCsv").addEventListener("click", () => {
  const header = ["Date", "Ticker", "Shares", "Purchase Price", "Closing Price", "Decision", "Portfolio Total", "Reflection"];
  const rows = state.records.flatMap((record) => record.entries.map((entry) => [record.date, entry.ticker, entry.shares, entry.purchasePrice, entry.closePrice, entry.decision, record.totalValue, record.reflection]));
  const csv = [header, ...rows].map((row) => row.map((cell) => `"${String(cell ?? "").replaceAll('"', '""')}"`).join(",")).join("\r\n");
  downloadFile(`${state.studentName.replace(/[^a-z0-9]+/gi, "-")}-marketquest.csv`, csv, "text/csv;charset=utf-8");
});

$("#exportJson").addEventListener("click", () => downloadFile(`${state.studentName.replace(/[^a-z0-9]+/gi, "-")}-marketquest-backup.json`, JSON.stringify(state, null, 2), "application/json"));
$("#importJson").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  try {
    const imported = JSON.parse(await file.text());
    if (imported.version !== 1 || !Array.isArray(imported.holdings) || !Array.isArray(imported.records)) throw new Error("Invalid backup");
    state = imported;
    saveState();
    render();
    alert("Backup restored successfully.");
  } catch (error) {
    alert("That file is not a valid MarketQuest backup.");
  }
  event.target.value = "";
});

$("#resetApp").addEventListener("click", () => {
  if (!confirm("Erase this entire portfolio and start over? This cannot be undone.")) return;
  state = freshState();
  localStorage.removeItem(STORAGE_KEY);
  activateTab("portfolio");
  render();
});

$("#purchaseDate").value = today();
$("#recordDate").value = today();
if ("serviceWorker" in navigator && location.protocol.startsWith("http")) navigator.serviceWorker.register("service-worker.js").catch(() => {});
render();
