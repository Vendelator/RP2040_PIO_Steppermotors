# PIO_Steppermotors
> Uses Micropython to get up to 4 stepper motors run simultaneously. 
> This is done using PIO programs. Each program use 2 state machines.

## Functionallity of the program:
- Drive stepper drivers that takes one Step pin and one Direction pin like a4988, DRV8825 among others.
- Synchronous activation of 4 PIO programs each running 2 state machines with call-back to main program to make sure they are all completed before they can all simultanoeusly can be activated again. Each program can control 1 stepper motor.
- Motors will move like MOVJ (joint movement) which means they will travel their steps as fast as possible and then wait for the other motors.
- Input desired angle for each motor x, y, z and r as ```angle(180, -90, 45, 0) ```. Negative integers are counter clockwise (CCW)
- Input desired number of steps for each motor x, y, z and r as ```steps(3200, -1200, 123, -313) ```. Negative integers are counter clockwise (CCW)
- Each movement instruction calls ```position()``` which will print the motors position in degrees.
- At any point, ```zero()``` will return all motors to their original position.
- There is also a primitive method of feeding ```steps()``` with nestled tuples using ```instructor()``` which unpacks one
element at a time and push these to ```steps()```.


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

## Next release
- Add 3D models
- Video of functionality

## Roadmap (and ideas in no particular order)
- ~~Finish a working example of running 4 motors.~~
- Add functionality of programing motors and store them without the need for a computer. Button, Joy-stick, separate .py-file?
- Look into usin DMA or Array to feed PIO program with instructions to simulate acceleration and retardation? 
- 3D model stl-files to be used as an example. (Crude models exists already)
- Add primitive ramp-up / ramp-down functionallity over PIO
- Add alternative method that works for both Pico and Pico W. It's important to get the visual feedback.
- Using UART to daisy-chain several Pi Picos to be able to have even more motors activate simultanously, still all activating simultanously.
