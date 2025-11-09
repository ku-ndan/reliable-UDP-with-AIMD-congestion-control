import socket
import time
import hashlib
import matplotlib.pyplot as plt

# Server information
SERVER_HOST ="10.17.7.218" 
SERVER_PORT = 9801  
timeOut=0.03

start=time.time()*1000
previousTimeOutTime=0
previousRequest=0
static_counter=0
total_rtt=0.001

requestTime=[]
replyTime=[]
requestOffset=[]
replyOffset=[]

def change_timeOut(clientsocket,current_rtt,currentRequest):
    global previousRequest
    global previousTimeOutTime
    global timeOut
    global total_rtt
    if(currentRequest<=previousRequest+1):
        time.sleep(0.001)
        return
    total_rtt+=current_rtt
    timeOut=10*total_rtt/((currentRequest+1)*1000)

    if static_counter > 2:
        timeOut *= (1 + 0.5 * static_counter)   # slower if many losses
        static_counter = 0 
    clientsocket.settimeout(timeOut)


def server_request(message,server_host,server_port,clientsocket,offset, requestNumber):
    global static_counter
    while True:
        try:
            t1=time.time()*1000-start
            clientsocket.sendto(message.encode(),(server_host,server_port))
            currentTime=time.time()*1000-start
            if(offset!=-1):
                requestOffset.append(offset)
                requestTime.append(currentTime)
            serverResponse,serverAddress=clientsocket.recvfrom(2048)
            t2=time.time()*1000-start
            currentTime=time.time()*1000-start
            if(offset!=-1):
                replyOffset.append(offset)
                replyTime.append(currentTime)
            if requestNumber!=-1:
                change_timeOut(clientsocket,t2-t1,requestNumber)
            break
        except socket.timeout as e:
            static_counter+=1
    serverResponse=serverResponse.decode()
    return serverResponse

def connect_server( server_host,server_port):
    global previousTimeOutTime
    clientsocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    clientsocket.settimeout(timeOut)
    message = "SendSize\nReset\n\n"
    serverResponse=server_request(message,server_host,server_port,clientsocket,-1,-1)
    dataSize=int(serverResponse[5:len(serverResponse)-2])
    flag=False
    requestCount=dataSize//1448
    if(1448*requestCount!=dataSize):
        requestCount+=1
    data=[""]*requestCount
    print(dataSize, requestCount)
    totalRcvd=0
    previousTimeOutTime=time.time()*1000-start
    while flag==False:
        for j  in range(0,requestCount):
            if(data[j]!=""):
                continue
            offset=1448
            firstByte=j*1448
            if(j==requestCount-1):
                offset=dataSize-1448*j
            # print("firstByte",firstByte)
            # print("offset",offset)
            message="Offset: "+str(firstByte)+"\nNumBytes: "+str(offset)+"\n\n"
            serverResponse=server_request(message,server_host,server_port,clientsocket,firstByte,j)
            # print(serverResponse)
            data[j]=serverResponse.split("\n\n")[1]
            # if len(serverResponse.split("\n\n")[0].split("\n"))==3:
            #     print(serverResponse.split("\n\n")[0].split("\n")[-1])
            #     print("Squished------------------------------------------------------------------------------------------")
            # print(len(data[j]))
            totalRcvd+=len(data[j])
            # print("Request no.:",j)
            # print("Total data is recievd:" ,totalRcvd)
        # print("************************************************************************************************************************************************")
        # print("Total data requested: ",dataSize)
        # print("Total data is recieved after one loop:",totalRcvd)
        flag=True
        for i in range(0,requestCount):
            if data[i]=="":
                flag=False
                break
    final_data=""
    for i in data:
        final_data+=i
    result=hashlib.md5(final_data.encode())
    hash=result.hexdigest()
    message="Submit: mcs232479_mcs232484@ak\nMD5: "+str(hash)+"\n\n"
    serverResponse=server_request(message,server_host,server_port,clientsocket,-1,-1)
    print(serverResponse)
    with open('data.txt','w') as file:
        file.write(final_data)
    plt.title("Figure 1: Sequence-number trace")
    plt.xlabel("time")
    plt.ylabel("offset")
    plt.scatter(requestTime,requestOffset,label="Request")
    plt.scatter(replyTime,replyOffset,label="Reply")
    plt.legend()
    plt.grid()
    plt.savefig('Sequence-number trace.jpg', format='jpg')
    plt.show()
    

def main():
    connect_server(SERVER_HOST, SERVER_PORT)

if __name__=='__main__':
    main()

