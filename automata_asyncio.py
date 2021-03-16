import time
import serial
import random
import asyncio
from math import fsum


# Establish serial connection via PySerial
ser = serial.Serial(
    port='/dev/rfcomm0', # Has to be changed according to the bluetooth serial port
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

catStuff = ['kwkF', 'ksit', 'khi', 'kbuttUp',  'kpee']
weights = [10, 20, 5, 5, 5]  # Increase chance with higher values
avoidanceManeuvers = ['kwkL', 'kwkR']


# Define asynchronous tasks

async def randomMovement():
    while True:
        currentAction = random.choices(catStuff, weights, k=1)
        ser.write(str.encode(currentAction[0])) 
        ser.reset_input_buffer()
        await asyncio.sleep(random.random()*20)


async def avoidObstacle():  
    while True:
        distance = await checkDistance()
        if ((distance[0] and distance[1]) > 1.0):
            print(distance)
            criticalDistance = fsum(distance)/2
            if ((20.0 < criticalDistance < 80.0) and (distance[1] < distance[0]*1.03)):
                ser.write(str.encode(random.choice(avoidanceManeuvers)))              
                await asyncio.sleep(random.random()*3) # 3 worked well, but Nybble tends to walk in circles
                #await asyncio.sleep(1)
            elif (0.0 < criticalDistance <= 20.0):            
                ser.write(str.encode('kbk'))
                await asyncio.sleep(random.random()*3)
            elif ((criticalDistance >= 80.0) and (distance[1]*1.03 > distance[0])):
                ser.write(str.encode('kwkF'))
                await asyncio.sleep(random.random()*3) 


async def checkDistance():
    try:
        distanceT1 = float(ser.readline().decode("ascii"))
        ser.reset_input_buffer()
        await asyncio.sleep(0.5)
        distanceT2 = float(ser.readline().decode("ascii"))
    except:
        distanceT1 = 0
        distanceT2 = 0
    return distanceT1, distanceT2


# Initialize Nybble
time.sleep(10)
ser.write(str.encode('kbalance'))
time.sleep(2)
ser.reset_input_buffer()

# Create Nybble loop
nybble = asyncio.get_event_loop()
asyncio.ensure_future(checkDistance())
#asyncio.ensure_future(randomMovement())
asyncio.ensure_future(avoidObstacle())


nybble.run_forever()


