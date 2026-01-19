import datetime as dt
from flask import Flask
from flask import render_template
from flask import request
from sqlalchemy import select
from sqlalchemy import or_
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import Session

import models

timezone = dt.timezone(dt.timedelta(hours=+2.0))

app = Flask("Web UI")

engine = create_engine("sqlite+pysqlite:////app/database/data.db", echo=True)
models.Base.metadata.create_all(engine)
conn = engine.connect()
session = Session(conn)
conn.begin()


@app.route("/")
def index():
    stations = session.execute(select(models.Station.station_id).order_by(models.Station.station_id)).scalars().all()

    page = request.args.get("page")
    if page == None:
        page = 0
    else:
        try:
            page = int(page)
        except:
            page = 0

    per_page = 25

    selected_stations = request.args.getlist("station_id[]")
    selected_metrics = request.args.getlist("metrics[]")
    start_time = request.args.get("start")
    end_time = request.args.get("end")

    if len(selected_stations) == 0:
        selected_stations = stations
    
    if len(selected_metrics) == 0:
        selected_metrics = ["temperature", "humidity", "wind_speed"]

    if start_time == None or start_time == "":
        start_time = dt.datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone).isoformat()
    
    if end_time == None or end_time == "":
        end_time = dt.datetime.now(tz=timezone).isoformat()
    
    stmt = select(models.Metric)
    
    all_data = session.scalar(select(func.count(models.Metric.id)).\
                            where(or_(*(models.Metric.station_id == station for station in selected_stations))).\
                            where(start_time <= models.Metric.timestamp).\
                            where(models.Metric.timestamp <= end_time).\
                            where(or_(*(models.Metric.data.contains(f"{metric_type}") for metric_type in selected_metrics)))
                            )

    print(all_data)
    stmt =  select(models.Metric).\
            where(or_(*(models.Metric.station_id == station for station in selected_stations))).\
            where(start_time <= models.Metric.timestamp).\
            where(models.Metric.timestamp <= end_time).\
            where(or_(*(models.Metric.data.contains(f"{metric_type}") for metric_type in selected_metrics))).\
            order_by(models.Metric.timestamp).slice(page*per_page, (page+1)*per_page)
    result = session.execute(stmt)

    metrics = result.scalars().all()
    
    print(all_data, page, per_page, selected_stations, selected_metrics)

    return render_template('index.html', 
                            all_data=all_data, page=page, per_page=per_page,
                            stations=stations, selected_metrics=selected_metrics,
                            start_time=start_time, end_time=end_time, metrics=metrics
                        )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)