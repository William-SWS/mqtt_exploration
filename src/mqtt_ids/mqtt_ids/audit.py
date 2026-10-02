from __future__ import annotations
import pandas as pd 

DATASETS = {
    "dos" : ("DoS.csv", "DoS"),
    "mitm" : ("MitM.csv", "mitm"),
    "intrusion" : ("Intrusion.csv" , "intrusion")
}

MSGTYPE_NAMES = {  
    
1: "CONNECT",    
2: "CONNACK",
3: "PUBLISH",
4: "PUBACK",
5: "PUBREC",
6: "PUBREL",
7: "PUBCOMP",
8: "SUBSCRIBE",
9: "SUBACK",
10: "UNSUBSCRIBE",
11: "UNSUBACK",
12: "PINGREQ",
13: "PINGRESP",
14: "DISCONNECT",
}

NO_MQTT = "(sem MQTT)"
RESERVED = "(tipo fora da tabela)"

def msgtype_by_clss(df: pd.DataFrame) -> pd.DataFrame:
    """Conta frames por tipo de pacote MQTT e por classe"""
    codes = df["mqtt.msgtype"]
    names = codes.map(MSGTYPE_NAMES)
    names = names.mask(codes.notna() & names.isna(), RESERVED).fillna(NO_MQTT)
    table = pd.crosstab(names, df["type"])
    