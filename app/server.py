"""
房价预测系统 - Flask 入口
v2.0：支持广州 + 上海双城市预测
"""
<<<<<<< HEAD
import re, os, csv, numpy as np
from datetime import datetime
=======
import re, os, numpy as np
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
from flask import Flask, render_template, jsonify, request
import joblib
import pandas as pd

app = Flask(__name__)

# 使用相对于脚本的路径，保证跨机器可移植
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'model')

# ==================== 加载广州模型 ====================
gz_model = joblib.load(os.path.join(MODEL_DIR, 'best_model.pkl'))
gz_scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
gz_features = joblib.load(os.path.join(MODEL_DIR, 'feature_cols.pkl'))
gz_encoders = joblib.load(os.path.join(MODEL_DIR, 'encoders.pkl'))
print(f'[Guangzhou] Model: {type(gz_model).__name__}, Features: {len(gz_features)}')

# ==================== 加载上海模型 ====================
sh_model = joblib.load(os.path.join(MODEL_DIR, 'sh_model.pkl'))
sh_scaler = joblib.load(os.path.join(MODEL_DIR, 'sh_scaler.pkl'))
sh_features = joblib.load(os.path.join(MODEL_DIR, 'sh_feature_cols.pkl'))
sh_encoders = joblib.load(os.path.join(MODEL_DIR, 'sh_encoders.pkl'))
print(f'[Shanghai] Model: {type(sh_model).__name__}, Features: {len(sh_features)}')

# ==================== 加载统计数据 ====================
df_gz = pd.read_csv(os.path.join(MODEL_DIR, 'filtered_data.csv'), encoding='utf-8-sig')
# Shanghai: load raw and parse
df_sh_raw = pd.read_csv(os.path.join(BASE_DIR, '上海链家二手房.csv'), encoding='utf-8')

<<<<<<< HEAD
# ==================== 预测历史记录 ====================
HISTORY_FILE = os.path.join(BASE_DIR, '预测历史.csv')
HISTORY_COLS = [
    'id', 'timestamp', 'city', 'district', 'bedroom', 'hall', 'area_num',
    'floor_lvl', 'total_floor', 'house_age', 'direction',
    'decoration', 'elevator_num', 's_cate',
    'predicted_price', 'unit_price', 'room_type_label',
]

def init_history():
    """初始化预测历史CSV文件"""
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(HISTORY_COLS)

def save_prediction(data, predicted_price, unit_price):
    """保存一条预测记录到历史CSV"""
    init_history()
    # 读取当前最大id
    max_id = 0
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                try:
                    max_id = max(max_id, int(row.get('id', 0)))
                except ValueError:
                    pass
    except Exception:
        pass

    new_id = max_id + 1
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    city = data.get('city', 'guangzhou')
    bedroom = int(data.get('bedroom', 0))
    hall = int(data.get('hall', 0))
    room_type_label = f'{bedroom}室{hall}厅'

    row = {
        'id': new_id, 'timestamp': ts,
        'city': city, 'district': data.get('district', ''),
        'bedroom': bedroom, 'hall': hall,
        'area_num': float(data.get('area', 0)),
        'floor_lvl': int(data.get('floor_lvl', 1)),
        'total_floor': int(data.get('total_floor', 1)),
        'house_age': int(data.get('age', 10)),
        'direction': data.get('direction', '南'),
        'decoration': data.get('decoration', ''),
        'elevator_num': int(data.get('elevator_num', 1)),
        's_cate': data.get('s_cate', ''),
        'predicted_price': round(predicted_price, 2),
        'unit_price': round(unit_price, 0),
        'room_type_label': room_type_label,
    }

    with open(HISTORY_FILE, 'a', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=HISTORY_COLS)
        w.writerow(row)
    return new_id

=======
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
# ==================== 特征构建 ====================

def build_gz_features(data):
    area_num = float(data.get('area', 0))
    bedroom = int(data.get('bedroom', 0))
    hall = int(data.get('hall', 0))
    floor_lvl = int(data.get('floor_lvl', 1))
    total_floor = int(data.get('total_floor', 1))
    house_age = int(data.get('age', 10))
    follow_num = float(data.get('follow_num', 50))
    visit_num = float(data.get('visit_num', 30))
    elevator_num = int(data.get('elevator_num', 1))
    direction = data.get('direction', '南')
    district = data.get('district', '天河')
    decoration = data.get('decoration', '精装')

    def safe(encoder, value):
        return encoder.transform([value])[0] if value in encoder.classes_ else 0

    vals = {
        'bedroom': bedroom, 'hall': hall, 'area_num': area_num,
        'room_total': bedroom + hall,
        'floor_lvl': floor_lvl, 'total_floor': total_floor,
        'floor_ratio': floor_lvl / max(total_floor, 1),
        'house_age': house_age, 'follow_num': follow_num,
        'visit_num': visit_num, 'elevator_num': elevator_num,
        'area_code': safe(gz_encoders['area'], district),
        'toward_code': safe(gz_encoders['toward'], direction),
        'deco_code': safe(gz_encoders['decoration'], decoration),
        'street_code': 0,
        'area_log': np.log1p(area_num)
    }
