// @ts-nocheck
import { describe, expect, it } from 'vitest'
import { fiAssists, fiCount, fiGames, fiGoals, fiNoun, fiPoints } from '../utils/finnishPlural.js'

describe('finnishPlural', () => {
    it('uses the nominative singular for exactly one', () => {
        expect(fiGoals(1)).toBe('1 maali')
        expect(fiAssists(1)).toBe('1 syöttö')
        expect(fiPoints(1)).toBe('1 piste')
        expect(fiGames(1)).toBe('1 ottelu')
    })

    it('uses the partitive singular for other counts', () => {
        expect(fiGoals(0)).toBe('0 maalia')
        expect(fiGoals(2)).toBe('2 maalia')
        expect(fiGoals(21)).toBe('21 maalia')
        expect(fiAssists(3)).toBe('3 syöttöä')
        expect(fiPoints(56)).toBe('56 pistettä')
        expect(fiGames(82)).toBe('82 ottelua')
    })

    it('coerces missing and string counts', () => {
        expect(fiGoals(undefined)).toBe('0 maalia')
        expect(fiGoals(null)).toBe('0 maalia')
        expect(fiGoals('1')).toBe('1 maali')
        expect(fiGames('12')).toBe('12 ottelua')
    })

    it('falls back safely for non-numeric counts', () => {
        expect(fiCount(Number.NaN, 'maali', 'maalia')).toBe('0 maalia')
        expect(fiNoun(5, 'maali', 'maalia')).toBe('maalia')
        expect(fiNoun(1, 'maali', 'maalia')).toBe('maali')
    })
})
