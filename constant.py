MID_RANGE = 2147483647
MAX_RANGE = MID_RANGE * 2
MAX_SPEED = 300000 #12800 * 3 * 4 safe max speed without stagging is 350000, 1 m/s is about 201575pps with defualt stteping
STEPPING = 8 # 256 microstep refer to page 72 of manual
STEPPING_TABLE={0:1,1:0.5,2:4,3:8,4:16,5:32,6:64,7:128,8:256}
lead = 0.0