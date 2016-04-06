from cinderblock.cli import CLI
from cinderblock import icinderblock
from zope.interface import implementer
from zope.interface.verify import verifyObject
import pytest
import sys


@implementer(icinderblock.ITrigger)
class FakeTrigger(object):

    def __init__(self, api_token):
        self._builds_triggered = []
        self._api_token = api_token

    def trigger_circleci_build(self,
                               target_owner,
                               target_repo,
                               target_branch,
                               source_url,
                               source_build,
                               source_commit):
        self._builds_triggered.append(locals().copy())


@implementer(icinderblock.IUpdate)
class FakeUpdate(object):

    def __init__(self):
        self._github_statuses = []

    def post_github_commit_status(self,
                                  state,
                                  context,
                                  details_url,
                                  repo_name,
                                  commit_sha1,
                                  github_user,
                                  github_api_token):
        self._github_statuses.append(locals().copy())


@pytest.fixture
def cli():
    return CLI(Trigger=FakeTrigger, Update=FakeUpdate)


def test_faketrigger_interface():
    verifyObject(icinderblock.ITrigger, FakeTrigger(None))


def test_fakeupdate_interface():
    verifyObject(icinderblock.IUpdate, FakeUpdate())


def test_noargs(capsys, monkeypatch):
    '''Exits with an error if no arguments are provided.'''
    monkeypatch.setattr(sys, 'argv', ['cinderblock'])
    from cinderblock.cli import entrypoint
    with pytest.raises(SystemExit):
        entrypoint()

    _, err = capsys.readouterr()
    assert 'too few arguments' in err


def test_invalid_action(cli, capsys):
    '''Exits with an error if the action is invalid.'''
    with pytest.raises(SystemExit):
        cli.main('toast')

    _, err = capsys.readouterr()
    assert 'argument action: invalid choice' in err


@pytest.fixture
def circleci_env(monkeypatch):
    '''Set CIRCLE_* environment variables like CircleCI does.'''
    env = {
        'CIRCLE_PROJECT_USERNAME': 'source_owner',
        'CIRCLE_PROJECT_REPONAME': 'source_project',
        'CIRCLE_SHA1': 'source_sha1',
        'CIRCLE_BUILD_NUM': 'source_sha1',
        'CIRCLE_BUILD_URL': 'https://circleci.example.com/build/42',
    }

    for key, value in env.items():
        monkeypatch.setenv(key, value)

    return env


@pytest.fixture
def triggered_build(cli, monkeypatch, circleci_env):
    '''Return a build triggered with `cinderblock trigger`'''

    monkeypatch.setenv('CINDERBLOCK_CIRCLE_API_TOKEN', 'api_token')

    cli.main('trigger',
             'target_owner/target_repo/target_branch')

    assert cli.trigger._api_token == 'api_token'
    assert len(cli.trigger._builds_triggered) == 1

    return cli.trigger._builds_triggered[0]


def test_trigger_target(triggered_build):
    '''The target comes from the first command-line argument.'''
    assert triggered_build['target_owner'] == 'target_owner'
    assert triggered_build['target_repo'] == 'target_repo'
    assert triggered_build['target_branch'] == 'target_branch'


def test_trigger_source_commit(triggered_build, circleci_env):
    '''The source commit comes from CIRCLE_* environment variables.'''
    assert triggered_build['source_commit'] == '%s/%s/%s' % (
        circleci_env['CIRCLE_PROJECT_USERNAME'],
        circleci_env['CIRCLE_PROJECT_REPONAME'],
        circleci_env['CIRCLE_SHA1'],
    )


def test_trigger_source_build(triggered_build, circleci_env):
    '''The source build comes from CIRCLE_* environment variables.'''
    assert triggered_build['source_build'] == '%s/%s/%s' % (
        circleci_env['CIRCLE_PROJECT_USERNAME'],
        circleci_env['CIRCLE_PROJECT_REPONAME'],
        circleci_env['CIRCLE_BUILD_NUM'],
    )


def test_trigger_source_url(triggered_build, circleci_env):
    '''The source URL comes from CIRCLE_BUILD_URL.'''
    assert triggered_build['source_url'] == circleci_env['CIRCLE_BUILD_URL']


@pytest.fixture
def update_environment(monkeypatch):
    '''Set CINDERBLOCK_* environment variables like cinderblock trigger would.'''
    env = {
        'CINDERBLOCK_SOURCE_COMMIT': 'source/commit/12345678deadbeef',
        'CINDERBLOCK_SOURCE_BUILD': 'source/build/42',
    }

    for key, value in env.items():
        monkeypatch.setenv(key, value)

    return env


@pytest.fixture
def commit_status(cli, monkeypatch, circleci_env, update_environment):
    monkeypatch.setenv('CINDERBLOCK_GITHUB_API_TOKEN', 'api_token')
    cli.main('update', 'success')

    assert len(cli.update._github_statuses) == 1
    return cli.update._github_statuses[0]


def test_update_commit(commit_status, update_environment):
    '''The commit to update comes from $CINDERBLOCK_SOURCE_COMMIT.

    The github user is always "paperg". This is a kludge. When we post the
    commit status to github, github_user (or "owner" as the github API docs
    describe it) needs to be the owner of the repo being merged into, not
    merged from.

    With some more sophistication, we could determine if tests are running for
    a PR, and then determine the being-merged-into owner from that. But that's
    hard, and in practice almost all PRs are into repos owned by "paperg", so
    just do the easy thing for now.
    '''
    source_commit = update_environment['CINDERBLOCK_SOURCE_COMMIT']
    user, repo, sha1 = source_commit.split('/')
    assert commit_status['github_user'] == 'paperg'
    assert commit_status['repo_name'] == repo
    assert commit_status['commit_sha1'] == sha1


def test_update_github_token(commit_status):
    '''The GitHub API token comes from CINDERBLOCK_GITHUB_API_TOKEN.'''
    assert commit_status['github_api_token'] == 'api_token'


def test_update_state(commit_status):
    '''The commit state comes from command line arguments.'''
    assert commit_status['state'] == 'success'


def test_update_details_url(commit_status, circleci_env):
    '''The details URL comes from CIRCLE_BUILD_URL'''
    assert commit_status['details_url'] == circleci_env['CIRCLE_BUILD_URL']


def test_update_context(commit_status):
    '''The context is always ci/cinderblock.'''
    assert commit_status['context'] == 'ci/cinderblock'


def test_update_noenvironment(cli, monkeypatch, circleci_env):
    monkeypatch.setenv('CINDERBLOCK_GITHUB_API_TOKEN', 'api_token')
    monkeypatch.delenv('CINDERBLOCK_SOURCE_COMMIT', raising=False)
    cli.main('update', 'success')
    assert len(cli.update._github_statuses) == 0
