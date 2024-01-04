filter on - means grab the list and filter by a pk

using pk - directly use the pk given in the model

show - from database

grab - from user


### TASK

form
issue command TASK >
    makes agent w arguments_to_agent
    > makes endpoint w agent and protocol
        links many protocol to endpoint

view associated ENDPOINT >
    navigate to endpoint page using pk
    
view associated USER >
    navigate to user page using pk
    
view associated TASKRESULT >
    show taskresult w filter on task
    
view associated LOGS >
    show logs w filter on endpoint or task result
    

view RUNNING/COMPLETED TASKS >
    count all TASK by using in_progress_bool

view TOTAL TASKS >
    count all TASKS

view OPEN CALLBACKS >
    what the fuck is this

view ALL TASKS >
    show endpoint, user, time_stamp



### ENDPOINT
form
generate payload ENDPOINT > 
    makes agent
    associates encryption and hmac key w endpoint (reg POST)
    links many protocols to endpoint (checkboxes)

view associated TASKS w ENDPOINT >
    show tasks w filter on endpoint

view associated LOGS w ENDPOINT >
    show logs w filter on endpoint

show ENDPOINTS > 
    show name, hostname, addres, date

show ENDPOINT graph >
    what the fuck is this
    communication by protocol??? 


### AGENT

register AGENT >
    create new agent

delete AGENT > 

show AGENTS >
    show agents list
        > show name, os, protocol, endpoint count
            endpoint count > count endpoints with filter agents 

create payload ENDPOINT from AGENT >
    make endpoint prefilled with agent
    # temporarily just link to endpoint page

show command list >
    no way to do this from backend unless destructuring the file or smth

show related ENDPOINTS >
    filter endpoints using agent pk


### PROTOCOL

register PROTOCOL >
    create new protocol

delete PROTOCOL > 

show PROTOCOLS >
    show protocols list
        > show name, endpoint count
            endpoint count > count endpoints with filter protocols 

show PROTOCOL graph >
    what the fuck is this
    communication by protocol??? 



### FILES

show FILE list >
    show filename, filepath
    show timestamp >
        what timestamp do we show? end_time on task?
    show source >
        show endpoint >
            filter tasks using pk
        



### CREDS

show CREDS list >
    show filename, filepath, credential value/type, expiry
    show timestamp >
        what timestamp do we show? end_time on task?
    show source >
        show endpoint >
            filter tasks using pk
    
    



### REPORTING
form
generate REPORT >
    > filter
        grab source / endpoint
        grab user 
        grab task
        grab log
        grab start_time 
        grab category 
        grab end time
    > export only needed
        grab log, source, user, task, category, level, timestamp, data
    > export format
        grab format
