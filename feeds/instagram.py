from instauto.api import client
from instauto.api.client import ApiClient
from pathlib import Path
import os, re, arrow, random
from django.conf import settings
import stackprinter
stackprinter.set_excepthook(style='darkbg2')
from django.db import models
from django.db.utils import IntegrityError
import requests
import string
from nodes.models import Node

__all__ = [
    'Instagrampost'
]

DATA_DIR = os.path.join(Path(__file__).parent, '.data')

SESSION = os.path.join(DATA_DIR, 'session.instauto')

HEADERS = os.path.join(DATA_DIR, 'headers.ig')

if not os.path.isfile(SESSION):
    initial = ApiClient(username='__essntls__', password=os.environ['IGAUTH'])
    initial.log_in()
    initial.save_to_disk(SESSION)

API = ApiClient.initiate_from_file(SESSION)

PHOTO_DIR = os.path.join(
    settings.MEDIA_ROOT, 'feeds', 'instagram'
)

SESS = requests.Session()

with open(HEADERS) as f:
    headers = eval(f.read())

SESS.headers.update(headers)

def oembed_generator(post_id: str):
    post_url = f'https://www.instagram.com/p/{post_id}'
    return f'https://api.instagram.com/oembed/?url={post_url}/'

def get_post_details(post_id: str):
    oembed_url = oembed_generator(post_id)
    get_post = SESS.get(oembed_url)
    if get_post.status_code != 200: return False
    return get_post.json()

def download_thumbnail(url: str, save_to: str = os.path.join(settings.MEDIA_ROOT, 'thumbnail.jpg')):
    pic = SESS.get(url)
    if pic.status_code != 200: return False
    with open(save_to, 'wb') as o:
        o.write(pic.content)
    return True

    
class Instagrampost(models.Model):
    post_id = models.CharField(max_length=25, unique=True)
    title = models.TextField(blank=True)
    embed_src = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='feeds/instagram', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    viewers = models.ManyToManyField(
        to=Node, blank=True,
        related_name='viewed_instagram_posts'
    )

    class Meta:
        verbose_name = 'Instagram Post'


    def fetch_meta(self) -> bool:
        meta = get_post_details(self.post_id)
        self.title = meta['title']
        PHOTO_PATH = os.path.join(PHOTO_DIR, f'{self.post_id}.jpg')
        if download_thumbnail(
            meta['thumbnail_url'],
            PHOTO_PATH
        ):
            self.thumbnail = f'feeds/instagram/{self.post_id}.jpg'
        else:
            return False
        src: str = meta['html']
        self.embed_src = src
        self.save()
        return True

    def get_absolute_url(self):
        return f'https://www.instagram.com/p/{self.post_id}/'

    def __str__(self) -> str:
        return self.post_id

    def __gt__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        if other.created_at:
            if self.created_at:
                return self.created_at > other.created_at
            else:
                return False
        else:
            return True

    def __lt__(self, other) -> bool:
        return not self > other

    def __ge__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        return self.created_at >= other.created_at

    def __le__(self, other) -> bool:
        return not self >= other

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(
                'Can\'t compare YouTube object to {} object.'.format(
                    type(other)
                )
            )
        return self.post_id == other.post_id

    def title_parsed(self):
        raw: str = self.title
        URL = r"(http|www).+\w"
        MENTION = r'@[\w\._-]+'
        TAG = r'#\w+'
        urls = {}
        mentions = {}
        tags = {}
        printable = string.ascii_letters + string.punctuation.strip('@').strip('#') + string.digits
        replace_substring = lambda string, span, value: string[:span[0]] + value + string[span[1]:]
        for match in re.finditer(URL, raw):
            placeholder = ''.join([f"{random.choice(printable)}" for x in range(len(match.group()))])
            parsed = f"<a class='ig-url-link' href='{match.group()}'>{match.group()}</a>"
            urls[placeholder] = parsed
            raw = replace_substring(raw, match.span(), placeholder)
        for match in re.finditer(MENTION, raw):
            placeholder = ''.join([f"{random.choice(printable)}" for x in range(len(match.group()))])
            parsed = f'''<a class='ig-profile-link' href="https://www.instagram.com/{match.group().strip('@')}">{match.group()}</a>'''
            mentions[placeholder] = parsed
            raw = replace_substring(raw, match.span(), placeholder)
        for match in re.finditer(TAG, raw):
            placeholder = ''.join([f"{random.choice(printable)}" for x in range(len(match.group()))])
            parsed = f"<a class='ig-tag-link' href='https://www.instagram.com/explore/tags/{match.group().strip('#')}/'>{match.group()}</a>"
            mentions[placeholder] = parsed
            raw = replace_substring(raw, match.span(), placeholder)
        for x in urls:
            raw = raw.replace(x, urls[x])
        for x in mentions:
            raw = raw.replace(x, mentions[x])
        for x in tags:
            raw = raw.replace(x, tags[x])
        return raw

    def __hash__(self):
        return super().__hash__()

    def __ne__(self, other) -> bool:
        return not self == other

        




