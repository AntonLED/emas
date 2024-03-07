__docformat__ = "reStructuredText"

import logging
import sys
import mysql.connector

from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core
from mas.transactions.topics import MARKET_STATE_TOPIC
from mas.transactions.database_commands import Database_commands

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


def scheduler(config_path, **kwargs):
    try:
        config = utils.load_config(config_path)
    except Exception:
        config = {}

    name = config.get("name", "SchedulerAgent")

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    return Scheduler(name, **kwargs)


class Scheduler(Agent):
    def __init__(self, name="SchedulerAgent", **kwargs):
        super(Scheduler, self).__init__(**kwargs)
        self.name = name
        # self.triger_messages = ["demand-bid", "bid-offer", "market-clearing", "timeout"]
        self.triger_messages = ["demand-bid", "bid-offer", "market-clearing"]
        self.cur_msg_num = 0
        self.msg_count = len(self.triger_messages)
        ###
        self.curtime = 60 * 15

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        pass

    @Core.periodic(5)  # period in seconds
    def market_state_trigger(self):
        cur_state = self.triger_messages[self.cur_msg_num]
        self.vip.pubsub.publish(
            peer="pubsub", topic=MARKET_STATE_TOPIC, message=cur_state
        )
        self.cur_msg_num += 1
        self.cur_msg_num %= self.msg_count
        # FIXME: bad code for time rendering
        if cur_state == "demand-bid":
            t1 = self._format_time()
            self.curtime += 10
            t2 = self._format_time()
            self._update_ui(t1, t2)

    def _format_time(self):
        h = self.curtime // 60
        m = self.curtime - h * 60
        return (h % 24) * 100 + m

    def _update_ui(self, t1, t2):
        # database = mysql.connector.connect(
        #     host=Database_commands.database_params.host,
        #     port=Database_commands.database_params.port,
        #     database=Database_commands.database_params.database,
        #     user=Database_commands.database_params.user,
        #     password=Database_commands.database_params.password,
        # )
        database = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="test"
        )
        if not database:
            return
        cursor = database.cursor()
        query = f"UPDATE tab2 SET val=%s WHERE no = {Database_commands.left_bound}"
        vals = [t1]
        try:
            cursor.execute(query, vals)
            database.commit()
        except Exception as ex:
            _log.error(f"ERROR during mysql query: {ex}")
            database.rollback()
        cursor = database.cursor()
        query = f"UPDATE tab2 SET val=%s WHERE no = {Database_commands.right_bound}"
        vals = [t2]
        try:
            cursor.execute(query, vals)
            database.commit()
        except Exception as ex:
            _log.error(f"ERROR during mysql query: {ex}")
            database.rollback()


def main():
    """Main method called to start the agent."""
    utils.vip_main(scheduler, version=__version__)


if __name__ == "__main__":
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
