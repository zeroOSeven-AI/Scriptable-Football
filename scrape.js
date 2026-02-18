const fs = require("fs");
const puppeteer = require("puppeteer");

const players = {
  modric: "https://www.flashscore.com/player/modric-luka/bZWyoJnA/",
  bellingham: "https://www.flashscore.com/player/bellingham-jude/0vgscFU0/"
};

async function scrapePlayer(name, url, page) {
  await page.goto(url, { waitUntil: "networkidle2", timeout: 0 });

  // čekamo da se pojave zadnje utakmice
  await page.waitForSelector("body", { timeout: 20000 });

  const data = await page.evaluate(() => {
    const text = document.body.innerText;

    // hvata PRVU ocjenu tipa 7.4 ili 6.9
    const ratingMatch = text.match(/\b\d\.\d\b/);
    const rating = ratingMatch ? Number(ratingMatch[0]) : 0;

    // hvata minute tipa 90'
    const minMatch = text.match(/(\d{1,3})'/);
    const minutes = minMatch ? Number(minMatch[1]) : 0;

    // hvata rezultat tipa 2\n1
    const resMatch = text.match(/\n(\d)\n(\d)\n/);
    const result = resMatch ? `${resMatch[1]}:${resMatch[2]}` : "-";

    return { rating, minutes, result };
  });

  return { player: name, ...data };
}

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox"]
  });

  const page = await browser.newPage();

  let result = {};

  for (const [name, url] of Object.entries(players)) {
    try {
      result[name] = await scrapePlayer(name, url, page);
      console.log("OK:", name);
    } catch (e) {
      console.log("ERR:", name, e.message);
      result[name] = { player: name, rating: 0, minutes: 0, result: "-" };
    }
  }

  await browser.close();

  fs.writeFileSync(
    "db.json",
    JSON.stringify(
      {
        updated: new Date().toISOString(),
        data: result
      },
      null,
      2
    )
  );

  console.log("DB SAVED");
})();
