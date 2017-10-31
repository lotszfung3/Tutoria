from datetime import datetime, timezone

def getSlotIdfromDateTime(s_date,tutor_type):
    if(tutor_type=="Private"):
        res=10*(s_date-datetime.now(timezone.utc)).days
        res+=s_date.hour-1
    else:
        res=20*(s_date-datetime.now(timezone.utc)).days
        res+=(s_date.hour-1)*2+(0 if s_date.minute==0 else 1)
    return res
