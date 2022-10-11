         ### Libraries ###
from time import sleep                      # To be able to add delays (sleep)
from machine import Pin                     # To allow software to manipulate board pins
from rp2 import PIO, StateMachine, asm_pio  # Is used to make PIO programs

         ### Global Variables ###
motor_1 = False                   # To be able to check if a motor is completed
motor_2 = False                   # - " -
motor_3 = False                   # - " -
motor_4 = False                   # - " -
x_last = 0                        # To store relative position in steps
y_last = 0                        # - " -
z_last = 0                        # - " -
r_last = 0                        # - " -
base_delay = 200                  # Sets the motor speed based on a Loop in a PIO routine.



         ### Stepper motor setup ###
# These settings are made for rotational movement only. (Belts, gears etc)
# This means if you want to use a trapetziod for a linear actuator, use the other motor settings.
drv_ms = 32               # resolution of microstepping 1 / 1, 2, 4, 8, 16, 32, 64, 128, write the denominator only
mtr_steps_rev = 200 # steps per full revolution, often 200 or 400
gear_ratio = 1            # This is the total gear ration. Gear ratio 5:1 means you write 5
steps_rev = mtr_steps_rev * drv_ms * gear_ratio # This is the number of steps to move output.
step_angle = 360 / steps_rev # This is the step resolution in degrees
lead_screw_pitch = 2 # This is how far each rotation will move something. 2 [mm] pitch is common for 3D printers.
step_pitch = lead_screw_pitch / steps_rev # This is how far along the lead screw we are moved for each step.
print("For gears, belts and arms.")
print("Steps per revolution:", steps_rev, "steps.",
      "\nOne step is", step_angle, "degrees.\n")
print("For lead screws.")
print ("[mm] per revolution:", lead_screw_pitch,
       "\nOne steps is", step_pitch, "[mm].\n")

# Whith the example above, we get:
# Belt, Gear or Arm 
# Steps per revolution: 3200
# Wormgear or Lead screw
# [mm] per revolution: 2
# One step is 0.1125 degrees


         ### Synchronization Pin ###
activation_pin = Pin(25, Pin.OUT) # Pin 25 is used to trigger our PIO programs/functions
                                  # and is mandatory to have synchronous activation of motors
                                  # For Pi Pico W, chose another Pin and add LED activation for
                                  # visual feedback.

         ### PIO functions ###
# step_counter is a PIO program that takes in a value (desired number of steps)
# by pulling it from FIFO placing it in OSR,
# then copying it over to X and iterates over x until
# it reaches 0, whichs means all steps have been made.
# after each steps, a second PIO program within the same PIO-block
# is called which adds a delay to slow down the steps.
#
#      The available blocks and their state machines are:
#           -- PIO block 0 --           -- PIO block 1 --
#        State machine 0, 1, 2, 3    State machine 4, 5, 6, 7

@asm_pio(sideset_init=PIO.OUT_LOW) # Assembly decorator, sideset pin default Low
                                           # and that it's assigned Pin should be Low / Off 
                                           # when the program starts.
def step_counter():
    pull()                         # wait for FIFO to fill (put), then pull data to OSR
    mov(x, osr)                    # copy OSR data into X (load our steps into x)
    wait(1, gpio, 25)              # waiting for "activation_pin.value(1)"
    label("count")                 # this is a header we jump back to for counting steps
    jmp(not_x, "end")              # if x is 0(zero), jmp to end - Side Step Pin On
    irq(5) .side(1) [1]            # sets IRQ 5 high, starting step_speed() - Side Step Pin Off
    irq(block, 4) .side(0)         # waiting for IRQ flag 4 to clear
    jmp(x_dec, "count")            # if x is NOT 0(zero), remove one (-1) from x and jump back to count, Else, continue
    label("end")                   # This is a header we can jmp to if x is 0.
    irq(block, rel(0))             # Signals IRQ handler that all steps have been made and waits for handler to clear the flag (block)

