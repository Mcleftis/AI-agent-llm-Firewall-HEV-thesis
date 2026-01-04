import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')#pws tha fainontai ta logs

class CANBusFirewall:
    def __init__(self):
        #tamonadika IDs pou tha epitrepoume
        self.allowed_ids = [
            0x100, # Engine
            0x200, # Brakes
            0x300, # Battery
            0x400  # Steering
        ]
        #exoume amaksi pou ta pragmata genika einai standard, opote vazoume sygkekrimena stoixeia pou mporoun na mpoun
        
        #edw apothikevetai h teleftaia timh gia kathe ID
        #{ packet_id: value }
        self.last_values = {} 
        
        #to pername sto antikeimeno
        self.max_delta = max_delta 

    def inspect_packet(self, packet_id, payload):
        #eisai mesa stis listes pou orisame?
        if packet_id not in self.allowed_ids:
            logging.warning(f"SECURITY ALERT: Unknown ID {packet_id} tried to enter!")
            return False 
        
        #DoS check
        self.packet_timestamps = [t for t in self.packet_timestamps if current_time - t < 1.0]#krata ta timestamps pou hrthan sto teleftaio defterolepto
        self.packet_timestamps.append(current_time)#kai to neo paketo
        if len(self.packet_timestamps) > self.max_packets_per_sec:#an hrtan mesa sto teleftaio defterolepto polla paketa, pithanothta gia DoS attack
            logging.error(f"DoS ATTACK: High traffic ID {packet_id}")
            self.blocked_ids.append(packet_id)#prosthese afth thn id sta mplokarismena
            return False

        #Delta Check
        try:
            current_value = float(payload) #an den einai noumero, den mporoume na kanoume tipota me to delta
        except (ValueError, TypeError):
            #an px einai leksh den mporoume na kanoume tpt
            return True 

        #exoume ksanadei afto to id?
        if packet_id in self.last_values:
            last_value = self.last_values[packet_id]
            
            #edw ginetia to delta
            delta = abs(current_value - last_value)
            
            if delta > self.max_delta:
                logging.error(f"SPOOFING ALERT: ID {packet_id} jumped from {last_value} to {current_value}!")
                return False # ΜΠΛΟΚΑΡΙΣΜΑ

        #apothikevoume th twrinh timh gia metepeita
        self.last_values[packet_id] = current_value
        
        return True