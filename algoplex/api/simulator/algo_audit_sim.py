import datetime
import re
from algoplex.api.common.audit import Audit

class AlgoAuditSim(Audit):

    def __init__(self):
        print("Using simulated audit");
        self.messages = []
        self.index = 0

    def log(self, msg):
        timestamp = datetime.datetime.now().strftime("%I:%M:%S_%p_B%d%Y")
        msg = '{}: {}: {}'.format(str(self.index), timestamp, msg)
        print(msg)
        self.messages.append(msg)
        self.index += 1

    def get_messages(self):
        return self.messages

    def contains_msg(self, msg_pattern):
        pattern = re.compile(msg_pattern)
        msg = next((m for m in self.messages if pattern.match(m)), None)
        return msg != None

