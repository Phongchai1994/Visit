from dataclasses import dataclass
from smartcard.System import readers
from smartcard.util import toHexString
from typing import Callable, List, Optional, Tuple
import sys

def thai2unicode(data: List[int]) -> str:
    return (
        bytes(data)
        .decode('tis-620', errors='replace')
        .replace('#', ' ')
        .strip()
    )

@dataclass(frozen=True)
class APDUCommand:
    ins: List[int]
    label: str
    decoder: Callable[[List[int]], str] = thai2unicode

class ThaiIDReader:
    def __init__(self):
        self.cid = ""
        self.title = ""
        self.firstname = ""
        self.lastname = ""
        self.address = ""

    class SmartCard:
        SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08]
        APPLET = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]

        def __init__(self, connection):
            self.conn = connection
            self.req: List[int] = []

        def connect(self):
            self.conn.connect()
            atr = self.conn.getATR()
            print("ATR:", toHexString(atr))
            self.req = [0x00, 0xC0, 0x00, 0x01] if atr[:2] == [0x3B, 0x67] else [0x00, 0xC0, 0x00, 0x00]

        def transmit(self, apdu: List[int]) -> Tuple[List[int], int, int]:
            return self.conn.transmit(apdu)

        def initialize(self):
            sw1, sw2 = self.transmit(self.SELECT + self.APPLET)[1:]
            print(f"Select Applet: {sw1:02X} {sw2:02X}")

        def get_data(self, cmd: List[int]) -> List[int]:
            data, sw1, sw2 = self.transmit(cmd)
            data, sw1, sw2 = self.transmit(self.req + [cmd[-1]])
            return data

        def read_field(self, cmd: APDUCommand) -> str:
            data = self.get_data(cmd.ins)
            result = cmd.decoder(data)
            print(f"{cmd.label}: {result}")
            return result

    def select_reader(self) -> Optional[object]:
        rlist = readers()
        if not rlist:
            print("No smartcard readers found.")
            return None
        print("Available readers:")
        for i, r in enumerate(rlist):
            print(f"  [{i}] {r}")
        choice = 0
        print(f"Auto-select reader [0]: {rlist[0]}")
        return rlist[choice]

    def read_card(self):
        reader = self.select_reader()
        if reader is None:
            raise Exception("No reader found")
        conn = reader.createConnection()
        card = self.SmartCard(conn)
        card.connect()
        card.initialize()

        commands = [
            APDUCommand([0x80, 0xB0, 0x00, 0x04, 0x02, 0x00, 0x0D], "CID"),
            APDUCommand([0x80, 0xB0, 0x00, 0x11, 0x02, 0x00, 0x64], "TH Fullname"),
            APDUCommand([0x80, 0xB0, 0x15, 0x79, 0x02, 0x00, 0x64], "Address"),
        ]

        for cmd in commands:
            result = card.read_field(cmd)
            if cmd.label == "CID":
                self.cid = result
            elif cmd.label == "TH Fullname":
                # ใช้ split() เฉยๆ เพื่อแยกทุกช่องว่าง
                parts = result.split()
                if len(parts) >= 3:
                    self.title = parts[0].strip()
                    self.firstname = parts[1].strip()
                    self.lastname = ' '.join(parts[2:]).strip()
                else:
                    self.title = ""
                    self.firstname = result
                    self.lastname = ""
            elif cmd.label == "Address":
                self.address = result

    def get_person_info(self):
        return {
            "cid": self.cid,
            "title": self.title,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "address": self.address
        }

# if __name__ == "__main__":
#     try:
#         reader = ThaiIDReader()
#         reader.read_card()
#         info = reader.get_person_info()
#         print("เลขบัตร:", info["cid"])
#         print("คำนำหน้า:", info["title"])
#         print("ชื่อ:", info["firstname"])
#         print("สกุล:", info["lastname"])
#         print("ที่อยู่:", info["address"])
#     except Exception as e:
#         print("Error:", e)
#     finally:
#         sys.exit()