@asm_pio()                         # Tells the program that this is a PIO program/function.
def step_speed():
    pull(noblock)           # Pulls delay value into PIO routine (OSR)
    mov(x, osr)             # Copies OSR value into X
    mov(y, x)               # Makes a copy of X into Y 
    wait(1, irq, 5)         # Waiting for IRQ flag 5 from step_counter and then clears it
    label("delay")          # This is a header we jump back to for adding a delay
    jmp(x_dec, "delay")     # If y not 0(zero), remove one (-1) from y make jump to delay, Else, continue
    irq(clear, 4)           # Clear IRQ flag 4, allowing step_counter() to continue
    mov(x, y)               # Refills x with y
    mov(osr, y)


     ### PIO interupt handlers ###
# These are triggered by step_counter in each PIO block and thus
# there are two similar functions that does the same thing.
# When they are triggered, motor_n turns True and
# they print x or y steps to REPL and which statemachine is done.
def pio_0_handler(sm): # Motor 1
    global motor_1
    motor_1 = True
    print(sm, "x:", x_last)

def pio_1_handler(sm): # Motor 2
    global motor_2
    motor_2 = True
    print(sm, "y:", y_last)

def pio_2_handler(sm): # Motor 3
    global motor_3
    motor_3 = True
    print(sm, "z:", z_last)

def pio_3_handler(sm): # Motor 4
    global motor_4
    motor_4 = True
    print(sm, "r:", r_last)

     ### Setting up state machines ###
sc_freq = 1_000_000 # step_counter frequency
ss_freq = 1_000_000 # step_speed frequency

# Motor 1 - Pio Block 0
step_pin_1 = Pin(19, Pin.OUT)
dir_pin_1 = Pin(18, Pin.OUT)         # Defines Pin 16 as direction pin of motor 1 and as an Output pin
sm_0 = StateMachine(0,           # Creates object called sm_0 and binds it to state machine 0 inPIO block 0
    step_counter,                    # Assigns step_counter as PIO program/function
    freq=sc_freq,                    # Sets the PIO frequency to sc_freq
    sideset_base=step_pin_1          # Sets Pin 17 as first sideset pin of PIO program/function
)

sm_0.irq(pio_0_handler)              # Directs interrupts from sm_0 to the interrupt handler pio_0_handler()
sm_1 = StateMachine(1,           # Creates object called sm_1 and binds it to state machine 1 in PIO block 0
                        step_speed,  # Assigns step_speed as PIO program/function
                        freq=ss_freq # Sets the PIO frequency to ss_freq
)

# Motor 2 - Pio Block 1
step_pin_2 = Pin(16, Pin.OUT)                                                  # Step Pin 4
dir_pin_2 = Pin(17, Pin.OUT)                                                   # Direction Pin 5
sm_4 = StateMachine(4, step_counter, freq=sc_freq+1, sideset_base=step_pin_2) # Statemachine 4 - PIO block 1
sm_4.irq(pio_1_handler)                                                        #
sm_5 = StateMachine(5, step_speed, freq=ss_freq+1)                        # Statemachine 5 - PIO block 1

# Motor 3 - Pio Block 0
step_pin_3 = Pin(26, Pin.OUT)                                                  # Step Pin 5
dir_pin_3 = Pin(22, Pin.OUT)                                                   # Direction Pin 6
sm_2 = StateMachine(2, step_counter, freq=sc_freq+2, sideset_base=step_pin_3) # Statemachine 2 - PIO block 0
sm_2.irq(pio_2_handler)                                                        #
sm_3 = StateMachine(3, step_speed, freq=ss_freq+2)                        # Statemachine 3 - PIO block 0

# Motor 4 - Pio Block 1
step_pin_4 = Pin(28, Pin.OUT)                                                  # Step Pin 8
dir_pin_4 = Pin(27, Pin.OUT)                                                   # Direction Pin 9
sm_6 = StateMachine(6, step_counter, freq=sc_freq+3, sideset_base=step_pin_4) # Statemachine 6 - PIO block 1
sm_6.irq(pio_3_handler)                                                        #
sm_7 = StateMachine(7, step_speed, freq=ss_freq+3)                        # Statemachine 7 - PIO block 1