<<<<<<< HEAD
    X = pd.DataFrame([[vals[c] for c in gz_features]], columns=gz_features)
=======
    X = np.array([[vals[c] for c in gz_features]])
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
    return gz_scaler.transform(X), vals


def build_sh_features(data):
    area_num = float(data.get('area', 0))
    bedroom = int(data.get('bedroom', 0))
    hall = int(data.get('hall', 0))
    floor_lvl = int(data.get('floor_lvl', 1))
    total_floor = int(data.get('total_floor', 1))
    house_age = int(data.get('age', 10))
    direction = data.get('direction', '南')
    district = data.get('district', '浦东')
    s_cate = data.get('s_cate', '')

    def safe(encoder, value):
        return encoder.transform([value])[0] if value in encoder.classes_ else 0

    # Shanghai direction may be "朝南" or just "南"
    if direction.startswith('朝'):
        direction = direction[1:]

    vals = {
        'bedroom': bedroom, 'hall': hall, 'area_num': area_num,
        'room_total': bedroom + hall,
        'floor_lvl': floor_lvl, 'total_floor': total_floor,
        'floor_ratio': floor_lvl / max(total_floor, 1),
        'house_age': house_age,
        'district_code': safe(sh_encoders['district'], district),
        'direction_code': safe(sh_encoders['direction'], direction),
        's_cate_code': safe(sh_encoders['s_cate'], s_cate),
        'area_log': np.log1p(area_num)
    }
<<<<<<< HEAD
    X = pd.DataFrame([[vals[c] for c in sh_features]], columns=sh_features)
=======
    X = np.array([[vals[c] for c in sh_features]])
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
    return sh_scaler.transform(X), vals


# ==================== 页面路由 ====================


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# ==================== API ====================


@app.route('/api/cities')
def api_cities():
    """返回支持的城市列表"""
    return jsonify({
        'success': True,
        'data': {
            'cities': [
                {'id': 'guangzhou', 'name': '广州'},
                {'id': 'shanghai', 'name': '上海'}
            ]
        }
    })


@app.route('/api/districts')
def api_districts():
    """返回指定城市的行政区列表"""
    city = request.args.get('city', 'guangzhou')
    if city == 'shanghai':
        districts = sorted([d.replace('二手房', '') for d in df_sh_raw['district'].unique()])
        s_cates = sorted(df_sh_raw['s_cate'].unique())
        return jsonify({
            'success': True,
            'data': {
                'districts': [d for d in districts if d not in ('上海周边',)],
                's_cates': s_cates,
                'decorations': [],  # not available in SH model
                'directions': sh_encoders['direction'].classes_.tolist()
            }
        })
    else:
        return jsonify({
            'success': True,
            'data': {
                'districts': gz_encoders['area'].classes_.tolist(),
                'decorations': gz_encoders['decoration'].classes_.tolist(),
                'directions': gz_encoders['toward'].classes_.tolist(),
                's_cates': []
            }
        })


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data'})

        city = data.get('city', 'guangzhou')

        if city == 'shanghai':
            X, vals = build_sh_features(data)
            price = float(sh_model.predict(X)[0])
        else:
            X, vals = build_gz_features(data)
            price = float(gz_model.predict(X)[0])

        area = vals['area_num']
        unit_price = price / area * 10000 if area > 0 else 0

<<<<<<< HEAD
        # 保存预测历史
        save_prediction(data, price, unit_price)

