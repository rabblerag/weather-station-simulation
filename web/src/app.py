import datetime as dt
from flask import Flask
from flask import render_template
from sqlalchemy import select
from sqlalchemy import create_engine
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
    target_time = dt.datetime.combine(dt.datetime.today(), dt.time(hour=(dt.datetime.now(timezone).hour )%24)).isoformat()
    stmt = select(models.Metric).\
            where(models.Metric.station_id == "station_5").\
            where(models.Metric.timestamp >= target_time)
    result = session.execute(stmt)
    
    
    return render_template('index.html', metrics=result.scalars().all())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)