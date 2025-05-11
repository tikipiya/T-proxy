from os import system
from colorama import Fore, init, Style, Back
import requests
import re
import time
import threading
from proxy_checker import ProxyChecker
from sys import stdout
from asyncx import TaskManager, Task, sync_to_async
import asyncio
import aiohttp
from datetime import datetime

init(autoreset=True)  # coloramaの自動リセットを有効化

lock = threading.Lock()

class UI:
    @staticmethod
    def banner():
        banner = f'''
    {Fore.CYAN}╔════════════════════════════════════════════════════════════╗
    ║                      {Fore.WHITE}T-Proxy{Fore.CYAN}                              ║
    ║                {Fore.LIGHTBLACK_EX}Made by tikisan{Fore.CYAN}                           ║
    ╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    '''
        return banner

    @staticmethod
    def menu():
        menu = f'''
        {Fore.CYAN}╔════════════════════════════════════════════════════════════╗
        ║                      {Fore.WHITE}メインメニュー{Fore.CYAN}                          ║
        ╠════════════════════════════════════════════════════════════╣
        ║  {Fore.RED}[1]{Style.RESET_ALL} プロキシスクレイピング                                ║
        ║  {Fore.RED}[2]{Style.RESET_ALL} プロキシチェック                                    ║
        ╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        '''
        return menu

    @staticmethod
    def progress_bar(current, total, prefix='', suffix='', length=50, fill='█'):
        percent = ("{0:.1f}").format(100 * (current / float(total)))
        filled_length = int(length * current // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        return f'\r{prefix} |{bar}| {percent}% {suffix}'

    @staticmethod
    def status_box(title, content):
        box = f'''
        {Fore.CYAN}╔════════════════════════════════════════════════════════════╗
        ║  {Fore.WHITE}{title:<50}{Fore.CYAN}  ║
        ╠════════════════════════════════════════════════════════════╣
        ║  {content:<50}  ║
        ╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        '''
        return box

def write(arg, end='\n'):
    lock.acquire()
    stdout.flush()
    print(arg, end=end)
    lock.release()

def write_status(message, status_type='info'):
    colors = {
        'info': Fore.BLUE,
        'success': Fore.GREEN,
        'warning': Fore.YELLOW,
        'error': Fore.RED
    }
    timestamp = datetime.now().strftime('%H:%M:%S')
    write(f'{colors.get(status_type, Fore.WHITE)}[{timestamp}] {message}{Style.RESET_ALL}')

class XProxy:
    proxy_w_regex = [
    ["http://spys.me/proxy.txt","%ip%:%port% "],
    ["http://www.httptunnel.ge/ProxyListForFree.aspx"," target=\"_new\">%ip%:%port%</a>"],
    ["https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.json", "\"ip\":\"%ip%\",\"port\":\"%port%\","],
    ["https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list", '"host": "%ip%".*?"country": "(.*?){2}",.*?"port": %port%'],
    ["https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt", '%ip%:%port% (.*?){2}-.-S \\+'],
    ["https://www.us-proxy.org/", "<tr><td>%ip%<\\/td><td>%port%<\\/td><td>(.*?){2}<\\/td><td class='hm'>.*?<\\/td><td>.*?<\\/td><td class='hm'>.*?<\\/td><td class='hx'>(.*?)<\\/td><td class='hm'>.*?<\\/td><\\/tr>"],
    ["https://free-proxy-list.net/", "<tr><td>%ip%<\\/td><td>%port%<\\/td><td>(.*?){2}<\\/td><td class='hm'>.*?<\\/td><td>.*?<\\/td><td class='hm'>.*?<\\/td><td class='hx'>(.*?)<\\/td><td class='hm'>.*?<\\/td><\\/tr>"],
    ["https://www.sslproxies.org/", "<tr><td>%ip%<\\/td><td>%port%<\\/td><td>(.*?){2}<\\/td><td class='hm'>.*?<\\/td><td>.*?<\\/td><td class='hm'>.*?<\\/td><td class='hx'>(.*?)<\\/td><td class='hm'>.*?<\\/td><\\/tr>"],
    ['https://www.socks-proxy.net/', "%ip%:%port%"],
    ['https://free-proxy-list.net/uk-proxy.html', "<tr><td>%ip%<\\/td><td>%port%<\\/td><td>(.*?){2}<\\/td><td class='hm'>.*?<\\/td><td>.*?<\\/td><td class='hm'>.*?<\\/td><td class='hx'>(.*?)<\\/td><td class='hm'>.*?<\\/td><\\/tr>"],
    ['https://free-proxy-list.net/anonymous-proxy.html', "<tr><td>%ip%<\\/td><td>%port%<\\/td><td>(.*?){2}<\\/td><td class='hm'>.*?<\\/td><td>.*?<\\/td><td class='hm'>.*?<\\/td><td class='hx'>(.*?)<\\/td><td class='hm'>.*?<\\/td><\\/tr>"],
    ["https://www.proxy-list.download/api/v0/get?l=en&t=https", '"IP": "%ip%", "PORT": "%port%",'],
    ["https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=6000&country=all&ssl=yes&anonymity=all", "%ip%:%port%"],
    ["https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt", "%ip%:%port%"],
    ["https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt", "%ip%:%port%"],
    ["https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt", "%ip%:%port%"],
    ["https://www.hide-my-ip.com/proxylist.shtml", '"i":"%ip%","p":"%port%",'],
    ["https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json", '"ip": "%ip%",\n.*?"port": "%port%",'],
    ['https://www.freeproxychecker.com/result/socks4_proxies.txt', "%ip%:%port%"],
    ['https://proxy50-50.blogspot.com/', '%ip%</a></td><td>%port%</td>'], 
    ['http://free-fresh-proxy-daily.blogspot.com/feeds/posts/default', "%ip%:%port%"],
    ['http://free-fresh-proxy-daily.blogspot.com/feeds/posts/default', "%ip%:%port%"],
    ['http://www.live-socks.net/feeds/posts/default', "%ip%:%port%"],
    ['http://www.socks24.org/feeds/posts/default', "%ip%:%port%"],
    ['http://www.proxyserverlist24.top/feeds/posts/default',"%ip%:%port%" ] ,
    ['http://proxysearcher.sourceforge.net/Proxy%20List.php?type=http',"%ip%:%port%"],
    ['http://proxysearcher.sourceforge.net/Proxy%20List.php?type=socks', "%ip%:%port%"],
    ['http://proxysearcher.sourceforge.net/Proxy%20List.php?type=socks', "%ip%:%port%"], 
    ['https://www.my-proxy.com/free-anonymous-proxy.html', '%ip%:%port%'],
    ['https://www.my-proxy.com/free-transparent-proxy.html', '%ip%:%port%'],
    ['https://www.my-proxy.com/free-socks-4-proxy.html', '%ip%:%port%'],
    ['https://www.my-proxy.com/free-socks-5-proxy.html','%ip%:%port%'],
    ['https://www.my-proxy.com/free-proxy-list.html','%ip%:%port%'],
    ['https://www.my-proxy.com/free-proxy-list-2.html','%ip%:%port%'],
    ['https://www.my-proxy.com/free-proxy-list-3.html','%ip%:%port%'],
    ['https://www.my-proxy.com/free-proxy-list-4.html', '%ip%:%port%'],
    ['https://www.my-proxy.com/free-proxy-list-5.html','%ip%:%port%'],
    ['https://www.my-proxy.com/free-proxy-list-6.html','%ip%:%port%'],
    ['https://www.my-proxy.com/free-proxy-list-7.html','%ip%:%port%'],
    ['https://www.my-proxy.com/free-proxy-list-8.html','%ip%:%port%'],
    ['https://www.my-proxy.com/free-proxy-list-9.html','%ip%:%port%'],
    ['https://www.my-proxy.com/free-proxy-list-10.html','%ip%:%port%'],
    ]

    proxy_direct = [
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all',
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=5000&country=all&ssl=all&anonymity=all',
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=5000&country=all&ssl=all&anonymity=all',         
        'https://www.proxyscan.io/download?type=http',
        'https://www.proxyscan.io/download?type=https',
        'https://www.proxyscan.io/download?type=socks4',
        'https://www.proxyscan.io/download?type=socks5',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'https://github.com/TheSpeedX/PROXY-List/blob/master/socks4.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt',
        'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
        'https://multiproxy.org/txt_all/proxy.txt',
        'http://rootjazz.com/proxies/proxies.txt',
        'http://ab57.ru/downloads/proxyold.txt',
        'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
        'https://proxy-spider.com/api/proxies.example.txt',
        'https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt',
        'https://www.proxy-list.download/api/v1/get?type=socks4'
        'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt'
        ]
                       

    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"}

    def __init__(self):
        self.proxy_output = []
        self.scrape_counter = 0
        self.checked_counter = 0
        self.max_proxies = 5000
        self.protocol_counts = {
            'http': 0,
            'https': 0,
            'socks4': 0,
            'socks5': 0
        }

    def _update_title(self):
        while True:
            elapsed = time.strftime('%H:%M:%S', time.gmtime(time.time() - self.start))
            system('title X-Proxy - Elapsed: %s ^| Scraped: %s ^| Checked :%s'% (elapsed, self.scrape_counter, self.checked_counter))
            time.sleep(0.4)

    def file_read(self, name):
        with open(name, 'r', encoding='UTF-8') as f:
            text = [line.strip('\n') for line in f]
            return text

    def file_write(self, name, contents):
        with open(name, 'w', encoding='UTF-8' ) as f:
            for x in contents:
                f.write(x + '\n')

    def background_task(self):
        self.start = time.time()
        threading.Thread(target = self._update_title, daemon=True).start()


    def get_proxies(self):
        return self.proxy_output

    def save_proxy(self, proxy, protocol):
        # プロトコル別のカウントを更新
        if protocol in self.protocol_counts:
            self.protocol_counts[protocol] += 1
            write_status(f'{protocol.upper()}プロキシを保存: {proxy}', 'info')

        # プロトコル別に保存
        filename = f'{protocol}_alive.txt'
        with open(filename, 'a', encoding='UTF-8') as f:
            f.write(proxy + '\n')

        # すべてのプロキシを保存
        with open('all_alive.txt', 'a', encoding='UTF-8') as f:
            f.write(proxy + '\n')

    def print_protocol_stats(self):
        write_status('プロトコル別の統計:', 'info')
        total = sum(self.protocol_counts.values())
        for protocol, count in self.protocol_counts.items():
            percentage = (count / total * 100) if total > 0 else 0
            write(f'{Fore.CYAN}{protocol.upper()}: {count}個 ({percentage:.1f}%){Style.RESET_ALL}')
        write(f'{Fore.CYAN}合計: {total}個{Style.RESET_ALL}')

class ProxyScrape(XProxy):
    def __init__(self):
        XProxy.__init__(self)
        write_status('プロキシスクレイパーを初期化中...', 'info')
        self.checker = ProxyChecker()
        system('cls')

    async def _scrape_async(self, url, custom_regex):
        try:
            if self.scrape_counter >= self.max_proxies:
                write_status(f'最大プロキシ数（{self.max_proxies}個）に達しました。', 'warning')
                return

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5, headers=self.headers) as response:
                    proxylist = await response.text()
                    custom_regex = custom_regex.replace('%ip%', '([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})')
                    custom_regex = custom_regex.replace('%port%', '([0-9]{1,5})')

                    for proxy in re.findall(re.compile(custom_regex), proxylist):
                        if self.scrape_counter >= self.max_proxies:
                            return

                        proxy_str = proxy[0] + ":" + proxy[1]
                        self.proxy_output.append(proxy_str)
                        write(f'{Fore.CYAN} > {proxy_str}{Style.RESET_ALL}')
                        self.scrape_counter += 1
                        
                        if self.scrape_counter % 100 == 0:
                            write_status(f'100個のプロキシを収集しました。チェックを開始します...', 'warning')
                            await self.check_current_proxies_async()

        except Exception as e:
            write_status(f'スクレイピング中にエラーが発生: {url} - {str(e)}', 'error')

    async def check_single_proxy_async(self, proxy):
        try:
            # 非同期でプロキシをチェック
            c = await sync_to_async(self.checker.check_proxy)(proxy)
            if c and c['protocols']:  # プロトコルが存在する場合のみ処理
                protocol = c['protocols'][0].lower()
                write(f'{Fore.GREEN}[ALIVE] {proxy} | {c["anonymity"]} | Timeout:{c["timeout"]} {c["country_code"]} {protocol}{Style.RESET_ALL}')
                
                # プロトコル別に保存
                if protocol in ['http', 'https', 'socks4', 'socks5']:
                    await sync_to_async(self.save_proxy)(proxy, protocol)
                else:
                    write_status(f'不明なプロトコル: {protocol} - {proxy}', 'warning')
            else:
                write(f'{Fore.RED}[DEAD] {proxy}{Style.RESET_ALL}')
                await sync_to_async(self.save_dead_proxy)(proxy)
        except Exception as e:
            write_status(f'プロキシチェック中にエラーが発生: {proxy} - {str(e)}', 'error')
            await sync_to_async(self.save_error_proxy)(proxy, str(e))
        finally:
            self.checked_counter += 1

    def save_dead_proxy(self, proxy):
        with open('dead_proxies.txt', 'a', encoding='UTF-8') as f:
            f.write(proxy + '\n')

    def save_error_proxy(self, proxy, error):
        with open('error_proxies.txt', 'a', encoding='UTF-8') as f:
            f.write(f'{proxy} - {error}\n')

    def save_proxy(self, proxy, protocol):
        try:
            # プロトコル別のカウントを更新
            if protocol in self.protocol_counts:
                self.protocol_counts[protocol] += 1
                write_status(f'{protocol.upper()}プロキシを保存: {proxy}', 'info')

                # プロトコル別のファイルに保存
                filename = f'{protocol}_alive.txt'
                with open(filename, 'a', encoding='UTF-8') as f:
                    f.write(proxy + '\n')

                # すべての有効なプロキシを保存
                with open('all_alive.txt', 'a', encoding='UTF-8') as f:
                    f.write(f'{proxy} - {protocol}\n')
        except Exception as e:
            write_status(f'プロキシ保存中にエラーが発生: {proxy} - {str(e)}', 'error')

    async def check_proxies_async(self, proxies):
        manager = TaskManager()
        tasks = []
        
        # プロキシをバッチに分割して処理
        batch_size = 50  # 同時に処理するプロキシの数
        for i in range(0, len(proxies), batch_size):
            batch = proxies[i:i + batch_size]
            for proxy in batch:
                task = Task(
                    name=f"check_{proxy}",
                    func=lambda p=proxy: self.check_single_proxy_async(p),
                    priority=1
                )
                tasks.append(task)
            
            # バッチごとに実行
            await manager.run_tasks(tasks)
            tasks = []  # タスクリストをクリア
            
            # 進捗状況を表示
            progress = min(i + batch_size, len(proxies))
            write_status(f'プロキシチェック進捗: {progress}/{len(proxies)}', 'info')

        # 最終的な統計を表示
        self.print_protocol_stats()

    async def check_current_proxies_async(self):
        current_proxies = self.proxy_output[-100:]
        write_status(f'100個のプロキシをチェック中...', 'info')
        await self.check_proxies_async(current_proxies)
        write_status(f'\n{Fore.GREEN}[INFO] チェック完了。次の100個のプロキシを収集します...{Style.RESET_ALL}\n', 'success')

    async def scrape_regex_async(self):
        tasks = []
        for source in self.proxy_w_regex:
            task = Task(
                name=f"scrape_{source[0]}",
                func=lambda s=source: self._scrape_async(s[0], s[1]),
                priority=1
            )
            tasks.append(task)
        
        manager = TaskManager()
        await manager.run_tasks(tasks)

    async def scrape_direct_async(self):
        tasks = []
        for source in self.proxy_direct:
            task = Task(
                name=f"scrape_direct_{source}",
                func=lambda s=source: self._scrape_direct_async(s),
                priority=1
            )
            tasks.append(task)
        
        manager = TaskManager()
        await manager.run_tasks(tasks)

    async def _scrape_direct_async(self, source):
        try:
            if self.scrape_counter >= self.max_proxies:
                return

            async with aiohttp.ClientSession() as session:
                async with session.get(source, timeout=5, headers=self.headers) as response:
                    page = await response.text()
                    for proxy in re.findall(re.compile('([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}):([0-9]{1,5})'), page):
                        if self.scrape_counter >= self.max_proxies:
                            return

                        self.proxy_output.append(proxy[0] + ':' + proxy[1])
                        write(f'{Fore.CYAN} > {proxy[0]}:{proxy[1]}{Style.RESET_ALL}')
                        self.scrape_counter += 1

                        if self.scrape_counter % 100 == 0:
                            write_status(f'100個のプロキシを収集しました。チェックを開始します...', 'warning')
                            await self.check_current_proxies_async()

        except Exception as e:
            write_status(f'エラーが発生しました: {str(e)}', 'error')

