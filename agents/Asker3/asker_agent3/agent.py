__docformat__ = "reStructuredText"

import logging
import sys
import mysql.connector

from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, RPC
from base_agents.BaseAsker import BaseAsker
from mas.transactions.point import Point

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


def asker_agent3(config_path, **kwargs):
    try:
        config = utils.load_config(config_path)
    except Exception:
        config = {}

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    name = config.get("name")
    database_params = config.get("database_params")

    return AskerAgent3(name, database_params, **kwargs)


class AskerAgent3(BaseAsker):
    def __init__(self, name, database_params, **kwargs):
        super().__init__(name, **kwargs)
        ### agent properties
        self.database_params = database_params
        self.database = None
        ###  configuration store routin
        self.default_config = self.get_default_config()
        self.vip.config.set_default("config", self.default_config)
        self.vip.config.subscribe(self.start, actions=["NEW"], pattern="config")
        self.vip.config.subscribe(self.configure, actions=["UPDATE"], pattern="config")

    def get_default_config(self):
        default_config = {
            "name": "asker_default",
            "database_params": {
                "host": "192.168.50.104",
                "port": 3306,
                "database": "Database1",
                "user": "localuser",
                "password": "miptlocal",
            },
        }
        return default_config

    def db_connect(self):
        try:
            self.database = mysql.connector.connect(
                host=self.database_params["host"],
                port=self.database_params["port"],
                database=self.database_params["database"],
                user=self.database_params["user"],
                password=self.database_params["password"],
            )
        except mysql.connector.Error as err:
            _log.error(f"ERROR during database connection: {err}")
            self.database = None

    def start(self, config_name, action, contents):
        self.configure(config_name, action, contents)
        self.db_connect()
        _log.debug(f"\n\nSTARTING\n\n")

    def configure(self, config_name, action, contents):
        config = self.default_config.copy()
        config.update(contents)
        try:
            name = config["name"]
            database_params = config["database_params"]
        except ValueError as ex:
            _log.error(f"Error during config store: {ex}")
            return
        self.name = name
        self.database_params = database_params
        _log.debug(f"\n\nCONFIGURING\n\n")

    def update_curve(self):
        points = [Point(0, 2), Point(0.3, 2)]
        if self.curve.points:
            self.curve.clear()
        for point in points:
            self.curve.add(point)

    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        if self.database:
            self.database.close()


def main():
    """Main method called to start the agent."""
    utils.vip_main(asker_agent3, version=__version__)


if __name__ == "__main__":
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
