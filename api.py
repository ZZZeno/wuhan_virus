from flask import Flask, Blueprint
import requests
from requests import Timeout
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from models import ProvView, TotalView, db
import re
import datetime
import json
from common import get_page, wrap_response
from sqlalchemy import func

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

    area_data = area_stat.text.split('getAreaStat =')[-1].split('}catch')[0]
    area_result = json.loads(area_data)

    overview_data = total_stat.text.split('getStatisticsService =')[-1].split('}catch')[0]
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
    total = [x.sure + x.suspicion for x in total_view]
    confirmed_vals = [x.sure for x in total_view]
    suspicion_vals = [x.suspicion for x in total_view]
    dead_vals = [x.cured for x in total_view]
    cured_vals = [x.dead for x in total_view]

    dates = [x.added_time for x in total_view]

    return wrap_response(0, msg={
                            'total': total,
                            'confirmed_vals': confirmed_vals,
                            'suspicion_vals': suspicion_vals,
                            'cured_vals': cured_vals,
                            'dead_vals': dead_vals,
                            "dates": dates
    })


@wuhan.route('/prov_plot')
def prov_plot():
    prov_view = db.session.query(ProvView.added_time,
                               func.sum(ProvView.cured).label('cured'),
                               func.sum(ProvView.dead).label('dead'),
                               func.sum(ProvView.for_sure).label('sure'))\
        .filter(ProvView.prov != "湖北")\
        .group_by(ProvView.added_time).all()
    total = [int(x.sure) for x in prov_view]
    confirmed_vals = [int(x.sure) for x in prov_view]
    # suspicion_vals = [x.suspicion for x in prov_view]
    cured_vals = [int(x.cured) for x in prov_view]
    dead_vals = [int(x.dead) for x in prov_view]

    dates = [x.added_time for x in prov_view]
    print({
        'total': total,
        'confirmed_vals': confirmed_vals,
        # 'suspicion_vals': suspicion_vals,
        'cured_vals': cured_vals,
        'dead_vals': dead_vals,
        "dates": dates
    })
    return wrap_response(0, msg={
        'total': total,
        'confirmed_vals': confirmed_vals,
        # 'suspicion_vals': suspicion_vals,
        'cured_vals': cured_vals,
        'dead_vals': dead_vals,
        "dates": dates
    })


@wuhan.route('/change_time_zone')
def change_time_zone():
    total_view = TotalView.query.filter().all()
    for item in total_view:
        utc8 = datetime.strptime(item.added_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)
        item.added_time = utc8.strftime('%Y-%m-%d %H:%M:%S')
    db.session.commit()

    prov_view = ProvView.query.filter().all()
    for item in prov_view:
        utc8 = datetime.strptime(item.added_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)
        item.added_time = utc8.strftime('%Y-%m-%d %H:%M:%S')
    db.session.commit()
    return wrap_response(0, 'done')
