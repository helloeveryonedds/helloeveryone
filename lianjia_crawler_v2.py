"""
链家二手房爬虫 v2 — 基于 Playwright（无头浏览器）
解决反爬问题，支持广州 / 上海

安装:
  pip install playwright beautifulsoup4 lxml
  playwright install chromium

用法:
  python lianjia_crawler_v2.py --city guangzhou --pages 3
  python lianjia_crawler_v2.py --city shanghai --pages 3 --latest
  python lianjia_crawler_v2.py --city guangzhou --pages 5 --no-headless  # 可见浏览器
"""
import re, os, csv, time, random, argparse, sys
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ==================== 配置 ====================

CITY_CONFIG = {
    'guangzhou': {
        'url': 'https://gz.lianjia.com/ershoufang/',
        'name': '广州',
        'columns': ['index', 'area', 'street', 'community', 'introduction',
                    'room_type', 'acreage', 'price', 'unit_price',
                    'toward', 'decoration', 'elevator', 'floor',
                    'year', 'follow', 'visit', 'release_time', 'url'],
    },
    'shanghai': {
        'url': 'https://sh.lianjia.com/ershoufang/',
        'name': '上海',
        'columns': ['house_title', 'house_img', 's_cate_href', 'house_desc',
                    'zone_href', 'district', 'house_detail', 'house_price',
                    'house_href', 's_cate', 'singel_price', 'house_time'],
    }
}

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
              'AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/126.0.0.0 Safari/537.36')


# ==================== 页面解析（同 v1） ====================

def parse_list_gz(html):
    """解析广州列表页"""
    soup = BeautifulSoup(html, 'lxml')
    items = []
    for li in soup.select('ul.sellListContent li'):
        try:
            info = li.select_one('.info')
            if not info:
                continue
            title_el = info.select_one('.title a')
            url = title_el.get('href', '') if title_el else ''
            house_title = title_el.get_text(strip=True) if title_el else ''

            position = info.select_one('.positionInfo a')
            community = position.get_text(strip=True) if position else ''
            area_spans = info.select('.flood a')
            area = area_spans[0].get_text(strip=True) if len(area_spans) > 0 else ''
            street = area_spans[1].get_text(strip=True) if len(area_spans) > 1 else ''

            house_info = info.select_one('.houseInfo')
            house_text = house_info.get_text(strip=True) if house_info else ''
            parts = [p.strip() for p in house_text.replace('|', '|').split('|')]
            room_type = parts[0] if len(parts) > 0 else ''
            acreage = parts[1] if len(parts) > 1 else ''
            toward = parts[2] if len(parts) > 2 else ''
            decoration = parts[3] if len(parts) > 3 and '电梯' not in parts[3] else ''
            elevator = '有电梯' if '电梯' in house_text and '有电梯' in house_text else \
                       ('无电梯' if '电梯' in house_text else '')

            floor_info = info.select_one('.positionInfo')
            floor_text = floor_info.get_text(strip=True).replace(community, '').strip() if floor_info else ''

            price_el = info.select_one('.totalPrice span')
            price = price_el.get_text(strip=True) if price_el else '0'
            unit_price_el = info.select_one('.unitPrice span')
            unit_price = unit_price_el.get_text(strip=True) if unit_price_el else ''

            items.append({
                'url': url, 'house_title': house_title,
                'area': area, 'street': street, 'community': community,
                'introduction': house_title,
                'room_type': room_type, 'acreage': acreage,
                'price': price, 'unit_price': unit_price,
                'toward': toward, 'decoration': decoration,
                'elevator': elevator, 'floor': floor_text,
                'follow_follow': '', 'follow_visit': '', 'release_time': '',
                'house_desc': f'{room_type}|{acreage}|{floor_text}|{toward}',
            })
        except Exception as e:
            print(f'  [PARSE ERROR] {e}')
            continue
    return items


