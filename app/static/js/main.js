/* ==========================================
   房价预测系统 v2.0 - 双城市
   ========================================== */

let currentCity = 'guangzhou';
let districtData = {};
let cityAvgPrice = { guangzhou: 389, shanghai: 557 };
<<<<<<< HEAD
let lastFormData = null;
let lastResult = null;
let _loadingFav = false;  // 收藏加载中标志，阻止城市切换事件干扰
=======
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5

// 示例数据
const EXAMPLES = {
    guangzhou: [
        { area: 89, bedroom: 3, hall: 1, floor: 12, total_floor: 28, floor_lvl: '1', direction: '南', decoration: '精装', district: '天河', age: 8, elevator_num: 1 },
<<<<<<< HEAD
        { area: 120, bedroom: 4, hall: 2, floor: 18, total_floor: 32, floor_lvl: '2', direction: '南', decoration: '精装', district: '番禺', age: 3, elevator_num: 1 },
=======
        { area: 120, bedroom: 4, hall: 2, floor: 18, total_floor: 32, floor_lvl: '2', direction: '南北', decoration: '豪装', district: '番禺', age: 3, elevator_num: 1 },
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
        { area: 75, bedroom: 2, hall: 1, floor: 3, total_floor: 18, floor_lvl: '0', direction: '东', decoration: '简装', district: '增城', age: 12, elevator_num: 0 },
        { area: 100, bedroom: 3, hall: 1, floor: 15, total_floor: 30, floor_lvl: '1', direction: '北', decoration: '精装', district: '越秀', age: 15, elevator_num: 1 }
    ],
    shanghai: [
<<<<<<< HEAD
        { area: 90, bedroom: 2, hall: 1, floor: 12, total_floor: 28, floor_lvl: '1', direction: '南', district: '浦东', age: 10, s_cate: '陆家嘴' },
        { area: 70, bedroom: 2, hall: 1, floor: 6, total_floor: 18, floor_lvl: '1', direction: '南', district: '虹口', age: 20, s_cate: '曲阳' },
        { area: 120, bedroom: 3, hall: 2, floor: 15, total_floor: 32, floor_lvl: '1', direction: '南', district: '徐汇', age: 8, s_cate: '徐家汇' },
        { area: 55, bedroom: 1, hall: 1, floor: 8, total_floor: 24, floor_lvl: '1', direction: '东', district: '静安', age: 15, s_cate: '江宁路' }
=======
        { area: 90, bedroom: 2, hall: 1, floor: 12, total_floor: 28, floor_lvl: '1', direction: '南', decoration: '精装', district: '浦东', age: 10, elevator_num: 1, s_cate: '陆家嘴' },
        { area: 70, bedroom: 2, hall: 1, floor: 6, total_floor: 18, floor_lvl: '1', direction: '南北', decoration: '简装', district: '虹口', age: 20, elevator_num: 0, s_cate: '曲阳' },
        { area: 120, bedroom: 3, hall: 2, floor: 15, total_floor: 32, floor_lvl: '1', direction: '南', decoration: '精装', district: '徐汇', age: 8, elevator_num: 1, s_cate: '徐家汇' },
        { area: 55, bedroom: 1, hall: 1, floor: 8, total_floor: 24, floor_lvl: '1', direction: '东', decoration: '精装', district: '静安', age: 15, elevator_num: 1, s_cate: '江宁路' }
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
    ]
};

