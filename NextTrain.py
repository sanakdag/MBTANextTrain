
###############################################################################
############################## NextTrain.py ###################################
###############################################################################
############################  San Akdag 2021 ##################################
###############################################################################
'''
Numerated Coding Challenge 

Please see requirements.txt

Please use Python 3.9.5 ...

and install the requests pkg with the following command (if not installed):
	
	pip3 install requests

NextTrain.py prompts the user for a route, stop, and direction (if applicable) 
and prints the next departure time for the route/stop/direction combination if 
one is scheduled. NextTrain.py will ensure that the rate limit set by the MBTA
API is not exceeded and will cache all route, stop, and direction information 
in order avoid submitting duplicate requests to the API and to improve 
performance.

Thank you for your consideration and I'm looking forward to the next steps :)

'''

import sys
import requests
import json 
import datetime
import time


###############################################################################
############################## NextTrain.py ###################################
###############################################################################
###########################  Method Definitions ###############################
###############################################################################
# helper function to make the API calls
# handles bad responses and handles rate limiting for the program
def getData(url):

	# make the request
	r = requests.get(url)

	# header values for rate limiting
	remaining = int((r.headers["x-ratelimit-remaining"]))
	reset = int(r.headers["x-ratelimit-reset"])

	# if the status status code is good, we return the data
	if (int(r.status_code) == 200):
		# closer the program is to exceeding the rate limit => longer hang
		time.sleep(5-(remaining/4))
		return r.json()["data"]

	# bad status code
	else:
		# failsafe: status code for rate limit exceeded causes the program to
		# invoke itself recursively, but this shouldn't get executed
		if (int(r.status_code) == 429):
			time.sleep(5)
			return getData(url)
		else:
			# if it's an unexpected status code, raise an exception
			raise Exception('response: {}'.format(r.status_code))
	
	# if it's the last request before the limit is exceeded...
	# wait until the reset time 
	if (remaining==0):
		while datetime.datetime.now() < datetime.datetime.fromtimestamp(reset):
			time.sleep(1)

	# closer the program is to exceeding the rate limit => longer hang
	time.sleep(5-(remaining/4))


# helper function to prompt the user for numeral input response to a 
# route/stop/direction prompt.

def promptUserInput(min,max,message):

	# user can pass a message or use the default
	if message != None:
		user_input = input(message)
	else:
		user_input = input("enter "+str(min)+"-"+str(max)+": ")
	
	# this is to ensure the input is in numeral form before int()-ing it
	try:
		user_input = int(user_input)
		message ="Enter a number in the range "+str(min)+" to "+str(max)
		# if the input is a number, we test that it is in bounds
		if ((user_input < min) or (user_input > max)):
			print (message)
			# if not we let the user try again... infinitely 
			return promptUserInput(min,max,message)
		return user_input
	# if the input is not a number
	except ValueError:
		# but the user can type q and quit if they are savvy 
		if (user_input == "q"):
			quit()
		if (user_input == "help"):
			helpMessage()
	
	# if a good input is not received, we try again
	return promptUserInput(min,max,message)
	 

# Gets the list of subway routes... only invoked once
def getRoutes():
	routes = []
	url = "https://api-v3.mbta.com/routes"
	token = "filter[type]=0,1"
	doc = getData(url+"?"+token)
	for x in doc:
		route = {}
		route["name"] = x["attributes"]["long_name"]
		route["id"] = x["id"]
		route["direction_destinations"]=x["attributes"]["direction_destinations"]
		route["direction_names"]=x["attributes"]["direction_names"]
		routes.append(route)
	return routes

# Gets the list of stops based on route info
def getStops(route):
	stops = []
	url = "https://api-v3.mbta.com/stops"
	token = "filter[route]="+route["id"]
	doc = getData(url+"?"+token)
	for x in doc:
		stop = {}
		stop["name"] = x["attributes"]["name"]
		stop["id"] = x["id"]
		stops.append(stop)
	return stops

# prompt the user to choose one of the routes
def promptRoute(routes,route_num):
	print()
	print("Please select a route: ")
	i = 1
	for x in routes:
		print(str(i)+") "+routes[i-1]["name"])
		i = i+1
	
	if (route_num == None):
		route_num = promptUserInput(1,len(routes),None)
	
	route = routes[route_num-1]
	route["route_num"] = route_num
	return route

# non-interactive method to get the route by string, not numeral input
# spaces " " in the route name should be changed to "_" so that each 
# can be supplied as its own command line argument
# See the help section for use info
def getRoute(routes,route_name):
	i = 1
	for x in routes:
		if routes[i-1]["name"] == route_name.replace("_", " "):
			route = routes[i-1]
			route["route_num"] = i
			return route
		i += 1
	print ("Route not found")
	quit()
	
	
