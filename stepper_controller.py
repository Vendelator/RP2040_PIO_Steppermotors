     ### Libraries ###
import time                      # To be able to add delays (sleep)
from machine import Pin          # To allow software to manipulate board pins
import rp2                       # Is used to make PIO programs

     ### Variables ###
motor_1 = False                   # To be able to check if a motor is completed
motor_2 = False                   # - " -
x = 0                             # Creates variable early to avoid errors
y = 0                             # - " -

     ### Stepper motor setup ###
drv_ms = 16 # resolution of microstepping 1 / 1, 2, 4, 8, 16, 32, 64, 132
motor_steps_per_rev = 200 # Steps per full revolution
gear_ratio = 1 # This is how many times the motor needs to spin to turn output one time 
steps_per_rev = motor_steps_per_rev * drv_ms * gear_ratio # This is steps for one full rotation of output
step_angle = 360 / steps_per_rev # This is the step resolution in degrees
print("Steps per revolution:", steps_per_rev, "steps.",
      "\nOne step is", step_angle, "degrees"
)

     ### Onboard Pin (GPIO 25) set as output pin ###
activation_pin = Pin(25, Pin.OUT) # This pin is used to trigger our PIO programs/functions
                                  # and is mandatory to have synchronous activation of motors

     ### PIO functions ###
# step_counter is a PIO program that takes in a value (desired number of steps)
# by pulling it from FIFO placing it in OSR,
# then copying it over to X and iterates over x until
# it reaches 0, whichs means all steps have been made.
# after each steps, a second PIO program within the same PIO-block
# is called which adds a delay to slow down the steps.
#
# The available blocks and their state machines are:
#      -- PIO block 0 --           -- PIO block 1 --
#   State machine 0, 1, 2, 3    State machine 4, 5, 6, 7
#
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW) # Tells the program that this is a PIO program/function.
                                       # and that it's assigned Pin should be Low / Off 
                                       # when the program starts.
def step_counter():
    wait(1, gpio, 25)       # wait for activation from main function steps()
    
    pull(block)             # pull data from FIFO to OSR, do not proceed if empty
    mov(x, osr)             # copy OSR data into X

    label("count")          # this loop counts down all steps
    jmp(not_x, "end")       # if there are 0 steps jump to end
    set(pins, 1)            # sets Step pin high and waits for 2 us IF ERROR, add [1] or [2]
    set(pins, 0)            # sets step pin low again
    irq(5)                  # sets IRQ 5 high
    irq(block, 4)           # wait for IRQ flag 4 to clear
    jmp(x_dec, "count")     # once IRQ is cleared, removes one x and starts over

    label("end")            # jump here to signal all steps have been made
    irq(block, rel(0))      # Signals IRQ handler that all steps have been made
                            # And waits for handler to clear flag (block)

@rp2.asm_pio()                         # Tells the program that this is a PIO program/function.
                                       # Does nothing extra
def step_speed():
    wait(1, irq, 5)         # waiting for IRQ 2 from SM 0/5, does NOT clear
    set(y, 31)              # set a value to y

    label("delay")          # This should be 1024 us in this loop
    #jmp(not_y, "end")      # If there are 0 steps jump to end
    nop() [20]              # do nothing for [n] instructions
    jmp(y_dec, "delay")     # y not zero, make jump and remove one from y.
    
    #label("end")           # jump here to signal all steps have been made
    irq(clear, 4)           # clear IRQ 4

     ### PIO interupt handlers ###
# These are triggered by step_counter in each PIO block and thus
# there are two similar functions that does the same thing.
# When they are triggered, motor_n turns True and
# they print x or y steps to REPL and which statemachine is done.
def pio_0_handler(sm):
    global motor_1, x
    # Print a (wrapping) timestamp, and the state machine object.
    #print(time.ticks_ms(), sm)
    motor_1 = True
    print(sm, "x: ", x)

def pio_1_handler(sm):
    global motor_2, y
    # Print a (wrapping) timestamp, and the state machine object.
    #print(time.ticks_ms(), sm)
    motor_2 = True
    print(sm, "y: ", y)

     ### Setting up state machines ###