=======
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
        return jsonify({
            'success': True,
            'predicted_price': round(price, 1),
            'unit_price': round(unit_price, 0),
            'area': area,
            'city': city
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/stats')
def api_stats():
    """统计数据"""
    city = request.args.get('city', 'guangzhou')
    try:
        price_bins = [0, 100, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000]
        price_labels = ['<100', '100-200', '200-300', '300-400', '400-500',
                        '500-600', '600-800', '800-1000', '1000-1500', '1500-2000', '2000+']

        if city == 'shanghai':
            df = df_sh_raw.copy()
            df['price'] = pd.to_numeric(df['house_price'], errors='coerce')
            df = df[(df['price'] > 0) & (df['price'] < 3000)]
            df['district_clean'] = df['district'].str.replace('二手房', '')

            # Parse area from house_desc
            def parse_area(desc):
                if pd.isna(desc): return 0
                m = re.search(r'\|(\d+\.?\d*)平', str(desc))
                return float(m.group(1)) if m else 0
            df['area_num'] = df['house_desc'].apply(parse_area)

            # Price distribution
            df['price_bin'] = pd.cut(df['price'], bins=price_bins,
                                     labels=price_labels, right=False)
            price_dist = df['price_bin'].value_counts().reindex(price_labels).fillna(0).tolist()

            # District avg price
            dist_avg = df.groupby('district_clean')['price'].agg(['mean','count']).round(1)
            dist_avg = dist_avg.sort_values('mean', ascending=False)

            return jsonify({
                'success': True,
                'city': 'shanghai',
                'data': {
                    'total_count': int(len(df)),
                    'avg_price': float(round(df['price'].mean(), 1)),
                    'max_price': float(round(df['price'].max(), 1)),
                    'min_price': float(round(df['price'].min(), 1)),
                    'avg_area': float(round(df['area_num'].mean(), 1)) if len(df) > 0 else 0,
                    'price_distribution': {
                        'labels': price_labels,
                        'values': [int(v) for v in price_dist]
                    },
                    'area_avg_price': {str(k): float(v) for k, v in dist_avg['mean'].to_dict().items()},
                    'area_count': {str(k): int(v) for k, v in dist_avg['count'].to_dict().items()},
                    'top_districts': [str(d) for d in dist_avg.head(5).index.tolist()]
                }
            })
        else:
            df_gz['price_bin'] = pd.cut(df_gz['price'], bins=price_bins,
                                        labels=price_labels, right=False)
            price_dist = df_gz['price_bin'].value_counts().reindex(price_labels).fillna(0).tolist()

            dist_avg = df_gz.groupby('area')['price'].agg(['mean','count']).round(1)
            dist_avg = dist_avg.sort_values('mean', ascending=False)

            toward_dist = df_gz['toward_clean'].value_counts().head(8)
            deco_dist = df_gz['deco_clean'].value_counts()
            br_dist = df_gz['bedroom'].value_counts().sort_index()

            return jsonify({
                'success': True,
                'city': 'guangzhou',
                'data': {
                    'total_count': len(df_gz),
                    'avg_price': round(float(df_gz['price'].mean()), 1),
                    'max_price': round(float(df_gz['price'].max()), 1),
                    'min_price': round(float(df_gz['price'].min()), 1),
                    'avg_area': round(float(df_gz['area_num'].mean()), 1),
                    'avg_age': round(float(df_gz['house_age'].mean()), 1),
                    'price_distribution': {
                        'labels': price_labels,
                        'values': [int(v) for v in price_dist]
                    },
                    'area_avg_price': {str(k): float(v) for k, v in dist_avg['mean'].to_dict().items()},
                    'area_count': {str(k): int(v) for k, v in dist_avg['count'].to_dict().items()},
                    'top_districts': dist_avg.head(5).index.tolist(),
                    'toward_distribution': {str(k): int(v) for k, v in toward_dist.to_dict().items()},
                    'decoration_distribution': {str(k): int(v) for k, v in deco_dist.to_dict().items()},
                    'bedroom_distribution': {str(k): int(v) for k, v in br_dist.to_dict().items()}
                }
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/features')
def api_features():
    """返回模型特征重要性（含中文显示名）"""
    FEATURE_NAMES = {
        'area_num': '面积', 'area_log': '面积(对数)',
        'area_code': '行政区', 'street_code': '街道',
        'total_floor': '总楼层', 'house_age': '房龄',
        'follow_num': '关注数', 'visit_num': '看房数',
        'floor_ratio': '楼层比', 'toward_code': '朝向',
        'elevator_num': '电梯', 'room_total': '房间总数',
        'bedroom': '卧室数', 'deco_code': '装修',
        'hall': '厅数', 'floor_lvl': '楼层位置',
        'district_code': '行政区', 's_cate_code': '板块',
        'direction_code': '朝向',
    }
    city = request.args.get('city', 'guangzhou')
    try:
        model = sh_model if city == 'shanghai' else gz_model
        features = sh_features if city == 'shanghai' else gz_features

        if hasattr(model, 'feature_importances_'):
            pairs = sorted(zip(features, model.feature_importances_.tolist()),
                           key=lambda x: x[1], reverse=True)
            return jsonify({
                'success': True,
                'data': [{'name': f[0], 'display': FEATURE_NAMES.get(f[0], f[0]),
                          'importance': round(f[1], 4)} for f in pairs]
            })
        return jsonify({'success': False, 'error': '模型不支持特征重要性'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


<<<<<<< HEAD
# ==================== 最新房源预测验证 ====================

def _extract_rooms(text):
    b = re.search(r'(\d+)室', str(text))
    h = re.search(r'(\d+)厅', str(text))
    return int(b.group(1)) if b else 0, int(h.group(1)) if h else 0


def _extract_floor(text):
    if not text:
        return 1, 0
    lvl = re.search(r'[低中高]', str(text))
    total = re.search(r'(\d+)层', str(text))
    level = lvl.group(0) if lvl else '中'
    t = int(total.group(1)) if total else 1
    return (0 if '低' in level else (2 if '高' in level else 1), t)


def _extract_area(text):
    m = re.search(r'([\d.]+)平', str(text))
    return float(m.group(1)) if m else 0


def _predict_latest_gz(row):
    """解析爬虫最新数据一行 → 预测 → 返回 (predicted, actual, area)"""
    try:
        bedroom, hall = _extract_rooms(row.get('room_type', ''))
        area_num = _extract_area(row.get('acreage', ''))
        floor_lvl, total_floor = _extract_floor(row.get('floor', ''))
        toward = row.get('toward', '南')
        deco = row.get('decoration', '精装')
        area = row.get('area', '')
        street = row.get('street', '')
        elevator = row.get('elevator', '有')
        actual = float(row.get('price', '0'))

        def safe(encoder, value):
            return encoder.transform([value])[0] if value in encoder.classes_ else 0

        vals = {
            'bedroom': bedroom, 'hall': hall, 'area_num': area_num,
            'room_total': bedroom + hall,
            'floor_lvl': floor_lvl, 'total_floor': total_floor,
            'floor_ratio': floor_lvl / max(total_floor, 1),
            'house_age': 10, 'follow_num': 50, 'visit_num': 30,
            'elevator_num': 1 if '有' in elevator else 0,
            'area_code': safe(gz_encoders['area'], area),
            'toward_code': safe(gz_encoders['toward'], toward),
            'deco_code': safe(gz_encoders['decoration'], deco),
            'street_code': safe(gz_encoders['street'], street),
            'area_log': np.log1p(area_num),
        }
        X = pd.DataFrame([[vals[c] for c in gz_features]], columns=gz_features)
        predicted = float(gz_model.predict(gz_scaler.transform(X))[0])
        return predicted, actual, area_num
    except Exception:
        return None, None, None


def _predict_latest_sh(row):
    """解析爬虫最新数据一行 → 预测 → 返回 (predicted, actual, area)"""
    try:
        desc = row.get('house_desc', '')
        parts = desc.split('|')
        bedroom, hall = _extract_rooms(parts[0] if len(parts) > 0 else '')
        area_num = _extract_area(parts[1] if len(parts) > 1 else '')
        floor_lvl, total_floor = 1, 1
        direction = '南'
        if len(parts) > 2:
            floor_lvl, total_floor = _extract_floor(parts[2])
        if len(parts) > 3:
            direction = parts[3].replace('朝', '').strip()
        district = row.get('district', '').replace('二手房', '')
        s_cate = row.get('s_cate', '')
        actual = float(row.get('house_price', '0'))

        def safe(encoder, value):
            return encoder.transform([value])[0] if value in encoder.classes_ else 0

        vals = {
            'bedroom': bedroom, 'hall': hall, 'area_num': area_num,
            'room_total': bedroom + hall,
            'floor_lvl': floor_lvl, 'total_floor': total_floor,
            'floor_ratio': floor_lvl / max(total_floor, 1),
            'house_age': 10,
            'district_code': safe(sh_encoders['district'], district),
            'direction_code': safe(sh_encoders['direction'], direction),
            's_cate_code': safe(sh_encoders['s_cate'], s_cate),
            'area_log': np.log1p(area_num),
        }
        X = pd.DataFrame([[vals[c] for c in sh_features]], columns=sh_features)
        predicted = float(sh_model.predict(sh_scaler.transform(X))[0])
        return predicted, actual, area_num
    except Exception:
        return None, None, None


@app.route('/api/latest_prediction')
def api_latest_prediction():
    """读取最新爬取的数据，逐条预测并与实际价格对比"""
    city = request.args.get('city', 'guangzhou')
    city_name = '广州' if city == 'guangzhou' else '上海'
    filename = os.path.join(BASE_DIR, f'最新房源_{city_name}.csv')

    if not os.path.exists(filename):
        return jsonify({'success': True, 'data': {'file_exists': False,
            'message': f'暂无最新房源数据，请先运行爬虫: python lianjia_crawler.py --city {city} --latest'}})

    predict_fn = _predict_latest_gz if city == 'guangzhou' else _predict_latest_sh
    results = []

    with open(filename, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            predicted, actual, area = predict_fn(row)
            if predicted is not None and actual > 0:
                results.append({
                    'actual': actual,
                    'predicted': round(predicted, 1),
                    'area': area,
                    'district': row.get('area', row.get('district', '')),
                })

    if not results:
        return jsonify({'success': True, 'data': {'file_exists': True, 'count': 0}})

    actuals = np.array([r['actual'] for r in results])
    predicted = np.array([r['predicted'] for r in results])
    errors = predicted - actuals
    abs_errors = np.abs(errors)
    pct_errors = (errors / actuals) * 100

    # 按价格区间分组
    price_bins = [(0, 200), (200, 400), (400, 600), (600, 1000), (1000, 9999)]
    bin_stats = []
    for lo, hi in price_bins:
        mask = (actuals >= lo) & (actuals < hi)
        n = int(mask.sum())
        if n == 0:
            continue
        bin_stats.append({
            'range': f'{lo}-{hi}万', 'count': n,
            'mae': round(float(np.mean(abs_errors[mask])), 1),
            'mape': round(float(np.mean(np.abs(pct_errors[mask]))), 1),
        })

    # 误差分布
    error_bins = [0, 5, 10, 15, 20, 30, 50, 100]
    error_dist = []
    for i, eb in enumerate(error_bins):
        hi_pct = error_bins[i + 1] if i + 1 < len(error_bins) else 999
        cnt = int(np.sum((np.abs(pct_errors) >= eb) & (np.abs(pct_errors) < hi_pct)))
        error_dist.append({'range': f'{eb}-{hi_pct}%' if hi_pct < 999 else f'{eb}%+', 'count': cnt})

    # Top 10 偏差
    top_errors = []
    sorted_idx = np.argsort(np.abs(errors))[::-1][:10]
    for idx in sorted_idx:
        r = results[idx]
        top_errors.append({
            'actual': r['actual'], 'predicted': r['predicted'],
            'error': round(float(errors[idx]), 1),
            'error_pct': round(float(pct_errors[idx]), 1),
            'area': r['area'], 'district': r['district'],
        })

    return jsonify({
        'success': True,
        'data': {
            'file_exists': True,
            'city': city,
            'count': len(results),
            'mae': round(float(np.mean(abs_errors)), 1),
            'rmse': round(float(np.sqrt(np.mean(errors ** 2))), 1),
            'mape': round(float(np.mean(np.abs(pct_errors))), 1),
            'median_error': round(float(np.median(abs_errors)), 1),
            'bias_mean': round(float(np.mean(errors)), 1),
            'bias_median': round(float(np.median(errors)), 1),
            'over_count': int(np.sum(errors > 0)),
            'under_count': int(np.sum(errors < 0)),
            'over_pct': round(float(np.sum(errors > 0) / len(results) * 100), 1),
            'under_pct': round(float(np.sum(errors < 0) / len(results) * 100), 1),
            'within_10_pct': round(float(np.sum(np.abs(pct_errors) <= 10) / len(results) * 100), 1),
            'within_20_pct': round(float(np.sum(np.abs(pct_errors) <= 20) / len(results) * 100), 1),
            'within_30_pct': round(float(np.sum(np.abs(pct_errors) <= 30) / len(results) * 100), 1),
            'within_10_count': int(np.sum(np.abs(pct_errors) <= 10)),
            'within_20_count': int(np.sum(np.abs(pct_errors) <= 20)),
            'within_30_count': int(np.sum(np.abs(pct_errors) <= 30)),
            'price_bins': bin_stats,
            'error_distribution': error_dist,
            'top_errors': top_errors,
        }
    })


# ==================== 预测历史趋势 ====================

@app.route('/api/history/trend')
def api_history_trend():
    """返回相似房源的价格趋势（按天聚合）"""
    city = request.args.get('city', 'guangzhou')
    district = request.args.get('district', '')
    bedroom = request.args.get('bedroom', '')
    area_from = request.args.get('area_from', '')
    area_to = request.args.get('area_to', '')

    if not os.path.exists(HISTORY_FILE):
        return jsonify({'success': True, 'data': []})

    try:
        df = pd.read_csv(HISTORY_FILE, encoding='utf-8-sig')
    except Exception:
        return jsonify({'success': True, 'data': []})

    if df.empty:
        return jsonify({'success': True, 'data': []})

    # 过滤
    df = df[df['city'] == city]
    if district:
        df = df[df['district'] == district]
    if bedroom:
        df = df[df['bedroom'] == int(bedroom)]
    if area_from:
        df = df[df['area_num'] >= float(area_from)]
    if area_to:
        df = df[df['area_num'] <= float(area_to)]

    if df.empty:
        return jsonify({'success': True, 'data': []})

    # 按日期聚合
    df['date'] = pd.to_datetime(df['timestamp']).dt.strftime('%m-%d')
    daily = df.groupby('date')['predicted_price'].agg(['mean', 'count', 'min', 'max']).reset_index()
    daily = daily.sort_values('date')

    return jsonify({
        'success': True,
        'data': [{
            'date': r['date'],
            'avg_price': round(float(r['mean']), 1),
            'count': int(r['count']),
            'min_price': round(float(r['min']), 1),
            'max_price': round(float(r['max']), 1),
        } for _, r in daily.iterrows()]
    })


@app.route('/api/history/similar')
def api_history_similar():
    """查询与指定条件相似的最近预测记录"""
    city = request.args.get('city', 'guangzhou')
    district = request.args.get('district', '')
    bedroom = request.args.get('bedroom', '')
    area = float(request.args.get('area', 0))
    limit = int(request.args.get('limit', 5))

    if not os.path.exists(HISTORY_FILE):
        return jsonify({'success': True, 'data': [], 'count': 0})

    try:
        df = pd.read_csv(HISTORY_FILE, encoding='utf-8-sig')
    except Exception:
        return jsonify({'success': True, 'data': [], 'count': 0})

    if df.empty:
        return jsonify({'success': True, 'data': [], 'count': 0})

    # 筛选相似房源：同城市 + 同行政区 + 同卧室数 + 面积±20%
    mask = (df['city'] == city)
    if district:
        mask &= (df['district'] == district)
    if bedroom:
        mask &= (df['bedroom'] == int(bedroom))
    if area > 0:
        lo, hi = area * 0.8, area * 1.2
        mask &= (df['area_num'] >= lo) & (df['area_num'] <= hi)

    similar = df[mask].sort_values('timestamp', ascending=False).head(limit)

    return jsonify({
        'success': True,
        'count': len(similar),
        'data': [{
            'id': int(r['id']),
            'timestamp': r['timestamp'],
            'district': r['district'],
            'area_num': float(r['area_num']),
            'room_type_label': r.get('room_type_label', ''),
            'predicted_price': float(r['predicted_price']),
        } for _, r in similar.iterrows()]
    })


@app.route('/api/history/stats')
def api_history_stats():
    """获取预测历史统计"""
    city = request.args.get('city', 'guangzhou')

    if not os.path.exists(HISTORY_FILE):
        return jsonify({'success': True, 'data': {'total': 0, 'today': 0, 'this_week': 0}})

    try:
        df = pd.read_csv(HISTORY_FILE, encoding='utf-8-sig')
    except Exception:
        return jsonify({'success': True, 'data': {'total': 0, 'today': 0, 'this_week': 0}})

    if df.empty:
        return jsonify({'success': True, 'data': {'total': 0, 'today': 0, 'this_week': 0}})

    df_city = df[df['city'] == city]
    today = datetime.now().strftime('%Y-%m-%d')

    total = len(df_city)
    today_count = len(df_city[df_city['timestamp'].str.startswith(today)])

    return jsonify({
        'success': True,
        'data': {
            'total': total,
            'today': int(today_count),
            'districts': df_city['district'].value_counts().head(10).to_dict(),
        }
    })


# ==================== 我的收藏 ====================

FAVORITES_FILE = os.path.join(BASE_DIR, '我的收藏.csv')
FAVORITES_COLS = [
    'id', 'timestamp', 'city', 'district', 'bedroom', 'hall', 'area_num',
    'floor', 'floor_lvl', 'total_floor', 'house_age', 'direction',
    'decoration', 'elevator_num', 's_cate',
    'predicted_price', 'unit_price', 'note',
]


def init_favorites():
    if not os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(FAVORITES_COLS)


@app.route('/api/favorites/list')
def api_favorites_list():
    city = request.args.get('city', '')
    if not os.path.exists(FAVORITES_FILE):
        return jsonify({'success': True, 'data': [], 'count': 0})
    try:
        df = pd.read_csv(FAVORITES_FILE, encoding='utf-8-sig')
    except Exception:
        return jsonify({'success': True, 'data': [], 'count': 0})
    if city:
        df = df[df['city'] == city]
    items = []
    for _, r in df.iterrows():
        items.append({
            'id': int(r['id']), 'timestamp': r['timestamp'],
            'city': r['city'], 'district': r['district'],
            'bedroom': int(r['bedroom']), 'hall': int(r['hall']),
            'area_num': float(r['area_num']),
            'predicted_price': float(r['predicted_price']),
            'unit_price': float(r['unit_price']),
            'note': '' if pd.isna(r.get('note', '')) else str(r.get('note', '')),
        })
    return jsonify({'success': True, 'data': items[::-1], 'count': len(items)})


@app.route('/api/favorites/save', methods=['POST'])
def api_favorites_save():
    init_favorites()
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data'})
    max_id = 0
    try:
        with open(FAVORITES_FILE, 'r', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                try:
                    max_id = max(max_id, int(row.get('id', 0)))
                except ValueError:
                    pass
    except Exception:
        pass
    new_id = max_id + 1
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = {
        'id': new_id, 'timestamp': ts,
        'city': data.get('city', ''),
        'district': data.get('district', ''),
        'bedroom': int(data.get('bedroom', 0)),
        'hall': int(data.get('hall', 0)),
        'area_num': float(data.get('area', 0)),
        'floor_lvl': int(data.get('floor_lvl', 1)),
        'total_floor': int(data.get('total_floor', 1)),
        'house_age': int(data.get('age', 10)),
        'direction': data.get('direction', ''),
        'decoration': data.get('decoration', ''),
        'elevator_num': int(data.get('elevator_num', 1)),
        'floor': int(data.get('floor', 0)),
        's_cate': data.get('s_cate', ''),
        'predicted_price': float(data.get('predicted_price', 0)),
        'unit_price': float(data.get('unit_price', 0)),
        'note': data.get('note', ''),
    }
    with open(FAVORITES_FILE, 'a', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=FAVORITES_COLS)
        w.writerow(row)
    return jsonify({'success': True, 'id': new_id})


@app.route('/api/favorites/load')
def api_favorites_load():
    fid = request.args.get('id')
    if not fid or not os.path.exists(FAVORITES_FILE):
        return jsonify({'success': False})
    try:
        df = pd.read_csv(FAVORITES_FILE, encoding='utf-8-sig')
        row = df[df['id'] == int(fid)]
        if row.empty:
            return jsonify({'success': False})
        r = row.iloc[0]
        # NaN → empty string for JSON safety
        def safe_val(v):
            if pd.isna(v): return ''
            return v
        return jsonify({
            'success': True,
            'data': {
                'city': r['city'], 'district': r['district'],
                'area': float(r['area_num']),
                'bedroom': int(r['bedroom']), 'hall': int(r['hall']),
                'floor': int(r['floor']),
                'floor_lvl': int(r['floor_lvl']),
                'total_floor': int(r['total_floor']),
                'age': int(r['house_age']),
                'direction': safe_val(r['direction']),
                'decoration': safe_val(r['decoration']),
                'elevator_num': int(r['elevator_num']),
                's_cate': safe_val(r['s_cate']),
            }
        })
    except Exception:
        return jsonify({'success': False})


@app.route('/api/favorites/delete', methods=['POST'])
def api_favorites_delete():
    data = request.get_json()
    fid = data.get('id')
    if not fid or not os.path.exists(FAVORITES_FILE):
        return jsonify({'success': False})
    try:
        df = pd.read_csv(FAVORITES_FILE, encoding='utf-8-sig')
        df = df[df['id'] != int(fid)]
        df.to_csv(FAVORITES_FILE, index=False, encoding='utf-8-sig')
        return jsonify({'success': True})
    except Exception:
        return jsonify({'success': False})


# ==================== 预算推荐 ====================

@app.route('/api/recommend')
def api_recommend():
    city = request.args.get('city', 'guangzhou')
    budget = float(request.args.get('budget', 0))
    if budget <= 0:
        return jsonify({'success': False, 'error': '请输入预算'})
    try:
        if city == 'shanghai':
            df = df_sh_raw.copy()
            df['price'] = pd.to_numeric(df['house_price'], errors='coerce')
            df = df[(df['price'] > 0) & (df['price'] < 3000)]
            df['district_clean'] = df['district'].str.replace('二手房', '')
            for d in ('上海周边', '崇明', '金山'):
                df = df[df['district_clean'] != d]

            def parse_area(desc):
                if pd.isna(desc): return 0
                m = re.search(r'\|(\d+\.?\d*)平', str(desc))
                return float(m.group(1)) if m else 0
            df['area_num'] = df['house_desc'].apply(parse_area)

            dist_stats = df.groupby('district_clean').agg(
                avg_price=('price', 'mean'),
                count=('price', 'count'),
                avg_area=('area_num', 'mean'),
            ).round(1)
            dist_stats = dist_stats[dist_stats['count'] >= 10].sort_values('avg_price')
            avg_unit_prices = {}
            for d in dist_stats.index:
                sub = df[df['district_clean'] == d]
                avg_a = sub['area_num'].mean()
                avg_p = sub['price'].mean()
                avg_unit_prices[d] = avg_p / avg_a * 10000 if avg_a > 0 else 0
        else:
            dist_stats = df_gz.groupby('area').agg(
                avg_price=('price', 'mean'),
                count=('price', 'count'),
                avg_area=('area_num', 'mean'),
            ).round(1)
            dist_stats = dist_stats[dist_stats['count'] >= 5].sort_values('avg_price')
            avg_unit_prices = {}
            for d in dist_stats.index:
                sub = df_gz[df_gz['area'] == d]
                avg_a = sub['area_num'].mean()
                avg_p = sub['price'].mean()
                avg_unit_prices[d] = avg_p / avg_a * 10000 if avg_a > 0 else 0

        recommendations = []
        for district, row in dist_stats.iterrows():
            unit_price = avg_unit_prices.get(district, 0)
            if unit_price <= 0:
                continue
            max_area = budget * 10000 / unit_price
            if max_area < 20:
                continue

            configs = []
            if max_area >= 100:
                configs.append(('3室2厅', 3, 2, round(max_area * 0.95, 0)))
                configs.append(('4室2厅', 4, 2, round(max_area, 0)))
            if max_area >= 70:
                configs.append(('2室1厅', 2, 1, round(max_area * 0.9, 0)))
                configs.append(('3室1厅', 3, 1, round(max_area * 0.85, 0)))
            if max_area >= 40:
                configs.append(('2室1厅', 2, 1, round(max_area * 0.8, 0)))
            configs.append(('1室1厅', 1, 1, round(min(max_area * 0.7, 60), 0)))

            seen_keys = set()
            unique_configs = []
            for label, br, hl, ar in configs:
                key = f'{br}_{hl}'
                if key not in seen_keys:
                    seen_keys.add(key)
                    est = round(ar * unit_price / 10000, 1)
                    unique_configs.append({
                        'label': label, 'bedroom': br, 'hall': hl,
                        'area': ar, 'estimated_price': est,
                        'remaining': round(budget - est, 1),
                    })

            recommendations.append({
                'district': district,
                'avg_price': round(float(row['avg_price']), 1),
                'unit_price': round(unit_price, 0),
                'max_area': round(max_area, 0),
                'count': int(row['count']),
                'configs': unique_configs[:3],
            })

        recommendations.sort(key=lambda x: x['max_area'], reverse=True)

        return jsonify({
            'success': True,
            'data': {
                'city': city, 'budget': budget,
                'recommendations': recommendations[:8],
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})
=======
@app.route('/api/history')
def api_history():
    return jsonify({'success': False, 'message': '开发中'})
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': '接口不存在'}), 404


if __name__ == '__main__':
<<<<<<< HEAD
    init_history()
    init_favorites()
=======
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
    print('=' * 50)
    print('  房价预测系统 v2.0 (双城市)')
    print('  支持: 广州 | 上海')
    print('  访问: http://127.0.0.1:5000')
<<<<<<< HEAD
    print('  快速启动: python run.py (含数据爬取)')
=======
>>>>>>> b73c8c5998bff8646c4d8dd5a12440f9a940bff5
    print('=' * 50)
    app.run(debug=True, port=5000)
