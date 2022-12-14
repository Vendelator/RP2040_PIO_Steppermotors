import stepper_controller as ctrl

# stepper_controller can take 3 commands
# angle(x, y)
# steps(x, y)
# instructor((x,y),)

# About the output in REPL and arguments used in the program.
# Steps are always integers, there are no half steps.
# Angles can be float or integers.
# Elements within instructor tuple are treated as steps.
# Calling position will give the angle that is required .

                   ### Angle ###
# Takes a desired positive or negative angle and calculates how.
# many steps to take in any direction to move n degrees.
# Rotate first motor 180 degrees clockwise.
# Rotate second motor 45 degrees counter clockwise.
#ctrl.angle(180, -45)

                   ### Steps ###
# Takes a desired positive or negative number of steps.
# and outputs these steps in positive or negative direction.
# Rotate first motor counter clockwise for 1600 steps.
# Rotate second motor clockwise for 400 steps.
#ctrl.steps(-1600, 400)

                   ### Instructor ###
# This is more of an example to showcase how many instructions can be stored in.
# tuples within tuples to be executed in order. The program also waits.
# for all motors to finish before starting all motors again.
# Each integers here are steps.
#ctrl.instructor(((200, 400), (-400, 800), (800, 1600), (-1600, 3200), (3200, 6400)))

                   ### Position ###
# Calling this function with no arguments tells out program at what angle the motor is currenly at. 720 deg would
# mean we are at position zero, but have turned 2 full turns.
# ctrl.position() - Prints angle for both motors.
# ctrl. position (1, 0) - Returns angle for motor x.
# ctrl. position (0, 1) - Returns angle for motor y.
# ctrl. position (1, 1) - Returns angle for motor x and y in from of a Tuple.
# The tuple can be accessed with ctrl.position(1, 1)[0] for motor x (Element 0)
# and ctrl.position(1, 1)[1] for motor y (Element 1).

# Some basic scorcery can be done to zero stepper by using position inside angle
# ctrl.angle(-1*ctrl. position (1, 0), -1*ctrl. position (0, 1)) which flips the current angles polarities and use them as instructions.
# The function ctrl.zero() does this with less input. This is not the same as home.

#TEST
if __name__ == "__main__":
#     pass
    machine.freq(250_000_000) # Setch CPU frequency to 250 MHz
#     input("\nPress enter to perform test")
#     ctrl.angle(90, -90, 180, -180) # Moves X 90 Deg CW and Y -90 DEG CCW
#     ctrl.steps(-1600, 1600, 200, 400) # Moves X 1600 steps CCW and Y 1600 steps CW
#     ctrl.instructor(((200, 400, -400, 800), (800, -200, 800, -800)))
#     input("Press enter to return to zero")
#     ctrl.zero() # Checks how many steps from start and rotates back.
