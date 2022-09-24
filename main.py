import stepper_controller as controller

# stepper_controller can take 3 commands
# angle(x, y)
# steps(x, y)
# instructor((x,y),)

                   ### Angle ###
# Takes a desired positive or negative angle and calculates how.
# many steps to take in any direction to move n degrees.
# Rotate first motor 180 degrees clockwise.
# Rotate second motor 45 degrees counter clockwise.
controller.angle(180, -45)

                   ### Steps ###
# Takes a desired positive or negative number of steps.
# and outputs these steps in positive or negative direction.
# Rotate first motor counter clockwise for 1600 steps.
# Rotate second motor clockwise for 400 steps.
controller.steps(-1600, 400)

                   ### Instructor ###
# This is more of an example to showcase how many instructions can be stored in.
# tuples within tuples to be executed in order. The program also waits.
# for all motors to finish before starting all motors again.
# Each integers here are steps.
controller.instructor(((200, 400), (-400, 800), (800, 1600), (-1600, 3200), (3200, 6400)))
