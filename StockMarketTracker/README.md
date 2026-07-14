# MarketQuest

MarketQuest is a no-login classroom stock-market simulator designed for iPads and modern browsers. Students begin with $10,000, enter their stock purchases, record daily closing prices, decide whether to keep or sell, and view a graph of total portfolio gains and losses.

## Run it

The app is plain HTML, CSS, and JavaScript with no build step.

1. From this folder, start a local web server. For example: `python -m http.server 8000`
2. Open `http://localhost:8000` in a browser.

For student iPads, publish this folder to any static host (for example, a school web server, GitHub Pages, Netlify, or Cloudflare Pages). On an iPad, students can use Safari's **Share → Add to Home Screen** option.

## How data is saved

Data is stored only in that browser's local storage. It saves automatically and does not collect student information on a server. Clearing Safari/browser data will erase the portfolio. Students should download a backup from **Save & share** if they may change devices or if the browser could be reset.

## Suggested classroom workflow

1. One portfolio per student or team, with a $10,000 starting balance.
2. Add stocks using the price on the class's chosen purchase date.
3. After market close, enter each stock's closing price in **Daily check-in**.
4. Select **Keep** or **Sell all shares** and write an optional explanation.
5. Use **Results** at the end of the unit and download the CSV for submission.

This app intentionally uses student-entered prices, so it does not need an API key or live market-data subscription.
