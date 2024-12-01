# Balance Beam Project by Santiago
import machine, time #importing necesary libraries
servo = machine.PWM(26) #attaches a PWM object to the servo name
servo.freq(50) #sets it t0 50Hz, (based on specification of servo)
servo.duty(78) #the way I placed the servo plastic, as well as the general offset of the servo, gave me this number for 0 degrees.
from hcsr04 import HCSR04 #ultrasonic sensor library

sensor = HCSR04(trigger_pin=13, echo_pin=12)

offset = 78
perfectprop = 0.10
perfectinte = 0.05
perfectderi = 0.03

# function that sets the servo with a specific PWM length
def manual(n):
    servo.duty(n+offset)

def sweep(minangle,maxangle):
    #repeats sweep 5 times
    maxangle*=-1
    time.sleep(0.5)
    servo.duty(offset+minangle)
    time.sleep(0.5)
    servo.duty(offset+maxangle)
    time.sleep(0.5)
    servo.duty(offset+minangle)
    time.sleep(0.5)
    servo.duty(offset+maxangle)
    time.sleep(0.5)
    servo.duty(offset+minangle)
    time.sleep(0.5)
    servo.duty(offset+maxangle)
    time.sleep(0.5)
    servo.duty(offset+minangle)
    time.sleep(0.5)
    servo.duty(offset+maxangle)
    time.sleep(0.5)
    servo.duty(offset+minangle)
    time.sleep(0.5)
    servo.duty(offset+maxangle)
        
def onOffControl():
    sp = 150
    bound = 20
    usp = sp + bound
    lsp = sp - bound
    
    servo.duty(offset+5)
    
    while True:
        d = sensor.distance_mm()
        if d < 350:
            if d > usp:
                servo.duty(offset+15)
            if d < lsp:
                servo.duty(offset-15)
            
    
    

def balance(pgain,igain,dgain):
    prev = sensor.distance_mm()
    ptime = time.time_ns()
    deltaT = 0
    deltaE = 0
    
    prop = 0
    inte = 0
    deri = 0
    
    propgain = pgain
    integain = igain
    derigain = dgain

    sp = 150
    
    bufferAge = 1
    delay = 0.1
    numSamples = int(bufferAge / delay)
    
    counter = 0
    buffer = []
    for i in range(numSamples):
        buffer.append(0)
        
    time.sleep(delay)
    while True:
        #check point
        d = sensor.distance_mm()
        dtime = time.time_ns()
        #check if valid
        if d < 350:
            #calculating error
            e = d - sp
            
            prop = int(propgain*e) #proportional action
            
            #adding error to integral buffer
            if counter == numSamples-1:
                buffer[counter] = e
                counter = 0
            else: #resetting direction for buffer allocation
                buffer[counter] = e
                counter += 1
                
            inte = int(integain*sum(buffer)/numSamples) #integral action
                
            
            #calculating time difference  
            deltaE = e - (prev - sp)
            deltaT = (dtime - ptime)/1e9
            prev = d
            ptime = dtime
            
            deri = int(derigain*(deltaE/deltaT)) #derivative action
            
            newangle = prop + inte + deri #final angle
            
            #final error checking (within operating bounds)
            if newangle > 29:
                newangle = 29
            elif newangle < -26:
                newangle = -26
            servo.duty(newangle+offset)
            print(f"prop: {prop}, inte: {inte}, deri: {deri}, error: {e}") # was used for debugging

             
        
        time.sleep(delay)




# basic Command Line Interface
def main():
    print("Welcome!")
    while True:
        option = input("Please Select Mode by Entering the Corresponding Letter:\na) Control Mode\nb) Testing Mode\n")
        if option == "a":
            while True:
                option = input("Please Select Control Mode by Entering the Corresponding Letter:\na) ON/OFF\nb) Continuous\nc) Previous Menu\n")
                if option == "a":
                    print("Controlling...")
                    onOffControl()
                elif option == "b":
                    while True:
                        option = input("Please Select Actions by Entering the Corresponding Letter:\na) Proportional\nb) Proportional-Integral\nc) Proportional-Integral-Derivative\nd) Previous Menu\n")
                        if option == "a":
                            balance(perfectprop, 0, 0)
                        elif option == "b":
                            balance(perfectprop, perfectinte, 0)
                        elif option == "c":
                            balance(perfectprop, perfectinte, perfectderi)
                        elif option == "d":
                            break
                        else:
                            print("option not available")
                elif option == "c":
                    break
                else:
                    print("option not available")
        elif option == "b":
            print("Entering Testing Mode...\nEnter \"help\" for list of commands")
            while True:
                option = input()
                if option == "help":
                    print("Servo position: e.g. \"set:13\", sets position")
                    print("Alternate: e.g. \"jump:10:10\", alternates between +10 and -10")
                elif option.startswith("jump"):
                    parts = option.split(":")
                    sweep(int(parts[1]),int(parts[2]))
                elif option.startswith("set"):
                    manual(int(option.split(":")[1]))
                elif option == "exit":
                    break
                else:
                    print("Command not Recognized")
                
                
                
        

main()


