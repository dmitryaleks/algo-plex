import datetime
from algoplex.api.common.audit import Audit

class AlgoAudit(Audit):

    def __init__(self):
        self.fileName = "trading_{}.log".format(datetime.datetime.now()
                                        .strftime("%Y-%m-%d_%H:%M:%S"))
        print("Audit file name:{}".format(self.fileName))
        self.index = 0

    def log(self, msg):
        timestamp = datetime.datetime.now().strftime("%I:%M:%S_%p_B%d%Y")
        msg = '{}: {}: {}'.format(str(self.index), timestamp, msg)
        print(msg)
        with open(self.fileName, "a") as out_file:
            print(msg, file=out_file)
            self.index += 1
            out_file.close()