// ============ 初始化 ============
<<<<<<< HEAD
document.addEventListener('DOMContentLoaded', async function() {
    await loadDistricts('guangzhou');

    // 城市切换
    document.querySelectorAll('input[name="city"]').forEach(radio => {
        radio.addEventListener('change', async function() {
            if (_loadingFav) return;  // 收藏加载时不触发
            currentCity = this.value;
            await loadDistricts(currentCity);
            renderExamples();
            updateCityStats();
            loadFavorites();
=======
document.addEventListener('DOMContentLoaded', function() {
    loadDistricts('guangzhou');

    // 城市切换
    document.querySelectorAll('input[name="city"]').forEach(radio => {
        radio.addEventListener('change', function() {
            currentCity = this.value;
            loadDistricts(currentCity);
            renderExamples();
            updateCityStats();
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
        });
    });

    // 表单提交
    document.getElementById('predictForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await submitPrediction();
    });

    updateCityStats();
    renderExamples();
<<<<<<< HEAD
    loadFavorites();
=======
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
});

// ============ 加载行政区 ============
async function loadDistricts(city) {
    try {
        const r = await fetch('/api/districts?city=' + city);
        const res = await r.json();
        if (!res.success) return;
        districtData = res.data;

        const distSel = document.getElementById('district');
        distSel.innerHTML = '<option value="">请选择</option>';
        res.data.districts.forEach(d => {
            distSel.innerHTML += `<option>${d}</option>`;
        });

        const dirSel = document.getElementById('direction');
        dirSel.innerHTML = '';
        const dirs = res.data.directions || ['东','南','西','北','南北','东南','西南','东北','西北'];
        dirs.forEach(d => {
            if (d.length <= 3) dirSel.innerHTML += `<option>${d}</option>`;
        });

        // 城市专有字段
        if (city === 'shanghai') {
            document.getElementById('decorationGroup').style.display = 'none';
            document.getElementById('elevatorGroup').style.display = 'none';
            document.getElementById('sCateGroup').style.display = 'block';
            const scSel = document.getElementById('s_cate');
            scSel.innerHTML = '<option value="">请选择板块</option>';
            (res.data.s_cates || []).forEach(s => {
                scSel.innerHTML += `<option>${s}</option>`;
            });
        } else {
            document.getElementById('decorationGroup').style.display = 'block';
            document.getElementById('elevatorGroup').style.display = 'block';
            document.getElementById('sCateGroup').style.display = 'none';
            const decoSel = document.getElementById('decoration');
            decoSel.innerHTML = '';
            (res.data.decorations || ['毛坯','简装','精装','豪装']).forEach(d => {
                decoSel.innerHTML += `<option>${d}</option>`;
            });
        }
    } catch (e) {
        console.error('Load districts error:', e);
    }
}

// ============ 统计 ============
async function updateCityStats() {
    try {
        const r = await fetch('/api/stats?city=' + currentCity);
        const res = await r.json();
        const el = document.getElementById('cityStats');
        if (res.success) {
            cityAvgPrice[currentCity] = res.data.avg_price;
            el.textContent = `📊 ${res.data.total_count} 套房源 | 均价 ${res.data.avg_price}万`;
        }
    } catch (e) {}
}

// ============ 示例 ============
function renderExamples() {
    const list = document.getElementById('exampleList');
    list.innerHTML = '';
    const exs = EXAMPLES[currentCity] || EXAMPLES.guangzhou;
    exs.forEach((ex, i) => {
        const div = document.createElement('div');
        div.className = 'example-item';
        const badgeCls = ['bg-primary','bg-success','bg-info','bg-warning text-dark'][i];
        const label = currentCity === 'shanghai' ? ex.district : ex.district;
        div.innerHTML = `<span class="badge ${badgeCls} me-2">${label}</span> ${ex.area}m² ${ex.bedroom}室 ${ex.direction}向`;
        div.onclick = () => fillExample(i);
        list.appendChild(div);
    });
}

function fillExample(idx) {
    const ex = EXAMPLES[currentCity][idx];
    if (!ex) return;
    for (const [k, v] of Object.entries(ex)) {
        const el = document.getElementById(k);
        if (el) el.value = v;
    }
    submitPrediction();
}

// ============ 预测 ============
async function submitPrediction() {
    const formData = {
        city: currentCity,
        area: parseFloat(document.getElementById('area').value) || 0,
        bedroom: parseInt(document.getElementById('bedroom').value) || 0,
        hall: parseInt(document.getElementById('hall').value) || 0,
        floor: parseInt(document.getElementById('floor').value) || 0,
        total_floor: parseInt(document.getElementById('total_floor').value) || 1,
        floor_lvl: parseInt(document.getElementById('floor_lvl').value) || 1,
        direction: document.getElementById('direction').value,
        district: document.getElementById('district').value,
        age: parseInt(document.getElementById('age').value) || 0,
        follow_num: 50,
        visit_num: 30
    };

    if (currentCity === 'guangzhou') {
        formData.decoration = document.getElementById('decoration').value;
        formData.elevator_num = parseInt(document.getElementById('elevator').value) || 1;
    } else {
        formData.s_cate = document.getElementById('s_cate').value;
<<<<<<< HEAD
    }
    formData.floor = parseInt(document.getElementById('floor').value) || 0;
=======
        // decoration and elevator are not used in SH model
    }
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5

    // Validate
    if (!formData.area || formData.area < 15) { showAlert('请输入面积 (>=15m²)', 'warning'); return; }
    if (!formData.bedroom || formData.bedroom < 1) { showAlert('请输入卧室数', 'warning'); return; }
    if (!formData.total_floor) { showAlert('请输入总楼层', 'warning'); return; }
    if (!formData.direction) { showAlert('请选择朝向', 'warning'); return; }
    if (!formData.district) { showAlert('请选择行政区', 'warning'); return; }

    document.getElementById('waitingArea').style.display = 'none';
    document.getElementById('resultArea').style.display = 'block';
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('predictedPrice').textContent = '计算中...';

    try {
        const r = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        const result = await r.json();
        document.getElementById('loadingSpinner').style.display = 'none';

        if (result.success) {
            const p = result.predicted_price;
            document.getElementById('predictedPrice').textContent = '¥ ' + Number(p).toLocaleString('zh-CN') + ' 万';
            document.getElementById('unitPrice').textContent = Number(result.unit_price).toLocaleString('zh-CN') + ' 元/m²';
            document.getElementById('resultAreaText').textContent = result.area + ' m²';
            document.getElementById('resultTotalPrice').textContent = Number(p).toLocaleString('zh-CN') + ' 万';

            const range = document.getElementById('priceRange');
            const avg = cityAvgPrice[result.city] || (result.city === 'shanghai' ? 525 : 386);
            if (p < avg * 0.6) range.textContent = '💰 低于城市均价';
            else if (p < avg) range.textContent = '💰 略低于城市均价';
            else if (p < avg * 1.5) range.textContent = '💰 接近城市均价';
            else range.textContent = '💰 高于城市均价';
<<<<<<< HEAD

            // 保存本次预测数据用于收藏
            lastFormData = formData;
            lastResult = result;

            // 加载相似房源趋势
            loadSimilarTrend(currentCity, formData);
=======
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
        } else {
            showAlert('预测失败: ' + (result.error || '未知错误'), 'danger');
            document.getElementById('waitingArea').style.display = 'block';
            document.getElementById('resultArea').style.display = 'none';
        }
    } catch (err) {
        document.getElementById('loadingSpinner').style.display = 'none';
        showAlert('网络错误: ' + err.message, 'danger');
        document.getElementById('waitingArea').style.display = 'block';
        document.getElementById('resultArea').style.display = 'none';
    }
}

function showAlert(msg, type) {
    const div = document.createElement('div');
    div.className = 'alert alert-' + type + ' alert-dismissible fade show position-fixed';
    div.style.cssText = 'top: 80px; right: 20px; z-index: 9999; max-width: 400px;';
    div.innerHTML = `<strong>${type==='warning'?'⚠️':'❌'}</strong> ${msg} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    document.body.appendChild(div);
    setTimeout(() => { if (div.parentNode) div.remove(); }, 4000);
}
<<<<<<< HEAD

// ============ 相似房源价格趋势 ============

let trendChartInstance = null;

async function loadSimilarTrend(city, formData) {
    const card = document.getElementById('trendCard');
    if (!card) return;

    try {
        const area = formData.area || 0;
        const district = formData.district || '';
        const bedroom = formData.bedroom || 0;
        const areaLo = Math.max(0, area * 0.8).toFixed(0);
        const areaHi = (area * 1.2).toFixed(0);

        // 并行请求趋势和相似列表
        const [trendRes, similarRes, statsRes] = await Promise.all([
            fetch(`/api/history/trend?city=${city}&district=${district}&bedroom=${bedroom}&area_from=${areaLo}&area_to=${areaHi}`),
            fetch(`/api/history/similar?city=${city}&district=${district}&bedroom=${bedroom}&area=${area}&limit=5`),
            fetch(`/api/history/stats?city=${city}`),
        ]);
        const trend = await trendRes.json();
        const similar = await similarRes.json();
        const stats = await statsRes.json();

        const hasTrendData = trend.success && trend.data && trend.data.length > 0;
        const hasSimilarData = similar.success && similar.data && similar.data.length > 0;

        if (!hasTrendData && !hasSimilarData) {
            card.style.display = 'none';
            return;
        }

        card.style.display = 'block';

        // 趋势提示
        const info = document.getElementById('trendInfo');
        let infoText = `${district} ${bedroom}室 面积${areaLo}-${areaHi}m²`;
        if (stats.success && stats.data) {
            infoText += ` | 共记录 ${stats.data.total} 次预测`;
        }
        info.textContent = infoText;

        // 趋势折线图
        if (hasTrendData) {
            renderTrendChart(trend.data);
        }

        // 相似记录列表
        if (hasSimilarData) {
            const list = document.getElementById('similarList');
            let html = '<div class="text-muted mb-1">最近相似预测：</div>';
            similar.data.forEach(r => {
                html += `<div class="d-flex justify-content-between border-bottom py-1">
                    <span>${r.timestamp.slice(5)} ${r.district} ${r.room_type_label || r.area_num + 'm²'}</span>
                    <span class="fw-bold">${Number(r.predicted_price).toLocaleString()}万</span>
                </div>`;
            });
            list.innerHTML = html;
        } else {
            document.getElementById('similarList').innerHTML = '<div class="text-muted">暂无完全匹配的相似记录</div>';
        }
    } catch (e) {
        console.error('Trend load error:', e);
        document.getElementById('trendCard').style.display = 'none';
    }
}

function renderTrendChart(data) {
    const dom = document.getElementById('trendChart');
    if (!dom) return;
    if (trendChartInstance) trendChartInstance.dispose();
    trendChartInstance = echarts.init(dom);

    const dates = data.map(d => d.date);
    const avgPrices = data.map(d => d.avg_price);
    const counts = data.map(d => d.count);

    trendChartInstance.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                const i = params[0].dataIndex;
                const d = data[i];
                return `${d.date}<br/>均价: ${d.avg_price}万 (${d.count}次)<br/>范围: ${d.min_price}-${d.max_price}万`;
            }
        },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: {
            type: 'category', data: dates,
            axisLabel: { fontSize: 10 }
        },
        yAxis: {
            type: 'value', name: '预测均价 (万)',
            axisLabel: { fontSize: 10 }
        },
        series: [{
            type: 'line',
            smooth: true,
            data: avgPrices,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { width: 2, color: '#5470c6' },
            itemStyle: { color: '#5470c6' },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(84,112,198,0.4)' },
                    { offset: 1, color: 'rgba(84,112,198,0.05)' }
                ])
            },
            markLine: {
                silent: true,
                data: avgPrices.length > 0 ? [{ type: 'average', name: '均值' }] : []
            }
        }]
    }, true);
}

// ============ 我的收藏 ============

async function saveFavorite() {
    if (!lastFormData || !lastResult) return;
    const btn = document.getElementById('favBtn');
    const msg = document.getElementById('favMsg');
    btn.disabled = true;
    btn.textContent = '⏳ 收藏中...';
    try {
        const data = { ...lastFormData, ...lastResult };
        const r = await fetch('/api/favorites/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        const res = await r.json();
        if (res.success) {
            msg.style.display = 'inline';
            setTimeout(() => msg.style.display = 'none', 2000);
            loadFavorites();
        }
    } catch (e) {
        console.error('Save favorite error:', e);
    }
    btn.disabled = false;
    btn.textContent = '⭐ 收藏此房源';
}

async function loadFavorites() {
    try {
        const r = await fetch('/api/favorites/list?city=' + currentCity);
        const res = await r.json();
        const count = document.getElementById('favCount');
        const list = document.getElementById('favList');
        if (!res.success || !res.data || res.data.length === 0) {
            count.textContent = '0';
            list.innerHTML = '<p class="text-muted small mb-0">暂无收藏</p>';
            return;
        }
        count.textContent = res.count;
        let html = '<div class="list-group list-group-flush">';
        res.data.forEach(item => {
            const price = Number(item.predicted_price).toLocaleString();
            html += `<div class="list-group-item list-group-item-action px-0 d-flex justify-content-between align-items-center">
                <div class="small" style="cursor:pointer;flex:1;" onclick="loadFavoriteToForm(${item.id})">
                    <strong>${item.district}</strong> ${item.bedroom}室 ${item.area_num}m²
                    <span class="text-primary fw-bold">${price}万</span>
                    <span class="text-muted">${item.timestamp.slice(5)}</span>
                </div>
                <button class="btn btn-sm btn-outline-danger py-0 px-1" onclick="deleteFavorite(${item.id})" title="删除">✕</button>
            </div>`;
        });
        html += '</div>';
        list.innerHTML = html;
    } catch (e) {
        console.error('Load favorites error:', e);
    }
}

async function loadFavoriteToForm(id) {
    console.log('loadFavoriteToForm called with id:', id);
    try {
        const r = await fetch('/api/favorites/load?id=' + id);
        const res = await r.json();
        console.log('Load response:', res);
        if (!res.success || !res.data) {
            showAlert('加载收藏数据失败', 'danger');
            return;
        }
        const d = res.data;

        // 设置标志阻止 radio change 事件干扰
        _loadingFav = true;

        // 更新城市
        currentCity = d.city;
        document.querySelectorAll('input[name="city"]').forEach(radio => {
            radio.checked = radio.value === currentCity;
        });

        // 加载城市表单数据
        await loadDistricts(currentCity);
        _loadingFav = false;
        renderExamples();
        updateCityStats();

        // 字段映射：form元素id → API返回的key
        const fieldMap = {
            'area': 'area', 'bedroom': 'bedroom', 'hall': 'hall',
            'floor': 'floor', 'total_floor': 'total_floor',
            'floor_lvl': 'floor_lvl', 'age': 'age',
            'direction': 'direction', 'decoration': 'decoration',
            'district': 'district', 's_cate': 's_cate',
            'elevator': 'elevator_num',
        };
        for (const [elId, dataKey] of Object.entries(fieldMap)) {
            const el = document.getElementById(elId);
            if (!el) continue;
            let val = d[dataKey];
            // NaN → 空字符串，避免设置无效值
            if (val === null || val === undefined || (typeof val === 'number' && isNaN(val))) {
                val = '';
            }
            el.value = val;
        }

        // 直接重新预测
        submitPrediction();
    } catch (e) {
        console.error('Load favorite error:', e);
        showAlert('加载收藏出错: ' + e.message, 'danger');
    }
}

async function deleteFavorite(id) {
    if (!confirm('确定删除这条收藏？')) return;
    try {
        await fetch('/api/favorites/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id }),
        });
        loadFavorites();
    } catch (e) {
        console.error('Delete favorite error:', e);
    }
}

// ============ 预算推荐 ============

async function loadRecommendations() {
    const budget = document.getElementById('budgetInput').value;
    const city = document.getElementById('budgetCity').value;
    if (!budget || budget < 50) {
        alert('请输入预算（至少50万）');
        return;
    }
    const div = document.getElementById('recommendResult');
    div.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-success"></div><p class="text-muted mt-2">计算推荐中...</p></div>';

    try {
        const r = await fetch(`/api/recommend?city=${city}&budget=${budget}`);
        const res = await r.json();
        if (!res.success || !res.data || !res.data.recommendations || res.data.recommendations.length === 0) {
            div.innerHTML = '<div class="alert alert-warning mb-0">该预算下暂无合适推荐，请调整预算后重试</div>';
            return;
        }
        const recs = res.data.recommendations;
        let html = `<div class="small text-muted mb-2">预算 <strong>${Number(budget).toLocaleString()}万</strong>，共推荐 ${recs.length} 个区域</div>`;
        html += '<div class="row">';
        recs.forEach(rec => {
            const bgColor = rec.max_area >= 100 ? 'border-success' : rec.max_area >= 60 ? 'border-info' : 'border-warning';
            html += `<div class="col-md-6 mb-2">
                <div class="card ${bgColor} h-100">
                    <div class="card-header bg-white py-1 px-2 d-flex justify-content-between">
                        <strong>${rec.district}</strong>
                        <span class="text-muted small">均价 ${Number(rec.avg_price).toLocaleString()}万 | 单价 ${Number(rec.unit_price).toLocaleString()}元/m²</span>
                    </div>
                    <div class="card-body p-2">
                        <div class="small mb-1">预算可买 <strong>约${rec.max_area}m²</strong></div>`;
            rec.configs.forEach(cfg => {
                html += `<span class="badge bg-light text-dark me-1 mb-1 border" style="cursor:pointer;" onclick="fillFromRecommend('${city}','${rec.district}',${cfg.bedroom},${cfg.hall},${cfg.area})">
                    ${cfg.label} ${cfg.area}m² ≈ ${Number(cfg.estimated_price).toLocaleString()}万
                    ${cfg.remaining >= 0 ? `<span class="text-success">(余${Number(cfg.remaining).toLocaleString()}万)</span>` : `<span class="text-danger">(超${Number(Math.abs(cfg.remaining)).toLocaleString()}万)</span>`}
                </span>`;
            });
            html += `</div></div></div>`;
        });
        html += '</div>';
        div.innerHTML = html;
    } catch (e) {
        div.innerHTML = '<div class="alert alert-danger mb-0">获取推荐失败</div>';
        console.error('Recommend error:', e);
    }
}

function fillFromRecommend(city, district, bedroom, hall, area) {
    const cityRadio = document.getElementById(city === 'shanghai' ? 'citySH' : 'cityGZ');
    if (cityRadio) {
        cityRadio.checked = true;
        currentCity = city;
    }
    // 切换城市后异步加载表单，得等加载完成后填充
    const waitAndFill = async () => {
        await loadDistricts(currentCity);
        renderExamples();
        document.getElementById('area').value = area;
        document.getElementById('bedroom').value = bedroom;
        document.getElementById('hall').value = hall;
        document.getElementById('district').value = district;
        document.getElementById('total_floor').value = Math.max(Math.round(area / 4), 6);
        document.getElementById('floor').value = Math.round(document.getElementById('total_floor').value / 2);
        document.getElementById('floor_lvl').value = '1';
        document.getElementById('age').value = 10;
        document.getElementById('direction').value = '南';
        if (document.getElementById('decoration')) document.getElementById('decoration').value = '精装';
        if (document.getElementById('elevator')) document.getElementById('elevator').value = '1';
        submitPrediction();
    };
    waitAndFill();
}
=======
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
