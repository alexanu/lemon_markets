
from keys_config import *
import requests
from BeautifulSoup4 import BeautifulSoup

FEAR_GREED_URL = 'https://edition.cnn.com/markets/fear-and-greed'
r = requests.get(FEAR_GREED_URL)

print(r.content)


'''
/html/body/div[1]/section[3]/section[1]/section[1]/div/section/div[1]/div[2]/div[1]/div/div[1]/div[1]/div/div[4]/span
40
<span class="market-fng-gauge__dial-number-value">40</span>
div.market-fng-gauge__overview:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(4) > span:nth-child(1)
html.userconsent-cntry-de.userconsent-reg-gdpr.lkkimoxavk body.layout.layout-with-rail.markets div.layout__content-wrapper.layout-with-rail__content-wrapper section.layout__wrapper.layout-with-rail__wrapper section.layout__main-wrapper.layout-with-rail__main-wrapper section.layout__main.layout-with-rail__main div.static section.tabcontent.active div.market-tabbed-container div.market-tabbed-container__content div.market-tabbed-container__tab.market-tabbed-container__tab--1 div.market-fng-gauge div.market-fng-gauge__overview div.market-fng-gauge__meter-container div.market-fng-gauge__meter div.market-fng-gauge__dial-number span.market-fng-gauge__dial-number-value'''