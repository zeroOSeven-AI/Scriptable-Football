const fs = require("fs");
const puppeteer = require("puppeteer");

const players = {
  modric: "https://www.flashscore.com/player/modric-luka/bZWyoJnA/",
  bellingham: "https://www.flashscore.com/player/bellingham-jude/0vgscFU0/"
};

async function scrapePlayer(name, url, page) {
  await page.goto(url, { waitUntil: "networkidle2", timeout: 0 });

  // čekamo da se stats pojave
  await page.waitForSelector("body", { timeout: 15000 });

  const data = await page.evaluate(() => {
    const text = document.body.innerText;

    function find(label) {
      const r = new RegExp(label + "\\s*(\\d+\\.?\\d*)");
      const m = text.match(r);
      return m ? m[1] : 0;
    }

    return {
      goals: Number(find("Goals")),
      assists: Number(find("Assists")),
      matches: Number(find("Matches")),
      rating: Number(find("Rating"))
    };
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
      console.log("ERR:", name);
      result[name] = { player: name, goals: 0, assists: 0, matches: 0, rating: 0 };
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
