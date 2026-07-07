/* ==========================================
   房价预测系统 v2.0 - 数据看板
   ========================================== */

let dashCity = 'guangzhou';
const charts = {};

// 颜色方案
const COLORS = ['#5470c6','#91cc75','#fac858','#ee6666','#73c0de','#3ba272','#fc8452','#9a60b4','#ea7ccc','#f47920'];

function initChart(domId) {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    if (charts[domId]) { charts[domId].dispose(); }
    charts[domId] = echarts.init(dom);
    return charts[domId];
}

function resizeAll() {
    for (const k in charts) {
        if (charts[k]) charts[k].resize();
    }
}

// ============ 统计卡片 ============
function updateStatCards(data) {
    document.getElementById('statTotal').textContent = data.total_count.toLocaleString();
    document.getElementById('statAvgPrice').textContent = data.avg_price;
    document.getElementById('statMaxPrice').textContent = data.max_price;
    document.getElementById('statAvgArea').textContent = data.avg_area || '--';
}

// ============ 房价分布 ============
function renderPriceDist(data) {
    const chart = initChart('priceDistChart');
    if (!chart) return;
    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: data.labels, axisLabel: { rotate: 30, fontSize: 11 } },
        yAxis: { type: 'value', name: '房源数' },
        series: [{
            type: 'bar',
            data: data.values,
            itemStyle: {
                borderRadius: [4,4,0,0],
                color: new echarts.graphic.LinearGradient(0,0,0,1, [
                    { offset: 0, color: '#5470c6' }, { offset: 1, color: '#b7c8f0' }
                ])
            },
            label: { show: true, position: 'top', fontSize: 11 }
        }]
    }, true);
}

// ============ 各区均价 ============
function renderDistrict(data) {
    const chart = initChart('districtChart');
    if (!chart) return;
    const names = Object.keys(data).sort((a,b) => data[a] - data[b]);
    const vals = names.map(n => data[n]);

    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: p => `${p[0].name}<br/>均价: ${p[0].value} 万` },
        grid: { left: '3%', right: '10%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value', name: '均价 (万)', nameLocation: 'middle', nameGap: 25 },
        yAxis: { type: 'category', data: names, axisLabel: { fontSize: 11 } },
        series: [{
            type: 'bar',
            data: vals.map((v, i) => ({
                value: v,
                itemStyle: { color: COLORS[i % COLORS.length], borderRadius: [0,4,4,0] }
            })),
            label: { show: true, position: 'right', fontSize: 11, formatter: p => p.value + '万' }
        }]
    }, true);
}

// ============ 朝向饼图 ============
function renderToward(data) {
    const chart = initChart('towardChart');
    if (!chart) return;
    const entries = Object.entries(data).sort((a,b) => b[1] - a[1]);
    chart.setOption({
        tooltip: { trigger: 'item', formatter: p => `${p.name}: ${p.value} (${p.percent}%)` },
        legend: { orient: 'vertical', left: 'left', top: 'center', itemWidth: 10, itemHeight: 10 },
        series: [{
            type: 'pie',
            radius: ['35%', '60%'],
            center: ['55%', '50%'],
            avoidLabelOverlap: true,
            itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
            label: { show: false },
            emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
            data: entries.map(([k,v], i) => ({ name: k, value: v, itemStyle: { color: COLORS[i % COLORS.length] } }))
        }]
    }, true);
}

// ============ 户型分布 ============
function renderBedroom(data) {
    const chart = initChart('bedroomChart');
    if (!chart) return;
    const keys = Object.keys(data).map(Number).sort((a,b) => a-b);
    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: keys.map(k => k + '室') },
        yAxis: { type: 'value', name: '房源数' },
        series: [{
            type: 'bar',
            data: keys.map(k => data[k.toString()]),
            itemStyle: {
                borderRadius: [4,4,0,0],
                color: new echarts.graphic.LinearGradient(0,0,0,1, [
                    { offset: 0, color: '#91cc75' }, { offset: 1, color: '#d4edc9' }
                ])
            },
            label: { show: true, position: 'top', fontSize: 11 }
        }]
    }, true);
}

// ============ 装修分布 ============
function renderDeco(data) {
    const chart = initChart('decoChart');
    if (!chart) return;
    const entries = Object.entries(data);
    chart.setOption({
        tooltip: { trigger: 'item', formatter: p => `${p.name}: ${p.value} (${p.percent}%)` },
        legend: { bottom: 0, itemWidth: 10, itemHeight: 10 },
        series: [{
            type: 'pie',
            radius: ['0%', '70%'],
            center: ['50%', '45%'],
            itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
            label: { formatter: p => `${p.name}\n${p.percent}%`, fontSize: 11 },
            data: entries.map(([k,v], i) => ({ name: k, value: v, itemStyle: { color: COLORS[i % COLORS.length] } }))
        }]
    }, true);
}

