import json
import os

from bs4 import BeautifulSoup
import requests


class SteamApp:
    r = None
    app_id = None

    def __init__(self, app_id):
        self.app_id = str(app_id)

        # If cached item exists, load it. Otherwise, send and receive request
        if os.path.exists('./cache/' + self.app_id + ".json"):
            cached_file = ('./cache/' + self.app_id + ".json")

            with open(cached_file) as file:
                self.r = json.loads(file.read())
                file.close()
        else:
            self.r = json.loads(
                requests.get(("https://store.steampowered.com/api/appdetails?appids=" + self.app_id)).text)

            with open('./cache/' + self.app_id + '.json', 'w') as file:
                file.write(json.dumps(self.r))  # Need to write in proper json
                file.close()

    def __str__(self, ) -> str:
        return "\nTitle: " + self.get(key="name") + "\nid: " + self.app_id

    def get_id(self):
        return self.app_id

    def is_free(self):
        # Checking if the game is free.
        if not self.r[self.app_id]['data']['is_free']:
            return False
        else:
            return True

    def get_dlc(self):
        return self.r[str(self.app_id)]['data']['dlc']

    def get_dlc_apps(self):
        return [SteamApp(app_id=x) for x in self.get_dlc()]

    def get(self, key):
        try:
            return self.r[self.app_id]['data'][str(key)]
        except KeyError as e:
            return "Error: Parameter not recognized. If you need help, check the documentation." + "\n" + str(e)


if __name__ == "__main__":
    # Creating a new instance of the class SteamApp, and passing the app_id 107410 to it.
    arma_3 = SteamApp(107410)
    print(arma_3.get("name"))

    my_dlc_list = arma_3.get_dlc()
    print(my_dlc_list)

    my_dlc = arma_3.get_dlc_apps()
    print(my_dlc[0])

    print(my_dlc[0].is_free())
