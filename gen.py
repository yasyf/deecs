#!/usr/bin/env python

import sys, random

def init():
	global globals, bump_sensor
	g_str = " ".join(globals)
	print "init"
	print "global [%s]" % (g_str)
	print
	print "to init"
	for g in globals:
		print "  set%s %s" % (g, str(globals[g]))
	print "  when [%s = 0] [\n    song\n    stop!\n  ]" % (bump_sensor)
	print "  main"
	print "end"

def off_track(first_dir, second_dir):
	return """ 
        ifelse is_white %s = 1 [
          setstatus 2
          left 5 5
        ] [
          ifelse is_white %s = 1 [
            setstatus 3
            right 5 5
          ] [
            ifelse ever_on_track = 1 [
              ifelse recovery_attempts < 4 [
                setstatus 4
                back 5 3
                setrecovery_attempts recovery_attempts + 1
              ] [
                setstatus 5
                forward 5 3
              ]
            ] [
              setstatus 6
              forward 5 3
            ]
          ]
        ]""" % (first_dir, second_dir)
def main():
	global sensor_left,sensor_right
	print "to main"
	#TODO add logic if not on track
	print """loop[
    check_on_track
    ifelse on_track = 1 [
      setever_on_track 1
      setrecovery_attempts 0
      setstatus 1
      forward 5 8
    ] [
      ab, off
      ifelse ((timer %% 4) %% 2) = 0 [%s
      ]
      [%s
      ]
      if debug = 1 [
        send status
      ]
    ]
  ]""" % (off_track(sensor_left, sensor_right), off_track(sensor_right, sensor_left))
	print "end"

def music():
	global notes_string
	notes_dict = {"c": "119","c#": "110", "db": "110", "d": "105", "d#": "100", "eb": "100", "e": "94", "f": "89", "f#": "84", "gb": "84", "g": "79", "g#": "74", "ab": "74", "a": "70", "a#": "66", "bb": "66", "b": "62", "c2": "59"}
	notes = notes_string.lower().split()
	print "to song"
	for note in notes:
		if note in notes_dict:
			print "  note %s 3" % (notes_dict.get(note))
	print "end"


def directions():
	global motor_forwards, motor_backwards, motor_left, motor_right
	
	for colour in ["black","white"]:
		print "to is_%s :sensor_value" % (colour)
		print "  if :sensor_value > %s_lower [" % (colour)
		print "    if :sensor_value < %s_upper [" % (colour)
		print "      output 1\n    ]\n  ]\n  output 0\nend"
		
	dirs1 = {"left": motor_forwards, "right": motor_backwards}
	for dir in dirs1:
		print
		print "to %s :time :power" % (dir) 
		print "  ab, %s" % (dirs1[dir])
		print "  ab, setpower :power\n  ab, onfor :time\nend"

	dirs2 = {"forward": {motor_left: motor_forwards, motor_right: motor_backwards}, "back": {motor_left: motor_backwards, motor_right: motor_forwards}}
	for dir in dirs2:
		print
		print "to %s :time :power" % (dir) 
		print "  %s, %s" % (motor_left, dirs2[dir][motor_left])
		print "  %s, %s" % (motor_right, dirs2[dir][motor_right])
		print "  ab, setpower :power\n  ab, onfor :time\nend"
		
def utilities():
	global sensor_front
	
	print """
to check_on_track
  if is_white %s = 1 [
    seton_track 1
  ]
  seton_track 0
end"""  % (sensor_front)

def go():
	init()
	print
	main()
	print
	music()
	print
	directions()
	print
	utilities()

globals = {"white_lower": 0, "white_upper": 50, "black_lower": 150, "black_upper": 255, "on_track": 0, "ever_on_track": 0, "recovery_attempts": 0, "debug": 1, "status": 6}
#Status Codes: 0 (Error) | 1 (On Track) | 2 (Off Track: Track Found In First Direction) | 3 (Off Track: Track Found In Second Direction) | 4 (Off Track: Attempting Recovery) | 5 (Off Track: Recovery Failed) | 6 (Never On Track)
bump_sensor = "sensord"
motor_forwards = "thisway"
motor_backwards = "thatway"
motor_left = "b"
motor_right = "a"
sensor_left = "sensora"
sensor_right = "sensorb"
sensor_front = "sensorc"
try:
	notes_string = sys.argv[1]
except IndexError:
	notes_string = raw_input("Enter Notes (Delimited By Spaces): ")

go()