// ============ 特征重要性 ============
function renderFeatures(features) {
    const chart = initChart('featureChart');
    if (!chart) return;
    const names = features.map(f => f.display || f.name);
    const vals = features.map(f => f.importance);
    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: p => `${p[0].name}<br/>重要性: ${(p[0].value * 100).toFixed(2)}%` },
        grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value', name: '重要性', max: Math.max(...vals) * 1.2, axisLabel: { formatter: v => (v*100).toFixed(0) + '%' } },
        yAxis: { type: 'category', data: names.reverse(), axisLabel: { fontSize: 10 } },
        series: [{
            type: 'bar',
            data: vals.reverse().map((v, i) => ({
                value: v,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0,0,1,0, [
                        { offset: 0, color: '#fac858' }, { offset: 1, color: '#ee6666' }
                    ]),
                    borderRadius: [0,4,4,0]
                }
            })),
            label: { show: true, position: 'right', fontSize: 10, formatter: p => (p.value * 100).toFixed(1) + '%' }
        }]
    }, true);
}

// ============ SH 区县表格 ============
function renderShDistrictTable(avgPrice, count) {
    const container = document.getElementById('shDistrictTable');
    if (!container) return;
    const names = Object.keys(avgPrice).sort((a,b) => avgPrice[b] - avgPrice[a]);
    let html = `<table class="table table-hover table-sm mb-0">
        <thead class="table-light"><tr><th>区</th><th class="text-end">均价 (万)</th><th class="text-end">房源数</th></tr></thead><tbody>`;
    names.forEach(n => {
        html += `<tr><td>${n}</td><td class="text-end">${avgPrice[n]}</td><td class="text-end">${count[n] || 0}</td></tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

// ============ 切换城市显示 ============
function toggleCityPanels() {
    const isGZ = dashCity === 'guangzhou';
    document.getElementById('towardPanel').style.display = isGZ ? 'block' : 'none';
    document.getElementById('shInfoPanel').style.display = isGZ ? 'none' : 'block';
    document.getElementById('gzOnlyRow').style.display = isGZ ? 'flex' : 'none';
}

// ============ 加载所有数据 ============
async function loadDashboardData() {
    toggleCityPanels();
    try {
        const [sr, fr] = await Promise.all([
            fetch('/api/stats?city=' + dashCity),
            fetch('/api/features?city=' + dashCity)
        ]);
        const statsRes = await sr.json();
        const featRes = await fr.json();

        if (!statsRes.success) return;
        const d = statsRes.data;

        // Stat cards
        updateStatCards(d);

        // Price distribution
        renderPriceDist(d.price_distribution);

        // District chart
        renderDistrict(d.area_avg_price);

        // City-specific
        if (dashCity === 'guangzhou') {
            renderToward(d.toward_distribution || {});
            renderBedroom(d.bedroom_distribution || {});
            renderDeco(d.decoration_distribution || {});
        } else {
            renderShDistrictTable(d.area_avg_price, d.area_count);
        }

        // Feature importance
        if (featRes.success) {
            renderFeatures(featRes.data);
        }

<<<<<<< HEAD
        // Prediction history trend
        loadPredTrend(dashCity);

=======
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
    } catch (e) {
        console.error('Dashboard load error:', e);
    }
}

// ============ 初始化 ============
document.addEventListener('DOMContentLoaded', function() {
    // 城市切换
    document.querySelectorAll('input[name="dashCity"]').forEach(radio => {
        radio.addEventListener('change', function() {
            dashCity = this.value;
            loadDashboardData();
<<<<<<< HEAD
            loadLatestPrediction();
=======
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
        });
    });

    loadDashboardData();
<<<<<<< HEAD
    loadLatestPrediction();
    window.addEventListener('resize', resizeAll);
});

// ============ 最新房源预测验证 ============

function renderLatestPrediction(data) {
    const status = document.getElementById('latestPredictionStatus');
    const content = document.getElementById('latestPredictionContent');

    if (!data || !data.file_exists) {
        status.style.display = 'block';
        content.style.display = 'none';
        status.innerHTML = `<span class="text-warning">⚠️ ${data ? data.message : '暂无最新房源数据'}</span>`;
        return;
    }
    if (data.count === 0) {
        status.style.display = 'block';
        content.style.display = 'none';
        status.textContent = '最新房源文件为空，请重新爬取';
        return;
    }

    status.style.display = 'none';
    content.style.display = 'block';

    document.getElementById('lpMAE').textContent = data.mae + '万';
    document.getElementById('lpRMSE').textContent = data.rmse + '万';
    document.getElementById('lpMAPE').textContent = data.mape + '%';
    document.getElementById('lpCount').textContent = data.count + '条';

    document.getElementById('lpOverPct').textContent = data.over_pct + '%';
    document.getElementById('lpOverCount').textContent = data.over_count + '条';
    document.getElementById('lpUnderPct').textContent = data.under_pct + '%';
    document.getElementById('lpUnderCount').textContent = data.under_count + '条';
    document.getElementById('lpWithin20').textContent = data.within_20_pct + '%';

    const errChart = initChart('lpErrorDistChart');
    if (errChart && data.error_distribution) {
        const ed = data.error_distribution;
        errChart.setOption({
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: { type: 'category', data: ed.map(e => e.range), axisLabel: { fontSize: 10, rotate: 0 } },
            yAxis: { type: 'value', name: '房源数' },
            series: [{
                type: 'bar', barWidth: '60%',
                data: ed.map((e, i) => ({
                    value: e.count,
                    itemStyle: {
                        color: i < 2 ? '#91cc75' : i < 4 ? '#fac858' : '#ee6666',
                        borderRadius: [3,3,0,0]
                    }
                })),
                label: { show: true, position: 'top', fontSize: 10 }
            }]
        }, true);
    }

    const binChart = initChart('lpPriceBinChart');
    if (binChart && data.price_bins) {
        const bins = data.price_bins;
        binChart.setOption({
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: { type: 'category', data: bins.map(b => b.range), axisLabel: { fontSize: 9 } },
            yAxis: { type: 'value', name: 'MAE (万)' },
            series: [{
                type: 'bar', barWidth: '50%',
                data: bins.map(b => ({
                    value: b.mae,
                    itemStyle: { color: '#5470c6', borderRadius: [3,3,0,0] }
                })),
                label: { show: true, position: 'top', fontSize: 10, formatter: p => p.value + '万' }
            }]
        }, true);
    }

    const container = document.getElementById('lpTopErrors');
    if (data.top_errors && data.top_errors.length > 0) {
        let html = `<h6 class="text-muted">偏差最大房源 (Top ${data.top_errors.length})</h6>
            <div class="table-responsive"><table class="table table-sm table-hover mb-0">
            <thead class="table-warning"><tr>
                <th>#</th><th>区域</th><th>面积</th><th class="text-end">实际总价</th>
                <th class="text-end">预测总价</th><th class="text-end">误差</th><th class="text-end">误差率</th>
            </tr></thead><tbody>`;
        data.top_errors.forEach((r, i) => {
            const errClass = Math.abs(r.error_pct) > 30 ? 'text-danger' : Math.abs(r.error_pct) > 15 ? 'text-warning' : '';
            html += `<tr>
                <td>${i+1}</td>
                <td>${r.district || '--'}</td>
                <td>${r.area || '--'}</td>
                <td class="text-end">${r.actual}万</td>
                <td class="text-end">${r.predicted}万</td>
                <td class="text-end ${errClass}">${r.error > 0 ? '+' : ''}${r.error}万</td>
                <td class="text-end ${errClass}">${r.error_pct > 0 ? '+' : ''}${r.error_pct}%</td>
            </tr>`;
        });
        html += '</tbody></table></div>';
        container.innerHTML = html;
    }
}

async function loadLatestPrediction() {
    try {
        const res = await fetch('/api/latest_prediction?city=' + dashCity);
        const json = await res.json();
        if (json.success) {
            renderLatestPrediction(json.data);
        }
    } catch (e) {
        console.error('Latest prediction error:', e);
    }
}

// ============ 预测活动趋势 ============

let predTrendChart = null;

async function loadPredTrend(city) {
    try {
        const [trendRes, statsRes] = await Promise.all([
            fetch(`/api/history/trend?city=${city}`),
            fetch(`/api/history/stats?city=${city}`),
        ]);
        const trend = await trendRes.json();
        const stats = await statsRes.json();

        const info = document.getElementById('predTrendInfo');
        if (stats.success && stats.data) {
            info.textContent = `| 共 ${stats.data.total} 次预测`;
        }

        if (!trend.success || !trend.data || trend.data.length === 0) return;

        const dom = document.getElementById('predTrendChart');
        if (!dom) return;
        if (predTrendChart) predTrendChart.dispose();
        predTrendChart = echarts.init(dom);

        const dates = trend.data.map(d => d.date);
        const avgPrices = trend.data.map(d => d.avg_price);
        const counts = trend.data.map(d => d.count);

        predTrendChart.setOption({
            tooltip: {
                trigger: 'axis',
                formatter: function(params) {
                    const i = params[0].dataIndex;
                    const d = trend.data[i];
                    return `${d.date}<br/>预测均价: ${d.avg_price}万<br/>预测次数: ${d.count}次<br/>范围: ${d.min_price}~${d.max_price}万`;
                }
            },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: { type: 'category', data: dates, axisLabel: { fontSize: 10 } },
            yAxis: { type: 'value', name: '预测均价 (万)', axisLabel: { fontSize: 10 } },
            series: [{
                type: 'line',
                smooth: true,
                data: avgPrices,
                symbol: 'diamond',
                symbolSize: 8,
                lineStyle: { width: 3, color: '#3ba272' },
                itemStyle: { color: '#3ba272' },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(59,162,114,0.3)' },
                        { offset: 1, color: 'rgba(59,162,114,0.02)' }
                    ])
                },
                markLine: {
                    silent: true,
                    data: avgPrices.length > 0 ? [{ type: 'average', name: '均值' }] : []
                }
            }]
        }, true);
    } catch (e) {
        console.error('Pred trend error:', e);
    }
}
=======
    window.addEventListener('resize', resizeAll);
});
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
