// @ts-nocheck
import { base } from '$app/paths'

const CONFERENCES = { E: 'eastern', W: 'western' }
const DIVISIONS = { A: 'atlantic', M: 'metropolitan', C: 'central', P: 'pacific' }

export function adaptStandingsSnapshot(snapshot) {
    if (
        !snapshot ||
        !Array.isArray(snapshot.standings) ||
        snapshot.standings.length !== 32 ||
        !Number.isInteger(snapshot.seasonId) ||
        snapshot.seasonId % 10000 !== Math.floor(snapshot.seasonId / 10000) + 1 ||
        !/^\d{4}-\d{2}-\d{2}$/.test(snapshot.sourceDate) ||
        !Number.isFinite(Date.parse(snapshot.fetchedAt))
    ) {
        throw new Error('Virallista sarjataulukkoa ei ole saatavilla.')
    }
    const conferences = {
        eastern: { atlantic: [], metropolitan: [] },
        western: { central: [], pacific: [] },
    }
    const seen = new Set()
    const leagueRanks = new Set()
    for (const row of snapshot.standings) {
        const team = row.teamAbbrev?.default
        const conference = CONFERENCES[row.conferenceAbbrev]
        const division = DIVISIONS[row.divisionAbbrev]
        if (
            !team ||
            seen.has(team) ||
            !conferences[conference]?.[division] ||
            row.seasonId !== snapshot.seasonId ||
            row.date !== snapshot.sourceDate ||
            row.gamesPlayed !== row.wins + row.losses + row.otLosses ||
            row.points !== 2 * row.wins + row.otLosses ||
            (row.pointPctg != null &&
                (!Number.isFinite(row.pointPctg) || row.pointPctg < 0 || row.pointPctg > 1)) ||
            ['gamesPlayed', 'wins', 'losses', 'otLosses', 'points', 'goalFor', 'goalAgainst'].some(
                (key) => !Number.isInteger(row[key]) || row[key] < 0
            ) ||
            ['divisionSequence', 'conferenceSequence', 'leagueSequence'].some(
                (key) => !Number.isInteger(row[key]) || row[key] < 1
            )
        ) {
            throw new Error('Sarjataulukon tiedot ovat puutteelliset.')
        }
        seen.add(team)
        leagueRanks.add(row.leagueSequence)
        conferences[conference][division].push({
            team,
            teamName: row.teamName?.default || team,
            gamesPlayed: row.gamesPlayed,
            wins: row.wins,
            losses: row.losses,
            overtimeLosses: row.otLosses,
            points: row.points,
            pointsPercentage: row.gamesPlayed
                ? (row.pointPctg ?? row.points / (2 * row.gamesPlayed))
                : null,
            goalsFor: row.goalFor,
            goalsAgainst: row.goalAgainst,
            goalDifferential: row.goalFor - row.goalAgainst,
            regulationWins: row.regulationWins,
            regulationPlusOTWins: row.regulationPlusOtWins,
            divisionRank: row.divisionSequence,
            conferenceRank: row.conferenceSequence,
            leagueRank: row.leagueSequence,
            streak: row.streakCode && row.streakCount ? `${row.streakCode}${row.streakCount}` : '',
            last10: ['l10Wins', 'l10Losses', 'l10OtLosses'].every(
                (key) => Number.isInteger(row[key]) && row[key] >= 0
            )
                ? `${row.l10Wins}-${row.l10Losses}-${row.l10OtLosses}`
                : null,
            clinchIndicator: row.clinchIndicator || '',
        })
    }
    if (leagueRanks.size !== 32 || Math.max(...leagueRanks) !== 32)
        throw new Error('Sarjataulukon sijoitukset ovat puutteelliset.')
    const wildCards = {}
    for (const [conference, divisions] of Object.entries(conferences)) {
        const teams = Object.values(divisions).flat()
        if (
            new Set(teams.map((team) => team.conferenceRank)).size !== 16 ||
            Math.max(...teams.map((team) => team.conferenceRank)) !== 16
        ) {
            throw new Error('Konferenssin sijoitukset ovat puutteelliset.')
        }
        for (const division of Object.values(divisions)) {
            if (
                division.length !== 8 ||
                new Set(division.map((team) => team.divisionRank)).size !== 8 ||
                Math.max(...division.map((team) => team.divisionRank)) !== 8
            ) {
                throw new Error('Divisioonan sijoitukset ovat puutteelliset.')
            }
            division.sort((a, b) => a.divisionRank - b.divisionRank)
        }
        wildCards[conference] = teams
            .filter((team) => team.divisionRank > 3)
            .sort((a, b) => a.conferenceRank - b.conferenceRank)
            .slice(0, 2)
            .map((team) => team.team)
    }
    return {
        conferences,
        metadata: {
            seasonId: snapshot.seasonId,
            sourceDate: snapshot.sourceDate,
            fetchedAt: snapshot.fetchedAt,
            source: snapshot.source,
            wildCards,
        },
    }
}

export function isStandingsStale(metadata, now = Date.now()) {
    return !metadata || now - Date.parse(metadata.fetchedAt) > 3 * 60 * 60 * 1000
}

export class StandingsService {
    async loadLatest({ force = false } = {}) {
        const response = await fetch(
            `${base}/data/standings.json${force ? `?refresh=${Date.now()}` : ''}`,
            { cache: 'no-store' }
        )
        if (!response.ok) throw new Error('Virallisen sarjataulukon lataaminen epäonnistui.')
        return adaptStandingsSnapshot(await response.json())
    }
}
