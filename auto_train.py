"""
房价预测系统 — 自动训练脚本 v2.0
支持广州 / 上海数据集，自动检测、训练、集成

用法:
  python auto_train.py --file <数据集路径> [--city auto|guangzhou|shanghai]

示例:
  python auto_train.py --file 广州链家二手房数据.xlsx
  python auto_train.py --file 上海链家二手房.csv --city shanghai
  python auto_train.py --file 广州链家二手房数据.xlsx --city guangzhou --update
"""
import re, os, sys, argparse, warnings, json
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

# ==================== 配置 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

# 特征中文名（用于报告）
FEATURE_DISPLAY = {
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

# ==================== 城市检测 ====================

def detect_city(df):
    """根据列名自动检测城市"""
    cols = set(df.columns.str.lower())
    # 广州特征列
    gz_keys = {'room_type', 'acreage', 'toward', 'decoration', 'elevator'}
    # 上海特征列
    sh_keys = {'house_desc', 's_cate', 'house_price'}

    gz_score = len(gz_keys & cols)
    sh_score = len(sh_keys & cols)

    if gz_score >= 3 and gz_score > sh_score:
        return 'guangzhou'
    elif sh_score >= 2:
        return 'shanghai'
    # 再尝试通过列名前缀判断
    if any('house_desc' in c for c in cols):
        return 'shanghai'
    if any('acreage' in c for c in cols):
        return 'guangzhou'
    raise ValueError(f'无法自动判断城市格式。广州应包含 room_type/acreage 等列，'
                     f'上海应包含 house_desc/s_cate 等列。\n当前列: {list(df.columns)}')


# ==================== 广州特征工程 ====================

def build_gz_pipeline(df_raw):
    """广州数据清洗 + 特征工程，返回 (X, y, feature_cols, scaler, encoders)"""
    df = df_raw.copy()

    # 解析室/厅
    def extract_rooms(t):
        if pd.isna(t): return 0, 0
        b = re.search(r'(\d+)室', str(t))
        h = re.search(r'(\d+)厅', str(t))
        return (int(b.group(1)) if b else 0, int(h.group(1)) if h else 0)
    df[['bedroom', 'hall']] = df['room_type'].apply(lambda x: pd.Series(extract_rooms(x)))

    # 面积
    df['area_num'] = df['acreage'].str.extract(r'(\d+\.?\d*)').astype(float)

    # 楼层
    def extract_floor(s):
        if pd.isna(s): return 1, 0
        lvl = re.search(r'([低中高])', str(s))
        total = re.search(r'共(\d+)层', str(s))
        level = lvl.group(1) if lvl else '中'
        t = int(total.group(1)) if total else 0
        return (0 if '低' in level else (2 if '高' in level else 1), t)
    df[['floor_lvl', 'total_floor']] = df['floor'].apply(lambda x: pd.Series(extract_floor(x)))

    # 房龄
    df['year_num'] = df['year'].apply(
        lambda x: int(re.search(r'(\d{4})', str(x)).group(1))
        if not pd.isna(x) and re.search(r'(\d{4})', str(x)) else 2020)
    df['house_age'] = 2026 - df['year_num']

    # 关注 / 看房 / 电梯
    df['follow_num'] = df['follow'].str.extract(r'(\d+)').astype(float)
    df['visit_num'] = df['visit'].str.extract(r'(\d+)').astype(float)
    df['elevator_num'] = df['elevator'].apply(lambda x: 1 if str(x) == '有电梯' else 0)

    # 朝向清洗
    def clean_toward(t):
        if pd.isna(t): return '未知'
        t = str(t).strip()
        if re.match(r'^\d+\.?\d*', t): return '未知'
        if re.match(r'^[东南西北]+$', t): return t
        return '其他'
    df['toward_clean'] = df['toward'].apply(clean_toward)

    # 装修清洗
    def clean_deco(t):
        if pd.isna(t): return '其他'
        t = str(t).strip()
        if t in ('精装', '简装', '毛坯', '豪装', '其他', '普装', '中装', '粗装'):
            return t
        if '精装' in t: return '精装'
        if '简装' in t: return '简装'
        if '毛坯' in t: return '毛坯'
        if '豪装' in t: return '豪装'
        return '其他'
    df['deco_clean'] = df['decoration'].apply(clean_deco)

    # 目标变量
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    # 编码
    le_area = LabelEncoder()
    le_toward = LabelEncoder()
    le_deco = LabelEncoder()
    le_street = LabelEncoder()
    df['area_code'] = le_area.fit_transform(df['area'])
    df['toward_code'] = le_toward.fit_transform(df['toward_clean'])
    df['deco_code'] = le_deco.fit_transform(df['deco_clean'])
    df['street_code'] = le_street.fit_transform(df['street'])

    # 衍生特征
    df['floor_ratio'] = df['floor_lvl'] / (df['total_floor'] + 1)
    df['room_total'] = df['bedroom'] + df['hall']
    df['area_log'] = np.log1p(df['area_num'])

    # 过滤异常值
    before = len(df)
    df = df[(df['price'] > 10) & (df['price'] < 3000)]
    df = df[(df['area_num'] >= 15) & (df['area_num'] <= 500)]
    df = df[df['bedroom'] > 0]
    df = df[(df['house_age'] >= 0) & (df['house_age'] <= 60)]
    filtered = before - len(df)

    feature_cols = [
        'bedroom', 'hall', 'area_num', 'room_total',
        'floor_lvl', 'total_floor', 'floor_ratio',
        'house_age', 'follow_num', 'visit_num', 'elevator_num',
        'area_code', 'toward_code', 'deco_code', 'street_code',
        'area_log'
    ]

    X = df[feature_cols].fillna(0)
    y = df['price'].values

    encoders = {'area': le_area, 'toward': le_toward,
                'decoration': le_deco, 'street': le_street}

    return X, y, feature_cols, filtered, encoders


# ==================== 上海特征工程 ====================

def build_sh_pipeline(df_raw):
    """上海数据清洗 + 特征工程，返回 (X, y, feature_cols, scaler, encoders)"""
    df = df_raw.copy()

    # 从 house_desc 解析: "1室0厅|37.6平|低区/6层|朝南"
    def parse_desc(desc):
        if pd.isna(desc):
            return 0, 0, 0.0, 1, 1, '南'
        try:
            parts = desc.split('|')
            room_part = parts[0]
            bed = int(re.search(r'(\d+)室', room_part).group(1)) if re.search(r'(\d+)室', room_part) else 0
            hall = int(re.search(r'(\d+)厅', room_part).group(1)) if re.search(r'(\d+)厅', room_part) else 0
            area = float(re.search(r'(\d+\.?\d*)平', parts[1]).group(1)) if len(parts) > 1 and re.search(r'(\d+\.?\d*)平', parts[1]) else 0.0
            floor_lvl = 1
            total_floor = 1
            if len(parts) > 2:
                if '低区' in parts[2]: floor_lvl = 0
                elif '高区' in parts[2]: floor_lvl = 2
                else: floor_lvl = 1
                tf = re.search(r'/(\d+)层', parts[2])
                total_floor = int(tf.group(1)) if tf else 1
            direction = parts[3].replace('朝', '') if len(parts) > 3 else '南'
            return bed, hall, area, floor_lvl, total_floor, direction
        except Exception:
            return 0, 0, 0.0, 1, 1, '南'

    df[['bedroom', 'hall', 'area_num', 'floor_lvl', 'total_floor', 'direction']] = df['house_desc'].apply(
        lambda x: pd.Series(parse_desc(x)))

    # 区
    df['district_clean'] = df['district'].str.replace('二手房', '').str.replace('上海周边', '周边')

    # 房龄
    def extract_year(t):
        if pd.isna(t): return 2020
        m = re.search(r'(\d{4})', str(t))
        return int(m.group(1)) if m else 2020
    df['year_num'] = df['house_time'].apply(extract_year)
    df['house_age'] = 2026 - df['year_num']

    # 目标变量
    df['price'] = pd.to_numeric(df['house_price'], errors='coerce')

    # 编码
    le_district = LabelEncoder()
    le_s_cate = LabelEncoder()
    le_direction = LabelEncoder()
    df['district_code'] = le_district.fit_transform(df['district_clean'])
    df['s_cate_code'] = le_s_cate.fit_transform(df['s_cate'])
    df['direction_code'] = le_direction.fit_transform(df['direction'])

    # 衍生特征
    df['room_total'] = df['bedroom'] + df['hall']
    df['floor_ratio'] = df['floor_lvl'] / df['total_floor'].replace(0, 1)
    df['area_log'] = np.log1p(df['area_num'])

    # 过滤
    before = len(df)
    df = df[df['price'] >= 30]
    df = df[df['price'] <= 3000]
    df = df[df['area_num'] >= 15]
    df = df[df['area_num'] <= 500]
    df = df[df['bedroom'] > 0]
    df = df[(df['house_age'] >= 0) & (df['house_age'] <= 70)]
    filtered = before - len(df)

    feature_cols = [
        'bedroom', 'hall', 'area_num', 'room_total',
        'floor_lvl', 'total_floor', 'floor_ratio',
        'house_age',
        'district_code', 'direction_code', 's_cate_code',
        'area_log'
    ]

    X = df[feature_cols].fillna(0)
    y = df['price'].values

    encoders = {'district': le_district, 's_cate': le_s_cate,
                'direction': le_direction}

    return X, y, feature_cols, filtered, encoders


# ==================== 训练 ====================

def train_model(X, y):
    """训练 MLP + RandomForest，返回最优模型"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    results = {}

    # --- MLP ---
    print('\n  [MLP] 训练中...')
    mlp = MLPRegressor(
        hidden_layer_sizes=(256, 128, 64, 32),
        activation='relu', solver='adam', alpha=0.001,
        batch_size=128, learning_rate='adaptive',
        learning_rate_init=0.001, max_iter=500,
        random_state=42, early_stopping=True,
        validation_fraction=0.1, n_iter_no_change=20, verbose=False
    )
    mlp.fit(X_train_s, y_train)
    y_pred = mlp.predict(X_test_s)
    results['MLP'] = {
        'model': mlp,
        'r2': r2_score(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'mae': mean_absolute_error(y_test, y_pred),
    }
    print(f'  [MLP]  RMSE: {results["MLP"]["rmse"]:.2f}  MAE: {results["MLP"]["mae"]:.2f}  R²: {results["MLP"]["r2"]:.4f}')

    # --- Random Forest ---
    print('\n  [RF]  训练中...')
    rf = RandomForestRegressor(
        n_estimators=200, max_depth=20,
        min_samples_split=5, min_samples_leaf=2,
        random_state=42, n_jobs=-1
    )
    rf.fit(X_train_s, y_train)
    y_pred = rf.predict(X_test_s)
    results['RandomForest'] = {
        'model': rf,
        'r2': r2_score(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'mae': mean_absolute_error(y_test, y_pred),
    }
    print(f'  [RF]   RMSE: {results["RandomForest"]["rmse"]:.2f}  MAE: {results["RandomForest"]["mae"]:.2f}  R²: {results["RandomForest"]["r2"]:.4f}')

    # 选最优
    best_name = max(results, key=lambda k: results[k]['r2'])
    best = results[best_name]

    print(f'\n  ✅ 最优模型: {best_name} (R²={best["r2"]:.4f})')

    return best['model'], scaler, results


# ==================== 主流程 ====================

def main():
    parser = argparse.ArgumentParser(description='房价预测系统 — 自动训练脚本')
    parser.add_argument('--file', required=True, help='数据集文件路径 (.csv 或 .xlsx)')
    parser.add_argument('--city', default='auto',
                        choices=['auto', 'guangzhou', 'shanghai'],
                        help='城市 (auto=自动检测)')
    parser.add_argument('--update', action='store_true',
                        help='训练后更新系统模型文件 (覆盖已有模型)')
    args = parser.parse_args()

    print('=' * 60)
    print('  房价预测系统 — 自动训练')
    print('=' * 60)

    # 1. 读取数据
    filepath = args.file
    if not os.path.exists(filepath):
        # 尝试相对路径
        alt = os.path.join(BASE_DIR, filepath)
        if os.path.exists(alt):
            filepath = alt
        else:
            print(f'❌ 文件不存在: {filepath}')
            sys.exit(1)

    print(f'\n📂 读取数据集: {filepath}')
    if filepath.endswith('.csv'):
        # 尝试多种编码
        for enc in ('utf-8', 'utf-8-sig', 'gbk', 'gb18030'):
            try:
                df = pd.read_csv(filepath, encoding=enc)
                print(f'   编码: {enc}')
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            print('❌ 无法识别文件编码')
            sys.exit(1)
    elif filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath, engine='openpyxl')
    else:
        print('❌ 不支持的文件格式，请使用 .csv 或 .xlsx')
        sys.exit(1)

    print(f'   行数: {len(df)}')
    print(f'   列数: {len(df.columns)}')
    print(f'   列名: {list(df.columns)}')

    # 2. 检测城市
    city = args.city
    if city == 'auto':
        try:
            city = detect_city(df)
            print(f'\n🏙️ 自动检测城市: {"广州" if city == "guangzhou" else "上海"}')
        except ValueError as e:
            print(f'\n❌ {e}')
            sys.exit(1)
    else:
        print(f'\n🏙️ 指定城市: {"广州" if city == "guangzhou" else "上海"}')

    # 3. 特征工程
    print(f'\n{"=" * 60}')
    print(f'  [1/3] 特征工程 ({city})')
    print(f'{"=" * 60}')

    if city == 'guangzhou':
        X, y, feature_cols, filtered, encoders = build_gz_pipeline(df)
    else:
        X, y, feature_cols, filtered, encoders = build_sh_pipeline(df)

    print(f'   过滤异常值: {filtered} 行')
    print(f'   最终样本: {len(X)} 行')
    print(f'   特征数: {len(feature_cols)}')
    print(f'   价格范围: {y.min():.0f} ~ {y.max():.0f} 万')
    print(f'   平均价格: {y.mean():.0f} 万')

    if len(X) < 100:
        print('⚠️  样本量过少（<100），训练效果可能不佳')

    # 4. 训练
    print(f'\n{"=" * 60}')
    print(f'  [2/3] 训练模型')
    print(f'{"=" * 60}')

    best_model, scaler, results = train_model(X, y)

    # 5. 保存
    print(f'\n{"=" * 60}')
    print(f'  [3/3] 保存模型')
    print(f'{"=" * 60}')

    if city == 'guangzhou':
        model_files = {
            'model': 'best_model.pkl',
            'scaler': 'scaler.pkl',
            'features': 'feature_cols.pkl',
            'encoders': 'encoders.pkl',
        }
    else:
        model_files = {
            'model': 'sh_model.pkl',
            'scaler': 'sh_scaler.pkl',
            'features': 'sh_feature_cols.pkl',
            'encoders': 'sh_encoders.pkl',
        }

    # 如果不更新，使用带时间戳的文件名备份
    if not args.update:
        from datetime import datetime
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        suffix = f'_{ts}'
    else:
        suffix = ''

    def save_path(key):
        name, ext = os.path.splitext(model_files[key])
        return os.path.join(MODEL_DIR, f'{name}{suffix}{ext}')

    joblib.dump(best_model, save_path('model'))
    joblib.dump(scaler, save_path('scaler'))
    joblib.dump(feature_cols, save_path('features'))
    joblib.dump(encoders, save_path('encoders'))

    print(f'\n   模型目录: {MODEL_DIR}')
    for key in model_files:
        path = save_path(key)
        size = os.path.getsize(path) / 1024 / 1024
        print(f'   📄 {os.path.basename(path)} ({size:.1f} MB)')

    if not args.update:
        print('\n💡 使用 --update 参数可覆盖系统模型文件')
    else:
        print('\n✅ 系统模型已更新！请重启 Flask 服务器生效。')

    # 6. 训练报告
    print(f'\n{"=" * 60}')
    print(f'  训练报告')
    print(f'{"=" * 60}')
    print(f'  城市: {"广州" if city == "guangzhou" else "上海"}')
    print(f'  数据集: {os.path.basename(filepath)}')
    print(f'  样本数: {len(X)}')
    print(f'  特征数: {len(feature_cols)}')

    for name, r in results.items():
        print(f'  {name:>15}: R²={r["r2"]:.4f}  RMSE={r["rmse"]:.1f}万  MAE={r["mae"]:.1f}万')

    best_name = max(results, key=lambda k: results[k]['r2'])
    print(f'  {"=" * 40}')
    print(f'  最优: {best_name}')

    # 特征重要性
    if hasattr(best_model, 'feature_importances_'):
        print(f'\n  特征重要性排名:')
        pairs = sorted(zip(feature_cols, best_model.feature_importances_),
                       key=lambda x: x[1], reverse=True)
        for i, (name, imp) in enumerate(pairs, 1):
            dname = FEATURE_DISPLAY.get(name, name)
            bar = '█' * int(imp * 50) + '░' * (50 - int(imp * 50))
            print(f'  {i:2d}. {dname:<10} {imp:>6.2%} |{bar}|')

    print(f'\n{"=" * 60}')
    print(f'  训练完成!')
    print(f'{"=" * 60}')


if __name__ == '__main__':
    main()