# Activating all state machine
sm_0.active(1), sm_1.active(1) # Motor 1 State machine 0 and 1 in PIO block 0
sm_4.active(1), sm_5.active(1) # Motor 2 State machine 4 and 5 in PIO block 1
sm_2.active(1), sm_3.active(1) # Motor 3 State machine 2 and 3 in PIO block 0
sm_6.active(1), sm_7.active(1) # Motor 4 State machine 6 and 7 in PIO block 1



def runner(x, y, z, r): # Feeds the PIO programs and activates them.
    global motor_1, motor_2, motor_3, motor_4
    global x_last, y_last, z_last, r_last
    global base_delay
    x_last = x + x_last
    y_last = y + y_last
    z_last = z + z_last
    r_last = r + r_last
    x_steps = round(x)
    y_steps = round(y)
    z_steps = round(z)
    r_steps = round(r)
    if int(x) < 0:
        dir_pin_1.value(1)
        x_steps = x_steps * (-1)
    if int(y) < 0:
        dir_pin_2.value(1)
        y_steps = y_steps * (-1)
    if int(z) < 0:
        dir_pin_3.value(1)
        z_steps = z_steps * (-1)
    if int(r) < 0:
        dir_pin_4.value(1)
        r_steps = r_steps * (-1)
    delay_adjustment = motor_sync(x, y, z, r)
#     print(delay_adjustment)

    # Clear sm_1 so that only new values exists as delays
    sm_1.exec("mov(osr, null)"), sm_1.exec("mov(x, null)"), sm_1.exec("mov(y, null)") # Clear statemachine sm_1
    sm_5.exec("mov(osr, null)"), sm_5.exec("mov(x, null)"), sm_5.exec("mov(y, null)") # Clear statemachine sm_5
    sm_3.exec("mov(osr, null)"), sm_3.exec("mov(x, null)"), sm_3.exec("mov(y, null)") # Clear statemachine sm_3
    sm_7.exec("mov(osr, null)"), sm_7.exec("mov(x, null)"), sm_7.exec("mov(y, null)") # Clear statemachine sm_7
    
    sm_1.put(delay_adjustment[0])                              # Add new delay value
    sm_5.put(delay_adjustment[1])                              # Add new delay value
    sm_3.put(delay_adjustment[2])                              # Add new delay value
    sm_7.put(delay_adjustment[3])                              # Add new delay value
    
    sleep(0.5)
    
    sm_0.put(x_steps)                                                                 # Add new n steps to sm_0
    sm_4.put(y_steps)                                                                 # Add new n steps to sm_4
    sm_2.put(z_steps)                                                                 # Add new n steps to sm_2
    sm_6.put(r_steps)                                                                 # Add new n steps to sm_6
    
    sleep(0.5)                                                                        # Short delay to make sure all state machines
                                                                                      # have recieved their values
    activation_pin.value(1)                                                           # Start running motors.
    print("\n### Stepping the steps... ###")
    print("\nSteps from origin: " + "\nx:" +  str(x_last) + "\ny:" + str(y_last), "\nz:" +  str(z_last) + "\nr:" + str(r_last), "\n")
    while True:
        if motor_1 and motor_2 and motor_3 and motor_4:
            dir_pin_1.value(0)
            dir_pin_2.value(0)
            dir_pin_3.value(0)
            dir_pin_4.value(0)
            motor_1 = False
            motor_2 = False
            motor_3 = False
            motor_4 = False
            activation_pin.value(0) # This is active until both processes have signaled that they are done.
            position()
            return
        sleep(0.2)

def steps(x_steps, y_steps, z_steps, r_steps):
    runner(x_steps, y_steps, z_steps, r_steps)

def angle(x_deg, y_deg, z_deg, r_deg):
    #global step_angle # Redundant? Because only read state
    x_steps = round(x_deg / step_angle) # No need to round?! Because angle is a product from steps and step_angle already.
    y_steps = round(y_deg / step_angle)
    z_steps = round(z_deg / step_angle)
    r_steps = round(r_deg / step_angle)
    runner(x_steps, y_steps, z_steps, r_steps)

