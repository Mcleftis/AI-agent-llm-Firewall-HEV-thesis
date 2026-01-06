import time
import logging
from typing import List, Dict, Optional 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')#pws fainetai to logging

class CANBusFirewall:
    #type-hinting
    def __init__(self, max_delta: float = 10.0, max_packets: int = 50, auth_token: str = "SECRET_DRIVER_KEY_2026") -> None:#den epistrefei kati
        self.allowed_ids: List[int] = [0x100, 0x200, 0x300, 0x400]#lista apo integers
        self.last_values: Dict[int, float] = {} #ti hrthe teleftaio
        self.packet_timestamps: List[float] = []#ti wra hrthe
        self.blocked_ids: List[int] = []
       
        #pairnw ttis times pou edwse o xrhsths ston constructor
        self.max_delta: float = max_delta
        self.max_packets_per_sec: int = max_packets
        self.auth_token: str = auth_token

    def verify_token(self, input_token: str) -> bool: #epistrefei boolean
        if input_token == self.auth_token:#pou dinoume emeis panw
            logging.info("ACCESS GRANTED: Valid Token.")
            return True
        else:
            logging.critical(f"ACCESS DENIED: Invalid Token '{input_token}'")
            return False

    def inspect_packet(self, packet_id: int, payload: str) -> bool:
        current_time: float = time.time()#wra ekeinh th stigmh

        if packet_id in self.blocked_ids:
            return False

        if packet_id not in self.allowed_ids:
            logging.warning(f"SECURITY ALERT: Unknown ID {packet_id}")
            return False 
        
        #Type Hinting pali
        self.packet_timestamps = [t for t in self.packet_timestamps if current_time - t < 1.0]#krata ta timestamps pou hrthan sto teleftaio sec
        self.packet_timestamps.append(current_time)#apo twra h lista exei kai to neo paketo
        
        if len(self.packet_timestamps) > self.max_packets_per_sec:#an mesa se ena sec hrthan perissoterra apketa apo to epitrepto,exw pithano DoS attack
            logging.error(f"DoS ATTACK: High traffic ID {packet_id}")
            self.blocked_ids.append(packet_id)
            return False

        try:
            current_value: float = float(payload)
        except (ValueError, TypeError):#to payload den einai egkyros arithmos, to payload den einai typos pou mporei na ginei float
            return True 

        if packet_id in self.last_values:#exoume prohgoumenh timh giafth thn IP, an nai delta check
            last_value: float = self.last_values[packet_id]
            delta: float = abs(current_value - last_value)
            
            if delta > self.max_delta:#synthiki gia spoofing
                logging.error(f"SPOOFING ALERT: ID {packet_id} Delta: {delta}")
                return False

        self.last_values[packet_id] = current_value
        return True