"""Defines trends calculations for stations"""
import logging

import faust

import json


logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")

topic = app.topic("events_stations", value_type=Station)

out_topic = app.topic("org.chicago.cta.stations.table.v1", partitions=1, value_type=TransformedStation)

table = app.Table(
     "stations_table",
    default=TransformedStation,
    partitions=1,
    changelog_topic=out_topic,
)

@app.agent(topic)
async def station_event(station_events):
    async for se in station_events:
        
        if se.red:
            line = "red"
        elif se.blue:
            line = "blue"
        elif se.green:
            line = "green"

        table[se.station_id] = TransformedStation(
            station_id=se.station_id,
            station_name=se.station_name,
            order=se.order,
            line=line
        )



if __name__ == "__main__":
    app.main()
