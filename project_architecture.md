## this is a file that describe in high level , the implmentation and data flow and roles for each microservice in the system, and the communication between them .

###project - Portfolio Analyzer

goals:

- prototype end-to-end pipeline (upload → parse → analyze → fetch result)
- understand event-based microservice workflow

the system will be separated to 4 micro-services.
it will be event-base system that will trigger by the messaging queue.

1. node service - http server that will get the files that the user upload, store the files in the DB (in this case the Docker volume / in the future maybe it will be in the cloud),

2. python worker- an python server that its role is to parse the files, validate them and make them ready for the ai request.

3. python al pipeline - a python server that will executer the proccess and the action of the lang-chain . to parse and analyze the data and provide key intakes .

4. messaging queue - a messaging queue that will orchestrate this entire operation and trigger the services when they needed.

break down the key components -

1. http server - will be written in ts- bun . due to its high preference.

2. python server - will be written in python, due to the extensive and popular data parsing libris - pandas.

3. python ai pipeline - will be written in python and implement a service of lang-chain.

4. messaging queue- some local message broker. to trigger the services

additional requirements-
need to impment a docker for the system - it holdes a key role - due its will store the shared data between the microservices.

data flow-
file upload to the server from the restApi server -> after the file been upload and store in the shared data (in the docker) -> the service (restApi server) will transmit a message to the message broker -> message broker will transmit to the python worker the files_ids to parse. after its done and the python server finish, -> transmit message to the message broker-> the python ai pipeline trigger and execute the lang-chain process. store the data in the docker -> transmit to the data broker that the operation ended.

\*the message borker will tracke the files by there name (on save of the files the files will be get uniq ne (file_id) and that how the files will be tracked. )

# rest api server endpoints-

-uploading files
/upload - will allow singel file or more (under 3 files) type csv, xlsx (excel). each file must be under 5mb. Additionaly will return a uniq number. this number will be the key for getting this data after afterwards

-get info
/analyzedInfo/:user_uniq_number - will retrieve the info based on the key.

main goals -

- express server
- python server
- lang-chain agent
- message broker
- pandemic
- docker
- micro services
- unit testing

side quests goals-

- swagger
- rate limiter
- idempotency
- (if make sense) redis and redis caching.
- indexing
- load balancing

next steps (need to delete this text):
go trow the files that in the node service and chack that it algined with the project archtcture .
