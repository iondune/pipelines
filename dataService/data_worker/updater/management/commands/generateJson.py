from django.db.models import Q
from django.db.models.query import QuerySet
import geojson
from updater.models import DailySummary
from updater.models import Station
import datetime
from django.core.management.base import BaseCommand
from django.db.transaction import commit_on_success
from django.contrib.gis.geos import Polygon, GEOSGeometry
from djgeojson.serializers import Serializer as GeoJSONSerializer
from geojson import Feature, FeatureCollection, Point

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        generateJson()

        self.stdout.write('Successfully generated JSON.')

@commit_on_success
def generateJson():
    # summaries = Station.objects.all().order_by('?')[:15]
    # summaries = DailySummary.objects.all()

    summaries = DailySummary.objects.select_related('station')\
        .exclude(station__isnull=True)\
        .order_by('station').filter(Q(date__gte='2013-01-01') & Q(date__lte='2013-01-31'))[:310]

    # summaries = sorted(summaries, key=lambda summ: summ.date)
    # sorted(student_objects, key=lambda student: student.age)

    for summary in summaries:
        print '\n' + str(summary.station.usaf), str(summary.station.wban), str(summary.station.location)

    dicts = summaries.values()
    features = []

    # todo: optimize the querying here
    for i in xrange(len(summaries)):
        if i % 50 == 0 and i > 0:
            print 'Processed', i, 'summaries into GeoJSON.'

        location = summaries[i].station.location
        point = Point((location[0], location[1]))
        dict = dicts[i]
        dict['date'] = dict['date'].isoformat()
        feature = Feature(geometry=point, properties=dict)
        features.append(feature)

    features = FeatureCollection(features)

    file = open('weather.json', 'w')
    geojson.dump(features, file, sort_keys=False)
    file.close()

    # dump = geojson.dumps(features, sort_keys=False)
    # print dump

    # geojson = GeoJSONSerializer().serialize(summaries, use_natural_keys=True, geometry_field="location", primary_key="id")

    # print geojson

    # >> > from geojson import Feature, Point, FeatureCollection
    # >> > my_feature = Feature(geometry=Point((1.6432, -19.123)))
    # >> > my_other_feature = Feature(geometry=Point((-80.234, -22.532)))
    # >>> Feature(geometry=my_point, properties={"country": "Spain"})
    # >> > FeatureCollection([my_feature, my_other_feature])  # doctest: +ELLIPSIS
    # {"features": [
    #     {"geometry": {"coordinates": [1.643..., -19.12...], "type": "Point"},
    #      "id": null, "properties": {}, "type": "Feature"},
    #     {"geometry": {"coordinates": [-80.23..., -22.53...], "type": "Point"},
    #      "id": null, "properties": {}, "type": "Feature"}],
    #  "type": "FeatureCollection"}



def get_summaries_in_polygon(points_list):

    wkt = ''

    for i in xrange(len(points_list)):
        point = points_list[i]

        if i > 0:
            wkt + ', '

        wkt += point[0] + ' ' + point[1]

    wkt = 'POLYGON ((' + wkt + '))'

def getSummariesInPolygon(well_known_text):
    return DailySummary.objects\
        .filter(station__location__within=well_known_text)


def get_station_for_summary(summary):
    pass





if __name__ == "__main__":
    generateJson()