from flask import Blueprint, request
from datetime import datetime
from bs4 import BeautifulSoup
from models import ProvView, TotalView, db
import json
from common import get_page, wrap_response
from sqlalchemy import func, and_, or_
import pytz

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
    tz = pytz.timezone('Asia/Shanghai')
    tm = datetime.now(tz=tz).strftime("%Y-%m-%d %H:%M:%S")

    total_view = TotalView(tm, confirmed_cnt, suspected_cnt, dead_cnt, cured_cnt)
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
    cured_vals = [x.cured for x in total_view]
    dead_vals = [x.dead for x in total_view]

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


@wuhan.route('/data', methods=['GET'])
def get_data_by_params():
    view = request.args.get('view')
    time_from = request.args.get('from', '2020-01-01')
    time_to = request.args.get('to', datetime.now().strftime('%Y-%m-%d')) + 'z'
    data = []
    hour = db.session.query(ProvView.added_time).order_by(ProvView.id.desc()).first().added_time
    if view == 'hubei':
        view_data = db.session.query(ProvView.added_time,
                                     func.sum(ProvView.cured).label('cured'),
                                     func.sum(ProvView.dead).label('dead'),
                                     func.sum(ProvView.for_sure).label('confirmed')) \
            .filter(ProvView.prov == "湖北") \
            .filter(or_(ProvView.added_time.like('%10:0%'), ProvView.added_time.like('%22:0%'))) \
            .filter(and_(ProvView.added_time >= time_from, ProvView.added_time <= time_to)) \
            .group_by(ProvView.added_time).all()

        last_data = db.session.query(ProvView.added_time,
                                     func.sum(ProvView.cured).label('cured'),
                                     func.sum(ProvView.dead).label('dead'),
                                     func.sum(ProvView.for_sure).label('confirmed')) \
            .filter(ProvView.prov == "湖北") \
            .filter(ProvView.added_time.like(f'%{hour}%')) \
            .group_by(ProvView.added_time).all()[-1]
    elif view == 'except':
        view_data = db.session.query(ProvView.added_time,
                                     func.sum(ProvView.cured).label('cured'),
                                     func.sum(ProvView.dead).label('dead'),
                                     func.sum(ProvView.for_sure).label('confirmed')) \
            .filter(ProvView.prov != "湖北") \
            .filter(or_(ProvView.added_time.like('%10:0%'), ProvView.added_time.like('%22:0%'))) \
            .filter(and_(ProvView.added_time >= time_from, ProvView.added_time <= time_to)) \
            .group_by(ProvView.added_time).all()
        last_data = db.session.query(ProvView.added_time,
                                     func.sum(ProvView.cured).label('cured'),
                                     func.sum(ProvView.dead).label('dead'),
                                     func.sum(ProvView.for_sure).label('confirmed')) \
            .filter(ProvView.prov != "湖北") \
            .filter(ProvView.added_time.like(f'%{hour}%')) \
            .group_by(ProvView.added_time).all()[-1]
    else:
        view_data = db.session.query(TotalView.added_time,
                                     func.sum(TotalView.cured).label('cured'),
                                     func.sum(TotalView.dead).label('dead'),
                                     func.sum(TotalView.suspicion).label('suspicion'),
                                     func.sum(TotalView.sure).label('confirmed')) \
            .filter(or_(TotalView.added_time.like('%10:0%'), TotalView.added_time.like('%22:0%'))) \
            .filter(and_(TotalView.added_time >= time_from, TotalView.added_time <= time_to)) \
            .group_by(TotalView.added_time).all()
        last_data = db.session.query(TotalView.added_time,
                                     func.sum(TotalView.cured).label('cured'),
                                     func.sum(TotalView.dead).label('dead'),
                                     func.sum(TotalView.suspicion).label('suspicion'),
                                     func.sum(TotalView.sure).label('confirmed')) \
            .filter(TotalView.added_time.like(f'%{hour}%')) \
            .group_by(TotalView.added_time).all()[-1]

    for item in view_data:
        tm = item.added_time
        tm_key = datetime.strptime(tm, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
        try:
            suspicion = int(item.suspicion)
        except:
            suspicion = 0
        confirmed = int(item.confirmed)
        cured = int(item.cured)
        dead = int(item.dead)

        point = {
                'total': confirmed + suspicion,
                'confirmed': confirmed,
                'cured': cured,
                'dead': dead,
                'date': tm_key
            }
        if view not in ('hubei', 'except'):
            point.update({'suspicion': suspicion})
        data.append(point)

    if hour not in ('10:0', '22:0'):
        tm = last_data.added_time
        tm_key = datetime.strptime(tm, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
        try:
            suspicion = int(last_data.suspicion)
        except:
            suspicion = 0
        confirmed = int(last_data.confirmed)
        cured = int(last_data.cured)
        dead = int(last_data.dead)

        point = {
            'total': confirmed + suspicion,
            'confirmed': confirmed,
            'cured': cured,
            'dead': dead,
            'date': tm_key
        }
        if view not in ('hubei', 'except'):
            point.update({'suspicion': suspicion})
        data.append(point)

    return wrap_response(0, msg=view, data=data)
