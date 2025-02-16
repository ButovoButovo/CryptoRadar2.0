import { analyzeMarket } from './src/bybitSignalCalc.js';

const formatNumber = (value, precision = 2) => 
    value?.toFixed?.(precision) || 'N/A';

const displayAnalysis = (results) => {
    console.log('\n📊 Market Analysis Report');
    console.log('=============================================');

    Object.values(results).forEach(({
        symbol,
        ema14,
        ema200,
        atr,
        bollinger,
        vwap,
        trendSlope
    }) => {
        console.log(`\n🔹 ${symbol}`);
        console.log('---------------------------------------------');
        console.log(`EMA 14       | ${formatNumber(ema14.slice(-1)[0])}`);
        console.log(`EMA 200      | ${formatNumber(ema200.slice(-1)[0])}`);
        console.log(`ATR          | ${formatNumber(atr.slice(-1)[0], 4)}`);
        console.log(`BB Upper     | ${formatNumber(bollinger.upper.slice(-1)[0])}`);
        console.log(`BB Middle    | ${formatNumber(bollinger.middle.slice(-1)[0])}`);
        console.log(`BB Lower     | ${formatNumber(bollinger.lower.slice(-1)[0])}`);
        console.log(`VWAP         | ${formatNumber(vwap.slice(-1)[0])}`);
        console.log(`Trend Slope  | ${trendSlope.m.toExponential(2)}`);
    });

    console.log(`\n✅ Valid symbols: ${Object.keys(results).length}`);
};

(async () => {
    try {
        console.log('🚀 Starting market analysis...');
        const startTime = Date.now();
        
        const analysisResults = await analyzeMarket();
        
        console.log(`⏱  Analysis completed in ${((Date.now() - startTime)/1000).toFixed(1)}s`);
        displayAnalysis(analysisResults);
        
    } catch (error) {
        console.error('💥 Critical error:', error.message);
        process.exit(1);
    }
})();