def parse_list_sh(html):
    """解析上海列表页"""
    soup = BeautifulSoup(html, 'lxml')
    items = []
    for li in soup.select('ul.sellListContent li'):
        try:
            info = li.select_one('.info')
            if not info:
                continue
            title_el = info.select_one('.title a')
            house_href = title_el.get('href', '') if title_el else ''
            house_title = title_el.get_text(strip=True) if title_el else ''

            house_info = info.select_one('.houseInfo')
            house_desc = house_info.get_text(strip=True).replace('| ', '|') if house_info else ''

            position = info.select_one('.positionInfo')
            pos_as = position.select('a') if position else []
            zone_href = pos_as[0].get('href', '') if len(pos_as) > 0 else ''
            district = pos_as[0].get_text(strip=True) + '二手房' if len(pos_as) > 0 else ''
            s_cate = pos_as[1].get_text(strip=True) if len(pos_as) > 1 else ''
            s_cate_href = pos_as[1].get('href', '') if len(pos_as) > 1 else ''

            detail_el = info.select_one('.communityName a')
            house_detail = detail_el.get_text(strip=True) if detail_el else ''

            price_el = info.select_one('.totalPrice span')
            house_price = price_el.get_text(strip=True) if price_el else '0'
            unit_el = info.select_one('.unitPrice span')
            singel_price = unit_el.get_text(strip=True) if unit_el else ''

            img_el = li.select_one('.lj-lazy')
            house_img = img_el.get('data-original', '') if img_el else ''
            if not house_img:
                img_el = li.select_one('img')
                house_img = img_el.get('data-original', img_el.get('src', '')) if img_el else ''

            items.append({
                'house_title': house_title, 'house_img': house_img,
                's_cate_href': s_cate_href, 'house_desc': house_desc,
                'zone_href': zone_href, 'district': district,
                'house_detail': house_detail, 'house_price': house_price,
                'house_href': house_href, 's_cate': s_cate,
                'singel_price': singel_price, 'house_time': '',
            })
        except Exception as e:
            print(f'  [PARSE ERROR] {e}')
            continue
    return items


# ==================== Playwright 爬虫 ====================

def random_delay(min_s=1.5, max_s=4.0):
    """随机延迟，模拟人类行为"""
    time.sleep(random.uniform(min_s, max_s))


def human_scroll(page):
    """模拟人类滚动页面"""
    for _ in range(random.randint(2, 5)):
        delta = random.randint(200, 600)
        page.evaluate(f'window.scrollBy(0, {delta})')
        time.sleep(random.uniform(0.3, 1.0))
    # 滚回顶部
    page.evaluate('window.scrollTo(0, 0)')
    time.sleep(random.uniform(0.3, 0.8))


def has_listing_content(page):
    """检查页面是否包含房源列表内容"""
    content = page.content()
    # 核心判断：有房源列表容器
    if '.sellListContent' in content or 'sellListContent' in content:
        soup = BeautifulSoup(content, 'lxml')
        items = soup.select('ul.sellListContent li')
        if items:
            return True
    return False


def is_blocked_page(page):
    """判断是否被反爬封禁（非正常页面）"""
    # 封禁页特征：没有房源内容 + URL 跳转到验证域名
    current_url = page.url
    blocked_domains = ['verify', 'captcha', 'security']
    for d in blocked_domains:
        if d in current_url.lower():
            return True
    # 没有房源列表，也没有正常页面的基本结构
    content = page.content().lower()
    normal_signals = ['selllistcontent', 'ershoufang', 'totalprice']
    has_normal = any(s in content for s in normal_signals)
    blocked_signals = ['验证码', 'captcha', 'verify', 'security verification']
    has_blocked = any(s in content for s in blocked_signals)
    return (not has_normal) and has_blocked


def check_and_wait_captcha(page, page_num=0):
    """检测反爬，如果需要则等待用户手动解决"""
    if has_listing_content(page):
        return False  # 有内容，无需处理

    if is_blocked_page(page):
        print(f'\n  [第{page_num}页] 触发反爬限制! 请在浏览器窗口中完成验证')
        current_url = page.url
        print(f'  [第{page_num}页] URL: {current_url}')
        print(f'  [第{page_num}页] 完成后按 Enter 继续...')
        input()
        time.sleep(2)
        # 重新检查
        if has_listing_content(page):
            print(f'  [第{page_num}页] 验证通过，继续爬取')
            return False
        else:
            print(f'  [第{page_num}页] 仍无法获取数据')
            return False

    # 无内容但也不是封禁页（可能是最后一页无数据）
    return False


