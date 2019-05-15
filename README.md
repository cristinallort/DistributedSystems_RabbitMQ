# Distributed Systems: functions in the Cloud
Foundations of distributed systems: Playing out with serverless functions in the Cloud

## Authors
Catalina Vilsan and Cristina Llort.

## How it works?
1. Implement one function, and then spawn this function 10, 20, 50, 80, ... times.
2. First of all the function must select a leader by using a RabbitMQ queue (Centralized/Distributed algorithm). 
3. Once the leader is selected, it will decide which function is allowed to write in each moment (mutual exclusion). 
4. The function must generate a random integer number (for example between 0 and 1000). 
5. Then synchronize this number with the rest of the functions by putting (append) the number into a list. 
6. At the end, all the functions must return the same list. 

## How to execute it?
1. Create an IBM Cloud account -> then create a bucket and upload a text file.
2. Modify ibm_cloud_config.txt -> include your credentials and change the format to yaml format.
3. Login to IBM Cloud in your console (Linux): ibmcloud login -a cloud.ibm.com
4. Execute the makefile (Linux).
5. Execute orchestrator.py:
python3 orchestrator.py "number_of_mappers"

## Architecture and implementation
