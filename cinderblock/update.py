#!/usr/bin/python

from cinderblock.icinderblock import IUpdate
from zope.interface import implementer
import json
import requests


@implementer(IUpdate)
class Update(object):

    def __init__(self, post=requests.post):
        self.post = post

    def post_github_commit_status(self,
                                  state,
                                  context,
                                  details_url,
                                  repo_name,
                                  commit_sha1,
                                  github_user,
                                  github_api_token):
        url = 'https://api.github.com/repos/%s/%s/statuses/%s' % (
            github_user,
            repo_name,
            commit_sha1,
        )
        url += '?access_token=' + github_api_token

        data = {
            'state': state,
            'context': context,
            'description': '{} status: {}'.format(context, state),
            'target_url': details_url,
        }
        headers = {
            'Content-Type': 'application/json',
        }
        self.post(url, data=json.dumps(data), headers=headers)
