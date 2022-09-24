# PIO_Steppermotors
Uses Micropython to get 2-4 synchronized motor activations that are being runned from PIO, using input of steps and angle input possible. It is also possible to read back where the stepper motor is currently at, which is called back as angle in degrees. Motors can run in both direction.

Stepper_controller.py requires manual input of desired pins to use, gear ratio of stepper motor etc and transforms into actual steps on 
the output. This means the user needs to understand that using 20 teeth to drive 40 teeth will double the number of steps per 
full rotation of the output shaft, or what have you.

In Stepper_controller.py you also specify what microstepping resolution you are using, how many steps per revolution your motor currenly 
have at its output (including any attached gear-box).

The PIO programs are activated simultanously and can be doubled if needed. This will require some tinkering by the user. The programs runs at a fixed speeed.

stepper_controller.py is imported into your program as exemplified in main.py where examples on how to call functions are made.
This "demo" Assumes 200 steps per revolution at 1/16 microstepping with an output gear ratio of 1:1.

This will drive most stepper driver boards that uses a Step pin and Direction Pin. Currently tested with A4988 but more boards on the way.
