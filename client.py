import socket
import time
import hashlib
import matplotlib.pyplot as plt

# Server information
SERVER_HOST = "127.0.0.1" 
SERVER_PORT = 9801  
timeOut=1
start=time.time()*1000
requestTime=[]
replyTime=[]
requestOffset=[]
replyOffset=[]

def server_request(message,server_host,server_port,clientsocket,offset=-1):
    while True:
        try:
            clientsocket.sendto(message.encode(),(server_host,server_port))
            currentTime=time.time()*1000-start
            if(offset!=-1):
                requestOffset.append(offset)
                requestTime.append(currentTime)
            serverResponse,serverAddress=clientsocket.recvfrom(2048)
            currentTime=time.time()*1000-start
            if(offset!=-1):
                replyOffset.append(offset)
                replyTime.append(currentTime)
            break
        except socket.timeout as e:
            print("Timeout error")
    # timeOut=time.time()-start
    # clientsocket.settimeout(timeOut)
    serverResponse=serverResponse.decode()
    return serverResponse

def connect_server( server_host,server_port):
    clientsocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    clientsocket.settimeout(timeOut)
    message = "SendSize\nReset\n\n"
    serverResponse=server_request(message,server_host,server_port,clientsocket)
    dataSize=int(serverResponse[5:len(serverResponse)-2])
    flag=False
    requestCount=dataSize//1448
    if(1448*requestCount!=dataSize):
        requestCount+=1
    data=[""]*requestCount
    print(dataSize, requestCount)
    totalRcvd=0
    while flag==False:
        for j  in range(0,requestCount):
            if(data[j]!=""):
                continue
            offset=1448
            firstByte=j*1448
            if(j==requestCount-1):
                offset=dataSize-1448*j
            print("firstByte",firstByte)
            print("offset",offset)
            message="Offset: "+str(firstByte)+"\nNumBytes: "+str(offset)+"\n\n"
            serverResponse=server_request(message,server_host,server_port,clientsocket,firstByte)
            # print(serverResponse)
            newLineCnt=0
            for i in range(0,len(serverResponse)):
                if serverResponse[i]=='\n':
                    newLineCnt+=1
                    if newLineCnt==3:
                        if serverResponse[i-8:8]=="Squished":
                            i+=1
                        data[j]=serverResponse[i+1:]
                        totalRcvd+=len(data[j])
                        break
            print("Request no.:",j)
            print("Total data is recievd:" ,totalRcvd)
        print("************************************************************************************************************************************************")
        print("Total data is recieved after one loop:",totalRcvd)
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
    serverResponse=server_request(message,server_host,server_port,clientsocket)
    print(serverResponse)
    plt.title("Figure 1: Sequence-number trace")
    plt.xlabel("time")
    plt.ylabel("offset")
    plt.scatter(requestTime,requestOffset,label="Request")
    plt.scatter(replyTime,replyOffset,label="Reply")
    plt.grid()
    plt.savefig('Sequence-number trace.jpg', format='jpg')
    plt.show()
    

def main():
    connect_server(SERVER_HOST, SERVER_PORT)

if __name__=='__main__':
    main()

