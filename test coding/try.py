import json 


class Save_Axis_Pram:
    def __init__(self):
        super().__init__()
        self
axis=0
value=836249  
# function to add to JSON 
def write_json(data, filename='data.json'): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4) 
      
      

file_name='ref_pos.json'

try:
    with open(file_name) as json_file:
        data=json.load(json_file)
            
except :
        data={}
dictionary={
                "axis_0":{"lenght":value}
            }
data.update(dictionary)



print(data)

write_json(data,file_name)