def angle_instructor(aquired_tuple):
    instruction_tuple = aquired_tuple
    for i in range(len(instruction_tuple)): # loads each item within the instruction tuple and assign to each motor.
        x_steps = int(instruction_tuple[i][0] / step_angle)
        y_steps = int(instruction_tuple[i][1] / step_angle)
        z_steps = int(instruction_tuple[i][2] / step_angle)
        r_steps = int(instruction_tuple[i][3] / step_angle)
        runner(x_steps, y_steps, z_steps, r_steps)

def step_instructor(aquired_tuple):
    instruction_tuple = aquired_tuple
    for j in range(len(instruction_tuple)): # loads each item within the instruction tuple and assign to each motor.
        x_steps = int(instruction_tuple[j][0])
        y_steps = int(instruction_tuple[j][1])
        z_steps = int(instruction_tuple[j][2])
        r_steps = int(instruction_tuple[j][3])
        runner(x_steps, y_steps, z_steps, r_steps)

def position(x = 0, y = 0, z=0, r=0):
    global x_last, y_last, z_last, r_last
    x_angle = step_angle * x_last
    y_angle = step_angle * y_last
    z_angle = step_angle * z_last
    r_angle = step_angle * r_last
    if x != 0 and y != 0 and z != 0 and r != 0:
        print("x at:", x_angle, "\u00B0")
        print("y at:", y_angle, "\u00B0")
        print("z at:", z_angle, "\u00B0")
        print("r at:", r_angle, "\u00B0")
        return x_angle, y_angle, z_angle, r_angle
    elif x != 0:
        print("x at:", x_angle, "\u00B0")
        return x_angle
    elif y != 0:
        print("y at:", y_angle, "\u00B0")
        return y_angle
    elif z != 0:
        print("z at:", z_angle, "\u00B0")
        return z_angle
    elif r != 0:
        print("r at:", r_angle, "\u00B0")
        return r_angle
    else:
        print("x at:", x_angle, "\u00B0")
        print("y at:", y_angle, "\u00B0")
        print("z at:", z_angle, "\u00B0")
        print("r at:", r_angle, "\u00B0")

def zero():
    angle(-1 * position (1, 0, 0, 0), -1 * position (0, 1, 0, 0), -1 * position (0, 0, 1, 0), -1 * position (0, 0, 0, 1))

def motor_sync(x, y, z, r):
    global base_delay
    tupl = (abs(x), abs(y), abs(z), abs(r))
    highest_count = max(tupl)
    if tupl[0] > 0:
        x_delay = tupl[0] / highest_count
    else:
        x_delay = 1
    if tupl[1] > 0:
        y_delay = tupl[1] / highest_count
    else:
        y_delay = 1
    if tupl[2] > 0:
        z_delay = tupl[2] / highest_count
    else:
        z_delay = 1
    if tupl[3] > 0:
        r_delay = tupl[3] / highest_count
    else:
        r_delay = 1
    
    print(x_delay, y_delay, z_delay, r_delay)
    
    if x_delay != 1.0:
        x_delay = -(-base_delay // x_delay)#*2
    else:
        x_delay = base_delay
    
    if y_delay != 1.0:
        y_delay = -(-base_delay // y_delay)#*2
    else:
        y_delay = base_delay
    
    if z_delay != 1.0:
        z_delay = -(-base_delay // z_delay)#*2
    else:
        z_delay = base_delay
    
    if r_delay != 1.0:
        r_delay = -(-base_delay // r_delay)#*2
    else:
        r_delay = base_delay
    
    print(x_delay, y_delay, z_delay, r_delay)
    
    return (round(x_delay), round(y_delay), round(z_delay), round(r_delay))

if __name__ == "__main__":
    machine.freq(250_000_000)
#     print(machine.freq()/1000000, "MHz clock-speed")
#     input("\nPress any key to test:\nstep_instructor()")
#     step_instructor(((200, 400, -400, 800), (800, -200, 800, -800)))

