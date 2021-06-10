NextTrain.py
San Akdag 2021
Numerated Coding Challenge

Run "python3 NextTrain.py help" to display a helpful printout

Interactive mode:
The program will prompt you to...

1. Select an MBTA route
2. Select a stop along the previously-selected MBTA route
3. Select a direction of travel (if the stop is not a terminus)... 

... it then prints the predicted departure time of the next train and will prompt you to...

4. Return to Step 1 (above) or exit the program

Run "python3 NextTrain.py" to use the program in interactive mode

Command-line mode:
If the desired route/stop/direction are known in advance they can be
supplied as command line arguments to the program. 
The names one uses must match route names and station names exactly 
as described in the respective attributes objects. Any spaces in the name
must be replaced with underscores in order to keep the number of command
line arguments consistent. 
The directions are..

  0 - South/West/Outbound 
  
  1 - North/East/Inbound 

The direction argument is required in command line mode, but ignored if the stop is a terminus
See the help menu for more information.

Run "python3 NextTrain.py Red_Line Park_Street 0" 

I have also implemented an automation test that (eventually) checks all of the
possible route/stop/direction combinations to ensure that no accepted input generates an unforeseen error.

Run "python3 NextTrain.py test" to run the test

Thank you very much for your consideration and I look forward to hearing back.

-San Akdag
