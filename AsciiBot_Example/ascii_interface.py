import math
import os
import sys

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from dots.interpreter import AsciiDotsInterpreter
from dots.environment import Env
from pathlib import Path
from dots.callbacks import IOCallbacksStorageConstructor

FILE_NAME = "agent.dots"

class AsciiAgent(BaseAgent):
	
	# Gets the side we are on as a 0 or 1
	def get_side(self):
		return -1 if self.team == 1 else 1
	
	# Allows for inverting the team if the math doesn't work out
	def get_team(self):
		return self.team
	
	def parse(self, packet: GameTickPacket):
		side = self.get_side()
		team = self.get_team()
		inputs = []
		
		# Ball
		game_ball = packet.game_ball.physics
		inputs.append(game_ball.location.x * side)
		inputs.append(game_ball.location.y * side)
		inputs.append(game_ball.location.z)
		inputs.append(game_ball.velocity.x * side)
		inputs.append(game_ball.velocity.y * side)
		inputs.append(game_ball.velocity.z)
		inputs.append(game_ball.angular_velocity.x * side)
		inputs.append(game_ball.angular_velocity.y * side)
		inputs.append(game_ball.angular_velocity.z)
		inputs.append(packet.game_ball.drop_shot_info.damage_index)
		
		# Agent
		agent_car = packet.game_cars[self.index]
		agent_car_phys = agent_car.physics
		inputs.append(agent_car_phys.location.x * side)
		inputs.append(agent_car_phys.location.y * side)
		inputs.append(agent_car_phys.location.z)
		inputs.append(agent_car_phys.velocity.x * side)
		inputs.append(agent_car_phys.velocity.y * side)
		inputs.append(agent_car_phys.velocity.z)
		inputs.append((agent_car_phys.rotation.yaw + math.pi * team) % (math.pi * 2))
		inputs.append(agent_car_phys.rotation.pitch)
		inputs.append(agent_car_phys.rotation.roll)
		inputs.append(agent_car_phys.angular_velocity.x * side)
		inputs.append(agent_car_phys.angular_velocity.y * side)
		inputs.append(agent_car_phys.angular_velocity.z)
		
		inputs.append(agent_car.is_super_sonic)
		inputs.append(agent_car.jumped)
		inputs.append(agent_car.double_jumped)
		inputs.append(agent_car.boost)
		inputs.append(agent_car.is_demolished)
		inputs.append(agent_car.has_wheel_contact)
		
		# Reserved
		inputs.append(None)
		inputs.append(None)
		
		# Game info
		game_info = packet.game_info
		inputs.append(game_info.seconds_elapsed)
		inputs.append(game_info.game_time_remaining)
		inputs.append(game_info.is_unlimited_time)
		inputs.append(game_info.is_kickoff_pause)
		inputs.append(game_info.is_round_active)
		inputs.append(game_info.world_gravity_z)
		inputs.append(game_info.is_overtime)
		inputs.append(game_info.is_match_ended)
		
		# Reserved
		while len(inputs) < 98:
			inputs.append(None)
		
		# Other cars in the game
		inputs.append(packet.num_cars)
		cars = packet.game_cars
		for i in range(packet.num_cars):
			car = cars[i]
			if i != self.index:
				car_phys = car.physics
				inputs.append(car_phys.location.x * side)
				inputs.append(car_phys.location.y * side)
				inputs.append(car_phys.location.z)
				inputs.append(car_phys.velocity.x * side)
				inputs.append(car_phys.velocity.y * side)
				inputs.append(car_phys.velocity.z)
				inputs.append((car_phys.rotation.yaw + math.pi * team) % (math.pi * 2))
				inputs.append(car_phys.rotation.pitch)
				inputs.append(car_phys.rotation.roll)
				inputs.append(car_phys.angular_velocity.x * side)
				inputs.append(car_phys.angular_velocity.y * side)
				inputs.append(car_phys.angular_velocity.z)
				
				inputs.append(car.is_super_sonic)
				
				# Reserved
				inputs.append(None)
				inputs.append(None)
				inputs.append(None)
				inputs.append(None)
				
				inputs.append(car.is_demolished)
				inputs.append(car.has_wheel_contact)
				
				# Reserved
				inputs.append(None)
				inputs.append(None)
		
		return inputs
		
	
	def get(self, data):
		c = SimpleControllerState()
		c.throttle = max(min(data[0], 1), -1)
		c.steer = max(min(data[1], 1), -1)
		c.pitch = max(min(data[2], 1), -1)
		c.yaw = max(min(data[3], 1), -1)
		c.roll = max(min(data[4], 1), -1)
		c.jump = data[5]
		c.boost = data[6]
		c.handbrake = data[7]
		c.use_item = data[8]
		return c
	
	def initialize_agent(self):
		
		global interpreter
		
		cwd = os.getcwd()
		
		path = os.path.dirname(os.path.realpath(__file__))
		
		os.chdir(path)
		
		env = Env()
		env.io = IOCallbacksStorageConstructor(get_input, on_output, on_finish, on_error, on_microtick)
		env.io.env = env
		
		program_dir = os.path.dirname(os.path.realpath(FILE_NAME))
		with open(FILE_NAME, encoding='utf-8') as file:
			program = file.read()
		
		interpreter = AsciiDotsInterpreter(env, program, program_dir, True)
		
		self.game_packet = []
		self.controller_state = SimpleControllerState()
		
		os.chdir(cwd)
	
	def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
		interpreter.send(self.parse(packet))
		interpreter.step()
		return self.get(interpreter.recieve())

def get_input(ascii_char=False):
	pass

def on_output(value):
	pass

def on_finish():
	pass

def on_error(error_text):
	print(error_text)

def on_microtick(dot):
	pass
