import socket,pickle,struct,pyaudio

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = socket.gethostbyname(socket.gethostname())
port = 2900
s.bind((host,port))

s.listen(1)

c, addr = s.accept()
print('Got connection from', addr)

readdata = b""
payload_size = struct.calcsize("Q")
stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True, output=True,frames_per_buffer=FRAMES_PER_BUFFER)

while True:
    if c:
        while len(readdata) < payload_size:
            packet = c.recv(4*1024)
            if not packet: break
            readdata+=packet
        packed_message_size = readdata[:payload_size]
        readdata = readdata[payload_size:]
        message_size = struct.unpack("Q", packed_message_size)[0]

        while len(readdata) < message_size:
            readdata += c.recv(4*1024)
        stream_data = readdata[:message_size]
        readdata = readdata[message_size:]
        pstream = pickle.loads(stream_data)
        stream.write(pstream)

        senddata = stream.read(FRAMES_PER_BUFFER)
        serialized_struct = pickle.dumps(senddata)
        message = struct.pack("Q",len(serialized_struct))+serialized_struct
        c.sendto(message, addr)

        if False:
            c.close()