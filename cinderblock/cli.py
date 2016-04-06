#!/usr/bin/python
'''
Triggers an integration CircleCI job
'''

from cinderblock.trigger import Trigger
from cinderblock.update import Update
import argparse
import os
import sys


class CLI(object):
    def __init__(self, Trigger=Trigger, Update=Update):
        self.Trigger = Trigger
        self.Update = Update

    def main(self, *args):
        arg_parser = _arg_parser()
        args = arg_parser.parse_args(args)

        if args.action == 'trigger':
            self.trigger(args)
        elif args.action == 'update':
            self._update(args)
        else:
            arg_parser.error('too few arguments')

    def trigger(self, args):
        api_token = os.environ['CINDERBLOCK_CIRCLE_API_TOKEN']

        source_build = '%s/%s/%s' % (
            os.environ['CIRCLE_PROJECT_USERNAME'],
            os.environ['CIRCLE_PROJECT_REPONAME'],
            os.environ['CIRCLE_BUILD_NUM'],
        )

        source_commit = '%s/%s/%s' % (
            os.environ['CIRCLE_PROJECT_USERNAME'],
            os.environ['CIRCLE_PROJECT_REPONAME'],
            os.environ['CIRCLE_SHA1'],
        )

        # TODO: handle cases where these environment variables are missing

        target_owner, target_repo, target_branch = args.target.split('/')
        self.trigger = self.Trigger(api_token)
        self.trigger.trigger_circleci_build(
            target_owner=target_owner,
            target_repo=target_repo,
            target_branch=target_branch,
            source_url=os.environ['CIRCLE_BUILD_URL'],
            source_build=source_build,
            source_commit=source_commit)

    def _update(self, args):
        self.update = self.Update()
        try:
            commit = os.environ['CINDERBLOCK_SOURCE_COMMIT']
        except KeyError:
            # I guess there was no source commit triggering us. Do nothing,
            # successfully.
            return
        github_token = os.environ['CINDERBLOCK_GITHUB_API_TOKEN']
        # TODO: handle missing environment variable
        github_user, repo_name, commit_sha = commit.split('/')
        github_user = 'paperg'
        self.update.post_github_commit_status(state=args.state,
                                              context='ci/cinderblock',
                                              details_url=args.details_url,
                                              repo_name=repo_name,
                                              commit_sha1=commit_sha,
                                              github_user=github_user,
                                              github_api_token=github_token)


def _arg_parser():
    arg_parser = argparse.ArgumentParser(description=__doc__)

    subparsers = arg_parser.add_subparsers(dest='action')

    trigger = subparsers.add_parser('trigger')
    trigger.add_argument('target')

    update = subparsers.add_parser('update')
    update.add_argument('state',
                        help='State: [success | failure | pending ]')
    update.add_argument('-d', '--details-url', '--target-url',
                        default=os.environ.get('CIRCLE_BUILD_URL'),
                        help='target for the "details" link on GitHub')

    return arg_parser


def entrypoint():
    cli = CLI()
    cli.main(*sys.argv[1:])


if __name__ == '__main__':
    entrypoint()
