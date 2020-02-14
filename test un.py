from Phantom_Pi import *
import matplotlib.pyplot as plt
import math


def load_motion_data(filename, delimiter='\t'):
    data = read_csv_file(filename, delimiter=delimiter)
    x = selecting_column(data, 0)
    v = selecting_column(data, 1)
    a = selecting_column(data, 2)
    return x, v, a


def velocity_movement(lead):
    x, v, a = load_motion_data("sin_taj.csv", ',')
    v[:] = [round(item / lead) for item in v]
    a[:] = [round(item) for item in a]
    v = v[::21] # .02 values
    a =a [::21]  # .02 values
    # v=v[:75]
    i = 0
    movement_log = []
    pos=0
    while i < 1:
        for item, a_item in zip(v[:-1], a[:-1]):
            # module_tmcm_1276.rotate(item)
            # time.sleep(.02)
            pos = round((pos+item*.02),2)
            movement_log.append([i, item, pos, a_item])
        i += 1
        # print(i)
        # print_position(module_tmcm_1276)
    return movement_log


x, v, a = load_motion_data("sin_taj.csv", ',')
lead = lead_per_pulse(256, 0.10, 'in')
out=velocity_movement(lead)

_y=[]
for item in out:
    _y.append(round(item[1],4))
print(sum(_y))
print(pulse_to_unit(sum(_y)))
_x = range(0, len(_y))

plt.plot(_x,_y)
plt.show() 
print("WEW")