def promptStop(stops,route,stop_num):
	print()
	print("Please select a stop: ")
	i = 1
	for x in stops:
		print(str(i)+") "+stops[i-1]["name"])
		i = i+1

	if (stop_num == None):
		stop_num = promptUserInput(1,len(stops),None)
	
	stop = stops[stop_num-1]
	stop["stop_num"] = stop_num
	stop["num_stops"] = len(stops)
	return stop

# non-interactive method to get the stop by string, not numeral input
# spaces " " in the stop name should be changed to "_" so that each 
# can be supplied as its own command line argument
# See the help section for use info
def getStop(stops,route,stop_name):
	i = 1
	for x in stops:
		if stops[i-1]["name"] == stop_name.replace("_", " "):
			stop = stops[i-1]
			stop["stop_num"] = i
			stop["num_stops"] = len(stops)
			return stop
		i += 1
	print("Stop not found")
	quit()

# This method prompts the user to select one of the directions
# that the train goes. The direction information is cached when the user 
# selects a route. 
def promptDirection(route,stop,direction_num):
	time.sleep(.1)
	stop_num = stop["stop_num"]
	route_num = route["route_num"]

	if ((stop_num == 1) or (stop_num == stop["num_stops"])):
		if (stop_num == 1):
			direction_num = 0
		else:
			direction_num = 1
	else:
		if (direction_num != None):
			return direction_num
		print()
		print("Which direction are you riding?")
		i = 0
		while i < len(route["direction_destinations"]):
			print(str(i+1)+") "+route["direction_names"][i]+" - "+route["direction_destinations"][i])
			i += 1
		direction_num = promptUserInput(1,2,None)-1

	return direction_num
	
# This uses the route, stop, and direction selected to get the next train time
# It uses the predictions API and filters  on stop id, direction id, and 
# route type. It sorts the results based on departure_time and returns the 
# first that yields a non-negative result when the difference between the 
# current time and the departure_time is calculated (i.e. the train hasn't 
# already left the station)

def getNextTrainTime(route,stop,direction):
	print()
	# this is a special case for the ashmont terminal station
	if (route["name"])=="Red Line" and stop["name"] == "Ashmont":
		direction = 1
	if ((stop["stop_num"] == 1) or (stop["stop_num"] == stop["num_stops"])):
		if (stop["stop_num"] == 1):
			direction = 0
		else:
			direction = 1

	url = "https://api-v3.mbta.com/predictions"
	token = "filter[stop]="+stop["id"]+"&filter[direction_id]="+str(direction)+"&filter[route_type]=0,1&sort=departure_time"
	doc = getData(url+"?"+token)
	min_time = {"hours":100,"minutes":100,"seconds":100}
	
	for x in doc:
		arrival = x["attributes"]["departure_time"]
		if arrival != None:
			nextTrainTime = arrival.split("T")[1].split("-")[0]
			now = str(datetime.datetime.now()).split(" ")[1].split(".")[0]
			hours = int(nextTrainTime.split(":")[0])-int(now.split(":")[0])
			minutes = int(nextTrainTime.split(":")[1])-int(now.split(":")[1])
			seconds = int(nextTrainTime.split(":")[2])-int(now.split(":")[2])
			if seconds < 0:
				seconds += 60
				minutes -= 1 
			if minutes < 0:
				minutes += 60
				hours -= 1
			if (hours >=0):
				min_time = {"hours":(hours),"minutes":minutes,"seconds":(seconds)}
				break
	if (min_time["hours"] != 100):
		return min_time
	return None

# Helper function that prints the "next train departs in... " message
def printMessage(nextTrainTime):

	if (nextTrainTime != None):
		print("The next train will depart in "+str(nextTrainTime["minutes"])+" minutes and "+str(nextTrainTime["seconds"])+" seconds")
	else:
		print("No upcoming departures, seek alternate route.")

# Helper function that prints the Help page
def helpMessage():
	print("")
	print("NextTrain.py - San Akdag 2021")
	print("")
	print("Run without arguments to use interactive mode")
	print()
	print("Run with 3 command line arguments if you know which route,")
	print("station, and direction you would like to check")
	print("Route should be the full name that appears in the menu.")
	print("(Note: Replace spaces with underscores)")
	print("The lines are:")
	print("	Red Line")
	print("	Mattapan Trolley")
	print("	Orange Line")
	print("	Green Line B")
	print("	Green Line C")
	print("	Green Line D")
	print("	Green Line E")
	print("	Blue Line")
	print("")
	print("Stops should also match as they appear in the 'name' field:")
	print("Note: Replace spaces with underscores")
	print("	Alewife")
	print("	Davis")
	print("	Porter")
	print("	Harvard")
	print("	Central")
	print("	Kendall/MIT")
	print("	Charles/MGH")
	print("	Park Street")
	print("	...")
	print("")
	print("Finally, directional code... ")
	print("1 = South/West/Outbound")
	print("2 = North/East/Inbound")
	print("")
	print("example:")
	print("	python3 NextTrain.py Red_Line Park_Street 1")
	print()


