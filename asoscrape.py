# -*- coding: utf-8 -*-
import requests, os, csv, time, sys
from bs4 import BeautifulSoup

if os.path.exists(os.path.join('scrapy_tool','scrapy_tool.py')) == True:
    from scrapy_tool.scrapy_tool import *



class spider():
    def __init__(self,path_input= 'input'):
        #1. 新建必要的文件夹和工具文件
        #1.1 新建文件夹及子文件夹
        self.path_temp = 'temp' #用于存储工具文件used_id.txt和errorid.txt
        self.path_data = 'asodata' #数据文件夹：用于存放爬取的数据
        self.path_intro = os.path.join(self.path_data,'intro') #数据文件夹子文件夹：用于存放爬取的简介文本
        self.path_update = os.path.join(self.path_data,'update') #数据文件夹的子文件夹：用于存放爬取的更新日志
        for p in [self.path_temp,self.path_data,self.path_intro,self.path_update]:
            if os.path.exists(p) == False:
                os.mkdir(p)
                print('path {} is built'.format(p))
            else:
                print('path {} already exists, skip building directory'.format(p))
        #1.2 新建必要的工具文件
        self.path_usedid = os.path.join('temp','usedid.txt')#用于存储已经爬取成功的appleid
        self.path_errorid = os.path.join('temp','errorid.txt')#用于存储爬取失败的appleid
        for p in [self.path_errorid,self.path_usedid]:
            if os.path.exists(p) == False:
                with open(p,'a+') as f:
                    pass
                print('tool file {} is created'.format(p))
            else:
                print('tool file {} already exists, skip building tool file'.format(p))
        #1.3 数据表路径
        self.path_baseinfo_pub = os.path.join(self.path_data,'baseinfo_pub.csv')#用于存储爬取的结构化的gameapp基本信息和开发者信息的数据
        self.path_version = os.path.join(self.path_data,'version.csv')#用于存储爬取的结构化的版本更新信息的数据
        #1.4 输入的appleid 的路径
        self.path_appleid = os.path.join(path_input,os.listdir(path_input)[0])
        print('file: {} is used to read appleid'.format(os.listdir(path_input)[0]))
        #1.5 其他
        self.base_url = 'http://aso.niaogebiji.com'
        #1.6 代理和header工具
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
        try:
            self.st = scrapy_tool()
        except:
            self.st = None
        #1.7 休息时间
        self.sleep_short = 10
        if  self.st == None:
            self.sleep_long = 120
        else:
            self.sleep_long = 30

        print('='*20+'\nStart scrape data\n'+'='*20)
    #主程序
    def scrape_data(self):
        #0. 打开errorid.txt 和 usedid.txt文件
        usedid = self.txt2list(self.path_usedid) + self.txt2list(self.path_errorid)
        #1. 查看是否导入了爬虫工具，如果有那么就可以使用随机代理和头文件
        if self.st != None:
            headers = self.st.random_headers()
            proxies = self.st.random_proxies(self.base_url)
        else:
            headers = self.default_headers
            proxies = None
        #2. 读取appleid的文件，开始遍历appleid并开始下载
        for appleid in self.txt2list(self.path_appleid):
            #2.0 检查appleid是否已经下载过了
            if appleid in usedid:
                continue
            # 2.1 构造url
            bsurl = 'http://aso.niaogebiji.com/app/baseinfo?id={}'.format(appleid)
            vurl = 'http://aso.niaogebiji.com/app/version?id={}'.format(appleid)
            purl = 'http://aso.niaogebiji.com/app/samepubapp?id={}'.format(appleid)
            #2.2 打开构造的url并爬取数据
            try:
                [datalist_bi, introcontent, filename_intro] = self.scrape_baseinfo(appleid,bsurl,headers,proxies)
                data_ver = self.scrape_version(appleid, vurl,headers,proxies)
                datalist_pub = self.scrape_publisher(appleid, purl,headers,proxies)
                datalist_bi_pub = datalist_bi + datalist_pub #这句代码可以往下移动
            except:
                print('Error: in open url: {}'.format(appleid))
                with open(self.path_errorid, 'a+') as f:
                    f.write('{}\n'.format(appleid))
                if proxies != None:
                    proxies = self.st.random_proxies(self.base_url)
                    headers = self.st.random_headers()
                time.sleep(self.sleep_long)
                continue
            #2.3 存储数据
            #try:
            self.saveascsv(datalist_bi_pub,self.path_baseinfo_pub)
            self.saveastxt(introcontent,os.path.join(self.path_intro,filename_intro))
            for ver in data_ver:
                self.saveascsv(ver[0],self.path_version)
                self.saveastxt(ver[1],os.path.join(self.path_update,ver[2]))
            # except:
            #     print('Error: in save data: {}'.format(appleid))
            #     with open(self.path_errorid, 'a+') as f:
            #         f.write('{}\n'.format(appleid))
            #     continue
            #2.4 将顺利爬取数据的appleid写入usedid.txt并报告成功，进行必要是休息
            with open(self.path_usedid,'a+') as f:
                f.write('{}\n'.format(appleid))
            print('Success: {} has been downloaded '.format(appleid))
            time.sleep(self.sleep_short)
        #3 庆祝顺利完成
        print('='*20+'\nall have been download\n'+'='*20)




    #过程程序
    #1. 打开并解析基本信息页面
    def scrape_baseinfo(self, appleid, url, headers, proxies):
        if proxies == None:
            res = requests.get(url, headers = headers)
        else:
            res = requests.get(url, headers = headers, proxies = proxies)
        time.sleep(2)
        soup = BeautifulSoup(res.text, 'html.parser')
        basecontentdiv1 = soup.find('div', class_='appinfoTxt flex1 mobile-hide')
        appName = basecontentdiv1.find('p', class_='appname ellipsis').get_text()
        vdict = {'appType': 'category', 'price': 'price', 'latestVersion': 'version'}
        for key in vdict:
            targetdiv = basecontentdiv1.find('div', class_=vdict[key])
            if targetdiv != None:
                try:
                    if key == 'appType':
                        vdict[key] = targetdiv.a.get_text()
                    else:
                        vdict[key] = targetdiv.find('div', class_='info').get_text()
                except:
                    vdict[key] = ''
            else:
                vdict[key] = ''

        appType = vdict['appType']
        price = vdict['price']
        latestVersion = vdict['latestVersion']

        baseinfotable = soup.find('table', class_='base-info base-area mobile-hide')
        variabledict = {"developerFirm": "开发商", "developer": "开发者", "tags": "分类", "releaseDate": "发布日期",
                        "lastestDate": "更新日期", "bundleId": "Bundle ID", "lastestVer": "版本", "size": "大小",
                        "payInApp": "是否有内购", "support": "支持网站", "compatibility": "兼容性", "lang": "语言",
                        "contentRank": "内容评级"}
        for key in variabledict:
            targettd = baseinfotable.find('td', text=variabledict[key])
            if targettd != None:
                try:
                    if key == 'support':
                        variabledict[key] = targettd.next_sibling.a.get_text()
                    else:
                        testtd = targettd.next_sibling.next_sibling
                        variabledict[key] = testtd.get_text()
                except:
                    variabledict[key] = ''
            else:
                variabledict[key] = ''
        developerFirm = variabledict['developerFirm']
        developer = variabledict['developer']
        tags = variabledict['tags']
        releaseDate = variabledict['releaseDate']
        lastestDate = variabledict['lastestDate']
        bundleId = variabledict['bundleId']
        lastestVer = variabledict['lastestVer']
        size = variabledict['size']
        payInApp = variabledict['payInApp']
        support = variabledict['support']
        compatibility = variabledict['compatibility']
        lang = variabledict['lang']
        contentRank = variabledict['contentRank']

        datalist = [appleid, appName, appType, price, latestVersion, developerFirm, developer, tags, releaseDate,
                    lastestDate,
                    bundleId, lastestVer, size, payInApp, support, compatibility, lang, contentRank]

        intro = soup.find('div', class_='vertxt')
        if intro != None:
            introcontent = str(intro).replace('<br>', '').replace('<div class="vertxt" style="max-height: 156px;">',
                                                                  '').replace('<div class="vertxt">', '').replace(
                '<br/>',
                '').replace(
                '</div>', '')
        else:
            introcontent = ''
        introfilename = 'intro{}.txt'.format(appleid)
        return [datalist, introcontent, introfilename]

    # 2. 打开并解析版本更新页面
    def scrape_version(self, appleid, url, headers, proxies):
        if proxies == None:
            res = requests.get(url, headers = headers)
        else:
            res = requests.get(url, headers = headers, proxies = proxies)
        time.sleep(2)
        soup = BeautifulSoup(res.text, 'html.parser')
        targetdiv = soup.find('div', class_='rankcontent')
        verdivlist = targetdiv.find_all('div', class_='versionItem')
        for verdiv in verdivlist:
            verDate = verdiv.find('div', class_='verDate').get_text()
            versionTitle = verdiv.find('p', class_='versionTitle').get_text()
            versionTitle2 = 'v' + versionTitle
            vertxt = verdiv.find('div', class_='vertxt')
            vercontent = str(vertxt).replace('<div class="vertxt">', '').replace('<br>', '').replace('</div>',
                                                                                                     '').replace(
                '<br/>', '')
            timeArray = time.strptime(verDate, "%Y年%m月%d日")
            timestamp = time.mktime(timeArray)
            filename = '%sv%s.txt' % (appleid, versionTitle)
            filename = filename.replace('.', '_').replace('_txt', '.txt')
            datalist = [appleid, verDate, timestamp, versionTitle, versionTitle2, filename]
            yield [datalist, vercontent, filename]

    #3. 打开并解析同开发者应用页面
    def scrape_publisher(self, appleid, url, headers, proxies):
        if proxies == None:
            res = requests.get(url, headers = headers)
        else:
            res = requests.get(url, headers = headers, proxies = proxies)
        time.sleep(2)
        soup = BeautifulSoup(res.text, 'html.parser')
        samepubapp = soup.find('div', {'id': 'samepubapp'})
        artistname = soup.find('div', {'class': 'artistnamezh'}).get_text()
        table = samepubapp.find('tbody')
        if table is None:
            samepubappnum = 0
            samepubapplist = " "
            samepubapplistid = " "
        else:
            tr = table.find_all('tr')
            samepubappnum = len(tr)
            samepubapplist = []
            samepubappidlist = []
            for t in tr:
                ainfo = t.find('a', {'class': 'app_name'})
                sameappid = ainfo['href'].replace('/app/weekdatareport?id=', '')
                sameappname = ainfo.get_text().replace(',', '')
                samepubapplist.append(sameappname)
                samepubappidlist.append(sameappid)
            samepubapplist = '|'.join(samepubapplist)
            samepubapplistid = '|'.join(samepubappidlist)
        data = [appleid, artistname, samepubappnum, samepubapplist, samepubapplistid]
        return data

    #4.存储数据
    #4.1 结构化数据
    def saveascsv(self, datalist, filepath):
        with open(filepath, 'a+', newline='', encoding='utf-8') as csvfile:
            w = csv.writer(csvfile)
            w.writerow(datalist)
        time.sleep(0.25)
    #4.2 非结构化数据
    def saveastxt(self, content, filepath):
        if content != '':
            with open(filepath, 'a+', encoding='utf-8') as txtfile:
                txtfile.write(content)
            time.sleep(0.25)
    # 辅助应用
    # txt转list
    def txt2list(self, path_file, break_mark = '\n'):
        with open(path_file, 'r') as f:
            temp = f.read()
        templist = temp.split(break_mark)
        return templist




if __name__ == '__main__':
    sp = spider()
    sp.scrape_data()
