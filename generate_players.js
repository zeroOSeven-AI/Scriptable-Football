import fs from "fs";
import fetch from "node-fetch";
import * as cheerio from "cheerio";

const LEAGUES = [
  {
    name: "serie-a",
    url: "https://www.flashscore.com/football/italy/serie-a/teams/"
  },
  {
    name: "premier-league",
    url: "https://www.flashscore.com/football/england/premier-league/teams/"
  }
];

const OUTPUT = "players.json";
const DELAY = 1200;

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function getHTML(url) {
  const res = await fetch(url, {
    headers: { "User-Agent": "Mozilla/5.0" }
  });
  return await res.text();
}

async function getTeams(leagueUrl) {
  const html = await getHTML(leagueUrl);
  const $ = cheerio.load(html);

  const teams = [];

  $("a[href*='/team/']").each((_, el) => {
    const href = $(el).attr("href");
    const name = $(el).text().trim();

    if (!href || !name) return;

    teams.push({
      name,
      url: "https://www.flashscore.com" + href
    });
  });

  return [...new Map(teams.map(t => [t.url, t])).values()];
}

async function getPlayers(team) {
  const squadUrl = team.url + "squad/";
  const html = await getHTML(squadUrl);
  const $ = cheerio.load(html);

  const players = [];

  $("a[href*='/player/']").each((_, el) => {
    const href = $(el).attr("href");
    const name = $(el).text().trim();

    if (!href || !name) return;

    players.push({
      name,
      url: "https://www.flashscore.com" + href
    });
  });

  return [...new Map(players.map(p => [p.url, p])).values()];
}

async function main() {
  const result = {};

  for (const league of LEAGUES) {
    console.log("Liga:", league.name);

    const teams = await getTeams(league.url);

    for (const team of teams) {
      console.log(" Klub:", team.name);

      try {
        const players = await getPlayers(team);

        for (const p of players) {
          const key = p.name
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-z0-9]/g, "");

          result[key] = {
            name: p.name,
            url: p.url
          };
        }

        await sleep(DELAY);

      } catch (e) {
        console.log("  ERR squad:", team.name);
      }
    }
  }

  fs.writeFileSync(OUTPUT, JSON.stringify(result, null, 2));
  console.log("Gotovo. Igrača:", Object.keys(result).length);
}

main();
