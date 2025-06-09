# hello ! 

first the data for testing is zipped , unzip it and check that the folder is on .gitignore to do not make troubles xd 

this data is not completed , this is just for now testing and first implementations , 
the data first is structured :
```

data/
├── locationid=X/   # the X is the id of the location of the sensor ( a location can contains one or many sensors )
│   └── year=20YZ/  # 20YZ is the date where the statistic is captured 
│   │   └── month=AB/ # AB is the month expl : 07 or 11 
│   │   │   └── location-X-20XXABCD.csv.gz  # CD is the date 

```


note hadoop is working with Java , we hose to learn something new and make some difference o work with python , there's some libraries tha help generate hadoop necessary classes 

now , if you wanna get all te dependencies for hadoop , hawkoum fel dockerfile file just run an image oof it using this command : 

```bash
docker build -t hadoop-python-local .
```
and after that run a container of that image : 

```bash
docker run -it --name hadoop-container hadoop-python-local  // docker run -it --name 
hadoop-container hadoop-image /bin/bash
```

to run python  we need , to install the lbraries :

    pip install pyarrow


okkey now how to run el hadoop ya e5watii : 

- first pull the image from ``idpx/hadoop-cluster:latest`` : 

```bash
docker pull idpx/hadoop-cluster:latest
docker network create --driver=bridge hadoop
docker run -itd --net=hadoop -p 9870:9870 -p 8088:8088 -p 7077:7077 -p 16010:16010 --name hadoop-master --hostname hadoop-master idpx/hadoop-cluster:latest
docker run -itd -p 8040:8042 --net=hadoop --name hadoop-worker-1 --hostname hadoop-worker-1 idpx/hadoop-cluster:latest
docker run -itd -p 8041:8042 --net=hadoop --name hadoop-worker-2 --hostname hadoop-worker-2 idpx/hadoop-cluster:latest
docker run -itd -p 8042:8042 --net=hadoop --name hadoop-worker-3 --hostname hadoop-worker-3 idpx/hadoop-cluster:latest
docker exec -it hadoop-master bash 
```
    # ./start-hadoop.sh
emchi el cmd marra o5ra w cp the mapreduce folder on the hadoop-master : 
    docker cp /path/to/mapreduce/locally/fel/pc/mte3ik hadoop-master: /root/

Now I use the data to check (the split-data ) BUT IT's not here in repository bc it containes so much data files 
    
be3id n7outou el mapper w el reducer fi hdfs
    docker exec -it hadoop-master bash
        hdfs dfs -mkdir -p /user/root/mapreduce
        hdfs dfs -put ./mapreduce/mapper.py /user/root/mapreduce/
        hdfs dfs -put ./mapreduce/reducer.py /user/root/mapreduce/

create the input file /input in hdfs also and add on it the input data 

then know test the streaming  (hadoop mapreduce ) 
        hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar   -files ./mapreduce/mapper.py,./mapreduce/reducer.py   -input /input   -output /output   -mapper "python3 mapper.py"   -reducer "python3 reducer.py"


