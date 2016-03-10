from zope.interface import Interface


class ITrigger(Interface):
    def trigger_circleci_build(target_owner,
                               target_repo,
                               target_branch,
                               source_build,
                               source_commit):
        '''Trigger another CircleCI build.

        The appropriate environment variables for `cinderblock update` work on
        the other end will be set.
        '''


class IUpdate(Interface):
    def post_github_commit_status(state,
                                  context,
                                  details_url,
                                  repo_name,
                                  commit_sha1,
                                  github_user,
                                  github_api_token):
        '''Update the status of a commit on GitHub.

        After a build has been triggered (with ITrigger, probably), this updates
        the source commit to indicate the status of the integration tests.
        '''
