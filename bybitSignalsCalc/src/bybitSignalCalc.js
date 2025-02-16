import * as ss from 'simple-statistics';
import tulind from 'tulind';
import { getMarketData } from './db.js';

const INDICATOR_CONFIG = {
    emaPeriods: [14, 200],
    bollingerParams: [20, 2],
    atrPeriod: 14,
    vwapWindow: 20
};

async function calculateTulindIndicator(indicator, inputs, params) {
    return new Promise((resolve) => {
        indicator.indicator(inputs, params, (err, res) => {
            err ? resolve(null) : resolve(res.flat());
        });
    });
}

export async function calculateIndicatorsForSymbol(symbol, candles) {
    try {
        if (!candles || candles.length < INDICATOR_CONFIG.vwapWindow) {
            return null;
        }

        const closes = candles.map(c => c.close);
        const highs = candles.map(c => c.high);
        const lows = candles.map(c => c.low);
        const volumes = candles.map(c => c.volume);

        const [ema14, ema200, atr, bb] = await Promise.all([
            calculateTulindIndicator(tulind.indicators.ema, [closes], [INDICATOR_CONFIG.emaPeriods[0]]),
            calculateTulindIndicator(tulind.indicators.ema, [closes], [INDICATOR_CONFIG.emaPeriods[1]]),
            calculateTulindIndicator(tulind.indicators.atr, [highs, lows, closes], [INDICATOR_CONFIG.atrPeriod]),
            calculateTulindIndicator(tulind.indicators.bbands, [closes], INDICATOR_CONFIG.bollingerParams)
        ]);

        if (!ema14 || !ema200 || !atr || !bb) {
            return null;
        }

        return {
            symbol,
            timestamps: candles.map(c => c.timestamp),
            ema14,
            ema200,
            atr,
            bollinger: { upper: bb[0], middle: bb[1], lower: bb[2] },
            vwap: calculateVWAP(candles, volumes),
            trendSlope: calculateTrendSlope(closes)
        };
    } catch (error) {
        console.error(`❌ Indicator error for ${symbol}:`, error.message);
        return null;
    }
}

function calculateVWAP(candles, volumes) {
    return candles.map((_, i) => {
        if (i < INDICATOR_CONFIG.vwapWindow - 1) return null;
        const window = candles.slice(i - INDICATOR_CONFIG.vwapWindow + 1, i + 1);
        const totalVolume = window.reduce((sum, c, idx) => sum + volumes[i - INDICATOR_CONFIG.vwapWindow + 1 + idx], 0);
        return window.reduce((sum, c, idx) => 
            sum + ((c.high + c.low + c.close)/3) * volumes[i - INDICATOR_CONFIG.vwapWindow + 1 + idx], 0
        ) / totalVolume;
    });
}

function calculateTrendSlope(closes) {
    try {
        return ss.linearRegression(closes.map((c, i) => [i, c]));
    } catch (e) {
        return { m: 0, b: 0 };
    }
}

export async function analyzeMarket(hours = 200) {
    try {
        const marketData = await getMarketData(hours);
        const results = {};

        await Promise.all(
            Object.entries(marketData).map(async ([symbol, candles]) => {
                const analysis = await calculateIndicatorsForSymbol(symbol, candles);
                if (analysis) {
                    results[symbol] = analysis;
                }
            })
        );

        return results;
    } catch (error) {
        console.error('❌ Market analysis failed:', error.message);
        return {};
    }
}