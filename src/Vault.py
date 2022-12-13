import requests

class Vault():

    base_url = "https://api.github.com"

    def __init__(self):
        self.username = 'user'
        self.pat = 'pass'
        self.headers = {'Content-Type': 'application/json'}



    def _getRepos(self, token, namespace):
        try:
            with open("templates/config", "r") as file:
                data = file.read()
                data = data.replace("##certificate_authority_data##", self.certificate_authority_data)
                data = data.replace("##api_server##", self.api_server)
                data = data.replace("##cluster_name##", self.cluster_name)
                data = data.replace("##namespace##", namespace)
                data = data.replace("##token##", token)
            return data
        except Exception as e:
            logging.error(e)

    def createNewKubeConfig(self, namespace):
        try:
            KubeConfig._createNameSpace(self, namespace)

            KubeConfig._createServiceAccount(self, namespace)

            KubeConfig._createSaRbac(self, namespace)

            token = KubeConfig._getServiceAccountToken(self, namespace)

            return KubeConfig._createKubeConfig(self, token, namespace)
        except Exception as e:
            logging.error(e)