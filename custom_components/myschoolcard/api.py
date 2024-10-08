import datetime

import requests
import logging
from .const import (
    DN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

_LOGGER = logging.getLogger(__name__)


class MySchoolCard:
    def __init__(self, phone_number, password):
        self.phone_number = phone_number
        self.password = password
        self.id = ""
        self.uid = ""
        self.cards = []
        self.info = {}

    def login(self):
        login_url = DN + "school/api/login"
        auth_data = {"phone": self.phone_number, "password": self.password}
        session = requests.Session()
        r = session.post(
            login_url,
            data=auth_data,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
            },
        )
        if r.status_code == 200:
            response = r.json()
            self.id = response["parent"]["id"]
            self.uid = response["parent"]["uid"]
            r = session.post(
                DN + "school/api-loginparent?puid=" + str(self.uid),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
                },
                )
            response = r.json()
            if r.status_code == 200:
                for clientlist in response["clientlist"]:
                    self.cards.append(clientlist["id"])
                    self.info[clientlist["id"]] = {}
                    self.info[clientlist["id"]]["line_name"] = clientlist["nick"]
                    self.info[clientlist["id"]]["balance"] = float(
                        clientlist["nicebalance"].replace(" ", "")
                    )
                    self.info[clientlist["id"]]["docnumber"] = clientlist["docnumber"]
                    self.info[clientlist["id"]]["yearpayment"] = clientlist["yearpayment"]
                    self.info[clientlist["id"]]["tctarif"] = clientlist["tctarif"]
            return True
        else:
            _LOGGER.error(r)
            return False

    def get_all_data(self):
        self.login()
        return self.info
