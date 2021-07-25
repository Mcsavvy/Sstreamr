import arrow
from time import perf_counter
from youtube_api import YouTubeDataAPI
from django.conf import settings
from .models import YouTube

# CONSTANTS

START_DATE = arrow.get(2021, 7, 20)
KEYWORDS = (
    ('Big brother naija', 50),
    ('Big brother naija abeg', 50),
    ('Big brother 9ja abeg', 50),
    ('Big brother 9ja', 30),
    ('Big brother naija live', 20),
    ('Big brother naija 2021', 20),
    ('Big brother naija 2k21', 10),

)
API = YouTubeDataAPI(settings.YOUTUBE_DATA_API_KEY)

def prepopulate():
    print('Prepopulating...')
    start = perf_counter()
    for keyword, max_results in KEYWORDS:
        print(
            "Querying %s..." % keyword
        )
        start_ = perf_counter()
        results = API.search(
            q=keyword,
            max_results=max_results,
            published_after=START_DATE.datetime,
            search_type='video'
        )
        for content in results:
            content['video_publish_date'] = arrow.get(
                content['video_publish_date']
            ).datetime
            new = YouTube.add(content)
            print(new)
        print(
            'Queried and populated {} in {:0.4f} seconds with {} results.'.format(
                keyword, (perf_counter() - start_),  len(results)
            )
        )
    print(
        "Prepopulation took {:0.4f} seconds".format(perf_counter() - start)
    )

def populate():
    from core.models import YouTubes
    ALL = YouTubes()
    last_date = max(ALL.all).createdAt
    print('Populating...')
    start = perf_counter()
    for keyword, max_results in KEYWORDS:
        print(
            "Querying %s..." % keyword
        )
        start_ = perf_counter()
        results = API.search(
            q=keyword,
            max_results=max_results,
            published_after=last_date,
            search_type='video'
        )
        for content in results:
            content['video_publish_date'] = arrow.get(
                content['video_publish_date']
            ).datetime
            new = YouTube.add(content)
            print(new)
        print(
            'Queried and populated {} in {:0.4f} seconds with {} results.'.format(
                keyword, (perf_counter() - start_),  len(results)
            )
        )
    print(
        "Population took {:0.4f} seconds".format(perf_counter() - start)
    )