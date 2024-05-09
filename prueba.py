from time import sleep
import requests
import pandas as pd
from bs4 import BeautifulSoup

def soup2list(src, list_, attr=None):
    if attr:
        for val in src:
            list_.append(val[attr])
    else:
        for val in src:
            list_.append(val.get_text())

users = []
userReviewNum = []
ratings = []
locations = []
dates = []
reviews = []

from_page = 1
to_page = 6
company = 'mefx.company'

for i in range(from_page, to_page+1):

   result = requests.get(fr"https://www.trustpilot.com/review/{company}?page={i}")
   soup = BeautifulSoup(result.content)

   # Trust Pilot was setup in a way that's not friendly to scraping, so this hacky method will do.
   soup2list(soup.find_all('span', {'class','typography_heading-xxs__QKBS8 typography_appearance-default__AAY17'}), users)
   soup2list(soup.find_all('div', {'class','typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_detailsIcon__Fo_ua'}), locations)
   soup2list(soup.find_all('span', {'class','typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l'}), userReviewNum)
   soup2list(soup.find_all('div', {'class','styles_reviewHeader__iU9Px'}), dates)
   soup2list(soup.find_all('div', {'class','styles_reviewHeader__iU9Px'}), ratings, attr='data-service-review-rating')
   soup2list(soup.find_all('div', {'class','styles_reviewContent__0Q2Tg'}), reviews)

   # To avoid throttling
   sleep(1)

review_data = pd.DataFrame(
{
   'Username':users,
   'Total reviews':userReviewNum,
   'location':locations,
   'date':dates,
   'content':reviews,
   'Rating': ratings
})


