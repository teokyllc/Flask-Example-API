from flask import Flask, request, jsonify
from ldap3 import Server, Connection, ALL
import requests
import logging
import json
from Github import Github

app = Flask(__name__)
global ldap_server, netbios, vault_server, tls_verify
ldap_server = "ad1.teokyllc.internal"
netbios = "teokyllc"
vault_server = "https://vault.teokyllc.internal:8200"
tls_verify = False

consoleHandler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)-10s: %(message)s")
consoleHandler.setFormatter(formatter)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(consoleHandler)


def authorize_user(headers):
    log.info("Pulling credentials from header")
    username = headers.get('username')
    login_name = netbios + "\\" + username
    password = headers.get('password')

    print(password)

    log.info("Connecting to the LDAP server: " + ldap_server)

    try:
        server = Server(ldap_server, port=636, use_ssl=True)
        conn = Connection(server, user=login_name, password=password, auto_bind=True)
        conn.bind()
    except:
        log.info(f"Invalid credentials for user {login_name} on server {ldap_server}")
        return 'Unauthorized', 401

    log.info("Authentication was successful")
    log.info(f"Checking AD group membership for user {username}")

    conn.search('DC=teokyllc,DC=internal',f'(&(objectclass=user)(sAMAccountName={username}))', attributes=['memberOf'])
    response = json.loads(conn.response_to_json())
    groups = response["entries"][0]["attributes"]["memberOf"]
    log.debug(groups)

    for group in groups:
        if group == "CN=Domain Admins,CN=Users,DC=teokyllc,DC=internal":
            log.debug(f"Found {group}")
            matched = True

    if matched != True:
        log.info(f"User {username} was not authorized")
        return 'Unauthorized', 401

    log.info(f"Checking if {username} can aquire a Vault token")
    url = vault_server + "/v1/auth/ldap/login/" + username
    data = {"password": password}
    try:
        response = requests.post(url, data=data, verify=tls_verify)
        token = response.json()["auth"]["client_token"]
    except:
        log.info(f"User {username} could not aquire a Vault token")
        return 'Unauthorized', 401

    log.info(f"User {username} was successfully authorized")
    return 'User authorized successfully', 200, token


def getVaultSecret(token, mount, secret_path, key):
    headers = {"X-Vault-Token": token}
    base_url = "https://vault.teokyllc.internal:8200"
    url = base_url + "/v1/" + mount + "/data/" + secret_path
    response = requests.get(url, headers=headers, verify=tls_verify)
    if response.status_code == 200:
        try:
            return response.json()["data"]["data"][key]
        except:
            print(f"Could not find key named {key} in the secret {secret_path}")
    else:
        print(response.json())


@app.route('/repo/<name>', methods=['POST'])
def new_repo(name):
    log.debug("POST /repo")
    # Create github repo
    # create ADO pipeline
    
    log.debug("authorize_user function")
    authorized = authorize_user(request.headers)
    if authorized[1] != 200:
        print(authorized)
        return 'Unauthorized', 401

    vault_token = authorized[2]
    log.debug("Vault token aquired")

    github_pat = getVaultSecret(vault_token, "kv", "github", "pat")

    try:
        github = Github(pat=github_pat)
        github.createRepo("test-repo")
        return 'Git repo created successfully', 200
    except:
        return 'Git repo failed to create', 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