###############################################################################
############################## NextTrain.py ###################################
###############################################################################
################################  "Main" ######################################
###############################################################################
'''
 run the interactive user-input based routine with the following
 command:
 		$ python3 NextTrain.py
 
  The program will prompt you to select from a list of routes
  and your response should be the number that precedes the stop
  you have selected i.e.
 
	$ python3 NextTrain.py
	
	Which line are you riding?
	1) Red Line
	2) Mattapan Trolley
	3) Orange Line
	4) Green Line B
	5) Green Line C
	6) Green Line D
	7) Green Line E
	8) Blue Line
	enter 1-8:
	$ 1

entering 1 will select the Red Line ...
you will then be prompted for which stop you'd like to receive information
for and, if applicable, the direction you are travelling at which point
the next departure time for the route, stop, and direction is printed to the
screen.

The last prompt asks the user to enter 0/1 to exit the program or to lookup 
another departure time
'''
###############################################################################
if (len(sys.argv) == 1):
	active = 1
	routes = getRoutes()
	while (active == 1):

		route = promptRoute(routes,None)
		if "stops" not in route.keys():
			route["stops"] = getStops(route)
		
		stop = promptStop(route["stops"],route,None)

		direction = promptDirection(route,stop,None)
		nextTrainTime = getNextTrainTime(route,stop,direction)
		printMessage(nextTrainTime)
		print()
		time.sleep(1)
		print("Would you like to check another time?")
		u_input = promptUserInput(0,1,"Enter 0 to quit or 1 to continue...")
		if (u_input == 0): quit()

########################### Automation Test ###################################
# run the test by adding the command line argument "test":
#
# 	$ python3 NextTrain.py test
#
# This test loops thru the routes and all possible stops
# highlighting that the program caches route and stop names, 
# monitors and prevent the rate-limit set by the server from 
# being exceeded, and handles the special case that Ashmont is 
# a terminus despite not being the 0th or (len(stops)-1)th stop
elif (sys.argv[1] == "test"):

	routes = getRoutes()

	# testing the Ashmont special case
	# Red line has 3 termini (forks) and stop 17 is also a terminus
	route = promptRoute(routes,1)
	if "stops" not in route.keys():
	 		route["stops"] = getStops(route)
	stop = promptStop(route["stops"],route,17)
	direction = 0
	direction = promptDirection(route,stop,direction)
	print("Checking "+str(route["name"])+", "+str(stop["name"])+", "+"terminus special case test")
	nextTrainTime = getNextTrainTime(route,stop,direction)
	printMessage(nextTrainTime)

	# This test loops through all of the routes, stops on each route,
	# and direction at each stop. Covers all possible accepted input and
	# shows that the rate limiting capabilities function, as far greater than
	# the maximum number of API calls per period need to be made overall.
	# Also shows that even if an incorrect direction is passed to the internal
	# method (i.e. a direction value is passed to the method for a terminal 
	# stop), only the correct information makes it into the request.
	# (i.e. a train leaves a terminus in only 1 direction)

	for x in range(1,len(routes)):
		route = promptRoute(routes,x)
		if "stops" not in route.keys():
			route["stops"] = getStops(route)
		for y in range (1,len(route["stops"])):
			stop = promptStop(route["stops"],route,y)
			print("Checking "+str(route["name"])+", "+str(stop["name"])+", "+route["direction_names"][0]+" - "+route["direction_destinations"][0])
			nextTrainTime = getNextTrainTime(route,stop,0)
			printMessage(nextTrainTime)
			print("Checking "+str(route["name"])+", "+str(stop["name"])+", "+route["direction_names"][1]+" - "+route["direction_destinations"][1])
			nextTrainTime = getNextTrainTime(route,stop,1)
			printMessage(nextTrainTime)
			

	print ("test passed!")

# this prints the help menu
elif (sys.argv[1] == "help"):
	help_message()

# this is the command-line mode
# replace all spaces in routes and stops with "_"
# If you know the "name" attribute of the route and stop and the direction
# you want to travel already, you can skip the interactive mode
# and submit your query directly on the command line
# example:
#	$ python3 NextTrain.py Red_Line Park_Street 0
#	The next train will depart in 0 minutes and 43 seconds 
else:
	if len(sys.argv) != 4:
		help_message()
	routes = getRoutes()
	route_name = sys.argv[1]
	stop_name = sys.argv[2]
	direction = sys.argv[3]
	route = getRoute(routes,route_name)
	route["stops"] = getStops(route)
	stop = getStop(route["stops"],route,stop_name)
	nextTrainTime = getNextTrainTime(route,stop,direction)
	printMessage(nextTrainTime)

	




