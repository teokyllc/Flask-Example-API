import requests
import logging

class Github:

    base_url = "https://api.github.com"
    github_org = "teokyllc"

    def __init__(self, pat):
        self.pat = pat

    def _createHeader(self, pat):
        header = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": "Bearer " + pat
        }
        return header

    def createRepo(self, name, description="", homepage="", private=True, issues=True, projects=False, wiki=False):
        endpoint = "/orgs/" + self.github_org + "/repos"
        url = self.base_url + endpoint
        header = self._createHeader(self.pat)
        data = {
            "name": name,
            "description": description,
            "homepage": homepage,
            "private": private,
            "has_issues": issues,
            "has_projects": projects,
            "has_wiki": wiki
        }
        response = requests.post(url, headers=header, json=data)
        if response.status_code == 200:
            print(response.json())
        else:
            print('Request failed with status code: ' + str(response.status_code))