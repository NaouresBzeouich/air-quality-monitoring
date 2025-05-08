import pyarrow as pa
import pyarrow.hdfs as hdfs

# Define HDFS connection details
hdfs_host = 'localhost'  
hdfs_port = 9000         # Default Hadoop HDFS port

# Establish a connection to HDFS
fs = hdfs.HadoopFileSystem(host=hdfs_host, port=hdfs_port)

# Path on HDFS to read/write data
hdfs_path = '/user/hadoop/testfile.txt'

# Writing to HDFS
with fs.open(hdfs_path, 'wb') as f:
    f.write(b'Hello from Python to HDFS!')

# Reading from HDFS
with fs.open(hdfs_path, 'rb') as f:
    data = f.read()
    print(f'Read from HDFS: {data.decode()}')
