import stepper_controller as ctrl

# stepper_controller can take 3 commands
# angle(x, y)
# steps(x, y)
# instructor((x,y),)

# About the output in REPL and arguments used in the program.
# Steps are always integers, there are no half steps.
# Angles can be float as they are rounded to the closest integer.
# Elements within instructor tuple are treated as steps.
# Calling position will give the angle that is required 

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
# ctrl.position() - Prints corrent angle for both motors.
# ctrl. position (1, 0) - Returns angle for motor x
# ctrl. position (0, 1) - Returns angle for motor y'
# ctrl. position (1, 1) - Returns angle for motor x and y from a Tuple
# The tuple can be accessed with ctrl.position(1, 1)[0] for motor x (Element 0)
# and ctrl.position(1, 1)[1] for motor y (Element 1)

# Some basic scorcery can be done to zero stepper by using position inside angle
# ctrl.angle(-1*ctrl. position (1, 0), -1*ctrl. position (0, 1)) which flips the current angles polarities and use them as instructions.

input("Press enter to perform test")

#TEST
ctrl.angle(180, -45)
ctrl.steps(-1600, 400)
ctrl.instructor(((200, 400), (-400, 800), (800, 1600), (-1600, 3200), (3200, 6400)))
input("Press enter to return to zero")
ctrl.angle(-1*ctrl. position (1, 0), -1*ctrl. position (0, 1))
