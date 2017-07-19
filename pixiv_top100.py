# coding:utf-8
__author__ = '123woscc'
__date__='2017/7/19'

import os
from multiprocessing.dummy import Pool

import requests
from bs4 import BeautifulSoup

session = requests.session()
domain_url = 'https://www.pixiv.net'
headers = {
        'Referer': 'https://www.pixiv.net/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
 }

#登陆保持session
def pixiv_login(pixiv_id,password):
    login_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    soup = BeautifulSoup(session.get(login_url).content, 'lxml')
    post_key = soup.find(id='old-login').input.get('value')
    formdata = {
        'pixiv_id': pixiv_id,
        'password': password,
        'captcha': '',
        'g_recaptcha_response': '',
        'post_key': post_key,
        'source': 'pc',
        'ref': 'wwwtop_accounts_index',
        'return_to': 'http://www.pixiv.net/'
    }
    session.post('https://accounts.pixiv.net/api/login',data=formdata)
    print(BeautifulSoup(session.get('http://www.pixiv.net/setting_profile.php').content,'lxml').find('input', id='nick').get('value'))
    return session


#获取国际排行榜TOP100链接
def get_top_urls():
    top_url = 'https://www.pixiv.net/ranking_area.php?type=detail&no=6'
    urls = []
    html = session.get(top_url)
    soup = BeautifulSoup(html.content, 'lxml')
    for div in soup.find_all('div', class_='ranking-item'):
        url = domain_url + div.find_all('a')[1].get('href')
        urls.append(url)
    return urls



#获取条目图片链接
def get_page_imgs(url):
    try:
        html = session.get(url, headers=headers)
        soup = BeautifulSoup(html.content, 'lxml')

        if soup.find('a', class_='read-more'):
            more_url = domain_url + soup.find('a', class_='read-more').get('href')
            html2 = session.get(more_url, headers=headers)
            soup2 = BeautifulSoup(html2.content, 'lxml')
            page = soup2.find_all('a', class_='full-size-container')
            urls = [domain_url + img.get('href') for img in page]
            imgs = []
            for url in urls:
                img = BeautifulSoup(session.get(url, headers=headers).content, 'lxml').find('img').get('src')
                imgs.append(img)
            return imgs
        else:
            imgs = soup.find_all('img', class_='original-image')
            return [img.get('data-src') for img in imgs]
    except:
        print('获取图片链接失败',url)

#保存图片
def save_imgs(urls):
    if not os.path.exists(dir_path):
        try:
            os.mkdir(dir_path)
        except Exception as e:
            print('文件夹创建失败：',e)
    if len(urls)>1:
        return
    else:
        url = urls[0]
        file_name = url.split('/')[-1]
        try:
            with open('{}/{}'.format(dir_path,file_name), 'wb') as f:
                f.write(session.get(url, headers=headers).content)
            print('[下载完成]：', file_name)
        except Exception as e:
            print('保存图片失败', url)


if __name__ == '__main__':
    #Pixiv邮箱密码
    pixiv_id = 'xxxxx@xx.com'
    password = 'password'
    pixiv_login(pixiv_id, password)

    #文件夹目录
    dir_path = './full'

    pages=get_top_urls()
    #多线程爬取图片链接
    pool=Pool(32)
    imgs=pool.map(get_page_imgs,pages)
    pool.close()
    pool.join()

    print(imgs)

    print('开始下载')
    #多线程下载图片
    pool2 = Pool(16)
    pool2.map(save_imgs,imgs)
    pool2.close()
    pool2.join()
    print('下载完成')




