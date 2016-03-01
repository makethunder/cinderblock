#!/usr/bin/python
'''
Triggers an integration CircleCI job
'''

import argparse
import os
from circleclient import circleclient


def main():
    args = __parse_args()
    client = circleclient.CircleClient(args.circle_api_token)

    # Trigger a parametized build with the integration project with
    # env variables to identify the trigger project and the version
    print('Triggering CircleCI build for {}/{}:{} with args: {}'.format(
        args.repo_owner, args.circle_project_reponame, args.branch, args))
    client.build.trigger(username=args.repo_owner,
                         project=args.integration_repo,
                         branch=args.branch,
                         CINDERBLOCK_REPO_OWNER=args.repo_owner,
                         CINDERBLOCK_REPO_NAME=args.circle_project_reponame,
                         CINDERBLOCK_COMMIT_SHA=args.circle_sha1,
                         CINDERBLOCK_BUILD_NUM=args.circle_build_num,
                         CINDERBLOCK_TARGET_URL=args.circle_build_url)
    print('Build triggered at: https://www.circleci.com/gh/{}/{}/'.format(
        args.repo_owner, args.integration_repo))


def __validate_args(args, argparser):
    try:
        assert args.repo_owner, \
            "repo_owner missing or CINDERBLOCK_REPO_OWNER is not set!"
        assert args.integration_repo, \
            "integration_repo missing or CINDERBLOCK_INTEGRATION_REPO is not set!"
        assert args.circle_api_token, \
            "CIRCLE_API_TOKEN is not set!"
        assert args.circle_project_reponame, \
            "CIRCLE_PROJECT_REPONAME is not set!"
        assert args.circle_sha1, \
            "No commit specified or CIRCLE_SHA1 is not set!"
        assert args.circle_build_num, \
            "No build number specified or CIRCLE_BUILD_NUMBER is not set!"
    except AssertionError as error:
        argparser.print_help()
        raise error


def __parse_args():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-o', '--repo-owner', default=os.environ.get('CINDERBLOCK_REPO_OWNER'))
    argparser.add_argument(
        '-i', '--integration-repo',
        default=os.environ.get('CINDERBLOCK_INTEGRATION_REPO'))
    argparser.add_argument(
        '-b', '--branch', default='master')

    args = argparser.parse_args()
    args.circle_api_token = os.environ.get('CIRCLE_API_TOKEN')
    args.circle_build_num = os.environ.get('CIRCLE_BUILD_NUM')
    args.circle_sha1 = os.environ.get('CIRCLE_SHA1')
    args.circle_build_url = os.environ.get('CIRCLE_BUILD_URL')
    args.circle_project_reponame = os.environ.get('CIRCLE_PROJECT_REPONAME')
    __validate_args(args, argparser)
    return args

if __name__ == '__main__':
    main()