# Motor 1 is separated in the code to better explain each step.
# Motor 2 uses the same code, but is written in a much more readable way.
# Motor 2 is the prefered way to write code.
sc_freq = 4_000_000 # step_counter frequency
ss_freq = 1_000_000 # step_speed frequency
                    # 1_000_000 Hz = 1 MHz means each instruction in PIO is 1us long
                    # 4_000_000 Hz = 4 MHz means each instruction in PIO is 0.25 us long
# Motor 1 - Pio Block 0
dir_pin_1 = Pin(16, Pin.OUT) # Defines Pin 16 as direction pin of motor 1 and as an Output pin
sm_0 = rp2.StateMachine(0,   # Creates object called sm_0 and binds it to state machine 0 inPIO block 0
    step_counter,            # Assigns step_counter as PIO program/function
    freq=sc_freq,            # Sets the PIO frequency to sc_freq
    set_base=Pin(17)         # Sets Pin 17 as first output pin of PIO program/function
)

sm_0.irq(pio_0_handler)              # Directs interrupts from sm_0 to the interrupt handler pio_0_handler()
sm_1 = rp2.StateMachine(1,           # Creates object called sm_1 and binds it to state machine 1 in PIO block 0
                        step_speed,  # Assigns step_speed as PIO program/function
                        freq=ss_freq # Sets the PIO frequency to ss_freq
)

# Motor 2 - Pio Block 1
dir_pin_2 = Pin(21, Pin.OUT)                                                # Direction Pin 17
sm_4 = rp2.StateMachine(4, step_counter, freq=sc_freq+10, set_base=Pin(20)) # Statemachine 4 - PIO block 1
sm_4.irq(pio_1_handler)                                                     #
sm_5 = rp2.StateMachine(5, step_speed, freq=ss_freq+10)                     # Statemachine 5 - PIO block 1

# Activating all state machine
sm_0.active(1), sm_1.active(1) # State machine 0 and 1 in PIO block 0
sm_4.active(1), sm_5.active(1) # State machine 4 and 5 in PIO block 1

def steps(x, y): # Feeds the PIO programs and activates them.
    global motor_1, motor_2
    motor_1 = False
    motor_2 = False
    x_steps = x
    y_steps = y
    if int(x) < 0:
        dir_pin_1.value(1)
        x_steps = x_steps * (-1)
    if int(y) < 0:
        dir_pin_2.value(1)
        y_steps = y_steps * (-1)
    sm_0.put(x_steps)
    sm_4.put(y_steps)
    activation_pin.value(1)
    print("\n### Stepping the steps ###")
    while True:
        if motor_1 and motor_2:
            dir_pin_1.value(0)
            dir_pin_2.value(0)
            activation_pin.value(0) # This is active until both processes have signaled that they are done.
            return
        time.sleep_ms(1)

def angle(x_deg, y_deg):
    global step_angle
    x_steps = round(x_deg / step_angle)
    y_steps = round(y_deg / step_angle)
    if int(x_deg) < 0:
        dir_pin_1.value(1)
        x_steps = x_steps * (-1)
    if int(y_deg) < 0:
        dir_pin_2.value(1)
        y_steps = y_steps * (-1)
#     print(x_steps, y_steps)
    steps(x_steps, y_steps)

def instructor(aquired_tuple):
    instruction_tuple = aquired_tuple
    #Example tuple to use: instructor(((200, 400), (-400, 800), (800, 1600), (-1600, 3200), (3200, 6400)))
    for i in range(len(instruction_tuple)): # loads each item within the instruction tuple and assign to each motor.
        x = int(instruction_tuple[i][0])
        y = int(instruction_tuple[i][1])
        print("\nstepping to: " + "x:" +  str(x) + ", " + "y:" + str(y))
        steps(x, y)

if __name__ == "__main__":
    machine.freq(250_000_000)
    print(machine.freq()/1000000, "MHz clock-speed")
    input("\nPress any key to test:\ninstructor(((200, 400), (-400, 800), (800, 1600), (-1600, 3200), (3200, 6400)))")
    instructor(((200, 400), (-400, 800), (800, 1600), (-1600, 3200), (3200, 6400)))
