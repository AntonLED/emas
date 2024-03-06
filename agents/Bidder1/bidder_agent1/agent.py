__docformat__ = "reStructuredText"

import logging
import sys
import mysql.connector

from volttron.platform.agent import utils
from volttron.platform.vip.agent import Core
from base_agents.BaseBidder import BaseBidder
from mas.transactions.database_commands import Database_commands

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


def bidder_agent1(config_path, **kwargs):
    try:
        config = utils.load_config(config_path)
    except Exception:
        config = {}

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    name = config.get("name", "b")
    rorm = config.get("rorm", 0.0)
    price = config.get("price", 1.0)
    power = config.get("power", 10.0)
    database_params = config.get("database_params")

    return BidderAgent1(name, rorm, price, power, database_params, **kwargs)


class BidderAgent1(BaseBidder):
    def __init__(self, name, rorm, price, power, database_params, **kwargs):
        super().__init__(name=name, rorm=rorm, price=price, power=power, **kwargs)
        ### agent properties
        self.database_params = database_params
        self.database = None
        self.db_connect()
        self.debug_mode = False
        self.fix_power = 3.5 + 2.0
        ###  configuration store routin
        self.default_config = self.get_default_config()
        self.vip.config.set_default("config", self.default_config)
        self.vip.config.subscribe(self.start, actions=["NEW"], pattern="config")
        self.vip.config.subscribe(self.configure, actions=["UPDATE"], pattern="config")

    def get_default_config(self):
        default_config = {
            "name": "Wind",
            "rorm": 0.2,
            "price": 1.0,
            "power": 10.0,
            "debug": False,
            "fix_power": 5.5,
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
        params = {
            "host": "192.168.50.104",
            "port": 3306,
            "database": "Database1",
            "user": "localuser",
            "password": "miptlocal",
        }
        try:
            self.database = mysql.connector.connect(**params)
        except mysql.connector.Error as err:
            _log.error(f"Error during sql connection: {err}")

    def start(self, config_name, action, contents):
        self.configure(config_name, action, contents)
        _log.debug(f"\n\nSTARTING  {self.price}, {self.avail_power} \n\n")

    def configure(self, config_name, action, contents):
        config = self.default_config.copy()
        config.update(contents)
        try:
            name = config["name"]
            rorm = config["rorm"]
            price = config["price"]
            power = config["power"]
            database_params = config["database_params"]
            debug_mode = config["debug"]
            fix_power = config["fix_power"]
        except ValueError as ex:
            _log.error(f"Error during config store: {ex}")
            return
        self.name = name
        self.rorm = rorm
        self.price = price
        self.avail_power = power
        self.database_params = database_params
        self.debug_mode = debug_mode
        self.fix_power = fix_power
        _log.debug(f"\n\nCONFIGURING  {self.price}, {self.avail_power} \n\n")

    def update_power(self):
        if self.debug_mode:
            self.power = self.fix_power
        else:
            return super().update_power()

    # FIXME: fix this shit
    @staticmethod
    def get_price(power):
        return -power * (11.0 - 3.0) / 8.0 / 2.0 + 11.0 / 2.0

    def apply_cycle(self):
        self.update_ui()

    def update_ui(self):
        if not self.database:
            return
        cursor = self.database.cursor()
        query = f"UPDATE tab2 SET val=%s WHERE no = {Database_commands.input_value}"
        vals = [self.power * 1000]
        try:
            cursor.execute(query, vals)
            self.database.commit()
        except Exception as ex:
            _log.error(f"ERROR during mysql query: {ex}")
            self.database.rollback()
        cursor = self.database.cursor()
        query = f"UPDATE tab2 SET val=%s WHERE no = {Database_commands.input_price}"
        vals = [round(BidderAgent1.get_price(self.power), 2)]
        try:
            cursor.execute(query, vals)
            self.database.commit()
        except Exception as ex:
            _log.error(f"ERROR during mysql query: {ex}")
            self.database.rollback()

    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        if self.database:
            self.database.close()
            self.database.disconnect()


def main():
    utils.vip_main(bidder_agent1, version=__version__)


if __name__ == "__main__":
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