class ProxyCheck(XProxy):
    def __init__(self):
        XProxy.__init__(self)
        write_status('プロキシチェッカーを初期化中...', 'info')
        self.checker = ProxyChecker()
        system('cls')

    def check_single_proxy(self, proxy):
        try:
            c = self.checker.check_proxy(proxy)
            if c and c['protocols']:  # プロトコルが存在する場合のみ処理
                protocol = c['protocols'][0].lower()
                write(f'{Fore.GREEN}[ALIVE] {proxy} | {c["anonymity"]} | Timeout:{c["timeout"]} {c["country_code"]} {protocol}{Style.RESET_ALL}')
                
                # プロトコル別に保存
                if protocol in ['http', 'https', 'socks4', 'socks5']:
                    self.save_proxy(proxy, protocol)
                else:
                    write_status(f'不明なプロトコル: {protocol} - {proxy}', 'warning')
            else:
                write(f'{Fore.RED}[DEAD] {proxy}{Style.RESET_ALL}')
                with open('dead_proxies.txt', 'a', encoding='UTF-8') as f:
                    f.write(proxy + '\n')
        except Exception as e:
            write_status(f'プロキシチェック中にエラーが発生: {proxy} - {str(e)}', 'error')
            with open('error_proxies.txt', 'a', encoding='UTF-8') as f:
                f.write(f'{proxy} - {str(e)}\n')
        finally:
            self.checked_counter += 1

    def save_proxy(self, proxy, protocol):
        try:
            # プロトコル別のカウントを更新
            if protocol in self.protocol_counts:
                self.protocol_counts[protocol] += 1
                write_status(f'{protocol.upper()}プロキシを保存: {proxy}', 'info')

                # プロトコル別のファイルに保存
                filename = f'{protocol}_alive.txt'
                with open(filename, 'a', encoding='UTF-8') as f:
                    f.write(proxy + '\n')

                # すべての有効なプロキシを保存
                with open('all_alive.txt', 'a', encoding='UTF-8') as f:
                    f.write(f'{proxy} - {protocol}\n')
        except Exception as e:
            write_status(f'プロキシ保存中にエラーが発生: {proxy} - {str(e)}', 'error')

    def print_protocol_stats(self):
        write_status('プロトコル別の統計:', 'info')
        total = sum(self.protocol_counts.values())
        for protocol, count in self.protocol_counts.items():
            percentage = (count / total * 100) if total > 0 else 0
            write(f'{Fore.CYAN}{protocol.upper()}: {count}個 ({percentage:.1f}%){Style.RESET_ALL}')
        write(f'{Fore.CYAN}合計: {total}個{Style.RESET_ALL}')

    async def check_proxies_async(self, proxies):
        manager = TaskManager()
        tasks = []
        
        for proxy in proxies:
            task = Task(
                name=f"check_{proxy}",
                func=lambda p=proxy: self.check_single_proxy(p),
                priority=1
            )
            tasks.append(task)
        
        await manager.run_tasks(tasks)
        self.print_protocol_stats()  # チェック完了後に統計を表示

