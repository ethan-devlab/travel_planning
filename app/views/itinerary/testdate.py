# coding=utf-8

from django.utils.timezone import get_current_timezone, now
import datetime

# date = "2025-06-02T00:23"
date = "2025-06-02 12:41 AM"
t1 = datetime.datetime.strptime(date, "%Y-%m-%d %I:%M %p").strftime("%Y-%m-%dT%H:%M")
print(t1)
# current_tz = get_current_timezone()
# t2 = current_tz.localize(t1)
# print(t2)
