# PIO_Steppermotors
Uses Micropython to get 4 stepper motors to activate synchronized with each other. Stepper motors are then being run using PIO programs. Motors can be driven using input of steps and angle(deg). It is also possible to read back where the stepper motor is currently at. Motors can run in both direction. Instructions can also be stored in a nested tuple, where the program then executes one tuple at a time, waiting for all PIO programs to finish before executing a new tuple until all tuples have been driven. 


## About stepper_controller.py
Stepper_controller.py requires manual input of desired pins to use, gear ratio of stepper motor etc and transforms into actual steps on 
the output. This means the user needs to understand that using 20 teeth to drive 40 teeth will double the number of steps per 
full rotation of the output shaft, or what have you.

In Stepper_controller.py you also specify what microstepping resolution you are using with your driver, how many steps per revolution your motor currenly 
have at its output (including any attached gear-box).

Only two PIO programs are currenlty added to the programbut they can be doubled if needed. This will require some tinkering by the user. The programs runs at a fixed speed. Adding this to the program hold high priority and is due in next release.


## About main.py
stepper_controller.py is imported into your program as exemplified in main.py where examples on how to call functions are made.
This "demo" Assumes 200 steps per revolution at 1/16 microstepping with an output gear ratio of 1:1.

This will drive most stepper driver boards that uses a Step pin and Direction Pin. Currently tested with A4988 but more boards on the way.

## Next release
- 4 stepper motors.

## Roadmap (and ideas in no particular order)
- Create 3 files depending on how many motors that are pre-configured 2, 3 and 4 motors.
- 3D model stl-files to be used as an example. (Crude models exists already)
- Add primitive ramp-up / ramp-down functionallity over PIO
- Add alternative method that works for both Pico and Pico W. It's important to get the visual feedback.
- Using UART to daisy-chain several Pi Picos to be able to have even more motors activate simultanously, still all activating simultanously.