async def main_async():
    x = UI()
    p = ProxyScrape()
    system('title T-Proxy by Nightfall#2512 ^| AIO Proxy Tool')
    system('cls')

    print(x.banner())
    print(x.menu())

    try:
        user_input = int(input(f'\n{Fore.CYAN}[{Fore.RED}>{Style.RESET_ALL}] 選択してください: '))
        if user_input == 1:
            system('cls')
            print(x.banner())
            p.background_task()
            write_status('プロキシのスクレイピングを開始します...', 'info')
            write_status(f'最大{p.max_proxies}個のプロキシを収集します。', 'info')
            
            await p.scrape_regex_async()
            await p.scrape_direct_async()

            output = p.get_proxies()

            write_status('重複をチェック中...', 'info')
            print(f'{Fore.CYAN}現在の数: {len(output)}')
            clean_output = list(set(output))
            print(f'重複削除後の数: {len(clean_output)}')

            write_status('scraped.txtに書き込み中...', 'info')
            p.file_write('scraped.txt', clean_output)
            
            write_status('プロトコル別の統計を表示します...', 'info')
            p.print_protocol_stats()
            
            write_status('完了しました！', 'success')
            system('pause>nul')
            await main_async()  # メインメニューに戻る

        elif user_input == 2:
            pc = ProxyCheck()
            system('cls')
            print(x.banner())

            path = input(f'{Fore.CYAN}ファイルパスを入力してください: {Style.RESET_ALL}')
            if '"' in path:
                new_path = path.replace('"','')
            else:
                new_path = path

            proxy_list = pc.file_read(new_path)
            thread_count = int(input(f'{Fore.CYAN}スレッド数を入力してください [例: 200]: {Style.RESET_ALL}'))
            write_status('読み込み中...', 'info')
            
            system('cls')
            print(x.banner())
            pc.background_task()

            await pc.check_proxies_async(proxy_list)
            write_status('チェックが完了しました！', 'success')
            system('pause>nul')
            await main_async()  # メインメニューに戻る
            
        else:
            write_status('無効な入力です！', 'error')
            await main_async()

    except ValueError:
        write_status('数値を入力してください！', 'error')
        await main_async()

if __name__ == '__main__':
    asyncio.run(main_async())