def crawl_city(city, max_pages=10, headless=True, output=None, save_latest=False,
              user_data_dir=None):
    """使用 Playwright 爬取指定城市的房源数据"""
    cfg = CITY_CONFIG[city]
    base_url = cfg['url']
    city_name = cfg['name']
    columns = cfg['columns']

    if not output:
        ts = datetime.now().strftime('%Y%m%d')
        output = f'链家{city_name}二手房_{ts}.csv'

    latest_file = f'最新房源_{city_name}.csv' if save_latest else None
    all_items = []
    total_count = 0

    print(f'\n{"="*60}')
    print(f'  开始爬取 {city_name} 链家二手房 (Playwright v2)')
    print(f'  列表页: {base_url}')
    print(f'  最大页数: {max_pages}')
    print(f'  浏览器模式: {"有头(可见)" if not headless else "无头(后台)"}')
    if user_data_dir:
        print(f'  用户数据目录: {user_data_dir}')
    print(f'  输出文件: {output}')
    print(f'{"="*60}\n')

    with sync_playwright() as p:
        if user_data_dir:
            # 持久化上下文（Cookie、会话保持）
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-web-security',
                ],
                viewport={'width': 1920, 'height': 1080},
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
                user_agent=USER_AGENT,
            )
            browser = None  # 持久化模式下 context 就是顶层管理器
        else:
            # 启动浏览器
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-web-security',
                ],
            )
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
                user_agent=USER_AGENT,
                accept_downloads=False,
            )

        # 注入反检测脚本
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh'] });
        """)

        page = context.new_page()

        # 先访问首页建立 cookie
        print(f'[初始化] 访问首页 {base_url}')
        page.goto(base_url, wait_until='networkidle', timeout=30000)
        random_delay(2, 4)
        check_and_wait_captcha(page, 0)

        for pg in range(1, max_pages + 1):
            url = f'{base_url}pg{pg}/' if pg > 1 else base_url
            print(f'[第{pg}/{max_pages}页] {url}')

            try:
                page.goto(url, wait_until='networkidle', timeout=30000)
            except Exception as e:
                print(f'  [TIMEOUT] 页面加载超时: {e}')
                continue

            random_delay(1, 3)

            # 检测并处理反爬
            check_and_wait_captcha(page, pg)

            # 模拟人类滚动
            human_scroll(page)

            # 检测是否有数据
            content = page.content()
            if '该区域暂无房源' in content or '没有找到' in content:
                print(f'  [EMPTY] 第{pg}页无数据')
                break

            # 解析
            if city == 'guangzhou':
                page_items = parse_list_gz(content)
            else:
                page_items = parse_list_sh(content)

            if not page_items:
                print(f'  [EMPTY] 未解析到房源')
                continue

            print(f'  解析到 {len(page_items)} 条')
            all_items.extend(page_items)
            total_count += len(page_items)

            # 页间延迟
            delay = random.uniform(3, 6)
            print(f'  等待 {delay:.1f}s...\n')
            time.sleep(delay)

        # 关闭浏览器
        if user_data_dir:
            context.close()
        else:
            browser.close()

    # ============ 保存 CSV ============
    if not all_items:
        print('没有爬取到任何数据')
        return

    if city == 'guangzhou':
        rows = []
        for idx, item in enumerate(all_items, 1):
            rows.append({
                'index': idx, 'area': item.get('area', ''),
                'street': item.get('street', ''),
                'community': item.get('community', ''),
                'introduction': item.get('introduction', ''),
                'room_type': item.get('room_type', ''),
                'acreage': item.get('acreage', ''),
                'price': item.get('price', ''),
                'unit_price': item.get('unit_price', ''),
                'toward': item.get('toward', ''),
                'decoration': item.get('decoration', ''),
                'elevator': item.get('elevator', ''),
                'floor': item.get('floor', ''),
                'year': item.get('year', ''),
                'follow': item.get('follow', ''),
                'visit': item.get('visit', ''),
                'release_time': item.get('release_time', ''),
                'url': item.get('url', ''),
            })
    else:
        rows = []
        for item in all_items:
            rows.append({c: item.get(c, '') for c in columns})

    with open(output, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    if latest_file:
        if city == 'guangzhou':
            latest_cols = ['room_type', 'acreage', 'price', 'toward', 'decoration',
                           'elevator', 'area', 'street', 'floor', 'url']
            with open(latest_file, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.DictWriter(f, fieldnames=latest_cols)
                w.writeheader()
                for r in rows:
                    w.writerow({c: r.get(c, '') for c in latest_cols})
        else:
            latest_cols = ['house_desc', 'house_price', 'district', 's_cate', 'house_href']
            with open(latest_file, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.DictWriter(f, fieldnames=latest_cols)
                w.writeheader()
                for item in all_items:
                    w.writerow({c: item.get(c, '') for c in latest_cols})
        print(f'  另存(预测验证用): {latest_file}')

    print(f'\n{"="*60}')
    print(f'  爬取完成!')
    print(f'  城市: {city_name}')
    print(f'  条数: {total_count}')
    print(f'  文件: {output}')
    print(f'{"="*60}')


# ==================== 入口 ====================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='链家二手房爬虫 v2 (Playwright)')
    parser.add_argument('--city', required=True, choices=['guangzhou', 'shanghai'],
                        help='城市')
    parser.add_argument('--pages', type=int, default=10,
                        help='爬取页数（每页约30条）')
    parser.add_argument('--no-headless', action='store_true',
                        help='有头模式（显示浏览器窗口，更稳定）')
    parser.add_argument('--output', default=None,
                        help='输出文件路径')
    parser.add_argument('--latest', action='store_true',
                        help='另存为最新房源文件')
    parser.add_argument('--user-data-dir', default=None,
                        help='浏览器用户数据目录（持久化Cookie，减少验证码）')
    args = parser.parse_args()

    crawl_city(
        city=args.city,
        max_pages=args.pages,
        headless=not args.no_headless,
        output=args.output,
        save_latest=args.latest,
        user_data_dir=args.user_data_dir,
    )
