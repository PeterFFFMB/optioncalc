import csv
import requests
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import numpy as np
from scipy.stats import norm
import datetime

CONTRACT = 'RTS-6.22'
CONTRACT_EXPIRATION_DATE = '19-05-22'
CSV_URL = 'https://www.moex.com/ru/derivatives/optionsdesk-csv.aspx?sid=1&sby=1&c1=on&c4=on&c6=on&c7=on&submit=submit&marg=1\
&code={code}\
&delivery={delivery}\
'.format(code=CONTRACT, delivery=CONTRACT_EXPIRATION_DATE)
strike = '110000.000'
future = 'RIM2'
S = float(strike)
N = norm.cdf
NP = norm.pdf

def main():
    data = get_data(CSV_URL)
    data_csv = data_to_csv(data)
    data_list = list(data_csv)
    sigma = get_iv(strike, data_list)
    future_price = get_future_price(future)
    days_to_expiration = days_to_exp(CONTRACT_EXPIRATION_DATE )
    T = days_to_expiration/365
    d1 = get_d1(future_price, S, sigma, T)
    d2 = get_d2(d1, sigma, T)
    delta_c = delta_call(d1)
    delta_p = delta_put(d1)
    gamma_c = gamma_call(d1, future_price, sigma, T)
    vega_c = vega_call(d1, future_price, T)
    theta_c = call_theta(d1, future_price, sigma, T)
    print(delta_c)
    print(future_price)
    print(theta_c)
    print(days_to_expiration)
    print(sigma)
    print(gamma_c)
    print(vega_c)



def get_data(url):
    response = requests.get(url)
    content = response.content
    data = content.decode(encoding='windows-1251')
    return data


def data_to_csv(data):
    data_csv = csv.reader(data.splitlines(), delimiter=',')
    return data_csv

def get_iv(strike, data_list):
    x = [x for x in data_list if strike in x][0]
    n = data_list.index(x)
    IV = data_list[n][10]
    sigma = float(IV)
    return sigma/100

def days_to_exp(CONTRACT_EXPIRATION_DATE):
    today = datetime.datetime.now().strftime('%y-%m-%d')
    CONTRACT_EXPIRATION_DATE = datetime.datetime.strptime(CONTRACT_EXPIRATION_DATE, '%d-%m-%y')
    today = datetime.datetime.strptime(today, '%y-%m-%d')
    days_exp = CONTRACT_EXPIRATION_DATE - today
    days_exp  = days_exp.days
    return days_exp

def get_future_price(future):
    url = urlopen('https://iss.moex.com/iss/engines/futures/markets/forts/boards/RFUD/securities/{code}.xml?iss.meta=off&iss.only=marketdata&marketdata'.format(code = future))
    soup = BS(url, 'xml')
    future_price = soup.find('row').get("LAST")
    return float(future_price)

def get_d1(future_price,S,sigma,T):
  d1 = (np.log(future_price / S) + (0.5 * (sigma ** 2)) * T) / (sigma * np.sqrt(T))
  return d1

def get_d2(d1, sigma, T):
    d2 = d1 - sigma*np.sqrt(T)
    return d2

def delta_call(d1):
    delta = N(d1)
    return delta

def delta_put(d1):
    delta = 1 - N(d1)
    return delta

def gamma_call(d1, future_price, sigma, T):
    gamma = NP(d1) / (future_price * sigma * np.sqrt(T))
    return  gamma * 1e+1

def vega_call(d1, future_price, T):
    vega = future_price * np.sqrt(T) * NP(d1) / 100
    return vega

def call_theta(d1, future_price, sigma, T):
    theta = -((future_price * sigma * NP(d1)) / (2 * (T ** 0.5))) / 365
    return theta

if __name__ == '__main__':
    main()
