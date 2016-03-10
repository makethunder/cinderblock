from cinderblock import icinderblock
from cinderblock.update import Update
from zope.interface.verify import verifyObject
import json
import pytest


@pytest.fixture
def fakePoster():
    class FakePoster(object):
        '''I provide a `post` method which looks like requests.post.'''
        def __init__(self):
            self._posted = []

        def post(self, url, data='{}', headers={}):
            self._posted.append((url, json.loads(data), headers))

    return FakePoster()


@pytest.fixture
def update(fakePoster):
    return Update(post=fakePoster.post)


@pytest.fixture
def posted(update, fakePoster):
    update.post_github_commit_status(
        'state',
        'context',
        'details_url',
        'repo_name',
        'commit_sha1',
        'github_user',
        'github_api_token',
    )

    assert len(fakePoster._posted) == 1
    return fakePoster._posted[0]


@pytest.fixture
def posted_data(posted):
    _, data, _ = posted
    return data


@pytest.fixture
def posted_headers(posted):
    _, _, headers = posted
    return headers


def test_interface(update):
    verifyObject(icinderblock.IUpdate, update)


def test_state(posted_data):
    assert posted_data['state'] == 'state'


def test_context(posted_data):
    assert posted_data['context'] == 'context'


def test_description(posted_data):
    assert posted_data['description'] == 'context status: state'


def test_target_url(posted_data):
    assert posted_data['target_url'] == 'details_url'


def test_content_type(posted_headers):
    assert posted_headers['Content-Type'] == 'application/json'


def test_url(posted):
    url, _, _ = posted
    expected_url = '/'.join([
        'https://api.github.com/repos',
        'github_user',
        'repo_name',
        'statuses',
        'commit_sha1',
    ])
    expected_url += '?access_token=github_api_token'

    assert url == expected_url
