import requests                     # for downloading web pages
import subprocess                   # for checking ungoogled-chromium version
from bs4 import BeautifulSoup       # for parsing html
import hashlib                      # for verifying file integrity
import os                           # for os functions

url = 'https://ungoogled-software.github.io/ungoogled-chromium-binaries/releases/archlinux/'
r = requests.get(url)
soup = BeautifulSoup(r.content, 'html.parser')

new_chromium_version = ([i.a for i in soup.find_all('li')][0])
new_chromium_version = str(new_chromium_version).split('>')[1].split('<')[0].strip()

chromium_installed = not subprocess.getoutput('pacman -Q ungoogled-chromium').startswith('error: package')
chromium_version = subprocess.getoutput('pacman -Q ungoogled-chromium').split(' ', 1)[-1].strip()
up_to_date = chromium_version == new_chromium_version

home = os.path.expanduser('~')

def get_chromium_info():
    info = {}

    download_page_url = url + new_chromium_version
    dr = requests.get(download_page_url)
    rsoup = BeautifulSoup(dr.content, 'html.parser')
    for litag in rsoup.find_all('li'):
        litext = str(litag.text)
        if litext.strip().startswith('MD5:'):
            md5hash = litext.split(': ', 1)[-1]
            info['md5_hash'] = md5hash
    for atag in rsoup.find_all('a'):
        if str(atag['href']).endswith('.pkg.tar.zst'):
            download_url = str(atag['href'])
            info['download_url'] = download_url
            info['filename'] = atag.text

    return info

# downloads from url to ~/.cache/ and installs using pacman -U.
def install(url, output):
    print(f'downloading {url}\n => {home}/.cache/{output}')
    ru = requests.get(url)
    with open(f'{home}/.cache/{output}', 'wb+') as f:
        for chunk in ru.iter_content(chunk_size=16*1024):
            f.write(chunk)
    print(' => done.')

    print(f'installing with command "sudo pacman -U {home}/.cache/{output}"')
    print(f' => running command...')
    os.system(f'sudo pacman -U {home}/.cache/{output}')




if __name__ == '__main__':
    if up_to_date:
        print('ungoogled-chromium is already up to date.')
        exit() 
    info = get_chromium_info()
    if not chromium_installed:
        prompt = 'ungoogled-chromium is not installed. Would you like to install it now? [Y/n] '
        i = input(prompt).strip().lower()
        if i == '' or i == 'y':
            install(info['download_url'], info['filename'])
        else:
            exit()

    install(info['download_url'], info['filename'])

    print('done.')
