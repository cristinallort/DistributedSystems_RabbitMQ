# Distributed Systems: functions in the Cloud
Foundations of distributed systems: Playing out with serverless functions in the Cloud

## Authors
Catalina Vilsan and Cristina Llort.

## How it works?
1. First of all we call the leader (my_master_function), whose queue (master_queue) is implemented by using a Direct RabbitMQ queue. 
2. Then, we have implemented one function (my_function_map) that is called 10, 20, 50, 80, ... times. One call for every mapper.
3. Every mapper will send a petition to the leader.
4. The leader will read the petitions and will decide which function is allowed to write in each moment (mutual exclusion). 
5. The function must generate a random integer number (between 0 and 1000). 
6. Then we synchronize this number with the rest of the functions using a Fanout RabbitMQ queue.
7. Every mapper will put (append) the number into a list. 
6. At the end, all the functions must return the same list. 

## How to execute it?
1. Create an IBM Cloud account with a RabbitMQ Service.
2. Modify pywren_config -> include your credentials and put the file in your home directory.
3. Execute orchestrator.py in your console(Linux):
python3 orchestrator.py "number_of_mappers"

## Architecture and implementation
