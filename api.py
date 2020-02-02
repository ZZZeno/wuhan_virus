from flask import Flask, Blueprint
import requests
from requests import Timeout
from bs4 import BeautifulSoup
from models import ProvView, TotalView, db
import re
import datetime
import json
from common import get_page, wrap_response
import matplotlib.pyplot as plt

wuhan = Blueprint(
    'wuhan',
    __name__,
    url_prefix='/wuhan'
)


@wuhan.route('/api/scheduler')
def index():
    response = get_page()
    if not response:
        return wrap_response("fail")
    soup = BeautifulSoup(response.text, 'lxml')
    area_stat = soup.find(id='getAreaStat')
    total_stat = soup.find(id='getStatisticsService')

    area_data = area_stat.text.split('=')[-1].split('}catch')[0]
    area_result = json.loads(area_data)

    overview_data = total_stat.text.split('=')[-1].split('}catch')[0]
    overview_result = json.loads(overview_data)

    confirmed_cnt = overview_result.get('confirmedCount')
    suspected_cnt = overview_result.get('suspectedCount')
    cured_cnt = overview_result.get('curedCount')
    dead_cnt = overview_result.get('deadCount')

    tm = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_view = TotalView(tm, confirmed_cnt, suspected_cnt, cured_cnt, dead_cnt)
    db.session.add(total_view)
    db.session.commit()

    for item in area_result:
        name = item.get('provinceShortName')
        confirmed = item.get('confirmedCount')
        cured = item.get('curedCount')
        dead = item.get('deadCount')
        prov = ProvView(tm, name, confirmed, cured, dead)
        db.session.add(prov)
    db.session.commit()

    return wrap_response("success")


@wuhan.route('/plot')
def plot():
    total_view = TotalView.query.filter().all()
    sum_vals = [x.sure + x.suspicion for x in total_view]
    confirmed_vals = [x.sure for x in total_view]
    suspicion_vals = [x.suspicion for x in total_view]

    dates = [x.added_time for x in total_view]

    return wrap_response(0,msg={
                            'sum_vals': sum_vals,
                            'confirmed_vals': confirmed_vals,
                            'suspicion_vals': suspicion_vals,
                            "dates": dates
    })


@wuhan.route('/test')
def test():
    return 'aaa'
