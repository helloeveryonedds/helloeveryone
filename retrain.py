"""
模型重训脚本 — 爬取最新数据 → 加权合并 → 重新训练模型

新数据在训练中占更高权重（通过重复采样实现），使预测更贴近当前市场。

用法:
  python retrain.py                          # 默认爬5页，加权重训
  python retrain.py --crawl-pages 20         # 爬20页（约600条），更充分
  python retrain.py --skip-crawl             # 不爬取，仅用已有数据重训
  python retrain.py --weight 5               # 新数据权重设为5倍（默认3倍）
"""
import os
import sys
import subprocess
import argparse
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
CRAWLER = os.path.join(BASE_DIR, 'lianjia_crawler_v2.py')


def run_crawler(city, pages, headless=False, user_data_dir=None):
    """运行 Playwright 爬虫"""
    print(f'\n--- 爬取 {city} 最新房源 ({pages}页) ---')
    cmd = [
        sys.executable, '-u', CRAWLER,
        '--city', city,
        '--pages', str(pages),
        '--latest',
    ]
    if not headless:
        cmd.append('--no-headless')
    if user_data_dir:
        cmd.extend(['--user-data-dir', user_data_dir])
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(cmd, cwd=BASE_DIR, env=env)
    return result.returncode == 0


def merge_with_weight(city, new_data_path, orig_data_path, weight=3):
    """
    合并新旧数据，新数据通过重复采样获得更高权重。

    参数:
      city: 城市名（仅用于显示）
      new_data_path: 爬取的最新数据 CSV
      orig_data_path: 原始训练数据 CSV
      weight: 新数据权重（重复次数）
    """
    print(f'\n[{city}] 合并数据...')

    if not os.path.exists(new_data_path):
        print(f'  跳过: 新数据不存在 ({new_data_path})')
        return None
    if not os.path.exists(orig_data_path):
        print(f'  跳过: 原始数据不存在 ({orig_data_path})')
        return None

    encoding_new = 'utf-8-sig' if city == '广州' else 'utf-8-sig'
    encoding_orig = 'utf-8-sig' if city == '广州' else 'utf-8'

    new_df = pd.read_csv(new_data_path, encoding=encoding_new)
    orig_df = pd.read_csv(orig_data_path, encoding=encoding_orig)

    print(f'  原始数据: {len(orig_df)} 条')
    print(f'  新爬取:   {len(new_df)} 条')

    if new_df.empty:
        print('  新数据为空，跳过')
        return None

    # 新数据重复 N 次以提高权重
    weighted_new = pd.concat([new_df] * weight, ignore_index=True)
    print(f'  加权后新数据: {len(weighted_new)} 条 (权重{weight}倍)')

    # 合并（新数据在前，便于训练时优先采样）
    combined = pd.concat([weighted_new, orig_df], ignore_index=True)
    print(f'  训练集总计: {len(combined)} 条')
    print(f'  新数据占比: {len(weighted_new) / len(combined) * 100:.1f}%')

    ts = datetime.now().strftime('%Y%m%d')
    out_path = os.path.join(BASE_DIR, f'{city}训练数据_合并_{ts}.csv')
    combined.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f'  输出: {os.path.basename(out_path)}')
    return out_path


def run_training(city, data_path):
    """调用 auto_train.py 训练模型"""
    city_arg = 'guangzhou' if city == '广州' else 'shanghai'
    print(f'\n[{city}] 训练模型...')
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run([
        sys.executable, '-u', 'auto_train.py',
        '--file', data_path,
        '--city', city_arg,
        '--update',
    ], cwd=BASE_DIR, env=env)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description='房价预测 — 加权重训')
    parser.add_argument('--crawl-pages', type=int, default=5,
                        help='爬取页数（每页约30条，默认5页）')
    parser.add_argument('--weight', type=int, default=3,
                        help='新数据权重倍数（默认3倍）')
    parser.add_argument('--skip-crawl', action='store_true',
                        help='跳过爬取，仅用已有数据重训')
    parser.add_argument('--headless', action='store_true',
                        help='无头模式运行爬虫（默认有头可见，可手动验证）')
    parser.add_argument('--user-data-dir', default=None,
                        help='浏览器用户数据目录路径（持久化Cookie，减少验证码）')
    args = parser.parse_args()

    print('=' * 60)
    print(f'  房价预测系统 — 模型更新')
    print(f'  新数据权重: {args.weight}倍  |  爬取页数: {args.crawl_pages if not args.skip_crawl else "跳过"}')
    print(f'  浏览器模式: {"无头(后台)" if args.headless else "有头(可见)"}')
    print('=' * 60)

    # Step 1: 爬取
    if not args.skip_crawl:
        run_crawler('guangzhou', args.crawl_pages,
                     headless=args.headless,
                     user_data_dir=args.user_data_dir)
        run_crawler('shanghai', args.crawl_pages,
                     headless=args.headless,
                     user_data_dir=args.user_data_dir)
    else:
        print('\n跳过爬取，使用已有最新数据')

    # Step 2: 合并（加权）
    gz_data = merge_with_weight(
        '广州',
        os.path.join(BASE_DIR, '最新房源_广州.csv'),
        os.path.join(MODEL_DIR, 'filtered_data.csv'),
        weight=args.weight,
    )
    sh_data = merge_with_weight(
        '上海',
        os.path.join(BASE_DIR, '最新房源_上海.csv'),
        os.path.join(BASE_DIR, '上海链家二手房.csv'),
        weight=args.weight,
    )

    # Step 3: 训练
    if gz_data:
        run_training('广州', gz_data)
    if sh_data:
        run_training('上海', sh_data)

    print(f'\n{"=" * 60}')
    print(f'  模型更新完成！预测将更贴近最新市场数据。')
    print(f'  请重启 Flask 服务以加载新模型。')
    print(f'{"=" * 60}')


if __name__ == '__main__':
    main()
