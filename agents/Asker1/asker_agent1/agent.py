__docformat__ = "reStructuredText"

import logging
import sys
import mysql.connector

from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, RPC
from base_agents.BaseAsker import BaseAsker
from mas.transactions.point import Point
from mas.transactions.database_commands import Database_commands

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


def asker_agent1(config_path, **kwargs):
    try:
        config = utils.load_config(config_path)
    except Exception:
        config = {}

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    name = config.get("name")
    database_params = config.get("database_params")
    power_params = config.get("power_params")

    return AskerAgent1(name, database_params, power_params, **kwargs)


class AskerAgent1(BaseAsker):
    def __init__(self, name, database_params, power_params, **kwargs):
        super().__init__(name, **kwargs)
        ### agent properties
        self.database_params = database_params
        self.database = None
        ###  configuration store routin
        self.default_config = self.get_default_config()
        self.db_connect()
        self.vip.config.set_default("config", self.default_config)
        self.vip.config.subscribe(self.start, actions="NEW", pattern="config")
        self.vip.config.subscribe(self.configure, actions="UPDATE", pattern="config")
        ###
        self.power_params = power_params

    def get_default_config(self):
        default_config = {
            "name": "asker_default1",
            "database_params": {
                "host": "192.168.50.104",
                "port": 3306,
                "database": "Database1",
                "user": "localuser",
                "password": "miptlocal",
            },
            "power_params": {"power": 3.0, "price": 3.0},
        }
        return default_config

    def db_connect(self):
        # params = {
        #     "host": "192.168.50.104",
        #     "port": 3306,
        #     "database": "Database1",
        #     "user": "localuser",
        #     "password": "miptlocal",
        # }
        params = {
            "host": "localhost", 
            "user": "root", 
            "password": "test"
        }
        try:
            self.database = mysql.connector.connect(**params)
        except mysql.connector.Error as err:
            _log.error(f"Error during sql connection: {err}")

    def db_disconnect(self):
        self.database.close()
        if self.database.is_connected():
            self.database.disconnect()

    def start(self, config_name, action, contents):
        config = self.default_config.copy()
        config.update(contents)
        try:
            name = config["name"]
            database_params = config["database_params"]
            power_params = config["power_params"]
        except ValueError as ex:
            _log.error(f"Error during config store: {ex}")
            return
        self.name = name
        self.database_params = database_params
        self.power_params = power_params
        _log.debug(f"\n\nSTARTING, name: {self.name}")
        _log.debug("power: " + str(self.power_params["power"]))
        _log.debug("price: " + str(self.power_params["price"]))
        _log.debug("\n\n")

    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        if self.database:
            self.database.close()

    def configure(self, config_name, action, contents):
        config = self.default_config.copy()
        config.update(contents)
        try:
            name = config["name"]
            database_params = config["database_params"]
            power_params = config["power_params"]
        except ValueError as ex:
            _log.error(f"Error during config store: {ex}")
            return
        self.name = name
        self.database_params = database_params
        self.power_params = power_params
        _log.debug(f"\n\nCONFIGURING, name: {self.name}")
        _log.debug("power: " + str(self.power_params["power"]))
        _log.debug("price: " + str(self.power_params["price"]))
        _log.debug("\n\n")

    def apply_clearing(self):
        if self.cur_power is None or self.cur_price is None:
            return
        if self.cur_price > 0.0 and self.cur_power > 0.0:
            self.switch(True)
        else:
            self.cur_power = 0.0
            self.cur_price = 0.0
            self.switch(False)
        self.update_ui(self.power_params["price"])

    def update_curve(self):
        points = [
            Point(0, self.power_params["price"]),
            Point(self.power_params["power"], self.power_params["price"]),
            Point(self.power_params["power"] * 1.000001, 0),
        ]
        if self.curve.points:
            self.curve.clear()
        for point in points:
            self.curve.add(point)

    def switch(self, state: bool):
        if not self.database:
            return
        cursor = self.database.cursor()
        query = f"UPDATE tab2 SET val=%s WHERE no = {Database_commands.relay2_state}"
        vals = [state]
        try:
            cursor.execute(query, vals)
            self.database.commit()
        except Exception as ex:
            _log.error(f"ERROR during mysql query: {ex}")
            self.database.rollback()

    def update_ui(self, price: float):
        if not self.database:
            return
        cursor = self.database.cursor()
        query = f"UPDATE tab2 SET val=%s WHERE no = {Database_commands.asker2_price}"
        vals = [price]
        try:
            cursor.execute(query, vals)
            self.database.commit()
        except Exception as ex:
            _log.error(f"ERROR during mysql query: {ex}")
            self.database.rollback()


def main():
    """Main method called to start the agent."""
    utils.vip_main(asker_agent1, version=__version__)


if __name__ == "__main__":
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
