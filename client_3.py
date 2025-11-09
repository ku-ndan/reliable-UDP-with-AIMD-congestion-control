import socket
import time
import hashlib
import matplotlib.pyplot as plt

# Server information
SERVER_HOST =   '10.17.7.218'#'10.17.6.5' #'10.17.51.115'#"10.17.7.218" #'10.17.6.5'# 'vayu.iitd.ac.in'#  "127.0.0.1"#  
SERVER_PORT = 9802  
timeOut=0.01

start=time.time()*1000
predicted_rtt=0.4
predicted_deviation=0
alpha=0.25
beta=0.125

threshold=8

requestTime=[]
replyTime=[]
requestOffset=[]
replyOffset=[]
burstSize=[]
burstSizeTime=[]

def change_timeOut(clientsocket,current_rtt):
    global predicted_rtt
    global predicted_deviation
    global alpha
    global beta
    actual_deviation=abs(current_rtt-predicted_rtt)
    predicted_rtt=alpha*current_rtt+(1-alpha)*predicted_rtt
    predicted_deviation=beta*actual_deviation+(1-beta)*predicted_deviation
    timeOut=predicted_rtt+4*predicted_deviation
    clientsocket.settimeout(timeOut)

def change_windowSize(windowSize,requestRcvd,squished):
    global threshold
    if windowSize<=requestRcvd+1:
        if windowSize<=threshold:
            return min(16,2*windowSize)
        else:
            return min(16,windowSize+2)
    windowSize//=2
    threshold=windowSize//2
    if squished==1:
        return 1
    else:
        return windowSize


def connect_server( server_host,server_port):
    global timeOut
    global predicted_rtt
    clientsocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    clientsocket.settimeout(timeOut)
    message = "SendSize\nReset\n\n"
    sc=0
    while True:
        try:
            clientsocket.sendto(message.encode(),(server_host,server_port))
            serverResponse,serverAddress=clientsocket.recvfrom(2048)
            break
        except socket.timeout as e:
            print("Sendsize timeout error")
    dataSize=int(serverResponse[5:len(serverResponse)-2])
    requestCount=dataSize//1448
    if(1448*requestCount!=dataSize):
        requestCount+=1
    data=[""]*requestCount
    data_remains=[0]*requestCount
    for i in range(requestCount):
        data_remains[i]=i
    windowSize=1
    destinationTransmissionTime=0.01
    lastnumbytes=dataSize-1448*(requestCount-1)
    squished=0
    requestinterval=0.00001
    cnt=0
    prelength=len(data_remains)
    prelength2=len(data_remains)
    cnt2=0
    while len(data_remains)>0:
        cnt+=1
        cnt2+=1
        if squished==0:
            if cnt>20 and prelength-len(data_remains)<=10:
                prelength=len(data_remains)
                requestinterval+=0.000001
                cnt=0
            elif cnt2<=20 and prelength2-len(data_remains)>200:
                requestinterval-=0.000001
                prelength2=len(data_remains)
                cnt2=0
        else:
            time.sleep(0.10)
            requestinterval*=10
        currentRtt=0.01
        windowSize=min(windowSize,len(data_remains))
        burstSize.append(windowSize)
        burstSizeTime.append(time.time()*1000-start)
        for i in range(windowSize):
            j=data_remains[i]
            offset=1448
            firstByte=j*1448
            if(j==requestCount-1):  
                offset=lastnumbytes
            message="Offset: "+str(firstByte)+"\nNumBytes: "+str(offset)+"\n\n"
            # print(message)
            requestTime.append(time.time()*1000-start)
            requestOffset.append(firstByte)
            clientsocket.sendto(message.encode(),(server_host,server_port))
            if i==windowSize-1:
                t1=time.time()*1000-start   
            time.sleep(requestinterval)
        requestRcvd=0
        for i in range(windowSize):
            squished=0
            # clientsocket.settimeout(predicted_rtt+(windowSize-i-1)*destinationTransmissionTime)
            try:
                serverResponse,serverAddress=clientsocket.recvfrom(2048)
                serverResponse=serverResponse.decode()
                tempList=serverResponse.split("\n\n")[0].split("\n")
                firstByte=int(tempList[0].split(":")[1])
                replyTime.append(time.time()*1000-start)
                replyOffset.append(firstByte)
                if len(tempList)==3:
                    squished=1
                    sc+=1
                    print(sc,"squished--------------------------------------------------------------------------------------------------------------------------------------------------------------")
                t2=time.time()*1000-start
                ind=firstByte//1448
                data[ind]=serverResponse.split("\n\n")[1]
                data_remains.remove(ind)
                # print(ind)
                # print(data_remains)
                destinationTransmissionTime=(t2-t1)/(i+1)
                if i==0:
                    currentRtt=t2-t1
                requestRcvd+=1
            except:
                print("TimeOut") 
                break
        print(len(data_remains),"************************************************************************************************************************************************************************")
        change_timeOut(clientsocket,currentRtt/1000)
        windowSize=change_windowSize(windowSize,requestRcvd,squished)

    final_data=""
    for i in data:
        final_data+=i
    result=hashlib.md5(final_data.encode())
    hash=result.hexdigest()
    message="Submit: mcs232479_mcs232484@ak\nMD5: "+str(hash)+"\n\n"
    while True:
        try:
            clientsocket.sendto(message.encode(),(server_host,server_port))
            serverResponse,serverAddress=clientsocket.recvfrom(2048)
            break
        except socket.timeout as e:
            print("Submission timeout error")
    serverResponse=serverResponse.decode()
    print(serverResponse)
    print(f"Total data: {dataSize}")
    plt.title("Figure 1: Sequence-number trace")
    plt.xlabel("time")
    plt.ylabel("offset")
    plt.scatter(requestTime,requestOffset,label="Request")
    plt.scatter(replyTime,replyOffset,label="Reply")
    plt.legend()
    plt.grid()
    plt.savefig('Sequence-number trace.jpg', format='jpg')
    plt.figure()
    plt.title("Figure 2: Burst-size-trace")
    plt.xlabel("time")
    plt.ylabel("windowSize")
    plt.plot(burstSizeTime,burstSize)
    plt.grid()
    plt.savefig('burstSize trace.jpg', format='jpg')
    # plt.show()
    

def main():
    connect_server(SERVER_HOST, SERVER_PORT)

if __name__=='__main__':
    main()


