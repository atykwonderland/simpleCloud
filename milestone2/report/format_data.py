import pandas as pd

dirs = ['roundrobin_data/', 'random_data/', 'leastcon_data/']
files = ['light_data_', 'medium_data_', 'heavy_data_']
types = ['50','70']

# ['percent', 'pod name', 'time function called', 'time function returned', 'duration', 'output']

dataframe = pd.DataFrame(columns = ['percent', 'pod name', 'duration', 'algorithm'])

# merge all data and parse
for d in dirs:
    for f in files:
        for t in types:
            df = pd.read_csv('/home/comp598-user/milestone2/'+d+f+t)
            df['algorithm']=d[:-6]
            df.drop('time function called', inplace=True, axis=1)
            df.drop('time function returned', inplace=True, axis=1)
            dataframe.append(df, ignore_index = True)

# get averages for each test type

# rate = 5 requests per second

# compare between different pods for:
# algorithm within pods 
# percent within pods

# Compares throughput of the system between the different pods
# Compares throughput of the system within a pod with different node configurations.

for d in dirs:
    for f in files:
        algo = d[:-6]
        pod = f[:-6]+'_pod'
        df.loc[ df['algorithm'] == algo & df['pod name'] == algo ]
        for t in types:
            df.loc[ df['percent'] == t & df['pod name'] == algo ]