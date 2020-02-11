from Phantom_Pi import *

def load_motion_data(filename,delimiter='\t'):
    data=read_csv_file(filename,delimiter=delimiter)
    x=selecting_column(data,0)
    v=selecting_column(data,1)
    a=selecting_column(data,2)
    return x, v, a

x, v, a =load_motion_data("sin_taj.csv",',')
lead = lead_per_pulse(256, 0.10, 'in')
print(lead)
v[:]= [round(item / lead) for item in v] 
print(v[:-1])

print(pulse_to_unit(51200))
