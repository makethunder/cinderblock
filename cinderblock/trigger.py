from cinderblock.icinderblock import ITrigger
from circleclient.circleclient import CircleClient
from zope.interface import implementer


@implementer(ITrigger)
class Trigger(object):

    def __init__(self, api_token, CircleClient=CircleClient):
        self.circleci_client = CircleClient(api_token)

    def trigger_circleci_build(self,
                               target_owner,
                               target_repo,
                               target_branch,
                               source_build,
                               source_commit):

        build_args = {
            'CINDERBLOCK_SOURCE_BUILD': source_build,
            'CINDERBLOCK_SOURCE_COMMIT': source_commit,
            'CINDERBLOCK_CIRCLE_API_TOKEN': self.circleci_client.api_token
        }
        self.circleci_client.build.trigger(target_owner, target_repo, target_branch, **build_args)

        print('Build triggered at https://www.circleci.com/gh/%s/%s/tree/%s' % (
            target_owner, target_repo, target_branch))
