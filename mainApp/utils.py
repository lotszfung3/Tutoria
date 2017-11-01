from datetime import datetime, timezone

def getSlotIdfromDateTime(s_date,tutor_type):
    roundedA = s_date.replace(hour = 0, minute = 0)
    roundedB = datetime.now(timezone.utc).replace(hour = 0, minute = 0,second=0,microsecond=0)
    days = (roundedA - roundedB).days
    print("days: "+str(roundedA)+" "+str(roundedB))
    if(tutor_type=="Private"):
        days*=10
        days+=s_date.hour-1
    else:
        days*=20
        days+=(s_date.hour-1)*2+(0 if s_date.minute==0 else 1)
    return days
